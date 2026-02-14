---
name: executing-plans
description: Use to execute bd tasks via agent teams delegation - lead orchestrates from main context, executor teammate implements with TDD, reviewer subagent verifies. No manual /clear cycling needed.
---

<skill_overview>
Lead orchestrates execution via agent teams. Spawns a single executor teammate for implementation, receives structured summaries after each task, validates proposals against epic requirements and anti-patterns, dispatches reviewer subagent for final verification. The lead preserves epic context and cross-task learnings continuously — no manual /clear cycling needed. Epic requirements are immutable, tasks adapt to reality.
</skill_overview>

<rigidity_level>
LOW FREEDOM - Follow exact orchestration process. Lead never implements directly — only orchestrates via messages. Epic requirements are immutable.

Do not skip proposal validation, reviewer dispatch, or shutdown protocol. Do not implement code in the lead context. Do not auto-approve proposals without checking the epic.
</rigidity_level>

<quick_reference>

| Step | Action | Tool/Command |
|------|--------|--------------|
| **Load Epic** | Read immutable requirements | `bd show <epic-id>` |
| **Create Team** | Initialize team for this epic | TeamCreate |
| **Spawn Executor** | Start executor teammate | Task tool with `team_name` and `name` params |
| **Receive Summary** | Read executor's structured report | Auto-delivered message (no action needed) |
| **Validate Proposal** | Check against epic requirements/anti-patterns | `bd show <epic-id>` + systematic check |
| **Approve** | Tell executor to proceed | SendMessage type: "message" |
| **Redirect** | Tell executor to change course | SendMessage type: "message" with modified task |
| **Handle Escalation** | Decide on obstacle | Check Design Discovery + SendMessage |
| **Dispatch Reviewer** | Final verification | Task tool (subagent, no `team_name`) |
| **Shutdown** | Terminate executor | SendMessage type: "shutdown_request" |
| **Cleanup** | Remove team | TeamDelete |

**Critical:** Lead orchestrates, executor implements. Epic = contract (immutable). Lead's value = validation against epic on every proposal.

</quick_reference>

<when_to_use>
**Use after hyperpowers:writing-plans creates epic and first task.**

Symptoms you need this:
- bd epic exists with tasks ready to execute
- Need to implement features iteratively with TDD
- Requirements clear, but implementation path will adapt
- Want continuous cross-task learning without context exhaustion
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

**Decision matrix:**

| Team exists? | Executor state | bd state | Action |
|-------------|---------------|----------|--------|
| No | N/A | No in-progress tasks | Fresh start → Step 1 |
| No | N/A | In-progress task exists | Fresh start → Step 1 (executor will resume from bd) |
| Yes | Idle | Tasks remain | Resume → SendMessage to executor to continue |
| Yes | Active | Tasks remain | Resume → Wait for executor's next message |
| Yes or No | N/A | All tasks closed, epic open | Skip to Step 4 (reviewer dispatch) |

**If multiple epics are open:** Ask the user which epic to execute (use AskUserQuestion). One team per epic, one epic at a time.

**Do not ask "where did we leave off?"** — bd state and team state tell you exactly where to resume.

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

**Why this matters:** The lead holding this context continuously is the core advantage over the old solo mode. You never lose the epic vision or cross-task learnings.

## 2. Create Team and Spawn Executor

### 2a. Create the team

```
TeamCreate:
  team_name: "epic-<epic-id>"
  description: "Executing epic <epic-id>: <epic title>"
```

**If TeamCreate fails because team already exists:** Skip to resumption — the team is from a previous session. Check executor state and resume from Step 0 decision matrix.

### 2b. Spawn the executor

```
Task tool:
  subagent_type: "general-purpose"
  team_name: "epic-<epic-id>"
  name: "executor"
  mode: "bypassPermissions"
  prompt: "You are the executor agent. Execute tasks for epic <epic-id>.
           Follow the executor agent definition in agents/executor.md exactly.
           Start with: bd show <epic-id>"
```

The executor will:
1. Read the epic from bd
2. Find the first ready task
3. Execute it with TDD (red-green-refactor-commit)
4. Send you a structured task completion message
5. Wait for your approval before continuing

**After spawning:** Wait for the executor's first message. It will arrive automatically.

## 3. Lead Orchestration Loop

