# Hyperpowers Execution Workflows - Complete Analysis

## Executive Summary

Hyperpowers currently implements a **single linear execution path** for feature development:

```
brainstorming → writing-plans → executing-plans → review-implementation → finishing-a-development-branch
```

The team/wave-based parallel execution system (multi-agent parallel execution) was removed in commit aa7d145 because it didn't match actual work patterns (mostly sequential) and multiple agents struggle to work on the same repo simultaneously.

**Current state:** Solo sequential workflow only. No team/wave execution available.

---

## 1. BRAINSTORMING SKILL

**File:** `/Users/abugosh/g/hyperpowers/skills/brainstorming/SKILL.md`

### Purpose
Turn rough ideas into validated designs stored as bd epics with immutable requirements.

### Context Requirements
- User describes rough feature idea or provides incomplete requirements
- Team needs to understand what they're building before coding

### Process (7-Step)
1. **Understanding:** Ask Socratic questions (1-5 max per round, use AskUserQuestion tool)
2. **Research:** Dispatch agents to check codebase patterns and external docs
3. **Propose approaches:** Present 2-3 approaches with trade-offs, recommend one
4. **Present design:** Share in 200-300 word chunks, validate each section
5. **Create bd epic:** Store immutable requirements, anti-patterns, success criteria
6. **Create ONLY first task:** Not full tree (subsequent tasks created iteratively)
7. **SRE refinement:** REQUIRED - Run sre-task-refinement before handoff

### Inputs (Receives)
- User description of feature/idea (rough, incomplete)
- Existing codebase state (via codebase-investigator agent)
- External library/API docs (via internet-researcher agent)

### Outputs (Produces)
- **bd epic:** Immutable contract containing:
  - Requirements (specific, testable)
  - Success criteria (all must be true)
  - Anti-patterns (forbidden shortcuts with reasoning)
  - Approach (summary of chosen strategy)
  - Architecture (key components, data flow)
  - Design Rationale (problem, research findings, approaches considered, scope boundaries)
  - **Design Discovery section:** Preserves full context for future task creation
    - Key Decisions Made (Socratic Q&A with implications)
    - Research Deep-Dives (findings from agents)
    - Dead-End Paths (approaches abandoned during research with WHY)
    - Open Concerns Raised (user concerns and how addressed/deferred)
- **First task only:** bd-N with detailed implementation checklist
- **First task refined:** Via sre-task-refinement skill (Opus 4.1 corner-case analysis)

### Handoff Mechanism
After SRE refinement approved:
```
"Epic bd-1 is ready with immutable requirements.
First task bd-2 has been refined and is ready to execute.
Ready to start implementation? I'll use executing-plans."
```

### Rigidity Level
**HIGH FREEDOM** - Adapt Socratic questions to context, but ALWAYS:
- Create immutable epic before code
- Create ONLY first task (not full tree)
- Run SRE refinement before handoff

