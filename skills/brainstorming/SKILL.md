---
name: brainstorming
description: Use when creating or developing anything, before writing code - refines rough ideas into bd epics with immutable requirements
---

<skill_overview>
Turn rough ideas into validated designs stored as bd epics with immutable requirements; writing-plans produces the full task tree upfront before execution begins.
</skill_overview>

<rigidity_level>
HIGH FREEDOM - The 8-step order is fixed, but Socratic questioning within steps adapts to context.
</rigidity_level>

<quick_reference>
| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | Ask questions (one at a time, AskUserQuestion) | Understanding of the problem and context |
| 2 | Research codebase and external patterns; propose 2-3 approaches | Recommended option with trade-offs documented |
| 3 | Present design in sections (200-300 words each); friction detection | Validated architecture; /intuition offered if friction detected |
| 4 | Architecture Impact Check (5 structural questions) | Impact recorded in epic; /intuition offered if any YES |
| 5 | Create bd epic with IMMUTABLE requirements | Epic with 7 top-level sections and anti-patterns |
| 6 | Sizing gate check, then create complete task tree | All tasks planned upfront with simple/medium classification |
| 7 | Run SRE batch review on full task tree | Refined task tree ready for handoff |
| 8 | Hand off to executing-plans | Lead orchestrates executor subagents with dynamic model selection |
</quick_reference>

<when_to_use>
- User describes new feature to implement
- User has rough idea that needs refinement
- About to write code without clear requirements
- Need to explore approaches before committing
- Requirements exist but architecture unclear
- /intuition Resolution Protocol routes here with a tension as context

**Don't use for:**
- Executing existing plans (use hyperpowers:executing-plans)
- Fixing bugs (use hyperpowers:fixing-bugs)
- Refactoring (use hyperpowers:refactoring-safely)
- Requirements already crystal clear and epic exists
</when_to_use>

<the_process>

**Announce:** "I'm using the brainstorming skill."

---

## Step 1 — Understanding the Idea

Ask focused questions to understand what the user wants to build and why. Use the AskUserQuestion tool — do not print questions and wait.

**Question format:**

```
Question: [Clear question ending with ?]
Options:
  A. [Option] (Recommended) - [Why this is the default]
  B. [Option] - [Trade-off]
  C. Other (please specify)

Priority: CRITICAL | IMPORTANT | NICE_TO_HAVE
```

