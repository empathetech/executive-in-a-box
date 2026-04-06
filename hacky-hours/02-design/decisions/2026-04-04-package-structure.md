# ADR: Python package structure for V1

**Date:** 2026-04-04
**Status:** Accepted

## Context

The V1 web app requires adding FastAPI, an async job system, and SSE streaming
alongside the existing CLI codebase. The existing package (`src/exec_in_a_box/`)
is a flat set of modules that are already effectively a core layer — they contain
business logic, not CLI-specific code. `__main__.py` is the thin CLI entry point.

Two options were considered:
1. Introduce a `core/` subpackage, move existing modules into it, add `server/` alongside
2. Leave existing modules flat, add `server/` subpackage for FastAPI only

## Decision

**Option 2: minimal reorganization.** Leave all existing modules flat and unchanged.
Add `server/` as a new subpackage for FastAPI. Add `jobs.py` as a new top-level
module for the async job system. Rename `web.py` → `fetch.py` to free up the `web`
namespace.

Final structure:

```
src/exec_in_a_box/
  __main__.py         # CLI entry point — add 'web' and 'dev' commands
  archetypes.py       # unchanged
  config.py           # unchanged
  credentials.py      # unchanged
  fetch.py            # renamed from web.py
  jobs.py             # new — async job system
  providers.py        # unchanged
  session.py          # unchanged
  setup.py            # unchanged
  slack.py            # unchanged
  storage.py          # unchanged
  wrapper.py          # unchanged
  server/
    __init__.py
    app.py            # FastAPI instance, startup, static file serving
    routes/
      __init__.py
      artifacts.py    # GET/POST /api/artifacts
      config.py       # GET/POST /api/config
      jobs.py         # GET /api/jobs/{id}
      session.py      # POST /api/session/message
      slack.py        # POST /api/slack/announce
      stream.py       # GET /api/stream/{id} (SSE)

web/                  # React + TypeScript app (project root)
  src/
  package.json
  tsconfig.json
  vite.config.ts
```

## Rationale

- The existing flat modules are already a clean core layer. A `core/` reorganization
  would touch every import and every test for zero functional gain.
- `server/` isolates all FastAPI code — the CLI never imports from `server/`, and
  `server/` routes call into the flat core modules exactly as the CLI does.
- `web.py` → `fetch.py` is the only change to existing files (besides `__main__.py`
  gaining two new commands). All other existing code is untouched.
- The CLI continues to work throughout the entire V1 build — no breakage at any point.

## What changes in existing files

| File | Change |
|------|--------|
| `web.py` | Renamed to `fetch.py` |
| `__main__.py` | Add `web` and `dev` CLI commands |
| Any file importing `web.py` | Update import to `fetch` |
| `pyproject.toml` | Add FastAPI, uvicorn dependencies; add package data for `web/dist/` |

## What is net-new

- `src/exec_in_a_box/jobs.py` — async job system
- `src/exec_in_a_box/server/` — entire FastAPI layer
- `web/` — React + TypeScript app

## TypeScript

The React app uses TypeScript. `tsconfig.json` configured with strict mode.
API response types defined in `web/src/types/` and kept in sync with the
Python schemas in `server/routes/`.

## State management

React built-in (`useState`, `useContext`, `useReducer`) only. No Redux or Zustand
in V1. Revisit if state complexity grows beyond what hooks handle cleanly.
