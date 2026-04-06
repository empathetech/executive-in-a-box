"""Autonomy level enforcement and action type registry.

Level 3 (Delegated): auto-approve low-stakes actions per action type registry.
Level 4 (Autonomous): act on conclusions within scope, full async audit log.

Levels 3 and 4 require explicit acknowledgment before enabling.

HARD RULE: The action types listed in ALWAYS_REQUIRE_APPROVAL can never
be approved automatically, regardless of autonomy level. This is enforced
in code, not configuration.

Reference: hacky-hours/02-design/ARCHITECTURE.md § Autonomy Model
Reference: hacky-hours/02-design/BUSINESS_LOGIC.md § Autonomy Level Contract
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum

from exec_in_a_box import storage


class AutonomyLevel(IntEnum):
    ADVISOR = 1
    RECOMMENDER = 2
    DELEGATED = 3
    AUTONOMOUS = 4


# Action types that ALWAYS require user approval, regardless of autonomy level.
# These are hard-coded and cannot be overridden by configuration.
ALWAYS_REQUIRE_APPROVAL: frozenset[str] = frozenset(
    {
        "external_api_call",       # any call to an external API
        "file_write_outside_data", # writing outside the data directory
        "send_email",              # sending any email
        "financial_transaction",   # any financial action
        "publish_content",         # posting to social media, websites, etc.
        "modify_config",           # changing tool configuration
        "delete_data",             # deleting any user data
    }
)

# Action types auto-approved at Level 3 (Delegated).
# All other action types require approval even at Level 3.
AUTO_APPROVE_AT_LEVEL_3: frozenset[str] = frozenset(
    {
        "log_decision",         # writing to decisions.md
        "save_session",         # saving session transcript
        "update_memory",        # updating memory/strategic-context.md
        "flag_open_question",   # adding to memory/open-questions.md
    }
)


@dataclass
class ActionRequest:
    """A request to take an action on behalf of the user."""

    action_type: str
    description: str
    archetype_slug: str
    autonomy_level: AutonomyLevel


@dataclass
class ActionDecision:
    """The outcome of evaluating an action request."""

    approved: bool
    reason: str
    requires_user_confirmation: bool = False


def evaluate_action(request: ActionRequest) -> ActionDecision:
    """Evaluate whether an action can proceed given the current autonomy level.

    Always blocks actions in ALWAYS_REQUIRE_APPROVAL.
    At Level 1-2: all actions require user confirmation.
    At Level 3: AUTO_APPROVE_AT_LEVEL_3 actions are approved automatically.
    At Level 4: all actions within scope are approved automatically.
    """
    # Hard block — no exceptions
    if request.action_type in ALWAYS_REQUIRE_APPROVAL:
        return ActionDecision(
            approved=False,
            reason=(
                f"Action '{request.action_type}' always requires user approval "
                f"regardless of autonomy level."
            ),
            requires_user_confirmation=True,
        )

    if request.autonomy_level <= AutonomyLevel.RECOMMENDER:
        return ActionDecision(
            approved=False,
            reason="At autonomy levels 1-2, all actions require user confirmation.",
            requires_user_confirmation=True,
        )

    if request.autonomy_level == AutonomyLevel.DELEGATED:
        if request.action_type in AUTO_APPROVE_AT_LEVEL_3:
            return ActionDecision(
                approved=True,
                reason=f"Auto-approved at Level 3 (Delegated): {request.action_type}",
            )
        return ActionDecision(
            approved=False,
            reason=(
                f"Action '{request.action_type}' is not in the auto-approve list "
                f"for Level 3. User confirmation required."
            ),
            requires_user_confirmation=True,
        )

    # Level 4 — Autonomous
    return ActionDecision(
        approved=True,
        reason=f"Auto-approved at Level 4 (Autonomous): {request.action_type}",
    )


def write_audit_log(
    archetype_slug: str,
    action_type: str,
    description: str,
    approved: bool,
    reason: str,
) -> None:
    """Append an entry to the audit log.

    The audit log is always written regardless of autonomy level.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    status = "APPROVED" if approved else "BLOCKED"
    entry = (
        f"\n## {timestamp}\n\n"
        f"**Archetype:** {archetype_slug}\n"
        f"**Action:** {action_type}\n"
        f"**Description:** {description}\n"
        f"**Status:** {status}\n"
        f"**Reason:** {reason}\n"
    )
    storage.append_file("audit.log.md", entry)


# ---- Acknowledgment flow ----

ACKNOWLEDGMENT_TEXT_LEVEL_3 = """\
LEVEL 3 — DELEGATED AUTONOMY

At this level, the CEO will automatically:
  - Log decisions to your decisions file
  - Save session transcripts
  - Update strategic memory
  - Flag open questions

The CEO will still ask for your confirmation before:
  - Any external API call
  - Any file write outside the data directory
  - Sending emails, posts, or messages
  - Any financial action
  - Any change to your configuration

Type CONFIRM to enable Level 3 for this archetype, or press Enter to cancel:
"""

ACKNOWLEDGMENT_TEXT_LEVEL_4 = """\
LEVEL 4 — AUTONOMOUS

At this level, the CEO will automatically act on its conclusions within scope.
A full audit log is always available.

IMPORTANT: The following action types ALWAYS require your approval regardless
of autonomy level and cannot be delegated:
  - External API calls
  - File writes outside the data directory
  - Sending emails, posts, or messages
  - Financial transactions
  - Configuration changes
  - Deleting data

Type CONFIRM to enable Level 4 for this archetype, or press Enter to cancel:
"""


def get_acknowledgment_text(level: int) -> str | None:
    """Return the acknowledgment text for a given level, or None if not needed."""
    if level == 3:
        return ACKNOWLEDGMENT_TEXT_LEVEL_3
    if level == 4:
        return ACKNOWLEDGMENT_TEXT_LEVEL_4
    return None
