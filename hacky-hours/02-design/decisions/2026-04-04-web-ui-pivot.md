# ADR: Pivot to web UI as primary interface; three-interface model; async job system

**Date:** 2026-04-04
**Status:** Accepted

## Context

The v0.2.0 CLI experience was not meeting expectations. The interaction model felt
thrashy and non-conversational — users had to wait for responses with no feedback,
couldn't interact with other advisors while one was thinking, and the output format
didn't lend itself to the ongoing advisory relationship the product is meant to enable.

The core value proposition (strategic guidance from a board of AI advisors) is sound.
The form factor was wrong.

## Decision

Redesign the product around three first-class interfaces, all with feature parity on
the core experience:

1. **Web app** — locally-served, accessible via `localhost` or Tailscale. Primary interface.
   Design language: neon/8-bit, inspired by Rocko's Modern Life color register (spandex
   80s-90s colors), 8-16 bit pixel aesthetic, CRT panel treatments.

2. **CLI** — maintained as a first-class interface with an ASCII/Unicode design language
   that is tonally consistent with the web app. Not a degraded fallback — full feature parity.

3. **Claude skill** — a `/exec-in-a-box` slash command for use inside Claude Code.
   Markdown formatting conventions consistent with the design language. Full feature parity.

All three interfaces connect to the same Python backend. The backend, not the UI layer,
is responsible for all async job management, state persistence, and CEO context.

A **job system** is introduced as a core backend component. "Deep work" queries (long-running
LLM calls, multi-step reasoning, document generation) are dispatched as background jobs.
Each interface can submit a job for one CEO and continue interacting with other CEOs while
the job runs — analogous to sending a party member on an async quest in an RPG. The
interface is notified (via toast, status line, or message) when the job completes.

Slack integration stays **outbound-only** for now (webhook model from v0.2.0). A two-way
Slack bot is deferred to V2+.

The web app is locally-served for V1. The roadmap includes a future milestone for hosted
deployment with an auth layer, but local-first is preserved as the default.

## Rationale

- The CLI's thrashy UX came from synchronous blocking calls with no feedback. The job
  system solves this at the backend level, so all interfaces benefit.
- Three interfaces serve different user contexts: web app for focused sessions, CLI for
  users who live in the terminal, Claude skill for users already in a Claude Code session.
- Feature parity across interfaces ensures the product's value isn't gated on any one
  deployment preference.
- Locally-served web app preserves the local-first privacy commitment while enabling a
  far richer UX than the CLI alone.
- Tailscale exposure lets small teams share a single instance without cloud infrastructure.

## Tradeoffs

- Significantly more implementation surface than a CLI-only approach.
- The job system adds complexity to the backend (job state, polling/notification, failure
  handling across interfaces).
- Web app requires a frontend tech stack decision (deferred to implementation planning).
- Slack inbound deferral means the Slack integration remains one-directional for V1 —
  acceptable given that outbound covers the primary use case (sharing recommendations
  with a team channel).

## What this changes

- `PRODUCT_OVERVIEW.md` — Where section updated to reflect three-interface model
- `ARCHITECTURE.md` — CLI layer becomes interface layer (three variants); job system added
  as a new backend component; Slack stays outbound-only; Tailscale exposure documented
- `USER_JOURNEYS.md` — full rewrite for web UI flows
- `SECURITY_PRIVACY.md` — Tailscale as a new trust boundary; Slack inbound removed from V1
- `STYLE_GUIDE.md` — new document covering all three interface design languages
- `BUSINESS_LOGIC.md` — async job rules; Announce compose flow; streaming handling
- `ACCESSIBILITY.md` — web UI activates WCAG 2.1 AA requirements now
- `ROADMAP.md` — V1 reordered: web app → CLI design pass → Claude skill

## What this does not change

- Core advisory function (archetypes, board model, aggregation)
- Local-first storage model
- Autonomy level system
- Privacy commitment (no telemetry, no cloud by default)
- MIT license
- Python as the implementation language

## Alternatives considered

- **CLI improvements only**: streaming output and async jobs could be added to the CLI
  without a web app. Rejected because the chat-window model (persistent history, portrait
  switching, artifact panel) is hard to approximate well in a terminal, and the CLI-only
  approach doesn't serve users who want a more visual, session-oriented experience.
- **Electron/Tauri desktop app**: same web tech but packaged as a native app. Deferred —
  locally-served is simpler to ship first; Electron/Tauri can be evaluated later without
  changing the architecture.
- **Hosted web app from day one**: rejected because it conflicts with the local-first
  privacy commitment and adds infrastructure complexity before the UX is proven.
