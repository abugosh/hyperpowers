---
name: sre-task-refinement
description: Use when reviewing bd task specs before execution — checks that a cold executor with no context can run each spec, that the edge cases with consequences are covered, and that every item traces to a requirement; strengthens and trims specs directly.
---

<skill_overview>
Review bd task specs with a Google Fellow SRE perspective so that a cold executor — a fresh agent whose only context is the spec — can execute each one without questions: catch the edge cases that have consequences, verify granularity, strengthen weak criteria, and trim what no requirement needs.
</skill_overview>

<rigidity_level>
LOW FREEDOM - Rules 1-8 in critical_rules have no exceptions.
</rigidity_level>

<quick_reference>
| Category | Key Questions | Auto-Reject If |
|----------|---------------|----------------|
| 1. Granularity | Task classified simple or medium per the bands in `skills/common-patterns/pipeline-constants.md`? | Task exceeds the ceiling in `skills/common-patterns/pipeline-constants.md` without a recommended split |
| 2. Implementability | Cold executor can execute without questions? | Vague language, missing details |
| 3. Verification | Simple: 1+ measurable outcome plus the hooks line? Medium: 3+ measurable criteria? | Simple task missing a Verification section; medium task criteria can't be verified ("works well") |
| 4. Dependencies | Correct parent-child, blocking relationships? | Circular dependencies |
| 5. Safety Standards | Epic has an anti-patterns section? Risky tasks have task-level anti-patterns? | Epic missing anti-patterns section, or risky task missing task-level anti-patterns |
| 6. Edge Cases | Which failure modes reach this task, and what happens when they do? | No edge case consideration |
| 7. Red Flags | Placeholder text? Vague instructions? | "[detailed above]", "TODO" |
| 8. Test Meaningfulness | Tests catch real bugs? Not tautological? | Tests only verify syntax/existence |
| 9. Scope Proportionality | Does every implementation item and verification criterion trace to a requirement or success criterion, an anti-pattern, or a named-consequence edge case? | Never for a trim; a task whose items mostly trace to nothing is a structural finding |

**Perspective**: Google Fellow SRE with 20+ years of experience. The spec's reader is a cold executor with no context beyond the spec: anything it would have to ask is missing, and anything it does not need is cost.

**Modes**: Single-task mode (default) and batch mode (full task tree from brainstorming).
</quick_reference>

