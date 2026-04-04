"""Core session loop — the primary user interaction.

User asks a strategic question, the board deliberates, user decides.
Supports multi-CEO switching, Executize background jobs, and artifact commands.

Reference: hacky-hours/02-design/USER_JOURNEYS.md § Ask the CEO a Question
Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Error Handling Contract
"""

from __future__ import annotations

import sys
import threading
from datetime import datetime
from typing import Optional

from exec_in_a_box import storage
from exec_in_a_box.archetypes import get_archetype, list_archetypes
from exec_in_a_box.cli_display import (
    C,
    colorize,
    divider,
    print_banner,
    print_ceo_header,
    print_error,
    print_executizing,
    print_job_complete,
    print_response,
    print_thinking,
    print_warning,
)
from exec_in_a_box.config import load_config, save_autonomy_level
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


def _get_decision(autonomy_level: int, has_slack: bool) -> str:
    """Get the user's decision. Returns 'y', 'n', 'm', 'h', or 's'."""
    slack_hint = " / " + colorize("[S]lack", C.LIME) if has_slack else ""
    label = "recommendation" if autonomy_level == 2 else "position"
    prompt = (
        colorize(f"\n  Adopt this {label}? ", C.DIM)
        + colorize("[Y]es", C.LIME) + colorize(" / ", C.DIM)
        + colorize("[N]o", C.MAGENTA) + colorize(" / ", C.DIM)
        + colorize("[M]odify", C.YELLOW) + colorize(" / ", C.DIM)
        + colorize("[H]ow", C.CYAN) + colorize(" (reasoning)", C.DIM)
        + slack_hint
        + colorize(": ", C.DIM)
    )

    while True:
        raw = _input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return "y"
        if raw in ("n", "no"):
            return "n"
        if raw in ("m", "modify"):
            return "m"
        if raw in ("h", "how", "reasoning"):
            return "h"
        if raw in ("s", "slack") and has_slack:
            return "s"
        print(colorize("  Enter: Y, N, M, H" + (", S" if has_slack else ""), C.DIM))


def _send_to_slack(response: ValidatedResponse, config, archetype) -> None:
    """Let user craft and send a message to Slack."""
    from exec_in_a_box.slack import send_message

    print()
    print(colorize("  What would you like to send to Slack?", C.CYAN))
    print()
    print(colorize("  1. ", C.DIM) + "The recommendation as-is")
    print(colorize("  2. ", C.DIM) + "Write a custom message")
    print(colorize("  3. ", C.DIM) + "Cancel")
    print()

    choice = _input("  Pick [1-3]: ").strip()

    if choice == "1":
        message = response.position
    elif choice == "2":
        print()
        message = _input(colorize("  Message: ", C.CYAN)).strip()
        if not message:
            print(colorize("  Empty message. Cancelled.", C.DIM))
            return
    else:
        print(colorize("  Cancelled.", C.DIM))
        return

    # Always preview before sending (enforced in BUSINESS_LOGIC.md)
    print()
    print(colorize("  ─── Preview ───", C.DIM))
    print(f"  {message}")
    print(colorize("  ───────────────", C.DIM))
    print()
    confirm = _input(
        colorize("  Send to Slack? ", C.DIM)
        + colorize("[Y]es", C.LIME)
        + colorize(" / ", C.DIM)
        + colorize("[E]dit", C.YELLOW)
        + colorize(" / ", C.DIM)
        + colorize("[C]ancel", C.MAGENTA)
        + colorize(": ", C.DIM)
    ).strip().lower()

    if confirm in ("e", "edit"):
        message = _input(colorize("  Corrected message: ", C.CYAN)).strip()
        if not message:
            print(colorize("  Empty message. Cancelled.", C.DIM))
            return
        print()
        print(colorize("  ─── Preview ───", C.DIM))
        print(f"  {message}")
        print(colorize("  ───────────────", C.DIM))
        print()
        confirm = _input(
            colorize("  Send to Slack? [Y/N]: ", C.DIM)
        ).strip().lower()

    if confirm not in ("y", "yes"):
        print(colorize("  Cancelled.", C.DIM))
        return

    print(colorize("  Sending to Slack...", C.CYAN), end=" ", flush=True)
    success = send_message(
        message,
        archetype_slug=config.archetype_slug,
        archetype_name=archetype.name,
    )
    if success:
        print(colorize("Sent!", C.LIME))
    print()


