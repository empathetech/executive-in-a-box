# Security & Privacy

<!-- This document defines the threat model, trust boundaries, and privacy
     commitments for Executive in a Box.

     Rule: any feature that crosses a trust boundary (stores data, calls an
     external service, acts autonomously) must be reviewed against this doc
     before implementation. See AUDIT_MODEL.md for the standing audit process. -->

---

## Core Privacy Commitment

Executive in a Box is local-first by design. No user data — org profiles,
session transcripts, strategic notes, API keys, credentials — leaves the user's
machine unless they explicitly configure an integration that requires it.

The tool does not:
- Phone home
- Collect usage telemetry (without explicit opt-in)
- Store anything in a cloud service by default
- Share data between users

---

## Trust Boundaries

*Updated 2026-04-04 — see [ADR](decisions/2026-04-04-web-ui-pivot.md) for context on
the web UI pivot, Tailscale exposure model, and Slack inbound deferral.*

A trust boundary is any point where data or control crosses from one system to
another. Every trust boundary is a potential risk surface.

| Boundary | Present in V1? | Risk |
|----------|----------------|------|
| User input → LLM provider API | Yes | Prompts and org context sent to external provider |
| Local file system → LLM context | Yes | Context files must not contain secrets |
| Local web server → browser (localhost) | Yes (V1) | Low — same machine; mitigated by local-only binding |
| Local web server → Tailscale network | Optional (V1) | Medium — server accessible to all Tailscale peers; no auth layer in V1 |
| Tool → Slack (outbound webhook) | Yes (V1) | Low — one-directional; only sends what user explicitly composes |
| Slack → Tool (inbound events) | No (V2+) | Medium — external system pushing data to local server |
| Tool → external integrations (LinkedIn, email, etc.) | No (V2+) | High — autonomous action on external systems |
| Local → cloud sync | No (V2+) | Medium — data leaves machine |
| Multi-user shared context | No (V2+) | Medium — data shared between people |

---

## Threat Model

### MVP Threats

**T1 — API key exposure**
LLM provider API keys are sensitive credentials that must be protected.

Mitigations:
- API keys are stored in the OS keychain (macOS Keychain, Windows
  Credential Locker, Linux Secret Service) — encrypted at rest, accessible
  only to the user's account
- Keys are never stored in plaintext files, config files, or session logs
- Keys are never echoed to terminal output after initial entry
- Environment variables are supported as an alternative for headless environments
- `.gitignore` template excludes the data directory as a defense-in-depth measure
- Documentation explicitly explains how keys are stored and protected

**T2 — Sensitive org context sent to LLM provider**
Every prompt to an LLM provider includes org context (mission, decisions,
stakeholders, etc.). That data is subject to the provider's privacy policy.

Mitigations:
- User is informed at setup which provider each archetype uses and what data is sent
- Documentation advises users to review their provider's data retention policy
- Local model support (Ollama) is a first-class option for users who need full data sovereignty
- Future: a "what gets sent to the LLM" transparency view in the UI

**T3 — Malicious or hallucinated advice acted on without review**
At autonomy levels 3–4, the CEO can act without explicit per-action approval.
A hallucinated or adversarially influenced recommendation could cause real harm.

Mitigations:
- Autonomy levels 3–4 are not available in MVP
- When introduced, every autonomous action is logged with full reasoning chain
- High-stakes action categories (financial, external communications, org structure
  changes) require explicit user configuration to be eligible for autonomous execution
- User can always roll back to Level 1 at any time

**T4 — Context files contain secrets**
A user pastes an API key, password, or credential into a context file (e.g.,
`stakeholders.md`). That file gets included in LLM prompts and sent to the provider.

Mitigations:
- Tool scans context files for common secret patterns before including them in prompts
- Flags suspected secrets with a warning before sending
- Documentation clearly instructs users not to store credentials in context files

**T5 — Tailscale exposure with no auth layer**
When the local server is bound to a Tailscale IP, any peer on the Tailscale network
can access the instance — including all org context, session history, and artifacts.
In V1 there is no authentication layer.

