# Task Spec Templates (Two-Tier)

Single source of truth for the two-tier task spec format and the
prep-refactor kind. Brainstorming, writing-plans, sre-task-refinement, and
the executor all reference this file — never restate the templates.

Time bands, the hard ceiling, and the spec-depth rule are defined in
`skills/common-patterns/pipeline-constants.md`. This file carries the
template bodies and classification examples only.

Both tiers REQUIRE a Why section — the executor must understand how the task
fits the epic and what breaks if it is skipped.

## Simple task spec

Fields: Goal, Why, Changes, Verification — nothing more.

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
- Pre-commit hooks passing
```

The Verification field's final line is standing: every simple task ends with "Pre-commit hooks passing" — the executor's commit runs the hooks, making them the one universal automated check for mechanical edits. sre-task-refinement Category 3 verifies this line by citing this file.

## Medium task spec

Fields: Goal, Why, Context, Implementation, Tests, Verification, Boundaries.
The canonical field name is `## Implementation` (not "Implementation
guidance" or other variants).

```markdown
## Goal
[One sentence: what is delivered]

## Why
[How this task fits into the epic — what depends on it, what breaks if skipped]

## Context
[Key files, functions, or patterns the executor must read before starting]

## Implementation
[Step-by-step: what to create/modify/delete, with exact file paths. Follow the
spec-depth rule (skills/common-patterns/pipeline-constants.md): write intent —
goal, constraints, test cases, verification commands, boundaries. Complete code
only where the planning session verified the exact site.]

For new features (TDD):
1. Write the failing test
2. Run to confirm RED
3. Implement minimal code
4. Run to confirm GREEN
5. Refactor, keep green

Include in each step:
- Exact file path
- Complete code where the planning session verified the exact site; otherwise
  the constraints and expected shape, per the spec-depth rule
- Exact command to run
- Expected output

## Tests
[Which tests to write and what they must assert — omit this section for
pure-documentation tasks]

## Verification
[Exact commands to confirm all success criteria]

## Boundaries
[What is explicitly out of scope for this task]
```

## Standing scope

The boy-scout rule (`skills/common-patterns/prose-style.md`) applies to every
task at both tiers: noise-comment cleanup within spec-named files is always
in-scope. Specs need not restate it, and Boundaries sections do not need to
re-grant it.

## Prep-refactor kind

A task that changes no behavior and exists so a named following task's
change is small: make the change easy, then make the easy change. Either
tier may carry it. The spec declares it with one standing line directly
under `## Goal`:

    Kind: prep-refactor (for bd-<id>)

The line is a Boundary in itself: no behavior change. A change that needs a
test's expected value to move, or new behavior to land, belongs to the task
it names. There is no Tests section — there is no new behavior to test; the
existing suite is the evidence, so Verification names the suite command,
green before the change and green after. Consumers cite this section; none
restates it.

## Classification examples

Definitions and time bands live in `pipeline-constants.md`. Examples:

- **Simple:** rename, config change, documentation update, applying a
  pre-defined pattern to a file. Mechanical, exact known edits, no judgment.
- **Medium:** new component with architectural decisions, logic with
  non-obvious edge cases, test suite requiring coverage strategy. Reserved
  for irreducible complexity that cannot be fully specified upfront.

A task with an Implementation section and Tests section must be classified
as medium. A task with only exact change descriptions can be simple.
