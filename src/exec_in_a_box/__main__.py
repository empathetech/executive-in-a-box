"""CLI entry point for Executive in a Box."""

import argparse
import sys

from exec_in_a_box import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exec-in-a-box",
        description=(
            "AI-powered executive advisor — "
            "CEO-level strategic guidance without a human CEO."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"exec-in-a-box {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("setup", help="Run the setup wizard")
    subparsers.add_parser("history", help="List recent sessions")

    config_parser = subparsers.add_parser("config", help="View or change configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    config_subparsers.add_parser("autonomy", help="View or change your autonomy level")

    test_parser = subparsers.add_parser(
        "test-connection", help="Test your API key for a provider"
    )
    test_parser.add_argument(
        "provider",
        choices=["anthropic", "openai"],
        help="The provider to test",
    )

    return parser


def cmd_setup() -> None:
    from exec_in_a_box.setup import run_setup

    run_setup()


def cmd_session() -> None:
    from exec_in_a_box import storage
    from exec_in_a_box.session import run_session
    from exec_in_a_box.setup import run_setup

    if not storage.is_initialized():
        print("Welcome to Executive in a Box!")
        print("Let's get you set up first.")
        run_setup()
        print()
        print("Setup complete. Starting your first session...")
        print()

    run_session()


def cmd_autonomy() -> None:
    from exec_in_a_box.config import load_config, save_autonomy_level

    config = load_config()
    if config is None:
        print("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    print()
    print(f"Current autonomy level: {config.autonomy_level}")
    print()
    print("  Level 1 -- Advisor")
    print("    Presents options and explains tradeoffs. You decide everything.")
    print()
    print("  Level 2 -- Recommender")
    print("    Gives you a specific recommendation. You approve or change it.")
    print()
    print("  Levels 3 and 4 are coming in V1.")
    print()

    raw = input("New level [1-2] (or Enter to keep current): ").strip()
    if not raw:
        print("No change.")
        return

    try:
        new_level = int(raw)
    except ValueError:
        print("Please enter 1 or 2.")
        return

    if new_level not in (1, 2):
        if new_level in (3, 4):
            print("Levels 3 and 4 are not available yet (coming in V1).")
        else:
            print("Please enter 1 or 2.")
        return

    if new_level == config.autonomy_level:
        print("No change.")
        return

    save_autonomy_level(new_level)
    print(f"Autonomy level changed to {new_level}.")


def cmd_test_connection(provider_name: str) -> None:
    from exec_in_a_box.config import load_config
    from exec_in_a_box.credentials import get_api_key
    from exec_in_a_box.providers import ProviderError, create_provider

    config = load_config()
    if config is None:
        print("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    if config.provider_name != provider_name:
        print(
            f"Your configured provider is "
            f"{config.provider_name}, not {provider_name}."
        )
        print(
            f"To test {provider_name}, set the "
            "appropriate environment variable"
        )
        print(
            "or run exec-in-a-box setup to "
            "change your provider."
        )
        sys.exit(1)

    api_key = get_api_key(provider_name)
    if api_key is None:
        print(
            f"No API key found for {provider_name}. "
            "Run: exec-in-a-box setup"
        )
        sys.exit(1)

    print(
        f"Testing connection to {provider_name}...",
        end=" ",
        flush=True,
    )
    try:
        provider = create_provider(
            provider_name, api_key=api_key
        )
        provider.test_connection()
        print("Connected successfully.")
    except ProviderError as e:
        print("Failed.")
        print(f"  {e.user_message}")
        sys.exit(1)


def cmd_history() -> None:
    from exec_in_a_box import storage

    sessions = storage.list_sessions()
    if not sessions:
        print("No sessions yet. Run: exec-in-a-box")
        return

    print()
    print("Recent sessions:")
    print()
    for path in sessions[:20]:
        # Read first non-empty, non-header line as preview
        text = path.read_text(encoding="utf-8")
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.startswith("#")
        ]
        preview = lines[0][:70] if lines else "(empty)"
        print(f"  {path.name}  {preview}")
    print()
    total = len(sessions)
    if total > 20:
        print(f"  ... and {total - 20} more")
    print(f"  Sessions stored at: {storage.get_data_dir() / 'sessions'}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        cmd_session()
        return

    if args.command == "setup":
        cmd_setup()
        return

    if args.command == "config":
        if args.config_command == "autonomy":
            cmd_autonomy()
        else:
            parser.parse_args(["config", "--help"])
        return

    if args.command == "test-connection":
        cmd_test_connection(args.provider)
        return

    if args.command == "history":
        cmd_history()
        return


if __name__ == "__main__":
    main()