**Guidelines:**
- 1-5 questions maximum per round (don't overwhelm)
- Multiple choice preferred; include suggested default marked "(Recommended)"
- Fast-path: for IMPORTANT/NICE_TO_HAVE questions with good defaults, offer "Reply 'defaults' to accept all recommended options"
- Ask one CRITICAL question at a time; group IMPORTANT/NICE_TO_HAVE together
- Stop asking once the design space is clear — unresolved NICE_TO_HAVE questions become Open Questions in the epic

**As each question is answered, record in "Key Decisions Made":**
- Question asked
- User's answer
- Implication for requirements or anti-patterns

---

## Step 2 — Exploring Approaches

**Research first, propose second.** Never propose an approach before researching what already exists.

**When to dispatch which agent:**
- Similar feature exists in the codebase → dispatch `hyperpowers:codebase-investigator`
- New integration or unfamiliar library → dispatch `hyperpowers:internet-researcher`
- Both apply → dispatch both

**Capture research findings** as you go: file paths/patterns from codebase, API capabilities/constraints from external sources, dead-end paths (what was explored, why abandoned).

**Propose 2-3 approaches with trade-offs.** Lead with the recommended option and link the recommendation to specific findings (e.g., "matches existing pattern at path/to/file.ts").

---

## Step 3 — Presenting the Design

**Once approach is chosen, present design in 200-300 word sections:**
- Ask after each section: "Does this look right so far?"
- Cover in order: architecture, components, data flow, error handling, testing
- Show research findings inline (e.g., "auth/passport-config.ts already does X")
- Be ready to go back and clarify any section

**Design-time friction detection.** If the architect expresses structural friction during design — uncertainty about where responsibility belongs, coupling concerns, "feels off" comments, difficulty deciding between two component boundaries, mention of a "shim" or pattern contradiction — offer /intuition explicitly. Do NOT auto-redirect; the architect decides.

Suggested phrasing: *"This sounds like structural friction. /intuition can examine your architecture for tensions before you commit. If you'd like to run it, pass prose focus describing the area — e.g., 'examine the [A]/[B] boundary for tensions' — so /intuition can target evidence gathering. Continue with current design, or run /intuition?"*

---

## Step 4 — Architecture Impact Check

After the design is validated, ask these 5 structural questions against the designed solution:

1. Creates a new component/module?
2. Changes the public interface of an existing component?
3. Adds or removes a cross-component dependency?
4. Creates a new request path through 2 or more components?
5. Moves responsibility from one component to another?

Record YES/NO for each in the epic's Architecture Impact section (Step 5 template).

**Routing:**
- 0 boxes checked → proceed to epic creation
- 1+ boxes checked → offer /intuition before epic creation. Pass prose focus naming the affected components. Architect decides; record the routing decision in the epic.

This is a routing mechanism, not a gate — the architect can always proceed.

---

## Step 5 — Creating the bd Epic

After design is validated and Architecture Impact Check recorded, create the epic as an immutable contract.

**Anti-patterns section is required.** It prevents watering down requirements when blockers occur. Always include reasoning.

**Example anti-patterns:**
- ❌ NO localStorage tokens (security: httpOnly prevents XSS token theft)
- ❌ NO new user model (consistency: must integrate with existing db/models/user.ts)
- ❌ NO mocking OAuth in integration tests (validation: defeats purpose of testing real flow)

**Create the epic:**

```bash
bd create "[Feature Name]" \
  --type epic \
  --priority [0-4] \
  --design "$(cat <<'EOF'
## Requirements (IMMUTABLE)
[What MUST be true when complete — specific, testable]
- Requirement 1: [concrete requirement]
- Requirement 2: [concrete requirement]

## Success Criteria (MUST ALL BE TRUE)
- [ ] Criterion 1 (objective, testable — e.g., 'Integration tests pass')
- [ ] Criterion 2 (objective, testable)
- [ ] All tests passing
- [ ] Pre-commit hooks passing

## Anti-Patterns (FORBIDDEN)
- ❌ [Pattern] ([reasoning] — e.g., 'NO localStorage tokens (security: httpOnly prevents XSS token theft)')
- ❌ [Pattern] ([reasoning])

## Approach
[2-3 paragraph summary of chosen approach and why it was selected over alternatives]

## Architecture
[Key components, data flow, integration points, affected files]

## Architecture Impact
(Result of Step 4 Architecture Impact Check)

- [ ] Creates a new component/module — [YES/NO]
- [ ] Changes public interface of existing component — [YES/NO]
- [ ] Adds/removes cross-component dependency — [YES/NO]
- [ ] Creates new request path through 2+ components — [YES/NO]
- [ ] Moves responsibility between components — [YES/NO]

Result: [N] boxes checked. /intuition [was offered and run / was offered and deferred / was not offered (0 checks)].

## Design Rationale

### Problem
[1-2 sentences: what problem this solves, why the status quo is insufficient]

### Research Findings
**Codebase:**
- [file.ts:line] — [what it does, why relevant]
- [pattern discovered, implications]

**External:**
- [API/library] — [key capability or constraint discovered]
- None because [specific reason — e.g., this is a skill-framework refactor with no external dependencies]

### Key Decisions Made

| Question | User Answer | Implication |
|----------|-------------|-------------|
| [Socratic question asked] | [User's response] | [How this shapes requirements or anti-patterns] |

### Approaches Considered

#### 1. [Chosen Approach] (chosen)

**What it is:** [2-3 sentence description]

**Investigation:**
- Researched [X] — found [Y]
- Referenced [file:line] — shows [pattern]

**Pros:**
- [benefit with evidence]

**Cons:**
- [drawback and mitigation]

**Chosen because:** [specific reasoning linking to requirements and codebase patterns]

#### 2. [Rejected Approach A] (rejected)

**What it is:** [2-3 sentence description]

**Why explored:** [what made this seem viable initially]

**Investigation:**
- [what was researched or tried]

**Pros:**
- [benefits it would have had]

**Cons:**
- [fatal flaw or significant drawback]

**REJECTED BECAUSE:** [specific reasoning, linking to anti-patterns or requirements]

**DO NOT REVISIT UNLESS:** [specific condition that would change this decision]

#### 3. [Rejected Approach B] (rejected, if applicable)

**What it is:** [2-3 sentence description]

**Why explored:** [what made this seem viable]

**Investigation:**
- [what was researched]

**Pros:**
- [benefits it would have had]

**Cons:**
- [fatal flaw]

**REJECTED BECAUSE:** [specific reasoning]

**DO NOT REVISIT UNLESS:** [specific condition]

### Scope Boundaries

**In scope:**
- [explicit inclusions]

**Out of scope:**
- [explicit exclusions with reasoning — e.g., "GitHub OAuth: deferred to future epic; single provider is sufficient now"]
- None because [specific reason if nothing is explicitly excluded]

### Open Questions
- [uncertainties to resolve during implementation]
- [decisions deferred to execution phase]
- None because [specific reason if all questions were resolved during brainstorm]
EOF
)"
```

**Every subsection that could reasonably be empty MUST have a "None because [grounded reason]" entry.** Bare "None" or "N/A" is forbidden — it enables skip-thinking rationalization.

---

## Step 6 — Sizing Gate, Then Complete Task Tree

### 6a — Sizing Gate

Before creating tasks, check whether this epic is too large for a single leaf epic:

- Estimated tasks exceed 10?
- Work spans 3 or more distinct components?
- Multiple independent deliverables that could ship separately?

If any are true, offer escalation to grand planner:

> "This scope looks large for a single epic (~[N] tasks across [M] components). The grand planner can decompose it into leaf epics with dependencies, so each epic stays focused. Continue here, or escalate to /grand-plan?"

This is a gate the user can override — not a hard block. If the user says "proceed anyway," create the task tree and note in the epic that the sizing gate was triggered but overridden.

---

### 6b — Create Complete Task Tree

Create ALL tasks for the epic upfront. Every task must be classified as **simple** (2-10 min, Haiku) or **medium** (10-30 min, Sonnet) and linked to the epic.

**Simple task spec** — Goal, Why, Changes, Verification:

```bash
bd create "Task N: [Specific Deliverable]" \
  --type feature \
  --priority [match-epic] \
  --design "$(cat <<'EOF'
## Goal
[What this task delivers — one clear outcome]

## Why
[How this fits the epic — what breaks without it]

## Changes
- [file.ts line/function] — [exact change]
- [file.ts line/function] — [exact change]

## Verification
- [ ] [Specific, measurable outcome]
- [ ] Pre-commit hooks passing
EOF
)"
bd dep add bd-[task] bd-[epic] --type parent-child
```

**Medium task spec** — Goal, Why, Context, Implementation, Tests, Verification, Boundaries:

```bash
bd create "Task N: [Specific Deliverable]" \
  --type feature \
  --priority [match-epic] \
  --design "$(cat <<'EOF'
## Goal
[What this task delivers — one clear outcome]

## Why
[How this fits the epic — what breaks without it]

## Context
[Key files, patterns, or interfaces the executor needs to know]

## Implementation
1. [Step with file path and what to change]
2. [Step with file path and what to change]

## Tests
[Test cases to write — scenario and expected behavior]

## Verification
- [ ] [Specific, measurable outcome]
- [ ] Tests passing
- [ ] Pre-commit hooks passing

## Boundaries
[What is explicitly OUT of scope for this task]
EOF
)"
bd dep add bd-[task] bd-[epic] --type parent-child
```

**Classification guide:**
- Simple: rename, config change, single-file edit, documentation update
- Medium: new component, cross-file change, logic with edge cases, test suite addition

Set task dependencies in bd so execution order is clear: `bd dep add bd-[task-B] bd-[task-A] --type blocking` for tasks that must run in sequence.

---

## Step 7 — Batch SRE Review

**REQUIRED. Do not skip.**

```
Use Skill tool: hyperpowers:sre-task-refinement
```

SRE refinement runs **once against the full task tree** — not per-task, not just the first task. It applies an 8-category corner-case analysis across all tasks: granularity, implementability, success criteria quality, dependency structure, safety standards, edge cases, red flags, and test meaningfulness.

SRE refinement can suggest: splitting tasks that are too large, adding tasks that are missing, reordering dependencies, and strengthening success criteria. The output is a refined task tree ready for execution.

The full task tree review catches systemic gaps (e.g., missing error handling across all tasks). Skipping on "feels heavy" grounds is exactly the rationalization the rule guards against.

---

## Step 8 — Handoff to Executing-Plans

After refinement approved, present the handoff:

```
"Epic [bd-N] is ready with immutable requirements and success criteria.
Full task tree has been batch-reviewed by SRE and is ready to execute.

Ready to start implementation? I'll use executing-plans to orchestrate execution.

The executing-plans skill will:
1. Read the full upfront task list from bd and classify each task as simple or medium
2. Dispatch a fresh executor subagent per task with dynamic model selection
   (Haiku for simple 2-10 min tasks, Sonnet for medium 10-30 min tasks)
3. The executor reads the self-contained task spec, implements, commits, and returns
   a one-liner status (DONE, BLOCKED, or NEEDS_HELP)
4. After each task: lead runs a two-stage review (spec check + code quality),
   then dispatches fresh executor for next task
5. When all tasks complete, a reviewer agent verifies the assembled whole against the epic spec

This approach prevents context exhaustion (small bounded tasks with dynamic model selection)
while keeping full scope visible upfront — all tasks are planned before execution begins."
```

</the_process>

<examples>
Worked examples (skipped-research, upfront-task-tree, missing-anti-patterns) live in `examples.md`. Read that file when you need a concrete reference.
</examples>

<key_principles>
- **One question at a time** — Don't overwhelm; group only IMPORTANT/NICE_TO_HAVE
- **Multiple choice preferred** — Easier to answer; include recommended default
- **Delegate research** — Use codebase-investigator and internet-researcher agents
- **YAGNI ruthlessly** — Remove unnecessary features from all designs
- **Explore alternatives** — Propose 2-3 approaches before settling
- **Incremental validation** — Present design in sections, validate each
- **Epic is contract** — Requirements immutable, tasks adapt
- **Anti-patterns prevent shortcuts** — Explicit forbidden patterns stop rationalization under pressure
- **Complete task tree upfront** — All tasks planned before execution; execution order set by dependencies
</key_principles>

<critical_rules>
1. **Use AskUserQuestion tool** → Don't print questions and wait
2. **Research BEFORE proposing** → Use agents to understand context before suggesting approaches
3. **Propose 2-3 approaches with trade-offs** → Don't jump to a single solution
4. **Epic requirements IMMUTABLE** → Tasks adapt, requirements don't
5. **Include anti-patterns section with reasoning** → Prevents watering down requirements when blockers occur
6. **Create the complete task tree** → All tasks planned upfront with simple/medium classification; check sizing gate first
7. **Run SRE batch review before handoff** → Reviews full task tree once; catches systemic gaps and weak criteria
8. **Offer /intuition when design-time friction detected** → Architect-decides routing, not a gate
9. **Architecture Impact Check required before epic finalization** → 5 questions, record result in epic, offer /intuition if any YES
10. **Subsection 'None' requires grounded justification** → "None because [specific reason]"; bare "None" enables skip-thinking

**Common excuses that mean STOP and follow the process:**
- "Requirements obvious, don't need questions" — Questions reveal hidden complexity
- "I know this pattern, don't need research" — Research might show a better way or a conflict
- "Scope is small, sizing gate doesn't apply" — Check task count and components anyway; gate is cheap
- "Anti-patterns section is overkill" — Prevents rationalization under pressure
- "Epic can evolve" — Requirements are a contract; tasks evolve, requirements don't
- "Batch SRE review is overkill for a small plan" — Full-tree review catches systemic gaps a per-task pass misses
- "Only one box checked, /intuition not worth it" — Offer it; the architect decides
- "'None' is fine here" — Bare 'None' enables skip-thinking; write the reason
</critical_rules>

<verification_checklist>
Before handing off to executing-plans:

- [ ] Used AskUserQuestion for all clarifying questions
- [ ] Researched codebase + external (when applicable); proposed 2-3 approaches
- [ ] Architecture Impact Check done (Step 4); /intuition offered if 1+ YES or friction detected
- [ ] bd epic has all 7 sections; Design Rationale has 6 subsections; every empty subsection has "None because [reason]"
- [ ] Anti-patterns include reasoning ("NO X (reason: Y)")
- [ ] Sizing gate checked; all tasks created with simple/medium classification and linked to epic
- [ ] Batch SRE review run against full task tree; refinements applied
- [ ] Announced handoff to executing-plans

**Can't check all boxes?** Return to the process and complete the missing steps.
</verification_checklist>

<integration>
**Calls:** codebase-investigator, internet-researcher (Step 2); sre-task-refinement (Step 7); executing-plans (Step 8).

**Bidirectional with /intuition:**
- brainstorm → /intuition: design-time friction (Step 3) or Impact Check 1+ YES (Step 4)
- /intuition → brainstorm: Resolution Protocol "Brainstorm" option hands off with tension as context

**Called by:** new-feature requests; using-hyper (mandatory before code); /intuition Step 4 Resolution Protocol.

**Tools required:** AskUserQuestion (Rule 1).
</integration>

<resources>
**When stuck:**
- User gives vague answer → Ask a follow-up multiple choice question with a recommended default
- Research yields nothing → Ask user for direction explicitly
- Too many approaches → Narrow to top 2-3; explain why others were eliminated
- User changes requirements mid-design → Acknowledge, return to Step 1
- Architecture Impact Check results in debate → Offer /intuition; the architect decides
- "None" feels right for a subsection → Write "None because [specific reason]"; this is load-bearing

**Worked examples:** see `examples.md` for skipped-research, upfront-task-tree, and missing-anti-patterns scenarios.
</resources>
