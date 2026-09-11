# Prose Style

Single source of truth for comment policy, the boy-scout rule, and the
human-facing prose baseline. Skills reference this file — never restate it.

## Comment Policy

The default is no comment. A comment earns its place by stating what the
code cannot: a constraint, an invariant, a non-obvious why, a hazard.
Anything else is noise — a comment that narrates the next line, restates
what the code already says, summarizes the change for a reviewer, or
justifies the edit. Passing that test is necessary, not sufficient: the
rules below decide what a legitimate comment may contain and how long it may
be. When in doubt, leave it out — a file with zero comments is clean, and
between a defensive paragraph and nothing, nothing wins.

**The code first.** Before writing a comment, make the code say it: a name
that carries the constraint, a CHECK or assertion that enforces it, a test
whose message names it. A comment is what remains when none of those can
hold the fact, and it exists for one reader — the editor who would
otherwise make a specific wrong change. Name that change to yourself; if
you cannot, there is no comment. A hazard the code already makes hard to
break — a test reds, a constraint refuses — needs none. In a function with
good names the usual number of comments is zero. The four categories above
describe what a comment is about, never what earns one; "this is subtle"
earns nothing.

**The reader is the next maintainer, never the reviewer.** A comment is read
by whoever edits that line next, cold, months later. It is never addressed
to whoever is reviewing this change: no argument that the change is right,
no answer to an earlier review round, no record of what an earlier version
of the comment said, and no pre-emption of an objection nobody has raised —
"this is not defensive padding", "do not simplify this back to X", "it is
not theoretical". A comment that anticipates a critic is written for the
critic, and the maintainer pays for it. Text written so the change survives
review is noise even when every sentence of it is true.

**State the hazard; never prove it.** A comment names the constraint and, if
the code cannot show it, the one fact that makes it necessary — one or two
sentences. The proof that the constraint holds is real content with a home
of its own, and that home is never the code:

| Content | Home |
|---|---|
| Which assertions fail if a clause is removed; mutation results | The test's own assertion messages; the task's bd note |
| Why the change was made; the alternatives rejected | The commit message body |
| A fact about another file — its guard, its index predicate, its line numbers | That file. Name the function or constraint if you must; never copy its contents or cite its lines |
| A design decision and its reasoning | An ADR or the epic's bd notes; the comment names it |
| Deferred work and why it waits | The tracker; the code carries the issue id at most |
| What this comment used to say | Git history |

A hazard that needs a paragraph is an ADR with a one-sentence comment
pointing at it, never a paragraph in the code. A spec's Why and Context are
written for the executor; nothing in them is transcribed into comments.

**A wrong comment is cut, never extended.** When review finds a comment's
claim false or overstated, the fix is to delete the comment or trim it to
the sentence that is true. Rewriting it longer so it survives the next round
is the defect growing; the lead-fix path never does it.

**Shape is evidence.** The policy is semantic — no comment count, no ratio,
no per-file cap, and ten good comments are clean. But a comment longer than
the code it annotates, or a file whose comment lines outnumber its code
lines, is presumed to carry misplaced content, and the presumption is
rebutted one comment at a time against the rules above — never by observing
that each comment is "about an invariant". Reviewers name the block and the
table row its content belongs in, and file it as a `[convention]` concern
opening `Contract: comment policy`: the policy is part of every task's
standing scope (`skills/common-patterns/spec-templates.md`), so this is a
contract miss and never a reading-effort claim
(`skills/common-patterns/pipeline-constants.md`, Severity Anchor).

Examples:

```python
# Legit — states an invariant the code can't express on its own
# Retry budget assumes the upstream circuit breaker trips within 3s;
# raise this if that SLA changes.
RETRY_TIMEOUT_S = 3

# Noise — narrates the next line
# Loop over all users
for user in users:
    process(user)

# Noise — justifies the edit instead of the code
# Changed this to a dict for O(1) lookup per code review feedback
cache = {}
```

The same hazard, stated and then proved:

