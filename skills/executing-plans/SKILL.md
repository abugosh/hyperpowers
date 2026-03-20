---
name: executing-plans
description: Use to execute bd tasks via agent teams delegation - lead orchestrates from main context, a fresh executor teammate is spawned for each individual task, health monitoring catches silent executor death, project memory bridges cross-task learnings.
---

<skill_overview>
Lead orchestrates execution via agent teams. Spawns a fresh executor teammate for each individual task (not one long-running executor), receives structured summaries and progress checkpoints, validates proposals against epic requirements and anti-patterns, monitors executor health with two-tier timeout (10 min + 5 min), recovers from executor death via respawn, dispatches reviewer subagent for final verification. Project memory replaces in-context accumulation for cross-task learnings — executor writes discoveries before shutdown, next executor reads them on startup. Epic requirements are immutable, tasks adapt to reality.
</skill_overview>

<rigidity_level>
LOW FREEDOM - Follow exact orchestration process. Lead never implements directly — only orchestrates via messages. Epic requirements are immutable.

Do not skip proposal validation, health monitoring, reviewer dispatch, or shutdown protocol. Do not implement code in the lead context. Do not auto-approve proposals without checking the epic. Do not skip memory read/write at executor lifecycle boundaries.
</rigidity_level>

<quick_reference>

| Step | Action | Tool/Command |
|------|--------|--------------|
| **Load Epic** | Read immutable requirements + project memory | `bd show <epic-id>` + read memory |
| **Create Team** | Initialize team for this epic (ONCE per epic) | TeamCreate |
| **Spawn Executor** | Start fresh executor for ONE task | Task tool with `team_name` and `name` params |
| **Monitor** | Track time since last message, reset on any message | Timer (10 min threshold) |
| **Receive Progress** | Note TDD checkpoint, reset health timer | No response needed (unless anti-pattern spotted) |
| **Validate Proposal** | Check against epic requirements/anti-patterns | `bd show <epic-id>` + systematic check |
| **Shutdown Executor** | Gracefully end current executor (per-task) | SendMessage type: "shutdown_request" |
| **Spawn Next** | Fresh executor for next approved task | Task tool with `team_name` and `name` params |
| **Health Check (Tier 1)** | Status check after 10 min silence | SendMessage status question |
| **Health Check (Tier 2)** | Assume dead after 5 min no response | Trigger recovery protocol |
| **Dispatch Reviewer** | Final verification (subagent, not teammate) | Task tool (no `team_name`) |
| **Shutdown at Epic End** | Terminate executor after reviewer APPROVED | SendMessage type: "shutdown_request" |
| **Cleanup** | Remove team (epic end only) | TeamDelete |

**Critical:** Executor is spawned/shutdown PER TASK, not per epic. Team persists for the epic. Lead's value = validation against epic on every proposal + proactive health monitoring.

</quick_reference>

<when_to_use>
**Use after hyperpowers:writing-plans creates epic and first task.**

Symptoms you need this:
- bd epic exists with tasks ready to execute
- Need to implement features iteratively with TDD
- Requirements clear, but implementation path will adapt
- Want cross-task learnings bridged via project memory without context exhaustion

**Key difference from old pattern:** Executor is a fresh spawn per task. Context exhaustion is structurally impossible because each executor has a bounded, single-task lifecycle.
</when_to_use>

<the_process>

## 0. Resumption Check (Every Invocation)

Every time this skill is invoked, check current state before acting:

```bash
bd list --type epic --status open  # Find active epic
bd ready                           # Check for ready tasks
bd list --status in_progress       # Check for in-progress tasks
```

Also check for an existing team:

```bash
ls ~/.claude/teams/  # Check for active team directories
```

Also check project memory for epic-scoped learnings:
```
Read any memory files matching the pattern: epic-<epic-id>-*
Location: /Users/<you>/.claude/projects/<project-path>/memory/
```

**Decision matrix:**

