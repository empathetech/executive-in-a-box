# Style Guide

<!-- Design language for Executive in a Box across all three interfaces.
     Three interfaces, one aesthetic register — adapted per medium.

     Web app:      neon/8-bit/CRT
     CLI:          ASCII/Unicode, ANSI color
     Claude skill: markdown conventions

     When adding a new UI element or interface pattern, check this doc first.
     If the pattern isn't covered, add it here before implementing. -->

---

## Core Aesthetic

The design language draws from:
- **Rocko's Modern Life** color register: hyper-saturated neon, 80s-90s spandex palette
- **8-16 bit pixel art**: chunky pixels, dithering, sprite-style portraits
- **CRT aesthetic**: scanlines, screen glow, slightly curved screen treatment on specific panels
- **Retro-futurism**: the vibe is "what if a 1992 Saturday morning cartoon made enterprise software"

This isn't irony. The aesthetic is deliberate — it signals that the tool is on the user's side,
not dressed in the gray/blue corporate visual language of the products it's meant to replace.

Energy: loud, confident, a little chaotic, but organized underneath. Fun to look at and use.

---

## Color Palette

Primary neons (web + ANSI CLI equivalents):

| Name | Hex | ANSI | Use |
|------|-----|------|-----|
| Hot Magenta | `#FF2D78` | `\e[95m` | Primary accent, CEO portrait borders, active states |
| Electric Cyan | `#00F5FF` | `\e[96m` | Secondary accent, streaming text, links |
| Lime Zap | `#7FFF00` | `\e[92m` | Success states, confirmed actions, "complete" job state |
| Solar Yellow | `#FFE600` | `\e[93m` | Warnings, "thinking" / Executizing state |
| Deep Purple | `#3D00CC` | `\e[34m` | Background panels, depth |
| Void Black | `#0A0A0F` | `\e[40m` | Primary background |
| Ghost White | `#F0F0FF` | `\e[97m` | Primary text on dark backgrounds |

Avoid: gray-blue corporate palettes, pastels, anything that looks like Slack or Notion.

---

## Web App

### Layout

Three-pane layout:

```
┌─────────────┬──────────────────────────┬──────────────────┐
│  ARTIFACTS  │         CHAT             │   WHITEBOARD     │
│  (explorer) │   (center, primary)      │  (right, CRT)    │
│             │                          │                  │
│  session    │  [CEO portrait strip]    │  default:        │
│  artifacts  │  ──────────────────      │  usage/cost      │
│  listed     │  chat history            │  dashboard       │
│  here —     │  per active CEO          │                  │
│  click to   │                          │  future:         │
│  open       │  [input bar]             │  charts,         │
│             │  [Executize btn]         │  report views    │
└─────────────┴──────────────────────────┴──────────────────┘
```

- Left pane: ~20% width, dark background, artifact file tree
- Center pane: ~55% width, chat interface
- Right pane: ~25% width, CRT aesthetic (scanline overlay, slight screen-glow border)

### CEO Portrait Strip

Each configured CEO archetype has a portrait card displayed in a horizontal strip
above the chat area. Portrait style: 8-16 bit pixel art, archetype-specific design.

Portrait states:
- **Active**: full color, Hot Magenta border, selected indicator
- **Available**: full color, no border, clickable to switch
- **Executizing**: desaturated/faded, Solar Yellow pulsing border, archetype-specific
  verb displayed below the portrait (e.g., "Strategizing...", "Ruminating...",
  "Projecting...", "Synthesizing..."). Chat input for this CEO is disabled.
- **Error/Failed**: red border, error icon

Archetype verb bank (used during Executizing state):
- Operator: "Operationalizing...", "Stress-testing...", "Scoping..."
- Visionary: "Dreaming...", "Horizon-scanning...", "Envisioning..."
- Advocate: "Listening...", "Weighing...", "Centering..."
- Analyst: "Crunching...", "Modeling...", "Triangulating..."

### Chat Window

- Dark background (`#0A0A0F`)
- CEO messages: Electric Cyan username label, Ghost White text, left-aligned
- User messages: Hot Magenta label, right-aligned
- Streaming/typewriter rendering: characters appear progressively; cursor blinks
  in Electric Cyan while streaming
- Timestamps: small, Ghost White at low opacity, right-aligned per message
- Horizontal rule between sessions/days

### Executizing Button

A dedicated button to trigger deep-work / async job mode for the active CEO.
Label: **"Executize"** (verb form, deliberate).
Style: Solar Yellow background, Void Black text, pixel-art border.
On activation: CEO portrait enters Executizing state, input disabled, job dispatched.

### Toast Notifications

Used for job completion, errors, Slack send confirmation.
Style: slide in from bottom-right, 8-bit border, color matches state (Lime Zap for
success, Solar Yellow for info, Hot Magenta for error). Auto-dismiss after 5s.
Job completion toast: CEO portrait thumbnail + "The [Archetype] is back." + action button.

### Artifact Explorer (Left Pane)

File tree style. Session artifacts grouped by date. Artifact types:
- Document (page icon)
- Spreadsheet (grid icon)
- Analysis/report (chart icon)

All icons: pixel-art style, consistent with archetype portrait aesthetic.
Click to open artifact in an overlay or new tab.

### Whiteboard / Right Pane (CRT Treatment)

CRT aesthetic applied via:
- Subtle scanline overlay (CSS repeating gradient, low opacity)
- Outer glow border (Electric Cyan or Deep Purple, blurred)
- Slight vignette on corners
- Monospace font for all text in this panel

