---
name: peek
description: "Use when reviewing a colleague's branch, MR, or PR ('review this branch', 'review this MR', 'review this PR') — deep parallel-lens review (code, architecture, aimed-vs-achieved) with no bd spec required, producing a harsh-but-fair report that opens with a verdict (APPROVE / APPROVE WITH CHANGES / REQUEST CHANGES), weights the MR's prior review, and offers an optional draft comment."
---

<skill_overview>
Thin orchestrator for a fixed 8-step review flow: resolve the target, stand up a disposable worktree, dispatch the peek agent's RECON mode to establish intent, confirm that intent with the user, fan out three parallel judgment lenses (CODE, ARCHITECTURE, DELIVERY), synthesize their returns into a single aimed-vs-achieved report, offer a draft comment, and always clean up the worktree. No bd epic is required — this is for reviewing someone else's branch, MR, or PR on demand.

All review protocol — mode charters, evidence rules, return contracts — lives in `agents/peek.md`. This skill never restates it; it only wires the flow.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — the 8-step flow order and its gates (intent confirm, draft-comment approval) are fixed and must not be skipped or reordered. Judgment inside each lens and during synthesis adapts to what the branch actually contains.
</rigidity_level>

<quick_reference>
| Step | Action | How |
|------|--------|-----|
| 1 | Resolve target | Parse `/peek` argument (URL / number / branch / none); detect forge + rung (`forge-detection.md`) |
| 2 | Worktree setup | `git worktree add --detach <tmp> <ref>` (remote fetch or local ref); abort before creating anything if unresolved |
| 3 | RECON dispatch | Agent tool, subagent_type "hyperpowers:peek", model "sonnet", blocking; returns aims, inventory, Prior Review |
| 4 | Intent confirm gate | AskUserQuestion: confirm/correct/add aims, confirm/correct the Prior Review summary, opt-in suite run; HOLD on expiry |
| 5 | Parallel lens dispatch | 3x Agent tool (CODE/ARCHITECTURE/DELIVERY), one message, no model override, blocking |
| 6 | Synthesis | Lead dedups, applies the re-check, derives the verdict (loop-interfaces.md), assembles the report |
| 7 | Draft comment offer | AskUserQuestion; comment opens with the verdict and ends with the `<!-- peek: <sha> -->` marker; post only after the user approves the exact text |
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

Put the tmp path under the system temp dir, unique per run. Resolve the base ref via the base-branch idiom cited from `forge-detection.md` (Base branch section). The user's own checkout is never touched. Record the worktree path — every dispatch in Steps 3-5 and the cleanup in Step 8 need it.

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

**Derive the verdict** per `skills/common-patterns/loop-interfaces.md` (Verdict Contracts, peek entry) — cite the derivation; never hand-pick.

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

