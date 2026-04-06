"""Board deliberation API route.

POST /api/board/deliberate
  Run a multi-archetype board deliberation in parallel.
  Returns all member responses, common ground, spectrum, and aggregated pros/cons.

Reference: hacky-hours/02-design/ARCHITECTURE.md § Board of Directors Engine
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from exec_in_a_box.archetypes import list_archetypes
from exec_in_a_box.board import run_board
from exec_in_a_box.config import load_config
from exec_in_a_box.credentials import get_api_key

router = APIRouter(prefix="/api/board", tags=["board"])


class DeliberateRequest(BaseModel):
    question: str
    archetype_slugs: list[str] | None = None  # None = all archetypes


@router.post("/deliberate")
async def deliberate(body: DeliberateRequest):
    config = load_config()
    if config is None:
        raise HTTPException(status_code=503, detail="Not configured. Run setup first.")

    api_key = get_api_key(config.provider_name)
    if api_key is None:
        raise HTTPException(
            status_code=503,
            detail=f"No API key for provider: {config.provider_name}",
        )

    slugs = body.archetype_slugs or [a.slug for a in list_archetypes()]

    # Run in thread pool (synchronous providers)
    def _run():
        return run_board(slugs, body.question, config.provider_name, api_key)

    result = await asyncio.to_thread(_run)

    return {
        "members": [
            {
                "archetype_slug": m.archetype.slug,
                "archetype_name": m.archetype.name,
                "response": {
                    "archetype": m.response.archetype,
                    "position": m.response.position,
                    "reasoning": m.response.reasoning,
                    "confidence": m.response.confidence,
                    "ambition_level": m.response.ambition_level,
                    "pros": m.response.pros,
                    "cons": m.response.cons,
                    "flags": m.response.flags,
                    "questions_for_user": m.response.questions_for_user,
                }
                if m.response
                else None,
                "error": m.error,
            }
            for m in result.members
        ],
        "common_ground": result.common_ground,
        "spectrum": [{"slug": s, "ambition_level": a} for s, a in result.spectrum],
        "aggregated_pros": result.aggregated_pros,
        "aggregated_cons": result.aggregated_cons,
        "errors": result.errors,
    }