| Team exists? | Executor state | bd state | Action |
|-------------|---------------|----------|--------|
| No | N/A | No in-progress tasks | Fresh start → Step 1 |
| No | N/A | In-progress task exists | Fresh start → Step 1 (spawn executor to resume that task) |
| Yes | Idle | Task in progress | Resume → SendMessage to executor to continue current task |
| Yes | Active | Task in progress | Resume → Enter monitoring mode (wait for messages) |
| Yes or No | N/A | All tasks closed, epic open | Skip to Step 4 (reviewer dispatch) |
| Yes | Unknown | Multiple in-progress tasks | ERROR STATE → Close all but most recently updated, spawn executor for that one |
| Yes | Running for multiple tasks | Any | MIGRATION STATE → Send shutdown_request to old executor, then proceed with per-task model |

**Migration from old pattern:** If you find a team where the same executor has been running across multiple tasks (identifiable by task completion messages covering multiple bd tasks without shutdown/respawn), this is the old long-running pattern. Send it a shutdown_request, confirm it writes learnings to memory, then resume with per-task model for remaining tasks.

**If multiple epics are open:** Ask the user which epic to execute (use AskUserQuestion). One team per epic, one epic at a time.

**Do not ask "where did we leave off?"** — bd state, team state, and project memory tell you exactly where to resume.

## 1. Load Epic Context

Before doing anything else, load the epic into your context:

```bash
bd list --type epic --status open  # Find epic
bd show <epic-id>                  # Load epic details
```

**Extract and hold in mind (you keep this for the entire session):**
- **Requirements** — IMMUTABLE. Never water down, even when executor reports blockers.
- **Success Criteria** — Your validation checklist for every proposal.
- **Anti-Patterns** — FORBIDDEN. Reject any proposal that violates these.
- **Design Discovery** — Reference context for obstacle decisions and escalations.
- **Approaches Considered** — Especially the rejected approaches and their "DO NOT REVISIT UNLESS" conditions.

**Also read project memory** for any learnings written by previous executors on this epic:
```
Read: /Users/<you>/.claude/projects/<project-path>/memory/epic-<epic-id>-*.md
```
These files contain cross-task discoveries, gotchas, and decisions from prior executor runs. They are the knowledge bridge between executor lifetimes.

**Why this matters:** The lead holding epic context + project memory continuously is the core advantage. Each executor has a single-task lifetime, but learnings persist via memory.

## 2. Create Team and Spawn Executor (per-task model)

### 2a. Create the team (once per epic)

```
TeamCreate:
  team_name: "epic-<epic-id>"
  description: "Executing epic <epic-id>: <epic title>"
```

**If TeamCreate fails because team already exists:** Skip to resumption — the team is from a previous session. Check executor state and resume from Step 0 decision matrix.

**The team is created ONCE per epic and persists until epic closure (Step 5). Executors are spawned and shutdown within it, one per task.**

### 2b. Spawn executor for the specific task

Identify the specific task to execute (first ready task, or the task approved in the last completion message):

```bash
bd ready  # Find next ready task
```

Spawn the executor with a full prompt that includes all required context:

```
Task tool:
  subagent_type: "general-purpose"
  team_name: "epic-<epic-id>"
  name: "executor"
  mode: "bypassPermissions"
  prompt: |
    You are the executor agent. Execute tasks for epic <epic-id>.
    Follow the executor agent definition in agents/executor.md exactly.

    Your scope is task <task-id> ONLY. After completing it, send a
    Task Completion Report to the lead and wait for shutdown.

    Start with: bd show <epic-id>

    Then: bd show <task-id>

    Important context:
    - The lead's name in this team is: team-lead. Send ALL messages
      (progress, escalation, completion report) to "team-lead".
    - Read project memories matching epic-<epic-id>-* for cross-task
      learnings from prior tasks.
    - Send brief progress messages at TDD checkpoints: when you finish
      writing the failing test (RED), when the test passes (GREEN),
      after refactoring (REFACTOR), and after committing (COMMIT).
    - Before sending your completion report, write key learnings to
      project memory at the path shown in agents/executor.md, using
      filename: epic-<epic-id>-task-<task-id>-learnings.md
```

**After spawning:** Start your health monitoring timer. The first progress message (RED checkpoint) typically arrives within a few minutes as the executor reads the epic and writes the failing test.

## 3. Lead Orchestration Loop

Messages from the executor are auto-delivered to you. For each message, determine its type and respond:

**Start tracking time since last message from executor.** ANY message from the executor (progress, completion, escalation) resets the timer to 10 minutes.

### A) Progress Message (TDD Checkpoint)

The executor sends these brief signals at TDD checkpoints:

