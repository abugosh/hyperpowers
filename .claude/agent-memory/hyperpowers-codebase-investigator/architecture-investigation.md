# Architecture System Investigation - LikeC4 Migration Planning

## Current State Summary

The hyperpowers plugin has a complete architecture system built on **bd-based task management** using Lowy's volatility-based decomposition. This is NOT code execution; it's a structured workflow documented in markdown.

**Key insight:** The architecture system is orthogonal to code - it's purely a planning/design abstraction layer managed through bd tasks and ADR files.

## System Components

### 1. Skill Files (Markdown Workflows)

#### skills/brainstorming/SKILL.md (Line 1-900+)
- **Lines 52-130**: Architecture node detection and context loading
  - Checks for existing architecture graph: `bd list --label arch --type epic --status open`
  - Loads component nodes: `bd list --label arch,component --parent <epic-id>`
  - Loads volatility axis, layer, interface contract from bd design field
  - Loads adjacent nodes from bd dependencies
  - Loads relevant ADRs from doc/arch/adr-*.md
  - Dispatches codebase-investigator for component-scoped data flow
  - **KEY**: Architecture context is loaded BEFORE Socratic questioning starts
  - Line 117: "The architect decides during the brainstorm which architectural tradeoffs become anti-patterns"

#### skills/volatility-decomposition/SKILL.md (Line 1-1060)
- **Lines 0-27**: Metadata - produces "architecture graph in bd with ADRs"
- **Lines 46-119**: Step 0 - Context Detection
  - Lines 52-55: Checks for existing architecture epic with `bd list --label arch`
  - Lines 57-65: REVISION MODE - loads existing graph, component nodes, edges
  - Lines 67-79: INCEPTION MODE - dispatches codebase-investigator to map structure
  - Lines 81-108: Step 0b - Data coupling investigation (REQUIRED for both modes)
- **Lines 121-292**: Step 1 - Socratic Questioning (Lowy Framework)
  - Uses AskUserQuestion tool throughout (NEVER prints questions)
  - Questions probe: forces, volatility, variability, customer axis, layer assignment
  - Weaves data coupling evidence into questions
  - **KEY**: Coupling evidence from Step 0b feeds into questions
- **Lines 318-365**: Step 2 - Structure Proposal
  - ALWAYS present 2-3 alternatives (NEVER just one)
  - Each proposal includes: node list, edge list, optimization goals, tradeoffs
  - **KEY**: Annotations reference data coupling if evidence exists
- **Lines 387-475**: Step 3 - Encode in bd
  - Creates architecture epic: `bd create '[System Name] Architecture' --type epic --label arch`
  - Creates component nodes: `bd create '[Component Name]' --type feature --label arch,component --parent <epic>`
  - Sets stability state: `bd set-state <component-id> stability=exploring`
  - Creates edges: `bd dep add` for blocks, `bd relate` for relates_to
  - **KEY**: Each component node has design field with: Volatility Axis, Layer, Interface Contract, Responsibility
- **Lines 478-532**: Step 4 - Create ADRs
  - Guides architect through ADR creation
  - Creates doc/arch/adr-NNN.md files
  - ADRs created for: major boundary decisions, significant tradeoffs
  - **KEY**: ADRs reference consequences of previous ADRs (flow forward)
- **Lines 535-559**: Step 5 - Handoff Guidance
  - Summary of graph, ADRs created, recommended next steps
  - References /audit-arch and /brainstorm

#### skills/architectural-audit/SKILL.md (Line 1-934)
- **Lines 0-24**: Metadata - "Hickey simplicity-based audit"
- **Lines 42-97**: Step 0 - Load Architecture Graph
  - Finds architecture epic: `bd list --label arch --type epic --status open`
  - Loads full graph: `bd show <epic>`, `bd list --label arch,component`, `bd show <component>`, `bd dep tree`
  - Records: components, volatility axes, layers, interface contracts, edges, stability states
  - Lines 84-96: Loads existing ADRs from doc/arch/adr-*.md
