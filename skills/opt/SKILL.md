---
name: opt
description: "Use when review feedback arrives on your MR/PR ('address the review', 'respond to MR comments', 'the reviewer said X') — triage each finding against project reality, escalate accepted defects to root cause and bug class, apply proportioned fixes, draft gated replies"
---

<skill_overview>
The receiving side of code review. A fixed seven-step loop: resolve the target and ingest its review threads, normalize them into finding records, verify each against project reality, escalate accepted defects to root cause and bug class, take one batch disposition gate, execute the approved work in tiers, then draft per-thread replies and take one outward gate covering replies and push together.

Two properties define it. Nothing is accepted at face value — a reviewer's claim is a hypothesis until checked against the code, the conventions, and the design that produced it. Nothing goes outward — no reply, no commit on the branch — until the architect approves the exact text and the exact diff.

peek gives reviews; opt receives them. Shared forge plumbing lives in `skills/common-patterns/forge-detection.md`; this skill never restates it.
</skill_overview>

<rigidity_level>
MEDIUM-LOW FREEDOM — the step order, the disposition vocabulary, the escalation trigger, and both gates are rigid: they do not bend for small reviews, senior reviewers, or obvious fixes. Investigation depth inside Step 3 and Step 4 adapts to what the finding actually claims.
</rigidity_level>

<quick_reference>
| Step | Action | How |
|------|--------|-----|
| 1 | Resolve & ingest | Parse argument (URL / number / branch / none); detect forge + rung (`forge-detection.md`); read threads WITH resolution state; record target state, worktree path, and pre-run tip; unresolved threads are the work queue |
| 2 | Normalize | One finding record per claim: source thread, reviewer, claim, location, class + severity (`pipeline-constants.md`) |
| 3 | Verify against reality | Code, conventions, ADRs, source epic's design and anti-patterns; codebase-investigator for structure; every finding exits confirmed / refuted / contested with evidence |
| 4 | Escalation check | Accepted `[capability]` defects only: origin-or-symptom (root-cause-tracing) + class sweep for sibling sites (debugging-with-tools Rule 4). Proposes; never acts |
| 5 | Batch disposition gate | ONE table, AskUserQuestion: FIX NOW / FILE FOLLOW-UP / DECLINE / NEEDS REVIEWER INPUT. Gate-state persisted on timeout |
| 6 | Execute (tiered) | Carve-out-eligible fixes lead-fixed at the worktree (bar: `pipeline-constants.md`); confirmed defects failing-test-first; approved class fixes across swept sites; FILE FOLLOW-UP → fresh bd issues |
| 7 | Replies + outward gate | Per-thread drafts in colleague prose; ONE gate covers posting AND pushing; re-check target state; wrap-up report |
</quick_reference>

<when_to_use>
Use for:
- Review feedback that has arrived on your own MR/PR — a colleague's threads, a posted peek comment, or review text pasted into the session
- Deciding what to do about a review whose findings you are not sure are right for this project
- Turning an accepted review finding into the fix its bug class actually needs, rather than patching only the flagged line

**Don't use for:**
- Reviewing someone else's branch, MR, or PR → `hyperpowers:peek`
- Re-verifying a completed epic against its bd spec when no review exists → `hyperpowers:review-implementation`
- Claiming your own work is done with no reviewer involved → `hyperpowers:verification-before-completion`
</when_to_use>

<the_process>

## Step 1: Resolve & Ingest

Parse the `/opt` argument:
- MR/PR URL → forge and number from the URL shape
- Bare number → the current repo's MR/PR at that number
- Branch name → that branch's open MR/PR
- No argument → the current branch (`git branch --show-current`) and its open MR/PR
- Review text pasted into the session → the degradation floor; skip forge reads entirely and go to Step 2 with the pasted text as the sole source. Skipping the forge read also skips the only source of target state, so record it as `unknown` and carry that forward: Step 7's re-check becomes a question at the outward gate — the architect states whether the target is still open, and until they do, nothing is pushed. If they name the MR/PR there, read its state through the normal path instead of asking.

Run the Detection idiom from `skills/common-patterns/forge-detection.md` and state which rung of its Degradation ladder is in force. Then two reads, both taken from that file and never restated here: its Read command for the target itself, which carries the target's metadata, state and author; and its Review state commands for the threads with their resolution state — GitLab folds resolution per note from `discussions --paginate`, GitHub reads `reviewThreads` through GraphQL.

