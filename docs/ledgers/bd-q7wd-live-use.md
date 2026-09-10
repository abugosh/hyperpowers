# bd-q7wd live use — verbatim records

Epic bd-q7wd (Harsh but fair: plan-side minimality and prep-refactor, v3.39.0) was built author/editor, not through brainstorm → execute-plan. Acceptance was one live use per changed behavior. Scratchpad files do not survive sessions, so the two agent returns are recorded here verbatim. Outcomes and decisions are in the epic's bd notes.

## Live use B — brainstorming Step 2 + Step 5 on a toy problem (2026-09-09)

Inputs: the working-tree text of Step 2 (approach selection) and Step 5's Problem subsection, plus the toy problem below. Fresh general-purpose agent, session model, no other files.

### Toy problem (as given)

Toy repo (described, not on disk — reason from the description; do not dispatch agents or read files):

`lib/report.py` has one function, `render(rows)`, that builds a CSV string by hand: it joins each row's fields with "," and rows with "\n". Three callers use it: `cli.py` (writes the string to stdout), `export.py` (writes it to a file), and `mail.py` (attaches it to an email). A user reported that a customer name containing a comma ("Acme, Inc") breaks the exported file: the row gains an extra column.

Requirements (IMMUTABLE):
- R1: The file `export.py` writes round-trips through Python's `csv.reader` unchanged for fields containing a comma, a double quote, or a newline.
- R2: The three callers keep their current call signature.
- R3: The existing suite (11 tests, all on `render`) stays green.

Anti-patterns (FORBIDDEN):
- NO new runtime dependencies (this ships inside a locked-down image).

Approaches (research is done for you):
- A. In `export.py`, after calling `render`, re-parse the returned string line by line and re-emit it through the standard library's `csv.writer`. About 6 changed lines in one file, one new concept (a writer object). Meets R1 for the exported file. `cli.py` and `mail.py` keep emitting the unquoted rows.
- B. Replace the hand-built join inside `render` with `csv.writer` into an `io.StringIO`, keeping the signature. About 12 changed lines in one file, one new concept (a writer object). All three callers get RFC 4180 output.
- C. Introduce a `Formatter` protocol with `CsvFormatter` and `TsvFormatter` classes, inject the formatter into `render(rows, formatter=CsvFormatter())`, and migrate the three callers. About 90 changed lines across 4 files, three new concepts. Fixes the bug and makes future formats pluggable.

Do exactly two things and nothing else:
1. Apply Step 2's approach selection to A, B, C and state which you choose and why, in at most six sentences.
2. Write the epic's `### Problem` subsection as Step 5's template requires it, filled in for this problem.
Return only those two things.

### Agent return (verbatim)

**1. Approach selection**

I choose B. A has the fewest lines, but it meets R1 by re-parsing render's already-broken output downstream of the origin, so under Step 2 it is not the smaller diff: the comma bug stays live in cli.py and mail.py and the next epic pays for it. C changes the origin but costs about 90 lines across four files and three new concepts, two of which (the protocol and TsvFormatter) no requirement asks for, so it loses the tie-break to B on both diff size and concept count. B replaces the hand-built join inside render, the site that produces the bug, keeps the signature for R2, uses only the standard library so the no-new-dependency rule holds, and fixes all three callers rather than one. One R3 constraint: csv.writer defaults to a "\r\n" line terminator, so render must pass lineterminator="\n" to keep the eleven existing tests green, and csv.reader accepts either terminator so R1 still holds. B is small without any structure change, so no prep-refactor task is needed.

**2. Epic Problem subsection**

### Problem
`render(rows)` in `lib/report.py` builds CSV by joining fields with "," and never quotes or escapes, so a field containing a comma, a double quote, or a newline shifts or splits columns; a customer named "Acme, Inc" already produced an extra column in an exported file. All three callers (`cli.py`, `export.py`, `mail.py`) emit this output, so any consumer that parses it as CSV can misread it.
Origin: the hand-built join inside `render` in `lib/report.py`, which has no quoting step; this epic changes that site directly.

## Live use A — sre-task-refinement batch mode against bd-3ahi's closed tree (2026-09-09)

Dispatch: fresh general-purpose agent, session model, instructed to Read the skill at the repo path (the Skill tool resolves to the installed plugin cache, which was still 3.38.0 — a first attempt that used the Skill tool was discarded for that reason), make no bd writes, and record every would-be `bd update` under the task's Changes Made or Removed / Over-specified slot.

Final message: `SRE VERDICT: NEEDS REVISION — report: <scratchpad>/sre-live-bd-3ahi-v2.md — 7 specs updated`

### Report (verbatim)

## Plan Review Results

### Epic: Harsh but fair: peek verdict bar and forge approval (bd-3ahi)

Mode: BATCH (full task tree). Calibration run against a CLOSED tree — no bd writes were made; every change below is recorded as the exact `bd update --design` (or `--title`) text that would have been applied, and counted as applied.

Skill: `skills/sre-task-refinement/SKILL.md` (working tree), with `skills/common-patterns/spec-templates.md`, `skills/common-patterns/pipeline-constants.md`, and `skills/common-patterns/loop-interfaces.md` (Verdict Contracts) read at the repo path.

Evidence base beyond `bd show`: the pre-epic commit `8626dc0` (parent of the first bd-3ahi commit `6502ad7`) was read for every exact-site anchor the specs quote — `agents/peek.md` :8/:38/:114, `skills/common-patterns/forge-detection.md` :10 and its Review state subsections (:98, :136), `skills/opt/SKILL.md` :67, `skills/common-patterns/pipeline-constants.md` :74-77/:101-109, README :40/:76/:91, CLAUDE.md :159/:208 — and `docs/ledgers/bd-zk46-pressure-tests.md` :22/:771/:773-777/:789-792/:760-771. All anchors hold except one off-by-one noted under bd-3mdj.

### Overall Assessment
NEEDS REVISION ⚠️ — content is strong across the tree (exact anchors, relocation rules, per-line greps, file-scope diffs); the revision items are structural: three tasks exceed the 30-minute ceiling (splits recommended), one task sits at it, and the reduced GREEN set leaves R1's line untested on real lens output (Category 8). Seven specs carry direct changes.

### Dependency Structure Review
```
bd-3mdj  T1 bikeshed fixture + RED baseline            depends: —            blocks: T2
bd-3m8x  T2 contract + synthesis fixtures               depends: T1           blocks: T3, T6
bd-bg7w  T3 Severity Anchor                             depends: T2           blocks: T4
bd-7q2n  T4 agents/peek.md                              depends: T3           blocks: T5
bd-pv20  T5 peek SKILL Step 6                           depends: T4           blocks: T7, T9
bd-2tf8  T6 forge-detection                             depends: T2           blocks: T7
bd-rupp  T7 peek SKILL Step 7                           depends: T5, T6       blocks: T8, T9
bd-lcjy  T8 satellites (opt, loop-interfaces, README, CLAUDE.md)  depends: T7  blocks: T10
bd-syo7  T9 GREEN                                       depends: T5, T7       blocks: T10
bd-uhzb  T10 version + sweep                            depends: T8, T9       blocks: —
```
(`bd list --parent bd-3ahi --all -n 0` plus per-task `bd show` DEPENDS ON / BLOCKS.)

