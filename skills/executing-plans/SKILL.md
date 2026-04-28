---
name: executing-plans
description: Lead validates task proposals against bd epic requirements. Fresh executor subagent per task. Native TaskCreate for progress. Project memory bridges cross-task learnings.
---

<skill_overview>
Lead orchestrates execution by validating proposals against the epic. Dispatches a fresh executor subagent per task, validates every executor return value against requirements and anti-patterns, dispatches reviewer subagent for final verification. Project memory bridges cross-task learnings — executor writes discoveries before returning, next executor reads them on startup. Epic requirements are immutable.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — Validation protocol is rigid (always check epic on every proposal, always check Design Discovery on escalations). Agent lifecycle is blocking (lead waits for each executor subagent to return). Use judgment on orchestration details, never on validation steps.

Do not skip proposal validation, Design Discovery checks, reviewer dispatch, or memory bridge. Do not implement code in the lead context. Do not auto-approve proposals.
</rigidity_level>

<quick_reference>

| Step | Action | How |
|------|--------|-----|
| **Load Epic** | Read requirements + project memory | `bd show <epic-id>` + read memory files |
| **Dispatch Executor** | Start fresh executor subagent for ONE task | Agent tool (blocking subagent dispatch) |
| **Validate Proposal** | Check against epic requirements/anti-patterns | `bd show <epic-id>` + 5-item checklist |
| **Handle Escalation** | Check Design Discovery before deciding | `bd show <epic-id>` + Approaches Considered |
| **Completion Gate** | Verify criteria + dispatch reviewer | Agent tool (blocking subagent dispatch) |

**Critical:** Executor is dispatched per task as a blocking subagent. The Agent tool call blocks until the executor returns — lead stays actively computing (no idle throttling). Each executor reads project memory on startup.

</quick_reference>

<when_to_use>
**Use after hyperpowers:writing-plans creates epic and first task.**

Symptoms you need this:
- bd epic exists with tasks ready to execute
- Need to implement features iteratively with TDD
- Want cross-task learnings bridged via project memory without context exhaustion

If invoked mid-epic: read `bd list --status in_progress` and project memory files matching `epic-<epic-id>-*` to determine where work left off. Dispatch executor for the current or next ready task.
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

## 2. Dispatch Executor

Dispatch a fresh executor subagent for the specific task using this exact briefing template:

```
Agent tool:
  subagent_type: "hyperpowers:executor"
  mode: "bypassPermissions"
  prompt: |
    You are the executor agent. Execute task <task-id> in epic <epic-id>.

    Your scope is task <task-id> ONLY. After completing it, output a
    structured completion report (Status: COMPLETE) as your final response.

    Start with: bd show <epic-id>
    Then: bd show <task-id>

    Important context:
    - Read project memories matching epic-<epic-id>-* for cross-task
      learnings from prior tasks.
    - Use TaskCreate to track your TDD sub-steps (RED/GREEN/REFACTOR/COMMIT).
    - The completion report MUST be one of three envelopes: COMPLETE, ESCALATION,
      or CONTEXT_LIMIT — see "Final Output Contract" section at the top of
      agents/executor.md. Do NOT run hyperpowers:sre-task-refinement; the lead
      runs it on your proposal before dispatching the next executor.
    - Before outputting your completion report, write key learnings to
      project memory using filename: epic-<epic-id>-task-<task-id>-learnings.md
    - If you hit an escalation trigger, commit partial work, write partial
      memory, and return immediately with Status: ESCALATION output.
```

The Agent tool blocks until the executor returns its structured output. Parse the `## Status:` header from the return value to determine next action.

## 3. Validate Proposals

### 3a. On Task Completion Report (Status: COMPLETE)

Executor returns structured output as the Agent tool result:
```
## Status: COMPLETE

### Task: <id>
### Done — [summary]
### Commits — [hash: message]
### Learned — [discoveries]
### Changed from plan — [deviations]
### Proposed next task — [title, goal, approach]
```

**Validation process:**

0. **Verify commits first.** Check for a `### Commits` section with at least one actual commit hash. If missing or placeholder text: dispatch a fresh executor for the same task, including in the prompt that a commit is required before returning COMPLETE. Do NOT evaluate proposal until commits are present.

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
   - **APPROVE** — Dispatch fresh executor for next task using briefing template.
   - **MODIFY** — Dispatch fresh executor with adjusted task description. Note what was modified and why in the prompt.
   - **REDIRECT** — Dispatch fresh executor with a different task. Note why proposal was rejected in the prompt.