def _log_decision(
    question: str,
    response: ValidatedResponse,
    decision: str,
    modification: Optional[str],
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
    modification: Optional[str],
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


def _switch_ceo_interactive() -> Optional[str]:
    """Interactive CEO switcher. Returns new slug or None if cancelled."""
    archetypes = list_archetypes()
    print()
    print(colorize("  Select CEO:", C.CYAN))
    print()
    for i, a in enumerate(archetypes, 1):
        print(f"  {colorize(str(i), C.BOLD, C.WHITE)}. {a.name} {colorize('—', C.DIM)} {a.one_line}")
    print()
    raw = _input(
        colorize(f"  Pick [1-{len(archetypes)}] or Enter to cancel: ", C.DIM)
    ).strip()
    if not raw:
        return None
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(archetypes):
            return archetypes[idx].slug
    except ValueError:
        pass
    print(colorize("  Invalid choice.", C.DIM))
    return None


def _dispatch_executize_job(
    archetype_slug: str,
    question: str,
    api_key: str,
    provider_name: str,
) -> Optional[str]:
    """Dispatch an Executize job in a background thread. Returns job_id."""
    from exec_in_a_box.jobs import create_job, _persist

    job = create_job(archetype_name=archetype_slug, prompt=question)
    job_id = job["id"]

    def _run():
        try:
            job["status"] = "running"
            _persist(job)

            archetype = get_archetype(archetype_slug)
            if archetype is None:
                raise ValueError(f"Unknown archetype: {archetype_slug}")

            from exec_in_a_box.credentials import get_api_key as _get_key
            key = _get_key(provider_name) or api_key

            provider = create_provider(provider_name, api_key=key)
            system_prompt, user_message, _ = build_prompt(archetype, question)
            response = provider.send(system_prompt, user_message)
            result = validate_response(response.content)

            if isinstance(result, list):
                job["status"] = "failed"
                job["error"] = "Response validation failed."
            else:
                import json
                job["status"] = "complete"
                job["result"] = json.dumps({
                    "valid": True,
                    "archetype": result.archetype,
                    "position": result.position,
                    "reasoning": result.reasoning,
                    "confidence": result.confidence,
                    "ambition_level": result.ambition_level,
                    "pros": result.pros,
                    "cons": result.cons,
                    "flags": result.flags,
                    "questions_for_user": result.questions_for_user,
                })
            _persist(job)
        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)
            _persist(job)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return job_id


