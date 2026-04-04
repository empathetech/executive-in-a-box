# Architecture

<!-- System design for Executive in a Box.
     When a design decision changes, write an ADR in decisions/ rather than
     rewriting this doc in place. Add a note here pointing to the ADR.

     Pivoted 2026-04-04: CLI → three-interface model (web app, CLI, Claude skill)
     with async job system. See decisions/2026-04-04-web-ui-pivot.md. -->

## System Overview

Executive in a Box is a local-first AI executive tool. It runs on the user's
machine, stores context in plain files the user can read and edit directly, and
connects to one or more LLM providers of the user's choice. There is no required
server, no required account, and no data leaves the machine by default.

The user is always the final decision-maker. The tool advises; it never acts
without the user's knowledge and consent (unless the user explicitly configures
it to do so — see Autonomy Model below).

The backend is a Python process that serves all three interfaces: a locally-served
web app, a CLI, and a Claude Code skill. All interfaces connect to the same backend
and have full feature parity.

---

## Components

### 1. Interface Layer

Three first-class interfaces, all connecting to the same backend:

#### 1a. Web App

A locally-served web app (`localhost:PORT`, optionally exposed via Tailscale).
The primary interface.

Responsibilities:
- Three-pane layout: artifact explorer (left), chat (center), whiteboard/chart (right)
- Chat window per CEO archetype — persistent history, portrait switching
- Streaming/typewriter response rendering (via SSE from the backend)
- "Executizing" state per CEO: faded portrait, disabled input, toast notification on completion
- Artifact panel: session artifacts listed, clickable to open (documents, etc.)
- Default right pane: LLM usage/cost dashboard (tokens used, cost, quota status, reset dates)
- Autonomy level controls per CEO: toggle buttons with hover tooltips
- Announce modal: compose and preview Slack posts (Slack block element rendering) before sending
- Setup/onboarding wizard on first launch

