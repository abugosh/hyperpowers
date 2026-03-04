---
name: ponder
description: "Architecture model ownership — dispatches ponder subagent for all LikeC4 .c4 file operations (update, bootstrap, review). Single owner for model creation and maintenance."
---

<skill_overview>
Dispatch the ponder subagent to create, update, or review LikeC4 architecture models. This skill is the single owner of all .c4 file operations — no other skill or workflow creates or modifies architecture model files directly. The skill detects the appropriate mode, constructs structured input, dispatches the ponder agent, and handles the returned summary.

The ponder agent runs in its own context to keep mechanical .c4 work (MCP calls, file edits, validation output) out of the caller's strategic context window.
</skill_overview>

<rigidity_level>
HIGH FREEDOM for when to invoke — callers decide when model work is needed.
RIGID for quality criteria enforcement — the agent always enforces consistent abstraction, metadata, relationship descriptions, markdown docs, and validation. No shortcuts.
RIGID for dispatch pattern — always dispatch as subagent, never inline .c4 work in the caller's context.
</rigidity_level>

<quick_reference>
| Mode | Trigger | Input | Output |
|------|---------|-------|--------|
| UPDATE | Specific change description | What changed, which components affected | Summary of .c4 edits + spot-check + validation |
| BOOTSTRAP | No .c4 files + component list | Component list, system name, known relationships | Full model structure created + validation |
| REVIEW | .c4 files exist + review/accuracy request | Review scope (or general) | Discrepancy list + quality issues |
</quick_reference>

<when_to_use>
- After implementing features that change component interfaces, dependencies, or boundaries (via review-implementation checklist)
- When Intuition Step 4 resolves a tension and no model exists yet (bootstrap)
- When the architect suspects model staleness and wants accuracy verification (review)
- When brainstorming completes an epic that changed architecture (via epic template reference)
- Directly via `/ponder` when the architect wants to update, bootstrap, or review the model

**Don't use for:**
- Finding architectural tensions (use hyperpowers:intuition)
- Designing features (use hyperpowers:brainstorming)
- Implementation work (use hyperpowers:executing-plans)
</when_to_use>

<the_process>

## Mode Detection

Determine the mode from the invocation context:

### UPDATE mode
**Triggered when:** Caller provides a description of what changed in the codebase.
- Review-implementation's architecture checklist answered "yes" to any question
- Brainstorming epic template references model update
- Architect directly describes a change

### BOOTSTRAP mode
**Triggered when:** No `docs/arch/*.c4` files exist AND caller provides component information.
- Intuition Step 4 first Resolve on Mode 2 audit
- Architect requests initial model creation
- Check: `ls docs/arch/*.c4 2>/dev/null` — if no files found, this is bootstrap

### REVIEW mode
**Triggered when:** `docs/arch/*.c4` files exist AND caller requests accuracy/hygiene check.
- Intuition Step 0 suggests model freshness review
- Architect requests model review
- Default when mode is ambiguous (safest — read-only)

## Dispatch Protocol

### 1. Construct structured input

**For UPDATE:**
```
Mode: UPDATE

What changed:
- [description of interface/dependency/component change]

Components affected:
- [component name]: [what specifically changed about it]

Context:
- [why this change was made — epic reference, task reference, or description]
```

**For BOOTSTRAP:**
```
Mode: BOOTSTRAP

System name: [name for the top-level system]

Components:
- [name]: [description] (layer: [orchestration|domain|data|infrastructure|utility])
- [name]: [description] (layer: [layer])

Known relationships:
- [componentA] -> [componentB]: [what flows]

Source: [where this component list came from — Intuition findings, architect knowledge, brainstorm]
```

**For REVIEW:**
```
Mode: REVIEW

Scope: [general accuracy check | specific components to focus on]

Context: [why review was requested — staleness concern, post-implementation check, periodic hygiene]
```

### 2. Dispatch the ponder subagent

```
Dispatch hyperpowers:ponder agent with the structured input above.
```

The agent runs in its own context: loads model via MCP, makes changes (UPDATE/BOOTSTRAP) or gathers findings (REVIEW), validates, and returns a summary.

### 3. Handle the returned summary

**For UPDATE summary:**
- Report changes made to the architect
- If spot-check found discrepancies, flag them
- If validation failed, escalate (agent should have fixed it, but report if not)

**For BOOTSTRAP summary:**
- Announce model creation to the architect
- Report components, relationships, and validation status
- Note: "Future audits will run in Mode 1"

**For REVIEW summary:**
- Present discrepancies and quality issues to the architect
- If corrections needed: ask architect which discrepancies to fix
- For approved corrections: dispatch ponder again in UPDATE mode with the specific fixes

## Model Freshness Heuristic

When checking whether the model might be stale (used by Intuition Step 0):