<when_to_use>
Use when:
- **Batch mode** (mainline): After brainstorming Step 6c creates the complete task tree (Step 7 calls this skill against the entire epic's task tree as a unit)
- **Single-task mode**: Against a spec that hyperpowers:writing-plans repaired or expanded off-mainline (gap-fix tasks, mid-flight amendments, externally created tasks)

Don't use when:
- Task already being implemented (too late)
- Just need to understand existing code (use codebase-investigator)
- Debugging issues (use debugging-with-tools)
- Want to create plan from scratch (use brainstorming)
</when_to_use>

<the_process>
## How This Skill Is Invoked

This skill is loaded and executed BY a dispatched review subagent — the lead dispatches a fresh subagent (Agent tool, blocking) whose prompt loads this skill and names the epic or task to review. The review never runs in the context that authored or repaired the plan: an author reviewing its own just-written tasks is the weakest possible comparator, and fresh-context review is the point of this skill. Batch mode arrives via brainstorming Step 7's dispatch block; single-task mode arrives via a dispatch after writing-plans repairs a spec.

**Authority (the one rule — stated once here, referenced everywhere else in this skill):** You may strengthen task specs directly via `bd update`, and you may remove or narrow an item in a spec when you name the reason: it fails the Category 9 trace, or it exceeds what the requirements ask. Preserve existing sections; never insert placeholders. Do not create, close, or re-classify tasks — structural suggestions (splits, new tasks, reclassification in either direction, reordering) go in your report, not in bd.

**Single-task mode:** Return your verdict and findings as your final message — it is data for the lead, not prose for a human.

**Batch mode:** Follow the Report File Contract below instead — the full report goes to a file, not the final message.

## Batch Mode (Full Task Tree Review)

Use batch mode when reviewing a complete task tree as a unit — this is required when called from brainstorming Step 7.

### Input
```bash
bd list --parent <epic-id>   # List all child tasks (bd dep tree is childless for epics in bd 0.50.x)
bd show <task-id>            # Read each child task
```

### Report File Contract (batch mode)

The dispatch prompt supplies an absolute report file path. Write the full report incrementally to that file — never hold it for a single final-message dump:

1. **Create the file at review start**, before reviewing the first task.
2. **Append each per-task review block as it is completed** (Phase 1, one task at a time). A mid-run failure must leave partial evidence on disk, not nothing — if you stop after task 3 of 10, the file holds 3 complete task reviews.
3. **Append the Cross-Task Analysis** (Phase 2) once all per-task reviews are done.
4. The file MUST end with the `### Batch Verdict` block (template in Batch Mode Output Format, below).

**Final message template (verbatim):**
```
SRE VERDICT: <APPROVE|NEEDS REVISION|REJECT> — report: <path> — <N> specs updated
```
This vocabulary is registered in `skills/common-patterns/loop-interfaces.md` (Verdict Contracts).

**Verify-before-return gate:** Before returning, confirm the report file exists and contains a verdict: `grep -c "### Batch Verdict" <path>` must return at least 1. If absent, finish the report first — a batch return without a verdict-bearing report file is a contract violation. Do not fall back to returning the report in chat if the file write failed; fix the write and confirm the gate before returning.

### Process

**Phase 1: Per-Task Review**
Apply the 9-category checklist (below) to every task in the tree. Same rigor as single-task mode — no shortcuts because there are many tasks.

**Phase 2: Cross-Task Analysis**
After reviewing each task individually, run these systemic checks:

**a. Dependency completeness**
- Do all ordering constraints have `bd dep` declarations?
- Are there implicit dependencies (task B uses output of task A) without a blocking relationship?
- Check: if task B reads a file created by task A, is there a declared dependency?

**b. Systemic gaps and systemic excess**
- Does the same missing edge case appear across multiple tasks? (e.g., no error handling for nil inputs in every data-transformation task)
- Is there a missing task that several tasks implicitly depend on (shared utility, migration, config change)?
- Are Verification sections consistently strong, or does one task have measurable checks while others use vague language?
- Does the same untraceable item repeat across tasks (a criterion no requirement sets, pasted into every Verification)? Trim it everywhere, once, with one reason.

**c. Classification consistency** (canonical templates: `skills/common-patterns/spec-templates.md`)
- Flag any task whose spec complexity doesn't match its classification (e.g., a task with full Implementation + Tests sections classified as simple)
- A correctly classified simple task is not penalized for lacking a 3+ criteria list, a 3+ item checklist, or a task-level anti-patterns section — those are medium-tier requirements (Categories 3, 5, 7)

**d. Coverage**
- Do the tasks collectively cover every success criterion in the epic?
- List each epic success criterion and map it to at least one task
- Flag any criterion with no corresponding task

### Batch Mode Output Format
This is the format of the report FILE (per the Report File Contract above), not of the final message. After per-task reviews, append a cross-task section:

```markdown
## Cross-Task Analysis

### Granularity Consistency
[Summary: all within range / exceptions listed]

### Dependency Completeness
[Summary: all declared / missing deps listed with recommendation]

### Systemic Gaps and Excess
[Any patterns found across multiple tasks — missing or over-specified — or "None found"]

### Classification Consistency
[Any mismatches between spec complexity and simple/medium label]

### Epic Coverage
| Success Criterion | Covered By |
|-------------------|------------|
| [criterion text]  | bd-N        |
| [criterion text]  | bd-N, bd-M  |
| [criterion text]  | ❌ No task covers this |

### Batch Verdict
[APPROVE ✅ / NEEDS REVISION ⚠️ / REJECT ❌]
[If NEEDS REVISION or REJECT: list recommended additions or splits]
```

---

## Review Checklist (Apply to Every Task)

### 1. Task Granularity

**Check:**
- [ ] Task classified as simple or medium per the bands in `skills/common-patterns/pipeline-constants.md`?
- [ ] No task exceeds the hard ceiling in `skills/common-patterns/pipeline-constants.md`?
- [ ] Spec carries exactly the tier's sections, with the prep-refactor and pure-documentation exceptions (`skills/common-patterns/spec-templates.md`)?
- [ ] Prep-refactor kind (`Kind:` line, `skills/common-patterns/spec-templates.md`): names a task in this tree and carries no Tests section?
- [ ] Each task independently completable?
- [ ] Each task has a clear deliverable?

**If task exceeds the ceiling in `skills/common-patterns/pipeline-constants.md`:**
- Flag the task and write a split recommendation in your report: proposed subtask titles, scope for each, and dependencies between them (see "Recommending Task Splits" below)

---

### 2. Implementability (Cold Executor Test)

**Check:**
- [ ] Can a cold executor — no context beyond the spec — implement without asking questions?
- [ ] Function signatures/behaviors described, not just "implement X"?
- [ ] Test scenarios described (what they verify, not just names)?
- [ ] "Done" clearly defined with verifiable criteria?
- [ ] All file paths specified or marked "TBD: new file"?

---

### 3. Verification Quality

**Tier-aware — see `skills/common-patterns/pipeline-constants.md` for the simple/medium bands.**

**Check:**
- [ ] **Simple task**: Has a Verification section with at least one specific, measurable outcome, plus the standing "Pre-commit hooks passing" line (canonical: `skills/common-patterns/spec-templates.md`, simple tier)?
- [ ] **Medium task**: Has 3+ specific, measurable verification criteria? (Prep-refactor: the suite command, green before and after — `skills/common-patterns/spec-templates.md`)
- [ ] All criteria testable/verifiable (not subjective)?
- [ ] Includes automated verification (tests pass, clippy clean) where applicable?
- [ ] No vague criteria like "works well" or "is implemented"?

**Good criteria examples:**
- ✅ Medium: "5+ unit tests pass (valid VIN, invalid checksum, various formats)"
- ✅ Medium: "Clippy clean with no warnings"
- ✅ Simple: "`rg 'old_name' src/` returns zero" plus "Pre-commit hooks passing" (per `skills/common-patterns/spec-templates.md`)

---

### 4. Dependency Structure

**Check:**
- [ ] Parent-child relationships correct (epic → phases → subtasks)?
- [ ] Blocking dependencies correct (earlier work blocks later)?
- [ ] No circular dependencies?
- [ ] Dependency graph makes logical sense?

**Verify with:**
```bash
bd list --parent bd-1   # All children
bd show bd-N            # Per-task blocking/blocked-by
```

---

### 5. Safety & Quality Standards

**Anti-patterns are checked at the EPIC level.** The epic's own Anti-Patterns (FORBIDDEN) section (created in hyperpowers:brainstorming Step 5) is the default coverage for every task under it. A task requires its own task-level anti-patterns section only when the task carries task-specific risk beyond what the epic already forbids — e.g. it introduces regex, touches concurrency, or adds a new external dependency. Simple tasks are exempt from a mandatory task-level anti-patterns section unless they carry that kind of risk.

**Check:**
- [ ] Epic has an Anti-Patterns (FORBIDDEN) section?
- [ ] If this task carries task-specific risk: does it have its own anti-patterns covering that risk (unwrap/expect, TODO without issue #, stub implementations, regex backtracking, etc.)?
- [ ] Error handling requirements specified where the task touches a failure path (use Result, avoid panic)?

---

### 6. Edge Cases & Failure Modes (Fellow SRE Perspective)

**Ask for each task:** malformed input, empty/nil/zero values, load and concurrency, dependency failure, Unicode and large inputs — which of these reach this task, and what happens when they do?

**Add to the Context section (medium) or as Verification notes (simple)** the edge cases that reach the task and have a consequence you can name: the case, the mitigation, and a reference to similar code that handles it. A case that cannot reach the task, or reaches it without consequence in this epic, is not added — and if the spec already carries one, it is a Category 9 trim.

---

### 7. Red Flags (AUTO-REJECT)

**Check for these — reject the plan for any you cannot fix under the Authority rule; a fixed one is a Changes Made entry:**
- ❌ Any task exceeding the ceiling in `skills/common-patterns/pipeline-constants.md` without a recommended split in the report
- ❌ Vague language: "implement properly", "add support", "make it work"
- ❌ Verification criteria that can't be checked: "code is good", "works well"
- ❌ Missing test specifications where the tier requires a Tests section (`skills/common-patterns/spec-templates.md`)
- ❌ "We'll handle this later" or "TODO" in the plan itself
- ❌ Epic missing anti-patterns section, or risky task missing task-level anti-patterns
- ❌ No simple/medium classification present (the classification itself carries the time band)
- ❌ Missing error handling considerations on a task that touches a failure path
- ❌ **CRITICAL: Placeholder text in design field** - "[detailed above]", "[as specified]", "[complete steps here]"

---

### 8. Test Meaningfulness (Fellow SRE Perspective)

**Tests must catch real bugs, not inflate coverage.** For every test specification:

**Ask these questions:**
- [ ] What specific bug would this test catch?
- [ ] Could production code break while this test still passes?
- [ ] Does this test exercise a real user scenario or failure mode?
- [ ] Is the assertion meaningful? (`result == expected` vs `result != nil`)

**Good test specifications:**
- ✅ "test_invalid_checksum_rejected" - catches missing checksum validation
- ✅ "test_malformed_json_returns_400_not_500" - catches error handling bug

**Bad test specifications (reject or strengthen):**
- ❌ "test_user_model_exists" - tautological, compiler catches this
- ❌ "test_basic_functionality" - vague, what specific bug does it catch?

**When reviewing test specifications:**
```markdown
Test: "test_vin_validation"
- What bug does it catch? ⚠️ Unclear - need specific scenarios
- Could code break while test passes? ⚠️ Unknown without specifics

STRENGTHEN TO:
- test_valid_vin_checksum_accepted
- test_invalid_vin_checksum_rejected (catches missing checksum validation)
- test_lowercase_vin_normalized (catches case handling bug)
```

---

### 9. Scope Proportionality

For each implementation item and each verification criterion, name what it traces to: an epic requirement or success criterion, an immutable anti-pattern, or an edge case the spec names with a consequence in this epic. An item that traces to none of these is over-specification — trim it under the Authority rule and record it under Removed / Over-specified with the reason. Narrow rather than delete when part of the item traces: a coverage criterion where the requirement says "suite passes" is narrowed to that, and the threshold goes.

This category is advisory: trims never change the verdict on their own. A task whose items mostly trace to nothing is a structural finding for the report (recommend drop or merge), and a structural finding can change it.

**Check:**
- [ ] Every item the earlier categories added in this review passes the same test?

---

## Review Process

For each task in the plan:

**Step 1: Read the task**
```bash
bd show bd-3
```

**Step 2: Apply the checklist** — Categories 1 through 9, every task.

**Step 3: Document findings**
Take notes:
- What's missing
- What's vague or ambiguous
- Hidden failure modes not addressed
- Items to trim, each with its reason (Category 9)
- Whether to recommend the `Executor: opus` promotion flag (see `skills/common-patterns/pipeline-constants.md`) for an irreducibly hard task — a suggestion to the lead, not something SRE sets directly

**Step 4: Update the task**

Use `bd update` to add what is missing and remove what does not trace. This example updates a **medium** task spec — extend its existing sections, never add sections the two-tier format doesn't define (`skills/common-patterns/spec-templates.md`):

```bash
bd update bd-3 --design "$(cat <<'EOF'
## Goal
[Original goal, preserved]

## Why
[Original Why, preserved]

## Context
[Original Context, preserved]

**Edge Case: Empty Input**
- Empty string reaches parse() from the CLI's default argument (R2: every input path returns a typed error)
- MUST validate input length before processing

**Reference Implementation**
- Study src/similar/module.rs for the pattern to follow

## Implementation
[Original Implementation, preserved]

## Tests
[Original Tests, preserved]

## Verification
- [ ] Existing criteria
- [ ] NEW: measurable criterion replacing a vague one, with its requirement named
[The benchmark criterion that traced to no requirement is gone; it is recorded in the report under Removed / Over-specified, not in the spec]

## Boundaries
[Original Boundaries, preserved]
EOF
)"
```

**For a simple task**, the same update only ever touches `## Changes` and `## Verification` — a simple spec has no Context, Implementation, or Boundaries sections to extend. If findings require one of those sections, the task no longer fits the simple tier — do not add the section; recommend reclassification to medium in your report.

**IMPORTANT:** Use `--design` for full detailed description, NOT `--description` (title only).

**Step 5: Verify no placeholder text (MANDATORY)**

After updating, read back with `bd show bd-N` and verify:
- ✅ All sections contain actual content, not meta-references
- ✅ No placeholder text like "[detailed above]", "[as specified]", "[will be added]"
- ❌ If ANY placeholder text found: REJECT and rewrite with actual content

---

## Recommending Task Splits

If a task exceeds the ceiling in `skills/common-patterns/pipeline-constants.md`, do not create subtasks directly — see Authority above. Analyze the split and write the recommendation into your report; the lead decides whether to accept it and creates the actual tasks.

**Where to draw the boundary:**
- Split along component or file boundaries, not arbitrary line/time counts — each proposed subtask must be independently completable and independently verifiable
- Identify sequencing: does one subtask's output feed another's input? Note that as a proposed dependency, not a parallel pair
- Each proposed subtask needs enough detail that a cold executor could pick it up without asking questions — same bar as any task spec (`skills/common-patterns/spec-templates.md`)

**Recommendation format** (in the report's Recommendations section; in batch mode the Batch Verdict block lists it too):

```markdown
### Recommended Split: bd-3 (was N min, exceeds ceiling)

1. **Subtask 1: [Specific Component]** (simple/medium)
   - Goal: [what this subtask achieves]
   - Changes/Implementation: [scope — what it covers]
   - Verification: [how completion is checked]
   - Depends on: none

2. **Subtask 2: [Another Component]** (simple/medium)
   - Goal: [what this subtask achieves]
   - Changes/Implementation: [scope — what it covers]
   - Verification: [how completion is checked]
   - Depends on: Subtask 1
```

---

## Output Format

After reviewing all tasks:

```markdown
## Plan Review Results

### Epic: [Name] ([epic-id])

### Overall Assessment
[APPROVE ✅ / NEEDS REVISION ⚠️ / REJECT ❌]

### Dependency Structure Review
[Output of `bd list --parent [epic-id]`]

**Structure Quality**: [✅ Correct / ❌ Issues found]
- [Comments on parent-child relationships]
- [Comments on blocking dependencies]
- [Comments on granularity]

### Task-by-Task Review

#### [Task Name] (bd-N)
**Classification**: [simple / medium] ([✅ Within range / ❌ Too large - split recommended])
**Status**: [✅ Ready / ⚠️ Needs Minor Improvements / ❌ Needs Major Revision]

**Critical Issues** (must fix):
- [Blocking problems]

**Not applied (structural)**:
- [What needs a task change the Authority rule doesn't cover]

**Changes Made**:
- [Specific improvements added via `bd update`]

**Removed / Over-specified**:
- [Item trimmed or narrowed via `bd update` — reason: what it failed to trace to (Category 9), or that it exceeds what the requirements ask; or "None — every item traces"]

---

[Repeat for each task/phase/subtask]

### Summary of Changes

**Issues Updated**:
- bd-3 - Added edge case handling for empty input (R2); removed benchmark criterion (no requirement sets a performance bound)
- bd-5 - Recommended split into 3 subtasks (was 40 min, proposed 3x10 min)
- bd-7 - Strengthened Verification (added test names, verification commands)

### Recommendations

[If APPROVE]:
✅ APPROVE — ready for implementation.

[If NEEDS REVISION]:
⚠️ Plan needs improvements before implementation:
- [List major items that need addressing]
- After changes, re-run hyperpowers:sre-task-refinement

[If REJECT]:
❌ Plan has fundamental issues and needs redesign:
- [Critical problems]
```

**In batch mode:** this format plus the Cross-Task Analysis goes to the report file; the final message is the one-line template (Report File Contract above).
</the_process>

<examples>
<example>
<scenario>Reviewer skips edge case analysis (Category 6)</scenario>

<code>
# Review of bd-3: Implement VIN scanner

## Checklist review:
1. Granularity: ✅ 20 min (medium)
2. Implementability: ✅ Cold executor can implement
3. Verification: ✅ Has 5 test scenarios
4. Dependencies: ✅ Correct
5. Safety Standards: ✅ Anti-patterns present
6. Edge Cases: [SKIPPED - "looks straightforward"]
7. Red Flags: ✅ None found

Conclusion: "Task looks good, approve ✅"

# Task ships without edge case review
# Production issues occur:
- VIN scanner matches random 17-char strings (no checksum validation)
- Lowercase VINs not handled (should normalize)
- Catastrophic regex backtracking on long inputs (DoS vulnerability)
</code>

<why_it_fails>
- Skipped Category 6 assuming the task was "straightforward" — never asked what happens with an invalid checksum, lowercase input, or a long input
- Each of those reaches the scanner from ordinary text and has a consequence: false positives, missed matches, DoS
- The executor had no way to know: the spec was its only context
</why_it_fails>

<correction>
**Apply Category 6 — which cases reach this task, and what happens:**

```markdown
## Edge Case Analysis for bd-3: VIN Scanner

- Malformed input? VIN has a checksum — a pattern match alone accepts random strings (R1: no false positives)
- Empty/nil? Empty string reaches the scanner from empty documents; the scanner must return no match, not error
- Concurrency? Read-only scanner, no shared state — nothing to add
- Dependency failures? No external dependencies — nothing to add
- Unicode/special chars? VIN is alphanumeric only, but lowercase VINs exist in the corpus
- Large inputs? `.*` patterns backtrack catastrophically on long inputs (anti-pattern: no regex without a backtracking check)

Findings:
❌ Checksum validation not mentioned (will match random strings)
❌ Case normalization not mentioned (lowercase VINs exist)
❌ Regex backtracking risk not mentioned (DoS)
```

**Update task:**
```bash
bd update bd-3 --design "$(cat <<'EOF'
[... original content ...]

## Context
[Original Context, preserved]

**VIN Checksum**:
- ISO 3779 transliteration table and weighted sum modulo 11
- MUST validate checksum, not just pattern — prevents false positives (R1)

**Case Normalization**:
- MUST normalize to uppercase before validation; test with "1hgbh41jxmn109186"

**Regex Backtracking Risk**:
- Pattern `.*[A-HJ-NPR-Z0-9]{17}.*` backtracks; use bounded repetition

## Tests
[Original Tests, preserved]
- Valid pattern but invalid checksum (should NOT match)
- Lowercase VIN "1hgbh41jxmn109186" (should normalize and validate)
- 10000 'X's followed by a 16-char string (should return within the suite's timeout, not DoS)
EOF
)"
```

Concurrency and dependency failure were asked and not added: nothing reaches the task through them. That is the shape of a Category 6 pass — the questions are always asked; only the cases with a consequence go in.
</correction>
</example>

<example>
<scenario>Reviewer approves a task with placeholder text (Category 7)</scenario>

<code>
# Review of bd-5: Implement License Plate Scanner

bd show bd-5:

## Implementation
- [ ] Create scanner module
- [ ] [Complete implementation steps detailed above]
- [ ] Add tests

## Verification
- [ ] [As specified in the Implementation section]
- [ ] Tests pass

## Context
- [Will be added during implementation]

# Reviewer:
"Looks comprehensive, has an Implementation section and Verification ✅"

# During execution the cold executor returns:
NEEDS_HELP: spec says "[Complete implementation steps detailed above]" — nothing is detailed above; what are the steps, what verification should I run, and what belongs in Context?
</code>

<why_it_fails>
- "[Complete implementation steps detailed above]" is a meta-reference, "[As specified in the Implementation section]" is circular, "[Will be added during implementation]" is a deferral — none is content
- The spec is the executor's only context, so every placeholder is a question it must return to the lead
- The task looked complete and was not; the review existed to catch exactly this
</why_it_fails>

<correction>
**Read the design field line by line for placeholders:**

```markdown
Line 15: "[Complete implementation steps detailed above]"  ❌ PLACEHOLDER — meta-reference
Line 22: "[As specified in the Implementation section]"     ❌ PLACEHOLDER — circular reference
Line 30: "[Will be added during implementation]"            ❌ PLACEHOLDER — deferral

DECISION: REJECT ❌ — contains placeholder text; not ready for implementation
```

**Update task with actual content:**
```bash
bd update bd-5 --design "$(cat <<'EOF'
## Goal
Detect US license plate numbers (CA/NY/TX + generic fallback) in healthcare-context text, using the existing scanner plugin pattern.

## Why
Extends the PII/PHI scanner suite so license plate numbers are flagged alongside VINs when they appear near healthcare context. Without this scanner, plate numbers in medical records go undetected — a gap in the same coverage VIN scanning already closes.

## Context
- **Reference implementation**: Study `src/scan/plugins/scanners/vehicle_identifier.rs` — follow the same pattern (regex + context check + tests)
- **Registration point**: `src/scan/plugins/scanners/mod.rs`
- **State format regex patterns**:
  - CA: `[0-9][A-Z]{3}[0-9]{3}` (e.g., 1ABC123)
  - NY: `[A-Z]{3}[0-9]{4}` (e.g., ABC1234)
  - TX: `[A-Z]{3}[0-9]{4}|[0-9]{3}[A-Z]{3}` (e.g., ABC1234 or 123ABC)
  - Generic: `[A-Z0-9]{5,8}` (fallback)
- **False Positive Risk**: license plates are short and generic (5-8 chars). MUST require healthcare context via `has_healthcare_context()` — without that gate, the scanner will match random alphanumeric sequences like "ABC1234" wherever they appear, not just in medical records.

## Implementation
1. Write failing tests in `src/scan/plugins/scanners/license_plate.rs`'s test module covering the scenarios in Tests below. Run `cargo test license_plate` and confirm RED — tests fail because `LicensePlateScanner` doesn't exist yet.
2. Implement the minimal `LicensePlateScanner` struct implementing the `ScanPlugin` trait in `src/scan/plugins/scanners/license_plate.rs`:
   - Add the CA/NY/TX/generic regex patterns from Context
   - Implement the `has_healthcare_context()` gate — no match is reported without healthcare context present
   - Run `cargo test license_plate` and confirm GREEN
3. Register `LicensePlateScanner` in `src/scan/plugins/scanners/mod.rs`
4. Refactor for clarity (regex compilation reuse, module docstring listing supported formats) while keeping `cargo test license_plate` green

## Tests
- `test_valid_ca_plate_detected_in_healthcare_context`: "1ABC123" is detected when healthcare context is present
- `test_valid_ny_plate_detected_in_healthcare_context`: "ABC1234" is detected when healthcare context is present
- `test_too_short_string_rejected`: "123" is NOT detected (too short to match any pattern)
- `test_valid_plate_not_detected_outside_healthcare_context`: "ABC1234" is NOT detected without healthcare context present — proves the false-positive gate works
- One test per pattern (CA/NY/TX/generic) plus the edge cases above

## Verification
- [ ] `cargo test license_plate` passes

## Boundaries
- Common US plate formats only (CA/NY/TX + generic fallback) — international plates are out of scope, noted for a future iteration
- No changes to other scanners (e.g. `vehicle_identifier.rs`) beyond reading it as a reference
EOF
)"
```

**Verify no placeholder text:** `bd show bd-5`, read the entire output, confirm every section has actual content.
</correction>
</example>

<example>
<scenario>Reviewer strengthens vague criteria by adding everything that could be measured (Category 3 without Category 9)</scenario>

<code>
# Review of bd-7: Implement Data Encryption

bd show bd-7:
## Verification
- [ ] Encryption is implemented correctly
- [ ] Code is good quality
- [ ] Tests work properly
- [ ] Coverage >90% via cargo tarpaulin

# Epic requirements: R1 "files encrypted at rest with AES-256-GCM", R2 "key derived
# from the user's passphrase", R3 "existing suite passes". Anti-patterns: NO unwrap
# in production code.

# Reviewer's update — five headed blocks, twenty-six criteria:
**Encryption Implementation**: AES-256-GCM; PBKDF2 100,000 iterations; unique IV; auth tag verified
**Code Quality**: clippy; rustfmt; no unwrap; no TODO
**Test Coverage**: 12+ named tests including test_large_plaintext_10mb and
  test_concurrent_encryption; coverage >90% via cargo tarpaulin
**Documentation**: module docstring; function examples; security considerations documented
**Security Review**: no hardcoded keys; key zeroized after use; constant-time tag comparison
</code>

<why_it_fails>
- Three vague criteria became twenty-six measurable ones, and most trace to nothing: no requirement sets a coverage threshold, a 10MB performance case, concurrency (the CLI encrypts one file per invocation), an iteration count, or documentation content
- The executor spends its budget on tarpaulin and docstrings, and the review that follows checks those instead of R1-R3
- Category 3 was applied without Category 9: measurable is necessary, not sufficient
</why_it_fails>

<correction>
**Strengthen each criterion to something measurable that traces:**

```markdown
## Verification analysis for bd-7

Current: 0 testable criteria (Category 3) → strengthen; one measurable criterion that traces to nothing (Category 9) → remove. Each replacement must trace:

- "Encryption is implemented correctly"
  → AES-256-GCM with a unique IV per call and the auth tag verified on decrypt (R1)
- "Code is good quality"
  → `cargo clippy -- -D warnings` clean; `rg '\.unwrap\(\)' src/crypto/` returns 0 (anti-pattern: NO unwrap)
- "Tests work properly"
  → `cargo test crypto` passes with: roundtrip; wrong key fails auth; modified ciphertext fails auth (R1: authenticated encryption); empty plaintext (edge case: the CLI accepts an empty file; consequence: a zero-length ciphertext must still carry a tag)

Removed:
- coverage >90% — no requirement sets a threshold; R3 says the suite passes

Not added, with reason:
- 10MB and concurrency tests — the CLI encrypts one file per invocation; no path reaches concurrent calls
- PBKDF2 iteration count — R2 says derived from the passphrase; the count is the executor's call within the library's default
- documentation criteria — no requirement names docs
```

**Update:**
```bash
bd update bd-7 --design "$(cat <<'EOF'
[... original content ...]

## Verification
- [ ] AES-256-GCM with a unique IV per call; auth tag verified on decrypt (R1)
- [ ] `cargo clippy -- -D warnings` clean
- [ ] `rg '\.unwrap\(\)' src/crypto/` returns 0
- [ ] `cargo test crypto` passes: roundtrip, wrong-key fails auth, modified-ciphertext fails auth, empty plaintext carries a tag
- [ ] `cargo test` passes (R3)
EOF
)"
```

**Report entry:**
```markdown
**Changes Made**: replaced three vague criteria with five measurable ones traced to R1, R3, and the unwrap anti-pattern
**Removed / Over-specified**: coverage >90% — no requirement sets a threshold; R3 says the suite passes. The other three blocks were not added (reasons in the analysis)
```
</correction>
</example>
</examples>

<critical_rules>
## Rules That Have No Exceptions

1. **Apply all 9 categories to every task** → No skipping any category for any task
2. **Reject plans with placeholder text** → "[detailed above]", "[as specified]" = instant reject
3. **Verify no placeholder after updates** → Read back with `bd show` and confirm actual content
4. **Flag tasks exceeding the ceiling** → Recommend a split in the report (see "Recommending Task Splits"); ceiling defined in `skills/common-patterns/pipeline-constants.md`
5. **Strengthen vague criteria** → "Works correctly" → measurable verification commands that trace
6. **Ask the edge-case questions of every task** → Add the cases that reach it with a named consequence; trim the ones that don't
7. **Every item traces or goes** → Your own additions are held to the same test as the author's (Category 9)
8. **Strengthen tautological tests** → Tests must catch bugs, not verify compiler-checked facts

## Common Excuses

All of these mean: **STOP. Apply the full process.**

- "Task looks straightforward" (Edge cases hide in "straightforward" tasks)
- "Has 3 criteria, meets minimum" (Criteria must be measurable, not just 3+ items)
- "Placeholder text is just formatting" (Placeholders mean incomplete specification)
- "Can handle edge cases during implementation" (Must specify upfront, not defer)
- "The executor will figure it out" (A cold executor has nothing to figure it out from — we specify)
- "Too detailed, feels like micromanaging" (Detail the executor needs is not micromanagement; detail no requirement needs is over-specification — trim it, don't keep it to be safe)
- "More edge cases can't hurt" (Every item costs executor context and review attention; a case with no consequence in this epic is noise the executor has to weigh)
- "Detail prevents questions" (Detail that traces prevents questions; detail that doesn't creates them — the executor asks why it is there)
- "Taking too long to review" (One gap caught saves hours of rework)
- "Any tests are better than none" (Tautological tests are worse - give false confidence)
- "Tests are specified, don't need to review them" (Test quality matters more than quantity)
- "Coverage metrics will catch missing tests" (Coverage gaming = meaningless tests)
</critical_rules>

<verification_checklist>
Before completing SRE review:

**Per task reviewed:**
- [ ] Applied Categories 1-9
- [ ] Checked for placeholder text in design field
- [ ] Applied strengthening and trims via `bd update --design`, then read back with `bd show` (no placeholders remain)
- [ ] Recorded every trim under Removed / Over-specified with its reason
- [ ] Recommended splits in the report for any task exceeding the ceiling in `skills/common-patterns/pipeline-constants.md`

**Overall plan:**
- [ ] Verified dependency structure with `bd list --parent` + per-task `bd show`

**Can't check all boxes?** Return to review process and complete missing steps.
</verification_checklist>

<integration>
**Call chains:**
```
Upfront planning (batch mode, mainline):
hyperpowers:brainstorming → creates full task tree (Step 6c) → hyperpowers:sre-task-refinement [BATCH] (Step 7) → hyperpowers:executing-plans
                                                                        ↓
                                                              (if gaps: revise tasks, re-run batch)

Spec repair (single-task mode, off-mainline):
hyperpowers:writing-plans (repairs/expands a spec) → hyperpowers:sre-task-refinement [SINGLE] → hyperpowers:executing-plans
```

</integration>
