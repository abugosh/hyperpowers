# Architecture Impact Check

Single source of truth for the 5 structural questions, asked in two tenses:
design-time (before building) and post-build (after building or when
re-verifying). All callers reference this file — never restate the
questions.

**Design-time:** brainstorming (designed solution) and preordain (entire
initiative) — ask before committing, routing to an /intuition offer.

**Post-build:** executing-plans completion (work just implemented) and
review-implementation re-verification (prior implementation) — ask after
implementation, routing to a ponder UPDATE dispatch.

## The 5 Questions

| # | Design-time phrasing | Post-build phrasing |
|---|---|---|
| 1 | Creates a new component/module? | Did this work create a new component or remove an existing one? |
| 2 | Changes the public interface of an existing component? | Did this work change a component's public interface? |
| 3 | Adds or removes a cross-component dependency? | Did this work add or remove a dependency between components? |
| 4 | Creates a new request path through 2 or more components? | Did this work create a new request path through 2+ components? |
| 5 | Moves responsibility from one component to another? | Did this work move responsibility from one component to another? |

## Recording

Record YES/NO for each in the epic's Architecture Impact section (brainstorm),
or — for preordain's initiative-level check — in each leaf epic's Context for Brainstorming section
(identical across the initiative's epics, so it is reconstructable from bd alone).

## Design-Time Routing

- 0 YES → proceed.
- 1+ YES → offer /intuition before committing. Pass prose focus naming the
  affected components so evidence gathering is targeted. The architect
  decides; record the routing decision.

This is a routing mechanism, not a gate — the architect can always proceed.
If the audit function was already served recently (e.g., a completed findings
review covering the same ground), say so in the offer rather than pushing a
duplicate run.

## Post-Build Routing

Ask the post-build phrasing against the work just completed.

- **All NO** → architecture model is unaffected. Skip ponder dispatch.
- **Any YES** → check whether a model exists: `ls docs/arch/*.c4 2>/dev/null`
  - **Model exists** → dispatch `/ponder` in UPDATE mode with structured
    input:

    ```
    Mode: UPDATE

    What changed:
    - [for each YES: interface change / dependency added or removed /
      component added or removed / responsibility shift / new request path]

    Components affected:
    - [component name]: [what specifically changed]

    Context:
    - [epic-id or task-id] — [why this change was made]
    ```

    The ponder agent edits the .c4 files, spot-checks, validates, and
    returns a summary.
  - **No model exists** → note the architectural changes in the completion
    report instead:

    ```
    ### Architecture Changes Noted (No Model)

    The following architectural changes occurred but no architecture model
    exists to update:
    - [list changes from questions answered yes]

    Consider running /ponder bootstrap or /intuition to create an initial
    architecture model.
    ```

    Never dispatch ponder UPDATE when no model exists — update mode requires
    an existing model.