```
[RED] Writing failing test for <deliverable>
[GREEN] Test passing: <test name>
[REFACTOR] Cleanup complete, all tests green
[COMMIT] Committed: <short hash>: <message>
```

**Your response:**
- Reset your health check timer to 10 minutes
- No response required (executor continues autonomously)
- **Exception:** If a progress message reveals an anti-pattern violation (e.g., "GREEN: bypassed the database layer with mocks"), interject immediately:
  ```
  SendMessage:
    type: "message"
    recipient: "executor"
    content: "Stop — that approach violates [anti-pattern]. Do not proceed. [Correction]."
    summary: "Anti-pattern violation — stop and correct"
  ```

### B) Task Completion Message

The executor sends this after closing a task. Format:
```
## Task <id> Complete
### Done — [implementation summary]
### Commits — [hash: message]
### Learned — [discoveries]
### Changed from plan — [deviations]
### Proposed next task — [title, goal, approach, SRE refined]
```

**Your response process:**

0. **Verify commit hashes.** Check the executor's message for a `### Commits` section containing at least one entry in the format `<short hash>: <message>`. If the Commits section is missing, empty, or contains placeholder text instead of actual commit hashes, do NOT proceed to proposal validation — redirect the executor to commit first (see REDIRECT below for missing commits).

1. **Read the summary.** Note what was learned and what changed.

2. **Re-read the epic** to keep requirements fresh:
```bash
bd show <epic-id>
```

3. **Validate the proposed next task** against the epic. Check each of these:
   - Does it advance toward a success criterion? (Which one?)
   - Does it violate any anti-pattern? (Check each one explicitly.)
   - Does it touch any rejected approach from Design Discovery?
   - Is it consistent with the learnings reported?

4. **If proposal is valid → shutdown current executor and spawn fresh one for next task:**

   First, shutdown the current executor:
   ```
   SendMessage:
     type: "shutdown_request"
     recipient: "executor"
     content: "Task complete. Write your key learnings to project memory (epic-<epic-id>-task-<task-id>-learnings.md) before shutting down. Then confirm."
   ```
   Wait for shutdown_response with `approve: true`.

   Then create the next bd task and spawn fresh executor:
   ```bash
   bd create <next task title> --parent <epic-id>  # If task not yet in bd
   ```
   ```
   Task tool:
     subagent_type: "general-purpose"
     team_name: "epic-<epic-id>"
     name: "executor"
     mode: "bypassPermissions"
     prompt: |
       [same as 2b — include epic-id, task-id, memory path,
        single-task scope, progress message instruction,
        memory write instruction]
   ```

   **MODIFY** — Proposal is mostly valid but needs adjustment:
   Shutdown the current executor (as above), spawn fresh executor with modified task description:
   ```
   [In the spawn prompt, adjust the task description and include:]
   "Modified from executor's proposal: [specific modifications and reasoning]."
   ```

   **REDIRECT** — Proposal is invalid, do something different:
   Shutdown the current executor (as above), spawn fresh executor with the different task:
   ```
   [In the spawn prompt, describe the correct next task and include:]
   "Note: Lead redirected — original proposal was [reason]. Correct approach: [description]."
   ```

   **REDIRECT (missing commits)** — Executor did not commit before closing task:
   ```
   SendMessage:
     type: "message"
     recipient: "executor"
     content: "Task completion message is missing commit hashes. Commit all work for the task before I can evaluate your proposal. Send updated completion message with ### Commits section containing hash and message."
     summary: "Commit first — missing commit hashes"
   ```
   Do NOT shutdown or spawn next executor yet — wait for updated completion message with commits.

### C) Escalation Message

The executor sends this when hitting an obstacle that might violate epic requirements. Format:
```
## Escalation: [obstacle summary]
### Problem — [what's blocking]
### Epic context — [relevant anti-pattern or requirement]
### Options — [approaches with tradeoffs]
### My recommendation — [which option and why]
```

**Your response process:**

1. **Read the problem and options.**

2. **Re-read the epic** and specifically check Design Discovery:
```bash
bd show <epic-id>
```

3. **Check "Approaches Considered"** for any rejected approach the executor wants to try:
   - Find the "REJECTED BECAUSE" reasoning
   - Find the "DO NOT REVISIT UNLESS" conditions
   - Determine if revisit conditions are met

