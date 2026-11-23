---
name: peek
description: "Use when reviewing a colleague's branch, MR, or PR ('review this branch', 'review this MR', 'review this PR') — deep parallel-lens review (code, architecture, aimed-vs-achieved) with no bd spec required, running without a question from `/peek` through delivery: a report that opens with a verdict (APPROVE / APPROVE WITH CHANGES / REQUEST CHANGES) and weights the MR's prior review, then mechanical fixes pushed, a comment posted, and — when the verdict clears and the caller is not the author — a forge approval, with the report saved to a local file; words with the invocation ('report only', 'no fixes', 'no approval') narrow what goes out."
---

<skill_overview>
Thin orchestrator for a fixed 8-step review flow: resolve the target, stand up a disposable worktree, dispatch the peek agent's RECON mode to establish intent, fan out three parallel judgment lenses (CODE, ARCHITECTURE, DELIVERY), each writing its report to a file, synthesize those files into a single aimed-vs-achieved report, elect what goes out, deliver it — fixes, a comment, a forge approval — and always clean up the worktree. The run asks nothing between `/peek` and its closing lines: the report says what is going out and why, and a saved copy is there to read afterwards. No bd epic is required — this is for reviewing someone else's branch, MR, or PR on demand.

All review protocol — mode charters, evidence rules, return contracts — lives in `agents/peek.md`. This skill never restates it; it only wires the flow.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — the 8-step flow order and its two holds (no stated aim at all; a lens failing twice) are fixed and must not be skipped, reordered, or added to; no other step asks the user anything. Judgment inside each lens and during synthesis adapts to what the branch actually contains.
</rigidity_level>

<quick_reference>
| Step | Action | How |
|------|--------|-----|
| 1 | Resolve target | Parse `/peek` argument (URL / number / branch / none) and any words narrowing what goes out; detect forge + rung (`forge-detection.md`) |
| 2 | Worktree setup | `git worktree add --detach <tmp> <ref>` (remote fetch or local ref); abort before creating anything if unresolved; record the reviewed tip, the fix-path facts, and the suite command |
| 3 | RECON dispatch | Agent tool, subagent_type "hyperpowers:peek", model "sonnet", blocking; writes aims, inventory, Prior Review to `<run-dir>/recon.md` and returns the one RECON line (`report-file-contract.md`); HOLD only when Stated Aims reads `(none)` |
| 4 | Parallel lens dispatch | 3x Agent tool (CODE/ARCHITECTURE/DELIVERY), one message, no model override, blocking, one report file each, RECON's aims and Surprises as written; a non-compliant lens is re-dispatched alone, once |
| 5 | Synthesis | Lead reads the four report files, dedups, applies the re-check (Critical and Important demotions, every move marked), marks fix-eligible findings `[fix-proposed]` per `pipeline-constants.md` (Peek Fix Carve-out), derives the pre-fix verdict and the Path line (loop-interfaces.md), runs the grading-word self-check (prose-style.md), assembles the report |
| 6 | Election | Lead-owned, no question: after the identity and target reads, every `[fix-proposed]` finding and the comment are elected, an approval available on APPROVE / APPROVE WITH CHANGES at rung 1 (open target, caller not the author, not already approved) is elected unless the review found a reason for it to wait, and each Decision item gets a position; the invocation's narrowing is applied; the `Going out:` line is written, the report is saved to its local file and printed — the first thing printed since `/peek` |
| 7 | Delivery | No gate: fixes, then the comment, then the approval; at most one comment per run, opening with the verdict, carrying the follow-up line under it (Critical: fix and re-review; Important: fix, no re-review), ending with the `<!-- peek: <sha> -->` marker; a fix that fails the suite or needs judgment reverts to an ordinary finding and the run continues; every failure is reported verbatim, never retried; the run ends with one line per thing that went out, with its link, and the saved report's path |
| 8 | Cleanup | `git worktree remove <tmp> --force` + prune; always runs, even on abort |
</quick_reference>

<when_to_use>
Use for:
- Reviewing a colleague's branch, MR, or PR ad hoc — no bd epic exists or is needed
- Producing an aimed-vs-achieved report with a derived verdict before approving, merging, or commenting on someone else's work
- Deep code + architecture judgment on a delta that has no plan document to check it against

