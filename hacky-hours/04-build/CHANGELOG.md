# Changelog

<!-- Record of completed milestones and releases.
     Add entries here when a milestone is complete and you cut a release.
     Move entries older than 3 releases to archive/changelog/.

     Format:
     ## [vX.Y.Z] — YYYY-MM-DD
     ### Added
     - ...
     ### Changed
     - ...
     ### Fixed
     - ... -->

## [v0.1.0] — 2026-03-21

### Added

**Framework & Design**
- Hacky Hours framework scaffolded (ideate, design, roadmap, build)
- Product overview with 5Ws and Constraints & Values
- Architecture document: board of directors model, autonomy levels, local-first storage
- Business logic document: wrapper layer contract, archetype system prompts, output schema, aggregation logic, prompt injection defenses
- Security & privacy document: threat model, trust boundaries, data inventory
- Audit model: standing security/privacy/design checklist for every feature PR
- User journeys: setup wizard, board session, all-hands, autonomy change, exec audit, easter egg
- Accessibility standards (WCAG 2.1 AA target, CLI commitments)
- Licensing document (MIT, dependency compatibility tracking)
- Roadmap: MVP / V1 / V2+ feature prioritization

**User-Facing Documentation**
- README with project overview, install instructions, and point of view
- Setup guide: complete first-run walkthrough for non-technical users
- Provider guide: API key setup, pricing, and data policies for Anthropic and OpenAI
- Autonomy guide: plain-language explanation of the four trust levels
- Archetype guide: each advisor's reasoning style, strengths, and blind spots
- Contributing guide: dev setup, audit requirement, writing standards
- Security disclosure process (SECURITY.md)

**Implementation (Python CLI)**
- Project scaffolding: pyproject.toml, pip-installable package, `exec-in-a-box` CLI
- Local file storage layer: plain markdown/JSON files in `~/.executive-in-a-box/`
- LLM provider adapter: Anthropic and OpenAI with plain-language error handling
- Four built-in archetypes: Operator, Visionary, Advocate, Analyst
- Wrapper layer (pre-call): secret scanner, context injection, prompt injection defense
- Wrapper layer (post-call): strict JSON schema validation on all LLM responses
- Secure credential storage via OS keychain (keyring library)
- Setup wizard: interactive org profile, archetype, provider, and autonomy configuration
- Core session loop: ask a question, get structured advice, decide, log
- Autonomy level enforcement (levels 1-2; levels 3-4 hard-blocked for V1)
- Session history and transcript logging
- 32 passing tests