Messages from the executor are auto-delivered to you. You do not need to poll or check — they appear as new conversation turns. For each message, determine its type and respond:

### A) Task Completion Message

The executor sends this after closing a task. Format:
```
## Task <id> Complete
### Done — [implementation summary]
### Learned — [discoveries]
### Changed from plan — [deviations]
### Proposed next task — [title, goal, approach, SRE refined]
```

**Your response process:**

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

4. **Decide and respond** via SendMessage to the executor:

   **APPROVE** — Proposal is valid, proceed as described:
   ```
   SendMessage:
     type: "message"
     recipient: "executor"
     content: "Approved. Proceed with proposed task as described."
     summary: "Approved proposed task"
   ```

   **MODIFY** — Proposal is mostly valid but needs adjustment:
   ```
   SendMessage:
     type: "message"
     recipient: "executor"
     content: "Approved with changes: [specific modifications and reasoning]. Proceed with these adjustments."
     summary: "Approved with modifications"
   ```

   **REDIRECT** — Proposal is invalid, do something different:
   ```
   SendMessage:
     type: "message"
     recipient: "executor"
     content: "Do not proceed with proposed task. Instead: [different task description with rationale referencing epic requirements]."
     summary: "Redirected to different task"
   ```

### B) Escalation Message

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

### C) Completion Report

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
3. If report looks complete → proceed to Step 4 (dispatch reviewer).
4. If report has gaps → SendMessage to executor with specific items to address.

### Handling Idle Notifications

**The executor going idle after sending a message is completely normal.** This is standard agent teams behavior — the executor sends its message and waits for your response. Do NOT:
- Treat idle as an error
- Send "are you still there?" messages
- Interpret idle as the executor being done

Simply process the executor's most recent message and respond when ready.

## 4. Dispatch Reviewer

When the executor reports all success criteria met and you've verified the completion report:

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
- SendMessage to executor with the specific gaps to fix:
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

**If reviewer returns partial verdict** (context exhaustion on large epic):
- Check what was reviewed and what remains
- Re-dispatch reviewer for remaining tasks

## 5. Shutdown and Present

After reviewer returns APPROVED:

### 5a. Shut down the executor

```
SendMessage:
  type: "shutdown_request"
  recipient: "executor"
  content: "All success criteria met and reviewer approved. Shutting down. Thank you."
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
<scenario>Lead implements directly instead of delegating to executor</scenario>

<code>
Executor sends task completion message with proposed next task.

Lead thinks: "I already have context on this codebase, I'll just
implement the next feature directly. It'll be faster than waiting
for the executor to do it."

Lead starts writing code, editing files, running tests in main context.
</code>

<why_it_fails>
**Violates core principle — lead orchestrates, never implements:**
- Lead context fills with implementation verbosity
- Cross-task learnings get pushed out of context
- Epic requirements and Design Discovery get compressed
- Lead loses ability to validate future proposals
- Defeats the entire purpose of the delegation model

**Why it happens:** "I can do it faster" rationalization. But speed
isn't the goal — context preservation is. The lead's job is holding
the big picture, not writing code.
</why_it_fails>

<correction>
**Lead validates the proposal and delegates:**

1. Re-read epic: `bd show <epic-id>`
2. Check proposed task against requirements and anti-patterns
3. If valid:
```
SendMessage:
  type: "message"
  recipient: "executor"
  content: "Approved. Proceed with proposed task as described."
  summary: "Approved proposed task"
```

**Result:** Lead preserves context. Executor implements with TDD.
Each role does what it's designed for.
</correction>
</example>

<example>
<scenario>Lead auto-approves executor's proposal without checking epic</scenario>

<code>
Executor sends:
"## Task bd-5 Complete
### Proposed next task
Title: Add caching layer with Redis
Goal: Improve API response times
Approach: Add Redis caching to all endpoints"

Lead thinks: "Sounds reasonable, executor knows what they're doing."

SendMessage: "Approved. Proceed."

# But epic anti-patterns say:
# "FORBIDDEN: Adding external dependencies (Redis, Memcached)
#  without explicit user approval. Use in-memory caching only."
</code>

<why_it_fails>
**Skipped proposal validation — lead's core responsibility:**
- Epic explicitly forbids adding Redis without user approval
- Lead approved a task that violates an anti-pattern
- Executor will implement something that must be reverted
- Time wasted on forbidden approach
- Lead's value is validation — without it, lead is just a message relay

**Why it happens:** Trust in executor + desire to move fast.
But the executor doesn't have the lead's continuous epic context.
That's precisely why validation exists.
</why_it_fails>

<correction>
**Systematic validation before every approval:**

1. Re-read epic: `bd show <epic-id>`
2. Check anti-patterns:
   - "Adding external dependencies without user approval" — Redis is external
   - VIOLATION DETECTED
3. Redirect the executor:
```
SendMessage:
  type: "message"
  recipient: "executor"
  content: "Do not proceed with Redis caching. Epic anti-pattern
            forbids external dependencies without user approval.
            Instead: propose an in-memory caching approach
            (e.g., LRU cache in the application process)."
  summary: "Redirected — Redis violates anti-pattern"
