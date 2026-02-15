---
name: architectural-audit
description: "Hickey simplicity-based audit of architecture graphs -- finds complection, coupling, and drift without making recommendations"
---

<skill_overview>
Examine an architecture graph (and codebase if available) for complection, hidden coupling, temporal coupling, layer violations, and state/identity conflation using Hickey's simplicity framework. Produce a structured tension report that surfaces both pulls of every tension without resolving them. The architect reads the report and decides.
</skill_overview>

<rigidity_level>
RIGID - Same 6 analysis passes every time, same output format, same self-check procedure. No adaptation, no shortcuts, no skipping passes. The analytical rigor IS the value.
</rigidity_level>

<quick_reference>
| Step | Action | Deliverable |
|------|--------|-------------|
| 0 | Load architecture graph from bd | Graph state + ADRs loaded |
| 1 | Gather evidence (codebase-investigator) | Module structure, imports, co-change data |
| 2 | Run 6 analysis passes | Raw tension findings |
| 3 | Self-check + present | Tension report (no recommendations) |

**Key:** This skill is ANALYTICAL. No AskUserQuestion during analysis. Load, analyze, report.
**Key:** Tensions surface both pulls. NO recommendations, NO severity rankings.
</quick_reference>

<when_to_use>
- After /decompose created or revised an architecture graph
- When structure feels wrong but you cannot articulate why
- Periodic health check on an existing architecture
- Before inner-loop handoff: verify a node is truly stable
- After significant implementation: check for drift from declared intent

**Don't use for:**
- Creating a new decomposition (use /decompose)
- Inner-loop feature work (use hyperpowers:brainstorming)
- Bug fixes (use hyperpowers:fixing-bugs)
- When no architecture graph exists (run /decompose first)
</when_to_use>

<the_process>

## Step 0 -- Load Architecture Graph

**Announce:** "I'm using the architectural-audit skill to examine your architecture graph for complection and hidden coupling."

**Load the graph:**

```bash
# Find architecture epic
bd list --label arch --type epic --status open
```

**If no architecture epic found:**
```
No architecture graph found in bd. The audit skill examines an existing
architecture graph for tensions and complection.

To create an architecture graph, run /decompose first.
```
Stop here -- cannot audit without a graph.

**If found, load full graph:**

```bash
# Load epic
bd show <epic-id>

# Load all component nodes
bd list --label arch,component --parent <epic-id>

# For each component, load full details
bd show <component-id>

# Load dependency tree
bd dep tree <epic-id>
```

Record for analysis:
- All component nodes with their volatility axes, layers, interface contracts
- All edges (blocks, relates_to) with their interaction descriptions
- Stability states of each component
- Layer assignments (Manager, Engine, Resource Accessor, Utility)

**Load existing ADRs:**

```bash
ls doc/arch/adr-*.md 2>/dev/null
```

If ADRs exist, read each one. Record:
- Decision title and status (accepted, deprecated, superseded)
- What was decided (the structural choice)
- Consequences stated
- These will be used to: (a) skip already-accepted tensions, (b) detect drift

If no ADRs exist, note this and proceed -- analysis uses graph and codebase evidence.

---

## Step 1 -- Gather Evidence

**This step is ANALYTICAL. No AskUserQuestion. Gather evidence silently.**

**If codebase exists:** Dispatch `hyperpowers:codebase-investigator` with a comprehensive prompt that gathers evidence for ALL 6 analysis passes:

```
Examine the codebase and report on the following. Stay at module/package level,
not class/function level.

1. MODULE STRUCTURE AND BOUNDARIES
   - Top-level modules/packages and their responsibilities
   - Which modules have clear boundaries (well-defined exports) vs fuzzy boundaries
     (everything exported, or internal details leaking)

2. IMPORT/DEPENDENCY GRAPHS
   - Which modules import from which other modules
   - Any circular import chains
   - Modules with unusually high fan-in (many dependents) or fan-out (many dependencies)
   - Any imports that cross what appear to be layer boundaries

3. CO-CHANGE PATTERNS
   - Files or modules that frequently change together in recent commits
   - Changes that span multiple modules (cross-cutting modifications)
   - Any modules that appear independent in structure but coupled in change history

4. ACTUAL CALL PATTERNS
   - How modules actually interact at runtime (function calls, message passing, events)
   - Any interactions not visible in the import graph (dynamic dispatch, reflection,
     shared configuration, environment variables)
   - Any upward calls (lower-layer module calling higher-layer module)

5. INTERFACE SURFACE AREA
   - What each module exports (public API) vs what it keeps internal
   - Interfaces that seem too broad (exposing internal implementation details)
   - Interfaces that carry multiple concerns (one API serving unrelated purposes)

6. SHARED STATE
   - Global variables, singletons, shared mutable state between modules
   - Configuration that multiple modules depend on
   - Any state that creates hidden coupling between otherwise independent modules
```

