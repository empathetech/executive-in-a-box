# User Journeys

<!-- Maps how users move through the product across key scenarios.
     These journeys define what the tool must do, in what order, and what
     the user sees at each step. Implementation must match these flows.
     When a journey changes, update this doc and write an ADR if the change
     is significant.

     Rewritten 2026-04-04 for web app + CLI + Claude skill three-interface model.
     See decisions/2026-04-04-web-ui-pivot.md. Prior CLI-only journeys archived. -->

---

## Journey 1: First Launch (Setup / Onboarding)

Runs once on first launch. Establishes the org profile, configures the board,
and sets the autonomy level. Must be completable by a non-technical user in
under 15 minutes across all three interfaces.

### Web App

```
[Navigate to localhost:PORT for the first time]
        |
        v
[Full-screen onboarding wizard — styled in the product aesthetic]
  Step 1: Welcome
    "Executive in a Box. Let's set up your board."
    Brief explanation of what the tool is. No jargon.
        |
        v
  Step 2: Your Org
    - Org name
    - What does it do? (1-2 sentences)
    - What are the most important values it operates by?
    Saved to org/profile.md
        |
        v
  Step 3: Your Board
    - Board size: one advisor or multiple?
    - Pick archetypes from illustrated cards (portrait + plain-language description)
    - For each archetype: pick LLM provider
    - Enter API key per provider (masked input, stored in OS keychain)
    - Test call made to validate each key before proceeding
        |
        v
  Step 4: Autonomy Level
    - Four levels shown as illustrated cards with plain-language examples
    - Recommend Level 1 for new users, explain why
    - User picks a level
    - If Level 3 or 4: explicit acknowledgment modal required
        |
        v
  Step 5: Review & Launch
    - Show board composition: portrait strip with archetype name and provider
    - Show autonomy level with description
    - "You can change any of this in Settings at any time."
    - [Launch] → main three-pane interface
```

### CLI

```
[Run exec-in-a-box for the first time]
        |
        v
[ASCII welcome banner — design per STYLE_GUIDE.md]
  Wizard prompts run sequentially in the terminal.
  Same steps as web app, adapted for text input.
  Provider API keys entered with masked echo.
  Test call validates each key before proceeding.
  Setup complete → drop into main chat prompt.
```

### Claude Skill

```
[Run /exec-in-a-box for the first time]
        |
        v
[Skill detects no config exists]
  Prints setup instructions — directs user to run the CLI or web app
  setup wizard first. The skill does not run its own setup wizard;
  it reads the config written by the other interfaces.
```

**Guardrails (all interfaces):**
- Cannot proceed without minimum valid config (org name + at least one archetype + one provider)
- API keys validated by test call before setup completes
- No LLM call made until board config is confirmed by user
- Level 3/4 always require explicit acknowledgment, cannot be skipped

---

## Journey 2: A Board Session (Core Loop)

The primary interaction. User asks a strategic question; the board responds;
user decides. This is a **conversational** loop — follow-up questions are natural
and expected. Session history persists within the interface.

### Web App

```
[User types a question in the chat input for the active CEO]
  e.g. "Should we hire a contractor for payments or build it ourselves?"
        |
        v
[Wrapper pre-flight (our code, not the LLM)]
  - Scan context for secrets
  - Load archetype system prompt + org context + relevant memory
  - Log query to session transcript
        |
        v
[Streaming response]
  - Response streams to the chat window in typewriter style
  - CEO portrait shows active/thinking state during streaming
  - User can switch to another CEO's chat tab while this streams
        |
        v
[Response rendered in chat]
  - CEO's position, reasoning, confidence, pros/cons, flags shown
  - Collapsible "How it got here" section
  - Schema validation has already run — only valid output is shown
        |
        v
[User decision — per autonomy level]
  Level 1/2: Y/N/Modify action shown below the response
  Level 3/4: auto-acted if within configured scope; logged for async review
        |
        v
[Record outcome]
  - Decision logged to org/decisions.md
  - Strategic memory updated if relevant
  - Follow-up question or next topic continues the conversation naturally
```

### Deep Work (Executize path)

```
[User clicks "Executize" or backend estimates long duration]
        |
        v
[Job dispatched to backend job system]
  - CEO portrait enters Executizing state (faded, archetype verb displayed)
  - Chat input for that CEO is disabled
  - Toast: "[Archetype] is [verb]. You can still chat with other CEOs."
        |
        v
[User continues chatting with other CEO tabs — fully interactive]
        |
        v
[Job completes]
  - Toast notification: "The [Archetype] is back." + action to view response
  - CEO portrait returns to active state
  - Response delivered to that CEO's chat window
```

