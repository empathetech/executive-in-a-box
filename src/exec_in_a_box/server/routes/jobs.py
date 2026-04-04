"""Job state API routes.

GET /api/jobs        — list all jobs (newest first)
GET /api/jobs/{id}  — get a single job by ID
DELETE /api/jobs/{id} — cancel a running job
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from exec_in_a_box import jobs as job_system

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def list_jobs():
    return {"jobs": job_system.list_jobs()}


@router.get("/{job_id}")
def get_job(job_id: str):
    job = job_system.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return job


@router.delete("/{job_id}")
def cancel_job(job_id: str):
    job = job_system.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    cancelled = job_system.cancel_job(job_id)
    return {"cancelled": cancelled}