4. **If a rejected approach is being considered and revisit conditions are NOT met:**
   Reject it. Explain why the original rejection still applies.

5. **If a rejected approach is being considered and revisit conditions ARE met:**
   Present to the USER for confirmation before approving. Use AskUserQuestion:
   ```
   AskUserQuestion:
     "The executor hit [obstacle] and is considering [rejected approach].
      Original rejection: [reason]. Revisit condition: [condition].
      The condition appears met because [evidence]. Approve switching?"
   ```

6. **SendMessage to executor** with your decision and reasoning.

### D) Completion Report

The executor sends this when all success criteria appear met. Format:
```
## Epic Completion Report
### Success Criteria Status — [each criterion with evidence]
### Summary — [overview of entire implementation]
### Recommendation — Ready for review-implementation.
```

**Your response process:**

1. **Verify each criterion** in the report against the epic's actual success criteria.
2. **Spot-check the evidence** — does it make sense? Are any criteria missing?
3. If report looks complete → proceed to Step 4 (dispatch reviewer). The executor remains alive during reviewer dispatch (needed for gap fixes).
4. If report has gaps → SendMessage to executor with specific items to address.

### E) Health Check Protocol

**The executor MUST send progress messages at TDD checkpoints.** Absence of messages is a health signal, not normal idle behavior.

**Tier 1 — 10 minutes without any message (progress or otherwise):**

```
SendMessage:
  type: "message"
  recipient: "executor"
  content: "Progress check — what is your current status?"
  summary: "Health check — 10 min silence"
```

If executor responds → it is alive. Reset timer to 10 minutes. Continue waiting.

**Tier 2 — 5 minutes after Tier 1 with no response:**

Executor is assumed dead. Trigger recovery protocol (Step 3.F).

**Timer rules:**
- ANY message from executor (progress, completion, escalation) resets timer to 10 min
- Sending Tier 1 check starts a separate 5-min countdown for Tier 2
- Lead must NOT kill active executor based on elapsed time alone — a response to the health check means it is alive
- If SendMessage to executor errors or hangs (process gone): proceed directly to recovery without waiting for Tier 2

### F) Recovery Protocol

On assumed executor death (Tier 2 triggered or SendMessage error):

1. **Check git log** for recent executor commits:
```bash
git log --oneline -10
```

2. **Check bd task status:**
```bash
bd show <task-id>
```

3. **Check project memory** for any final learnings the executor may have written:
```
Read: /Users/<you>/.claude/projects/<project-path>/memory/epic-<epic-id>-task-<task-id>-learnings.md
```

4. **Determine recovery path:**

   - **IF committed passing code (task shows progress, tests pass):**
     Spawn fresh executor:
     ```
     [In spawn prompt, add:]
     "Previous executor died. Prior progress: [commits]. Continue task bd-<id> from where it left off. Review commits to understand current state, then continue with remaining items."
     ```

   - **IF committed failing code (commits exist but tests were failing):**
     Spawn fresh executor:
     ```
     [In spawn prompt, add:]
     "Previous executor died. Prior work has failing tests. Review commits [hashes], fix the failing tests, then continue with remaining task items."
     ```

   - **IF no commits (executor died before any work was saved):**
     Spawn fresh executor with standard task prompt (same as Step 2b).

5. **Lead NEVER implements during recovery.** Recovery means assessing state and respawning — not writing code.

## 4. Dispatch Reviewer

When the executor reports all success criteria met and you've verified the completion report:

**The executor remains alive during reviewer dispatch** — it may be needed to fix gaps found by the reviewer.

```
Task tool:
  subagent_type: "general-purpose"
  prompt: "You are the reviewer agent. Review the implementation for epic <epic-id>.
           Follow the reviewer agent definition in agents/reviewer.md exactly.
           Start with: bd show <epic-id>"
```

The reviewer is a **subagent** (no `team_name` parameter) — a one-shot analysis that returns its verdict directly in the Task tool output. It is NOT a teammate.

**Handle the verdict:**

**APPROVED:**
- Proceed to Step 5 (shutdown and present).

**GAPS FOUND:**
- Read the gaps list from the reviewer's output
- SendMessage to executor (still alive) with the specific gaps to fix:
  ```
  SendMessage:
    type: "message"
    recipient: "executor"
    content: "Reviewer found gaps. Fix these before we can close:
              [list gaps from reviewer verdict with evidence].
              After fixing, send updated completion report."
    summary: "Fix gaps from reviewer"
  ```
