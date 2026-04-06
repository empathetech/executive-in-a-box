# Changelog

<!-- Record of completed milestones and releases.
     Add entries here when a milestone is complete and you cut a release.
     Move entries older than 3 releases to archive/changelog/.

     Format:
     ## [vX.Y.Z] — YYYY-MM-DD
     ### Added
     - ...
     ### Changed
     - ...
     ### Fixed
     - ... -->

## [v1.0.0] — 2026-04-04

### Added

**Three-Interface Model**
- Web app (FastAPI + React + TypeScript + Vite, served at `localhost:8421`)
- CLI design pass: neon ANSI colors, box-drawing, NO_COLOR support
- Claude skill: `/exec-in-a-box` slash command for Claude Code

**Web App**
- Three-pane layout: artifact explorer / chat / usage dashboard
- CEO portrait strip with active/Executizing/error states and autonomy toggles
- Per-CEO persistent chat history with typewriter-effect support
- Executize button: dispatches deep-work jobs as async background tasks
- Multi-CEO switching while jobs run (SSE job completion notifications)
- Artifact explorer (left pane): session artifacts listed, click to open
- LLM usage/cost dashboard (right pane, CRT treatment)
- Announce modal: compose + preview + send to Slack (preview enforced before send)
- Design language: neon/8-bit/CRT aesthetic per STYLE_GUIDE.md
- Tailwind CSS + custom CSS variables for full design system

**CLI Design Pass**
- ANSI color design language (respects NO_COLOR)
- Unicode box drawing for response display
- Ambition level spectrum bar
- `/switch` meta-command for multi-CEO switching mid-session
- `/executize` meta-command for background job dispatch
- `/jobs` meta-command for job status listing
- `exec-in-a-box artifacts list|open` subcommands
- `exec-in-a-box usage` subcommand (job/session summary)

**Async Job System**
- `jobs.py`: queued → running → complete/failed lifecycle
- Job state persisted to `~/.executive-in-a-box/jobs/<job-id>.json`
- SSE streaming for web app job notifications (`GET /api/stream/jobs/{id}`)
- Background threading for CLI job dispatch

**FastAPI Server**
- `server/` subpackage (never imported by CLI)
- Routes: `/api/config`, `/api/session/message`, `/api/jobs`, `/api/stream`, `/api/artifacts`, `/api/slack`, `/api/board`
- `exec-in-a-box web` command (production — serves pre-built React app)
- `exec-in-a-box dev` command (FastAPI + Vite with hot reload)
- `--host` flag for Tailscale exposure

**Multi-LLM Board**
- `board.py`: parallel deliberation across all archetypes using ThreadPoolExecutor
- Common ground detection, spectrum view, aggregated pros/cons
- Rate-limit safe (configurable max_workers)
- `/api/board/deliberate` endpoint

**Memory**
- `memory/open-questions.md` injected into org context alongside strategic-context.md

**Autonomy Levels 3 & 4**
- `autonomy.py`: action type registry with ALWAYS_REQUIRE_APPROVAL hard set
- Explicit acknowledgment flow (CLI + web) required before enabling Level 3 or 4
- Audit log (`audit.log.md`) written for every action evaluation
- Level 3: auto-approve low-stakes actions (log, save, memory updates)
- Level 4: autonomous within scope; all ALWAYS_REQUIRE_APPROVAL types remain blocked

**All-Hands Meeting**
- `all_hands.py`: context gather → agenda → board deliberation → summary → decisions log
- `exec-in-a-box all-hands` CLI command

**Ollama Provider**
- `OllamaProvider` adapter for local LLM via Ollama
- Auto-detects running Ollama server at `http://localhost:11434`
- Provider option: `ollama` (fully offline operation)

**Package**
- `web.py` renamed to `fetch.py`; all import sites updated
- `storage.py` extended with `jobs` and `artifacts` subdirectories
- Version bumped to 1.0.0

### Dependencies Added
- fastapi, uvicorn[standard], sse-starlette (server)

---

## [v1.0.1] — 2026-04-04

### Added