Mitigations:
- Default binding is `localhost` only; Tailscale exposure is an explicit opt-in
- Documentation clearly explains that Tailscale exposure = network-level trust,
  and advises users to treat Tailscale network membership as access control
- Future milestone: auth layer before any hosted/public deployment

**T6 — XSS / local web server**
A locally-served web app that renders user-provided content (session history,
org context, LLM responses) could be vulnerable to cross-site scripting if
content is not properly escaped.

Mitigations:
- All user-provided and LLM-provided content must be HTML-escaped before rendering
- No `eval()` or `innerHTML` with unescaped content
- Content Security Policy headers set on local server responses

### V2+ Threats (document before implementing)

**T5 — Autonomous external action**
The CEO posts to LinkedIn, emails investors, or interacts with external services
on the org's behalf. A bad decision, hallucination, or misconfiguration could
damage relationships or reputation.

Required mitigations before any external integration ships:
- Full audit log of every external action taken
- Per-integration confirmation flow at setup
- Autonomy level applies per-integration (can enable LinkedIn posting at Level 3
  while keeping email at Level 2, for example)
- Explicit "undo" or "retract" where the platform allows it
- Rate limits to prevent runaway loops

**T6 — Cloud storage breach**
If cloud sync is added, org data is stored on a third-party server.

Required mitigations before cloud storage ships:
- Encryption at rest (user-controlled key preferred)
- Documented data residency and retention policy
- Explicit opt-in with clear explanation of what moves to the cloud
- Local-only mode always remains available

---

## Data Inventory

### What the tool stores locally

| Data | Location | Sensitivity | Notes |
|------|----------|-------------|-------|
| Org profile (name, mission, values) | `org/profile.md` | Low–Medium | User-authored |
| Stakeholder info (names, roles) | `org/stakeholders.md` | Medium | May contain personal info |
| Decision log | `org/decisions.md` | Medium | Strategic context |
| Board config + autonomy level | `board/config.md` | Low | No credentials |
| Session transcripts | `sessions/` | Medium–High | Contains full prompts and responses |
| LLM provider API keys | OS keychain or env var | High | Encrypted at rest; never in plaintext files |
| Strategic memory | `memory/` | Medium | Running org context |
| Job state | `jobs/` | Low | Job IDs, status, results — no credentials |
| Session artifacts | `artifacts/` | Medium | Documents, analyses generated during sessions |
| Slack webhook URL | local config | Low | Not a credential; a send-only URL |

### What leaves the machine (V1)

- Prompts (including org context) sent to the configured LLM provider API
- Messages explicitly composed and sent by the user to Slack (outbound webhook)
- Nothing else

---

## Autonomy Level Security Requirements

| Level | External action allowed? | Audit log required? | User confirmation required? |
|-------|--------------------------|---------------------|-----------------------------|
| 1 — Advisor | No | Recommended | Yes (every action) |
| 2 — Recommender | No | Yes | Yes (every action) |
| 3 — Delegated | Low-stakes only (configured) | Yes, real-time | No (low-stakes), Yes (high-stakes) |
| 4 — Autonomous | Yes (configured) | Yes, real-time | No — async review only |

Levels 3 and 4 are not available until V1. When introduced, they require the user
to explicitly acknowledge the autonomy risks in a one-time confirmation flow.

---

## User Input Validation

All user input that crosses a trust boundary must be validated:

- Prompts to LLM: strip or escape content that could be used for prompt injection
- File paths provided by user: validate and sanitize before file system access
- External integration inputs (V2+): validate before sending to third-party APIs

The tool should never expose internal error details to the user. Errors are
described in plain language with a suggested action; stack traces and internal
state go to a debug log, not the terminal.

---

## Incident Response (Community Projects)

If a security issue is found:
1. Report it privately via the repo's security disclosure process (to be set up — see BACKLOG)
2. Do not open a public issue for active vulnerabilities
3. Maintainers acknowledge within 72 hours and communicate a timeline

This is an open source project. There is no SLA. But we take security seriously
because the people using this tool are trusting it with real strategic information.
