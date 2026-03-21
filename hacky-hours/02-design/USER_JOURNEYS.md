# User Journeys

<!-- Maps how users move through the product across key scenarios.
     These journeys define what the tool must do, in what order, and what
     the user sees at each step. Implementation must match these flows.
     When a journey changes, update this doc and write an ADR if the change
     is significant. -->

---

## Journey 1: First Launch (Setup Wizard)

The setup wizard runs once on first launch. It establishes the org profile,
configures the board, and sets the autonomy level. It must be completable by
a non-technical user in under 15 minutes.

```
[Launch tool for the first time]
        |
        v
[Welcome screen]
  "Executive in a Box helps you run your org with AI-powered strategic guidance.
   You're always in charge. Let's get you set up."
        |
        v
[Step 1: Your Org]
  - What's your org's name?
  - In one or two sentences, what does it do?
  - What are the most important values your org operates by?
  (Plain text inputs. Saved to org/profile.md)
        |
        v
[Step 2: Your Board]
  - Do you want one advisor (simple) or a board of advisors (multiple perspectives)?
  - [If board] Pick archetypes from the list. Each one explains what it brings.
  - For each archetype: which LLM provider should power it? (List available providers)
  - [Provider setup] Enter your API key for each provider. (Stored locally, never transmitted)
  (Saved to board/config.md)
        |
        v
[Step 3: How much should your CEO do on its own?]
  - Present the four autonomy levels in plain language with examples:
    Level 1: "I'll always ask you before doing anything. You're fully in control."
    Level 2: "I'll give you a recommendation and you approve or change it."
    Level 3: "I'll handle routine decisions myself and flag the big ones."
    Level 4: "I'll act on my conclusions. You review what I did."
  - Recommend Level 1 for first-time users. Explain why.
  - User picks a level.
  (Saved to board/config.md)
        |
        v
[Step 4: Quick orientation]
  - Show the user what their board looks like (names, archetypes, providers)
  - Show their autonomy level
  - Explain: "You can change any of this at any time by running: exec setup"
  - Offer to run a demo board session on a sample question
        |
        v
[Setup complete. Drop into main prompt.]
```

**Guardrails:**
- Setup cannot be skipped. The tool will not proceed without a minimum valid config
  (org name + at least one archetype + one provider configured)
- API keys are validated by making a test call before setup completes. If the call
  fails, the user is told in plain language and setup does not proceed
- No LLM call is made until the user has reviewed and confirmed their board config

---

## Journey 2: A Board Session (Core Loop)

The primary interaction. User asks a strategic question; the board deliberates;
user decides.

```
[User submits a question or topic]
  e.g. "Should we hire a contractor to build the payments feature or do it ourselves?"
        |
        v
[Pre-flight checks — our code, not the LLM]
  - Is the question within scope? (Not a request for illegal/harmful action)
  - Does the context include any secrets? (Scan before sending)
  - Which archetypes are active? Load their system prompts.
  - What context is relevant? Load org profile + strategic memory + recent decisions
  - Log the query to the session file
        |
        v
[Each archetype responds independently]
  - Archetype system prompt + org context + user question → LLM API call
  - Responses are collected in parallel (or sequentially if provider rate limits apply)
  - Each response is validated against the output schema before use (see BUSINESS_LOGIC.md)
        |
        v
[Board Engine aggregates responses]
  - Identifies common ground across all positions
  - Maps each position on the ambition/caution spectrum
  - Extracts and deduplicates pros and cons
  - Synthesizes a CEO conclusion
  - Builds the "how it got here" reasoning chain
        |
        v
[Present results to user]
  Default view:
    - CEO conclusion (the synthesized recommendation)
    - Common ground (what everyone agreed on)
    - Spectrum summary (who leaned which way and how far)
    - Aggregated pros and cons

  On request:
    - Each board member's full position
    - "How it got here" reasoning chain

        |
        v
[User decision — based on autonomy level]
  Level 1/2: "Do you want to adopt this recommendation? [Y/N/Modify]"
  Level 3/4: Conclusion is acted on automatically (if within configured scope)
             User can review at any time via session log
        |
        v
[Record outcome]
  - Log the decision and outcome to org/decisions.md
  - Update strategic memory if relevant
  - Offer to add follow-up tasks to the backlog
```

**Guardrails:**
- The aggregation step is done by our code, not a second LLM call — it operates on
  structured output from each archetype, not free text (see BUSINESS_LOGIC.md)
