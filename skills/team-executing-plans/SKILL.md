---
name: team-executing-plans
description: Use after wave-planning to spawn agent teams for parallel wave execution - coordinates teammates with hybrid delegation, reviews results at wave boundaries, reconciles beads state
---

<skill_overview>
Execute waves of parallelizable tasks using Claude Code agent teams. The lead spawns teammates for each wave task, operates in delegate mode (coordinate only, no implementation), reviews results at wave boundaries, reconciles beads state, and presents mandatory STOP checkpoints for human review before planning the next wave.
</skill_overview>

<rigidity_level>
LOW FREEDOM - Follow exact process: load wave context, prepare team, spawn teammates, collect results, review wave, reconcile beads, STOP. Lead NEVER implements code during team execution. STOP at every wave boundary. Do not skip beads reconciliation or wave review.
</rigidity_level>

<quick_reference>

| Step | Action | Critical Rule |
|------|--------|---------------|
| **Load Context** | `bd show <epic-id>` + `bd ready` | Extract requirements, anti-patterns, wave tasks |
| **Validate Wave** | Check task count and independence | If only 1 task, fall back to solo executing-plans |
| **Prepare Prompts** | Build teammate spawn prompt per task | Include ALL 7 components (see template) |
| **Spawn Team** | Launch teammates via Task tool with `run_in_background: true` | Spawn ALL teammates in single message (parallel) |
| **Delegate Mode** | Lead coordinates only, no implementation | Lead NEVER writes code, edits files, or runs project commands |
| **Collect Results** | Read each teammate output via TaskOutput | Check success/partial/failed for each |
| **Verify Integration** | Run integration tests via test-runner agent | Catch cross-team conflicts |
| **Check File Ownership** | `git diff --name-only` cross-referenced against boundaries | Revert violations, flag in review |
| **Reconcile Beads** | Verify/fix task statuses + `bd sync` | Close tasks teammates missed, sync git |
| **Wave Review** | Present per-teammate results table | Mandatory STOP checkpoint |
| **STOP** | Wait for user to approve or adjust | NEVER auto-continue to next wave |

**FORBIDDEN:** Lead implementing code. Teammates creating bd tasks. Skipping STOP checkpoints. Spawning team for 1 task.

</quick_reference>

<when_to_use>
**Use after wave-planning creates wave tasks and user approves the wave.**

This skill sits in the team execution path:
```
brainstorming → sre-task-refinement → wave-planning → team-executing-plans
```

Symptoms you need this:
- Wave tasks exist and are approved by user
- 2+ independent tasks ready for parallel execution
- Need to spawn agent teams for parallel work
- Previous wave completed and next wave tasks are ready

**Don't use when:**
- Only 1 task in the wave (use executing-plans solo path)
- Wave tasks not yet created (use wave-planning first)
- Wave not approved by user (present wave-planning summary first)
- Executing solo workflow (use executing-plans)
</when_to_use>

<the_process>

## 0. Resumption Check (Every Invocation)

When invoked, check current state:

```bash
bd list --type epic --status open  # Find active epic
bd ready                           # Check for ready tasks
bd list --status in_progress       # Check for in-progress tasks
```

**Fresh start (wave tasks ready, none in-progress):** Proceed to Step 1.

**Mid-wave resumption (in-progress tasks exist):** Check if teammates are still running. If not, proceed to Step 4 (collect results from whatever state exists).

**Wave complete (all wave tasks closed, epic still open):** Hand back to wave-planning for next wave creation, or proceed to Step 6 (final check) if all streams are done.

**Do not ask "where did we leave off?"** - bd state tells you exactly where to resume.

## 1. Load Wave Context

```bash
bd show <epic-id>  # Load epic: requirements, anti-patterns, Parallelism Map
bd ready           # Find wave tasks ready for execution
```

**Extract from epic:**
- Requirements (IMMUTABLE) - these go into every teammate prompt
- Anti-Patterns (FORBIDDEN) - these constrain every teammate
- Parallelism Map - file ownership boundaries for each stream

**Extract from wave tasks:**
- Task IDs and details (`bd show <task-id>` for each)
- File ownership boundaries per task
- Success criteria per task

**Validate wave size:**
- If only 1 ready task: **Fall back to solo execution.** Tell the user: "Only 1 wave task ready. Using solo executing-plans instead." Then use the executing-plans skill.
- If 2+ ready tasks: Continue with team execution.

## 2. Prepare Teammate Spawn Prompts

