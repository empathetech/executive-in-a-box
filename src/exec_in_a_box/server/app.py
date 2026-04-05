"""FastAPI application factory.

In production (`exec-in-a-box web`), FastAPI serves the pre-built React app
as static files alongside the API. In development (`exec-in-a-box dev`),
Vite runs separately on its own port and proxies API calls to this server.

Reference: hacky-hours/02-design/decisions/2026-04-04-frontend-stack.md
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from exec_in_a_box.server.routes import (
    artifacts,
    board,
    config,
    feedback,
    integrations,
    jobs,
    session,
    sessions,
    slack,
    stats,
    stream,
)

app = FastAPI(
    title="Executive in a Box",
    description="AI-powered executive advisor API",
    version="1.0.0",
)

# Register API routes
app.include_router(config.router)
app.include_router(board.router)
app.include_router(session.router)
app.include_router(sessions.router)
app.include_router(jobs.router)
app.include_router(stream.router)
app.include_router(artifacts.router)
app.include_router(slack.router)
app.include_router(stats.router)
app.include_router(integrations.router)
app.include_router(feedback.router)


def _find_web_dist() -> Path | None:
    """Locate the pre-built React app.

    Checks in order:
    1. Package-installed dist (bundled into the pip wheel)
    2. Local dev build (web/dist relative to project root)
    """
    # 1. Package-installed (pip install)
    try:
        ref = importlib.resources.files("exec_in_a_box") / "web_dist"
        if ref.is_dir():
            return Path(str(ref))
    except Exception:
        pass

    # 2. Local dev build — walk up from this file to find web/dist
    here = Path(__file__).parent
    for _ in range(5):
        candidate = here / "web" / "dist"
        if candidate.is_dir():
            return candidate
        here = here.parent

    return None


def mount_static(dist: Path) -> None:
    """Mount the React build as static files and add SPA fallback."""
    app.mount(
        "/assets",
        StaticFiles(directory=dist / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        index = dist / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"error": "Web app not built. Run: cd web && npm run build"}


def create_app(serve_static: bool = True) -> FastAPI:
    """Return the FastAPI app, optionally with static file serving."""
    if serve_static:
        dist = _find_web_dist()
        if dist:
            mount_static(dist)
    return app
