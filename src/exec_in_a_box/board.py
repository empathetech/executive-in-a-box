"""Board of Directors engine.

Collects independent responses from multiple CEO archetypes in parallel
and aggregates them into a board deliberation result.

Reference: hacky-hours/02-design/ARCHITECTURE.md § Board of Directors Engine
"""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass, field

from exec_in_a_box.archetypes import Archetype, get_archetype, list_archetypes
from exec_in_a_box.providers import ProviderError, create_provider
from exec_in_a_box.wrapper import (
    ValidatedResponse,
    build_prompt,
    validate_response,
)


@dataclass
class MemberResult:
    """Result from a single board member."""

    archetype: Archetype
    response: ValidatedResponse | None
    error: str | None = None


@dataclass
class BoardResult:
    """Aggregated result from the full board deliberation."""

    members: list[MemberResult]
    common_ground: list[str] = field(default_factory=list)
    spectrum: list[tuple[str, str]] = field(default_factory=list)  # (slug, ambition_level)
    aggregated_pros: list[str] = field(default_factory=list)
    aggregated_cons: list[str] = field(default_factory=list)
    synthesis: str | None = None
    errors: list[str] = field(default_factory=list)


def _call_one(
    archetype_slug: str,
    question: str,
    provider_name: str,
    api_key: str,
) -> MemberResult:
    """Call a single archetype. Designed to run in a thread pool."""
    archetype = get_archetype(archetype_slug)
    if archetype is None:
        return MemberResult(
            archetype=get_archetype("operator") or list_archetypes()[0],
            response=None,
            error=f"Unknown archetype: {archetype_slug}",
        )

    try:
        system_prompt, user_message, _ = build_prompt(archetype, question)
        provider = create_provider(provider_name, api_key=api_key)
        raw = provider.send(system_prompt, user_message)
        result = validate_response(raw.content)

        if isinstance(result, list):
            return MemberResult(
                archetype=archetype,
                response=None,
                error=f"Validation failed: {result[0].message}",
            )
        return MemberResult(archetype=archetype, response=result)
    except ProviderError as e:
        return MemberResult(archetype=archetype, response=None, error=e.user_message)
    except Exception as e:
        return MemberResult(archetype=archetype, response=None, error=str(e))


def _find_common_ground(responses: list[ValidatedResponse]) -> list[str]:
    """Find pros that appear across multiple members.

    A simple heuristic: find keywords that appear in at least 2 member positions.
    Returns a summary, not an exhaustive list.
    """
    if len(responses) < 2:
        return []

    # Collect all positions as a set of significant words
    all_positions = [r.position.lower() for r in responses]
    common: list[str] = []

    # Find shared pro themes (simple keyword overlap)
    for i, resp in enumerate(responses):
        for pro in resp.pros:
            pro_lower = pro.lower()
            # Check if any other member shares this theme
            for j, other in enumerate(responses):
                if i != j and any(
                    word in other.position.lower() or
                    any(word in p.lower() for p in other.pros)
                    for word in pro_lower.split()
                    if len(word) > 5
                ):
                    if pro not in common:
                        common.append(pro)
                    break

    return common[:5]  # Cap at 5 items


AMBITION_ORDER = [
    "very_cautious", "cautious", "moderate", "ambitious", "very_ambitious"
]


def _build_spectrum(results: list[MemberResult]) -> list[tuple[str, str]]:
    """Sort members along the cautious → ambitious spectrum."""
    members_with_ambition = [
        (r.archetype.slug, r.response.ambition_level)
        for r in results
        if r.response is not None
    ]
    return sorted(
        members_with_ambition,
        key=lambda x: AMBITION_ORDER.index(x[1]) if x[1] in AMBITION_ORDER else 2,
    )


def _aggregate_pros_cons(responses: list[ValidatedResponse]) -> tuple[list[str], list[str]]:
    """Collect all pros and cons, deduplicating by rough similarity."""
    seen_pros: set[str] = set()
    seen_cons: set[str] = set()
    pros: list[str] = []
    cons: list[str] = []

    for r in responses:
        for p in r.pros:
            key = p.lower()[:40]
            if key not in seen_pros:
                seen_pros.add(key)
                pros.append(f"[{r.archetype}] {p}")
        for c in r.cons:
            key = c.lower()[:40]
            if key not in seen_cons:
                seen_cons.add(key)
                cons.append(f"[{r.archetype}] {c}")

    return pros, cons


def run_board(
    slugs: list[str],
    question: str,
    provider_name: str,
    api_key: str,
    max_workers: int = 4,
) -> BoardResult:
    """Run the full board deliberation in parallel.

    Each archetype is called independently in a thread pool (rate-limit
    safe — max_workers controls concurrency).
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_call_one, slug, question, provider_name, api_key): slug
            for slug in slugs
        }
        members: list[MemberResult] = []
        for future in concurrent.futures.as_completed(futures):
            try:
                members.append(future.result())
            except Exception as e:
                slug = futures[future]
                arch = get_archetype(slug) or list_archetypes()[0]
                members.append(MemberResult(archetype=arch, response=None, error=str(e)))

    successful = [m for m in members if m.response is not None]
    responses = [m.response for m in successful if m.response is not None]

    common = _find_common_ground(responses)
    spectrum = _build_spectrum(members)
    pros, cons = _aggregate_pros_cons(responses)
    errors = [f"{m.archetype.slug}: {m.error}" for m in members if m.error]

    return BoardResult(
        members=members,
        common_ground=common,
        spectrum=spectrum,
        aggregated_pros=pros,
        aggregated_cons=cons,
        errors=errors,
    )