Default content: LLM usage/cost dashboard.

#### Usage/Cost Dashboard

Displays per-provider, per-archetype:
- Tokens used (in / out)
- Estimated cost (in user's currency)
- Quota status: progress bar in Lime Zap → Solar Yellow → Hot Magenta as limit approaches
- Reset date / next billing period

Style: bar charts rendered in ASCII/pixel style within the CRT panel.
Numbers in Solar Yellow, labels in Ghost White. Quota bar changes color as it fills.

### Announce Modal (Slack)

A modal for composing Slack messages before sending.
Left half: markdown/text input.
Right half: live preview rendering Slack block elements (mrkdwn formatting, section blocks).
Send button: Lime Zap when ready, disabled (gray) until a message is composed.
Confirmation step: "Post to #channel-name?" with preview of final rendered output.

### Autonomy Level Controls

Displayed per CEO portrait card, below the portrait and verb/status area.
Four buttons labeled 1–4. Active level highlighted in Hot Magenta.
Hover tooltip on each button: plain-language description of the level.
Levels 3 and 4 show a warning icon; activation requires confirmation modal.

---

## CLI

### Design Principle

The CLI should feel like the web app's cousin, not its discount version. Same energy,
adapted for the terminal. A user switching between interfaces should recognize the
same product.

### Color Usage

Use ANSI escape codes to apply the palette (see Color Palette above). Gracefully
degrade to no color on terminals that don't support it (detect via `$TERM` / `NO_COLOR`).

### Layout Conventions

Headers: ASCII box-drawing characters (`┌─┐│└─┘`) in Hot Magenta.
Section dividers: `═══` or `───` in Deep Purple / dim.
CEO labels: `[OPERATOR]` in Electric Cyan, `[YOU]` in Hot Magenta.
Status lines: left-aligned, Solar Yellow for in-progress states.
Success confirmations: Lime Zap prefix (`✓` or `[OK]`).
Errors: Hot Magenta prefix (`✗` or `[ERR]`).

### CEO Switching

```
exec-in-a-box --ceo operator   # switch active CEO
exec-in-a-box --ceo visionary
```

Or interactively via a numbered menu. Current active CEO shown in the prompt prefix.

### Executizing State

When a job is dispatched for one CEO:
```
[VISIONARY] Envisioning... (job abc123 running)
You can interact with other CEOs while this runs.
Type 'exec-in-a-box jobs' to check status.
```

Prompt remains active for other CEOs. On completion:
```
╔══════════════════════════════╗
║ ✓ THE VISIONARY IS BACK.     ║
╚══════════════════════════════╝
[VISIONARY] Here's what I've been thinking...
```

Box border in Lime Zap. Archetype name in Electric Cyan.

### Artifact Commands

```
exec-in-a-box artifacts list       # list session artifacts
exec-in-a-box artifacts open <id>  # open artifact (prints to stdout or opens in $EDITOR)
```

### Usage/Cost Summary

```
exec-in-a-box usage    # print per-provider token + cost summary
```

Output in CRT-style ASCII table: Solar Yellow numbers, Ghost White labels,
Lime Zap → Solar Yellow → Hot Magenta quota bar rendered in ASCII.

---

## Claude Skill

### Design Principle

The Claude skill renders in Claude Code's output pane, which is markdown. The aesthetic
should feel consistent with the other interfaces — same voice, same energy — but adapted
for a markdown-rendered context. No raw ANSI codes; use markdown formatting instead.

### Conventions

- CEO labels: bold, e.g., `**[OPERATOR]**`
- Section headers: `##` or `###`, not plain text
- Status/state indicators: emoji as icons — ⚡ for active, 🌀 for Executizing, ✅ for complete, ❌ for error
- Confidence levels: displayed as a row of blocks, e.g., `▓▓▓░░ Medium`
- Artifact references: code blocks or blockquotes with a type label
- Quota/usage: inline table in markdown

### Executizing State

When a deep-work job is dispatched:
```
🌀 **[VISIONARY] Envisioning...** *(job abc123 queued)*

You can interact with other CEOs. Run `/exec-in-a-box status abc123` to check,
or just ask your next question — I'll let you know when they're back.
```

On completion:
```
✅ **THE VISIONARY IS BACK.**
```

### Multi-CEO Switching

```
/exec-in-a-box --ceo analyst "What's the risk profile here?"
```

Active CEO tracked in skill session state.

---

## Voice and Tone

Consistent across all interfaces:

- **Direct.** No filler. No "Certainly!" No "Great question!"
- **Confident but honest about uncertainty.** The CEO says what it thinks and flags
  what it doesn't know.
- **Warm, not corporate.** This tool is on the user's side. That should be audible.
- **The Executizing verbs are fun on purpose.** Lean into it.
- **Error messages are plain language.** Never expose internal state. Never be cold
  about it — "We couldn't reach Anthropic. Check your connection and API key." not
  "Error 503: upstream provider unavailable."

---

## What Not To Do

- Don't use gray-blue corporate color palettes
- Don't use rounded, "friendly" sans-serif fonts without pixel/CRT contrast somewhere
- Don't make the Executizing state feel like a spinner — it should feel like the CEO
  is genuinely busy, not just loading
- Don't collapse the CRT right pane into something that looks like a generic dashboard
- Don't soften the neon palette "for readability" without checking ACCESSIBILITY.md first
  (contrast requirements apply — we can be neon and accessible)