- **Lines 100-164**: Step 1 - Gather Evidence
  - **Lines 104-141**: Dispatches codebase-investigator with comprehensive prompt
    - Maps MODULE structure and boundaries (not classes/functions)
    - Gathers: imports, circular deps, fan-in/fan-out
    - Gathers: co-change patterns, cross-module modifications
    - Gathers: actual call patterns, undeclared flows, upward calls
    - Gathers: interface surface area, what's exported vs internal
    - Gathers: shared state, globals, singletons, configuration coupling
  - **Lines 147-163**: Step 1b - Data flow investigation
    - Traces entry points through modules
    - Identifies undeclared flows between graph nodes
    - Identifies implicit ordering
- **Lines 167-285**: Step 2 - Run 6 Analysis Passes (RIGID - all executed always)
  - **Pass 1**: Complection Scan - concerns braided together
  - **Pass 2**: Interface Analysis - interfaces carrying multiple concerns
  - **Pass 3**: Temporal Coupling - things needing specific ordering
  - **Pass 4**: Hidden Dependencies - deps not in declared graph
  - **Pass 5**: Layer Violations - Lowy layer rule violations
  - **Pass 6**: State/Identity Conflation - mutable shared state
  - **KEY**: Each pass uses BOTH graph evidence AND codebase evidence (when available)
  - Each pass may produce 0+ tensions
  - Skips tension if existing ADR already accepts it
- **Lines 288-406**: Step 3 - Self-Check and Present
  - **Lines 290-321**: MANDATORY self-check for recommendation language
    - Scans for: "should", "must", "recommend", "better", "prefer", "consider", etc.
    - Scans for: severity keywords ("critical", "high", "low", "important")
    - Scans for: ordering/prioritization ("address first", "primary concern")
    - Rewrites all to neutral, structural language
  - **Lines 323-391**: Tension Report Format
    - Per-tension structure: name, components, analysis pass, both pulls, assumptions, observation, evidence
    - **KEY**: Both pulls presented equally - NO recommendations
    - Accepted Tensions section - ADRs that cover tensions
    - Drift Detected section - where codebase contradicts ADRs
    - Graph Summary table
    - Audit Outcome
  - **Lines 393-407**: Updates stability states on clean components

### 2. Command Files

#### commands/decompose.md
- Points to: `hyperpowers:volatility-decomposition` skill

#### commands/audit-arch.md
- Points to: `hyperpowers:architectural-audit` skill

### 3. Common Patterns

#### skills/common-patterns/adr-template.md
- **Format**: ADR-NNN with Status, Context, Decision, Consequences
- **Location**: doc/arch/adr-NNN.md
- **Numbering**: Sequential, never reused (superseded ADRs kept for history)
- **Key principle** (Line 46): "ADRs outlive the architecture graph. The graph is a temporary work plan; ADRs capture why decisions were made."

#### skills/common-patterns/bd-commands.md
- Basic bd commands for reading/creating/updating issues
- Shows --label usage: `--label arch`, `--label arch,component`
- Shows --type usage: `--type epic`, `--type feature`

## Data Storage

### bd Task Structure

**Architecture Epic** (Lines in volatility-decomposition):
```
bd create '[System Name] Architecture' --type epic --label arch \
  --design '## System Purpose
## Lowy Layer Map
## Global Constraints'
```

**Component Node** (Lines in volatility-decomposition):
```
bd create '[Component Name]' --type feature --label arch,component --parent <epic> \
  --design '## Volatility Axis
## Layer: [Manager|Engine|Resource Accessor|Utility]
## Interface Contract
- IN: [operations exposed]
- OUT: [operations called]
## Responsibility'
```

**Dependencies**:
- `bd dep add <downstream> <upstream>` - interface dependency (blocks)
- `bd relate <node-a> <node-b>` - non-blocking interaction

**Stability States** (Line 432-434, architectural-audit):
- `bd set-state <component> stability=exploring` (initial)
- `bd set-state <component> stability=audited` (passed audit)
- Fallback: `bd label <component> arch:exploring` (if set-state unavailable)

