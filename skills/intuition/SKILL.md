---
name: intuition
description: "Brand-informed empirical audit of architecture — finds complection, coupling, shearing layer mismatches, workaround cascades, mechanism bypass, and drift through structured observation of codebase and model"
---

<skill_overview>
Examine an architecture model (if one exists) and codebase for complection, hidden coupling, temporal coupling, structural dependency violations, state/identity conflation, rate-of-change mismatches, workaround cascades, and mechanism bypass using Hickey's simplicity framework and Brand's empirical observation. Produce a structured tension report that surfaces both pulls of every tension without resolving them. The architect reads the report and decides.

When no architecture model exists, run a codebase-only audit to find tensions in raw code structure. Dynamic view drift (model view vs actual code path) is checked via /ponder REVIEW.
</skill_overview>

<rigidity_level>
RIGID - Same 9 analysis passes every time (Passes 1-9), same output format, same self-check procedure. No adaptation, no shortcuts, no skipping passes. The analytical rigor IS the value. When no architecture model exists, model-level analysis produces "evidence insufficient — codebase only" outputs (not skipped) — the audit still finds real tensions.
</rigidity_level>

<quick_reference>
| Step | Action | Deliverable |
|------|--------|-------------|
| 0 | Detect model (load if present); load ADRs (with age check); accept optional prose focus | Evidence sources identified; prose focus recorded if provided |
| 1 | Gather evidence (codebase-investigator) | Module structure, imports, co-change data; request paths and undeclared flows |
| 2 | Run 9 analysis passes | Raw tension findings (Passes 1-9) |
| 3 | Self-check + present | Tension report (no recommendations) |
| 4 | Resolution protocol (interactive) | Per-tension resolution: accept / resolve / brainstorm / investigate |

**Key:** Steps 0-3 are ANALYTICAL. No AskUserQuestion during analysis. Load, analyze, report.
**Key:** Step 4 is INTERACTIVE. Walk through each tension with the architect.
**Key:** Tensions surface both pulls. NO recommendations, NO severity rankings.
</quick_reference>

<when_to_use>
- When friction suggests structural mismatch — something feels wrong but you cannot articulate why
- Periodic health check on an existing architecture
- When brainstorming suggests architectural investigation before designing
- After significant implementation: check for drift from declared intent
- Before a major feature: understand current structural tensions

**Don't use for:**
- Inner-loop feature work (use hyperpowers:brainstorming)
- Bug fixes (use hyperpowers:fixing-bugs)
- Refactoring (use hyperpowers:refactoring-safely)
</when_to_use>

<the_process>

## Step 0 -- Prepare Audit

**Announce:** "I'm using the intuition skill to examine your architecture for complection, coupling, and structural tensions."

### Optional: Prose Focus

Invoker may provide free-form prose (1-3 sentences typical) describing the audit focus, e.g., "Examine the auth/payments boundary for tensions this design might interact with." The prose focus is used to (a) target the codebase-investigator dispatch in Step 1 and (b) filter the tension report in Step 3 — see those steps for specifics.

Default (no prose focus): full audit. All tensions reported; no filtering.

**Check for architecture model:**

```bash
ls docs/arch/*.c4 2>/dev/null
```

**If model exists:**
- Validate syntax: `likec4 validate docs/arch/`. If validation fails, report errors and halt — MCP queries against an invalid model produce unreliable results.
- Load via LikeC4 MCP (REQUIRED — if MCP not available, fail with: "LikeC4 MCP server required. Run: likec4 mcp --stdio"):
  ```
  read-project-summary         # overview
  search-element (by kind or name)
  read-element <element-id>    # for each component
  find-relationships <element-id>
  read-view <view-id>          # for each view in docs/arch/views/data-flows/
  ```
- Record components, relationships, and dynamic views for analysis.
- If no landscape view exists, soft-warn: "No landscape view found. Consider running /ponder to create one." (audit proceeds regardless)

**If no model exists:** announce: "No architecture model found. Audit will use codebase evidence only." Continue.

**Read existing ADRs** (regardless of model presence):

```bash
ls docs/arch/adr/adr-*.md 2>/dev/null
```

For each ADR: read the file; record decision title, status, what was decided, consequences, last-modified date. These are used to: skip already-accepted tensions, detect drift, flag stale ADRs.

**ADR age check:** For each accepted ADR, check when it was last modified:
```bash
git log -1 --format="%ai" -- docs/arch/adr/adr-NNN.md
```
If an ADR has not been modified in 6+ months, flag it as a maintenance note in the report (not a tension): "ADR-NNN: [title] — last updated [date] (6+ months ago, consider reviewing)"

If no ADRs exist, note "no ADRs found" and proceed.

---

## Step 1 -- Gather Evidence

**This step is ANALYTICAL. No AskUserQuestion. Gather evidence silently.**

**Dispatch `hyperpowers:codebase-investigator`** with a comprehensive prompt that gathers evidence for ALL analysis passes.

**If a prose focus was provided in Step 0**, prepend to the dispatch prompt:
> "Focus this investigation on: [prose focus verbatim]. Apply the standard module-level investigation but prioritize evidence relevant to the focus area."
If no prose focus, dispatch with the standard prompt unchanged.

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
   - Any imports that cross what appear to be abstraction boundaries