**Record the target state** (`open`, `merged`, `closed`, or `unknown` when no forge read happened) from that target read. Step 6 and Step 7 both consult it.

**The work queue is the unresolved threads.** A resolved thread is settled — never re-triage it. Resolution is the reviewer's signal that the exchange is done, and honoring it is what makes a second `/opt` run on the same MR safe.

Three queue states this step must handle before anything else runs:

- **Nothing to triage.** Every thread is resolved, or the target carries no review activity at all. Report that in at most three sentences — target, rung, thread counts — and end the run. No normalization, no escalation, no gates: a run with an empty queue fires nothing.
- **Awaiting-reviewer threads.** An unresolved thread whose latest comment is ours, with no reviewer activity after it, is awaiting-reviewer, not new work. It stays out of the queue and appears in Step 7's wrap-up as pending. A thread re-enters the queue only when a reviewer has commented after that last reply of ours — that new comment is the finding, not the whole thread again.

  **"Ours" is a login match, not a memory.** A fresh session remembers no prior run, so identity comes from the reads this step already made: the target's own author login — `/opt` runs on your own MR/PR, so its author is you — matched against the author each thread comment carries. Both operands come from the target read and the Review state reads already run above; the field names differ per forge and `skills/common-patterns/forge-detection.md` (Author fields) gives them. Step 7 posts every reply into its source thread rather than as a new top-level comment, so this loop's own replies are among the comments this check reads. That comparison is what makes a second `/opt` run on the same target idempotent, and it holds for replies posted by hand as well as by this loop. When the reads cannot establish that login, say so and treat every unresolved thread as work: a duplicated reply is recoverable, a dropped finding is not.
- **Merged or closed target.** The MR/PR moved on while the review sat. Keep going: triage, verification and dispositions are all still worth doing. But nothing may be pushed to a merged or closed target — at Step 6 every accepted fix becomes a FILE FOLLOW-UP instead, and Step 7's gate covers replies only.

**peek-sourced comments.** A comment ending in `<!-- peek: <sha> -->` came from `hyperpowers:peek`: it opens with a verdict line and carries findings already anchored to severity and file:line. The line directly under its verdict — which findings need a re-review and which the author self-certifies — is the comment's follow-up line, not a finding: Step 2 records nothing for it. Treat that structure as a head start on Step 2 — and nothing more. It buys no exemption from Step 3; a structured claim is still a claim.

**The worktree.** Work happens on a checkout of the MR branch. If the current directory is already on that branch, use it. Otherwise find the worktree `hyperpowers:finishing-a-development-branch` kept when it created the MR (`git worktree list`), and if it is gone, re-create it: `git worktree add <path> <branch>`. Record two facts about it:

- **Worktree path** — Steps 3, 6 and 7 all use it.
- **Pre-run tip** — `git -C <worktree> rev-parse HEAD`, run immediately after the worktree is resolved, before any fix touches it. This SHA is the diff boundary at Step 7's outward gate: it is what the architect's approval is measured against, so it must be captured before Step 6 can move HEAD.

**Ingestion valve.** Above **25 unresolved threads** in the queue, do not read them all in the lead. Dispatch one general-purpose subagent with the forge read commands and the Step 2 record schema, and have it return only the normalized finding records — no thread bodies. Below that threshold, read them in the lead: the comment text is needed for judgment in Step 3 and for reply drafting in Step 7 anyway, and 25 threads is where that stops being cheap.

## Step 2: Normalize

Each review item becomes one finding record:

```
F<n> | thread: <thread id / permalink>  | reviewer: <login>
claim:    <what the reviewer asserts, in their terms>
location: <file>:<line>  (or "unanchored" for a general comment)
class:    [capability] | [convention]
severity: <per the Severity Anchor>
```

Class tags and severity come from `skills/common-patterns/pipeline-constants.md` (Finding Classification; Severity Anchor). That file scopes classification to reviews "or otherwise" and gives the lead final say, which is the authority to tag prose comments a colleague wrote without any tag at all. Cite those definitions; do not restate them.

Severity is exactly one of the Severity Anchor's three words — Critical, Important, Suggestion. No fourth tier (`Minor`, `Low`, `Nice-to-have`) is invented for a convention nit that feels more actionable than "Suggestion" sounds; a non-blocking finding is Suggestion, full stop.