def run_session(initial_slug: Optional[str] = None) -> None:
    """Run the interactive board session loop."""
    from exec_in_a_box.credentials import get_api_key

    config = load_config()
    if config is None:
        print_error("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    active_slug = initial_slug or config.archetype_slug
    archetype = get_archetype(active_slug)
    if archetype is None:
        print_error(f"Unknown archetype: {active_slug}. Run: exec-in-a-box setup")
        sys.exit(1)

    api_key = get_api_key(config.provider_name)
    if api_key is None:
        print_error(f"No API key found for {config.provider_name}. Run: exec-in-a-box setup")
        sys.exit(1)

    effective_level = min(config.autonomy_level, 2)

    # Active background jobs: {job_id: archetype_slug}
    active_jobs: dict[str, str] = {}

    print_banner()
    print_ceo_header(archetype.name, effective_level, config.provider_name)

    while True:
        # Check for completed jobs before each prompt
        for job_id in list(active_jobs.keys()):
            from exec_in_a_box.jobs import get_job
            job = get_job(job_id)
            if job and job["status"] in ("complete", "failed"):
                a_slug = active_jobs.pop(job_id)
                a = get_archetype(a_slug)
                a_name = a.name if a else a_slug
                if job["status"] == "complete" and job.get("result"):
                    print_job_complete(a_name)
                    try:
                        import json
                        result_data = json.loads(job["result"])
                        from exec_in_a_box.wrapper import ValidatedResponse as VR
                        vr = VR(
                            archetype=result_data["archetype"],
                            position=result_data["position"],
                            reasoning=result_data["reasoning"],
                            confidence=result_data["confidence"],
                            ambition_level=result_data["ambition_level"],
                            pros=result_data["pros"],
                            cons=result_data["cons"],
                            flags=result_data["flags"],
                            questions_for_user=result_data["questions_for_user"],
                        )
                        print_response(vr, effective_level, a_name)
                    except Exception:
                        print(colorize(f"  Result: {job['result'][:200]}", C.DIM))
                else:
                    print_error(f"{a_name}'s job failed: {job.get('error', 'Unknown error')}")

        prompt_str = (
            colorize("\n  ", C.DIM)
            + colorize(f"[{archetype.name}]", C.BOLD, C.CYAN)
            + colorize(" > ", C.DIM)
        )
        question = _input(prompt_str).strip()

        if not question:
            continue

        # ---- Meta-commands ----
        if question.lower() in ("/quit", "/exit", "quit", "exit", "q"):
            print(colorize("\n  Session ended.", C.DIM))
            break

        if question.lower() == "/switch":
            new_slug = _switch_ceo_interactive()
            if new_slug:
                new_arch = get_archetype(new_slug)
                if new_arch:
                    archetype = new_arch
                    active_slug = new_slug
                    print(colorize(f"\n  Switched to {archetype.name}.", C.LIME))
                    print(divider())
            continue

        if question.lower().startswith("/executize"):
            # Extract message after the command
            parts = question.split(None, 1)
            msg = parts[1].strip() if len(parts) > 1 else ""
            if not msg:
                msg = _input(colorize(
                    "  What should they work on? ", C.CYAN
                )).strip()
            if not msg:
                print(colorize("  No prompt given. Cancelled.", C.DIM))
                continue
            job_id = _dispatch_executize_job(
                active_slug, msg, api_key, config.provider_name
            )
            if job_id:
                active_jobs[job_id] = active_slug
                print_executizing(archetype.name, job_id)
            continue

        if question.lower() == "/jobs":
            from exec_in_a_box.jobs import list_jobs
            jobs = list_jobs()
            if not jobs:
                print(colorize("\n  No jobs yet.", C.DIM))
            else:
                print()
                for j in jobs[:10]:
                    short_id = j["id"][:8]
                    status_color = {
                        "queued": C.YELLOW,
                        "running": C.CYAN,
                        "complete": C.LIME,
                        "failed": C.MAGENTA,
                    }.get(j["status"], C.DIM)
                    print(
                        colorize(f"  {short_id}…", C.DIM)
                        + " "
                        + colorize(j["status"], status_color)
                        + colorize(f" — {j['archetype']}: {j['prompt'][:50]}", C.DIM)
                    )
            continue

        # Check for URLs
        from exec_in_a_box.fetch import extract_urls

        urls = extract_urls(question)
        if urls:
            print()
            for url in urls:
                print(colorize(f"  Fetching: {url}", C.DIM))

        # Build prompt
        system_prompt, user_message, secret_matches = build_prompt(archetype, question)

        # Handle secrets
        if secret_matches:
            print_warning("Suspected secrets found in your context:")
            for match in secret_matches:
                source = match.file_path or "unknown"
                line = f" (line {match.line_number})" if match.line_number else ""
                print(
                    colorize(f"    - {match.pattern_name}", C.YELLOW)
                    + colorize(f" in {source}{line}: {match.matched_text}", C.DIM)
                )
            print()
            confirm = _input(
                colorize("  Continue with redacted context? [Y/N]: ", C.DIM)
            ).strip().lower()
            if confirm not in ("y", "yes"):
                print(colorize("  Cancelled.", C.DIM))
                continue

        # Call the LLM
        print_thinking(archetype.name)

        try:
            provider = create_provider(config.provider_name, api_key=api_key)
            provider_response = provider.send(system_prompt, user_message)
        except ProviderError as e:
            print_error(e.user_message)
            continue

        # Validate
        result = validate_response(provider_response.content)

        if isinstance(result, list):
            print_error("The advisor's response couldn't be parsed. Try rephrasing your question.")
            storage.append_file(
                "debug.log",
                f"\n--- Validation failure at {datetime.now().isoformat()} ---\n"
                f"Raw response:\n{provider_response.content}\n"
                f"Errors: {[f'{e.field}: {e.message}' for e in result]}\n",
            )
            continue

        print_response(result, effective_level, archetype.name)

        from exec_in_a_box.slack import get_webhook_url
        has_slack = get_webhook_url() is not None

        while True:
            decision = _get_decision(effective_level, has_slack)
            if decision == "h":
                print()
                print(colorize(f"  ─── How {result.archetype} got here ───", C.CYAN))
                print()
                print(
                    colorize("  Ambition level: ", C.DIM)
                    + colorize(result.ambition_level.replace("_", " "), C.BOLD, C.WHITE)
                )
                print()
                print(f"  {result.reasoning}")
                print()
                print(colorize("  ─────────────────────────────────────", C.CYAN))
                continue
            if decision == "s":
                _send_to_slack(result, config, archetype)
                continue
            break

        modification = None
        if decision == "m":
            modification = _input(
                colorize("  What would you change? ", C.CYAN)
            ).strip()

        _log_decision(question, result, decision, modification)
        _save_session(question, result, decision, modification)

        decision_text = {"y": "Adopted", "n": "Rejected", "m": "Modified"}[decision]
        print(
            colorize(f"\n  Decision recorded: ", C.DIM)
            + colorize(decision_text, C.LIME)
        )