- Return to Step 3 (orchestration loop) and wait for executor's response.
- After executor fixes gaps and sends updated completion report, re-dispatch reviewer.

**If reviewer returns partial verdict** (context exhaustion on large epic):
- Check what was reviewed and what remains
- Re-dispatch reviewer for remaining tasks

## 5. Shutdown and Present (Epic End Only)

This step runs ONCE at epic end — after reviewer returns APPROVED. **Do not run per-task shutdown here; per-task shutdown is handled in Step 3.B.**

### 5a. Shut down the executor

```
SendMessage:
  type: "shutdown_request"
  recipient: "executor"
  content: "All success criteria met and reviewer approved. Write any final learnings to project memory before shutting down. Thank you."
```

Wait for the executor to confirm shutdown (shutdown_response with approve: true).

### 5b. Clean up the team

```
TeamDelete
```

### 5c. Present to user

Present the final status:

```markdown
## Epic <epic-id> — Implementation Complete

### Summary
[2-3 sentence overview from executor's completion report]

### Success Criteria
[Each criterion with status and evidence from completion report]

### Reviewer Verdict
APPROVED — [summary from reviewer]

### Next Step
Run `/hyperpowers:finish-branch` to close the epic and integrate.
```

</the_process>

<examples>

<example>
<scenario>Proper per-task flow: executor completes task, lead validates, shuts down executor, spawns fresh one for next task</scenario>

<code>
# Lead spawned executor for task bd-3. Executor sends progress messages:

Executor: "[RED] Writing failing test for user registration endpoint"
# Lead: timer reset to 10 min, no response needed

Executor: "[GREEN] Test passing: test_user_registration_returns_201"
# Lead: timer reset to 10 min, no response needed

Executor: "[REFACTOR] Cleanup complete, all tests green"
# Lead: timer reset to 10 min, no response needed

Executor: "[COMMIT] Committed: a1b2c3d: feat: implement user registration with bcrypt"
# Lead: timer reset to 10 min, no response needed

# Then executor sends task completion:
Executor: "## Task bd-3 Complete
### Done
- Implemented user registration endpoint with bcrypt password hashing
- Added input validation for email, password strength, username uniqueness

### Commits
- `a1b2c3d`: feat: implement user registration with bcrypt and input validation

### Learned
- The existing User model already has a `verified` field but no verification flow
- There's an unused email template system in lib/mailer.ts

### Changed from plan
- None — executed as planned

### Proposed next task
Title: Implement email verification flow
Goal: Add email verification using existing mailer system
Approach: Use lib/mailer.ts template system to send verification emails,
          add /verify endpoint, set User.verified on confirmation
SRE refined: yes
Key considerations: Token expiry (24h), rate limiting on resend,
                    idempotent verification (double-click safe)"
</code>

<why_it_works>
**Lead follows the per-task lifecycle correctly:**

1. Received progress messages throughout — health timer stayed fresh
2. Read summary — notes discovery about existing mailer system
3. Re-read epic: `bd show <epic-id>`
4. Validated proposal:
   - Advances success criterion "User registration with email verification" ✓
   - Uses existing code (lib/mailer.ts) — not adding new dependencies ✓
   - No anti-pattern violations ✓
   - Not touching any rejected approach ✓
   - SRE refined ✓
5. Noticed: epic Design Discovery mentions "rate limiting must use the existing RateLimiter middleware"
6. Shutdown current executor with memory write instruction:
```
SendMessage:
  type: "shutdown_request"
  recipient: "executor"
  content: "Task complete. Write your key learnings to project memory
            (epic-bxk-task-bd-3-learnings.md) before shutting down.
            Include: verified field exists on User, lib/mailer.ts is available."
```
7. After shutdown confirmed, spawned fresh executor for bd-4:
```
Task tool:
  team_name: "epic-bxk"
  name: "executor"
  prompt: "...Your scope is task bd-4 only...
           Read project memories matching epic-bxk-* for cross-task learnings.
           Modified from proposal: For rate limiting, use existing RateLimiter
           middleware from lib/middleware/rate-limiter.ts (Design Discovery
           constraint). Do not implement custom rate limiting..."
```

