---
name: wave-planning
description: Use after brainstorming when Parallelism Map shows 3+ independent streams - creates waves of parallelizable tasks with beads dependencies for team execution
---

<skill_overview>
Analyze the Parallelism Map from a bd epic and create batches of parallelizable tasks (waves) with beads dependencies and file ownership boundaries, then run SRE refinement on the wave batch. Only creates one wave at a time — subsequent waves are created after learning from previous wave results.
</skill_overview>

<rigidity_level>
LOW FREEDOM - Follow exact process: load epic, validate map, create Wave 1 tasks only, run SRE refinement on each, present wave summary, STOP. Do not create multiple waves upfront. Do not skip SRE refinement. Do not skip file ownership validation.
</rigidity_level>

<quick_reference>

| Step | Action | Critical Rule |
|------|--------|---------------|
| **Load Epic** | `bd show <epic-id>` | Extract Parallelism Map section |
| **Validate Map** | Check 3+ independent streams | Error if <3 — should have taken solo path |
| **Validate Files** | Check file ownership conflicts | No two wave tasks claim same exclusive file |
| **Create Wave Tasks** | `bd create` for each stream in wave | ONLY current wave — never all waves upfront |
| **Set Dependencies** | `bd dep add` for parent-child and blocking | Wave tasks are siblings (no blocking between them) |
| **SRE Refinement** | Run `sre-task-refinement` on each task | Never skip — each task needs corner-case analysis |
| **Present Summary** | Wave composition + file ownership matrix | STOP for user review before team execution |

**FORBIDDEN:** Creating all waves upfront. Only create the current wave.

</quick_reference>

<when_to_use>
**Use after brainstorming creates an epic with a Parallelism Map showing 3+ independent streams.**

This skill sits in the team execution path:
```
brainstorming → sre-task-refinement → wave-planning → team-executing-plans
```

Symptoms you need this:
- Epic has Parallelism Map with 3+ independent streams
- User chose team execution path during brainstorming handoff
- Need to create parallelizable task batches for agent teams

**Don't use when:**
- <3 independent streams (use writing-plans → executing-plans solo path)
- No Parallelism Map in epic (run brainstorming first)
- Tasks already created for current wave (use team-executing-plans)
- Executing solo workflow (use executing-plans)
</when_to_use>

<the_process>

## 0. Resumption Check

When invoked, check current state:

```bash
bd show <epic-id>           # Load epic with Parallelism Map
bd list --status open        # Check for existing wave tasks
bd list --status in_progress # Check for active tasks
```

**Fresh start (no wave tasks exist):** Proceed to Step 1.

**Resuming after wave completion:** team-executing-plans completed a wave and handed back. Load epic, check which streams are done, determine next wave, proceed to Step 2 with next wave's streams.

**Wave tasks already exist but not started:** Skip to Step 5 (present summary).

## 1. Load Epic and Extract Parallelism Map

```bash
bd show <epic-id>  # Load full epic
```

Extract from the epic:
- **Requirements (IMMUTABLE)** — these go into every wave task
- **Anti-Patterns (FORBIDDEN)** — these go into every wave task
- **Parallelism Map** — the source for wave composition:
  - Independent Work Streams (names, scopes, complexity)
  - Stream Dependencies (which streams block others)
  - Suggested Waves (initial groupings from brainstorming)
  - File Ownership Boundaries (exclusive + shared files)
  - Parallelism Assessment (confirmation of team path)

**Validate 3+ independent streams exist:**
- If <3 streams: ERROR — this epic should have taken the solo path. Recommend `writing-plans → executing-plans` instead.
- If 3+ streams: Continue.

## 2. Validate File Ownership Boundaries

Before creating tasks, check for file conflicts within the target wave:

**For each pair of streams in the wave:**
1. Compare "Owns (exclusive)" columns
2. If two streams claim the same exclusive file → CONFLICT

**Handling conflicts:**

**Option A — Coordination task:** Create a separate task that modifies the shared file BEFORE the conflicting streams start. This task runs in a prior wave or as a prerequisite within the current wave.

**Option B — Sequencing:** Move one of the conflicting streams to the next wave. The first stream modifies the shared file, the second stream uses the stable version.

**Handling shared files (from "Shared (needs coordination)" column):**
- Shared files listed in the Parallelism Map are expected to need coordination
- Verify the shared file is handled by an infrastructure/coordination stream (often in Wave 1)
- If no coordination stream exists, create one

