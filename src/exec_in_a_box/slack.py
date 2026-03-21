"""Slack webhook integration (outbound only).

Posts messages to a configured Slack channel via incoming webhook.
The webhook URL is stored in the OS keychain.

This is an external integration — it is opt-in, logged, and only
triggered by explicit user action.
"""

from __future__ import annotations

import json
import sys

import httpx
import keyring

SERVICE_NAME = "executive-in-a-box"
KEYRING_USER = "slack-webhook-url"


def get_webhook_url() -> str | None:
    """Retrieve the Slack webhook URL from the OS keychain."""
    try:
        return keyring.get_password(SERVICE_NAME, KEYRING_USER)
    except keyring.errors.KeyringError:
        return None


def store_webhook_url(url: str) -> None:
    """Store the Slack webhook URL in the OS keychain."""
    keyring.set_password(SERVICE_NAME, KEYRING_USER, url)


def send_message(message: str) -> bool:
    """Send a message to the configured Slack webhook.

    Returns True on success, False on failure (with error printed).
    """
    webhook_url = get_webhook_url()
    if webhook_url is None:
        print(
            "No Slack webhook configured. "
            "Run: exec-in-a-box slack setup"
        )
        return False

    try:
        response = httpx.post(
            webhook_url,
            json={"text": message},
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
    print("The URL looks like:")
    print("  https://hooks.slack.com/services/T.../B.../...")
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
            confirm = input("Use it anyway? [Y/N]: ").strip().lower()
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
        "Executive in a Box connected successfully."
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

    if args[0] == "--last":
        # Read the most recent session and extract the position
        from exec_in_a_box import storage

        sessions = storage.list_sessions()
        if not sessions:
            print("No sessions yet. Ask the CEO a question first.")
            sys.exit(1)

        content = sessions[0].read_text(encoding="utf-8")

        # Extract the position line from the session
        lines = content.splitlines()
        position = None
        for i, line in enumerate(lines):
            if line.startswith("**Position:**"):
                position = line.replace("**Position:**", "").strip()
                break

        if position is None:
            print(
                "Couldn't find a recommendation in the "
                "last session."
            )
            sys.exit(1)

        print(f"Sending to Slack: {position[:80]}...")
        if send_message(position):
            print("Sent!")
        return

    # Treat everything as the message
    message = " ".join(args)
    print(f"Sending to Slack: {message[:80]}...")
    if send_message(message):
        print("Sent!")
