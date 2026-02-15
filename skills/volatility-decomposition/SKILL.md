---
name: volatility-decomposition
description: "Lowy volatility-based decomposition producing architecture graph in bd with ADRs"
---

<skill_overview>
Guide architects through Lowy's volatility-based decomposition via Socratic dialogue, producing 2-3 alternative component structures encoded as a bd architecture graph, with key decisions captured as ADRs in the repository.
</skill_overview>

<rigidity_level>
HIGH FREEDOM - Socratic questions adapt to domain and system context. Output structure is rigid: always 2-3 alternatives with tradeoffs, always bd graph encoding, always ADRs for key decisions.

The questioning adapts. The deliverable format does not.
</rigidity_level>

<quick_reference>
| Step | Action | Deliverable |
|------|--------|-------------|
| 0 | Context detection | Existing graph or fresh start determined |
| 1 | Socratic questioning (Lowy framework) | Volatility axes and forces identified |
| 2 | Structure proposal (2-3 alternatives) | Alternatives with tradeoff tables |
| 3 | Encode chosen structure in bd | Architecture epic + component nodes |
| 4 | Create ADRs for key decisions | doc/arch/adr-NNN.md files |
| 5 | Handoff guidance | Next steps toward audit and inner loop |

**Key:** Graph = temporary work plan (created, consumed, closed). ADRs = permanent intent.
</quick_reference>

<when_to_use>
- Project inception: system needs its first structural decomposition
- Major inflection point: new capability demands structural rethinking
- Structure fights you: existing boundaries cause repeated friction across features
- Fractal sub-decomposition: a component is too large and needs its own internal structure
- Revision after audit: /audit-arch surfaced tensions that require restructuring

**Don't use for:**
- Inner-loop feature work (use hyperpowers:brainstorming)
- Bug fixes (use hyperpowers:fixing-bugs)
- Refactoring within existing boundaries (use hyperpowers:refactoring-safely)
- Evaluating existing structure (use /audit-arch instead)
- Implementation-level design (classes, functions, data structures)
</when_to_use>

<the_process>

## Step 0 -- Context Detection

**Announce:** "I'm using the volatility-decomposition skill to guide you through structural decomposition."

**Check for existing architecture graph:**

```bash
# Check for existing architecture epic
bd list --label arch --type epic --status open
```

**If found (REVISION MODE):**
```bash
# Load existing graph
bd show <epic-id>
bd list --label arch,component --parent <epic-id>
```
- Read all component nodes, their volatility axes, stability states, and edges
- Summarize current graph state for the architect before proceeding
- Socratic questions will focus on what feels wrong and where restructuring is needed

**If not found (INCEPTION MODE):**
- Starting fresh -- all evidence comes from Socratic dialogue and codebase investigation

**Codebase detection:**
- If codebase exists: dispatch `hyperpowers:codebase-investigator` with prompt:
  ```
  Map the current module/package structure, dependency graph between top-level
  modules, and any existing architectural boundaries. Stay at module level, not
  class/function level. Report: top-level modules, which modules depend on which,
  any obvious layering patterns, and areas where module boundaries seem unclear
  or violated.
  ```
- If no codebase (greenfield): pure design mode -- all evidence comes from Socratic dialogue

**Check for existing ADRs:**
```bash
ls doc/arch/adr-*.md 2>/dev/null
```
- If ADRs exist: read them to understand prior architectural decisions
- These constrain or inform the decomposition

---

## Step 1 -- Socratic Questioning (Lowy Framework)

**REQUIRED: Use AskUserQuestion tool for ALL questions. Do not print questions and wait.**

Work through these question families, adapting to domain. Each round uses AskUserQuestion with multiple-choice options where possible.

### Forces Discovery

Start with the broadest question to understand the system:

**For INCEPTION MODE:**
```
AskUserQuestion:
  question: "What are the 3-5 major forces acting on this system? What pushes it to change?"
  header: "System Forces"
  options:
    - label: "Business rule changes"
      description: "Pricing, policies, workflows change frequently"
    - label: "Technology/infrastructure changes"
      description: "Databases, APIs, frameworks evolve"
    - label: "User experience changes"
      description: "UI, interaction patterns, accessibility"
    - label: "Integration changes"
      description: "External systems, partners, data sources"
    - label: "Regulatory/compliance changes"
      description: "Legal requirements, data handling rules"
    - label: "Other (please describe)"
      description: "Forces not listed above"
```

**For REVISION MODE:**
```
AskUserQuestion:
  question: "What about the current structure feels wrong? Where is it fighting you?"
  header: "Structural Friction"
  options:
    - label: "Changes to X require changing Y too"
      description: "Two things that should be independent are coupled"
    - label: "A component does too many things"
      description: "Single component has multiple reasons to change"
    - label: "Interfaces are too broad"
      description: "Components know too much about each other"
    - label: "New features don't fit cleanly anywhere"
      description: "Structure doesn't accommodate growth"
    - label: "Other (please describe)"
      description: "Different friction not listed above"
```