**Structure Quality**: ✅ Correct
- Parent-child: all ten tasks are children of bd-3ahi; the epic itself blocks bd-1hm5 (sibling, out of scope here).
- Blocking: a single chain with one fork (T3 and T6 both wait on T2) and one join (T7). Every implicit data dependency is declared: T2 reads T1's ledger and `<sp>/red/`; T4 reads T3's anchor text; T5 reads T4's template lines; T7 reads T6's Identity/Approve subsections and T5's Step 6; T9 grades against T2's contract and runs T3-T5's prompts; T10 sweeps everything. No cycles.
- One over-constraint, harmless: T6 waits on T2 but consumes nothing from T1 or T2 (forge-detection is not a prompt under test). It could run beside T1; the serialization costs the epic roughly one task's wall time and protects nothing. Left as-is (structural; lead's call).
- Granularity: see Cross-Task Analysis — three over-ceiling tasks with splits proposed in the Batch Verdict.

### Task-by-Task Review

#### Task 1: bikeshed fixture + RED baseline (two runs, new ledger) (bd-3mdj)
**Classification**: medium, `Executor: opus` (❌ Too large — estimated 60-90 min: fixture build, scanner, unit run, ten nested dispatches across two RED runs, extraction, ledger with the full script embedded; split recommended)
**Status**: ⚠️ Needs Minor Improvements (content) — structural split in Batch Verdict

Checklist trace:
1. Granularity — over the 30-min ceiling (`pipeline-constants.md`); the wall clock is dispatch-bound (10 Opus/Sonnet dispatches) and the executor's own context carries two full RED transcripts' extraction. Deliverable is clear (ledger + `<sp>/red/`).
2. Implementability — a cold executor can run it: every ledger line reference pairs with a content anchor it can verify (`sed -n '22p;771p'` prints two fence lines — confirmed at the repo), the FIXTURE 5 block is verbatim, the dispatch method is spelled out, the RED block is a template. One wrong internal pointer (step 3 sends the executor to "step 7" for the safety lines; they belong to step 8(b)) and one off-by-one (ledger :773 is the `PRODUCTION-SAFETY READ` header, the four lines are :774-777) — both fixed below.
3. Verification — 11 measurable criteria plus the hooks line; the ledger greps match the SC11 shape (`^RED BASELINE`).
4. Dependencies — root of the chain; blocks T2 only. Correct.
5. Safety — epic anti-patterns 7 (no fixture editing to shape RED) and 10 (no `hyperpowers:peek` dispatch, body by file) both restated as Boundaries where the executor acts; the "safety read finds a real defect" path is handled (fix it, keep the four surfaces, say so).
6. Edge cases — asked: nested dispatch pauses (covered: SendMessage resume); worktree reuse between runs (covered); tree mismatch with clean's main (covered: verified); two runs disagree (covered: OBSERVATIONS); a lens returns `ERROR: <MODE> dispatch missing <input>` — NOT covered here though T9 covers the same dispatch shape; consequence: an errored lens counted as a lens with zero findings corrupts the baseline every GREEN rule in this epic is graded against. Added. Unicode/large input/concurrency — nothing reaches a fixture builder and a sequential dispatch chain.
7. Red flags — none. `<sp>`, `<sha>`, `<date>`, `<word>` are executor-filled slots with `<sp>` defined in Context, not placeholders.
8. Test meaningfulness — the fixture's own suite (10 tests, must pass) proves the copy-pasted tests are honest, which is what makes bikeshed "no defect"; the RED itself is a measurement, not a test.
9. Scope — every step traces: fixture and two runs → R7; by-file body and no-`hyperpowers:peek` → anti-pattern 10; scanner and sentence counts → the inherited grading rule T2's contract rule (4) binds on this epic; ledger block → SC11. Nothing to trim.

**Critical Issues** (must fix):
- None at the content level.

**Not applied (structural)**:
- Exceeds the ceiling — Recommended Split T1a/T1b in the Batch Verdict.

**Changes Made** (would have been applied via `bd update bd-3mdj --design`, Context and Implementation preserved otherwise):
- Implementation step 3, last sentence: `The four inherited lines at ledger :773-777 are copied verbatim into step 7.` → `The four inherited lines at ledger :774-777 (the header at :773 is not copied) are copied verbatim into the ledger at step 8(b).` Context bullet 2 likewise: `at :773-777` → `at :774-777, under the header at :773`.
- Implementation step 6(d), appended sentence: `A lens that returns `ERROR: <MODE> dispatch missing <input>` is a dispatch-shape bug in this task — re-dispatch with the input and do not count the run; the RED block records only runs whose four returns are complete.` (R7: the baseline measures the prompts, not the dispatch; same sentence T9 already carries.)

**Removed / Over-specified**:
- None — every item traces.

---

#### Task 2: pressure-test contract + reconstructed synthesis fixtures (bd-3m8x)
**Classification**: medium, `Executor: opus` (❌ At/over the ceiling — estimated 30-40 min: nine fixture files, six of them handcrafted lens returns in the pre-edit contract shapes, plus a ~40-line contract block and a verbatim ledger block; split recommended, lower priority than T1/T7/T9)
**Status**: ⚠️ Needs Minor Improvements

Checklist trace:
1. Granularity — at the ceiling by this review's estimate; two independently verifiable halves exist (fixture reconstruction; contract authoring).
2. Implementability — the contract block is ~90% verbatim in the spec (as amended post-RED with the LEAD DECISION quotes); the synth fixture contents are named finding by finding with severities, locations, lines present/absent; the RECON copies are `sed -n` ranges with a diff check and an off-by-one rule. A cold executor needs `agents/peek.md` :127-157/:178-211/:226-269 for the return shapes — named. No questions left.
3. Verification — 5 grep lines, a 3-way `diff`, an `ls`, per-file line-count greps on the synth files, the file-scope diff, hooks. Measurable throughout.
4. Dependencies — depends on T1 (reads the RED block and `<sp>/red/`); blocks T3 and T6. Correct.
5. Safety — anti-patterns 7 (no relaxing a pass rule, no editing fixtures) restated in Boundaries with the NEEDS_HELP route; "never write a rule RED fails by construction" is the right guard.
6. Edge cases — asked: fixture cannot support a rule (covered: NEEDS_HELP with the gap recorded); marker line included in a range (covered); `<sp>/red/` gone because the session changed (NOT covered — scratchpad files do not survive a session, and step 1 reads "both bikeshed REPORTs" from there; consequence: the grading-word extension cannot cite "the run and sentence it came from"; the rule (3) quotes are already verbatim in the amended spec, so only step 1 is reached). Added as a one-clause fallback.
7. Red flags — none.
8. Test meaningfulness — the contract is honest that rule (3) is the only bikeshed discriminator and that (1), (2), (4)-(8), (10) are regression guards RED already passes, with (9) vacuous. ADDED RULE (+) is the one rule that tests R1's line on real lens output, and by the contract's own words it "discriminates on real lens output (bad-no-critical's Importants) where bikeshed cannot" — see T9 and Cross-Task (b): under the reduced run plan, no run exercises it on a real lens.
9. Scope — synth amendments (a)/(b) → R2 (both fallback branches); contract → R7; grading-word list never trimmed → anti-pattern 7; `testing-methodology.md :140-200 — verbatim evidence only` → the same anti-pattern's "tighten after RED" half. Nothing to trim.

