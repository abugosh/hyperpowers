# bd Task Naming and Quality Guidelines

This guide covers best practices for naming tasks, setting priorities, sizing work, and defining success criteria.

## Task Naming Conventions

### Principles

- **Actionable**: Start with action verbs (add, fix, update, remove, refactor, implement)
- **Specific**: Include enough context to understand without opening
- **Consistent**: Follow project-wide templates

### Templates by Task Type

#### User Stories

**Template:**
```
As a [persona], I want [something] so that [reason]
```

**Examples:**
```
As a customer, I want one-click checkout so that I can purchase quickly
As an admin, I want bulk user import so that I can onboard teams efficiently
As a developer, I want API rate limiting so that I can prevent abuse
```

**When to use:** Features from user perspective

#### Bug Reports

**Template 1 (Capability-focused):**
```
[User type] can't [action they should be able to do]
```

**Examples:**
```
New users can't view home screen after signup
Admin users can't export user data to CSV
Guest users can't add items to cart
```

**Template 2 (Event-focused):**
```
When [action/event], [system feature] doesn't work
```

**Examples:**
```
When clicking Submit, payment form doesn't validate
When uploading large files, progress bar freezes
When session expires, user isn't redirected to login
```

**When to use:** Describing broken functionality

#### Tasks (Implementation Work)

**Template:**
```
[Verb] [object] [context]
```

**Examples:**
```
feat(auth): Implement JWT token generation
fix(api): Handle empty email validation in user endpoint
test: Add integration tests for payment flow
refactor: Extract validation logic from UserService
docs: Update API documentation for v2 endpoints
```

**When to use:** Technical implementation tasks

#### Features (High-Level Capabilities)

**Template:**
```
[Verb] [capability] for [user/system]
```

**Examples:**
```
Add dark mode toggle for Settings page
Implement rate limiting for API endpoints
Enable two-factor authentication for admin users
Build export functionality for report data
```

**When to use:** Feature-level work (may become epic with multiple tasks)

### Context Guidelines

- **Which component**: "in login flow", "for user API", "in Settings page"
- **Which user type**: "for admins", "for guests", "for authenticated users"
- **Avoid jargon** in user stories (user perspective, not technical)
- **Be specific** in technical tasks (exact API, file, function)

### Good vs Bad Names

**Good names:**
- `feat(auth): Implement JWT token generation`
- `fix(api): Handle empty email validation in user endpoint`
- `As a customer, I want CSV export so that I can analyze my data`
- `test: Add integration tests for payment flow`
- `refactor: Extract validation logic from UserService`

**Bad names:**
- `fix stuff` (vague - what stuff?)
- `implement feature` (vague - which feature?)
- `work on backend` (vague - what work?)
- `Report` (noun, not action - should be "Generate Q4 Sales Report")
- `API endpoint` (incomplete - "Add GET /users endpoint" better)

## Priority Guidelines

Use bd's priority system consistently:

- **P0:** Critical production bug (drop everything)
- **P1:** Blocking other work (do next)
- **P2:** Important feature work (normal priority)
- **P3:** Nice to have (do when time permits)
- **P4:** Someday/maybe (backlog)

## Granularity Guidelines

Task size bands are defined once, in
`skills/common-patterns/pipeline-constants.md` (Task Classification) — that
file is the source of truth; this section is a brief pointer, not a restatement:

- **Simple (2-5 min):** mechanical changes with exact known edits, no
  judgment required. Uses the simple task spec.
- **Medium (5-30 min):** changes requiring judgment or design decisions.
  Uses the medium task spec.
- **Hard ceiling: 30 minutes.** Any task estimated above the ceiling must be
  split before execution, not accepted as-is — see pipeline-constants.md for
  the exact rule.

**Too small:**
- Estimated well under 2 minutes on its own
- Too granular to track as an independent task
- Fold it into a related task instead of creating a standalone one

## Defining done in task specs

Under the two-tier spec model (`skills/common-patterns/spec-templates.md`),
task completion is not a per-task checklist plus a separately-referenced
universal quality checklist. The two questions that framework used to split
across two sections are now answered by parts of the spec itself:

- **"Does it work?"** → the spec's own **Verification** section: exact
  commands with expected outcomes, checked by actually running them. This is
  what a per-task acceptance-style checklist used to capture — instead of
  prose bullets asserting behavior, the executor runs a command and reads
  real output.
- **"Is it done?"** → the simple tier's Verification section ends with the
  standing line "Pre-commit hooks passing"; the medium tier adds a Tests
  section (RED/GREEN/refactor) ahead of Verification. This is what a
  universal done-checklist used to capture — code review, tests passing,
  lint clean. Task specs never carry their own checkbox-criteria section for
  this; broader release-readiness criteria (the old done-checklist's role)
  live at the epic level, in the epic's own design — owned by
  brainstorming — not duplicated into every task.

Both tiers' full field lists and template bodies are defined once in
`skills/common-patterns/spec-templates.md` — don't reproduce them here.

**Worked example (simple tier — a rename):**

```markdown
## Goal
Rename `getUserData()` to `fetchUserProfile()` in `src/api/users.ts` to
match the naming convention used by the other fetch* functions in this file.

## Why
Callers currently have to guess between `get*` and `fetch*` naming for this
one function; fixing the holdout keeps the file internally consistent before
the next task adds `fetchUserSettings()` beside it.

## Changes
- `src/api/users.ts` line 42: rename `getUserData` to `fetchUserProfile`
- `src/api/users.ts`: update the 3 in-file call sites to the new name
- `src/components/Profile.tsx` line 18: update the one external call site

## Verification
- `grep -rn "getUserData" src/` → 0 hits
- `npm test -- users.test.ts` → all passing
- Pre-commit hooks passing
```

## Dependency Management

**Good dependency usage:**
- Technical dependency (feature B needs feature A's code)
- Clear ordering (must do A before B)
- Unblocks work (completing A unblocks B)

**Bad dependency usage:**
- "Feels like should be done first" (vague)
- No technical relationship (just preference)
- Circular dependencies (A depends on B depends on A)
