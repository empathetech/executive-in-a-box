"""Slack webhook integration — supports multiple workspaces and channels.

Webhooks are stored in ~/.executive-in-a-box/integrations/slack.json.
Each entry: {id, workspace, channel, webhook_url}.
"""
from __future__ import annotations

import sys
import uuid

import httpx
import keyring

from exec_in_a_box import storage

WEBHOOKS_FILE = "integrations/slack.json"
SERVICE_NAME = "executive-in-a-box"
OLD_KEYRING_USER = "slack-webhook-url"

ICON_BASE = "https://raw.githubusercontent.com/empathetech/executive-in-a-box/main/assets"
ARCHETYPE_ICONS = {
    "operator": f"{ICON_BASE}/ceo-operator.png",
    "visionary": f"{ICON_BASE}/ceo-visionary.png",
    "advocate": f"{ICON_BASE}/ceo-advocate.png",
    "analyst": f"{ICON_BASE}/ceo-analyst.png",
}


def _migrate_keychain() -> None:
    """Migrate old single-webhook keychain entry to the new file format."""
    try:
        old_url = keyring.get_password(SERVICE_NAME, OLD_KEYRING_USER)
        if old_url and storage.read_file(WEBHOOKS_FILE) is None:
            entry = {
                "id": uuid.uuid4().hex[:8],
                "workspace": "Empathetech",
                "channel": "#general",
                "webhook_url": old_url,
            }
            import json
            storage.write_file(WEBHOOKS_FILE, json.dumps([entry], indent=2) + "\n")
            keyring.delete_password(SERVICE_NAME, OLD_KEYRING_USER)
    except Exception:
        pass


def list_webhooks() -> list[dict]:
    """Read all configured webhooks. Runs migration on first call."""
    import json

    raw = storage.read_file(WEBHOOKS_FILE)
    if raw is None:
        _migrate_keychain()
        raw = storage.read_file(WEBHOOKS_FILE)
        if raw is None:
            return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return []


def get_webhook(webhook_id: str) -> dict | None:
    """Find a webhook entry by id."""
    for w in list_webhooks():
        if w.get("id") == webhook_id:
            return w
    return None


def add_webhook(workspace: str, channel: str, url: str) -> dict:
    """Add a new webhook entry and save. Returns the new entry."""
    import json

    entry: dict = {
        "id": uuid.uuid4().hex[:8],
        "workspace": workspace,
        "channel": channel,
        "webhook_url": url,
    }
    webhooks = list_webhooks()
    webhooks.append(entry)
    storage.write_file(WEBHOOKS_FILE, json.dumps(webhooks, indent=2) + "\n")
    return entry


def remove_webhook(webhook_id: str) -> bool:
    """Remove a webhook by id. Returns True if found and removed."""
    import json

    webhooks = list_webhooks()
    updated = [w for w in webhooks if w.get("id") != webhook_id]
    if len(updated) == len(webhooks):
        return False
    storage.write_file(WEBHOOKS_FILE, json.dumps(updated, indent=2) + "\n")
    return True


def send_message(
    message: str,
    webhook_id: str | None = None,
    archetype_slug: str | None = None,
    archetype_name: str | None = None,
) -> bool:
    """Send a message to a Slack webhook.

    If webhook_id is provided, look up that entry. Otherwise fall back to the
    first webhook in the list.

    Returns True on success, False on failure.
    """
    if webhook_id is not None:
        entry = get_webhook(webhook_id)
    else:
        webhooks = list_webhooks()
        entry = webhooks[0] if webhooks else None

    if entry is None:
        print("No Slack webhook configured. Run: exec-in-a-box slack setup")
        return False

    webhook_url = entry["webhook_url"]
    payload: dict = {"text": message}

    if archetype_slug and archetype_slug in ARCHETYPE_ICONS:
        payload["icon_url"] = ARCHETYPE_ICONS[archetype_slug]
    if archetype_name:
        payload["username"] = archetype_name

    try:
        response = httpx.post(webhook_url, json=payload, timeout=10.0)
        if response.status_code == 200 and response.text == "ok":
            return True
        print(f"Slack returned an error: {response.status_code} — {response.text}")
        return False
    except httpx.TimeoutException:
        print("Slack request timed out. Try again.")
        return False
    except httpx.RequestError:
        print("Couldn't reach Slack. Check your internet connection.")
        return False


