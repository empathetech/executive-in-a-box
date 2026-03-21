# Audit Model

<!-- This document defines the standing audit process for Executive in a Box.
     Every feature addition, change, or removal triggers this process.
     The goal is to catch security, privacy, and design drift before it ships. -->

---

## When an Audit Is Required

An audit is required whenever a pull request:

- Adds a new feature or capability
- Removes an existing feature or capability
- Changes how data is stored, transmitted, or processed
- Adds, removes, or upgrades a dependency
- Changes the autonomy model or trust boundaries
- Introduces a new external integration
- Changes authentication or credential handling

Routine refactors, documentation changes, and test-only changes do not require
a full audit, but should still pass the pre-merge checklist.

---

## The Audit Checklist

Run through all sections that apply to the change. Record findings in the PR
description. Block merge if any STOP items are unresolved.

### Security

- [ ] Does this change introduce a new trust boundary? If yes, is it documented in SECURITY_PRIVACY.md?
- [ ] Does this change handle user input that crosses a trust boundary? If yes, is it validated and sanitized?
- [ ] Does this change store, transmit, or log any sensitive data (API keys, credentials, personal info, session content)?
  - If yes: is that storage/transmission necessary? Is it encrypted? Is it documented?
- [ ] Does this change send data to an external service? If yes:
  - Is the user informed?
  - Is it opt-in?
  - Is the data minimized to what's strictly necessary?
- [ ] Could this change enable autonomous action on an external system? If yes, is it gated behind Autonomy Level 3+ with explicit user confirmation?
- [ ] Do error messages in this change expose internal state, stack traces, or file paths?

### Privacy

- [ ] Does this change collect or store data that wasn't collected or stored before?
  - If yes: is it necessary? Is it documented in the Data Inventory in SECURITY_PRIVACY.md?
- [ ] Does this change affect what gets sent to an LLM provider?
  - If yes: is the user informed? Is there a local model alternative?
- [ ] Does this change affect the context files on disk? Could it cause sensitive data to be included in prompts?

### Design Consistency

- [ ] Does this change contradict any existing design document in `02-design/`?
  - If yes: update the design doc and write an ADR in `decisions/` before merging
- [ ] Does this change affect the autonomy model? If yes, is ARCHITECTURE.md updated?
- [ ] Does this change add a dependency? If yes, is LICENSING.md updated with the dependency's license and compatibility?
- [ ] Does this change affect accessibility? If yes, is ACCESSIBILITY.md updated?

### Documentation

- [ ] Is this change understandable to a non-technical user who reads the relevant docs?
- [ ] If this change introduces a new configuration option or behavior, is it documented in user-facing docs?
- [ ] If this change introduces infrastructure (cloud, external service), does the documentation explain setup, risks, and how to undo it?

---

## How to Record Audit Results

In the PR description, add a section:

```
## Audit

Security: [pass / pass with notes / blocked — reason]
Privacy: [pass / pass with notes / blocked — reason]
Design consistency: [pass / pass with notes / blocked — reason]
Documentation: [pass / pass with notes / blocked — reason]

Notes: [anything that needs follow-up, links to updated docs or new ADRs]
```

If a finding requires a design doc update or ADR, that update must be in the
same PR — not a follow-up. Design drift happens in the gap between "we'll fix
the docs later" and later never arriving.

---

## Feature Removal Audit

Removing a feature is not automatically safe. Before removing:

- [ ] Is this feature documented as a dependency of any other feature?
- [ ] Are there users who depend on this? Is there a migration path or communication plan?
- [ ] Does removing this feature change the security or privacy posture? (Sometimes removal improves it — document that too.)
- [ ] Does the removal need an ADR to explain why the decision was made?

---

## Dependency Audit (on every add/upgrade/remove)

- [ ] What is the dependency's license? Is it in LICENSING.md?
- [ ] What does the dependency do? What data does it touch?
- [ ] Is this the simplest dependency that solves the problem? (Could a smaller lib or stdlib work?)
- [ ] What happens if this dependency is abandoned or compromised?

---

## Audit Review Cadence

In addition to per-PR audits, run a full audit of the project before every release:

1. Run `/hacky-hours audit` — checks secrets, git status, framework doc readiness
2. Review SECURITY_PRIVACY.md — is the threat model still accurate?
3. Review LICENSING.md — are all dependencies accounted for?
4. Review AUDIT_MODEL.md itself — does the process still fit the project?

The audit process should evolve as the project grows. If a checklist item is
consistently irrelevant, remove it. If a risk pattern keeps appearing, add it.
