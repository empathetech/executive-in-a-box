"""CEO feedback synthesis API routes.

GET  /api/feedback/{slug}         — load current feedback (summary + trait adjustments)
POST /api/feedback/{slug}/refresh — call LLM to synthesize new feedback from decision history
DELETE /api/feedback/{slug}       — clear feedback for a CEO (revert to baseline)

The feedback loop:
  1. User makes decisions (Adopt / Reject / Modify with reasons).
  2. Clicking "Update Feedback" calls the LLM to synthesise a calibration from those decisions.
  3. The calibration is stored as a `system_prompt_addon` injected into every future prompt
     for that CEO — closing the feedback loop without requiring retraining.
  4. The feedback also carries `trait_adjustments` (±0.3 per axis) rendered as a secondary
     overlay on the personality radar chart.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from exec_in_a_box import storage
from exec_in_a_box.archetypes import TRAIT_LABELS, get_archetype

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

_FEEDBACK_DIR = "feedback"


def _feedback_path(slug: str) -> Path:
    return storage.get_data_dir() / _FEEDBACK_DIR / f"{slug}.json"


def _load(slug: str) -> dict | None:
    path = _feedback_path(slug)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save(slug: str, data: dict) -> None:
    path = _feedback_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _recent_decisions(slug: str, n: int = 20) -> list[dict]:
    """Pull the n most recent decisions for this CEO from the session index."""
    index = storage.read_session_index()
    ceo_records = [e for e in index if e.get("slug") == slug]
    return list(reversed(ceo_records[-n:]))


def _build_synthesis_prompt(archetype, decisions: list[dict]) -> str:
    trait_keys = ", ".join(f'"{t}"' for t in TRAIT_LABELS)
    decision_lines = []
    for d in decisions:
        line = (
            f"- Question: {d.get('question', '?')!r}\n"
            f"  Position: {d.get('position', '?')!r}\n"
            f"  Decision: {d.get('decision', '?')}"
        )
        if d.get("reason"):
            line += f" | Reason: {d['reason']}"
        if d.get("modification"):
            line += f" | Modification: {d['modification']}"
        decision_lines.append(line)

    decisions_block = "\n".join(decision_lines) if decision_lines else "(no decisions yet)"

    return f"""\
You are analysing feedback for an AI executive advisor to help it improve.

ADVISOR IDENTITY:
{archetype.role_definition}

REASONING STYLE:
{archetype.reasoning_style}

RECENT USER DECISIONS (most recent first):
{decisions_block}

YOUR TASK:
Analyse the patterns in these decisions. Where did the user reject or modify responses? \
What did they accept? What do the reasons and modifications tell you about what this \
advisor needs to change?

Produce ONLY valid JSON — no markdown fences, no preamble, no trailing text:
{{
  "summary": "A 1-2 sentence first-person reflection (start with I, be specific, include the opening and closing quote marks in the string itself — e.g., \\"I have learned that...\\". )",
  "trait_adjustments": {{{", ".join(f'"{t}": 0.0' for t in TRAIT_LABELS)}}},
  "system_prompt_addon": "CALIBRATION FROM USER FEEDBACK: write 3-5 concrete behavioural directives."
}}

Rules for trait_adjustments:
- Positive = increase that trait score, negative = decrease.
- Only adjust traits that the feedback directly addresses; leave others at 0.0.
- Clamp all values to [-0.3, 0.3].

Rules for system_prompt_addon:
- Start with: CALIBRATION FROM USER FEEDBACK (apply these adjustments to all future responses):
- Write specific, actionable directives. Example: "Be more concise — users have repeatedly \
rejected long answers. When uncertain, ask a clarifying question rather than hedging."
"""


@router.get("/{slug}")
def get_feedback(slug: str):
    """Return stored feedback for a CEO, or empty baseline if none exists."""
    if get_archetype(slug) is None:
        raise HTTPException(status_code=404, detail=f"Unknown archetype: {slug}")
    data = _load(slug)
    if data is None:
        return {
            "slug": slug,
            "summary": None,
            "trait_adjustments": {t: 0.0 for t in TRAIT_LABELS},
            "system_prompt_addon": None,
            "updated_at": None,
            "decision_count": len(_recent_decisions(slug)),
            "active": True,
        }
    # Back-fill active field for records written before this field existed
    data.setdefault("active", True)
    return data


@router.post("/{slug}/refresh")
async def refresh_feedback(slug: str):
    """Call the LLM to synthesise a new feedback calibration from decision history."""
    import asyncio
    from datetime import datetime, timezone

    from exec_in_a_box.config import load_config
    from exec_in_a_box.credentials import get_api_key
    from exec_in_a_box.providers import ProviderError, create_provider

    archetype = get_archetype(slug)
    if archetype is None:
        raise HTTPException(status_code=404, detail=f"Unknown archetype: {slug}")

    config = load_config()
    if config is None:
        raise HTTPException(status_code=503, detail="Not configured.")

    api_key = get_api_key(config.provider_name)
    if api_key is None:
        raise HTTPException(status_code=503, detail=f"No API key for {config.provider_name}.")

    decisions = _recent_decisions(slug, n=20)
    synthesis_prompt = _build_synthesis_prompt(archetype, decisions)

    system = (
        "You are a meta-advisor that analyses AI performance data. "
        "You respond only with valid JSON exactly as requested."
    )

    def _call():
        provider = create_provider(config.provider_name, api_key=api_key)
        return provider.send(system, synthesis_prompt)

    try:
        response = await asyncio.to_thread(_call)
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=e.user_message)

    raw = response.content.strip()
    # Strip markdown fences if the model added them anyway
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM returned malformed JSON: {e}. Raw: {raw[:200]}",
        )

    # Validate and clamp trait adjustments
    adj = parsed.get("trait_adjustments", {})
    clean_adj = {}
    for t in TRAIT_LABELS:
        v = float(adj.get(t, 0.0))
        clean_adj[t] = round(max(-0.3, min(0.3, v)), 3)

    # Preserve existing active flag if feedback already existed
    existing = _load(slug)
    result = {
        "slug": slug,
        "summary": str(parsed.get("summary", "")),
        "trait_adjustments": clean_adj,
        "system_prompt_addon": str(parsed.get("system_prompt_addon", "")),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "decision_count": len(decisions),
        "active": existing.get("active", True) if existing else True,
    }
    _save(slug, result)
    return result


@router.post("/{slug}/active")
def set_feedback_active(slug: str, body: dict):
    """Toggle whether feedback adjustments are injected into LLM requests."""
    if get_archetype(slug) is None:
        raise HTTPException(status_code=404, detail=f"Unknown archetype: {slug}")
    data = _load(slug)
    if data is None:
        raise HTTPException(status_code=404, detail="No feedback stored — synthesise feedback first.")
    data["active"] = bool(body.get("active", True))
    data.setdefault("decision_count", len(_recent_decisions(slug)))
    _save(slug, data)
    return data


@router.delete("/{slug}")
def clear_feedback(slug: str):
    """Remove stored feedback for a CEO (reverts to baseline)."""
    if get_archetype(slug) is None:
        raise HTTPException(status_code=404, detail=f"Unknown archetype: {slug}")
    path = _feedback_path(slug)
    if path.exists():
        path.unlink()
    return {"cleared": True}
