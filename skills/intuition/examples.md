# Intuition Examples

Worked examples for the intuition skill. Read these only when you need a concrete reference — the SKILL.md file has the full process.

The five examples cover:
1. Good audit with architecture model (order processing, finds 2 tensions)
2. Good audit without architecture model (codebase-only, finds 3 tensions)
3. BAD — audit that makes recommendations and ranks severity (with self-check correction)
4. Good audit detecting ADR drift (no tensions, 1 drift)
5. BAD — audit that skips the self-check step (with self-check correction)

<examples>

<example>
<scenario>Good audit finding real tensions in an order processing architecture (with architecture model)</scenario>

<code>
Claude loads architecture model:
  ls docs/arch/*.c4
  [Found: spec.c4, model.c4, components/*.c4]
  Queries LikeC4 MCP: read-project-summary, read-element for each
  [Found: Order Orchestrator, Pricing Engine, Fulfillment Engine,
   Payment Gateway, Order Store]
  [ADRs: docs/arch/adr/adr-001.md (isolate payment as independent component)]

Claude dispatches codebase-investigator:
  [Evidence gathered: import graphs, co-change patterns, call patterns, shared state]

Claude runs 9 analysis passes:

Pass 3 (Temporal Coupling) finds:
  Pricing Engine and Fulfillment Engine changed together in 7 of last 10 commits.
  Model shows relates_to edge but no blocks edge.

Pass 4 (Hidden Dependencies) finds:
  Order Store is accessed directly by Pricing Engine (imports order_store module)
  but model shows no edge between them.

Pass 1 (Complection) finds nothing.
Pass 2 (Interface Analysis) finds nothing.
Pass 5 (Structural Dependency Direction) finds nothing.
Pass 6 (State/Identity) finds nothing.
Pass 7 (Rate-of-Change Mismatch) finds nothing.
Pass 8 (Workaround Cascade) finds nothing.
Pass 9 (Mechanism Bypass) skipped — no cascades from Pass 8.

Claude self-checks output:
  No recommendation keywords found. Neutral language confirmed.

Claude presents:

## Architectural Intuition Report

**Focus:** full audit (no focus provided)
**Model:** Order Processing Architecture
**Components audited:** 5
**Modules analyzed:** 5
**Evidence sources:** model + codebase
**ADRs reviewed:** 1
**Dynamic views checked:** 0

---

### Tensions Found

## Tension: Pricing-Fulfillment Co-Change Coupling
**Components/Modules:** Pricing Engine, Fulfillment Engine
**Analysis pass:** Temporal Coupling
**Pull 1:** Keep separate -- Gain: independent deployment of pricing
  and fulfillment logic. Cost: co-changes require coordinated updates
  across both components.
**Pull 2:** Merge into unified Order Engine -- Gain: co-changes become
  single-component updates. Cost: lose independent change isolation.
**If you assume:** pricing and fulfillment will eventually diverge in
  change frequency, then keeping them separate is correct.
**If you assume:** shipping costs will always affect final pricing (the
  current coupling pattern), then merging reduces coordination overhead.
**Structural observation:** Both components changed together in 7 of
  last 10 commits. relates_to edge exists but may understate the coupling.
**Evidence:** Git log shows co-changes in src/pricing/ and src/fulfillment/
  in commits abc123, def456, ghi789, ... (7 of 10 recent commits).

## Tension: Undeclared Pricing-Storage Dependency
**Components/Modules:** Pricing Engine, Order Store
**Analysis pass:** Hidden Dependencies
**Pull 1:** Add explicit edge — Gain: model reflects reality. Cost: Pricing Engine gains a second dependency.
**Pull 2:** Remove direct access, route through Orchestrator — Gain: Pricing Engine stays pure. Cost: Orchestrator mediates all data.
**If you assume:** Pricing data needs are simple, routing through Orchestrator is correct.
**If you assume:** Pricing requires complex queries, direct access with declared edge is correct.
**Structural observation:** Pricing Engine imports from order_store module in 3 files. No model edge exists.
**Evidence:** src/pricing/calculator.rs:12, src/pricing/discount.rs:5, src/pricing/tax.rs:8.

### Accepted Tensions (Skipped)

- ADR-001: Isolate payment processing as independent component --
  covers Payment Gateway independence

### Drift Detected

None.

### Module Summary

| Component/Module | Tensions | Notes |
|------------------|----------|-------|
| Order Orchestrator | 0 | |
| Pricing Engine | 2 | |
| Fulfillment Engine | 1 | |
| Payment Gateway | 0 | |
| Order Store | 1 | |

### Audit Outcome

**Tensions found:** 2
**Accepted (via ADRs):** 1
**Drift detected:** 0
**Clean:** no

2 tensions require architect resolution. Options for each tension:
- Accept the tension (create ADR documenting the acceptance)
- Create ADR + bd ticket to restructure
- Investigate further (dispatch codebase-investigator for deeper analysis)
</code>

<why_it_works>
- All 9 passes executed (even those with no findings)
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
<scenario>Good audit — codebase only, no architecture model</scenario>

<code>
Claude checks for model:
  ls docs/arch/*.c4
  [No .c4 files found]

Claude announces:
  "No architecture model found. Running codebase-only audit to find
  structural tensions from empirical observation of the code."

Claude checks for ADRs:
  ls docs/arch/adr/adr-*.md
  [No ADRs found]

Claude dispatches codebase-investigator (Step 1a):
  [Evidence: 4 top-level modules — api/, core/, storage/, utils/
   api/ imports from core/ and storage/
   core/ imports from storage/ and utils/
   storage/ imports from utils/
   BUT: storage/cache.rs imports from api/middleware (upward dependency)
   Co-change: api/ and core/ change together in 8 of 12 recent commits]

Claude dispatches codebase-investigator (Step 1b — data flows):
  [Evidence: POST /orders flows through api/ -> core/ -> storage/
   GET /reports flows through api/ -> storage/ directly (bypasses core/)
   storage/cache.rs calls api/middleware::get_auth_context() for cache key]

Claude runs 9 analysis passes:

Pass 3 (Temporal Coupling):
  api/ and core/ changed together in 8 of 12 recent commits.

Pass 4 (Hidden Dependencies):
  GET /reports bypasses core/ — api/ accesses storage/ directly.

Pass 5 (Structural Dependency Direction):
  storage/cache.rs imports from api/middleware — lower abstraction
  depends on higher abstraction.

Pass 7 (Rate-of-Change Mismatch):
  Analyzed 45 commits (excluded 3 bulk, 2 generated-only, 1 manifest-only).
  api/ changed 30 times, utils/ changed 2 times — but they share no boundary,
  no tension. core/ and storage/ both changed ~15 times — no mismatch within
  any shared boundary.

Passes 1, 2, 6: nothing found.
Pass 8 (Workaround Cascade): nothing found.
Pass 9 (Mechanism Bypass): skipped — no cascades from Pass 8.

Claude self-checks: no recommendation language found.

Claude presents:

## Architectural Intuition Report

**Focus:** full audit (no focus provided)
**Model:** none — codebase-only audit
**Components audited:** N/A — no model
**Modules analyzed:** 4 (api, core, storage, utils)
**Evidence sources:** codebase only
**ADRs reviewed:** none found

---

### Tensions Found

## Tension: API-Core Co-Change Coupling
**Components/Modules:** api/, core/
**Analysis pass:** Temporal Coupling
**Pull 1:** Keep separate — Gain: API layer handles HTTP concerns
  independently from business logic. Cost: changes frequently span both.
**Pull 2:** Merge API routing into core — Gain: co-changes become
  single-module updates. Cost: HTTP concerns braided with business logic.
**If you assume:** the coupling is incidental (current feature work touches
  both), keeping separate is correct.
**If you assume:** API and core are structurally entangled (core shapes
  the API surface), merging reduces coordination.
**Structural observation:** Both modules changed together in 8 of 12
  recent commits.
**Evidence:** Git log co-change analysis across recent commits.

## Tension: Reports Bypass Core
**Components/Modules:** api/, storage/
**Analysis pass:** Hidden Dependencies
**Pull 1:** Route reports through core/ — Gain: centralized business logic. Cost: extra indirection.
**Pull 2:** Accept direct api/ -> storage/ for reads — Gain: simpler path. Cost: two access patterns.
**If you assume:** reports will gain business logic, routing through core is correct.
**If you assume:** reports remain pure reads, direct access is correct.
**Structural observation:** GET /reports: api/ -> storage/ (bypasses core/). POST /orders: api/ -> core/ -> storage/.
**Evidence:** Step 1b data flow trace.

## Tension: Storage-to-API Upward Dependency
**Components/Modules:** storage/cache.rs, api/middleware
**Analysis pass:** Structural Dependency Direction
**Pull 1:** Move auth context to utils/ — Gain: storage/ no longer depends on api/. Cost: cross-cutting concern.
**Pull 2:** Pass auth context as parameter — Gain: explicit direction. Cost: function signatures grow.
**If you assume:** auth context is cross-cutting, utils/ is correct.
**If you assume:** auth context is request-scoped, passing as parameter is correct.
**Structural observation:** storage/cache.rs (lower abstraction) imports from api/middleware (higher abstraction).
**Evidence:** storage/cache.rs:15 — `use api::middleware::get_auth_context;`

### Accepted Tensions (Skipped)

None (no ADRs found).

### Drift Detected

None (no ADRs to drift from).

### Module Summary

| Component/Module | Tensions | Notes |
|------------------|----------|-------|
| api/ | 2 | |
| core/ | 1 | |
| storage/ | 2 | |
| utils/ | 0 | |

### Audit Outcome

**Tensions found:** 3
**Accepted (via ADRs):** 0
**Drift detected:** 0
**Clean:** no

3 tensions require architect resolution. Options for each tension:
- Accept the tension (create ADR documenting the acceptance)
- Create ADR + bd ticket to restructure
- Investigate further (dispatch codebase-investigator for deeper analysis)
</code>

<why_it_works>
- Audit without architecture model correctly identified and announced
- All 9 passes executed (Pass 7 ran with filtering stats, Pass 8 ran with no cascades found, Pass 9 correctly skipped)
- Tensions found from codebase evidence alone — no model needed
- Pass 5 caught upward dependency without needing layer vocabulary
- Pass 7 reported filtering stats and found no mismatches within shared boundaries
- Structural observations use neutral facts
- No recommendations — both pulls presented equally
- Report format correctly adapted for audit without model
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
**Components/Modules:** Pricing Engine, Fulfillment Engine
**Analysis pass:** Temporal Coupling
**Pull 1:** Keep separate -- Gain: independent change isolation.
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

No severity rankings. No ordering. Both pulls presented equally.
(Second tension rewritten similarly — no severity, both pulls, structural observation.)
</correction>
</example>

<example>
<scenario>Good audit detecting ADR drift</scenario>

<code>
Claude loads model and ADRs:
  ADR-001: "We will isolate payment processing into a dedicated Payment Gateway
  component. The Order Orchestrator will interact with payments only through
  this interface."

Claude dispatches codebase-investigator:
  Evidence: src/orders/checkout.rs:45 directly imports payment::charge_card()
  Evidence: src/orders/refund.rs:12 directly imports payment::process_refund()
  These bypass the Orchestrator and call Payment Gateway directly from order logic.

Claude runs 9 analysis passes... Pass 4 (Hidden Dependencies) detects the drift.

Claude self-checks: no recommendation language found.

Claude presents:

## Architectural Intuition Report

**Focus:** full audit (no focus provided)
**Model:** Order Processing Architecture
**Components audited:** 5
**Modules analyzed:** 5
**Evidence sources:** model + codebase
**ADRs reviewed:** 1
**Dynamic views checked:** 0

---

### Tensions Found

None.

### Accepted Tensions (Skipped)

None.

### Drift Detected

## Drift: ADR-001 -- Isolate payment processing as independent component
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

### Module Summary

| Component/Module | Tensions | Notes |
|------------------|----------|-------|
| Order Orchestrator | 0 | drift: ADR-001 |
| Pricing Engine | 0 | |
| Fulfillment Engine | 0 | |
| Payment Gateway | 0 | drift: ADR-001 |
| Order Store | 0 | |

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
Claude runs all 9 analysis passes and finds tensions.
Claude skips self-check ("output looks fine, no need to review").
Claude presents:

## Tension: Critical Orchestrator Overload
**Components/Modules:** Order Orchestrator
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
**Components/Modules:** Pricing Engine, Order Store
**Analysis pass:** Interface Analysis
**Pull 1:** ...
**Pull 2:** ...
**Structural observation:** This is a low-priority concern that can be
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
- "can be addressed after" -- ordering = recommendation
- Self-check would have caught ALL of these:
  - "Critical" -> remove severity word from title
  - "most important" -> remove prioritization
  - "Minor" -> remove severity word from title
  - "low-priority" -> remove
  - "can be addressed after" -> remove ordering
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
  "can be addressed after" -> REMOVE (ordering)

Corrected output:

## Tension: Orchestrator Scope Growth
**Components/Modules:** Order Orchestrator
**Analysis pass:** Complection Scan
**Pull 1:** Split into domain-specific coordinators -- Gain: each coordinator
  handles one workflow. Cost: more components and interfaces.
**Pull 2:** Keep single Orchestrator -- Gain: single coordination point.
  Cost: grows with every new workflow.
**If you assume:** workflow count stays manageable, single Orchestrator is correct.
**If you assume:** workflow count grows significantly, splitting reduces per-coordinator complexity.
**Structural observation:** Orchestrator has edges to all 4 other components.
  Currently coordinates 3 workflows (order, refund, exchange).
**Evidence:** Model shows 4 blocks edges from Orchestrator.

No severity words. No ordering. No prioritization.
(Second tension rewritten similarly — "Interface Leak", no severity, structural observation only.)
</correction>
</example>

</examples>