For each wave task, construct a teammate prompt using this template. **All 7 components are required** — teammates have zero context without them.

```markdown
You are a teammate executing one task in a parallel wave. Work independently within your file ownership boundaries.

## Your Task
[Paste full `bd show` output for this task, including all design details and success criteria]

## Epic Contract (IMMUTABLE)
**Requirements:**
[Copy RELEVANT requirements from epic — not the entire epic, but requirements pertaining to this task]

**Anti-Patterns (FORBIDDEN):**
[Copy anti-patterns from epic that apply to this task's work]

## File Ownership Boundaries
**You OWN (modify these files only):**
- [exclusive file paths from this task's design]

**You MUST NOT modify (owned by other teammates):**
- [file paths from other wave tasks' ownership]

**Shared files (read-only for you):**
- [shared file paths, if any]

## Methodology
- Follow TDD: Write test first (RED) → run test to see it fail → implement minimal code (GREEN) → refactor → commit
- Before claiming done: run all tests, capture output as evidence
- Commit after each GREEN phase with a descriptive message
- Use verification-before-completion: evidence before assertions

## Beads Constraints
- RUN: `bd update <your-task-id> --status in_progress` when you start
- RUN: `bd close <your-task-id>` when ALL success criteria are met
- DO NOT RUN: `bd sync`, `bd create`, `bd dep add`, or any other bd commands
- DO NOT modify any other task's status

## Communication Protocol
- If you discover work that should be done but is NOT in your task: note it in your final summary (lead will create a task if needed)
- If you hit a blocker that prevents completion: stop and report the blocker clearly in your summary
- DO NOT attempt to fix problems outside your file ownership boundary
- DO NOT communicate with other teammates directly
```

**Prompt sizing:** If the epic is very large, copy only RELEVANT requirements and anti-patterns (not the entire epic). Include the `bd show <task-id>` command in the prompt so teammates can reload context if needed.

## 3. Spawn Teammates

**Spawn ALL teammates in a single message** to maximize parallelism. Use the Task tool with `run_in_background: true` for each:

```
For each wave task, in a SINGLE message with multiple tool calls:

Task tool:
  subagent_type: general-purpose
  description: "Wave N: [Stream Name]"
  prompt: [teammate spawn prompt from Step 2]
  run_in_background: true
  model: sonnet  (default; use opus for high-complexity tasks from SRE refinement)
```

**Critical rules during team execution:**
- **Lead operates in delegate mode**: coordinate only, no implementation
- Lead NEVER: writes code, edits files, runs project build/test commands, modifies source files
- Lead CAN: check teammate progress via TaskOutput (non-blocking), read files for context, run bd commands
- Lead WAITS for all teammates to finish before proceeding to Step 4

**Monitoring progress (optional):**
```
TaskOutput tool:
  task_id: [teammate task ID]
  block: false    # non-blocking check
  timeout: 5000   # short timeout
```

Use non-blocking checks sparingly. Teammates will complete on their own. Do not micromanage.

## 4. Collect and Review Wave Results

After all teammates finish (TaskOutput with `block: true` for each):

### a) Collect Results

For each teammate:
```
TaskOutput tool:
  task_id: [teammate task ID]
  block: true
  timeout: 300000  # 5 min timeout per teammate
```

Record for each teammate:
- **Status:** success / partial / failed / timed out
- **Summary:** what they accomplished
- **Proposed work:** any new tasks they suggested
- **Blockers:** any issues they reported

### b) Handle Teammate Failures

