---
name: analyzing-test-effectiveness
description: Use to audit test quality with Google Fellow SRE scrutiny - dispatches the test-effectiveness-analyst agent for the analysis, creates a bd epic with improvement tasks, then runs batch SRE refinement against the full task tree.
---

<skill_overview>
Orchestrate a test-effectiveness audit end to end: confirm scope, dispatch the test-effectiveness-analyst agent to apply Google Fellow SRE scrutiny, present its findings to the user, create a bd epic with tracked improvement tasks, and run one batch SRE review against the full tree before handing off to execution.

**CRITICAL MINDSET: Assume tests were written by junior engineers optimizing for coverage metrics.** The analyst agent applies this skeptical default — RED or YELLOW until proven GREEN, GREEN only with evidence — and reads production code before categorizing any test. This skill's job is orchestration and bd tracking, not re-deriving that methodology.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM - Follow the 5-step orchestration (Scope, Dispatch Analyst, Present Findings, Create bd Epic + Tasks, Batch SRE Review) exactly; this is the rigid spine. The categorization methodology (RED/YELLOW/GREEN criteria, corner-case categories) is rigid too, but it lives in agents/test-effectiveness-analyst.md — this skill never restates it. Task-template wording is flexible but every generated task must carry the two-tier spec sections.
</rigidity_level>

<quick_reference>
| Step | Action | Output |
|------|--------|--------|
| 1. Scope | Confirm target suites/dirs; AskUserQuestion when ambiguous | Confirmed analysis scope |
| 2. Dispatch Analyst | Blocking dispatch to hyperpowers:test-effectiveness-analyst | Full analysis report (Return Contract) |
| 3. Present Findings | Relay executive summary + counts; agree what to act on | Action decision (remove/strengthen/add) |
| 4. Create bd Epic + Tasks | Epic + up to 4 two-tier tasks, linked with dependencies | Tracked improvement plan |
| 5. Batch SRE Review | Fresh subagent runs sre-task-refinement against the full tree | APPROVE / NEEDS REVISION / REJECT + handoff |

**Methodology owner:** `agents/test-effectiveness-analyst.md` holds the RED/YELLOW/GREEN criteria, the corner-case categories, and the full analysis process (including the per-language mutation-testing commands). This skill never restates them — read the agent file directly if you need the criteria.

**bd Integration (MANDATORY):**
- Create bd epic for test quality improvement
- Create bd tasks for: remove RED, strengthen YELLOW, add corner cases, validate
- Run hyperpowers:sre-task-refinement in batch mode against the full task tree (once, not per-task)
- Link tasks to epic with dependencies
</quick_reference>

<when_to_use>
**Use this skill when:**
- Production bugs appear despite high test coverage
- Suspecting coverage gaming or tautological tests
- Before major refactoring (ensure tests catch regressions)
- Onboarding to unfamiliar codebase (assess test quality)
- After hyperpowers:review-implementation flags test quality issues
- Planning test improvement initiatives

**Don't use when:**
- Writing new tests (use hyperpowers:test-driven-development)
- Debugging test failures (use hyperpowers:debugging-with-tools)
- Just need to run tests (use hyperpowers:test-runner agent)
</when_to_use>

<the_process>
## Announcement

**Announce:** "I'm using hyperpowers:analyzing-test-effectiveness to audit test quality with Google Fellow SRE-level scrutiny."

---

## Step 1: Scope

Confirm what to analyze before dispatching:
- User named a specific module/directory/suite → use it directly
- Scope is the whole codebase or otherwise ambiguous → use AskUserQuestion to confirm target suites/dirs. Analyzing an entire monorepo in one dispatch produces a report too large to act on.

Record the confirmed scope in one sentence — it becomes the prompt for Step 2.

---

## Step 2: Dispatch Analyst

Dispatch the analysis as a fresh blocking subagent — this keeps verbose per-test justification (line-by-line RED/YELLOW breakdowns) out of the lead's context.