def run_slack_setup() -> None:
    """Interactive management interface for Slack webhooks."""
    print()
    print("=" * 50)
    print("  Slack Webhook Management")
    print("=" * 50)

    while True:
        print()
        webhooks = list_webhooks()

        if webhooks:
            print("  Configured webhooks:")
            print()
            for i, w in enumerate(webhooks, 1):
                print(f"  {i}. {w.get('workspace', '?')} / {w.get('channel', '?')}")
            print()
        else:
            print("  No webhooks configured yet.")
            print()

        print("  [A]dd new   [R]emove   [T]est   [D]one")
        print()

        try:
            choice = input("  Pick: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Cancelled.")
            return

        if choice in ("d", "done", ""):
            print()
            return

        elif choice in ("a", "add"):
            # Add flow
            print()
            try:
                workspace = input("  Workspace name (e.g. Acme Corp): ").strip()
                if not workspace:
                    print("  Cancelled.")
                    continue
                channel = input("  Channel (e.g. #general): ").strip()
                if not channel:
                    print("  Cancelled.")
                    continue
                url = input("  Webhook URL: ").strip()
                if not url:
                    print("  Cancelled.")
                    continue
            except (EOFError, KeyboardInterrupt):
                print("\n  Cancelled.")
                continue

            if not url.startswith("https://hooks.slack.com/"):
                print()
                print("  That doesn't look like a Slack webhook URL.")
                try:
                    confirm = input("  Use it anyway? [Y/N]: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n  Cancelled.")
                    continue
                if confirm not in ("y", "yes"):
                    print("  Cancelled.")
                    continue

            # Test it
            print()
            print("  Testing webhook...", end=" ", flush=True)
            entry = {"id": "test", "workspace": workspace, "channel": channel, "webhook_url": url}
            payload: dict = {
                "text": "Executive in a Box connected successfully.",
                "username": "The Operator",
                "icon_url": ARCHETYPE_ICONS["operator"],
            }
            try:
                import httpx as _httpx
                resp = _httpx.post(url, json=payload, timeout=10.0)
                ok = resp.status_code == 200 and resp.text == "ok"
            except Exception:
                ok = False

            if ok:
                print("OK!")
                new_entry = add_webhook(workspace, channel, url)
                print(f"  Saved (id: {new_entry['id']})")
            else:
                print("Failed.")
                try:
                    save_anyway = input("  Save anyway? [Y/N]: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n  Cancelled.")
                    continue
                if save_anyway in ("y", "yes"):
                    new_entry = add_webhook(workspace, channel, url)
                    print(f"  Saved (id: {new_entry['id']})")
                else:
                    print("  Cancelled.")

        elif choice in ("r", "remove"):
            if not webhooks:
                print("  Nothing to remove.")
                continue
            print()
            for i, w in enumerate(webhooks, 1):
                print(f"  {i}. {w.get('workspace', '?')} / {w.get('channel', '?')}")
            print()
            try:
                raw = input(f"  Pick [1-{len(webhooks)}] to remove: ").strip()
                idx = int(raw) - 1
                if not (0 <= idx < len(webhooks)):
                    raise ValueError
            except (ValueError, EOFError, KeyboardInterrupt):
                print("  Invalid choice. Cancelled.")
                continue
            removed = remove_webhook(webhooks[idx]["id"])
            if removed:
                print(f"  Removed {webhooks[idx].get('workspace', '?')} / {webhooks[idx].get('channel', '?')}")

        elif choice in ("t", "test"):
            if not webhooks:
                print("  No webhooks to test.")
                continue
            print()
            for i, w in enumerate(webhooks, 1):
                print(f"  {i}. {w.get('workspace', '?')} / {w.get('channel', '?')}")
            print()
            try:
                raw = input(f"  Pick [1-{len(webhooks)}] to test: ").strip()
                idx = int(raw) - 1
                if not (0 <= idx < len(webhooks)):
                    raise ValueError
            except (ValueError, EOFError, KeyboardInterrupt):
                print("  Invalid choice. Cancelled.")
                continue
            print()
            print("  Sending test message...", end=" ", flush=True)
            ok = send_message(
                "Executive in a Box test message.",
                webhook_id=webhooks[idx]["id"],
                archetype_slug="operator",
                archetype_name="The Operator",
            )
            if ok:
                print("Sent!")
            else:
                print("Failed.")
        else:
            print("  Unknown option.")


