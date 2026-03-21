# Architecture

<!-- System design for Executive in a Box.
     When a design decision changes, write an ADR in decisions/ rather than
     rewriting this doc in place. Add a note here pointing to the ADR. -->

## System Overview

Executive in a Box is a local-first AI executive tool. It runs on the user's
machine, stores context in plain files the user can read and edit directly, and
connects to one or more LLM providers of the user's choice. There is no required
server, no required account, and no data leaves the machine by default.

The user is always the final decision-maker. The tool advises; it never acts
without the user's knowledge and consent (unless the user explicitly configures
it to do so — see Autonomy Model below).

---

## Components

### 1. CLI / Interface Layer

The entry point for the user. MVP is a CLI. A desktop UI is a future option.

Responsibilities:
- Runs the setup wizard on first launch
- Routes user input to the appropriate module (board session, strategic query, meeting facilitation, etc.)
- Displays board output in a readable, structured format
- Surfaces the autonomy controls and "how it got here" view on request

### 2. Board of Directors Engine

The core reasoning module. Manages one or more LLM "board members" and
synthesizes their output for the user.

Key behaviors:
- Each board member responds independently to the same context and prompt
- The engine then produces an aggregated view (see Board Output Format below)
- Board size is configurable: one LLM ("board of one") or many
- Board members are composed from CEO archetypes/profiles (see below)

#### CEO Archetypes

Rather than asking users to configure raw LLM parameters, users select from
named archetypes that have pre-set system prompts, reasoning styles, and biases.

Examples (to be designed in detail during V1):
- **The Operator** — pragmatic, execution-focused, risk-aware
- **The Visionary** — ambitious, long-horizon, tolerant of uncertainty
- **The Advocate** — people-first, equity-focused, skeptical of growth-for-growth's-sake
- **The Analyst** — data-driven, cautious, wants to see evidence before committing

Users compose their board by picking archetypes. A board of one is valid.
The user can also customize archetypes or create their own.

#### Board Output Format

When the board deliberates on a question, the output surfaces:

1. **Each member's position** — what they recommended and why (collapsible)
2. **Common ground** — advice or direction that appeared across multiple members
3. **Spectrum view** — where members landed on an aggressive/ambitious vs. cautious/conservative axis
4. **Aggregated pros and cons** — synthesized from all positions
5. **CEO conclusion** — the board's synthesized recommendation
6. **How it got here** — the reasoning chain behind the conclusion (opt-in, always available)

The user's interaction with the conclusion is a simple yes/no (adopt or reject).
If the user fully defers to the CEO, the conclusion is acted on automatically.

### 3. Autonomy Model

Configured during the setup wizard and adjustable at any time.

Two axes:
- **Opinion vs. Decision**: Does the CEO give you advice, or does it make the call?
- **Deference level**: How much does the user want to be in the loop on each step?

Implemented as a progressive trust model:

| Level | Name | Behavior |
|-------|------|----------|
| 1 | Advisor | CEO presents options, explains tradeoffs. User decides everything. |
| 2 | Recommender | CEO makes a recommendation with reasoning. User approves or overrides. |
| 3 | Delegated | CEO acts on low-stakes decisions automatically; flags high-stakes ones for user review. |
| 4 | Autonomous | CEO acts on its conclusions. User reviews asynchronously. Full audit log always available. |

Level 1 is the default. The setup wizard helps the user find their starting level.
As users build familiarity and trust, they can move up. The tool should gently
suggest when a user might be ready for more delegation based on usage patterns,
but never push.

### 4. Context / Memory Store

All persistent data is stored as plain markdown and JSON files in a directory
on the user's machine (default: `~/.executive-in-a-box/` or a user-specified path).

Plain files were chosen deliberately:
- Any user with basic reading skills can open and understand them
- No database to install, configure, or learn
- Easy to back up, version control, or share
- Compatible with a future MCP memory server integration without migration

#### File Structure

```
~/.executive-in-a-box/
  org/
    profile.md          # org name, mission, values, structure
    stakeholders.md     # key people, roles, relationships
    decisions.md        # log of decisions made and rationale
  board/
    config.md           # board composition, archetype assignments, autonomy level
    archetypes/         # custom archetype definitions (if any)
  sessions/
    YYYY-MM-DD-*.md     # session transcripts, one file per session
  memory/
    strategic-context.md  # running summary of key context for the CEO
    open-questions.md     # things flagged for future resolution
```

Files are human-readable and human-editable. The tool should never write in a
way that makes a file hard to read or edit manually.

### 5. LLM Provider Adapter

Abstracts the connection to LLM APIs so the board engine doesn't care which
model is powering which archetype.

- Each archetype is bound to a provider + model at config time
- Supported providers are added via adapters (OpenAI, Anthropic, Ollama for local models, etc.)
- Local models (via Ollama or similar) are a first-class option — users who want
  fully offline operation should be able to get it
- API keys are stored in the OS keychain (encrypted at rest), never in
  plaintext files, and never transmitted anywhere except directly to the
  configured provider

### 6. External Integration Layer (V2+)

Handles outbound actions on behalf of the org: LinkedIn, funding databases,
email outreach, etc.

This module does not exist in MVP or V1. When introduced:
- Every integration is opt-in with explicit setup steps
- Credentials are stored locally (never in cloud config)
- Each action the CEO takes on an external system is logged and reviewable
- Autonomy level applies here too — no external action at Level 1 or 2 without
  explicit user confirmation

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage format | Plain markdown + JSON files | Accessible to non-technical users; no database dependency; future MCP-compatible |
| Infrastructure | Local-first | No server to manage; no data leaves the machine by default; respects user privacy |
| LLM flexibility | Pluggable provider adapter | Users choose their LLMs; no lock-in to a single provider |
| Default autonomy | Level 1 (Advisor) | Trust is earned progressively; user is always in control by default |
| Board model | Archetypes, not raw models | Lowers barrier to entry; gives non-technical users meaningful choices |

See `decisions/` for ADRs on significant changes to any of the above.

---

## What This Architecture Deliberately Does Not Include (MVP)

- No cloud sync or remote storage
- No external integrations (LinkedIn, email, funding APIs)
- No web UI
- No multi-user / team shared context (single user, local machine)
- No MCP memory server (planned for V1)

These are roadmap items, not oversights. The MVP proves the core value loop
(board deliberation → user decision → context persistence) before adding
complexity.