**One comment can hold several findings.** A reviewer who writes "this leaks a handle and the variable name is wrong" filed one comment and two findings: they get separate records, separate verification, and separate dispositions. They share a source thread, so Step 7 merges their replies back into one.

## Step 3: Verify Against Project Reality

No finding is accepted because a reviewer wrote it. Findings whose correctness is self-evident — a typo, a name the code plainly does not have — pass through with a one-line evidence note. Everything else gets checked against:

- **The code** at the worktree — read the cited site and its callers, not just the diff hunk.
- **Project conventions** — CLAUDE.md, sibling implementations, the surrounding file's existing style.
- **Architecture decisions** — `docs/arch/adr/` when it exists. A finding that contradicts a recorded decision is a DECLINE candidate with the strongest evidence there is.
- **The source epic's design and anti-patterns** — when the branch is identifiable (an `epic/<id>` branch name, or `bd:` trailers in the branch's commits), `bd show <epic-id>` and read its Design and Anti-Patterns. A reviewer suggesting exactly what the epic forbids is the single most common false finding this step catches.

Dispatch `hyperpowers:codebase-investigator` for structure questions ("does anything else call this?", "is this pattern used elsewhere?"). With three or more independent questions, dispatch them in parallel per `hyperpowers:dispatching-parallel-agents`.

Every finding exits this step in exactly one state, with the evidence attached:

- **confirmed** — the claim holds against the code and the conventions.
- **refuted** — the claim does not hold, and the evidence says why. Feeds DECLINE.
- **contested** — the claim rests on a preference, a convention this project does not share, or information neither side has. Feeds DECLINE-with-reasoning or NEEDS REVIEWER INPUT.

## Step 4: Escalation Check

Runs on **accepted `[capability]` defects only** — confirmed findings heading for a fix. `[convention]` findings never enter this step: no root-cause pass, no sweep. Proportionality is a requirement, not a mood.

**(a) Origin or symptom.** Is the flagged site where the defect originates, or where it surfaces? Trace backward per `hyperpowers:root-cause-tracing` until you reach the site that creates the bad state. A reviewer points at what they can see; that is frequently not where the fix belongs. Record the answer as `origin` or `symptom — origin at <file>:<line>`.

**(b) Class sweep.** Does the same bug shape exist elsewhere? Grep for the pattern, or dispatch codebase-investigator when the shape is structural rather than textual. This is `hyperpowers:debugging-with-tools` Rule 4 — one fix, many symptoms prevented — applied to a reviewer's finding instead of a bug report. Record `no siblings` or `N sibling sites: <file>:<line>, ...`.

Both results attach to the finding's row in the Step 5 table as evidence. **This step proposes and never acts.** Widening a fix from the flagged line to five sibling sites is a scope decision, and scope decisions belong to the architect at the gate — not to the loop that discovered them.

## Step 5: Batch Disposition Gate

One table, one gate. Every finding in the queue appears exactly once:

```
| Finding | Source | Class / Severity | Evidence | Class sweep | Proposed disposition |
|---------|--------|------------------|----------|-------------|----------------------|
| F1 <one-line claim> | <reviewer>, thread <id> | [capability] / <tier> | confirmed — <evidence> | symptom; 3 sibling sites | FIX NOW (+ class fix) |
| F2 <one-line claim> | <reviewer>, thread <id> | [convention] / <tier> | confirmed — <evidence> | n/a | FIX NOW |
| F3 <one-line claim> | <reviewer>, thread <id> | [capability] / <tier> | refuted — <evidence> | n/a | DECLINE — <reasoning> |
```

Dispositions come from exactly four words, registered in `skills/common-patterns/loop-interfaces.md`. No fifth word is invented here or anywhere else:

- **FIX NOW** — fixed on this branch, in this run.
- **FILE FOLLOW-UP** — real, not now: a fresh bd issue carries it. The source epic is closed by the time an MR draws review, so follow-ups never reopen it.
- **DECLINE** — not doing it, **and the row carries the written reasoning**. Declining a finding the evidence refutes is the correct outcome, and the reasoning is what makes it a professional answer rather than a refusal.
- **NEEDS REVIEWER INPUT** — the disagreement or ambiguity needs the reviewer before anything is decided. Step 7 replies with the question.

