---
name: brainstorming
description: Use when creating or developing anything, before writing code - refines rough ideas into bd epics with immutable requirements
---

<skill_overview>
Turn rough ideas into validated designs stored as bd epics with immutable requirements; tasks created iteratively as you learn, not upfront.
</skill_overview>

<rigidity_level>
HIGH FREEDOM - The 8-step order is fixed, but Socratic questioning within steps adapts to context.
</rigidity_level>

<quick_reference>
| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | Ask questions (one at a time, AskUserQuestion) | Understanding of the problem and context |
| 2 | Research codebase and external patterns; propose 2-3 approaches | Recommended option with trade-offs documented |
| 3 | Present design in sections (200-300 words each); friction detection | Validated architecture; /intuition offered if friction detected |
| 4 | Architecture Impact Check (5 structural questions) | Impact recorded in epic; /intuition offered if any YES |
| 5 | Create bd epic with IMMUTABLE requirements | Epic with 7 top-level sections and anti-patterns |
| 6 | Create ONLY first task | First bd task ready for SRE refinement |
| 7 | Run SRE refinement | Refined first task ready for handoff |
| 8 | Hand off to executing-plans | Lead orchestrates executor subagent |
</quick_reference>

<when_to_use>
- User describes new feature to implement
- User has rough idea that needs refinement
- About to write code without clear requirements
- Need to explore approaches before committing
- Requirements exist but architecture unclear
- /intuition Resolution Protocol routes here with a tension as context

**Don't use for:**
- Executing existing plans (use hyperpowers:executing-plans)
- Fixing bugs (use hyperpowers:fixing-bugs)
- Refactoring (use hyperpowers:refactoring-safely)
- Requirements already crystal clear and epic exists
</when_to_use>

<the_process>

**Announce:** "I'm using the brainstorming skill."

---

## Step 1 — Understanding the Idea

Ask focused questions to understand what the user wants to build and why. Use the AskUserQuestion tool — do not print questions and wait.

**Question format:**

```
Question: [Clear question ending with ?]
Options:
  A. [Option] (Recommended) - [Why this is the default]
  B. [Option] - [Trade-off]
  C. Other (please specify)

Priority: CRITICAL | IMPORTANT | NICE_TO_HAVE
```

