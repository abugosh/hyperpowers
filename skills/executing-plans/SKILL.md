---
name: executing-plans
description: Lead reads pre-planned task list, dispatches fresh blocking executor subagent (Sonnet by default, promotable) per task, runs two-stage per-task review, and escalates to user when plan proves invalid.
---

<skill_overview>
Lead orchestrates execution of a pre-planned task list. All tasks exist in bd before execution begins. Lead dispatches a fresh executor subagent per task, runs two-stage review (lead epic-coherence check + reviewer spec-match/code quality check), and escalates to user when the plan proves invalid. Epic requirements are immutable.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — Pre-dispatch verification uses judgment. Dispatch, review, and escalation protocol are rigid (follow exactly). Do not skip stage 1 or stage 2 review. Do not implement code in the lead context. Do not redesign the plan autonomously.
</rigidity_level>

<quick_reference>

| Step | Action | How |
|------|--------|-----|
| **Startup** | Load epic, list all tasks, verify specs | `bd show <epic-id>` + `bd list --parent <epic-id>` |
| **Pre-dispatch** | Verify spec exists and dependencies met | `bd show <task-id>` |
| **Dispatch** | Record base SHA, then fresh blocking executor subagent per task | `git rev-parse HEAD` + Agent tool (no team_name, Sonnet unless promoted) |
| **Stage 1** | Lead reads diff vs recorded base SHA for epic coherence | `git diff <base-SHA>` |
| **Stage 2** | Spec-match + code quality review | Agent tool (Sonnet unless promoted) |
| **Escalation** | Halt, summarize, recommend, wait | AskUserQuestion |

**Critical:** Executor returns a one-liner (DONE:, BLOCKED:, or NEEDS_HELP:) — not a multi-section envelope. Parse the first word only. All three loop verdict vocabularies are single-sourced in `skills/common-patterns/loop-interfaces.md` (Verdict Contracts).

</quick_reference>

<when_to_use>
**Use after brainstorming produces a complete task tree for an epic** (contract defined in `skills/common-patterns/pipeline-constants.md`, Complete Task Tree).

All tasks must exist in bd with specs before invoking this skill. If tasks are missing specs, route the spec-less tasks through writing-plans (the off-mainline spec repair utility) first.

If invoked mid-epic: `bd list --parent <epic-id>` to find remaining open tasks. Resume from the next unfinished task in dependency order.
</when_to_use>

<the_process>

## 1. Startup

```bash
bd show <epic-id>              # Load epic details
bd list --parent <epic-id>     # List all child tasks
```

**Extract and hold for the entire session:**
- **Requirements** — IMMUTABLE. Never water down.
- **Success Criteria** — Your completion checklist.
- **Anti-Patterns** — FORBIDDEN. Reject any executor action that violates these.

**Read the epic's bd notes for the latest GATE STATE block** — if one exists, resume from the state it records rather than re-deriving it (format: `skills/common-patterns/loop-interfaces.md`).

**Verify:** Every task has a non-empty spec (design field). If any task is missing a spec, do not start execution — route the spec-less tasks through writing-plans (the off-mainline spec repair utility).

**Determine execution order** from bd dependencies. Tasks blocked by uncompleted dependencies must wait.

## 2. Pre-dispatch Verification

Before dispatching each task, verify:
1. Task has a non-empty spec (design field).
2. Blocking dependencies are met (all tasks that must complete before this one are done).

If either check fails, skip the task and note why.

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

    <paste full task spec from bd show output here>

    Working directory: <pwd>
    Branch: <current branch>
```

The prompt contains ONLY the task spec. No epic context, no adjacent task details. The task spec's Why section provides the necessary context.

The Agent tool blocks until the executor returns. Parse the first word of the return value.

## 4. Handle Executor Return

### DONE

Executor committed the work. Run two-stage review:

**Stage 1 — Lead epic-coherence check:**
```bash
git diff <base-SHA>    # Diff against the commit recorded before dispatch (Step 3), not just the
                       # immediately preceding commit — an executor may have made several
