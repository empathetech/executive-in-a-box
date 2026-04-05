"""Session message API routes.

POST /api/session/message
  - executize=false: runs LLM call in thread pool, returns validated response
  - executize=true:  dispatches background job, returns job_id immediately

Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Session Message Flow
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from exec_in_a_box.archetypes import get_archetype
from exec_in_a_box.config import load_config
from exec_in_a_box.credentials import get_api_key
from exec_in_a_box.jobs import create_job, dispatch
from exec_in_a_box.providers import ProviderError, create_provider
from exec_in_a_box.wrapper import build_prompt, validate_response

router = APIRouter(prefix="/api/session", tags=["session"])


class ModificationContext(BaseModel):
    original_position: str
    feedback: str


class MessageRequest(BaseModel):
    message: str
    archetype_slug: str | None = None  # defaults to configured archetype
    executize: bool = False
    modification_context: ModificationContext | None = None


def _build_modification_message(original_question: str, original_position: str, feedback: str) -> str:
    """Construct the user message for a modify re-run."""
    return (
        f"I previously asked you:\n{original_question}\n\n"
        f"Your response was:\n{original_position}\n\n"
        f"I have feedback on this response:\n{feedback}\n\n"
        "Please revise your position based on my feedback. "
        "Use the same JSON response format."
    )


async def _run_llm(archetype_slug: str, message: str) -> dict:
    """Run an LLM call in a thread pool (providers are synchronous)."""
    config = load_config()
    if config is None:
        raise ValueError("Not configured. Run setup first.")

    slug = archetype_slug or config.archetype_slug
    archetype = get_archetype(slug)
    if archetype is None:
        raise ValueError(f"Unknown archetype: {slug}")

    api_key = get_api_key(config.provider_name)
    if api_key is None:
        raise ValueError(f"No API key for provider: {config.provider_name}")

    system_prompt, user_message, secret_matches = build_prompt(archetype, message)

    # Inject feedback calibration if available — this is the grading feedback loop
    from exec_in_a_box.server.routes.feedback import _load as _load_feedback
    fb = _load_feedback(slug)
    if fb and fb.get("active", True) and fb.get("system_prompt_addon"):
        system_prompt = system_prompt + "\n\n" + fb["system_prompt_addon"]

    def _call():
        provider = create_provider(config.provider_name, api_key=api_key)
        return provider.send(system_prompt, user_message)

    response = await asyncio.to_thread(_call)

    result = validate_response(response.content)
    if isinstance(result, list):
        # Validation errors — return raw content with a flag
        return {
            "valid": False,
            "raw_content": response.content,
            "validation_errors": [
                {"field": e.field, "message": e.message} for e in result
            ],
            "model": response.model,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "secret_warnings": len(secret_matches),
        }

    # Save artifact server-side if the LLM produced one
    artifact = result.artifact
    if artifact:
        from datetime import date
        from exec_in_a_box import storage as _storage
        session_id = date.today().isoformat()
        rel_path = f"artifacts/{session_id}/{artifact['filename']}"
        _storage.write_file(rel_path, artifact["content"])

    return {
        "valid": True,
        "archetype": result.archetype,
        "position": result.position,
        "reasoning": result.reasoning,
        "confidence": result.confidence,
        "ambition_level": result.ambition_level,
        "pros": result.pros,
        "cons": result.cons,
        "flags": result.flags,
        "questions_for_user": result.questions_for_user,
        "artifact": artifact,
        "model": response.model,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
        "secret_warnings": len(secret_matches),
    }


@router.post("/message")
async def post_message(body: MessageRequest):
    config = load_config()
    if config is None:
        raise HTTPException(status_code=503, detail="Not configured. Run setup first.")

    slug = body.archetype_slug or config.archetype_slug

    if body.executize:
        # Dispatch background job and return immediately
        job = create_job(archetype_name=slug, prompt=body.message)

        async def _job_runner(prompt: str) -> str:
            result = await _run_llm(slug, prompt)
            import json
            return json.dumps(result)

        await dispatch(job["id"], _job_runner, body.message)
        return {"job_id": job["id"], "status": "queued"}

    # Direct (fast) path — run inline and return
    try:
        if body.modification_context:
            effective_message = _build_modification_message(
                body.message,
                body.modification_context.original_position,
                body.modification_context.feedback,
            )
        else:
            effective_message = body.message
        result = await _run_llm(slug, effective_message)
        if body.modification_context:
            result["is_modification"] = True
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=e.user_message)


class DecisionRequest(BaseModel):
    archetype_slug: str
    question: str
    position: str
    confidence: str = ""
    ambition_level: str = ""
    decision: str  # "adopted" | "rejected" | "modified"
    modification: str | None = None
    reason: str | None = None       # optional reason for adopt/reject
    is_modification: bool = False   # true when this decision follows a Modify re-run


@router.post("/decision")
def post_decision(body: DecisionRequest):
    from datetime import datetime
    from exec_in_a_box import storage
    from exec_in_a_box.archetypes import get_archetype as _get_archetype

    arch = _get_archetype(body.archetype_slug)
    archetype_name = arch.name if arch else body.archetype_slug

    # Normalise decision text
    decision_map = {
        "adopted": "Adopted",
        "rejected": "Rejected",
        "modified": "Modified",
    }
    decision_text = decision_map.get(body.decision.lower(), body.decision.capitalize())

    now = datetime.now()
    timestamp = now.isoformat(timespec="seconds")

    # Build markdown entry
    lines = [
        f"## {timestamp}",
        "",
        f"**Question:** {body.question}",
        "",
        f"**Advisor:** {archetype_name} (confidence: {body.confidence})",
        "",
        f"**Position:** {body.position}",
        "",
        f"**Decision:** {decision_text}",
    ]
    if body.modification:
        lines += ["", f"**Modification:** {body.modification}"]
    if body.reason:
        lines += ["", f"**Reason:** {body.reason}"]
    if body.is_modification:
        lines += ["", "*(This was a revised response following a Modify re-run)*"]
    lines += ["", "---", ""]

    storage.append_file("org/decisions.md", "\n".join(lines))

    # Append to session index
    entry_id = f"web-{now.strftime('%Y%m%d-%H%M%S')}"
    storage.append_session_index({
        "id": entry_id,
        "slug": body.archetype_slug,
        "timestamp": timestamp,
        "decision": decision_text,
        "question": body.question,
        "position": body.position,
        "confidence": body.confidence,
        "ambition_level": body.ambition_level,
        "reason": body.reason or "",
        "is_modification": body.is_modification,
    })

    return {"recorded": True, "decision": decision_text}
