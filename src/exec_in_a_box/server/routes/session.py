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


class MessageRequest(BaseModel):
    message: str
    archetype_slug: str | None = None  # defaults to configured archetype
    executize: bool = False


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
        result = await _run_llm(slug, body.message)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=e.user_message)
