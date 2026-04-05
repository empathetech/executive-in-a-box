"""Slack API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/slack", tags=["slack"])


class AnnounceRequest(BaseModel):
    message: str
    webhook_id: str
    archetype_slug: str | None = None


class WebhookCreate(BaseModel):
    workspace: str
    channel: str
    webhook_url: str


@router.get("/channels")
def get_channels():
    from exec_in_a_box.slack import list_webhooks
    webhooks = list_webhooks()
    return {"channels": [{"id": w["id"], "workspace": w["workspace"], "channel": w["channel"]} for w in webhooks]}


@router.post("/webhooks")
def add_webhook(body: WebhookCreate):
    from exec_in_a_box.slack import add_webhook as _add
    if not body.workspace.strip() or not body.channel.strip() or not body.webhook_url.strip():
        raise HTTPException(status_code=400, detail="workspace, channel, and webhook_url are required.")
    entry = _add(body.workspace.strip(), body.channel.strip(), body.webhook_url.strip())
    return {"id": entry["id"], "workspace": entry["workspace"], "channel": entry["channel"]}


@router.delete("/webhooks/{webhook_id}")
def remove_webhook(webhook_id: str):
    from exec_in_a_box.slack import remove_webhook as _remove
    removed = _remove(webhook_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Webhook not found.")
    return {"deleted": True}


@router.get("/default")
def get_default_webhook():
    """Return the current default webhook id, or null."""
    from exec_in_a_box import storage
    import json
    raw = storage.read_file("integrations/slack_default.json")
    if raw is None:
        return {"default_webhook_id": None}
    try:
        return {"default_webhook_id": json.loads(raw).get("id")}
    except Exception:
        return {"default_webhook_id": None}


class DefaultWebhookBody(BaseModel):
    webhook_id: str


@router.post("/default")
def set_default_webhook(body: DefaultWebhookBody):
    """Save the default webhook id."""
    from exec_in_a_box.slack import get_webhook
    from exec_in_a_box import storage
    import json
    if get_webhook(body.webhook_id) is None:
        raise HTTPException(status_code=404, detail="Webhook not found.")
    storage.write_file("integrations/slack_default.json", json.dumps({"id": body.webhook_id}) + "\n")
    return {"default_webhook_id": body.webhook_id}


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
