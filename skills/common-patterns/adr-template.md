# ADR Template (Architecture Decision Records)

ADRs capture architecturally significant decisions using the Nygard format. They are permanent artifacts stored in the repository at `doc/arch/adr-NNN.md`.

## Format

```markdown
# ADR-NNN: [Decision Title]

## Status
[proposed | accepted | deprecated | superseded by ADR-NNN]

## Context
[Forces that led to this decision. Neutral language -- describe the situation
and pressures, not the solution. What constraints exist? What tradeoffs are at play?]

## Decision
We will [active voice, full sentences describing the structural choice].

## Consequences
- [Positive consequence -- what this enables]
- [Negative consequence -- what tradeoff we accept]
- [What this constrains or enables for future work]
```

## Status Values

- **proposed** -- Decision under discussion, not yet committed
- **accepted** -- Decision committed and active
- **deprecated** -- Decision no longer applies (system evolved past it)
- **superseded by ADR-NNN** -- Replaced by a newer decision (this ADR remains for historical context)

## File Naming

- Location: `doc/arch/adr-NNN.md`
- Number sequentially: `adr-001.md`, `adr-002.md`, `adr-003.md`
- Never reuse numbers, even for superseded ADRs
- Superseded ADRs remain in the repository for historical context

## Key Principles

- **Consequences flow forward:** Consequences of one ADR become Context for subsequent ADRs
- **Neutral context:** Context section describes forces and pressures, not the solution
- **Active voice decisions:** "We will..." not "It was decided..."
- **Both sides of tradeoffs:** Always state what you gain AND what you give up
- **Permanent intent:** ADRs outlive the architecture model. The model describes current reality; ADRs capture why structural decisions were made.

## Example ADRs

### Example 1: Boundary Decision (from empirical observation)

```markdown
# ADR-001: Isolate payment processing as independent component

## Status
Accepted

## Context
The order processing system faces multiple forces of change. Payment provider
requirements change independently from business logic -- adding a new payment
provider (Stripe, PayPal, crypto) should not require changes to pricing rules
or fulfillment logic. Git history shows payment-related changes occur at a
different rate than order processing logic (payment: 12 commits/month vs
order logic: 3 commits/month). Currently, payment code is interspersed
throughout the order processing module, causing unnecessary coupling.

## Decision
We will extract payment processing into a dedicated Payment Gateway component
with a stable interface that abstracts provider-specific details. The Order
Orchestrator will interact with payments only through this interface.

## Consequences
- Payment provider changes (adding providers, changing APIs) are isolated to one component
- Order processing logic never needs to know which payment provider is in use
- Adds one interface boundary to maintain (Payment Gateway contract)
- Future payment features (refunds, partial payments) have a clear home
- Testing payment logic in isolation becomes straightforward
- Future audits should verify the rate-of-change difference persists (if it converges, revisit this boundary)
```

### Example 2: Tension Resolution

```markdown
# ADR-002: Merge Content Engine and Routing Engine into Notification Engine

## Status
Accepted

## Context
Architectural audit found that Content Engine and Routing Engine change at the
same rate: every new notification type requires changes to both components
simultaneously. The original boundary (ADR-001 context) assumed content
rendering and channel routing would change independently. Six months of git
history showed this assumption was wrong -- notification type is the true
shearing layer boundary, encompassing both what to say and how to deliver it.

## Decision
We will merge Content Engine and Routing Engine into a single Notification Engine
that encapsulates all notification type changes, including content rendering,
personalization, and channel selection.

## Consequences
- Eliminates the false boundary between content and routing
- Reduces interface count from two engine interfaces to one
- Notification Engine is larger but changes for a single reason (notification type)
- Simplifies the Notification Orchestrator (one engine call instead of two)
- Future audit should verify Email Accessor and Push Accessor remain truly independent
- If notification types later diverge (content changes independently from routing), this decision should be revisited (supersede this ADR)
```

### Example 3: Tension Acceptance

```markdown
# ADR-003: Accept coupling between Catalog Accessor and Search Accessor

## Status
Accepted

## Context
Architectural audit identified that Catalog Accessor and Search Accessor share
some data structures -- product schema changes require updates to both components.
Merging them would eliminate the coupling but would combine two different
infrastructure concerns (relational database access and search index access)
into one component, combining things that change for different reasons.

The coupling is structural (shared schema) not behavioral (they don't call each
other). Schema changes are infrequent (quarterly at most).

## Decision
We accept the coupling between Catalog Accessor and Search Accessor. Both
components will reference a shared product schema definition, and schema changes
will require coordinated updates to both.

## Consequences
- Catalog and Search remain separate components with independent rates of change
  (database technology vs search technology)
- Schema changes require coordinated updates (accepted cost)
- The shared schema definition becomes a de facto interface contract between them
- Revisit if schema changes become frequent (monthly or more) -- at that point,
  merging may reduce friction more than separation provides isolation
```