**Present conflict resolution to user when shared files detected:**
```markdown
### File Ownership Conflict Detected

**Shared file:** `routes/auth.ts`
**Streams affected:** Google OAuth (Stream 1), GitHub OAuth (Stream 2)

**Option A:** Create coordination task for `routes/auth.ts` in Wave 1 that sets up the routing scaffold. Streams 1 and 2 then only add their own route handlers in Wave 2.

**Option B:** Sequence Streams 1 and 2 into separate waves. Stream 1 modifies `routes/auth.ts` in Wave 2, Stream 2 uses stable version in Wave 3.

**Recommended:** [Option A/B with reasoning]
```

Use AskUserQuestion to confirm resolution approach.

## 3. Create Wave Tasks

**CRITICAL: Only create tasks for the CURRENT wave. Never create all waves upfront.**

Determine which wave to create:
- First invocation: Create Wave 1 (streams with no dependencies, or infrastructure streams)
- After Wave N completes: Create Wave N+1 (streams unblocked by Wave N completion)

**For each stream in the current wave, create a bd task:**

```bash
bd create "Wave N: [Stream Name]" \
  --type task \
  --priority [match-epic] \
  --design "$(cat <<'EOF'
## Goal
[What this stream delivers — from Parallelism Map]

## Epic Context
**Epic:** <epic-id>
**Requirements (IMMUTABLE):**
[Copy relevant requirements from epic — teammates need the contract]

**Anti-Patterns (FORBIDDEN):**
[Copy anti-patterns from epic — teammates need the constraints]

## File Ownership
**This task OWNS (exclusive — only this task modifies these files):**
- [file paths from Parallelism Map]

**This task MUST NOT modify (owned by other streams):**
- [file paths owned by other wave tasks]

**Shared files (coordination handled by [task/wave]):**
- [shared file paths and how coordination is managed]

## Implementation
[Detailed steps for this stream]

1. Study existing code
   [Point to relevant files and patterns]

2. Write tests first (TDD)
   [Specific test cases for this stream]

3. Implementation checklist
   - [ ] [exact file: what to create/modify]
   - [ ] [test file: what scenarios to test]

## Success Criteria
- [ ] [Specific, measurable outcome for this stream]
- [ ] All tests passing
- [ ] No modifications to files outside ownership boundary
- [ ] Pre-commit hooks passing
EOF
)"

# Link to epic
bd dep add <task-id> <epic-id> --type parent-child
```

