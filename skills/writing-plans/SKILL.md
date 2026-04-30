---
name: writing-plans
description: Use to expand bd tasks into self-contained two-tier specs (simple/Haiku 2-10 min or medium/Sonnet 10-30 min) with exact file paths, complete code, verification commands
---

<skill_overview>
Expand bd tasks into self-contained two-tier specs. Each task is classified as simple (2-10 min, Haiku) or medium (10-30 min, Sonnet) and written with enough detail that an executor can implement it with zero prior context. Every spec includes a Why section — so the executor understands how the task fits into the epic.

The task tree is created upfront by brainstorming. This skill expands the specs, it does not create the task tree.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM - Follow task-by-task validation pattern, use codebase-investigator for verification.

Adapt implementation details to actual codebase state. Never use placeholders or meta-references.
</rigidity_level>

<quick_reference>

| Step | Action | Critical Rule |
|------|--------|---------------|
| **Identify Scope** | Single task, range, or full epic | No artificial limits |
| **Classify** | Simple (2-10 min) or Medium (10-30 min) | No task exceeds 30 min |
| **Verify Codebase** | Use `codebase-investigator` agent | NEVER verify yourself, report discrepancies |
| **Draft Spec** | Use two-tier format for the task's tier | Must include Why section; medium must include Boundaries |
| **Present to User** | Show COMPLETE expansion FIRST | Then ask for approval |
| **Update bd** | `bd update bd-N --design "..."` | Only after user approves |
| **Continue** | Move to next task automatically | NO asking permission between tasks |

**FORBIDDEN:** Placeholders like `[Full implementation steps as detailed above]`
**REQUIRED:** Actual content - complete code, exact paths, real commands

</quick_reference>

<when_to_use>
**Use after brainstorming creates the task tree (and optionally after SRE batch review).**

Symptoms:
- bd tasks exist but need self-contained specs
- Tasks lack Why, Changes, or Boundaries sections
- Specs reference context not included in the task itself

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

**Create TodoWrite tracker:**
```
- [ ] bd-2: [Task Title]
- [ ] bd-3: [Task Title]
...
```

## 2. For EACH Task (Loop Until All Done)

### 2a. Mark In Progress and Read Current State

```bash
# Mark in TodoWrite: in_progress
bd show bd-3  # Read current task design
```

### 2b. Classify the Task

**Simple (2-10 min, Haiku):** Single-file or mechanical changes with exact known edits. No judgment required.
- Renaming a term across files
- Adding a config value
- Updating a doc section
- Adding a small standalone function with a known signature

**Medium (10-30 min, Sonnet):** Multi-file changes or changes requiring judgment.
- New component or skill
- Cross-file refactor
- Implementation with design decisions
- Any task with a Tests section

**No task should exceed 30 minutes.** If a task feels larger, flag it for splitting before expanding.

### 2c. Verify Codebase State

**CRITICAL: Use codebase-investigator agent, NEVER verify yourself.**

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

Use the template for the task's tier. Both tiers REQUIRE a Why section.

---

**Simple task spec template (2-10 min, Haiku):**

```markdown
## Goal
[One sentence: what changes]

## Why
[How this task fits into the epic — what breaks if it is skipped]

## Changes
- `exact/path/to/file.ext` line N: [exact change, complete replacement text]
- `exact/path/to/other.ext`: [add/remove/replace what]

## Verification
[Exact command to confirm the change is correct, e.g. grep, test run, or manual check]
```

---

**Medium task spec template (10-30 min, Sonnet):**

```markdown
## Goal
[One sentence: what is delivered]

## Why
[How this task fits into the epic — what depends on it, what breaks if skipped]

## Context
[Key files, functions, or patterns the executor must read before starting]

## Implementation guidance
[Step-by-step: what to create/modify/delete, with exact file paths and complete code]

For new features (TDD):
1. Write the failing test
2. Run to confirm RED
3. Implement minimal code
4. Run to confirm GREEN
5. Refactor, keep green

Include in each step:
- Exact file path
- Complete code example (not pseudo-code)
- Exact command to run
- Expected output

## Tests
[Which tests to write and what they must assert — omit this section for pure-documentation tasks]

## Verification
[Exact commands to confirm all success criteria]

## Boundaries
[What is explicitly out of scope for this task]
```

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

**THEN ask for approval using AskUserQuestion:**
- Question: "Is this expansion approved for bd-[N]?"
- Options:
  - "Approved - continue to next task"
  - "Needs revision"
  - "Other"

