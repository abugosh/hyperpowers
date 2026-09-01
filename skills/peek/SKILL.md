---
name: peek
description: "Use when reviewing a colleague's branch, MR, or PR ('review this branch', 'review this MR', 'review this PR') — deep parallel-lens review (code, architecture, aimed-vs-achieved) with no bd spec required, producing a harsh-but-fair report that opens with a verdict (APPROVE / APPROVE WITH CHANGES / REQUEST CHANGES), weights the MR's prior review, and offers an optional draft comment plus an optional gated fix path that applies and pushes mechanical fixes only after the user approves the exact diff."
---

<skill_overview>
Thin orchestrator for a fixed 8-step review flow: resolve the target, stand up a disposable worktree, dispatch the peek agent's RECON mode to establish intent, confirm that intent with the user, fan out three parallel judgment lenses (CODE, ARCHITECTURE, DELIVERY), synthesize their returns into a single aimed-vs-achieved report, offer gated fixes and a draft comment, and always clean up the worktree. No bd epic is required — this is for reviewing someone else's branch, MR, or PR on demand.

All review protocol — mode charters, evidence rules, return contracts — lives in `agents/peek.md`. This skill never restates it; it only wires the flow.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — the 8-step flow order and its gates (intent confirm, then the fix and comment approvals at Step 7) are fixed and must not be skipped or reordered. Judgment inside each lens and during synthesis adapts to what the branch actually contains.
</rigidity_level>

<quick_reference>
| Step | Action | How |
|------|--------|-----|
| 1 | Resolve target | Parse `/peek` argument (URL / number / branch / none); detect forge + rung (`forge-detection.md`) |
| 2 | Worktree setup | `git worktree add --detach <tmp> <ref>` (remote fetch or local ref); abort before creating anything if unresolved |
| 3 | RECON dispatch | Agent tool, subagent_type "hyperpowers:peek", model "sonnet", blocking; returns aims, inventory, Prior Review |
| 4 | Intent confirm gate | AskUserQuestion: confirm/correct/add aims, confirm/correct the Prior Review summary, opt-in suite run; HOLD on expiry |
| 5 | Parallel lens dispatch | 3x Agent tool (CODE/ARCHITECTURE/DELIVERY), one message, no model override, blocking |
| 6 | Synthesis | Lead dedups, applies the re-check, marks fix-eligible findings `[fix-proposed]` per `pipeline-constants.md` (Peek Fix Carve-out), derives the pre-fix verdict (loop-interfaces.md), assembles the report |
| 7 | Fix + comment gate | Two phases: elect fixes and/or a comment (A), then — only when fixes were applied — approve the exact diff, comment text, and delivery target at (B); at most one comment is posted per run, never before the user approves its exact text; comment opens with the verdict and ends with the `<!-- peek: <sha> -->` marker |
| 8 | Cleanup | `git worktree remove <tmp> --force` + prune; always runs, even on abort |
</quick_reference>

<when_to_use>
Use for:
- Reviewing a colleague's branch, MR, or PR ad hoc — no bd epic exists or is needed
- Producing a harsh-but-fair aimed-vs-achieved report before approving, merging, or commenting on someone else's work
- Deep code + architecture judgment on a delta that has no plan document to check it against

**Don't use for:**
- Re-verifying a completed epic against its bd spec → `hyperpowers:review-implementation`
- Reviewing your own in-flight epic work → `executing-plans`' two-stage per-task review already covers it
</when_to_use>

<the_process>

## Step 1: Resolve Target

Parse the `/peek` argument:
- MR/PR URL → extract forge + number from the URL shape
- Bare number → the current repo's MR/PR at that number
- Branch name → that literal branch
- No argument → the current branch (`git branch --show-current`)

Run the Detection idiom from `skills/common-patterns/forge-detection.md` to determine the forge (`gh`, `glab`, or `none`) and state which rung of its Degradation ladder is in force. Cite that file for the detection commands and ladder — do not restate them here.

## Step 2: Worktree Setup

Two cases, by where the target lives:

- **Remote target** (an MR/PR, or a branch that resolves on the remote): `git fetch origin <source-branch>`, then `git worktree add --detach <tmp-path> FETCH_HEAD`.
- **Local target** (no remote configured, the fetch fails, or the target is the current branch or a local-only branch): `git worktree add --detach <tmp-path> <branch>` directly from the local ref.

