---
name: brainstorming
description: Use when creating or developing anything, before writing code - refines rough ideas into bd epics with immutable requirements
---

<skill_overview>
Turn rough ideas into validated designs stored as bd epics with immutable requirements; tasks created iteratively as you learn, not upfront.
</skill_overview>

<rigidity_level>
HIGH FREEDOM - Adapt Socratic questioning to context, but always create immutable epic before code and only create first task (not full tree).
</rigidity_level>

<quick_reference>
| Step | Action | Deliverable |
|------|--------|-------------|
| 0 | **Mode detection gate** | THINKING or BUILDING mode |
| 1 | Ask questions (one at a time) | Understanding (thinking: open Socratic; building: requirement-eliciting) |
| 2 | Research (agents for codebase/internet) | Existing patterns and approaches [BUILDING only] |
| 3 | Propose 2-3 approaches with trade-offs | Recommended option [BUILDING only] |
| 4 | Present design in sections (200-300 words) | Validated architecture [BUILDING only] |
| 5 | Create bd epic with IMMUTABLE requirements | Epic with anti-patterns [BUILDING only] |
| 6 | Create ONLY first task | Ready for executing-plans [BUILDING only] |
| 7 | Hand off to executing-plans | Lead orchestrates executor [BUILDING only] |

**Key:** Step 0 gates everything. THINKING mode uses only Step 1 (open Socratic questions, no context loading). BUILDING mode uses all steps. Thinking can transition to building; reverse should not happen.
</quick_reference>

<when_to_use>
- User describes new feature to implement
- User has rough idea that needs refinement
- About to write code without clear requirements
- Need to explore approaches before committing
- Requirements exist but architecture unclear

**Don't use for:**
- Executing existing plans (use hyperpowers:executing-plans)
- Fixing bugs (use hyperpowers:fixing-bugs)
- Refactoring (use hyperpowers:refactoring-safely)
- Requirements already crystal clear and epic exists
</when_to_use>

<the_process>
## 0. Mode Detection Gate

**Announce:** "I'm using the brainstorming skill."

**Before doing ANYTHING else** (no context loading, no agent dispatch, no architecture checks), determine the user's mode from their prompt.

**Evaluate signals IN ORDER — first match wins:**

**BUILDING MODE (check first — specificity wins over uncertainty):**
- Specific bead ID referenced: 'bd-42', 'the card pool component'
- Specific feature named: 'let's build the checkout flow'
- Action language with specifics: 'I want to implement X', 'pull X from the backlog'
- Architecture component referenced by name
- Invoked by another skill (using-hyper, executing-plans) with specific task context

**THINKING MODE (check second — uncertainty without specificity):**
- Open-ended questions WITHOUT specific references: 'what should we...', 'how might we...'
- Exploratory language: 'I'm thinking about...', 'I'm not sure whether...'
- No specific component/bead/feature reference
- Uncertainty expressed: 'what are the tradeoffs of...'

**MIXED SIGNALS RULE:** If prompt contains BOTH uncertainty language AND specific component/feature references, resolve to **BUILDING MODE**. Rationale: specific references indicate the user knows WHAT they want to work on, even if uncertain about HOW.

**AMBIGUOUS (neither set matches):** Use AskUserQuestion — 'Are you exploring an idea or ready to build something specific?'

**After detection, announce the mode:**
- THINKING: "This sounds like you're exploring — let's think through this together."
- BUILDING: "You have something specific in mind — let me load context and help you design it."

---

## 1. Understanding the Idea

### THINKING MODE path

**Do NOT:**
- Load architecture context
- Dispatch codebase-investigator or internet-researcher preemptively
- Check for architecture nodes
- Produce backlog triage or bd commands

**Do:**
- Start with ONE open Socratic question using AskUserQuestion:
  - 'What problem are you trying to solve?' (if user described a solution without a problem)
  - 'What are you trying to learn?' (if user expressed general uncertainty)
  - 'What would change if you knew the answer?' (if user asked a specific question)
  - 'What constraints are you working within?' (if user described options without context)
- Only dispatch agents if conversation reveals need for codebase/external knowledge
- Continue Socratic exploration as long as the user is exploring

**Transition to building mode when user names a specific deliverable:**
- 'okay let's build X', 'I want to implement Y'
- Makes a decision: 'let's go with approach A'
- References specific component/bead: 'the card pool needs Z'

When transitioning: announce 'Switching to building mode — let me load context.' Then proceed with building mode path from the top of Step 1.

**Thinking mode can end without producing an epic.** Not every brainstorm leads to building. Do NOT nudge toward building mode.

### BUILDING MODE path

**Check current state:**
- Recent commits, existing docs, codebase structure
- Dispatch `hyperpowers:codebase-investigator` for existing patterns
- Dispatch `hyperpowers:internet-researcher` for external APIs/libraries

**Check for architecture model context:**