```

**Result:** Anti-pattern caught. Executor redirected to valid approach.
Epic requirements preserved.
</correction>
</example>

<example>
<scenario>Lead dismisses escalation without checking Design Discovery</scenario>

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

SendMessage: "Go with Option B, custom JWT."

# But Design Discovery says:
# "Custom JWT was REJECTED BECAUSE it requires rewriting 15 files
#  and introduces security risks from hand-rolled crypto.
#  DO NOT REVISIT UNLESS passport.js is fully deprecated."
</code>

<why_it_fails>
**Dismissed escalation without checking Design Discovery:**
- Custom JWT was explicitly rejected during brainstorming
- Rejection reason still applies (15 file rewrite, security risk)
- Revisit condition NOT met (passport.js not deprecated, just missing one feature)
- Lead approved a previously rejected approach without realizing it
- Executor lacks the Design Discovery context — that's why they escalated

**Why it happens:** Deferring to executor's technical judgment. But
escalations exist specifically because the lead holds design context
the executor doesn't have.
</why_it_fails>

<correction>
**Check Design Discovery on every escalation:**

1. Re-read epic: `bd show <epic-id>`
2. Find "Approaches Considered" → Custom JWT
3. Check: "REJECTED BECAUSE: requires rewriting 15 files, security risk"
4. Check: "DO NOT REVISIT UNLESS: passport.js fully deprecated"
5. passport.js is not deprecated — just missing PKCE in v0.6
6. Revisit condition NOT met → reject Option B
7. Research Option A more carefully:
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

**Result:** Rejected approach blocked. Design Discovery honored.
Executor investigates better alternatives.
</correction>
</example>

<example>
<scenario>Proper end-to-end flow: executor completes task, lead validates and modifies</scenario>

<code>
# Executor sends task completion:

"## Task bd-3 Complete
### Done
- Implemented user registration endpoint with bcrypt password hashing
- Added input validation for email, password strength, username uniqueness

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
**Lead follows the full validation process:**

1. Read summary — notes discovery about existing mailer system
2. Re-read epic: `bd show <epic-id>`
3. Validate proposal:
   - Advances success criterion "User registration with email verification" ✓
   - Uses existing code (lib/mailer.ts) — not adding new dependencies ✓
   - No anti-pattern violations ✓
   - Not touching any rejected approach ✓
   - SRE refined ✓
4. But notice: epic Design Discovery mentions "rate limiting must use
   the existing RateLimiter middleware, not custom implementation"
5. Modify proposal to include this constraint:

```
SendMessage:
  type: "message"
  recipient: "executor"
  content: "Approved with one modification: For rate limiting on
            resend, use the existing RateLimiter middleware from
            lib/middleware/rate-limiter.ts (per Design Discovery
            constraint). Do not implement custom rate limiting.
            Proceed with this adjustment."
  summary: "Approved with rate limiter constraint"
