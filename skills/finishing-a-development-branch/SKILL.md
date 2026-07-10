---
name: finishing-a-development-branch
description: Use when implementation complete and tests pass - verifies epic tasks and tests, presents integration options (merge/MR/keep/discard), closes the epic on success or records a discard note, executes choice
---

<skill_overview>
Verify epic tasks are complete, verify tests pass, present 4 integration options, execute choice — closing the epic inside the successful paths (merge/MR/keep) or recording a discard note that leaves it open — cleanup worktree appropriately.
</skill_overview>

<rigidity_level>
LOW FREEDOM - Follow the 6-step process exactly. Present exactly 4 options. Never skip test verification. Must confirm before discarding. Never close the epic before the integration choice succeeds.
</rigidity_level>

<quick_reference>
| Step | Action | If Blocked |
|------|--------|------------|
| 1 | Verify reviewer gate + epic tasks complete | Marker absent or tasks open → STOP |
| 2 | Verify tests pass (test-runner agent) | Tests fail → STOP |
| 3 | Determine base branch | Ask if needed |
| 4 | Present exactly 4 options | Wait for choice |
| 5 | Execute choice (closes epic on Options 1-3; records discard note and leaves epic open on Option 4) | Follow option workflow |
| 6 | Cleanup worktree (options 1,2,4 only) | Option 3 keeps worktree |

**Options:** 1=Merge locally, 2=MR, 3=Keep as-is, 4=Discard (confirm)
</quick_reference>

<when_to_use>
- End-of-epic reviewer APPROVED (dispatched by executing-plans' completion; or via `/hyperpowers:review-implementation` for on-demand re-verification)
- Manual validation/testing complete
- All bd tasks for epic are done
- Ready to integrate work back to main branch

**Prerequisites:**
- The end-of-epic reviewer gate in executing-plans' completion must have returned APPROVED (verified in Step 1 via the persisted `Verdict: APPROVED` marker)
- Complete your manual testing while epic is still open
- Then run this skill to integrate and close the epic (or record a discard note, leaving it open)

**Don't use for:**
- Work still in progress
- Tests failing
- Epic has open tasks
- Mid-implementation (use hyperpowers:executing-plans)
- Before manual validation (the reviewer gate must pass first)
</when_to_use>

<the_process>
## Step 1: Verify Epic Tasks Complete

**Announce:** "I'm using hyperpowers:finishing-a-development-branch to complete this work."

**Verify the end-of-epic reviewer gate:**
```bash
bd show bd-1    # epic notes must contain the completion gate-state marker
```
The epic's notes must contain a line beginning `Verdict: APPROVED (end-of-epic reviewer` — persisted by executing-plans' Completion (format: `skills/common-patterns/loop-interfaces.md`).

**If the marker is absent or not APPROVED:**
```
Cannot proceed with bd-1: no APPROVED end-of-epic reviewer gate is recorded on
the epic. Run executing-plans' Completion first — the end-of-epic reviewer must
return APPROVED and the gate-state block (with its Verdict: APPROVED marker)
must be persisted to the epic's bd notes.
```
**STOP. Do not proceed.**

**Verify all tasks closed:**

```bash
bd list --parent bd-1  # List child tasks
bd list --status open --parent bd-1  # Check for open tasks
```

**If any tasks still open:**
```
Cannot proceed with bd-1: N tasks still open:
- bd-3: Task Name (status: in_progress)
- bd-5: Task Name (status: open)

Complete all tasks before finishing.
```

**STOP. Do not proceed.**

**If all tasks closed:** Continue to Step 2.

**Note:** The epic itself is NOT closed here. Closure happens later, inside Step 5's successful integration paths (Options 1-3). This ordering matters: if tests fail in Step 2, or the user picks Option 4 (discard), the epic must still be open to reflect reality.

---

## Step 2: Verify Tests

**IMPORTANT:** Use hyperpowers:test-runner agent to avoid context pollution.

Dispatch hyperpowers:test-runner agent:
```
Run: <project's test command>
(examples: cargo test / npm test / pytest / go test ./...)
```

Agent returns summary + failures only.

**If tests fail:**
```
Tests failing (N failures). Must fix before completing:

[Show failures]

Cannot proceed until tests pass. Epic bd-1 remains open.
```

**STOP. Do not proceed.**

**If tests pass:** Continue to Step 3.

---

## Step 3: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main - is that correct?"

---

## Step 4: Present Options

Present exactly these 4 options:

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Merge Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Don't add explanation.** Keep concise.

---

## Step 5: Execute Choice

### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
Dispatch hyperpowers:test-runner: "Run: <test command>"

# If tests pass
git branch -d <feature-branch>
bd close bd-1
```

Then: Step 6 (cleanup worktree)

---

### Option 2: Push and Create MR

**Get epic info:**

```bash
bd show bd-1
bd list --parent bd-1  # List child tasks
```

**Create MR:**

```bash
git push -u origin <feature-branch>

glab mr create --title "feat: <epic-name>" --description "$(cat <<'EOF'
## Epic

Closes bd-<N>: <Epic Title>

## Summary
<2-3 bullets from epic implementation>

## Tasks Completed
- bd-2: <Task Name>
- bd-3: <Task Name>

## Test Plan
- [ ] All tests passing
- [ ] <verification steps from epic>
EOF
)"
```

**After MR created:**

```bash
bd close bd-1
```

Then: Step 6 (cleanup worktree)

---

### Option 3: Keep As-Is

```bash
bd close bd-1
```

Report: "Keeping branch <name>. Worktree preserved at <path>. Epic bd-1 closed."

**Don't cleanup worktree.**

---

### Option 4: Discard

**Confirm first:**

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact "discard" confirmation.

**If confirmed:**

```bash
git checkout <base-branch>
git branch -D <feature-branch>
bd update bd-1 --notes "Implementation discarded <date>: <reason>. Branch <feature-branch> deleted. Epic remains open — re-attempt or close explicitly."
```

**Do not close the epic.** It stays open, honestly reflecting that the work was discarded rather than completed.

Then: Step 6 (cleanup worktree)

---

## Step 6: Cleanup Worktree

**For Options 1, 2, 4 only:**

```bash
# Check if in worktree
git worktree list | grep $(git branch --show-current)