### ADR Files

**Location**: doc/arch/adr-NNN.md
**Format**: Nygard format (Status, Context, Decision, Consequences)
**Key principle**: Consequences of one ADR become Context for subsequent ADRs

## Integration Points

### With brainstorming skill
- **Line 52-130**: Detects architecture node context before Socratic questioning
- **Auto-detection**: If user mentions component/module/bd-id, loads context
- **Loads from bd**: Volatility axis, layer, interface contract, adjacent nodes
- **Loads from ADRs**: Relevant architectural decisions
- **Dispatch**: Component-scoped codebase-investigator to get data flow
- **Output**: Architecture context presented BEFORE normal brainstorming starts
- **Decision point** (Line 122): "The architect decides during the brainstorm which architectural tradeoffs become anti-patterns"

### With volatility-decomposition skill
- **Inception mode**: Fresh decomposition starting from Socratic dialogue + codebase structure
- **Revision mode**: Restructures existing graph after audit/feedback
- **Produces**: bd graph + ADR files for all major decisions

### With architectural-audit skill
- **Loads from bd**: Entire graph state + all component nodes
- **Loads from ADRs**: To check what tensions are already accepted
- **Produces**: Tension report + drift report (no recommendations)
- **Never makes recommendations** - presents both pulls of each tension equally

## Critical Design Assumptions

1. **bd is the source of truth** for architecture state
   - Components stored as bd tasks with label `arch,component`
   - Volatility axis/layer/interface stored in `--design` field
   - Dependencies stored via `bd dep add` and `bd relate`

2. **ADRs are permanent, graph is temporary work plan**
   - Graph can be restructured freely
   - ADRs capture intent and remain for history
   - Superseded ADRs stay in repo with status update

3. **No recommendations from audit**
   - Audit finds tensions (both sides equally)
   - Architect decides resolution
   - ADRs accept tensions or graph restructures

4. **Architecture node context loads BEFORE feature brainstorming**
   - Brainstorming detects architecture context
   - Loads from bd: volatility, layer, interface, adjacent nodes
   - Loads from ADRs: relevant decisions
   - Dispatch: component-scoped data flow from codebase
   - Feature requirements informed by architectural constraints

5. **Data coupling evidence feeds architectural analysis**
   - Volatility-decomposition Step 0b gathers coupling evidence
   - Evidence weaves into Socratic questions
   - Proposals annotate with coupling information
   - Audit uses coupling to detect hidden dependencies

## Areas that Need LikeC4 Migration Planning

### 1. Primary: bd Architecture Graph
- **Current**: Stored as bd tasks with labels + design field
- **Migration path**: Need to decide:
  - Does LikeC4 replace bd storage, or supplement it?
  - If replace: How do we maintain Lowy layer metadata?
  - If supplement: Sync strategy between bd and LikeC4?

### 2. Secondary: Brainstorming Architecture Detection
- **Current** (brainstorming.md Lines 52-130): Detects via bd labels, loads context from bd
- **Migration path**: After LikeC4 migration, brainstorming needs to detect LikeC4 context instead of bd

### 3. Tertiary: Volatility-Decomposition Output
- **Current** (Lines 387-475): Creates bd epic + component nodes
- **Migration path**: After LikeC4 migration, should it create LikeC4 definitions instead?

### 4. Tertiary: Architectural-Audit Analysis
- **Current** (Lines 42-97): Loads graph from bd
- **Migration path**: After LikeC4 migration, should it load from LikeC4 instead?

### 5. Tertiary: Stability State Tracking
- **Current** (Lines 432-434): Using bd set-state or labels (arch:exploring, arch:audited, arch:accepted, arch:stable)
- **Migration path**: After LikeC4 migration, where does stability state live?

## No LikeC4 References Found

**Search results**: No existing references to LikeC4, c4model, or architecture-as-code in repo (as of Feb 2026).

This is a greenfield integration - LikeC4 doesn't currently exist in the plugin.