```
Agent tool:
  subagent_type: "hyperpowers:test-effectiveness-analyst"
  prompt: |
    Analyze test effectiveness for: [confirmed scope from Step 1].
    Apply the skeptical RED/YELLOW/GREEN methodology and corner-case
    discovery process you own. Return the complete report per your
    Output Format (Return Contract) section: executive summary,
    per-test justifications, missing corner cases, and the
    improvement plan.
```

No model override — the agent's own frontmatter pin (`model: sonnet`) governs.

The agent file owns the methodology. This skill never restates the RED/YELLOW/GREEN criteria, the corner-case categories, or the analysis process — if a finding needs more depth, ask the analyst to elaborate rather than re-deriving categories here.

---

## Step 3: Present Findings

Relay the analyst's executive summary to the user: total tests analyzed, RED/YELLOW/GREEN counts and percentages, missing corner cases, and overall assessment.

Agree with the user what to act on:
- Remove the RED tests?
- Strengthen the YELLOW tests?
- Add missing corner cases — which priority tier (P0 only, or further)?
- Validate with mutation testing once the above land?

The user's decision determines which of the four task templates in Step 4 actually get created — not every analysis warrants all four.

---

## Step 4: Create bd Epic + Tasks

### Epic

```bash
bd create "Test Quality Improvement: [Module/Project]" \
  --type epic \
  --priority 1 \
  --description "Remove tautological tests, strengthen weak ones, add missing corner cases" \
  --design "$(cat <<'EOF'
## Goal
Improve test effectiveness by removing tautological tests, strengthening weak tests, and adding missing corner case coverage.

## Success Criteria
- [ ] All RED tests removed or replaced with meaningful tests
- [ ] All YELLOW tests strengthened with proper assertions
- [ ] All P0 missing corner cases covered
- [ ] Mutation score ≥80% for P0 modules

## Scope
[Summary of modules analyzed and findings, from the Step 2 report]

## Anti-patterns
- ❌ Adding tests that only check `!= nil`
- ❌ Adding tests that verify mock behavior
- ❌ Adding happy-path-only tests
- ❌ Leaving tautological tests "for coverage"
EOF
)"
```

### Task templates

