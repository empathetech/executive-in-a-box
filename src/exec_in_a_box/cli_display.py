"""CLI display utilities — ANSI colors, box drawing, typewriter effect.

Respects NO_COLOR env var per https://no-color.org/.

Reference: hacky-hours/02-design/STYLE_GUIDE.md § CLI Interface
"""

from __future__ import annotations

import os
import sys
import time

# Honor NO_COLOR env var
_NO_COLOR = bool(os.environ.get("NO_COLOR"))


# ---- ANSI color codes ----

class C:
    """ANSI color/style constants. Empty strings when NO_COLOR is set."""

    if _NO_COLOR:
        RESET = BOLD = DIM = ""
        CYAN = MAGENTA = LIME = YELLOW = PURPLE = RED = WHITE = ""
        BG_BLACK = ""
    else:
        RESET   = "\033[0m"
        BOLD    = "\033[1m"
        DIM     = "\033[2m"
        # Brand palette approximated in ANSI 256-color
        CYAN    = "\033[38;5;51m"    # electric cyan
        MAGENTA = "\033[38;5;198m"   # hot magenta
        LIME    = "\033[38;5;118m"   # lime zap
        YELLOW  = "\033[38;5;226m"   # solar yellow
        PURPLE  = "\033[38;5;57m"    # deep purple
        RED     = "\033[38;5;196m"   # error red
        WHITE   = "\033[38;5;255m"   # ghost white
        BG_BLACK = "\033[40m"


def colorize(text: str, *codes: str) -> str:
    """Wrap text in ANSI codes if color is enabled."""
    if _NO_COLOR or not codes:
        return text
    return "".join(codes) + text + C.RESET


# ---- Box drawing ----

def box(title: str, lines: list[str], width: int = 60) -> str:
    """Render a box with a title and content lines.

    Uses Unicode box-drawing characters, falls back to ASCII if locale
    doesn't support them (NO_COLOR doesn't affect box chars).
    """
    try:
        tl, tr, bl, br = "╔", "╗", "╚", "╝"
        h, v = "═", "║"
    except Exception:
        tl, tr, bl, br = "+", "+", "+", "+"
        h, v = "-", "|"

    inner = width - 2
    title_pad = title[:inner].center(inner)

    result = [f"{tl}{h * inner}{tr}"]
    result.append(f"{v}{colorize(title_pad, C.BOLD, C.CYAN)}{v}")
    result.append(f"{'╠' if not _NO_COLOR else '+'}{'═' * inner}{'╣' if not _NO_COLOR else '+'}")

    for line in lines:
        # Wrap long lines
        words = line.split()
        current = ""
        wrapped = []
        for word in words:
            if len(current) + len(word) + 1 <= inner - 2:
                current = current + " " + word if current else word
            else:
                if current:
                    wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)

        if not wrapped:
            result.append(f"{v}{' ' * inner}{v}")
        for w in wrapped:
            result.append(f"{v}  {w:<{inner - 2}}{v}")

    result.append(f"{bl}{h * inner}{br}")
    return "\n".join(result)


def divider(width: int = 60) -> str:
    return colorize("─" * width, C.DIM)


# ---- Typewriter effect ----

def typewrite(text: str, delay: float = 0.008) -> None:
    """Print text character-by-character for a typewriter effect.

    Skips the effect if stdout is not a TTY (e.g. piped output).
    """
    if not sys.stdout.isatty() or _NO_COLOR:
        print(text)
        return
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_banner() -> None:
    """Print the Executive in a Box ASCII banner."""
    lines = [
        colorize("  Executive in a Box", C.BOLD, C.CYAN),
        colorize("  AI-powered CEO advisory", C.DIM),
    ]
    for line in lines:
        print(line)
    print(divider())


def print_ceo_header(
    archetype_name: str,
    autonomy_level: int,
    provider: str,
    one_line: str = "",
    response_style_blurb: str = "",
    feedback: "dict | None" = None,
) -> None:
    """Print the active CEO info line."""
    level_label = {1: "Advisor", 2: "Recommender", 3: "Delegated", 4: "Autonomous"}
    print()
    print(
        colorize(f"  CEO: {archetype_name}", C.BOLD, C.WHITE)
        + colorize(f"  ·  Level {autonomy_level} ({level_label.get(autonomy_level, '?')})", C.DIM)
        + colorize(f"  ·  {provider}", C.DIM)
    )
    if one_line:
        print(colorize(f"  {one_line}", C.DIM))
    if response_style_blurb:
        print(colorize(f"  Style: {response_style_blurb}", C.DIM))
    if feedback and feedback.get("summary"):
        active = feedback.get("active", True)
        mode = colorize("● Adjusted", C.LIME) if active else colorize("○ Baseline", C.DIM)
        summary_preview = feedback["summary"][:72]
        if len(feedback["summary"]) > 72:
            summary_preview += "…"
        print(
            colorize("  Feedback: ", C.DIM)
            + mode
            + colorize(f'  "{summary_preview}"', C.DIM)
        )
    print(divider())
    print(
        colorize("  Commands: ", C.DIM)
        + colorize("/switch", C.CYAN) + colorize(" (CEO)  ", C.DIM)
        + colorize("/feedback", C.CYAN) + colorize(" (calibration)  ", C.DIM)
        + colorize("/executize", C.CYAN) + colorize(" (deep work)  ", C.DIM)
        + colorize("/quit", C.CYAN) + colorize(" (exit)", C.DIM)
    )
    print()