### CLI

```
[User types a question at the prompt]
  Active CEO shown in prompt prefix: [OPERATOR] >
        |
        v
[Streaming output to terminal — typewriter style via progressive print]
        |
        v
[Response printed with ASCII structure per STYLE_GUIDE.md]
  Position / reasoning / confidence / pros / cons / flags
        |
        v
[Y/N/Modify prompt per autonomy level]
        |
        v
[For deep work: "exec --executize 'question'" dispatches a background job]
  Status line shows Executizing state.
  Other CEO prompts remain available via --ceo flag.
  Completion notification printed when job finishes.
```

### Claude Skill

```
[User runs /exec-in-a-box "question"]
        |
        v
[Skill submits to backend, streams response as markdown output]
        |
        v
[For deep work: skill returns immediately with job ID]
  "🌀 [VISIONARY] Envisioning... (job abc123). Ask other CEOs or check back."
  User runs /exec-in-a-box status abc123 or asks another CEO.
  Skill notifies when job is complete on next invocation.
```

**Guardrails (all interfaces):**
- Aggregation is done in code, not a second LLM call
- Invalid archetype responses are excluded; session continues with valid ones
- User's final decision is always recorded, even at Level 4
- Streaming interruptions save partial output to transcript and offer retry

---

## Journey 3: Switching Between CEOs

Users can maintain separate ongoing conversations with each CEO archetype.
Each conversation has its own persistent history.

### Web App

```
[CEO portrait strip visible above chat area]
  Each portrait: name, archetype, autonomy level toggle, Executizing state if active
        |
        v
[User clicks a portrait to switch active CEO]
  Chat history for that CEO loads in the center pane.
  Input bar activates for the selected CEO.
  Other CEOs' conversations are preserved exactly.
```

### CLI

```
[User switches active CEO]
  exec-in-a-box --ceo visionary
  Or interactively: type /switch at the prompt for a numbered menu.
  Prompt prefix updates: [VISIONARY] >
  Prior conversation history for this CEO is shown on switch.
```

### Claude Skill

```
[User specifies CEO in command]
  /exec-in-a-box --ceo analyst "What's the risk profile?"
  Skill tracks active CEO in session state.
  History accessible via /exec-in-a-box history --ceo analyst
```

---

## Journey 4: Creating and Managing Artifacts

When a CEO generates a document, analysis, or other artifact, it is saved
and accessible across sessions.

### Web App

```
[CEO response contains or generates an artifact]
  e.g. "Here's the strategic brief you asked for: [artifact]"
        |
        v
[Artifact saved to artifacts/<session-id>/]
  Artifact appears in the left pane artifact explorer immediately.
  Type icon assigned (document, spreadsheet, analysis).
        |
        v
[User clicks artifact in left pane]
  Opens in an overlay panel or new tab.
  User can rename, export, or delete.
```

### CLI

```
exec-in-a-box artifacts list          # list all artifacts
exec-in-a-box artifacts open <id>     # open in $EDITOR or print to stdout
exec-in-a-box artifacts export <id>   # save to a specified path
```

### Claude Skill

```
Artifact reference returned inline as a markdown block.
/exec-in-a-box artifacts list    # list artifacts
/exec-in-a-box artifacts <id>    # print artifact content
```

---

## Journey 5: Announce to Slack

User composes and sends a message to a configured Slack channel. The CEO never
auto-sends — the user always reviews before anything is posted.

### Web App

```
[User clicks "Announce" button or opens Announce from a CEO response]
        |
        v
[Modal opens]
  Left half: markdown/text input (pre-populated with selected CEO response if triggered from one)
  Right half: live Slack preview (renders mrkdwn formatting and block elements)
        |
        v
[User edits, previews, confirms]
  "Post to #channel-name?" confirmation with final rendered preview
        |
        v
[Webhook call sent]
  Success: toast "Posted to #channel-name."
  Failure: "Couldn't reach Slack. Check your webhook URL in settings."
```

### CLI

```
exec-in-a-box slack "message"         # send a message
exec-in-a-box slack --last            # send last CEO recommendation
exec-in-a-box slack --preview "msg"   # print Slack block preview to terminal before sending
```

### Claude Skill

```
/exec-in-a-box slack --last           # announce last recommendation
/exec-in-a-box slack "message"        # send a composed message
```

---

## Journey 6: Changing Autonomy Level

Adjustable per-CEO at any time. Levels 3 and 4 always require explicit acknowledgment.

### Web App