**If no codebase (greenfield with graph only):** Skip this step. Analysis will use only graph evidence. Note in the report: "Audit based on graph evidence only -- no codebase to verify against."

Record all evidence for use in Step 2.

---

## Step 2 -- Run 6 Analysis Passes

Run each pass using both graph evidence and codebase evidence (when available). Each pass may produce zero or more tensions.

**Before recording a tension:** Check if an existing ADR already accepts this tension. If an accepted ADR covers the exact structural choice, skip the tension and note: "Accepted via ADR-NNN: [title]".

### Pass 1: Complection Scan

**What to look for:** Concerns braided together that should be independent.

**Graph evidence:**
- Components with multiple volatility axes listed (should have exactly one)
- Components whose responsibility description mentions multiple unrelated concerns
- Components that appear in edges for unrelated interaction types

**Codebase evidence:**
- Modules that import from multiple unrelated domains
- Files that contain logic for multiple independent concerns
- Functions that combine data access, business logic, and orchestration

**Tension pattern:** "[Component] braids [Concern A] and [Concern B]"

### Pass 2: Interface Analysis

**What to look for:** Interfaces that carry more than one concern or leak implementation details.

**Graph evidence:**
- Interface contracts (IN/OUT) that mix different types of operations
- Components whose interface exposes internal structure
- Edges where the interaction description suggests the caller needs implementation knowledge

**Codebase evidence:**
- Exported APIs that serve unrelated purposes through one surface
- Interfaces that require callers to understand internal state
- Data structures passed across boundaries that contain implementation details

**Tension pattern:** "Interface between [A] and [B] carries [Concern X] and [Concern Y]"

### Pass 3: Temporal Coupling

**What to look for:** Things that must happen in a specific order but are not explicitly sequenced.

**Graph evidence:**
- Components that interact (relates_to) but have no sequencing (no blocks edge)
- Initialization order dependencies not captured in the graph
- Components whose interface contracts imply ordering ("call X before Y")

**Codebase evidence:**
- Co-change patterns: modules that always change together suggest coupling
- Initialization sequences that break if reordered
- Event handlers that assume specific execution order

**Tension pattern:** "[A] and [B] have implicit ordering dependency not captured in graph"

### Pass 4: Hidden Dependencies

**What to look for:** Dependencies that exist but are not visible in the declared graph.

**Graph evidence:**
- Components with no declared dependencies that seem like they should have some
- Missing edges between components that clearly interact
- Components that share concepts (similar vocabulary in their descriptions) without a declared relationship

**Codebase evidence:**
- Actual imports/calls between modules not reflected in graph edges
- Shared configuration or environment variables creating invisible coupling
- Dynamic dispatch or event systems hiding concrete dependencies
- Shared data formats or schemas without explicit interface contracts

**Tension pattern:** "[A] depends on [B] through [mechanism] but graph shows no relationship"

### Pass 5: Layer Violations

**What to look for:** Violations of Lowy layer rules.

**Graph evidence:**
- Edges where a lower layer calls a higher layer (Engine calling Manager)
- Managers that contain business logic (should only orchestrate)
- Engines that access resources directly (should go through Resource Accessors)
- Resource Accessors that contain business rules (should only access data)
- Utilities that depend on domain-specific components (should be cross-cutting)

**Codebase evidence:**
- Imports that go upward in the layer hierarchy
- Business logic found in orchestration or data access modules
- Data access code found in business logic modules
- Domain-specific code in utility modules

**Tension pattern:** "[A] (Layer: [X]) calls [B] (Layer: [Y]) -- upward dependency"

### Pass 6: State/Identity Conflation

**What to look for:** Mutable shared state, identity used where value would suffice.

