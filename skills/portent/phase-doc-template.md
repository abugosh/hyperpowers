# Phase [N] — [Phase Name]

## Overview

**Goal:** [What this phase delivers for the initiative, in one or two
sentences.]

**Context:** [What earlier phases established that this phase builds on.
"First phase" is a valid answer.]

**Services in this phase:** [service-a], [service-b], ...

**Cross-service ordering:** [Which slices must land before which, and why.
"None — slices are independent" is a valid answer.]

Every section below is filled in for every service. Where a section has
nothing to say, write "None" — an empty section left out reads as an
oversight; "None" reads as a decision.

---

## [service-a]

### Deliverable & Requirements

[What this service ships in this phase, in one or two sentences.]

Must hold when done:

- [Requirement — specific enough that a reviewer can check it.]
- [Requirement.]

### Contracts

Exposes:

- [Interface, endpoint, event, or artifact] — consumed by [service-b].
  [One line on shape, version, or where the definition lives.]

Consumes:

- [Interface] — owned by [service-c]. [Status: already exists, or lands in
  this phase via that service's slice.]

[If this service releases as more than one deployable unit, name which unit
owns each contract.]

### Dependencies

Depends on: [The slice or system that must land first, or "None".]

Blocks: [Slices waiting on this one, or "None".]

### Boundaries

Not this service's job in this phase:

- [Adjacent work someone might assume belongs here, and which service
  actually owns it.]

### Settled Decisions

- [Decision] — [why it was made, and what was considered and rejected.]
- ["None" if nothing is settled beyond the requirements above.]

### Open for Design

- [Question the implementing team is expected to answer during their own
  design work.]
- ["None" means the design is fully settled and this slice is
  implementation only.]

### Release Framing

[How this ships: behind a feature flag, dark-launched, in lockstep with a
named service's deploy, or after a named migration. "Independently
deployable" if there are no constraints.]

---

## [service-b]

[Repeat the same seven sections for each remaining service in the phase.]
