---
name: writing-plans
description: Use when bd tasks exist without complete self-contained specs — expands or repairs specs (gap-fix tasks, mid-flight amendments, externally created tasks) with codebase verification.
---

<skill_overview>
Expand or repair bd task specs into the self-contained two-tier format. Each task is classified as simple or medium (time bands: skills/common-patterns/pipeline-constants.md) and written with enough detail that an executor can implement it with zero prior context. Every spec includes a Why section — so the executor understands how the task fits into the epic.

The standard flow is brainstorm-owned: Step 6c creates the complete task tree with codebase-verified specs upfront. This skill is the off-mainline utility for tasks that bypassed that flow or need their specs repaired — reviewer gap-fix tasks, mid-flight spec amendments, and tasks created outside the brainstorm flow.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM - Follow task-by-task validation pattern, use codebase-investigator for verification.

Adapt implementation details to actual codebase state. Never use placeholders or meta-references.
</rigidity_level>

<quick_reference>

| Step | Action | Critical Rule |
|------|--------|---------------|
| **Identify Scope** | Single task, range, or full epic | No artificial limits |
| **Classify** | Simple or Medium (bands: skills/common-patterns/pipeline-constants.md) | No task exceeds the ceiling in skills/common-patterns/pipeline-constants.md |
| **Verify Codebase** | Investigator for broad questions; direct reads for exact edit sites | Never write unverified references |
| **Draft Spec** | Use two-tier format for the task's tier | Must include Why section; medium must include Boundaries |
| **Present to User** | Show COMPLETE expansion FIRST | Then ask for approval |
| **Update bd** | `bd update bd-N --design "..."` | Only after user approves |
| **Continue** | Move to next task automatically | NO asking permission between tasks |

**FORBIDDEN:** Placeholders like `[Full implementation steps as detailed above]`
**REQUIRED:** Actual content per the spec-depth rule (skills/common-patterns/pipeline-constants.md) — intent — goal, constraints, test cases, verification commands, boundaries; complete code only where this session verified the exact site

</quick_reference>

<when_to_use>
**Use when bd tasks exist without complete self-contained specs — not as the standard planning step.** The standard flow is brainstorm-owned: Step 6c creates the complete task tree with codebase-verified specs before any execution begins. Reach for this skill when a task bypassed that flow or its spec needs repair.

Symptoms:
- Executing-plans startup verification found tasks missing specs (routed here before execution begins)
- A mid-flight amendment changes a task's scope after brainstorming closed
- A task was created outside the brainstorm flow (directly by the user, or by another tool) and lacks Why, Changes, or Boundaries sections
- An existing spec references context not included in the task itself

</when_to_use>

<the_process>

## 1. Identify Tasks to Expand

**User specifies scope:**
- Single: "Expand bd-2"
- Range: "Expand bd-2 through bd-5"
- Epic: "Expand all tasks in bd-1"

**If epic:**
```bash
bd dep tree bd-1  # View complete dependency tree
# Note all child task IDs
```

**Track progress in bd when the repo uses beads; TodoWrite otherwise:**
```
- [ ] bd-2: [Task Title]
- [ ] bd-3: [Task Title]
...
```

## 2. For EACH Task (Loop Until All Done)

### 2a. Mark In Progress and Read Current State

```bash
# Mark in the tracker: in_progress
bd show bd-3  # Read current task design
```

### 2b. Classify the Task

Time bands and the hard ceiling are defined in skills/common-patterns/pipeline-constants.md — cite that file rather than restating the numbers.

**Simple:** Mechanical changes with exact known edits. No judgment required.
- Renaming a term across files
- Adding a config value
- Updating a doc section
- Adding a small standalone function with a known signature

**Medium:** Changes requiring judgment or design decisions. Reserved for irreducible complexity.
- New component or skill
- Cross-file refactor
- Implementation with design decisions
- Any task with a Tests section

**No task should exceed the hard ceiling in skills/common-patterns/pipeline-constants.md.** If a task feels larger, flag it for splitting before expanding. For irreducibly hard tasks within the ceiling, the `Executor: opus` promotion flag is available — see skills/common-patterns/pipeline-constants.md.

### 2c. Verify Codebase State

**CRITICAL: Never write unverified references.** Two lanes: broad structure questions (does a pattern already exist, the shape of a directory, dependency presence) → dispatch `codebase-investigator`. Exact edit sites you are about to write into a spec → read the file directly first — a direct read is ground-truth verification, not assumption. Never assume in either lane.

Mechanical existence-verification like this may run on a cheap model — pass model haiku explicitly in the dispatch rather than inheriting silently.