### Critical Rules
1. Use AskUserQuestion tool for all questions (not just print and wait)
2. Research BEFORE proposing approaches (dispatch agents)
3. Propose 2-3 approaches with trade-offs
4. Epic requirements are IMMUTABLE (tasks adapt, requirements don't)
5. Anti-patterns include reasoning ("NO X because Y")
6. Only create first task (prevents brittle task trees)
7. REQUIRED: Run sre-task-refinement before handoff

### Pain Points & Limitations
- Epic requirements must be crystal clear before tasks can adapt (incomplete brainstorming → bad tasks)
- Anti-patterns section critical (prevents watering down when obstacles hit)
- Design Discovery preservation is KEY for handling obstacles during execution

---

## 2. WRITING-PLANS SKILL

**File:** `/Users/abugosh/g/hyperpowers/skills/writing-plans/SKILL.md`

### Purpose
Expand bd tasks with detailed implementation steps - exact file paths, complete code, verification commands. For engineers with zero context.

### Context Requirements
- bd epic exists with tasks needing expansion
- Tasks have high-level checklists but need step-by-step detail
- Engineer will execute with zero codebase context

### Process (3-Step Loop)
1. **Identify scope:** Single task, range, or full epic
2. **For EACH task:**
   - Read current task from bd
   - Verify codebase state with **codebase-investigator agent** (NEVER manually)
   - Agent reports discrepancies between bd assumptions and reality
   - Draft implementation steps based on actual codebase
   - Present COMPLETE expansion to user (full text before asking approval)
   - After approval: Update bd, continue to next task (NO asking permission between)
3. **Offer execution:** After all tasks expanded, offer to run executing-plans

### Inputs (Receives)
- bd epic + tasks with checklists
- Codebase state (verified by codebase-investigator agent)

### Outputs (Produces)
- **Expanded tasks:** bd updated with:
  - Complete implementation steps (not placeholders)
  - Exact file paths (not "src/auth.ts if exists")
  - Complete code examples (not pseudo-code)
  - Exact commands to run
  - Expected output/verification
  - Follows TDD pattern (write test → run RED → implement → run GREEN → refactor → commit)

### Handoff Mechanism
After all tasks expanded:
```
"All bd issues now contain detailed implementation steps.
Epic ready for execution.

Ready to execute? I can use hyperpowers:executing-plans to implement iteratively."
```

### Rigidity Level
**MEDIUM FREEDOM** - Follow task-by-task validation pattern, use codebase-investigator for verification. Adapt implementation details to actual codebase state.

### Critical Rules
1. **NO placeholders** → Write actual content
   - ❌ FORBIDDEN: `[Full implementation steps as detailed above]`
   - ✅ REQUIRED: Complete code, exact paths, real commands
2. **Use codebase-investigator agent** → NEVER verify yourself
   - Agent gets bd assumptions
   - Agent reports discrepancies
   - You adjust plan to match reality
3. **Present COMPLETE expansion before asking** → User must SEE before approving
4. **Continue automatically between validations** → Don't ask permission
   - TodoWrite list IS your plan
   - Execute it completely
5. **Write definitive steps** → Never conditional
   - ❌ "Update index.js if exists"
   - ✅ "Create src/auth.ts" (investigator confirmed doesn't exist)

### Pain Points & Limitations
- Writing-plans is NOT a skill for "small enhancements" - tasks still need full expansion
- Relies heavily on codebase-investigator accuracy
- Placeholders are tempting when context is unclear (must resist!)
- Current model doesn't handle "update by pattern matching" well

---

## 3. EXECUTING-PLANS SKILL

**File:** `/Users/abugosh/g/hyperpowers/skills/executing-plans/SKILL.md`

### Purpose
Execute bd tasks one at a time with mandatory checkpoints. Load epic → Execute task → Review learnings → Create next task → Run SRE refinement → STOP.

### Context Requirements
- bd epic exists with first task ready
- Epic has immutable requirements and success criteria
- Engineer will work through tasks sequentially with user review between

### Process (Resumption + 5-Step Loop)
**Step 0: Resumption Check (every invocation)**
```bash
bd list --type epic --status open  # Find active epic
bd ready                           # Check for ready tasks
bd list --status in_progress       # Check for in-progress tasks
```
- In-progress task exists → Resume at Step 2 (continue executing)
- Ready task exists → Resume at Step 2 (start executing)
- All tasks closed but epic open → Resume at Step 4 (check criteria)
- Fresh start → Resume at Step 1 (load epic)

**Step 1: Load Epic Context (once at start)**
```bash
bd show bd-1  # Keep requirements fresh, check anti-patterns
```

**Step 2: Execute Current Ready Task**
```bash
bd ready              # Find next task
bd update bd-2 --status in_progress  # Start it
bd show bd-2          # Read details
```
- CRITICAL: Create TodoWrite for ALL substeps (e.g., "Step 1: Write test", "Step 2: Run RED", etc.)
- Use test-driven-development skill for features
- Mark each substep completed immediately after finishing
- Use test-runner agent for verifications
- Pre-close verification: All TodoWrite substeps completed? If incomplete → continue with remaining

**Step 2a: When Hitting Obstacles**
- CRITICAL: Check Design Discovery in epic BEFORE switching approaches
- Find "Approaches Considered" section
- Check if alternative was already rejected
- Read "⚠️ REJECTED BECAUSE" reasoning
- Check "🚫 DO NOT REVISIT UNLESS" conditions
- If reconsidering: Document why rejection reason no longer applies, get user confirmation

**Step 3: Review Against Epic and Create Next Task**
After each task, adapt plan based on reality.
- Re-read epic (keep requirements fresh)
- What did we learn?
- Does this move us toward epic success criteria?
- Three cases:
  - **A) Next task still valid** → Proceed to Step 2
  - **B) Next task now redundant** → Delete task (plan invalidation allowed)
  - **C) Need new task** → Create based on learnings
    - Run SRE refinement on new task (REQUIRED)
    - Create dependencies (parent-child, blocks)