**Result:**
- Old executor context discarded — no accumulation
- Fresh executor starts clean with memory bridge
- Design Discovery constraint applied before spawn
- Lead preserved epic vision across executor boundary
</why_it_works>
</example>

<example>
<scenario>Lead detects executor death via health check and recovers</scenario>

<code>
# Lead spawned executor for task bd-5 at 14:00.
# Received "[RED] Writing failing test for payment processing" at 14:03.
# Timer reset. No further messages.

# At 14:13 (10 min since last message):
Lead sends health check:
SendMessage:
  type: "message"
  recipient: "executor"
  content: "Progress check — what is your current status?"
  summary: "Health check — 10 min silence"

# No response for 5 minutes (14:18).
# Executor assumed dead. Recovery protocol triggered.

# Step 1: Check git log
$ git log --oneline -5
# Output: no commits since executor was spawned

# Step 2: Check bd task status
$ bd show bd-5
# Status: in_progress (executor marked it, but no implementation commits)

# Step 3: Check project memory
# No epic-bxk-task-bd-5-learnings.md found (executor died before writing)

# Recovery path: no commits → standard restart
Lead spawns fresh executor for bd-5 with standard prompt.
New executor starts: "[RED] Writing failing test for payment processing"
</code>

<why_it_works>
**Lead used health check, not elapsed-time kill:**
- Sent status check at 10 min, not immediately killed on silence
- Waited 5 min for response before assuming dead
- Did NOT implement the payment feature directly during recovery
- Assessed git/bd/memory state before deciding recovery path
- Spawned fresh executor with standard prompt (no commits to recover from)
- Fresh executor starts with clean context, reads epic + project memory on startup

**Key:** Lead's monitoring preserved the recovery evidence. The health check protocol distinguished "working slowly" from "dead." Respawning, not implementing, is the correct recovery action.
</why_it_works>
</example>

<example>
<scenario>Lead validates escalation against Design Discovery before approving</scenario>

<code>
Executor escalates:
"## Escalation: Authentication library doesn't support OAuth2 PKCE
### Problem: passport.js v0.6 has no PKCE support
### Options:
A. Upgrade passport.js to v1.0 (breaking changes, 2 days)
B. Switch to custom JWT implementation (more control)
### My recommendation: Option B, custom JWT"

Lead thinks: "Executor knows the technical details, I'll just approve
their recommendation."

# WRONG — lead must check Design Discovery first.

# Correct process:
# 1. Re-read epic: bd show <epic-id>
# 2. Find "Approaches Considered" → Custom JWT
# 3. Check: "REJECTED BECAUSE: requires rewriting 15 files, security risk"
# 4. Check: "DO NOT REVISIT UNLESS: passport.js fully deprecated"
# 5. passport.js is not deprecated — just missing PKCE in v0.6
# 6. Revisit condition NOT met → reject Option B
</code>

<why_it_fails>
**Skipping Design Discovery on escalations loses the lead's core value:**
- Custom JWT was explicitly rejected during brainstorming
- Rejection reason still applies (15 file rewrite, security risk)
- Revisit condition NOT met (passport.js not deprecated, just missing one feature)
- Lead approved a previously rejected approach without realizing it
- Executor lacks Design Discovery context — that's exactly why they escalated
</why_it_fails>

<correction>
**Check Design Discovery on every escalation:**

```
SendMessage:
  type: "message"
  recipient: "executor"
  content: "Do NOT use custom JWT — it was rejected during design
            because it requires rewriting 15 files and introduces
            security risks. The revisit condition (passport.js
            fully deprecated) is not met.

            Instead, investigate Option A more carefully:
            - What specific breaking changes does passport.js v1.0 have?
            - Is there a v0.7 or v0.8 with PKCE but fewer breaking changes?
            - Can we use a passport.js PKCE plugin/middleware instead?

            Report findings before proceeding."
  summary: "Rejected custom JWT — checking alternatives"
```

**Result:** Rejected approach blocked. Design Discovery honored. Executor investigates better alternatives.
</correction>
</example>

</examples>

<critical_rules>

## Rules That Have No Exceptions

1. **Lead NEVER implements** → Only orchestrates via messages
   - No editing files, writing code, or running tests in lead context
   - Delegation is the entire point of this skill — even during recovery
   - "I can do it faster" = rationalization, not efficiency

