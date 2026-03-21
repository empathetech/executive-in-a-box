## Project State Machine

At the start of every session, orient yourself:
1. Run `gh issue list --milestone @current --state open` to see active work (if this repo has a GitHub remote and `gh` is available)
2. Read `hacky-hours/04-build/BACKLOG.md` to see queued tasks
3. Report current state in one sentence before asking what to do next

When completing a task:
1. Remove the item from `hacky-hours/04-build/BACKLOG.md`
2. Add it to `hacky-hours/04-build/CHANGELOG.md` under the current version
3. Close the linked GitHub Issue if one exists: `gh issue close <number>`
4. Commit with a clear message referencing the issue: `fix: ... closes #<number>`

When `hacky-hours/04-build/BACKLOG.md` is empty:
- Tell the user the milestone is complete
- Suggest running `/hacky-hours audit` first to check for any issues before publishing
- Then `/hacky-hours sync` to publish the GitHub Release
- Do not start new work without direction

Design constraints live in `hacky-hours/02-design/`. Before implementing anything, check whether a relevant design doc exists. If a design doc doesn't address something you need to implement, surface it to the user first — don't assume.

Before adding any dependency or external service, check `hacky-hours/02-design/LICENSING.md` for compatibility with the project's chosen license.

## Feature Audit Requirement

Every PR that adds, changes, or removes a feature must be audited before merging.
The audit checklist lives in `hacky-hours/02-design/AUDIT_MODEL.md`.

When completing any feature task:
1. Run through the relevant sections of the audit checklist
2. Record results in the PR description (Security / Privacy / Design / Docs)
3. If the audit finds a design doc that needs updating, update it in the same PR — not a follow-up
4. If the audit finds a significant decision was made, write an ADR in `hacky-hours/02-design/decisions/`

Do not mark a task complete if the audit has unresolved STOP items.
