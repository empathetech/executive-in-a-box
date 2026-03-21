# Slack Integration Guide

Executive in a Box can post messages to a Slack channel using a webhook.
This is one-way: the tool sends messages to Slack, but it doesn't receive
messages from Slack (that's coming in V1).

---

## What you'll need

1. A Slack workspace you have admin access to (or permission to add apps)
2. About 5 minutes

---

## Step 1: Create a Slack app and webhook

1. Go to **https://api.slack.com/apps**
2. Click **Create New App**
3. Choose **From scratch**
4. Name it something like "Executive in a Box" and select your workspace
5. In the left sidebar, click **Incoming Webhooks**
6. Toggle **Activate Incoming Webhooks** to On
7. Click **Add New Webhook to Workspace**
8. Pick the channel you want the CEO to post to (e.g., `#general` or
   `#ceo-updates`)
9. Click **Allow**
10. You'll see a webhook URL. It starts with
    `https://hooks.slack.com/services/` followed by a series of
    letters and numbers. Copy this URL.

---

## Step 2: Configure the tool

Run:
```bash
exec-in-a-box slack setup
```

Paste your webhook URL when prompted. The URL is stored securely in your
OS keychain (same as your API keys — never in a plaintext file).

The tool will send a test message to your channel to confirm it works.

---

## Step 3: Send messages

**Send a custom message:**
```bash
exec-in-a-box slack "We're prioritizing bug fixes this sprint based on user feedback."
```

**Send the last CEO recommendation:**
```bash
exec-in-a-box slack --last
```
This grabs the recommendation from your most recent board session and
posts it to Slack.

---

## How your webhook URL is protected

- Stored in your OS keychain (macOS Keychain, Windows Credential Locker,
  Linux Secret Service) — encrypted at rest
- Never stored in a plaintext file
- Never logged to session transcripts or debug files
- Only used when you explicitly run `exec-in-a-box slack`

---

## Changing or removing the webhook

**Change it:** Run `exec-in-a-box slack setup` again. The new URL replaces
the old one.

**Remove it:** Find "executive-in-a-box" in your OS keychain manager and
delete the "slack-webhook-url" entry.

---

## Tips

- Create a dedicated channel like `#ceo-updates` for the tool's messages,
  so they don't get lost in general conversation
- The tool only posts when you tell it to — it will never post automatically
  (not even at higher autonomy levels in V1)
- Webhook messages appear as the app name you chose in Step 1. You can
  customize the icon and name in Slack's app settings.
