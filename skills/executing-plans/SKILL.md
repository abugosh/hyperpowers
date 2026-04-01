---
name: executing-plans
description: Lead validates task proposals against bd epic requirements. Fresh executor per task. Native TaskCreate for progress. Project memory bridges cross-task learnings.
---

<skill_overview>
Lead orchestrates execution by validating proposals against the epic. Spawns a fresh executor teammate per task, validates every completion message against requirements and anti-patterns, dispatches reviewer subagent for final verification. Project memory bridges cross-task learnings — executor writes discoveries before completing, next executor reads them on startup. Epic requirements are immutable.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — Validation protocol is rigid (always check epic on every proposal, always check Design Discovery on escalations). Agent lifecycle is native (Claude Code manages teams, executors idle out naturally). Use judgment on orchestration details, never on validation steps.

Do not skip proposal validation, Design Discovery checks, reviewer dispatch, or memory bridge. Do not implement code in the lead context. Do not auto-approve proposals.
</rigidity_level>

<quick_reference>

| Step | Action | How |
|------|--------|-----|
| **Load Epic** | Read requirements + project memory | `bd show <epic-id>` + read memory files |
| **Spawn Executor** | Start fresh executor for ONE task | Agent tool with `team_name` and `name` params |
| **Validate Proposal** | Check against epic requirements/anti-patterns | `bd show <epic-id>` + 5-item checklist |
| **Handle Escalation** | Check Design Discovery before deciding | `bd show <epic-id>` + Approaches Considered |
| **Completion Gate** | Verify criteria + dispatch reviewer | Agent tool (no `team_name`) |

**Critical:** Executor is spawned per task, not per epic. Old executor idles out naturally — no explicit shutdown needed.

</quick_reference>

<when_to_use>
**Use after hyperpowers:writing-plans creates epic and first task.**

Symptoms you need this:
- bd epic exists with tasks ready to execute
- Need to implement features iteratively with TDD
- Want cross-task learnings bridged via project memory without context exhaustion

If invoked mid-epic: read `bd list --status in_progress` and project memory files matching `epic-<epic-id>-*` to determine where work left off. Spawn executor for the current or next ready task.
</when_to_use>

<the_process>

## 1. Load Epic Context

```bash
bd list --type epic --status open  # Find epic
bd show <epic-id>                  # Load epic details
bd ready                           # Find first task
```

**Extract and hold for the entire session:**
- **Requirements** — IMMUTABLE. Never water down.
- **Success Criteria** — Your validation checklist for every proposal.
- **Anti-Patterns** — FORBIDDEN. Reject any proposal that violates these.
- **Design Discovery** — Reference context for obstacle decisions and escalations.
- **Approaches Considered** — Especially rejected approaches and "DO NOT REVISIT UNLESS" conditions.

**Read project memory** for learnings from prior executors on this epic:
```
Read: /Users/<you>/.claude/projects/<project-path>/memory/epic-<epic-id>-*.md
```

If multiple epics open: ask the user which to execute (AskUserQuestion). One epic at a time.

## 2. Spawn Executor

**The executor MUST be spawned as a teammate in a team (Agent tool with `team_name`), not as a standalone subagent.** Standalone dispatch is fire-and-forget — no mid-flight escalation, no proposal validation, no correction channel. The team model exists because executors hit obstacles, need direction, and should not grade their own work. This applies even for single-task epics.

Spawn a fresh executor for the specific task using this exact briefing template:

```
Agent tool:
  subagent_type: "hyperpowers:executor"
  team_name: "epic-<epic-id>"
  name: "executor"
  mode: "bypassPermissions"
  prompt: |
    You are the executor agent. Execute task <task-id> in epic <epic-id>.

    Your scope is task <task-id> ONLY. After completing it, send a
    Task Completion Report to the lead and wait.

    Start with: bd show <epic-id>
    Then: bd show <task-id>

    Important context:
    - The lead's name in this team is: team-lead. Send ALL messages
      (progress, escalation, completion report) to "team-lead".
    - Read project memories matching epic-<epic-id>-* for cross-task
      learnings from prior tasks.
    - Use TaskCreate to track your TDD sub-steps (RED/GREEN/REFACTOR/COMMIT).
    - Before sending your completion report, write key learnings to
      project memory using filename: epic-<epic-id>-task-<task-id>-learnings.md
```