**Step 4: Check Epic Success Criteria and STOP**
- ALL criteria met? → Step 5 (final validation)
- Some missing? → Step 4a (STOP for user review)

**Step 4a: STOP Checkpoint (MANDATORY)**
Present summary to user:
```markdown
## Task bd-N Complete - Checkpoint

### What Was Done
- [Summary of implementation]
- [Key learnings/discoveries]

### Next Task Ready
- bd-M: [Title]
- [Brief description]

### Epic Progress
- [X/Y success criteria met]
- [Remaining criteria]

### To Continue
Run `/hyperpowers:execute-plan` to execute the next task.
```
**Why STOP is mandatory:**
- User can clear context (prevents context exhaustion)
- User can review implementation before next task
- User can adjust next task if needed
- Prevents runaway execution without oversight

**Do NOT rationalize skipping:**
- "Good context loaded" → Context reloads are cheap, wrong decisions aren't
- "Momentum" → Checkpoints ensure quality over speed
- "User didn't ask to stop" → Stopping is default, continuing requires explicit command

**Step 5: Final Validation and Closure**
When all success criteria appear met:
1. Run full verification (tests, hooks, manual checks)
2. REQUIRED: Use review-implementation skill
3. Only close epic after review approves

### Inputs (Receives)
- bd epic with immutable requirements and anti-patterns
- First task refined via sre-task-refinement
- User approval to start execution

### Outputs (Produces)
- **Completed tasks:** All substeps done, tests passing, committed
- **New tasks created:** Based on learnings, not initial assumptions
- **Learnings documented:** In bd task descriptions
- **Next task ready:** Refined via SRE, ready for next execution cycle
- **STOP checkpoint:** Summary to user, waiting for approval to continue

### Handoff Mechanism
After STOP checkpoint:
```
User clears context, reviews implementation.
User runs `/hyperpowers:execute-plan` again.
Skill resumes via resumption check (finds ready task, continues).
```

### Rigidity Level
**LOW FREEDOM - Follow exact process:** Load epic, execute ONE task, review, create next task with SRE refinement, STOP.

### Critical Rules (No Exceptions)
1. **STOP after each task** → User needs checkpoint, may need to clear context
2. **SRE refinement for new tasks** → REQUIRED, no skipping
3. **Epic requirements immutable** → Never water down when blocked
4. **Check Design Discovery before switching approaches** → Rejection reasons usually still apply
5. **All substeps completed** → Never close task with pending substeps
6. **Plan invalidation allowed** → Delete redundant tasks based on learnings
7. **Review before closing epic** → Use review-implementation skill

### Pain Points & Limitations
- Manual STOP checkpoint creates workflow friction (but necessary for user oversight)
- Context limit enforcement (every task cycle needs fresh load)
- SRE refinement delays (Opus 4.1 needed, adds time)
- Task creation based on learnings requires careful judgment
- Handling obstacles is complex (Design Discovery preserved but requires careful reading)

---

## 4. SRE-TASK-REFINEMENT SKILL

**File:** `/Users/abugosh/g/hyperpowers/skills/sre-task-refinement/SKILL.md`

### Purpose
Apply 7-category corner-case analysis (uses Opus 4.1) to identify edge cases and failure modes before execution.

### Context Requirements
- Task exists with implementation checklist
- Task needs deeper analysis before execution

### Process
1. Read task specification
2. Apply 7-category corner-case analysis:
   - Input validation (empty, max, invalid)
   - Failure modes (network, database, permission errors)
   - Concurrency (race conditions, deadlocks)
   - Security (injection, auth bypass)
   - Performance (edge cases that slow down)
   - Integration (API changes, version mismatches)
   - Recovery (rollback, recovery from errors)
3. Strengthen success criteria with findings
4. Ensure task is ready for implementation

### Inputs (Receives)
- bd task with checklist

### Outputs (Produces)
- Strengthened task with:
  - Edge cases identified
  - Failure modes documented
  - Success criteria refined with corner cases
  - Task ready for execution

### Rigidity Level
**MEDIUM FREEDOM** - Apply corner-case analysis with appropriate depth for task scope.

### Integration
- **Called by:** brainstorming (after first task created), executing-plans (for new tasks)
- **Uses:** Opus 4.1 model for deep analysis