```sql
-- Legit — one sentence, the fact the code can't show
-- A batch is tenant-wide, so batch_id alone would match every
-- account's jobs.
AND prior.account_id = v_account_id

-- Noise — the same clause written for the reviewer. Every sentence is
-- true, and every one has a home that is not this file.
-- THE ACCOUNT SCOPE IS LOAD-BEARING AND IS NOT DEFENSIVE PADDING.
-- chk_batches_shape forces account_id IS NULL on a tenant batch, so
-- every account shares ONE batch_id. Without this clause retiring one
-- account's job would cancel every other account's queued job, silently.
-- Pinned: drop this clause and C1 and C2 red. It is not theoretical —
-- test_requeue.sql already parks two accounts on one shared batch.
-- Tracked as PROJ-123 for the tie case.
AND prior.account_id = v_account_id
```

## Boy-Scout Rule

Within a file a task spec already directs you to edit, removing noise
comments and correcting stale docstrings you encounter there is mandatory
and in-scope — it is not scope drift, and it does not require spec
amendment. Opening a file the spec does not name — for cleanup or any other
reason — remains prohibited; the boy-scout rule extends what you fix inside
an authorized file, never which files are authorized.

## The Reader (Audience Contract)

Every human-facing report is read by the architect-governor — the governor
defined in `skills/common-patterns/loop-interfaces.md` (not restated here).
They own direction, return cold, did not watch the work happen, and think
in components, boundaries, contracts, consequences, and decisions-needed.
They never saw the files the writer read.

**The layering rule.** Every report has two layers. The **top layer**
explains at architect altitude in role-based plain language — what changed
in system terms, what it means, what needs deciding. The **evidence
layer** beneath carries file:line and identifiers — evidence attaches to
claims; it never becomes the narrative spine of the top layer.

**The vocabulary rule.** Internal pipeline vocabulary — lens names, pass
numbers, stage labels, mode words — is banned from the top layer, the same
ban colleague-facing docs already carry (`brainstormable-unit.md`; peek's
draft-comment rule).

**The context rule.** Never presume the reader saw a file or a session;
name things by their role in the system on first mention.

**The anti-pattern.** A vacuous top layer is a defect — "improves
quality"-style virtue prose fails the contract. The top layer states
concrete system changes and consequences. Reviewers flag violations as a
`[convention]` finding.

**The tone rule.** Whether prose may grade at all — the system, not the
work — is settled in the Human-Facing Prose Baseline below; cited here, not
restated.

## Human-Facing Prose Baseline

Applies to anything a human reads: review reports presented to the user,
MR/PR comments, epic summaries, commit message bodies. Consumers: executor,
code-reviewer, reviewer, peek, executing-plans, opt, ponder, intuition,
verification-before-completion, loop-interfaces, spec-templates. The
baseline governs tone; the Audience Contract above governs reader and
altitude.

- Lead with the finding or outcome. Don't bury it under setup.
- Grade the system, never the work or the author. Human-facing prose
  describes what changed and what it means for the system; it never
  evaluates the quality, effort, or diligence of the work, in either
  direction, anywhere in a report — not only as an opener. A grading word
  is rewritten into the concrete evidence behind it or deleted. The verdict
  line is the only grade a report carries; a clean result produces a short
  report, and short is the signal.
  Grading-word list (the minimum a self-check scans for): careful,
  carefully, thoughtful, clean, solid, thorough, well-tested, disciplined,
  high-quality, great care, sloppy, rushed, careless, lazy, right, honest,
  earn, declines, slip, reasonable, defensible, good.
- Sentence counts in report templates are ceilings, never floors. A slot
  that reads "at most N sentences" may be one sentence; nothing is padded
  to reach a length.
- No hedging vocabulary — no numeric self-scored confidence, no
  "I believe" / "note that" filler.
- Evidence citations (file:line, command output) live in internal reports
  and bd notes. Outward-facing prose states conclusions plainly and leaves
  the trail behind it, not embedded in every sentence.
