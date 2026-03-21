"""Core session loop — the primary user interaction.

User asks a strategic question, the board deliberates, user decides.

Reference: hacky-hours/02-design/USER_JOURNEYS.md § Journey 2
Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Error Handling Contract
"""

from __future__ import annotations

import sys
from datetime import datetime

from exec_in_a_box import storage
from exec_in_a_box.archetypes import get_archetype
from exec_in_a_box.config import load_config
from exec_in_a_box.providers import ProviderError, create_provider
from exec_in_a_box.wrapper import (
    ValidatedResponse,
    build_prompt,
    validate_response,
)


def _input(prompt: str) -> str:
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n\nSession ended.")
        sys.exit(0)


def _display_response(response: ValidatedResponse, autonomy_level: int) -> None:
    """Format and display a validated response to the user."""
    print()
    print(f"{'=' * 60}")
    print(f"  {response.archetype}'s Position")
    print(f"{'=' * 60}")
    print()

    if autonomy_level == 2:
        print(f"  RECOMMENDATION: {response.position}")
    else:
        print(f"  {response.position}")
    print()

    print(f"  Confidence: {response.confidence.upper()}")
    print()

    print("  Pros:")
    for pro in response.pros:
        print(f"    + {pro}")
    print()

    print("  Cons:")
    for con in response.cons:
        print(f"    - {con}")
    print()

    if response.flags:
        print("  Flags:")
        for flag in response.flags:
            print(f"    ! {flag}")
        print()

    if response.questions_for_user:
        print("  Questions for you:")
        for q in response.questions_for_user:
            print(f"    ? {q}")
        print()

    print(f"{'=' * 60}")


def _display_reasoning(response: ValidatedResponse) -> None:
    """Show the full reasoning chain."""
    print()
    print(f"--- How {response.archetype} got here ---")
    print()
    print(f"  Ambition level: {response.ambition_level.replace('_', ' ')}")
    print()
    print(f"  {response.reasoning}")
    print()
    print("---")


def _get_decision(autonomy_level: int, has_slack: bool) -> str:
    """Get the user's decision. Returns 'y', 'n', 'm', 'h', or 's'."""
    slack_hint = " / [S]lack" if has_slack else ""
    if autonomy_level == 2:
        prompt = (
            "Adopt this recommendation? "
            f"[Y]es / [N]o / [M]odify{slack_hint}: "
        )
    else:
        prompt = (
            "Adopt this position? "
            f"[Y]es / [N]o / [M]odify{slack_hint}: "
        )

    while True:
        raw = _input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return "y"
        if raw in ("n", "no"):
            return "n"
        if raw in ("m", "modify"):
            return "m"
        if raw in ("h", "how", "how did you get here", "reasoning"):
            return "h"
        if raw in ("s", "slack") and has_slack:
            return "s"
        options = "Y, N, M, H (reasoning)"
        if has_slack:
            options += ", S (Slack)"
        print(f"  Enter {options}.")


