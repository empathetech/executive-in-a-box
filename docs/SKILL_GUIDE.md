# Claude Skill Guide

This guide explains how to install and use the Executive in a Box Claude Code skill —
a slash command (`/exec-in-a-box`) you can use directly inside Claude Code without
switching to the web app or terminal.

---

## Before you start

You'll need:
- **Claude Code** installed. Download it at https://claude.ai/code or install via npm:
  ```
  npm install -g @anthropic-ai/claude-code
  ```
- **Executive in a Box** installed and configured. Complete the [Setup Guide](SETUP_GUIDE.md)
  first — the skill reads the config you set up there.

---

## Installing the skill

In your terminal, run:

```
exec-in-a-box install-skill
```

This installs the `/exec-in-a-box` command into Claude Code. You only need to do
this once.

To verify it worked, open Claude Code and type `/exec-in-a-box help`. You should
see a short usage summary.

---

## Basic usage

Ask your CEO a question:

```
/exec-in-a-box "Should we prioritize the payments feature or the onboarding flow?"
```

The active CEO responds in the Claude Code chat. By default, this uses whichever
CEO you last configured.

---

## Switching CEOs

```
/exec-in-a-box --ceo operator "What's the most realistic path to launch?"
/exec-in-a-box --ceo visionary "Where should we be in 3 years?"
/exec-in-a-box --ceo analyst "What data do we need before committing to this?"
```

Each CEO has their own separate conversation history in the skill session.

---

## Deep work (Executize)

For questions that need more time and depth:

```
/exec-in-a-box --executize "Write a full strategic brief on our pricing model"
```

The skill returns immediately with a job ID. While that CEO is working, you can
keep using Claude Code and chat with other CEOs. When the job finishes, you'll
see a completion message. Check the result with:

```
/exec-in-a-box status <job-id>
```

---

## Posting to Slack

Send the last CEO recommendation to your Slack channel:

```
/exec-in-a-box slack --last
```

Or send a custom message:

```
/exec-in-a-box slack "We've decided to push the launch by two weeks. Here's why..."
```

Requires Slack to be configured — see the [Slack Guide](SLACK_GUIDE.md).

---

## Viewing artifacts

List files created during your sessions:

```
/exec-in-a-box artifacts list
```

Open a specific artifact (prints to the Claude Code chat):

```
/exec-in-a-box artifacts <artifact-id>
```

---

## Checking usage and cost

```
/exec-in-a-box usage
```

Shows token usage and estimated cost per provider.

---

## Getting help

```
/exec-in-a-box help
/exec-in-a-box help --ceo
/exec-in-a-box help --executize
```