```

**Result:**
- Proposal validated against all epic requirements
- Design Discovery constraint caught and applied
- Executor proceeds with correct constraints
- Lead preserves cross-task learning (mailer system, rate limiter)
</why_it_works>
</example>

</examples>

<critical_rules>

## Rules That Have No Exceptions

1. **Lead NEVER implements** → Only orchestrates via messages
   - No editing files, writing code, or running tests in lead context
   - Delegation is the entire point of this skill
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

4. **Reviewer is a subagent, not a teammate** → One-shot dispatch
   - No `team_name` parameter when dispatching reviewer
   - Reviewer returns verdict in Task tool output
   - Do not add reviewer to the team

5. **Epic requirements are immutable** → Lead enforces this on all proposals
   - If executor proposes something that waters down a requirement: redirect
   - If executor escalates because a requirement is hard: research or ask user
   - Never approve a proposal that violates an anti-pattern

6. **Shutdown executor before TeamDelete** → Graceful, not abrupt
   - Send shutdown_request and wait for confirmation
   - Then call TeamDelete
   - Abrupt cleanup leaves executor in undefined state

7. **Idle executor = normal** → Do not treat as error
   - Executor goes idle after every message — this is expected
   - Do not send "are you still there?" messages
   - Simply process the executor's message and respond when ready

8. **One epic at a time** → Do not mix execution across epics
   - If multiple epics open: ask user which to execute
   - Team name includes epic ID to prevent confusion

## Common Excuses

All of these mean: follow the process, validate against epic, delegate to executor:

- "I already have context, I'll implement it directly" → Lead never implements. SendMessage to executor.
- "Executor knows what they're doing, I'll just approve" → Validate. Every. Time.
- "This escalation is clearly the right choice" → Check Design Discovery first. Always.
- "The reviewer is overkill for this small epic" → Dispatch reviewer. No exceptions.
- "I'll skip the team setup, just implement solo" → Hard commit to delegation. No solo mode.
- "Executor went idle, something must be wrong" → Idle is normal. Read their last message.
- "Let me just fix this one small thing myself" → Send it to the executor. Lead doesn't implement.
- "This requirement is unrealistic based on what executor found" → Requirements are immutable. Research or ask user.

</critical_rules>

<verification_checklist>

Before approving any proposal:
- [ ] Re-read epic (`bd show <epic-id>`)
- [ ] Checked proposal against each success criterion
- [ ] Checked proposal against each anti-pattern
- [ ] Checked Design Discovery if proposal is near rejected approaches
- [ ] Decision (approve/modify/redirect) documented in SendMessage

Before dispatching reviewer:
- [ ] All success criteria reported as met by executor
- [ ] Evidence provided for each criterion
- [ ] No pending or in-progress tasks in bd (all closed)
- [ ] Completion report verified against actual epic criteria

Before shutting down:
- [ ] Reviewer returned APPROVED verdict
- [ ] Shutdown_request sent to executor
- [ ] Executor confirmed shutdown (shutdown_response approve: true)
- [ ] TeamDelete called
- [ ] Final status presented to user

</verification_checklist>

<integration>

**This skill calls:**
- agents/executor.md (spawned as teammate via Task tool with `team_name`)
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
- executor (teammate — persistent context, continuous work, TDD discipline)
- reviewer (subagent — one-shot verdict, APPROVED or GAPS FOUND)
- test-runner (used by executor internally for running tests — not invoked by lead)

**Workflow pattern:**
```
/hyperpowers:execute-plan
  → Load epic → Create team → Spawn executor
  → Executor works → sends structured summary → Lead validates → approves/modifies/redirects
  → ...repeats until all criteria met...
  → Lead dispatches reviewer (subagent) → APPROVED or GAPS FOUND
  → If GAPS: send to executor for fixes, re-review
  → If APPROVED: shutdown executor → TeamDelete → present to user
  → User runs /hyperpowers:finish-branch to close epic and integrate
```

</integration>

<resources>

**bd command reference:**
- See [bd commands](../common-patterns/bd-commands.md) for complete command list

**Agent teams API tools:**
- TeamCreate — create team (one per epic)
- Task tool with `team_name` + `name` — spawn teammate (executor)
- Task tool without `team_name` — spawn subagent (reviewer)
- SendMessage type: "message" — direct message to executor
- SendMessage type: "shutdown_request" — graceful shutdown
- TeamDelete — cleanup after shutdown

**When stuck:**
- Executor not responding → Check if team exists and executor is idle. If idle, SendMessage to continue. If team gone, respawn.
- Reviewer returns GAPS → Send gap details to executor, return to orchestration loop
- Escalation about rejected approach → Check Design Discovery, ask USER if revisit conditions met
- Multiple epics open → Ask user which to execute
- TeamCreate fails → Team already exists from previous session. Skip to resumption.
- Executor goes idle → Normal. Process their last message and respond.

</resources>
