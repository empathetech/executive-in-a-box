# ADR: Frontend stack — React + FastAPI, Option B (Python serves built app)

**Date:** 2026-04-04
**Status:** Accepted

## Context

The web UI pivot requires choosing a frontend framework and deciding how the
frontend and Python backend connect. Two viable options were evaluated.

## Decision

**Framework:** React + Vite, served by FastAPI (Option B).

**Option B:** FastAPI serves the built React app as static files. One process,
one port, one command for users (`exec-in-a-box web`). In development, Vite
runs alongside FastAPI for hot reload — either two terminals, or a single
`exec-in-a-box dev` convenience command that starts both.

**Why React over HTMX/Alpine.js:** Expected contributors have React backgrounds.
The UI has genuine state complexity (multiple independent SSE streams, per-CEO
chat history, live artifact panel, job state). React handles this cleanly.
HTMX could do it, but would require more creative workarounds as the UI grows.

**Why Option B over Option A:** Option A (two separate processes always) breaks
the "one command, open your browser" product promise. Option B is one process in
production. Dev experience is identical to Option A when doing frontend work —
Vite still runs with hot reload — but Python-only contributors never need to
touch Node.js after the initial build.

## Rationale

- Contributor pool: React is widely known; lowers the barrier for frontend PRs
- User experience: `exec-in-a-box web` starts everything, no process management
- Packaging: React dist files bundled into the pip package (built in CI, not checked into git)
- CORS: not needed — same origin in production
- Dev workflow: `exec-in-a-box dev` convenience command starts both processes

## Switching to Option A in the future

Option B → Option A is a low-friction change if needed. It requires:
1. Adding CORS middleware to FastAPI (`fastapi.middleware.cors`, ~5 lines)
2. Configuring the React app's API base URL as an environment variable
3. Removing the static file serving routes from FastAPI
4. Deciding where the React app is hosted (CDN, separate server, etc.)

Reasons to switch: if the API becomes a separate shared service used by multiple
frontends, or if the frontend needs to be deployed independently (e.g., to a CDN
for a hosted version). Neither applies in V1.

## Tradeoffs

- Contributors need Node.js installed for frontend work (one-time setup)
- Build step required before the web app is usable from a fresh clone
  (`cd web && npm install && npm run build`)
- The pip package must include pre-built dist files — handled in CI/release,
  not a day-to-day concern

## Alternatives considered

- **HTMX + Alpine.js + Jinja2**: no Node.js required, one language throughout.
  Rejected because expected contributors have React backgrounds, not HTMX
  backgrounds, and the UI complexity will likely grow.
- **Vue + Vite**: same tradeoffs as React, smaller contributor pool.
- **Option A (always two processes)**: rejected because it breaks the single-command
  user experience that is core to the product's accessibility commitment.
