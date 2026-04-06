"""Config API routes.

GET  /api/config          — return current board config + archetype list
POST /api/config/autonomy — change autonomy level for an archetype
POST /api/config/archetype — change active archetype
"""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from exec_in_a_box import storage
from exec_in_a_box.archetypes import list_archetypes
from exec_in_a_box.config import load_config, save_autonomy_level
from exec_in_a_box.credentials import get_api_key
from exec_in_a_box.slack import list_webhooks

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
def get_config():
    config = load_config()
    if config is None:
        raise HTTPException(status_code=404, detail="Not configured. Run setup first.")

    api_key = get_api_key(config.provider_name)
    webhooks = list_webhooks()

    archetypes = [
        {
            "slug": a.slug,
            "name": a.name,
            "one_line": a.one_line,
            "traits": a.traits,
            "response_style_blurb": a.response_style_blurb,
        }
        for a in list_archetypes()
    ]

    return {
        "archetype_slug": config.archetype_slug,
        "archetype_name": config.archetype_name,
        "provider_name": config.provider_name,
        "autonomy_level": config.autonomy_level,
        "api_key_set": api_key is not None,
        "slack_configured": len(webhooks) > 0,
        "archetypes": archetypes,
    }


class AutonomyRequest(BaseModel):
    level: int
    acknowledged: bool = False  # must be True for levels 3 and 4


@router.post("/autonomy")
def set_autonomy(body: AutonomyRequest):
    if body.level not in (1, 2, 3, 4):
        raise HTTPException(status_code=400, detail="Level must be 1, 2, 3, or 4.")
    if body.level in (3, 4) and not body.acknowledged:
        from exec_in_a_box.autonomy import get_acknowledgment_text
        return {
            "requires_acknowledgment": True,
            "level": body.level,
            "acknowledgment_text": get_acknowledgment_text(body.level),
        }
    config = load_config()
    if config is None:
        raise HTTPException(status_code=404, detail="Not configured.")
    save_autonomy_level(body.level)
    return {"autonomy_level": body.level, "requires_acknowledgment": False}


class ArchetypeRequest(BaseModel):
    slug: str


@router.post("/archetype")
def set_archetype(body: ArchetypeRequest):
    archetypes = {a.slug: a for a in list_archetypes()}
    chosen = archetypes.get(body.slug)
    if chosen is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown archetype slug: {body.slug}",
        )

    text = storage.read_file("board/config.md")
    if text is None:
        raise HTTPException(status_code=404, detail="Not configured.")

    text = re.sub(r"^slug:.*$", f"slug: {chosen.slug}", text, flags=re.MULTILINE)
    text = re.sub(r"^name:.*$", f"name: {chosen.name}", text, flags=re.MULTILINE)
    storage.write_file("board/config.md", text)

    return {"archetype_slug": chosen.slug, "archetype_name": chosen.name}
