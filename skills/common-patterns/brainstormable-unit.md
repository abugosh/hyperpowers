# Brainstormable Unit

Single source of truth for the seed a design session needs to start work
without the author present. The unit is defined once here and rendered
through two transports: a **phase-document service slice** (shared planning
repo, multiservice work) and a **bd leaf epic** (single-repo work). Skills
cite this file; they never restate the section definitions.

## Definition

A brainstormable unit is the smallest self-contained package of intent that
lets a fresh design session — or a colleague who has never spoken to the
author — produce a complete task tree without reopening anything the unit
already settles.

**The cold-session test (acceptance test for every unit):** given only this
unit plus its surrounding overview, a fresh session must know

1. what to build (deliverable and requirements),
2. what is already decided (and why),
3. what is genuinely open for design,
4. where the edges are (what belongs to siblings).

If any of the four requires asking the author, the unit fails the test.

## Sections

Every unit addresses all seven sections. Each maps to a downstream need:

| Section | What it holds | Downstream need it serves |
|---------|---------------|---------------------------|
| Deliverable & Requirements | What ships, and what must be true when it does — specific and testable | Becomes the design session's immutable requirements |
| Contracts | What this unit exposes to and consumes from siblings, with the owning sibling named; aligned to per-service build/release units | Sibling coordination, contract-symmetry checking, interface-first design |
| Dependencies | What must land before this unit starts; what this unit blocks | Sequencing, blocking dependencies, parallel-lane planning |
| Boundaries | What is explicitly a sibling's job, and which sibling owns it | Scope-creep prevention; keeps multi-epic splits clean |
| Settled Decisions | Choices already made, each with its rationale and what was rejected | The don't-re-ask rule: downstream sessions never reopen these |
| Open for Design | Questions the downstream design round is expected to answer | Scopes the question round — anything not listed here is either settled or out of scope |
| Release Framing | How the deliverable reaches production: flags, ordering, lockstep constraints | Release-alignment checking, deploy-order planning |

**Required means addressed, not necessarily long.** A section with nothing
to say states that explicitly ("None") rather than being omitted — absence
must be a statement, not an accident. Transports define how the sections
are rendered; the obligation to address all seven is transport-independent.

## Separability Rule

Requirements inside a unit are written so subsets can be pulled apart
cleanly: one unit may spawn several epics, and each requirement should be
attributable to exactly one of them. A unit that outgrows a single design
session is not trimmed to fit — it becomes the initiative input to
/hyperpowers:preordain, which decomposes it into leaf-sized units
(thresholds: `skills/common-patterns/pipeline-constants.md`).

## Transport 1 — Phase-Document Service Slice

Used for multiservice work planned in a shared planning repo. A phase
document holds a phase overview plus one slice per service; each slice is
one unit, rendered with the seven sections as plain headings.

**Colleague-facing constraint:** the document must read as a normal
engineering planning doc. Machine legibility comes from consistent
structure only — no tool names, no plugin vocabulary, no markup beyond
ordinary markdown. Colleagues who have never heard of this plugin are
first-class readers.

Copyable template: `skills/portent/phase-doc-template.md`.

## Transport 2 — bd Leaf Epic

Used for single-repo work. The unit renders into the epic's design field:

| Unit section | bd epic design section |
|--------------|------------------------|
| Deliverable & Requirements | `## Requirements (IMMUTABLE)` |
| Boundaries | `## Boundaries` |
| Dependencies | `## Dependencies` (plus `bd dep add` for blocking links) |
| Settled Decisions | `## Settled Decisions` |
| Open for Design | `## Open for Design` |
| Contracts, Release Framing | Fold into `## Context for Brainstorming` when the epic is single-service; keep as their own headings when the epic touches cross-service contracts |

Creation scaffold: `skills/preordain/SKILL.md` (leaf-epic creation).

## Schema Evolution (additive-only)

These documents outlive plugin versions and are read by people who do not
track them; epics cite them by file and commit SHA. Therefore:

1. The seven sections above are the only permanently required sections.
2. New sections may be added later and are **always optional** — for every
   document, forever.
3. Existing section names and meanings are frozen. Renaming or removal
   happens only by deprecation: the old name stays valid, is marked
   deprecated here, and conformance checks report it as informational.
4. A conformance check never fails a document for missing a section added
   after the document was written; such gaps are informational flags only.
5. A genuinely breaking change is a successor schema — a new file, proposed
   to the user — never an in-place edit of this one.

Changelog: v1 (2026-07-06) — initial seven sections.
