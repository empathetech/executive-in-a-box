# Archetype Guide

This guide explains what archetypes are, what each one does, and how to
choose the right advisor for your org.

---

## What are archetypes?

An archetype is a reasoning style — a way of approaching strategic decisions.
When you pick an archetype, you're telling the tool how to think about your
problems, not what to think about them.

Archetypes are **not personalities.** The Advocate isn't "nice" — it's
structurally biased toward outcomes that benefit your workers and your stated
values. The Analyst isn't "cold" — it wants evidence before committing your
limited resources to something unproven.

Every archetype gets the same information about your org (name, mission,
values, recent decisions). They differ in what they prioritize, what they're
skeptical of, and where they look for risk and opportunity.

---

## The four built-in archetypes

### The Operator

**One line:** Pragmatic, execution-focused, risk-aware.

**How it thinks:**
The Operator starts with what's real: your current resources, your team's
capacity, your timeline. It asks "can we actually do this?" before asking
whether we should. It favors the path that gets something concrete in front
of users fastest, with the least risk of stalling or overcommitting.

**Example question:** "Should we rebuild our auth system or keep patching it?"

**The Operator's style:**
> "How many hours has your team spent patching auth in the last month?
> If it's less than 10% of your capacity, keep patching — a rebuild is a
> multi-week project that blocks everything else. If it's more, the patches
> are the expensive option and a rebuild pays for itself within a quarter.
> Either way, don't rebuild and patch at the same time."

**Strengths:**
- Cuts through ambiguity with actionable next steps
- Good at identifying when a plan is too big or too vague to execute
- Keeps you honest about what your team can actually ship

**Blind spots:**
- May undervalue long-term bets that don't have an obvious near-term payoff
- Can be conservative about bold moves even when the risk is worth it
- Tends to optimize for "what's doable" over "what's transformative"

**Best for:** Orgs in execution mode — you know what you want to build and
need someone to keep you focused, realistic, and shipping.

---

### The Visionary

**One line:** Ambitious, long-horizon, tolerant of uncertainty.

**How it thinks:**
The Visionary asks where you want to be in two years and works backward.
It's comfortable with uncertainty and willing to take calculated risks on
unproven ideas if the upside is high enough. It pushes you to think bigger
than your current constraints suggest.

**Example question:** "Should we rebuild our auth system or keep patching it?"

**The Visionary's style:**
> "Neither. Auth is a solved problem — use a third-party provider and spend
> your engineering time on the thing only you can build. The real question
> is: what would you build with those hours if auth wasn't on your plate?
> That's where your competitive advantage lives."

**Strengths:**
- Good at reframing problems to find opportunities you hadn't considered
- Pushes you past incremental thinking
- Helps you see how small decisions connect to your bigger picture

**Blind spots:**
- May underestimate execution cost — the big idea still needs to get built
- Can be impatient with the operational realities of a small team
- Sometimes the boring, incremental answer is the right one

**Best for:** Orgs figuring out their direction — you're exploring what's
possible and need someone to expand your thinking.

---

### The Advocate

**One line:** People-first, equity-focused, skeptical of growth-for-growth's-sake.

**How it thinks:**
The Advocate starts with your people: your team, your users, the communities
your org operates in. It evaluates every decision against your org's stated
values and flags when a recommendation contradicts them — even if the
contradiction is profitable. It's structurally skeptical of "we need to
grow" unless growth serves the people the org exists for.

**Example question:** "Should we rebuild our auth system or keep patching it?"

**The Advocate's style:**
> "What's the impact on your users right now? If auth bugs are causing login
> failures, that's a trust issue — and for a co-op, trust is the whole thing.
> Fix what your users are hitting first, then invest in a rebuild when you
> have the runway. And involve your team in the decision — they're the ones
> who'll do the work, so they should have a say in the priority."

**Strengths:**
- Keeps your decisions aligned with your values even under pressure
- Good at identifying when a "business" decision has human consequences
- Protects against the drift toward extractive practices

**Blind spots:**
- May be slow to recommend hard tradeoffs even when they're necessary
- Can prioritize harmony over decisive action in urgent situations
- Sometimes the org needs to make a move that's uncomfortable for people
  in the short term to serve them in the long term

**Best for:** Co-ops, worker-owned orgs, and anyone who needs a voice in the
room that always asks "what does this mean for our people?"

---

### The Analyst

**One line:** Data-driven, cautious, wants evidence before committing.

**How it thinks:**
The Analyst wants to see the numbers, the evidence, or at least a reasoned
estimate before recommending action. It's comfortable saying "we don't have
enough information to decide this" and will suggest ways to get that
information cheaply before making a bet. It's skeptical of intuition-based
decisions, even good ones.

**Example question:** "Should we rebuild our auth system or keep patching it?"

**The Analyst's style:**
> "What's the data? How many auth-related incidents in the last 90 days?
> What's the mean time to resolve each one? What's the estimated effort
> for a rebuild vs. projected patch effort over the next 6 months? If you
> don't have those numbers, get them first — tracking incidents for two
> weeks will cost you almost nothing and will make this decision obvious."

**Strengths:**
- Prevents expensive decisions based on gut feeling alone
- Good at designing low-cost experiments to reduce uncertainty
- Keeps you honest about what you know vs. what you assume

**Blind spots:**
- Not everything important is measurable — values, culture, trust
- Can delay decisions that need to be made with imperfect information
- Sometimes the cost of gathering more data exceeds the cost of being wrong

**Best for:** Orgs making resource-intensive decisions — hiring, major
features, pivots — where being wrong is expensive and being rigorous
pays off.

---

## How to choose

**There's no right answer.** Each archetype gives you something the others
don't, and each has a gap the others fill.

Ask yourself: **what kind of thinking am I least likely to do on my own?**

| If you tend to... | Consider... |
|-------------------|-------------|
| Jump to action without a plan | The Analyst — it'll slow you down just enough |
| Overthink and delay | The Operator — it'll push you to ship |
| Lose sight of the big picture | The Visionary — it'll pull you back up |
| Deprioritize your people under pressure | The Advocate — it'll hold the line |

Don't pick the archetype that thinks like you already do. Pick the one that
fills your blind spot.

---

## Board of many (coming in V1)

In V1, you'll be able to have multiple archetypes active at the same time.
Each one weighs in independently on your question, and the tool shows you
where they agree, where they disagree, and why.

This is the "board of directors" model. You compose your board by picking
the perspectives you want represented, and you're always the tiebreaker.

Good board compositions:

| Board | Why it works |
|-------|-------------|
| Operator + Visionary | Balances "can we do it?" with "should we think bigger?" |
| Advocate + Analyst | Balances values-alignment with evidence-based rigor |
| All four | Maximum diversity of perspective — best for big, complex decisions |
| One archetype | Nothing wrong with this. Sometimes one clear lens is all you need. |

---

## Custom archetypes (coming in V1)

In V1, you'll be able to edit the built-in archetypes or create your own.
A custom archetype is a reasoning style you define: what it prioritizes,
what it's skeptical of, and how it approaches problems.

For example, you might create:
- **The Founder** — obsessed with product-market fit, moves fast, allergic
  to anything that doesn't serve the core user
- **The Steward** — focused on long-term sustainability, cautious about
  debt (financial and technical), thinks in decades

Custom archetypes use the same structured output format as built-in ones,
so they work with all the same tools — board aggregation, spectrum view,
and the full audit trail.