Design language: neon/8-16 bit pixel aesthetic, 80s-90s spandex color register
(Rocko's Modern Life), CRT panel treatments on the right pane. See STYLE_GUIDE.md.

#### 1b. CLI

A terminal interface maintaining full feature parity with the web app.

Responsibilities:
- Conversational chat loop with history per CEO archetype
- ASCII/Unicode design language consistent with the web app's aesthetic
- Multi-CEO switching (select active CEO, others remain available)
- "Executizing" state: status line indicator ("The Operator is strategizing..."),
  other CEOs remain interactive while job runs, notification on completion
- Artifact listing and open commands
- Usage/cost summary view
- Autonomy level control per CEO

Design language: ASCII/Unicode art, color via ANSI escape codes, tonally consistent
with the web app. See STYLE_GUIDE.md.

#### 1c. Claude Skill

A `/exec-in-a-box` slash command for use inside Claude Code.

Responsibilities:
- Full feature parity: conversational history, multi-CEO switching, async jobs
- Artifact creation and reference
- Markdown formatting conventions consistent with the design language
- Async jobs: job submitted, user can interact with other CEOs, result delivered when ready

Design language: markdown formatting conventions. See STYLE_GUIDE.md.

---

### 2. Backend API

The Python backend that all three interfaces connect to. Serves the web app over
HTTP (REST + SSE for streaming), and is called directly by the CLI and skill.

Responsibilities:
- Routes requests to the appropriate backend module (board session, job dispatch, etc.)
- Manages SSE streams for real-time response delivery to the web app
- Exposes job state endpoints for polling (CLI, skill) and push (web SSE)
- Handles all auth and trust enforcement (autonomy levels, action permissions)

---

### 3. Board of Directors Engine

The core reasoning module. Manages one or more LLM "board members" and
synthesizes their output for the user. Unchanged from original architecture.

Key behaviors:
- Each board member responds independently to the same context and prompt
- The engine then produces an aggregated view (see Board Output Format below)
- Board size is configurable: one LLM ("board of one") or many
- Board members are composed from CEO archetypes/profiles (see below)

#### CEO Archetypes

Rather than asking users to configure raw LLM parameters, users select from
named archetypes that have pre-set system prompts, reasoning styles, and biases.

Built-in archetypes:
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

---

### 4. Job System

The async task execution layer. All "deep work" queries — long-running LLM calls,
multi-step reasoning, document generation — are dispatched as background jobs. This
is a backend component: the interface layer does not manage job state.

Key behaviors:
- A job is created for each deep-work request, assigned to a specific CEO archetype
- Jobs have states: `queued → running → complete → failed`
- While a job runs for one CEO, other CEOs remain fully interactive
- Job state is persisted to local storage (`~/.executive-in-a-box/jobs/`)
- Interfaces subscribe to job state via their respective mechanisms:
  - **Web app**: SSE stream — receives state change events, triggers toast notification
  - **CLI**: polls job state on a loop; displays status line; prints notification on completion
  - **Claude skill**: checks job state on each invocation; delivers result when ready
- On failure: job state set to `failed`, interface notified with plain-language error

Job state file structure:
```
~/.executive-in-a-box/jobs/
  <job-id>.json    # { id, archetype, status, created_at, updated_at, result?, error? }
```

"Normal" queries (fast, conversational responses) bypass the job system and stream
directly. The interface layer decides which path to use based on query type and
estimated duration. A dedicated "Executizing" button / command triggers the job path
explicitly for deep work.

---

### 5. Autonomy Model

Configured during setup and adjustable per-CEO at any time via the interface.

| Level | Name | Behavior |
|-------|------|----------|
| 1 | Advisor | CEO presents options, explains tradeoffs. User decides everything. |
| 2 | Recommender | CEO makes a recommendation with reasoning. User approves or overrides. |
| 3 | Delegated | CEO acts on low-stakes decisions automatically; flags high-stakes ones for user review. |
| 4 | Autonomous | CEO acts on its conclusions. User reviews asynchronously. Full audit log always available. |

Level 1 is the default. The web app exposes autonomy level as toggle buttons per CEO portrait,
with hover tooltips describing each level. The CLI exposes it as a per-CEO setting command.
Levels 3 and 4 require explicit acknowledgment before enabling.

---

### 6. Context / Memory Store

All persistent data is stored as plain markdown and JSON files in a directory
on the user's machine (default: `~/.executive-in-a-box/` or a user-specified path).

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
  jobs/
    <job-id>.json         # async job state (see Job System above)
  artifacts/
    <session-id>/         # artifacts created during a session (documents, etc.)
```

Files are human-readable and human-editable. The tool should never write in a
way that makes a file hard to read or edit manually.

---

### 7. LLM Provider Adapter

Abstracts the connection to LLM APIs so the board engine doesn't care which
model is powering which archetype. Unchanged from original architecture.

- Each archetype is bound to a provider + model at config time
- Supported providers added via adapters (OpenAI, Anthropic, Ollama for local models)
- Local models (via Ollama) are a first-class option for fully offline operation
- API keys stored in OS keychain (encrypted at rest), never in plaintext files
- Usage and cost data tracked per provider for the dashboard (tokens in/out, estimated cost)

---

### 8. Slack Integration

Outbound-only for V1. The tool sends messages to a configured Slack channel via
incoming webhook. No inbound Slack events in V1.

- Webhook URL stored in local config (not keychain — not a credential, just a URL)
- Web app: Announce modal — compose post with markdown/block element preview, send on confirm
- CLI: `exec-in-a-box slack "message"` and `--last` flag (current behavior, v0.2.0)
- Claude skill: skill command to send last recommendation or compose a message

Two-way Slack bot (inbound events, slash commands from Slack) is deferred to V2+.

---

### 9. External Integration Layer (V2+)

Handles outbound actions on behalf of the org: LinkedIn, funding databases,
email outreach, etc. Does not exist in V1. See original architecture doc for
planned design — unchanged in intent.

---

## Tech Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Python web framework | FastAPI + uvicorn | Async-first, native SSE support |
| Frontend | React + Vite | Served by FastAPI in production (Option B) |
| Streaming | SSE (Server-Sent Events) | LLM responses + job state notifications |
| Job system | asyncio background tasks | State persisted to `jobs/<job-id>.json`; no Celery/Redis |
| Styling | Tailwind + custom CSS | Tailwind for layout; custom CSS for pixel-art/CRT treatments |
| Build output | `web/dist/` bundled into pip package | Built in CI; not checked into git |

**Development workflow:**
```bash
exec-in-a-box dev        # starts FastAPI + Vite together (hot reload)
exec-in-a-box web        # production mode — serves pre-built React app
cd web && npm run build  # manual build (required after fresh clone)
```

See `decisions/2026-04-04-frontend-stack.md` for the React vs. HTMX decision
and Option A vs. Option B rationale, including notes on switching to Option A
in the future if needed.

---

## Deployment Model

### V1: Locally-served

The backend runs as a local Python server. The web app is served at `localhost:PORT`.
The CLI and Claude skill connect directly to the backend process.

**Tailscale exposure:** The local server can be bound to a Tailscale IP, making it
accessible to other devices on the same Tailscale network. This allows small teams
to share a single instance without cloud infrastructure. Tailscale traffic is
encrypted in transit; the server itself has no auth layer in V1 (access = Tailscale
network membership).

**Trust implication:** When exposed via Tailscale, anyone on the Tailscale network
can access the instance. See SECURITY_PRIVACY.md for the full trust boundary
analysis.

### Future: Hosted with auth

A future milestone introduces hosted deployment with an auth layer. When introduced:
- Full documentation of data residency, retention, and deletion
- Explicit opt-in from the user
- Local-only mode always remains available
- Auth layer options and tradeoffs documented for non-technical contributors

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage format | Plain markdown + JSON files | Accessible to non-technical users; no database dependency; future MCP-compatible |
| Infrastructure | Local-first | No server to manage; no data leaves the machine by default |
| LLM flexibility | Pluggable provider adapter | Users choose their LLMs; no lock-in |
| Default autonomy | Level 1 (Advisor) | Trust is earned progressively; user always in control |
| Board model | Archetypes, not raw models | Lowers barrier to entry; meaningful choices for non-technical users |
| Primary interface | Locally-served web app | Richer UX than CLI alone; preserves local-first model |
| Async model | Backend job system | Interface-agnostic; all three interfaces get the same async behavior |
| Slack | Outbound-only (V1) | Covers primary use case; two-way bot deferred to V2+ |

See `decisions/` for ADRs on significant changes to any of the above.

---

## What This Architecture Deliberately Does Not Include (V1)

- No cloud sync or remote storage
- No external integrations (LinkedIn, email, funding APIs)
- No inbound Slack events or slash commands
- No multi-user auth (Tailscale access = trust in V1)
- No MCP memory server (planned for V1 — not yet implemented)
- No hosted deployment

These are roadmap items, not oversights.