**CLI Functional Parity (post-1.0.0 audit)**
- `feedback show` now displays trait modifier bar chart (±delta per trait, color-coded green/magenta)
- `feedback refresh/toggle/reset` subcommands
- `artifacts delete <id>` subcommand with confirmation prompt
- `history` command rewritten: reads session index, newest-first, ANSI decision colors, reason indented
- Feedback calibration injected into CLI session prompts (checks `active` flag)
- Adopt/reject prompt now collects optional reason text
- Modify → LLM re-run → Y/N only (no chained Modify)
- `exec-in-a-box slack` "last session" now reads from session index (not brittle markdown parsing)
- `exec-in-a-box slack` extracts `<announce>` tags same as web
- `_heal_json()` fallback parser for LLM responses with literal newlines in JSON strings
- OUTPUT_FORMAT_DIRECTIVE updated to remind LLM to escape newlines inside JSON strings
- Shared `_get_ceo_colors()` helper for consistent archetype colors across CLI commands

**Web Fixes**
- Update Feedback button no longer incorrectly disabled when `decisionCount === 0`
- History tab preview text colored by decision outcome
- Radar chart: expanded viewBox (320×290), UPPERCASE BOLD labels, no clip
- Radar chart: both polygons always visible; adjusted overlay in complementary color
- Default adjusted mode (not baseline); toggle controls LLM injection, not chart visibility
- `statsVersion` counter triggers CeoHeroPanel stats refresh after each decision
- AnnounceModal: default webhook pre-selected via `getSlackDefault()`
- Announce from session: extracts multiple `<announce>` blocks using `matchAll`
- `POST /api/feedback/{slug}/active` endpoint for active/baseline toggle

**Design Docs**
- `hacky-hours/02-design/PARITY.md` — living CLI ↔ Web parity tracker
- Journey 6b added to USER_JOURNEYS.md — Feedback Calibration (Scoring and Modifiers)
- CLAUDE.md parity enforcement rule

---

## [v0.2.0] — 2026-03-21

### Added
- Web content fetching: include URLs in questions and the CEO reads the page content as context
- Slack webhook integration: post messages to Slack channels via `exec-in-a-box slack`
- Configuration commands: `exec-in-a-box config show/archetype/provider/autonomy` for reconfiguring the CEO without re-running full setup
- Slack setup guide (docs/SLACK_GUIDE.md)

### Dependencies
- Added beautifulsoup4 for HTML-to-text conversion
- httpx was already a transitive dependency, now used directly for web fetching and Slack webhooks

---

## [v0.1.0] — 2026-03-21

### Added

**Framework & Design**
- Hacky Hours framework scaffolded (ideate, design, roadmap, build)
- Product overview with 5Ws and Constraints & Values
- Architecture document: board of directors model, autonomy levels, local-first storage
- Business logic document: wrapper layer contract, archetype system prompts, output schema, aggregation logic, prompt injection defenses
- Security & privacy document: threat model, trust boundaries, data inventory
- Audit model: standing security/privacy/design checklist for every feature PR
- User journeys: setup wizard, board session, all-hands, autonomy change, exec audit, easter egg
- Accessibility standards (WCAG 2.1 AA target, CLI commitments)
- Licensing document (MIT, dependency compatibility tracking)
- Roadmap: MVP / V1 / V2+ feature prioritization

**User-Facing Documentation**
- README with project overview, install instructions, and point of view
- Setup guide: complete first-run walkthrough for non-technical users
- Provider guide: API key setup, pricing, and data policies for Anthropic and OpenAI
- Autonomy guide: plain-language explanation of the four trust levels
- Archetype guide: each advisor's reasoning style, strengths, and blind spots
- Contributing guide: dev setup, audit requirement, writing standards
- Security disclosure process (SECURITY.md)

**Implementation (Python CLI)**
- Project scaffolding: pyproject.toml, pip-installable package, `exec-in-a-box` CLI
- Local file storage layer: plain markdown/JSON files in `~/.executive-in-a-box/`
- LLM provider adapter: Anthropic and OpenAI with plain-language error handling
- Four built-in archetypes: Operator, Visionary, Advocate, Analyst
- Wrapper layer (pre-call): secret scanner, context injection, prompt injection defense
- Wrapper layer (post-call): strict JSON schema validation on all LLM responses
- Secure credential storage via OS keychain (keyring library)
- Setup wizard: interactive org profile, archetype, provider, and autonomy configuration
- Core session loop: ask a question, get structured advice, decide, log
- Autonomy level enforcement (levels 1-2; levels 3-4 hard-blocked for V1)
- Session history and transcript logging
- 32 passing tests
