# Git Commit Workflow - End-to-End

## Overview

The commit workflow is orchestrated across three components:
1. **Executor Agent** (agents/executor.md) - Implements tasks with TDD and creates commits
2. **Test-Driven Development Skill** (skills/test-driven-development/SKILL.md) - Enforces RED-GREEN-REFACTOR cycle
3. **Test-Runner Agent** (agents/test-runner.md) - Runs tests/commits, returns summary only

## Commit Points in the Workflow

### In Executor Agent (agents/executor.md, lines 83-91)

The executor commits after each refactor phase in the TDD cycle:

```bash
git add <specific files>
git commit -m "<descriptive message>

bd: <task-id>"
```

**Context:**
- Lines 56-91: Execution loop describes the RED-GREEN-REFACTOR-**COMMIT** cycle
- Line 83: "Commit" appears after "Step 5 — Refactor"
- Lines 87-91: Exact commit syntax with task ID in footer
- Lines 85-98: Completion check - all TodoWrite substeps must be marked complete before moving to task closure
- Line 103: Task is closed via `bd close <task-id>` AFTER commit

**Key Rules:**
- Commits are per-deliverable (RED-GREEN-REFACTOR-COMMIT cycle for each one)
- Commit message includes bd task ID in footer (line 90: `bd: <task-id>`)
- Commits happen BEFORE closing task (line 103 closes task, implying commits happened earlier)

### In Test-Driven Development Skill (skills/test-driven-development/SKILL.md)

The TDD skill does NOT mention commits explicitly. It only covers:
- **RED** phase: Write failing test (lines 47-54)
- **Verify RED** phase: Watch test fail (lines 58-68)
- **GREEN** phase: Write minimal code (lines 70-75)
- **Verify GREEN** phase: Confirm tests pass (lines 76-86)
- **REFACTOR** phase: Clean up code (lines 88-95)
- **Repeat** for next feature (lines 97-99)

**Finding:** The TDD skill does not prescribe commit behavior. Commits are handled by the executor agent as part of its cycle.

### In Test-Runner Agent (agents/test-runner.md)

The test-runner can execute commits:

**Key Lines:**
- Line 28: "Git commit: `git commit`"
- Lines 226-247: Git Commit Report sections showing success/failure formats
- Line 3 example: "Ready to commit changes... I'll use the test-runner agent to run git commit"
- Lines 20-24: Identifies command type including `git commit`

**Purpose:**
- Test-runner captures commit output in its own context (line 15: "only summary + failures go to the requestor")
- Returns concise report: commit hash, message, files committed (lines 230-233)
- Executor uses test-runner to avoid commit output pollution (line 252 in executor: "Always use the test-runner agent for test execution")

**Report Format (lines 226-247):**
```
✓ Commit successful
- Commit: [commit hash]
- Message: [commit message]
- Files committed: [file list]
- Exit code: 0
```

## Commit Hooks and Protections

### Pre-commit Hook Protection (hooks/post-tool-use/03-block-pre-commit-bash.py)

Blocks any Bash command that attempts to modify `.git/hooks/pre-commit`:

**Patterns Blocked:**
- Direct file path references to `.git/hooks/pre-commit` (line 15)
- Redirections: `> pre-commit`, `>> pre-commit` (lines 19-20)
- sed/awk/perl modifications (lines 23-24)
- mv/cp operations (lines 27-28)
- echo/cat piping (lines 34-35)
- tee operations (line 38)
- cat redirections (lines 41-42)

**Purpose (lines 78-103):**
- Prevents bypassing quality standards
- Ensures hooks stay in version control
- Blocks `--no-verify` workarounds indirectly by blocking hook modifications

## How Commits Flow Through the System

```
Executor Agent
│
├─ For each deliverable in task:
│  │
│  ├─ RED: Write test → Verify FAIL
│  ├─ GREEN: Write code → Verify PASS
│  ├─ REFACTOR: Clean code → Verify PASS
│  │
│  └─ COMMIT (line 83-91):
│     └─ Dispatch test-runner agent
│        └─ Run: git add + git commit -m "...\n\nbd: <id>"
│        └─ Returns: ✓ Commit successful (hash, message, files)
│        └─ Output stays in test-runner context
│
├─ All substeps completed? (TodoWrite check)
│  └─ YES → Close task (bd close <task-id>)
│  └─ NO → Continue with remaining substeps
│
├─ Next task or escalate/propose
│  └─ Lead approves proposal
│  └─ Continue to next task
│
└─ All tasks complete
   └─ Send Epic Completion Report to lead
   └─ Lead dispatches reviewer
   └─ Reviewer approves
   └─ Lead shuts down executor
```

## Critical Constraints

1. **TDD is mandatory** (test-driven-development.md, lines 10-13, 244)
   - Every deliverable starts with failing test
   - No code without failing test first

2. **Commits include bd task ID** (executor.md, line 90)
   - Message format: `"<descriptive message>\n\nbd: <task-id>"`
   - Traces implementation back to task

3. **Pre-commit hooks cannot be modified** (hooks/post-tool-use/03-block-pre-commit-bash.py)
   - Bash commands attempting modifications are blocked
   - Users must fix issues hook detected, not bypass hooks

4. **Test-runner handles verbose output** (test-runner.md, lines 15, 252)
   - Executor delegates test/commit execution to avoid context pollution
   - Only summary returned to executor

5. **One commit per deliverable** (executor.md, lines 56-91)
   - RED-GREEN-REFACTOR-COMMIT cycle repeats for each task deliverable
   - Not one commit per task, but per feature/behavior within task

## Files Involved

- **agents/executor.md** - Lines 83-91 (commit syntax)
- **agents/executor.md** - Lines 56-91 (execution loop with commit phase)
- **agents/executor.md** - Lines 252 (test-runner delegation)
- **skills/test-driven-development/SKILL.md** - Lines 47-99 (TDD cycle, no commit details)
- **agents/test-runner.md** - Lines 226-247 (commit report format)
- **agents/test-runner.md** - Line 28 (git commit as command type)
- **hooks/post-tool-use/03-block-pre-commit-bash.py** - Lines 13-43 (blocking patterns)
