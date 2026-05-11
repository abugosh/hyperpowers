---
name: executing-plans
description: Lead reads pre-planned task list, dispatches fresh blocking executor subagent (Sonnet) per task, runs two-stage per-task review, and escalates to user when plan proves invalid.
---

<skill_overview>
Lead orchestrates execution of a pre-planned task list. All tasks exist in bd before execution begins. Lead dispatches a fresh executor subagent per task, runs two-stage review (spec check + code quality), and escalates to user when the plan proves invalid. Epic requirements are immutable.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — Pre-dispatch verification uses judgment. Dispatch, review, and escalation protocol are rigid (follow exactly). Do not skip stage 1 or stage 2 review. Do not implement code in the lead context. Do not redesign the plan autonomously.
</rigidity_level>

<quick_reference>

| Step | Action | How |
|------|--------|-----|
| **Startup** | Load epic, list all tasks, verify specs | `bd show <epic-id>` + `bd list --parent <epic-id>` |
| **Pre-dispatch** | Verify spec exists and dependencies met | `bd show <task-id>` |
| **Dispatch** | Fresh blocking executor subagent per task | Agent tool (no team_name) |
| **Stage 1** | Lead reads diff vs task spec | `git diff HEAD~1` |
| **Stage 2** | Code quality review | Agent tool (Sonnet) |
| **Escalation** | Halt, summarize, recommend, wait | AskUserQuestion |

**Critical:** Executor returns a one-liner (DONE:, BLOCKED:, or NEEDS_HELP:) — not a multi-section envelope. Parse the first word only.

</quick_reference>

<when_to_use>
**Use after writing-plans produces a complete task tree for an epic.**

All tasks must exist in bd with specs before invoking this skill. If tasks are missing specs, return to writing-plans first.

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

**Verify:** Every task has a non-empty spec (design field). If any task is missing a spec, do not start execution — return to writing-plans.

**Determine execution order** from bd dependencies. Tasks blocked by uncompleted dependencies must wait.

## 2. Pre-dispatch Verification

Before dispatching each task, verify:
1. Task has a non-empty spec (design field).
2. Blocking dependencies are met (all tasks that must complete before this one are done).

If either check fails, skip the task and note why.

## 3. Executor Dispatch

Dispatch a fresh executor subagent for the current task:

```
Agent tool:
  subagent_type: "hyperpowers:executor"
  model: "sonnet"
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

**Stage 1 — Lead spec check:**
```bash
git diff HEAD~1    # Read the executor's changes
```
Compare the diff against the task spec. Does the implementation match what was specified? If NO: note the gaps, re-dispatch with feedback (see Stage 1 feedback template below).

**Stage 2 — Code quality review:**

```
Agent tool:
  subagent_type: "hyperpowers:code-reviewer"
  model: "sonnet"
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
If reviewer returns CONCERNS: re-dispatch executor with the concern list.

**Stage 1 feedback template** (when lead spec check fails):
```
Re-execute this task. The prior attempt did not match the spec.

Gaps found:
- <gap 1>
- <gap 2>

Task spec:
<paste task spec>

Working directory: <pwd>
Branch: <current branch>
```

### BLOCKED

Executor hit an obstacle it could not resolve. Assess the scope:

**Task-level block** (wrong file path, ambiguous spec, missing fixture): Clarify and re-dispatch:
```
Re-execute this task. The prior executor was blocked: <description>.
Resolution: <clarification or instruction>.

Task spec:
<paste task spec>

Working directory: <pwd>
Branch: <current branch>
```

**Plan-level block** (approach fundamentally broken, assumptions in remaining tasks are invalid): Trigger escalation protocol (see section 5).

**Consecutive BLOCKED threshold:**
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
3. **Wait for user decision.** Use AskUserQuestion. Do NOT continue without user input.
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

   **APPROVED:** Present final status to user. Hand off to `/hyperpowers:finish-branch`.

   **GAPS FOUND:** Create fix task(s) inline for each gap and dispatch executors — this is the one exception to "all tasks planned upfront." These gap-fix tasks follow the same dispatch and two-stage review loop. After all gaps resolved, re-dispatch reviewer.

</the_process>

<examples>

<example>
<scenario>Normal task dispatch and DONE return with passing review</scenario>
<code>
Lead verifies bd-42: non-empty spec, no blocking dependencies pending. Dispatches executor (Sonnet).
Executor returns:
"DONE: Added error handling to auth.ts:validate() and committed as 3f9a1b2."

Stage 1: git diff HEAD~1 → matches spec (error handling added at the right location). ✓
Stage 2: code-reviewer returns "PASS". ✓

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

4. **Two-stage review on every DONE** — Stage 1 (lead spec check) and Stage 2 (code quality review) are both mandatory. Do not skip either stage.

5. **Never redesign autonomously** — On plan-level failures, halt and escalate. Present options; the user decides. Never continue without user input after escalation.

6. **Executor dispatch is blocking** — No team_name parameter. The Agent tool call blocks until the executor returns.

7. **Task spec only in dispatch prompt** — No epic context, no adjacent task details, no cross-task learnings in the executor prompt. The task spec's Why section is the executor's only context.

8. **Epic requirements are immutable** — Never water down a requirement. If an executor's changes violate an anti-pattern, reject in Stage 1 and re-dispatch.

## Common Rationalizations

- "I'll skip Stage 2 since Stage 1 looked fine" → Both stages are mandatory. Dispatch the code-reviewer.
- "I'll just clarify this one thing in the spec and continue" → If it's a plan-level issue, escalate. Don't patch forward.
- "The reviewer is overkill for gap-fix tasks" → Dispatch reviewer after all gaps are fixed. No exceptions.
- "I can answer this NEEDS_HELP myself and keep going" → Answer it in the re-dispatch prompt. Do not implement it in the lead context.

</critical_rules>

<verification_checklist>

Before dispatching each task:
- [ ] Task has a non-empty spec
- [ ] Dependencies are met (blocking tasks completed first)

After each DONE return:
- [ ] Stage 1: Lead read the diff against the task spec
- [ ] Stage 2: Code-reviewer dispatched and returned PASS
- [ ] Task marked done in bd

Before completion:
- [ ] `bd list --parent <epic-id> --status open` returns 0
- [ ] Reviewer dispatched as blocking subagent
- [ ] Verdict handled (APPROVED → finish-branch; GAPS FOUND → fix tasks)

</verification_checklist>

<integration>

**Calls:** agents/executor.md (blocking subagent, per task) · agents/code-reviewer.md (Sonnet, per task) · agents/reviewer.md (blocking subagent, once at end)

**Called by:** User via /hyperpowers:execute-plan · after writing-plans produces the task tree

**Flow:** Startup → Pre-dispatch verification → Dispatch executor (blocks) → Parse one-liner → Two-stage review → Next task → ... → Reviewer gate → Present → /hyperpowers:finish-branch

**bd command reference:** See [bd commands](../common-patterns/bd-commands.md)

**When stuck:**
- Executor timed out → Re-dispatch same task with prompt: 'Prior executor timed out. Check git log for progress. Continue from where it left off.'
- Reviewer GAPS FOUND → Create gap-fix tasks, dispatch executors, re-dispatch reviewer
- Escalation → Summarize, recommend, wait for user

</integration>