2. **Validate EVERY proposal against epic** → No auto-approvals
   - Re-read epic before every approval decision
   - Check each anti-pattern explicitly
   - Check Design Discovery if proposal is near rejected approaches
   - Lead's value IS validation — skip it and lead is just a message relay

3. **Check Design Discovery for ALL escalations** → Never decide without context
   - Read "Approaches Considered" before approving alternatives
   - Check "REJECTED BECAUSE" and "DO NOT REVISIT UNLESS"
   - If rejected approach needed and conditions met: ask USER first, never decide alone
   - Executor escalates BECAUSE they lack this context — provide it

4. **Executor is spawned and shutdown PER TASK, not per epic** → Bounded lifecycle
   - Team persists; executor within it does not
   - Shutdown current executor before spawning next one
   - Each executor starts with clean context + project memory from prior runs
   - Context exhaustion is structurally impossible with this model

5. **Health monitoring is mandatory** → Silence is a signal, not normal behavior
   - Executor MUST send progress messages at TDD checkpoints
   - Start timer after every spawn; reset on ANY executor message
   - Send Tier 1 health check at 10 min silence — no exceptions
   - Send Tier 2 recovery at 5 min after Tier 1 with no response
   - Never kill active executor based on time alone — only kill on health check failure

6. **Executor writes project memory before every shutdown** → Memory is the knowledge bridge
   - Instruct executor to write memory in BOTH per-task shutdown (Step 3.B) and epic-end shutdown (Step 5a)
   - Memory filename: `epic-<epic-id>-task-<task-id>-learnings.md`
   - Next executor reads this memory on startup — it replaces in-context accumulation

7. **Reviewer is a subagent, not a teammate** → One-shot dispatch
   - No `team_name` parameter when dispatching reviewer
   - Reviewer returns verdict in Task tool output
   - Executor remains alive during reviewer dispatch (for gap fixes)

8. **Epic requirements are immutable** → Lead enforces this on all proposals
   - If executor proposes something that waters down a requirement: redirect
   - If executor escalates because a requirement is hard: research or ask user
   - Never approve a proposal that violates an anti-pattern

9. **Shutdown executor before TeamDelete** → Graceful, not abrupt
   - Send shutdown_request and wait for confirmation
   - TeamDelete runs ONCE at epic end, not per task
   - Abrupt cleanup leaves executor in undefined state

10. **One epic at a time** → Do not mix execution across epics
    - If multiple epics open: ask user which to execute
    - Team name includes epic ID to prevent confusion

## Common Excuses

All of these mean: follow the process, validate against epic, delegate to executor:

- "I already have context, I'll implement it directly" → Lead never implements. Spawn executor.
- "Executor knows what they're doing, I'll just approve" → Validate. Every. Time.
- "This escalation is clearly the right choice" → Check Design Discovery first. Always.
- "The reviewer is overkill for this small epic" → Dispatch reviewer. No exceptions.
- "I'll skip the team setup, just implement solo" → Hard commit to delegation. No solo mode.
- "Executor went silent, maybe it's just slow" → At 10 min, send health check. At 15 min, recover.
- "Let me just fix this one small thing myself" → Send it to the executor. Lead doesn't implement.
- "This requirement is unrealistic based on what executor found" → Requirements are immutable. Research or ask user.
- "I'll check on the executor in a bit" → 10 minutes. Not "a bit." Set a mental timer.
- "The executor must have written memory before dying" → Check the file. Don't assume.

</critical_rules>

<verification_checklist>

Before approving any proposal:
- [ ] Verified ### Commits section contains at least one actual commit hash
- [ ] Re-read epic (`bd show <epic-id>`)
- [ ] Checked proposal against each success criterion
- [ ] Checked proposal against each anti-pattern
- [ ] Checked Design Discovery if proposal is near rejected approaches
- [ ] Decision (approve/modify/redirect) documented in SendMessage

Before shutdown of per-task executor (Step 3.B):
- [ ] Instructed executor to write project memory before shutdown
- [ ] Received shutdown_response with approve: true
- [ ] Next task identified (approved proposal or redirect)
- [ ] Fresh executor spawned with correct prompt (epic ID, task ID, memory path, single-task scope)

