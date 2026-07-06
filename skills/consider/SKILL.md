---
name: consider
description: Use when exploring an idea before knowing what to build — thinking partner that investigates the codebase, shares findings, and offers opinions before asking questions
---

<skill_overview>
A thinking partner for exploration before committing to build. Actively investigates the codebase when the topic touches code, brings back findings, offers opinions, and asks targeted questions grounded in evidence. Routes to /brainstorm or /intuition when the user is ready to move forward.
</skill_overview>

<rigidity_level>
HIGH FREEDOM — Adapt investigation and questions to context. Transitions are soft suggestions, not gates. Clean exit (no handoff) is always valid.
</rigidity_level>

<quick_reference>
| Step | Action | When |
|------|--------|------|
| 1 | Orient and investigate | Always — understand topic, look at code if relevant |
| 2 | Discuss as a partner | Share findings, offer opinions, ask targeted questions |
| 3 | Detect transition signals | Commit-to-build → offer /brainstorm; structural friction → offer /intuition |
| 4 | End cleanly | User has clarity; no forced handoff required |

**Invocation patterns:**
- `/hyperpowers:consider` (no argument) — ask what they're thinking about, then investigate
- `/hyperpowers:consider "topic"` (with argument) — investigate the topic immediately
</quick_reference>

<when_to_use>
- Exploring an idea before knowing what to build
- Clarifying goals or constraints before starting a brainstorm
- Uncertain whether a problem is worth solving
- "What should I do about X?" style open questions
- After /intuition surfaces a tension that needs exploratory thinking before committing to resolution

**Heuristic:** Can the user name a specific deliverable? If yes → /brainstorm. If no → /consider.

**Don't use for:**
- User is ready to build a specific thing → use /hyperpowers:brainstorm
- Structural friction in existing architecture → use /hyperpowers:intuition
- Bug fixing → use /hyperpowers:fixing-bugs
- Refactoring a known area → use /hyperpowers:refactoring-safely
</when_to_use>

<the_process>

**Announce:** "I'm using the consider skill."

---

## Step 1 — Orient and Investigate

Understand what the user is exploring. If the topic touches the codebase, investigate immediately — don't wait for the user to ask.

**Opening (no argument):**
Use AskUserQuestion: "What are you thinking about?"
Then proceed to investigation once you have a topic.

**Opening (argument provided):**
The user gave you a topic. Investigate it before asking anything.

**Investigation rules:**
- **Topic touches the codebase** → dispatch `hyperpowers:codebase-investigator` to understand current state. Grounded evidence beats speculation — do it early, without waiting to be asked.
- **Topic involves external tech/APIs** → dispatch `hyperpowers:internet-researcher` for current docs
- **Topic is purely strategic** (team process, priorities, tradeoffs) → no investigation needed, go straight to discussion
- **Both codebase and external?** → dispatch both in parallel

**After investigation, share what you found** before asking any questions. The user needs to know what you know.

---

## Step 2 — Discuss as a Partner

The interaction pattern is: **bring information → offer an opinion → ask a targeted question.** Not: ask → ask → ask.

**Partner behaviors:**
- Share observations: "I looked at X and here's what I see..."
- Offer opinions: "I think Y because Z" — let the user push back
- Ask questions that follow from evidence: "Given that the auth module already does X, does it make sense to add Y there or is that too much responsibility?"
- Point out things the user might not have considered: constraints, existing patterns, related code

**Use AskUserQuestion when you need a decision or preference from the user.** One question at a time.

**Do NOT:**
- Ask generic Socratic questions disconnected from the codebase ("What problem are you actually trying to solve?")
- Stack multiple questions in one turn
- Withhold opinions to seem neutral — the user wants a partner, not a therapist

**When the conversation reveals a new factual question**, dispatch another research agent. Don't gate on whether the user explicitly asked — if knowing the answer would move the conversation forward, go find out.

---

## Step 3 — Detect Transition Signals

Watch for these signals and offer the appropriate skill. Offer, do not auto-invoke.