Present the table via AskUserQuestion, following `skills/common-patterns/question-format.md` for form and gate discipline: propose a disposition for every row, and let the architect accept the batch or override rows. Findings that are contested, or that carry a Critical severity, may take an individual follow-up question after the batch round — those are the rows where a single wrong default costs the most.

**On timeout.** An expired question box is not an answer. Re-ask in durable prose and HOLD, emitting a Gate-State Block per `skills/common-patterns/loop-interfaces.md`. When a bd epic is identifiable for the branch, persist that block to its notes (`bd update <epic-id> --notes`) even though the epic is closed — a closed epic is still the branch's durable home, and a fresh session reconstructs the gate from bd alone. When no epic is identifiable, the block lives in the session transcript only; say so explicitly at the gate, so the architect knows the state is not recoverable from bd.

## Step 6: Execute (Tiered)

Work only the dispositions the architect approved. Nothing here is pushed or posted — Step 7's gate owns everything outward.

**Tier 1 — lead-fixed at the worktree.** Only the findings the eligibility bar in `skills/common-patterns/pipeline-constants.md` (Peek Fix Carve-out) admits; its suite rule governs here too. Read that section and apply it whole — this skill paraphrases no part of it, because a half-copied bar is how one bar becomes two. Anything the bar excludes takes Tier 2 instead. Verify each edit by reading or grepping the changed site, and dispatch `hyperpowers:test-runner` for the suite evidence the carve-out requires; edits the carve-out demotes land in Tier 2 rather than going out the door. A finding against a comment's claim is fixed by cutting the comment to what is true or deleting it — never by extending it (`skills/common-patterns/prose-style.md`, Comment Policy).

**Tier 2 — confirmed defects, failing test first.** Write the test that reproduces the defect, watch it fail for the right reason, then fix. `hyperpowers:test-driven-development` owns the cycle and `hyperpowers:testing-anti-patterns` owns what the test must not do. A reviewer who found a real defect found a missing test with it.

**Tier 3 — approved class fixes.** Only the sibling sites the architect approved at the gate, each through the Tier 2 path. A class fix with no test at each site is a claim, not a fix.

**FILE FOLLOW-UP.** Fresh bd issues in the standard form (`skills/common-patterns/bd-commands.md`): `bd create "<title>" --type bug|task --description "<one-line summary>" --design "<the finding and its evidence>"`. Class-level work that needs design rather than mechanical repetition routes to `/hyperpowers:brainstorm` instead of becoming a task nobody can execute. bd issues exist for FILE FOLLOW-UP dispositions and for nothing else in this loop — a FIX NOW does not get a tracking issue, and a DECLINE never does.

Run `hyperpowers:verification-before-completion` before any claim that something is fixed. The reply drafted in Step 7 states what changed; that statement must already be evidence.

**Commits.** Additive on the MR branch, one per finding or per coherent fix. The reviewer is the reader: an imperative subject describing the change itself, no class tags, no disposition words, no step or skill names — `skills/common-patterns/prose-style.md`'s human-facing baseline governs. Never amend, squash, rebase, or force-push a branch under review.

## Step 7: Reply Drafts + Outward Gate

**Draft one reply per source thread**, merging the findings that shared it:

- **Fixed** — what changed, in the reviewer's terms, and the commit SHA.
- **Deferred** — what was filed and where, so the reviewer can see it was not dropped.
- **Declined** — the reasoning in plain colleague prose: what was checked, what it showed. Never "we disagree" alone, and never a plugin word in sight.
- **Needs input** — the specific question, asked so a one-line answer can settle it.

Reply prose follows `skills/common-patterns/prose-style.md` (human-facing baseline): lead with the outcome, no praise-padding, no hedging, and no internal vocabulary of any kind — not class tags, not severity words, not disposition words, not the names of these steps. The reviewer never sees this machinery and should never learn it exists.

**Re-check the target state** before anything leaves. Re-read it the way Step 1 did; when Step 1 recorded `unknown` because no forge read was available, the re-check is the gate question named there — the architect confirms the target is still open, and an unanswered question is not a confirmation. If the MR/PR became merged or closed since Step 1, or its state is still unconfirmed, no commits are pushed on any path: every fix that was applied becomes a FILE FOLLOW-UP bd issue instead, the replies drop their commit SHAs, and the gate below covers replies alone.