def _send_to_slack(response, config, archetype) -> None:
    """Let user craft and send a message to Slack."""
    from exec_in_a_box.slack import send_message

    print()
    print("  What would you like to send to Slack?")
    print()
    print("  1. The recommendation as-is")
    print("  2. Write a custom message")
    print("  3. Cancel")
    print()

    try:
        choice = _input("  Pick [1-3]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return

    if choice == "1":
        message = response.position
    elif choice == "2":
        print()
        print("  Type your message (the CEO's advice is")
        print("  available for reference above):")
        print()
        message = _input("  Message: ").strip()
        if not message:
            print("  Empty message. Cancelled.")
            return
    else:
        print("  Cancelled.")
        return

    # Always preview before sending
    print()
    print("  --- Preview ---")
    print(f"  {message}")
    print("  ---------------")
    print()
    confirm = _input(
        "  Send this to Slack? "
        "[Y]es / [E]dit / [C]ancel: "
    ).strip().lower()

    if confirm in ("e", "edit"):
        print()
        print("  Type the corrected message:")
        print()
        message = _input("  Message: ").strip()
        if not message:
            print("  Empty message. Cancelled.")
            return
        print()
        print("  --- Preview ---")
        print(f"  {message}")
        print("  ---------------")
        print()
        confirm = _input(
            "  Send this to Slack? [Y/N]: "
        ).strip().lower()

    if confirm not in ("y", "yes"):
        print("  Cancelled.")
        return

    print("  Sending to Slack...", end=" ", flush=True)
    success = send_message(
        message,
        archetype_slug=config.archetype_slug,
        archetype_name=archetype.name,
    )
    if success:
        print("Sent!")
    print()


def _log_decision(
    question: str,
    response: ValidatedResponse,
    decision: str,
    modification: str | None,
) -> None:
    """Append the decision to the decisions log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    decision_text = {"y": "Adopted", "n": "Rejected", "m": "Modified"}[decision]

    entry = (
        f"\n## {timestamp}\n\n"
        f"**Question:** {question}\n\n"
        f"**Advisor:** {response.archetype} (confidence: {response.confidence})\n\n"
        f"**Position:** {response.position}\n\n"
        f"**Decision:** {decision_text}\n"
    )
    if modification:
        entry += f"\n**Modification:** {modification}\n"

    storage.append_file("org/decisions.md", entry)


def _save_session(
    question: str,
    response: ValidatedResponse,
    decision: str,
    modification: str | None,
) -> None:
    """Save the full session transcript."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = storage.next_session_path()

    content = (
        f"# Session — {timestamp}\n\n"
        f"## Question\n{question}\n\n"
        f"## {response.archetype}'s Response\n\n"
        f"**Position:** {response.position}\n\n"
        f"**Reasoning:** {response.reasoning}\n\n"
        f"**Confidence:** {response.confidence}\n"
        f"**Ambition level:** {response.ambition_level}\n\n"
        f"**Pros:**\n"
    )
    for pro in response.pros:
        content += f"- {pro}\n"
    content += "\n**Cons:**\n"
    for con in response.cons:
        content += f"- {con}\n"
    if response.flags:
        content += "\n**Flags:**\n"
        for flag in response.flags:
            content += f"- {flag}\n"
    if response.questions_for_user:
        content += "\n**Questions:**\n"
        for q in response.questions_for_user:
            content += f"- {q}\n"

    decision_text = {"y": "Adopted", "n": "Rejected", "m": "Modified"}[decision]
    content += f"\n## Decision\n{decision_text}\n"
    if modification:
        content += f"\n**Modification:** {modification}\n"

    storage.write_file(str(path.relative_to(storage.get_data_dir())), content)


def run_session() -> None:
    """Run the interactive board session loop."""
    from exec_in_a_box.credentials import get_api_key

    config = load_config()
    if config is None:
        print("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    archetype = get_archetype(config.archetype_slug)
    if archetype is None:
        print(
            f"Unknown archetype: {config.archetype_slug}. "
            "Run: exec-in-a-box setup"
        )
        sys.exit(1)

    api_key = get_api_key(config.provider_name)
    if api_key is None:
        print(
            "No API key found for "
            f"{config.provider_name}. "
            "Run: exec-in-a-box setup"
        )
        sys.exit(1)

    # Enforce autonomy level bounds
    if config.autonomy_level > 2:
        print("Autonomy levels 3 and 4 are not available yet (coming in V1).")
        print("Your level has been treated as Level 2 for this session.")
        effective_level = 2
    else:
        effective_level = config.autonomy_level

    print()
    print(f"Executive in a Box — {archetype.name}")
    print(f"Autonomy: Level {effective_level}")
    print(
        "Type your question, or 'quit' to exit."
        " Include URLs to give the CEO web context."
    )
    print()

    while True:
        question = _input("> ").strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Session ended.")
            break

        # Check for URLs and notify user
        from exec_in_a_box.web import extract_urls

        urls = extract_urls(question)
        if urls:
            print()
            for url in urls:
                print(f"  Fetching: {url}")

        # Build prompt (pre-call enforcement)
        system_prompt, user_message, secret_matches = build_prompt(archetype, question)

        # Handle secret detection
        if secret_matches:
            print()
            print("  ! WARNING: Suspected secrets found in your context:")
            for match in secret_matches:
                source = match.file_path or "unknown"
                line = f" (line {match.line_number})" if match.line_number else ""
                print(f"    - {match.pattern_name} in {source}{line}: {match.matched_text}")
            print()
            print("  The matched content has been redacted before sending.")
            confirm = _input("  Continue with redacted context? [Y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("  Call cancelled. Remove the secret from your context files and try again.")
                continue

        # Call the LLM
        print()
        print(f"  {archetype.name} is thinking...", flush=True)

        try:
            provider = create_provider(
                config.provider_name, api_key=api_key
            )
            provider_response = provider.send(system_prompt, user_message)
        except ProviderError as e:
            print(f"\n  {e.user_message}")
            continue

        # Validate response (post-call enforcement)
        result = validate_response(provider_response.content)

        if isinstance(result, list):
            # Validation failed
            print("\n  The advisor's response couldn't be used (formatting issue).")
            print("  Try rephrasing your question.")
            # Log raw response to debug file
            storage.append_file(
                "debug.log",
                f"\n--- Validation failure at {datetime.now().isoformat()} ---\n"
                f"Raw response:\n{provider_response.content}\n"
                f"Errors: {[f'{e.field}: {e.message}' for e in result]}\n",
            )
            continue

        # Display the response
        _display_response(result, effective_level)

        # Check if Slack is configured
        from exec_in_a_box.slack import get_webhook_url, send_message

        has_slack = get_webhook_url() is not None

        # Decision loop
        while True:
            decision = _get_decision(effective_level, has_slack)
            if decision == "h":
                _display_reasoning(result)
                continue
            if decision == "s":
                _send_to_slack(result, config, archetype)
                continue
            break

        modification = None
        if decision == "m":
            modification = _input(
                "  What would you change? "
            ).strip()

        # Log and save
        _log_decision(question, result, decision, modification)
        _save_session(question, result, decision, modification)

        decision_text = {
            "y": "Adopted",
            "n": "Rejected",
            "m": "Modified",
        }[decision]
        print(f"\n  Decision recorded: {decision_text}")
        print()
