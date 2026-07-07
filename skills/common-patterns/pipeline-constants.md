# Pipeline Constants

Single source of truth for workflow sizing, classification, and executor
routing. Skills reference these values instead of embedding them. If a value
must change, change it here and only here.

## Sizing Gate (brainstorm -> preordain escalation)

Escalate when ANY of:
- Estimated tasks exceed 10
- Work spans 3 or more distinct components
- Multiple independent deliverables that could ship separately

Evaluated at brainstorm Step 1 exit — as soon as a scope estimate exists,
before any epic is created. Re-checked before task creation only if scope
grew during design. The gate is an offer, not a hard block: the architect
can override, and the override is recorded in the epic.

## Leaf Epic Target

Preordain decomposes initiatives into leaf epics of 5-10 tasks so each stays
under the sizing gate. A mostly-simple task list may modestly exceed the
target at the architect's discretion — record the reasoning in the epic.

## Task Classification (spec depth)

- Simple (2-5 min): mechanical changes with exact known edits, no judgment.
  Concise spec: Goal, Why, Changes, Verification.
- Medium (5-30 min): changes requiring judgment or design decisions.
  Full spec: Goal, Why, Context, Implementation, Tests (when code),
  Verification, Boundaries.

Hard ceiling: 30 minutes per task. Tasks estimated over 30 minutes must be
split before execution.

## Spec Depth Rule

Medium specs carry intent: goal, constraints, test cases, verification
commands, boundaries. Exact code appears only where the planner verified the
exact site during planning. Drift protection comes from tests, boundaries,
and immutable epic requirements — not from pre-written code.

## Executor Promotion Flag

Default executor model is Sonnet. A task spec containing the line
"Executor: opus" is dispatched on Opus instead. The flag is set by:
1. The planner at spec time, for irreducibly hard tasks
2. SRE batch review, as a recommendation
3. The lead automatically on re-dispatch after a BLOCKED or CONCERNS
   failure — one escalation rung before interrupting the user

## Complete Task Tree (Handoff Contract)

What brainstorming hands to executing-plans. "Complete" means all four:
1. Every task for the epic exists in bd (no tasks created during execution;
   sole exception: reviewer gap-fix tasks).
2. Every task has a self-contained two-tier spec
   (`skills/common-patterns/spec-templates.md`).
3. Dependencies are recorded so execution order is derivable from bd alone.
4. The tree passed batch SRE review.
Producers and consumers cite this definition; neither restates it.
