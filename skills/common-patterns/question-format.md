# Question Format (AskUserQuestion)

Single source of truth for how skills ask the user questions. Settled by the
RW3 rework (brainstorm partner mode). Skills reference this file — never
restate a question-format template.

## The Form

Use the AskUserQuestion tool — never print questions and wait for a reply.

- At most 4 questions per round; multiple choice preferred.
- Put your recommended option FIRST, labeled "(Recommended)", with the
  evidence for it in the description.
- Ask one critical/blocking question at a time; group lesser ones.
- Ground questions in evidence gathered first (investigate → share → opine →
  ask); generic interrogation misses hidden constraints.
- Stop once the design space is clear — remaining minor unknowns become Open
  Questions in the epic or record.

## Timeouts and Gates

An expired question box is not an answer: the user may be in another window.
Re-ask in durable prose and hold at the gate patiently — never proceed
through a decision gate on a timeout (signal policy:
`skills/common-patterns/loop-interfaces.md`).