### Volatility Identification (per force)

For each force identified, probe for independence and encapsulation:

```
AskUserQuestion:
  question: "If you had to completely replace [X], what else would have to change?"
  header: "Isolation Test: [X]"
  options:
    - label: "Nothing else changes"
      description: "[X] is well-isolated behind a stable interface"
    - label: "[Y] would also change"
      description: "[X] and [Y] are coupled -- may be same volatility axis"
    - label: "Several things would change"
      description: "[X] is deeply entangled -- needs decomposition"
    - label: "Not sure"
      description: "Need to investigate further"
```

Follow up with rate-of-change questions:

```
AskUserQuestion:
  question: "How often does [X] change?"
  header: "Change Frequency: [X]"
  options:
    - label: "Weekly/monthly"
      description: "High volatility -- strong candidate for encapsulation"
    - label: "Quarterly/yearly"
      description: "Medium volatility -- encapsulate if independent"
    - label: "Rarely/never"
      description: "Low volatility -- stable foundation"
    - label: "Varies by customer/deployment"
      description: "May be variability, not volatility"
```

### Volatility vs Variability Check

This is the critical diagnostic. Volatility drives architecture; variability is handled in code.

```
AskUserQuestion:
  question: "When [X] changes, does it require a new component/module (architectural change) or just different configuration/parameters (code-level change)?"
  header: "Volatility vs Variability: [X]"
  options:
    - label: "New component/module needed"
      description: "This is volatility -- drives decomposition"
    - label: "Configuration/parameter change"
      description: "This is variability -- handle with strategy pattern, config, etc."
    - label: "Depends on the specific change"
      description: "May need both architectural and code-level handling"
```

### Customer Axis (Lowy's Second Dimension)

```
AskUserQuestion:
  question: "Do different customers/user types need different [X]?"
  header: "Customer Dimension: [X]"
  options:
    - label: "Yes, fundamentally different behavior"
      description: "Second volatility axis -- must be independent from time axis"
    - label: "Minor variations only"
      description: "Variability, not volatility -- handle in code"
    - label: "All customers get the same [X]"
      description: "No customer axis for this component"
    - label: "Not sure yet"
      description: "Need to investigate customer segments"
```

### Layer Assignment

For each identified component, determine its Lowy layer:

```
AskUserQuestion:
  question: "What does [component] primarily do?"
  header: "Layer Assignment: [component]"
  options:
    - label: "Orchestrates workflow between other components"
      description: "Manager layer -- coordinates, no business logic"
    - label: "Computes business logic and rules"
      description: "Engine layer -- pure business logic, no data access"
    - label: "Accesses data or external systems"
      description: "Resource Accessor layer -- data/API access, no business logic"
    - label: "Provides cross-cutting capability"
      description: "Utility layer -- logging, auth, config, etc."
```

**Challenge patterns (use when answers seem inconsistent):**
- "You said [component] is an Engine, but it accesses the database directly -- should that data access be separated into a Resource Accessor?"
- "You said [A] and [B] are independent, but they both change when [event happens] -- are they really independent axes?"
- "This looks like functional decomposition (UserService, OrderService) rather than volatility decomposition. What independent change axis does each one encapsulate?"

### For REVISION MODE, additional probes:

```
AskUserQuestion:
  question: "If you restructure [X], what happens to its interfaces with [Y] and [Z]?"
  header: "Restructuring Impact"
  options:
    - label: "Interfaces stay the same"
      description: "Internal restructuring only -- low risk"
    - label: "Interfaces need to change"
      description: "Ripple effect -- need to assess downstream impact"
    - label: "Not sure"
      description: "Need to investigate current interfaces"
```

```
AskUserQuestion:
  question: "Does splitting [X] create genuinely independent axes, or will the halves still change together?"
  header: "Independence Check"
  options:
    - label: "Genuinely independent"
      description: "Good split -- each half changes for different reasons"
    - label: "Still change together sometimes"
      description: "Questionable split -- may create coupling"
    - label: "Always change together"
      description: "Bad split -- these belong together"
```

### Minimal Answers Handling

If the architect gives one-word or yes/no answers, provide concrete follow-up options via AskUserQuestion. Never print open-ended questions and wait.

Example follow-up when architect answers "yes" to "Do different customers need different payment handling?":

```
AskUserQuestion:
  question: "How do customer payment needs differ?"
  header: "Payment Volatility Detail"
  options:
    - label: "Different payment providers per region"
      description: "Geographic volatility axis"
    - label: "Different billing models (subscription vs one-time)"
      description: "Business model volatility axis"
    - label: "Different compliance requirements"
      description: "Regulatory volatility axis"
    - label: "Different pricing tiers with different logic"
      description: "Pricing volatility axis"
    - label: "Other (please describe)"
      description: "Different dimension"
```