**Provide agent with bd assumptions:**
```
Assumptions from bd-3:
- Auth service should be in src/services/auth.ts with login() and logout()
- User model in src/models/user.ts with email and password fields
- Test file at tests/services/auth.test.ts
- Uses bcrypt dependency for password hashing

Verify these assumptions and report:
1. What exists vs what bd-3 expects
2. Structural differences (different paths, functions, exports)
3. Missing or additional components
4. Current dependency versions
```

**Based on investigator report:**
- ✓ Confirmed assumptions → Use in implementation
- ✗ Incorrect assumptions → Adjust plan to match reality
- + Found additional → Document and incorporate

**NEVER write conditional steps:**
❌ "Update `index.js` if exists"
❌ "Modify `config.py` (if present)"

**ALWAYS write definitive steps:**
✅ "Create `src/auth.ts`" (investigator confirmed doesn't exist)
✅ "Modify `src/index.ts:45-67`" (investigator confirmed exists)

### 2d. Draft the Task Spec (Two-Tier Format)

Use the template for the task's tier from `skills/common-patterns/spec-templates.md` — the single source for both tiers (simple: Goal, Why, Changes, Verification; medium: Goal, Why, Context, Implementation, Tests, Verification, Boundaries). Both tiers REQUIRE a Why section. The canonical medium field name is `## Implementation`. Do not restate or improvise the templates here.

---

### 2e. Present COMPLETE Expansion to User

**CRITICAL: Show the full expansion BEFORE asking for approval.**

**Format:**
```markdown
**bd-[N]: [Task Title]** (simple / medium)

**Codebase verification findings:**
- ✓ Confirmed: [what matched]
- ✗ Incorrect: [what issue said] - ACTUALLY: [reality]
- + Found: [unexpected discoveries]

**Expanded spec:**
[Full spec using two-tier template for the task's tier]
```

When pausing at this approval gate, emit the gate-state block and persist it to the task's (or its epic's) bd notes (format: `skills/common-patterns/loop-interfaces.md`) — the approval must be answerable in durable prose whenever the user returns.

**THEN ask for approval using AskUserQuestion:**
- Question: "Is this expansion approved for bd-[N]?"
- Options:
  - "Approved - continue to next task"
  - "Needs revision"
  - "Other"

### 2f. If Approved: Update bd and Continue

```bash
bd update bd-3 --design "[paste complete expansion]"
# Mark completed in the tracker
# IMMEDIATELY continue to next task (NO asking permission)
```

### 2g. If Needs Revision: Iterate

- Keep as in_progress in the tracker
- Revise based on feedback
- Present again (step 2e)

## 3. After ALL Tasks Done

```
All repaired/expanded tasks now have self-contained two-tier specs.
Ready for execution.
```

**Offer next step:**
"Ready to proceed? I can optionally have the repaired spec(s) reviewed, then use hyperpowers:executing-plans to implement."

If the user opts into review, dispatch it as a fresh subagent — this session repaired the specs, so the review must come from a context that did not:

```
Agent tool:
  subagent_type: "general-purpose"
  mode: "bypassPermissions"
  prompt: |
    Load the skill hyperpowers:sre-task-refinement with the Skill tool and
    run its SINGLE-TASK MODE against <task-id(s)>. You may strengthen the
    spec via bd update (no placeholders). Return your findings and any
    updates applied.
```

Do not pass a model override — the review inherits the session model.

</the_process>

<examples>

<example>
<scenario>Developer writes a task spec without a Why section or Boundaries section</scenario>

<code>
bd update bd-3 --design "## Goal
Add logout() function to src/services/auth.ts

## Implementation
### Step 1: Write failing test
[test code]

### Step 2: Implement logout()
[implementation code]

## Verification
pytest tests/auth/"
</code>

<why_it_fails>
**Missing Why section:**
- Executor has zero context on why this task exists
- Executor cannot judge "is this change locally correct but globally wrong?"
- Without Boundaries, executor may refactor auth.ts broadly while implementing logout()

**Missing Boundaries section (medium task):**
- Executor implements logout(), then "helpfully" also refactors login() it sees along the way
- Drift compounds across tasks
</why_it_fails>

<correction>
**Write the complete two-tier spec:**

