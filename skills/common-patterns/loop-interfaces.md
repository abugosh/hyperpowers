# Loop Interfaces

Single source of truth for the artifacts that cross the boundary between a
working session and its governor (the human rotating across parallel lanes),
and between per-repo sessions and a shared planning layer. Skills reference
these formats instead of restating them. Reports read by the governor
follow the Audience Contract in `skills/common-patterns/prose-style.md`.

## Gate-State Block

Emitted whenever a session pauses at a user gate (approval, escalation,
completion, handoff) — AND persisted to the epic's bd notes (`bd update
<epic-id> --notes`), so a fresh session reconstructs the gate from bd alone.
A stalled lane is acceptable only when the stall is visible on return.

Format (three sections, always in this order):

```
GATE STATE (<date>, <context>):
Where we are: <one or two sentences — phase, what is complete, what is in flight>
Decided: <decisions taken since the last gate, including async-veto items>
Needs you: <the specific decision(s) or confirmation(s) the gate is waiting on;
  or "nothing — informational" for completion states>
```

Completion gate-states — emitted when the end-of-epic reviewer returns
APPROVED — MUST additionally include the fixed marker line
`Verdict: APPROVED (end-of-epic reviewer, <date>)`. It is
machine-checkable: finishing-a-development-branch greps the epic's bd
notes for it before integrating.

Gate questions must be answerable in durable prose — never only via an
expiring interactive element. The governor may return hours later.

The Decided section exists so that decisions made in conversation always
land in bd — a fresh session must never depend on chat history for a
decision's existence.

## Plan-Impact Notice

Emitted when per-repo work invalidates or constrains an assumption in a
shared planning layer (a phase document in a planning repo). Sessions NEVER
write the shared docs — the notice is carried upward and applied by the user.

Persist to bd (epic notes, prefixed `PLAN-IMPACT:`) and include in the
gate-state block's Decided or Needs-you section.

Format:

```
PLAN-IMPACT: <one-line title>
Assumption affected: <what the plan doc asserts, with file/section if known>
What was learned: <the evidence from this repo's work>
Siblings likely affected: <which other services/epics care, or "none known">
Proposed edit: <concrete wording or diff for the planning-repo doc — the
  user applies it at the base view>
```

## Signal Policy (pushed vs pulled)

**Pushed to the user** (surface immediately in the gate-state block and,
where it exists, the lane's final message): plan-impact notices, provenance
drift flags (a cited plan doc changed since the epic recorded its SHA),
escalations, lane-completion gate-states, and disagreement counter-signals
(a session's evidence-backed objection to a decision it is executing —
stated once at the gate; if the governor holds, their call stands and the
objection remains on record in the Decided section). These are drift-tier
or blocking — the costs the governor ranks highest.

**Pulled on demand** (recorded in bd, never volunteered): executor churn
statistics, token burn, and progress rollups. These are noise-tier — bd
holds them for whoever asks.

## Verdict Contracts

Single source for the six verdict vocabularies in the pipeline.
Definition sites cite this section; parse sites must match it exactly.

- **Executor → lead** (defined in `agents/executor.md`, parsed by
  executing-plans): final message is exactly one of `DONE: <commit-hash> —
  <summary>`, `BLOCKED: <what failed, attempted, error>`, `NEEDS_HELP:
  <question, attempted, needed>`. One line, no envelope. The lead parses
  the first word, then reads the DONE commit hash from its fixed position
  immediately after `DONE: `. BLOCKED and NEEDS_HELP name any landed
  commit hashes in prose when partial commits exist.
- **Stage-2 code-reviewer → lead** (stated in `agents/code-reviewer.md`,
  dispatched by executing-plans): leading verdict line `PASS` or
  `CONCERNS: <one-line summary>`, followed by the concern list only — one
  line per concern: `[capability|convention] <file>:<line> — <what and
  why>` — exactly one class tag per line, definitions in
  `pipeline-constants.md` (Finding Classification). May be followed by
  non-blocking `SUGGESTION: <file>:<line> — <note>` lines, which the lead
  persists to the epic's bd notes and never acts on in-round. Never the
  full structured review: the lead's context must not accumulate per-task
  review bodies.
- **End-of-epic reviewer → lead (completion)** (defined in `agents/reviewer.md`):
  structured verdict `APPROVED` or `GAPS FOUND` with the gap list. Gap
  entries carry the same `[capability]`/`[convention]` tags as Stage 2. A
  non-blocking Suggestions section may follow the gap list and never
  blocks approval.
- **SRE batch reviewer → lead** (defined in `skills/sre-task-refinement/SKILL.md`,
  batch mode Report File Contract; dispatched by brainstorming Step 7 and
  analyzing-test-effectiveness Step 5): final message is exactly one line —
  `SRE VERDICT: <APPROVE|NEEDS REVISION|REJECT> — report: <path> — <N> specs updated`.
  The full report lives in the file at the path; the lead parses the verdict
  word immediately after `SRE VERDICT: ` and reads the report file on demand.
- **Peek synthesis → user** (derived in `skills/peek/SKILL.md` Step 6 from
  severities anchored in `pipeline-constants.md`, Severity Anchor): the
  review report and the draft comment open with exactly one of
  `Verdict: APPROVE`, `Verdict: APPROVE WITH CHANGES`,
  `Verdict: REQUEST CHANGES`. Derived mechanically after the synthesis
  re-check, over the findings not fixed by review (pipeline-constants.md,
  Peek Fix Carve-out; on runs without the fix path that is
  every surviving finding) — any Critical → REQUEST CHANGES; else any
  Important → APPROVE WITH CHANGES; else APPROVE.
  The lead never hand-picks it.
- **Peek report Path → user** (derived in `skills/peek/SKILL.md` Step 6,
  stated once under the report's Overall Assessment): exactly one of
  `Path: fix in place`, `Path: rework`. `fix in place` — each surviving
  finding is addressed where it stands and the branch's shape holds.
  `rework` — the surviving findings share one cause that has to be
  addressed at its source; fixing them one by one leaves the cause
  standing. Derivation: `rework` only when the lead names one cause shared
  by two or more surviving findings in the Overall Assessment sentences;
  otherwise `fix in place`. Path never changes the verdict, and the label
  never appears in colleague-facing text — the cause sentence may, in plain
  language. The accompanying `Decision:` line names what only the reader
  can decide (a declared reshape to accept or send back, an aim to drop
  from the description) or reads `(none)`.
- **Opt disposition → user** (defined in `skills/opt/SKILL.md`, disposition
  gate; proposed by the lead, decided by the user): every incoming review
  finding carries exactly one of `FIX NOW`, `FILE FOLLOW-UP`, `DECLINE`,
  `NEEDS REVIEWER INPUT` in the disposition table. `DECLINE` lines always
  carry written reasoning. Dispositions are proposals until the user
  approves the table, and never appear in colleague-facing text.

The vocabularies are deliberately stage-distinct — do not merge them; do
not invent new verdict words at any site.
