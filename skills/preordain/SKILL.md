---
name: preordain
description: Decomposes large initiatives into leaf epics with dependencies; handles initiative-level architecture analysis; routes each leaf epic to brainstorming
---

<skill_overview>
Decomposes large initiatives that exceed a single leaf epic's capacity into independently brainstormable leaf epics with explicit dependencies. Architecture analysis happens here — not in per-leaf-epic brainstorming.
</skill_overview>

<rigidity_level>
HIGH FREEDOM — Socratic questioning within steps adapts to context. The 6-step order is fixed. Cybernetic rule is rigid: user confirms decomposition before epics are created.
</rigidity_level>

<quick_reference>
| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | Understand the initiative (AskUserQuestion) | Clear scope, problem, and constraints |
| 2 | Research codebase and external patterns | Decomposition informed by reality |
| 3 | Decompose into leaf epics | Proposed epic list with boundaries |
| 4 | Architecture Impact Check at initiative level | /intuition offered if any YES |
| 5 | Create leaf epics in bd with dependencies | bd epics with requirements and ordering |
| 6 | Handoff to brainstorming | User routes each leaf epic to /brainstorm |

**Invocation patterns:**
- `/hyperpowers:preordain` — user arrives with a large initiative
- `/hyperpowers:preordain` — brainstorming sizing gate escalation (prior work becomes context for Step 1)
</quick_reference>

<when_to_use>
- Initiative exceeds the sizing gate (thresholds defined in `skills/common-patterns/pipeline-constants.md`)
- Brainstorming sizing gate triggered and user chose to escalate
- An oversized phase-doc slice arrives as the initiative input (separability rule in `skills/common-patterns/brainstormable-unit.md`)
- Multiple independent deliverables that could ship in separate epics
- Initiative spans multiple teams or codebases that need coordination boundaries defined

**Don't use for:**
- Single leaf epic worth of work — use /hyperpowers:brainstorm directly
- Executing existing epics — use /hyperpowers:execute-plan
- Bug fixing — use /hyperpowers:fixing-bugs
- Architecture-only analysis with no build decision — use /hyperpowers:intuition
</when_to_use>

<the_process>

**Announce:** "I'm using the preordain skill."

---

## Step 1 — Understand the Initiative

Ask focused questions to understand what the user wants to build and why. Use the AskUserQuestion tool — do not print questions and wait.

**If escalated from brainstorming sizing gate:** Receive the prior work as context. Acknowledge what brainstorming already established — do not re-ask answered questions. Open with: "You escalated from brainstorming with [prior context]. Let me ask about the parts that weren't yet explored."

**If invoked fresh:** Open with questions covering:
- What is the core problem or opportunity?
- What does "done" look like at the initiative level?
- Which parts of the codebase or system are involved?
- Are there ordering constraints — work that must ship before other work can start?
- What's the timeline or priority?

**Question format:** follow `skills/common-patterns/question-format.md` (AskUserQuestion-native; at most 4 per round; recommended option first with evidence; one critical/blocking question at a time). Stop when the initiative scope and success condition are clear. Record each answer in a "Key Decisions Made" running log.

---

## Step 2 — Research

**Research before decomposing.** Never propose a decomposition before understanding the current state of the codebase.

**When to dispatch which agent:**
- Initiative involves existing codebase components → dispatch `hyperpowers:codebase-investigator`
- Initiative involves new integrations or external APIs → dispatch `hyperpowers:internet-researcher`
- Both apply → dispatch both

**Capture findings:**
- Existing components that will be affected and how
- Integration points between would-be leaf epics
- Constraints (shared models, shared interfaces) that affect decomposition boundaries
- Dead-end paths explored and why they were abandoned

---

## Step 3 — Decompose into Leaf Epics

Propose a decomposition into leaf epics. Present it to the user and ask for confirmation before creating anything in bd.