**Graph evidence:**
- relates_to edges that represent shared mutable state (not just interaction)
- Components that both read and write the same state
- Identity-based references where value-based would decouple

**Codebase evidence:**
- Global mutable state accessed by multiple modules
- Singletons that carry mutable state between components
- Object identity used for comparison where value equality would work
- Caches or registries that create hidden state dependencies

**Tension pattern:** "[A] and [B] share mutable state [S] creating hidden coupling"

---

## Step 3 -- Self-Check and Present

### Self-Check (MANDATORY)

Before presenting the tension report, scan ALL output text for accidental recommendations. This step is not optional.

**Scan for these keyword patterns:**

Recommendation language (rewrite if found):
- "should" -> rewrite to neutral observation
- "must" -> rewrite to "currently does/does not"
- "recommend" -> remove entirely
- "better" -> rewrite to tradeoff comparison
- "prefer" -> remove entirely
- "consider changing" -> remove entirely
- "the best approach" -> remove entirely
- "you should" -> remove entirely
- "however I think" -> remove entirely
- "ideally" -> remove entirely

Severity language (rewrite if found):
- "critical" -> use structural observation: "affects N downstream nodes"
- "high/medium/low" severity -> remove entirely
- "severe" -> use structural observation
- "urgent" -> remove entirely
- "important" -> use structural observation
- "minor" -> remove entirely

Ordering language (rewrite if found):
- "address first" -> remove (implies priority = recommendation)
- "most pressing" -> remove
- "primary concern" -> remove

**If any keyword found:** Rewrite that tension to use only neutral, structural language. Both pulls stated equally. No implied preference.

### Present Tension Report

**Report format:**

```
## Architectural Audit Report

**Graph:** [Epic name] ([epic-id])
**Components audited:** [count]
**Evidence sources:** [graph | graph + codebase]
**ADRs reviewed:** [count, or "none found"]

---

### Tensions Found

## Tension: [Descriptive Name]
**Components:** [Component A], [Component B]
**Analysis pass:** [which of the 6 passes found this]
**Pull 1:** [Structural choice] -- Gain: [what you get]. Cost: [what you pay].
**Pull 2:** [Alternative choice] -- Gain: [what you get]. Cost: [what you pay].
**If you assume:** [condition that makes Pull 1 correct].
**If you assume:** [condition that makes Pull 2 correct].
**Structural observation:** [neutral fact -- e.g., "affects 3 downstream nodes",
  "both components changed together in 7 of last 10 commits"]
**Evidence:** [specific codebase/graph evidence that surfaced this]

---

[Repeat for each tension]

### Accepted Tensions (Skipped)

- ADR-NNN: [title] -- [which tension this covers]

### Drift Detected

## Drift: [ADR-NNN title]
**Declared:** [What the ADR says should be true]
**Observed:** [What the codebase actually does]
**Evidence:** [Specific files, imports, or patterns that show the divergence]

---

[Repeat for each drift]

### Graph Summary

| Component | Layer | Stability | Tensions | Drift |
|-----------|-------|-----------|----------|-------|
| [name] | [layer] | [state] | [count] | [yes/no] |

### Audit Outcome

**Tensions found:** [count]
**Accepted (via ADRs):** [count]
**Drift detected:** [count]
**Clean (no tensions, no drift):** [yes/no]

[If clean:]
All components passed audit. Nodes currently in 'exploring' state
can transition to 'audited'.

[If tensions found:]
[count] tensions require architect resolution. Options for each tension:
- Modify graph structure (run /decompose to restructure)
- Accept the tension (create ADR documenting the acceptance)
- Investigate further (dispatch codebase-investigator for deeper analysis)
```

**Update component stability states after audit:**

For components with no tensions and no drift:
```bash
bd set-state <component-id> stability=audited \
  --reason 'passed architectural audit with no tensions'
```

Fallback if set-state not available:
```bash
bd label <component-id> arch:audited
```

For components with tensions: leave stability unchanged (still 'exploring').

</the_process>

<examples>

<example>
<scenario>Good audit finding real tensions in an order processing architecture</scenario>

<code>
Claude loads architecture graph:
  bd list --label arch --type epic --status open
  [Found: bd-abc 'Order Processing Architecture']
  bd list --label arch,component --parent bd-abc
  [Found: Order Orchestrator, Pricing Engine, Fulfillment Engine,
   Payment Gateway, Order Store]
  [ADRs: doc/arch/adr-001.md (isolate payment as independent axis)]

