# Accessibility

<!-- Accessibility is not a feature — it's a baseline. Build it in from day one.
     Target: WCAG 2.1 AA unless your users or platform require a higher standard.

     Updated 2026-04-04: web app is now the primary interface — WCAG 2.1 AA
     is a hard requirement, not a target. The neon/8-bit design language must
     meet contrast requirements. See STYLE_GUIDE.md for the palette. -->

## Standards

- Target compliance level: WCAG 2.1 AA (hard requirement for web app)
- Platforms: web app (V1, primary), CLI (V1, full feature parity), Claude skill (V1)

---

## Web App

The neon/8-bit palette is loud by design. It must also be accessible.
"We can't do accessible neon" is not an acceptable tradeoff — test and fix contrast
ratios before shipping, not after.

- [ ] Color contrast: 4.5:1 minimum for all body text; 3:1 for large text and UI components
- [ ] Contrast testing required for every new color combination in STYLE_GUIDE.md
- [ ] No color-only signaling: Executizing state, job completion, errors must use shape/text/icon in addition to color
- [ ] All CEO portrait states (active, Executizing, error) have accessible text labels — not just visual indicators
- [ ] Keyboard navigation for all interactive elements: CEO switching, Executize button, autonomy toggles, Announce modal
- [ ] Focus indicators visible and high-contrast (don't remove browser default outlines without replacing them)
- [ ] All icons (artifact types, autonomy level buttons) have accessible labels (`aria-label` or visible text)
- [ ] Chat input meets minimum target size (44x44px touch target)
- [ ] Error messages tied to the relevant input; descriptive, not generic
- [ ] Toast notifications announced to screen readers (`aria-live` region)
- [ ] Streaming/typewriter text: screen readers should receive the complete response, not intermediate states (use `aria-live="polite"`)
- [ ] CRT panel (right pane): scanline overlay must not reduce text contrast below the 4.5:1 threshold
- [ ] Screen reader tested before each release

### Specific neon palette notes

The Hot Magenta (`#FF2D78`) and Solar Yellow (`#FFE600`) are primary accent colors.
On a `#0A0A0F` background:
- Hot Magenta on Void Black: verify contrast ratio — likely passes for large text / UI elements, may need adjustment for small body text
- Ghost White (`#F0F0FF`) on Void Black: high contrast — use for all primary body text
- Electric Cyan (`#00F5FF`) on Void Black: verify — likely passes for large text
- Any new color combination introduced must be contrast-checked before merging

Use a tool like WebAIM Contrast Checker or the browser devtools accessibility panel.

---

## CLI

- [ ] All output is plain text — readable by screen readers and assistive terminal tools without modification
- [ ] No color-only signaling: errors, warnings, Executizing state must use text/symbols (`[ERR]`, `✗`, status text) in addition to ANSI color
- [ ] Graceful color degradation: detect `NO_COLOR` env var and `$TERM` — disable ANSI codes when not supported
- [ ] Clear, descriptive prompts — no ambiguous single-character inputs without explanation
- [ ] Keyboard-only operation (CLI is keyboard-native by default)
- [ ] ASCII box-drawing characters used for structure, not meaning — structure is also conveyed by text labels

---

## Claude Skill

- [ ] All output is standard markdown — renders accessibly in Claude Code's output pane
- [ ] Status indicators use both emoji and text (e.g., `🌀 **Executizing...** *(job running)*` not emoji alone)
- [ ] Response structure uses semantic markdown headers (`##`, `###`), not formatting alone

---

## Runbook / Documentation Accessibility

The product's documentation is a first-class feature. Non-technical users must be
able to set up and use the tool without needing an engineer to interpret the docs.

- Plain language throughout — define any technical term the first time it's used
- Step-by-step setup instructions with expected outcomes at each step ("you should see...")
- Screenshots or ASCII diagrams where a visual would meaningfully help
- Every error message in the product has a corresponding plain-language explanation in the docs

See `docs/` for user-facing runbooks.

---

## Known Gaps

- Neon palette contrast ratios need formal verification against WCAG 2.1 AA thresholds before V1 ships — flagged as a pre-release gate, not a post-launch fix
- Screen reader testing requires a real screen reader (VoiceOver, NVDA) — schedule this before V1 release
