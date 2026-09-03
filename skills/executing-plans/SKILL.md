---
name: executing-plans
description: Lead reads pre-planned task list, dispatches fresh blocking executor subagent (Sonnet by default, promotable) per task, runs two-stage per-task review, and escalates to user when plan proves invalid.
---

<skill_overview>
Lead orchestrates execution of a pre-planned task list. All tasks exist in bd before execution begins. Lead dispatches a fresh executor subagent per task, runs two-stage review (lead epic-coherence check + Stage-2 code-reviewer spec-match/code quality check), and escalates to user when the plan proves invalid. Epic requirements are immutable.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — Pre-dispatch verification uses judgment. Dispatch, review, and escalation protocol are rigid (follow exactly). Do not skip stage 1 or stage 2 review. Do not redesign the plan autonomously.

The lead never implements task work in the lead context. One carve-out: `[convention]`-class finding fixes (Stage 2 CONCERNS handling and the GAPS FOUND branch below), which the lead applies directly. A convention fix must never change behavior — the moment it would, it stops being a convention fix (retag and dispatch it).
</rigidity_level>

<quick_reference>

| Step | Action | How |
|------|--------|-----|
| **Startup** | Load epic, list all tasks, verify specs | `bd show <epic-id>` + `bd list --parent <epic-id>` |
| **Branch** | Establish working branch; never dispatch on the default | `git branch --show-current` (+ `git checkout -b epic/<epic-id>` when on main) |
| **Pre-dispatch** | Verify spec exists and dependencies met | `bd show <task-id>` |
| **Dispatch** | Record base SHA, then fresh blocking executor subagent per task | `git rev-parse HEAD` + Agent tool (no team_name, Sonnet unless promoted) |
| **Stage 1** | Lead reads diff vs recorded base SHA for epic coherence (boy-scout cleanup is in-scope, not drift) | `git merge-base --is-ancestor <hash> HEAD` + `git diff <base-SHA>..HEAD` |
| **Stage 2** | Stage-2 code-reviewer: spec-match + code quality review; findings resolve by class — `[convention]` lead-fixed, `[capability]` re-dispatched (cap: 2 rounds — `pipeline-constants.md`) | Agent tool (Sonnet unless promoted) |
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

Do not re-check whether the implementation matches the task spec line-by-line — that is Stage 2's job.

**Sanctioned, not drift:** an executor that removed noise comments or corrected stale docstrings inside a file the spec already named was following the boy-scout rule (`skills/common-patterns/prose-style.md`), which makes that cleanup mandatory and in-scope. Do not flag it as scope drift. Opening a file the spec does not name is still drift — the boy-scout rule extends what gets fixed inside an authorized file, never which files are authorized.

If any check above fails: note the violation(s), re-dispatch with feedback (see Stage 1 feedback template below).

**Stage 2 — Code-reviewer spec-match and code quality check:**

The fresh Stage-2 code-reviewer owns both spec-match and code quality — the lens Stage 1 does not cover:

```
Agent tool:
  subagent_type: "hyperpowers:code-reviewer"
  model: "sonnet"    # "opus" if the task spec contains the line `Executor: opus`
  prompt: |
    Review this change for code quality.

    Task spec:
    <paste task spec here>

    Changes (git diff):
    <paste git diff output here>

    Check: Does the implementation match the spec? Any anti-patterns,
    missing error handling, or quality issues?
    Reply PASS or CONCERNS: <one-line summary>, followed by the concern
    list — one line per concern: `[capability|convention] <file>:<line>
    — <what and why>` (contract: skills/common-patterns/loop-interfaces.md).
```

Task closure is owned by the lead — the executor never closes tasks. Exactly two paths authorize closure: a Stage-2 PASS, or a convention-only CONCERNS verdict whose every concern line has been lead-fixed, verified, and recorded (below). No other path closes a task, and both require verifying the working branch (Branch Establishment rule) before `bd close <task-id>`.

If the Stage-2 code-reviewer returns PASS: verify the working branch, run `bd close <task-id>`, then proceed to the next task.

If the Stage-2 code-reviewer returns CONCERNS: the concern lines arrive class-tagged (`[capability]` or `[convention]`, one tag per line — format: `skills/common-patterns/loop-interfaces.md`). The lead owns final classification (`skills/common-patterns/pipeline-constants.md`, Finding Classification) and may retag a line; record the retag in a one-line bd note. Resolution splits by class:

- **`[convention]` concerns — lead fixes them directly, now.** Edit the named sites yourself, verify by grep/read against each concern line, commit on the working branch, and record it: `bd update <task-id> --notes "Convention concerns lead-fixed: <short list> (<commit hash>)"`. No re-dispatch and no Stage-2 re-run for these lines. **Bound:** a convention fix must not change behavior. If mid-fix it turns out to require one, stop, retag the line `[capability]` (one-line bd note), and route it through the capability path below.
- **`[capability]` concerns — re-dispatch** with the capability concern list only (template below). Promotion rule unchanged: if this is the task's first re-dispatch and it is not already promoted, add `Executor: opus` to the task spec and note it in bd (e.g. `bd update <task-id> --notes "Auto-promoted to opus after Stage 2 [capability] CONCERNS"`). **Round cap (`skills/common-patterns/pipeline-constants.md`): after 2 capability fix→re-review rounds on the same task without PASS, stop and escalate (section 5), carrying the concern history from every round.**
- **Mixed verdicts:** lead-fix the `[convention]` lines first, then re-dispatch with only the `[capability]` lines.
- **`SUGGESTION:` lines** are non-blocking: persist them to the epic's bd notes as optional follow-ups. Never act on them in-round; they never gate task closure.