Claude dispatches codebase-investigator:
  [Evidence gathered: import graphs, co-change patterns, call patterns, shared state]

Claude runs 6 analysis passes:

Pass 3 (Temporal Coupling) finds:
  Pricing Engine and Fulfillment Engine changed together in 7 of last 10 commits.
  Graph shows relates_to edge but no blocks edge.

Pass 4 (Hidden Dependencies) finds:
  Order Store is accessed directly by Pricing Engine (imports order_store module)
  but graph shows no edge between them.

Pass 1 (Complection) finds nothing.
Pass 2 (Interface Analysis) finds nothing.
Pass 5 (Layer Violations) finds nothing.
Pass 6 (State/Identity) finds nothing.

Claude self-checks output:
  No recommendation keywords found. Neutral language confirmed.

Claude presents:

## Architectural Audit Report

**Graph:** Order Processing Architecture (bd-abc)
**Components audited:** 5
**Evidence sources:** graph + codebase
**ADRs reviewed:** 1

---

### Tensions Found

## Tension: Pricing-Fulfillment Co-Change Coupling
**Components:** Pricing Engine, Fulfillment Engine
**Analysis pass:** Temporal Coupling
**Pull 1:** Keep separate -- Gain: independent deployment of pricing
  and fulfillment logic. Cost: co-changes require coordinated updates
  across both components.
**Pull 2:** Merge into unified Order Engine -- Gain: co-changes become
  single-component updates. Cost: lose independent volatility isolation.
**If you assume:** pricing and fulfillment will eventually diverge in
  change frequency, then keeping them separate is correct.
**If you assume:** shipping costs will always affect final pricing (the
  current coupling pattern), then merging reduces coordination overhead.
**Structural observation:** Both components changed together in 7 of
  last 10 commits. relates_to edge exists but may understate the coupling.
**Evidence:** Git log shows co-changes in src/pricing/ and src/fulfillment/
  in commits abc123, def456, ghi789, ... (7 of 10 recent commits).

## Tension: Undeclared Pricing-Storage Dependency
**Components:** Pricing Engine, Order Store
**Analysis pass:** Hidden Dependencies
**Pull 1:** Add explicit edge (Pricing Engine blocks Order Store) --
  Gain: graph accurately reflects reality. Cost: Pricing Engine now has
  two dependencies (Orchestrator and Store), increasing its coupling.
**Pull 2:** Remove direct access (Pricing Engine reads data only through
  Orchestrator) -- Gain: Pricing Engine stays pure business logic with
  single dependency. Cost: Orchestrator becomes intermediary for data
  Pricing Engine needs.
**If you assume:** Pricing Engine's data needs are simple and can be
  passed by the Orchestrator, then removing direct access is correct.
**If you assume:** Pricing Engine requires complex queries against order
  history, then direct access through a declared edge is correct.
**Structural observation:** Pricing Engine imports from order_store module
  in 3 files. No graph edge exists between these components.
**Evidence:** src/pricing/calculator.rs:12 imports order_store::OrderRepo.
  src/pricing/discount.rs:5 imports order_store::OrderHistory.
  src/pricing/tax.rs:8 imports order_store::TaxRateCache.

### Accepted Tensions (Skipped)

- ADR-001: Isolate payment processing as independent volatility axis --
  covers Payment Gateway independence

### Drift Detected

None.

### Graph Summary

| Component | Layer | Stability | Tensions | Drift |
|-----------|-------|-----------|----------|-------|
| Order Orchestrator | Manager | exploring | 0 | no |
| Pricing Engine | Engine | exploring | 2 | no |
| Fulfillment Engine | Engine | exploring | 1 | no |
| Payment Gateway | Resource Accessor | exploring | 0 | no |
| Order Store | Resource Accessor | exploring | 1 | no |

### Audit Outcome

**Tensions found:** 2
**Accepted (via ADRs):** 1
**Drift detected:** 0
**Clean:** no

2 tensions require architect resolution. Options for each tension:
- Modify graph structure (run /decompose to restructure)
- Accept the tension (create ADR documenting the acceptance)
- Investigate further (dispatch codebase-investigator for deeper analysis)
</code>

