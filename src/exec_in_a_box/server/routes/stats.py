"""CEO decision statistics API route.

GET /api/stats
  Returns per-CEO aggregated decision stats (adoption/rejection/modification
  rates, avg confidence, avg ambition) and a recent decision history per CEO.
  Data is parsed from session transcripts in ~/.executive-in-a-box/sessions/.
"""
from __future__ import annotations

from fastapi import APIRouter

from exec_in_a_box.stats import get_ceo_stats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def get_stats():
    ceo_stats, total_sessions = get_ceo_stats()
    return {
        "ceos": ceo_stats,
        "total_sessions": total_sessions,
    }
