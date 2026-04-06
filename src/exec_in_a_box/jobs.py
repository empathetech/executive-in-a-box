"""Async job system for deep-work (Executizing) tasks.

Jobs are background tasks assigned to a CEO archetype. While a job runs,
other archetypes remain fully interactive. Job state is persisted to
~/.executive-in-a-box/jobs/<job-id>.json.

States: queued → running → complete | failed

Reference: hacky-hours/02-design/ARCHITECTURE.md § Job System
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

from exec_in_a_box import storage

# In-memory registry of running asyncio tasks (keyed by job id)
_running_tasks: dict[str, asyncio.Task] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(archetype_name: str, prompt: str) -> dict:
    """Create a new job record in queued state and persist it."""
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "archetype": archetype_name,
        "prompt": prompt,
        "status": "queued",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "result": None,
        "error": None,
    }
    _persist(job)
    return job


def get_job(job_id: str) -> dict | None:
    """Load a job record from disk. Returns None if not found."""
    return storage.read_json(f"jobs/{job_id}.json")


def list_jobs() -> list[dict]:
    """Return all job records, newest first."""
    jobs_dir = storage.get_data_dir() / "jobs"
    if not jobs_dir.exists():
        return []
    records = []
    for path in sorted(jobs_dir.glob("*.json"), reverse=True):
        try:
            import json
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return records


def _persist(job: dict) -> None:
    job["updated_at"] = _now_iso()
    storage.write_json(f"jobs/{job['id']}.json", job)


async def dispatch(
    job_id: str,
    run_fn: Any,  # async callable(prompt: str) -> str
    prompt: str,
) -> None:
    """Dispatch a job as a background asyncio task.

    run_fn must be an async callable that accepts (prompt: str) and returns
    the result string. Typically wraps a provider call via asyncio.to_thread.
    """
    job = get_job(job_id)
    if job is None:
        return

    job["status"] = "running"
    _persist(job)

    async def _run():
        try:
            result = await run_fn(prompt)
            job["status"] = "complete"
            job["result"] = result
        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)
        finally:
            _persist(job)
            _running_tasks.pop(job_id, None)

    task = asyncio.create_task(_run())
    _running_tasks[job_id] = task


def cancel_job(job_id: str) -> bool:
    """Cancel a running job. Returns True if a task was found and cancelled."""
    task = _running_tasks.get(job_id)
    if task and not task.done():
        task.cancel()
        job = get_job(job_id)
        if job:
            job["status"] = "failed"
            job["error"] = "Cancelled by user."
            _persist(job)
        return True
    return False