<why_it_works>
- All 6 passes executed (even those with no findings)
- Tensions use exact structured format with both pulls
- No recommendations -- both options presented equally with gain/cost
- Conditional assumptions state when each pull is correct
- Structural observations use neutral facts (commit counts, import counts)
- ADR-001 recognized and its tension skipped
- Evidence is specific (file paths, line numbers, commit hashes)
- Self-check confirmed no recommendation language
</why_it_works>
</example>

<example>
<scenario>BAD -- Audit that makes recommendations and ranks severity</scenario>

<code>
Claude presents audit results:

## Audit Results

### Critical: Pricing-Fulfillment Coupling (HIGH SEVERITY)
The Pricing Engine and Fulfillment Engine are tightly coupled and should be
merged into a single component. This is the most pressing issue and should
be addressed first.

### Medium: Hidden Storage Dependency
Pricing Engine accesses Order Store directly, which is a violation. I recommend
adding an explicit edge or, better yet, routing all data access through the
Orchestrator. Consider changing the Pricing Engine to use a data transfer
object pattern.

### Low: Minor Interface Concern
The Order Orchestrator interface is slightly broad. This is a minor issue
that can be addressed later.
</code>

<why_it_fails>
- "Critical", "HIGH SEVERITY", "Medium", "Low" -- severity rankings are recommendations
  in disguise. They tell the architect what to care about, denying them judgment.
- "should be merged" -- direct recommendation. Audit presents both pulls, not solutions.
- "most pressing issue" -- prioritization = recommendation
- "should be addressed first" -- ordering = recommendation
- "I recommend" -- explicit recommendation
- "better yet" -- preference = recommendation
- "Consider changing" -- suggestion = recommendation
- "minor issue" -- severity assessment = recommendation
- "can be addressed later" -- prioritization = recommendation
- Missing: structured tension format, both pulls, conditional assumptions
- Missing: evidence references (file paths, commit data)
- Missing: self-check step (would have caught all of these keywords)
</why_it_fails>

<correction>
Apply self-check and rewrite every tension:

Self-check scan:
  "Critical" -> FOUND. Remove severity. Use structural observation.
  "HIGH SEVERITY" -> FOUND. Remove.
  "should be merged" -> FOUND. Rewrite as both pulls.
  "most pressing" -> FOUND. Remove ordering.
  "should be addressed first" -> FOUND. Remove prioritization.
  "I recommend" -> FOUND. Remove.
  "better yet" -> FOUND. Remove preference.
  "Consider changing" -> FOUND. Remove suggestion.
  "minor issue" -> FOUND. Remove severity.
  "can be addressed later" -> FOUND. Remove prioritization.

Corrected output:

## Tension: Pricing-Fulfillment Co-Change Coupling
**Components:** Pricing Engine, Fulfillment Engine
**Analysis pass:** Temporal Coupling
**Pull 1:** Keep separate -- Gain: independent volatility isolation.
  Cost: co-changes require coordinated updates.
**Pull 2:** Merge -- Gain: co-changes become single-component updates.
  Cost: lose independent deployment.
**If you assume:** pricing and fulfillment will diverge in change frequency,
  then keeping them separate is correct.
**If you assume:** they will continue changing together, then merging
  reduces coordination overhead.
**Structural observation:** Both components changed together in 7 of
  last 10 commits.
**Evidence:** Git log co-change analysis.

## Tension: Undeclared Pricing-Storage Dependency
**Components:** Pricing Engine, Order Store
**Analysis pass:** Hidden Dependencies
**Pull 1:** Add explicit graph edge -- Gain: graph reflects reality.
  Cost: increases Pricing Engine coupling.
**Pull 2:** Remove direct access, route through Orchestrator -- Gain:
  Pricing Engine stays pure. Cost: Orchestrator mediates all data.
**If you assume:** Pricing data needs are simple, then routing through
  Orchestrator is correct.
**If you assume:** Pricing needs complex queries, then direct access
  with declared edge is correct.
**Structural observation:** 3 files in src/pricing/ import from
  order_store module.
**Evidence:** src/pricing/calculator.rs:12, src/pricing/discount.rs:5,
  src/pricing/tax.rs:8.

No severity rankings. No ordering. Both pulls presented equally.
</correction>
</example>

