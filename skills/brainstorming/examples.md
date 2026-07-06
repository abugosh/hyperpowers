# Brainstorming Examples

Worked examples for the brainstorming skill. Read these only when you need a concrete reference — the SKILL.md file has the full process.

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

3. **Ask the evidence-grounded question (AskUserQuestion, recommended option first):**
   ```
   Question: "Extend the existing passport setup for OAuth, or replace the auth model?"
   Options:
     - "Extend auth/passport-config.ts (Recommended)" — matches the existing
       strategy pattern at auth/strategies/local.ts; smallest delta
     - "Replace with custom JWT" — full control, but 15 files currently use
       req.session and would need rewriting
   ```
   The question carries the evidence; the user decides with the trade-off visible.

**What you gain:**
- Leverages existing code (faster implementation)
- Consistent architecture (maintainable)
- Research informs design (correct assumptions)
- User sees you understand the codebase (trust)
</correction>
</example>

<example>
<scenario>Developer creates tasks iteratively during execution</scenario>

<code>
bd create "Epic: Add OAuth" # with immutable requirements
bd create "Task 1: Configure OAuth provider"

# "I'll create the next task after I see how this one goes."

# Execute Task 1
bd create "Task 2: Integrate with existing middleware"  # invented mid-execution

# Execute Task 2
bd create "Task 3: Add OAuth button to login UI"        # invented mid-execution
</code>

<why_it_fails>
- The plan never exists as a reviewable artifact — there is nothing for the human to approve before execution begins
- SRE batch review has nothing to review; systemic gaps across the plan are never caught
- Dependencies are unknowable — execution order emerges by accident instead of by design
- Drift is invisible until late: each mid-flight task quietly reinterprets the epic
- The session's context becomes the plan; a fresh session cannot resume the work from bd alone
</why_it_fails>

<correction>
**Correct approach (complete verified task tree upfront — Step 6c):**

```bash
bd create "Epic: Add OAuth" # with immutable requirements

# Draft ALL tasks, then run pre-create verification on every draft:
# broad structure questions → codebase-investigator
# exact edit sites → read the file directly before writing the change
# Verification catches reality BEFORE tasks are created:
#   ✗ OAuth library handles refresh automatically — no refresh task needed
#   + Middleware already exists at src/middleware/auth.ts — integrate, don't create

bd create "Task 1: Configure OAuth provider"        # paths verified
bd create "Task 2: Extend auth/passport-config.ts"  # confirmed to exist
bd create "Task 3: Add OAuth button to login UI"    # component location verified
bd dep add bd-[t2] bd-[t1] --type blocking
bd dep add bd-[t3] bd-[t2] --type blocking

# Batch SRE review of the full tree (Step 7), then execution begins
```

**When reality still disagrees during execution:** the executor returns BLOCKED or NEEDS_HELP, the lead clarifies or escalates, and the reviewer's gap-fix path creates repair tasks. Adaptation flows through a defined channel — not by improvising the plan mid-flight.

**What you gain:**
- The full plan is reviewable — by the human and by SRE — before any code changes
- Pre-create verification kills wrong-assumption tasks before they exist (the old failure mode of upfront planning)
- Dependencies set execution order deliberately (time bands and ceiling: skills/common-patterns/pipeline-constants.md)
- A fresh session resumes from bd alone — the artifacts carry the state
- Epic requirements stay immutable; tasks adapt through the execution loop (contract preserved)
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
(questions per skills/common-patterns/architecture-impact-check.md)
- Q1 new component: NO
- Q2 public interface change: YES (User model: add googleId field)
- Q3 cross-component dependency added/removed: NO
- Q4 new request path (2+ components): NO
- Q5 responsibility moved: NO

Result: 1 YES. /intuition was offered and deferred (user chose to proceed).

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