**The outward gate — one approval covering both.** Show the architect, together, before anything leaves the worktree:

1. The exact reply text for every thread.
2. The full diff of what will be pushed: `git -C <worktree> diff <pre-run-tip>..HEAD`, against the tip recorded in Step 1.
3. The named target — the branch, the remote, and the MR/PR the replies land on.

Nothing outward precedes this gate: no reply posted, no commit pushed, not even the "obvious" one. On approval, push first, then post — a reply naming a SHA the branch does not carry is worse than a late reply:

- Push: `git -C <worktree> push origin HEAD:<branch>`. Never force-push. On a rejected or non-fast-forward push, report git's output verbatim, do not retry by overwriting and do not rebase; hold the SHA-carrying replies and take the architect's call, because those replies are now claims about commits the branch does not have.
- Post: one reply into each source thread, using the **Thread reply** write commands in `skills/common-patterns/forge-detection.md` — never that file's top-level comment form, which opens a conversation the reviewer's thread never sees and which, on GitHub, overwrites the previous reply instead of adding one. Its caveats govern the fallbacks per forge: C10 for the reply forms themselves — a rejected GitLab reply may go out as a top-level comment after all (C2: `note create` first, the legacy form second), while a rejected GitHub reply is handed over as copy-paste per C10, never pushed through the overwriting top-level form. At rung 2 or 3, hand the reply text over as copy-paste instead of posting.

**Thread resolution belongs to the reviewer.** Post the reply into the thread and leave the thread open. Resolving your own threads takes the reviewer's decision away from them and breaks the next run's work queue.

**Wrap-up report.** Two layers per the Audience Contract (`skills/common-patterns/prose-style.md`, The Reader) — one citation, not restated:

```
## Review Response: <MR/PR> — <branch>

[Top layer, at most 6 sentences at architect altitude: what the review changed about the
system, what was declined and on what grounds, what moved to follow-up work, and
anything still open. No file:line, no internal vocabulary.]

### Dispositions
[Evidence layer — the Step 5 table as executed, one row per finding, with commit
SHAs for fixes and issue ids for follow-ups]

### Filed
[bd issues created, with ids; "- (none)" when empty]

### Pending
[Awaiting-reviewer threads carried from Step 1, and threads left open on
NEEDS REVIEWER INPUT; "- (none)" when empty]
```

</the_process>

<critical_rules>
## Rules That Have No Exceptions

1. **No finding is accepted at face value.** Step 3 runs on every finding whose correctness is not self-evident — including findings from a senior reviewer, and including structured findings carrying a peek marker. A claim is a hypothesis until the code says otherwise.
2. **Nothing outward before the Step 7 gate.** No reply posted, no commit pushed, until the architect approves the exact text and the exact diff in one approval.
3. **Accepted `[capability]` defects always get the escalation check.** Origin-or-symptom, then class sweep. Fixing only the flagged line is the whack-a-mole this skill exists to prevent.
4. **`[convention]` findings never escalate.** No root-cause pass, no sweep, no bd issue. Proportionality is a rule here, not a preference.
5. **The escalation check proposes; the architect decides scope.** Sweep results are evidence in the Step 5 table. Widening a fix without approval is scope taken, not scope granted.
6. **DECLINE is a first-class outcome and always carries written reasoning.** A refuted finding gets declined with its evidence. Silently complying with a wrong finding damages the code and teaches the reviewer nothing.
7. **bd issues exist only for FILE FOLLOW-UP.** Not for fixes made, not for declines, not for tracking the run.
8. **Resolved threads are settled; reviewer threads are the reviewer's to resolve.** Never re-triage a resolved thread, never resolve one yourself.
9. **Colleague-facing text carries zero plugin vocabulary.** Replies and commit messages name changes, not classes, severities, dispositions, or steps.
10. **Never rewrite the branch under review.** Additive commits only; no amend, squash, rebase, or force-push.

## Common Excuses

All of these mean: **STOP. Follow the process as written.**

