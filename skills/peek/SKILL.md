---
name: peek
description: "Use when reviewing a colleague's branch, MR, or PR ('review this branch', 'review this MR', 'review this PR') — deep parallel-lens review (code, architecture, aimed-vs-achieved) with no bd spec required, producing a report that opens with a verdict (APPROVE / APPROVE WITH CHANGES / REQUEST CHANGES), weights the MR's prior review, and offers an optional draft comment, an optional gated fix path that applies and pushes mechanical fixes only after the user approves the exact diff, and an optional forge approval when the verdict clears and the caller is not the author."
---

<skill_overview>
Thin orchestrator for a fixed 8-step review flow: resolve the target, stand up a disposable worktree, dispatch the peek agent's RECON mode to establish intent, confirm that intent with the user, fan out three parallel judgment lenses (CODE, ARCHITECTURE, DELIVERY), synthesize their returns into a single aimed-vs-achieved report, offer gated fixes, a draft comment, and — when eligible — a forge approval, and always clean up the worktree. No bd epic is required — this is for reviewing someone else's branch, MR, or PR on demand.

All review protocol — mode charters, evidence rules, return contracts — lives in `agents/peek.md`. This skill never restates it; it only wires the flow.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — the 8-step flow order and its gates (intent confirm, then Step 7's approvals of the exact comment text, the exact fix diff, and the exact approve action) are fixed and must not be skipped or reordered. Judgment inside each lens and during synthesis adapts to what the branch actually contains.
</rigidity_level>

<quick_reference>
| Step | Action | How |
|------|--------|-----|
| 1 | Resolve target | Parse `/peek` argument (URL / number / branch / none); detect forge + rung (`forge-detection.md`) |
| 2 | Worktree setup | `git worktree add --detach <tmp> <ref>` (remote fetch or local ref); abort before creating anything if unresolved |
| 3 | RECON dispatch | Agent tool, subagent_type "hyperpowers:peek", model "sonnet", blocking; returns aims, inventory, Prior Review |
| 4 | Intent confirm gate | AskUserQuestion: confirm/correct/add aims, mark a surprise intended (becomes an aim), confirm/correct the Prior Review summary, opt-in suite run; HOLD on expiry |
| 5 | Parallel lens dispatch | 3x Agent tool (CODE/ARCHITECTURE/DELIVERY), one message, no model override, blocking |
| 6 | Synthesis | Lead dedups, applies the re-check (Critical and Important demotions, every move marked), marks fix-eligible findings `[fix-proposed]` per `pipeline-constants.md` (Peek Fix Carve-out), derives the pre-fix verdict and the Path line (loop-interfaces.md), runs the grading-word self-check (prose-style.md), assembles the report |
| 7 | Fix + comment gate | Two phases: elect a comment, fixes, and — on APPROVE / APPROVE WITH CHANGES at rung 1 when the identity read shows the caller is not the author — a forge approval (A); then — only when applied fixes survive — approve the exact diff, comment text, delivery target, and approve command at (B), the comment text and the approve command being approved beside each other at (A) on every other path, the approval withdrawn unsubmitted when delivery finds the branch moved past the reviewed tip; at most one comment per run, never before the user approves its exact text; comment opens with the verdict, carries the follow-up line under it (Critical: fix and re-review; Important: fix, no re-review), and ends with the `<!-- peek: <sha> -->` marker; delivery order is fixes, comment, approval |
| 8 | Cleanup | `git worktree remove <tmp> --force` + prune; always runs, even on abort |
</quick_reference>

<when_to_use>
Use for:
- Reviewing a colleague's branch, MR, or PR ad hoc — no bd epic exists or is needed
- Producing an aimed-vs-achieved report with a derived verdict before approving, merging, or commenting on someone else's work
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

Play back RECON's Stated Aims and Surprises via AskUserQuestion (form and gate discipline: `skills/common-patterns/question-format.md`) and a one-line Prior Review summary (decision, approvers and when, settled-point count, prior peeks with SHA and finding count — or "unavailable at rung N"). Offer: confirm as-is / correct (free text) / add a missing aim / mark a surprise as intended (it becomes a confirmed aim) / correct the review history (free text). When a standard test runner is detected in the repo, the same round also offers the opt-in suite run, with "run it" as the default suggestion.

An aim added or a surprise marked intended at this gate covers the change it names: a reshape it describes counts as declared for this review, and a surprise left uncovered stays undeclared — the ARCHITECTURE lens grades an undeclared reshape as a structural-class Critical (Severity Anchor, pipeline-constants.md). This gate is the one place the reader's decision enters the record, so say so when asking.

An expired question box is not an answer — re-ask in durable prose and HOLD (per `question-format.md`, Timeouts and Gates). Never proceed on a provisional intent: the lenses in Step 5 are expensive, and wrong intent wastes every one of them.

Carry forward from this step: the confirmed aims (including surprises marked intended), the Surprises block as corrected (intended ones removed), the Prior Review block (as corrected), and the suite-run decision.

## Step 5: Parallel Lens Dispatch

One message, three Agent calls:

```
Agent tool (single message, three calls — no team_name):
  1. subagent_type: "hyperpowers:peek", prompt: "Mode: CODE ..."
  2. subagent_type: "hyperpowers:peek", prompt: "Mode: ARCHITECTURE ..."
  3. subagent_type: "hyperpowers:peek", prompt: "Mode: DELIVERY ..."
```

No `model` field on any of the three — lenses inherit the session model (review depth is the product; it must not be silently downgraded).

Every prompt carries: Mode, target identity (`Target: <branch> -> <base ref>`, both halves — `agents/peek.md` requires the full target identity on every dispatch), the confirmed aims, RECON's change inventory, the worktree path, forge rung, and RECON's Prior Review block verbatim (all three lenses — `agents/peek.md` lists it as a required input; a lens dispatch without it is an error per that file). DELIVERY and ARCHITECTURE additionally carry the Surprises block as corrected at Step 4. CODE additionally carries the suite-run decision from Step 4. `agents/peek.md`'s Mode Detection section defines the full required-input set per mode — cite it, never restate it; a DELIVERY or ARCHITECTURE dispatch missing Surprises is an error per that file, not something this skill improvises around.

## Step 6: Synthesis (Lead)

Dedup overlapping findings first: same file:line + same defect = one finding, keep the highest severity.

**Re-check (lead-owned, every move visible in the report):** a Critical whose `Trigger:` or `Consequence:` line is missing or empty becomes Important when it carries a filled `Hits:` or `Maintainer cost:` line, marked `[downgraded: no consequence named]`, and otherwise Suggestion, marked `[downgraded: no consequence named; no cost named]`; a `[convention]` Critical takes the same two-stage move, marked `[downgraded: convention]` or `[downgraded: convention; no cost named]`; an Important whose `Hits:` and `Maintainer cost:` lines are both missing or empty, or whose cost line names only reading effort (the Severity Anchor's excluded words — cite `skills/common-patterns/pipeline-constants.md`), becomes Suggestion, marked `[downgraded: no cost named]`; a Suggestion whose `Direction:` is to leave the code as it stands, or offers leaving it as an acceptable outcome (an either/or whose other arm is no change, or a change deferred until some future condition holds), moves to Questions for the Author when it names a real uncertainty and is otherwise dropped, marked `[moved: no change asked]` in Questions or listed under a one-line `Dropped:` note at the end of Findings — never silently; a previously-reviewed finding without a `Prior review:` line moves to Questions for the Author; a finding missing Scope is treated as delta; a finding missing Class is assigned one by the lead (`skills/common-patterns/pipeline-constants.md`, Finding Classification: the lead owns final classification). The aims table and the Stance block are inputs to this re-check, not only text to render: an aims-table row reading `missing` with no matching delivery-class Critical is filed by the lead, marked `[lead-added: aim missing]`, with Trigger and Consequence drawn from the row and the confirmed aim; a Stance of reshapes with `Declared by: none` and no matching structural-class Critical is filed by the lead, marked `[lead-added: undeclared reshape]`, with Trigger and Consequence drawn from the Stance reasoning; an aim finding whose severity exceeds its table row is corrected to the row's severity, marked `[downgraded: aim partial]`. A lead-added Critical carries both lines or the first rule in this paragraph demotes it. Dedup runs first and the re-check runs on the surviving finding, so a Suggestion never rises above what its evidence supports. The re-check reads the lines; it never fills one in — a cost or a hit the lens did not name is not the lead's to supply, and a demotion is reported with its marker, never silently. A lead-added Critical carries the Trigger and Consequence drawn from the row or the Stance and no Hits or Maintainer cost line — that line is the lens's to write — and with both Trigger and Consequence present it is never demoted.

**Fix-eligibility pass (lead-owned):** mark each surviving finding `[fix-proposed]` when `skills/common-patterns/pipeline-constants.md` (Peek Fix Carve-out) makes it eligible. That file owns which findings qualify and what evidence delivering them requires — cite it, never restate it. The mark is a proposal and nothing more: no file is edited, no commit is made, and nothing is delivered during synthesis. Skip this pass entirely when Step 2 found the fix path unavailable for this target; no finding gets marked and the run proceeds as review-only.

**Path and Decision (lead-owned):** `Path: rework` only when one cause shared by two or more surviving findings can be named, and that cause is stated in the Overall Assessment sentences; otherwise `Path: fix in place`. `Decision:` names what only the reader can decide — a declared reshape to accept or send back, an aim to drop from the description — or reads `(none)`. The vocabulary and its rule are registered in `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek report Path entry) — cite, never restate. Path never changes the verdict.

**Derive the verdict** per `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek entry) — cite the derivation; never hand-pick. The Step 6 report carries the honest pre-fix verdict, derived over every surviving finding, because nothing has been fixed yet; Step 7 re-derives it only when applied fixes survive.

Then assemble the report for the architect-governor reader per the Audience Contract (`skills/common-patterns/prose-style.md`, The Reader) — one citation, not restated here. RECON's Change Inventory, carried by every lens dispatch since Step 5, is no longer discarded after intent-gathering: it opens the report. This template is this skill's core output contract:

```
## Peek Review: <branch> -> <base>

**Verdict: <APPROVE | APPROVE WITH CHANGES | REQUEST CHANGES>** — [one sentence, architect altitude: for REQUEST CHANGES or APPROVE WITH CHANGES the consequence that decides it; for APPROVE the system change that ships]

### What This Branch Does
[At most 6 sentences, architect altitude, role-based plain language: what the branch changes in
system terms (components/areas touched, contracts or behavior affected, magnitude) and what
that means for the system — no file:line, no lens names, no internal vocabulary] + RECON's
area-grouped Change Inventory rendered as a short list + one line of review history (who
approved and at what point; prior peeks)

### Aimed vs Achieved
[At most 4 sentences, top layer per the Audience Contract] + DELIVERY's per-aim table + Undeclared Changes

### Prior Peek Findings
[DELIVERY's closure list; omit this section when Prior Review lists no prior peeks]

### Overall Assessment
[At most 4 sentences, top layer per the Audience Contract: ARCHITECTURE's stance
(fits/fights/reshapes) stated as a system consequence, never as a lens citation; when
findings share a cause, that cause named here. Describes the system, never grades the
work — no quality, effort, or diligence words in either direction (prose-style.md,
Human-Facing Prose Baseline)]
Path: fix in place | rework   [exactly one, per the Path rule above]
Decision: [what only the reader can decide, or (none)]

### Findings
[evidence layer — Critical, then Important, then Suggestions — each with severity, class, scope, file:line, evidence, suggested direction, and any downgrade marker; `- (none)` when the lenses returned none]
[findings the lead can resolve at the worktree carry a trailing `[fix-proposed]` mark — a proposal Step 7 offers, not work already done]

### Questions for the Author
[evidence layer — merged from all lenses, deduped; entries marked `[out-of-lane: <LENS>]` are routed into the owning
lens's Findings during this synthesis step instead — see agents/peek.md Shared Rule 3 for the marker; `- (none)` when empty]

### Coverage
[evidence layer — union of all four lenses' Coverage blocks; anything unreviewed listed explicitly, never silently dropped]
```

**Self-check before presenting (lead-owned):** reread the top layer — the verdict sentence, What This Branch Does, the Aimed vs Achieved narrative, Overall Assessment — against the grading-word list in `skills/common-patterns/prose-style.md` (Human-Facing Prose Baseline). Every hit is rewritten into the concrete evidence behind it or deleted. An APPROVE with `- (none)` under Findings is a short report; nothing is added to make it look reviewed.

## Step 7: Fix + Draft Comment Gate

Two phases: phase A elects what should happen, phase B approves exactly what leaves the worktree. When no finding carries `[fix-proposed]` — nothing was eligible, or Step 2 found the fix path unavailable — phase A is the only phase, with the same options and the same behavior this step has always had. A forge approval, when eligible, is a third election at phase A and a fourth item at phase B — it is never implied by the verdict.

**Approval eligibility (lead-owned, before phase A).** The approve election is offered only when ALL of these hold: the verdict — the Step 6 verdict, or the re-derived verdict when applied fixes survive — is `APPROVE` or `APPROVE WITH CHANGES`; the run is at rung 1; the target's state is open; the identity read (`skills/common-patterns/forge-detection.md`, Identity — cite it, never restate the command) returned a login, and that login differs from the target's own author login (the Author fields table in the same file); and RECON's Prior Review approvals do not already list that login — at the reviewed tip on GitHub, at all on GitLab, whose approvals carry no SHA (caveats C14 and C15). When any condition fails the offer is withdrawn and phase A says which one and why, in one line — `forge approval not offered: identity read failed (<error>)`, `self-peek: you are the author (<login>)`, `already approved at this tip` (on GitLab, where no SHA exists to name, `already approved` — C14), `target is not open (<state>)`, `rung <2|3>: no forge` — never silently. One line in that set fires later than phase A: `branch moved since the reviewed tip (<reviewed-tip> -> <current-tip>)`, stated at delivery time on the two moved-branch fallbacks below — a rejected or non-fast-forward push, and a failed compare-and-swap — where the lead re-reads the target's tip and finds the branch past the tip the review read. Eligibility clearing at phase A is never a promise the approval submits; it holds only while the reviewed tip is still the target's tip. Self-peek is comment-only on both forges even where the forge would accept the approval (GitLab Free does). The target's state and its author login come from the Read commands `skills/common-patterns/forge-detection.md` lists — the `gh pr view --json` read carries `state` and `author`, and the `glab mr view -F json` read carries `state` and `author` too; that file names each forge's state vocabulary, and any value other than its open value means the target is not open; cite that file's Read commands and its Author fields, never restate them — and the caller's login comes from its Identity subsection. The lead runs those reads at eligibility time, because RECON's return carries neither the target's state nor the caller's login.

**Phase A — the offer.** AskUserQuestion (form and gate discipline: `skills/common-patterns/question-format.md`): draft a comment for the MR/PR? The standing options are unchanged — comment as drafted, or no comment. When `[fix-proposed]` findings exist, offer one additional option alongside them: apply the proposed fixes, then approve the diff, the comment, and the target together at phase B before anything is pushed or posted. Name the eligible findings in the question so the election is informed. When approval is eligible, offer it as a further option beside the comment. Electing approval implies electing the comment: the comment carries the marker record a later RECON matches, and no forge state changes without that record. An election of approval alone is answered by offering the pair.

**The draft comment.** A professional, direct comment built from the report in three parts (four when fixes are delivered — see Re-derivation below) — (a) opens with the report's `Verdict:` line verbatim (the same `Verdict: <word>` text, before anything else), followed on the next line by the follow-up line, which tells the author what each tier asks of them in three fixed cases — with any Critical present: "The items marked Critical need a fix and a re-review; the Important items need a fix you verify yourself, no re-review." (when no Important accompanies the Critical, the sentence ends at the semicolon) — with Importants and no Critical: "Fix the Important items and merge; no re-review is needed." — with nothing above Suggestion: "Nothing blocks merge; the suggestions are yours to take or leave." — the split is the Severity Anchor's (`skills/common-patterns/pipeline-constants.md`, cited not restated), (b) lists findings and questions per the existing prose rules (no internal vocabulary — no lens names, no mode words; the Overall Assessment's cause sentence may appear in plain language, the `Path:` and `Decision:` labels never do), (c) ends with `<!-- peek: <sha> -->`, where `<sha>` is the reviewed tip recorded at Step 2, which on a run with no fixes applied is also `git -C <tmp-path> rev-parse HEAD` — the marker renders as nothing on GitHub and GitLab and lets a later RECON recognize this review. Comment prose otherwise follows `skills/common-patterns/prose-style.md`: findings and questions only — no restated report sections, no Coverage block, no praise-padding; target a comment the author reads in under a minute, longer only when the finding count itself demands it. Posting goes through the write commands cited from `forge-detection.md`. On GitLab, the C2 caveat applies: try the `note create` form first, fall back to the legacy `note -m` form second, per `forge-detection.md`'s caveat table. On rung 2/3 (no forge, or no MR/PR resolvable), hand over copy-paste text instead of posting — that text carries the `Verdict:` opening, the follow-up line under it (the same three-case text, so the author still reads which items need a re-review and which need no re-review), and the `<!-- peek: <sha> -->` marker too.

**When the comment is drafted and posted.** At most one comment leaves a run — none when the user declines one — and nothing is posted until the user approves that exact text. The path decides when both happen:

- **No fixes elected** (phase A is the only phase): draft the three-part comment here from the Step 6 report, show the user that exact text, and post it on their approval — the comment path is unchanged. When approval was also elected, show the exact approve command, the target, and the identity line ("you are <login>; the author is <login>") together with the comment text; on approval, post the comment first and approve second.
- **Fixes elected:** draft and post nothing here. The comment is built after Re-derivation below, in its four-part form, and the user approves it together with the diff and the target at phase B — it is posted after delivery, or in its report-only form on any fallback path.
- **Fixes elected, none survived:** when every applied fix is reverted before delivery, the worktree is back at the reviewed tip and there is no diff for phase B to approve. The run rejoins the first bullet's timing — the report-only comment (the no-surviving-fix fallback below) is drafted from the Step 6 report, shown to the user as that exact text, and posted on their approval — reached after the application attempt instead of before it.

Posting the pre-fix draft on a fix run is the failure this split exists to prevent: it puts a superseded verdict, no list of what the review fixed, and a marker naming a tip the branch has moved past in front of the author, and a second comment after delivery only compounds it.

**Application — only when the user elects fixes.** All work happens at the worktree:

- One commit per finding, `[convention]` fixes first, then `[capability]` fixes.
- Commit message: an imperative subject describing the change itself, 60 characters or fewer, and a body of exactly `Applied during review; details in the review comment.` The branch author is the reader, so no plugin vocabulary belongs anywhere in the message — no mode or lens words, no class tags, no severity words.
- If any `[capability]` fix was applied, dispatch `hyperpowers:test-runner` at the worktree for the repo's suite. On a red or unrunnable suite, run `git -C <tmp-path> reset --hard <last-convention-commit>` and demote those capability fixes back to ordinary findings for the author — the suite rule in `skills/common-patterns/pipeline-constants.md` (Peek Fix Carve-out), cited not restated. When no convention commit exists, the reset target is the reviewed tip recorded at Step 2.
- If an edit that looked exact turns out to need judgment mid-fix, it was never eligible: reset the worktree to the last good commit, drop the `[fix-proposed]` mark, and return the finding to the report at its original severity for the author to resolve.

When reverting leaves no fix standing — the reset landed back on the reviewed tip because no convention commit existed, or every elected fix was dropped mid-fix — the fix set is empty. Skip Re-derivation and phase B; the no-surviving-fix fallback below owns the rest of the run.

**Re-derivation — only when applied fixes survive.** The verdict is re-derived per `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek entry), which scopes it to the findings not fixed by review. The report gains a `### Fixed by review` block, placed between Overall Assessment and Findings — one line per fix naming the defect and its commit SHA. A fixed finding lives in that block and leaves the Findings section.

The draft comment then has four parts, in order: (a) the re-derived `Verdict:` line with the follow-up line under it, (b) a short `Fixed directly (N commits pushed)` list, one line per fix in the author's language, (c) the remaining findings and questions, (d) the `<!-- peek: <sha> -->` marker. `<sha>` is `git -C <tmp-path> rev-parse HEAD`, which after fixes is the post-fix tip — deliberately so: that is the tip the author's branch carries once the fixes land, and the SHA a later RECON must match to recognize this review.

Approval eligibility is re-read against the re-derived verdict: a run whose surviving findings were all fixed by review may become eligible here, and a run whose fixes all reverted keeps the pre-fix verdict's eligibility.

The post-fix tip is correct ONLY when the fixes are actually delivered. On every fallback path below — an empty fix set after reverts, a decline at phase B, a rejected or non-fast-forward push, a failed compare-and-swap — the marker MUST name the reviewed tip recorded at Step 2 instead. Wherever fix commits were built and not delivered, the worktree's HEAD still carries them until Step 8 removes them, so reading HEAD on a fallback path stamps the comment with a SHA that never reaches the branch and breaks the next RECON's prior-peek matching.

**Phase B — approve the exact delivery.** Runs only when applied fixes survive, and runs every time they do. Show the user these together, before anything leaves the worktree:

1. The full diff: `git -C <tmp-path> diff <reviewed-tip>..HEAD`.
2. The exact comment text that will be posted.
3. The named delivery target — the branch, and the remote or repo the commits land on.
4. When approval is elected: the exact approve command from `skills/common-patterns/forge-detection.md` (Approve) — on GitLab with `--sha` set to the tip the comment's marker names — the target, and the identity line ("you are <login>; the author is <login>").

Only on approval, deliver:

- **Remote target:** `git -C <tmp-path> push origin HEAD:<source-branch>`.
- **Local target:** `git -C <target-repo> update-ref refs/heads/<branch> <new-sha> <reviewed-tip>` — the trailing old value makes it a compare-and-swap that fails if the branch moved. Refuse the update outright when Step 2's checkout state found the branch checked out in any worktree; the ref moves only for a branch checked out nowhere.

Never force-push — every other bound on how commits land is the carve-out's Delivery rule (`skills/common-patterns/pipeline-constants.md`, Peek Fix Carve-out), cited not restated.

Then post the comment under the rules above, and only then submit the approval. Delivery order is fixed — fixes, comment, approval — so a failure at any point leaves everything before it delivered and everything after it undone, and says so.

**Approval failures — reported, never retried.** GitHub's refusal of a self-approval (`Can not approve your own pull request`), GitLab's bare 401, and GitLab's 409 on a `--sha` mismatch — the branch moved, and the posture is a rejected push's: say so, do not chase the new tip — each end the approval step with the forge's output quoted verbatim. The comment stays posted, the branch stays as delivered, no second comment is posted, and the approval is never re-submitted in the run. A moved branch caught BEFORE submission is a withdrawal, not a failure: the moved-branch fallbacks below withhold the approval and state the moved-tip line, and only the narrower race — the branch moving between that tip re-read and the approve call — reaches this paragraph, where GitLab's 409 is the forge catching what GitHub's SHA-less approve cannot. Every message and status here is the one `skills/common-patterns/forge-detection.md` documents (Approve, caveats C12-C15) — cite it, never restate it.

**Fallbacks — the review still lands, the fixes do not.** Each of these leaves the author's branch exactly as the review found it, and each falls back to the report-only comment: the original findings, the pre-fix verdict, and the reviewed tip as the marker SHA. Approval eligibility on a fallback is read against the pre-fix verdict, and what an approval elected at phase A then does splits on whether the branch is known to have moved. On the three fallbacks that leave the reviewed tip standing — no applied fix survives, a cross-fork MR, and a decline at phase B — the approval rides with that report-only comment: its exact command, target, and identity line shown beside the comment text, and submitted only after the comment posts. On the two moved-branch fallbacks — a rejected or non-fast-forward push, and a failed compare-and-swap — it is withdrawn unsubmitted with the `branch moved since the reviewed tip (<reviewed-tip> -> <current-tip>)` line, because the branch now carries a tip the review never read: GitLab's approve binds to `--sha` and would refuse it, while GitHub's carries no SHA at all and would approve the new tip silently (`skills/common-patterns/forge-detection.md`, Approve — cite it, never restate it). The comment still posts; only the state change is withheld.

- **No applied fix survives to delivery** — the suite demotion above reset a capability-only fix set back to the reviewed tip because no convention commit existed to land on, or every elected fix turned out to need judgment and was dropped mid-fix: nothing is left to deliver and no diff is left to approve, so phase B never runs. Restore those findings to the report's Findings section at their original severity, drop their `[fix-proposed]` marks, and take the report-only comment on the same terms as every other fallback here. Say plainly which fixes were attempted and why they went back to the author.
- **Push rejected, or non-fast-forward** (the author moved the branch while the review ran): report git's output verbatim, then fall back. Do not retry by overwriting the remote branch, and do not rebase onto the new tip. An elected approval is withdrawn unsubmitted here, stated as `branch moved since the reviewed tip (<reviewed-tip> -> <current-tip>)`.
- **Compare-and-swap failure on a local target** (the old-value check fails because the branch moved): same fallback, reported the same way, and an elected approval is withdrawn unsubmitted on the same `branch moved since the reviewed tip (<reviewed-tip> -> <current-tip>)` line.
- **Cross-fork MR** — the source branch does not live on `origin`: Step 2's availability test screens the fork-ness it can see, so reaching here means it only became visible at delivery. Do not hunt for the author's fork remote and do not add remotes. Treat delivery as unavailable, take the same fallback, and say plainly that the fixes could not be delivered because the branch lives on a fork.
- **The user declines at phase B:** discard the fixed form and offer today's report-only comment. The decline covers everything phase B showed, an elected approval included; that approval reaches the forge only if the user elects and approves it again beside the report-only comment. Step 8's forced worktree removal is the discard mechanism — no separate cleanup, and nothing to undo on the author's branch.

Both phases follow `skills/common-patterns/question-format.md`: an expired question box is not an answer — re-ask in durable prose and HOLD. Nothing is posted, pushed, ref-updated, or approved on a timeout.

NEVER post without the user's approval of the exact text that goes out, NEVER push or move a ref without the user's approval of the exact diff, comment, and target, and NEVER approve on the forge without the user's approval of the exact command, target, and identity line.

## Step 8: Cleanup

```
git worktree remove <tmp-path> --force
git worktree prune
```

This is an always-run closer — it runs even when the user aborts mid-flow, declines at a gate, or a dispatch fails partway through. Every path through this skill ends here. The forced removal is also how unapproved fix commits are discarded: any commit Step 7 built but did not deliver dies with the worktree, which is why no separate revert is needed on a fallback path.

</the_process>

<critical_rules>
## Rules That Have No Exceptions

1. **Never auto-post, never auto-push, never auto-approve.** A draft comment goes out only after the user approves the exact text, and a fix commit reaches the author's branch only after the user approves the exact diff, comment, and delivery target at Step 7's phase B. A forge approval reaches the forge only after the user approves the exact approve command, target, and identity line — at phase B on a fix run, beside the comment text on every other path — only after the comment is posted, and never on a self-peek or at rung 2/3.
2. **Never skip the intent gate.** "The diff is tiny, skip confirmation" is the named rationalization — the gate runs every time, regardless of branch size.
3. **Never restate agent protocol.** Mode charters, evidence rules, and return contracts live in `agents/peek.md`. Cite, never copy.
4. **The report must open with the `Verdict:` line, carry `Path:` and `Decision:` under Overall Assessment, and include Coverage.** A synthesis that omits any of these is incomplete: the `Verdict:` line is derived, never hand-picked; `Path:` is likewise derived per `skills/common-patterns/loop-interfaces.md`, never hand-picked; and anything unreviewed must be named in Coverage, not silently dropped.
5. **The worktree is always cleaned up.** Step 8 runs on every path, including aborts and dispatch failures.
6. **The fix path is bounded by the Peek Fix Carve-out** (`skills/common-patterns/pipeline-constants.md`). Critical findings are never fixed at review; nothing is pushed or ref-updated without phase-B approval of the exact diff.

## Common Excuses

All of these mean: **STOP. Follow the process as written.**

- "The diff is small, skip RECON" — RECON runs every time; size does not exempt intent-gathering.
- "CI is green, skip CODE" — a green suite does not substitute for the CODE lens's judgment. The same goes for skipping any lens: all three dispatch every run (Step 5); no lens is optional.
- "I can infer intent without the gate" — Step 4 is interactive by design; inferred intent is not confirmed intent.
- "The author is senior, soften the findings" — softening includes dropping: every finding stays in the report at its true severity, whoever the author is. The finding set does not scale with seniority; only phrasing may be professional, never the finding set.
- "No Critical makes the review look shallow" — a clean return is a complete result. Severity follows the anchor, not the reviewer's need to look rigorous; manufacturing a finding is the mirror image of softening one.
- "It has been reviewed four times, something must be wrong" — prior review is evidence to weigh, not a quota to beat. A finding on previously-reviewed code says what the earlier reviewers missed, or it is a question.
- "It was approved, drop the finding" — approval never suppresses a finding; it demands the `Prior review:` justification. Deferring is the other way to be wrong.
- "The fix is obvious, push it without the gate" — phase B runs every time an applied fix survives. Obviousness is not approval, and a diff nobody looked at is a diff nobody agreed to.
- "The verdict is APPROVE, just approve it on the forge" — approval is an election plus the user's approval of the exact command, target, and identity line at the gate that shows them; a verdict is a finding, not a permission.
- "It is my own MR and GitLab allows it" — self-peek is comment-only on both forges; an approval means a second person looked.
- "APPROVE WITH CHANGES, so wait for the re-peek" — an Important needs no re-review: the author fixes and self-certifies (Severity Anchor, cited). Only a Critical asks for a re-review, and the follow-up line under the verdict says which is which.
- "Fix the Critical too while I'm in there" — a Critical is never fix-eligible (`skills/common-patterns/pipeline-constants.md`, Peek Fix Carve-out). The author must confront it; quietly resolving it at review hides the one finding that most needed their attention.
- "The suite is missing, push the capability fix anyway" — no green suite, no capability fix: demote it back to an ordinary finding for the author. Convention fixes are unaffected by the suite's state.
- "Post the comment now, deliver the fixes after" — at most one comment leaves a run, and on a fix run it is never the pre-fix draft. On a fix run it is drafted after re-derivation and posted at phase B — or, when no fix survives to deliver, drafted report-only once the fix set is empty; a comment posted ahead of delivery carries a superseded verdict, omits what the review fixed, and stamps a marker the branch has already moved past.
- "A clean branch deserves some acknowledgment" — the APPROVE verdict is the acknowledgment. An adjective that appears on every report carries no information; describe what the branch changes and stop.
- "The findings feel like a rework, call it one" — `Path: rework` requires a named shared cause in the Overall Assessment; a feeling without a cause is `fix in place`, and the findings speak for themselves.
</critical_rules>

<verification_checklist>
Before presenting the report to the user:
- [ ] Forge and degradation rung detected and stated (Step 1)
- [ ] Worktree created with `--detach`, base ref resolved, user's checkout untouched (Step 2)
- [ ] RECON dispatched with the sonnet model override, blocking, and returned Stated Aims plus Prior Review before the intent gate (Step 3)
- [ ] User confirmed or corrected the aims and the Prior Review summary — no provisional intent carried forward; surprises marked intended moved into the aims (Step 4)
- [ ] All three lenses dispatched in one message, no model override, with their mode-specific required inputs (Surprises to DELIVERY and ARCHITECTURE) (Step 5)
- [ ] Findings deduped; re-check applied with every move visible (a Critical without Trigger/Consequence demoted to Important or Suggestion by its Hits / Maintainer cost line; an Important without that line demoted to Suggestion); fix-eligibility pass run and eligible findings marked `[fix-proposed]` (or skipped because the fix path is unavailable); verdict derived per loop-interfaces.md; report opens with the `Verdict:` line and includes Aimed vs Achieved, Overall Assessment, Findings (`- (none)` is a complete Findings section), Questions for the Author, and Coverage; Overall Assessment carries `Path:` and `Decision:`; lead-added and downgraded aim/reshape moves visible; top layer passed the grading-word self-check (Step 6)
- [ ] At most one comment left the run (none when the user declined one) — drafted pre-fix and posted at phase A on a no-fix run, drafted after re-derivation and posted at phase B on a fix run, or — when no applied fix survived — the report-only comment posted with no phase B at all — opening with the verdict, carrying the follow-up line under it (Critical: re-review; Important: no re-review), ending with the marker, posted only after explicit approval of the exact text, or handed over as copy-paste at rung 2/3 (Step 7)
- [ ] Fixes (if elected) applied per the carve-out, suite green before any `[capability]` fix was delivered, the exact diff and comment text approved at phase B before any push or ref-update, and every non-delivery path left nothing on the author's branch with the marker naming the reviewed tip (Step 7)
- [ ] Approval (if eligible and elected): identity read cited from forge-detection, caller's login differed from the author's, target open, no existing approval at the tip; the exact command, target, and identity line approved by the user at the gate that showed them (phase B on a fix run); submitted only after the comment posted; any refusal quoted verbatim and never retried; on self-peek, rung 2/3, or an identity failure the withdrawal was stated at phase A, and on a moved-branch fallback — a rejected push or a failed compare-and-swap — the approval was withdrawn unsubmitted with the moved-tip line stated (Step 7)
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