```
[User clicks autonomy level buttons below CEO portrait]
  Buttons labeled 1–4. Active level highlighted in Hot Magenta.
  Hover tooltip describes each level in plain language.
        |
        v
[If moving to Level 3 or 4]
  Confirmation modal: plain-language description of what this level means,
  what it will do automatically, and an explicit "I understand" checkbox.
  User must check the box and confirm — not just click OK.
        |
        v
[Change saved. Button state updates. Change logged with timestamp.]
```

### CLI

```
exec-in-a-box config autonomy --ceo operator --level 2
  Shows current level + description of target level.
  Requires explicit confirmation for Level 3/4 ("type CONFIRM to proceed").
  Change logged to board/config.md with timestamp.
```

---

## Journey 6b: Feedback Calibration (Scoring and Modifiers)

After enough decisions accumulate, the user calibrates the CEO's future behavior
by synthesizing feedback. This adjusts per-trait scoring weights that get injected
into future prompts.

### Web App

```
[User opens ScorecardPanel → Feedback tab]
  Shows: current feedback summary text, active/baseline status, trait modifier radar overlay
        |
        v
[User clicks ↻ Update Feedback]
  LLM synthesizes from all decisions for this CEO.
  New summary + trait_adjustments (±0.3 per axis) saved.
  RadarChart updates: adjusted overlay shown in complementary color.
        |
        v
[User reviews feedback]
  Toggle button below radar: "◈ Adjusted Active" / "◇ Baseline Active"
  Toggle state saved — controls whether adjustments inject into future prompts.
  Reset clears feedback and reverts to baseline.
```

### CLI

```
exec-in-a-box feedback show [slug]
  Prints: summary, active/baseline status, last updated
  Trait modifiers bar chart: each trait with adjusted score + ±delta colored by direction
  Recent decisions list (last 5)

exec-in-a-box feedback refresh [slug]
  Synthesizes from decisions → updates summary + trait_adjustments
  Prints updated summary and active state

exec-in-a-box feedback toggle [slug]
  Flips active/baseline — controls prompt injection for future sessions

exec-in-a-box feedback reset [slug]
  Clears all feedback, reverts to archetype baseline
```

### Claude Skill

```
(Not yet implemented — deferred to future milestone)
```

**Guardrails (all interfaces):**
- Synthesis requires at least one decision; if none exist, user is told to make decisions first
- Trait adjustments clamped to ±0.3 per axis; LLM cannot exceed this range
- Toggle state persists between sessions; default is active (adjusted)
- Reset is irreversible — no undo

---

## Journey 7: All-Hands Meeting Facilitation

(V1 feature — not available in current release.)

The tool plans and facilitates a meeting about product direction.

```
[User requests an all-hands via any interface]
        |
        v
[Tool gathers context: roadmap, decisions log, open questions]
  Asks: who is attending? What topics must be covered?
        |
        v
[Agenda generated → user reviews and approves before anything proceeds]
        |
        v
[Meeting facilitation mode]
  Each agenda item presented in sequence.
  Board invoked for items needing strategic input.
  Decisions tracked in real time.
        |
        v
[Post-meeting summary → user reviews and approves → saved]
  Summary saved to sessions/. Decisions added to org/decisions.md.
  Action items offered for backlog.
```

**Guardrails:**
- Agenda always user-approved before facilitation begins
- Summary always user-approved before being saved
- Tool does not send meeting summaries externally without explicit user action

---

## Journey 8: The Exec Replacement Audit (V2+)

For users building a case for replacing or restructuring their executive team.

```
[User requests an exec audit]
        |
        v
[Tool asks for org structure context]
  Current structure, stated mission/values, what outcomes matter most to workers.
        |
        v
[Board analyzes structure]
  Each archetype assesses against stated mission/values.
  Identifies gaps, bottlenecks, misaligned incentives.
        |
        v
[Structured report generated → user reviews]
  What the structure optimizes for.
  Where it contradicts stated values.
  What a more democratic/worker-aligned structure could look like.
  Plain-language, suitable for sharing internally.
```

**Guardrails:**
- Report explicitly framed as analysis, not legal/HR advice
- Disclaimer included in output and cannot be removed

---

## Journey 9: The Easter Egg — What We Would Have Built (V2+)

A hidden, optional, cathartic feature. Not in main navigation.

```
[User discovers or activates the feature]
  (specific command or prompt phrase)
        |
        v
[Tool asks: tell me about the product you were working on and what happened]
        |
        v
[Board session: the alternative timeline]
  Generative and celebratory — not a postmortem.
  What could this have become? What was genuinely good about it?
  What did the team that built it deserve?
        |
        v
[Optional export as a document the user keeps]
```

**Guardrails:**
- Does not connect to external services
- Output never automatically shared anywhere
- The tool does not provide "both sides" of a layoff. It is on the user's side.
