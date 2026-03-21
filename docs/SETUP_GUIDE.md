# Setup Guide

This guide walks you through installing Executive in a Box and running your
first board session. It assumes you've never used a tool like this before.
If you get stuck at any step, that's a bug in this guide — please open an
issue.

---

## Before you start

You'll need three things:

1. **A computer running macOS, Linux, or Windows**
   The tool runs on your machine — no cloud account or server needed.

2. **A terminal (command line)**
   This is the text-based interface where you type commands.
   - **macOS**: open the Terminal app (search for "Terminal" in Spotlight)
   - **Windows**: open PowerShell (search for "PowerShell" in Start)
   - **Linux**: you probably already know where your terminal is

   If you've never used a terminal before, that's okay. This guide tells you
   exactly what to type at each step.

3. **An API key from an AI provider**
   The tool needs access to an AI model to give you advice. You'll need an
   account and API key from at least one of these providers:
   - **Anthropic** (makes Claude) — see the [Provider Guide](PROVIDER_GUIDE.md#anthropic)
   - **OpenAI** (makes GPT) — see the [Provider Guide](PROVIDER_GUIDE.md#openai)

   An API key is like a password that lets the tool talk to the AI on your
   behalf. It costs money per use (usually pennies per question). The Provider
   Guide has full details on pricing and how to set one up.

---

## Step 1: Install

You'll need Python 3.10 or later installed on your machine.

- **macOS**: Python 3 is usually pre-installed. Check by typing `python3 --version`
  in Terminal. If it's not there, install it from https://www.python.org/downloads/
- **Windows**: Download from https://www.python.org/downloads/ — during install,
  check the box that says "Add Python to PATH"
- **Linux**: Use your package manager (e.g., `sudo apt install python3 python3-pip`)

Then install Executive in a Box:

```bash
pip install executive-in-a-box
```

Or install from source (for contributors):
```bash
git clone https://github.com/empathetech/executive-in-a-box.git
cd executive-in-a-box
pip install -e .
```

**What you should see:** A success message ending with
`Successfully installed executive-in-a-box`. If you see an error about `pip`
not being found, try `pip3` instead of `pip`.

---

## Step 2: Run the setup wizard

The first time you run the tool, it walks you through a setup wizard. This
takes about 5–10 minutes.

```bash
exec-in-a-box setup
```

<!-- NOTE: `exec-in-a-box` is a placeholder command name. Final CLI name TBD. -->

The wizard asks you four things:

### 2a. Your organization

```
What's your org's name?
> Sunrise Co-op

In one or two sentences, what does it do?
> We build accessible productivity tools for freelancers.

What are the most important values your org operates by?
> Worker ownership, transparency, accessibility, sustainable growth.
```

Type your real answers. There are no wrong answers here — the tool uses this
to understand your org's context when giving advice. You can change these
later.

**What this creates:** A file at `~/.executive-in-a-box/org/profile.md`
containing your answers. It's a plain text file — you can open it in any
text editor and change it anytime.

### 2b. Your advisor

```
Pick an advisor archetype. Each one has a different strategic lens:

  1. The Operator   — pragmatic, execution-focused, risk-aware
  2. The Visionary  — ambitious, long-horizon, tolerant of uncertainty
  3. The Advocate   — people-first, equity-focused, skeptical of growth-for-growth's-sake
  4. The Analyst    — data-driven, cautious, wants evidence before committing

Pick a number [1-4]:
> 3
```

This determines the personality and reasoning style of your AI advisor. The
Operator gives you practical, "how do we actually do this" advice. The
Visionary pushes you to think bigger. The Advocate keeps the focus on your
people. The Analyst wants to see the numbers.

There's no right answer. Pick the one that sounds like the perspective you
most need — not the one you already have.

In V1, you'll be able to have multiple advisors that debate each other.
For now, you get one.

### 2c. Your AI provider

```
Which AI provider should power your advisor?

  1. Anthropic (Claude)
  2. OpenAI (GPT)

Pick a number [1-2]:
> 1

Enter your API key. It will be stored securely in your
operating system's keychain (macOS Keychain, Windows
Credential Locker, or Linux Secret Service).
It is never stored in a plaintext file.

API key: sk-ant-...

Testing connection... ✓ Connected successfully.
```

The tool needs this API key to talk to the AI model on your behalf.

**How your API key is protected:**

Your API key is stored in your operating system's **keychain** — the same
secure system your computer uses to store passwords for websites, Wi-Fi
networks, and other applications:

- **macOS**: stored in Keychain Access (the same place your Mac stores
  all your passwords). You can see it by opening the Keychain Access app
  and searching for "executive-in-a-box".
- **Windows**: stored in Windows Credential Locker. You can see it in
  Control Panel → User Accounts → Credential Manager.
- **Linux**: stored in your desktop's Secret Service (GNOME Keyring or
  KDE Wallet, depending on your desktop environment).

The key is **encrypted at rest** by your operating system and is only
accessible to your user account. It is **never** stored in a plaintext
file anywhere on your machine.

**What happens with your key when you ask a question:**

1. The tool reads your key from the OS keychain
2. It sends your key + your question + your org context directly to your
   chosen provider (Anthropic or OpenAI) over an encrypted HTTPS connection
3. The provider processes it and sends back a response
4. That's it. Your key is not stored, logged, or sent anywhere else.

**Your key is never:**
- Written to any file on disk (not config files, not session logs, not
  debug logs — nowhere)
- Displayed on your screen after you enter it
- Sent to us, to other services, or to anyone other than the provider
  you chose
- Included in the context sent to the AI as part of a question

**Alternative: environment variables.** If you prefer not to use the
keychain (for example, if you're running this on a server without a
desktop environment), you can set your key as an environment variable
instead:

```bash
# For Anthropic:
export EXEC_ANTHROPIC_API_KEY="sk-ant-your-key-here"

# For OpenAI:
export EXEC_OPENAI_API_KEY="sk-your-key-here"
```

The tool checks for environment variables first. If one is set, it uses
that and doesn't touch the keychain. Note that environment variables are
only active for the current terminal session — you'll need to set them
again each time, or add them to your shell profile.

See the [Provider Guide](PROVIDER_GUIDE.md) for how to get a key and what
it costs.

**If the connection test fails:** The tool will tell you what went wrong in
plain language. Common issues:
- The API key was copied incorrectly (try again, make sure you got the whole thing)
- Your provider account doesn't have billing set up (check the Provider Guide)
- Your internet connection is down

### 2d. Your autonomy level

```
How much should your CEO do on its own?

  Level 1 — Advisor
    "I'll present options and explain tradeoffs. You decide everything."

  Level 2 — Recommender
    "I'll give you a specific recommendation. You approve or change it."

Pick a level [1-2]:
> 1

We recommend Level 1 to start. You can change this anytime.
```

This controls how much independence your AI advisor has. At Level 1, it only
gives you information and lets you decide. At Level 2, it also tells you what
it would do and why.

Higher autonomy levels (3 and 4) will be available in V1 — they let the tool
handle routine decisions on its own. We don't offer those yet because trust
should be earned, not assumed.

### Setup complete

```
Your CEO is ready.

  Org:       Sunrise Co-op
  Advisor:   The Advocate (Anthropic Claude)
  Autonomy:  Level 1 — Advisor

  Your data is stored at: ~/.executive-in-a-box/
  You can change any of this by running: exec-in-a-box setup

  Ready to ask your first question? Just type it below.
  Or type 'help' to see what else you can do.

>
```

---

## Step 3: Ask your first question

Type a real strategic question. Something you've actually been thinking about.

```
> Should we focus on building new features or fixing the bugs our current users reported?
```

**What happens next:**

1. The tool loads your org's context (name, mission, values)
2. It sends your question and context to the AI provider
3. It gets back a structured response and shows you:

```
━━━ The Advocate's Position ━━━

Recommendation: Fix the bugs first.

Your org values transparency and sustainability. Shipping new features while
known bugs affect your current users contradicts both. The people already
using your tool chose to trust you — honor that before chasing new users.

Confidence: High

Pros:
  • Builds trust with your existing user base
  • Reduces support burden so you can focus future feature work
  • Aligns with your stated value of accessibility — bugs are access barriers

Cons:
  • Delays new feature delivery, which may affect growth targets
  • Some bugs may be low-impact and not worth prioritizing over features

Flags:
  ⚠ This advice assumes your current users are your priority audience.
    If you're trying to reach a new market segment, the calculus changes.

Questions for you:
  • How severe are the reported bugs? Do any of them block core workflows?
  • Is there a deadline or external pressure driving the new features?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Adopt this recommendation? [Y]es / [N]o / [M]odify
>
```

4. You decide. Type `Y` to adopt it, `N` to reject it, or `M` to modify it.
5. Your decision is logged to `~/.executive-in-a-box/org/decisions.md` —
   a running record of what you decided and why.

**To see the full reasoning behind any recommendation:**

```
> how did you get here?
```

This shows the complete reasoning chain — the full context the advisor
considered and how it arrived at its position.

---

## Step 4: What just happened

After setup and your first question, the tool created these files on your
machine:

```
~/.executive-in-a-box/
  org/
    profile.md          ← Your org's name, mission, and values
    decisions.md        ← A log of decisions you've made with the tool
  board/
    config.md           ← Which advisor you picked, your provider, your autonomy level
  sessions/
    2026-03-21-001.md   ← A transcript of your first session
```

**Notice what's NOT here:** your API key. It's stored securely in your
operating system's keychain, not in any of these files. You'll never
find it in a plaintext file on your machine.

All of the files above are plain text. You can:
- **Open them** in any text editor to see what's there
- **Edit them** to correct or add context (the tool picks up changes automatically)
- **Back them up** by copying the folder
- **Delete them** to start fresh

Your data is your data. The tool doesn't hide it or lock it away.

---

## Common questions

**How much does it cost to use?**
The tool itself is free. You pay the AI provider for each question you ask.
A typical strategic question costs a few cents. See the [Provider Guide](PROVIDER_GUIDE.md)
for exact pricing.

**Can I use it offline?**
Not in MVP — it needs to reach your AI provider's servers. In V1, you'll be
able to use a local AI model (via Ollama) that runs entirely on your machine.

**Is my data private?**
Your data stays on your machine. The only thing that leaves is the question
you ask and your org context — sent directly to the AI provider you chose.
Nothing is sent to us or anyone else. See the [Provider Guide](PROVIDER_GUIDE.md)
for each provider's data policy.

**Can I change my advisor, provider, or autonomy level later?**
Yes. Run `exec-in-a-box setup` again, or edit the files in
`~/.executive-in-a-box/board/` directly.

**Something went wrong. What do I do?**
The tool always tells you what went wrong in plain language and suggests
what to do. If you're stuck, open a GitHub issue — we'll help.

---

## Next steps

- Read the [Archetype Guide](ARCHETYPE_GUIDE.md) to learn more about each
  advisor's strengths and blind spots
- Read the [Autonomy Guide](AUTONOMY_GUIDE.md) to understand the trust
  model and when to give your CEO more independence
- Check the [Provider Guide](PROVIDER_GUIDE.md) if you want to switch
  providers or understand the cost structure