def run_slack_command(args: list[str]) -> None:
    """Handle the slack subcommand."""
    if not args or args[0] == "setup":
        run_slack_setup()
        return

    # Interactive announce flow
    webhooks = list_webhooks()
    if not webhooks:
        print("No Slack webhooks configured. Run: exec-in-a-box slack setup add")
        sys.exit(1)

    from exec_in_a_box.archetypes import list_archetypes
    from exec_in_a_box import storage as _storage

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

        # ── Step 2: Pick webhook (workspace / channel) ────────────────────
        print()
        print("  Which channel?")
        print()

        # Group by workspace
        workspaces: dict[str, list[dict]] = {}
        for w in webhooks:
            ws = w.get("workspace", "?")
            workspaces.setdefault(ws, []).append(w)

        flat: list[dict] = []
        for ws, channels in workspaces.items():
            for ch in channels:
                flat.append(ch)
                print(f"  {len(flat)}. {ws} / {ch.get('channel', '?')}")
        print()

        raw = input(f"  Pick [1-{len(flat)}]: ").strip()
        try:
            widx = int(raw) - 1
            if not (0 <= widx < len(flat)):
                raise ValueError
        except ValueError:
            print("  Invalid choice. Cancelled.")
            return
        chosen_webhook = flat[widx]

        # ── Step 3: Compose message ───────────────────────────────────────
        import re as _re

        # Gather <announce> blocks from last session if available
        index = _storage.read_session_index()
        last_record = index[-1] if index else None
        last_blocks: list[str] = []
        if last_record and last_record.get("position"):
            raw_pos = last_record["position"]
            found = [m.strip() for m in _re.findall(
                r"<announce>([\s\S]*?)<\/announce>", raw_pos, _re.IGNORECASE
            )]
            last_blocks = found if found else [raw_pos]

        def _pick_message() -> str | None:
            print()
            print("  What do you want to send?")
            print()
            options: list[str] = []
            if last_blocks:
                for i, block in enumerate(last_blocks, 1):
                    preview = block[:60].replace("\n", " ")
                    if len(block) > 60:
                        preview += "…"
                    label = f"Announcement {i}" if len(last_blocks) > 1 else "Last session's position"
                    options.append(block)
                    print(f"  {len(options)}. {label}: \"{preview}\"")
            n = len(options)
            print(f"  {n + 1}. Write a message")
            print(f"  {n + 2}. Cancel")
            print()
            raw = input(f"  Pick [1-{n + 2}]: ").strip()
            try:
                idx = int(raw)
            except ValueError:
                return None
            if idx == n + 2:
                return None
            if idx == n + 1:
                print()
                msg = input("  Message: ").strip()
                return msg if msg else None
            if 1 <= idx <= n:
                return options[idx - 1]
            return None

        def _preview_and_confirm(message: str) -> str | None:
            """Preview loop. Returns message to send or None to cancel."""
            sep = "─" * (len(archetype.name) + 16)
            while True:
                print()
                print(f"  ─── Preview ({archetype.name}) ───")
                for line in message.splitlines():
                    print(f"  {line}")
                print(f"  {sep}")
                print()

                prompt = "  Send to Slack? [S]end / [E]dit"
                if len(last_blocks) > 1:
                    prompt += " / [P]ick another"
                prompt += " / [C]ancel: "
                confirm = input(prompt).strip().lower()

                if confirm in ("s", "send", "y", "yes"):
                    return message
                if confirm in ("e", "edit"):
                    print()
                    edited = input("  Edit message: ").strip()
                    if edited:
                        message = edited
                    continue
                if len(last_blocks) > 1 and confirm in ("p", "pick"):
                    return "PICK_AGAIN"
                return None

        # Main loop
        while True:
            message = _pick_message()
            if message is None:
                print("  Cancelled.")
                return

            result = _preview_and_confirm(message)
            if result == "PICK_AGAIN":
                continue
            if result is None:
                print("  Cancelled.")
                return

            # ── Step 5: Send ─────────────────────────────────────────────
            print()
            print("  Sending...", end=" ", flush=True)
            success = send_message(
                result,
                webhook_id=chosen_webhook["id"],
                archetype_slug=archetype.slug,
                archetype_name=archetype.name,
            )
            if success:
                print("Sent!")
            print()
            return

    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return