<example>
<scenario>Good audit detecting ADR drift</scenario>

<code>
Claude loads graph and ADRs:
  ADR-001: "We will isolate payment processing into a dedicated Payment Gateway
  component. The Order Orchestrator will interact with payments only through
  this interface."

Claude dispatches codebase-investigator:
  Evidence: src/orders/checkout.rs:45 directly imports payment::charge_card()
  Evidence: src/orders/refund.rs:12 directly imports payment::process_refund()
  These bypass the Orchestrator and call Payment Gateway directly from order logic.

Claude runs analysis passes... Pass 4 (Hidden Dependencies) detects the drift.

Claude self-checks: no recommendation language found.

Claude presents:

## Architectural Audit Report

**Graph:** Order Processing Architecture (bd-abc)
**Components audited:** 5
**Evidence sources:** graph + codebase
**ADRs reviewed:** 1

---

### Tensions Found

None.

### Accepted Tensions (Skipped)

None.

### Drift Detected

## Drift: ADR-001 -- Isolate payment processing as independent volatility axis
**Declared:** "The Order Orchestrator will interact with payments only through
  [the Payment Gateway] interface." Order logic should not directly call
  payment functions.
**Observed:** Two files in src/orders/ directly import and call payment module
  functions, bypassing the Orchestrator.