---

## Step 2 -- Structure Proposal

**Present 2-3 alternative decompositions. NEVER present just one.**

Each proposal must include:
- Node list: name, responsibility (1 sentence), volatility axis (what it encapsulates), Lowy layer
- Edge list: which nodes have interface dependencies (blocks), which interact but don't block (relates_to)
- What this decomposition optimizes for
- What it trades off

**Format:**

```
### Proposal A: [Name -- what it optimizes for]

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| [Name] | [1 sentence] | [What changes it isolates] | Manager |
| [Name] | [1 sentence] | [What changes it isolates] | Engine |
| [Name] | [1 sentence] | [What changes it isolates] | Resource Accessor |
| [Name] | [1 sentence] | [What changes it isolates] | Utility |

Edges:
- [Node A] blocks [Node B] (interface: [what flows between them])
- [Node C] relates_to [Node D] (interaction: [how they interact])

**Optimizes for:** [What this structure does best]
**Trades off:** [What you give up]

### Proposal B: [Name -- what it optimizes for]

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| ... | ... | ... | ... |

Edges:
- ...

**Optimizes for:** [What this structure does best]
**Trades off:** [What you give up]

### Proposal C: [Name -- what it optimizes for] (optional third)

...
```

After presenting all proposals:

```
AskUserQuestion:
  question: "Which structure best matches your understanding of the system's volatility?"
  header: "Choose Decomposition"
  options:
    - label: "Proposal A: [name]"
      description: "[1-line summary of what it optimizes]"
    - label: "Proposal B: [name]"
      description: "[1-line summary of what it optimizes]"
    - label: "Proposal C: [name]" (if presented)
      description: "[1-line summary of what it optimizes]"
    - label: "Combine elements"
      description: "Take specific nodes/edges from different proposals"
    - label: "None of these -- let me explain"
      description: "Back to questioning with new information"
```

---

## Step 3 -- Encode in bd

After the architect chooses a structure:

**Create architecture epic:**

```bash
bd create '[System Name] Architecture' --type epic --label arch \
  --design '## System Purpose
[1-2 sentences from Socratic dialogue]

## Lowy Layer Map
- Manager: [components at this layer]
- Engine: [components at this layer]
- Resource Accessor: [components at this layer]
- Utility: [components at this layer]

## Global Constraints
[Cross-cutting rules from Socratic dialogue -- e.g., "no component may
access storage directly except Resource Accessors"]'
```

**Create component nodes (one per component):**

```bash
bd create '[Component Name]' --type feature --label arch,component \
  --parent <epic-id> \
  --design '## Volatility Axis
[What this component encapsulates -- which force/change it isolates]

## Layer: [Manager|Engine|Resource Accessor|Utility]
[Why this layer -- what it does and does NOT do]

## Interface Contract
- IN: [operations this component exposes to others]
- OUT: [operations this component calls on others]

## Responsibility
[1-2 sentences -- what it does, what it does NOT do]'
```

**Set initial stability state:**

```bash
# Primary approach: state dimensions
bd set-state <component-id> stability=exploring \
  --reason 'initial decomposition, not yet audited'
```

If `bd set-state` is not available (bd version may not support it), use labels as fallback:

```bash
# Fallback: label-based stability tracking
bd label <component-id> arch:exploring
# Later transitions: arch:audited, arch:accepted, arch:stable
```

**Create edges between components:**

```bash
# Interface dependency (downstream depends on upstream)
bd dep add <downstream-id> <upstream-id>

# Non-blocking interaction
bd relate <node-a-id> <node-b-id>
```

**For REVISION MODE:** Update existing nodes rather than creating duplicates. If a component is being fundamentally replaced (not just edited), use supersedes:

```bash
# Update existing component
bd update <component-id> --design '[updated design]'

# If replacing a component entirely
bd create '[New Component Name]' --type feature --label arch,component \
  --parent <epic-id> --design '[new design]'
bd dep add <new-id> <old-id> --type supersedes
bd close <old-id>
```

**For fractal sub-decomposition:** Create sub-components as children of the component being decomposed. They follow the same rules (layers, volatility axes, ADRs).

```bash
# Sub-components use hierarchical IDs
bd create '[Sub-Component Name]' --type feature --label arch,component \
  --parent <component-id> \
  --design '[same structure as regular component nodes]'
```

---

## Step 4 -- Create ADRs

For each significant decomposition decision, guide the architect through creating an ADR.

**Check existing ADR numbering:**

```bash
ls doc/arch/adr-*.md 2>/dev/null | sort | tail -1
# Determine next sequential number
```

**Create doc/arch/ directory if needed:**