# If yes
git worktree remove <worktree-path>
```

**For Option 3:** Keep worktree (don't cleanup).
</the_process>

<examples>
<example>
<scenario>Developer skips test verification before presenting options</scenario>

<code>
# Step 1: Verified epic tasks complete ✓
bd list --parent bd-1  # List child tasks
bd list --status open --parent bd-1
# No open tasks

# Step 2: SKIPPED test verification
# Jump directly to presenting options

"Implementation complete. What would you like to do?
1. Merge back to main locally
2. Push and create MR
..."

User selects Option 1

git checkout main
git merge feature-branch
# Tests fail! Broken code now on main
# bd close bd-1 already ran inside Option 1 — epic now falsely shows complete
</code>

<why_it_fails>
- Skipped mandatory test verification
- Merged broken code to main branch
- Other developers pull broken main
- CI/CD fails, blocks deployment
- Must revert, fix, merge again (wasted time)
- Epic closed on broken work — bd state lies about reality
</why_it_fails>

<correction>
**Follow Step 2 strictly:**

```bash
# After verifying epic tasks complete
bd list --parent bd-1  # ✓ no open tasks

# MANDATORY: Verify tests BEFORE presenting options
Dispatch hyperpowers:test-runner agent: "Run: cargo test"

# Agent reports
"Test suite passed (127 tests, 0 failures, 2.3s)"

# NOW present options
"Implementation complete. What would you like to do?
1. Merge back to main locally
..."

# Epic bd-1 is closed only after the chosen path succeeds (Step 5),
# never before tests are verified
```

**What you gain:**
- Confidence tests pass before integration
- No broken code merged to main
- CI/CD stays green
- Other developers unblocked
- Professional workflow
- Epic close always reflects reality
</correction>
</example>

<example>
<scenario>Developer auto-cleans worktree for MR option</scenario>

<code>
# User selects Option 2: Create MR
git push -u origin feature-auth
glab mr create --title "feat: Add OAuth" --description "..."

# Developer immediately cleans up worktree
git worktree remove ../feature-auth-worktree

# MR gets feedback: "Please add rate limiting"
# User: "Can you address the MR feedback?"
# Worktree is gone! Have to recreate it
git worktree add ../feature-auth-worktree feature-auth
# Lost local state, uncommitted experiments, etc.
</code>

<why_it_fails>
- Cleaned worktree when MR still active
- User likely needs worktree for MR feedback
- Have to recreate worktree for changes
- Lost any local uncommitted work
- Inefficient workflow
</why_it_fails>

<correction>
**Option 2 workflow (correct):**

```bash
git push -u origin feature-auth
glab mr create --title "feat: Add OAuth" --description "..."

# Report MR created
"Merge request created: https://gitlab.com/user/repo/-/merge_requests/42

Keeping worktree at ../feature-auth-worktree for MR updates."

# NO worktree cleanup
# User can address MR feedback in same worktree
```

**Cleanup happens later when:**
- MR is merged
- User explicitly requests cleanup
- User uses finishing-a-development-branch again after MR merges

**What you gain:**
- Worktree available for MR feedback
- No need to recreate worktree
- Preserve local state and experiments
- Efficient MR iteration workflow
</correction>
</example>

<example>
<scenario>Developer discards work without confirmation</scenario>

<code>
# User says: "Actually, discard this work"

# Developer immediately executes
git checkout main
git branch -D feature-experimental
git worktree remove ../feature-experimental-worktree

# 50 commits deleted
# User: "Wait, I meant discard the LAST commit, not the whole branch!"
# Too late - work is gone
</code>

<why_it_fails>
- No confirmation before destructive action
- Misunderstood user intent
- Permanent data loss
- No way to recover work
- Catastrophic for user
</why_it_fails>

<correction>
**Option 4 workflow (correct):**

```
User: "Discard this work"