**Each proposed leaf epic must:**
- Be independently brainstormable — has its own clear requirements without needing concurrent work in another epic
- Be independently executable — no shared in-flight state with other leaf epics
- Target the leaf-epic size defined in `skills/common-patterns/pipeline-constants.md` (so it stays below brainstorming's sizing gate)
- Have clear boundaries — what is in scope, what belongs to adjacent epics

**Proposal format:**
```
Proposed decomposition into [N] leaf epics:

1. [Epic Name] — [1-sentence description]
   Scope: [what's included]
   Boundary: [what's excluded, belongs to another epic]
   Depends on: [none | Epic N first]

2. [Epic Name] — [1-sentence description]
   Scope: [what's included]
   Boundary: [what's excluded]
   Depends on: [Epic 1 first]

...

Ordering: [Epic 1] → [Epic 2] → [Epic 3 and 4 can run in parallel] → [Epic 5]

Does this decomposition look right, or should any scopes shift?
```

**Iterate with the user until the decomposition is agreed upon.**

**Edge cases to handle in the proposal:**

*Initiative is actually small enough for a single epic:*
> "This initiative fits in a single leaf epic (~[N] tasks across [M] components). Rather than decompose, routing to /brainstorm is the right call. Want to do that instead?"

*Leaf epic that would still exceed sizing gate:*
Continue decomposing until every proposed leaf epic would pass the brainstorming sizing gate (thresholds defined in `skills/common-patterns/pipeline-constants.md`). Never create a leaf epic that requires preordain decomposition again.

*Initiative spans multiple codebases or repos:*
> "This initiative spans [repo A] and [repo B]. The preordain covers single-repo work. Cross-repo coordination (API contracts, deployment ordering) is out of scope — document the handoff point between repos and manage cross-repo coordination manually."

---

## Step 4 — Architecture Impact Check at Initiative Level

After decomposition is agreed, run the Architecture Impact Check against the entire initiative (not per leaf epic). The 5 questions, recording rule, and routing live in `skills/common-patterns/architecture-impact-check.md` — do not restate them.

Suggested phrasing when 1+ YES:
*"This initiative touches [components] in ways that suggest structural changes. /intuition can examine the architecture for tensions before you commit leaf epics. If you'd like to run it, pass prose focus — e.g., 'examine the [A]/[B] boundary under the [initiative] initiative'. Continue with decomposition, or run /intuition first?"*

---

## Step 5 — Create Leaf Epics in bd

After user confirms the decomposition (and any /intuition run), create each leaf epic in bd.

**Each leaf epic renders the brainstormable unit** — the seed a design
session needs to run without the author present. Section definitions live
in `skills/common-patterns/brainstormable-unit.md` (Transport 2 — bd leaf
epic); do not restate or reinterpret them here. Every section is addressed:
"None" is a statement, omission is an accident.

**Creation command:**
```bash
bd create "[Initiative]: [Leaf Epic Name]" \
  --type epic \
  --priority [match initiative] \
  --description "[One-line summary for bd list views]" \
  --design "$(cat <<'EOF'
## Requirements (IMMUTABLE)
[What this leaf epic must achieve — specific, testable]
- Requirement 1: [concrete requirement]
- Requirement 2: [concrete requirement]

## Boundaries
**In scope:**
- [explicit inclusions]

**Out of scope:**
- [explicit exclusions — what belongs to adjacent epics]

## Dependencies
Depends on: [none | [Epic Name] (bd-[id]) must complete first because [reason]]

## Provenance
[Source: <planning-repo file> @ <commit SHA>, ingested <date> — or "<path> + <date>, unversioned" for untracked input — or "None because the initiative arrived as direct user input with no governing plan document"]

## Settled Decisions
[Choices already made during preordain, each with rationale and what was
rejected — the brainstorm session never reopens these. "None" if nothing
is settled beyond the requirements.]

## Open for Design
[Questions this epic's brainstorm round is expected to answer. "None"
means the design is fully settled.]

## Context for Brainstorming
[Background the brainstorm session will need — existing components,
constraints, integration points. Fold contracts and release framing in
here when the epic is single-service; give them their own headings when
the epic touches cross-service contracts.]
EOF
)"
```

**After creating all epics, set blocking dependencies:**
```bash
# Epic B cannot start until Epic A is complete
bd dep add bd-[epic-B] bd-[epic-A]
```

---

## Step 6 — Handoff to Brainstorming

Present the handoff to the user:

```
[N] leaf epics created:
- bd-[id]: [Epic 1 Name]
- bd-[id]: [Epic 2 Name] (blocked by bd-[Epic 1 id])
...

Each leaf epic is ready for a brainstorm session. Suggested order follows dependencies:
1. /hyperpowers:brainstorm for [Epic 1] (no blockers)
2. /hyperpowers:brainstorm for [Epic 2] (after Epic 1 ships)
...

You can brainstorm and execute epics sequentially, or run parallel brainstorm sessions
for epics with no blocking dependencies. All leaf epics contribute to a single branch/MR
if that's the delivery model.

Ready to start with [Epic 1]?
```

The user drives which epic to brainstorm first. Do not auto-invoke /brainstorm.

</the_process>

<critical_rules>

## Rules That Have No Exceptions

1. **Use AskUserQuestion for all clarifying questions** — never print questions and wait
2. **Research before decomposing** — dispatch codebase-investigator or internet-researcher before proposing any leaf epic boundaries
3. **User confirms decomposition before creating epics** — present the decomposition proposal, get explicit confirmation, then run `bd create`
4. **Preordain creates epics, not tasks** — brainstorming creates tasks; preordain's only bd artifact is leaf epics
5. **No leaf epic that re-triggers the sizing gate** — each leaf epic must target the leaf-epic size in `skills/common-patterns/pipeline-constants.md`; if larger, decompose further
6. **No circular dependencies between leaf epics** — dependencies must be sequential (DAG only)
7. **Architecture analysis at initiative level, not per-leaf-epic** — offer /intuition once for the full initiative; individual leaf epics run their own Step 4 during brainstorming only if new friction appears
8. **Cybernetic: recommend, do not decide** — if the decomposition has ambiguous boundary choices, present options with tradeoffs and let the user decide

## Common Excuses

All of these mean: **STOP. Reread the critical rules.**

- "I already understand the codebase well enough to skip research" → violates rule 2; dispatch agents
- "I'll create the epics now and adjust boundaries during brainstorming" → violates rule 3; confirm first
- "I'll create tasks for the first epic since we know what it needs" → violates rule 4; preordain creates epics only
- "This leaf epic is big but brainstorming can handle it" → violates rule 5; decompose further
- "Epic B can start while Epic A is finishing" → violates rule 6 if it creates a circular dependency; check the DAG
- "Each brainstorm session will do its own architecture check" → violates rule 7; architecture impact check happens here at initiative level

</critical_rules>

<verification_checklist>
Before claiming preordain session is complete:

- [ ] Used AskUserQuestion for all questions (not printed)
- [ ] Dispatched research agents before proposing decomposition
- [ ] Presented decomposition to user and received explicit confirmation
- [ ] Architecture Impact Check recorded (YES/NO for all 5 questions)
- [ ] /intuition offered if any YES (and routing decision recorded)
- [ ] All leaf epics created in bd rendering the brainstormable unit (Requirements, Boundaries, Dependencies, Settled Decisions, Open for Design, Context for Brainstorming)
- [ ] Blocking dependencies set in bd for epics with ordering constraints
- [ ] Handoff presented to user with suggested brainstorm order
- [ ] No tasks created (only epics)
- [ ] No circular dependencies in the dependency graph
</verification_checklist>

<integration>
**Called from:**
- Direct user invocation (`/hyperpowers:preordain`)
- Brainstorming sizing gate — evaluated at Step 1 exit, re-checked at Step 6a ("continue here, or escalate to /preordain?")

**Calls (never auto-invokes, always offers):**
- `/hyperpowers:intuition` — offered at Step 4 if Architecture Impact Check has any YES
- `/hyperpowers:brainstorm` — offered at Step 6 handoff; user decides when and which epic to start

**Produces:**
- Leaf epics in bd, each conforming to the brainstormable unit's bd transport (`skills/common-patterns/brainstormable-unit.md`) and independently brainstormable
- Blocking dependencies between epics in bd
- Architecture Impact Check recorded in session output

**Does NOT produce:**
- bd tasks (brainstorming creates tasks)
- Implementation plans (task specs are created by brainstorming; writing-plans only repairs specs off-mainline)
- Code or implementation artifacts

**Relationship to brainstorming:**
- Preordain creates epics with requirements and boundaries
- Brainstorming takes each leaf epic and creates the full task tree
- When called from brainstorming sizing gate: prior brainstorming work becomes Step 1 context; preordain does not re-ask answered questions
</integration>
