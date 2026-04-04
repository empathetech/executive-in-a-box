"""Slack announce API route.

POST /api/slack/announce — send a message to the configured Slack webhook.

The user must preview and confirm before sending (enforced in the UI).
This endpoint performs the actual send.

Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Slack Announce Flow
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from exec_in_a_box.slack import get_webhook_url, send_message

router = APIRouter(prefix="/api/slack", tags=["slack"])


class AnnounceRequest(BaseModel):
    message: str
    archetype_slug: str | None = None


@router.post("/announce")
def announce(body: AnnounceRequest):
    webhook_url = get_webhook_url()
    if webhook_url is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Slack is not configured. "
                "Run: exec-in-a-box slack setup"
            ),
        )

    try:
        success = send_message(
            message=body.message,
            archetype_slug=body.archetype_slug,
        )
        if not success:
            raise HTTPException(
                status_code=502,
                detail="Slack returned an error. Check your webhook URL.",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Slack send failed: {e}",
        )

    return {"sent": True}
