# Product Overview

<!-- Synthesizes IDEATION.md into a clear, shareable product definition.
     Someone unfamiliar with the project should be able to read this and understand
     what's being built, who it's for, and why it matters. -->

## Who

Solo builders and small teams who need executive-level strategic guidance without hiring — or deferring to — a human CEO. Specifically:

- People who were recently laid off and are starting something new on their own terms
- Small teams and co-ops that operate democratically and want tools that match their values
- Existing small orgs that want to make the case internally for replacing or bypassing a traditional executive structure
- Anyone who wants to build something worker-owned and worker-directed, and needs the strategic muscle to actually pull it off

The ideal user is someone who does the actual work, understands the product and the people, and is done watching executives extract value at everyone else's expense.

## What

An AI-powered executive assistant — an "executive in a box" — that gives any team access to CEO-level strategic capabilities without a human CEO. It:

- Provides ongoing strategic guidance: direction, focus, priorities, org structure
- Can convene a "board of directors" made up of multiple LLMs (user's choice) that debate and argue — user is always the tiebreaker and final decision-maker
- Manages external-facing executive work: LinkedIn networking, funding outreach, pitching to investors and partners
- Plans and facilitates all-hands meetings on product direction
- Acts as a steward of the org's principles — the voice and face of what the org decided it stands for
- Handles KPIs, ROIs, and stakeholder communication in plain, meaningful language — no jargon
- For existing orgs: can audit the current structure and build a structured case for replacing the executive team
- Easter egg: helps users ideate what a better version of their old product would have been — the "what we would have built if we hadn't been let go for stupid reasons" feature

The tool captures what's genuinely valuable about a CEO (strategic clarity, external representation, stakeholder alignment) and cuts everything that makes a human CEO costly and harmful (politics, shareholder appeasement, labor extraction).

## Where

*Pivoted 2026-04-04 — see [ADR](../02-design/decisions/2026-04-04-web-ui-pivot.md) for context.*

Three first-class interfaces, all with feature parity on the core experience:

1. **Web app (primary)** — locally-served Python web server, accessed via browser at
   `localhost`. Can be exposed over Tailscale for small-team access without cloud
   infrastructure. Design language: neon/8-bit, 80s-90s spandex color register,
   CRT panel treatments.

2. **CLI** — maintained as a full-feature interface with an ASCII/Unicode design
   language tonally consistent with the web app. Not a fallback — same conversational
   model, same async job system, same multi-CEO switching.

3. **Claude skill** — a `/exec-in-a-box` slash command for use inside Claude Code.
   Markdown formatting conventions consistent with the design language. Full feature
   parity with the other interfaces.

All interfaces connect to the same Python backend. The backend owns async job state,
CEO context, and all persistence. Cloud hosting with an auth layer is a future milestone,
introduced with full documentation and opt-in consent at each step.

## When

- MVP: core strategic guidance loop — a single LLM "CEO" the user can configure, query, and direct
- V1: board of directors model (multiple LLMs), memory/context persistence, all-hands meeting facilitation
- V2+: external integrations (LinkedIn, funding sources), cloud storage option, audit/replace-the-exec-team feature, easter egg

## Why

The value a human CEO provides is real — strategic clarity, external relationships, stakeholder communication — but it's available for maybe 10% of what a traditional CEO costs in salary, politics, and damage to people and product. Workers who build the thing are systematically cut off from those capabilities and from the org structures that would actually serve them. This tool puts that capability in the hands of the people doing the work, in service of structures where they actually have power.

The timing is deliberate: executives are using AI as an excuse to eliminate labor. This tool uses the same AI to make those executives unnecessary.

## Constraints & Values

### Licensing Intent

MIT License. Open source, freely usable and modifiable. Anyone can fork it, build on it, or charge for a product built on it. The tool itself stays free.

### Privacy Stance

Local-first by default. Sensitive data — org structure, financials, strategic notes, any credentials used for external integrations — stays on the user's machine unless they explicitly opt into cloud storage. Cloud options, when introduced, should be well-documented, use established compliant services, and make the tradeoffs legible to users who aren't infrastructure experts. A memory MCP server for persistent CEO context is a promising V1/V2 direction.

### Infrastructure Preference

Self-hosted and local first. If cloud infrastructure becomes valuable (e.g., for shared team context or external integrations), it gets introduced on the roadmap with clear, comprehensive setup documentation and explicit risk explanations. Contributors should not need a cloud infrastructure background to participate — documentation is a first-class feature, not an afterthought.