```
Read the diff for what only the lead can see and the reviewer cannot — the reviewer is never given the epic. Check for:
- Violations of the epic's anti-patterns (FORBIDDEN list)
- Watering-down of any immutable requirement
- Contradictions with other tasks — already-completed work, or assumptions that remaining tasks depend on

Do not re-check whether the implementation matches the task spec line-by-line — that is Stage 2's job. If any check above fails: note the violation(s), re-dispatch with feedback (see Stage 1 feedback template below).

**Stage 2 — Reviewer spec-match and code quality check:**

The fresh reviewer owns both spec-match and code quality — the lens Stage 1 does not cover:

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

If reviewer returns PASS: mark task done in bd, proceed to next task.

If reviewer returns CONCERNS: classify before re-dispatching.
- **Capability-class** (correctness or quality issue — spec mismatch, wrong logic, missing error handling): if this is the task's first re-dispatch and it is not already promoted, add `Executor: opus` to the task spec and note the promotion in bd (e.g. `bd update <task-id> --notes "Auto-promoted to opus after Stage 2 CONCERNS"`). Re-dispatch with the concern list.
- **Cosmetic/convention-class** (formatting, citation style, naming): re-dispatch with the concern list at the lead's discretion. Do NOT promote — promotion is reserved for capability-class failures, and spending it on a convention fix wastes the escalation rung.

**Stage 1 feedback template** (when the lead's epic-coherence check fails):
```
Re-execute this task. The prior attempt conflicts with the epic.

Violations found:
- <violation 1>
- <violation 2>

Task spec:
<paste task spec>

Working directory: <pwd>
Branch: <current branch>
```

### BLOCKED

Executor hit an obstacle it could not resolve. Assess the scope:

**Task-level block** (wrong file path, ambiguous spec, missing fixture): Clarify and re-dispatch.

**Upstream-plan mismatch:** If the block reveals that an assumption from a shared planning layer is wrong (a contract, schema, or interface the plan doc asserts), emit a plan-impact notice (format: `skills/common-patterns/loop-interfaces.md`) into the epic's bd notes in addition to handling the block — the user carries it to the planning repo; sessions never write the shared docs.

**Auto-promotion rung:** If this is the task's first BLOCKED return and it is not already promoted, add `Executor: opus` to the task spec before re-dispatching and note the promotion in bd (e.g. `bd update <task-id> --notes "Auto-promoted to opus after BLOCKED"`). This is one rung below interrupting the user. A BLOCKED return is always a capability-class signal — the executor could not do the work — so it always qualifies for auto-promotion, unlike Stage 2 CONCERNS, which must be classified first (see Stage 2 above). A task that is already promoted does not promote again; its next BLOCKED goes straight to the consecutive-BLOCKED threshold below (count this BLOCKED toward that task's total like any other — promotion path does not reset or bypass the count).

```
Re-execute this task. The prior executor was blocked: <description>.
Resolution: <clarification or instruction>.

Task spec:
<paste task spec — include the `Executor: opus` line if auto-promoting>

Working directory: <pwd>
Branch: <current branch>
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

Task spec:
<paste task spec>

Working directory: <pwd>
Branch: <current branch>
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

2. Dispatch reviewer as a blocking subagent:
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

   **APPROVED:** Emit the completion gate-state block and persist it to the epic's bd notes (format: `skills/common-patterns/loop-interfaces.md`), including any accumulated plan-impact notices. Present final status to user. Hand off to `/hyperpowers:finish-branch`.

   **GAPS FOUND:** Create fix task(s) inline for each gap — spec body per the tier templates in `skills/common-patterns/spec-templates.md` — and dispatch executors. This is the one exception to "all tasks planned upfront." These gap-fix tasks follow the same dispatch and two-stage review loop. After all gaps resolved, re-dispatch reviewer.

</the_process>

<examples>

<example>
<scenario>Normal task dispatch and DONE return with passing review</scenario>
<code>
Lead records base SHA (git rev-parse HEAD → a1b2c3d), then verifies bd-42: non-empty spec, no
blocking dependencies pending. Dispatches executor on Sonnet (spec carries no promotion flag).
Executor returns:
"DONE: Added error handling to auth.ts:validate() and committed as 3f9a1b2."