**Don't use for:**
- Re-verifying a completed epic against its bd spec → `hyperpowers:review-implementation`
- Reviewing your own in-flight epic work → `executing-plans`' per-task review and end-of-epic reviewer already cover it
</when_to_use>

<the_process>

## Step 1: Resolve Target

Parse the `/peek` argument:
- MR/PR URL → extract forge + number from the URL shape
- Bare number → the current repo's MR/PR at that number
- Branch name → that literal branch
- No argument → the current branch (`git branch --show-current`)

Anything else the user says with the invocation, or types while the run is working, that narrows what goes out — `report only`, `no fixes`, `no comment`, `no approval`, in whatever words — is recorded here and applied at Step 6. Narrowing only removes: it never makes a finding fix-eligible or an approval available.

Run the Detection idiom from `skills/common-patterns/forge-detection.md` to determine the forge (`gh`, `glab`, or `none`) and state which rung of its Degradation ladder is in force. Cite that file for the detection commands and ladder — do not restate them here.

## Step 2: Worktree Setup

Two cases, by where the target lives:

- **Remote target** (an MR/PR, or a branch that resolves on the remote): `git fetch origin <source-branch>`, then `git worktree add --detach <tmp-path> FETCH_HEAD`.
- **Local target** (no remote configured, the fetch fails, or the target is the current branch or a local-only branch): `git worktree add --detach <tmp-path> <branch>` directly from the local ref.

`--detach` is REQUIRED in both cases — git refuses to add a worktree for a branch that is already checked out, and the default invocation (no argument = current branch) always hits that refusal without it.

When the target is the current branch and a same-named remote branch also exists, prefer the LOCAL ref — local commits may be ahead of the remote, and reviewing a stale remote head reviews the wrong code.

If neither the fetch nor a local ref resolves the target, abort with a clear message BEFORE creating anything — there is nothing to clean up in that case.

Put the tmp path under the system temp dir, unique per run. Resolve the base ref via the base-branch idiom cited from `forge-detection.md` (Base branch section). Record the worktree path — every dispatch in Steps 3-4 and the cleanup in Step 8 need it.

Create the run's report directory in the session scratchpad — `<scratchpad>/peek-<run-id>/` — and record it: every dispatch in Steps 3-4 names its own file there (`recon.md`, `code.md`, `architecture.md`, `delivery.md`) per `skills/common-patterns/report-file-contract.md`, and Step 5 synthesizes from those files. The directory is session scratch and is not cleaned up by Step 8; the worktree is.

Record these further facts at setup; Steps 4, 6, and 7 read them:

- **Target kind** — remote or local, as resolved above.
- **Reviewed tip** — `git -C <tmp-path> rev-parse HEAD`, run immediately after the worktree exists. This SHA is the pre-fix baseline: the base of the diff Step 7 delivers, the reset target when a fix is reverted, and the marker SHA on every path where fixes are not delivered.
- **Checkout state** (local targets only) — `git worktree list --porcelain | grep -F "branch refs/heads/<branch>"` in the target repo. A hit means some worktree holds that branch and its ref must not be moved.
- **Delivery remote** (remote targets only) — `git ls-remote --exit-code --heads origin <source-branch>`. A miss means `origin` does not carry the branch at all, which is what a cross-fork MR looks like from here: the review can read that code but can never deliver a commit to it.
- **Suite command** — the repo's standard test runner, when one is detected at the worktree; none when it is not. Step 4 hands it to CODE, and Step 7 runs it before any `[capability]` fix is delivered.

The fix path is available for a remote target whose source branch lives on `origin`, and for a local target whose branch is checked out nowhere. Two targets never get it and run review-only: the current branch, checked out by definition, and a cross-fork MR, whose source branch `origin` does not carry — Step 6 never elects a fix on a target that cannot receive it. The user's own checkout is never touched on any path: fixes are made in the disposable worktree and delivered by pushing, or by moving a ref no checkout holds.

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
    Report path: <run-dir>/recon.md