If the spawned name differs from "executor" (e.g. "executor-2"): use the actual assigned name for all SendMessage calls. No workaround needed — just track it.

## 3. Validate Proposals

### 3a. On Task Completion Report

Executor sends completion reports in this format:
```
## Task <id> Complete
### Done — [summary]
### Commits — [hash: message]
### Learned — [discoveries]
### Changed from plan — [deviations]
### Proposed next task — [title, goal, approach]
```

**Validation process:**

0. **Verify commits first.** Check for a `### Commits` section with at least one actual commit hash. If missing or placeholder text: send message to executor requesting commit before proceeding. Do NOT evaluate proposal until commits are present.

1. **Re-read the epic:**
```bash
bd show <epic-id>
```

2. **Validate proposed next task — check ALL five:**
   1. Does it advance toward a specific success criterion? (Which one?)
   2. Does it violate ANY anti-pattern? (Check each one individually.)
   3. Does it touch a rejected approach from Design Discovery? If yes, check "DO NOT REVISIT UNLESS" conditions.
   4. Is it consistent with the learnings reported?
   5. Is scope appropriate? (Not too broad, not trivially small.)

3. **Decide:**
   - **APPROVE** — Spawn fresh executor for next task using briefing template. Old executor idles out naturally.
   - **MODIFY** — Spawn fresh executor with adjusted task description. Note what was modified and why in the prompt.
   - **REDIRECT** — Spawn fresh executor with a different task. Note why proposal was rejected in the prompt.

### 3b. On Escalation

**Response process:**

1. Re-read the epic (`bd show <epic-id>`).
2. Check **Approaches Considered** for any rejected approach the executor wants to try.
3. If revisit conditions are **NOT met**: reject, explain why original rejection still applies.
4. If revisit conditions **ARE met**: present to USER via AskUserQuestion before approving — never decide alone.
5. SendMessage to executor with decision and reasoning.

### 3c. On Progress Message

Executor uses native TaskCreate/TaskUpdate for TDD sub-step tracking. No response required unless a message reveals an anti-pattern violation — then interject immediately via SendMessage.

## 4. Completion Gate

When executor reports all success criteria met:

1. Verify each criterion in the report against the epic's actual success criteria.
2. Spot-check evidence — does it make sense? Are any criteria missing?
3. Dispatch reviewer as **subagent** (no `team_name`):
```
Agent tool:
  subagent_type: "hyperpowers:reviewer"
  prompt: "Review implementation for epic <epic-id>.
           Follow agents/reviewer.md exactly.
           Start with: bd show <epic-id>"
```

**Handle the verdict:**

**APPROVED:**
Present final status to user and hand off to `/hyperpowers:finish-branch`.

**GAPS FOUND:**
Send gap details to executor via SendMessage with specific items to fix. Wait for updated completion report, then re-dispatch reviewer.

## 5. Memory Bridge

Before completing each task, the executor writes a learnings file to project memory:
- **Filename:** `epic-<epic-id>-task-<task-id>-learnings.md`
- **Location:** `/Users/<you>/.claude/projects/<project-path>/memory/`
- **Format:** frontmatter with `type: project` + learnings content
- **What to include:** unexpected constraints, rejected approaches confirmed/ruled out, design decisions affecting future tasks, gotchas for next executor
- **What NOT to include:** code patterns derivable from reading code, git log summaries, ephemeral session state

Each new executor reads these files on startup — they are the cross-task knowledge bridge. Brief the executor on this in the spawn prompt (already in the template above).

</the_process>

<examples>

<example>
<scenario>Completion report validation and fresh executor spawn</scenario>
<code>
Executor: "## Task bd-3 Complete
### Commits: a1b2c3d: feat: implement user registration
### Learned: lib/mailer.ts exists but has no verification flow
### Proposed next task: Implement email verification flow"

Lead:
1. Commits present ✓
2. bd show <epic-id>
3. Five-item check: advances "email verification" criterion ✓, no anti-pattern violations ✓,
   no rejected approaches ✓, consistent with learnings ✓, scope appropriate ✓
4. Design Discovery note: rate limiting must use RateLimiter middleware → include in spawn prompt

Spawns fresh executor for bd-4 with constraint in prompt. Old executor idles out naturally.
</code>
</example>

<example>
<scenario>Escalation: executor proposes rejected approach</scenario>
<code>
Executor: "## Escalation: passport.js has no PKCE support
### Options: A. Upgrade to v1.0  B. Custom JWT
### Recommendation: B"

