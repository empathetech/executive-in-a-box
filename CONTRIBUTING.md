# Contributing to Executive in a Box

Thank you for being here. Whether you're writing code, improving docs, or
reporting a bug — you're helping build a tool that puts strategic power in
the hands of the people who do the actual work.

---

## Ways to contribute

**Documentation is as valued as code.** Our users are not necessarily
technical. Clear, honest, jargon-free documentation is one of the most
impactful things you can contribute.

- Fix or improve a doc — if something confused you, it'll confuse others
- Report a bug — open a GitHub issue with what you expected vs. what happened
- Pick a task from the backlog — see `hacky-hours/04-build/BACKLOG.md`
- Suggest a feature — open a GitHub issue. We'd rather hear a rough idea
  than lose it
- Review a pull request — a second set of eyes catches what the first misses

---

## Getting set up

### Prerequisites

- Git
- Python 3.10 or later
- A terminal you're comfortable with

### Clone and install

```bash
git clone https://github.com/empathetech/executive-in-a-box.git
cd executive-in-a-box
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
pip install pytest ruff
```

### Run the tests

```bash
pytest tests/ -v
```

### Run the linter

```bash
ruff check src/ tests/
```

### Understand the project structure

The project uses the [Hacky Hours](https://github.com/empathetech/hacky-hours-docs)
documentation framework. Here's where things live:

```
hacky-hours/
  01-ideate/                 # Product vision (why this exists)
  02-design/                 # Architecture, security, business logic, user journeys
    ARCHITECTURE.md          # System design and component overview
    BUSINESS_LOGIC.md        # Wrapper layer, guardrails, aggregation logic
    SECURITY_PRIVACY.md      # Threat model and privacy commitments
    AUDIT_MODEL.md           # The audit checklist for every feature PR
    USER_JOURNEYS.md         # How users interact with the tool, step by step
    ACCESSIBILITY.md         # Accessibility standards and commitments
    LICENSING.md             # MIT license and dependency compatibility
    decisions/               # Architecture Decision Records (ADRs)
  03-roadmap/
    ROADMAP.md               # MVP / V1 / V2+ feature roadmap
  04-build/
    BACKLOG.md               # Current task queue — pick your task from here
    CHANGELOG.md             # Release history
docs/                        # User-facing guides
src/                         # Source code
```

**Before writing code, read the design docs.** They define how the product
works and constrain the implementation. If a design doc doesn't address
something you need to build, open an issue or bring it up in your PR —
don't assume.

---

## The workflow

### 1. Pick a task

Check `hacky-hours/04-build/BACKLOG.md` for open tasks. If you want to
work on one, comment on the linked GitHub Issue (if there is one) or open
a new issue saying what you plan to do.

### 2. Create a branch

Name your branch for the task:
```bash
git checkout -b feat/setup-wizard     # for new features
git checkout -b fix/api-key-validation # for bug fixes
git checkout -b docs/setup-guide       # for documentation
```

### 3. Do the work

- Reference the relevant design docs as you work
- Follow the existing code style (linter config TBD)
- Write for your audience: non-technical users for docs, future maintainers
  for code comments

### 4. Run the audit

**Every PR that adds, changes, or removes a feature must be audited.**
The full audit checklist is in `hacky-hours/02-design/AUDIT_MODEL.md`.

In your PR description, add:

```
## Audit

Security: [pass / pass with notes / blocked — reason]
Privacy: [pass / pass with notes / blocked — reason]
Design consistency: [pass / pass with notes / blocked — reason]
Documentation: [pass / pass with notes / blocked — reason]

Notes: [anything that needs follow-up]
```

If the audit finds a design doc that needs updating, update it in the same
PR — not a follow-up.

Routine refactors, documentation-only changes, and test-only changes do not
need a full audit but should still pass the pre-merge checklist:

```
[ ] Implementation matches the relevant design document
[ ] No secrets, API keys, or credentials in code or commit history
[ ] All user input that crosses a trust boundary is validated
[ ] Error messages don't expose internal system state
[ ] Change has been manually tested against the relevant user journey
```

### 5. Open a PR

- Write a clear description of what you changed and why
- Link the relevant backlog task or issue
- Include the audit section
- Request a review

### 6. Merge

After approval, squash merge with a clear commit message:
```
feat: add setup wizard (#12)
fix: validate API key before saving (#15)
docs: add provider guide for Anthropic (#18)
```

---

## Commit conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `refactor:` | Code change that doesn't fix a bug or add a feature |
| `test:` | Adding or updating tests |
| `chore:` | Build, tooling, or dependency changes |

If your commit closes a GitHub Issue, add `closes #<number>` to the message.

---

## Writing for this project

Our users include people who have never used a command-line tool before.
When writing documentation or user-facing text:

- **Use plain language.** If a 5th-grader couldn't follow it, simplify.
- **No jargon without explanation.** The first time you use a technical
  term, explain it.
- **Be honest about limitations.** Don't oversell what the tool can do.
  Don't bury the cost. Don't minimize the risks.
- **Be direct.** Say what you mean. One clear sentence beats three hedged ones.
- **Be warm, not corporate.** This project has a point of view. The docs
  should sound like a thoughtful person talking to another person — not a
  product marketing team.

For code comments: write for someone who will maintain this six months from
now with no context. Explain *why*, not just *what*.

---

## Security issues

If you find a security vulnerability, **do not open a public issue.** See
[SECURITY.md](SECURITY.md) for how to report it privately.

---

## Code of Conduct

Be decent. Treat people the way this tool treats its users — with respect,
honesty, and the assumption that they're capable of making their own decisions.

This project is built by and for workers. It doesn't have room for behavior
that makes people feel unwelcome, unsafe, or disrespected. If you see
something, say something — open an issue or reach out to a maintainer
directly.

A formal Code of Conduct document will be adopted as the contributor
community grows.

---

## Questions?

Open a GitHub issue. There are no dumb questions — if something about this
project confused you, improving that is a contribution.