Every task below follows the two-tier spec format (`skills/common-patterns/spec-templates.md` — cite, don't restate). Only create the tasks the user agreed to act on in Step 3.

**Task: Remove Tautological Tests — classification: simple**

```bash
bd create "Remove tautological tests from [module]" \
  --type task \
  --priority 0 \
  --description "Delete RED-rated tests that pass regardless of code correctness" \
  --design "$(cat <<'EOF'
## Goal
Delete the RED-rated tests the analyst identified — they pass regardless of code correctness and provide false confidence.

## Why
Tautological and mock-testing tests inflate coverage without catching bugs. They must come out before the strengthen task, so effort isn't spent polishing tests that are about to be deleted.

## Changes
- `[file:line]` - [test name]: delete ([one-line reason from the analyst's RED section])
[... one line per RED test in the analyst's report]

## Verification
- Test suite still passes after deletion: [project test command]
- None of the deleted test names remain in the suite (grep the suite for each name)
EOF
)"
```

**Task: Strengthen Weak Tests — classification: medium**

```bash
bd create "Strengthen weak assertions in [module]" \
  --type task \
  --priority 1 \
  --description "Replace YELLOW-rated weak assertions with exact-value checks and missing edge cases" \
  --design "$(cat <<'EOF'
## Goal
Replace each YELLOW test's weak assertion with an exact-value check, and add the edge cases the analyst flagged as missing from happy-path-only tests.

## Why
A weak assertion or happy-path-only test passes even when the production logic is wrong — strengthening these is what turns high coverage into bug-catching coverage. Depends on the removal task landing first, so strengthening isn't wasted on soon-to-be-deleted tests.

## Context
Read the analyst's YELLOW section for each test below — it already has the file:line breakdown, the current weak assertion, and the specific bug that slips through.

## Implementation
For each YELLOW test in the analyst's report:
- `[file:line]` - [test name]: current `[weak assertion]` → strengthen to `[exact-value assertion]`
[... one line per YELLOW test]

## Tests
Each strengthened test must name the specific bug it now catches (test name or adjacent comment) and assert exact production values — never `!= nil`, `> 0`, or `toBeDefined()`.

## Verification
- Test suite passes with the strengthened assertions: [project test command]
- No remaining weak-assertion patterns (`!= nil`, `not.toBeNull()`, etc.) in the listed files

## Boundaries
Do not add new corner-case tests here — that is the next task. Do not touch tests outside the YELLOW list from the analyst's report.
EOF
)"
```

**Task: Add Missing Corner Cases — classification: medium**

```bash
bd create "Add missing corner case tests for [module]" \
  --type task \
  --priority 1 \
  --description "Cover the P0 corner cases the analyst identified as missing" \
  --design "$(cat <<'EOF'
## Goal
Add tests for the P0 corner cases the analyst's report flagged as missing, using TDD.

## Why
Missing corner cases (empty input, unicode, concurrency, injection) are exactly where production bugs hide despite high coverage — this is the epic's actual coverage gain, not cleanup. Depends on the strengthen task so new tests follow the same exact-assertion bar.

## Context
Read the analyst's "Missing Corner Case Tests" table for the module(s) in scope — it lists each corner case, its bug risk, and a recommended test name.

## Implementation
For each corner case in the analyst's table:
1. Write the failing test first (RED)
2. Run it — confirm it fails for the right reason
3. Implement the minimal production fix if the corner case reveals a real gap
4. Run it — confirm it passes (GREEN)

Corner cases to add (from the analyst's report):
- [recommended test name] - prevents [bug risk]
[... one line per P0 corner case]

## Tests
Each new test must document the specific bug it prevents (test name or comment) and use a meaningful assertion — no line-hitters.

## Verification
- All new tests pass: [project test command]
- Spot-check 1-2 new tests by manually removing the corresponding production guard and confirming the test fails

## Boundaries
Limit to the P0 corner cases from the analyst's report. P1/P2 cases become follow-up tasks only if the user asked for them in Step 3.
EOF
)"
```

**Task: Validate with Mutation Testing — classification: simple**

```bash
bd create "Validate test improvements with mutation testing" \
  --type task \
  --priority 1 \
  --description "Prove the improved suite catches more bugs via mutation score" \
  --design "$(cat <<'EOF'
## Goal
Run mutation testing against the improved suite and confirm the mutation score meets the epic's target.

## Why
Coverage alone is a vanity metric — this epic exists because of it. Mutation score is the evidence that removing RED tests, strengthening YELLOW tests, and adding corner cases actually improved bug-catching ability. Depends on the prior three tasks.

## Changes
- Run the mutation-testing tool for the project's language (see `agents/test-effectiveness-analyst.md` Output Format for the per-language command — Pitest/Stryker/mutmut/Stryker.NET)
- If the score is below target, list surviving mutants and open follow-up tasks to kill them — do not lower the target

## Verification
- P0 modules: mutation score ≥80%
- P1 modules: mutation score ≥70%
- No surviving mutants in critical paths (auth, payments)
EOF
)"
```

### Link Tasks to Epic

```bash
# Link all tasks as children of epic
bd dep add bd-2 bd-1 --type parent-child
bd dep add bd-3 bd-1 --type parent-child
bd dep add bd-4 bd-1 --type parent-child
bd dep add bd-5 bd-1 --type parent-child

# Set dependencies (remove before strengthen before add before validate)
bd dep add bd-3 bd-2  # strengthen depends on remove
bd dep add bd-4 bd-3  # add depends on strengthen
bd dep add bd-5 bd-4  # validate depends on add
```

---

## Step 5: Batch SRE Review

**MANDATORY. Do not skip.**

Dispatch SRE task refinement as a fresh blocking subagent — this session authored the improvement tasks, so the review must come from a context that did not.

```
Agent tool:
  subagent_type: "general-purpose"
  mode: "bypassPermissions"
  prompt: |
    Load the skill hyperpowers:sre-task-refinement with the Skill tool and
    run its BATCH MODE against epic <epic-id> (the test improvement tasks).
    Inputs: bd show <epic-id>, then bd show each child task.
    You may strengthen task specs directly via bd update (preserve existing
    sections; never insert placeholders). Do not create, close, or
    re-classify tasks — structural suggestions go in your report.
    Return: the batch verdict (APPROVE / NEEDS REVISION / REJECT), the
    cross-task analysis including the epic-coverage table, per-task
    one-liners, and an exact list of bd updates you applied.
```

Do not pass a model override — the review inherits the session model.

The review applies all 8 categories across the task tree, especially:
- **Category 8 (Test Meaningfulness)**: Verify the proposed tests actually catch bugs
- **Category 6 (Edge Cases)**: Ensure corner cases are comprehensive
- **Category 3 (Success Criteria)**: Ensure criteria are measurable

SRE refinement runs once against the full task tree — not per-task.

On APPROVE (or NEEDS REVISION resolved via the bd updates above), hand off to hyperpowers:executing-plans to implement the tasks.

---

## Output Format

```markdown
# Test Effectiveness Analysis: [Project Name]

## Executive Summary

| Metric | Count | % |
|--------|-------|---|
| Total tests analyzed | N | 100% |
| RED (remove/replace) | N | X% |
| YELLOW (strengthen) | N | X% |
| GREEN (keep) | N | X% |
| Missing corner cases | N | - |

**Overall Assessment:** [CRITICAL / NEEDS WORK / ACCEPTABLE / GOOD]

## Detailed Findings

### RED Tests (Must Remove/Replace)

#### Tautological Tests
| Test | File:Line | Problem | Action |
|------|-----------|---------|--------|

#### Mock-Testing Tests
| Test | File:Line | Problem | Action |
|------|-----------|---------|--------|

#### Line Hitters
| Test | File:Line | Problem | Action |
|------|-----------|---------|--------|

#### Evergreen Tests
| Test | File:Line | Problem | Action |
|------|-----------|---------|--------|

### YELLOW Tests (Must Strengthen)

#### Weak Assertions
| Test | File:Line | Current | Recommended |
|------|-----------|---------|-------------|

#### Happy Path Only
| Test | File:Line | Missing Edge Cases |
|------|-----------|-------------------|

### GREEN Tests (Exemplars)

[List 3-5 tests that exemplify good testing practices for this codebase]

## Missing Corner Cases by Module

### [Module: name] - Priority: P0
| Corner Case | Bug Risk | Recommended Test |
|-------------|----------|------------------|

[Repeat for each module]

## bd Issues Created

### Epic
- **bd-N**: Test Quality Improvement: [Project Name]

### Tasks
| bd ID | Task | Priority | Status |
|-------|------|----------|--------|
| bd-N | Remove tautological tests from [module] | P0 | Created |
| bd-N | Strengthen weak assertions in [module] | P1 | Created |
| bd-N | Add missing corner case tests for [module] | P1 | Created |
| bd-N | Validate with mutation testing | P1 | Created |

### Dependency Tree
```
bd-1 (Epic: Test Quality Improvement)
├── bd-2 (Remove tautological tests)
├── bd-3 (Strengthen weak assertions) ← depends on bd-2
├── bd-4 (Add corner case tests) ← depends on bd-3
└── bd-5 (Validate with mutation testing) ← depends on bd-4
```

## SRE Task Refinement Status

- [ ] One batch SRE review dispatched against the full task tree (not per-task)
- [ ] Verdict recorded: APPROVE / NEEDS REVISION / REJECT
- [ ] Category 8 (Test Meaningfulness) and Category 6 (Edge Cases) covered in the cross-task analysis
- [ ] Success criteria are measurable across the tree
- [ ] Anti-patterns specified per task

## Next Steps

1. Run `bd ready` to see tasks ready for implementation
2. Implement tasks using hyperpowers:executing-plans
3. Run validation task to verify improvements
```
</the_process>

<examples>
<example>
<scenario>High coverage but production bugs keep appearing</scenario>

<code>
# Test suite stats
Coverage: 92%
Tests: 245 passing

# Yet production issues:
- Auth bypass via empty password
- Data corruption on concurrent updates
- Crash on unicode usernames
</code>

<why_it_fails>
- Coverage measures execution, not assertion quality
- Tests likely tautological or weak assertions
- Corner cases (empty, concurrent, unicode) not tested
- High coverage created false confidence
</why_it_fails>

<correction>
**Orchestrate the audit instead of re-deriving the criteria:**

Step 1 (Scope): Confirm target — `auth.test.ts`, `user.test.ts`, `data.test.ts` in `src/`.

Step 2 (Dispatch Analyst): Blocking dispatch to hyperpowers:test-effectiveness-analyst with the confirmed scope. It returns the full report — per-test justifications, missing corner cases, improvement plan — this skill never re-derives the RED/YELLOW/GREEN criteria that produced it.

Step 3 (Present Findings): Relay the executive summary.
```markdown
| Metric | Count |
|--------|-------|
| RED | 2 |
| YELLOW | 1 |
| GREEN | 1 |
| Missing corner cases (P0) | 3 |
```
Agree with the user: remove the 2 RED tests, strengthen the 1 YELLOW test, add the 3 P0 corner cases (empty password, unicode username, concurrent login).

Step 4 (Create bd Epic + Tasks):
```
bd-1 (Epic: Test Quality Improvement - auth/data)
├── bd-2 (Remove 2 RED tests)
├── bd-3 (Strengthen 1 YELLOW test) ← depends on bd-2
└── bd-4 (Add 3 P0 corner case tests) ← depends on bd-3
```

Step 5 (Batch SRE Review): Fresh subagent runs sre-task-refinement once against bd-1's full tree. APPROVE hands off to executing-plans.

**Result:** Production bugs (auth bypass, unicode crash, concurrent corruption) become tracked, reviewed work instead of vanishing behind a 92% coverage number.
</correction>
</example>
</examples>

<critical_rules>
## Rules That Have No Exceptions

1. **Methodology lives in the agent file** → agents/test-effectiveness-analyst.md owns RED/YELLOW/GREEN criteria and corner-case categories; cite it, never restate or re-derive it here
2. **Dispatch, don't analyze** → The analyst runs as a blocking subagent; never perform the categorization in the lead's own context
3. **Confirm scope before dispatching** → Ambiguous or whole-codebase scope gets AskUserQuestion first, not a guess
4. **Every generated task carries its two-tier spec sections** → Goal, Why, Boundaries (and the rest of `skills/common-patterns/spec-templates.md`) are non-negotiable per task
5. **All findings tracked in bd** → Create epic + tasks for every issue found
6. **Batch SRE review, not per-task** → Run hyperpowers:sre-task-refinement as a batch SRE review against the full task tree (once, as a fresh subagent) before execution

## Common Excuses

All of these mean: **STOP. You're skipping the orchestration process.**

- "I'll just fix these without bd" (Untracked work = forgotten work)
- "SRE refinement is overkill for test fixes" (Test tasks need same rigor as feature tasks)
- "I'll restate the RED/YELLOW/GREEN criteria here for clarity" (Methodology lives in agents/test-effectiveness-analyst.md — restating it here creates drift between the two)
</critical_rules>

<verification_checklist>
Before completing analysis:

**Scope & Dispatch (MANDATORY):**
- [ ] Scope confirmed before dispatch (named directly, or confirmed via AskUserQuestion when ambiguous)
- [ ] Analyst dispatched as a blocking subagent; full report received per its Output Format (Return Contract)
- [ ] Findings presented to the user and action agreed (remove/strengthen/add/validate)

**Per module:**
- [ ] Every generated task conforms to its two-tier spec template

**Overall:**
- [ ] Executive summary with counts and percentages
- [ ] Detailed findings table for each category
- [ ] Missing corner cases documented per module

**bd Integration (MANDATORY):**
- [ ] Created bd epic for test quality improvement
- [ ] Created bd tasks for each category (remove, strengthen, add)
- [ ] Linked tasks to epic with parent-child relationships
- [ ] Set task dependencies (remove → strengthen → add → validate)
- [ ] Ran a batch SRE review against the full task tree (once, as a fresh subagent, via hyperpowers:sre-task-refinement)
- [ ] Created validation task with mutation testing

**SRE Refinement Verification:**
- [ ] Category 8 (Test Meaningfulness) covered in the batch review's cross-task analysis
- [ ] Success criteria are measurable (not "tests work")
- [ ] Anti-patterns specified for each task
- [ ] No placeholder text in task designs

**Validation:**
- [ ] Would removing RED tests lose any bug-catching ability? (No = correct)
- [ ] Would strengthening YELLOW tests catch more bugs? (Yes = correct)
- [ ] Would adding corner cases catch known production bugs? (Yes = correct)
</verification_checklist>

<integration>
**This skill is called by:**
- hyperpowers:review-implementation (when test quality issues flagged)
- User request to audit test quality
- Before major refactoring efforts

**This skill calls (MANDATORY):**
- hyperpowers:sre-task-refinement (batch SRE review against the full task tree, once, as a fresh subagent)
- hyperpowers:test-runner agent (to run tests during analysis)
- hyperpowers:test-effectiveness-analyst agent (dispatched in Step 2 — owns the analysis methodology)

**This skill creates:**
- bd epic for test quality improvement
- bd tasks for removing, strengthening, and adding tests
- bd validation task with mutation testing

**Workflow chain:**
```
analyzing-test-effectiveness
    ↓ (creates bd issues)
sre-task-refinement BATCH MODE (full task tree, once)
    ↓ (refines tasks)
executing-plans (implements tasks + reviewer gate verifies quality)
    ↓ (on-demand re-check available)
review-implementation (re-verification)
```

**This skill informs:**
- hyperpowers:sre-task-refinement (test specifications in plans)
- hyperpowers:test-driven-development (what makes a good test)

**Mutation testing:** the analyst recommends per-language mutation tooling in its report — see the Mutation Testing Recommendations section of agents/test-effectiveness-analyst.md.
</integration>

<resources>
**Research sources:**
- [Google Testing Blog: Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)
- [Software Testing Anti-patterns](https://blog.codepipes.com/testing/software-testing-antipatterns.html)
- [Tautological Tests](https://randycoulman.com/blog/2016/12/20/tautological-tests/)
- [Mutation Testing Guide](https://mastersoftwaretesting.com/testing-fundamentals/types-of-testing/mutation-testing)
- [Codecov: Beyond Coverage Metrics](https://about.codecov.io/blog/measuring-the-effectiveness-of-test-suites-beyond-code-coverage-metrics/)
- [Google SRE: Testing Reliability](https://sre.google/sre-book/testing-reliability/)

**Key insight from Google:** "Coverage mainly tells you about code that has no tests: it doesn't tell you about the quality of testing for the code that's 'covered'."

**When stuck:**
- Analyst's report is thin or a category call looks wrong → don't re-derive the categorization here; ask the analyst to elaborate, or surface the specific call to the user to override with rationale.
- Scope came back too large to act on → re-scope to a subdirectory/suite and re-dispatch (Step 1).
- User wants to skip bd tracking → hold; untracked improvements get lost (see Common Excuses).
</resources>
