# Executive in a Box

The most replaceable job due to AI is the CEO.

An AI-powered executive advisor that gives any team access to CEO-level
strategic guidance — without a human CEO.

You bring the org. You bring the values. You make the decisions.
The tool brings the strategic thinking, the structured advice, and the
relentless focus on what actually matters for your product and your people.

---

## What is this?

Executive in a Box is a command-line tool that acts as your organization's
AI-powered CEO. You configure it with your org's mission, values, and context.
You ask it strategic questions. It gives you structured, opinionated advice.
You decide what to do with it.

It runs on your machine. Your data stays on your machine. You pick the AI
model that powers it. You're always in charge.

Think of it as the 10% of a CEO that's actually useful — strategic clarity,
structured thinking, honest tradeoff analysis — without the 90% that isn't:
the politics, the shareholder appeasement, the thoughtless layoffs, the
jargon-filled all-hands that could have been an email.

## Who is this for?

- **Solo builders** who need a strategic thinking partner, not a boss
- **Co-ops and worker-owned orgs** that operate democratically and want
  tools that match their structure
- **Small teams** that need CEO-level guidance but don't need (or want)
  a CEO
- **People who were recently laid off** and are building something new on
  their own terms — this is your executive team now

If you've ever sat in an all-hands meeting thinking "I could do this better,"
this tool is for you.

## What can it do?

**Available now: design and documentation**

This project is in active development. The design is complete and the full
architecture, security model, and user experience are documented. Code
implementation is underway.

Read the design docs in `hacky-hours/02-design/` to see exactly what's
being built and how.

**MVP (in progress):**
- Setup wizard: configure your org profile, pick an AI advisor archetype,
  connect your LLM provider
- Strategic board sessions: ask a question, get structured advice with
  clear reasoning, pros/cons, confidence level, and flags
- Four advisor archetypes to choose from — each with a different strategic
  lens (pragmatic, visionary, people-first, evidence-driven)
- Full local storage: your org context, decisions, and session history
  stay on your machine in plain text files you can read and edit
- Supports Anthropic (Claude) and OpenAI (GPT) to start

**Coming in V1:**
- Board of directors: multiple AI advisors that each weigh in independently,
  with aggregated views showing common ground, where they disagree, and why
- Strategic memory: the CEO remembers your past decisions and context across
  sessions
- All-hands meeting facilitation
- Local model support via Ollama (your data never leaves your machine — period)
- Higher autonomy levels for when you trust the tool enough to let it handle
  routine decisions on its own

**On the roadmap (V2+):**
- Executive replacement audit: the tool analyzes your current org structure and
  builds a structured case for a more democratic alternative
- External integrations: LinkedIn networking, investor pitching, funding outreach
- Cloud sync (opt-in, documented, your choice)
- And one easter egg we're not going to spoil here

## How do I install and run it?

### Requirements
- Python 3.10 or later
- An API key from [Anthropic](https://console.anthropic.com/) or
  [OpenAI](https://platform.openai.com/) — see the
  [Provider Guide](docs/PROVIDER_GUIDE.md) for setup and pricing

### Install

```bash
pip install executive-in-a-box
```

Or install from source:
```bash
git clone https://github.com/empathetech/executive-in-a-box.git
cd executive-in-a-box
pip install -e .
```

### Run

```bash
exec-in-a-box
```

The first time you run it, a setup wizard walks you through configuring your
org, picking an advisor, and connecting your AI provider. Takes about 5
minutes. After that, you're dropped into the session prompt — ask your first
question.

See the [Setup Guide](docs/SETUP_GUIDE.md) for a detailed walkthrough.

## What does it NOT do?

Let's be upfront:

- **It does not make decisions for you** (by default). You are always the
  final decision-maker unless you explicitly configure a higher autonomy level.
- **It is not a lawyer, accountant, or HR department.** Its advice is
  strategic, not legal or financial. Use your judgment.
- **It can be wrong.** AI models produce confident-sounding output that is
  sometimes incorrect, incomplete, or hallucinated. The tool is designed to
  surface uncertainty honestly, but you should always apply your own judgment
  — especially for significant or irreversible decisions.
- **It does not send your data anywhere by default.** The only external
  calls it makes are to the LLM provider you configured, and only with the
  context you've approved.

## Project structure

```
executive-in-a-box/
  hacky-hours/                 # Framework documentation
    01-ideate/                 # Product vision and overview
    02-design/                 # Architecture, security, business logic, user journeys
    03-roadmap/                # MVP / V1 / V2+ feature roadmap
    04-build/                  # Backlog and changelog
  docs/                        # User-facing guides (setup, providers, archetypes)
  src/                         # Source code (coming soon)
  README.md                    # You are here
  CLAUDE.md                    # AI assistant project instructions
  SECURITY.md                  # Security disclosure process
  CONTRIBUTING.md              # How to contribute
  LICENSE                      # MIT License
```

## Contributing

We're actively looking for contributors. This project values documentation
as much as code — if you're a good writer, you're a good contributor.

A full contributing guide is coming soon. In the meantime:

1. Read the design docs in `hacky-hours/02-design/` to understand what's
   being built
2. Check the backlog in `hacky-hours/04-build/BACKLOG.md` for open tasks
3. Every feature PR requires a security and design audit before merging
   (see `hacky-hours/02-design/AUDIT_MODEL.md`)

If you've been laid off and want to channel that energy into something
that actually helps workers — pull up a chair.

## The point of view

Executives are using AI to eliminate jobs. We're using AI to eliminate
executives.

Not out of spite (okay, maybe a little). But because the value a human CEO
provides — strategic clarity, stakeholder alignment, external representation —
is available at a fraction of the cost without the politics, the extraction,
and the human damage that comes with the traditional model.

This tool puts that capability in the hands of the people who do the actual
work.

## License

[MIT License](LICENSE) — use it, fork it, build on it, sell what you build
on it. The tool stays free.
