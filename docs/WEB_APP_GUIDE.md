# Web App Guide

This guide walks you through starting the Executive in a Box web app and
using it for the first time. The web app runs on your own computer — nothing
is sent to a server. You access it through your browser at a local address.

If you get stuck at any step, that's a bug in this guide — please open an issue.

---

## Before you start

Complete the main [Setup Guide](SETUP_GUIDE.md) first. You'll need:
- Executive in a Box installed (`pip install executive-in-a-box`)
- At least one AI provider configured (API key set up)

---

## Starting the web app

In your terminal, run:

```
exec-in-a-box web
```

You should see something like:

```
Executive in a Box — web app running at http://localhost:8080
Press Ctrl+C to stop.
```

Open your browser and go to: **http://localhost:8080**

> **First time?** The setup wizard will open automatically. It takes about
> 5 minutes and walks you through everything.

---

## The three panes

The web app has three sections:

**Left — Artifacts**
Documents and files created during your sessions. Click any item to open it.
Files are saved to your machine at `~/.executive-in-a-box/artifacts/`.

**Center — Chat**
This is where you talk to your executive board. At the top you'll see a portrait
for each CEO you've configured. Click a portrait to switch to that CEO's conversation.
Each CEO has their own chat history.

**Right — Whiteboard**
By default, shows your AI provider usage and costs — how many tokens you've used,
estimated cost, and how close you are to any limits. This pane will gain more views
over time (charts, analysis views).

---

## Talking to your CEO

Type your question in the input bar at the bottom of the center pane and press Enter.

Responses stream in as they're generated — you'll see the text appear in real time
rather than waiting for the whole response to finish.

**For complex questions that take longer:** click the **Executize** button instead of
pressing Enter. This sends the CEO off to think in the background. While they're
working, you can switch to another CEO and keep chatting. You'll get a notification
when they're back.

---

## Switching between CEOs

Click any CEO portrait in the strip at the top of the chat pane. Each CEO has their
own separate conversation history. A CEO shown as faded with a verb below their
portrait (like "Strategizing...") is currently working on a deep task for you.

---

## Posting to Slack

Click **Announce** to open the Slack compose window. Type your message on the left,
see a preview of how it'll look in Slack on the right, then click **Post** to send.

You need to have Slack configured first — see the [Slack Guide](SLACK_GUIDE.md).

---

## Changing your CEO's autonomy level

Below each CEO portrait, you'll see four numbered buttons (1–2–3–4). These control
how much you want that CEO to act on its own vs. checking with you first.
Hover over each button to see what it means. See the [Autonomy Guide](AUTONOMY_GUIDE.md)
for a full explanation.

---

## Stopping the web app

Go back to your terminal and press **Ctrl+C**. Your data is saved automatically —
nothing is lost when you stop the app.

---

## Changing the port

If port 8080 is already in use on your machine, you can change it:

```
exec-in-a-box web --port 9000
```

Then open http://localhost:9000 in your browser.
