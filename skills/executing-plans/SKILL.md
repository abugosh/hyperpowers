---
name: executing-plans
description: Lead reads pre-planned task list, dispatches fresh blocking executor subagent (Sonnet by default, promotable) per task, runs two-stage per-task review, and escalates to user when plan proves invalid.
---

<skill_overview>
Lead orchestrates execution of a pre-planned task list. All tasks exist in bd before execution begins. Lead dispatches a fresh executor subagent per task, runs two-stage review (lead epic-coherence check + Stage-2 code-reviewer spec-match/code quality check), and escalates to user when the plan proves invalid. Epic requirements are immutable.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — Pre-dispatch verification uses judgment. Dispatch, review, and escalation protocol are rigid (follow exactly). Do not skip stage 1 or stage 2 review. Do not implement code in the lead context. Do not redesign the plan autonomously.
</rigidity_level>

<quick_reference>

| Step | Action | How |
|------|--------|-----|
| **Startup** | Load epic, list all tasks, verify specs | `bd show <epic-id>` + `bd list --parent <epic-id>` |
| **Branch** | Establish working branch; never dispatch on the default | `git branch --show-current` (+ `git checkout -b epic/<epic-id>` when on main) |
| **Pre-dispatch** | Verify spec exists and dependencies met | `bd show <task-id>` |
| **Dispatch** | Record base SHA, then fresh blocking executor subagent per task | `git rev-parse HEAD` + Agent tool (no team_name, Sonnet unless promoted) |
| **Stage 1** | Lead reads diff vs recorded base SHA for epic coherence | `git merge-base --is-ancestor <hash> HEAD` + `git diff <base-SHA>..HEAD` |
| **Stage 2** | Stage-2 code-reviewer: spec-match + code quality review | Agent tool (Sonnet unless promoted) |
| **Escalation** | Halt, summarize, recommend, wait | AskUserQuestion |

**Critical:** Executor returns a one-liner (DONE:, BLOCKED:, or NEEDS_HELP:) — not a multi-section envelope. Parse the first word only. All three loop verdict vocabularies are single-sourced in `skills/common-patterns/loop-interfaces.md` (Verdict Contracts).

</quick_reference>

<when_to_use>
**Use after brainstorming produces a complete task tree for an epic** (contract defined in `skills/common-patterns/pipeline-constants.md`, Complete Task Tree).

All tasks must exist in bd with specs before invoking this skill. If tasks are missing specs, route the spec-less tasks through writing-plans (the off-mainline spec repair utility) first. Writing-plans carries a mandatory per-expansion user-approval gate — routing happens at startup only, never mid-flight.

If invoked mid-epic: `bd list --parent <epic-id>` to find remaining open tasks. Resume from the next unfinished task in dependency order.
</when_to_use>

<the_process>

**Announce:** "I'm using the executing-plans skill."

## 1. Startup

```bash
bd show <epic-id>              # Load epic details
bd list --parent <epic-id>     # List all child tasks
```

### Branch Establishment

```bash
git branch --show-current
```

- On the default branch (main/master) → create the epic branch: `git checkout -b epic/<epic-id>`. If `epic/<epic-id>` already exists (e.g. resuming after a subagent left the repo on main — the exact bd-go7m incident), check it out instead: `git checkout epic/<epic-id>`.
- On any other branch → accept it as-is (resumes and user-created branches are both valid).
- Empty output (detached HEAD) → not on any branch; create the epic branch from here (`git checkout -b epic/<epic-id>`), which preserves the current state.

Record the result as the **working branch** for the session. Executors are NEVER dispatched on the default branch.

Subagents can and do switch branches. Re-verify `git branch --show-current` equals the working branch (a) before every executor dispatch and (b) before every lead-side git commit or bd mutation that triggers a sync commit (bd close, bd update, gate-state persist). On mismatch: `git checkout <working-branch>` before proceeding.

**Extract and hold for the entire session:**
- **Requirements** — IMMUTABLE. Never water down.
- **Success Criteria** — Your completion checklist.
- **Anti-Patterns** — FORBIDDEN. Reject any executor action that violates these.