Stage 1: git diff a1b2c3d → no anti-pattern violations, requirements intact, no conflict with other
completed tasks. ✓
Stage 2: code-reviewer returns "PASS" (spec-match and quality both check out). ✓

Lead marks bd-42 done. Proceeds to bd-43.
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

1. **All tasks pre-planned** — Do not create tasks during execution (exception: gap-fix tasks after reviewer GAPS FOUND verdict).

2. **No SRE per-task** — SRE batch review runs before execution begins. Never invoke SRE between tasks.

3. **Parse the one-liner** — Executor returns DONE:, BLOCKED:, or NEEDS_HELP: as a one-liner. There are no multi-section status envelopes to parse.

4. **Two-stage review on every DONE** — Stage 1 (lead epic-coherence check against the recorded base SHA) and Stage 2 (reviewer spec-match and code quality check) are both mandatory. Do not skip either stage.

5. **Never redesign autonomously** — On plan-level failures, halt and escalate. Present options; the user decides. Never continue without user input after escalation.

6. **Executor dispatch is blocking** — No team_name parameter. The Agent tool call blocks until the executor returns.

7. **Task spec only in dispatch prompt** — No epic context, no adjacent task details, no cross-task learnings in the executor prompt. The task spec's Why section is the executor's only context.

8. **Epic requirements are immutable** — Never water down a requirement. If an executor's changes violate an anti-pattern, reject in Stage 1 and re-dispatch.

## Common Rationalizations

- "I'll skip Stage 2 since Stage 1 looked fine" → Both stages are mandatory. Dispatch the code-reviewer.
- "I'll just clarify this one thing in the spec and continue" → If it's a plan-level issue, escalate. Don't patch forward.
- "The reviewer is overkill for gap-fix tasks" → Dispatch reviewer after all gaps are fixed. No exceptions.
- "I can answer this NEEDS_HELP myself and keep going" → Answer it in the re-dispatch prompt. Do not implement it in the lead context.
- "I'll promote to opus since the reviewer raised a concern" → Not for cosmetic or convention-level concerns (formatting, citation style, naming). Promotion is reserved for capability-class failures — don't spend the rung on a convention fix.

</critical_rules>

<verification_checklist>

Before dispatching each task:
- [ ] Task has a non-empty spec
- [ ] Dependencies are met (blocking tasks completed first)
- [ ] Base SHA recorded (`git rev-parse HEAD`) before dispatch

After each DONE return:
- [ ] Stage 1: lead read the diff against the recorded base SHA for epic coherence
- [ ] Stage 2: reviewer dispatched and returned PASS (spec-match and code quality)
- [ ] Any CONCERNS/BLOCKED classified before re-dispatch; promotion applied only to capability-class failures
- [ ] Task marked done in bd

Before completion:
- [ ] `bd list --parent <epic-id> --status open` returns 0
- [ ] Reviewer dispatched as blocking subagent
- [ ] Verdict handled (APPROVED → finish-branch; GAPS FOUND → fix tasks)

</verification_checklist>

<integration>

**Calls:** agents/executor.md (blocking subagent, Sonnet unless promoted, per task) · agents/code-reviewer.md (Sonnet unless promoted, per task) · agents/reviewer.md (blocking subagent, once at end)

**Called by:** User via /hyperpowers:execute-plan · after brainstorming produces the task tree

**Flow:** Startup → Pre-dispatch verification → Record base SHA → Dispatch executor (blocks) → Parse one-liner → Two-stage review → Next task → ... → Reviewer gate → Present → /hyperpowers:finish-branch

**bd command reference:** See [bd commands](../common-patterns/bd-commands.md)

**When stuck:**
- Executor timed out → Re-dispatch same task with prompt: 'Prior executor timed out. Check git log for progress. Continue from where it left off.'
- Reviewer GAPS FOUND → Create gap-fix tasks, dispatch executors, re-dispatch reviewer
- Escalation → Summarize, recommend, wait for user

</integration>
