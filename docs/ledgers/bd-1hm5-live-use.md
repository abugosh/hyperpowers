# bd-1hm5 live use — verbatim record

Epic bd-1hm5 (Harsh but fair: in-epic judges under one anchor, v3.40.0) was built author/editor. Acceptance was one live use: the rewritten end-of-epic reviewer (`agents/reviewer.md`, read from the working tree by path — the installed plugin copy is stale on a branch) run against the closed, merged epic bd-3ahi with the delta range 6502ad7..e574c31 named in the dispatch and no bd writes. Scratchpad files do not survive sessions, so the return is recorded here verbatim. The outcome and the one prose fix it produced are in the epic's bd notes.

## Reviewer return (verbatim)

## Implementation Review: APPROVED

### Epic: bd-3ahi - Harsh but fair: peek verdict bar and forge approval

### Architect Summary
The review pipeline's Important tier now has a checkable bar: an Important finding must name either who hits the defect or the next edit that pays for it, the report-assembly step demotes any finding that cannot, and a Critical that fails its own class check falls to Important only when that line is filled and otherwise to Suggestion, every move marked in the report. The draft comment tells the author which items need a re-review and which they fix and self-certify, and the forge-command reference gained an identity read and an approve write for both GitHub and GitLab, so peek can submit an approval behind the user's exact-action gate on an approve verdict, with or without requested changes, when the reviewer is not the author. Two deviations were decided by the user during the build and are recorded in the governance ledger: the pressure-test set was cut to the new bikeshed fixture plus the three synthesis fixtures on cost grounds, and the approval step was rewritten from an enumerated contingency list to a short principles paragraph, which superseded several of that task's original wording checks. One anti-pattern was crossed in letter at branch close-out: the epic's tracker notes were rewritten to move governance blocks into a ledger file after the record exceeded the tracker's line limit; every moved line is verbatim in the ledger and nothing was lost. Remaining for manual validation: a live forge run of the approval path on a real merge request where you are not the author, since no forge CLI was available during authoring and all six new commands sit in the unverified-caveats table, plus a first-use read of the trimmed approval step.

### Tasks Reviewed
- bd-3mdj: Task 1: bikeshed fixture + RED baseline (two runs, new ledger) — PASS
- bd-3m8x: Task 2: pressure-test contract + reconstructed synthesis fixtures — PASS
- bd-bg7w: Task 3: Severity Anchor — Important bar (Hits / Maintainer cost), fallback past Important — PASS
- bd-7q2n: Task 4: agents/peek.md — colleague posture, Hits / Maintainer cost lines, clarity as Suggestion — PASS
- bd-pv20: Task 5: skills/peek/SKILL.md Step 6 — Important demotion and two-stage Critical fallback — PASS (one Verification phrase relocated to the anchor by a later lead fix; see per-task table)
- bd-2tf8: Task 6: forge-detection.md — identity read, approve write, caveats C11-C16 — PASS
- bd-rupp: Task 7: skills/peek/SKILL.md Step 7 — follow-up line, gated forge approval, identity precondition — PASS at task close; seven of its Verification greps are superseded at the delta's end by the user-directed trim (see per-task table and Suggestion 1)
- bd-lcjy: Task 8: satellites — opt follow-up-line sentence, loop-interfaces check, README/CLAUDE.md peek lines — PASS
- bd-syo7: Task 9: GREEN — bikeshed x2, clean x2, bad-no-critical x2, reshape x1, missing x1, 3 synthesis; bounded fix rounds; ledger — PASS (reduced scope per USER DECISION 2026-09-09; SC11 amended to 5 of 5)
- bd-uhzb: Task 10: version 3.38.0 + final consistency sweep — PASS

Review basis: range `6502ad7..e574c31` (28 commits), `$DELTA` = 14 files. The working tree (HEAD 96bedb5, bd-1hm5 in progress) differs from e574c31 on five delta files — `.beads/issues.jsonl`, `.claude-plugin/plugin.json`, `CLAUDE.md`, `README.md`, `skills/common-patterns/pipeline-constants.md` — plus `skills/common-patterns/loop-interfaces.md` outside the delta; every read and grep on those files below was taken at `e574c31` via `git show`. The remaining delta files are byte-identical between the working tree and e574c31 (`git diff e574c31 --stat` on the delta list).