3. CO-CHANGE PATTERNS
   - Files or modules that frequently change together in recent commits
   - Changes that span multiple modules (cross-cutting modifications)
   - Any modules that appear independent in structure but coupled in change history

4. ACTUAL CALL PATTERNS
   - How modules actually interact at runtime (function calls, message passing, events)
   - Any interactions not visible in the import graph (dynamic dispatch, reflection,
     shared configuration, environment variables)
   - Any upward calls (lower-abstraction module calling higher-abstraction module)

5. INTERFACE SURFACE AREA
   - What each module exports (public API) vs what it keeps internal
   - Interfaces that seem too broad (exposing internal implementation details)
   - Interfaces that carry multiple concerns (one API serving unrelated purposes)

6. SHARED STATE
   - Global variables, singletons, shared mutable state between modules
   - Configuration that multiple modules depend on
   - Any state that creates hidden coupling between otherwise independent modules

7. COMPENSATING CODE PATTERNS
   - Special-case filters, exception lists, or conditional branches that handle
     one subsystem differently from all others
   - Adapter or translation layers between components that should speak the
     same interface
   - Code whose purpose is to suppress, filter, or work around effects from
     a specific code path rather than to deliver end-user value

8. FIX CLUSTERING (from git history)
   - Clusters of related fixes in the same area within short time windows
     (e.g., 3+ related commits in the same module within 2 weeks)
   - Areas where commit messages reference workarounds, fixes for side effects,
     or handling special cases
```

**If no codebase exists (design-phase model only):** Skip this step. Analysis will use only model evidence. Note in the report: "Audit based on model evidence only — no codebase to verify against."

Record all evidence for use in Step 2.

**Step 1b -- Data flow investigation (skip if no codebase):**

After the structural investigation above returns results, dispatch a second `hyperpowers:codebase-investigator` to gather data flow evidence, using the structural findings and the architecture model (if available) to target questions precisely.

```
Based on these structural findings: [include Step 1a results]
[If model is loaded, also include: elements and relationships from LikeC4 MCP]

Trace data flows at module level:
1. For each entry point in the codebase, trace the request path through modules. Which modules participate in each request path?
2. Identify data flows between modules that suggest implicit structural relationships.
   [When model is loaded: note flows with no declared relationship in the architecture model (undeclared flows).]
3. Identify implicit ordering: which modules must process data before others?
   [When model is loaded: note whether this ordering is captured in the model relationships.]

Report at module level. [When model is loaded: reference LikeC4 element names where modules map to components.]
```

The flow evidence from Step 1b feeds into passes 1, 3, 4, and 9 — it does NOT replace the structural evidence from Step 1a.

---

## Step 2 -- Run 10 Analysis Passes

Run each pass using whatever evidence is available. When an architecture model is loaded, both model-level and codebase-level analysis run. When no model is loaded, model-level analysis produces zero tensions with note "evidence insufficient — codebase only" and codebase-level analysis still runs. Each pass may produce zero or more tensions.

**Before recording a tension:** Check if an existing ADR already accepts this tension. If an accepted ADR covers the exact structural choice, skip the tension and note: "Accepted via ADR-NNN: [title]".

### Pass 1: Complection Scan

**What to look for:** Concerns braided together that should be independent.

**Model evidence (when model is loaded):**
- Components whose responsibility description mentions multiple unrelated concerns
- Components that appear in edges for unrelated interaction types

**Codebase evidence:**
- Modules that import from multiple unrelated domains
- Files that contain logic for multiple independent concerns
- Functions that combine data access, business logic, and orchestration

**Flow evidence (from Step 1b, when available):**
- Modules that participate in request paths for multiple unrelated features (a module appearing in both the checkout path and the reporting path participates in independent concerns)
- Request paths that pass through a single module for unrelated reasons

**Tension pattern:** "[Component/Module] braids [Concern A] and [Concern B]"

### Pass 2: Interface Analysis

**What to look for:** Interfaces that carry more than one concern or leak implementation details.

**Model evidence (when model is loaded):**
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

**Model evidence (when model is loaded):**
- Components that interact (relates_to) but have no sequencing (no blocks edge)
- Initialization order dependencies not captured in the model
- Components whose interface contracts imply ordering ("call X before Y")

**Codebase evidence:**
- Co-change patterns: modules that always change together suggest coupling
- Initialization sequences that break if reordered
- Event handlers that assume specific execution order

**Flow evidence (from Step 1b, when available):**
- Request paths where module A must process data before module B, but no blocks edge exists between the corresponding model nodes (when model is loaded)
- Implicit ordering derived from data flow direction that is not captured in declared relationships (when model is loaded) or that suggests undocumented dependencies (when no model)

**Tension pattern:** "[A] and [B] have implicit ordering dependency not captured in [model/code structure]"

### Pass 4: Hidden Dependencies

**What to look for:** Dependencies that exist but are not visible in declared structure.

**Model evidence (when model is loaded):**
- Components with no declared dependencies that seem like they should have some
- Missing edges between components that clearly interact
- Components that share concepts (similar vocabulary in their descriptions) without a declared relationship

**Codebase evidence:**
- Actual imports/calls between modules not reflected in model edges (when model is loaded) or not obvious from module structure (when no model)
- Shared configuration or environment variables creating invisible coupling
- Dynamic dispatch or event systems hiding concrete dependencies
- Shared data formats or schemas without explicit interface contracts

**Flow evidence (from Step 1b, when available):**
- Data flows between modules that map to model nodes with no declared edge (when model is loaded)
- Undeclared flows that only become visible when tracing request paths end-to-end

**Tension pattern:** "[A] depends on [B] through [mechanism] but [model shows no relationship / dependency is not structurally visible]"

### Pass 5: Structural Dependency Direction

**What to look for:** Dependencies that flow upward from lower-abstraction modules toward higher-abstraction modules — violations of one-way dependency flow.

The principle: dependencies should flow from orchestration (higher abstraction) toward data access and infrastructure (lower abstraction). When lower-abstraction modules call or import from higher-abstraction modules, the dependency direction creates coupling that makes independent change difficult.

**Model evidence (when model is loaded):**
- Edges where a lower-abstraction component depends on a higher-abstraction component
- Orchestration components that contain business logic (should only coordinate)
- Data access components that contain business rules (should only access data)
- Infrastructure/utility components that depend on domain-specific components

**Codebase evidence:**
- Imports that go upward in the abstraction hierarchy (data modules importing from orchestration modules, utility modules importing from domain modules)
- Business logic found in orchestration or data access modules
- Data access code found in business logic modules
- Domain-specific code in utility/infrastructure modules

**Tension pattern:** "[A] (lower abstraction) depends on [B] (higher abstraction) — upward dependency"

### Pass 6: State/Identity Conflation

**What to look for:** Mutable shared state, identity used where value would suffice.

**Model evidence (when model is loaded):**
- relates_to edges that represent shared mutable state (not just interaction)
- Components that both read and write the same state
- Identity-based references where value-based would decouple

**Codebase evidence:**
- Global mutable state accessed by multiple modules
- Singletons that carry mutable state between components
- Object identity used for comparison where value equality would work
- Caches or registries that create hidden state dependencies

**Tension pattern:** "[A] and [B] share mutable state [S] creating hidden coupling"

### Pass 7: Rate-of-Change Mismatch (Brand's Shearing Layers)

**What to look for:** Modules within the same component that change at significantly different rates — empirical evidence that shearing layers are misaligned with component boundaries.

**Skip if:** fewer than 10 non-filtered commits in the repository. **Warn if:** shallow clone detected (fewer than 100 commits available) — results may be unreliable.

**Step 7a — Gather change frequency data:**

Dispatch `hyperpowers:codebase-investigator` with:
```
Analyze git history to determine change frequency per module/directory.

