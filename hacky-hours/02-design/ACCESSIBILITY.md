# Accessibility

<!-- Accessibility is not a feature — it's a baseline. Build it in from day one.
     Target: WCAG 2.1 AA unless your users or platform require a higher standard. -->

## Standards

- Target compliance level: WCAG 2.1 AA
- Platform(s): CLI (MVP), desktop UI (V1+)

## Commitments

### CLI (MVP)
- [ ] All output is plain text — readable by screen readers without modification
- [ ] No color-only signaling (errors, warnings, status must also use text/symbols)
- [ ] Clear, descriptive prompts — no ambiguous single-character inputs
- [ ] Keyboard-only operation (CLI is keyboard-native by default)

### Desktop UI (V1+, if applicable)
- [ ] Native UI components used — no custom-rolled interactive widgets without accessibility review
- [ ] Keyboard navigation supported for all interactive elements
- [ ] Sufficient color contrast (4.5:1 for normal text, 3:1 for large text)
- [ ] All icons have accessible labels
- [ ] Error messages are descriptive and tied to the relevant input
- [ ] Screen reader tested before each release

## Known Gaps

- Desktop UI not yet designed — accessibility requirements will be revisited when UI platform is chosen.
- If a web UI is introduced, WCAG 2.1 AA becomes a hard requirement, not a target.
