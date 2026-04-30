# Hyperpowers Architecture Patterns

## 1. Skill Structure Conventions

### Frontmatter (YAML)
```yaml
---
name: skill-name                          # kebab-case ID, matches directory
description: One-sentence usage guidance  # When to invoke this skill
---
```

### Content Structure (All Skills)
Every skill follows this pattern:

1. **`<skill_overview>`** - Core principle & context (1-2 sentences)
2. **`<rigidity_level>`** - HIGH FREEDOM vs LOW FREEDOM vs MEDIUM FREEDOM
   - HIGH FREEDOM: Adapt to context but follow core principle
   - MEDIUM FREEDOM: Follow pattern, adapt implementation details
   - LOW FREEDOM: Follow exactly, no adaptation
3. **`<quick_reference>`** - Scannable table summarizing steps/actions
4. **`<when_to_use>`** - Decision criteria (use/don't use)
5. **`<the_process>`** - Numbered steps with exact commands/tools
6. **`<examples>`** - 3-4 scenarios showing failure modes and corrections
7. **`<key_principles>`** or **`<critical_rules>`** - Non-negotiable rules
8. **`<verification_checklist>`** - Evidence-based completion checklist
9. **`<integration>`** - Which skills call this, which this calls, agents used
10. **`<resources>`** - Links to common-patterns/, when stuck

### Rigidity Levels (Establish Skill Personality)

**HIGH FREEDOM** (Brainstorming, Refactoring)
- Core principle immutable
- Process steps adaptive (Socratic questions change per context)
- Typical structure: Research → Propose → Validate → Deliver artifact

**MEDIUM FREEDOM** (Writing Plans, Managing BD Tasks)
- Pattern must be followed
- Implementation details adapt to codebase reality
- Typical structure: Verify → Draft → Present → Validate → Update

**LOW FREEDOM** (Executing Plans, TDD, Review Implementation)
- Step-by-step process rigid
- No skipping steps even when blocked
- Typical structure: Load context → Execute exact steps → Report evidence

## 2. Artifact/Output Model

Skills produce **artifacts** which are bd issues (epics or tasks) with structured design fields:

### Epic Artifact (from brainstorming)
Key sections in `--design` field:
- **Requirements (IMMUTABLE)** - What MUST be true
- **Success Criteria (MUST ALL BE TRUE)** - Objective, testable
- **Anti-Patterns (FORBIDDEN)** - What is explicitly prohibited (with reasoning)
- **Approach** - 2-3 paragraph summary of chosen approach
- **Architecture** - Key components, data flow, integration points
- **Design Rationale** - Problem statement, research findings, approaches considered with rejected reasoning
- **Scope Boundaries** - In scope / Out of scope (deferred/never)
- **Open Questions** - Uncertainties to resolve during execution
- **Design Discovery** (Reference Context) - Preserves brainstorming context for obstacle handling
  - Key Decisions Made (table: question → answer → implication)
  - Research Deep-Dives (per topic: findings & conclusions)
  - Dead-End Paths (why explored, why abandoned)
  - Open Concerns Raised (how addressed/deferred)

### Task Artifact (from writing-plans or iterative proposal)
Key sections in `--design` field:
- **Goal** - What this task delivers (one clear outcome)
- **Implementation** - Detailed step-by-step for this specific task
  - Point to similar implementations: `file.ts:line`
  - Test-driven: failing test → run → implement → run → refactor → commit
  - Each step includes: exact file path, complete code, exact command, expected output
- **Success Criteria** - 3+ specific, measurable criteria
- **No placeholder text** - Write actual content, not "[full implementation as detailed above]"

## 3. Skill Integration Patterns

### Call Chain Topology (Greenfield Feature Development)

```
brainstorming
    ↓
[Optional: dispatch codebase-investigator + internet-researcher]
    ↓
[Socratic questions + research findings → Design Discovery section]
    ↓
[Create bd epic with all sections]
    ↓
[Create ONLY first task]
    ↓
sre-task-refinement
    ↓
writing-plans (optional, to expand all tasks with details)
    ↓
executing-plans (spawn executor teammate)
    ↓
[executor implements tasks with TDD]
    ↓
review-implementation (verify against epic)
    ↓
finishing-a-development-branch (cleanup, PR)
```

### Skill Invocation Model

1. **Commands surface skills** - `commands/*.md` contains frontmatter + "Use skill X exactly"
2. **User types `/hyperpowers:command-name`**
3. **Command file loaded** → instructs to use Skill tool
4. **Skill tool loads `skills/*/SKILL.md`**
5. **Claude follows skill's exact process**

Commands map 1:1 to skills:
- `/brainstorm` → brainstorming skill
- `/write-plan` → writing-plans skill
- `/execute-plan` → executing-plans skill
- etc.

### Agent Dispatch Patterns

#### Pattern 1: Research Agents (Parallel, Read-Only)
Used in brainstorming to understand existing codebase + external libraries:
```
Dispatch in parallel (single message):
- codebase-investigator: "Find existing pattern for X"
- internet-researcher: "Find current API docs for Y"

Wait for both → Incorporate findings into design
```

#### Pattern 2: Executor Teammate (Persistent, Implements)
Used in executing-plans:
```
Lead creates team: TeamCreate(epic-id)
↓
Lead spawns executor: Task(team_name, name="executor")
↓
Executor reads epic + tasks
↓
Executor implements with TDD, sends structured summary after each task
↓
Lead validates proposal against epic requirements/anti-patterns
↓
Lead sends approval/redirection via SendMessage
↓
Executor continues to next task (or waits for shutdown)
```

#### Pattern 3: Reviewer Subagent (One-Shot, Verification)
Used in executing-plans after all tasks done:
```
Lead dispatches reviewer: Task(subagent_type, prompt with epic + implementations)
↓
Reviewer checks implementation against spec
↓
Returns: APPROVED or GAPS FOUND verdict
↓
If APPROVED: proceed to finishing-a-development-branch
If GAPS: executor addresses gaps (loop back)
```

#### Pattern 4: Parallel Agents (Independent Investigations)
Used in dispatching-parallel-agents for 3+ independent failures:
```
Verify independence: fix A doesn't affect B, no shared code, different error patterns
↓
Create 3+ focused prompts (scope, goal, constraints, output)
↓
Dispatch ALL in SINGLE message (multiple Task() calls)
↓
Wait for all to complete
↓
Check for conflicts (same files? contradictory decisions?)
↓
Integrate results
↓
Run full verification
```

## 4. bd/Beads Persistence Model

### Issue Types
- **epic** - Feature/initiative container, immutable requirements
- **task** - Feature implementation, specific deliverable
- **bug** - Bug report (from fixing-bugs workflow)
- **feature** - Task subtype (same as task)

### Issue Fields Available
```
id:        bd-123 (auto-assigned)
type:      epic | task | bug | feature
title:     "[Type]: Name"
status:    open | in_progress | done | closed
priority:  0-4 (higher number = more urgent)
design:    Long-form design field (primary artifact store)
notes:     Additional notes field
assignee:  Team member assignment
created:   Timestamp
updated:   Timestamp
```

### Dependency Model
- **parent-child** - Hierarchical (epic contains tasks)
- **blocking** - Task A blocks task B (can't start B until A done)
- **related** - Informational link
- **cross-epic** - Dependency between tasks in different epics

Commands:
```bash
bd create "Title" --type epic --design "..."
bd create "Title" --type task --design "..."
bd dep add bd-2 bd-1 --type parent-child  # bd-2 is child of bd-1
bd dep tree bd-1                          # Show dependency tree
bd list --parent bd-1                     # All child tasks
bd ready                                  # Tasks unblocked (no dependencies)
bd close bd-1 --reason "..."              # Mark done
```

### Design Discovery Pattern
The epic's `design` field includes a special section called "Design Discovery" that preserves:
- **Key Decisions Made** - Table of Socratic Q&A from brainstorming
- **Research Deep-Dives** - Per-topic investigation findings
- **Dead-End Paths** - Why certain approaches were abandoned (prevents re-investigation)
- **Open Concerns Raised** - How concerns were addressed

This context is referenced during execution when obstacles arise.

### No Direct JSONL Access
- `.beads/issues.jsonl` cannot be read directly (hook blocks it)
- Only use bd CLI: `bd list`, `bd show`, `bd ready`, `bd dep tree`
- Database is SQLite-backed, syncs to JSONL via daemon

## 5. Skill Handoff Patterns

### Brainstorming → SRE Refinement → Executing Plans

1. **Brainstorming completes:**
   - Epic created with immutable requirements
   - First task created (not full tree)
   - SRE refinement ready to run

2. **SRE Refinement runs:**
   - Checks 8 categories (granularity, implementability, success criteria, dependencies, safety, edge cases, red flags, test meaningfulness)
   - Strengthens task criteria
   - Auto-rejects if critical gaps found
   - Updates bd task after approval

3. **Executing Plans starts:**
   - Lead loads epic from bd (keeps context entire session)
   - Creates team: `TeamCreate(epic-id)`
   - Spawns executor: `Task(team_name="epic-id", name="executor")`
   - Executor reads epic + first task from bd
   - Executor implements with TDD (red-green-refactor-commit)
   - After each task, executor sends structured summary to lead
   - Lead validates proposal against epic (not against plan, epic is the contract)
   - Lead approves/redirects
   - Executor proposes next task (SRE refined before proposal)
   - Loop until all tasks done

4. **Review Implementation runs:**
   - Loads epic + all completed tasks from bd
   - Reviews each task: automated checks, code reading, test quality audit
   - Reports: APPROVED or GAPS FOUND
   - If approved: proceed to finishing-a-development-branch
   - If gaps: executor addresses (no lead involvement, epic is contract)

5. **Finishing Branch:**
   - Creates PR, handles cleanup

### Key Design: Lead Holds Epic Context
The lead keeps the epic in its context throughout execution (not the executor). This is the critical advantage:
- **Lead validates proposals** against epic requirements/anti-patterns continuously
- **Executor doesn't need to remember epic** - can stay focused on current task
- **Cross-task learnings preserved** in lead context (epic design discovery referenced for obstacle decisions)
- **No `/clear` cycling needed** - lead context never exhausted

## 6. Common Patterns File Structure

Located in `skills/common-patterns/`:
- `bd-commands.md` - Standard bd command examples
- `common-anti-patterns.md` - Anti-pattern examples
- `common-rationalizations.md` - Excuses that signal failure

Skills reference these rather than duplicating content (DRY principle for workflow knowledge).

## 7. Hook System

PreToolUse/PostToolUse hooks provide guardrails:
- `block-beads-direct-read.py` - Prevents direct `.beads/issues.jsonl` read (forces bd CLI)
- Other hooks prevent common mistakes (e.g., editing .git/hooks/pre-commit)

## 8. Skill Success Indicators

A well-designed skill has:
1. ✓ Clear rigidity level (not ambiguous)
2. ✓ Quick reference table (scannable decision point)
3. ✓ 3-4 examples showing common failure modes (not happy paths)
4. ✓ Critical rules with "no exceptions" framing
5. ✓ Verification checklist with boxes to tick (evidence-based)
6. ✓ Integration section showing caller/callee relationships
7. ✓ Rationalizations section (mistakes people make)
8. ✓ No placeholder text anywhere
9. ✓ Exact commands, file paths, code examples
10. ✓ Agent dispatch uses Skill tool (not assumptions about agent behavior)

## 9. Artifact Handoff Mechanism

**How artifacts flow between skills:**

1. **Brainstorming** produces: bd epic (artifact)
2. **SRE Refinement** reads: bd epic + first task, updates: task design
3. **Executing Plans** reads: bd epic + tasks, writes: closed tasks (via executor), creates: next task (via executor)
4. **Review Implementation** reads: bd epic + all completed tasks, writes: none (verdict only)
5. **Finishing Branch** reads: git state + epic, writes: PR

**bd is single source of truth:**
- Epic requirements immutable, referenced by all downstream skills
- Tasks created iteratively (one at a time), not upfront
- Task dependencies track execution order
- Design Discovery section in epic preserves research context

---

## Key Insight for Designing New Outer-Loop Skills

**The epic is a contract.** All downstream work validates against epic requirements and anti-patterns, never tries to water them down. The lead holds the epic in context throughout execution and validates every proposal. Design Discovery preserves the "why" behind decisions so obstacles can be resolved consistently.

This pattern allows skills to be relatively simple (follow the checklist) because the epic has done the hard work of nailing down requirements with Design Discovery showing what was considered and rejected.