`--detach` is REQUIRED in both cases — git refuses to add a worktree for a branch that is already checked out, and the default invocation (no argument = current branch) always hits that refusal without it.

When the target is the current branch and a same-named remote branch also exists, prefer the LOCAL ref — local commits may be ahead of the remote, and reviewing a stale remote head reviews the wrong code.

If neither the fetch nor a local ref resolves the target, abort with a clear message BEFORE creating anything — there is nothing to clean up in that case.

Put the tmp path under the system temp dir, unique per run. Resolve the base ref via the base-branch idiom cited from `forge-detection.md` (Base branch section). Record the worktree path — every dispatch in Steps 3-5 and the cleanup in Step 8 need it.

Record these further facts at setup; Step 7's fix path reads all of them:

- **Target kind** — remote or local, as resolved above.
- **Reviewed tip** — `git -C <tmp-path> rev-parse HEAD`, run immediately after the worktree exists. This SHA is the pre-fix baseline: the diff boundary at Step 7's approval gate, the reset target when a fix is discarded, and the marker SHA on every path where fixes are not delivered.
- **Checkout state** (local targets only) — `git worktree list --porcelain | grep -F "branch refs/heads/<branch>"` in the target repo. A hit means some worktree holds that branch and its ref must not be moved.
- **Delivery remote** (remote targets only) — `git ls-remote --exit-code --heads origin <source-branch>`. A miss means `origin` does not carry the branch at all, which is what a cross-fork MR looks like from here: the review can read that code but can never deliver a commit to it.

The fix path is available for a remote target whose source branch lives on `origin`, and for a local target whose branch is checked out nowhere. Two targets never get it and run review-only: the current branch, checked out by definition, and a cross-fork MR, whose source branch `origin` does not carry — the offer must never be made on a target that cannot receive it. The user's own checkout is never touched on any path: fixes are made in the disposable worktree and delivered by pushing, or by moving a ref no checkout holds.

## Step 3: RECON Dispatch

```
Agent tool:
  subagent_type: "hyperpowers:peek"
  model: "sonnet"    # the ONLY model override in this skill — mechanical gathering
  prompt: |
    Mode: RECON
    Target: <branch> -> <base ref>
    Worktree path: <tmp-path>
    Forge: <gh | glab | none> at rung <1 | 2 | 3>
```

Blocking (no `team_name`). RECON's return contract (Stated Aims, Change Inventory, Surprises, Intent Basis, Coverage) is defined in `agents/peek.md` — do not restate it here.

## Step 4: Intent Confirm Gate (Interactive)

Play back RECON's Stated Aims and Surprises via AskUserQuestion (form and gate discipline: `skills/common-patterns/question-format.md`) and a one-line Prior Review summary (decision, approvers and when, settled-point count, prior peeks with SHA and finding count — or "unavailable at rung N"). Offer: confirm as-is / correct (free text) / add a missing aim / correct the review history (free text). When a standard test runner is detected in the repo, the same round also offers the opt-in suite run, with "run it" as the default suggestion.

An expired question box is not an answer — re-ask in durable prose and HOLD (per `question-format.md`, Timeouts and Gates). Never proceed on a provisional intent: the lenses in Step 5 are expensive, and wrong intent wastes every one of them.

Carry forward from this step: the confirmed aims, the Prior Review block (as corrected), and the suite-run decision.

## Step 5: Parallel Lens Dispatch

One message, three Agent calls:

```
Agent tool (single message, three calls — no team_name):
  1. subagent_type: "hyperpowers:peek", prompt: "Mode: CODE ..."
  2. subagent_type: "hyperpowers:peek", prompt: "Mode: ARCHITECTURE ..."
  3. subagent_type: "hyperpowers:peek", prompt: "Mode: DELIVERY ..."
```

No `model` field on any of the three — lenses inherit the session model (review depth is the product; it must not be silently downgraded).

