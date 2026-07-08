---
name: epic-bd-iaem-review-seam-reconciliation
description: Epic bd-iaem consolidates the end-of-epic review gate into executing-plans; T3-T7 all passed review; all 3 flagged epic-level gaps resolved; only end-of-epic reviewer dispatch remains
metadata:
  type: project
---

**UPDATE 2026-07-07 (T7 bd-6fn9 PASS — final task, epic ready for end-of-epic reviewer):**
Commit 7e473a8, diff base a605cb6. Diff exactly 3 files / 6 insertions+6 deletions, nothing
beyond spec: plugin.json version bump (1 line), analyzing-test-effectiveness/SKILL.md flow
diagram (3 lines: `executing-plans (implements tasks + reviewer gate verifies quality)` /
`(on-demand re-check available)` / `review-implementation (re-verification)` — minimal, did
not touch the adjacent known-stale "sre-task-refinement (on each task)" line which belongs to
a different epic), .beads/issues.jsonl (2 lines: bd-6fn9 open->in_progress, bd-tz73
in_progress->closed — ordinary self-status-update sync, not scope creep). Independently
re-ran all three sweep greps (case-insensitive review-implementation, "request path through",
"Did this work") — clean, every hit reads as on-demand/self-reference/historical, both
documented false-positive exceptions (intuition L196, analyzing-test-effectiveness L54/L1063)
confirmed still accurate. contract-test.sh 10/10. Ran epic bd-iaem's full 9-item Success
Criteria list as a final per-criterion spot audit (not just trusting the task's own checklist)
— all 9 pass independently, including verifying loop-interfaces.md's last 3 touching commits
all predate the epic's base commit (via `git merge-base --is-ancestor`). Gotcha worth noting
for future epic-closing tasks: `git diff <base> <head> -- .beads/issues.jsonl` on a large
JSONL file shows huge misleading "Output too large" previews because each bd issue is one
line — unified diff context pulls in whole neighboring JSON records as unchanged context.
Don't be alarmed by the size; check `--stat` and the actual `+`/`-` lines, not the preview.
All 7 tasks (bd-5qxo/bd-7eno/bd-q3az/bd-g01r/bd-gihs/bd-tz73/bd-6fn9) now closed or passed;
only the end-of-epic reviewer dispatch + epic closure remain.

**UPDATE 2026-07-07 (T5 bd-gihs PASS):** finishing-a-development-branch/SKILL.md
(commit b7944bd, diff base 3be5d8c) + commands/finish-branch.md re-gated on
"end-of-epic reviewer APPROVED" instead of review-implementation. Verified: grep for
"review-implementation" leaves only the L28 on-demand-re-verification mention (matches
review-implementation.md's own on-demand framing from T3); full-file read found no other
site describing the old chain; L464 call-chain diagram agrees with executing-plans'
L365 Flow line (reviewer gate + architecture check + STOP + user + finish-branch); diff
stat (5 insertions/9 deletions across 2 files, i.e. SKILL.md 4+/8-, finish-branch.md 1+/1-)
matches the task spec's five line-mapped edits exactly — no scope creep. Remaining before
close: T6 bd-tz73 (naming sweep), T7 bd-6fn9 (gated sweep + bump to 3.21.0, blocked on T6).

**UPDATE 2026-07-07 (T4 bd-g01r re-review PASS):** reviewer.md re-keyed to two-tier
spec vocab across commits 4cf6a5f/2bd8d48/3be5d8c. Final confirmation pass: PASS. The
three epic-level gaps I flagged during the T3 review (below) are ALL resolved:
- Gap #1 (dead-code tooling loss) — RESOLVED in T4: cargo/eslint/swiftlint/vulture
  unused-code detection + orphaned-tests reasoning restored to reviewer.md Step 3.
- Gaps #2/#3 (plan-impact citation, mid-epic caveat) — RESOLVED in commit d1012d0
  ("review-implementation: add plan-impact citation + mid-epic caveat").
T4 also added a "Tasks Reviewed" roster (with NOT YET REVIEWED (open) slot) to BOTH
verdict templates so a cold mid-epic reviewer has a slot for open tasks — honoring the
verdict-agnostic prose rule at reviewer.md:38. Frontmatter byte-identical vs epic base
d1012d0; APPROVED/GAPS FOUND vocabulary unchanged; loop-interfaces.md untouched.
Minor (non-blocking) observation: GAPS FOUND template now carries the failing-task
gap summary in two places — the new "Tasks Reviewed" roster AND the pre-existing
"Tasks with Issues" section (both `- <id>: <title> — [gap summary]`). Complementary
(roster = full accounting; Tasks with Issues = actionable subset), not incoherent.
Remaining before close: T5 bd-gihs (finish-branch prereqs), T6 bd-tz73 (naming sweep),
T7 bd-6fn9 (gated sweep + bump to 3.21.0, blocked on T4/T5/T6).

Epic bd-iaem ("Review seam reconciliation: single end-of-epic gate in executing-plans") makes
executing-plans own the reviewer dispatch + STOP + architecture checklist on the mainline, and
shrinks skills/review-implementation/SKILL.md to a <=150-line on-demand re-verification utility.
Seven tasks: bd-5qxo(T1 architecture-impact-check.md) done, T2 executing-plans update done
(commit 5e526d4), bd-q3az(T3 review-implementation shrink) done (commit 095e8cb, 1175->75 lines),
bd-g01r(T4 reviewer.md re-key to two-tier spec vocab) open, bd-gihs(T5 finish-branch prereqs) open,
bd-tz73(T6 naming sweep) open, bd-6fn9(T7 gated sweep + bump to 3.21.0) open, blocked on T4/T5/T6.

Task 3 review verdict: PASS against its own spec (wc -l 75<=150, dispatch block matches
executing-plans L232-241 verbatim, STOP semantics equivalent strength, no stale "called by
executing-plans" claim, no resources/ links, verdict vocabulary untouched, commands file only
description line changed). Boundaries respected (no reviewer.md/loop-interfaces.md edits).

Three epic-level gaps found during review, NOT blocking T3 (task followed its own Implementation
checklist faithfully) but worth resolving before bd-iaem closes:

1. **Dead-code tooling loss is bigger than the task's Context claimed.** Old SKILL.md L154-171
   had language-specific dead-code detection (cargo build warnings, eslint no-unused-vars,
   swiftlint, vulture) and a git-diff-based orphaned-tests check. T3's own Context section said
   "unique load-bearing content is ONLY Step 4 STOP+plan-impact and Step 5 architecture
   checklist" — but this L154-171 block is a third piece of unique content that is NOT in
   agents/reviewer.md (which only kept the textual grep patterns: fallback/legacy/deprecated,
   not compiler/linter-based detection or the orphaned-test check). Genuinely lost from the
   corpus, not relocated. Since reviewer.md is general-purpose (used on Rust/TS/Swift/Python
   projects the plugin installs into, not just this markdown-only repo), this reduces real
   review efficacy. Recommend folding into bd-g01r (T4, reviewer.md re-key) scope, or a new
   follow-up task, before epic close.
2. **Plan-impact-notice rule has a blind spot for on-demand paths.** The sibling-relevant-
   divergence rule ("emit a plan-impact notice... into the epic's bd notes; user carries it to
   the planning repo") survives verbatim in executing-plans L255, but the new 75-line
   review-implementation.md has no citation to it at all. review-implementation explicitly
   serves "auditing an epic implemented elsewhere" and "mid-epic sanity check" — exactly the
   cases where no executing-plans session exists to ever reach that completion-section rule.
   A one-line citation wouldn't violate T3's "no new review-protocol content" boundary (citing,
   not restating) — worth a small follow-up.
3. **Mid-epic sanity-check bullet may be incoherent with reviewer.md's partial-tree handling.**
   reviewer.md's startup protocol says "review every closed task under the epic" — it has no
   explicit accounting for open/in-progress tasks (no distinct verdict language for "not yet
   built" vs "built wrong"). review-implementation.md now advertises "mid-epic sanity check
   before all tasks are closed" as a valid use case. Whether this coheres depends on bd-g01r
   (T4)'s reviewer.md re-key — check when T4 lands; if unaddressed, review-implementation's
   bullet may need a one-sentence caveat about partial-tree verdict interpretation.

See also [[epic-bd-vv8-pipeline-coherence]] and [[epic-bd-854-hook-teardown]] for the same
citation-not-restatement review pattern in prior epics.
