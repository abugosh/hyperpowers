---
name: review-implementation
description: On-demand re-verification of an implementation against its bd epic spec — use for a post-gap-fix re-check, auditing an epic that was implemented elsewhere, or a mid-epic sanity check. The mainline gate already runs inside hyperpowers:executing-plans' Completion step; don't invoke this after a normal executing-plans run finishes.
---

<skill_overview>
Re-verify a completed (or partially completed) implementation against its bd epic spec, on demand, outside the mainline executing-plans loop. Dispatches the same reviewer agent the mainline gate uses, then runs the post-build Architecture Impact Check.
</skill_overview>

<rigidity_level>
LOW FREEDOM - Follow the process exactly. Never skip the reviewer dispatch or the architecture check. No approval without the reviewer's evidence.
</rigidity_level>

<when_to_use>
Use for:
- Re-checking an epic after a gap-fix, outside the executing-plans session that found the gap
- Auditing an epic that was implemented elsewhere (not via hyperpowers:executing-plans)
- A mid-epic sanity check before all tasks are closed

**Don't use after normal executing-plans completion** — the reviewer gate already ran there (see `skills/executing-plans/SKILL.md`, Completion section). Re-running this skill in that case duplicates work the mainline loop already did.
</when_to_use>

<the_process>
## Step 1: Dispatch the Reviewer

**Announce:** "I'm using hyperpowers:review-implementation to re-verify <epic-id> against its spec."

```
Agent tool:
  subagent_type: "hyperpowers:reviewer"
  mode: "bypassPermissions"
  prompt: |
    Review the implementation for epic <epic-id>.
    Follow agents/reviewer.md exactly.
    Start with: bd show <epic-id>
```

The reviewer owns the entire review protocol (evidence requirements, quality gates, dead-code audit, test-quality audit, anti-pattern checks) — see `agents/reviewer.md`. Do not restate its process here.

## Step 2: APPROVED

a. Run the post-build Architecture Impact Check against the epic's work, per `skills/common-patterns/architecture-impact-check.md` (Post-Build Routing) — cite that file, never restate the 5 questions. Any YES routes per that file: dispatch `/ponder` UPDATE when a model exists, or note-and-suggest when none exists.

b. Present the reviewer's APPROVED report to the user.

c. **STOP here.** Do not automatically call finishing-a-development-branch. The user decides the next step — closing the epic, further manual validation, or nothing further. Closing removes context the user may still need.

## Step 3: GAPS FOUND

Present the reviewer's gap list to the user as-is — do not summarize away detail.

If a pipeline session (hyperpowers:executing-plans) owns this epic and is still active, hand the gaps to its gap-fix loop (`skills/executing-plans/SKILL.md`, Completion section, GAPS FOUND branch) rather than fixing them here. If no pipeline session owns the epic (this is a standalone re-check), the user decides how to route the fixes — do not auto-dispatch an executor.

**STOP.** Do not proceed to finishing-a-development-branch.
</the_process>

<critical_rules>
## Rules That Have No Exceptions

1. **Always dispatch the reviewer** — never approve from memory or a prior review's cached verdict.
2. **Never restate the reviewer's protocol** — evidence requirements, quality gates, and test-quality audits live in `agents/reviewer.md`.
3. **Never restate the 5 architecture questions** — cite `skills/common-patterns/architecture-impact-check.md`.
4. **If GAPS FOUND → STOP** — don't proceed to finishing-a-development-branch.
5. **If APPROVED → STOP** — don't auto-call finishing-a-development-branch; the user decides.
</critical_rules>

<integration>
**This skill is called by:** the user, via `/hyperpowers:review-implementation` (on demand — no mainline caller).

**This skill calls:**
- `agents/reviewer.md` (blocking subagent, verdict: APPROVED / GAPS FOUND)
- `hyperpowers:ponder` (via the Architecture Impact Check's Post-Build Routing, when applicable)

**Verdict vocabulary:** identical to `skills/common-patterns/loop-interfaces.md` (Verdict Contracts) — `APPROVED` or `GAPS FOUND`, no new words.
</integration>