**Guidelines:**
- 1-5 questions maximum per round (don't overwhelm)
- Multiple choice preferred; include suggested default marked "(Recommended)"
- Fast-path: for IMPORTANT/NICE_TO_HAVE questions with good defaults, offer "Reply 'defaults' to accept all recommended options"
- Ask one CRITICAL question at a time; group IMPORTANT/NICE_TO_HAVE together
- Stop asking once the design space is clear — unresolved NICE_TO_HAVE questions become Open Questions in the epic

**As each question is answered, record in "Key Decisions Made":**
- Question asked
- User's answer
- Implication for requirements or anti-patterns

---

## Step 2 — Exploring Approaches

**Research first, propose second.** Never propose an approach before researching what already exists.

**When to dispatch which agent:**
- Similar feature exists in the codebase → dispatch `hyperpowers:codebase-investigator`
- New integration or unfamiliar library → dispatch `hyperpowers:internet-researcher`
- Both apply → dispatch both

**Capture research findings** as you go:
- Codebase findings: file paths, patterns discovered, relevant code
- External findings: API capabilities, library constraints, doc URLs
- Dead-end paths: what was explored, why abandoned (prevents re-investigation later)

**Propose 2-3 approaches with trade-offs:**

```
Based on [research findings], I recommend:

1. **[Approach A]** (recommended)
   - Pros: [benefits, especially "matches existing pattern at path/to/file.ts"]
   - Cons: [drawbacks]

2. **[Approach B]**
   - Pros: [benefits]
   - Cons: [drawbacks]

3. **[Approach C]** (if applicable)
   - Pros: [benefits]
   - Cons: [drawbacks]

I recommend option 1 because [specific reason linking to requirements and codebase patterns].
```

**Lead with the recommended option and explain why.**

---

## Step 3 — Presenting the Design

**Once approach is chosen, present design in 200-300 word sections:**
- Ask after each section: "Does this look right so far?"
- Cover in order: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify any section

**Show research findings inline:**
- "Based on codebase investigation: auth/ uses passport.js at auth/passport-config.ts..."
- Demonstrate how the design builds on existing code, not around it

**Design-time friction detection:**

If during design presentation the architect expresses structural friction — uncertainty about where responsibility belongs, coupling concerns, "something feels off about this structure", difficulty deciding between two component boundaries — offer /intuition explicitly:

```
"This sounds like structural friction — uncertainty about where boundaries
belong or how components should relate. /intuition can systematically
examine your architecture for tensions before you commit to this design.

Would you like to run /intuition first, or continue with the current design?"
```

Do NOT auto-redirect. This is a routing offer, not a gate. The architect decides.

**When to detect friction:**
- Architect says "something feels wrong" or "I'm not sure where this belongs"
- Two reasonable component boundaries both seem valid with no clear winner
- Design requires a "shim" or workaround to fit existing structure
- Architect mentions a pattern contradiction: "we said X but now we're doing Y"

---

## Step 4 — Architecture Impact Check

After the design is validated, run the Architecture Impact Check **before** creating the epic. This is a routing mechanism — it surfaces decisions to the architect, not a gate that halts progress.

**Ask these 5 structural questions against the designed solution:**

1. Creates a new component/module?
2. Changes the public interface of an existing component?
3. Adds or removes a cross-component dependency?
4. Creates a new request path through 2 or more components?
5. Moves responsibility from one component to another?

**Present results:**

```
## Architecture Impact Check

- [ ] Creates a new component/module — [YES/NO] [brief description if YES]
- [ ] Changes public interface of existing component — [YES/NO]
- [ ] Adds/removes cross-component dependency — [YES/NO]
- [ ] Creates new request path through 2+ components — [YES/NO]
- [ ] Moves responsibility between components — [YES/NO]

Result: [N] boxes checked.
```

**Routing logic:**
- 0 boxes checked: proceed to epic creation
- 1+ boxes checked: offer /intuition

```
"This design touches [N] architectural dimension(s). /intuition can examine
your existing architecture for tensions this change might interact with.

Would you like to run /intuition before creating the epic, or proceed?"
```

The architect decides. Record the Impact Check result (including the routing decision) in the epic's Architecture Impact section.

---

## Step 5 — Creating the bd Epic

After design is validated and Architecture Impact Check recorded, create the epic as an immutable contract.

**Anti-patterns section is required.** It prevents watering down requirements when blockers occur. Always include reasoning.

**Example anti-patterns:**
- ❌ NO localStorage tokens (security: httpOnly prevents XSS token theft)
- ❌ NO new user model (consistency: must integrate with existing db/models/user.ts)
- ❌ NO mocking OAuth in integration tests (validation: defeats purpose of testing real flow)

**Create the epic:**

```bash
bd create "[Feature Name]" \
  --type epic \
  --priority [0-4] \
  --design "$(cat <<'EOF'
## Requirements (IMMUTABLE)
[What MUST be true when complete — specific, testable]
- Requirement 1: [concrete requirement]
- Requirement 2: [concrete requirement]

## Success Criteria (MUST ALL BE TRUE)
- [ ] Criterion 1 (objective, testable — e.g., 'Integration tests pass')
- [ ] Criterion 2 (objective, testable)
- [ ] All tests passing
- [ ] Pre-commit hooks passing

## Anti-Patterns (FORBIDDEN)
- ❌ [Pattern] ([reasoning] — e.g., 'NO localStorage tokens (security: httpOnly prevents XSS token theft)')
- ❌ [Pattern] ([reasoning])

## Approach
[2-3 paragraph summary of chosen approach and why it was selected over alternatives]

## Architecture
[Key components, data flow, integration points, affected files]

## Architecture Impact
(Result of Step 4 Architecture Impact Check)

- [ ] Creates a new component/module — [YES/NO]
- [ ] Changes public interface of existing component — [YES/NO]
- [ ] Adds/removes cross-component dependency — [YES/NO]
- [ ] Creates new request path through 2+ components — [YES/NO]
- [ ] Moves responsibility between components — [YES/NO]

Result: [N] boxes checked. /intuition [was offered and run / was offered and deferred / was not offered (0 checks)].

## Design Rationale

### Problem
[1-2 sentences: what problem this solves, why the status quo is insufficient]

### Research Findings
**Codebase:**
- [file.ts:line] — [what it does, why relevant]
- [pattern discovered, implications]

**External:**
- [API/library] — [key capability or constraint discovered]
- None because [specific reason — e.g., this is a skill-framework refactor with no external dependencies]

### Key Decisions Made

| Question | User Answer | Implication |
|----------|-------------|-------------|
| [Socratic question asked] | [User's response] | [How this shapes requirements or anti-patterns] |

### Approaches Considered

#### 1. [Chosen Approach] (chosen)

**What it is:** [2-3 sentence description]

**Investigation:**
- Researched [X] — found [Y]
- Referenced [file:line] — shows [pattern]

**Pros:**
- [benefit with evidence]

**Cons:**
- [drawback and mitigation]

**Chosen because:** [specific reasoning linking to requirements and codebase patterns]

#### 2. [Rejected Approach A] (rejected)

**What it is:** [2-3 sentence description]

**Why explored:** [what made this seem viable initially]

**Investigation:**
- [what was researched or tried]

**Pros:**
- [benefits it would have had]

**Cons:**
- [fatal flaw or significant drawback]

**REJECTED BECAUSE:** [specific reasoning, linking to anti-patterns or requirements]

**DO NOT REVISIT UNLESS:** [specific condition that would change this decision]

#### 3. [Rejected Approach B] (rejected, if applicable)

**What it is:** [2-3 sentence description]

**Why explored:** [what made this seem viable]

**Investigation:**
- [what was researched]

**Pros:**
- [benefits it would have had]

**Cons:**
- [fatal flaw]

**REJECTED BECAUSE:** [specific reasoning]

**DO NOT REVISIT UNLESS:** [specific condition]

### Scope Boundaries

**In scope:**
- [explicit inclusions]

**Out of scope:**
- [explicit exclusions with reasoning — e.g., "GitHub OAuth: deferred to future epic; single provider is sufficient now"]
- None because [specific reason if nothing is explicitly excluded]

### Open Questions
- [uncertainties to resolve during implementation]
- [decisions deferred to execution phase]
- None because [specific reason if all questions were resolved during brainstorm]
EOF
)"
```

**Every subsection that could reasonably be empty MUST have a "None because [grounded reason]" entry.** Bare "None" or "N/A" is forbidden — it enables skip-thinking rationalization.

---

## Step 6 — Creating ONLY the First Task

Create one task, not a full tree.

```bash
bd create "Task 1: [Specific Deliverable]" \
  --type feature \
  --priority [match-epic] \
  --design "$(cat <<'EOF'
## Goal
[What this task delivers — one clear outcome]

## Implementation
[Detailed step-by-step for this task only]

1. Study existing code
   [Point to 2-3 similar implementations: file.ts:line]

2. Write tests first (TDD)
   [Specific test cases for this task]

3. Implementation checklist
   - [ ] file.ts:line — function_name() — [exactly what it does]
   - [ ] test.ts:line — test_name() — [what scenario it tests]

## Success Criteria
- [ ] [Specific, measurable outcome]
- [ ] Tests passing
- [ ] Pre-commit hooks passing
EOF
)"

bd dep add bd-2 bd-1 --type parent-child  # Link task to epic
```

**Why only one task?**
- Subsequent tasks are created iteratively by executing-plans as each task completes
- Each task reflects learnings from the previous one
- Avoids brittle task trees that break when initial assumptions prove wrong

---

## Step 7 — SRE Refinement

**REQUIRED. Do not skip.**

```
Use Skill tool: hyperpowers:sre-task-refinement
```

SRE refinement applies an 8-category corner-case analysis to the first task: granularity, implementability, success criteria quality, dependency structure, safety standards, edge cases, red flags, and test meaningfulness. It strengthens success criteria and identifies failure modes.

The first task sets the pattern for the entire epic. Skipping refinement on "feels heavy" grounds is exactly the rationalization the rule guards against.

---

## Step 8 — Handoff to Executing-Plans

After refinement approved, present the handoff:

```
"Epic [bd-N] is ready with immutable requirements and success criteria.
First task [bd-M] has been refined and is ready to execute.

Ready to start implementation? I'll use executing-plans to orchestrate execution.

The executing-plans skill will:
1. Dispatch a fresh executor subagent for each individual task
2. The executor implements the task with TDD (red-green-refactor-commit), tracks
   sub-steps via TaskCreate/TaskUpdate
3. I validate each proposed next task against epic requirements and anti-patterns
4. After each task: executor writes learnings to project memory and returns;
   lead dispatches fresh executor for next task
5. When all criteria met, a reviewer agent verifies the implementation against the epic spec

This approach prevents context exhaustion (bounded per-task executor lifetime) while
preserving learnings via project memory — no manual /clear cycling needed."
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
- Leverages existing code (faster implementation)
- Consistent architecture (maintainable)
- Research informs design (correct assumptions)
- User sees you understand the codebase (trust)
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
- Wastes time updating or deleting wrong tasks
- Rigid plan fights with reality
</why_it_fails>

<correction>
**Correct approach (iterative):**

```bash
bd create "Epic: Add OAuth" # with immutable requirements
bd create "Task 1: Configure OAuth provider"

# Execute Task 1
# Learn: OAuth library handles refresh; middleware already exists

bd create "Task 2: Integrate with existing middleware"
# [Created AFTER learning from Task 1]

# Execute Task 2
# Learn: UI needs OAuth button component

bd create "Task 3: Add OAuth button to login UI"
# [Created AFTER learning from Task 2]
```

**What you gain:**
- Tasks reflect current reality (accurate plan)
- No wasted time fixing wrong tasks (efficient)
- Each task informed by previous learnings (adaptive)
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

## Architecture
- auth/strategies/google.ts — New OAuth strategy
- auth/passport-config.ts — Register strategy (existing)
- db/models/user.ts — Add googleId field (existing)
- routes/auth.ts — OAuth callback routes

## Architecture Impact
- [ ] Creates a new component/module — NO
- [x] Changes public interface of existing component — YES (User model: add googleId field)
- [ ] Adds/removes cross-component dependency — NO
- [ ] Creates new request path through 2+ components — NO
- [ ] Moves responsibility between components — NO

Result: 1 box checked. /intuition was offered and deferred (user chose to proceed).

## Design Rationale

### Problem
Users must create accounts manually. Manual signup has 40% abandonment rate.
Google OAuth reduces friction and is the most-requested auth feature.

### Research Findings
**Codebase:**
- auth/passport-config.ts:1-50 — Existing passport setup, uses session-based auth
- auth/strategies/local.ts:1-30 — Pattern for adding strategies
- db/models/user.ts:1-80 — User model, already has email field

**External:**
- passport-google-oauth20 — Official Google strategy, 2M weekly downloads
- Google OAuth2 docs — Requires client ID, callback URL, scopes

### Key Decisions Made

| Question | User Answer | Implication |
|----------|-------------|-------------|
| Token storage preference? | httpOnly cookies for security | Anti-pattern: NO localStorage |
| New user model or extend existing? | Use existing at db/models/user.ts | Must add googleId field, not new table |
| Session duration? | 24h inactive timeout | Need refresh token logic |
| What if Google OAuth is down? | Graceful error message | No fallback auth required |

### Approaches Considered

#### 1. Extend passport.js with google-oauth20 (chosen)

**What it is:** Add passport-google-oauth20 strategy to existing passport.js setup.

**Investigation:**
- Reviewed auth/passport-config.ts — existing passport setup with session serialization
- Checked auth/strategies/local.ts:1-30 — shows pattern for adding strategies
- passport-google-oauth20 npm — 2M weekly downloads, actively maintained

**Pros:**
- Matches existing codebase pattern (auth/strategies/)
- Session handling already works (express-session configured)

**Cons:**
- Adds one npm dependency

**Chosen because:** Consistent with auth/strategies/local.ts pattern; minimal delta to existing code.

#### 2. Custom JWT-based OAuth (rejected)

**What it is:** Implement OAuth flow from scratch using JWTs instead of sessions.

**Why explored:** User mentioned 'maybe we should use JWTs'

**Investigation:**
- Counted 15 files using req.session pattern
- Estimated 2 weeks migration effort

**Pros:**
- No new npm dependency
- Stateless (scalability benefit at larger scale)

**Cons:**
- Would require rewriting 15 files using req.session
- Security complexity (token invalidation, refresh logic)

**REJECTED BECAUSE:** Scope creep — OAuth feature should not require rewriting the auth system.

**DO NOT REVISIT UNLESS:** We are already rewriting the entire auth system in a separate epic.

#### 3. Auth0 integration (rejected)

**What it is:** Use Auth0 managed service for OAuth.

**Why explored:** Third-party service might reduce implementation complexity.

**Investigation:**
- Evaluated Auth0 free tier — 7000 MAU limit
- Reviewed Auth0 SDK — different auth model than current codebase

**Pros:**
- Managed service (less code to maintain)

**Cons:**
- External vendor dependency, cost at scale
- Inconsistent with existing codebase auth model

**REJECTED BECAUSE:** Overkill for single OAuth provider; introduces vendor dependency.

**DO NOT REVISIT UNLESS:** We need 3+ OAuth providers AND are comfortable with vendor dependency.

### Scope Boundaries

**In scope:**
- Google OAuth login and signup
- Token storage in httpOnly cookies
- Profile sync with User model

**Out of scope:**
- Other OAuth providers (GitHub, Facebook) — deferred to future epic
- Account linking (connect Google to existing account) — deferred
- Custom OAuth scopes beyond profile/email — not needed now

### Open Questions
- None because all questions were resolved during brainstorm; decisions are in Key Decisions Made above.
"
```

**What you gain:**
- Requirements concrete and specific (testable)
- Forbidden patterns explicit with reasoning (prevents shortcuts)
- Approaches considered show why alternatives were rejected with DO NOT REVISIT conditions
- Open Questions section explicitly acknowledges nothing was deferred (grounded None)
</correction>
</example>

</examples>

<key_principles>
- **One question at a time** — Don't overwhelm; group only IMPORTANT/NICE_TO_HAVE
- **Multiple choice preferred** — Easier to answer; include recommended default
- **Delegate research** — Use codebase-investigator and internet-researcher agents
- **YAGNI ruthlessly** — Remove unnecessary features from all designs
- **Explore alternatives** — Propose 2-3 approaches before settling
- **Incremental validation** — Present design in sections, validate each
- **Epic is contract** — Requirements immutable, tasks adapt
- **Anti-patterns prevent shortcuts** — Explicit forbidden patterns stop rationalization under pressure
- **One task only** — Subsequent tasks created iteratively, not upfront
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

1. **Use AskUserQuestion tool** → Don't print questions and wait for answers
2. **Research BEFORE proposing** → Use agents to understand context before suggesting approaches
3. **Propose 2-3 approaches with trade-offs** → Don't jump to a single solution
4. **Epic requirements IMMUTABLE** → Tasks adapt, requirements don't
5. **Include anti-patterns section** → Prevents watering down requirements when blockers occur
6. **Create ONLY first task** → Subsequent tasks created iteratively as you learn
7. **Run SRE refinement before handoff** → The first task sets the pattern for the entire epic
8. **Offer /intuition when design-time friction detected** → When architect expresses structural uncertainty, shim language, pattern contradiction, or difficulty assigning responsibility
9. **Architecture Impact Check required before epic finalization** → All 5 questions against the designed solution; record result in epic; offer /intuition if any YES
10. **Subsection 'None' requires grounded justification** → "None because [specific reason]" is required; bare "None" or "N/A" enables skip-thinking rationalization

## Common Excuses

All of these mean: **STOP. Follow the process.**

- "Requirements obvious, don't need questions" (Questions reveal hidden complexity)
- "I know this pattern, don't need research" (Research might show a better way or a conflict)
- "Can plan all tasks upfront" (Plans become brittle; tasks adapt as you learn)
- "Anti-patterns section is overkill" (Prevents rationalization under pressure)
- "Epic can evolve" (Requirements are a contract; tasks evolve, requirements don't)
- "Can just print questions" (Use AskUserQuestion tool — it's more interactive and scannable)
- "SRE refinement is overkill for this task" (First task sets the pattern for the entire epic)
- "User said yes, design is done" (Still need Architecture Impact Check and SRE refinement)
- "Only one box checked, /intuition not worth it" (Offer it; the architect decides)
- "'None' is fine here" (Bare 'None' enables skip-thinking; write the reason)
</critical_rules>

<verification_checklist>
Before handing off to executing-plans, confirm:

- [ ] Used AskUserQuestion tool for all clarifying questions (one at a time)
- [ ] Researched codebase patterns (if applicable)
- [ ] Researched external docs or libraries (if applicable)
- [ ] Proposed 2-3 approaches with trade-offs
- [ ] Presented design in sections, validated each
- [ ] Design-time friction check done in Step 3 (offered /intuition if friction present)
- [ ] Architecture Impact Check done in Step 4 (all 5 questions against designed solution)
- [ ] Created bd epic with all 7 sections (Requirements, Success Criteria, Anti-Patterns, Approach, Architecture, Architecture Impact, Design Rationale)
- [ ] Design Rationale has all 6 subsections (Problem, Research Findings, Key Decisions Made, Approaches Considered, Scope Boundaries, Open Questions)
- [ ] Every empty-state subsection has "None because [specific reason]" (not bare "None")
- [ ] Requirements are IMMUTABLE and specific
- [ ] Anti-patterns include reasoning (not just "NO X" but "NO X (reason: Y)")
- [ ] Created ONLY first task (not full tree)
- [ ] First task has detailed implementation checklist
- [ ] Ran SRE refinement on first task (hyperpowers:sre-task-refinement)
- [ ] Announced handoff to executing-plans after refinement approved

**Can't check all boxes?** Return to the process and complete the missing steps.
</verification_checklist>

<integration>
**This skill calls:**
- hyperpowers:codebase-investigator (Step 2: finding existing patterns)
- hyperpowers:internet-researcher (Step 2: external documentation)
- hyperpowers:sre-task-refinement (Step 7: REQUIRED before handoff to executing-plans)
- hyperpowers:executing-plans (Step 8: handoff — lead orchestrates executor subagent after refinement approved)

**BIDIRECTIONAL integration with /intuition:**
- brainstorm → /intuition (two paths):
  - Step 3: design-time friction detected → offer /intuition before committing to design
  - Step 4: Architecture Impact Check returns 1+ YES → offer /intuition before creating epic
- /intuition → brainstorm (Resolution Protocol Step 4):
  - "Brainstorm" resolution option hands off with tension as context
  - The brainstorm produces a design that resolves the tension, resulting in an epic

**Call chain:**
```
FEATURE DEVELOPMENT:
  brainstorming → sre-task-refinement → executing-plans

ARCHITECTURE CYCLE:
  /brainstorm → build → /intuition (health check or tension resolution)
              ↕
  /intuition → find tensions → Step 4 Resolution Protocol
               → "Brainstorm" → /brainstorm (with tension as context)
```

**This skill is called by:**
- User requests for new features or designs
- hyperpowers:using-hyper (mandatory before writing code)
- /intuition Step 4 Resolution Protocol ("Brainstorm" option)
- Beginning of greenfield development

**Agents used:**
- codebase-investigator (understand existing code patterns)
- internet-researcher (find external documentation and library options)

**Tools required:**
- AskUserQuestion (for all clarifying questions — required by Rule 1)
</integration>

<resources>
**When stuck:**
- User gives vague answer → Ask a follow-up multiple choice question with a recommended default
- Research yields nothing → Ask user for direction explicitly
- Too many approaches → Narrow to top 2-3; explain why others were eliminated
- User changes requirements mid-design → Acknowledge, return to Step 1
- Architecture Impact Check results in debate → Offer /intuition; the architect decides
- "None" feels right for a subsection → Write "None because [specific reason]"; this is load-bearing
</resources>