```

Blocking (no `team_name`). RECON's return contract (Stated Aims, Change Inventory, Surprises, Intent Basis, Coverage) is defined in `agents/peek.md` — do not restate it here. It arrives as the file at the report path plus the one `RECON:` line; check the return per the receiving rules in `skills/common-patterns/report-file-contract.md` (file present, Coverage present) before Step 4, and read Stated Aims, Surprises, and Prior Review from the file — the line's counts are a pointer, not the input.

From here to the report, print nothing: no playback of RECON's aims, no lens progress, no interim verdicts. RECON's Stated Aims, Surprises, and Prior Review go to the lenses as written, and the report names them (Step 5, the Calls line).

One hold: when Stated Aims reads `(none)` — the record states no aim at all — ask the user for the aim in one AskUserQuestion (`skills/common-patterns/question-format.md`; an expired box is not an answer, re-ask in durable prose and HOLD) and carry what they give as the stated aims. This and a lens failing twice (Step 4) are the only questions the run asks; the lenses are expensive, and a review with no aim to hold the code against has nothing to deliver.

## Step 4: Parallel Lens Dispatch

One message, three Agent calls:

```
Agent tool (single message, three calls — no team_name):
  1. subagent_type: "hyperpowers:peek", prompt: "Mode: CODE ... Report path: <run-dir>/code.md"
  2. subagent_type: "hyperpowers:peek", prompt: "Mode: ARCHITECTURE ... Report path: <run-dir>/architecture.md"
  3. subagent_type: "hyperpowers:peek", prompt: "Mode: DELIVERY ... Report path: <run-dir>/delivery.md"
```

No `model` field on any of the three — lenses inherit the session model (review depth is the product; it must not be silently downgraded). Each lens writes its own file under the run directory — never a shared one.

Each lens returns one `LENS <MODE>:` line and its file. Check every return per the receiving rules in `skills/common-patterns/report-file-contract.md` — cited, not restated. A lens whose return is non-compliant (no file, no Coverage section, a report in chat instead of a file) is re-dispatched once, alone, with the same prompt and the same path so it resumes from the sections already on disk; the two compliant lenses' files stand and are not re-run. On a second non-compliant return from the same lens, HOLD: present the partial file to the user and ask how to proceed — the lens is never dropped from synthesis silently, and its absence is never papered over by the other two.

Every prompt carries: Mode, target identity (`Target: <branch> -> <base ref>`, both halves — `agents/peek.md` requires the full target identity on every dispatch), RECON's stated aims, RECON's change inventory, the worktree path, forge rung, and RECON's Prior Review block verbatim (all three lenses — `agents/peek.md` lists it as a required input; a lens dispatch without it is an error per that file). DELIVERY and ARCHITECTURE additionally carry RECON's Surprises block as written. CODE additionally carries the suite command from Step 2, or states that none was detected. `agents/peek.md`'s Mode Detection section defines the full required-input set per mode — cite it, never restate it; a DELIVERY or ARCHITECTURE dispatch missing Surprises is an error per that file, not something this skill improvises around.

## Step 5: Synthesis (Lead)

Synthesis works from the four report files under the run directory — RECON's and the three lenses' — read in full at this step. The return lines' counts and any text a lens put in chat are never inputs.

Dedup overlapping findings first: same file:line + same defect = one finding, keep the highest severity.

**Re-check (lead-owned, every move visible in the report):** "filled" below means filled in the Severity Anchor's terms (`skills/common-patterns/pipeline-constants.md`): a cost line that names only reading effort is empty. A Critical whose `Trigger:` or `Consequence:` line is missing or empty becomes Important when it carries a filled `Hits:` or `Maintainer cost:` line, marked `[downgraded: no consequence named]`, and otherwise Suggestion, marked `[downgraded: no consequence named; no cost named]`; a `[convention]` Critical takes the same two-stage move, marked `[downgraded: convention]` or `[downgraded: convention; no cost named]`; an Important whose `Hits:` and `Maintainer cost:` lines are both missing or empty becomes Suggestion, marked `[downgraded: no cost named]`; a Suggestion that asks for no change (the forms are closed in `agents/peek.md`, Shared Rule 10) moves to Questions for the Author when it names a real uncertainty and is otherwise dropped, marked `[moved: no change asked]` in Questions or listed under a one-line `Dropped:` note at the end of Findings — never silently; a previously-reviewed finding without a `Prior review:` line moves to Questions for the Author; a finding missing Scope is treated as delta; a finding missing Class is assigned one by the lead (`skills/common-patterns/pipeline-constants.md`, Finding Classification: the lead owns final classification). The aims table and the Stance block are inputs to this re-check, not only text to render: an aims-table row reading `missing` with no matching delivery-class Critical is filed by the lead, marked `[lead-added: aim missing]`, with Trigger and Consequence drawn from the row and the stated aim; a Stance of reshapes with `Declared by: none` and no matching structural-class Critical is filed by the lead, marked `[lead-added: undeclared reshape]`, with Trigger and Consequence drawn from the Stance reasoning; an aim finding whose severity exceeds its table row is corrected to the row's severity, marked `[downgraded: aim partial]`. Dedup runs first and the re-check runs on the surviving finding, so a Suggestion never rises above what its evidence supports. The re-check reads the lines; it never fills one in — a cost or a hit the lens did not name is not the lead's to supply, and a demotion is reported with its marker, never silently. A lead-added Critical carries the Trigger and Consequence drawn from the row or the Stance and no Hits or Maintainer cost line (the Severity Anchor's exemption for synthesis-filed Criticals), and with both present it is never demoted.

**Fix-eligibility pass (lead-owned):** mark each surviving finding `[fix-proposed]` when `skills/common-patterns/pipeline-constants.md` (Peek Fix Carve-out) makes it eligible. That file owns which findings qualify and what evidence delivering them requires — cite it, never restate it. The mark changes nothing by itself: no file is edited, no commit is made, and nothing is delivered during synthesis. Skip this pass entirely when Step 2 found the fix path unavailable for this target; no finding gets marked and the run proceeds as review-only.

**Path and Decision (lead-owned):** `Path: rework` only when one cause shared by two or more surviving findings can be named, and that cause is stated in the Overall Assessment sentences; otherwise `Path: fix in place`. `Decision:` names what only the reader can decide — a declared reshape to accept or send back, an aim to drop from the description — each with the position Step 6 takes on it, or reads `(none)`. The vocabulary and its rule are registered in `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek report Path entry) — cite, never restate. Path never changes the verdict.