**Read the epic's bd notes for the latest GATE STATE block** — if one exists, resume from the state it records rather than re-deriving it (format: `skills/common-patterns/loop-interfaces.md`).

**Verify:** Every task has a non-empty spec (design field). A spec containing a bracketed elision or placeholder marker — e.g. "[Remaining steps truncated]", "[see parent]", "[TBD]", "[detailed above]" — is a missing spec, not a valid one. If any task is missing a spec (empty or truncated/placeholder), do not start execution — route the spec-less tasks through writing-plans (the off-mainline spec repair utility). Its per-expansion approval gate runs before execution starts — never route to it mid-flight.

**Determine execution order** from bd dependencies. Tasks blocked by uncompleted dependencies must wait.

## 2. Pre-dispatch Verification

Before dispatching each task, verify:
1. Task has a non-empty spec (design field), free of truncation/placeholder markers.
2. Blocking dependencies are met (all tasks that must complete before this one are done).
3. Current branch equals the working branch (`git branch --show-current`) — restore it if a subagent switched branches.

If any check fails, skip the task and note why.

## 3. Executor Dispatch

Before dispatching, record the current commit as this task's base SHA. Stage 1 diffs against it later, so a multi-commit executor run is fully visible:

```bash
git rev-parse HEAD    # Save as this task's base SHA
```

**Dispatch model:** Use `"sonnet"` unless the task spec contains the line `Executor: opus` — then use `"opus"`. See skills/common-patterns/pipeline-constants.md for the full promotion-flag definition (planner-set, SRE-recommended, or lead-auto-promoted).

Dispatch a fresh executor subagent for the current task:

```
Agent tool:
  subagent_type: "hyperpowers:executor"
  model: "sonnet"    # "opus" if the task spec contains the line `Executor: opus`
  mode: "bypassPermissions"
  prompt: |
    Execute this task:

    Task: <bd-task-id>

    <paste full task spec from bd show output here>

    Working directory: <pwd>
    Branch: <working branch>
```

The prompt contains ONLY the task ID line and the task spec. No epic context, no adjacent task details. The task spec's Why section provides the necessary context.

The Agent tool blocks until the executor returns. Parse the first word of the return value.

## 4. Handle Executor Return

### DONE

Executor committed the work. Run two-stage review:

**Stage 1 — Lead epic-coherence check:**

First, verify the DONE-declared commit actually landed — the hash at the fixed position immediately after `DONE: ` (contract: `skills/common-patterns/loop-interfaces.md`, Verdict Contracts):

```bash
git merge-base --is-ancestor <done-hash> HEAD   # exit 0 = the DONE hash landed
git status --porcelain                          # must print nothing (clean tree)
```

Any non-zero exit from the ancestry check counts as not-landed — including a malformed or truncated hash (`fatal: Not a valid object name`); treat it as a contract failure, not a tooling problem. Untracked files count as a dirty tree — `git status --porcelain` prints `??` lines for them. If the hash is not in HEAD's history OR the tree is dirty: do NOT review the diff — re-dispatch using the commit-landed failure template (below).

Only after both checks pass, review the range that was actually committed:
```bash
git diff <base-SHA>..HEAD    # Diff against the commit recorded before dispatch (Step 3), not just the
                              # immediately preceding commit — an executor may have made several.
                              # The clean-tree check above has already ruled out uncommitted
                              # leftovers, so this range reads exactly what was committed.
```
Read the diff for what only the lead can see and the Stage-2 code-reviewer cannot — the Stage-2 code-reviewer is never given the epic. Check for:
- Violations of the epic's anti-patterns (FORBIDDEN list)
- Watering-down of any immutable requirement
- Contradictions with other tasks — already-completed work, or assumptions that remaining tasks depend on

Do not re-check whether the implementation matches the task spec line-by-line — that is Stage 2's job. If any check above fails: note the violation(s), re-dispatch with feedback (see Stage 1 feedback template below).

**Stage 2 — Code-reviewer spec-match and code quality check:**

