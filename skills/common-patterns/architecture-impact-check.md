# Architecture Impact Check

Single source of truth for the 5 structural questions. Brainstorming (Step 4,
asked against the designed solution) and preordain (Step 4, asked against the
entire initiative) reference this file — never restate the questions.

## The 5 Questions

1. Creates a new component/module?
2. Changes the public interface of an existing component?
3. Adds or removes a cross-component dependency?
4. Creates a new request path through 2 or more components?
5. Moves responsibility from one component to another?

## Recording

Record YES/NO for each in the epic's Architecture Impact section (brainstorm)
or the initiative record (preordain).

## Routing

- 0 YES → proceed.
- 1+ YES → offer /intuition before committing. Pass prose focus naming the
  affected components so evidence gathering is targeted. The architect
  decides; record the routing decision.

This is a routing mechanism, not a gate — the architect can always proceed.
If the audit function was already served recently (e.g., a completed findings
review covering the same ground), say so in the offer rather than pushing a
duplicate run.