```bash
bd update bd-3 --design "## Goal
Add logout() function to src/services/auth.ts

## Why
The executing-plans skill dispatches a fresh executor per task. Session cleanup depends on this function existing before the session-management task (bd-5) runs. Without it, bd-5 will fail.

## Context
- src/services/auth.ts — exists, has login() at line 12. logout() does not exist yet.
- tests/auth/test_auth.test.ts — existing test file for this service
- argon2 (0.31.2) is installed; no new dependencies needed

## Implementation

### Step 1: Write failing test
# tests/auth/test_auth.test.ts — add at end of file:
it('logs out a user by clearing the session token', async () => {
  const result = await logout('valid-token-123');
  expect(result.success).toBe(true);
});

### Step 2: Run to confirm RED
npx jest tests/auth/test_auth.test.ts
# Expected: TypeError: logout is not a function

### Step 3: Implement logout()
# src/services/auth.ts — add after login() at line 28:
export async function logout(token: string): Promise<{ success: boolean }> {
  await db.sessions.delete({ where: { token } });
  return { success: true };
}

### Step 4: Run to confirm GREEN
npx jest tests/auth/test_auth.test.ts
# Expected: 3 passed

## Tests
tests/auth/test_auth.test.ts — must assert logout clears the session token

## Verification
npx jest tests/auth/test_auth.test.ts

## Boundaries
- Do NOT refactor login() — that is out of scope
- Do NOT add token validation logic — that is bd-4's responsibility
- Do NOT modify session schema — that is bd-5's responsibility"
```

**Result:** Executor knows why the task exists, what not to touch, and can implement without any other context.
</correction>
</example>

<example>
<scenario>Developer assumes codebase state instead of verifying it in either lane</scenario>

<code>
Developer skims and assumes:
- Glances at src/services/auth.ts without reading the cited lines
- Guesses at package.json contents
- Assumes file structure from a quick look

Writes expansion based on assumption:
"Modify src/services/auth.ts (if exists)"
</code>

<why_it_fails>
**Assumption problems:**
- Misses nuances (existing functions, imports, structure)
- Creates conditional steps ("if exists")
- Doesn't catch version mismatches
- Doesn't report discrepancies from bd assumptions

**Result:** Implementation plan may not match actual codebase state.
</why_it_fails>

<correction>
**Use codebase-investigator agent:**

```
Dispatch agent with bd-3 assumptions:
"bd-3 expects auth service in src/services/auth.ts with login() and logout() functions.
Verify:
1. Does src/services/auth.ts exist?
2. What functions does it export?
3. How do login() and logout() work currently?
4. Any other relevant auth code?
5. What's the bcrypt version?"
```

**Agent reports:**
```
✓ src/services/auth.ts exists
✗ ONLY has login() function - NO logout() yet
+ Found: login() uses argon2 NOT bcrypt
+ Found: Session management in src/services/session.ts
✓ argon2 version: 0.31.2
```

**Write definitive steps based on findings:**
```
Step 1: Add logout() function to EXISTING src/services/auth.ts:45-67
(no "if exists" - investigator confirmed location)

Step 2: Use argon2 (already installed 0.31.2) not bcrypt
(no assumption - investigator confirmed actual dependency)
```

**Result:** Plan matches actual codebase state. (The other lane: for the exact lines a spec will cite — e.g. "add after login() at line 28" — read the file directly before writing the step; a direct read is ground-truth, not assumption.)
</correction>
</example>

<example>
<scenario>Developer asks permission between each task validation instead of continuing automatically</scenario>

<code>
After user approves bd-3 expansion:

Developer: "bd-3 expansion approved and updated in bd.
Should I continue to bd-4 now? What's your preference?"

[Waits for user response]
</code>

<why_it_fails>
**Breaks workflow momentum:**
- Unnecessary interruption
- User has to respond multiple times
- Slows down batch processing
- The tracker list IS the plan

**Why it happens:** Over-asking for permission instead of executing the plan.
</why_it_fails>

<correction>
**After user approves bd-3:**

```bash
bd update bd-3 --design "[expansion]"  # Update bd
# Mark completed in the tracker
```

**IMMEDIATELY continue to bd-4:**
```bash
bd show bd-4  # Read next task
# Dispatch codebase-investigator with bd-4 assumptions
# Draft expansion
# Present bd-4 expansion to user
```

**NO asking:** "Should I continue?" or "What's your preference?"

**ONLY ask user:**
1. When presenting each task expansion for validation
2. At the VERY END after ALL tasks done to offer execution choice

**Between validations: JUST CONTINUE.**

**Result:** Efficient batch processing of all tasks.
</correction>
</example>

</examples>

<critical_rules>

## Rules That Have No Exceptions

1. **No placeholders or meta-references** → Write actual content
   - ❌ FORBIDDEN: `[Full implementation steps as detailed above]`
   - ✅ REQUIRED: Intent per the spec-depth rule (skills/common-patterns/pipeline-constants.md) — goal, constraints, test cases, verification commands, boundaries; complete code only where this session verified the exact site; exact paths and real commands always