**Teammate timed out:**
- Mark task as still open (don't close it)
- Note timeout in wave review
- Do NOT retry automatically — present to user at STOP checkpoint

**Teammate crashed with error:**
- Capture error message from TaskOutput
- Mark task as still open
- Include error in wave review

**All teammates failed (0 successes):**
- Do NOT proceed to next wave
- Do NOT try to implement fixes (violates delegate mode)
- Present all failure reasons in wave review
- User decides: retry wave, switch to solo execution, or abort

### c) Check File Ownership Violations

After collecting all results, verify no teammate edited files outside their boundary:

```bash
git diff --name-only  # See all changed files
```

Cross-reference each changed file against the wave task file ownership boundaries:
- If a file was modified by a teammate who doesn't own it: **FLAG as violation**
- Remediation: `git checkout -- <violated-file>` to revert unauthorized changes
- Note violation in wave review for user awareness

### d) Run Integration Verification

Use the test-runner agent to verify the combined wave output:

```
Task tool:
  subagent_type: hyperpowers:test-runner
  prompt: "Run: validate"
```

This catches:
- Cross-teammate integration issues
- Tests that pass individually but fail together
- Build/compile errors from combined changes

## 5. Reconcile Beads State

After collecting results and running verification:

### a) Verify Task Statuses

For each wave task:
```bash
bd show <task-id>  # Check current status
```

- If teammate succeeded AND closed their task: Confirmed, no action needed
- If teammate succeeded BUT didn't close: `bd close <task-id> --reason "Completed by teammate, lead reconciliation"`
- If teammate failed: Keep task open, no changes
- If unsure whether task completed: Keep open, note for user review

### b) Sync Beads

```bash
bd sync  # Push beads state to git
```

**Do NOT skip bd sync.** This ensures all task status changes are persisted before the STOP checkpoint.

## 6. Present Wave Review Summary and STOP

**This is a mandatory STOP checkpoint.** Present the comprehensive review:

```markdown
## Wave N Complete - Review

### Per-Teammate Results
| Task | Stream | Status | Key Deliverable | Notes |
|------|--------|--------|-----------------|-------|
| bd-X | [Name] | success | [What was delivered] | [Any issues] |
| bd-Y | [Name] | success | [What was delivered] | [Proposed new work: ...] |
| bd-Z | [Name] | failed | [What was attempted] | [Blocker: ...] |

### Integration Verification
- Test suite: [pass/fail with summary from test-runner]
- File ownership violations: [none / list of violations and remediations]

### Beads Reconciliation
- bd-X: closed (by teammate)
- bd-Y: closed (by lead reconciliation — teammate completed but didn't close)
- bd-Z: open (teammate failed — see Notes)
- bd sync: completed

### Proposed New Work (from teammate summaries)
- [Teammate Y proposed: "Need a migration script for schema changes"]
- [Teammate X noted: "Error handling for edge case Z should be added"]

### Epic Progress
- Streams completed: [X/Y total]
- Success criteria met: [N/M]
- Remaining streams: [list]

### Next Steps
- [If more waves needed]: Run `/hyperpowers:write-plan` (wave-planning) to create next wave based on these learnings
- [If all streams complete]: Run `/hyperpowers:review-implementation` for final validation
- [If failures need addressing]: Review failed tasks and decide: retry, reassign to solo path, or adjust approach
```

**STOP and wait for user review. Mandatory.**

User may:
- **Approve and continue** → Run wave-planning for next wave
- **Retry failed tasks** → Re-run team-executing-plans with failed tasks
- **Switch to solo** → Use executing-plans for remaining work
- **Adjust scope** → Modify tasks or epic based on learnings
- **Abort** → Stop execution entirely

**Do NOT rationalize skipping the stop:**
- "All teammates succeeded" → STOP anyway, user needs to review integration
- "Next wave is obvious" → STOP anyway, learnings may change wave composition
- "Momentum" → STOP anyway, checkpoints prevent runaway execution

## 7. Final Check (When All Streams Complete)

When all streams from the Parallelism Map are complete and all wave tasks are closed:

```bash
bd show <epic-id>  # Check success criteria
```

If ALL success criteria appear met:

1. **Use review-implementation skill:**
```
Use Skill tool: hyperpowers:review-implementation
```

2. Review-implementation will verify:
   - Each requirement met
   - Each success criterion satisfied
   - No anti-patterns violated
   - If approved: STOP for manual validation (epic stays open)
   - If gaps found: Create remediation tasks, return to execution

3. After manual validation complete, user runs `/hyperpowers:finish-branch` to close epic and integrate.

</the_process>

<examples>

<example>
<scenario>3 teammates execute Wave 2 (OAuth providers) successfully — correct wave execution</scenario>

<code>
Wave 2 tasks ready after Wave 1 (infrastructure) completed:
- bd-3: Google OAuth (owns auth/strategies/google.ts, tests/auth/google.spec.ts)
- bd-4: GitHub OAuth (owns auth/strategies/github.ts, tests/auth/github.spec.ts)
- bd-5: Facebook OAuth (owns auth/strategies/facebook.ts, tests/auth/facebook.spec.ts)

**Step 1: Load context**
bd show bd-1  # Epic with requirements, anti-patterns
bd ready      # Shows bd-3, bd-4, bd-5 all ready

**Step 2: Prepare prompts**
Each teammate prompt includes:
1. Full task details from bd show
2. Epic requirements (OAuth must use passport.js strategies)
3. Anti-patterns (NO custom auth, NO mocking integration tests)
4. File ownership (each owns their strategy + test file only)
5. Must-not-touch (other providers' files)
6. TDD methodology
7. Beads constraints (update status, close own task)

**Step 3: Spawn team**
Single message with 3 Task tool calls:
- Task: "Wave 2: Google OAuth" (run_in_background: true, model: sonnet)
- Task: "Wave 2: GitHub OAuth" (run_in_background: true, model: sonnet)
- Task: "Wave 2: Facebook OAuth" (run_in_background: true, model: sonnet)

Lead waits (no code implementation).

**Step 4: Collect results**
- bd-3 (Google): SUCCESS - strategy implemented, 8 tests passing, task closed
- bd-4 (GitHub): SUCCESS - strategy implemented, 7 tests passing, task closed
- bd-5 (Facebook): SUCCESS - strategy implemented, 6 tests passing, task closed
  - Proposed: "Facebook requires additional scope for email access — need config update"

git diff --name-only shows only expected files modified. No violations.
Integration tests pass via test-runner agent.

**Step 5: Reconcile beads**
All 3 tasks already closed by teammates. bd sync completed.

**Step 6: Wave review**

## Wave 2 Complete - Review

### Per-Teammate Results
| Task | Stream | Status | Key Deliverable | Notes |
|------|--------|--------|-----------------|-------|
| bd-3 | Google OAuth | success | Google strategy + 8 tests | Clean implementation |
| bd-4 | GitHub OAuth | success | GitHub strategy + 7 tests | Clean implementation |
| bd-5 | Facebook OAuth | success | Facebook strategy + 6 tests | Proposed: email scope config |

### Integration Verification
- Test suite: PASS (21 new tests, all passing)
- File ownership violations: none

### Beads Reconciliation
- bd-3: closed (by teammate)
- bd-4: closed (by teammate)
- bd-5: closed (by teammate)
- bd sync: completed

### Proposed New Work
- Facebook teammate: "Facebook requires additional scope for email access — need config update in passport-config.ts"

### Epic Progress
- Streams completed: 4/5
- Success criteria met: 8/10
- Remaining: OAuth UI Components (Stream 5)

### Next Steps
Run wave-planning to create Wave 3 (UI Components) incorporating Facebook email scope discovery.

STOP — waiting for user review.
</code>

<why_it_fails>
N/A — this is the correct pattern demonstrating:
1. All teammates spawned in single message (parallel execution)
2. Lead operated in delegate mode (no code during execution)
3. Results collected systematically from each teammate
4. File ownership verified via git diff
5. Integration tests run via test-runner agent
6. Beads reconciled (all tasks confirmed closed, bd sync)
7. Wave review presented with per-teammate results table
8. Proposed new work surfaced from teammate summary
9. STOP checkpoint honored
</why_it_fails>

<correction>
This example demonstrates correct behavior. The key elements are:
- **Comprehensive teammate prompts** with all 7 components
- **Parallel spawning** in a single message
- **Delegate mode** — lead did no implementation
- **Systematic result collection** with status tracking
- **File ownership verification** prevented merge conflicts
- **Integration testing** caught cross-team issues (none in this case)
- **Beads reconciliation** ensured persistent state is correct
- **Wave review** gave user full visibility before proceeding
- **Discovery surfaced** — Facebook email scope will inform Wave 3 planning
</correction>
</example>

<example>
<scenario>Lead implements a fix for a teammate's failing test instead of flagging it</scenario>

<code>
Wave 2 executing. Lead checks on teammate progress:

TaskOutput for bd-3 (Google OAuth): teammate reports test failure in
google.spec.ts — assertion mismatch on callback URL.

Lead thinks: "Quick fix — I'll just update the test assertion."
Lead edits tests/auth/google.spec.ts to fix the assertion.
Lead continues monitoring other teammates.
</code>

<why_it_fails>
**Violates delegate mode:**
- Lead is forbidden from writing code during team execution
- Lead edited a file (google.spec.ts) that belongs to the bd-3 teammate
- This undermines the teammate's ownership and could create conflicts
- If teammate also fixes it, there's a merge conflict
- Lead's "quick fix" may not understand the teammate's intent

**Why it happens:**
- Lead sees an "easy" fix and wants to help
- Feels inefficient to wait for teammate to figure it out
- Rationalizes: "I'm just helping, not really implementing"

**Result:**
- Potential merge conflict with teammate's work
- Teammate's context is now incorrect (file changed externally)
- Violates file ownership boundaries
- Breaks the delegate mode contract
</why_it_fails>

<correction>
**Lead must NOT implement during team execution:**

1. **Note the issue** — record that bd-3 teammate has a test failure
2. **Do NOT edit any files** — delegate mode forbids implementation
3. **Wait for teammate** — they may fix it themselves
4. **If teammate reports failure in summary** — include it in wave review
5. **At STOP checkpoint** — user decides: retry task, help teammate, or adjust

**Correct lead behavior during team execution:**
- Monitor progress (read-only)
- Track issues for wave review
- NEVER write code, edit files, or run project commands
- Present all findings at STOP checkpoint for user decision

**Result:** Clean separation of concerns. User reviews the failure at the checkpoint and decides the appropriate response. No merge conflicts. No file ownership violations.
</correction>
</example>

</examples>

<critical_rules>

## Rules That Have No Exceptions

1. **Lead NEVER implements during team execution** → Delegate mode is mandatory
   - Lead does NOT: write code, edit files, run build/test commands on project files
   - Lead DOES: monitor progress, check bd state, prepare wave review, run bd commands
   - "Quick fix" = violation. Always.

2. **STOP at every wave boundary** → Human must review before next wave
   - Present comprehensive wave review summary
   - User approves before wave-planning creates next wave
   - No exceptions — even if all teammates succeeded

3. **Spawn ALL teammates in a single message** → Maximize parallelism
   - Multiple Task tool calls in one response
   - All with `run_in_background: true`
   - Do NOT spawn sequentially

4. **Fall back to solo for 1 task** → Team overhead exceeds benefit for single tasks
   - If only 1 wave task ready: use executing-plans (solo) instead
   - Do NOT spawn a team for a single task
   - Tell user: "Only 1 wave task ready. Using solo executing-plans instead."

5. **Teammates NEVER create bd tasks or manage dependencies** → Lead manages all bd mutations
   - Teammates can: `bd update --status in_progress`, `bd close` (own task only)
   - Teammates cannot: `bd sync`, `bd create`, `bd dep add`, or modify other tasks
   - Lead handles: task creation, dependency management, bd sync

6. **Verify file ownership after every wave** → Prevent merge conflicts
   - `git diff --name-only` cross-referenced against task boundaries
   - Revert violations: `git checkout -- <file>`
   - Report violations in wave review

7. **Reconcile beads before STOP** → Ensure persistent state is accurate
   - Verify each task status matches reality
   - Close tasks that teammates completed but didn't close
   - Run `bd sync` before presenting wave review

8. **Teammate prompts include ALL 7 components** → Teammates have zero context without them
   1. Task details (full bd show output)
   2. Epic requirements (IMMUTABLE)
   3. Anti-patterns (FORBIDDEN)
   4. File ownership boundaries (owns + must-not-touch + shared)
   5. TDD methodology
   6. Beads constraints
   7. Communication protocol

9. **Do NOT retry failed teammates automatically** → Present failures at STOP checkpoint
   - User decides: retry, reassign, adjust approach, or abort
   - Automatic retry wastes tokens if the failure is systemic
   - Lead cannot diagnose teammate failures without implementing (violates delegate mode)

## Common Excuses

All of these mean: **Follow delegate mode. Present at STOP. Let user decide.**

- "Quick fix for teammate's test" → Violates delegate mode. Note for wave review.
- "All succeeded, skip the review" → STOP anyway. Integration issues surface during review.
- "Just one more wave" → STOP. User needs checkpoint between every wave.
- "Teammate is stuck, let me help" → Note it. Present at STOP. User decides.
- "Only 1 task left, still spawn team" → Fall back to solo. Team overhead > benefit.
- "I'll fix the file ownership violation myself" → Revert it. Report it. User decides.
- "bd sync can wait" → Sync NOW. State must be consistent before STOP.
- "Teammate's prompt doesn't need all 7 sections" → It does. Teammates have ZERO context.
- "Let me retry the failed teammate" → Present failure at STOP. User decides.
- "Wave review is overkill for 2 tasks" → Every wave gets a full review. No exceptions.

</critical_rules>

<verification_checklist>

Before spawning teammates:
- [ ] Epic loaded — requirements, anti-patterns, Parallelism Map extracted
- [ ] Wave tasks validated — 2+ independent tasks ready (if 1, use solo path)
- [ ] Each teammate prompt includes ALL 7 components
- [ ] All teammate prompts have correct file ownership boundaries
- [ ] Teammate prompts reference specific task IDs for bd commands

During team execution:
- [ ] Lead is in delegate mode — NO code writing, file editing, or project commands
- [ ] All teammates spawned in single message (parallel)
- [ ] Lead monitoring via TaskOutput (non-blocking, read-only)

After teammates complete:
- [ ] Results collected from ALL teammates (TaskOutput with block: true)
- [ ] File ownership violations checked (git diff --name-only cross-referenced)
- [ ] Integration tests run via test-runner agent
- [ ] Failed teammates documented (not auto-retried)

Beads reconciliation:
- [ ] Each task status verified against teammate results
- [ ] Completed-but-not-closed tasks closed by lead
- [ ] Failed tasks left open with notes
- [ ] `bd sync` executed

Wave review:
- [ ] Per-teammate results table presented
- [ ] Integration verification results included
- [ ] Beads reconciliation summary included
- [ ] Proposed new work (from teammate summaries) listed
- [ ] Epic progress shown (streams completed, criteria met)
- [ ] Next steps recommended
- [ ] STOP checkpoint honored — waiting for user

Before closing epic:
- [ ] ALL streams complete (all waves executed)
- [ ] ALL success criteria met
- [ ] review-implementation skill used and approved
- [ ] No anti-patterns violated
- [ ] All tasks closed

</verification_checklist>

<integration>

**This skill is called by:**
- wave-planning (after user approves wave composition)
- User (via `/hyperpowers:execute-wave` command)
- User (to resume after STOP checkpoint with a new wave ready)

**This skill calls:**
- hyperpowers:test-runner agent (integration verification after each wave)
- hyperpowers:wave-planning (handoff for next wave creation after STOP)
- hyperpowers:executing-plans (fallback for single-task degenerate waves)
- hyperpowers:review-implementation (final validation when all streams complete)

**Call chain:**
```
wave-planning → [user approves] → team-executing-plans → wave review → STOP
  → [user approves] → wave-planning (next wave) → team-executing-plans → ...
  → [all streams complete] → review-implementation → finish-branch
```

**Agents used:**
- general-purpose (teammates — spawned via Task tool with run_in_background: true)
- hyperpowers:test-runner (integration verification — spawned via Task tool)

**bd commands used:**
- `bd show <epic-id>` — Load epic context
- `bd show <task-id>` — Load task details for teammate prompts
- `bd ready` — Find wave tasks ready for execution
- `bd list --status in_progress` — Check for active tasks (resumption)
- `bd close <task-id>` — Reconcile tasks teammates didn't close
- `bd sync` — Sync beads state at wave boundaries

**Workflow pattern:**
```
/hyperpowers:execute-wave → Spawn team → Collect results → Review → STOP
[User reviews wave, clears context]
/hyperpowers:write-plan (wave-planning) → Create next wave → STOP
[User approves wave]
/hyperpowers:execute-wave → Spawn team → Collect results → Review → STOP
[Repeat until all streams complete]
/hyperpowers:review-implementation → Final validation
/hyperpowers:finish-branch → Close epic and integrate
```

</integration>

<resources>

**Teammate model selection guide:**
| Task Complexity | SRE Edge Cases | Recommended Model |
|----------------|----------------|-------------------|
| Low | Few | sonnet (default) |
| Medium | Some | sonnet |
| High | Many | opus |

Default to sonnet for cost efficiency. Use opus only when task has high complexity AND many edge cases identified during SRE refinement.

**Wave execution timing:**
- Typical teammate execution: 2-10 minutes depending on task complexity
- Use `TaskOutput` with `timeout: 300000` (5 min) for each teammate collection
- If a teammate exceeds 5 minutes, extend timeout or flag as slow in wave review

**When stuck:**
- Teammate won't finish → Check TaskOutput with block: false, note status for wave review
- All teammates failed → Present to user at STOP, do NOT implement fixes
- File ownership conflict detected → Revert with `git checkout -- <file>`, document in review
- Beads state inconsistent → Keep uncertain tasks open, note for user
- Only 1 wave task → Use executing-plans (solo path), do NOT spawn a team
- Teammate proposed significant new work → Include in wave review "Proposed New Work" section
- Integration tests fail after wave → Include failures in wave review, user decides remediation

**Key anti-patterns to watch for:**
- Lead writing code "to help a teammate" → Delegate mode violation
- Retrying failed teammates without user approval → Wastes tokens, may repeat systemic failure
- Spawning teammates one at a time → Must be single message for parallelism
- Skipping file ownership check → Merge conflicts will surface later, harder to fix
- Closing epic without review-implementation → Tasks done ≠ criteria met

</resources>