```bash
mkdir -p doc/arch
```

**Draft ADR and present for validation:**

```
I'll draft an ADR for this decision. Review and tell me if this captures your intent:

# ADR-NNN: [Decision Title]

## Status
Accepted

## Context
[Forces from Socratic dialogue, stated in neutral language.
What pressures led to this decision? What constraints exist?]

## Decision
We will [active voice, full sentences describing the structural choice].

## Consequences
- [Positive consequence -- what this enables]
- [Negative consequence -- what tradeoff we accept]
- [What this constrains or enables for future work]
```

After architect approves, create the file:

```bash
# Use Write tool to create the ADR file
# Location: doc/arch/adr-NNN.md
# Number sequentially, never reuse numbers
```

**ADRs to create:**
- One per major boundary decision (why component X is separate from component Y)
- One per significant tradeoff accepted (why we chose structure A over structure B)
- Reference the [ADR template](../common-patterns/adr-template.md) for format details

**ADR flow:** Consequences of one ADR become context for subsequent ADRs. If a decision constrains future choices, state that explicitly in Consequences.

---

## Step 5 -- Handoff Guidance

Present a summary of the architecture graph and recommended next steps:

```
## Graph Summary

| Node | Layer | Volatility Axis | Stability |
|------|-------|-----------------|-----------|
| [name] | [layer] | [axis] | exploring |
| ... | ... | ... | exploring |

## ADRs Created
- doc/arch/adr-NNN.md: [Decision title]
- doc/arch/adr-NNN.md: [Decision title]

## Recommended Next Steps
- Run /audit-arch to stress-test this decomposition for hidden complection
- [List any nodes that are simple/obvious candidates for early stability]
- After audit: resolve or accept tensions, then stable nodes feed /brainstorm
- Stable nodes transition: exploring -> audited -> accepted -> stable
- When a node reaches 'stable', it's ready for inner-loop handoff via /brainstorm
  (/brainstorm will auto-detect the architecture node and load its context)
```

</the_process>

<examples>

<example>
<scenario>Good decomposition with clear volatility axes -- order processing system</scenario>

<code>
Architect: "We need to decompose an order processing system for an e-commerce platform."

Claude uses AskUserQuestion:
  question: "What are the 3-5 major forces acting on this system?"
  [Architect selects: business rule changes, integration changes, regulatory changes]

Claude uses AskUserQuestion:
  question: "If you had to completely replace the pricing logic, what else would change?"
  [Architect: "Nothing -- pricing is independent of fulfillment and payment"]

Claude uses AskUserQuestion:
  question: "If you had to completely replace the payment provider, what else would change?"
  [Architect: "Nothing -- we just swap the provider behind the payment interface"]

Claude uses AskUserQuestion:
  question: "If fulfillment rules change (new shipping carriers, warehouse logic), what else changes?"
  [Architect: "Nothing -- fulfillment is independent"]

Claude uses AskUserQuestion:
  question: "How often does pricing change vs fulfillment vs payment?"
  [Architect: "Pricing monthly, fulfillment quarterly, payment rarely"]

Claude presents proposals:

### Proposal A: Maximize Volatility Isolation

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| Order Orchestrator | Coordinates order lifecycle | Workflow sequencing | Manager |
| Pricing Engine | Computes prices, discounts, taxes | Pricing rule changes | Engine |
| Fulfillment Engine | Determines shipping, warehouse routing | Fulfillment rule changes | Engine |
| Payment Gateway | Processes payments via providers | Payment provider changes | Resource Accessor |
| Order Store | Persists order data | Storage technology changes | Resource Accessor |

Edges:
- Order Orchestrator blocks Pricing Engine (interface: price calculation requests)
- Order Orchestrator blocks Fulfillment Engine (interface: fulfillment requests)
- Order Orchestrator blocks Payment Gateway (interface: payment processing)
- Order Orchestrator blocks Order Store (interface: order persistence)
- Pricing Engine relates_to Fulfillment Engine (interaction: shipping cost affects total)

**Optimizes for:** Independent deployment of each volatility axis
**Trades off:** More interfaces to maintain (5 components vs fewer)

### Proposal B: Consolidate Low-Volatility Components

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| Order Orchestrator | Coordinates order lifecycle | Workflow sequencing | Manager |
| Pricing Engine | Computes prices, discounts, taxes | Pricing rule changes | Engine |
| Fulfillment Engine | Determines shipping, warehouse routing | Fulfillment rule changes | Engine |
| Infrastructure | Payment + storage behind unified interface | External system changes | Resource Accessor |

Edges:
- Order Orchestrator blocks Pricing Engine (interface: price calculation)
- Order Orchestrator blocks Fulfillment Engine (interface: fulfillment requests)
- Order Orchestrator blocks Infrastructure (interface: payment + persistence)
- Pricing Engine relates_to Fulfillment Engine (interaction: shipping costs)