"This will permanently delete:
- Branch feature-experimental
- All commits:
  * a1b2c3d Add OAuth integration
  * d4e5f6g Add rate limiting
  * g7h8i9j Update tests
  ... (47 more commits)
- Worktree at ../feature-experimental-worktree

Type 'discard' to confirm."

# WAIT for exact confirmation
User types: "discard"

# NOW execute
git checkout main
git branch -D feature-experimental
git worktree remove ../feature-experimental-worktree
# Record the discard on the epic (see Step 5, Option 4) — do NOT close it

"Branch feature-experimental deleted. Epic bd-1 remains open with a discard note."
```

**What you gain:**
- User sees exactly what will be deleted
- Explicit confirmation required
- Prevents accidental data loss
- Time to reconsider or clarify
- Safe destructive operations
- bd state stays honest — epic isn't marked closed for work that no longer exists
</correction>
</example>
</examples>

<option_matrix>
| Option | Merge | Push | Keep Worktree | Cleanup Branch | Cleanup Worktree |
|--------|-------|------|---------------|----------------|------------------|
| 1. Merge locally | ✓ | - | - | ✓ | ✓ |
| 2. Create MR | - | ✓ | ✓ | - | - |
| 3. Keep as-is | - | - | ✓ | - | - |
| 4. Discard | - | - | - | ✓ (force) | ✓ |
</option_matrix>

<critical_rules>
## Rules That Have No Exceptions

1. **Never skip test verification** → Tests must pass before presenting options
2. **Present exactly 4 options** → No open-ended questions
3. **Require confirmation for Option 4** → Type "discard" exactly
4. **Keep worktree for Options 2 & 3** → MR and keep-as-is need worktree
5. **Verify tests after merge (Option 1)** → Merged result might break
6. **Never close the epic before Step 5** → Task verification (Step 1) and test verification (Step 2) must both pass first; closing early leaves the epic marked done on unverified or broken work
7. **Discard never closes the epic** → Record a discard note on the epic instead (Step 5, Option 4); it stays open until someone re-attempts or closes it explicitly

## Common Excuses

All of these mean: **STOP. Follow the process.**

- "Tests passed earlier, don't need to verify" (Might have changed, verify now)
- "User knows what they want" (Present options, let them choose)
- "Obvious they want to discard" (Require explicit confirmation)
- "MR done, cleanup worktree" (MR likely needs updates, keep worktree)
- "Too many options" (Exactly 4, no more, no less)
- "Close the epic first, it's basically done" (No — close only inside Step 5, after tests are verified and the integration choice succeeds)
- "Discarding, no need to touch bd" (Wrong — record a discard note on the epic, or bd state lies about what happened)
</critical_rules>

<verification_checklist>
Before completing:

- [ ] End-of-epic reviewer gate marker verified in epic notes (Step 1)
- [ ] All child tasks verified closed (Step 1)
- [ ] Tests verified passing (via test-runner agent, Step 2)
- [ ] Presented exactly 4 options (no open-ended questions)
- [ ] Waited for user choice (didn't assume)
- [ ] If Option 1, 2, or 3: bd epic closed only after that path succeeded
- [ ] If Option 4: Got typed "discard" confirmation, then recorded a discard note on the epic and left it open
- [ ] Worktree cleaned for Options 1, 4 only (not 2, 3)
- [ ] If Option 1: Verified tests on merged result

**Can't check all boxes?** Return to process and complete missing steps.
</verification_checklist>

<integration>
**This skill is called by:**
- User (via `/hyperpowers:finish-branch` after manual validation complete)

**Call chain:**
```
hyperpowers:executing-plans (reviewer gate + architecture check + STOP) → user manual testing → /finish-branch
```

**Why user-invoked:** Epic stays open during manual validation so user has full context. User explicitly triggers closure when ready.

**This skill calls:**
- hyperpowers:test-runner agent (for test verification)
- bd commands (epic management)
- glab commands (MR creation)

**CRITICAL:** Never read `.beads/issues.jsonl` directly. Always use bd CLI commands.
</integration>

<resources>
**When stuck:**
- Tasks won't close → Check bd status, verify all child tasks done
- Tests fail → Fix before presenting options (can't proceed)
- User unsure → Explain options, but don't make choice for them
- Worktree won't remove → Might have uncommitted changes, ask user
</resources>