```bash
# Find most recent .c4 file modification
c4_age=$(stat -f %m docs/arch/*.c4 2>/dev/null | sort -rn | head -1)

# Find most recent code-touching commit
code_age=$(git log -1 --format=%ct -- '*.ts' '*.js' '*.rs' '*.py' '*.go' '*.java' '*.rb' '*.swift' '*.kt' 2>/dev/null)

# Count code commits since last .c4 modification
if [ -n "$c4_age" ] && [ -n "$code_age" ]; then
  commits_since=$(git log --since="@$c4_age" --oneline -- '*.ts' '*.js' '*.rs' '*.py' '*.go' '*.java' '*.rb' '*.swift' '*.kt' 2>/dev/null | wc -l)
  echo "Code commits since last model update: $commits_since"
fi
```

**Suggest review when:** More than 10 code-touching commits have occurred since the last .c4 file modification. This is a heuristic — adjust based on project activity level.

</the_process>

<examples>

<example>
<scenario>UPDATE mode — review-implementation checklist triggers model update</scenario>

<code>
Review-implementation runs the 5-question architecture checklist:
1. Did this work change a component's public interface? YES — Auth component now exposes refreshToken()
2. Did this work add or remove a dependency between components? YES — Auth now depends on TokenStore
3-5: No

Reviewer constructs structured input:

Mode: UPDATE

What changed:
- Auth component has new public method: refreshToken()
- New dependency: Auth -> TokenStore (token persistence)

Components affected:
- auth: new refreshToken() method in public interface
- tokenStore: new component (token persistence layer)

Context:
- Epic bd-t4i: Add token refresh support

Dispatch hyperpowers:ponder agent with the input above.

Agent returns:
## Ponder Update Summary
### Changes Made
- Added tokenStore component to docs/arch/components/token-store.c4 (layer: data, stability: exploring)
- Added relationship: auth -> tokenStore 'persists and retrieves refresh tokens'
- Updated auth interface in docs/arch/components/auth.c4 (added refreshToken to description)
- Created docs/arch/components/token-store.md
- Updated docs/arch/components/auth.md interface contract

### Spot-Check Result
- tokenStore: confirmed src/token-store/ exists with TokenStore class
- auth -> tokenStore: confirmed import in src/auth/refresh.ts

### Validation
- likec4 validate: PASS

Reviewer reports summary to architect.
</code>

<why_it_works>
- Mode correctly detected from structured input
- Scoped spot-check verified only changed components (not full model)
- Quality criteria enforced: metadata, markdown doc, relationship description
- Summary is concise — caller doesn't see MCP calls or file edit details
</why_it_works>
</example>

<example>
<scenario>BOOTSTRAP mode — Intuition first Resolve triggers model creation</scenario>

