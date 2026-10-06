## Behavior Checks and the A/B Method

The process in `SKILL.md` runs a behavior check only when a rule's behavior
is genuinely uncertain after reading, at most once per changed behavior.
This file says what that check looks like for each skill type, what makes
rule text hold up under pressure, and how a guard is removed.

## What a Check Looks Like, by Skill Type

### Discipline-enforcing skills (rules and requirements)

**Examples:** TDD, hyperpowers:verification-before-completion

**Check:** one pressure scenario combining two or three pressures (time,
sunk cost, authority, exhaustion), the agent reading the file from the
working tree. Record its exact words. A pass shows the rule renders the
behavior once under that pressure.

### Technique skills (how-to guides)

**Examples:** hyperpowers:root-cause-tracing, condition-based-waiting

**Check:** one application to a scenario the file does not use as its
example. A gap in the instructions shows as a step the agent had to invent.

### Pattern skills (mental models)

**Examples:** reducing-complexity, information-hiding

**Check:** one recognition case and one counter-example. The agent should
apply the pattern to the first and decline it for the second.

### Reference skills (documentation, APIs)

**Examples:** API documentation, command references

**Check:** one retrieval task. The agent should find the entry and use it
correctly; a wrong flag or a missed section is the finding.

**Every type:** the agent reads the file by path from the working tree, not
through the Skill tool, whose installed copy is stale on a branch. Record
the return verbatim.

## Writing Rule Text That Holds

Discipline skills are read by agents under pressure, and agents find
loopholes. The counters below are authoring guidance; each counter you add
is earned by an observation, not by anticipation.

**Why these work:** see [../persuasion-principles.md](../persuasion-principles.md)
(Cialdini, 2021; Meincke et al., 2025) on authority, commitment, scarcity,
social proof, and unity.

### Close the loophole you saw, explicitly

<Bad>
```markdown
Write code before test? Delete it.
```
</Bad>

<Good>
```markdown
Write code before test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Delete means delete
```
</Good>

Each bullet above was a loophole an agent took in its own words.

### Spirit versus letter

State early: **Violating the letter of the rules is violating the spirit of
the rules.** It closes a class of "I'm following the spirit" readings.

### The rationalization table

One row per excuse an agent has used, with the reality beside it:

```markdown
| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "Instruction was specific so I can skip the workflow" | Specific instructions = WHAT, not HOW. Route through the workflow. |
```

The second row is a counter class an A/B flip proved load-bearing against
lead-tier models (RW6b P8). Use counters your own observations earn.

### Red flags

A short list the agent can match itself against:

```markdown
## Red Flags - STOP and Start Over

- Code before test
- "I already manually tested it"
- "This is different because..."
```

### Description carries the symptom

The `description` names the moment the rule is about to be broken:

```yaml
description: use when implementing any feature or bugfix, before writing implementation code
```

## Re-Baselining and Pruning (A/B Method)

Models improve; counters calibrated to older models must be re-earned, not
assumed. Method (validated by the 2026-07 RW6b campaign, evidence in that
epic's bd notes):

- **Variant A (prune probe):** run the pressure scenario with the HARD RULE
  present but the excuse-table counter ABSENT. A-COMPLIES → the counter is
  dead weight at that tier: prune-candidate. A-VIOLATES → run **Variant B**
  (full text incl. counter): B must flip the verdict to COMPLIES, else the
  counter is dead weight AND the failure is real — write a better one.
- **Tier-scope every verdict.** A counter probed clean on one model tier is
  prunable only for that tier's loading surface; lead-tier (stronger-model)
  guardrails need their own probes. RW6b: 6/6 Sonnet probes complied bare,
  while the same session's Opus probe violated without its counter and
  flipped with it.
- **Verbatim evidence only.** Record the subject's exact words at judgment
  time; paraphrased evidence invites lenient scoring.
- **Mechanism beats prose for long-context failures.** Failure modes observed
  in long, high-inertia sessions (self-review leniency, stale-reference
  following, gate paraphrasing) tend NOT to reproduce in clean short-context
  scenarios — the fix that works is mechanism (transcribed gates, hooks,
  independent review), not more counter prose. Do not add doctrine a clean
  RED cannot motivate.
- **Prunes are edits too:** a prune requires its A-COMPLIES baseline the same
  way an addition requires its observation.

Removing a guard on an agent interface (the executor cluster named in
`docs/arch/adr/adr-003.md`) uses this method against live dispatches at the
guard's model tier; nothing else sanctions that removal.
