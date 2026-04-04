# Roadmap

<!-- Sequence what to build and prioritize ruthlessly.
     Milestones should be outcome-based ("users can complete a purchase")
     not task-based ("implement checkout UI").

     MVP = the smallest version that proves the core value proposition.
     V1  = MVP plus what's needed for it to be genuinely useful.
     V2+ = valuable but not required for V1.

     Updated 2026-04-04: V1 reordered for web UI pivot.
     See decisions/2026-04-04-web-ui-pivot.md. -->

---

## MVP ✅ (shipped as v0.2.0)

### Goal
A user can configure an AI advisor with their org's context, ask it a strategic
question, and get structured advice they can act on — all on their own machine.

### Shipped
- Setup wizard: org profile → archetype selection → LLM provider + API key → autonomy level
- 4 built-in archetypes: Operator, Visionary, Advocate, Analyst
- Board of one: single active archetype per session
- LLM provider adapter: Anthropic and OpenAI
- Core session loop: question → wrapper pre-flight → LLM call → schema validation → structured output → user decision → log
- Autonomy levels 1 and 2 (3 and 4 blocked)
- Local storage: org profile, decisions log, board config, session transcripts
- Wrapper layer: secret scanner, prompt injection defenses, output schema validation, error handling
- Web content fetching: URLs in questions → page content injected as context
- Slack outbound webhook: post messages and last recommendation to a channel
- Config commands: `exec-in-a-box config show/archetype/provider/autonomy`
- Documentation: README, setup guide, provider guide, Slack guide, SECURITY.md

---

## V1

V1 transforms the MVP into a genuinely great experience across three interfaces,
with a full board of advisors and memory that makes the CEO useful over time.

### Milestone 1: Web App

**Goal:** A user can run the locally-served web app, have a natural conversation
with their CEO board, dispatch deep-work jobs while chatting with other CEOs,
and manage artifacts — all in the neon/8-bit UI.

- [ ] Python web server (locally-served, `localhost:PORT`)
- [ ] Three-pane layout: artifact explorer / chat / whiteboard
- [ ] CEO portrait strip: archetype cards, active/Executizing/error states, autonomy toggles
- [ ] Chat window per CEO: persistent history, streaming/typewriter responses via SSE
- [ ] Executize button + async job system (backend job queue, state persistence, toast notifications)
- [ ] Multi-CEO switching while jobs run
- [ ] Artifact explorer: session artifacts listed, click to open
- [ ] Right pane default: LLM usage/cost dashboard (per-provider tokens, cost, quota bar)
- [ ] Announce modal: compose + Slack block element preview + send
- [ ] Onboarding wizard (web UI version of setup flow)
- [ ] Tailscale exposure support (configurable bind address)
- [ ] Design language implemented per STYLE_GUIDE.md
- [ ] WCAG 2.1 AA contrast verification for neon palette
- [ ] Documentation: web app setup runbook (non-technical audience)

### Milestone 2: CLI Design Pass

**Goal:** A user who prefers the terminal has a first-class experience that is
tonally and functionally consistent with the web app — not a degraded fallback.

- [ ] ASCII/Unicode design language per STYLE_GUIDE.md (ANSI colors, box-drawing borders)
- [ ] Streaming/typewriter output in terminal
- [ ] Multi-CEO switching (`--ceo` flag + interactive menu)
- [ ] Executizing state: status line + notification on completion
- [ ] Background job system connected to CLI (polls job state, notifies on completion)
- [ ] Artifact commands: list, open, export
- [ ] Usage/cost summary command
- [ ] `NO_COLOR` / graceful color degradation
- [ ] Documentation: CLI runbook update

### Milestone 3: Claude Skill

**Goal:** A user inside Claude Code can invoke `/exec-in-a-box` and get the full
advisory experience — including async deep-work jobs and multi-CEO switching —
without leaving their Claude Code session.