4. **Run SRE refinement on the approved proposed task before dispatch.**

   If the decision is APPROVE or MODIFY:

   ```
   Use Skill tool: hyperpowers:sre-task-refinement
   ```

   Run on the proposed task description. Apply refinement findings to the next-executor dispatch prompt — pass corner cases as additional context. (This responsibility was moved from executor to lead because running heavy analytical skills in the executor's late-life context caused format drift in completion reports — see bd-0he.)

### 3b. Handling ESCALATION Return

Executor returns ESCALATION when blocked by a trigger condition. Parse the Problem, Options, and Recommendation sections.

**Response process:**

1. Re-read the epic (`bd show <epic-id>`).
2. Check **Approaches Considered** for any rejected approach the executor wants to try.
3. If revisit conditions are **NOT met**: reject, explain why original rejection still applies.
4. If revisit conditions **ARE met**: present to USER via AskUserQuestion before approving — never decide alone.
5. Dispatch fresh executor subagent for the SAME task with decision in prompt:
   ```
   Prompt addition: Prior executor escalated: [problem]. Lead decision: [decision].
   Prior commits: [hashes from escalation output]. Read project memory for partial learnings.
   ```

### 3c. Handling CONTEXT_LIMIT Return

Executor returns CONTEXT_LIMIT when approaching context exhaustion. Parse the checkpoint info from the return value.

**Response process:**

1. Note what is committed and what remains from the return value.
2. Dispatch fresh executor subagent for the SAME task with checkpoint context in prompt:
   ```
   Prompt addition: Prior executor hit context limit. Progress: [committed work from return value].
   Remaining: [unchecked sub-steps from return value]. Read project memory for partial learnings.
   ```

## 4. Completion Gate

When executor COMPLETE output indicates all success criteria met:

1. Verify each criterion in the report against the epic's actual success criteria.
2. Spot-check evidence — does it make sense? Are any criteria missing?
3. Dispatch reviewer as a **blocking subagent**:
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
Dispatch fresh executor subagent for the SAME task with gap details in prompt:
```
Prompt addition: Reviewer found gaps. Fix these items: [gap list]. Prior commits: [hashes].
Task is already closed in bd — run bd update <task-id> --status in_progress before fixing gaps.
```
Wait for updated COMPLETE output, then re-dispatch reviewer.

## 5. Memory Bridge

Before completing each task, the executor writes a learnings file to project memory:
- **Filename:** `epic-<epic-id>-task-<task-id>-learnings.md`
- **Location:** `/Users/<you>/.claude/projects/<project-path>/memory/`
- **Format:** frontmatter with `type: project` + learnings content
- **What to include:** unexpected constraints, rejected approaches confirmed/ruled out, design decisions affecting future tasks, gotchas for next executor
- **What NOT to include:** code patterns derivable from reading code, git log summaries, ephemeral session state

Each new executor reads these files on startup — they are the cross-task knowledge bridge. Brief the executor on this in the dispatch prompt (already in the template above).

</the_process>

<examples>

<example>
<scenario>Completion report validation and fresh executor dispatch</scenario>
<code>
Agent tool returns:
"## Status: COMPLETE
### Task: bd-3
### Commits: a1b2c3d: feat: implement user registration
### Learned: lib/mailer.ts exists but has no verification flow
### Proposed next task: Implement email verification flow"

Lead:
1. Commits present ✓
2. bd show <epic-id>
3. Five-item check: advances "email verification" criterion ✓, no anti-pattern violations ✓,
   no rejected approaches ✓, consistent with learnings ✓, scope appropriate ✓
4. Design Discovery note: rate limiting must use RateLimiter middleware → include in dispatch prompt

Dispatches fresh executor subagent for bd-4 with constraint in prompt.
</code>
</example>

<example>
<scenario>Escalation: executor returns rejected approach</scenario>
<code>
Agent tool returns:
"## Status: ESCALATION
### Task: bd-5
### Problem: passport.js has no PKCE support
### Options: A. Upgrade to v1.0  B. Custom JWT
### Recommendation: B"

Lead checks Design Discovery → Custom JWT: REJECTED BECAUSE rewriting 15 files + security risk.
DO NOT REVISIT UNLESS passport.js fully deprecated. Not deprecated → reject Option B.

Dispatches fresh executor for bd-5 with prompt addition:
"Do NOT use custom JWT — rejected during design (15 file rewrite, security risk). Revisit condition
not met. Investigate Option A: breaking changes in v1.0? PKCE plugin available?"
</code>
</example>

</examples>

<critical_rules>

1. **Lead NEVER implements** — Only orchestrates via validation and dispatching. Even during recovery: assess state and re-dispatch, never write code.

2. **Validate EVERY proposal against epic** — Re-read epic before every approval. Check each anti-pattern individually. Check Design Discovery for proposals near rejected approaches.

3. **Check Design Discovery for ALL escalations** — Read "Approaches Considered" before approving alternatives. If rejected approach + conditions met: ask USER via AskUserQuestion, never decide alone.

4. **Executor dispatched per task** — Fresh context per task. Each executor returns structured output, lead dispatches next. Read project memory on startup.

5. **Memory bridge is mandatory** — Executor writes learnings before returning. Brief executor on this in dispatch prompt. Next executor reads these files.

6. **Reviewer is a blocking subagent** — Dispatch as subagent (no team parameter). One-shot verdict returned in Agent tool output.

7. **Epic requirements are immutable** — Redirect any proposal that waters down a requirement. Research or ask user when a requirement seems impossible — never soften it.

8. **One epic at a time** — If multiple epics open: ask user which to execute.

9. **Executor MUST be dispatched as blocking subagent** — Using the team dispatch mode causes the Agent tool to return immediately, leaving the lead idle and vulnerable to throttling. Blocking dispatch (no team parameter) keeps the lead actively computing between tasks.

10. **Run SRE refinement at lead-side, not executor-side** — When approving a proposed next task, run hyperpowers:sre-task-refinement before dispatching the next executor. The refinement adds corner-case context to the dispatch prompt. Never expect the executor to run SRE on its own proposal; that responsibility is the lead's. (Established by bd-6uw fix for bd-0he format drift.)

## Common Rationalizations

- "I'll implement this small thing directly" → Lead never implements. Dispatch executor.
- "Executor knows best, I'll just approve" → Validate every time. Re-read epic.
- "This escalation is clearly right" → Check Design Discovery first.
- "Reviewer is overkill here" → Dispatch reviewer. No exceptions.
- "This requirement is unrealistic" → Immutable. Research or ask user.
- "This is a single-task epic, blocking dispatch seems unnecessary" → Dispatch blocking subagent. Consistent dispatch model prevents idle throttling on every epic.
- "I'll use team dispatch, it's fine for this one" → No. Team dispatch causes idle throttling. Always dispatch as a blocking subagent.
- "The executor already ran SRE on this proposal" → As of bd-6uw (fix for bd-0he), executors don't run SRE. Lead runs it on approved proposals before dispatch.

</critical_rules>

<verification_checklist>

Before approving any proposal:
- [ ] Verified ### Commits section contains at least one actual commit hash
- [ ] Re-read epic (`bd show <epic-id>`)
- [ ] Checked proposal against each success criterion
- [ ] Checked proposal against each anti-pattern
- [ ] Checked Design Discovery if proposal is near rejected approaches
- [ ] Decision (approve/modify/redirect) noted with reasoning
- [ ] Ran SRE refinement on the approved proposed task before dispatching next executor

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

**Calls:** agents/executor.md (subagent, blocking, fresh per task) · agents/reviewer.md (subagent, blocking)

**Called by:** User via /hyperpowers:execute-plan · after brainstorming/writing-plans

**Flow:** Load epic → Dispatch executor subagent (blocks until return) → Parse Status → Validate COMPLETE → Dispatch fresh executor → ... → Reviewer gate → Present → /hyperpowers:finish-branch

**bd command reference:** See [bd commands](../common-patterns/bd-commands.md)

**Project memory:** `/Users/<you>/.claude/projects/<project-path>/memory/` · `epic-<epic-id>-task-<task-id>-learnings.md`

**When stuck:**
- Executor subagent timed out → Re-dispatch for same task with prompt: 'Prior executor timed out. Check git log and bd show for progress. Continue from where they left off.'
- Reviewer GAPS → Re-dispatch executor subagent with gap list in prompt (include bd task reopen instruction)
- Escalation about rejected approach → Check Design Discovery, ask USER if revisit conditions met
- Resume mid-epic → `bd list --status in_progress` + project memory → dispatch executor

</integration>
