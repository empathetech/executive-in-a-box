"""Session history API route.

GET /api/sessions — list all past sessions from the index, newest first.
"""
from __future__ import annotations

from fastapi import APIRouter

from exec_in_a_box import storage
from exec_in_a_box.stats import _parse_session

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _all_sessions() -> list[dict]:
    """Return all indexed session records, newest first."""
    index = storage.read_session_index()
    indexed_ids: set[str] = {e["id"] for e in index}

    # Pick up any session files not yet in the index
    for path in storage.list_sessions():
        if path.stem in indexed_ids:
            continue
        r = _parse_session(path)
        if r and r.get("archetype_slug"):
            index.append({
                "id": path.stem,
                "slug": r["archetype_slug"],
                "timestamp": r["timestamp"],
                "decision": r.get("decision", ""),
                "question": r.get("question", ""),
                "position": r.get("position", ""),
                "confidence": r.get("confidence", ""),
                "ambition_level": r.get("ambition_level", ""),
                "modification": r.get("modification", ""),
            })

    # Newest first
    return list(reversed(index))


@router.get("")
def list_sessions():
    return {"sessions": _all_sessions()}
