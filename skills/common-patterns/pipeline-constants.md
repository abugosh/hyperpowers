# Pipeline Constants

Single source of truth for workflow sizing, classification, and executor
routing. Skills reference these values instead of embedding them. If a value
must change, change it here and only here.

## Sizing Gate (brainstorm -> preordain escalation)

Escalate when ANY of:
- Estimated tasks exceed 10
- Work spans 3 or more distinct components
- Multiple independent deliverables that could ship separately

Evaluated in brainstorming as soon as a scope estimate exists,
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

## Finding Classification (resolution + promotion)

Every review finding — Stage 2, end-of-epic, peek, or otherwise — carries exactly
one class tag. This section supersedes older two-way severity wording that
predated the convention/capability split; other sections cite it rather
than restate it.

- `[capability]` — behavior correctness or quality: spec mismatch, wrong
  logic, missing error handling, broken contract, meaningful test gap.
  Resolution: the executor re-dispatch loop (executing-plans owns the
  handling); the Opus promotion ladder below applies.
- `[convention]` — style/prose/doc surface: noise comments, docstring
  drift, naming nits, formatting, stale cross-references. Resolution: the
  lead fixes directly under executing-plans' bounded carve-out — no
  dispatch, no re-review round, never promotes.

Reviewers propose the tag on each finding; the lead owns final
classification and may retag with a one-line bd note.

**Round cap: 2** — two capability fix→re-review rounds per task (Stage 2),
and two full end-of-epic gap rounds, then escalate to the user. Single
source for this constant.

## Severity Anchor (peek)

Single definition of the three severity tiers used by peek's lenses
(`agents/peek.md`) and synthesis (`skills/peek/SKILL.md`). Severity is
defined by the follow-up it requires, not by how the defect feels:

- **Critical** — a confirmed, reachable path to outage, data loss, security
  breach, or wrong result. The finding MUST name the Trigger (the input or
  sequence that reaches the path) and the Consequence (what happens when it
  does). Requires fix AND re-peek. A finding that cannot name both is
  Important, never Critical.
- **Important** — a confirmed defect below that bar that the author must
  fix before merge. No re-peek: the author self-certifies the fix.
- **Suggestion** — never blocks, never becomes a fix requirement, and never
  becomes Critical through dedup or synthesis.

`[convention]` findings (Finding Classification above) are never Critical.
Consumers cite this section; none restates it.

## Executor Promotion Flag

Default executor model is Sonnet. A task spec containing the line
"Executor: opus" is dispatched on Opus instead. The flag is set by:
1. The planner at spec time, for irreducibly hard tasks
2. SRE batch review, as a recommendation
3. The lead automatically on re-dispatch, one escalation rung before
   interrupting the user — always after a first BLOCKED; after Stage 2
   CONCERNS only when the lead classifies the concern as `[capability]`
   (see Finding Classification above). `[convention]` concerns never
   promote. executing-plans owns this classification; this entry defers
   to it.

## Complete Task Tree (Handoff Contract)

What brainstorming hands to executing-plans. "Complete" means all four:
1. Every task for the epic exists in bd (no tasks created during execution;
   sole exception: reviewer gap-fix tasks).
2. Every task has a self-contained two-tier spec
   (`skills/common-patterns/spec-templates.md`).
3. Dependencies are recorded so execution order is derivable from bd alone.
4. The tree passed batch SRE review.
Producers and consumers cite this definition; neither restates it.
