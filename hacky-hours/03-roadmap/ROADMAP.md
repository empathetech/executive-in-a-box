# Roadmap

<!-- Sequence what to build and prioritize ruthlessly.
     Milestones should be outcome-based ("users can complete a purchase")
     not task-based ("implement checkout UI").

     MVP = the smallest version that proves the core value proposition.
     V1  = MVP plus what's needed for it to be genuinely useful.
     V2+ = valuable but not required for V1. -->

## MVP

### Goal
A user can configure an AI advisor with their org's context, ask it a strategic
question, and get structured advice they can act on — all on their own machine.

### Features

**Setup & Configuration**
- [ ] Setup wizard: org profile (name, mission, values) → archetype selection → LLM provider + API key → autonomy level
- [ ] 3–4 built-in archetypes with system prompts (Operator, Visionary, Advocate, Analyst)
- [ ] Board of one: single active archetype per session
- [ ] LLM provider adapter supporting Anthropic and OpenAI

**Core Session Loop**
- [ ] User submits a strategic question via CLI
- [ ] Wrapper layer: secret scan context files before any LLM call
- [ ] Wrapper layer: inject org context + archetype system prompt
- [ ] LLM call → validate response against output schema
- [ ] Present structured output: position, reasoning, confidence, pros/cons, flags
- [ ] User decision (Y/N/Modify) — recorded to `org/decisions.md`
- [ ] "How it got here" view available on request

**Autonomy Levels**
- [ ] Level 1 (Advisor): every action requires explicit user approval
- [ ] Level 2 (Recommender): recommendation presented, user approves or overrides
- [ ] Levels 3 and 4 not available in MVP (enforced in code)

**Local Storage**
- [ ] `org/profile.md` — org name, mission, values
- [ ] `org/decisions.md` — log of decisions made and rationale
- [ ] `board/config.md` — archetype assignment, provider config, autonomy level
- [ ] `sessions/YYYY-MM-DD-*.md` — session transcripts

**Wrapper Layer & Guardrails**
- [ ] Output schema validation — invalid responses excluded, never partially used
- [ ] Secret scanner — redact and warn before any LLM call
- [ ] Prompt injection defenses — structural separation + schema validation backstop
- [ ] Error handling contract — plain language only, no internal state exposed
- [ ] API key stored locally, never logged or transmitted outside provider calls

**Documentation**
- [ ] README: what this is, what it isn't, how to install and run
- [ ] Setup guide: step-by-step for non-technical users
- [ ] Provider setup guide: how to get an API key for each supported provider and what it costs
- [ ] Security disclosure process (SECURITY.md)

---

## V1

### Goal
A full board of advisors that debate and aggregate, with memory that makes the
CEO genuinely useful across sessions over time.

### Features

**Multi-LLM Board**
- [ ] Board of many: configure multiple archetypes, each optionally powered by a different LLM
- [ ] Independent responses collected per archetype (parallel where rate limits allow)
- [ ] Board aggregation: common ground detection, spectrum view, aggregated pros/cons
- [ ] CEO conclusion synthesis (constrained LLM call against archetype outputs)
- [ ] Survey view: side-by-side archetype positions for user exploration

**Memory & Persistence**
- [ ] `memory/strategic-context.md` — running summary of key org context
- [ ] `memory/open-questions.md` — flagged items for future resolution
- [ ] Context injection rules: relevant memory included in prompts automatically
- [ ] MCP memory server integration (opt-in, documented setup)

**Local Model Support**
- [ ] Ollama adapter — use local models for full data sovereignty
- [ ] Documentation: how to set up Ollama and what the tradeoffs are vs. cloud providers

**All-Hands Meeting Facilitation**
- [ ] User requests an all-hands → tool gathers context from roadmap + decisions log
- [ ] Agenda generation → user review and approval before facilitation begins
- [ ] Facilitation mode: step through agenda items, invoke board for strategic items
- [ ] Post-meeting summary → user approval → saved to sessions/ and decisions.md
- [ ] Action items offered for backlog

**Autonomy Levels 3 & 4**
- [ ] Level 3 (Delegated): auto-approve low-stakes actions per configured action type registry
- [ ] Level 4 (Autonomous): act on conclusions within scope, full async audit log
- [ ] Explicit acknowledgment flow required to enable Level 3 or 4
- [ ] Hard-coded action types that always require user approval regardless of level

**Archetype Customization**
- [ ] User can edit built-in archetypes
- [ ] User can create custom archetypes

**Documentation**
- [ ] Autonomy level guide: what each level means, risks, and how to change it
- [ ] MCP memory server setup guide
- [ ] Ollama setup guide
- [ ] Board composition guide: how to pick archetypes and why it matters

---

## V2+

**Exec Replacement Audit**
- [ ] Analyze a current org structure against stated mission/values
- [ ] Generate a structured case for democratic restructuring
- [ ] Output as a plain-language shareable report with required disclaimer

**External Integrations**
- [ ] LinkedIn: networking, funding outreach, pitching — opt-in, per-action audit log
- [ ] Email outreach (investor/partner pitching) — opt-in, per-action audit log
- [ ] Each integration: explicit setup flow, credentials stored locally, autonomy level applies
- [ ] "Undo" or retract action where platform allows

**Cloud Sync (opt-in)**
- [ ] Encrypted cloud storage for org context and session history
- [ ] Documented data residency, retention, and how to delete
- [ ] Local-only mode always remains available
- [ ] Full infrastructure setup guide written for non-technical contributors

**Multi-User / Team Shared Context**
- [ ] Shared org profile and decisions log for small teams
- [ ] Access model: who can read/write which files

**Web UI**
- [ ] Visual board session interface
- [ ] Accessibility: WCAG 2.1 AA (required before any web UI ships)

**Easter Egg: What We Would Have Built**
- [ ] Hidden activation (specific command or prompt)
- [ ] Free-form user input: describe the product and what happened
- [ ] Board session: generative, celebratory alternative timeline
- [ ] Optional export as a document the user can keep
- [ ] No external connections. Output never auto-shared. Tool is on the user's side.

---

## Parking Lot

Ideas without a milestone yet — valid but not prioritized.

- Voice interface
- Mobile companion app
- Integration with project management tools (GitHub Issues, Linear)
- Digest / weekly summary mode: CEO summarizes the week's decisions and open questions
- Public archetype library: community-contributed archetypes users can install