**Optimizes for:** Fewer interfaces, simpler orchestration
**Trades off:** Payment and storage coupled (both rarely change, so coupling cost is low)

### Proposal C: Split by Customer Axis

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| Order Orchestrator | Coordinates order lifecycle | Workflow sequencing | Manager |
| B2C Pricing | Consumer pricing, promotions | Consumer pricing changes | Engine |
| B2B Pricing | Wholesale pricing, contracts | Business pricing changes | Engine |
| Fulfillment Engine | Determines shipping, warehouse routing | Fulfillment rule changes | Engine |
| Payment Gateway | Processes payments via providers | Payment provider changes | Resource Accessor |
| Order Store | Persists order data | Storage technology changes | Resource Accessor |

Edges:
- Order Orchestrator blocks B2C Pricing (interface: consumer price requests)
- Order Orchestrator blocks B2B Pricing (interface: wholesale price requests)
- Order Orchestrator blocks Fulfillment Engine (interface: fulfillment requests)
- Order Orchestrator blocks Payment Gateway (interface: payments)
- Order Orchestrator blocks Order Store (interface: persistence)

**Optimizes for:** Independent evolution of B2B vs B2C pricing
**Trades off:** More components, only justified if B2B and B2C truly diverge

Claude uses AskUserQuestion:
  question: "Which structure best matches your understanding of the system's volatility?"
  [Architect chooses Proposal A]

Claude encodes in bd:
  bd create 'Order Processing Architecture' --type epic --label arch --design '...'
  bd create 'Order Orchestrator' --type feature --label arch,component --parent <epic> --design '...'
  bd create 'Pricing Engine' --type feature --label arch,component --parent <epic> --design '...'
  [... for each component]

Claude drafts ADR:
  # ADR-001: Isolate pricing, fulfillment, and payment as independent volatility axes
  ## Status
  Accepted
  ## Context
  The order processing system faces three independent forces: pricing rules change monthly,
  fulfillment rules change quarterly, and payment providers change rarely. These forces are
  independent -- changing one does not require changing the others.
  ## Decision
  We will decompose the order processing system into five components, each encapsulating
  one volatility axis: Order Orchestrator (workflow), Pricing Engine (pricing rules),
  Fulfillment Engine (fulfillment rules), Payment Gateway (payment providers),
  and Order Store (storage technology).
  ## Consequences
  - Each volatility axis can evolve independently without affecting others
  - Five components means five interfaces to maintain
  - Orchestrator becomes the single point of coordination complexity
  - Future pricing changes (new discount types, tax rules) only touch Pricing Engine
</code>

<why_it_works>
- Each node explicitly names its volatility axis ("pricing rule changes", not just "pricing")
- Independence verified through isolation test questions
- Lowy layers respected: Manager orchestrates, Engines compute, Resource Accessors access
- Three alternatives with clear tradeoff analysis
- Architect given agency to choose
- ADR captures the decision with forces, active-voice decision, and consequences
</why_it_works>
</example>

<example>
<scenario>BAD -- Single recommendation instead of alternatives</scenario>

<code>
Architect: "We need to decompose a notification system."

Claude: "Based on your requirements, here is the decomposition:

| Node | Responsibility | Layer |
|------|---------------|-------|
| Notification Manager | Orchestrates notification flow | Manager |
| Template Engine | Renders notification content | Engine |
| Channel Router | Selects delivery channel | Engine |
| Email Sender | Sends emails via SMTP | Resource Accessor |
| Push Sender | Sends push notifications | Resource Accessor |

This is the right structure because it separates concerns cleanly."
</code>

<why_it_fails>
- Only one decomposition presented -- architect denied agency
- No tradeoff analysis -- cannot evaluate if this is optimal
- No volatility axes named -- "separates concerns" is not volatility-based reasoning
- No alternatives means no exploration of the design space
- "Right structure" is a recommendation -- decomposition skill never recommends, only presents options
- Missed opportunities: Template Engine and Channel Router might be one component, or Email/Push might be consolidated
</why_it_fails>

<correction>
Present 2-3 alternatives with explicit tradeoffs:

### Proposal A: Maximum Channel Isolation

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| Notification Orchestrator | Coordinates notification lifecycle | Workflow sequencing | Manager |
| Content Engine | Renders templates, personalizes content | Content format changes | Engine |
| Routing Engine | Selects channels based on preferences/rules | Routing rule changes | Engine |
| Email Accessor | Sends via SMTP/provider API | Email provider changes | Resource Accessor |
| Push Accessor | Sends via push provider | Push provider changes | Resource Accessor |
| SMS Accessor | Sends via SMS gateway | SMS provider changes | Resource Accessor |

**Optimizes for:** Adding/replacing individual channels independently
**Trades off:** More components, one Resource Accessor per channel