### Pain Point
- Only available when Opus 4.1 is accessible
- Adds time to task cycle (needed for quality)
- Requires careful reading of task to apply analysis meaningfully

---

## 5. REVIEW-IMPLEMENTATION SKILL

**File:** `/Users/abugosh/g/hyperpowers/skills/review-implementation/SKILL.md`

### Purpose
Verify implementation against bd spec with Google Fellow-level scrutiny. Check all criteria met, anti-patterns avoided, code quality production-ready.

### Context Requirements
- All bd tasks for epic are CLOSED
- executing-plans completed all tasks
- Ready to validate before closure

### Process (4-Step)
**Step 1: Load Epic Specification**
```bash
bd show bd-1          # Epic specification
bd dep tree bd-1      # Task tree
bd list --parent bd-1 # All tasks
```
Create TodoWrite tracker for each task to review.

**Step 2: Review Each Task**

For each task:
- **A. Read task specification** (goal, success criteria, implementation checklist, edge cases, anti-patterns)
- **B. Run automated code completeness checks:**
  - TODOs/FIXMEs without issue numbers
  - Stub implementations
  - Unsafe patterns in production
  - Ignored/skipped tests
- **B2. Dead code audit** (fallback code, unused functions, deprecation markers, orphaned tests, backwards compat shims)
- **C. Run quality gates via test-runner agent** (tests, format, lint)
- **D. Read actual implementation files** (CRITICAL: use Read tool, not just git diff)
- **E. Code quality review** (Google Fellow perspective):
  - Error handling (Result/Option or try/catch, no unwrap in production)
  - Safety (bounds checking, no panics, no race conditions)
  - Clarity (would junior understand in 6 months?)
  - Testing (edge cases, failure scenarios)
  - Production readiness (logging, performance)
- **E2. Test quality audit** (MANDATORY for all new tests):
  - What bug would this catch?
  - Tautological tests (❌ REJECT): Compiler ensures syntax, struct has fields, builder returns value
  - Meaningful tests (✅ APPROVE): Catch real bugs, test behavior not implementation, cover edge cases
- **F. Verify success criteria with evidence** (run verification commands)
- **G. Check anti-patterns** (search for each prohibited pattern)
- **H. Verify key considerations** (read code for edge case handling)
- **I. Record findings** (evidence-based, confidence scores 0.0-1.0)

**Step 3: Report Findings**
- **If NO gaps:** Report APPROVED with full evidence
- **If gaps found:** Report GAPS FOUND with exact issues

**Step 4: Gate Decision**
- **If APPROVED:** STOP for manual validation (epic stays open for user testing)
- **If gaps found:** STOP, don't proceed to finishing-a-development-branch

### Inputs (Receives)
- bd epic with all tasks CLOSED
- All implementation files (read from repo)
- Test output (via test-runner agent)

### Outputs (Produces)
- **Review report:** APPROVED or GAPS FOUND
- **Evidence-based findings:** Each claim backed by:
  - File paths and line numbers
  - Command output
  - Code inspection results
  - Confidence scores (findings <0.8 flagged as UNCERTAIN)

### Handoff Mechanism
If APPROVED:
```
## Implementation Review: APPROVED ✅

Automated checks have passed. The epic remains **open** for your manual testing.

When you've completed your manual validation, run:
- `/hyperpowers:finish-branch` to close the epic and integrate the work
```

**STOP here.** Do not call finishing-a-development-branch. Epic stays open for user manual validation.

### Rigidity Level
**LOW FREEDOM - Follow 4-step review process exactly.** Review with Google Fellow-level scrutiny (20+ years production experience).

### Critical Rules (No Exceptions)
1. **Review every task** → No skipping "simple" tasks
2. **Run all automated checks** → TODOs, stubs, unsafe patterns, ignored tests
3. **Run dead code audit** → Fallback code, unused functions, deprecation markers
4. **Read actual files** → Not just git diff
5. **Verify every success criterion** → With evidence, not assumptions
6. **Check all anti-patterns** → Search for prohibited patterns
7. **Apply Google Fellow scrutiny** → Production-grade code review
8. **Audit all new tests** → Tautological tests = gaps, not coverage
9. **If gaps found → STOP** → Don't proceed to finishing-a-development-branch

### Evidence Requirements
Every claim requires evidence:
| Claim Type | Required Evidence |
|------------|-------------------|
| "Code implements X" | File path:line showing implementation |
| "Test covers Y" | Test name + specific assertion |
| "Criterion met" | Command output proving criterion |
| "No anti-pattern" | Search command showing no matches |

