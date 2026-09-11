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
- `[convention]` — style/prose/doc surface: noise comments (a `Contract:
  comment policy` miss under the standing scope — `spec-templates.md`),
  docstring drift, naming nits, formatting, stale cross-references. Resolution: the consuming
  pipeline's bounded carve-out — executing-plans' lead-fix valve in-epic, or
  peek's fix path at review (Peek Fix Carve-out below) — no dispatch, no
  re-review round, never promotes.

Reviewers propose the tag on each finding; the lead owns final
classification and may retag with a one-line bd note.

**Round cap: 2** — two capability fix→re-review rounds per task (Stage 2),
and two full end-of-epic gap rounds, then escalate to the user. Single
source for this constant.

## Severity Anchor

Single definition of the three severity tiers used by peek's lenses
(`agents/peek.md`) and synthesis (`skills/peek/SKILL.md`), by opt's
finding normalization and triage (`skills/opt/SKILL.md`), and — Important
bar only — by the in-epic judges (`agents/reviewer.md`,
`agents/code-reviewer.md`; in-epic paragraph below). Severity is defined
by the follow-up it requires, not by how the defect feels:

- **Critical** — requires fix AND re-peek. A finding is Critical only when
  it belongs to one of three classes and names both its Trigger and its
  Consequence in that class's terms; a finding that cannot name both is not
  Critical: it is Important when it fills one of the Important lines below
  on its own, otherwise Suggestion.
  - *Production* — a confirmed, reachable path to outage, data loss,
    security breach, or wrong result. Trigger: the input or sequence that
    reaches the path, and it must exist in the reviewed repo or in an
    interface contract the repo publishes to callers outside it — a caller
    that would have to exist elsewhere is not a Trigger, and a comment or
    docstring describing how callers are expected to behave is not such a
    contract; that concern is a Question for the Author
    (agents/peek.md Shared Rule 3). Consequence: what happens when it does, stated
    concretely.
  - *Delivery* — a confirmed stated aim the branch does not deliver (the
    aims table row reads `missing`). Trigger: the aim, quoted, with its
    source. Consequence: the capability the merge record claims and the
    merge would not ship, and who relies on that claim.
  - *Structural* — a change of ownership, dependency direction, or boundary
    that no confirmed aim covers (an undeclared reshape). Trigger: the
    move — what responsibility or arrow, from where to where, at file:line.
    Consequence: the decision the merge would make without a record, and
    what inherits it afterwards.

  A `partial` aim is Important, not a delivery Critical. A reshape that a
  confirmed aim covers is a decision for the reader, never a finding from
  the stance alone. Every Critical finding names its class on a
  `Critical class:` line so synthesis and triage can read it.
- **Important** — requires fix before merge, no re-peek: the author
  self-certifies the fix — unless the finding was resolved at review under
  the Peek Fix Carve-out below, which removes it from the author's queue. A
  finding is Important only when it is a confirmed defect below the Critical
  bar AND fills exactly one of two lines, in the delta's terms:
  - `Hits:` — who reaches the defect and what they observe. The one who hits
    it is a caller, user, or job that exists in the reviewed repo or in an
    interface contract the repo publishes to callers outside it — the same
    reachability the production class requires of a Trigger; a caller that
    would have to exist elsewhere is a Question for the Author, not a hit.
  - `Maintainer cost:` — the next change that pays for the defect: a named
    future edit at file:line, and the step it must add or the fact it must
    hold that the code at that site does not itself state.
    Reading effort is not a cost: "confusing", "unclear", "harder to read",
    "surprising", and their synonyms never fill this line, and neither does
    a fact the site already states in code, a docstring, or a comment.
    A comment-policy violation (`prose-style.md`, Comment Policy) never
    travels through this line: in-epic it is a `Contract:` miss under the
    standing scope; on peek it is a `[convention]` finding, fix-eligible
    under the carve-out at whatever tier its line supports.

  A finding that fills neither line is Suggestion, whatever it feels like.
  Severity is a property of the code and the delta, never of what the
  author says about readiness. Critical findings carry the same line
  (exactly one of the two) beside their Trigger and Consequence, so a
  Critical that fails its class check lands at the tier its line supports.
  A Critical the synthesizing lead files from the aims table or the Stance
  carries Trigger and Consequence only; the line is a lens's to write.
- **Suggestion** — never blocks, never becomes a fix requirement, and never
  becomes Critical through dedup or synthesis. Clarity, naming, and
  structure opinions on a branch that ships live here unless they fill an
  Important line.

In-epic (the end-of-epic reviewer and the Stage-2 code-reviewer), a gap
or concern is either a contract miss — its line opens `Contract:` and
names the item missed — or a finding that fills one of the two Important
lines above; everything else is a Suggestion. The contract
at Stage 2 is the task spec and the standing scope every spec carries
(`spec-templates.md`, Standing scope); at the end-of-epic gate it adds
the epic's requirements, success criteria, and anti-patterns. In-epic
there is no Critical tier — a defect that would be Critical elsewhere is
a gap by the line it fills — and no follow-up split: the lead routes
every gap or concern by its class tag (Finding Classification).

On the receiving side (opt), severity weights triage; the fix-and-re-peek
follow-up requirements and the `Hits:` / `Maintainer cost:` line requirement
above bind the giving side only. The follow-up
split — Critical: fix and re-peek; Important: fix and self-certify;
Suggestion: optional — is what peek's draft comment tells the author
(`skills/peek/SKILL.md`, Step 7).

`[convention]` findings (Finding Classification above) are never Critical.
Consumers cite this section; none restates it.

## Peek Fix Carve-out

Bounded authority for peek's lead (skills/peek/SKILL.md, synthesis and gate
steps) to resolve findings at the review worktree instead of routing them
to the author. Lenses never fix — agents/peek.md's read-only rules are not
relaxed by this section. opt's Step 6 Tier 1 (`skills/opt/SKILL.md`) cites
the same eligibility and suite rules for architect-approved fixes on the
author's own branch — there routing-to-author does not arise, and delivery
waits on opt's outward gate instead of peek's.

- Eligibility: every `[convention]` finding; a `[capability]` finding only
  when its severity is Important or Suggestion AND the fix is an exact
  known edit requiring no judgment (the Simple-task bar above). Critical
  findings are never fix-eligible.
- Suite rule: applying any `[capability]` fix requires green-suite evidence
  from a test-runner dispatch at the worktree before anything is delivered.
  A red or unrunnable suite demotes the capability fixes back to ordinary
  findings; `[convention]` fixes are unaffected.
- Delivery: additive commits only, one per finding, pushed or ref-updated
  only after the user approves the exact diff, comment text, and target at
  peek's gate. Never a force-push; never an amend, squash, or rebase of
  author commits.
- Verdict: derived over the findings NOT fixed by review
  (loop-interfaces.md, Verdict Contracts, peek entry); fixed findings move
  to the report's Fixed-by-review block.

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