Every prompt carries: Mode, target identity (`Target: <branch> -> <base ref>`, both halves — `agents/peek.md` requires the full target identity on every dispatch), the confirmed aims, RECON's change inventory, the worktree path, forge rung, and RECON's Prior Review block verbatim (all three lenses — `agents/peek.md` lists it as a required input; a lens dispatch without it is an error per that file). DELIVERY additionally carries RECON's Surprises block. CODE additionally carries the suite-run decision from Step 4. `agents/peek.md`'s Mode Detection section defines the full required-input set per mode — cite it, never restate it; a DELIVERY dispatch missing Surprises is an error per that file, not something this skill improvises around.

## Step 6: Synthesis (Lead)

Dedup overlapping findings first: same file:line + same defect = one finding, keep the highest severity.

**Re-check (lead-owned, every move visible in the report):** a Critical whose `Trigger:` or `Consequence:` line is missing or empty becomes Important, marked `[downgraded: no consequence named]`; a `[convention]` Critical becomes Important, marked `[downgraded: convention]`; a previously-reviewed finding without a `Prior review:` line moves to Questions for the Author; a finding missing Scope is treated as delta; a finding missing Class is assigned one by the lead (`skills/common-patterns/pipeline-constants.md`, Finding Classification: the lead owns final classification). Dedup runs first and the re-check runs on the surviving finding, so a Suggestion never rises above what its evidence supports.

**Fix-eligibility pass (lead-owned):** mark each surviving finding `[fix-proposed]` when `skills/common-patterns/pipeline-constants.md` (Peek Fix Carve-out) makes it eligible. That file owns which findings qualify and what evidence delivering them requires — cite it, never restate it. The mark is a proposal and nothing more: no file is edited, no commit is made, and nothing is delivered during synthesis. Skip this pass entirely when Step 2 found the fix path unavailable for this target; no finding gets marked and the run proceeds as review-only.

**Derive the verdict** per `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek entry) — cite the derivation; never hand-pick. The Step 6 report carries the honest pre-fix verdict, derived over every surviving finding, because nothing has been fixed yet; Step 7 re-derives it only if fixes are actually applied.

Then assemble the report for the architect-governor reader per the Audience Contract (`skills/common-patterns/prose-style.md`, The Reader) — one citation, not restated here. RECON's Change Inventory, carried by every lens dispatch since Step 5, is no longer discarded after intent-gathering: it opens the report. This template is this skill's core output contract:

```
## Peek Review: <branch> -> <base>

**Verdict: <APPROVE | APPROVE WITH CHANGES | REQUEST CHANGES>** — [one sentence, architect altitude: the consequence that decides it]

### What This Branch Does
[3-6 sentences, architect altitude, role-based plain language: what the branch changes in
system terms (components/areas touched, contracts or behavior affected, magnitude) and what
that means for the system — no file:line, no lens names, no internal vocabulary] + RECON's
area-grouped Change Inventory rendered as a short list + one line of review history (who
approved and at what point; prior peeks)

### Aimed vs Achieved
[2-4 sentence narrative, top layer per the Audience Contract] + DELIVERY's per-aim table + Undeclared Changes

