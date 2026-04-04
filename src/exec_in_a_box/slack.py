"""Slack webhook integration (outbound only).

Posts messages to a configured Slack channel via incoming webhook.
The webhook URL is stored in the OS keychain.

This is an external integration — it is opt-in, logged, and only
triggered by explicit user action.
"""

from __future__ import annotations

import sys

import httpx
import keyring

SERVICE_NAME = "executive-in-a-box"
KEYRING_USER = "slack-webhook-url"

# GitHub raw URL base for archetype profile pics.
# Slack webhooks support icon_url for custom avatars.
ICON_BASE = (
    "https://raw.githubusercontent.com/"
    "empathetech/executive-in-a-box/main/assets"
)

ARCHETYPE_ICONS = {
    "operator": f"{ICON_BASE}/ceo-operator.png",
    "visionary": f"{ICON_BASE}/ceo-visionary.png",
    "advocate": f"{ICON_BASE}/ceo-advocate.png",
    "analyst": f"{ICON_BASE}/ceo-analyst.png",
}


def get_webhook_url() -> str | None:
    """Retrieve the Slack webhook URL from the OS keychain."""
    try:
        return keyring.get_password(SERVICE_NAME, KEYRING_USER)
    except keyring.errors.KeyringError:
        return None


def store_webhook_url(url: str) -> None:
    """Store the Slack webhook URL in the OS keychain."""
    keyring.set_password(SERVICE_NAME, KEYRING_USER, url)


def send_message(
    message: str,
    archetype_slug: str | None = None,
    archetype_name: str | None = None,
) -> bool:
    """Send a message to the configured Slack webhook.

    If archetype_slug is provided, the message is posted with
    the archetype's profile pic and display name.

    Returns True on success, False on failure (with error printed).
    """
    webhook_url = get_webhook_url()
    if webhook_url is None:
        print(
            "No Slack webhook configured. "
            "Run: exec-in-a-box slack setup"
        )
        return False

    payload: dict = {"text": message}

    # Set archetype avatar and name if available
    if archetype_slug and archetype_slug in ARCHETYPE_ICONS:
        payload["icon_url"] = ARCHETYPE_ICONS[archetype_slug]
    if archetype_name:
        payload["username"] = archetype_name

    try:
        response = httpx.post(
            webhook_url,
            json=payload,
            timeout=10.0,
        )
        if response.status_code == 200 and response.text == "ok":
            return True
        else:
            print(
                f"Slack returned an error: "
                f"{response.status_code} — {response.text}"
            )
            return False
    except httpx.TimeoutException:
        print("Slack request timed out. Try again.")
        return False
    except httpx.RequestError:
        print(
            "Couldn't reach Slack. "
            "Check your internet connection."
        )
        return False


def run_slack_setup() -> None:
    """Interactive setup for the Slack webhook."""
    print()
    print("=" * 50)
    print("  Slack Webhook Setup")
    print("=" * 50)
    print()
    print("To post messages to Slack, you need an")
    print("Incoming Webhook URL. Here's how to get one:")
    print()
    print("  1. Go to https://api.slack.com/apps")
    print("  2. Create a new app (or use an existing one)")
    print("  3. Go to Incoming Webhooks and enable them")
    print("  4. Click 'Add New Webhook to Workspace'")
    print("  5. Pick the channel you want to post to")
    print("  6. Copy the webhook URL")
    print()
    print("It will be stored securely in your OS keychain.")
    print()

    try:
        url = input("Webhook URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nSetup cancelled.")
        return

    if not url:
        print("No URL entered. Setup cancelled.")
        return

    if not url.startswith("https://hooks.slack.com/"):
        print()
        print(
            "That doesn't look like a Slack webhook URL. "
            "It should start with "
            "https://hooks.slack.com/services/"
        )
        try:
            confirm = (
                input("Use it anyway? [Y/N]: ").strip().lower()
            )
        except (EOFError, KeyboardInterrupt):
            print("\nSetup cancelled.")
            return
        if confirm not in ("y", "yes"):
            print("Setup cancelled.")
            return

    store_webhook_url(url)

    # Test it
    print()
    print("Testing webhook...", end=" ", flush=True)
    success = send_message(
        "Executive in a Box connected successfully.",
        archetype_slug="operator",
        archetype_name="The Operator",
    )
    if success:
        print("Message sent!")
        print()
        print("Setup complete. Use these commands:")
        print('  exec-in-a-box slack "your message"')
        print("  exec-in-a-box slack --last")
    else:
        print()
        print(
            "The webhook URL was saved but the test "
            "message failed. Check the URL and try again."
        )


def run_slack_command(args: list[str]) -> None:
    """Handle the slack subcommand."""
    if not args or args[0] == "setup":
        run_slack_setup()
        return

    # Verify webhook is configured before going further
    if get_webhook_url() is None:
        print("No Slack webhook configured. Run: exec-in-a-box slack setup")
        sys.exit(1)

    from exec_in_a_box.archetypes import list_archetypes
    from exec_in_a_box import storage

    try:
        # ── Step 1: Pick archetype ────────────────────────────────────────
        archetypes = list_archetypes()
        print()
        print("  Who's sending this?")
        print()
        for i, a in enumerate(archetypes, 1):
            print(f"  {i}. {a.name} — {a.one_line}")
        print()

        raw = input(f"  Pick [1-{len(archetypes)}]: ").strip()
        try:
            idx = int(raw) - 1
            if not (0 <= idx < len(archetypes)):
                raise ValueError
        except ValueError:
            print("  Invalid choice. Cancelled.")
            return
        archetype = archetypes[idx]

        # ── Step 2: Compose message ───────────────────────────────────────
        print()
        print("  What do you want to send?")
        print()
        print("  1. Write a message")

        sessions = storage.list_sessions()
        has_last = bool(sessions)
        if has_last:
            print("  2. Use last session's recommendation")
            print("  3. Cancel")
        else:
            print("  2. Cancel")
        print()

        choice = input("  Pick: ").strip()

        if choice == "1":
            print()
            message = input("  Message: ").strip()
            if not message:
                print("  Empty message. Cancelled.")
                return
        elif choice == "2" and has_last:
            content = sessions[0].read_text(encoding="utf-8")
            message = None
            for line in content.splitlines():
                if line.startswith("**Position:**"):
                    message = line.replace("**Position:**", "").strip()
                    break
            if not message:
                print("  Couldn't find a recommendation in the last session. Cancelled.")
                return
        else:
            print("  Cancelled.")
            return

        # ── Step 3: Preview ───────────────────────────────────────────────
        print()
        print(f"  ─── Preview ({archetype.name}) ───")
        print(f"  {message}")
        print("  " + "─" * (len(archetype.name) + 16))
        print()

        confirm = input("  Send to Slack? [Y]es / [E]dit / [C]ancel: ").strip().lower()

        if confirm in ("e", "edit"):
            print()
            message = input("  Corrected message: ").strip()
            if not message:
                print("  Empty message. Cancelled.")
                return
            print()
            print(f"  ─── Preview ({archetype.name}) ───")
            print(f"  {message}")
            print("  " + "─" * (len(archetype.name) + 16))
            print()
            confirm = input("  Send to Slack? [Y/N]: ").strip().lower()

        if confirm not in ("y", "yes"):
            print("  Cancelled.")
            return

        # ── Step 4: Send ──────────────────────────────────────────────────
        print()
        print("  Sending...", end=" ", flush=True)
        success = send_message(
            message,
            archetype_slug=archetype.slug,
            archetype_name=archetype.name,
        )
        if success:
            print("Sent!")
        print()

    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return
