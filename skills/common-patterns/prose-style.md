# Prose Style

Single source of truth for comment policy, the boy-scout rule, and the
human-facing prose baseline. Skills reference this file — never restate it.

## Comment Policy

A comment earns its place by stating what the code cannot: a constraint, an
invariant, a non-obvious why, a hazard. Anything else is noise — a comment
that narrates the next line, restates what the code already says, summarizes
the change for a reviewer, or justifies the edit. Noise is a review defect:
reviewers flag it as a `[convention]` finding
(`skills/common-patterns/pipeline-constants.md`, Finding Classification).

The policy is semantic, never numeric. There is no comment-count rule, no
ratio, no per-file cap — a file with zero comments can be clean and a file
with ten can be clean; judge each comment against the test above, not a
quota.

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

## Human-Facing Prose Baseline

Applies to anything a human reads: review reports presented to the user,
MR/PR comments, epic summaries, commit message bodies. Consumers: executor,
code-reviewer, reviewer, peek, executing-plans. The baseline governs tone;
the Audience Contract above governs reader and altitude.

- Lead with the finding or outcome. Don't bury it under setup.
- No praise-padding — no "strengths" preambles, no acknowledging-what-
  went-well openers before the substance.
- No hedging vocabulary — no numeric self-scored confidence, no
  "I believe" / "note that" filler.
- Evidence citations (file:line, command output) live in internal reports
  and bd notes. Outward-facing prose states conclusions plainly and leaves
  the trail behind it, not embedded in every sentence.
