"""Slack API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/slack", tags=["slack"])


class AnnounceRequest(BaseModel):
    message: str
    webhook_id: str
    archetype_slug: str | None = None


@router.get("/channels")
def get_channels():
    from exec_in_a_box.slack import list_webhooks
    webhooks = list_webhooks()
    return {"channels": [{"id": w["id"], "workspace": w["workspace"], "channel": w["channel"]} for w in webhooks]}


@router.post("/announce")
def announce(body: AnnounceRequest):
    from exec_in_a_box.slack import send_message, get_webhook
    from exec_in_a_box.archetypes import get_archetype
    webhook = get_webhook(body.webhook_id)
    if webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found.")
    arch = get_archetype(body.archetype_slug) if body.archetype_slug else None
    success = send_message(
        body.message,
        webhook_id=body.webhook_id,
        archetype_slug=body.archetype_slug,
        archetype_name=arch.name if arch else None,
    )
    if not success:
        raise HTTPException(status_code=502, detail="Slack returned an error.")
    return {"sent": True}