**Calls made without you (lead-owned):** one line under Decision naming every call the review rested on: the aims by count and source, naming any aim drawn from a commit message or a thread rather than the description (the Aimed vs Achieved table carries the aims themselves; the line never restates them); each Surprise left undeclared (an undeclared reshape among them is the structural Critical it produced); whether the suite ran, with its result, or did not and why; the Prior Review as read. Nothing else goes on the line.

**Derive the verdict** per `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek entry) — cite the derivation; never hand-pick. The report carries the pre-fix verdict, derived over every surviving finding, because nothing has been fixed yet; Step 7 re-derives it over the findings its fixes did not resolve.

Then assemble the report for the architect-governor reader per the Audience Contract (`skills/common-patterns/prose-style.md`, The Reader) — one citation, not restated here. RECON's Change Inventory, carried by every lens dispatch since Step 4, is no longer discarded after intent-gathering: it opens the report. This template is this skill's core output contract:

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
Decision: [what only the reader can decide, each with the position this run takes on it; or (none)]
Calls made without you: [aims: count and sources, any commit- or thread-sourced aim named; surprises left undeclared; suite ran / did not, why; prior review as read]
Going out: [written at Step 6 — fixes: which findings, or none and why; the comment; the approval: given | held, with the reason | not available, with the reason; anything the invocation narrowed away]

### Findings
[evidence layer — Critical, then Important, then Suggestions — each with severity, class, scope, file:line, evidence, suggested direction, and any downgrade marker; `- (none)` when the lenses returned none]
[findings the lead can resolve at the worktree carry a trailing `[fix-proposed]` mark — Step 7 applies them; the mark is not work already done]

### Questions for the Author
[evidence layer — merged from all lenses, deduped; entries marked `[out-of-lane: <LENS>]` are routed into the owning
lens's Findings during this synthesis step instead — see agents/peek.md Shared Rule 3 for the marker; `- (none)` when empty]

### Coverage
[evidence layer — union of all four lenses' Coverage blocks; anything unreviewed listed explicitly, never silently dropped]
```

**Self-check before presenting (lead-owned):** reread the top layer — the verdict sentence, What This Branch Does, the Aimed vs Achieved narrative, Overall Assessment — against the grading-word list in `skills/common-patterns/prose-style.md` (Human-Facing Prose Baseline). Every hit is rewritten into the concrete evidence behind it or deleted. An APPROVE with `- (none)` under Findings is a short report; nothing is added to make it look reviewed.

## Step 6: Election (Lead)