The fresh Stage-2 code-reviewer owns both spec-match and code quality — the lens Stage 1 does not cover:

```
Agent tool:
  subagent_type: "hyperpowers:code-reviewer"
  model: "sonnet"    # "opus" if the task spec contains the line `Executor: opus`
  mode: "bypassPermissions"
  prompt: |
    Review this change for code quality.

    Task spec:
    <paste task spec here>

    Changes (git diff):
    <paste git diff output here>

    Check: Does the implementation match the spec? Any anti-patterns,
    missing error handling, or quality issues?
    Reply PASS or CONCERNS: <list>.
```

If the Stage-2 code-reviewer returns PASS: Task closure is owned by the lead: the lead closes the task only after Stage 2 review passes — the executor never closes tasks. Verify the working branch (Branch Establishment rule), then run `bd close <task-id>`, then proceed to the next task.

If the Stage-2 code-reviewer returns CONCERNS: classify before re-dispatching. A task is NEVER closed with unaddressed CONCERNS — both classes below always re-dispatch with the concern list (Stage-2 CONCERNS re-dispatch template below). The lead's discretion governs only the classification (capability vs cosmetic), which governs promotion (see skills/common-patterns/pipeline-constants.md) — never whether to re-dispatch.
- **Capability-class** (correctness or quality issue — spec mismatch, wrong logic, missing error handling): if this is the task's first re-dispatch and it is not already promoted, add `Executor: opus` to the task spec and note the promotion in bd (e.g. `bd update <task-id> --notes "Auto-promoted to opus after Stage 2 CONCERNS"`). Re-dispatch with the concern list.
- **Cosmetic/convention-class** (formatting, citation style, naming): re-dispatch with the concern list. Do NOT promote — promotion is reserved for capability-class failures, and spending it on a convention fix wastes the escalation rung.