**Key rules for wave tasks:**
- Wave tasks within the same wave have NO blocking dependencies between them (they're parallel)
- Wave tasks depend on the epic (parent-child)
- Wave N+1 tasks may block on Wave N tasks (sequential dependency between waves)
- Every task includes epic requirements and anti-patterns (teammates need the full contract)
- Every task includes file ownership boundaries (teammates need to know what NOT to touch)

## 4. Run SRE Refinement on Wave Batch

**REQUIRED for every wave task. Never skip.**

For each task created in Step 3:

```
Use Skill tool: hyperpowers:sre-task-refinement
```

SRE refinement will:
- Apply 8-category corner-case analysis
- Strengthen success criteria
- Identify edge cases specific to this stream
- Verify file ownership boundaries are complete
- Ensure task is teammate-ready (junior engineer test)

**After refinement, verify each task with:**
```bash
bd show <task-id>  # Confirm no placeholder text, all sections complete
```

## 5. Present Wave Summary and STOP

**Present the complete wave plan to user:**

```markdown
## Wave N Ready for Review

### Wave Composition
| Task | Stream | Complexity | Key Deliverable |
|------|--------|------------|-----------------|
| bd-X | [Name] | [low/med/high] | [What it delivers] |
| bd-Y | [Name] | [low/med/high] | [What it delivers] |
| bd-Z | [Name] | [low/med/high] | [What it delivers] |

### File Ownership Matrix
| File | bd-X | bd-Y | bd-Z |
|------|------|------|------|
| [path] | owns | — | — |
| [path] | — | owns | — |
| [path] | — | — | owns |
| [shared] | reads | reads | — |

### Dependency Graph
- All Wave N tasks are independent (no blocking between them)
- [Any sequential dependencies from previous waves]

### Epic Progress
- Streams completed: [X/Y]
- Streams in this wave: [N]
- Streams remaining after this wave: [M]

### SRE Refinement Status
- bd-X: Refined (edge cases added: [summary])
- bd-Y: Refined (edge cases added: [summary])
- bd-Z: Refined (edge cases added: [summary])

### Next Steps
Approve this wave to proceed to team execution.
Run `/hyperpowers:execute-wave` to spawn agent teams for this wave.
```

**STOP for user review. Do not proceed to team execution without approval.**

User may:
- Approve → Hand off to team-executing-plans
- Request changes → Modify tasks, re-run SRE refinement
- Cancel → Delete wave tasks, return to solo path

</the_process>

<examples>

<example>
<scenario>5 independent streams across 2 waves — correct wave planning</scenario>

<code>
Epic bd-1 has Parallelism Map:

### Independent Work Streams
1. **Shared Infrastructure** (auth/passport-config.ts, db/models/user.ts)
   - Session handling, user model updates, callback routing
   - Estimated complexity: low
2. **Google OAuth** (auth/strategies/google.ts, tests/auth/google.spec.ts)
   - Google OAuth2 strategy implementation
   - Estimated complexity: medium
3. **GitHub OAuth** (auth/strategies/github.ts, tests/auth/github.spec.ts)
   - GitHub OAuth strategy implementation
   - Estimated complexity: medium
4. **Facebook OAuth** (auth/strategies/facebook.ts, tests/auth/facebook.spec.ts)
   - Facebook OAuth strategy implementation
   - Estimated complexity: medium
5. **OAuth UI Components** (components/login/*, tests/components/login.spec.ts)
   - Login buttons, callback handling, error states
   - Estimated complexity: medium

### Stream Dependencies
- Streams 2, 3, 4 depend on Stream 1 (shared infrastructure first)
- Stream 5 depends on Streams 2, 3, 4 (UI needs strategy implementations)
- Streams 2, 3, 4 are fully independent of each other

### Suggested Waves
- Wave 1: Stream 1 (infrastructure — must come first)
- Wave 2: Streams 2, 3, 4 (all providers in parallel)
- Wave 3: Stream 5 (UI depends on providers)

---

**Wave-planning creates Wave 1 only:**

bd create "Wave 1: Shared Infrastructure" \
  --type task \
  --design "[Full design with epic requirements, anti-patterns,
    file ownership: owns auth/passport-config.ts, db/models/user.ts, routes/auth.ts
    must-not-touch: auth/strategies/*, components/login/*]"

bd dep add bd-2 bd-1 --type parent-child

# Run SRE refinement on bd-2

## Wave 1 Ready for Review

| Task | Stream | Complexity | Key Deliverable |
|------|--------|------------|-----------------|
| bd-2 | Shared Infrastructure | low | Session handling, user model, routing scaffold |

Epic Progress: 0/5 streams complete, 1 in this wave, 4 remaining
Next: After Wave 1 completes, create Wave 2 (3 providers in parallel)
</code>

<why_it_fails>
N/A — this is the correct pattern. Wave 1 has only 1 task (infrastructure), so it could run as solo execution. After it completes, Wave 2 with 3 parallel tasks is created. Wave 3 (UI) is created only after Wave 2 results are known.
</why_it_fails>

<correction>
This example demonstrates correct behavior:

1. **Only Wave 1 created** — not all 3 waves upfront
2. **Infrastructure first** — shared file ownership is clear
3. **File ownership explicit** — Wave 1 owns shared files, Wave 2 tasks must not touch them
4. **SRE refinement run** — before presenting summary
5. **STOP checkpoint** — user reviews before execution

**After Wave 1 completes, wave-planning is invoked again:**
- Creates Wave 2: bd-3 (Google), bd-4 (GitHub), bd-5 (Facebook)
- Each task owns only its exclusive files
- No blocking deps between bd-3, bd-4, bd-5 (they're parallel)
- SRE refinement on each
- Present and STOP

**After Wave 2 completes:**
- Creates Wave 3: bd-6 (UI Components)
- Based on learnings from Wave 2 (maybe Facebook OAuth has different button requirements discovered during implementation)
- Task reflects reality, not original assumptions
</correction>
</example>

<example>
<scenario>Developer creates all waves upfront instead of iteratively</scenario>

<code>
Epic bd-1 has Parallelism Map with 3 waves.

Developer creates ALL tasks upfront:

# Wave 1
bd create "Wave 1: Shared Infrastructure"
# Wave 2
bd create "Wave 2: Google OAuth"
bd create "Wave 2: GitHub OAuth"
bd create "Wave 2: Facebook OAuth"
# Wave 3
bd create "Wave 3: OAuth UI Components"

# Starts executing Wave 1
# Discovers: passport-config.ts already has session handling
# Now Wave 1 task partially redundant
# Wave 2 tasks assumed certain API from Wave 1 that doesn't match reality
# Wave 3 task assumed UI patterns that Wave 2 hasn't established yet
# 4 tasks now contain incorrect assumptions
</code>

<why_it_fails>
**Violates epic anti-pattern: "NO creating full task trees upfront"**

- Wave 2 tasks were written assuming Wave 1 would produce specific APIs
- Wave 1 discoveries invalidate Wave 2 assumptions
- Wave 3 assumptions about UI patterns are premature
- 4 tasks need rewriting — wasted effort
- Upfront planning fights reality

**Why it happens:**
- Feels efficient to "batch everything"
- Developer wants to see full plan before starting
- Ignores that implementation discoveries change everything

**Result:**
- Tasks become incorrect as you learn
- Time wasted rewriting multiple tasks
- Assumptions compound (Wave 3 wrong because Wave 2 wrong because Wave 1 changed)
</why_it_fails>

<correction>
**Create only the current wave:**

```bash
# Wave 1 ONLY
bd create "Wave 1: Shared Infrastructure" --design "[detailed]"
# SRE refine → present → STOP

# After Wave 1 completes, learnings emerge:
# - passport-config.ts already has session handling (reuse, don't rewrite)
# - User model needs different fields than originally planned

# Wave 2 tasks INCORPORATE learnings:
bd create "Wave 2: Google OAuth" --design "[reflects Wave 1 reality]"
bd create "Wave 2: GitHub OAuth" --design "[reflects Wave 1 reality]"
bd create "Wave 2: Facebook OAuth" --design "[reflects Wave 1 reality]"
# SRE refine → present → STOP

# After Wave 2 completes:
# - Discovered Facebook needs different button component than Google/GitHub
# Wave 3 task INCORPORATES this learning:
bd create "Wave 3: OAuth UI Components" --design "[reflects Wave 2 reality]"
```

**What you gain:**
- Each wave's tasks reflect current reality
- No wasted effort on incorrect assumptions
- Discoveries from Wave N inform Wave N+1
- Tasks are always accurate when executed
</correction>
</example>

</examples>

<critical_rules>

## Rules That Have No Exceptions

1. **Only create current wave tasks** → Never create all waves upfront
   - Epic anti-pattern explicitly forbids this
   - Subsequent waves created after learning from previous wave results
   - Each wave's tasks reflect current reality, not original assumptions

2. **Validate file ownership before creating tasks** → No exclusive file conflicts within a wave
   - Two tasks claiming same exclusive file = merge conflict when agents execute in parallel
   - Resolve conflicts before task creation (coordination task or sequencing)

3. **Include epic context in every task** → Requirements, anti-patterns, file ownership
   - Teammates need the full contract (epic requirements are immutable)
   - Teammates need to know what NOT to touch (file ownership boundaries)
   - Teammates need the constraints (anti-patterns prevent shortcuts)

4. **Run SRE refinement on every wave task** → Never skip corner-case analysis
   - Each task needs 8-category review before agents can execute it
   - Tasks without refinement will miss edge cases
   - Use `hyperpowers:sre-task-refinement` skill

5. **STOP after presenting wave summary** → User must approve before team execution
   - User needs to review task composition, file ownership, dependencies
   - User may need to adjust tasks or resolve conflicts
   - Never proceed to team-executing-plans without explicit approval

6. **Wave tasks are independent within the wave** → No blocking deps between same-wave tasks
   - Tasks in the same wave execute in parallel — they cannot depend on each other
   - If two tasks have a dependency, they belong in different waves

7. **Wave sizing: 2-5 tasks per wave** → Below 2 use solo, above 5 coordination overhead grows
   - 1 task: Not a wave — use solo execution for this stream
   - 2 tasks: Minimum viable wave
   - 3-4 tasks: Sweet spot for agent teams
   - 5 tasks: Maximum before coordination overhead becomes significant
   - 6+ tasks: Split into two waves or combine low-complexity streams

## Wave Sizing Heuristics

**Complexity-based adjustments:**
- All low complexity: Can batch up to 5 tasks
- Mixed complexity: Keep to 3-4 tasks (high-complexity tasks take longer, leaving agents idle)
- All high complexity: Keep to 2-3 tasks (reduces blast radius if approach needs revision)

**Shared file considerations:**
- If streams share files via coordination task: Keep wave smaller (3 tasks max) to reduce integration risk
- If streams have zero shared files: Can batch more (up to 5)

**Confidence-based adjustments:**
- High confidence (well-understood domain, clear patterns): Larger waves (4-5)
- Low confidence (new domain, unclear patterns): Smaller waves (2-3) to learn faster

## Common Excuses

All of these mean: **STOP. Follow the process.**

- "Let me create all waves so we can see the full plan" → Only current wave. Full plan lives in Parallelism Map.
- "These two tasks in the same wave need each other" → Move one to next wave. Same-wave tasks must be independent.
- "SRE refinement is overkill for simple tasks" → Every task needs refinement. "Simple" tasks have hidden edge cases.
- "User already approved the epic, don't need wave approval" → Wave composition is a new decision. STOP and present.
- "File ownership is obvious, don't need validation" → Validate anyway. Conflicts cause merge failures during parallel execution.
- "This stream is too small for its own task" → Combine with related stream or include in coordination task.
- "Let me skip the infrastructure wave and go straight to features" → Dependencies exist for a reason. Infrastructure must be stable before features execute in parallel.

</critical_rules>

<verification_checklist>

Before presenting wave summary:
- [ ] Epic loaded and Parallelism Map extracted
- [ ] Verified 3+ independent streams (if <3, error — use solo path)
- [ ] File ownership validated — no exclusive file conflicts within wave
- [ ] Shared file handling resolved (coordination task or sequencing)
- [ ] Only current wave tasks created (NOT all waves)
- [ ] Each task includes: epic requirements, anti-patterns, file ownership boundaries
- [ ] Each task specifies: owns (exclusive), must-not-touch, shared (coordination)
- [ ] Wave tasks have no blocking deps between each other (they're parallel)
- [ ] All wave tasks linked to epic (parent-child)
- [ ] SRE refinement run on every wave task
- [ ] Each task verified with `bd show` — no placeholder text
- [ ] Wave sizing within 2-5 tasks (or justified exception)
- [ ] Wave summary presented with: composition table, file ownership matrix, dependency graph, SRE status
- [ ] STOPPED for user review (not proceeding to team execution)

After user approves wave:
- [ ] Hand off to team-executing-plans with wave task IDs

**Can't check all boxes?** Return to process and complete missing steps.

</verification_checklist>

<integration>

**This skill is called by:**
- hyperpowers:brainstorming (team path handoff when 3+ independent streams)
- hyperpowers:team-executing-plans (after wave completion, to create next wave)
- User (via command, to create next wave after reviewing previous wave results)

**This skill calls:**
- hyperpowers:sre-task-refinement (REQUIRED for each wave task)
- hyperpowers:team-executing-plans (handoff after wave approved by user)

**Call chain:**
```
brainstorming → sre-task-refinement → wave-planning → team-executing-plans
                                           ↑                    |
                                           |                    ↓
                                           ← (next wave) ← wave review
```

**Agents used:**
- None directly (SRE refinement and team execution are separate skills)

**bd commands used:**
- `bd show <epic-id>` — Load epic with Parallelism Map
- `bd create` — Create wave tasks
- `bd dep add <task> <epic> --type parent-child` — Link tasks to epic
- `bd dep add <task> <blocker>` — Set cross-wave dependencies
- `bd list --status open` — Check existing tasks
- `bd ready` — Find unblocked tasks

**Workflow pattern:**
```
wave-planning (Wave 1) → STOP → user approves → team-executing-plans (Wave 1)
  → wave review → wave-planning (Wave 2) → STOP → user approves → team-executing-plans (Wave 2)
  → ... → all streams complete → review-implementation → finish-branch
```

</integration>

<resources>

**Parallelism Map reference:**
The Parallelism Map is created by the brainstorming skill and lives in the epic's design field. It contains:
- Independent Work Streams (names, scopes, complexity estimates)
- Stream Dependencies (which streams block others)
- Suggested Waves (initial groupings — adapt based on learnings)
- File Ownership Boundaries (exclusive + shared files per stream)
- Parallelism Assessment (team vs solo recommendation)

**Wave sizing quick guide:**
| Scenario | Wave Size | Reason |
|----------|-----------|--------|
| All low complexity, no shared files | 4-5 | Low risk, maximum parallelism |
| Mixed complexity | 3-4 | Balance speed and coordination |
| All high complexity | 2-3 | Reduce blast radius |
| Shared files present | 3 max | Reduce integration risk |
| Low confidence domain | 2-3 | Learn faster with smaller batches |
| High confidence domain | 4-5 | Known patterns, predictable outcomes |

**When stuck:**
- Unclear which streams belong in which wave → Check Stream Dependencies in Parallelism Map
- File ownership ambiguous → Ask user to clarify; never guess file boundaries
- Stream too large for single task → Split stream into sub-streams (but keep in same wave if independent)
- Stream too small for own task → Combine with related stream
- SRE refinement rejects task → Fix issues, re-run refinement, don't skip it
- User wants all waves planned upfront → Explain iterative approach: "Parallelism Map shows the full plan. Wave tasks are created iteratively because implementation discoveries change details."

</resources>