### Prior Peek Findings
[DELIVERY's closure list; omit this section when Prior Review lists no prior peeks]

### Overall Assessment
[harsh but fair paragraph, top layer per the Audience Contract — ARCHITECTURE's stance
(fits/fights/reshapes) stated as a system consequence, not a lens citation]

### Findings
[evidence layer — Critical, then Important, then Suggestions — each with severity, class, scope, file:line, evidence, suggested direction, and any downgrade marker; `- (none)` when the lenses returned none]
[findings the lead can resolve at the worktree carry a trailing `[fix-proposed]` mark — a proposal Step 7 offers, not work already done]

### Questions for the Author
[evidence layer — merged from all lenses, deduped; entries marked `[out-of-lane: <LENS>]` are routed into the owning
lens's Findings during this synthesis step instead — see agents/peek.md Shared Rule 3 for the marker; `- (none)` when empty]

### Coverage
[evidence layer — union of all four lenses' Coverage blocks; anything unreviewed listed explicitly, never silently dropped]
```

## Step 7: Fix + Draft Comment Gate

Two phases: phase A elects what should happen, phase B approves exactly what leaves the worktree. When no finding carries `[fix-proposed]` — nothing was eligible, or Step 2 found the fix path unavailable — phase A is the only phase, with the same options and the same behavior this step has always had.

**Phase A — the offer.** AskUserQuestion (form and gate discipline: `skills/common-patterns/question-format.md`): draft a comment for the MR/PR? The standing options are unchanged — comment as drafted, or no comment. When `[fix-proposed]` findings exist, offer one additional option alongside them: apply the proposed fixes, then approve the diff, the comment, and the target together at phase B before anything is pushed or posted. Name the eligible findings in the question so the election is informed.

**The draft comment.** A professional, direct comment built from the report in three parts (four when fixes are delivered — see Re-derivation below) — (a) opens with the report's `Verdict:` line verbatim (the same `Verdict: <word>` text, before anything else), (b) lists findings and questions per the existing prose rules (no internal vocabulary — no lens names, no mode words), (c) ends with `<!-- peek: <sha> -->`, where `<sha>` is the reviewed tip recorded at Step 2, which on a run with no fixes applied is also `git -C <tmp-path> rev-parse HEAD` — the marker renders as nothing on GitHub and GitLab and lets a later RECON recognize this review. Comment prose otherwise follows `skills/common-patterns/prose-style.md`: findings and questions only — no restated report sections, no Coverage block, no praise-padding; target a comment the author reads in under a minute, longer only when the finding count itself demands it. Posting goes through the write commands cited from `forge-detection.md`. On GitLab, the C2 caveat applies: try the `note create` form first, fall back to the legacy `note -m` form second, per `forge-detection.md`'s caveat table. On rung 2/3 (no forge, or no MR/PR resolvable), hand over copy-paste text instead of posting — that text carries the `Verdict:` opening and the `<!-- peek: <sha> -->` marker too.

**When the comment is drafted and posted.** At most one comment leaves a run — none when the user declines one — and nothing is posted until the user approves that exact text. The path decides when both happen:

- **No fixes elected** (phase A is the only phase): draft the three-part comment here from the Step 6 report, show the user that exact text, and post it on their approval. This is today's flow, unchanged.
- **Fixes elected:** draft and post nothing here. The comment is built after Re-derivation below, in its four-part form, and the user approves it together with the diff and the target at phase B — it is posted after delivery, or in its report-only form on any fallback path.

Posting the pre-fix draft on a fix run is the failure this split exists to prevent: it puts a superseded verdict, no list of what the review fixed, and a marker naming a tip the branch has moved past in front of the author, and a second comment after delivery only compounds it.

**Application — only when the user elects fixes.** All work happens at the worktree:

- One commit per finding, `[convention]` fixes first, then `[capability]` fixes.
- Commit message: an imperative subject describing the change itself, 60 characters or fewer, and a body of exactly `Applied during review; details in the review comment.` The branch author is the reader, so no plugin vocabulary belongs anywhere in the message — no mode or lens words, no class tags, no severity words.
- If any `[capability]` fix was applied, dispatch `hyperpowers:test-runner` at the worktree for the repo's suite. On a red or unrunnable suite, run `git -C <tmp-path> reset --hard <last-convention-commit>` and demote those capability fixes back to ordinary findings for the author — the suite rule in `skills/common-patterns/pipeline-constants.md` (Peek Fix Carve-out), cited not restated. When no convention commit exists, the reset target is the reviewed tip recorded at Step 2.
- If an edit that looked exact turns out to need judgment mid-fix, it was never eligible: reset the worktree to the last good commit, drop the `[fix-proposed]` mark, and return the finding to the report at its original severity for the author to resolve.

**Re-derivation — only when fixes were applied.** The verdict is re-derived per `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek entry), which scopes it to the findings not fixed by review. The report gains a `### Fixed by review` block, placed between Overall Assessment and Findings — one line per fix naming the defect and its commit SHA. A fixed finding lives in that block and leaves the Findings section.

The draft comment then has four parts, in order: (a) the re-derived `Verdict:` line, (b) a short `Fixed directly (N commits pushed)` list, one line per fix in the author's language, (c) the remaining findings and questions, (d) the `<!-- peek: <sha> -->` marker. `<sha>` is `git -C <tmp-path> rev-parse HEAD`, which after fixes is the post-fix tip — deliberately so: that is the tip the author's branch carries once the fixes land, and the SHA a later RECON must match to recognize this review.

The post-fix tip is correct ONLY when the fixes are actually delivered. On every fallback path below — a decline at phase B, a rejected or non-fast-forward push, a failed compare-and-swap — the marker MUST name the reviewed tip recorded at Step 2 instead. The worktree's HEAD still carries the discarded fix commits until Step 8 removes them, so reading HEAD on a fallback path stamps the comment with a SHA that never reaches the branch and breaks the next RECON's prior-peek matching.

**Phase B — approve the exact delivery.** Runs only when fixes were applied, and runs every time they were. Show the user all three together, before anything leaves the worktree:

1. The full diff: `git -C <tmp-path> diff <reviewed-tip>..HEAD`.
2. The exact comment text that will be posted.
3. The named delivery target — the branch, and the remote or repo the commits land on.

Only on approval, deliver:

- **Remote target:** `git -C <tmp-path> push origin HEAD:<source-branch>`.
- **Local target:** `git -C <target-repo> update-ref refs/heads/<branch> <new-sha> <reviewed-tip>` — the trailing old value makes it a compare-and-swap that fails if the branch moved. Refuse the update outright when Step 2's checkout state found the branch checked out in any worktree; the ref moves only for a branch checked out nowhere.

Never force-push — every other bound on how commits land is the carve-out's Delivery rule (`skills/common-patterns/pipeline-constants.md`, Peek Fix Carve-out), cited not restated.

Then post the comment under the rules above.

**Fallbacks — the review still lands, the fixes do not.** Each of these leaves the author's branch exactly as the review found it, and each falls back to the report-only comment: the original findings, the pre-fix verdict, and the reviewed tip as the marker SHA.

- **Push rejected, or non-fast-forward** (the author moved the branch while the review ran): report git's output verbatim, then fall back. Do not retry by overwriting the remote branch, and do not rebase onto the new tip.
- **Compare-and-swap failure on a local target** (the old-value check fails because the branch moved): same fallback, reported the same way.
- **Cross-fork MR** — the source branch does not live on `origin`: Step 2's availability test screens the fork-ness it can see, so reaching here means it only became visible at delivery. Do not hunt for the author's fork remote and do not add remotes. Treat delivery as unavailable, take the same fallback, and say plainly that the fixes could not be delivered because the branch lives on a fork.
- **The user declines at phase B:** discard the fixed form and offer today's report-only comment. Step 8's forced worktree removal is the discard mechanism — no separate cleanup, and nothing to undo on the author's branch.

Both phases follow `skills/common-patterns/question-format.md`: an expired question box is not an answer — re-ask in durable prose and HOLD. Nothing is posted, pushed, or ref-updated on a timeout.

NEVER post without the user's approval of the exact text that goes out, and NEVER push or move a ref without the user's approval of the exact diff, comment, and target.

## Step 8: Cleanup

```
git worktree remove <tmp-path> --force
git worktree prune
```

This is an always-run closer — it runs even when the user aborts mid-flow, declines at a gate, or a dispatch fails partway through. Every path through this skill ends here. The forced removal is also how unapproved fix commits are discarded: any commit Step 7 built but did not deliver dies with the worktree, which is why no separate revert is needed on a fallback path.

</the_process>

<critical_rules>
## Rules That Have No Exceptions

1. **Never auto-post, never auto-push.** A draft comment goes out only after the user approves the exact text, and a fix commit reaches the author's branch only after the user approves the exact diff, comment, and delivery target at Step 7's phase B.
2. **Never skip the intent gate.** "The diff is tiny, skip confirmation" is the named rationalization — the gate runs every time, regardless of branch size.
3. **Never restate agent protocol.** Mode charters, evidence rules, and return contracts live in `agents/peek.md`. Cite, never copy.
4. **The report must open with the `Verdict:` line and include Coverage.** A synthesis that omits either is incomplete: the `Verdict:` line is derived, never hand-picked, and anything unreviewed must be named in Coverage, not silently dropped.
5. **The worktree is always cleaned up.** Step 8 runs on every path, including aborts and dispatch failures.
6. **The fix path is bounded by the Peek Fix Carve-out** (`skills/common-patterns/pipeline-constants.md`). Critical findings are never fixed at review; nothing is pushed or ref-updated without phase-B approval of the exact diff.

## Common Excuses

All of these mean: **STOP. Follow the process as written.**

- "The diff is small, skip RECON" — RECON runs every time; size does not exempt intent-gathering.
- "CI is green, skip CODE" — a green suite does not substitute for the CODE lens's judgment. The same goes for skipping any lens: all three dispatch every run (Step 5); no lens is optional.
- "I can infer intent without the gate" — Step 4 is interactive by design; inferred intent is not confirmed intent.
- "The author is senior, soften the findings" — softening includes dropping: every finding stays in the report at its true severity, whoever the author is. Harsh-but-fair does not scale with seniority; only phrasing may be professional, never the finding set.
- "No Critical makes the review look shallow" — a clean return is a complete result. Severity follows the anchor, not the reviewer's need to look rigorous; manufacturing a finding is the mirror image of softening one.
- "It has been reviewed four times, something must be wrong" — prior review is evidence to weigh, not a quota to beat. A finding on previously-reviewed code says what the earlier reviewers missed, or it is a question.
- "It was approved, drop the finding" — approval never suppresses a finding; it demands the `Prior review:` justification. Deferring is the other way to be wrong.
- "The fix is obvious, push it without the gate" — phase B runs every time fixes were applied. Obviousness is not approval, and a diff nobody looked at is a diff nobody agreed to.
- "Fix the Critical too while I'm in there" — a Critical is never fix-eligible (`skills/common-patterns/pipeline-constants.md`, Peek Fix Carve-out). The author must confront it; quietly resolving it at review hides the one finding that most needed their attention.
- "The suite is missing, push the capability fix anyway" — no green suite, no capability fix: demote it back to an ordinary finding for the author. Convention fixes are unaffected by the suite's state.
- "Post the comment now, deliver the fixes after" — at most one comment leaves a run, and on a fix run it is never the pre-fix draft. On a fix run it is drafted after re-derivation and posted at phase B; a comment posted ahead of delivery carries a superseded verdict, omits what the review fixed, and stamps a marker the branch has already moved past.
</critical_rules>

<verification_checklist>
Before presenting the report to the user:
- [ ] Forge and degradation rung detected and stated (Step 1)
- [ ] Worktree created with `--detach`, base ref resolved, user's checkout untouched (Step 2)
- [ ] RECON dispatched with the sonnet model override, blocking, and returned Stated Aims plus Prior Review before the intent gate (Step 3)
- [ ] User confirmed or corrected the aims and the Prior Review summary — no provisional intent carried forward (Step 4)
- [ ] All three lenses dispatched in one message, no model override, with their mode-specific required inputs (Step 5)
- [ ] Findings deduped; re-check applied with every move visible; fix-eligibility pass run and eligible findings marked `[fix-proposed]` (or skipped because the fix path is unavailable); verdict derived per loop-interfaces.md; report opens with the `Verdict:` line and includes Aimed vs Achieved, Overall Assessment, Findings (`- (none)` is a complete Findings section), Questions for the Author, and Coverage (Step 6)
- [ ] At most one comment left the run (none when the user declined one) — drafted pre-fix and posted at phase A on a no-fix run, or drafted after re-derivation and posted at phase B on a fix run — opening with the verdict, ending with the marker, posted only after explicit approval of the exact text, or handed over as copy-paste at rung 2/3 (Step 7)
- [ ] Fixes (if elected) applied per the carve-out, suite green before any `[capability]` fix was delivered, the exact diff and comment text approved at phase B before any push or ref-update, and every non-delivery path left nothing on the author's branch with the marker naming the reviewed tip (Step 7)
- [ ] Worktree removed and pruned (Step 8) — including on any abort path
</verification_checklist>

<integration>
**This skill calls:**
- `hyperpowers:peek` agent (subagent, x4 dispatches — RECON, CODE, ARCHITECTURE, DELIVERY)
- `hyperpowers:test-runner` (via the CODE lens, only when the user opts into the suite run at Step 4, and by the lead at Step 7 when a `[capability]` fix is applied)

**This skill is called by:**
- User, via `/hyperpowers:peek`

**Sibling, not overlap:** `hyperpowers:review-implementation` re-verifies a completed epic against its immutable bd spec — a fundamentally different input (a spec exists and is authoritative) from peek's spec-less branch/MR review. Don't route between them; they answer different questions.
</integration>