**Stage 1 feedback template** (when the lead's epic-coherence check fails):
```
Re-execute this task. The prior attempt conflicts with the epic.

Violations found:
- <violation 1>
- <violation 2>

Task: <bd-task-id>

Task spec:
<paste task spec>

Working directory: <pwd>
Branch: <working branch>
```

**Commit-landed failure template** (DONE's hash missing from history, or dirty tree):
```
Re-execute this task. The prior run returned DONE but the work did not land:
<the DONE hash <hash> is not in history / the working tree has uncommitted changes>.
Check git log and git status, complete any remaining work, commit everything
for this task, and return DONE: <commit-hash> — <summary> with the real hash.

Task: <bd-task-id>

Task spec:
<paste task spec>

Working directory: <pwd>
Branch: <working branch>
```

**Stage-2 CONCERNS re-dispatch template:**
```
Re-execute this task. The Stage-2 code review returned CONCERNS.

Concerns to address:
- <file:line — concern 1>
- <file:line — concern 2>

Task: <bd-task-id>

Task spec:
<paste task spec — include the `Executor: opus` line if promoting>

Working directory: <pwd>
Branch: <working branch>
```

### BLOCKED

Executor hit an obstacle it could not resolve. Assess the scope:

**Task-level block** (wrong file path, ambiguous spec, missing fixture): Clarify and re-dispatch.

**Upstream-plan mismatch:** If the block reveals that an assumption from a shared planning layer is wrong (a contract, schema, or interface the plan doc asserts), emit a plan-impact notice (format: `skills/common-patterns/loop-interfaces.md`) into the epic's bd notes in addition to handling the block — the user carries it to the planning repo; sessions never write the shared docs.

**Auto-promotion rung:** If this is the task's first BLOCKED return and it is not already promoted, add `Executor: opus` to the task spec before re-dispatching and note the promotion in bd (e.g. `bd update <task-id> --notes "Auto-promoted to opus after BLOCKED"`). This is one rung below interrupting the user. A BLOCKED return is always a capability-class signal — the executor could not do the work — so it always qualifies for auto-promotion, unlike Stage 2 CONCERNS, which must be classified first (see Stage 2 above). A task that is already promoted does not promote again; its next BLOCKED goes straight to the consecutive-BLOCKED threshold below (count this BLOCKED toward that task's total like any other — promotion path does not reset or bypass the count).

```
Re-execute this task. The prior executor was blocked: <description>.
Resolution: <clarification or instruction>.

Task: <bd-task-id>

Task spec:
<paste task spec — include the `Executor: opus` line if auto-promoting>

Working directory: <pwd>
Branch: <working branch>
```

**Plan-level block** (approach fundamentally broken, assumptions in remaining tasks are invalid): Trigger escalation protocol (see section 5).

**Consecutive BLOCKED threshold** (the rung above auto-promotion):
- 2 BLOCKED returns on the same task → trigger escalation (task-level issue that can't be clarified)
- 3 different tasks BLOCKED → trigger escalation (systematic plan problem)

### NEEDS_HELP

Executor has a specific question. If the lead can answer:

Re-dispatch with the answer:
```
Re-execute this task. Answer to your question: <answer>.

Task: <bd-task-id>

Task spec:
<paste task spec>

Working directory: <pwd>
Branch: <working branch>
```

If the lead cannot answer: escalate to user via AskUserQuestion. Wait for answer before re-dispatching.

## 5. Escalation Protocol

Triggered when:
- Multiple tasks BLOCKED by the same root cause
- Executor's changes contradict assumptions in remaining tasks
- A task reveals the approach is fundamentally wrong
- Consecutive BLOCKED threshold reached (see section 4)

**Steps — follow exactly:**

1. **Halt execution immediately.** Do not dispatch the next task.
2. **Summarize to user:**
   - Tasks completed (with commit hashes)
   - Current failure (what failed and why)
   - Remaining tasks affected
   - One recommendation: replan remaining tasks / revert and redesign / continue with adjustments
3. **Persist the gate, then wait.** Emit the gate-state block — including any accumulated plan-impact notices — and write it to the epic's bd notes (format: `skills/common-patterns/loop-interfaces.md`) — the user may return hours later or in a different session, and the question must be answerable in durable prose. Then wait for the user decision. Do NOT continue without user input.
4. **After user responds:** Execute the user's chosen path. If user says "continue as-is," resume from the next unfinished task. If the specific blocked task is still blocked, skip it and note it as deferred.

**Do not redesign the plan autonomously.** Present options; the user decides.

## 6. Completion

After all tasks return DONE and pass two-stage review:

1. Verify all tasks are closed in bd:
   ```bash
   bd list --parent <epic-id> --status open
   ```
   Must return 0 open tasks.

2. Dispatch the end-of-epic reviewer as a blocking subagent. **This dispatch is MANDATORY — you MUST NOT skip it.** "Every task passed per-task review" is not a review of the assembled whole: per-task review sees one diff at a time; the end-of-epic reviewer caught real gaps on 7 of 7 reworked epics. Skipping it because all tasks passed Stage 2 is the exact rationalization this gate exists to stop.
   ```
   Agent tool:
     subagent_type: "hyperpowers:reviewer"
     mode: "bypassPermissions"
     prompt: |
       Review the implementation for epic <epic-id>.
       Follow agents/reviewer.md exactly.
       Start with: bd show <epic-id>
   ```

3. Handle the verdict:

   **APPROVED:**

   a. Verify the working branch, then persist the completion gate-state block to the epic's bd notes (format: `skills/common-patterns/loop-interfaces.md`), including any accumulated plan-impact notices. The block MUST include the machine-checkable marker line `Verdict: APPROVED (end-of-epic reviewer, <date>)` (format: `skills/common-patterns/loop-interfaces.md`).
   b. Run the post-build Architecture Impact Check against the work just completed for this epic, per `skills/common-patterns/architecture-impact-check.md` (Post-Build Routing) — cite that file, do not restate the 5 questions here. Any YES routes per that file: dispatch `/ponder` in UPDATE mode when a model exists, or note-and-suggest in the completion report when no model exists.
   c. Present final status to the user.
   d. **STOP here.** Do not automatically call finishing-a-development-branch. The user needs time to test the implementation manually in their environment, verify edge cases automated tests don't cover, and confirm the feature works as expected in context. Closing the epic removes context the user may need during manual validation — let them explicitly trigger closure when ready.
   e. The epic remains open. The user runs `/hyperpowers:finish-branch` when ready.

   **GAPS FOUND:** Create fix task(s) inline for each gap — spec body per the tier templates in `skills/common-patterns/spec-templates.md` — and link each to the epic: `bd dep add bd-<fix-task> bd-<epic-id> --type parent-child` (the completion re-check and re-review enumerate tasks via `bd list --parent`) — and dispatch executors. This is the one exception to "all tasks planned upfront." These gap-fix tasks follow the same dispatch and two-stage review loop. After all gaps resolved, re-dispatch the end-of-epic reviewer.

   **If the review reveals sibling-relevant divergence** — the implementation departed from an upstream shared plan in a way other services or epics depend on — emit a plan-impact notice (format: `skills/common-patterns/loop-interfaces.md`) into the epic's bd notes; the user carries it to the planning repo; sessions never write the shared docs.

</the_process>

<examples>

<example>
<scenario>Normal task dispatch and DONE return with passing review</scenario>
<code>
Lead records base SHA (git rev-parse HEAD → a1b2c3d), then verifies bd-42: non-empty spec, no
blocking dependencies pending. Dispatches executor on Sonnet (spec carries no promotion flag;
dispatch prompt includes "Task: bd-42").
Executor returns:
"DONE: Added error handling to auth.ts:validate() and committed as 3f9a1b2."

Stage 1: hash 3f9a1b2 in history ✓, tree clean ✓, git diff a1b2c3d..HEAD → no anti-pattern
violations, requirements intact, no conflict with other completed tasks. ✓
Stage 2: code-reviewer returns "PASS" (spec-match and quality both check out). ✓

Lead closes bd-42 (`bd close bd-42`). Proceeds to bd-43.
</code>
</example>

<example>
<scenario>NEEDS_HELP — lead answers and re-dispatches</scenario>
<code>
Executor returns:
"NEEDS_HELP: Task says modify config.ts line 12 but that line is a type import. Should I
modify line 34 (the actual config object) instead?"

Lead answers in re-dispatch prompt:
"Re-execute this task. Answer: yes, modify line 34 (the config object). The spec meant
the config assignment, not the import.

Task spec:
<paste task spec>"
</code>
</example>

<example>
<scenario>Plan-level BLOCKED triggering escalation</scenario>
<code>
Tasks bd-51, bd-52, bd-53 are all BLOCKED because the assumed API endpoint
(/api/v2/tasks) does not exist — the API is still v1 with a different schema.

Lead halts. Summarizes to user:
- Completed: bd-48, bd-49, bd-50 (commits: a1b2c, d3e4f, g5h6i)
- Failure: API is v1, not v2. Tasks bd-51–bd-53 assume v2 schema.
- Recommendation: replan bd-51–bd-53 to use v1 API schema.

Waits for user response before proceeding.
</code>
</example>

</examples>

<critical_rules>

1. **All tasks pre-planned** — Do not create tasks during execution (exception: gap-fix tasks after end-of-epic reviewer GAPS FOUND verdict).

2. **No SRE per-task** — SRE batch review runs before execution begins. Never invoke SRE between tasks.

3. **Parse the one-liner** — Executor returns DONE:, BLOCKED:, or NEEDS_HELP: as a one-liner. There are no multi-section status envelopes to parse.

4. **Two-stage review on every DONE** — Stage 1 (lead epic-coherence check against the recorded base SHA — commit-landed check, then diff `<base-SHA>..HEAD`) and Stage 2 (code-reviewer spec-match and code quality check) are both mandatory. Do not skip either stage.

5. **Never redesign autonomously** — On plan-level failures, halt and escalate. Present options; the user decides. Never continue without user input after escalation.

6. **Executor dispatch is blocking** — No team_name parameter. The Agent tool call blocks until the executor returns.

7. **Task ID + task spec only in dispatch prompt** — No epic context, no adjacent task details, no cross-task learnings in the executor prompt. The task spec's Why section is the executor's only context.

8. **Epic requirements are immutable** — Never water down a requirement. If an executor's changes violate an anti-pattern, reject in Stage 1 and re-dispatch.

## Common Rationalizations

- "I'll skip Stage 2 since Stage 1 looked fine" → Both stages are mandatory. Dispatch the code-reviewer.
- "I'll just clarify this one thing in the spec and continue" → If it's a plan-level issue, escalate. Don't patch forward.
- "The end-of-epic reviewer is overkill for gap-fix tasks" → Dispatch the end-of-epic reviewer after all gaps are fixed. No exceptions.
- "I can answer this NEEDS_HELP myself and keep going" → Answer it in the re-dispatch prompt. Do not implement it in the lead context.
- "Every task passed two-stage review, the end-of-epic reviewer is redundant" → Per-task review sees one diff at a time. 7/7 epics had gaps only the end-of-epic reviewer caught. Dispatch it.
- "I'll promote to opus since the Stage-2 code-reviewer raised a concern" → Not for cosmetic or convention-level concerns (formatting, citation style, naming). Promotion is reserved for capability-class failures — don't spend the rung on a convention fix.

</critical_rules>

<verification_checklist>

Before dispatching each task:
- [ ] Task has a non-empty spec with no truncation/placeholder markers
- [ ] Dependencies are met (blocking tasks completed first)
- [ ] Base SHA recorded (`git rev-parse HEAD`) before dispatch
- [ ] Current branch equals the working branch

After each DONE return:
- [ ] Commit-landed check passed: DONE hash in history, `git status --porcelain` clean
- [ ] Stage 1: lead read the diff (`<base-SHA>..HEAD`) against the recorded base SHA for epic coherence
- [ ] Stage 2: code-reviewer dispatched and returned PASS (spec-match and code quality)
- [ ] Any CONCERNS re-dispatched with the concern list (never closed as-is); promotion applied only to capability-class failures
- [ ] Any BLOCKED classified before re-dispatch; promotion applied only to capability-class failures
- [ ] Task closed in bd by the lead (Stage 2 PASS)
- [ ] Working branch verified before task closure

Before completion:
- [ ] `bd list --parent <epic-id> --status open` returns 0
- [ ] End-of-epic reviewer dispatched as blocking subagent
- [ ] APPROVED → gate-state persisted, post-build Architecture Impact Check run (per `architecture-impact-check.md`), final status presented, then STOP — no automatic call to finish-branch
- [ ] GAPS FOUND → fix tasks created and dispatched, end-of-epic reviewer dispatched again to confirm
- [ ] Working branch verified before gate-state persist and any final commits

</verification_checklist>

<integration>

**Calls:** agents/executor.md (blocking subagent, Sonnet unless promoted, per task) · agents/code-reviewer.md (Sonnet unless promoted, per task) · agents/reviewer.md (blocking subagent, once at end)

**Called by:** User via /hyperpowers:execute-plan · after brainstorming produces the task tree

**Flow:** Startup → Establish branch → Pre-dispatch verification → Record base SHA → Dispatch executor (blocks) → Parse one-liner → Two-stage review → Next task → ... → End-of-epic reviewer gate → Architecture check → Present + STOP (manual validation) → user → /hyperpowers:finish-branch

**bd command reference:** See [bd commands](../common-patterns/bd-commands.md)

**When stuck:**
- Executor timed out → Re-dispatch same task with prompt:
  ```
  Prior executor timed out. Check git log for progress. Continue from where it left off.

  Task: <bd-task-id>

  Task spec:
  <paste task spec>

  Working directory: <pwd>
  Branch: <working branch>
  ```
- End-of-epic reviewer GAPS FOUND → Create gap-fix tasks, dispatch executors, re-dispatch the end-of-epic reviewer
- End-of-epic reviewer APPROVED → Persist gate-state, run the post-build Architecture Impact Check, present, then STOP — never auto-call finish-branch
- Escalation → Summarize, recommend, wait for user

</integration>