- [ ] `/exec-in-a-box` slash command installed as a Claude Code skill
- [ ] Conversational history per CEO in skill session state
- [ ] Streaming markdown output
- [ ] Async job dispatch + status check + completion notification
- [ ] Multi-CEO switching via `--ceo` flag
- [ ] Artifact references in skill output
- [ ] Slack announce command from skill
- [ ] Documentation: skill setup runbook

### Milestone 4: Multi-LLM Board + Memory

**Goal:** A full board of advisors that debate, aggregate, and remember — making
the CEO genuinely useful across sessions over time.

- [ ] Board of many: multiple archetypes, each optionally on a different LLM/provider
- [ ] Independent responses per archetype collected in parallel (rate-limit aware)
- [ ] Board aggregation: common ground detection, spectrum view, aggregated pros/cons
- [ ] CEO conclusion synthesis (constrained LLM call against archetype outputs)
- [ ] Survey view: side-by-side archetype positions
- [ ] `memory/strategic-context.md` — running summary of key org context
- [ ] `memory/open-questions.md` — flagged items for future resolution
- [ ] Context injection: relevant memory included in prompts automatically
- [ ] MCP memory server integration (opt-in, documented setup)
- [ ] Archetype customization: edit built-in archetypes, create custom ones

### Milestone 5: Local Model Support

**Goal:** A user who needs full data sovereignty can run the entire tool offline
using local models — no API keys, no data leaves the machine.

- [ ] Ollama adapter — use local models for any archetype
- [ ] Ollama setup guide (non-technical audience)
- [ ] Documentation: tradeoffs vs. cloud providers (quality, speed, hardware requirements)

### Milestone 6: Autonomy Levels 3 & 4

**Goal:** Users who have built trust with the tool can delegate routine decisions
and review asynchronously — with full audit log and hard safety limits.

- [ ] Level 3 (Delegated): auto-approve low-stakes actions per action type registry
- [ ] Level 4 (Autonomous): act on conclusions within scope, full async audit log
- [ ] Explicit acknowledgment flow to enable Level 3 or 4 (cannot be skipped)
- [ ] Hard-coded action types that always require user approval regardless of level
- [ ] All-hands meeting facilitation (gated on autonomy model being stable)
- [ ] Documentation: autonomy level guide (risks, how to change, how to roll back)

---

## V2+

**Exec Replacement Audit**
- [ ] Analyze current org structure against mission/values
- [ ] Generate plain-language case for democratic restructuring
- [ ] Required disclaimer in all output

**External Integrations**
- [ ] LinkedIn: networking, outreach, pitching — opt-in, per-action audit log
- [ ] Email outreach — opt-in, per-action audit log
- [ ] Slack two-way bot: inbound events and slash commands from Slack
- [ ] "Undo" or retract action where platform allows

**Hosted Deployment (opt-in)**
- [ ] Cloud hosting with auth layer
- [ ] Documented data residency, retention, deletion
- [ ] Local-only mode always remains available
- [ ] Full infrastructure setup guide for non-technical contributors

**Multi-User / Team Shared Context**
- [ ] Shared org profile and decisions log for small teams
- [ ] Access model: who can read/write which files

**Cloud Sync (opt-in)**
- [ ] Encrypted cloud storage for org context and session history
- [ ] Documented tradeoffs

**Web UI Packaging**
- [ ] Electron/Tauri desktop app (evaluate after locally-served web app is proven)

**Easter Egg: What We Would Have Built**
- [ ] Hidden activation
- [ ] Generative alternative timeline board session
- [ ] Optional export
- [ ] No external connections. Output never auto-shared.

---

## Parking Lot

Ideas without a milestone yet — valid but not prioritized.

- Voice interface
- Mobile companion app
- Integration with project management tools (GitHub Issues, Linear)
- Weekly digest / summary mode
- Public archetype library (community-contributed archetypes)
- Report / analysis view with charts (future right-pane expansion)
