"""Per-CEO decision statistics parsed from session transcripts.

Each session file is parsed to extract: archetype name, decision outcome
(Adopted/Rejected/Modified), confidence, and ambition level. These are
aggregated per CEO and exposed via the /api/stats endpoint and cmd_usage.
"""
from __future__ import annotations

import re
from pathlib import Path

from exec_in_a_box import storage
from exec_in_a_box.archetypes import list_archetypes

CONFIDENCE_SCORE: dict[str, float] = {
    "high": 1.0,
    "medium": 0.67,
    "low": 0.33,
}

AMBITION_SCORE: dict[str, float] = {
    "conservative": 0.25,
    "moderate": 0.5,
    "bold": 0.75,
    "visionary": 1.0,
}


def _parse_session(path: Path) -> dict | None:
    """Parse one session file. Returns a record dict or None if unparseable."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    ts_match = re.search(r"# Session — (.+)", text)
    timestamp = ts_match.group(1).strip() if ts_match else ""

    # Prefer the explicit slug field (written since the slug-tracking fix).
    # Fall back to the section header for older session files.
    slug_match = re.search(r"\*\*Archetype:\*\*\s*(\S+)", text)
    archetype_slug = slug_match.group(1).strip() if slug_match else ""

    arch_match = re.search(r"## (.+?)'s Response", text)
    archetype = arch_match.group(1).strip() if arch_match else ""

    q_match = re.search(r"## Question\n(.+?)(?=\n##)", text, re.DOTALL)
    question = q_match.group(1).strip() if q_match else ""

    pos_match = re.search(r"\*\*Position:\*\*\s*(.+?)(?=\n\n|\Z)", text, re.DOTALL)
    position = pos_match.group(1).strip() if pos_match else ""

    conf_match = re.search(r"\*\*Confidence:\*\*\s*(.+)", text)
    confidence = conf_match.group(1).strip().lower() if conf_match else ""

    amb_match = re.search(r"\*\*Ambition level:\*\*\s*(.+)", text)
    ambition_level = amb_match.group(1).strip().lower() if amb_match else ""

    dec_match = re.search(r"## Decision\n(.+?)(?:\n|$)", text)
    decision = dec_match.group(1).strip() if dec_match else ""

    mod_match = re.search(r"\*\*Modification:\*\*\s*(.+)", text)
    modification = mod_match.group(1).strip() if mod_match else ""

    if (not archetype and not archetype_slug) or not decision:
        return None

    return {
        "timestamp": timestamp,
        "archetype": archetype,
        "archetype_slug": archetype_slug,
        "question": question[:120],
        "position": position[:200],
        "decision": decision,
        "modification": modification,
        "confidence": confidence,
        "ambition_level": ambition_level,
    }


def get_ceo_stats() -> tuple[list[dict], int]:
    """Return (per-CEO stats list, total session count).

    Reads from sessions/index.json (reliable slug-keyed records written by code).
    Falls back to parsing individual session files for unindexed sessions.

    Each CEO stats dict contains:
      slug, name, total, adopted, rejected, modified,
      agreement_rate, modification_rate, rejection_rate,
      avg_confidence, avg_ambition, usage_share, recent_decisions (last 5)
    """
    # ── Indexed sessions (reliable) ──────────────────────────────────────────
    index = storage.read_session_index()
    indexed_ids: set[str] = {e["id"] for e in index}

    # ── Unindexed session files (fallback parsing) ───────────────────────────
    sessions = storage.list_sessions()
    for path in sessions:
        if path.stem in indexed_ids:
            continue
        r = _parse_session(path)
        if r and r.get("archetype_slug"):
            index.append({
                "id": path.stem,
                "slug": r["archetype_slug"],
                "timestamp": r["timestamp"],
                "decision": r["decision"],
                "question": r["question"],
                "position": r["position"],
                "confidence": r["confidence"],
                "ambition_level": r["ambition_level"],
            })

    archetypes = list_archetypes()
    max_total = max((sum(1 for e in index if e.get("slug") == a.slug) for a in archetypes), default=1)

    stats: list[dict] = []
    for arch in archetypes:
        ceo_records = [e for e in index if e.get("slug") == arch.slug]
        total = len(ceo_records)

        adopted = sum(1 for r in ceo_records if r["decision"] == "Adopted")
        rejected = sum(1 for r in ceo_records if r["decision"] == "Rejected")
        modified = sum(1 for r in ceo_records if r["decision"] == "Modified")

        conf_scores = [
            CONFIDENCE_SCORE[r["confidence"]]
            for r in ceo_records
            if r["confidence"] in CONFIDENCE_SCORE
        ]
        avg_confidence = sum(conf_scores) / len(conf_scores) if conf_scores else 0.0

        amb_scores = [
            AMBITION_SCORE[r["ambition_level"]]
            for r in ceo_records
            if r["ambition_level"] in AMBITION_SCORE
        ]
        avg_ambition = sum(amb_scores) / len(amb_scores) if amb_scores else 0.0

        stats.append({
            "slug": arch.slug,
            "name": arch.name,
            "total": total,
            "adopted": adopted,
            "rejected": rejected,
            "modified": modified,
            "agreement_rate": round(adopted / total, 3) if total else 0.0,
            "modification_rate": round(modified / total, 3) if total else 0.0,
            "rejection_rate": round(rejected / total, 3) if total else 0.0,
            "avg_confidence": round(avg_confidence, 3),
            "avg_ambition": round(avg_ambition, 3),
            # Normalized usage (0-1) for radar axis
            "usage_share": round(total / max_total, 3) if max_total else 0.0,
            # Last 5 decisions, most recent first
            "recent_decisions": list(reversed(ceo_records[-5:])),
        })

    return stats, len(index)