### Proposal B: Consolidated Delivery

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| Notification Orchestrator | Coordinates notification lifecycle | Workflow sequencing | Manager |
| Content Engine | Renders and personalizes content | Content format changes | Engine |
| Delivery Gateway | Routes and sends via all channels | Channel/provider changes | Resource Accessor |

**Optimizes for:** Fewer interfaces, simpler orchestration
**Trades off:** Channel changes ripple through one large Delivery Gateway

### Proposal C: Content-Channel Fusion

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| Notification Orchestrator | Coordinates notification lifecycle | Workflow sequencing | Manager |
| Notification Engine | Content + routing as unified concern | Notification logic changes | Engine |
| Delivery Gateway | Sends via all channels | Provider changes | Resource Accessor |

**Optimizes for:** Minimal components, lowest interface overhead
**Trades off:** Content and routing coupled -- must change together

Then ask architect to choose with AskUserQuestion.
</correction>
</example>

<example>
<scenario>BAD -- Non-independent volatility axes (functional decomposition in disguise)</scenario>

<code>
Architect: "We need to decompose our SaaS platform."

Claude identifies components:

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| UserService | Manages user accounts | User changes | Engine |
| OrderService | Processes orders | Order changes | Engine |
| ProductService | Manages product catalog | Product changes | Engine |
| PaymentService | Handles payments | Payment changes | Resource Accessor |

Architect approves and Claude encodes in bd.
</code>

<why_it_fails>
- This is functional decomposition, not volatility-based decomposition
- "User changes" and "Order changes" are not independent axes -- adding subscription support changes BOTH UserService and OrderService
- Adding a new pricing tier changes ProductService, OrderService, AND PaymentService simultaneously
- Volatility axis names are just the entity name with "changes" appended -- not actual independent forces
- No isolation test was performed ("if you replace X, does Y change?")
- Lowy's method would ask: "What independent forces act on this system?" not "What entities exist?"

**The tell:** When the component names match database tables or REST resources (User, Order, Product), it's almost always functional decomposition, not volatility decomposition.
</why_it_fails>

<correction>
Go back to forces discovery. Ask the isolation test questions:

Claude uses AskUserQuestion:
  question: "If you add subscription support, which of these change?"
  [Architect: "Users need subscription status, orders need recurring billing, products need subscription tiers"]
  -- This proves User/Order/Product are NOT independent axes

Claude uses AskUserQuestion:
  question: "What are the actual independent forces? What changes for one reason only?"
  [Architect identifies: "Pricing rules change independently. Fulfillment changes independently. User identity/auth changes independently. Subscription lifecycle changes independently."]

Now decompose by actual volatility:

### Proposal A: Volatility-Based

| Node | Responsibility | Volatility Axis | Layer |
|------|---------------|-----------------|-------|
| Platform Orchestrator | Coordinates cross-cutting workflows | Workflow sequencing | Manager |
| Identity Engine | Authentication, authorization, profiles | Auth/identity rule changes | Engine |
| Pricing Engine | Pricing tiers, discounts, billing rules | Pricing rule changes | Engine |
| Subscription Engine | Lifecycle, renewals, cancellations | Subscription model changes | Engine |
| Catalog Accessor | Product data storage and retrieval | Catalog storage changes | Resource Accessor |
| Payment Accessor | Payment provider integration | Payment provider changes | Resource Accessor |

Independence verification:
- Changing pricing rules does NOT affect identity or subscription lifecycle
- Changing subscription model does NOT affect how pricing is calculated
- Changing payment provider does NOT affect pricing rules or subscription lifecycle
- Each axis changes for ONE reason only

**Optimizes for:** True independence -- each component changes for exactly one reason
**Trades off:** Cross-entity features (like "subscription user with tiered pricing") require orchestration across components

### Proposal B: ...
[Continue with 1-2 more alternatives]
</correction>
</example>

<example>
<scenario>Good revision of an existing graph after audit found tension</scenario>

<code>
Context: After running /audit-arch, the architect got a tension report showing that the
Content Engine and Routing Engine in a notification system always change together --
"every time we add a new notification type, both engines need updating."

Architect invokes /decompose to restructure.

Claude detects REVISION MODE:
  bd list --label arch --type epic --status open
  [Found: bd-abc 'Notification System Architecture']
  bd list --label arch,component --parent bd-abc
  [Found: Notification Orchestrator, Content Engine, Routing Engine,
   Email Accessor, Push Accessor]

Claude summarizes current state:
"Your notification architecture has 5 components. The audit found Content Engine and
Routing Engine have coupled volatility -- they change together when notification types change.
Let me ask some questions about the restructuring."