- "The reviewer is senior, just do what they said" — seniority raises the prior, it does not replace Step 3. The most expensive findings to accept blindly are the confident ones.
- "They're obviously right, skip the verification" — self-evident findings pass Step 3 in one line. Deciding a finding is obvious *without opening the file* is the face-value failure wearing a different hat.
- "Just fix what they asked, don't go looking for more" — that is the escalation check being skipped by name. A confirmed defect gets the origin question and the sweep; the architect then decides how far the fix travels.
- "The sweep found four more sites, fix them all while I'm here" — the opposite failure. Sweep results are evidence for the gate, not authority to widen the diff.
- "It's a one-word fix, push it and reply now" — the gate does not scale with diff size. A one-word push nobody approved is still an unapproved push.
- "Every finding should get a bd issue for traceability" — ceremony inflation. The MR thread is the trace; issues exist for FILE FOLLOW-UP only.
- "Declining looks combative, just make the change" — a decline with evidence is a professional answer; a silent bad change is a defect with a reviewer's name on it.
- "I disagree, so decline it" — disagreement without evidence is NEEDS REVIEWER INPUT, not DECLINE. DECLINE requires something checked.
- "The review is one comment, this is too much process" — a one-finding run is one row in one table and one gate. The loop scales down; skipping steps is not how.
- "Resolve the threads so the MR looks clean" — resolution is the reviewer's signal, and taking it breaks the next run's queue.
- "The MR is already merged, push the fix anyway" — a merged or closed target takes no pushes. The accepted fixes become follow-up issues.
- "Restate the severity tiers here so the skill reads standalone" — cite `pipeline-constants.md`. Restating a single-sourced definition is how two definitions start disagreeing.
</critical_rules>

<verification_checklist>
Before presenting the wrap-up report:
- [ ] Forge and degradation rung stated; target state recorded; threads read WITH resolution state (Step 1)
- [ ] Work queue = unresolved threads only; awaiting-reviewer threads excluded and carried to the wrap-up; an empty queue ended the run with a short "nothing to triage" report and no gates (Step 1)
- [ ] Every review claim has its own finding record with class and severity assigned (Step 2)
- [ ] Every finding exits Step 3 confirmed, refuted, or contested — with evidence, and none accepted on the reviewer's authority alone
- [ ] Every accepted `[capability]` defect carries an origin-or-symptom answer and a class-sweep result; no `[convention]` finding was escalated (Step 4)
- [ ] One disposition table covered every finding exactly once, each with one of the four registered words; every DECLINE carries written reasoning; gate-state persisted on any timeout (Step 5)
- [ ] Fixes executed in tier: carve-out-eligible fixes verified and suite-checked, confirmed defects test-first, class fixes only across approved sites; bd issues created for FILE FOLLOW-UP only (Step 6)
- [ ] Commit messages and reply drafts carry no internal vocabulary (Step 6, Step 7)
- [ ] Target state re-checked before pushing; nothing pushed to a merged or closed target, or to one whose state was never confirmed (Step 7)
- [ ] One outward gate approved the exact replies, the exact diff, and the target before anything was pushed or posted; threads left for the reviewer to resolve (Step 7)
- [ ] Wrap-up report has both layers, with dispositions, filed issues, and pending threads (Step 7)
</verification_checklist>

<integration>
**This skill calls:**
- `hyperpowers:codebase-investigator` (Step 3 verification, Step 4 class sweep; in parallel per `hyperpowers:dispatching-parallel-agents` at 3+ independent questions)
- `hyperpowers:test-runner` (Step 6, suite evidence for capability-touching edits)
- `hyperpowers:test-driven-development` + `hyperpowers:testing-anti-patterns` (Step 6, Tier 2 and Tier 3 fixes)
- `hyperpowers:root-cause-tracing` and `hyperpowers:debugging-with-tools` (Step 4 escalation doctrine)
- `hyperpowers:verification-before-completion` (Step 6, before any fixed claim)
- `hyperpowers:brainstorming` (Step 6, design-shaped class work)
- general-purpose subagent (Step 1 ingestion valve, above 25 unresolved threads)

**This skill is called by:**
- User, via `/hyperpowers:opt`
- `hyperpowers:using-hyper`'s routing table, when review feedback arrives on the user's own MR/PR
- `hyperpowers:finishing-a-development-branch` — the worktree it keeps after creating an MR is where this loop works when feedback arrives

**Sibling, not overlap:** `hyperpowers:peek` reviews someone else's branch read-only and routes findings to its author. This skill is that author's side: it writes fixes on its own branch and answers the reviewer. Shared forge plumbing lives in `skills/common-patterns/forge-detection.md`, so neither duplicates the other.
</integration>
