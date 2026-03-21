"""Configuration loading.

Reads board/config.md to determine the active archetype, provider, and
autonomy level. API keys are NOT stored in this file — they live in
the OS keychain via the credentials module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from exec_in_a_box import storage


@dataclass
class BoardConfig:
    """Parsed board configuration."""

    archetype_slug: str
    archetype_name: str
    provider_name: str
    autonomy_level: int


def _extract(text: str, key: str) -> str | None:
    """Extract a value from 'key: value' format in markdown."""
    match = re.search(
        rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE
    )
    return match.group(1).strip() if match else None


def load_config() -> BoardConfig | None:
    """Load the board configuration. Returns None if not configured."""
    text = storage.read_file("board/config.md")
    if text is None:
        return None

    slug = _extract(text, "slug")
    name = _extract(text, "name")
    provider = _extract(text, "provider")
    level_str = _extract(text, "level")

    if not all([slug, name, provider, level_str]):
        return None

    try:
        level = int(level_str)
    except (ValueError, TypeError):
        level = 1

    return BoardConfig(
        archetype_slug=slug,
        archetype_name=name,
        provider_name=provider,
        autonomy_level=level,
    )


def save_autonomy_level(level: int) -> None:
    """Update the autonomy level in config."""
    from datetime import datetime

    text = storage.read_file("board/config.md")
    if text is None:
        return

    new_text = re.sub(
        r"^level:\s*\d+",
        f"level: {level}",
        text,
        flags=re.MULTILINE,
    )

    timestamp = datetime.now().isoformat(timespec="seconds")
    new_text += (
        f"\n# Autonomy changed to level {level} "
        f"at {timestamp}\n"
    )

    storage.write_file("board/config.md", new_text)