A task is still NEVER closed with unaddressed concerns — every concern line is either lead-fixed (`[convention]`) or re-dispatched (`[capability]`).

**Closing after CONCERNS.** A convention-only verdict — every concern line `[convention]` after any retags — closes on the lead-fix path, not on a Stage-2 re-run: no re-run is required or possible for these lines. Once every line is lead-fixed, verified by grep/read, committed, and recorded in the bd note above, verify the working branch (Branch Establishment rule) and run `bd close <task-id>`. A verdict carrying any `[capability]` line — capability-only or mixed — closes only when the re-dispatch loop reaches a Stage-2 PASS; if it hits the round cap first, the task stays open and escalates (section 5). The convention lead-fixes inside a mixed verdict never close the task on their own.

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

**Stage-2 CONCERNS re-dispatch template** (the concern list carries only `[capability]` lines — `[convention]` lines were already lead-fixed):
```
Re-execute this task. The Stage-2 code review returned CONCERNS.

Concerns to address:
- <file:line — capability concern 1>
- <file:line — capability concern 2>

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
- A round cap is reached (see section 4 Stage 2 and section 6 GAPS FOUND; cap constant: `skills/common-patterns/pipeline-constants.md`)

**Steps — follow exactly:**

1. **Halt execution immediately.** Do not dispatch the next task.
2. **Summarize to user:**
   - Where the epic stands: what it was building, in system terms — completed tasks trail as evidence (commit hashes), not the headline
   - The failure and what it means: what failed, why, and the system-level consequence
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
     prompt: |
       Review the implementation for epic <epic-id>.
       Follow agents/reviewer.md exactly.
       Start with: bd show <epic-id>
   ```

