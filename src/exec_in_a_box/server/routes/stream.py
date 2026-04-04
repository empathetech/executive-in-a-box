"""SSE streaming routes for job state notifications.

GET /api/stream/jobs/{id}
  Opens a server-sent event stream. The server polls job state and pushes
  events when it changes. Closes automatically when the job reaches a
  terminal state (complete or failed).

Reference: hacky-hours/02-design/ARCHITECTURE.md § Job System
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from exec_in_a_box import jobs as job_system

router = APIRouter(prefix="/api/stream", tags=["stream"])

_POLL_INTERVAL = 0.5  # seconds


@router.get("/jobs/{job_id}")
async def stream_job(job_id: str):
    async def _event_generator():
        last_status = None
        while True:
            job = job_system.get_job(job_id)
            if job is None:
                yield {"event": "error", "data": json.dumps({"error": "Job not found"})}
                break

            status = job["status"]
            if status != last_status:
                last_status = status
                yield {"event": "state", "data": json.dumps(job)}

            if status in ("complete", "failed"):
                break

            await asyncio.sleep(_POLL_INTERVAL)

    return EventSourceResponse(_event_generator())
