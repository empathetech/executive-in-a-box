# Provider Guide

This guide explains how to get an API key from each supported AI provider,
what it costs, and how Executive in a Box uses your key.

**The bottom line on cost:** You pay the AI provider per question. A typical
strategic question costs between $0.01 and $0.10 USD depending on the provider
and model. If you ask 10 questions a day, expect to spend $1–3 per month.
This is not a subscription — you only pay for what you use.

**The bottom line on privacy:** Your API key is stored on your machine and
sent directly to the provider when you ask a question. It is never sent to
us, logged, or transmitted anywhere else. The provider receives your question
and your org context in order to generate a response. Check each provider's
data policy below to understand how they handle that.

---

## Anthropic

Anthropic makes Claude. They are a safety-focused AI company.

### What it costs

Anthropic charges per token (roughly per word) of input and output. Current
pricing for relevant models:

| Model | Input cost (per 1M tokens) | Output cost (per 1M tokens) | Rough cost per question |
|-------|---------------------------|----------------------------|------------------------|
| Claude Haiku 4.5 | $0.80 | $4.00 | ~$0.01–0.02 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | ~$0.03–0.08 |
| Claude Opus 4.6 | $15.00 | $75.00 | ~$0.10–0.30 |

<!-- NOTE: These prices are current as of March 2026. Check
     https://www.anthropic.com/pricing for the latest. -->

Haiku is the cheapest and fastest. Sonnet is a good balance of quality and
cost. Opus is the most capable but significantly more expensive. For most
strategic questions, **Sonnet is the recommended starting point**.

You'll need to add a payment method to your Anthropic account. There is no
free tier for API usage, but there is typically a small amount of free credits
for new accounts.

### How to get an API key

1. Go to https://console.anthropic.com/
2. Click "Sign up" and create an account (email + password)
3. Once logged in, go to **API Keys** in the left sidebar
4. Click **Create Key**
5. Give it a name (e.g., "executive-in-a-box") and click **Create**
6. Copy the key — it starts with `sk-ant-`. **Save it somewhere safe.**
   You won't be able to see it again after you close this page.
7. Go to **Plans & Billing** in the sidebar and add a payment method

### How to check if your key works

During setup, the tool automatically tests your key by making a small API
call. If it fails, you'll see a plain-language error message.

To test manually:
```bash
exec-in-a-box test-connection anthropic
```

### How to revoke your key

If you think your key has been compromised (someone else has it):
1. Go to https://console.anthropic.com/
2. Go to **API Keys**
3. Click the trash icon next to the compromised key
4. Create a new key and update your Executive in a Box config

### Data policy

Anthropic's API data policy (as of March 2026): prompts sent via the API are
**not used to train models** by default. Check their current policy at
https://www.anthropic.com/policies for the latest.

---

## OpenAI

OpenAI makes GPT. They are the largest commercial AI provider.

### What it costs

OpenAI charges per token of input and output. Current pricing for relevant
models:

| Model | Input cost (per 1M tokens) | Output cost (per 1M tokens) | Rough cost per question |
|-------|---------------------------|----------------------------|------------------------|
| GPT-4.1 mini | $0.40 | $1.60 | ~$0.01 |
| GPT-4.1 | $2.00 | $8.00 | ~$0.02–0.06 |
| GPT-4o | $2.50 | $10.00 | ~$0.03–0.08 |

<!-- NOTE: These prices are current as of March 2026. Check
     https://openai.com/pricing for the latest. -->

GPT-4.1 mini is the cheapest. GPT-4.1 and GPT-4o are more capable.
For most strategic questions, **GPT-4.1 is the recommended starting point**.

You'll need to add a payment method to your OpenAI account. New accounts
may receive a small amount of free API credits.

### How to get an API key

1. Go to https://platform.openai.com/
2. Click "Sign up" and create an account
3. Once logged in, click your profile icon (top right) → **API keys**
4. Click **Create new secret key**
5. Give it a name (e.g., "executive-in-a-box") and click **Create**
6. Copy the key — it starts with `sk-`. **Save it somewhere safe.**
   You won't be able to see it again after you close this page.
7. Go to **Billing** in the sidebar and add a payment method

### How to check if your key works

During setup, the tool automatically tests your key. To test manually:
```bash
exec-in-a-box test-connection openai
```

### How to revoke your key

1. Go to https://platform.openai.com/
2. Go to **API keys**
3. Click the trash icon next to the compromised key
4. Create a new key and update your Executive in a Box config

### Data policy

OpenAI's API data policy (as of March 2026): data sent via the API is
**not used to train models** by default. You can verify and manage this in
your account settings. Check their current policy at
https://openai.com/policies for the latest.

---

## Ollama (coming in V1)

Ollama lets you run AI models directly on your own machine. No API key
needed. No data leaves your computer. Free.

This will be supported in V1. When it's ready, this section will include:
- How to install Ollama
- Which models work well for strategic advisory use
- Hardware requirements (some models need a lot of memory)
- How to configure Executive in a Box to use a local model

If keeping your data entirely on your machine is important to you, this is
the option to watch for.

---

## Which provider should I pick?

| If you want... | Pick... |
|----------------|---------|
| Best balance of quality and cost | Anthropic (Sonnet) or OpenAI (GPT-4.1) |
| Cheapest possible | OpenAI (GPT-4.1 mini) or Anthropic (Haiku) |
| Best reasoning quality (cost not a concern) | Anthropic (Opus) |
| Full data privacy — nothing leaves your machine | Ollama (coming in V1) |

You can switch providers at any time by running `exec-in-a-box setup` or
editing `~/.executive-in-a-box/board/config.md`.

---

## How the tool uses your key

1. Your API key is stored in your **operating system's keychain** — the
   same secure, encrypted storage your computer uses for website passwords:
   - macOS: Keychain Access
   - Windows: Credential Locker
   - Linux: Secret Service (GNOME Keyring or KDE Wallet)
2. The key is **encrypted at rest** by your OS and only accessible to
   your user account. It is **never stored in a plaintext file**.
3. When you ask a question, the tool reads the key from the keychain and
   sends it + your question + your org context directly to the provider's
   API over an encrypted HTTPS connection.
4. The provider processes it and sends back a response.
5. Your key is **never** written to any file, logged to session
   transcripts, displayed on screen, or sent anywhere other than directly
   to the provider you configured.

**Alternative: environment variables.** If you prefer not to use the
keychain (e.g., on a server without a desktop environment), you can set:
```bash
export EXEC_ANTHROPIC_API_KEY="sk-ant-..."
# or
export EXEC_OPENAI_API_KEY="sk-..."
```

The tool checks for environment variables first and uses them if present.
If an environment variable is set, the keychain is not accessed.

**To remove your key:** Run `exec-in-a-box setup` and enter a new key,
or find "executive-in-a-box" in your OS keychain manager and delete it
manually.