Claude uses AskUserQuestion:
  question: "The audit found Content Engine and Routing Engine change together. Does splitting them still make sense, or should they merge?"
  header: "Restructuring: Content + Routing"
  options:
    - label: "Merge into single Notification Engine"
      description: "Accept they share a volatility axis"
    - label: "Keep separate but redefine interfaces"
      description: "Maybe the coupling is in the interface, not the components"
    - label: "Let me explain what's actually happening"
      description: "The situation is more nuanced"

[Architect: "Merge -- they really do change together"]

Claude presents revision proposals:

### Proposal A: Merge Content + Routing

Change: Merge Content Engine and Routing Engine into Notification Engine

| Node | Change | Volatility Axis | Layer |
|------|--------|-----------------|-------|
| Notification Orchestrator | Unchanged | Workflow sequencing | Manager |
| Notification Engine | MERGED from Content + Routing | Notification type changes | Engine |
| Email Accessor | Unchanged | Email provider changes | Resource Accessor |
| Push Accessor | Unchanged | Push provider changes | Resource Accessor |

**Optimizes for:** Eliminates false boundary, simplifies interfaces
**Trades off:** Notification Engine is larger (but changes for one reason)

### Proposal B: Merge + Consolidate Delivery

Change: Merge Content + Routing AND merge Email + Push Accessors

| Node | Change | Volatility Axis | Layer |
|------|--------|-----------------|-------|
| Notification Orchestrator | Unchanged | Workflow sequencing | Manager |
| Notification Engine | MERGED from Content + Routing | Notification type changes | Engine |
| Delivery Gateway | MERGED from Email + Push | Delivery provider changes | Resource Accessor |

**Optimizes for:** Minimal component count, simplest orchestration
**Trades off:** Email and push provider changes affect same component

[Architect chooses Proposal A]

Claude updates bd (does not create duplicates):
  bd create 'Notification Engine' --type feature --label arch,component \
    --parent bd-abc --design '## Volatility Axis
  Notification type changes -- content rendering and channel routing change together
  when new notification types are added. Merged from former Content Engine and Routing Engine.
  ...'
  bd dep add <new-notification-engine> <old-content-engine> --type supersedes
  bd dep add <new-notification-engine> <old-routing-engine> --type supersedes
  bd close <old-content-engine>
  bd close <old-routing-engine>

Claude creates ADR:
  # ADR-003: Merge Content Engine and Routing Engine into Notification Engine
  ## Status
  Accepted
  ## Context
  Architectural audit (see audit report) found that Content Engine and Routing Engine
  have coupled volatility: every new notification type requires changes to both
  components. The original decomposition assumed content rendering and channel routing
  were independent axes, but practice showed they are not.
  ## Decision
  We will merge Content Engine and Routing Engine into a single Notification Engine
  that encapsulates all notification type changes (content, routing, and formatting).
  ## Consequences
  - Eliminates the false boundary between content and routing
  - Reduces interface count (one engine instead of two)
  - Notification Engine is larger but changes for a single reason
  - Future audit should verify Email Accessor and Push Accessor remain independent
</code>

<why_it_works>
- Loads existing graph before questioning (REVISION MODE)
- Socratic questions focus on the specific tension, not full re-decomposition
- Proposals are targeted revisions, not wholesale replacements
- Existing components updated or superseded, not duplicated
- ADR explains WHY the revision was needed (audit evidence)
- Consequences note what to watch in future audits
</why_it_works>
</example>

</examples>

<critical_rules>
## Rules That Have No Exceptions

1. **ALWAYS present 2-3 alternatives, NEVER a single recommendation.** Decomposition is not a recommendation engine. Present options with tradeoffs. Let the architect choose.

2. **Every node MUST name its volatility axis explicitly.** "Handles user logic" is not a volatility axis. "Encapsulates authentication rule changes" is. If a node cannot name its axis, it is not a volatility-based component.

3. **Challenge non-independent axes.** If two components change for the same reason, they may be the same volatility axis split artificially. Ask the isolation test: "If you replace X, does Y also change?"

4. **Challenge functional decomposition.** If component names match database tables or REST resources (UserService, OrderService, ProductService), push back. Ask: "What independent force does each one encapsulate?" Functional decomposition organized by entity is NOT volatility decomposition.

5. **Enforce Lowy layer rules.** No upward dependencies (Engine cannot call Manager). Managers have no business logic. Engines do not access resources directly. Resource Accessors do not contain business rules.

6. **Scale-agnostic vocabulary.** Adapt "component/module/service/layer" to the context. A module decomposition and a microservice decomposition follow the same principles.

7. **Think in components and boundaries, NOT classes and functions.** If the conversation descends to implementation details (class hierarchies, function signatures, data structures), redirect: "That's inner-loop territory. Let's stay at the component and interface level."

8. **Distinguish volatility from variability.** Volatility (needs architectural encapsulation) drives decomposition. Variability (different configurations, strategy patterns) is handled in code. Only volatility creates new components.

