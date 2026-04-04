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

    config_parser = subparsers.add_parser(
        "config", help="View or change configuration"
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_command"
    )
    config_subparsers.add_parser(
        "autonomy", help="View or change your autonomy level"
    )
    config_subparsers.add_parser(
        "archetype", help="Change your advisor archetype"
    )
    config_subparsers.add_parser(
        "provider", help="Change your LLM provider"
    )
    config_subparsers.add_parser(
        "show", help="Show current configuration"
    )

    test_parser = subparsers.add_parser(
        "test-connection", help="Test your API key for a provider"
    )
    test_parser.add_argument(
        "provider",
        choices=["anthropic", "openai"],
        help="The provider to test",
    )

    web_parser = subparsers.add_parser(
        "web",
        help="Start the web app (serves pre-built React UI + API)",
    )
    web_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1; use 0.0.0.0 for Tailscale)",
    )
    web_parser.add_argument(
        "--port",
        type=int,
        default=8421,
        help="Port to listen on (default: 8421)",
    )

    dev_parser = subparsers.add_parser(
        "dev",
        help="Start dev server (FastAPI + Vite with hot reload)",
    )
    dev_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for FastAPI (default: 127.0.0.1)",
    )
    dev_parser.add_argument(
        "--port",
        type=int,
        default=8421,
        help="Port for FastAPI (default: 8421)",
    )

    slack_parser = subparsers.add_parser(
        "slack",
        help="Send a message to Slack via webhook",
    )
    slack_parser.add_argument(
        "slack_args",
        nargs="*",
        default=[],
        help=(
            '"message" to send, '
            "--last for last recommendation, "
            "or setup to configure"
        ),
    )

    artifacts_parser = subparsers.add_parser(
        "artifacts",
        help="Manage session artifacts",
    )
    artifacts_subparsers = artifacts_parser.add_subparsers(dest="artifacts_command")
    artifacts_subparsers.add_parser("list", help="List all artifacts")
    artifacts_open = artifacts_subparsers.add_parser(
        "open", help="Print an artifact to stdout"
    )
    artifacts_open.add_argument(
        "artifact_id",
        help='Artifact ID in "session-id/filename" format',
    )

    subparsers.add_parser(
        "stats",
        help="Show CEO personality profiles and decision history",
    )

    all_hands_parser = subparsers.add_parser(
        "all-hands",
        help="Facilitate an all-hands meeting across all archetypes",
    )
    all_hands_parser.add_argument(
        "items",
        nargs="*",
        help="Agenda items (prompted interactively if not provided)",
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

    if new_level not in (1, 2, 3, 4):
        print("Please enter 1, 2, 3, or 4.")
        return

    if new_level in (3, 4):
        from exec_in_a_box.autonomy import get_acknowledgment_text
        ack_text = get_acknowledgment_text(new_level)
        print()
        print(ack_text)
        try:
            confirmation = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return
        if confirmation != "CONFIRM":
            print("Not confirmed. Level unchanged.")
            return

    if new_level == config.autonomy_level:
        print("No change.")
        return

    save_autonomy_level(new_level)
    print(f"Autonomy level changed to {new_level}.")


def cmd_config_show() -> None:
    from exec_in_a_box.config import load_config
    from exec_in_a_box.credentials import get_api_key
    from exec_in_a_box.slack import get_webhook_url

    config = load_config()
    if config is None:
        print("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    api_key = get_api_key(config.provider_name)
    key_status = "configured" if api_key else "not set"
    webhook = get_webhook_url()
    slack_status = "configured" if webhook else "not set"

    print()
    print("Current configuration:")
    print()
    print(f"  Archetype:  {config.archetype_name}")
    print(f"  Provider:   {config.provider_name}")
    print(f"  API key:    {key_status}")
    print(f"  Autonomy:   Level {config.autonomy_level}")
    print(f"  Slack:      {slack_status}")
    print()
    print("Change with:")
    print("  exec-in-a-box config archetype")
    print("  exec-in-a-box config provider")
    print("  exec-in-a-box config autonomy")
    print("  exec-in-a-box slack setup")


def cmd_config_archetype() -> None:
    import re

    from exec_in_a_box import storage
    from exec_in_a_box.archetypes import list_archetypes
    from exec_in_a_box.config import load_config

    config = load_config()
    if config is None:
        print("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    archetypes = list_archetypes()
    print()
    print(f"Current archetype: {config.archetype_name}")
    print()
    for i, a in enumerate(archetypes, 1):
        marker = (
            " (current)" if a.slug == config.archetype_slug else ""
        )
        print(f"  {i}. {a.name} — {a.one_line}{marker}")
    print()

    raw = input(
        f"Pick [1-{len(archetypes)}] "
        "(or Enter to keep current): "
    ).strip()
    if not raw:
        print("No change.")
        return

    try:
        idx = int(raw) - 1
        if not (0 <= idx < len(archetypes)):
            raise ValueError()
    except ValueError:
        print(
            "Please enter a number between "
            f"1 and {len(archetypes)}."
        )
        return

    chosen = archetypes[idx]
    if chosen.slug == config.archetype_slug:
        print("No change.")
        return

    text = storage.read_file("board/config.md")
    text = re.sub(
        r"^slug:.*$",
        f"slug: {chosen.slug}",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"^name:.*$",
        f"name: {chosen.name}",
        text,
        flags=re.MULTILINE,
    )
    storage.write_file("board/config.md", text)
    print(f"Archetype changed to {chosen.name}.")


def cmd_config_provider() -> None:
    import re

    from exec_in_a_box import storage
    from exec_in_a_box.config import load_config
    from exec_in_a_box.credentials import store_api_key
    from exec_in_a_box.providers import (
        ProviderError,
        create_provider,
    )

    config = load_config()
    if config is None:
        print("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    providers = ["anthropic", "openai"]
    print()
    print(f"Current provider: {config.provider_name}")
    print()
    for i, p in enumerate(providers, 1):
        marker = " (current)" if p == config.provider_name else ""
        print(f"  {i}. {p}{marker}")
    print()

    raw = input(
        "Pick [1-2] (or Enter to keep current): "
    ).strip()
    if not raw:
        print("No change.")
        return

    try:
        idx = int(raw) - 1
        if not (0 <= idx < len(providers)):
            raise ValueError()
    except ValueError:
        print("Please enter 1 or 2.")
        return

    new_provider = providers[idx]

    print()
    print(f"Enter your API key for {new_provider}:")
    api_key = input("API key: ").strip()
    if not api_key:
        print("No key entered. Cancelled.")
        return

    print(
        f"Testing connection to {new_provider}...",
        end=" ",
        flush=True,
    )
    try:
        provider = create_provider(new_provider, api_key=api_key)
        provider.test_connection()
        print("Connected.")
    except ProviderError as e:
        print("Failed.")
        print(f"  {e.user_message}")
        return

    store_api_key(new_provider, api_key)

    text = storage.read_file("board/config.md")
    text = re.sub(
        r"^provider:.*$",
        f"provider: {new_provider}",
        text,
        flags=re.MULTILINE,
    )
    storage.write_file("board/config.md", text)
    print(f"Provider changed to {new_provider}.")


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


def cmd_web(host: str, port: int, dev: bool) -> None:
    """Start the FastAPI server (and optionally Vite in dev mode)."""
    import subprocess
    import threading
    import uvicorn

    from exec_in_a_box import storage
    from exec_in_a_box.setup import run_setup

    if not storage.is_initialized():
        print("Welcome to Executive in a Box!")
        print("Let's get you set up first.")
        run_setup()
        print()

    if dev:
        # Start Vite in a background thread
        import shutil
        from pathlib import Path

        web_dir = Path(__file__).parent
        for _ in range(5):
            if (web_dir / "web" / "package.json").exists():
                break
            web_dir = web_dir.parent

        vite_dir = web_dir / "web"
        npm = shutil.which("npm")

        if npm and vite_dir.exists():
            def _run_vite():
                subprocess.run(
                    [npm, "run", "dev"],
                    cwd=str(vite_dir),
                )

            vite_thread = threading.Thread(target=_run_vite, daemon=True)
            vite_thread.start()
            print(f"  Vite dev server: http://localhost:5173")
        else:
            print(
                "  [!] Vite not started — web/ directory or npm not found. "
                "Run: cd web && npm install"
            )

    print(f"  API server:      http://{host}:{port}")
    print()

    from exec_in_a_box.server.app import create_app

    application = create_app(serve_static=not dev)
    uvicorn.run(application, host=host, port=port, log_level="warning")


def cmd_artifacts_list() -> None:
    from exec_in_a_box import storage
    from exec_in_a_box.cli_display import C, colorize

    base = storage.get_data_dir() / "artifacts"
    if not base.exists() or not any(base.iterdir()):
        print(colorize("  No artifacts yet.", C.DIM))
        return

    print()
    print(colorize("  Artifacts:", C.CYAN))
    print()
    for session_dir in sorted(base.iterdir(), reverse=True):
        if not session_dir.is_dir():
            continue
        for f in sorted(session_dir.iterdir()):
            if f.is_file():
                size = f.stat().st_size
                size_str = f"{size}B" if size < 1024 else f"{size // 1024}KB"
                print(
                    colorize(f"  {session_dir.name}/{f.name}", C.WHITE)
                    + colorize(f"  ({size_str})", C.DIM)
                )
    print()


def cmd_artifacts_open(artifact_id: str) -> None:
    from exec_in_a_box import storage
    from exec_in_a_box.cli_display import print_error

    parts = artifact_id.strip("/").split("/")
    if len(parts) != 2:
        print_error('Artifact ID must be "session-id/filename". Run: exec-in-a-box artifacts list')
        sys.exit(1)

    session_id, filename = parts
    path = storage.get_data_dir() / "artifacts" / session_id / filename
    if not path.exists():
        print_error(f"Artifact not found: {artifact_id}")
        sys.exit(1)

    print(path.read_text(encoding="utf-8"))


def cmd_stats() -> None:
    from exec_in_a_box.archetypes import TRAIT_LABELS, list_archetypes
    from exec_in_a_box.cli_display import C, colorize, divider
    from exec_in_a_box.jobs import list_jobs
    from exec_in_a_box.stats import get_ceo_stats

    archetypes = list_archetypes()
    ceo_stats, total_sessions = get_ceo_stats()
    jobs = list_jobs()

    # Index session stats by slug for easy lookup
    stats_by_slug = {s["slug"]: s for s in ceo_stats}

    print()
    print(colorize("  Stats", C.BOLD, C.CYAN))
    print(divider())

    BAR_W = 20
    CEO_COLORS = {
        "operator":  C.CYAN,
        "visionary": C.MAGENTA,
        "advocate":  C.LIME,
        "analyst":   C.YELLOW,
    }

    # ── General usage ───────────────────────────────────────────────────────
    print()
    print(colorize("  General Usage", C.BOLD))
    print()

    if total_sessions == 0:
        print(colorize("  No sessions yet.", C.DIM))
    else:
        print(colorize(f"  Total sessions: {total_sessions}", C.DIM))
        print()
        # Usage share bar per CEO
        for arch in archetypes:
            s = stats_by_slug.get(arch.slug, {})
            total = s.get("total", 0)
            share = total / total_sessions if total_sessions else 0
            filled = round(share * BAR_W)
            bar = "█" * filled + "░" * (BAR_W - filled)
            pct = f"{round(share * 100):>3}%"
            color = CEO_COLORS.get(arch.slug, C.WHITE)
            short = arch.name.replace("The ", "")
            print(
                colorize(f"    {short:<10}", color)
                + colorize(bar, color)
                + colorize(f" {pct}  ({total} sessions)", C.DIM)
            )

    if jobs:
        total_jobs = len(jobs)
        complete = sum(1 for j in jobs if j["status"] == "complete")
        failed = sum(1 for j in jobs if j["status"] == "failed")
        print()
        print(
            colorize(f"  Executize jobs: {total_jobs}", C.DIM)
            + colorize(f"  ✓ {complete}", C.LIME)
            + (colorize(f"  ✗ {failed}", C.MAGENTA) if failed else "")
        )

    # ── Per-CEO blocks ──────────────────────────────────────────────────────
    print()
    print(colorize("  CEO Profiles", C.BOLD))

    for arch in archetypes:
        color = CEO_COLORS.get(arch.slug, C.WHITE)
        s = stats_by_slug.get(arch.slug, {})
        total = s.get("total", 0)

        print()
        print(colorize(f"  {arch.name}", C.BOLD, color))
        print(colorize(f"  {arch.one_line}", C.DIM))
        print()

        # Personality traits
        for trait in TRAIT_LABELS:
            score = arch.traits.get(trait, 0.0)
            filled = round(score * BAR_W)
            bar = "█" * filled + "░" * (BAR_W - filled)
            pct = f"{round(score * 100):>3}%"
            print(
                colorize(f"    {trait:<22}", C.DIM)
                + colorize(bar, color)
                + colorize(f" {pct}", C.DIM)
            )

        # Decision history (only if sessions exist for this CEO)
        if total > 0:
            adopted  = s.get("adopted", 0)
            modified = s.get("modified", 0)
            rejected = s.get("rejected", 0)
            agr_pct  = f"{s.get('agreement_rate', 0) * 100:.0f}%"
            print()
            print(
                colorize(f"    {total} sessions · ", C.DIM)
                + colorize(f"✓ {adopted} adopted", C.LIME)
                + colorize(f"  ~ {modified} modified", C.YELLOW)
                + colorize(f"  ✗ {rejected} rejected", C.MAGENTA)
                + colorize(f"  ({agr_pct} agreement)", C.DIM)
            )
            recent = s.get("recent_decisions", [])
            if recent:
                print()
                for rec in recent[:3]:
                    icon = {"Adopted": "✓", "Rejected": "✗", "Modified": "~"}.get(
                        rec["decision"], "?"
                    )
                    icon_color = {
                        "Adopted": C.LIME,
                        "Rejected": C.MAGENTA,
                        "Modified": C.YELLOW,
                    }.get(rec["decision"], C.DIM)
                    print(
                        colorize(f"    {icon} ", icon_color)
                        + colorize(rec["question"][:55], C.DIM)
                    )
        else:
            print()
            print(colorize("    No sessions yet.", C.DIM))

    print()


def cmd_all_hands(items: list[str]) -> None:
    from exec_in_a_box.all_hands import (
        build_agenda,
        facilitate,
        gather_context,
        save_all_hands_log,
    )
    from exec_in_a_box.cli_display import C, colorize, divider, print_banner
    from exec_in_a_box.config import load_config
    from exec_in_a_box.credentials import get_api_key

    config = load_config()
    if config is None:
        print("No configuration found. Run: exec-in-a-box setup")
        sys.exit(1)

    api_key = get_api_key(config.provider_name)
    if api_key is None:
        print(f"No API key for {config.provider_name}. Run: exec-in-a-box setup")
        sys.exit(1)

    print_banner()
    print(colorize("  All-Hands Meeting Facilitation", C.BOLD, C.CYAN))
    print(divider())
    print()

    # Gather agenda items
    agenda_items = list(items)
    if not agenda_items:
        print(colorize("  Enter agenda items (one per line, empty line to finish):", C.DIM))
        print()
        while True:
            try:
                line = input(colorize("  Item: ", C.CYAN)).strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                break
            agenda_items.append(line)

    if not agenda_items:
        print(colorize("  No agenda items. Exiting.", C.DIM))
        return

    print()
    print(colorize(f"  {len(agenda_items)} agenda item(s). Gathering context...", C.DIM))
    org_context = gather_context()
    agenda = build_agenda(agenda_items, org_context)

    print(colorize("  Facilitating — all archetypes deliberating in parallel...", C.CYAN))
    print()

    result = facilitate(agenda, config.provider_name, api_key)

    print(colorize("  ─── Meeting Summary ───", C.CYAN))
    print()
    print(result.summary)

    if result.decisions:
        print()
        print(colorize("  ─── Tentative Decisions ───", C.LIME))
        for d in result.decisions:
            print(colorize(f"    • ", C.LIME) + d)

    print()
    try:
        save_choice = input(
            colorize("  Save summary and decisions to log? [Y/N]: ", C.DIM)
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        save_choice = "n"

    if save_choice in ("y", "yes"):
        save_all_hands_log(result)
        print(colorize("  Saved to sessions/all-hands.md and org/decisions.md.", C.LIME))
    print()


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
        elif args.config_command == "archetype":
            cmd_config_archetype()
        elif args.config_command == "provider":
            cmd_config_provider()
        elif args.config_command == "show":
            cmd_config_show()
        else:
            parser.parse_args(["config", "--help"])
        return

    if args.command == "test-connection":
        cmd_test_connection(args.provider)
        return

    if args.command == "history":
        cmd_history()
        return

    if args.command == "web":
        cmd_web(host=args.host, port=args.port, dev=False)
        return

    if args.command == "dev":
        cmd_web(host=args.host, port=args.port, dev=True)
        return

    if args.command == "slack":
        from exec_in_a_box.slack import run_slack_command

        run_slack_command(args.slack_args)
        return

    if args.command == "artifacts":
        if args.artifacts_command == "list":
            cmd_artifacts_list()
        elif args.artifacts_command == "open":
            cmd_artifacts_open(args.artifact_id)
        else:
            parser.parse_args(["artifacts", "--help"])
        return

    if args.command == "stats":
        cmd_stats()
        return

    if args.command == "all-hands":
        cmd_all_hands(args.items)
        return


if __name__ == "__main__":
    main()