<code>
Intuition Step 4: architect resolves first tension with "Resolve" on Mode 2 audit.
No docs/arch/*.c4 files exist.

Intuition constructs structured input:

Mode: BOOTSTRAP

System name: orderProcessing

Components:
- api: HTTP request handling and routing (layer: orchestration)
- core: Business logic and domain rules (layer: domain)
- storage: Data persistence and queries (layer: data)
- utils: Shared utilities (layer: utility)

Known relationships:
- api -> core: routes requests to business logic
- core -> storage: persists and retrieves domain data
- api -> storage: direct read queries for reports (tension noted in ADR)

Source: Intuition Mode 2 audit findings + architect input

Dispatch hyperpowers:ponder agent.

Agent returns:
## Ponder Bootstrap Summary
### Components Created
- api: HTTP request handling and routing (layer: orchestration, stability: exploring)
- core: Business logic and domain rules (layer: domain, stability: exploring)
- storage: Data persistence and queries (layer: data, stability: exploring)
- utils: Shared utilities (layer: utility, stability: exploring)

### Relationships
- api -> core: routes requests to business logic
- core -> storage: persists and retrieves domain data
- api -> storage: direct read queries for reports

### Files Created
- docs/arch/spec.c4, docs/arch/model.c4
- docs/arch/components/api.c4, core.c4, storage.c4, utils.c4
- docs/arch/views/landscape.c4
- docs/arch/components/api.md, core.md, storage.md, utils.md

### Validation
- likec4 validate: PASS

Architecture model bootstrapped. Future audits will run in Mode 1.
</code>

<why_it_works>
- Bootstrap triggered correctly (no .c4 files + component list)
- All elements start at exploring stability state
- Quality criteria met: metadata, markdown docs, relationship descriptions, landscape view
- Concise summary suitable for Intuition's context
</why_it_works>
</example>

<example>
<scenario>REVIEW mode — architect suspects model staleness</scenario>

<code>
Architect invokes /ponder and asks for model review.
docs/arch/*.c4 files exist. 15 code commits since last .c4 update.

Skill constructs structured input:

Mode: REVIEW

Scope: general accuracy check

Context: 15 code commits since last model update, periodic hygiene check

Dispatch hyperpowers:ponder agent.

Agent returns:
## Ponder Review Summary
### Model-vs-Code Accuracy
- auth: MATCH — src/auth/ matches model description and interfaces
- storage: DISCREPANCY — model shows 2 relationships, code has 3 (storage -> cache added)
- api: MATCH — src/api/ matches model

### Missing from Model
- cache: src/cache/ exists as separate module, not represented in model

### Stale in Model
- None

### Quality Issues
- storage component missing markdown doc (docs/arch/components/storage.md not found)

### Validation
- likec4 validate: PASS

### Recommendation
2 discrepancies found. Suggest update mode dispatch to add cache component and storage markdown doc.

Skill presents findings to architect. Architect approves corrections.
Skill dispatches ponder again in UPDATE mode with specific fixes.
</code>

<why_it_works>
- Review mode correctly detected (files exist + review request)
- Full model-vs-code comparison via codebase-investigator
- Quality criteria checked and violations reported
- No corrections made — findings returned for architect approval
- Follow-up UPDATE dispatch proposed for approved corrections
</why_it_works>
</example>

</examples>

<critical_rules>
## Rules That Have No Exceptions

1. **All .c4 operations go through ponder subagent.** No skill, agent, or workflow creates or modifies .c4 files directly. Ponder is the single owner.

2. **Always dispatch as subagent.** Never inline .c4 work in the caller's context. The mechanical work (MCP calls, file edits, validation) stays in the agent's context.

3. **Review mode is read-only.** Never combine review and correction in a single dispatch. Review returns findings, architect approves, then update applies corrections.

4. **No auto-inserting model updates.** Ponder proposes changes. The architect (or the skill's caller) approves before changes take effect. For UPDATE mode dispatched by review-implementation or Intuition, the dispatch itself constitutes approval (the caller already decided an update was needed).

5. **Model describes what IS.** No target elements, no aspirational components, no #target tags. If it doesn't exist in code, it doesn't go in the model.

6. **Quality criteria are non-negotiable.** Every operation must leave the model satisfying all quality criteria: consistent abstraction, metadata, relationship descriptions, markdown docs, landscape view, clean validation.

## Common Excuses

All of these mean: **STOP. Dispatch the ponder agent.**

- "I'll just quickly edit the .c4 file" (No. Dispatch ponder. It's the single owner.)
- "This is a tiny change, no need for a subagent" (Quality criteria apply to all changes, regardless of size.)
- "I can validate later" (No. Every change validates immediately.)
- "The markdown doc can wait" (No. Quality criteria require it with every component.)
- "Review and fix in one pass is more efficient" (No. Architect approval gate exists for a reason.)
</critical_rules>

<verification_checklist>
Before considering the ponder dispatch complete:

- [ ] Mode correctly detected (UPDATE / BOOTSTRAP / REVIEW)
- [ ] Structured input constructed with all required fields
- [ ] Ponder subagent dispatched (not inline .c4 work)
- [ ] Summary received and reported to architect/caller
- [ ] UPDATE: spot-check result reviewed for discrepancies
- [ ] UPDATE: validation passed
- [ ] BOOTSTRAP: all components have metadata, markdown docs, relationship descriptions
- [ ] BOOTSTRAP: landscape view created
- [ ] BOOTSTRAP: validation passed
- [ ] REVIEW: discrepancies presented to architect for approval
- [ ] REVIEW: no corrections made (read-only)
- [ ] REVIEW: follow-up UPDATE proposed if corrections needed
</verification_checklist>

<integration>
**This skill calls:**
- hyperpowers:ponder agent (subagent — all .c4 operations)
- hyperpowers:codebase-investigator (via ponder agent — spot-check and model-vs-code comparison)

**This skill is called by:**
- review-implementation (5-question architecture checklist — UPDATE mode when any answer is yes)
- Intuition Step 4 (model bootstrapping on first Resolve — BOOTSTRAP mode)
- Intuition Step 0 (model freshness check — suggests REVIEW mode when stale)
- brainstorming (epic template architecture update — references /ponder update)
- User (via /ponder command — any mode)

**Call chain:**
```
DIRECT INVOCATION:
  /ponder → mode detection → dispatch ponder agent → summary

FROM REVIEW-IMPLEMENTATION:
  review-impl → 5-question checklist → any yes → /ponder update → summary

FROM INTUITION:
  Step 0: freshness check → suggest /ponder review
  Step 4: first Resolve on Mode 2 → /ponder bootstrap → model created → future Mode 1

FROM BRAINSTORMING:
  epic template → architecture update → /ponder update → summary
```

**Agents used:**
- ponder (subagent — dispatched per invocation, returns summary)
- codebase-investigator (via ponder agent — scoped spot-check in UPDATE, full comparison in REVIEW)

**Tools required (by ponder agent):**
- LikeC4 MCP (read model state)
- Edit/Write (modify/create .c4 files and markdown docs)
- Read (load existing files)
- Bash (run likec4 validate, directory operations)

**Artifacts consumed:**
- LikeC4 model files (docs/arch/*.c4)
- Component markdown docs (docs/arch/components/*.md)
- Codebase (for spot-check and review)

**Artifacts produced:**
- .c4 model files (created in BOOTSTRAP, modified in UPDATE)
- Component markdown docs (created/modified)
- Discrepancy reports (REVIEW mode)
</integration>