Lead checks Design Discovery → Custom JWT: REJECTED BECAUSE rewriting 15 files + security risk.
DO NOT REVISIT UNLESS passport.js fully deprecated. Not deprecated → reject Option B.

SendMessage: "Do NOT use custom JWT — rejected during design (15 file rewrite, security risk).
Revisit condition not met. Investigate Option A: breaking changes in v1.0? PKCE plugin available?"
</code>
</example>

</examples>

<critical_rules>

1. **Lead NEVER implements** — Only orchestrates via validation and spawning. Even during recovery: assess state and respawn, never write code.

2. **Validate EVERY proposal against epic** — Re-read epic before every approval. Check each anti-pattern individually. Check Design Discovery for proposals near rejected approaches.

3. **Check Design Discovery for ALL escalations** — Read "Approaches Considered" before approving alternatives. If rejected approach + conditions met: ask USER via AskUserQuestion, never decide alone.

4. **Executor spawned per task** — Fresh context per task. Old executor idles out naturally — no shutdown needed. Each executor reads project memory on startup.

5. **Memory bridge is mandatory** — Executor writes learnings before completing each task. Brief executor on this in spawn prompt. Next executor reads these files.

6. **Reviewer is a subagent, not a teammate** — No `team_name` on reviewer dispatch. One-shot verdict returned in Agent tool output.

7. **Epic requirements are immutable** — Redirect any proposal that waters down a requirement. Research or ask user when a requirement seems impossible — never soften it.

8. **One epic at a time** — If multiple epics open: ask user which to execute.

9. **Team-based dispatch is mandatory** — Do NOT use the Agent tool without `team_name` to dispatch executors. Standalone dispatch (fire-and-forget) removes mid-flight escalation, proposal validation, and correction channels. Even for single-task epics, the team model is required — executors hit obstacles and should not grade their own work.

## Common Rationalizations

- "I'll implement this small thing directly" → Lead never implements. Spawn executor.
- "Executor knows best, I'll just approve" → Validate every time. Re-read epic.
- "This escalation is clearly right" → Check Design Discovery first.
- "Reviewer is overkill here" → Dispatch reviewer. No exceptions.
- "This requirement is unrealistic" → Immutable. Research or ask user.
- "This is a single-task epic, I don't need a team" → Yes you do. Teams enable escalation, mid-flight correction, and reviewer dispatch.
- "I'll just use the Agent tool directly, it's simpler" → Standalone dispatch is fire-and-forget. No escalation channel, no correction, no reviewer. Use team_name.

</critical_rules>

<verification_checklist>

Before approving any proposal:
- [ ] Verified ### Commits section contains at least one actual commit hash
- [ ] Re-read epic (`bd show <epic-id>`)
- [ ] Checked proposal against each success criterion
- [ ] Checked proposal against each anti-pattern
- [ ] Checked Design Discovery if proposal is near rejected approaches
- [ ] Decision (approve/modify/redirect) noted with reasoning

Before dispatching reviewer:
- [ ] All success criteria reported as met by executor
- [ ] Evidence provided for each criterion
- [ ] No pending or in-progress tasks in bd
- [ ] Completion report verified against actual epic criteria

After reviewer APPROVED:
- [ ] Final status presented to user
- [ ] Handed off to /hyperpowers:finish-branch

</verification_checklist>

<integration>

**Calls:** agents/executor.md (teammate, `team_name`, fresh per task) · agents/reviewer.md (subagent, no `team_name`)

**Called by:** User via /hyperpowers:execute-plan · after brainstorming/writing-plans

**Flow:** Load epic → Spawn executor (uses TaskCreate for TDD sub-steps) → Validate completion → Spawn fresh executor → ... → Reviewer gate → Present → /hyperpowers:finish-branch

**bd command reference:** See [bd commands](../common-patterns/bd-commands.md)

**Project memory:** `/Users/<you>/.claude/projects/<project-path>/memory/` · `epic-<epic-id>-task-<task-id>-learnings.md`

**When stuck:**
- Executor not responding → Check git/bd for prior progress, spawn fresh executor for same task
- Reviewer GAPS → SendMessage gap list to executor, wait for fixes, re-dispatch reviewer
- Escalation about rejected approach → Check Design Discovery, ask USER if revisit conditions met
- Resume mid-epic → `bd list --status in_progress` + project memory → spawn executor

</integration>
