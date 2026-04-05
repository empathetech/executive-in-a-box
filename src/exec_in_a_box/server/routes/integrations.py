"""LLM integrations API routes.

GET    /api/integrations/llm               — list all known providers + key status
POST   /api/integrations/llm/{provider}/key — save/update API key for a provider
DELETE /api/integrations/llm/{provider}/key — remove API key for a provider
POST   /api/integrations/llm/active         — switch the active provider
"""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from exec_in_a_box.providers import PROVIDERS

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

# Provider display metadata
_PROVIDER_META: dict[str, dict] = {
    "anthropic": {"label": "Anthropic (Claude)", "needs_key": True},
    "openai":    {"label": "OpenAI (GPT)",       "needs_key": True},
    "ollama":    {"label": "Ollama (local)",      "needs_key": False},
}


@router.get("/llm")
def list_llm_providers():
    """Return all known LLM providers with key status and which is active."""
    from exec_in_a_box.config import load_config
    from exec_in_a_box.credentials import get_api_key

    config = load_config()
    active = config.provider_name if config else None

    providers = []
    for slug in PROVIDERS:
        meta = _PROVIDER_META.get(slug, {"label": slug, "needs_key": True})
        key_set = (not meta["needs_key"]) or (get_api_key(slug) is not None)
        providers.append({
            "slug": slug,
            "label": meta["label"],
            "needs_key": meta["needs_key"],
            "key_set": key_set,
            "active": slug == active,
        })

    return {"providers": providers}


class ApiKeyBody(BaseModel):
    api_key: str


@router.post("/llm/{provider}/key")
def set_llm_key(provider: str, body: ApiKeyBody):
    """Save (or update) an API key for a provider."""
    from exec_in_a_box.credentials import store_api_key

    if provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
    meta = _PROVIDER_META.get(provider, {})
    if not meta.get("needs_key", True):
        raise HTTPException(status_code=400, detail=f"{provider} does not use an API key.")
    if not body.api_key.strip():
        raise HTTPException(status_code=400, detail="api_key cannot be empty.")

    store_api_key(provider, body.api_key.strip())
    return {"saved": True, "provider": provider}


@router.delete("/llm/{provider}/key")
def delete_llm_key(provider: str):
    """Remove the API key for a provider."""
    from exec_in_a_box.credentials import delete_api_key

    if provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
    delete_api_key(provider)
    return {"deleted": True, "provider": provider}


class ActiveProviderBody(BaseModel):
    provider: str


@router.post("/llm/active")
def set_active_provider(body: ActiveProviderBody):
    """Switch the active LLM provider (updates board/config.md)."""
    from exec_in_a_box import storage
    from exec_in_a_box.credentials import get_api_key

    if body.provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {body.provider}")

    meta = _PROVIDER_META.get(body.provider, {})
    if meta.get("needs_key", True) and get_api_key(body.provider) is None:
        raise HTTPException(
            status_code=400,
            detail=f"No API key set for {body.provider}. Add a key first.",
        )

    text = storage.read_file("board/config.md")
    if text is None:
        raise HTTPException(status_code=404, detail="Not configured.")

    updated = re.sub(r"^provider:\s*.+$", f"provider: {body.provider}", text, flags=re.MULTILINE)
    storage.write_file("board/config.md", updated)

    return {"active": body.provider}