2. **Every task spec must include a Why section** → Executor must understand purpose
   - Simple tasks: Why explains what breaks if this task is skipped
   - Medium tasks: Why explains what depends on this task and its role in the epic

3. **Every medium task spec must include a Boundaries section** → Prevents scope creep
   - List explicitly what is out of scope for this task
   - Prevents executor from doing "just a little more"

4. **Effort estimates in minutes, not hours** → No task exceeds the hard ceiling in skills/common-patterns/pipeline-constants.md
   - Simple and Medium time bands are defined in skills/common-patterns/pipeline-constants.md — cite it, don't restate the numbers
   - If a task feels larger than the ceiling: flag it for splitting, do not expand it

5. **Never write unverified references** → Broad questions go to codebase-investigator; exact edit sites get read directly before the spec names them
   - Agent gets bd assumptions and reports discrepancies
   - Direct reads confirm the exact lines a spec will cite
   - You adjust plan to match reality

6. **Present COMPLETE expansion before asking** → User must SEE before approving
   - Show full expansion in message text
   - Then use AskUserQuestion for approval
   - Never ask without showing first

7. **Continue automatically between validations** → Don't ask permission
   - The tracker list IS your plan
   - Execute it completely
   - Only ask: (a) task validation, (b) final next-step offer

8. **Write definitive steps** → Never conditional
   - ❌ "Update `index.js` if exists"
   - ✅ "Create `src/auth.ts`" (investigator confirmed)

## Common Excuses

All of these mean: Stop, apply the rule:
- "I'll add the details later" → Write actual content now
- "The Why is obvious" → Write it anyway; executor has zero context
- "Boundaries is implied" → Write explicit Boundaries section for medium tasks
- "This will take longer than the ceiling" → Flag for splitting, do not expand (ceiling defined in skills/common-patterns/pipeline-constants.md)

</critical_rules>

<verification_checklist>

Before marking each task complete in the tracker:
- [ ] Task classified as simple or medium
- [ ] Verified per the split-lane rule: investigator for broad questions, direct reads for exact edit sites — no unverified references
- [ ] Spec uses correct two-tier template for classification
- [ ] Spec includes Why section (both tiers)
- [ ] Medium spec includes Boundaries section
- [ ] Effort estimate is in minutes, per the bands in skills/common-patterns/pipeline-constants.md, not hours
- [ ] Presented COMPLETE expansion to user (showed full text)
- [ ] User approved expansion (via AskUserQuestion)
- [ ] Updated bd with actual content (no placeholders)
- [ ] No meta-references in design field

Before finishing all tasks:
- [ ] All tasks marked completed in the tracker
- [ ] All bd tasks updated with two-tier specs
- [ ] No task exceeds the hard ceiling in skills/common-patterns/pipeline-constants.md
- [ ] No conditional steps ("if exists")
- [ ] Complete code only where this session verified the exact site; intent (constraints, test cases, verification commands, boundaries) elsewhere
- [ ] Exact file paths and commands throughout

</verification_checklist>

<integration>

**This skill calls:**
- codebase-investigator (broad structure questions during task verification; exact edit sites are read directly per the split-lane rule)

**This skill is called by:**
- hyperpowers:executing-plans (startup routing only — spec-less tasks found during startup verification, before execution begins; mid-flight gap-fixes are authored inline by the lead per executing-plans' GAPS FOUND path, because this skill's per-expansion approval gate must not interrupt the execution loop)
- hyperpowers:managing-bd-tasks (tasks split, merged, or otherwise mutated outside the brainstorm flow)
- The user directly (via /hyperpowers:write-plan command) — for tasks created outside the brainstorm flow, or specs needing repair

**After this skill:**
- Optionally dispatch a fresh subagent to run hyperpowers:sre-task-refinement in single-task mode against the repaired spec (see the dispatch block in section 3)
- Then use hyperpowers:executing-plans to implement

**Agents used:**
- hyperpowers:codebase-investigator (verify assumptions, report discrepancies)

</integration>

<resources>

**Detailed guidance:**
- [bd command reference](../common-patterns/bd-commands.md)
- [Task structure examples](resources/task-examples.md) (if exists)

**When stuck:**
- Unsure about file structure → Dispatch codebase-investigator (broad lane)
- Don't know version → Dispatch codebase-investigator (broad lane)
- About to cite an exact line or symbol → Read the file directly first (surgical lane)
- Tempted to write "if exists" → Verify in the appropriate lane, then write the definitive step
- About to write placeholder → Stop, write actual content
- Want to ask permission → Check: Is this task validation or final choice? If neither, don't ask

</resources>