AMBITION_BAR = {
    "very_cautious":  ("▓░░░░", C.CYAN),
    "cautious":       ("▓▓░░░", C.CYAN),
    "moderate":       ("▓▓▓░░", C.YELLOW),
    "ambitious":      ("▓▓▓▓░", C.MAGENTA),
    "very_ambitious": ("▓▓▓▓▓", C.MAGENTA),
}


def format_response_cli(response, autonomy_level: int) -> list[str]:
    """Format a ValidatedResponse for terminal display. Returns lines."""
    bar_chars, bar_color = AMBITION_BAR.get(
        response.ambition_level, ("░░░░░", C.DIM)
    )

    lines = []

    if autonomy_level == 2:
        lines.append(colorize("  RECOMMENDATION", C.BOLD, C.LIME))
    else:
        lines.append(colorize("  POSITION", C.BOLD, C.CYAN))
    lines.append("")
    lines.append(f"  {response.position}")
    lines.append("")
    lines.append(
        colorize("  Confidence: ", C.DIM)
        + colorize(response.confidence.upper(), C.BOLD, C.WHITE)
        + colorize("  Ambition: ", C.DIM)
        + colorize(bar_chars, bar_color)
    )
    lines.append("")

    lines.append(colorize("  Pros:", C.LIME))
    for pro in response.pros:
        lines.append(colorize(f"    + ", C.LIME) + pro)
    lines.append("")

    lines.append(colorize("  Cons:", C.MAGENTA))
    for con in response.cons:
        lines.append(colorize(f"    - ", C.MAGENTA) + con)

    if response.flags:
        lines.append("")
        lines.append(colorize("  Flags:", C.YELLOW))
        for flag in response.flags:
            lines.append(colorize(f"    ! ", C.YELLOW) + flag)

    if response.questions_for_user:
        lines.append("")
        lines.append(colorize("  Questions for you:", C.CYAN))
        for q in response.questions_for_user:
            lines.append(colorize(f"    ? ", C.CYAN) + q)

    return lines


def print_response(response, autonomy_level: int, archetype_name: str) -> None:
    """Print a formatted response with typewriter effect on key fields."""
    print()
    title = f"  {archetype_name}'s Response"
    print(colorize("╔" + "═" * 58 + "╗", C.CYAN))
    print(colorize("║", C.CYAN) + colorize(title.center(58), C.BOLD, C.WHITE) + colorize("║", C.CYAN))
    print(colorize("╠" + "═" * 58 + "╣", C.CYAN))
    print()

    lines = format_response_cli(response, autonomy_level)
    for line in lines:
        print(line)

    print()
    print(colorize("╚" + "═" * 58 + "╝", C.CYAN))


def print_thinking(archetype_name: str) -> None:
    """Print the 'CEO is thinking' status line."""
    print()
    print(colorize(f"  ⚡ {archetype_name} is thinking...", C.CYAN), flush=True)


def print_executizing(archetype_name: str, job_id: str) -> None:
    """Print the Executizing dispatch confirmation."""
    short_id = job_id[:8]
    print()
    print(colorize(f"  ⚡ {archetype_name} has been dispatched on a deep-work mission.", C.CYAN))
    print(colorize(f"     Job ID: {short_id}...", C.DIM))
    print(colorize("     You can keep chatting or /switch to another CEO.", C.DIM))
    print()


def print_job_complete(archetype_name: str) -> None:
    """Print the job completion notification."""
    print()
    print(colorize(f"  ✓ {archetype_name} has returned from their mission.", C.LIME))
    print()


def print_error(message: str) -> None:
    print()
    print(colorize(f"  ✗ {message}", C.MAGENTA))
    print()


def print_warning(message: str) -> None:
    print()
    print(colorize(f"  ! {message}", C.YELLOW))
    print()