### 2f. If Approved: Update bd and Continue

```bash
bd update bd-3 --design "[paste complete expansion]"
# Mark completed in TodoWrite
# IMMEDIATELY continue to next task (NO asking permission)
```

### 2g. If Needs Revision: Iterate

- Keep as in_progress in TodoWrite
- Revise based on feedback
- Present again (step 2e)

## 3. After ALL Tasks Done

```
All bd tasks now have self-contained two-tier specs.
Epic ready for SRE batch review and execution.
```

**Offer next step:**
"Ready to proceed? I can run hyperpowers:sre-task-refinement in batch mode against the full plan, then use hyperpowers:executing-plans to implement."

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

## Implementation guidance

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
<scenario>Developer verifies codebase state themselves instead of using codebase-investigator agent</scenario>

<code>
Developer reads files manually:
- Reads src/services/auth.ts directly
- Checks package.json manually
- Assumes file structure based on quick look

Writes expansion based on quick check:
"Modify src/services/auth.ts (if exists)"
</code>

<why_it_fails>
**Manual verification problems:**
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

**Result:** Plan matches actual codebase state.
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
- TodoWrite list IS the plan

**Why it happens:** Over-asking for permission instead of executing the plan.
</why_it_fails>

<correction>
**After user approves bd-3:**

```bash
bd update bd-3 --design "[expansion]"  # Update bd
# Mark completed in TodoWrite
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
   - ✅ REQUIRED: Complete code, exact paths, real commands

2. **Every task spec must include a Why section** → Executor must understand purpose
   - Simple tasks: Why explains what breaks if this task is skipped
   - Medium tasks: Why explains what depends on this task and its role in the epic

3. **Every medium task spec must include a Boundaries section** → Prevents scope creep
   - List explicitly what is out of scope for this task
   - Prevents executor from doing "just a little more"

4. **Effort estimates in minutes, not hours** → No task exceeds 30 minutes
   - Simple: 2-10 min (Haiku)
   - Medium: 10-30 min (Sonnet)
   - If a task feels larger: flag it for splitting, do not expand it

5. **Use codebase-investigator agent** → Never verify yourself
   - Agent gets bd assumptions
   - Agent reports discrepancies
   - You adjust plan to match reality

6. **Present COMPLETE expansion before asking** → User must SEE before approving
   - Show full expansion in message text
   - Then use AskUserQuestion for approval
   - Never ask without showing first

7. **Continue automatically between validations** → Don't ask permission
   - TodoWrite list IS your plan
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
- "This will take longer than 30 min" → Flag for splitting, do not expand

</critical_rules>

<verification_checklist>

Before marking each task complete in TodoWrite:
- [ ] Task classified as simple or medium
- [ ] Used codebase-investigator agent (not manual verification)
- [ ] Spec uses correct two-tier template for classification
- [ ] Spec includes Why section (both tiers)
- [ ] Medium spec includes Boundaries section
- [ ] Effort estimate is in minutes (2-10 or 10-30), not hours
- [ ] Presented COMPLETE expansion to user (showed full text)
- [ ] User approved expansion (via AskUserQuestion)
- [ ] Updated bd with actual content (no placeholders)
- [ ] No meta-references in design field

Before finishing all tasks:
- [ ] All tasks in TodoWrite marked completed
- [ ] All bd tasks updated with two-tier specs
- [ ] No task exceeds 30-minute estimate
- [ ] No conditional steps ("if exists")
- [ ] Complete code examples in all medium task steps
- [ ] Exact file paths and commands throughout

</verification_checklist>

<integration>

**This skill calls:**
- codebase-investigator (REQUIRED for each task verification)

**This skill is called by:**
- User (via /hyperpowers:write-plan command)
- After brainstorming creates the task tree

**After this skill:**
- Run hyperpowers:sre-task-refinement in batch mode against the full plan
- Then use hyperpowers:executing-plans to implement

**Agents used:**
- hyperpowers:codebase-investigator (verify assumptions, report discrepancies)

</integration>

<resources>

**Detailed guidance:**
- [bd command reference](../common-patterns/bd-commands.md)
- [Task structure examples](resources/task-examples.md) (if exists)

**When stuck:**
- Unsure about file structure → Use codebase-investigator
- Don't know version → Use codebase-investigator
- Tempted to write "if exists" → Use codebase-investigator first
- About to write placeholder → Stop, write actual content
- Want to ask permission → Check: Is this task validation or final choice? If neither, don't ask

</resources>