Confidence scores (0.0-1.0):
- 1.0: Direct evidence (ran command, read code)
- 0.8: Strong indirect evidence
- 0.5: Uncertain (partial evidence)
- 0.3: Weak (limited investigation)

Findings <0.8 must be investigated until ≥0.8 or marked UNCERTAIN.

### Pain Points & Limitations
- Time-consuming (comprehensive review of all tasks required)
- Requires understanding code in multiple languages
- Test quality audit is nuanced (tautological tests are subtle)
- Dead code detection requires understanding codebase patterns
- High bar prevents shipping incomplete work (intentional)

---

## 6. FINISHING-A-DEVELOPMENT-BRANCH SKILL

**File:** `/Users/abugosh/g/hyperpowers/skills/finishing-a-development-branch/SKILL.md`

### Purpose
Close bd epic, verify tests pass, present 4 integration options, execute choice, cleanup worktree appropriately.

### Context Requirements
- review-implementation approved (automated checks passed)
- Manual validation completed by user
- All bd tasks closed
- Ready to integrate back to main

### Process (6-Step)
**Step 1: Close bd Epic**
```bash
bd dep tree bd-1  # Show task tree
bd list --status open --parent bd-1  # Check for open tasks
```
If any tasks still open → STOP. If all closed:
```bash
bd close bd-1
```

**Step 2: Verify Tests**
Use test-runner agent (avoid context pollution):
```
Dispatch test-runner: "Run: cargo test"
```
If tests fail → STOP. If pass → continue.

**Step 3: Determine Base Branch**
```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master
```

**Step 4: Present Options**
Present exactly these 4 options:
```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Merge Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

**Step 5: Execute Choice**

Option 1: Merge Locally
```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
# Dispatch test-runner to verify tests on merged result
git branch -d <feature-branch>
```

Option 2: Push and Create MR
```bash
git push -u origin <feature-branch>
glab mr create --title "feat: <epic-name>" --description "[epic info]"
```

Option 3: Keep As-Is
- No cleanup, worktree preserved

Option 4: Discard (requires confirmation)
```
"Type 'discard' to confirm"
[Wait for exact confirmation]
git checkout <base-branch>
git branch -D <feature-branch>
```

**Step 6: Cleanup Worktree**
Options 1, 2, 4 only:
```bash
git worktree remove <worktree-path>
```
Option 3: Keep worktree (don't cleanup).

### Inputs (Receives)
- bd epic CLOSED
- Tests passing
- User choice of integration option

### Outputs (Produces)
- **Option 1:** Code merged to main locally, branch deleted, worktree cleaned
- **Option 2:** Code pushed, MR created, worktree kept for feedback
- **Option 3:** Code on feature branch, worktree preserved, epic closed
- **Option 4:** Code deleted, branch deleted, worktree cleaned

### Rigidity Level
**LOW FREEDOM - Follow 6-step process exactly.** Present exactly 4 options. Never skip test verification. Must confirm before discarding.

### Critical Rules (No Exceptions)
1. **Never skip test verification** → Tests must pass before presenting options
2. **Present exactly 4 options** → No open-ended questions
3. **Require confirmation for Option 4** → Type "discard" exactly
4. **Keep worktree for Options 2 & 3** → MR and keep-as-is need worktree
5. **Verify tests after merge (Option 1)** → Merged result might break

### Pain Points & Limitations
- 4-option limitation might not cover all workflows
- Worktree cleanup timing (Option 2 can't cleanup yet, user might forget to cleanup later)
- MR creation requires glab (not all repos use GitLab)
- No automation for rebase-on-main before merge

---

## WORKFLOW HANDOFF DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│ brainstorming                                                   │
│ - Rough idea → Immutable epic + first task                      │
│ - Dispatch: codebase-investigator, internet-researcher          │
│ - REQUIRED: sre-task-refinement before handoff                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓ "Epic bd-1 ready, first task refined"
┌─────────────────────────────────────────────────────────────────┐
│ writing-plans (optional)                                        │
│ - Expand tasks with complete implementation steps               │
│ - Dispatch: codebase-investigator for verification              │
│ - Present COMPLETE expansion before approving                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓ "All tasks expanded, ready for execution"
                         │ (skips to executing-plans if already detailed)
┌─────────────────────────────────────────────────────────────────┐
│ executing-plans (main execution loop)                           │
│ - Resumption check → Load epic → Execute task →                │
│ - Review learnings → Create next task → SRE refine → STOP       │
│ - CRITICAL: STOP after each task for user review               │
│ - Dispatch: test-runner, sre-task-refinement                    │
├─────────────────────────────────────────────────────────────────┤
│ [User clears context, reviews implementation]                   │
│ [User runs /execute-plan again to continue]                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓ "All success criteria met"
┌─────────────────────────────────────────────────────────────────┐
│ review-implementation                                           │
│ - Verify all success criteria met                               │
│ - Check anti-patterns, code quality, test quality               │
│ - STOP for manual validation if approved                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓ "Approved ✅ / Gaps Found ❌"
                         │
                         ├─→ [If gaps: Return to executing-plans]
                         │
                         ↓ [If approved: User completes manual testing]
┌─────────────────────────────────────────────────────────────────┐
│ finishing-a-development-branch                                  │
│ - Close epic → Verify tests → Present 4 options                │
│ - Execute choice: Merge/MR/Keep/Discard                        │
│ - Cleanup worktree appropriately                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Context Flow

### Epic Requirements → Task Creation → Task Execution → Verification

**Epic (Immutable)**
```
Requirements (IMMUTABLE - contract)
Success Criteria (MUST ALL BE TRUE)
Anti-Patterns (FORBIDDEN - with reasoning)
Approaches Considered (rejected approaches with DO NOT REVISIT UNLESS)
Design Discovery (preserved context for obstacles)
```

**Tasks (Adaptive)**
- Created iteratively based on learnings
- Each task refined via SRE (corner-case analysis)
- Assumptions validated via codebase-investigator
- Execution: TDD cycle (RED → GREEN → REFACTOR)
- Verification: All substeps completed, tests passing

**Verification (Evidence-Based)**
- All success criteria verified with evidence
- All anti-patterns searched and cleared
- All new tests audited for meaningfulness (not tautological)
- Dead code audit for refactoring completeness
- Code quality review (production-grade scrutiny)

---

## Design Discovery - Critical Component

The epic's Design Discovery section preserves context for handling obstacles:

```
Key Decisions Made
├─ Socratic questions asked
├─ User's answers
└─ Implications for requirements/anti-patterns

