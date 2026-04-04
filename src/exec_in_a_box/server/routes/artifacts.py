"""Artifact storage API routes.

GET  /api/artifacts            — list all artifacts
GET  /api/artifacts/{id}       — get artifact content
POST /api/artifacts            — create a new artifact
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from exec_in_a_box import storage

router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])


def _artifacts_dir() -> Path:
    return storage.get_data_dir() / "artifacts"


def _list_all() -> list[dict]:
    base = _artifacts_dir()
    if not base.exists():
        return []
    results = []
    for session_dir in sorted(base.iterdir(), reverse=True):
        if not session_dir.is_dir():
            continue
        for f in sorted(session_dir.iterdir(), reverse=True):
            if f.is_file():
                results.append(
                    {
                        "id": f"{session_dir.name}/{f.name}",
                        "session_id": session_dir.name,
                        "filename": f.name,
                        "size_bytes": f.stat().st_size,
                        "modified_at": datetime.fromtimestamp(
                            f.stat().st_mtime, tz=timezone.utc
                        ).isoformat(),
                    }
                )
    return results


@router.get("")
def list_artifacts():
    return {"artifacts": _list_all()}


@router.get("/{session_id}/{filename}")
def get_artifact(session_id: str, filename: str):
    path = _artifacts_dir() / session_id / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return {
        "id": f"{session_id}/{filename}",
        "filename": filename,
        "content": path.read_text(encoding="utf-8"),
    }


class ArtifactCreate(BaseModel):
    session_id: str | None = None
    filename: str
    content: str


@router.post("/{session_id}/{filename}/reveal")
def reveal_artifact(session_id: str, filename: str):
    import platform
    import subprocess

    path = _artifacts_dir() / session_id / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found.")
    system = platform.system()
    if system == "Darwin":
        subprocess.Popen(["open", "-R", str(path)])
    elif system == "Linux":
        subprocess.Popen(["xdg-open", str(path.parent)])
    elif system == "Windows":
        subprocess.Popen(["explorer", f"/select,{path}"])
    return {"revealed": True}


@router.post("")
def create_artifact(body: ArtifactCreate):
    session_id = body.session_id or str(uuid.uuid4())
    artifact_dir = _artifacts_dir() / session_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename — no path traversal
    safe_name = Path(body.filename).name
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    path = artifact_dir / safe_name
    path.write_text(body.content, encoding="utf-8")

    return {
        "id": f"{session_id}/{safe_name}",
        "session_id": session_id,
        "filename": safe_name,
    }