**Evidence:**
  - src/orders/checkout.rs:45 -- `use payment::charge_card;`
  - src/orders/refund.rs:12 -- `use payment::process_refund;`
  - Both files are in the orders module (part of Order Orchestrator's domain)
    but call Payment Gateway directly instead of through the Orchestrator interface.

### Graph Summary

| Component | Layer | Stability | Tensions | Drift |
|-----------|-------|-----------|----------|-------|
| Order Orchestrator | Manager | exploring | 0 | yes |
| Pricing Engine | Engine | exploring | 0 | no |
| Fulfillment Engine | Engine | exploring | 0 | no |
| Payment Gateway | Resource Accessor | exploring | 0 | yes |
| Order Store | Resource Accessor | exploring | 0 | no |

### Audit Outcome

**Tensions found:** 0
**Accepted (via ADRs):** 0
**Drift detected:** 1
**Clean:** no

1 drift detected. The codebase has diverged from a declared architectural
decision. Options:
- Fix the code to match the ADR (restore the intended boundary)
- Supersede the ADR if the boundary is no longer appropriate
  (create new ADR documenting why the decision changed)
</code>

<why_it_works>
- Drift distinguished from tension -- drift is about ADR vs reality, not a new structural question
- Specific evidence: file paths and line numbers showing the violation
- No recommendation about which option to take (fix code vs supersede ADR)
- Options presented neutrally (both are valid responses to drift)
- ADR text quoted to show exactly what was declared
- Codebase evidence clearly shows the divergence
</why_it_works>
</example>

<example>
<scenario>BAD -- Audit that skips the self-check step</scenario>

<code>
Claude runs all 6 analysis passes and finds tensions.
Claude skips self-check ("output looks fine, no need to review").
Claude presents:

## Tension: Critical Orchestrator Overload
**Components:** Order Orchestrator
**Analysis pass:** Complection Scan
**Pull 1:** Split Orchestrator into domain-specific coordinators --
  Gain: each coordinator handles one workflow. Cost: more components.
**Pull 2:** Keep single Orchestrator -- Gain: single coordination point.
  Cost: Orchestrator grows with every new workflow.
**If you assume:** workflow count will stay low, single Orchestrator is fine.
**If you assume:** workflow count will grow, splitting prevents overload.
**Structural observation:** This is the most important tension to address
  as it affects the entire system's maintainability.

## Tension: Minor Interface Leak
**Components:** Pricing Engine, Order Store
**Analysis pass:** Interface Analysis
**Pull 1:** ...
**Pull 2:** ...
**Structural observation:** This is a low-priority concern that should be
  addressed after the Orchestrator issue.
</code>

<why_it_fails>
- Skipped self-check step: "output looks fine" is a rationalization
- "Critical" in tension name -- severity word that implies recommendation
- "most important tension to address" -- prioritization = recommendation
- "affects the entire system's maintainability" -- while factual-sounding,
  this is a severity assessment framing one tension as worse than another
- "Minor" in tension name -- severity word
- "low-priority concern" -- explicit priority ranking = recommendation
- "should be addressed after" -- ordering = recommendation
- Self-check would have caught ALL of these:
  - "Critical" -> remove severity word from title
  - "most important" -> remove prioritization
  - "Minor" -> remove severity word from title
  - "low-priority" -> remove
  - "should be addressed after" -> remove ordering
</why_it_fails>

<correction>
Run self-check BEFORE presenting:

Self-check scan:
  Title "Critical Orchestrator Overload" -> "Orchestrator Overload" (remove severity)
  "most important tension to address" -> REMOVE (prioritization)
  "affects the entire system's maintainability" -> rewrite: "Orchestrator
    is upstream of all 4 other components" (structural observation)
  Title "Minor Interface Leak" -> "Interface Leak" (remove severity)
  "low-priority concern" -> REMOVE (prioritization)
  "should be addressed after" -> REMOVE (ordering)

Corrected output:

## Tension: Orchestrator Scope Growth
**Components:** Order Orchestrator
**Analysis pass:** Complection Scan
**Pull 1:** Split into domain-specific coordinators -- Gain: each coordinator
  handles one workflow. Cost: more components and interfaces.
**Pull 2:** Keep single Orchestrator -- Gain: single coordination point.
  Cost: grows with every new workflow.
**If you assume:** workflow count stays manageable, single Orchestrator is correct.
**If you assume:** workflow count grows significantly, splitting reduces per-coordinator complexity.
**Structural observation:** Orchestrator has edges to all 4 other components.
  Currently coordinates 3 workflows (order, refund, exchange).
**Evidence:** Graph shows 4 blocks edges from Orchestrator.

## Tension: Pricing-Storage Interface Leak
**Components:** Pricing Engine, Order Store
**Analysis pass:** Interface Analysis
**Pull 1:** ...
**Pull 2:** ...
**Structural observation:** 2 internal data types from Order Store appear
  in Pricing Engine's imports.
**Evidence:** src/pricing/calculator.rs imports OrderRecord and TaxCache
  (internal Order Store types).

No severity words. No ordering. No prioritization. Both tensions
presented as structural observations for the architect to evaluate.
</correction>
</example>

</examples>

<critical_rules>
## Rules That Have No Exceptions

1. **NO recommendations.** Both pulls presented equally. Never say "should", "recommend", "better", "prefer", or "consider changing". If you catch yourself writing one, rewrite to neutral structural observation.

2. **NO severity rankings.** Never use "critical", "high", "medium", "low", "severe", "minor", "urgent", or "important" to describe tensions. Use structural observations: "affects N downstream nodes", "both components changed together in N commits", "3 files import across this boundary".

3. **NO ordering or prioritization.** Never say "address first", "most pressing", "primary concern", or "should be resolved before". All tensions presented without implied priority.

4. **Run self-check EVERY TIME.** Scan all output for recommendation, severity, and ordering keywords before presenting. This step is mandatory and non-negotiable. "Output looks fine" is a rationalization for skipping it.

5. **Run ALL 6 passes.** Never skip a pass, even if early passes found nothing. Each pass looks for a different category of problem. Skipping passes misses problems.

6. **ANALYTICAL, not Socratic.** No AskUserQuestion during analysis. Load graph, gather evidence, run passes, present report. The architect reads and decides.

7. **ADR-aware.** Read existing ADRs before analysis. Skip tensions that match accepted ADR decisions. Report drift when codebase contradicts ADRs.

8. **Dispatch codebase-investigator when codebase exists.** Evidence from the codebase feeds ALL 6 analysis passes, not just drift detection. Never skip codebase investigation when there is code to examine.

9. **Use structured tension format.** Every tension follows the exact format: tension name, components, analysis pass, Pull 1 (gain/cost), Pull 2 (gain/cost), conditional assumptions, structural observation, evidence. No free-form commentary.

10. **Think in components and boundaries, NOT classes and functions.** If the analysis descends to implementation details (class hierarchies, function signatures), you have crossed into inner-loop territory. Stay at the component level.

## Common Excuses

All of these mean: **STOP. Follow the process.**

- "This tension is obviously more important" (You are recommending. Present both pulls equally.)
- "Output looks fine, skip self-check" (Self-check exists because output never looks fine on first pass.)
- "Only 2 passes are relevant here" (Run all 6. The passes you skip are where surprises hide.)
- "No need for codebase investigation, graph is clear" (Graph is declared intent. Codebase is reality. Always check.)
- "I can see which pull is correct" (Your job is to present, not to judge. The architect decides.)
- "The severity is objectively higher" (There is no objective severity. There are structural observations.)
- "Self-check is redundant, I was careful" (Careful people still write recommendation language unconsciously.)
</critical_rules>

<verification_checklist>
Before presenting the audit report:

- [ ] Architecture graph loaded from bd (epic + all component nodes + edges)
- [ ] Existing ADRs read (or noted as absent)
- [ ] Codebase-investigator dispatched (if codebase exists)
- [ ] Evidence gathered covers: module structure, imports, co-change, call patterns, interfaces, shared state
- [ ] All 6 analysis passes executed (complection, interfaces, temporal coupling, hidden deps, layer violations, state/identity)
- [ ] Accepted ADR tensions skipped with note
- [ ] Drift detected where ADRs contradict codebase evidence
- [ ] Every tension uses structured format (name, components, pass, both pulls, assumptions, observation, evidence)
- [ ] Self-check completed: no recommendation keywords in output
- [ ] Self-check completed: no severity rankings in output
- [ ] Self-check completed: no ordering/prioritization in output
- [ ] Structural observations use neutral facts (counts, affected nodes, file paths)
- [ ] Component stability states updated for clean components
- [ ] No implementation-level detail (classes, functions, data structures)
- [ ] Report includes graph summary table and audit outcome

**Can't check all boxes?** Return to the relevant step and complete it.
</verification_checklist>

<integration>
**This skill calls:**
- hyperpowers:codebase-investigator (when codebase exists -- gathers evidence for all 6 passes)

**This skill is called by:**
- User (via /hyperpowers:audit-arch command)
- After /decompose creates or revises an architecture graph
- Periodic architecture health checks
- Before inner-loop handoff of stable nodes

**Call chain:**
```
OUTER LOOP:
  /decompose -> /audit-arch -> architect resolves tensions
       |              |              |
       v              v              v
  graph (bd)    tension report    ADRs (repo) or graph changes

RESOLUTION:
  tension -> /decompose (restructure) or ADR (accept)

HANDOFF (all tensions resolved/accepted):
  stable node -> /brainstorm (auto-loads arch context)
```

**Agents used:**
- codebase-investigator (gather module structure, imports, co-change, call patterns, interfaces, shared state)
- NO internet-researcher (audit uses only graph + codebase evidence)

**Tools required:**
- bd CLI (load graph, update stability states)
- Read (load ADR files)

**Artifacts consumed:**
- bd architecture epic + component nodes (from /decompose)
- ADR files in doc/arch/ (from /decompose or manual creation)

**Artifacts produced:**
- Tension report (presented to architect, not persisted)
- Drift report (presented to architect, not persisted)
- Updated stability states on clean components (in bd)
</integration>

<resources>
**Detailed guides:**
- [ADR template and examples](../common-patterns/adr-template.md)
- [bd command reference](../common-patterns/bd-commands.md)
- [Common anti-patterns](../common-patterns/common-anti-patterns.md)
- [Common rationalizations](../common-patterns/common-rationalizations.md)

**Hickey's simplicity framework:**
- Simple Made Easy (Rich Hickey) -- complection detection, simple vs easy
- Are We There Yet? (Rich Hickey) -- state, identity, value separation
- Hammock-Driven Development (Rich Hickey) -- think deeply before acting

**Lowy's layer rules (used in Pass 5):**
- Manager (orchestration) -> Engine (business logic) -> Resource Accessor (data) -> Utility (cross-cutting)
- No upward dependencies
- Managers have no business logic
- Engines do not access resources directly
- Resource Accessors do not contain business rules

**When stuck:**
- Graph has many components -> Work through passes systematically, one component pair at a time
- Codebase evidence contradicts graph -> Report as drift if ADR exists, as tension if not
- Unsure if something is a tension -> If two pulls exist with legitimate gains/costs, it is a tension
- Output has recommendation language -> Self-check caught it. Rewrite to neutral observation.
- No codebase exists -> Run with graph evidence only, note the limitation in the report
</resources>