Research Deep-Dives
├─ Topic explored
├─ Sources consulted
├─ Findings
└─ Conclusion

Dead-End Paths
├─ Why explored
├─ What investigated
└─ Why abandoned

Open Concerns Raised
├─ User concern
└─ How addressed/deferred
```

**Why this matters:** During executing-plans, when obstacles are hit, Design Discovery prevents:
- Revisiting rejected approaches (stored with rejection reasons and "DO NOT REVISIT UNLESS")
- Re-debating settled decisions (Socratic Q&A preserved)
- Rationalizing shortcuts (anti-patterns documented with reasoning)

---

## Current State Summary

**REMOVED (Commit aa7d145):**
- wave-planning skill (team-level wave execution)
- team-executing-plans skill (parallel agent coordination)
- execute-wave command
- Parallelism Map from brainstorming

**Reason:** Wave system didn't match actual work patterns (mostly sequential) and multiple agents struggle to work on the same repo simultaneously.

**Current workflow:** Solo sequential only. No team/wave execution available.

---

## Pain Points & Design Tensions

1. **Manual STOP Checkpoints**
   - Necessary for user oversight and context management
   - Creates workflow friction (can't execute end-to-end)
   - Mitigated by: Resumption check (can resume where left off)

2. **Task Creation Uncertainty**
   - Tasks created mid-execution based on learnings (not predictable)
   - Requires careful judgment
   - Mitigated by: SRE refinement provides structure

3. **Obstacle Handling Complexity**
   - Design Discovery must be carefully read when obstacles arise
   - "DO NOT REVISIT UNLESS" conditions require judgment
   - Mitigated by: Clear documentation in epic

4. **Agent Dispatch Overhead**
   - brainstorming and writing-plans dispatch multiple agents
   - Adds time but necessary for accuracy
   - Mitigated by: Agents return only essential info to main context

5. **Test Quality Audit Nuance**
   - Tautological tests are subtle (passing tests don't prove code works)
   - Requires human judgment for each test
   - Mitigated by: Clear criteria and examples in review-implementation

6. **Worktree Management**
   - Option 2 (MR) requires keeping worktree for feedback iterations
   - Users might forget to cleanup later
   - No automated reminder for cleanup