Three things can leave a run — fix commits, a comment, a forge approval — and the run elects all three itself. No question is asked: the report states the election, and Step 7 delivers it.

Before electing, run the identity read and the target read (`skills/common-patterns/forge-detection.md`, Identity, and Read commands: `state`, the author field, the number or iid) — RECON's return carries none of them.

- **Fixes.** Every `[fix-proposed]` finding is elected. None exists when Step 2 found the fix path unavailable.
- **The comment.** Always elected.
- **The approval.** Available when the report's verdict is `APPROVE` or `APPROVE WITH CHANGES` at rung 1, the target is open, the identity read shows the caller is not the target's author (that file's Author fields), and the caller has not already approved (C14 and C15 in that file give each forge's test); self-peek is comment-only on both forges even where the forge would allow it. An available approval is elected unless the review found a reason for it to wait: the forge would discard it before the merge (the project resets approvals on a push and the findings require one; a rebase or force-push is pending), or the merge is held on something outside this review that the approval would release (a merge order, a freeze). A hold names its reason; with none to name, the approval goes out.
- **Decision items.** Each item on the report's `Decision:` line gets a position, and the comment carries it as the review's ask: a declared reshape stands as declared; anything else takes the direction the evidence supports, or goes to the author as an open question when the evidence does not settle it. A position never grants what only the user can grant (an exception, a waiver, a sign-off), never commits the user to work, and never removes or demotes a finding; an item that would need any of these is an open question too.

Then apply the narrowing recorded at Step 1: `report only` removes all three, and `no comment` takes the approval with it — an approval always rides with a comment, because the comment carries the marker a later RECON matches and no forge state changes without that record.

Write the election on the report's `Going out:` line and each position on its `Decision:` line, with the reason for anything held, left open, or narrowed away. Save the report to `~/.hyperpowers/peek/<YYYY-MM-DD>-<repo>-<number or branch>-<reviewed tip, 8 characters>.md` (a `/` in a branch name becomes `-`): the file's first line names the target, the reviewed tip, and the date, and the report follows as printed. Then print the report — the first thing printed since `/peek` — and go straight to Step 7, or to Step 8 when nothing was elected.

## Step 7: Delivery

No gate: what Step 6 elected goes out in this order — fixes, comment, approval — and nothing is printed in between but the closing lines.

**Applying fixes.** At the worktree only: one commit per elected finding, `[convention]` first, an imperative subject of 60 characters or fewer, a body of exactly `Applied during review; details in the review comment.`, no plugin vocabulary anywhere in it. A `[capability]` fix needs green-suite evidence from a `hyperpowers:test-runner` dispatch at the worktree, on the suite command from Step 2, before delivery; a red or unrunnable suite resets those commits and demotes their findings back to the author (the suite rule in `skills/common-patterns/pipeline-constants.md`, Peek Fix Carve-out — cited, never restated). A fix that turns out to need judgment was never eligible: reset it and return the finding at its original severity. Neither stops the run: the finding takes its place in the comment as an ordinary finding, and the closing lines say which fixes reverted and why. A fix to a comment cuts or deletes it — never extends it (`skills/common-patterns/prose-style.md`, Comment Policy). Delivery: a remote target takes `git -C <tmp-path> push origin HEAD:<source-branch>`; a local target takes `git -C <target-repo> update-ref refs/heads/<branch> <new-sha> <reviewed-tip>`, a compare-and-swap, refused outright when Step 2 found the branch checked out in any worktree. Never force-push, amend, squash, or rebase — the carve-out's Delivery rule, cited not restated. Then re-derive the verdict over the findings not fixed (`skills/common-patterns/loop-interfaces.md`, Verdict Contracts, peek entry); on a run that delivered no fix, it is the report's verdict.