NOISE FILTERING (apply all before counting):
1. Exclude commits touching 50+ files (bulk operations like renames, migrations)
2. Exclude changes to generated files: *.lock, *.generated.*, dist/, build/, vendor/, node_modules/
3. Exclude commits whose message matches: /^(rename|migrate|bulk|refactor all|chore: bump|update deps)/i
4. Exclude dependency-manifest-only commits (e.g., commits that touch only package.json, Cargo.toml, go.mod without any source file changes)

After filtering, for each top-level module/directory:
- Count how many commits touched files in that module in the last 6 months
- Report the total commit count before and after filtering

Output format:
- "Analyzed N commits (excluded M bulk, K generated-only, J manifest-only)"
- Per-module change counts, sorted by frequency
- Flag any modules where ALL commits were filtered out (report as "no signal after filtering")
```

**Check for insufficient history:**
- `git rev-list --count HEAD` — if fewer than 10: skip Pass 7 entirely, note "Insufficient commit history for rate-of-change analysis (N commits). Pass 7 skipped."
- If fewer than 100: warn "Shallow history (N commits) — rate-of-change analysis may be unreliable."

**Step 7b — Identify mismatches:**

Compare change frequencies of modules that belong to the same component (when model is loaded) or that share the same parent directory / apparent boundary (when no model).

**Model evidence (when model is loaded):**
- Modules mapped to the same component that change at dramatically different rates (e.g., one module changed 30 times, another changed 2 times, both inside the same component boundary)
- Components whose described scope spans modules with divergent change rates

**Codebase evidence:**
- Modules under the same parent directory with significantly different change counts (use 5:1 ratio as a signal — e.g., 25 changes vs 5 changes)
- Co-located modules where one is effectively stable and another is highly active

**Tension format (same structure as Passes 1-6, with quantitative evidence):**
```
Name: Rate-of-change mismatch between [A] and [B]
Components: [A] (fast: N commits/month), [B] (slow: M commits/month)
Analysis Pass: 7 — Rate-of-Change Mismatch (Brand's Shearing Layers)
Pull A: Keep coupled — simpler architecture, fewer interfaces
Pull B: Decouple — let [A] move at its natural rate without dragging [B]
If you assume: [A]'s rate will slow as the feature stabilizes, coupling is temporary
If you assume: [A]'s rate reflects a real shearing layer, coupling is structural
Structural observation: [N] co-changes in last [period] where [A] changed independently [M] times
Evidence: [from git history analysis]
```

**Filtering stats (include in report header):** "Analyzed N commits (excluded M bulk, K generated-only, J manifest-only)"

### Pass 8: Workaround Cascade Detection

**What to look for:** Code that exists to compensate rather than to build value — the structural fingerprint of accumulated workarounds. A single workaround is not a cascade; look for clusters of 2+ compensating patterns in the same area, all handling special cases for the same subsystem or code path.

**Note:** Pass 8 may flag modules also flagged by Pass 1 (Complection). This is expected — a module can braid concerns (Pass 1) AND contain compensating code (Pass 8). Pass 8 adds the cascade framing: these are not independent concerns but symptoms of accumulated workarounds.

**Skip if:** no codebase (design-phase model only).

**Model evidence (when model is loaded):**
- Components with adapter relationships that exist solely to bridge one subsystem to a standard interface used by all other subsystems
- Components appearing in edges that duplicate an existing interaction pattern through a different mechanism

**Codebase evidence:**
- Special-case filtering: code that filters or handles data differently based on source/origin rather than content (e.g., 'if this came from subsystem X, exclude from Y')
- Description/label branching: different messages, labels, or descriptions depending on which code path produced the data
- Noise suppression: code that hides or suppresses effects that would not exist if the standard mechanism were used
- Exception lists: hardcoded lists of things to exclude or handle specially for one subsystem
- Adapter layers: translation between components that should already speak the same interface
- Fix clustering (from Step 1a item 8): 3+ related commits in the same area within a short timeframe, especially with commit messages referencing workarounds or side effects

**Flow evidence (from Step 1b, when available):**
- Request paths that route through extra adapter or filter modules that other paths do not need
- Data flows where one path requires transformation/translation layers that parallel paths skip

**Grouping rule:** Cluster workarounds by area and subsystem. A cascade requires 2+ compensating patterns in the same neighborhood, all related to the same subsystem or code path. Report each cluster as one cascade, not individual workarounds.

**Tension format:**
```
Name: Workaround cascade in [area] (compensating for [subsystem])
Components: [list of files/modules containing compensating code]
Analysis Pass: 8 — Workaround Cascade
Pull A: Accommodations are necessary — [subsystem] has legitimately different needs than other subsystems. Gain: handles real differences. Cost: maintenance burden of N workarounds.
Pull B: Accommodations compensate for an architectural shortcut in [subsystem] — address at the source. Gain: eliminates N workarounds. Cost: requires reworking [subsystem]'s approach.
If you assume: [subsystem]'s differences are inherent and permanent, the workarounds are justified
If you assume: [subsystem] could use the same mechanism as other subsystems, the workarounds are unnecessary
Structural observation: [N] compensating patterns in [area], all handling special cases for [subsystem]
Evidence: [specific files with workaround code, git history fix clusters]
Cascade members:
  1. [file:line] — [what this workaround compensates for]
  2. [file:line] — [what this workaround compensates for]
  ...
```

### Pass 9: Mechanism Bypass Detection

**What to look for:** A subsystem achieving the same outcome through a parallel path instead of the standard mechanism — the root cause behind a workaround cascade. Pass 9 does not scan independently; it takes each cascade cluster from Pass 8 as input and probes for the underlying bypass.

**Skip if:** Pass 8 found zero cascades (nothing to trace).

**Note:** Pass 9 is the first linked pass — it depends on Pass 8 output. This is by design: blind parallel-mechanism scanning produces false positives. Pass 8's cascade findings focus Pass 9 on areas where a bypass is likely.

**For each cascade from Pass 8, dispatch targeted `hyperpowers:codebase-investigator`:**

```
Pass 8 found a workaround cascade in [area] compensating for [subsystem].
Cascade members:
  [list cascade members from Pass 8 output]

Investigate:
1. What is the STANDARD mechanism that other subsystems use for the same
   outcome in this area? (e.g., the standard event system, the standard
   data pipeline, the standard API pattern)
2. How does [subsystem] achieve that same outcome? Trace its actual code path.
3. Where do the two paths DIVERGE? Identify the fork point — the place
   where [subsystem]'s path splits from the standard mechanism.
[When model is loaded, also:]
4. Check the architecture model: does [subsystem] have edges that duplicate
   an existing interaction pattern through a different mechanism?

Report:
- Standard path: [entry point] -> [module A] -> [module B] -> [outcome]
- Bypass path: [entry point] -> [different modules] -> [same outcome]
- Fork point: [where the paths diverge]
- Or: "No parallel path found — cascade exists but root cause is unclear"
```

**Model evidence (when model is loaded):**
- Components with parallel edges achieving the same outcome through different paths (e.g., subsystem A reaches storage through the event system, subsystem B reaches storage through direct database calls)
- Edges that duplicate an existing interaction pattern through a different mechanism

**Codebase evidence:**
- Two code paths achieving the same outcome: one using the standard mechanism (used by most subsystems) and one using an alternative path (used by the cascade-producing subsystem)
- Fork point where the bypass diverges from the standard path
- The bypass path's output requiring downstream compensating code (the cascade members from Pass 8)

**Tension format (bypass found):**
```
Name: Mechanism bypass in [subsystem] (causing cascade in [area])
Components: [subsystem modules using bypass], [modules on standard path]
Analysis Pass: 9 — Mechanism Bypass (linked to Pass 8 cascade)
Pull A: The bypass is intentional — [subsystem] has requirements that the standard mechanism cannot serve. Gain: [subsystem] operates without standard mechanism constraints. Cost: N workarounds downstream (see linked cascade).
Pull B: The bypass is an architectural shortcut — [subsystem] could use the standard mechanism. Gain: eliminates N downstream workarounds. Cost: requires reworking [subsystem] to use standard mechanism.
If you assume: [subsystem]'s requirements genuinely cannot be met by the standard mechanism, the bypass is necessary
If you assume: [subsystem]'s requirements can be met by the standard mechanism with adaptation, the bypass is unnecessary
Structural observation: [subsystem] achieves [outcome] via [bypass path] instead of [standard path]. Fork point: [where paths diverge]. This bypass produces [N] downstream workarounds (Pass 8 cascade).
Evidence:
  Standard path: [entry] -> [module A] -> [module B] -> [outcome]
  Bypass path: [entry] -> [different modules] -> [same outcome]
  Fork point: [specific file/module where paths diverge]
Linked cascade (Pass 8):
  [cascade name from Pass 8 output]
  Cascade members:
    1. [file:line] — [what this workaround compensates for]
    2. [file:line] — [what this workaround compensates for]
    ...
```

**Tension format (no bypass found — root cause unclear):**
```
Name: Workaround cascade in [area] — root cause unclear
Components: [list from Pass 8 cascade]
Analysis Pass: 9 — Mechanism Bypass (linked to Pass 8 cascade)
Pull A: The cascade has a root cause not visible in the current codebase — investigate further (e.g., historical decisions, external constraints, or removed code). Gain: may uncover actionable root cause. Cost: investigation effort.
Pull B: The cascade members are independent issues that coincidentally cluster in the same area — no single root cause exists. Gain: each workaround can be evaluated independently. Cost: may miss a hidden systemic cause.
If you assume: the clustering is not coincidental, there is a root cause worth finding
If you assume: the clustering is coincidental, individual evaluation is sufficient
Structural observation: [N] compensating patterns in [area] for [subsystem] (from Pass 8). Codebase-investigator found no parallel path bypassing the standard mechanism.
Evidence: [codebase-investigator findings — what was searched and not found]
Linked cascade (Pass 8):
  [cascade name from Pass 8 output]
```

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

**Tension report filtering:** If a prose focus was provided in Step 0, filter the Tensions Found section. Tensions involving components named in or implied by the focus are reported in full. Tensions outside the focus area are listed under a new subsection "Tensions Outside Focus (one-line summaries)" with format: "- [Tension Name] — Components: [A], [B] — Pass [N]". Full detail is suppressed for outside-focus tensions. The architect can re-run /intuition without prose focus to see all tensions in detail. If no prose focus, no filtering — all tensions reported in full.

**Determining "components touched by focus":** Use the prose focus to identify component or module names mentioned. Match against the components/modules in the loaded model (if any) and the modules identified in Step 1a evidence gathering. A tension "touches" the focus if any of its components/modules appears in the focus prose or is in a transitive 1-hop neighborhood of a named component.

**Report format:**

```
## Architectural Intuition Report

**Focus:** [prose focus verbatim, or "full audit (no focus provided)"]
**Model:** [System name from LikeC4, or "none — codebase-only audit"]
**Components audited:** [count from model, or "N/A — no model"]
**Modules analyzed:** [count from codebase]
**Evidence sources:** [model + codebase | codebase only]
**ADRs reviewed:** [count, or "none found"]
**Dynamic views checked:** [count, or "none", or "evidence insufficient — no model"]

---

### Tensions Found

## Tension: [Descriptive Name]
**Components/Modules:** [Component A], [Component B]
**Analysis pass:** [which of the 9 passes found this]
**Pull 1:** [Structural choice] -- Gain: [what you get]. Cost: [what you pay].
**Pull 2:** [Alternative choice] -- Gain: [what you get]. Cost: [what you pay].
**If you assume:** [condition that makes Pull 1 correct].
**If you assume:** [condition that makes Pull 2 correct].
**Structural observation:** [neutral fact -- e.g., "affects 3 downstream nodes",
  "both modules changed together in 7 of last 10 commits"]
**Evidence:** [specific codebase/model evidence that surfaced this]

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

### ADR Maintenance Notes

- ADR-NNN: [title] — last updated [date] (6+ months ago, consider reviewing)

[Omit section if no ADRs are stale, or if no ADRs exist]

### Module Summary

| Component/Module | Tensions | View Drift | Notes |
|------------------|----------|------------|-------|
| [name] | [count] | [yes/no/N/A] | [blank] |

### Audit Outcome

**Tensions found:** [count]
**Accepted (via ADRs):** [count]
**Drift detected (ADR):** [count]
**Rate-of-change mismatches (Pass 7):** [count, or "skipped — insufficient history"]
**Pass 7 filtering stats:** [Analyzed N commits (excluded M bulk, K generated-only, J manifest-only)]
**Workaround cascades (Pass 8):** [count, or "none"]
**Mechanism bypass (Pass 9):** [count, or "skipped — no cascades" or "none — cascades without identified bypass"]
**View drift: see /ponder REVIEW (model-vs-code accuracy)**
**Stale ADRs (6+ months):** [count, or "none"]
**Clean (no tensions, no drift):** [yes/no]

[If clean:]
All components/modules passed audit. No structural tensions detected.

[If tensions found:]
[count] tensions require architect resolution. See Step 4 for resolution protocol.
```

---

### Architect Questions

**Omit this section when zero tensions are found.** The questions are meaningless without tensions to reflect on.

After presenting the tension report and before moving to resolution, present these four questions. They are invitations to reflect — not recommendations. No should/must/recommend language.

```
### Architect Questions

1. **Meadows (leverage):** Where in this system would a small structural
   change produce a disproportionately large behavioral shift?

2. **Meadows (fixes-that-fail):** Which of these tensions, if "fixed" in
   the obvious way, would create a new tension elsewhere?

3. **Alexander (wholeness):** Which component boundaries feel forced rather
   than discovered — imposed on the code rather than emerging from it?

4. **Rao (legibility):** Which parts of this architecture exist to make the
   system legible to its maintainers rather than to serve its users?
```

These questions are part of the ANALYTICAL phase (Step 3). Present them as part of the report. The architect reflects on them during Step 4.

---

## Step 4 -- Resolution Protocol

After presenting the tension report, guide the architect through resolution of each tension. This step IS interactive — use AskUserQuestion for each tension.

**For each tension, present the four options:**

```
AskUserQuestion:
  question: "How do you want to resolve: [Tension Name]?"
  header: "Tension Resolution"
  options:
    - label: "Accept"
      description: "Create ADR documenting why this tension is acceptable. No code changes."
    - label: "Resolve"
      description: "Create ADR documenting the decision + bd ticket to restructure."
    - label: "Brainstorm"
      description: "This tension is complex — hand off to /brainstorm with tension as context."
    - label: "Investigate"
      description: "Need deeper evidence before deciding — dispatch codebase-investigator for targeted analysis."
    - label: "Skip"
      description: "Defer this tension to a future audit."
```

**Handle each response:**

### Accept
Create an ADR using the template from `skills/common-patterns/adr-template.md`:
- Title: "Accept [tension name]"
- Context: the tension's structural observation and evidence
- Decision: accept the tension, with reasoning from the architect
- Consequences: what remains true as a result of acceptance
- Write to `docs/arch/adr/adr-NNN.md`

### Resolve
Create an ADR + bd ticket:
- ADR: documents the structural decision (what the model will look like after the work is done)
- bd ticket: describes the restructuring work needed to resolve the tension
- `bd create "[Resolve tension: description]" --type task --priority 2 --design "[ADR reference, specific modules to change, expected outcome]"`
- If this is the first boundary being created and no model exists: trigger **Model Bootstrapping** (see below)

### Brainstorm
Hand off to brainstorming with tension context:
- "This tension requires design exploration. Handing off to /brainstorm with this context:"
- Include: tension name, both pulls, structural observation, evidence
- The brainstorm will produce a design that resolves the tension, resulting in an epic

### Investigate
Dispatch targeted codebase-investigator:
- Formulate specific questions based on what the architect wants to know
- Present findings and re-ask the resolution question with new evidence

### Skip
Note the tension as deferred and move to the next one.

---

### Linked Pass 8+9 Findings

When Pass 9 identifies a mechanism bypass for a Pass 8 cascade, present them together as a linked finding:

**Presentation:** Show the Pass 9 tension (which includes the linked Pass 8 cascade evidence) as a single resolution item. The architect sees both the bypass and its downstream cascade in one view.

**Resolution semantics:**
- **Resolving the bypass** (Pass 9) resolves the cascade (Pass 8) — the cascade is a symptom of the bypass. One ADR + one bd ticket addresses both.
- **Accepting the bypass** also accepts the cascade — if the bypass is intentional, its downstream workarounds are accepted consequences.
- **Brainstorming the bypass** includes the cascade as context — the brainstorm addresses the root cause, not individual workarounds.

**When no bypass found ("root cause unclear"):** Present the Pass 8 cascade as a standalone tension for resolution. The "root cause unclear" Pass 9 finding is informational — it tells the architect that investigation found no parallel path, so the cascade members may need individual evaluation or deeper investigation.

**Do NOT present Pass 8 cascades separately when a Pass 9 bypass was found.** The linked finding replaces both individual findings. This prevents the architect from resolving the cascade and bypass independently (which would be contradictory — the cascade is caused by the bypass).

---

### Model Bootstrapping (via /ponder)

When a "Resolve" decision creates the first architectural boundary and no architecture model exists, dispatch /ponder in BOOTSTRAP mode.

**Only bootstrap when:** (a) no docs/arch/*.c4 files exist, AND (b) a Resolve decision creates a meaningful boundary between modules. Do not bootstrap for Accept or Skip decisions.

**Dispatch:** Invoke `/hyperpowers:ponder` with the resolved tension's context (component names, descriptions, the relationship just decided). /ponder BOOTSTRAP mode constructs the structured input and handles all file creation, quality criteria enforcement, and validation. See `skills/ponder/SKILL.md` BOOTSTRAP mode for input construction details.

After /ponder returns, announce: "Architecture model bootstrapped via /ponder. Future audits will load the model."

</the_process>

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

| Component/Module | Tensions | View Drift | Notes |
|------------------|----------|------------|-------|
| Order Orchestrator | 0 | N/A | |
| Pricing Engine | 2 | N/A | |
| Fulfillment Engine | 1 | N/A | |
| Payment Gateway | 0 | N/A | |
| Order Store | 1 | N/A | |

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

| Component/Module | Tensions | View Drift | Notes |
|------------------|----------|------------|-------|
| api/ | 2 | N/A | |
| core/ | 1 | N/A | |
| storage/ | 2 | N/A | |
| utils/ | 0 | N/A | |

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

| Component/Module | Tensions | View Drift | Notes |
|------------------|----------|------------|-------|
| Order Orchestrator | 0 | N/A | drift: ADR-001 |
| Pricing Engine | 0 | N/A | |
| Fulfillment Engine | 0 | N/A | |
| Payment Gateway | 0 | N/A | drift: ADR-001 |
| Order Store | 0 | N/A | |

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

<critical_rules>
## Rules That Have No Exceptions

1. **NO recommendations.** Both pulls presented equally. Never say "should", "recommend", "better", "prefer", or "consider changing". If you catch yourself writing one, rewrite to neutral structural observation.

2. **NO severity rankings.** Never use "critical", "high", "medium", "low", "severe", "minor", "urgent", or "important" to describe tensions. Use structural observations: "affects N downstream nodes", "both modules changed together in N commits", "3 files import across this boundary".

3. **NO ordering or prioritization.** Never say "address first", "most pressing", "primary concern", or "should be resolved before". All tensions presented without implied priority.

4. **Run self-check EVERY TIME.** Scan all output for recommendation, severity, and ordering keywords before presenting. This step is mandatory and non-negotiable. "Output looks fine" is a rationalization for skipping it.

5. **Run ALL 9 passes.** Never skip a pass, even if early passes found nothing. Each pass looks for a different category of problem. Skipping passes misses problems. Pass 7 (rate-of-change mismatch) is skipped only when fewer than 10 non-filtered commits are available. Pass 8 (workaround cascade) is skipped only when no codebase exists. Pass 9 (mechanism bypass) is skipped only when Pass 8 finds zero cascades.

6. **ANALYTICAL in Steps 0-3, INTERACTIVE in Step 4.** No AskUserQuestion during analysis (Steps 0-3). Step 4 (resolution protocol) IS interactive — use AskUserQuestion to walk the architect through each tension's resolution.

7. **ADR-aware.** Read existing ADRs before analysis. Skip tensions that match accepted ADR decisions. Report drift when codebase contradicts ADRs. Flag ADRs older than 6 months as maintenance notes.

8. **Dispatch codebase-investigator when codebase exists.** Evidence from the codebase feeds ALL analysis passes, not just drift detection. Never skip codebase investigation when there is code to examine. Step 1a items 7-8 gather compensating code patterns and fix clustering specifically for Pass 8.

9. **Use structured tension format.** Every tension follows the exact format: tension name, components/modules, analysis pass, Pull 1 (gain/cost), Pull 2 (gain/cost), conditional assumptions, structural observation, evidence. No free-form commentary.

10. **Think in components and boundaries, NOT classes and functions.** If the analysis descends to implementation details (class hierarchies, function signatures), you have crossed into inner-loop territory. Stay at the component/module level.

11. **Audit without architecture model is a full audit.** Codebase-only mode runs all passes using codebase evidence. It is not a degraded mode — it finds real tensions. The only difference is model-level analysis reports "evidence insufficient — codebase only". Pass 7 still runs (git history is available without a model). Pass 8 and 9 run on codebase evidence (compensating code patterns, fix clustering, code path tracing). Dynamic view drift is checked in /ponder REVIEW (not in /intuition).

## Common Excuses

All of these mean: **STOP. Follow the process.**

- "This tension is obviously more important" (You are recommending. Present both pulls equally.)
- "Output looks fine, skip self-check" (Self-check exists because output never looks fine on first pass.)
- "Only 2 passes are relevant here" (Run all 9. The passes you skip are where surprises hide.)
- "No need for codebase investigation, model is clear" (Model is declared intent. Codebase is reality. Always check.)
- "I can see which pull is correct" (Your job is to present, not to judge. The architect decides.)
- "The severity is objectively higher" (There is no objective severity. There are structural observations.)
- "Self-check is redundant, I was careful" (Careful people still write recommendation language unconsciously.)
- "No model means limited audit" (Audit without a model finds real tensions from codebase alone. Run all passes — especially Pass 7 which needs only git history, and Pass 8 which detects cascades from codebase evidence.)
</critical_rules>

<verification_checklist>
Before presenting the audit report:

- [ ] Architecture model loaded if present (via LikeC4 MCP); otherwise codebase-only audit announced
- [ ] Dynamic views loaded from LikeC4 model (when model present and views exist)
- [ ] Existing ADRs read (or noted as absent)
- [ ] Prose focus recorded (if provided); evidence gathering and tension report filtering will use it
- [ ] Codebase-investigator dispatched (if codebase exists)
- [ ] Evidence gathered covers: module structure, imports, co-change, call patterns, interfaces, shared state
- [ ] Flow evidence gathered (Step 1b): request paths, undeclared data flows, implicit ordering (if codebase exists)
- [ ] All 9 analysis passes executed (complection, interfaces, temporal coupling, hidden deps, structural dependency direction, state/identity, rate-of-change mismatch, workaround cascade, mechanism bypass)
- [ ] Pass 7 analyzed git change frequencies with noise filtering, or skipped with reason (<10 commits)
- [ ] Pass 8 scanned for workaround cascades, or skipped (no codebase)
- [ ] Pass 9 dispatched targeted codebase-investigator per cascade, or skipped (no cascades from Pass 8)
- [ ] Linked Pass 8+9 findings presented together in Step 4 (bypass resolves cascade)
- [ ] Accepted ADR tensions skipped with note
- [ ] Drift detected where ADRs contradict codebase evidence
- [ ] Every tension uses structured format (name, components/modules, pass, both pulls, assumptions, observation, evidence)
- [ ] Self-check completed: no recommendation keywords in output
- [ ] Self-check completed: no severity rankings in output
- [ ] Self-check completed: no ordering/prioritization in output
- [ ] Structural observations use neutral facts (counts, affected components, file paths)
- [ ] No implementation-level detail (classes, functions, data structures)
- [ ] Report includes module summary table and audit outcome
- [ ] ADR age check: stale ADRs (6+ months) flagged as maintenance notes (not tensions)
- [ ] Step 4: each tension presented to architect with resolution options (accept/resolve/brainstorm/investigate/skip)
- [ ] Step 4: ADRs created for Accept and Resolve paths
- [ ] Step 4: bd tickets created for Resolve path
- [ ] Step 4: ponder subagent dispatched in bootstrap mode if first Resolve on audit without architecture model
- [ ] Step 3: architect questions presented (Meadows leverage, Meadows fixes-that-fail, Alexander wholeness, Rao legibility) — or omitted if zero tensions
- [ ] Step 3: architect questions contain no recommendation language (self-check applies)

**Can't check all boxes?** Return to the relevant step and complete it.
</verification_checklist>

<integration>
**This skill calls:**
- hyperpowers:codebase-investigator (when codebase exists — gathers evidence for all 9 passes)
- hyperpowers:ponder (Step 4 bootstrap — dispatched as subagent when first Resolve on audit without architecture model creates initial model)

**This skill is called by:**
- User (via /hyperpowers:intuition command)
- When friction suggests structural investigation
- Periodic architecture health checks
- When brainstorming suggests architectural analysis before designing

**Call chain:**
```
ARCHITECTURE CYCLE:
  /brainstorm → build → update model
              ↕
  /intuition → find tensions → Step 4 resolve → update model

RESOLUTION (Step 4 per-tension):
  tension → accept (ADR) / resolve (ADR + bd ticket) / brainstorm (complex) / investigate (deeper evidence) / skip (defer)

MODEL BOOTSTRAPPING (first Resolve on audit without architecture model):
  resolve tension → dispatch /ponder bootstrap → model created → future audits load the model

HANDOFF (all tensions resolved/accepted):
  clean architecture → /brainstorm (loads arch context from LikeC4 MCP)
```

**Agents used:**
- codebase-investigator (Step 1a: gather module structure, imports, co-change, call patterns, interfaces, shared state, compensating code patterns, fix clustering; Step 1b: gather request paths, undeclared data flows, implicit ordering; Pass 7: analyze git change frequencies per module with noise filtering; Pass 9: trace bypass paths for cascade root cause; Step 4 Investigate: targeted deep-dive on specific tensions)
- ponder (Step 4: bootstrap mode — dispatched when first Resolve on audit without architecture model creates initial model)
- NO internet-researcher (audit uses only model + codebase evidence)

**Tools required:**
- LikeC4 MCP (when model is loaded: read elements, read views — not needed when no model)
- Edit (update .c4 files if needed — via ponder agent for model operations)
- Write (create new ADR files during resolution)
- Read (load ADR files, load linked component markdown docs)

**Artifacts consumed:**
- LikeC4 model files (docs/arch/*.c4 — when model exists)
- Component documentation (docs/arch/components/*.md — when model exists)
- Dynamic views (docs/arch/views/data-flows/*.c4 — when model exists)
- ADR files in docs/arch/ (always)
- Codebase (always)

**Artifacts produced:**
- Tension report (presented to architect, not persisted)
- Drift report including dynamic view drift (presented to architect, not persisted)
- ADR files (created during Step 4 resolution — Accept or Resolve paths)
- bd tickets (created during Step 4 Resolve path)
- Architecture model files (created via ponder agent bootstrap mode — first Resolve on audit without architecture model)
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

**Brand's empirical architecture:**
- How Buildings Learn (Stewart Brand) -- shearing layers discovered by observing how buildings actually change over decades
- Six S's: Site, Structure, Skin, Services, Space Plan, Stuff -- each changes at a different rate
- Applied to software: components that change at different rates should be independently deployable
- Git history as empirical evidence of actual shearing layers

**Structural dependency direction principle:**
- Dependencies flow from orchestration (higher abstraction) toward data/infrastructure (lower abstraction)
- No upward dependencies: lower-abstraction modules should not import from higher-abstraction modules
- Orchestration modules coordinate, not compute
- Data access modules access, not decide
- Infrastructure/utility modules serve all levels without domain coupling

**When stuck:**
- Many components/modules -> Work through passes systematically, one pair at a time
- Codebase evidence contradicts model -> Report as drift if ADR exists, as tension if not
- Unsure if something is a tension -> If two pulls exist with legitimate gains/costs, it is a tension
- Output has recommendation language -> Self-check caught it. Rewrite to neutral observation.
- No codebase exists -> Run with model evidence only, note the limitation in the report
- No model exists -> Run with codebase evidence only; all passes still run (model-level analysis notes "evidence insufficient — codebase only")
</resources>
