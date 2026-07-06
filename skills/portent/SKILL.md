---
name: portent
description: Use when drafting or checking phase planning documents in a planning repo — structures roadmap thinking into conforming phase docs and checks slices for schema conformance, cold-session readiness, contract symmetry, and release alignment
---

<skill_overview>
Thin authoring skill for phase planning documents in a shared planning repo.
Two verbs: **draft** structures roadmap thinking into a phase doc that
conforms to the brainstormable-unit schema; **check** audits an existing
phase doc slice by slice. Signals only — it flags gaps and proposes edits;
the user decides. The documents it produces are read by colleagues who have
never heard of this plugin.
</skill_overview>

<rigidity_level>
MIXED — Draft is high freedom on content (the user's roadmap thinking leads)
but rigid on structure (every slice addresses all seven sections of
`skills/common-patterns/brainstormable-unit.md`). Check is a rigid
checklist: run all four checks on every slice, every time.
</rigidity_level>

<quick_reference>
| Verb | Input | Output |
|------|-------|--------|
| draft | Roadmap thinking: conversation, rough notes, an outline | A phase doc conforming to the template, gaps flagged |
| check | Path to an existing phase doc | Per-slice findings report (GAP / ASYMMETRY / INFO), each with a proposed edit |

**Invocation patterns:**
- `/hyperpowers:portent draft [topic or notes path]` — structure a phase doc
- `/hyperpowers:portent check <path to phase doc>` — audit an existing doc
- `/hyperpowers:portent` (no verb) — ask which verb via AskUserQuestion

**Key files:**
- Schema (what a slice must contain): `skills/common-patterns/brainstormable-unit.md`
- Template (what a finished doc looks like): `skills/portent/phase-doc-template.md`
</quick_reference>

<when_to_use>
- A planning-repo session structuring the next phase of a multiservice
  initiative into per-service slices
- Reviewing a phase doc before sharing it with colleagues or handing slices
  to per-service design sessions
- Converting rough roadmap notes into a doc that downstream sessions can
  design from without the author present

**Don't use for:**
- Single-repo work — the unit's bd-epic transport covers it via
  /hyperpowers:preordain and /hyperpowers:brainstorm
- Designing or implementing inside a service repo — this skill never writes
  service repos
- Decomposing an oversized slice — that is /hyperpowers:preordain with the
  slice as its initiative input
</when_to_use>

<the_process>

**Announce:** "I'm using the portent skill."

Parse the argument: first word is the verb (`draft` or `check`), the rest is
the topic or document path. No verb given → ask which one via
AskUserQuestion. Before either verb, read both key files —
`skills/common-patterns/brainstormable-unit.md` and
`skills/portent/phase-doc-template.md` — so structure comes from the current
schema, not from memory.

---

## Verb: draft

### Step 1 — Gather

Collect the raw material: the conversation so far, notes files the user
points at, prior phase docs in the repo. Establish:

- What is the phase goal, in one or two sentences?
- Which services take a slice in this phase?
- What did earlier phases establish?

Ask via AskUserQuestion **only for genuine unknowns** — never re-ask
anything the source material already settles. If the user's notes name the
services and the goal, start writing.

### Step 2 — Structure into the template

Write the phase doc following `skills/portent/phase-doc-template.md`:
overview first, then one slice per service, every slice addressing all
seven sections.

**Rules while writing:**
- Unknowns land in **Open for Design** — never invented as settled
  decisions. If the source material doesn't say why a choice was made, it
  is not settled; it is open or it needs the user.
- Every settled decision carries its rationale. A decision without a "why"
  gets flagged back to the user, not padded with a plausible one.
- Contracts name the owning sibling. If ownership is unclear, that is
  itself an Open for Design entry.
- Write in the team's voice. The output contains zero plugin vocabulary —
  colleagues must read it as a doc their teammate wrote.
- A section with nothing to say gets "None", not deletion.

### Step 3 — Self-check

Run the full check protocol (below) against your own draft before handing
it over. Fix conformance issues; leave genuine content gaps flagged.

### Step 4 — Hand off

Present the draft with remaining gaps listed explicitly: what needs the
user's knowledge, which slices are thin, which contracts lack owners. The
user edits, fills, and commits — the doc is theirs.

---

## Verb: check

Read the target doc, identify its slices, then run four checks per slice.
Report findings; change nothing unless the user asks.

### Check A — Schema conformance

Every slice addresses all seven sections of
`skills/common-patterns/brainstormable-unit.md`. A missing section is a
**GAP**. A section present but empty (no content and no "None") is a
**GAP**. Sections added to the schema after the doc was written are
**INFO**, never failures — see the schema's evolution rules.

### Check B — Cold-session test

Could a fresh design session produce a task tree from this slice plus the
overview alone? Concrete probes:

- Are the requirements specific enough to verify, or aspirational prose?
- Does every settled decision carry a rationale?
- Does every contract name its owning sibling?
- Are the Open for Design questions answerable by the implementing team,
  or do they secretly require the author?

Each probe failure is a **GAP** citing the slice and section.

### Check C — Contract symmetry

Across all slices in the doc:

- Every **Consumes** entry has a sibling slice (or named external system)
  exposing it — a consumer with no producer is an **ASYMMETRY**.
- Every **Exposes** entry names at least one consumer — an interface nobody
  consumes is an **INFO** (possibly future-proofing, possibly dead weight).
- Ownership matches: if slice A says the contract is owned by service B,
  slice B's sections must agree. Mismatch is an **ASYMMETRY**.
- Contracts align with deployable units: a contract attributed to a service
  that releases as several units must name which unit owns it.

### Check D — Release alignment

- Release framing is consistent with the dependency ordering — a slice that
  deploys "independently" while another slice blocks on it is a
  contradiction (**ASYMMETRY**).
- Lockstep deploys are named on **both** sides: if slice A ships in
  lockstep with service B, slice B's Release Framing must say so too.
- The overview's cross-service ordering agrees with the per-slice
  Dependencies sections.

### Report format

Every GAP and ASYMMETRY proposes a concrete edit; INFO findings are
observational and propose none.

```
Phase doc check: [path]

## [service-a]
- GAP (Settled Decisions): decision "[X]" has no rationale.
  Proposed edit: [concrete text or question for the author]
- INFO (Contracts): exposes [Y] with no named consumer.

## [service-b]
- ASYMMETRY (Contracts): consumes [Z] from service-a, but service-a's
  slice does not expose it. Proposed edit: [add to service-a's Exposes /
  correct the owner]

## Cross-slice
- ASYMMETRY (Release Framing): [service-a] claims lockstep with
  [service-b]; [service-b] says independently deployable. Proposed edit:
  [align both slices — name the lockstep constraint in service-b's Release
  Framing too, or drop it from service-a's]

[N] gaps, [M] asymmetries, [K] informational. The doc is yours — these are
signals, not verdicts.
```

</the_process>

<critical_rules>

## Rules That Have No Exceptions

1. **Signals only** — flag and propose; never decide, never silently
   rewrite. Check changes nothing without an explicit ask.
2. **Never write service repos** — this skill's outputs live in the
   planning repo only.
3. **No task-tracker artifacts** — the document is the output; downstream
   sessions create their own tracked work from it.
4. **Never invent settled decisions** — an unknown goes to Open for Design
   or back to the user; a fabricated rationale poisons every downstream
   session that trusts it.
5. **Zero plugin vocabulary in generated docs** — colleagues are
   first-class readers; the doc must read as their teammate's writing.
6. **Schema evolution is additive-only** — never rename, drop, or reweight
   sections while drafting; the schema changes only via
   `skills/common-patterns/brainstormable-unit.md` and its evolution rules.
7. **Read the schema and template fresh each run** — structure comes from
   the current files, not from memory of them.
8. **AskUserQuestion for questions** — never print questions and wait.

## Common Excuses

All of these mean: **STOP. Reread the critical rules.**

- "The author obviously meant X, I'll record it as settled" → violates rule
  4; unknowns go to Open for Design
- "I'll fix the asymmetry directly since it's clearly a typo" → violates
  rule 1; propose the edit, the user applies it
- "A quick note about which sessions consume this will help" → violates
  rule 5; colleagues read this doc
- "I remember the seven sections, no need to reread the schema" → violates
  rule 7; the schema evolves additively and memory goes stale
- "This slice is small, the full check is overkill" → check is rigid; four
  checks per slice, every time

</critical_rules>

<verification_checklist>
Before claiming a portent run complete:

- [ ] Read schema and template files this run (not from memory)
- [ ] Draft: every slice addresses all seven sections ("None" where empty)
- [ ] Draft: no invented rationales; unknowns in Open for Design
- [ ] Draft: self-check ran before handoff; remaining gaps listed
- [ ] Check: all four checks ran on every slice
- [ ] Check: every finding cites slice + section; every GAP and ASYMMETRY proposes an edit
- [ ] Output docs contain zero plugin vocabulary
- [ ] No writes outside the planning repo; no tracker artifacts created
</verification_checklist>

<integration>
**Schema:** `skills/common-patterns/brainstormable-unit.md` — defines the
unit this skill renders and audits. **Template:**
`skills/portent/phase-doc-template.md` — the copyable document shape.

**Downstream:** a phase-doc slice is the input a per-service design session
brainstorms from (the unit's other transport — the bd leaf epic — is
created by /hyperpowers:preordain in service repos). An oversized slice
routes to /hyperpowers:preordain with the slice as its initiative input.

**Interim role:** the check verb front-loads contract coherence at writing
time while the cross-service base-view review remains deferred.

**Never auto-invokes anything.** Portent produces and audits documents; the
user carries them across repos and sessions.
</integration>