9. **Use AskUserQuestion for ALL questions.** Never print questions and wait. Always provide options where possible, with an "Other" escape hatch.

10. **ADRs for key decisions.** Every significant boundary decision and every significant tradeoff gets an ADR in doc/arch/. The graph is temporary; ADRs are permanent.

## Common Excuses

All of these mean: **STOP. Follow the process.**

- "The decomposition is obvious" (Obvious decompositions are often functional, not volatility-based. Verify.)
- "Only one structure makes sense" (Present alternatives anyway. The architect may see options you don't.)
- "This component doesn't need a volatility axis" (Then it shouldn't be a component. Merge it.)
- "Layer rules are too strict" (They exist for a reason. Escalate if truly stuck.)
- "ADRs are overhead for this decision" (ADRs outlive the graph. Capture intent now or lose it.)
- "Classes and functions are relevant here" (Stay at component level. Implementation is the inner loop's job.)
- "The architect already knows what they want" (Still validate through Socratic questioning. Hidden assumptions surface.)
</critical_rules>

<verification_checklist>
Before completing decomposition:

- [ ] Used AskUserQuestion for all questions (never printed and waited)
- [ ] Dispatched codebase-investigator if codebase exists
- [ ] Checked for existing ADRs and architecture epic
- [ ] Identified volatility axes through isolation testing (not just entity listing)
- [ ] Verified axes are independent (each changes for one reason only)
- [ ] Distinguished volatility from variability for each force
- [ ] Presented 2-3 alternatives with tradeoff tables (never just one)
- [ ] Every node names its volatility axis explicitly
- [ ] Lowy layer rules respected (no upward deps, no business logic in Managers, no resource access in Engines)
- [ ] Architecture epic created in bd with --label arch
- [ ] Component nodes created with --label arch,component and --parent
- [ ] Component designs include: volatility axis, layer, interface contract, responsibility
- [ ] Stability state set on all components (exploring)
- [ ] Edges created (blocks for interface deps, relates_to for interactions)
- [ ] ADRs created for key boundary decisions and tradeoffs
- [ ] ADRs follow Nygard format (Status, Context, Decision, Consequences)
- [ ] Handoff guidance presented with graph summary and next steps
- [ ] No implementation-level detail (classes, functions, data structures) in any output
- [ ] For revisions: existing nodes updated or superseded, not duplicated

**Can't check all boxes?** Return to the relevant step and complete it.
</verification_checklist>

<integration>
**This skill calls:**
- hyperpowers:codebase-investigator (when codebase exists -- map module structure and boundaries)
- hyperpowers:internet-researcher (when evaluating technology options for component boundaries)

**This skill is called by:**
- User (via /hyperpowers:decompose command)
- Architecture work inception
- After /audit-arch surfaces tensions requiring restructuring

**Call chain:**
```
OUTER LOOP:
  /decompose <-> /audit-arch <-> architect resolves

HANDOFF (stable node):
  stable node -> /brainstorm (auto-loads arch context + ADRs)

INNER LOOP (unchanged):
  brainstorming -> sre-refinement -> writing-plans -> executing-plans -> review
```

**Agents used:**
- codebase-investigator (understand existing module structure)
- internet-researcher (evaluate technology options when relevant)

**Tools required:**
- AskUserQuestion (for all Socratic questions)
- Write (for creating ADR files)
- bd CLI (for graph encoding)

**Artifacts produced:**
- bd architecture epic (type: epic, labels: arch)
- bd component nodes (type: feature, labels: arch,component)
- ADR files (doc/arch/adr-NNN.md)
</integration>

<resources>
**Detailed guides:**
- [ADR template and examples](../common-patterns/adr-template.md)
- [bd command reference](../common-patterns/bd-commands.md)
- [Common anti-patterns](../common-patterns/common-anti-patterns.md)
- [Common rationalizations](../common-patterns/common-rationalizations.md)

**Lowy's volatility-based decomposition:**
- Righting Software (Juval Lowy) -- volatility analysis method
- Key concepts: volatility vs variability, two axes (time + customer), Manager/Engine/Resource Accessor/Utility layers
- SE Radio episode 407: Juval Lowy on Righting Software

**Hickey's simplicity framework (used by /audit-arch):**
- Simple Made Easy (Rich Hickey) -- complection detection
- Are We There Yet? (Rich Hickey) -- state/identity/value separation

**When stuck:**
- Architect gives minimal answers -> Provide concrete follow-up options via AskUserQuestion
- Cannot identify volatility axes -> Ask: "What forces push this system to change?"
- Component names match entities -> Challenge: "What independent change axis does each encapsulate?"
- Architect wants to skip to encoding -> Validate: "Can you name the volatility axis for each component?"
- Two axes seem dependent -> Test: "If you replace X, does Y also change?"
</resources>