3. Handle the verdict:

   **APPROVED:**

   a. Verify the working branch, then persist the completion gate-state block to the epic's bd notes (format: `skills/common-patterns/loop-interfaces.md`), including any accumulated plan-impact notices. The block MUST include the machine-checkable marker line `Verdict: APPROVED (end-of-epic reviewer, <date>)` (format: `skills/common-patterns/loop-interfaces.md`). Any non-blocking `### Suggestions` section the reviewer returns goes to the epic's bd notes as optional follow-ups — never acted on in-round, same disposition as the GAPS FOUND branch.
   b. Run the post-build Architecture Impact Check against the work just completed for this epic, per `skills/common-patterns/architecture-impact-check.md` (Post-Build Routing) — cite that file, do not restate the 5 questions here. Any YES routes per that file: dispatch `/ponder` in UPDATE mode when a model exists, or note-and-suggest in the completion report when no model exists.
   c. Present final status to the user, at architect altitude per the Audience Contract (`skills/common-patterns/prose-style.md`, The Reader — cite, don't restate):
      - **What was built:** at most 6 sentences of role-based plain language — the system change this epic delivered (components, behavior, contracts) — leaning on the reviewer's Architect Summary rather than restating the audit.
      - **Decided during build:** judgment calls the lead made that the architect didn't see — retags, convention lead-fixes, promotions, Suggestions filed to bd notes — as plain descriptions; commit hashes may appear as trailing evidence, never as the narrative.
      - **Needs you:** the manual-validation focus — what to exercise and why — plus any decisions left on file.
      No internal vocabulary (stage labels, class tags as narrative) belongs in this presentation; class tags may still appear in trailing evidence.
   d. **STOP here.** Do not automatically call finishing-a-development-branch. The user needs time to test the implementation manually in their environment, verify edge cases automated tests don't cover, and confirm the feature works as expected in context. Closing the epic removes context the user may need during manual validation — let them explicitly trigger closure when ready.
   e. The epic remains open. The user runs `/hyperpowers:finish-branch` when ready.

   **GAPS FOUND:** Gap entries arrive class-tagged, same vocabulary as Stage 2 (`skills/common-patterns/loop-interfaces.md`); the lead owns final classification (`skills/common-patterns/pipeline-constants.md`, Finding Classification). Resolve by class:

   - **`[convention]` gaps:** the lead fixes them directly under the same bounded carve-out as Stage 2 — no fix task, no executor. Edit, verify against each gap entry, commit on the working branch, and record it in the epic's bd notes (`bd update <epic-id> --notes "Convention gaps lead-fixed: <short list> (<commit hash>)"`). Same bound: if a fix turns out to require a behavior change, stop, retag it `[capability]`, and route it below.
   - **`[capability]` gaps:** create fix task(s) inline — spec body per the tier templates in `skills/common-patterns/spec-templates.md` — and link each to the epic: `bd dep add bd-<fix-task> bd-<epic-id> --type parent-child` (the completion re-check and re-review enumerate tasks via `bd list --parent`) — then dispatch executors. This is the one exception to "all tasks planned upfront." These gap-fix tasks follow the same dispatch and two-stage review loop.

   After ALL gaps are resolved — both classes — re-dispatch the end-of-epic reviewer. This re-review is mandatory and unchanged: convention gaps being lead-fixed does not exempt the epic from it.

   **Round cap (`skills/common-patterns/pipeline-constants.md`): after 2 full gap rounds (2 reviewer re-dispatches following the initial review) without APPROVED, stop and escalate (section 5), carrying the outstanding gap list.**

   Any non-blocking Suggestions section the reviewer returns goes to the epic's bd notes as optional follow-ups — it never blocks approval and is never fixed in-round.

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
- Status: implementing the task-sync migration; bd-48–50 landed cleanly (commits: a1b2c, d3e4f, g5h6i)
- Failure: the live API is still v1, not v2 as assumed — bd-51–53 all block on this schema mismatch
- Remaining tasks affected: bd-51, bd-52, bd-53
- Recommendation: replan bd-51–bd-53 to use the v1 API schema.

Waits for user response before proceeding.
</code>
</example>

</examples>

<critical_rules>

1. **All tasks pre-planned** — Do not create tasks during execution (exception: gap-fix tasks after end-of-epic reviewer GAPS FOUND verdict).

2. **No SRE per-task** — SRE batch review runs before execution begins. Never invoke SRE between tasks.

3. **Parse the one-liner** — Executor returns DONE:, BLOCKED:, or NEEDS_HELP: as a one-liner. There are no multi-section status envelopes to parse.

4. **Two-stage review on every DONE** — Stage 1 (lead epic-coherence check against the recorded base SHA — commit-landed check, then diff `<base-SHA>..HEAD`) and Stage 2 (code-reviewer spec-match and code quality check) are both mandatory on every DONE. Do not skip either stage. Class-split resolution changes only what happens to findings *after* Stage 2 returns — `[convention]` lead-fixes are a resolution path, never a substitute for running Stage 2.

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
- "I'll promote to opus since the Stage-2 code-reviewer raised a concern" → Not for `[convention]` concerns — those never reach an executor at all; the lead fixes them. Promotion is reserved for `[capability]` failures; don't spend the rung on a convention fix.
- "This concern is borderline — I'll call it `[convention]` and save a dispatch" → If the fix touches behavior in any way, it is `[capability]`. Dispatch it. The carve-out exists to skip dispatches that buy nothing, not to skip review of real changes.
- "This convention fix is growing, but I'm halfway through — I'll finish it here" → Stop. A convention fix that grows into behavior was misclassified. Retag it `[capability]`, note the retag, and dispatch it.

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
- [ ] Stage 2: code-reviewer dispatched (mandatory on every DONE, spec-match and code quality) and its verdict resolved — PASS, or CONCERNS handled per the class split below
- [ ] Any CONCERNS resolved by class — `[convention]` lines lead-fixed and verified, `[capability]` lines re-dispatched (never closed as-is); promotion applied only to `[capability]` failures
- [ ] Convention lead-fixes recorded in bd notes with the commit hash (`Convention concerns lead-fixed: ...`)
- [ ] No convention fix changed behavior — any that would have was retagged `[capability]` and dispatched
- [ ] Stage-2 round cap respected (`pipeline-constants.md`): 2 capability fix→re-review rounds on a task without PASS → escalated (section 5), not a 3rd round
- [ ] `SUGGESTION:` lines persisted to the epic's bd notes, not acted on in-round
- [ ] Any BLOCKED classified before re-dispatch; promotion applied only to capability-class failures
- [ ] Task closed in bd by the lead on an authorized path — Stage 2 PASS, or, for a convention-only CONCERNS verdict, every concern line lead-fixed, verified, and recorded
- [ ] Working branch verified before task closure

Before completion:
- [ ] `bd list --parent <epic-id> --status open` returns 0
- [ ] End-of-epic reviewer dispatched as blocking subagent
- [ ] APPROVED → gate-state persisted, post-build Architecture Impact Check run (per `architecture-impact-check.md`), final status presented, then STOP — no automatic call to finish-branch
- [ ] GAPS FOUND → `[convention]` gaps lead-fixed and recorded in the epic's bd notes, `[capability]` gaps turned into linked fix tasks and dispatched, end-of-epic reviewer dispatched again to confirm
- [ ] Gap-round cap respected (`pipeline-constants.md`): 2 reviewer re-dispatches without APPROVED → escalated (section 5), not a 3rd round
- [ ] Reviewer Suggestions (either verdict) persisted to the epic's bd notes as optional follow-ups
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
- End-of-epic reviewer GAPS FOUND → Lead-fix the `[convention]` gaps, create gap-fix tasks for the `[capability]` gaps and dispatch executors, then re-dispatch the end-of-epic reviewer
- End-of-epic reviewer APPROVED → Persist gate-state, run the post-build Architecture Impact Check, present, then STOP — never auto-call finish-branch
- Escalation → Summarize, recommend, wait for user

</integration>
