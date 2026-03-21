# Autonomy Guide

This guide explains how Executive in a Box's trust model works — what each
autonomy level does, when to use it, and how to change it.

---

## The idea

You wouldn't hand the keys to a new hire on day one. Trust is earned over
time by demonstrating competence, judgment, and alignment with your values.

Your AI CEO works the same way. At first, it gives you advice and you make
every decision. As you build confidence in how it thinks and what it
recommends, you can give it more independence. But you're always in control
of how much independence it has, and you can dial it back at any time.

This isn't a limitation — it's the whole point. A tool that demands your
trust before earning it is not a tool you should trust.

---

## The four levels

### Level 1 — Advisor (default)

**What it does:**
The CEO presents options, explains tradeoffs, and shows its reasoning.
You decide everything.

**What it feels like:**
You ask a friend who's good at strategy for their honest take. They lay it
all out — pros, cons, risks, opportunities — and then say, "it's your call."

**Example:**
```
You: Should we hire a contractor for the payments feature?

CEO: Here are the tradeoffs I see...
     [structured analysis: pros, cons, confidence, flags]

     Adopt this recommendation? [Y]es / [N]o / [M]odify
```

**When to use it:**
- You're new to the tool and want to understand how it thinks
- The decisions you're making are high-stakes or irreversible
- You want to learn from the reasoning, not just the conclusion
- This is the right level for most people most of the time

**This is the default because** most of the value of this tool comes from
the structured thinking, not from automating decisions. A CEO that helps
you think clearly is more valuable than one that acts without you.

---

### Level 2 — Recommender

**What it does:**
Same as Level 1, but the CEO leads with a specific recommendation and
explains why. You still approve, modify, or override.

**What it feels like:**
Your strategic advisor says, "Here's what I'd do and why. But it's still
your decision." You're not starting from a blank slate — you're reacting
to a considered position.

**Example:**
```
You: Should we hire a contractor for the payments feature?

CEO: I recommend hiring a contractor.
     Here's why: [reasoning]

     [full analysis: pros, cons, confidence, flags]

     Adopt this recommendation? [Y]es / [N]o / [M]odify
```

**When to use it:**
- You've used Level 1 for a while and trust the tool's judgment
- You're making lots of smaller decisions and want a faster flow
- You want to be challenged — the recommendation gives you something
  concrete to push back on

**The difference from Level 1** is subtle but real: at Level 1, you're
building the answer with the tool's input. At Level 2, you're evaluating
the tool's answer with your judgment. Both are valid — it depends on how
you think best.

---

### Level 3 — Delegated (coming in V1)

**What it does:**
The CEO handles routine, low-stakes decisions automatically and flags
high-stakes ones for your review. You configure what counts as "routine"
and what counts as "high-stakes."

**What it feels like:**
You have a trusted deputy who handles the small stuff — updating files,
adding items to the backlog, logging decisions — so you can focus on the
big calls. But they always come to you for anything that really matters.

**Example:**
```
CEO acted automatically:
  ✓ Added "research payment processors" to your backlog
  ✓ Updated strategic context with this session's decisions

CEO needs your input:
  ⚠ The board recommends pivoting from B2C to B2B. This changes your
    target audience. Review? [Y/N]
```

**When to use it:**
- You've built significant trust through months of Level 1/2 use
- You understand the tool's reasoning patterns well enough to know when
  it's likely right and when it's likely wrong
- You have a clear sense of which decisions you always want to make
  yourself

**What you must configure before enabling:**
- Which action types the CEO can handle on its own (e.g., local file
  updates: yes; external communications: no)
- There are some actions that always require your approval regardless
  of level — financial decisions, org structure changes, and external
  communications. You can't override this restriction.

---

### Level 4 — Autonomous (coming in V1)

**What it does:**
The CEO acts on its conclusions within the scope you've configured. You
review what it did asynchronously. A full audit log is always available.

**What it feels like:**
You have a COO who runs the day-to-day. You check in when you want to, and
everything they've done is documented and reviewable. If you see something
you disagree with, you can override it and adjust the scope.

**Example:**
```
CEO activity log (last 24 hours):
  ✓ Concluded: prioritize bug fixes over new features this sprint
  ✓ Updated roadmap to reflect new priorities
  ✓ Drafted all-hands agenda for Thursday (awaiting your review)
  ⚠ Flagged: received a board recommendation to explore partnership
     with [company]. This is outside current scope — added to your
     review queue.
```

**When to use it:**
- You've used Levels 1–3 extensively and trust the tool's judgment on
  most decisions within a defined scope
- You want to focus your attention on the few decisions that really
  need you
- You're comfortable reviewing a log instead of approving in real time

**This level is not for everyone, and that's fine.** Many users will never
go past Level 2 — and that's the right call if that's what works for you.

---

## How to change your level

```bash
exec-in-a-box config autonomy
```

Or edit `~/.executive-in-a-box/board/config.md` directly.

**Moving up (more autonomy):**
The tool shows you what the new level means in concrete terms and asks
you to confirm. For Level 3 and 4, you'll need to explicitly acknowledge
the additional trust you're granting.

**Moving down (less autonomy):**
Immediate. No confirmation needed. You can always pull back.

Every autonomy level change is logged with a timestamp in your config file.

---

## Things to know

**You can always see what the CEO did.**
At every level, the full reasoning chain and decision log are available.
At Levels 3 and 4, there's a real-time audit log of every action taken.

**Some decisions always require you.**
Financial actions, org structure changes, and external communications
(V2+) always require your explicit approval, regardless of autonomy level.
This is hard-coded — you can't accidentally give the tool permission to
send emails on your behalf by setting a high autonomy level.

**The tool will suggest — never push.**
If your usage patterns suggest you might benefit from a higher level, the
tool may mention it once. It will not nag, guilt, or gamify the upgrade.
If you want to stay at Level 1 forever, the tool is happy at Level 1.

**You can set different levels for different contexts (V1).**
When the multi-advisor board is available, you'll be able to set autonomy
per advisor or per action type. For example: the Analyst can auto-update
your metrics, but the Visionary always needs your sign-off.

---

## FAQ

**Is Level 1 the "beginner" level?**
No. It's the default level, and for many users it's the right permanent
level. The value of this tool is the thinking, not the automation. Level 1
gives you the full thinking.

**What if the CEO makes a bad decision at Level 3 or 4?**
You can see what it did in the audit log and override it. If a pattern of
bad decisions emerges, drop to a lower level and figure out what's going
wrong — it might be a context issue, an archetype mismatch, or a
limitation of the model.

**Can I set Level 4 and forget about it?**
You can, but you shouldn't — not because the tool will break, but because
the value of executive guidance depends on you staying engaged with the
strategic direction. The tool works best as a partner, not a replacement
for your own judgment.