If the user's request mentions a component, module, or architecture element, check for an existing LikeC4 architecture model:

```bash
ls arch/*.c4 2>/dev/null
```

If no arch/*.c4 files found: skip architecture context loading, proceed with normal brainstorming.

If arch/*.c4 files found, LikeC4 MCP is REQUIRED. If MCP is not available, fail with: "LikeC4 MCP server is required. Run: likec4 mcp --stdio"

**Load architecture context via LikeC4 MCP:**

1. Find the component matching the user's reference:
```
# Get model overview
read-project-summary

# Search for component by name, kind, tag, or metadata
search-element <user's component reference>
```

2. Load full component details:
```
# Read element with metadata
read-element <element-id>
# Returns: metadata (layer, stability_state), description, tags, links

# Get adjacent components
find-relationships <element-id>
# Returns: direct and indirect relationships (blocks, relatesTo)
```

3. Find relevant ADRs:
```bash
ls doc/arch/adr-*.md 2>/dev/null
# Read ADRs that mention the component or its rate of change
```

4. Load data flow context from dynamic views:
```
# Read dynamic views that include this component
read-view <view-id>
# Returns: view definition with component participation in flows
```

5. If a codebase exists, dispatch `hyperpowers:codebase-investigator` to derive fresh data flow context scoped to the detected component:

```
Dispatch codebase-investigator with prompt:
"For component [component name] with these boundaries: [adjacent components from find-relationships]

1. What data enters this component? (from which upstream modules, what shape at module level?)
2. What data exits this component? (to which downstream modules, what shape?)
3. What data transformations happen inside? (what shape goes in vs what comes out?)
4. What are the primary request paths that flow through this component?

Reference the component's interface contract from: doc/arch/components/[name].md"
```

This dispatch is COMPONENT-SCOPED — it asks about ONE component's data flow, not the entire system. Fresh derivation catches drift without stale artifacts.

If no codebase exists (greenfield/design phase), skip this dispatch entirely — the architecture model can exist before code does.

6. Present the loaded context before proceeding with Socratic questioning:
```
Architecture context loaded for [component name]:
- Change rate: [from git history — fast/medium/slow, commits/month]
- Layer: [from element metadata.layer]
- Stability state: [from element metadata.stability_state]
- Interface contract: [from doc/arch/components/<name>.md]
- Adjacent components: [from find-relationships — blocks and relatesTo]
- Relevant ADRs:
  - ADR-NNN: [title] — [key decision and consequences]
- Data flow context:
  - Dynamic views: [views this component participates in]
  - Inbound: [data from upstream in views + codebase-investigator]
  - Outbound: [data to downstream in views + codebase-investigator]
  - Request paths: [entry points flowing through]

These ADRs represent architectural decisions that may inform
anti-patterns for this epic.
```

If stability_state is 'pre-fit': note "Component boundaries are new — see ADR-NNN for the rationale and what would cause revisiting."

If the flow dispatch was skipped (no codebase), omit the codebase-derived data flow from the presentation.

The architect decides during the brainstorm which architectural tradeoffs become anti-patterns in the inner-loop epic. Do NOT auto-insert ADR tradeoffs as anti-patterns.

**Edge cases:**
- No architecture model exists (no arch/*.c4): skip detection, proceed with normal brainstorming
- No codebase but model exists: skip codebase-investigator dispatch, present architectural context only
- Multiple components referenced: load context for all matched (search-element for each)
- Component is pre-fit: load context, note boundaries are new and may be revisited
- No ADRs found for the component: note "No ADRs found for this component"
- User doesn't reference any component: skip detection, proceed normally
- LikeC4 MCP not running: fail with "LikeC4 MCP server required. Run: likec4 mcp --stdio"

**REQUIRED: Use AskUserQuestion tool with scannable format**

**Question Format Guidelines:**

1. **1-5 questions maximum** per round (don't overwhelm)
2. **Multiple choice preferred** with clear options
3. **Include suggested default** marked with "(Recommended)"
4. **Numbered for easy reference**
5. **Separate critical from nice-to-have**

**Question Structure:**
```
Question: [Clear question ending with ?]
Options:
  A. [Option] (Recommended) - [Why this is default]
  B. [Option] - [Trade-off]
  C. [Option] - [Trade-off]
  D. Other (please specify)

Priority: [CRITICAL | IMPORTANT | NICE_TO_HAVE]
```

**Priority Definitions:**
- **CRITICAL**: Must answer before proceeding (security, core functionality)
- **IMPORTANT**: Affects design significantly but has reasonable default
- **NICE_TO_HAVE**: Can defer to implementation phase

**Example using AskUserQuestion:**
```
AskUserQuestion:
  question: "Where should OAuth tokens be stored?"
  header: "Token storage"
  options:
    - label: "httpOnly cookies (Recommended)"
      description: "Prevents XSS token theft, industry standard"
    - label: "sessionStorage"
      description: "Cleared on tab close, less persistent"
    - label: "localStorage"
      description: "Persists across sessions, XSS vulnerable"
```

**Fast-Path Option:**
For IMPORTANT/NICE_TO_HAVE questions with good defaults, offer:
"Reply 'defaults' to accept all recommended options"

**Do NOT just print questions and wait for "yes"** - use the AskUserQuestion tool.

**CAPTURE for Design Discovery:**
As each question is answered, record in "Key Decisions Made" table:
- Question asked
- User's answer
- Implication for requirements/anti-patterns

This preserves the Socratic Q&A for future reference during task creation and obstacle handling.

---

## 2. Exploring Approaches

**Research first:**
- Similar feature exists → dispatch codebase-investigator
- New integration → dispatch internet-researcher
- Review findings before proposing

**IMPORTANT: Capture research findings for Design Discovery**
As you research, note down:
- Codebase findings: file paths, patterns discovered, relevant code
- External findings: API capabilities, library constraints, doc URLs
- These will populate the "Research Findings" section of the epic

**CAPTURE for Design Discovery:**
- **Research Deep-Dives**: For each major research topic, document:
  - Question explored
  - Sources consulted with key findings
  - Conclusion and how it informed the design
- **Dead-End Paths**: When you abandon an approach during research:
  - Why you explored it (what made it seem viable)
  - What investigation revealed
  - Why abandoned (specific reason linking to requirements/constraints)

Dead-end documentation prevents wasted re-investigation when obstacles arise later.

**Propose 2-3 approaches with trade-offs:**

```
Based on [research findings], I recommend:

1. **[Approach A]** (recommended)
   - Pros: [benefits, especially "matches existing pattern"]
   - Cons: [drawbacks]

2. **[Approach B]**
   - Pros: [benefits]
   - Cons: [drawbacks]

3. **[Approach C]**
   - Pros: [benefits]
   - Cons: [drawbacks]

I recommend option 1 because [specific reason, especially codebase consistency].
```

**Lead with recommended option and explain why.**

---

## 3. Presenting the Design

**Once approach is chosen, present design in sections:**
- Break into 200-300 word chunks
- Ask after each: "Does this look right so far?"
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify

**Show research findings:**
- "Based on codebase investigation: auth/ uses passport.js..."
- "API docs show OAuth flow requires..."
- Demonstrate how design builds on existing code

**Dynamic view proposal:**
If the design involves data flowing through 2+ existing architecture components, ask:

```
AskUserQuestion:
  question: "Does this feature create a new request path through 2+ existing components that's worth documenting?"
  header: "Dynamic View Proposal"
  options:
    - label: "Yes — [describe the flow]"
      description: "This creates a new path worth reasoning about as architecture"
    - label: "No — uses existing paths only"
      description: "No new cross-component flow to document"
    - label: "Not sure"
      description: "We can decide during implementation"
```

If yes, note the proposed dynamic view in the epic's Architecture Context section: "Proposed dynamic view: [flow name] ([component A] -> [component B] -> [component C])"

**CAPTURE for Design Discovery:**
When user raises concerns, hesitations, or "what if" questions:
- Record in "Open Concerns Raised" section
- Document how each was addressed or deferred
- Example: "What if Google OAuth is down?" → "Graceful degradation to error message"

These concerns often resurface during implementation - having the resolution documented prevents re-debating.

---

## 4. Creating the bd Epic

**After design validated, create epic as immutable contract:**

```bash
bd create "Feature: [Feature Name]" \
  --type epic \
  --priority [0-4] \
  --design "## Requirements (IMMUTABLE)
[What MUST be true when complete - specific, testable]
- Requirement 1: [concrete requirement]
- Requirement 2: [concrete requirement]
- Requirement 3: [concrete requirement]

## Success Criteria (MUST ALL BE TRUE)
- [ ] Criterion 1 (objective, testable - e.g., 'Integration tests pass')
- [ ] Criterion 2 (objective, testable - e.g., 'Works with existing User model')
- [ ] All tests passing
- [ ] Pre-commit hooks passing

## Anti-Patterns (FORBIDDEN)
- ❌ [Pattern] ([reasoning] - e.g., 'NO localStorage tokens (security: httpOnly prevents XSS token theft)')
- ❌ [Pattern] ([reasoning] - e.g., 'NO mocking OAuth in integration tests (validation: defeats purpose)')

## Approach
[2-3 paragraph summary of chosen approach]

## Architecture
[Key components, data flow, integration points]

## Architecture Context
(Include this section when architecture model exists — populated from LikeC4 MCP context loaded in Step 1)
- Component: [LikeC4 element name]
- Change rate: [from git history — fast/medium/slow, commits/month]
- Layer: [from metadata]
- Stability state: [from metadata]
- Adjacent components: [from relationships]
- Relevant ADRs: [ADR-NNN: title]
- Key data flows: [from dynamic views involving this component]
- Proposed dynamic view: [if new request path identified in Step 3, else 'None']

## Architecture Update Checklist
After inner-loop work completes, review-implementation runs these 5 questions:
1. Did this work change a component's public interface?
2. Did this work add or remove a dependency between components?
3. Did this work create a new component or remove an existing one?
4. Did this work move responsibility from one component to another?
5. Did this work create a new request path through 2+ components?

If any yes: update .c4 files, update linked markdown, propose dynamic view if Q5, confirm with architect.

## Design Rationale
### Problem
[1-2 sentences: what problem this solves, why status quo insufficient]

### Research Findings
**Codebase:**
- [file.ts:line] - [what it does, why relevant]
- [pattern discovered, implications]

**External:**
- [API/library] - [key capability, constraint discovered]
- [doc URL] - [relevant guidance found]

### Approaches Considered

#### 1. [Chosen Approach] ✓

**What it is:** [2-3 sentence description]

**Investigation:**
- Researched [X] - found [Y]
- Tested [pattern] - worked because [Z]
- Referenced [file:line] - shows [pattern]

**Pros:**
- [benefit with evidence]

**Cons:**
- [drawback and mitigation]

**Chosen because:** [specific reasoning linking to requirements and codebase patterns]

#### 2. [Rejected Approach A] ❌

**What it is:** [2-3 sentence description]

**Why we looked at this:** [what made this seem viable initially]

**Investigation:**
- Researched [X] - found [Y]
- [dead-end discovered]

**Pros:**
- [benefits it would have had]

**Cons:**
- [fatal flaw or significant drawback]

**⚠️ REJECTED BECAUSE:** [specific reasoning, linking to anti-patterns or requirements]

**🚫 DO NOT REVISIT UNLESS:** [specific condition that would change this decision]

#### 3. [Rejected Approach B] ❌ (if applicable)

**What it is:** [2-3 sentence description]

**Why we looked at this:** [what made this seem viable initially]

**Investigation:**
- [what was researched]

**Pros:**
- [benefits it would have had]

**Cons:**
- [fatal flaw or significant drawback]

**⚠️ REJECTED BECAUSE:** [specific reasoning]

**🚫 DO NOT REVISIT UNLESS:** [specific condition that would change this decision]

### Scope Boundaries
**In scope:**
- [explicit inclusions]

**Out of scope (deferred/never):**
- [explicit exclusions with reasoning]

### Open Questions
- [uncertainties to resolve during implementation]
- [decisions deferred to execution phase]

## Design Discovery (Reference Context)

> This section preserves detailed context from brainstorming for use during task creation.
> Reference this when defining tasks, handling obstacles, or validating implementation decisions.

### Key Decisions Made

| Question | User Answer | Implication |
|----------|-------------|-------------|
| [Socratic question asked] | [User's response] | [How this shapes requirements/anti-patterns] |

### Research Deep-Dives

#### [Topic 1: e.g., OAuth Library Selection]
**Question explored:** [What question drove this research?]
**Sources consulted:**
- [Source 1] - [key finding]
- [Source 2] - [key finding]

**Findings:**
- [Detailed finding 1]
- [Detailed finding 2]

**Conclusion:** [How this informed the design]

### Dead-End Paths

#### [Path: e.g., Custom JWT Implementation]
**Why explored:** [What made this seem worth investigating]
**Investigation:**
- [What was researched/tried]

**Why abandoned:** [Specific reason - links to requirements/anti-patterns]

### Open Concerns Raised

- [User concern 1] → [How it was addressed or deferred]
- [User concern 2] → [How it was addressed or deferred]"
```

**Critical:** Anti-patterns section prevents watering down requirements when blockers occur. Always include reasoning.

**Example anti-patterns:**
- ❌ NO localStorage tokens (security: httpOnly prevents XSS token theft)
- ❌ NO new user model (consistency: must integrate with existing db/models/user.ts)
- ❌ NO mocking OAuth in integration tests (validation: defeats purpose of testing real flow)
- ❌ NO TODO stubs for core authentication flow (completeness: core flow must be implemented)

---

## 5. Creating ONLY First Task

**Create one task, not full tree:**

```bash
bd create "Task 1: [Specific Deliverable]" \
  --type feature \
  --priority [match-epic] \
  --design "## Goal
[What this task delivers - one clear outcome]

## Implementation
[Detailed step-by-step for this task]

1. Study existing code
   [Point to 2-3 similar implementations: file.ts:line]

2. Write tests first (TDD)
   [Specific test cases for this task]

3. Implementation checklist
   - [ ] file.ts:line - function_name() - [exactly what it does]
   - [ ] test.ts:line - test_name() - [what scenario it tests]

## Success Criteria
- [ ] [Specific, measurable outcome]
- [ ] Tests passing
- [ ] Pre-commit hooks passing"

bd dep add bd-2 bd-1 --type parent-child  # Link to epic
```

**Why only one task?**
- Subsequent tasks created iteratively by executing-plans
- Each task reflects learnings from previous
- Avoids brittle task trees that break when assumptions change

---

## 6. SRE Refinement and Handoff

After epic and first task created:

**REQUIRED: Run SRE refinement before handoff**

```
Use Skill tool: hyperpowers:sre-task-refinement
```

SRE refinement will:
- Apply 7-category corner-case analysis (Opus 4.1)
- Strengthen success criteria
- Identify edge cases and failure modes
- Ensure task is ready for implementation

**Do NOT skip SRE refinement.** The first task sets the pattern for the entire epic.

**After refinement approved, present handoff:**

```
"Epic bd-1 is ready with immutable requirements and success criteria.
First task bd-2 has been refined and is ready to execute.

Ready to start implementation? I'll use executing-plans to orchestrate execution.

The executing-plans skill will:
1. Create a team and spawn an executor teammate for implementation
2. The executor implements tasks with TDD (red-green-refactor-commit)
3. I validate each proposed next task against epic requirements and anti-patterns
4. The executor proposes SRE-refined tasks, I approve or redirect
5. When all criteria met, a reviewer agent verifies the implementation
6. Review-implementation runs the architecture update checklist (5 questions)

This approach preserves epic context and cross-task learnings continuously — no manual /clear cycling needed."
```
</the_process>

<examples>
<example>
<scenario>Developer skips research, proposes approach without checking codebase</scenario>

<code>
User: "Add OAuth authentication"

Claude (without brainstorming):
"I'll implement OAuth with Auth0..."
[Proposes approach without checking if auth exists]
[Doesn't research existing patterns]
[Misses that passport.js already set up]
</code>

<why_it_fails>
- Proposes Auth0 when passport.js already exists in codebase
- Creates inconsistent architecture (two auth systems)
- Wastes time implementing when partial solution exists
- Doesn't leverage existing code
- User has to redirect to existing pattern
</why_it_fails>

<correction>
**Correct approach:**

1. **Research first:**
   - Dispatch codebase-investigator: "Find existing auth implementation"
   - Findings: passport.js at auth/passport-config.ts
   - Dispatch internet-researcher: "Passport OAuth2 strategies"

2. **Propose approaches building on findings:**
   ```
   Based on codebase showing passport.js at auth/passport-config.ts:

   1. Extend existing passport setup (recommended)
      - Add google-oauth20 strategy
      - Matches codebase pattern
      - Pros: Consistent, tested library
      - Cons: Requires OAuth provider setup

   2. Custom JWT implementation
      - Pros: Full control
      - Cons: Security complexity, breaks pattern

   I recommend option 1 because it builds on existing auth/ setup.
   ```

**What you gain:**
- Leverages existing code (faster)
- Consistent architecture (maintainable)
- Research informs design (correct)
- User sees you understand codebase (trust)
</correction>
</example>

<example>
<scenario>Developer creates full task tree upfront</scenario>

<code>
bd create "Epic: Add OAuth"
bd create "Task 1: Configure OAuth provider"
bd create "Task 2: Implement token exchange"
bd create "Task 3: Add refresh token logic"
bd create "Task 4: Create middleware"
bd create "Task 5: Add UI components"
bd create "Task 6: Write integration tests"

# Starts implementing Task 1
# Discovers OAuth library handles refresh automatically
# Now Task 3 is wrong, needs deletion
# Discovers middleware already exists
# Now Task 4 is wrong
# Task tree brittle to reality
</code>

<why_it_fails>
- Assumptions about implementation prove wrong
- Task tree becomes incorrect as you learn
- Wastes time updating/deleting wrong tasks
- Rigid plan fights with reality
- Context switching between fixing plan and implementing
</why_it_fails>

<correction>
**Correct approach (iterative):**

```bash
bd create "Epic: Add OAuth" [with immutable requirements]
bd create "Task 1: Configure OAuth provider"

# Execute Task 1
# Learn: OAuth library handles refresh, middleware exists

bd create "Task 2: Integrate with existing middleware"
# [Created AFTER learning from Task 1]

# Execute Task 2
# Learn: UI needs OAuth button component

bd create "Task 3: Add OAuth button to login UI"
# [Created AFTER learning from Task 2]
```

**What you gain:**
- Tasks reflect current reality (accurate)
- No wasted time fixing wrong plans (efficient)
- Each task informed by previous learnings (adaptive)
- Plan evolves with understanding (flexible)
- Epic requirements stay immutable (contract preserved)
</correction>
</example>

<example>
<scenario>Epic created without anti-patterns section</scenario>

<code>
bd create "Epic: OAuth Authentication" --design "
## Requirements
- Users authenticate via Google OAuth2
- Tokens stored securely
- Session management

## Success Criteria
- [ ] Login flow works
- [ ] Tokens secured
- [ ] All tests pass
"

# During implementation, hits blocker:
# "Integration tests for OAuth are complex, I'll mock it..."
# [No anti-pattern preventing this]
# Ships with mocked OAuth (defeats validation)
</code>

<why_it_fails>
- No explicit forbidden patterns
- Agent rationalizes shortcuts when blocked
- "Tokens stored securely" too vague (localStorage? cookies?)
- Requirements can be "met" without meeting intent
- Mocking defeats the purpose of integration tests
</why_it_fails>

<correction>
**Correct approach with anti-patterns and design rationale:**

```bash
bd create "Epic: OAuth Authentication" --design "
## Requirements (IMMUTABLE)
- Users authenticate via Google OAuth2
- Tokens stored in httpOnly cookies (NOT localStorage)
- Session expires after 24h inactivity
- Integrates with existing User model at db/models/user.ts

## Success Criteria
- [ ] Login redirects to Google and back
- [ ] Tokens in httpOnly cookies
- [ ] Token refresh works automatically
- [ ] Integration tests pass WITHOUT mocking OAuth
- [ ] All tests passing

## Anti-Patterns (FORBIDDEN)
- ❌ NO localStorage tokens (security: httpOnly prevents XSS token theft)
- ❌ NO new user model (consistency: must use existing db/models/user.ts)
- ❌ NO mocking OAuth in integration tests (validation: defeats purpose of testing real flow)
- ❌ NO skipping token refresh (completeness: explicit requirement from user)

## Approach
Extend existing passport.js setup at auth/passport-config.ts with Google OAuth2 strategy.
Use passport-google-oauth20 library. Store tokens in httpOnly cookies via express-session.
Integrate with existing User model for profile storage.

## Architecture
- auth/strategies/google.ts - New OAuth strategy
- auth/passport-config.ts - Register strategy (existing)
- db/models/user.ts - Add googleId field (existing)
- routes/auth.ts - OAuth callback routes

## Design Rationale
### Problem
Users currently have no SSO option - must create accounts manually.
Manual signup has 40% abandonment rate. Google OAuth reduces friction.

### Research Findings
**Codebase:**
- auth/passport-config.ts:1-50 - Existing passport setup, uses session-based auth
- auth/strategies/local.ts:1-30 - Pattern for adding strategies
- db/models/user.ts:1-80 - User model, already has email field

**External:**
- passport-google-oauth20 - Official Google strategy, 2M weekly downloads
- Google OAuth2 docs - Requires client ID, callback URL, scopes

### Approaches Considered

#### 1. Extend passport.js with google-oauth20 ✓

**What it is:** Add passport-google-oauth20 strategy to existing passport.js setup. Reuses session-based auth, follows existing pattern in auth/strategies/.

**Investigation:**
- Reviewed auth/passport-config.ts - existing passport setup with session serialization
- Checked auth/strategies/local.ts:1-30 - pattern for adding strategies
- passport-google-oauth20 npm - 2M weekly downloads, actively maintained

**Pros:**
- Matches existing codebase pattern (auth/strategies/)
- Session handling already works (express-session configured)
- Well-documented, large community

**Cons:**
- Adds npm dependency

**Chosen because:** Consistent with auth/strategies/local.ts pattern, minimal changes to existing code

#### 2. Custom JWT-based OAuth ❌

**What it is:** Implement OAuth flow from scratch using JWTs instead of sessions. Would replace existing session-based auth with stateless tokens.

**Why we looked at this:** User mentioned 'maybe we should use JWTs' - seemed potentially simpler

**Investigation:**
- Counted files using req.session - 15 files would need rewriting
- Reviewed existing session middleware - deeply integrated
- Researched JWT security best practices - significant complexity

**Pros:**
- No new dependencies
- Stateless (scalability benefit)

**Cons:**
- Would require rewriting 15 files using req.session
- Security complexity (token invalidation, refresh logic)
- Breaks existing session pattern

**⚠️ REJECTED BECAUSE:** Scope creep - OAuth feature shouldn't require rewriting existing auth system. 15 files affected is too much risk.

**🚫 DO NOT REVISIT UNLESS:** We're already rewriting the entire auth system in a separate epic.

#### 3. Auth0 integration ❌

**What it is:** Use Auth0 managed service for OAuth. Would handle tokens, sessions, and multiple providers.

**Why we looked at this:** Third-party service might reduce implementation complexity

**Investigation:**
- Evaluated Auth0 free tier - 7000 MAU limit
- Reviewed Auth0 SDK - different auth model than current codebase
- Estimated migration effort - significant test rewriting

**Pros:**
- Managed service (less code to maintain)
- Supports multiple providers out of box

**Cons:**
- External dependency, cost at scale
- Different auth model than existing code
- Test suite would need significant changes

**⚠️ REJECTED BECAUSE:** Overkill for single OAuth provider. Introduces new pattern inconsistent with codebase.

**🚫 DO NOT REVISIT UNLESS:** We need 3+ OAuth providers AND are okay with vendor dependency.

### Scope Boundaries
**In scope:**
- Google OAuth login/signup
- Token storage in httpOnly cookies
- Profile sync with User model

**Out of scope (deferred/never):**
- Other OAuth providers (GitHub, Facebook) - deferred to future epic
- Account linking (connect Google to existing account) - deferred
- Custom OAuth scopes beyond profile/email - not needed

### Open Questions
- Should failed OAuth create partial user record? (decide during implementation)
- Token refresh: silent vs prompt? (default to silent, user can configure)

## Design Discovery (Reference Context)

> Detailed context from brainstorming for task creation and obstacle handling.

### Key Decisions Made

| Question | User Answer | Implication |
|----------|-------------|-------------|
| Token storage preference? | httpOnly cookies for security | Anti-pattern: NO localStorage |
| New user model or extend existing? | Use existing at db/models/user.ts | Must add googleId field, not new table |
| Session duration? | 24h inactive timeout | Need refresh token logic |
| What if Google OAuth is down? | Graceful error message | No fallback auth required |

### Research Deep-Dives

#### OAuth Library Selection
**Question explored:** Which OAuth library to use?
**Sources consulted:**
- passport-google-oauth20 npm - 2M weekly downloads, well-maintained
- google-auth-library npm - official but lower-level
- Stack Overflow threads on passport vs alternatives

**Findings:**
- passport-google-oauth20 matches existing passport setup at auth/passport-config.ts
- google-auth-library would require rewriting session handling
- Passport has built-in session serialization

**Conclusion:** Use passport-google-oauth20 for consistency with existing auth/strategies/ pattern

#### Token Storage Strategy
**Question explored:** Where to store OAuth tokens?
**Sources consulted:**
- OWASP token storage guidelines
- Auth0 best practices article
- Existing codebase pattern at auth/session.ts

**Findings:**
- localStorage vulnerable to XSS (OWASP warns against)
- httpOnly cookies prevent JS access
- Existing session uses express-session with cookies

**Conclusion:** httpOnly cookies, documented as anti-pattern to use localStorage

### Dead-End Paths

#### Custom JWT Implementation
**Why explored:** User mentioned 'maybe we should use JWTs'
**Investigation:**
- Counted 15 files using req.session pattern
- Estimated 2 weeks migration effort
- Identified security complexity with token refresh

**Why abandoned:** Scope creep - OAuth feature shouldn't rewrite auth system

#### Auth0 Integration
**Why explored:** Third-party service might be simpler
**Investigation:**
- Evaluated Auth0 free tier limits
- Reviewed SDK integration requirements
- Estimated test rewriting effort

**Why abandoned:** Overkill for single provider, introduces vendor dependency

### Open Concerns Raised

- 'What if Google OAuth is down?' → Graceful degradation to error message, no fallback auth
- 'Should we support account linking later?' → Deferred to future epic, out of scope for now
- 'Token refresh - silent or prompt?' → Default silent, can configure later
"
```

**What you gain:**
- Requirements concrete and specific (testable)
- Forbidden patterns explicit with reasoning (prevents shortcuts)
- Agent can't rationalize away requirements (contract enforced)
- Design rationale preserves context for future tasks
- Approaches considered show why alternatives were rejected with DO NOT REVISIT conditions
- Design Discovery preserves full Q&A, research, and dead-ends for obstacle handling
- Open questions explicitly tracked for implementation decisions
</correction>
</example>

</examples>

<key_principles>
- **One question at a time** - Don't overwhelm
- **Multiple choice preferred** - Easier to answer when possible
- **Delegate research** - Use codebase-investigator and internet-researcher agents
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Epic is contract** - Requirements immutable, tasks adapt
- **Anti-patterns prevent shortcuts** - Explicit forbidden patterns stop rationalization
- **One task only** - Subsequent tasks created iteratively (not upfront)
</key_principles>

<research_agents>
## Use codebase-investigator when:
- Understanding how existing features work
- Finding where specific functionality lives
- Identifying patterns to follow
- Verifying assumptions about structure
- Checking if feature already exists

## Use internet-researcher when:
- Finding current API documentation
- Researching library capabilities
- Comparing technology options
- Understanding community recommendations
- Finding official code examples

## Research protocol:
1. Codebase pattern exists → Use it (unless clearly unwise)
2. No codebase pattern → Research external patterns
3. Research yields nothing → Ask user for direction
</research_agents>

<critical_rules>
## Rules That Have No Exceptions

1. **Mode detection FIRST** → Before ANY context loading, agent dispatch, or architecture checks
2. **Thinking mode = no context loading** → No bd commands, no agent dispatch, no architecture checks until conversation reveals need
3. **Thinking mode can end without epic** → Not every brainstorm produces artifacts. Do NOT nudge toward building.
4. **Building mode checks specificity first** → Specific references override uncertainty language (mixed signals = building)
5. **Use AskUserQuestion tool** → Don't just print questions and wait
6. **Research BEFORE proposing** → Use agents to understand context [BUILDING only]
7. **Propose 2-3 approaches** → Don't jump to single solution [BUILDING only]
8. **Epic requirements IMMUTABLE** → Tasks adapt, requirements don't
9. **Include anti-patterns section** → Prevents watering down requirements
10. **Create ONLY first task** → Subsequent tasks created iteratively
11. **Run SRE refinement** → Before handoff to executing-plans

## Common Excuses

All of these mean: **STOP. Follow the process.**

- "Let me just quickly check the codebase first" (Mode detection FIRST — no context loading in thinking mode)
- "The user probably wants to build something" (Check signals — uncertainty without specifics = thinking mode)
- "I should load architecture context to give a better answer" (Thinking mode is Socratic exploration, not backlog triage)
- "This open question implies a feature request" (Open questions = thinking mode, not building mode)
- "Requirements obvious, don't need questions" (Questions reveal hidden complexity)
- "I know this pattern, don't need research" (Research might show better way)
- "Can plan all tasks upfront" (Plans become brittle, tasks adapt as you learn)
- "Anti-patterns section overkill" (Prevents rationalization under pressure)
- "Epic can evolve" (Requirements contract, tasks evolve)
- "Can just print questions" (Use AskUserQuestion tool - it's more interactive)
- "SRE refinement overkill for first task" (First task sets pattern for entire epic)
- "User said yes, design is done" (Still need SRE refinement before execution)
</critical_rules>

<verification_checklist>
**Step 0 (both modes):**
- [ ] Mode detection performed BEFORE any context loading or agent dispatch
- [ ] Mode announced to user (thinking or building)
- [ ] If ambiguous, asked user with AskUserQuestion

**Thinking mode exit checklist (if session ended in thinking mode):**
- [ ] No bd commands were run
- [ ] No agents were dispatched preemptively
- [ ] Open Socratic questions were asked (not requirement-eliciting)
- [ ] User was NOT nudged toward building mode

**Building mode checklist (before handing off to executing-plans):**
- [ ] Used AskUserQuestion tool for clarifying questions (one at a time)
- [ ] Researched codebase patterns (if applicable)
- [ ] Researched external docs/libraries (if applicable)
- [ ] Proposed 2-3 approaches with trade-offs
- [ ] Presented design in sections, validated each
- [ ] Created bd epic with all sections (requirements, success criteria, anti-patterns, approach, architecture, design rationale)
- [ ] Requirements are IMMUTABLE and specific
- [ ] Anti-patterns include reasoning (not just "NO X" but "NO X (reason: Y)")
- [ ] Design Rationale complete: problem, research findings, approaches considered, scope boundaries, open questions
- [ ] Created ONLY first task (not full tree)
- [ ] First task has detailed implementation checklist
- [ ] Ran SRE refinement on first task (hyperpowers:sre-task-refinement)
- [ ] Announced handoff to executing-plans after refinement approved

**Can't check all boxes?** Return to process and complete missing steps.
</verification_checklist>

<integration>
**This skill calls:**
- hyperpowers:codebase-investigator (for finding existing patterns)
- hyperpowers:internet-researcher (for external documentation)
- hyperpowers:sre-task-refinement (REQUIRED before handoff to executing-plans)
- hyperpowers:executing-plans (handoff — lead orchestrates executor teammate after refinement approved)

**Call chain:**
```
ARCHITECTURE CYCLE:
  /brainstorm → build → update model
              ↕
  /intuition → find tensions → resolve → update model

INNER LOOP:
  brainstorming → sre-task-refinement → executing-plans
```

**This skill is called by:**
- hyperpowers:using-hyper (mandatory before writing code)
- User requests for new features
- Beginning of greenfield development
- Architecture tension resolution (via /intuition)

**Agents used:**
- codebase-investigator (understand existing code)
- internet-researcher (find external documentation)

**Tools required:**
- AskUserQuestion (for all clarifying questions)
</integration>

<resources>
**Detailed guides:**
- [bd epic template examples](resources/epic-templates.md)
- [Socratic questioning patterns](resources/questioning-patterns.md)
- [Anti-pattern examples by domain](resources/anti-patterns.md)

**When stuck:**
- User gives vague answer → Ask follow-up multiple choice question
- Research yields nothing → Ask user for direction explicitly
- Too many approaches → Narrow to top 2-3, explain why others eliminated
- User changes requirements mid-design → Acknowledge, return to understanding phase
</resources>
