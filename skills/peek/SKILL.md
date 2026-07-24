---
name: peek
description: "Use when reviewing a colleague's branch, MR, or PR ('review this branch', 'review this MR', 'review this PR') — deep parallel-lens review (code, architecture, aimed-vs-achieved) with no bd spec required, producing a harsh-but-fair report and optional draft comment."
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
| 3 | RECON dispatch | Agent tool, subagent_type "hyperpowers:peek", model "sonnet", blocking |
| 4 | Intent confirm gate | AskUserQuestion: confirm/correct/add aims + opt-in suite run; HOLD on expiry |
| 5 | Parallel lens dispatch | 3x Agent tool (CODE/ARCHITECTURE/DELIVERY), one message, no model override, blocking |
| 6 | Synthesis | Lead dedups findings, assembles the report (template owned by this skill) |
| 7 | Draft comment offer | AskUserQuestion; post only after the user approves the exact text |
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
  mode: "bypassPermissions"
  model: "sonnet"    # the ONLY model override in this skill — mechanical gathering
  prompt: |
    Mode: RECON
    Target: <branch> -> <base ref>
    Worktree path: <tmp-path>
    Forge: <gh | glab | none> at rung <1 | 2 | 3>
```

Blocking (no `team_name`). RECON's return contract (Stated Aims, Change Inventory, Surprises, Intent Basis, Coverage) is defined in `agents/peek.md` — do not restate it here.

## Step 4: Intent Confirm Gate (Interactive)

Play back RECON's Stated Aims and Surprises via AskUserQuestion (form and gate discipline: `skills/common-patterns/question-format.md`). Offer: confirm as-is / correct (free text) / add a missing aim. When a standard test runner is detected in the repo, the same round also offers the opt-in suite run, with "run it" as the default suggestion.

An expired question box is not an answer — re-ask in durable prose and HOLD (per `question-format.md`, Timeouts and Gates). Never proceed on a provisional intent: the lenses in Step 5 are expensive, and wrong intent wastes every one of them.

Carry forward from this step: the confirmed aims and the suite-run decision.

## Step 5: Parallel Lens Dispatch

One message, three Agent calls:

```
Agent tool (single message, three calls — no team_name):
  1. subagent_type: "hyperpowers:peek", mode: "bypassPermissions", prompt: "Mode: CODE ..."
  2. subagent_type: "hyperpowers:peek", mode: "bypassPermissions", prompt: "Mode: ARCHITECTURE ..."
  3. subagent_type: "hyperpowers:peek", mode: "bypassPermissions", prompt: "Mode: DELIVERY ..."
```

No `model` field on any of the three — lenses inherit the session model (review depth is the product; it must not be silently downgraded).

Every prompt carries: Mode, target identity (`Target: <branch> -> <base ref>`, both halves — `agents/peek.md` requires the full target identity on every dispatch), the confirmed aims, RECON's change inventory, the worktree path, and forge rung. DELIVERY additionally carries RECON's Surprises block. CODE additionally carries the suite-run decision from Step 4. `agents/peek.md`'s Mode Detection section defines the full required-input set per mode — cite it, never restate it; a DELIVERY dispatch missing Surprises is an error per that file, not something this skill improvises around.

## Step 6: Synthesis (Lead)

Dedup overlapping findings first: same file:line + same defect = one finding, keep the highest severity. Then assemble the report — this template is this skill's core output contract:

```
## Peek Review: <branch> -> <base>

### Aimed vs Achieved
[2-4 sentence narrative] + DELIVERY's per-aim table + Undeclared Changes

### Overall Assessment
[harsh but fair paragraph, including ARCHITECTURE's stance (fits/fights/reshapes) with its reasoning]

### Findings
[Critical, then Important, then Suggestions — each with file:line, evidence, suggested direction]

### Questions for the Author
[merged from all lenses, deduped; entries marked `[out-of-lane: <LENS>]` are routed into the owning
lens's Findings during this synthesis step instead — see agents/peek.md Shared Rule 3 for the marker]

### Coverage
[union of all four lenses' Coverage blocks; anything unreviewed listed explicitly, never silently dropped]
```

## Step 7: Draft Comment Offer

AskUserQuestion: draft a comment for the MR/PR? If yes: draft a professional, direct comment from the report (findings + questions; no internal vocabulary — no lens names, no mode words). Show the drafted text to the user. Only after the user approves that exact text, post it via the write commands cited from `forge-detection.md`. On GitLab, the C2 caveat applies at this step: try the `note create` form first, fall back to the legacy `note -m` form second, per `forge-detection.md`'s caveat table. On rung 2/3 (no forge, or no MR/PR resolvable), hand over copy-paste text instead of posting.

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
4. **The report must include Coverage.** A synthesis that omits the union Coverage block is incomplete — anything unreviewed must be named, not silently dropped.
5. **The worktree is always cleaned up.** Step 8 runs on every path, including aborts and dispatch failures.

## Common Excuses

All of these mean: **STOP. Follow the process as written.**

- "The diff is small, skip RECON" — RECON runs every time; size does not exempt intent-gathering.
- "CI is green, skip CODE" — a green suite does not substitute for the CODE lens's judgment.
- "I can infer intent without the gate" — Step 4 is interactive by design; inferred intent is not confirmed intent.
- "The author is senior, soften the findings" — harsh-but-fair cuts both ways: it does not scale with the author's seniority.
</critical_rules>

<verification_checklist>
Before presenting the report to the user:
- [ ] Forge and degradation rung detected and stated (Step 1)
- [ ] Worktree created with `--detach`, base ref resolved, user's checkout untouched (Step 2)
- [ ] RECON dispatched with the sonnet model override, blocking, and returned before the intent gate (Step 3)
- [ ] User confirmed or corrected the aims — no provisional intent carried forward (Step 4)
- [ ] All three lenses dispatched in one message, no model override, with their mode-specific required inputs (Step 5)
- [ ] Findings deduped; report includes Aimed vs Achieved, Overall Assessment, Findings, Questions for the Author, and Coverage (Step 6)
- [ ] Draft comment (if requested) posted only after explicit approval of the exact text, or handed over as copy-paste at rung 2/3 (Step 7)
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