**Critical Issues** (must fix):
- None.

**Not applied (structural)**:
- At the ceiling — optional Recommended Split T2a/T2b in the Batch Verdict.
- Mid-flight amendment gap (Cross-Task b): step 3's `Run counts:` line still names `clean ×2, bad-no-critical ×2, silent-reshape ×1, missing-aim ×1`, which T9's amended Goal and SC11 reduce to bikeshed ×2 + three synthesis. The ledger stays honest (T9's block records `NOT RUN`), but the two specs state different constants. Recommend a one-line amendment to step 3: `Run counts (superseded 2026-09-09 by USER DECISION, recorded at T9 and SC11): fixtures — bikeshed ×2 …; the inherited-fixture counts stand as the contract's intent for a later epic.`

**Changes Made** (would have been applied via `bd update bd-3m8x --design`):
- Implementation step 1, appended: `If `<sp>/red/` is absent (scratchpad files do not survive a session), the RED block's `grading words:` entries and its OBSERVATIONS quotes are the source for additions, and the Grading-word list line says so.` (R7: the contract is authored against the recorded RED; consequence named above.)

**Removed / Over-specified**:
- None — every item traces.

---

#### Task 3: Severity Anchor — Important bar (Hits / Maintainer cost), fallback past Important (bd-bg7w)
**Classification**: medium (✅ Within range — ~15 min; exact replacement text at verified sites plus one judgment step)
**Status**: ✅ Ready

Checklist trace:
1. Granularity — within range. Medium is right despite the exact text: step 4's re-read-for-contradictions is judgment, and this file is the definition site the whole epic cites.
2. Implementability — replacement text is verbatim; the pre-epic file matches every quoted anchor (:74-77 Critical opener, :101-106 Important/Suggestion, :108-109 receiving-side sentence — read at `8626dc0`). The line-wrap rule names each single-line grep phrase. Commit message given.
3. Verification — 8 measurable criteria, each a grep or a bounded `sed`, plus the file-scope diff and hooks; the `Consumers cite this section; none restates it.` count of 2 guards the carve-out section against accidental edits.
4. Dependencies — after T2 (rules before edits); blocks T4. Correct.
5. Safety — Boundaries restate anti-pattern 2 (no count cap) at the one file where a cap would be written.
6. Edge cases — asked: a re-wrap breaking a single-line grep (covered by the line-wrap rule, which is exactly the consequence-bearing case here since SC1/SC2 are single-line greps); line shift moving the scope-line check (the edits sit below :72, so `sed -n '67,72p'` holds); nothing else reaches a definition edit.
7. Red flags — none.
8. Test meaningfulness — pure documentation; T9's synth-old/synth-rework exercise both fallback branches this text defines.
9. Scope — Important bullet → R1; fallback sentence → R2; Suggestion homing → R1's last sentence; step 3's follow-up-split sentence → R4 (the anchor states the split Step 7's comment carries, so Step 7 cites rather than defines it); untouched sections → R8/Boundaries. Nothing to trim.

**Critical Issues** (must fix):
- None.

**Not applied (structural)**:
- None.

**Changes Made**:
- None.

**Removed / Over-specified**:
- None — every item traces.

---

#### Task 4: agents/peek.md — colleague posture, Hits / Maintainer cost lines, clarity as Suggestion (bd-7q2n)
**Classification**: medium (✅ Within range — ~25 min; eleven edits plus a sweep; near the ceiling but each edit is anchored and most are verbatim)
**Status**: ⚠️ Needs Minor Improvements

Checklist trace:
1. Granularity — within range, near the top. Not split: every edit lands in one file and the sweep (step 10) must see all of them.
2. Implementability — each step names its paragraph and gives text or a closed rewrite rule; line numbers are paired with a relocation instruction (`re-locate by the Evidence: line`). The pre-epic file confirms :8 (posture), :38 (harsh-but-fair mechanism sentence), :114 (junior clarity item) — and the frontmatter carries neither `harsh` nor `junior`, so the `grep -c 'harsh' agents/peek.md — 0` check and the "do not touch the frontmatter" boundary cannot collide.
3. Verification — 13 measurable greps, the file-scope diff, hooks. The `>= 19` Severity Anchor floor still holds after the narrowing below (13 existing + 6 template lines + the clarity item = 20).
4. Dependencies — after T3 (the anchor it cites), blocks T5 (the lines Step 6 reads). Correct.
5. Safety — anti-pattern 6 (no junior presumption) restated in step 10 with the closed sweep; Boundaries forbid restating the bar — which the spec's own template text then does (Category 9).
6. Edge cases — asked: line numbers shift after step 1 (covered); a second author-presuming sentence beyond :38/:114 (covered: the sweep's rewrite rule "to the artifact property it was standing in for"); RECON section drift (covered: sweep-only). Nothing else reaches a prompt edit.
7. Red flags — none.
8. Test meaningfulness — pure documentation; T9 bikeshed reads these templates; ADDED RULE (+) reads the lines.
9. Scope — FOUR sites paraphrase the anchor's definitions at a consumer, which exceeds what R8 asks (citation only) and trips epic anti-pattern 1 ("a half-copied bar becomes two bars"): the template bracket text in step 3 (`the next edit at file:line and the step or fact the site does not state` — the anchor's sentence with one word dropped, which is why the non-restatement grep passes it), Rule 9's exclusion clause in step 2 (`a cost line that names only reading effort (the anchor's excluded words) is empty`), the clarity item's tail in step 5 (`: a named future edit and the fact the site does not state`), and the production-readiness parenthetical in step 6 (`(a hit that needs a caller the repo does not have)`). Narrowed to citation form below. Steps 7 and 8 (DELIVERY items) instantiate the lines for the delivery case rather than restate the definition — kept. Corroboration from the epic's own PEEK note (2026-09-09 self-peek): "the anchor's new lines and fallback were copied or excepted in three consumers (agent templates, Shared Rule 9, …) instead of cited" — the same shape, found live.

**Critical Issues** (must fix):
- None blocking; the Category 9 narrowing is applied.

**Not applied (structural)**:
- Verification design: the tree's non-restatement greps check only the two sentinel phrases (`Reading effort is not a cost`, `does not itself state`), which a one-word paraphrase defeats. Recommend the consumers' checks also grep the definition's distinctive nouns (`reading effort`, `future edit`, `docstring`) — a lead-level change to T4, T5, T8, T10 Verification, recorded here rather than added four times.

**Changes Made** (would have been applied via `bd update bd-7q2n --design`; all other steps preserved):
- Step 3 template lines →
  ```
    Hits: [Critical and Important — filled per the Severity Anchor (`skills/common-patterns/pipeline-constants.md`); exactly one of Hits / Maintainer cost]
    Maintainer cost: [Critical and Important — filled per the Severity Anchor (`skills/common-patterns/pipeline-constants.md`); exactly one of Hits / Maintainer cost]
  ```
- Step 2 Rule 9 insert → `Every Critical and every Important carries exactly one of the anchor's two lines, `Hits:` or `Maintainer cost:`, filled in that file's terms and judged by the Severity Anchor's test for that line; an Important whose line is missing or fails that test is Suggestion. Suggestions carry neither line.`
- Step 5 clarity item → ends at `… unless it fills the anchor's `Maintainer cost:` line (Severity Anchor, Shared Rule 9).` (the trailing `: a named future edit and the fact the site does not state` is dropped).
- Step 6 production-readiness → `… otherwise it is Important only when it fills one of the anchor's Important lines, and otherwise a Question for the Author or a Suggestion, as the Severity Anchor's reachability rule decides.` (the parenthetical is dropped).

**Removed / Over-specified**:
- The four paraphrases above — reason: exceed R8 (consumers cite, none restates) and epic anti-pattern 1; each survives the tree's own non-restatement grep only because it drops or reorders a word of the anchor's sentence.

---

#### Task 5: skills/peek/SKILL.md Step 6 — Important demotion and two-stage Critical fallback (bd-pv20)
**Classification**: medium (✅ Within range — ~15 min)
**Status**: ⚠️ Needs Minor Improvements

Checklist trace:
1. Granularity — within range; one paragraph rewritten, two one-line satellites, a re-read.
2. Implementability — step 1's replacement clause embeds an instruction inside text the executor inserts verbatim: `(the Severity Anchor's excluded words — cite `skills/common-patterns/pipeline-constants.md`)` — a cold executor cannot tell whether "cite …" is content or a note to itself, and either reading ships. Resolved by the narrowing below. Everything else is exact (the clause to replace is quoted; "keep every other clause" lists them).
3. Verification — 9 greps plus the Step-7-untouched `diff` (the right shape for a shared-file edit) plus the file-scope diff and hooks.
4. Dependencies — after T4 (the lines exist in the templates); blocks T7 and T9. Correct.
5. Safety — Boundaries fence Step 7 and the derivation citation (anti-pattern 8).
6. Edge cases — asked: a Critical that passes its class check but carries no line (no verdict consequence — it stays Critical, the tier its class supports; not added); an Important with both lines filled (no verdict consequence; not added); a lead-added Critical (covered: never demoted with both class lines present); a Suggestion asking for no change (covered by 2b, post-RED). Nothing reaches the verdict that the spec does not already move.
7. Red flags — none.
8. Test meaningfulness — T9's synth-old exercises the Suggestion branch of both moves; synth-rework exercises the Important branch of the Critical fallback; bikeshed ×2 exercises the no-Important path. All three markers in the spec are the ones the contract greps.
9. Scope — `whose cost line names only reading effort (the Severity Anchor's excluded words …)` paraphrases the anchor's exclusion at a consumer (R8, anti-pattern 1). Narrowed. Step 6 uses "filled" repeatedly without saying once whose test decides it — a cold lead applies the demotion by feel, the failure R1 exists to remove; a one-sentence definition citing the anchor is added (R2: "applies this"). Corroboration: the epic's PEEK note fix (1) — "'filled' defined once at the head of Step 6's re-check in the anchor's sense, the redundant reading-effort clause dropped".

**Critical Issues** (must fix):
- None blocking.

**Not applied (structural)**:
- None.

**Changes Made** (would have been applied via `bd update bd-pv20 --design`):
- Step 1, Important-demotion clause → `an Important whose `Hits:` and `Maintainer cost:` lines are both missing, or whose present line is empty under the Severity Anchor's test for that line (`skills/common-patterns/pipeline-constants.md`), becomes Suggestion, marked `[downgraded: no cost named]`;`
- Step 1, new first sentence for the re-check paragraph (before the moves): `A line is filled when it meets the Severity Anchor's test for that line (`skills/common-patterns/pipeline-constants.md`) and empty otherwise; every move below reads the lines by that one test.`
- Verification, added: `grep -c 'reading effort' skills/peek/SKILL.md` — 0 (the exclusion lives in the anchor only).

**Removed / Over-specified**:
- The reading-effort paraphrase in step 1 — reason: R8 / anti-pattern 1; the anchor's test is cited, not copied.

---

#### Task 6: forge-detection.md — identity read, approve write, caveats C11-C16 (bd-2tf8)
**Classification**: medium (✅ Within range — ~20 min; every string is given and sourced to the epic's research notes)
**Status**: ⚠️ Needs Minor Improvements

Checklist trace:
1. Granularity — within range. Medium is right: the two subsections are prose plus fenced commands wrapped to the file's width, and the caveat rows carry Settled-by judgments.
2. Implementability — all commands, messages, and statuses are in the spec and in the epic's NOTES; the pre-epic file confirms :10 (`or wants to post a comment (e.g. peek)`), the heading set the Context lists, and the `Review state (GitLab)` / `Review state (GitHub)` reads the new text points at (`/approvals` at :105; `reviews[]`, `commit.oid`, `latestReviews` at :139-146). The fence note (outer fence for presentation) removes the one ambiguity a nested fence creates.
3. Verification — 14 measurable greps including the negative ones that guard anti-patterns (`retry once` = 0; no fenced `--request-changes` command), the Detection/Degradation section diff, the file-scope diff, hooks.
4. Dependencies — after T2 (over-constraint, harmless — see Structure); blocks T7. Correct.
5. Safety — anti-pattern 3 (no retry, no second comment) is verified by grep and stated inside C12/C13; Boundaries forbid inventing messages beyond the research.
6. Edge cases — asked: identity read returns empty/non-zero (covered: C11 → unknown, not "not the author"); self-approval on each forge (covered); repeat approve (covered: C14/C15 with the pre-read); `--sha` mismatch (covered: C13); URL/`!iid` argument forms (covered: C16). One defect: C12 attributes `body cannot be blank` to the `--approve` form, but the research notes it as the `--request-changes` refusal (`body cannot be blank for request-changes review`); consequence: a consumer keyed to that string for approve waits for a message the approve form does not emit, and the row's mitigation is keyed to the wrong trigger. Fixed below. (The live Stage 2 review found the same row; recorded here as spec-level.)
7. Red flags — none.
8. Test meaningfulness — no CLI on the authoring machine; the caveats table with Settled-by clauses is the honest test surface (R5 requires exactly this).
9. Scope — Identity and Approve subsections → R5; refusal behavior per forge → R5; C11-C16 → R5 + SC7; the request-changes paragraph → Key Decision 3. The `glab mr revoke <iid>` sentence and its Verification grep trace to nothing: R5 names an identity read and an approve write, no consumer in this epic revokes, and the anti-pattern forbids retry so no path reaches an unapprove. Trimmed.

**Critical Issues** (must fix):
- None blocking.

**Not applied (structural)**:
- None.

**Changes Made** (would have been applied via `bd update bd-2tf8 --design`):
- Step 5, C12 row → `| C12 | `gh pr review <number> --approve` with no `--body` is doc-verified (body optional for approve) but not run; the confirmed `body cannot be blank for request-changes review` string belongs to `--request-changes`, and the approve form's refusal text, if any, is unconfirmed | On any non-zero exit, report the output verbatim and treat the approval as not submitted — never match on a specific string, and never re-run with a `--body` the user did not approve at the consumer's gate (peek Step 7: approval failures are reported, never retried). Settled by: one approve on a test PR with no body; if the body proves mandatory, the command above gains a fixed one-line `--body` and this row closes |`

**Removed / Over-specified**:
- Step 3, GitLab bullet: the sentence ``glab mr revoke <iid>` removes the caller's own approval (404 when none is held).` and the Verification item `grep -c 'glab mr revoke' … — 1` — reason: no requirement, anti-pattern, or consequence-bearing edge case in this epic reaches an unapprove; forge-detection's Purpose ("MR/PR metadata, comment, approval") does not extend to it either.

---

#### Task 7: skills/peek/SKILL.md Step 7 — follow-up line, gated forge approval, identity precondition (bd-rupp)
**Classification**: medium, `Executor: opus` (❌ Too large — fifteen edits into one ~60-line region plus an end-to-end path re-read; estimated 45-75 min; split recommended along the R4 / R6 seam)
**Status**: ⚠️ Needs Minor Improvements (size only — content is complete and traceable)

Checklist trace:
1. Granularity — over the ceiling. The epic's own cost record corroborates: "T7 consumed ~600K subagent tokens over three executor runs and three reviews" and Step 7 later needed a lead trim from 3119 to 972 words. Two requirements (R4 follow-up line; R6 approval election) share the task and touch mostly distinct paragraphs — the natural seam.
2. Implementability — each step names its paragraph by its bold heading (line numbers are declared stale after T5 and relocation is by heading), gives verbatim text where the text is contractual (the three follow-up sentences, the row 7 cell, the excuses, the checklist lines) and intent where the spec-depth rule allows it (the eligibility and failure paragraphs). Step 3's prose mixes the paragraph's content with "(cite, never restate)" asides, but the paragraph is not fenced, so a cold executor reads it as intent — acceptable. Step 14's re-read names the paths to walk. No open question.
3. Verification — 15 measurable greps with the physical-line note that keeps `grep -c 'no re-review' >= 4` honest, the negative greps for restated commands and a request-changes path (anti-patterns 3-5), the Step-6-untouched diff, the file-scope diff, hooks.
4. Dependencies — after T5 (Step 6 done, same file) and T6 (Identity/Approve subsections to cite); blocks T8 and T9. Correct.
5. Safety — epic anti-patterns 3, 4, 5 are each carried into the text the task writes (phase-B exact action, no retry, no second comment; no self-peek approval; no approval without the comment) and each has a Verification grep or a Boundaries line. This is the epic's highest-risk task (outward forge writes) and it carries task-level guards proportionate to that.
6. Edge cases — asked, each with its trace: identity read fails (R6, C11); self-peek (R6, anti-pattern 4); already approved (C14/C15 — a second GitHub review is a silent write; GitLab 401 is ambiguous); target closed/merged (glab refuses before the API call; SC8 names the case); rung 2/3 (R6); GitHub self-approval refusal, GitLab 401, GitLab 409 (C12-C15, anti-pattern 3: reported, never retried); partial delivery (fixes landed, comment posted, approval failed — the fixed order says what is delivered); re-derived verdict after fixes (epic Open Question 4, explicitly delegated to this task); fallback paths (pre-fix verdict). Nothing reaches the election that the spec does not already state, and nothing stated lacks a consequence in this epic.
7. Red flags — none.
8. Test meaningfulness — none of the pressure fixtures exercises Step 7 (they run at rung 3 with no forge), and the CLI is absent; the spec says so ("verified by grep and by reading"). The epic's manual-validation STOP names the live forge run. Noted in Cross-Task (b); no spec change — a fixture cannot reach a forge.
9. Scope — walked step by step: 1, 5, 7(a), 12(third), 13(insert) → R4/SC6; 2, 3, 4, 6, 7(second paragraph), 8, 9, 10, 11, 12(first two), 13(new line) → R6/SC8/anti-patterns 3-5; 14 → R6's "nothing is submitted without the user approving the exact action". Nothing to trim.

**Critical Issues** (must fix):
- None.

**Not applied (structural)**:
- Exceeds the ceiling — Recommended Split T7a (R4) / T7b (R6) in the Batch Verdict. T7b still lands near 35 min; the lead's alternative, which the epic's later record shows was the one taken, is to write the eligibility, failure, and fallback paragraphs as principles (one sentence each: eligibility conditions; withdraw visibly; report, never retry; fixed delivery order) rather than enumerated cases — that trims T7b under the ceiling without a second split.

**Changes Made**:
- None.

**Removed / Over-specified**:
- None — every item traces.

---

#### Task 8: satellites — opt follow-up-line sentence, loop-interfaces check, README/CLAUDE.md peek lines (bd-lcjy)
**Classification**: simple (✅ Within range of the ceiling; ~8 min overruns the simple band's 5 min by a few mechanical insertions across three files — noted, no reclassification: nothing here needs Context, Tests, or Boundaries)
**Status**: ✅ Ready

Checklist trace:
1. Granularity — seven exact insertions/replacements plus one verify-unchanged. Simple shape, simple content.
2. Implementability — each change quotes its anchor text; the pre-epic files match every anchor (README :40 both phrases, :76, :91; CLAUDE.md :159, :208; opt :67 — read at `8626dc0`); the "line moved → relocate by quoted anchor, name the actual line" rule closes the drift case. Commit given.
3. Verification — per-line `sed -n 'Np' | grep -c` checks that defeat the pre-existing `approv` (diff-approval) on README :40/:91 — the right construction for a file that already contains the word; the loop-interfaces `git diff main` emptiness; the three-file `--stat`; hooks.
4. Dependencies — after T7 (the README/CLAUDE sentences describe Step 7's result); blocks T10. Correct.
5. Safety — anti-pattern 1 guarded by the no-restatement grep on all three files; anti-pattern 8 guarded by the derivation-sentence grep.
6. Edge cases — asked: line drift (covered); word masking (covered); loop-interfaces accidentally edited (covered by the diff). Nothing else reaches six sentence edits.
7. Red flags — none.
8. Test meaningfulness — N/A (documentation).
9. Scope — opt sentence → R8 (ingest must not create a finding from the follow-up line) + SC6; loop-interfaces verify → R8/SC9; README/CLAUDE lines → R9/SC12. README :91's clause names the two lines and the demotion without defining them — description, not restatement. Nothing to trim.

**Critical Issues** (must fix):
- None.

**Not applied (structural)**:
- None.

**Changes Made**:
- None.

**Removed / Over-specified**:
- None — every item traces.

---

#### Task 9: GREEN — bikeshed x2, clean x2, bad-no-critical x2, reshape x1, missing x1, 3 synthesis; bounded fix rounds; ledger (bd-syo7)
**Classification**: medium, `Executor: opus` (❌ Too large — thirteen nested dispatches, rule-by-rule grading of five reports with verbatim evidence, up to two fix rounds each re-running a scenario plus two synthesis fixtures; estimated 90+ min; split recommended)
**Status**: ⚠️ Needs Minor Improvements — plus one structural finding (Category 8)

Checklist trace:
1. Granularity — over the ceiling. The two halves (three synthesis runs; two bikeshed runs) are separately gradable; the fix-round coupling (a Step 6 or anchor fix re-runs the synthesis pair) is already handled by the spec's "a pass recorded before a later fix round stands at the blob shas it ran at" rule, so a split keeps that sentence and bounds executor context rather than wall clock.
2. Implementability — mirrors T1's method line for line; the run order (synthesis first, bikeshed last, so bikeshed's passes are at the final blobs) is stated; the rebuild-from-ledger rule covers a vanished scratchpad; the fix-round rules name the owning file, the cap, the NEEDS_HELP route, and the transcript-relocation rule that keeps the 13-file count honest. One soft spot: "Every Verification grep from tasks 3, 4, 5, 7" names ordinals, not bd IDs — resolvable through `bd list --parent bd-3ahi`, fixed below for a cold reader.
3. Verification — `5 of 5`, the 13-file count, per-scenario pass lines, the Deploy-body check on fix commits, the sibling greps, hooks. Measurable.
4. Dependencies — after T5 and T7 (the final prompt blobs); blocks T10. Correct.
5. Safety — anti-pattern 7 in both directions (no fixture/RED edits; no relaxing) and the fix-round constraints (owning file only; no cap, no restatement, no derivation change, no word-list trim) are all in Context/Boundaries.
6. Edge cases — asked: dispatch-shape ERROR (covered); nested pause (covered); missing scratchpad (covered); a fix landing after bikeshed passed (covered: re-run both); third failure (covered: NEEDS_HELP with the two edits tried); an Important on a bikeshed surface (covered: name the cost text and the anchor sentence that should have excluded it); superseded transcripts (covered). Nothing missing.
7. Red flags — the title and description contradict the body: both still list `clean x2, bad-no-critical x2, reshape x1, missing x1` while the Goal, the Implementation, and SC11 say those are NOT RUN (USER DECISION 2026-09-09). A cold executor reads the title first. Fixed below.
8. Test meaningfulness — STRUCTURAL: under the reduced plan no run exercises a real lens filling `Hits:` / `Maintainer cost:` on a real Important. bikeshed's GREEN target is zero Importants, and RED already returned zero on both runs, so its rules cannot fail on the line; synth-old/synth-new/synth-rework feed synthesis handcrafted returns, so ADDED RULE (+) there checks that synthesis preserves a line the fixture author wrote — it cannot fail for a lens-side reason; the four inherited fixtures, the only ones whose lenses write real Importants, are not run. T2's contract says this in its own words: "(+) … discriminates on real lens output (bad-no-critical's Importants) where bikeshed cannot". Consequence: GREEN passes 5 of 5 while the question R1 asks of the lenses — do they fill the line, and with what — is answered for the first time at first field use. (The epic's PEEK note records exactly that: "Finding 8 (lens-side line filling untested) closed by the LIVE RUN record".) Recommendation in the Batch Verdict: reinstate bad-no-critical ×1 — one scenario, five dispatches — as the sole real-lens run of (+). This narrows a recorded user decision on cost, so it is not applied here.
9. Scope — everything traces to R7, SC11, and anti-pattern 7; the writing-skills Deploy-body requirement traces to the contract's method of record. Nothing to trim.

**Critical Issues** (must fix):
- None at the spec-content level; the Category 8 gap is structural and escalated.

**Not applied (structural)**:
- Exceeds the ceiling — Recommended Split T9a/T9b in the Batch Verdict.
- Category 8: reinstate bad-no-critical ×1 (Batch Verdict). If the user's cost decision stands, record in the GREEN block that (+) had no real-lens run this epic, so the first field use is read as the test it is.

**Changes Made** (would have been applied via `bd update bd-syo7 --title` / `--description` and `--design`):
- Title → `Task 9: GREEN (reduced) — bikeshed x2 + 3 synthesis; bounded fix rounds; ledger`; Description → `Run the reduced GREEN set (bikeshed x2, synth-old/new/rework x1; inherited fixtures NOT RUN per USER DECISION 2026-09-09) against the edited prompts, grade against this epic's contract and the inherited rules, close loopholes within two fix rounds per scenario, record GREEN in the ledger`.
- Verification bullet → `Every Verification grep from tasks 3, 4, 5, 7 (bd-bg7w, bd-7q2n, bd-pv20, bd-rupp) still holds at this HEAD (re-run them after any fix round)`.

**Removed / Over-specified**:
- None — every item traces.

---

#### Task 10: version 3.38.0 + final consistency sweep (bd-uhzb)
**Classification**: simple (✅ Within range — ~5 min)
**Status**: ✅ Ready (one narrowing applied)

Checklist trace:
1. Granularity — one exact edit plus nine read-only greps; the conditional "fix one line in an in-scope file / NEEDS_HELP on an out-of-scope hit" is a closed rule, not judgment.
2. Implementability — every grep is verbatim with its expected output; the out-of-scope file list is SC13's, verbatim; commit given.
3. Verification — version grep, the sweep outputs listed one token each in the DONE line, the file-scope diff, hooks.
4. Dependencies — after T8 and T9 (last task). Correct.
5. Safety — anti-pattern 9 (no edits to sibling-owned files) is the NEEDS_HELP branch — the correct route; SC13 is checked here before the reviewer sees it.
6. Edge cases — asked: an in-scope grep fails (covered); an out-of-scope grep fails (covered); hooks contract test fails (a stop, reported by the DONE/BLOCKED contract). Nothing else reaches a bump.
7. Red flags — none.
8. Test meaningfulness — `./hooks/test/contract-test.sh` is the one executable test in the repo; running it here is right (no task in this epic touches hooks, so it is a regression guard, and SC lists it).
9. Scope — the Goal claims "every epic success-criterion grep green at this HEAD", but the sweep lists SC2, SC4, SC9, SC10, SC13, hooks, and slices of SC6/SC7 — SC1, SC3, SC5, SC8, SC11, SC12 are not swept. The end-of-epic reviewer gate evidences every SC (executing-plans), so extending the list would duplicate the gate; the sweep's value is the cross-file consistency checks the Why names. The Goal is narrowed to what the task delivers.

**Critical Issues** (must fix):
- None.

**Not applied (structural)**:
- None.

**Changes Made** (would have been applied via `bd update bd-uhzb --design`):
- Goal → `Bump the plugin to 3.38.0 and run the final cross-file consistency sweep: no author-presuming text left in peek, no anchor restatement at a consumer, the derivation sentence unchanged, out-of-scope files untouched, the hooks contract test green — the end-of-epic reviewer evidences every success criterion; this task checks the ones a stale sentence in one file would break.`

**Removed / Over-specified**:
- The Goal's "every epic success-criterion grep green" claim — narrowed; reason: the Changes list does not deliver it, and the reviewer gate already owns it (R8's consistency checks are what the sweep traces to).

---

### Summary of Changes

**Issues Updated** (7 of 10 — recorded, not written, per the calibration instruction):
- bd-3mdj (T1) — fixed the step-3 pointer (step 7 → step 8(b)) and the safety-line range (:774-777 under the :773 header); added the dispatch-shape ERROR rule T9 already carries (R7). Split recommended (T1a/T1b).
- bd-3m8x (T2) — added the vanished-`<sp>/red/` fallback for the grading-word extension (R7). Split optional (T2a/T2b). Structural: Run counts line superseded by the reduced GREEN scope.
- bd-7q2n (T4) — narrowed four anchor paraphrases (template lines, Rule 9, clarity item, production-readiness) to citation form (R8, anti-pattern 1).
- bd-pv20 (T5) — narrowed the reading-effort paraphrase to the anchor's test; defined "filled" once at the head of the re-check; added a `reading effort` = 0 grep (R2, R8).
- bd-2tf8 (T6) — corrected C12's trigger string (a `--request-changes` message attributed to `--approve`); trimmed the `glab mr revoke` sentence and its grep (Category 9).
- bd-syo7 (T9) — retitled/re-described to the reduced scope; named the four bd IDs in the sibling-greps bullet. Split recommended (T9a/T9b). Structural: bad-no-critical ×1 reinstatement (Category 8).
- bd-uhzb (T10) — narrowed the Goal to the sweep it delivers.

Unchanged: bd-bg7w (T3), bd-rupp (T7 — split recommended, content unchanged), bd-lcjy (T8).

## Cross-Task Analysis

### Granularity Consistency
Six tasks within range (T3 ~15, T4 ~25, T5 ~15, T6 ~20, T8 ~8, T10 ~5 min). T8 overruns the simple band (2-5 min) by a few mechanical insertions without approaching the ceiling — no reclassification. Four exceptions to the 30-minute hard ceiling (`pipeline-constants.md`): T1 (60-90 min, ten nested dispatches), T7 (45-75 min, fifteen edits into one region; corroborated by the epic's cost record of three executor runs and ~600K tokens), T9 (90+ min, thirteen dispatches plus fix rounds), and T2 at the boundary (30-40 min). No spec carries an explicit estimate — the tree classifies by section shape only, which the templates permit, so every ceiling figure here is this review's estimate. The two pressure-test tasks (T1, T9) are wall-clock-bound by dispatch, and the same shape shipped in bd-zk46 and bd-v5q5; the lead may record an override for those two rather than split. T7 is the one whose size had consequences in execution.

### Dependency Completeness
All declared; no cycles (verified per task via `bd show` DEPENDS ON / BLOCKS). Every task that reads another's output sits behind it: T2←T1 (ledger, `<sp>/red/`), T3←T2 (rules before edits), T4←T3, T5←T4, T7←T5+T6, T8←T7, T9←T5+T7, T10←T8+T9. One over-constraint: T6←T2 — forge-detection consumes nothing from T1/T2 and is not a prompt under test; T6 could run beside T1. Harmless; noted for the lead. T9's internal run order (synthesis first, bikeshed last) is the right ordering constraint inside one task and needs no dep.

### Systemic Gaps and Excess
1. **Anchor paraphrase at consumers** (T4 ×4 sites, T5 ×1). The tree's non-restatement checks grep two sentinel phrases only (`Reading effort is not a cost`, `does not itself state`); a paraphrase that drops one word passes them and trips epic anti-pattern 1 / R8. Fixed at both tasks by citation form. Pattern for the lead: a no-restatement Verification should also grep the definition's distinctive nouns (`reading effort`, `future edit`, `docstring`) at every consumer (T4, T5, T8, T10). Corroborated live by the epic's self-peek note.
2. **Mid-flight amendments landing unevenly.** Two amendments reached some specs and not their siblings: the post-RED LEAD DECISION (rule (3) / Rule 10 / Step 6 move) reached T2, T4 (9b), T5 (2b) — complete; the reduced-GREEN USER DECISION reached SC11 and T9's body but not T9's title/description or T2's `Run counts:` line. The ledger stays honest (T9's `NOT RUN` line), but two specs state different constants. Fixed at T9 (title); recommended at T2 (superseded note). Rule: an amendment that changes a value two specs state moves both.
3. **Real-lens test surface for R1's line is absent under the reduced plan** (Category 8, T9). bikeshed cannot fail on the line (target and RED are both zero Importants); the synthesis fixtures carry handcrafted lines; the inherited fixtures are not run. ADDED RULE (+) — the only rule that reads a real lens's `Hits:` / `Maintainer cost:` — has no run. Recommendation in the Batch Verdict (bad-no-critical ×1).
4. **No test reaches Step 7** (R4 follow-up line, R6 approval election): fixtures run at rung 3 with no forge and the CLI is absent. T7 says so; the epic's manual-validation STOP names the live forge run. No spec change — noted so grep coverage is not read as behavior coverage at the reviewer gate.
5. **Dispatch-shape ERROR handling** present in T9, absent in T1 (identical dispatch shape). Fixed at T1.
6. **`## Tests` — "None — …" on every pure-documentation and test-run task** (T1-T7, T9). The template says omit the section for pure-doc tasks; the tree carries it with a one-line reason, consistently. Harmless, zero executor cost — not trimmed.
7. **Strengths worth copying** (not findings): every line-number reference pairs with a relocation anchor; every task has a `git diff HEAD~1 --stat` file-scope check; shared-file edits (T5/T7) verify the sibling region byte-identical by `diff`; simple tasks use per-line greps to defeat pre-existing words; every ledger-pointer note is heredoc-only and never `--notes`; the `.beads/` porcelain allowance is stated where the executor appends notes.

### Classification Consistency
No mismatches. T8 and T10 are simple-shaped and simple in content. T3 and T6 are medium-shaped with mostly verbatim text — each carries one judgment step (T3 step 4's contradiction re-read; T6's width-wrap and refusal-behavior prose) and a Boundaries section that fences a definition file other epics touch, so medium is right. T1, T2, T9 are medium by shape and over the ceiling by size (above). No simple task was penalized for lacking a 3+ list or a task-level anti-patterns section.

### Epic Coverage
| Success Criterion | Covered By |
|-------------------|------------|
| SC1 Anchor bar (Hits / Maintainer cost / reading-effort / site-already-states) | bd-bg7w |
| SC2 Fallback past Important (`otherwise Suggestion`; `Important, never Critical` gone) | bd-bg7w |
| SC3 Agent templates (3 + 3 lines; Rule 9 names both) | bd-7q2n |
| SC4 Posture (no `junior` in agent + skill; `colleague` in the opening) | bd-7q2n (agent), bd-uhzb (sweep covers `skills/peek/SKILL.md`) |
| SC5 Synthesis moves (both markers, in Step 6) | bd-pv20 |
| SC6 Follow-up line (`no re-review` ≥ 2; opt `follow-up line`) | bd-rupp, bd-lcjy |
| SC7 Forge surface (identity, approve, self-approval string, C11+ rows) | bd-2tf8 |
| SC8 Approval election (`self-peek`, withdraw cases, delivery order, `you are`) | bd-rupp |
| SC9 Derivation shape kept; no `Maintainer cost` in loop-interfaces | bd-lcjy, bd-uhzb |
| SC10 One bar (4 consumers cite; `does not itself state` only in the anchor) | bd-7q2n, bd-pv20, bd-lcjy, bd-uhzb |
| SC11 Pressure tests (ledger; RED/CONTRACT/GREEN = 3; `5 of 5`; RED failed ≥ 1 rule) | bd-3mdj, bd-3m8x, bd-syo7 |
| SC12 Version 3.38.0; README :40/:76/:91 and CLAUDE.md :159/:208 | bd-uhzb, bd-lcjy |
| SC13 Out-of-scope files untouched | bd-uhzb |
| `./hooks/test/contract-test.sh` passes | bd-uhzb |
| Pre-commit hooks passing | every task (standing line) |

| Requirement | Covered By |
|-------------|------------|
| R1 Important positive bar | bd-bg7w |
| R2 Fallback past Important; Step 6 applies it with markers | bd-bg7w, bd-pv20 |
| R3 Colleague posture; no junior text; clarity → Suggestion | bd-7q2n |
| R4 Follow-up line in the comment and rung 2/3 text | bd-rupp (bd-bg7w states the split at the anchor) |
| R5 forge-detection identity read + approve write + caveats + refusal behavior | bd-2tf8 |
| R6 Gated approval election; self-peek and rungs 2/3 comment-only; AWC resolved | bd-rupp |
| R7 Bikeshed fixture; RED ×2; GREEN APPROVE on two runs; inherited rules kept | bd-3mdj, bd-3m8x, bd-syo7 |
| R8 Consumers cite, none restates; derivation shape kept | bd-7q2n, bd-pv20, bd-lcjy, bd-uhzb |
| R9 Minor bump; README and CLAUDE.md peek sentences | bd-lcjy, bd-uhzb |

No criterion or requirement lacks a task.

### Batch Verdict
NEEDS REVISION ⚠️

The content of the tree is ready: every anchor was verified at the pre-epic commit, every Verification is measurable, every edge case with a consequence is stated, and coverage is complete. The revision items are structural — the lead decides each:

1. **Recommended Split: bd-3mdj (T1, est. 60-90 min, exceeds ceiling)**
   1. **T1a: bikeshed fixture, scanner, ledger opened** (medium, `Executor: opus`)
      - Goal: build the bikeshed fixture beside the four inherited ones, write `<sp>/scan.py`, run the fixture suite, write the production-safety line, and open `docs/ledgers/bd-3ahi-pressure-tests.md` with the header and the FIXTURE SCRIPT block.
      - Implementation: T1 steps 1-3, 5, and 8(a)-(b); commit the ledger.
      - Verification: T1's fixture/tree/suite/summary-loop greps; `grep -c '^FIXTURE SCRIPT (bd-3ahi'` — 1; `grep -c 'production-safe because:'` — 5; file-scope diff; hooks.
      - Depends on: none.
   2. **T1b: RED baseline ×2** (medium, `Executor: opus`)
      - Goal: extract the by-file prompts, run RED twice against bikeshed, extract the record, append the RED BASELINE block, add the notes pointer.
      - Implementation: T1 steps 4, 6, 7, 8(c) and the commit/notes append; rebuild `<sp>` from T1a's ledger block if the session changed.
      - Verification: `ls <sp>/red | wc -l` — 10; `^RED BASELINE` — 1; `^- bikeshed run[12]:` — 2; `^- OBSERVATIONS:` — 1; file-scope diff; hooks.
      - Depends on: T1a.

2. **Recommended Split: bd-rupp (T7, est. 45-75 min, exceeds ceiling)**
   1. **T7a: follow-up line (R4)** (medium)
      - Goal: the draft comment and the rung 2/3 copy-paste text carry the three-case follow-up line under the verdict; quick reference, the third excuse, and the checklist insert say so.
      - Implementation: T7 steps 5, 7(a), 12 (third bullet), 13 (the insert into the existing Step 7 line), and the follow-up clause of step 1's row 7 cell.
      - Verification: `no re-review` ≥ 3; the two fixed sentences = 1 each; `wait for the re-peek` — 1; Step-6-untouched diff; file-scope diff; hooks.
      - Depends on: bd-pv20 (T5).
   2. **T7b: gated forge approval election (R6)** (medium, `Executor: opus`)
      - Goal: eligibility before phase A, the paired offer, phase B's fourth item, the fixed delivery order, failures reported never retried, rule 1, the first two excuses, the new checklist line, the path re-read.
      - Implementation: T7 steps 2, 3, 4, 6, 7 (second paragraph), 8, 9, 10, 11, 12 (first two bullets), 13 (new line), 14, and the approval clauses of step 1's row 7 cell — written as principles (one sentence per condition and per failure posture), not enumerated cases, to land under the ceiling.
      - Verification: T7's remaining greps (`self-peek` ≥ 2, `you are <login>` ≥ 2, `Approval eligibility` ≥ 2, `identity read failed` — 1, `already approved at this tip` — 1, `fixes, comment, approval` ≥ 1, `Approval failures` — 1, `never re-submitted` — 1, no restated forge command, no request-changes path); Step-6-untouched diff; file-scope diff; hooks.
      - Depends on: T7a, bd-2tf8 (T6).

3. **Recommended Split: bd-syo7 (T9, est. 90+ min, exceeds ceiling)**
   1. **T9a: synthesis fixtures GREEN ×3** (medium, `Executor: opus`)
      - Goal: run synth-old, synth-new, synth-rework once each against the post-edit Step 6, grade against this epic's contract (old, rework) and the bd-zk46 rules (new), fix rounds confined to the owning file with the cap, record three ledger lines.
      - Implementation: T9 steps 1 (blob record), 2 (regenerate `step6.md`), 3, 4, 5 (cap applies; a fix re-runs all three), the three `- synth-*:` ledger lines under a `GREEN (synthesis, …)` sub-block.
      - Verification: `ls <sp>/green/ | wc -l` — 3; the three `pass` lines; Deploy-body check on fix commits; hooks.
      - Depends on: bd-pv20 (T5).
   2. **T9b: bikeshed GREEN ×2 and GREEN RESULT** (medium, `Executor: opus`)
      - Goal: two fresh-worktree bikeshed runs at the final blobs, graded rule by rule; a fix that touches Step 6 or the anchor re-runs T9a's three (declared cross-task re-run, T9a's lines re-stamped at the new blobs); the GREEN block and GREEN RESULT written; notes pointer appended.
      - Implementation: T9 steps 1, 2 (bikeshed ×2 last), 4, 5, 6.
      - Verification: `ls <sp>/green/ | wc -l` — 13; `^GREEN RESULT` — 1 reading `5 of 5`; both `- bikeshed run[12]: pass`; sibling greps from bd-bg7w, bd-7q2n, bd-pv20, bd-rupp hold; hooks.
      - Depends on: T9a, bd-rupp (T7).
   The lead may instead record an override for T1 and T9 (wall clock is dispatch-bound; the shape shipped in bd-zk46 and bd-v5q5) — the split bounds executor context, which is the ceiling's purpose, but does not shorten the run.

4. **Optional Split: bd-3m8x (T2, est. 30-40 min, at ceiling)** — T2a: synthesis fixture reconstruction (step 2) + the SYNTHESIS FIXTURES ledger block (step 4); T2b: contract block (steps 1, 3) + notes pointer (step 5); T2b depends on T2a. Lower priority than the three above.

5. **Category 8 structural — reinstate bad-no-critical ×1 in the GREEN plan** (T9 / T9b). It is the one scenario where real lenses write real Importants, so it is the only run on which ADDED RULE (+) — and R1's line — can fail for a lens-side reason. Cost: one scenario, five dispatches. This narrows the USER DECISION of 2026-09-09; if the decision stands, the GREEN block records that (+) had no real-lens run and the first field use is the first test.

6. **Amendment consistency** — T2 step 3's `Run counts:` gains the superseded note; T9's title/description match its Goal (recorded above).

7. **Apply the seven spec updates** recorded under Changes Made / Removed (bd-3mdj, bd-3m8x, bd-7q2n, bd-pv20, bd-2tf8, bd-syo7, bd-uhzb), then re-run `hyperpowers:sre-task-refinement` in batch mode.