### Questions for the Author
[evidence layer — merged from all lenses, deduped; entries marked `[out-of-lane: <LENS>]` are routed into the owning
lens's Findings during this synthesis step instead — see agents/peek.md Shared Rule 3 for the marker; `- (none)` when empty]

### Coverage
[evidence layer — union of all four lenses' Coverage blocks; anything unreviewed listed explicitly, never silently dropped]
```

## Step 7: Draft Comment Offer

AskUserQuestion: draft a comment for the MR/PR? If yes: draft a professional, direct comment built from the report in three parts — (a) opens with the report's `Verdict:` line verbatim (the same `Verdict: <word>` text, before anything else), (b) lists findings and questions per the existing prose rules (no internal vocabulary — no lens names, no mode words), (c) ends with `<!-- peek: <sha> -->`, where `<sha>` is the reviewed tip (`git -C <tmp-path> rev-parse HEAD`) — the marker renders as nothing on GitHub and GitLab and lets a later RECON recognize this review. Comment prose otherwise follows `skills/common-patterns/prose-style.md`: findings and questions only — no restated report sections, no Coverage block, no praise-padding; target a comment the author reads in under a minute, longer only when the finding count itself demands it. Show the drafted text to the user. Only after the user approves that exact text, post it via the write commands cited from `forge-detection.md`. On GitLab, the C2 caveat applies at this step: try the `note create` form first, fall back to the legacy `note -m` form second, per `forge-detection.md`'s caveat table. On rung 2/3 (no forge, or no MR/PR resolvable), hand over copy-paste text instead of posting — that text carries the `Verdict:` opening and the `<!-- peek: <sha> -->` marker too.

NEVER post without the user's approval of the exact text that goes out.

## Step 8: Cleanup

```
git worktree remove <tmp-path> --force
git worktree prune
```

This is an always-run closer — it runs even when the user aborts mid-flow, declines at a gate, or a dispatch fails partway through. Every path through this skill ends here.

</the_process>

<critical_rules>
## Rules That Have No Exceptions

1. **Never auto-post.** A draft comment goes out only after the user approves the exact text (Step 7).
2. **Never skip the intent gate.** "The diff is tiny, skip confirmation" is the named rationalization — the gate runs every time, regardless of branch size.
3. **Never restate agent protocol.** Mode charters, evidence rules, and return contracts live in `agents/peek.md`. Cite, never copy.
4. **The report must open with the `Verdict:` line and include Coverage.** A synthesis that omits either is incomplete: the `Verdict:` line is derived, never hand-picked, and anything unreviewed must be named in Coverage, not silently dropped.
5. **The worktree is always cleaned up.** Step 8 runs on every path, including aborts and dispatch failures.

## Common Excuses

All of these mean: **STOP. Follow the process as written.**

- "The diff is small, skip RECON" — RECON runs every time; size does not exempt intent-gathering.
- "CI is green, skip CODE" — a green suite does not substitute for the CODE lens's judgment. The same goes for skipping any lens: all three dispatch every run (Step 5); no lens is optional.
- "I can infer intent without the gate" — Step 4 is interactive by design; inferred intent is not confirmed intent.
- "The author is senior, soften the findings" — softening includes dropping: every finding stays in the report at its true severity, whoever the author is. Harsh-but-fair does not scale with seniority; only phrasing may be professional, never the finding set.
- "No Critical makes the review look shallow" — a clean return is a complete result. Severity follows the anchor, not the reviewer's need to look rigorous; manufacturing a finding is the mirror image of softening one.
- "It has been reviewed four times, something must be wrong" — prior review is evidence to weigh, not a quota to beat. A finding on previously-reviewed code says what the earlier reviewers missed, or it is a question.
- "It was approved, drop the finding" — approval never suppresses a finding; it demands the `Prior review:` justification. Deferring is the other way to be wrong.
</critical_rules>

<verification_checklist>
Before presenting the report to the user:
- [ ] Forge and degradation rung detected and stated (Step 1)
- [ ] Worktree created with `--detach`, base ref resolved, user's checkout untouched (Step 2)
- [ ] RECON dispatched with the sonnet model override, blocking, and returned Stated Aims plus Prior Review before the intent gate (Step 3)
- [ ] User confirmed or corrected the aims and the Prior Review summary — no provisional intent carried forward (Step 4)
- [ ] All three lenses dispatched in one message, no model override, with their mode-specific required inputs (Step 5)
- [ ] Findings deduped; re-check applied with every move visible; verdict derived per loop-interfaces.md; report opens with the `Verdict:` line and includes Aimed vs Achieved, Overall Assessment, Findings (`- (none)` is a complete Findings section), Questions for the Author, and Coverage (Step 6)
- [ ] Draft comment (if requested) opens with the verdict, ends with the marker, and was posted only after explicit approval of the exact text, or handed over as copy-paste at rung 2/3 (Step 7)
- [ ] Worktree removed and pruned (Step 8) — including on any abort path
</verification_checklist>

<integration>
**This skill calls:**
- `hyperpowers:peek` agent (subagent, x4 dispatches — RECON, CODE, ARCHITECTURE, DELIVERY)
- `hyperpowers:test-runner` (via the CODE lens, only when the user opts into the suite run at Step 4)

**This skill is called by:**
- User, via `/hyperpowers:peek`

**Sibling, not overlap:** `hyperpowers:review-implementation` re-verifies a completed epic against its immutable bd spec — a fundamentally different input (a spec exists and is authoritative) from peek's spec-less branch/MR review. Don't route between them; they answer different questions.
</integration>
