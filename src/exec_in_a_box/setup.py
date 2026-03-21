"""Setup wizard — first-run configuration.

Walks the user through configuring their org profile, choosing an archetype,
connecting an LLM provider, and setting an autonomy level.

Reference: hacky-hours/02-design/USER_JOURNEYS.md § Journey 1
"""

from __future__ import annotations

import sys

from exec_in_a_box import storage
from exec_in_a_box.archetypes import Archetype, list_archetypes
from exec_in_a_box.providers import ProviderError, create_provider


def _input(prompt: str) -> str:
    """Read input, handling EOF/KeyboardInterrupt gracefully."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n\nSetup cancelled.")
        sys.exit(0)


def _choose(prompt: str, options: list[str], descriptions: list[str] | None = None) -> int:
    """Present numbered options and get a valid choice. Returns 0-based index."""
    print(prompt)
    print()
    for i, option in enumerate(options, 1):
        if descriptions:
            print(f"  {i}. {option}")
            print(f"     {descriptions[i - 1]}")
            print()
        else:
            print(f"  {i}. {option}")
    print()

    while True:
        raw = _input(f"Pick a number [1-{len(options)}]: ").strip()
        try:
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice - 1
        except ValueError:
            pass
        print(f"Please enter a number between 1 and {len(options)}.")


def run_setup() -> None:
    """Run the interactive setup wizard."""
    print()
    print("=" * 60)
    print("  Executive in a Box — Setup")
    print("=" * 60)
    print()
    print("This wizard helps you configure your AI executive advisor.")
    print("It takes about 5 minutes. You can change anything later")
    print("by running: exec-in-a-box setup")
    print()

    # --- Step 1: Org Profile ---
    print("-" * 40)
    print("  Step 1: Your Organization")
    print("-" * 40)
    print()

    org_name = ""
    while not org_name.strip():
        org_name = _input("What's your org's name? ")

    org_description = ""
    while not org_description.strip():
        org_description = _input("In one or two sentences, what does it do? ")

    org_values = ""
    while not org_values.strip():
        org_values = _input("What are the most important values your org operates by? ")

    profile_content = (
        f"# {org_name.strip()}\n\n"
        f"## Description\n{org_description.strip()}\n\n"
        f"## Values\n{org_values.strip()}\n"
    )

    print()

    # --- Step 2: Archetype ---
    print("-" * 40)
    print("  Step 2: Your Advisor")
    print("-" * 40)

    archetypes = list_archetypes()
    names = [a.name for a in archetypes]
    descriptions = [f"{a.one_line}" for a in archetypes]

    archetype_idx = _choose(
        "Pick an advisor archetype. Each one has a different strategic lens:",
        names,
        descriptions,
    )
    chosen_archetype: Archetype = archetypes[archetype_idx]
    print(f"  -> {chosen_archetype.name}")
    print()

    # --- Step 3: Provider ---
    print("-" * 40)
    print("  Step 3: Your AI Provider")
    print("-" * 40)

    provider_idx = _choose(
        "Which AI provider should power your advisor?",
        ["Anthropic (Claude)", "OpenAI (GPT)"],
        [
            "Safety-focused AI. Recommended starting model: Claude Sonnet. ~$0.03-0.08 per question.",
            "Largest commercial AI provider. Recommended starting model: GPT-4.1. ~$0.02-0.06 per question.",
        ],
    )
    provider_name = "anthropic" if provider_idx == 0 else "openai"

    # Get API key
    print()
    print("Enter your API key. It will be stored securely in your")
    print("operating system's keychain (macOS Keychain, Windows")
    print("Credential Locker, or Linux Secret Service).")
    print("It is never stored in a plaintext file.")
    print()

    api_key = ""
    while not api_key.strip():
        api_key = _input("API key: ")

    # Test connection
    print()
    print(f"Testing connection to {provider_name}...", end=" ", flush=True)
    try:
        provider = create_provider(provider_name, api_key=api_key.strip())
        provider.test_connection()
        print("Connected successfully.")
    except ProviderError as e:
        print("Failed.")
        print()
        print(f"  {e.user_message}")
        print()
        print("Setup cannot continue without a working API key.")
        print("Check the Provider Guide in docs/PROVIDER_GUIDE.md for help.")
        sys.exit(1)

    print()

    # --- Step 4: Autonomy Level ---
    print("-" * 40)
    print("  Step 4: How much should your CEO do on its own?")
    print("-" * 40)

    autonomy_idx = _choose(
        "Pick an autonomy level:",
        [
            "Level 1 -- Advisor",
            "Level 2 -- Recommender",
        ],
        [
            "I'll present options and explain tradeoffs. You decide everything.",
            "I'll give you a specific recommendation. You approve or change it.",
        ],
    )
    autonomy_level = autonomy_idx + 1

    print(f"  -> Level {autonomy_level}")
    if autonomy_level == 1:
        print("  Good choice for getting started. You're fully in control.")
    print()

    # --- Save everything ---
    storage.ensure_data_dir()
    storage.write_file("org/profile.md", profile_content)
    storage.write_file("org/decisions.md", f"# Decisions — {org_name.strip()}\n\n")
    storage.write_file("org/stakeholders.md", f"# Stakeholders — {org_name.strip()}\n\n")
    storage.write_file("memory/strategic-context.md", "")
    storage.write_file("memory/open-questions.md", "")

    config_content = (
        f"# Board Configuration\n\n"
        f"## Archetype\n"
        f"slug: {chosen_archetype.slug}\n"
        f"name: {chosen_archetype.name}\n\n"
        f"## Provider\n"
        f"provider: {provider_name}\n\n"
        f"## Autonomy\n"
        f"level: {autonomy_level}\n"
    )
    storage.write_file("board/config.md", config_content)

    # Store API key in OS keychain (not in config file)
    from exec_in_a_box.credentials import store_api_key

    store_api_key(provider_name, api_key.strip())

    # --- Summary ---
    data_dir = storage.get_data_dir()
    print("=" * 60)
    print("  Setup Complete")
    print("=" * 60)
    print()
    print(f"  Org:       {org_name.strip()}")
    print(f"  Advisor:   {chosen_archetype.name} ({provider_name.title()})")
    print(f"  Autonomy:  Level {autonomy_level}")
    print()
    print(f"  Your data is stored at: {data_dir}")
    print("  Change any of this by running: exec-in-a-box setup")
    print()
    print("  Ready to ask your first question? Just run: exec-in-a-box")
    print()