**The comment.** Professional and direct, built from the report as it stands after fixes: (a) the `Verdict:` line verbatim, and on the next line the follow-up line — with any Critical present, "The items marked Critical need a fix and a re-review; the Important items need a fix you verify yourself, no re-review." (drop the second clause when no Important accompanies it); with Importants only, "Fix the Important items and merge; no re-review is needed."; with nothing above Suggestion, "Nothing blocks merge; the suggestions are yours to take or leave." (or "Nothing blocks merge." when Findings reads `- (none)`) — the split is the Severity Anchor's (`skills/common-patterns/pipeline-constants.md`, cited not restated); (b) on a fix run, a short `Fixed directly (N commits pushed)` list in the author's language; (c) findings, each Decision position as the review's ask or as an open question, and questions per `skills/common-patterns/prose-style.md` — no internal vocabulary, no restated report sections, no Coverage block, readable in under a minute; (d) `<!-- peek: <sha> -->`, where `<sha>` is the tip the author's branch carries when the run ends — the reviewed tip recorded at Step 2, or the post-fix tip once fixes are delivered, never a tip that did not reach the branch — because that is the SHA the next RECON matches. At most one comment leaves a run, drafted after fixes are applied or reverted so it never carries a superseded verdict. Posting uses the write commands in `forge-detection.md` (the C2 caveat applies on GitLab). At rung 2/3 hand over the same text — follow-up line and marker included, so the author still reads which items need a re-review and which need no re-review — as copy-paste.