Before dispatching reviewer:
- [ ] All success criteria reported as met by executor
- [ ] Evidence provided for each criterion
- [ ] No pending or in-progress tasks in bd (all closed)
- [ ] Completion report verified against actual epic criteria
- [ ] Executor is still alive (do NOT shutdown before reviewer dispatch)

Before epic-end shutdown (Step 5):
- [ ] Reviewer returned APPROVED verdict
- [ ] Instructed executor to write final learnings to project memory
- [ ] Shutdown_request sent to executor
- [ ] Executor confirmed shutdown (shutdown_response approve: true)
- [ ] TeamDelete called
- [ ] Final status presented to user

Health monitoring checklist:
- [ ] Timer started after each executor spawn
- [ ] Timer reset on every executor message (progress, completion, escalation)
- [ ] Tier 1 health check sent at 10 min silence
- [ ] Recovery protocol triggered if no response after 5 min (Tier 2)
- [ ] Recovery path chosen based on git/bd/memory state (not assumptions)

</verification_checklist>

<integration>

**This skill calls:**
- agents/executor.md (spawned as teammate via Task tool with `team_name` — fresh spawn PER TASK)
- agents/reviewer.md (dispatched as subagent via Task tool without `team_name`)

**Skills used by executor (not invoked by lead directly):**
- test-driven-development (executor follows TDD cycle)
- sre-task-refinement (executor refines proposed tasks before sending to lead)
- verification-before-completion (executor verifies before closing tasks)

**Skills used by reviewer (not invoked by lead directly):**
- testing-anti-patterns (reviewer checks test quality)
- verification-before-completion (reviewer requires evidence for claims)

**This skill is called by:**
- User (via /hyperpowers:execute-plan command)
- After brainstorming/writing-plans creates epic
- Explicitly to resume after context clear or new session

**Agents used:**
- executor (teammate — single-task lifetime, TDD discipline, progress messages at checkpoints, project memory write before shutdown)
- reviewer (subagent — one-shot verdict, APPROVED or GAPS FOUND, executor alive during dispatch)
- test-runner (used by executor internally for running tests — not invoked by lead)

**Workflow pattern:**
```
/hyperpowers:execute-plan
  → Load epic + project memory → Create team (once per epic)
  → Spawn executor for task-1
  → Executor works → sends progress messages → Lead resets timer
  → Executor sends completion → Lead validates → shuts down executor → executor writes memory
  → Lead spawns fresh executor for task-2 (reads memory on startup)
  → ...repeats until all criteria met...
  → Executor sends completion report → Lead dispatches reviewer (subagent)
  → [Executor remains alive for gap fixes]
  → If GAPS: executor fixes → re-review
  → If APPROVED: shutdown executor (writes final memory) → TeamDelete → present to user
  → User runs /hyperpowers:finish-branch to close epic and integrate
```

</integration>

<resources>

**bd command reference:**
- See [bd commands](../common-patterns/bd-commands.md) for complete command list

**Agent teams API tools:**
- TeamCreate — create team (one per epic, persists until epic end)
- Task tool with `team_name` + `name` — spawn executor teammate (PER TASK, not per epic)
- Task tool without `team_name` — spawn subagent (reviewer)
- SendMessage type: "message" — direct message to executor
- SendMessage type: "shutdown_request" — graceful executor shutdown (per task and epic end)
- TeamDelete — cleanup at epic end only

**Project memory:**
- Path: `/Users/<you>/.claude/projects/<project-path>/memory/`
- Naming: `epic-<epic-id>-task-<task-id>-learnings.md`
- Format: frontmatter with `type: project` + learnings content
- Written by executor before each shutdown; read by each new executor on startup

**When stuck:**
- Executor not responding → Check health (Tier 1 at 10 min). If no response (Tier 2 at 15 min), trigger recovery protocol.
- Executor dead mid-task → Check git/bd/memory → respawn with recovery context (lead never implements)
- Reviewer returns GAPS → Send gap details to executor (still alive), return to orchestration loop
- Escalation about rejected approach → Check Design Discovery, ask USER if revisit conditions met
- Multiple epics open → Ask user which to execute
- TeamCreate fails → Team already exists from previous session. Skip to resumption.
- Multiple in-progress tasks in bd → Close all but most recently updated, spawn executor for that one
- Old long-running executor detected → Send shutdown_request, confirm memory write, resume with per-task model

</resources>