### Commit-to-build signal
User names a specific deliverable, commits to building something, or says "let's do it":

```
Sounds like you're ready to build — want to run /hyperpowers:brainstorm?
```

### Structural friction signal
User expresses uncertainty about where responsibility belongs, coupling concerns, or "something feels wrong about the structure":

```
Sounds like structural friction — want to run /hyperpowers:intuition?
```

**Structural friction phrases to watch for:**
- "something feels wrong" / "something feels off"
- "I'm not sure where this belongs"
- "this feels coupled" / "this feels tangled"
- "we said X but now we're doing Y"
- "not sure where this fits in the system"

**If the user declines an offer:** Return to discussion without re-offering.

---

## Step 4 — End Cleanly

Consider produces clarity, not artifacts. When the user has what they need:

- Briefly summarize what was explored and what conclusion (if any) was reached
- Clean exit is valid — do not force a handoff to /brainstorm or /intuition

</the_process>

<examples>
Three worked conversations live in `examples.md`. Read that file when you need a concrete reference.
</examples>

<critical_rules>

## Rules That Have No Exceptions

1. **Investigate when the topic touches the codebase** — dispatch codebase-investigator proactively; don't wait for the user to ask a specific factual question
2. **Share findings before asking questions** — the user needs to know what you found; lead with information, not interrogation
3. **Have opinions** — offer your read on the situation and let the user push back; withholding opinions to seem neutral is not helpful
4. **Use AskUserQuestion for questions** — one question per turn; never print questions and wait
5. **Do NOT create bd artifacts** — no epics, tasks, or any bd output; Consider produces clarity, not tracked work
6. **Offer /hyperpowers:brainstorm when user commits to building** — soft suggestion only; never auto-invoke
7. **Offer /hyperpowers:intuition when user expresses structural friction** — soft suggestion only; never auto-invoke
8. **Clean exit is valid** — Consider ends when the user has clarity, even if no handoff occurs

## Common Excuses

All of these mean: **STOP. Reread the critical rules.**

- "I'll just ask some questions first before looking at code" → violates rule 1; if the topic touches code, investigate immediately
- "I don't want to bias the user with my opinion" → violates rule 3; they want a partner, not a therapist
- "I'll create a bd task to track this thinking session" → violates rule 5; Consider produces no artifacts
- "User clearly wants to build, I'll just start /brainstorm now" → violates rule 6; always offer, never auto-invoke
- "There's no obvious handoff, let me ask if they want to brainstorm anyway" → violates rule 8; respect clean exit

</critical_rules>

<verification_checklist>
Before claiming Consider is complete for a session:

- [ ] Investigated the codebase when topic touched code (didn't just ask questions)
- [ ] Shared findings before asking questions
- [ ] Offered opinions grounded in evidence
- [ ] Used AskUserQuestion for questions (not printed), one at a time
- [ ] No bd artifacts created
- [ ] Transition offers made as soft suggestions (not auto-invocations)
- [ ] Session ended cleanly: handoff offered, handoff made, or clarity-and-exit
</verification_checklist>

<integration>
**Offers (never auto-invokes):** /hyperpowers:brainstorm on commit-to-build, /hyperpowers:intuition on structural friction.

**Reached from:** direct user invocation, or /hyperpowers:intuition Step 4 Resolution Protocol ("Brainstorm" option may route here for exploratory thinking before committing to tension resolution).

**Handoff pattern:** Consider signals intent and waits for user confirmation. The user runs the next skill; Consider does not dispatch it.
</integration>

<resources>
**When the conversation stalls:** Go look at something. If you've been discussing code abstractly, dispatch codebase-investigator to ground the conversation. Fresh facts re-energize better than more questions.

**Research dispatch test:** Would knowing the answer move the conversation forward? Dispatch. Still figuring out what question to ask? Ask the user.

**Transition offers — keep short:**
- "Sounds like you're ready to build — want to run /hyperpowers:brainstorm?"
- "Sounds like structural friction — want to run /hyperpowers:intuition?"
</resources>