**The approval.** Before the approve call, confirm the branch still carries the tip the marker names (the Step 2 read, `git ls-remote --heads origin <source-branch>`, returns the head to compare); a branch that has moved gets a stated withdrawal, never an approval of code the review did not read. Then the approve command from `forge-detection.md` (Approve; on GitLab with `--sha` set to the marker's tip).

**When something fails.** One rule covers every failure — a rejected or non-fast-forward push, a compare-and-swap miss, a fork that `origin` cannot deliver to, a suite that did not run, a forge refusing the comment or the approval (GitHub's self-approval refusal, GitLab's 401, GitLab's 409 when `--sha` no longer matches — all documented in `forge-detection.md`, Approve): report the tool's output verbatim, never retry or work around it, leave everything already delivered as it is and everything not yet delivered undone, and say so. Whatever was not delivered comes back as the report-only outcome — the original findings at their original severity, the pre-fix verdict, the marker naming the reviewed tip. Step 8's forced worktree removal discards every commit that did not go out.

**Closing lines.** The run ends with one line per thing that went out — the push (branch and new tip), the comment (its URL), the approval (the MR/PR URL) — one line per elected thing that did not go out, naming why (a reverted fix, a withdrawn approval, a failure), and a last line giving the saved report's path. At rung 2/3 the comment's line is the copy-paste text itself, since that is how it goes out. Nothing else: no recap of the report, no restated findings, no summary of the run. Append the same lines to the saved report under `### Delivered`, so the copy read later records what the run did as well as what it found.

## Step 8: Cleanup

```
git worktree remove <tmp-path> --force
git worktree prune
```

This is an always-run closer — it runs even when the user aborts mid-flow, Step 6 elects nothing, or a dispatch fails partway through. Every path through this skill ends here. The forced removal is also how undelivered fix commits are discarded: any commit Step 7 built but did not deliver dies with the worktree, which is why no separate revert is needed on a fallback path.

</the_process>

<critical_rules>
## Rules That Have No Exceptions

1. **The run elects and delivers without asking; nothing leaves that Step 6 did not elect.** Fix commits, the comment, and the forge approval go out on Step 6's election — every `[fix-proposed]` finding, the comment, an available approval with no named reason to wait — with no question before delivery and no confirmation of the text, diff, or command. What the user narrowed away never leaves. A forge approval never goes out on a self-peek, at rung 2/3, without its comment, or when the branch no longer carries the tip the marker names.
2. **No stop and nothing printed between `/peek` and the report.** RECON's aims, Surprises, and Prior Review go to the lenses as written; the report's Calls line names them. The only holds, and the only questions the run asks, are a `(none)` Stated Aims (Step 3) and a lens failing twice (Step 4). "The aims look wrong" and "the diff is tiny" both wait for the report.
3. **Never restate agent protocol.** Mode charters, evidence rules, and return contracts live in `agents/peek.md`. Cite, never copy.
4. **The report must open with the `Verdict:` line, carry `Path:`, `Decision:`, the Calls line, and `Going out:` under Overall Assessment, and include Coverage.** A synthesis that omits any of these is incomplete: the `Verdict:` line is derived, never hand-picked; `Path:` is likewise derived per `skills/common-patterns/loop-interfaces.md`, never hand-picked; and anything unreviewed must be named in Coverage, not silently dropped.
5. **The worktree is always cleaned up.** Step 8 runs on every path, including aborts and dispatch failures.
6. **The fix path is bounded by the Peek Fix Carve-out** (`skills/common-patterns/pipeline-constants.md`). Critical findings are never fixed at review; nothing is pushed or ref-updated that Step 6 did not elect.
7. **Every dispatch names a report file; synthesis reads files.** RECON and the three lenses each write to their own file under the run directory and return one line (`skills/common-patterns/report-file-contract.md`); a return with no file behind it is re-dispatched, never read.
8. **Every report is saved before anything is delivered.** Step 6 writes the saved copy and Step 7 closes it with the delivery lines; a run nobody watched is read from that file.

## Common Excuses

All of these mean: **STOP. Follow the process as written.**

- "The diff is small, skip RECON" — RECON runs every time; size does not exempt intent-gathering.
- "CI is green, skip CODE" — a green suite does not substitute for the CODE lens's judgment. The same goes for skipping any lens: all three dispatch every run (Step 4); no lens is optional.
- "The lens put its whole report in chat, that is as good as the file" — it is not: a chat report is the truncation path this contract removes, and the receiving rule reads nothing from it. Re-dispatch that lens alone with the same path; it resumes from whatever the file already holds.
- "Two lenses came back, synthesize from those" — a missing lens is a missing charter, not a thinner report. Re-dispatch it once; on a second failure HOLD with the partial file.
- "Let me confirm the aims before the lenses, to be safe" — across 89 intent gates the aims changed in about 6 runs, and once the calls moved onto the report none was overturned in 123 chances. The lenses run on RECON's aims; the report names every call.
- "Show the diff before pushing, to be safe" — 117 of about 118 delivery approvals went through unchanged. The election at Step 6 is the approval; what it elected goes out.
- "Ask what should go out before delivering, to be safe" — across 204 answered decision rounds the user posted the comment in 205 of 206 questions, followed the lead's approve-or-hold call in 119 of 119, and took every offered fix in 155 of 162. The open question cost a median 5 minutes and over an hour in one run in ten, and in 6 runs something elected never went out because the branch moved during the wait. Step 6 elects; the report says what is going out and why.
- "Nobody is watching this run, hold the approval to be safe" — the user followed the lead's call on all 119 approval questions, 101 of them to approve. A hold names a reason the review found (Step 6); an unattended run is not one.
- "The Decision is the user's to make, hold the run for them" — the user took the lead's position on 130 of 138 Decision items and accepted all 69 declared reshapes. Step 6 takes the position and the report records it; what only the user can grant goes to the author as an open question.
- "The author just pushed, or is mid-rebase, so leave the fix to them" — the user had the fix pushed in 7 of the 8 runs where the lead recommended leaving it. Every `[fix-proposed]` finding is applied; a push that cannot land fails under Step 7's one rule and the finding returns to the comment.
- "A fix push makes the user a commit author and could cost their approval, skip the fixes" — that trade is the user's, made with `no fixes` at the invocation. Without it every `[fix-proposed]` finding is applied.
- "The author is senior, soften the findings" — softening includes dropping: every finding stays in the report at its true severity, whoever the author is. The finding set does not scale with seniority; only phrasing may be professional, never the finding set.
- "No Critical makes the review look shallow" — a clean return is a complete result. Severity follows the anchor, not the reviewer's need to look rigorous; manufacturing a finding is the mirror image of softening one.
- "It has been reviewed four times, something must be wrong" — prior review is evidence to weigh, not a quota to beat. A finding on previously-reviewed code says what the earlier reviewers missed, or it is a question.
- "It was approved, drop the finding" — approval never suppresses a finding; it demands the `Prior review:` justification. Deferring is the other way to be wrong.
- "The fix is obvious, push it too" — Step 6 elects the `[fix-proposed]` findings and Step 7 pushes those and no other. Eligibility under the carve-out elects a fix; obviousness does not.
- "The verdict is APPROVE, just approve it on the forge" — the approval goes out only behind Step 6's identity and target reads and Step 7's tip check; a verdict alone clears none of them.
- "It is my own MR and GitLab allows it" — self-peek is comment-only on both forges; an approval means a second person looked.
- "APPROVE WITH CHANGES, so wait for the re-peek" — an Important needs no re-review: the author fixes and self-certifies (Severity Anchor, cited). Only a Critical asks for a re-review, and the follow-up line under the verdict says which is which.
- "Fix the Critical too while I'm in there" — a Critical is never fix-eligible (`skills/common-patterns/pipeline-constants.md`, Peek Fix Carve-out). The author must confront it; quietly resolving it at review hides the one finding that most needed their attention.
- "The suite is missing, push the capability fix anyway" — no green suite, no capability fix: demote it back to an ordinary finding for the author. Convention fixes are unaffected by the suite's state.
- "Post the comment now, deliver the fixes after" — at most one comment leaves a run, and on a fix run it is never the pre-fix draft: it is drafted after fixes are applied or reverted and posted after the push; a comment posted ahead of delivery carries a superseded verdict, omits what the review fixed, and stamps a marker the branch has already moved past.
- "A clean branch deserves some acknowledgment" — the APPROVE verdict is the acknowledgment. An adjective that appears on every report carries no information; describe what the branch changes and stop.
- "The findings feel like a rework, call it one" — `Path: rework` requires a named shared cause in the Overall Assessment; a feeling without a cause is `fix in place`, and the findings speak for themselves.
</critical_rules>

<verification_checklist>
Before the report is printed:
- [ ] Forge and degradation rung detected and stated; any narrowing said with the invocation recorded (Step 1)
- [ ] Worktree created with `--detach`, base ref resolved, user's checkout untouched, reviewed tip and suite command recorded (Step 2)
- [ ] RECON dispatched with the sonnet model override, blocking, with a report path under the run directory; its return checked per `report-file-contract.md` and Stated Aims plus Prior Review read from the file; held only on a `(none)` Stated Aims; nothing printed from here to the report (Step 3)
- [ ] All three lenses dispatched in one message, no model override, each with its own report path and its mode-specific required inputs (RECON's aims and Surprises as written; the suite command to CODE); every return checked per `report-file-contract.md`, any non-compliant lens re-dispatched alone once, a second failure held with the partial file (Step 4)
- [ ] Synthesis read from the four report files, never from chat text; findings deduped; re-check applied with every move visible (a Critical without Trigger/Consequence demoted to Important or Suggestion by its Hits / Maintainer cost line; an Important without that line demoted to Suggestion); fix-eligibility pass run and eligible findings marked `[fix-proposed]` (or skipped because the fix path is unavailable); verdict derived per loop-interfaces.md; report opens with the `Verdict:` line and includes Aimed vs Achieved, Overall Assessment, Findings (`- (none)` is a complete Findings section), Questions for the Author, and Coverage; Overall Assessment carries `Path:`, `Decision:`, and the Calls line; lead-added and downgraded aim/reshape moves visible; top layer passed the grading-word self-check (Step 5)
- [ ] No question asked outside the two holds; identity and target reads run; every `[fix-proposed]` finding and the comment elected; the approval elected only when the verdict clears at rung 1 on an open target and the caller is not the author and has not already approved, and held only for a reason the report names; every Decision item given a position that grants nothing in the user's name, commits them to no work, and removes no finding; the invocation's narrowing applied; `Going out:` written; the report saved to its local file, then printed (Step 6)

Before the run ends:
- [ ] Only what Step 6 elected went out, in the order fixes, comment, approval, with nothing asked; `[capability]` fixes carried green-suite evidence; a reverted fix returned to the comment as an ordinary finding; at most one comment, drafted after fixes, opening with the verdict, carrying the follow-up line, ending with the marker naming the tip the branch actually carries — posted, or handed over as copy-paste at rung 2/3; the approval submitted after the comment and only once the branch still carried the marker's tip; every failure reported verbatim and never retried, every withdrawal stated; the run ended with one line per thing that went out, with its link, the saved report's path, and no recap; the same lines appended to the saved report (Step 7)
- [ ] Worktree removed and pruned (Step 8) — including on any abort path
</verification_checklist>

<integration>
**This skill calls:**
- `hyperpowers:peek` agent (subagent, x4 dispatches — RECON, CODE, ARCHITECTURE, DELIVERY)
- `hyperpowers:test-runner` (via the CODE lens when Step 2 detected a suite command, and by the lead at Step 7 when a `[capability]` fix is applied)

**This skill is called by:**
- User, via `/hyperpowers:peek`

**Sibling, not overlap:** `hyperpowers:review-implementation` re-verifies a completed epic against its immutable bd spec — a fundamentally different input (a spec exists and is authoritative) from peek's spec-less branch/MR review. Don't route between them; they answer different questions.
</integration>
