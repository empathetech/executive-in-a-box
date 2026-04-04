# Backlog

<!-- This is a queue, not a ledger.
     Items are added during planning and removed when their PR is merged.
     An empty backlog means the milestone is complete.
     Completed work belongs in CHANGELOG.md, not here. -->

## Current Milestone: v1.0.0 — Reimagined

All items below are part of the `reimagined` branch and will ship together in one PR.
See hacky-hours/03-roadmap/ROADMAP.md for the full milestone descriptions.

---

### Milestone 1: Web App

- [ ] Python web server (FastAPI + uvicorn, locally-served at `localhost:PORT`)
- [ ] `exec-in-a-box web` CLI command (production — serves pre-built React app)
- [ ] `exec-in-a-box dev` CLI command (starts FastAPI + Vite together)
- [ ] React + TypeScript + Vite scaffold (`web/` at project root)
- [ ] Three-pane layout: artifact explorer / chat / whiteboard
- [ ] CEO portrait strip: archetype cards with active / Executizing / error states
- [ ] Autonomy level toggles per CEO portrait (buttons 1–4, hover tooltips)
- [ ] Chat window per CEO: persistent history, streaming/typewriter responses via SSE
- [ ] Async job system backend (`src/exec_in_a_box/jobs.py`)
- [ ] Executize button + job dispatch + toast notification on completion
- [ ] Multi-CEO switching while jobs run
- [ ] Artifact explorer (left pane): session artifacts listed, click to open
- [ ] Artifact storage (`~/.executive-in-a-box/artifacts/`)
- [ ] Right pane default: LLM usage/cost dashboard (tokens, cost, quota bar, reset date)
- [ ] Announce modal: compose + Slack block element preview + send
- [ ] Web app onboarding wizard (first-launch setup flow in browser)
- [ ] Tailscale exposure support (`--host` flag to bind to non-localhost)
- [ ] Design language implemented per STYLE_GUIDE.md (neon/8-bit/CRT)
- [ ] WCAG 2.1 AA contrast verification for neon palette
- [ ] `web.py` renamed to `fetch.py`; all import sites updated
- [ ] `server/` subpackage created; FastAPI routes isolated from CLI
- [ ] Tailwind CSS configured in Vite build
- [ ] TypeScript strict mode enabled (`tsconfig.json`)
- [ ] API response types defined in `web/src/types/`
- [ ] Documentation: WEB_APP_GUIDE.md updated with final command names and port

---

### Milestone 2: CLI Design Pass

- [ ] ASCII/Unicode design language applied per STYLE_GUIDE.md (ANSI colors, box-drawing)
- [ ] Streaming/typewriter output in terminal (progressive print)
- [ ] Multi-CEO switching (`--ceo` flag + interactive `/switch` menu)
- [ ] Executizing state: status line + completion notification
- [ ] CLI connected to async job system (polls state, prints notification on completion)
- [ ] `exec-in-a-box artifacts list` command
- [ ] `exec-in-a-box artifacts open <id>` command
- [ ] `exec-in-a-box artifacts export <id>` command
- [ ] `exec-in-a-box usage` command (token + cost summary, ASCII quota bar)
- [ ] `NO_COLOR` env var detection; graceful ANSI color degradation

---

### Milestone 3: Claude Skill

- [ ] `/exec-in-a-box` slash command scaffold (`.claude/commands/exec-in-a-box.md`)
- [ ] Conversational history per CEO in skill session state
- [ ] Streaming markdown output
- [ ] `--executize` flag: async job dispatch + status check + completion notification
- [ ] `--ceo` flag: multi-CEO switching
- [ ] Artifact references in skill output
- [ ] `/exec-in-a-box slack --last` and `/exec-in-a-box slack "message"` commands
- [ ] `/exec-in-a-box usage` command
- [ ] `/exec-in-a-box help` command
- [ ] Documentation: SKILL_GUIDE.md updated with final command syntax

---

### Milestone 4: Multi-LLM Board + Memory

- [ ] Board of many: multiple archetypes, each optionally on a different LLM/provider
- [ ] Independent archetype responses collected in parallel (rate-limit aware)
- [ ] Board aggregation: common ground detection, spectrum view, aggregated pros/cons
- [ ] CEO conclusion synthesis (constrained LLM call against archetype outputs)
- [ ] Survey view: side-by-side archetype positions
- [ ] `memory/strategic-context.md` — running summary of key org context
- [ ] `memory/open-questions.md` — flagged items for future resolution
- [ ] Context injection: relevant memory auto-included in prompts
- [ ] MCP memory server integration (opt-in, documented setup)
- [ ] Archetype edit: user can modify built-in archetypes
- [ ] Archetype create: user can define custom archetypes

---

### Milestone 5: Local Model Support (Ollama)

- [ ] Ollama provider adapter
- [ ] Ollama configured as a provider option in setup wizard and `exec-in-a-box config provider`
- [ ] Documentation: Ollama setup guide (non-technical audience, hardware requirements, tradeoffs)

---

### Milestone 6: Autonomy Levels 3 & 4 + All-Hands

- [ ] Level 3 (Delegated): auto-approve low-stakes actions per action type registry
- [ ] Level 4 (Autonomous): act on conclusions within scope, full async audit log
- [ ] Explicit acknowledgment flow required to enable Level 3 or 4 (modal in web, CONFIRM prompt in CLI)
- [ ] Hard-coded action types that always require user approval enforced in code
- [ ] All-hands meeting facilitation: context gather → agenda → facilitation → summary → decisions log
- [ ] Documentation: autonomy level guide updated for Levels 3 and 4