- The user's final yes/no is always recorded, even at Level 4 (async review)
- If any archetype response fails validation, it is flagged as invalid and excluded
  from aggregation — the session continues with remaining valid responses
- The session is never committed to disk until the user's decision is recorded

---

## Journey 3: All-Hands Meeting

The tool plans and facilitates a meeting about product direction with the user
and any other participants.

```
[User requests an all-hands]
  "Let's do an all-hands on Q2 priorities"
        |
        v
[Tool gathers context]
  - Reads current roadmap and backlog
  - Reads recent decisions log
  - Asks user: who is attending? What topics must be covered?
        |
        v
[Tool generates a meeting agenda]
  - Agenda is presented to user for review and edit before anything happens
  - User approves or modifies
        |
        v
[Meeting facilitation mode]
  - Tool presents each agenda item in sequence
  - For each item: surfaces relevant context, asks for input from user (and others if present)
  - Board can be invoked for any item that needs strategic input
  - Tool tracks what was decided for each item in real time
        |
        v
[Post-meeting summary]
  - Tool drafts a written summary of what was covered and what was decided
  - User reviews and approves before it is saved
  - Approved summary saved to sessions/ and relevant decisions added to org/decisions.md
  - Action items offered for addition to backlog
```

**Guardrails:**
- The agenda is always user-approved before facilitation begins
- The post-meeting summary is always user-approved before being saved
- The tool does not send meeting summaries anywhere (email, Slack, etc.) without
  explicit user action — even at autonomy Level 4

---

## Journey 4: Changing Autonomy Level

```
[User runs: exec config autonomy]
        |
        v
[Show current level with plain-language description]
        |
        v
[Show all four levels with examples]
  Highlight current level. If moving up, show a plain-language explanation of
  what additional trust the user is granting. If moving down, confirm.
        |
        v
[If moving to Level 3 or 4]
  - Require explicit acknowledgment: "I understand that at this level,
    the CEO will [specific behavior]. I want to proceed."
  - Log the change with timestamp to board/config.md
        |
        v
[Change saved. Confirm new level to user.]
```

**Guardrails:**
- Level 3 and 4 are not available in MVP (enforced in code, not config)
- Moving to Level 3 or 4 always requires an explicit acknowledgment — not just a Y/N
- Every autonomy level change is logged with timestamp

---

## Journey 5: The Exec Replacement Audit (Existing Orgs)

For users who want to build a case for replacing or restructuring their executive team.

```
[User requests an exec audit]
  "Build me a case for restructuring our leadership"
        |
        v
[Tool asks for context]
  - What is the current org structure? (User describes or uploads a doc)
  - What is the stated mission/values of the org?
  - What outcomes matter most to the workers and stakeholders you're trying to serve?
        |
        v
[Board analyzes the structure]
  - Each archetype independently assesses the structure against the stated mission/values
  - Identifies gaps between stated values and structural incentives
  - Identifies decision-making bottlenecks, single points of failure, misaligned incentives
        |
        v
[Tool produces a structured report]
  - What the current structure optimizes for (whether intentional or not)
  - Where the structure contradicts the org's stated values
  - What a more democratic/worker-aligned structure could look like
  - The case for change, written in plain language, suitable for sharing internally
        |
        v
[User reviews, edits, and decides what to do with it]
  The report is the user's document. The tool has no opinion on what they do next.
```

**Guardrails:**
- The report is explicitly framed as analysis and a case for consideration — not
  a legal document, HR advice, or a guarantee of any outcome
- A disclaimer is included in the report output and cannot be removed

---

## Journey 6: The Easter Egg — What We Would Have Built

A hidden, optional, cathartic feature. Not surfaced in main navigation.

```
[User discovers or activates the feature]
  (e.g., a specific command, or a prompt like "what would we have built?")
        |
        v
[Tool asks]
  "Tell me about the product you were working on and what happened.
   No filter — just say what you want to say."
        |
        v
[User vents / describes the product and the situation]
        |
        v
[Board session: the alternative timeline]
  "If the team that built this hadn't been let go, and they had the right
   resources and support, what could this product have become?"
  Board deliberates. Output is generative and celebratory — not a postmortem.
        |
        v
[Output: The Better Product]
  - What the product could have been
  - What was genuinely good about the work that was done
  - What the team that built it deserved
  The tone is warm, specific, and human. This is not a business analysis.
        |
        v
[Optional: export as a document the user can keep]
```

**Guardrails:**
- This feature does not connect to external services
- Output is never automatically shared anywhere
- The tool does not minimize, rationalize, or provide "both sides" of a layoff.
  Its job here is to be on the user's side.
