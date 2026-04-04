"""All-hands meeting facilitation.

Phases:
  1. Context gather — load relevant org context and prompt user for agenda items
  2. Agenda — synthesize context into a structured agenda
  3. Facilitation — each archetype weighs in on each agenda item
  4. Summary — synthesize all positions into a meeting summary
  5. Decisions log — write decisions to org/decisions.md

Reference: hacky-hours/02-design/ARCHITECTURE.md § Autonomy Model
"""

from __future__ import annotations

from dataclasses import dataclass, field

from exec_in_a_box.archetypes import list_archetypes
from exec_in_a_box.board import run_board
from exec_in_a_box.wrapper import load_org_context


@dataclass
class AgendaItem:
    title: str
    context: str | None = None


@dataclass
class AllHandsResult:
    agenda: list[AgendaItem]
    item_results: dict[str, object]  # title -> BoardResult
    summary: str
    decisions: list[str] = field(default_factory=list)


def gather_context() -> str:
    """Load org context for the meeting."""
    return load_org_context()


def build_agenda(items: list[str], org_context: str) -> list[AgendaItem]:
    """Build a structured agenda from raw item strings."""
    return [AgendaItem(title=item, context=org_context) for item in items if item.strip()]


def facilitate(
    agenda: list[AgendaItem],
    provider_name: str,
    api_key: str,
    archetype_slugs: list[str] | None = None,
) -> AllHandsResult:
    """Run the full all-hands facilitation.

    Each agenda item is a full board deliberation. Results are collected
    and summarized.
    """
    slugs = archetype_slugs or [a.slug for a in list_archetypes()]
    item_results: dict[str, object] = {}

    for item in agenda:
        question = item.title
        if item.context:
            question += f"\n\nContext:\n{item.context}"
        result = run_board(slugs, question, provider_name, api_key)
        item_results[item.title] = result

    # Build a plain-language summary
    lines = ["# All-Hands Meeting Summary\n"]
    decisions: list[str] = []

    for item in agenda:
        result = item_results.get(item.title)
        if result is None:
            continue
        lines.append(f"## {item.title}\n")

        from exec_in_a_box.board import BoardResult
        if isinstance(result, BoardResult):
            if result.common_ground:
                lines.append("**Common ground:**")
                for cg in result.common_ground:
                    lines.append(f"- {cg}")
                lines.append("")

            if result.spectrum:
                spectrum_str = " → ".join(
                    f"{s} ({a.replace('_', ' ')})" for s, a in result.spectrum
                )
                lines.append(f"**Spectrum:** {spectrum_str}\n")

            # Surface first successful member position as tentative decision
            for m in result.members:
                if m.response:
                    decisions.append(f"{item.title}: {m.response.position[:100]}")
                    break

    summary = "\n".join(lines)
    return AllHandsResult(
        agenda=agenda,
        item_results=item_results,
        summary=summary,
        decisions=decisions,
    )


def save_all_hands_log(result: AllHandsResult) -> None:
    """Save the all-hands summary and decisions to storage."""
    from datetime import datetime
    from exec_in_a_box import storage

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    storage.append_file("sessions/all-hands.md", f"\n\n{result.summary}")

    if result.decisions:
        decisions_entry = (
            f"\n## All-Hands Meeting — {timestamp}\n\n"
        )
        for d in result.decisions:
            decisions_entry += f"- {d}\n"
        storage.append_file("org/decisions.md", decisions_entry)
