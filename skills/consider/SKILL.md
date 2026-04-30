---
name: consider
description: Use when exploring an idea before knowing what to build — Socratic thinking partner that routes to /brainstorm on commit-to-build or /intuition on structural friction
---

<skill_overview>
A lightweight Socratic thinking partner for exploration before committing to build. Ask clarifying questions, optionally dispatch research agents when conversation reveals a factual need, and offer /brainstorm or /intuition when the user is ready to move forward.
</skill_overview>

<rigidity_level>
HIGH FREEDOM — Adapt Socratic questions to context. Transitions are soft suggestions, not gates. Research agents dispatch only when the conversation reveals a specific factual need. Clean exit (no handoff) is always valid.
</rigidity_level>

<quick_reference>
| Step | Action | When |
|------|--------|------|
| 1 | Understand via AskUserQuestion (one at a time) | Always — start here |
| 2 | Research on-demand | Only when conversation reveals a factual question |
| 3 | Detect transition signals | Commit-to-build → offer /brainstorm; structural friction → offer /intuition |
| 4 | End cleanly | User has clarity; no forced handoff required |

**Invocation patterns:**
- `/hyperpowers:consider` (no argument) — open with "What are you thinking about?"
- `/hyperpowers:consider "topic"` (with argument) — open with "You mentioned [topic] — what's the specific concern or uncertainty?"
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

## Step 1 — Understand via Socratic Questions

Use AskUserQuestion for each question — do not print questions and wait. One question at a time.

**Opening question (no argument):**
```
What are you thinking about?
```

**Opening question (argument provided):**
```
You mentioned [topic] — what's the specific concern or uncertainty?
```

**Useful Socratic patterns:**
- "What problem are you actually trying to solve?"
- "What would change if you knew the answer?"
- "What have you already ruled out, and why?"
- "What's the simplest thing that could work?"
- "What would need to be true for this to be worth doing?"
- "Who else is affected by this decision?"

**Guidelines:**
- Follow the user's answers — let the conversation determine the next question
- Do not ask more than one question per turn
- Stop asking when the thinking space is clear or the user has reached a conclusion

---

## Step 2 — Research On-Demand

Dispatch a research agent ONLY when the conversation reveals a factual question that cannot be answered Socratically.

**Triggers for research dispatch:**
- User asks "does library X support Y?" → dispatch `hyperpowers:internet-researcher`
- User asks "is there code in this repo that does Z?" → dispatch `hyperpowers:codebase-investigator`
- User says "I'm not sure if [factual thing] exists" → dispatch the appropriate agent

**Non-triggers (do NOT dispatch):**
- User expresses uncertainty, preference, or opinion
- User is still thinking through goals
- User hasn't named a specific factual question yet
- Skill start — never dispatch preemptively

**Never dispatch both agents at skill start.** Research serves the conversation; the conversation doesn't serve research.

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

**If the user declines an offer:** Return to exploration without re-offering. Do not lock into a transition once an offer was declined. The user may re-enter exploration freely.

---

## Step 4 — End Cleanly

Consider produces clarity, not artifacts. When the user has what they need:

- Briefly summarize what was explored and what conclusion (if any) was reached
- Clean exit is valid — do not force a handoff to /brainstorm or /intuition

**Example clean exit:**
```
You explored [topic]. The key insight was [conclusion]. No action committed to — 
status quo is acceptable given [reason]. Let me know if anything changes.
```

</the_process>

<examples>
Three worked conversations (caching commit-to-build, refactor clean-exit, rate-limiting friction-to-intuition) live in `examples.md`. Read that file when you need a concrete reference.
</examples>

<critical_rules>

## Rules That Have No Exceptions

1. **Use AskUserQuestion for all Socratic questions** — one question per turn; never print questions and wait
2. **Do NOT create a bd epic, task, or any bd artifact inside Consider** — Consider produces clarity, not outputs
3. **Do NOT load architecture context** — no architecture views, no decision-record scanning; architectural work belongs in /intuition
4. **Offer /hyperpowers:brainstorm when user commits to building** — soft suggestion only; never auto-invoke
5. **Offer /hyperpowers:intuition when user expresses structural friction** — soft suggestion only; never auto-invoke
6. **Research agents only on-demand** — never dispatch codebase-investigator or internet-researcher at skill start or preemptively
7. **Clean exit is valid** — Consider ends when the user has clarity, even if no handoff occurs

## Common Excuses

All of these mean: **STOP. Reread the critical rules.**

- "I'll run codebase-investigator to get context first" → violates rule 6; wait for a factual need to emerge
- "User seems uncertain, let me load architecture to help" → violates rule 3; architecture belongs in /intuition
- "I'll create a bd task to track this thinking session" → violates rule 2; Consider produces no artifacts
- "User clearly wants to build, I'll just start /brainstorm now" → violates rule 4; always offer, never auto-invoke
- "There's no obvious handoff, let me ask if they want to brainstorm anyway" → violates rule 7; respect clean exit

</critical_rules>

<verification_checklist>
Before claiming Consider is complete for a session:

- [ ] Used AskUserQuestion for every question (not printed)
- [ ] Asked one question at a time (no multi-question turns)
- [ ] Research agents dispatched only when conversation revealed factual need
- [ ] No architecture context loaded (no architecture views, no decision-record scanning)
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
**When the conversation stalls:** "What would change if you knew the answer?" — almost always re-energizes. If the user keeps giving vague answers, make the question concrete: "name one thing you'd change if you could."

**Research dispatch test:** Is the user stuck on a factual unknown (does X exist? does Y support Z?)? Dispatch. Still figuring out what they want? More Socratic questions, not research.

**Transition offers — keep short:**
- "Sounds like you're ready to build — want to run /hyperpowers:brainstorm?"
- "Sounds like structural friction — want to run /hyperpowers:intuition?"
</resources>