### Evidence Summary
| Epic Requirement / Criterion | Status | Evidence |
|-----------------|--------|----------|
| R1 Important defined with a positive bar (Hits / Maintainer cost; never "confusion") | Met | pipeline-constants.md@e574c31:101-119 — Important "only when ... fills exactly one of two lines"; `Hits:` :107-111 with reachability clause; `Maintainer cost:` :112-117 with "does not itself state" (:114) and "Reading effort is not a cost" (:115); "A finding that fills neither line is Suggestion" :119 |
| R2 Fallback runs past Important; Step 6 applies it with visible markers | Met | pipeline-constants.md@e574c31:76-78 "not Critical: it is Important when it fills one of the Important lines below on its own, otherwise Suggestion"; skills/peek/SKILL.md:120 two-stage move with `[downgraded: no consequence named]` / `[downgraded: no consequence named; no cost named]` and `[downgraded: no cost named]`; exercised: ledger:1111 (synth-old, both markers, APPROVE) and ledger:1113 (synth-rework, stop-at-Important) |
| R3 Colleague posture; no junior presumption; clarity item yields Suggestion unless it fills the bar | Met | agents/peek.md:8 ("colleague under load ... never at the person"); `grep junior` = 0 in agents/peek.md and skills/peek/SKILL.md (the base's one hit, the CODE Clarity item, removed in the range diff); agents/peek.md:114 "A clarity observation is a Suggestion unless it fills the Important bar's `Maintainer cost:` line" |
| R4 Draft comment carries the follow-up line; also in rung 2/3 copy-paste | Met | skills/peek/SKILL.md:177 — three fixed cases under the verdict line, and "At rung 2/3 hand over the same text — follow-up line and marker included"; quick reference :25; checklist :238 |
| R5 forge-detection gains identity read and approve write per forge via caveats; self-approval refusal documented | Met | forge-detection.md:205-222 (Identity: `gh api user --jq .login`, `glab api user \| jq -r .username`); :274-294 (Approve: `gh pr review <number> --approve`, `glab mr approve <iid> --sha <reviewed-tip>`); :296-320 self-approval per forge (GitHub refusal string :299; GitLab Free self-approve + bare 401 :305-311); C11-C16 :343-348, each with a "Settled by:" clause |
| R6 Approval as a gated election on APPROVE (AWC resolved: both), identity precondition, nothing submitted without exact-action approval, self-peek and rung 2/3 comment-only | Met | skills/peek/SKILL.md:175 (offer on APPROVE / APPROVE WITH CHANGES at rung 1 after the identity read; withdrawals: identity failure, self-peek, already approved via C14/C15, target not open, rung 2/3; "self-peek is comment-only on both forges"); :181 phase B shows the exact approve command and the identity line; :201 rule 1; Open-for-Design resolved in Key Decisions row 2 |
| R7 Bikeshed fixture joins the set; RED recorded; GREEN = APPROVE with (none)/Suggestion-only on two runs; inherited four keep their rules | Met | ledger:14-866 script with FIXTURE 5 (`# FIXTURE 5: bikeshed` 1 hit; inherited code byte-identical — diff against bd-zk46:23-770 changes only three header comment lines and the summary-loop line, adds 106); RED :875-880 (run1 APPROVE 0/0/3, run2 APPROVE 0/0/2); GREEN :1108-1109 (both APPROVE, C/I/S 0/0/3, Suggestion-only, 0 downgrade markers); inherited rules "stand unchanged" :888 and :1110 |
| R8 Every consumer cites the anchor, none restates; derivation shape kept | Met | `Severity Anchor` at e574c31: agents/peek.md 20, skills/peek/SKILL.md 4, skills/opt/SKILL.md 3, loop-interfaces.md 1; `git grep -l 'does not itself state' e574c31 -- agents skills` → pipeline-constants.md only; `git diff 6502ad7..e574c31 -- loop-interfaces.md` empty; derivation sentence present once (loop-interfaces.md@e574c31:116-117) |
| R9 Minor bump; README and CLAUDE.md peek sentences updated | Met | plugin.json@e574c31 `"version": "3.38.0"` (from 3.37.0); commit bb3ea19 diff: README.md:40, :76, :91 and CLAUDE.md:159, :208 |
| SC1 Anchor bar greps | Met | @e574c31: `Hits:` 2 (:107, :132), `Maintainer cost:` 2 (:112, :132) — all inside Severity Anchor (:67-140); `Reading effort is not a cost` 1; `does not itself state` 1 |
| SC2 Fallback past Important | Met | @e574c31: `otherwise Suggestion` 1 (:78); `Important, never Critical` 0 |
| SC3 Agent templates | Met | `^  Hits:` 3, `^  Maintainer cost:` 3 (agents/peek.md:138-139, :195-196, :254-255); Rule 9 names both (:44, grep = 1) |
| SC4 Posture | Met | `junior` 0 / 0; `colleague` 1, at agents/peek.md:8 (opening paragraph) |
| SC5 Synthesis moves | Met | both markers at skills/peek/SKILL.md:120 (Step 6) |
| SC6 Follow-up line | Met | `no re-review` 4 (skills/peek/SKILL.md:25, :177, :222, :238); `follow-up line` 1 (skills/opt/SKILL.md:67) |
| SC7 Forge surface | Met | forge-detection.md: `gh api user --jq .login` 1; `glab api user` 2; `gh pr review` 4; `glab mr approve` 4; `Can not approve your own pull request` 2; `^\| C1[1-9] \|` 6 |
| SC8 Approval election | Met | `self-peek` 3; identity read, the four withdrawal cases, and comment-only self-peek at skills/peek/SKILL.md:175; delivery order "fixes, comment, approval" :181; `you are` 1 (:181 identity line) |
| SC9 Derivation shape kept | Met | loop-interfaces.md@e574c31: derivation grep 1; `Maintainer cost` 0 |
| SC10 One bar | Met | 4 of 4 consumers cite; restatement phrase only in pipeline-constants.md |
| SC11 Pressure tests | Met | ledger exists (1116 lines); `^RED BASELINE\|^PRESSURE-TEST CONTRACT\|^GREEN RESULT` = 3 (:875, :882, :1114); GREEN RESULT reads `5 of 5` (:1114); RED records both runs' verdict and C/I/S (:877-878); rule (3) recorded as RED-failed (:887 "RED failed: rule (3)") |
| SC12 Version and satellites | Met | @e574c31 version 3.38.0; README `approv` 3 (lines 40, 76, 91 — per-line: 40 has "self-certify" and "forge approval", 76 "gated forge approval", 91 "Maintainer cost" and "forge approval"); CLAUDE.md `approv` 2 (159 "Maintainer cost" + "gated forge approval"; 208 "self-certify") |
| SC13 Out-of-scope files untouched | Met | `git diff 6502ad7...e574c31 --stat` on the eight listed paths: empty |
| `./hooks/test/contract-test.sh` passes | Met | test-runner: 10 passed, exit 0 |
| Pre-commit hooks passing | Met | `.git/hooks/pre-commit` is the bd JSONL flush hook (exit 0 when bd is present); no pre-commit framework config exists; all 28 range commits landed through it |

### Delta Checks
- Quality gates — Tests: PASS (hooks contract suite, 10 passed, 0 failed, via test-runner) · Format: N/A (markdown plugin, no formatter configured) · Lint: N/A (no linter; no `.pre-commit-config.yaml`)
- TODOs / stubs / placeholders / ignored tests: none in `$DELTA` (`rg "\[TODO\]|\[TBD\]|\[placeholder\]|\[fill in\]"` → none; the `todo|fixme` hits at CLAUDE.md:309 and README.md:158 are the word "TodoWrite" on lines this range did not add)
- Refactoring remnants / unused code / orphaned references: none. The `fallback|legacy` hits are pre-existing forge-detection C2 vocabulary (:244, :334), opt's C10 sentence (:182), peek Step 8's "fallback path" (:194), and ledger prose describing R2's own two-stage fallback. Cross-references resolve: skills/peek/SKILL.md cites C2, C14, C15, Identity, Approve, Shared Rules 9 and 10, Peek Fix Carve-out — all present; the bd-zk46 ledger's RECON markers stand at :838/:870/:904/:936 as the 3ahi ledger cites; the governance ledger's commit hashes (2847687, 89144f5, 36dd31c) exist in the range
- Epic anti-patterns:
  - Restating the Important bar at a consumer — not found (SC10; agents/peek.md template lines read "what the Severity Anchor requires" ×12; README/CLAUDE describe the line, they do not define it). Residual paraphrase of the reading-effort exclusion at agents/peek.md:44 and skills/peek/SKILL.md:120 — Suggestion 3
  - Finding-count cap — not found (`rg -i "at most [0-9]+ important|finding[- ]count cap|no more than [0-9]+"` → none; the only "at most" phrases are sentence ceilings and one-comment-per-run)
  - Forge write without phase-B approval; automatic retry; second comment after failure — not found (skills/peek/SKILL.md:173, :181, :201 exact command/target/identity line; :183 "never retry"; :177 "At most one comment leaves a run"; forge-detection.md C12 "never re-run", C13 "never retry")
  - Approval election on self-peek or rungs 2/3 — not found (skills/peek/SKILL.md:175, :201, :221)
  - Approval without the comment — not found (skills/peek/SKILL.md:175 "An approval always rides with a comment"; forge-detection.md:279-280)
  - Junior-engineer presumption — not found (`rg -i "junior|novice|inexperienced|beginner"` on agents/peek.md and skills/peek/SKILL.md → 0)
  - Fixture/RED edits to pass; rule relaxed at grading — not found. RED block vs its original commit (4bc8b45): only :873 (grep-recipe correction) and :879 (RECORD CORRECTION appended, d9efda5, Stage 2 of task 1) differ; verdict and count fields unchanged; GREEN "fix rounds: none" (:1114); inherited rule sets "stand unchanged" (:888, :1110); the four inherited fixtures' script code is byte-identical to bd-zk46:23-770
  - Change to the derivation sentence — not found (range diff on loop-interfaces.md empty)
  - Edits to reviewer.md / code-reviewer.md / executing-plans / plan-side files — not found (SC13 empty)
  - Ledger content in bd notes; `--notes` overwrite — letter crossed at e574c31 (branch close-out): the notes field was rewritten to move governance blocks into `docs/ledgers/bd-3ahi-governance.md` after the JSONL line reached 66,165 bytes. Verified: all 49 moved lines are byte-identical to the pre-move notes (at f7b4d96); 0 pre-move lines are absent from both the new notes and the ledger; the line is now 42,867 bytes (notes 13,976, down from 37,007). No ledger content ever sat in the notes (pressure-test evidence lives in the ledger; the notes carried pointer lines and gate states). Purpose served, letter crossed — Suggestion 2
  - `hyperpowers:peek` dispatch or retyped agent body in pressure tests — not found (RED :875-876 and GREEN :1106-1107 record `general-purpose` dispatches with the body delivered by file)

### Test Quality Audit
- Meaningful tests: 6 — bikeshed ×2 (rule (3) discriminates: RED failed it on both runs, GREEN passes; rules (1), (2), (4)-(8), (10) regression guards; rule (9) vacuous at RED and checked on GREEN lens output), synth-old (discriminates: pre-edit APPROVE WITH CHANGES → APPROVE, both demotion markers), synth-rework (guards R2's stop-at-Important branch — the bug it catches is a re-check that demotes a Trigger-less Critical past Important despite a filled cost line), synth-new (guards the lead-added-Critical exemption — the bug it catches is the new demotion clause demoting a synthesis-filed Critical that carries no Hits / Maintainer cost line, which skills/peek/SKILL.md:120's exemption prevents), LIVE RUN (ledger:1116 — 8 Importants on real content, each with exactly one filled line, 0 demotions)
- Tautological tests: 0
- Strengthen (Suggestions): 1 — bikeshed's R7 target (APPROVE, no Important) was already true at RED (ledger:879 records this), so that fixture evidences the no-change-Suggestion rule and the template plumbing rather than the bar itself; the bar's evidence is synth-old and the live run

### Suggestions (non-blocking)
1. bd-rupp's Verification section is stale against the delta's end state. The user-directed trim (2847687), the round-1 fix (89144f5) and the self-peek fixes (f7b4d96) removed the enumerated mechanism, so these greps now read: `Approval eligibility` 0 (spec ≥2), `identity read failed` 0, `already approved at this tip` 0, `Approval failures` 0, `never re-submitted` 0, `carries neither the target` 0 (now "carries none of them", 1), `you are <login>` 1 (spec ≥2). R4, R6, SC6 and SC8 hold at the end state and the decision is recorded (governance ledger :157-160). A one-line amendment note on bd-rupp, and on bd-pv20 for `that line is the lens` (now 0 — relocated to pipeline-constants.md@e574c31:124-125 "the line is a lens's to write", cited from skills/peek/SKILL.md:120), would keep a later re-verification from tripping.
2. The epic's anti-pattern "notes stay under 40KB" did not prevent the wedge: notes were 37,007 bytes when the line hit 66,165, because the design field is about 28KB. "NO `--notes` overwrite" also forbids the recovery the lead performed. A later pass on the brainstorming epic template (and the feedback_bd_jsonl_line_limit memory, which carries the same 40KB figure) should bound the JSONL line rather than the notes field and allow the verbatim move at branch close-out. Plugin-level, outside this epic's files.
3. agents/peek.md:44 (Shared Rule 9) and skills/peek/SKILL.md:120 each paraphrase the anchor's reading-effort exclusion in one clause ("a cost line that names only reading effort ... is empty"). Both are spec-inherited (bd-7q2n step 2; bd-pv20 step 1); the self-peek removed one duplicate and left these two. Citing "filled in the anchor's terms" alone would leave one definition. Sibling already filed: Rule 9's elliptical clause.
4. pipeline-constants.md@e574c31:98 "A `partial` aim is Important, not a delivery Critical" reads unconditional beside the filled-line requirement at :101-104; agents/peek.md:223 makes the line required on the agent side. Already filed (governance ledger :137 item 4) as a later-pass anchor clause.
5. Two delta files no task spec names: `.claude/agent-memory/hyperpowers-code-reviewer/MEMORY.md` (58977e1) and `epic-bd-3ahi-peek-verdict-bar.md` (force-added in f7b4d96 past `.gitignore:1`, like its four tracked siblings). Treated as authorized by the code-reviewer agent's standing `memory: project` setting (agents/code-reviewer.md@e574c31:5), not by any spec; content reviewed and consistent with the ledger (GREEN reduced to 5 runs; shas re-derived by the reviewer). Specs' clean-tree exemption names `.beads/` only; naming agent-memory paths beside it would make this explicit. The other unnamed files — `docs/ledgers/bd-3ahi-governance.md` (authorized by the epic's own anti-pattern clause "the ledger lives in docs/ledgers/", content verified verbatim above) and the two-line POINTER appended to `docs/ledgers/bd-zk46-pressure-tests.md` (self-peek Q5, lead-direct on the user's instruction; accurate) — need no action.

### Per-task Verification (evidence layer)

#### bd-3mdj — Task 1
| Verification Item | Status | Evidence |
|---|---|---|
| `fixtures.sh` runs twice, exit 0 | Met (indirect, multiple signals) | script survives at `<sp>/fixtures.sh` (30,012 bytes) with `<sp>/repos/` holding five repos; RED (:875) and GREEN (:1106-1107) both record the five TREE shas, bikeshed 9bbf967 identical across them; Stage 2 of task 9 re-derived the shas (agent-memory note) — not re-run here |
| log shows both commit messages | Met (indirect) | ledger:873 and the FIXTURE 5 block (`Add refund() to payments client`, 3 hits) |
| bikeshed main tree = clean main; branch tree ≠ d1c90ac | Met | ledger:875 (main tree 5e6db6c "identical to clean's main"; branch TREE 9bbf967) |
| unittest OK, 10 tests | Met | ledger:873 "`python3 -m unittest discover -q` at the worktree reports OK on 10 tests" |
| `ls <sp>/red` = 10 | Met | `ls` now: 10 files |
| ledger greps (RED 1; FIXTURE SCRIPT 1; production-safe 5; run lines 2; OBSERVATIONS 1) | Met | 1 / 1 / 5 / 4 (2 RED + 2 GREEN added by task 9) / 1 |
| commit touches only the ledger | Met | 4bc8b45 stat: `docs/ledgers/bd-3ahi-pressure-tests.md` only |
| `"bikeshed:feature/refund"` in the script once | Met | ledger:862 (the summary loop); the second hit at :14 is header prose |
| Pre-commit hooks | Met | bd flush hook |

#### bd-3m8x — Task 2
| Verification Item | Status | Evidence |
|---|---|---|
| CONTRACT 1; `RED failed:` 1; `leave the code as it stands` ≥1; `ADDED RULE (+)` ≥1; SYNTHESIS FIXTURES 1 | Met | 1 / 1 / 1 / 9 / 1 |
| synth dirs hold four files each | Met | `ls`: 4 / 4 / 4 |
| RECON.md diffs against bd-zk46 :839-869 / :871-903 / :905-935 empty | Met | all three `diff` runs identical now |
| synth-rework CODE.md: `Maintainer cost:` 3; `Trigger:\|Consequence:` 0; `Severity: Critical` 1; `Critical class: production` 1 | Met | 3 / 0 / 1 / 1 |
| synth-old files carry no Hits/Maintainer cost; CODE has no Trigger/Consequence | Met | 0 / 0 / 0; 0 |
| commit touches only the ledger | Met | 2abc4b8 stat: ledger + `.beads/` (spec-exempt) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-bg7w — Task 3 (all at e574c31)
| Verification Item | Status | Evidence |
|---|---|---|
| `Hits:` ≥1 and `Maintainer cost:` ≥1 inside the Severity Anchor | Met | 2 and 2, at :107/:112/:132, section :67-140 |
| `Reading effort is not a cost` 1; `does not itself state` 1 | Met | 1 / 1 |
| `otherwise Suggestion` ≥1; `Important, never Critical` 0 | Met | 1 / 0 |
| `fix and self-certify` 1 | Met | 1 (:133) |
| `Consumers cite this section; none restates it.` 2 | Met | 2 |
| scope line :67-72 names peek's lenses, synthesis, opt only | Met | :69-71 unchanged in the range diff |
| commit touches only pipeline-constants.md | Met | ff58f4e stat; diff hunks confined to :73-81 and :98-139 (Severity Anchor) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-7q2n — Task 4
| Verification Item | Status | Evidence |
|---|---|---|
| `^  Hits:` 3; `^  Maintainer cost:` 3 | Met | 3 / 3 |
| omit sentence ×3 | Met | "exactly one of Hits or Maintainer cost appears on every Critical and every Important" 3 (:147, :204, :263) |
| `junior` 0; `harsh` 0; `colleague under load` 1 | Met | 0 / 0 / 1 |
| no restatement phrases | Met | 0 |
| `Severity Anchor` ≥19 | Met | 20 |
| `never-drop, never-overstate mechanism` 1 | Met | 1 (:38) |
| Rule 10 sentence: `leave the code as it stands` 1; `deferred until some future condition holds` 1 | Met | 1 / 1 (:45) |
| `a Suggestion unless it fills` 1; `otherwise a Question for the Author` 1 | Met | 1 (:114) / 1 (:115) |
| DELIVERY: `who relies on the capability the merge record claims` 1; `the check the next change to it must do by hand` 1 | Met | 1 (:223) / 1 (:225) |
| commit touches only agents/peek.md | Met | 5393d04 stat (+ `.beads/`) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-pv20 — Task 5
| Verification Item | Status | Evidence |
|---|---|---|
| three markers ≥1 each | Met | 1 / 1 / 1 (:120) |
| `it never fills one in` 1 | Met | 1 (:120) |
| `[moved: no change asked]` ≥1; `that line is the lens` 1 | Met by relocation | 1; 0 — the sentence moved to the anchor by f7b4d96 (pipeline-constants.md@e574c31:124-125) and :120 now cites "the Severity Anchor's exemption for synthesis-filed Criticals" |
| `Critical and Important demotions` 1 (quick_reference); `demoted to Suggestion` ≥1 (checklist) | Met | 1 (:24) / 1 (:237) |
| Step 7 untouched by this task | Met | Step 7 identical between 5393d04 and 9580af0 |
| no restatement phrases | Met | 0 |
| commit touches only skills/peek/SKILL.md | Met | e13f540 stat (+ `.beads/`) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-2tf8 — Task 6
| Verification Item | Status | Evidence |
|---|---|---|
| `gh api user --jq .login` 1; `glab api user` ≥2 | Met | 1 / 2 |
| `retry once` 0 | Met | 0 |
| approve commands ≥1 each | Met | `gh pr review <number> --approve` 2; `glab mr approve <iid> --sha` 2 |
| refusal strings; `glab mr revoke` 1 | Met | `Can not approve your own pull request` 2; `401 Unauthorized` 1; `glab mr revoke` 1 |
| `^\| C1[1-6] \|` 6; `^\| C[0-9]* \|` 16 | Met | 6 / 16 |
| `^### Identity` 1; `^### Approve` 1 | Met | 1 / 1 (:205, :274) |
| `request-changes` ≥1 and no fenced request-changes command | Met | 2 / 0 |
| Detection section unchanged | Met | identical between 6502ad7 and e574c31; C1-C10 rows identical |
| commit touches only forge-detection.md | Met | 0980604 stat (+ `.beads/`) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-rupp — Task 7 (closed at 36dd31c; end-state greps below)
| Verification Item | Status | Evidence |
|---|---|---|
| `no re-review` ≥4; `wait for the re-peek` 1 | Met | 4 / 1 |
| `carries neither the target` 1 | Superseded | 0; the same fact reads "RECON's return carries none of them" (:175) after the trim (2847687, USER DECISION, governance ledger :157-160) |
| `self-peek` ≥2 | Met | 3 |
| `you are <login>` ≥2 | Superseded | 1 (:181); SC8's ≥1 holds |
| `Approval eligibility` ≥2; `identity read failed` 1; `already approved at this tip` 1 | Superseded | 0 / 0 / 0 — the eligibility paragraph and its five withdrawal lines collapsed into :175 (identity failure, self-peek, "already approved (C14 and C15 in that file give each forge's test)", target not open, rung 2/3) |
| `fixes, comment, approval` ≥1 | Met | 2 (:25, :181) |
| `Approval failures` 1; `never re-submitted` 1 | Superseded | 0 / 0 — one failure rule at :183 ("report the tool's output verbatim, never retry or work around it") |
| follow-up wordings ×2 | Met | 1 / 1 (:177) |
| no forge command restated | Met | `gh pr review\|glab mr approve\|gh api user\|glab api user` 0 |
| no request-changes election | Met | 0 |
| Step 6 untouched by this task's rounds and the trim | Met | Step 6 identical between 9580af0 and 2847687 |
| commit touches only skills/peek/SKILL.md | Met | 4a5bfbe stat (+ `.beads/`); the lead's 66362b5 also touched forge-detection.md (in-scope file, Stage 2 lead fix) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-lcjy — Task 8 (README/CLAUDE at e574c31)
| Verification Item | Status | Evidence |
|---|---|---|
| `follow-up line` in opt = 1 | Met | 1 (:67) |
| loop-interfaces derivation 1; no diff | Met | 1; range diff empty |
| README 40 self-certify 1, forge approval 1; 76 gated forge approval 1; 91 Maintainer cost 1, forge approval 1 | Met | each phrase present on the named line (bb3ea19 diff) |
| CLAUDE 159 Maintainer cost 1, gated forge approval 1; 208 self-certify 1 | Met | each present (bb3ea19 diff) |
| no restatement phrases in README/CLAUDE/opt | Met | 0 (git grep at e574c31; opt 0) |
| commit touches exactly opt, README, CLAUDE | Met | bb3ea19 stat (+ `.beads/`) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-syo7 — Task 9
| Verification Item | Status | Evidence |
|---|---|---|
| `^GREEN RESULT` 1 reading `5 of 5` | Met | :1114 |
| `ls <sp>/green` = 13 | Met | 13 files listed |
| bikeshed pass lines 2; synth pass lines 3 | Met | 2 / 3 (:1108-1109, :1111-1113) |
| fix-round commits carry the Deploy body | Met (vacuous) | "fix rounds: none" (:1114); no prompt edit between bb3ea19 and fc4b5a0 other than the user-directed trim 2847687, which precedes the GREEN blobs recorded at :1106 |
| Verification greps of tasks 3, 4, 5, 7 hold at this HEAD | Met, with the superseded items above | see the per-task tables |
| commit touches only the ledger | Met | fc4b5a0 stat (+ `.beads/`) |
| Pre-commit hooks | Met | bd flush hook |

#### bd-uhzb — Task 10 (at e574c31)
| Verification Item | Status | Evidence |
|---|---|---|
| `"version": "3.38.0"` 1 | Met | plugin.json@e574c31 |
| sweep greps | Met | `junior` 0 across the three files; `Important, never Critical` 0 across skills/agents/README/CLAUDE; restatement phrases only in pipeline-constants.md; derivation 1; `Severity Anchor` in 4/4; SC13 empty; hooks 10 passed; `no re-review` 4; `follow-up line` 1; `gh api user --jq .login` 1 |
| commit touches only plugin.json | Met | e358058 stat (+ `.beads/`) |
| Pre-commit hooks | Met | bd flush hook |
