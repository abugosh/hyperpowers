# Common Anti-Patterns

Anti-patterns that apply across multiple skills. Reference this to avoid duplication.

## Language-Specific Anti-Patterns

### Rust

```
❌ No unwrap() or expect() in production code
   Use proper error handling with Result/Option

❌ No todo!(), unimplemented!(), or panic!() in production
   Implement all code paths properly

❌ No #[ignore] on tests without a forge issue reference
   Fix or track broken tests

❌ No unsafe blocks without documentation
   Document safety invariants

❌ Use proper array bounds checking
   Prefer .get() over direct indexing in production
```

### Swift

```
❌ No force unwrap (!) in production code
   Use optional chaining or guard/if let

❌ No fatalError() in production code
   Handle errors gracefully

❌ No disabled tests without a forge issue reference
   Fix or track broken tests

❌ Use proper array bounds checking
   Check indices before accessing

❌ Handle all enum cases
   No default: fatalError() shortcuts
```

### TypeScript

```
❌ No @ts-ignore or @ts-expect-error without a forge issue reference
   Fix type issues properly

❌ No any types without justification
   Use proper typing

❌ No .skip() on tests without a forge issue reference
   Fix or track broken tests

❌ No throw in async code without proper handling
   Use try/catch or Promise.catch()
```

## General Anti-Patterns

### Code Quality

```
❌ No TODOs or FIXMEs without a forge issue reference
   Track work in the forge issue tracker, not in code comments
   (skills/common-patterns/forge-detection.md, Issues; bd holds epics in flight, never a backlog)

❌ No stub implementations
   Empty functions, placeholder returns forbidden

❌ No commented-out code
   Delete it - version control remembers

❌ No debug print statements in commits
   Remove console.log, println!, print() before committing

❌ No "we'll do this later"
   Either do it now or propose a forge issue at a gate and reference it

❌ No comments written for the reviewer
   "Pinned: drop this and C1 reds", "not defensive padding", "do not simplify"
   — that is evidence and argument; it lives in the test, the commit body,
   and bd notes (skills/common-patterns/prose-style.md, Comment Policy)

❌ No comment that proves its own claim
   State the hazard in a sentence. The proof has a home, and it is never the code
```

### Testing

```
❌ Don't test mock behavior
   Test real behavior or unmock it

❌ Don't add test-only methods to production code
   Put in test utilities instead

❌ Don't mock without understanding dependencies
   Understand what you're testing first

❌ Don't skip verifications
   Run the test, see the output, then claim it passes
```

### Process

```
❌ Don't commit without running tests
   Verify tests pass before committing

❌ Don't create MR without running full test suite
   All tests must pass before MR creation

❌ Don't skip validations
   Always run lint, typecheck, tests before committing

❌ Don't force push without explicit request
   Respect shared branch history

❌ Don't assume backwards compatibility is desired
   Ask if breaking changes are acceptable

❌ Don't accept a multi-section report in a subagent's final message
   Reports travel by file; the return is one line (report-file-contract.md)

❌ Don't file a follow-up ticket as the exit for real-but-awkward work
   Tickets are the operator's call (loop-interfaces.md, Opt disposition)
   - Price the work: files, tests, size, the scope line it crosses
   - Ask: bring in / defer / drop — never propose the defer yourself
   - A run that ends in new tickets is the exception

❌ Don't file work that outlives the epic in bd
   bd holds the epic in flight; the forge issue is the ask
   (skills/using-hyper/SKILL.md, Where work is tracked)
   - Bugs outside an epic, review follow-ups, resolve-tension work → forge issue
   - Proposed at a gate with title and body; filed only on approval
   - A decline is recorded, never silent

❌ Don't add or change a rule in a skill or agent prompt without a recorded observation
   The lead authors from evidence; a hypothesis is a question for the user
   (skills/writing-skills/SKILL.md)
   - Subagents: a fresh-agent editor pass, one live use or fixture when
     behavior is uncertain, the A/B probe when removing a guard
   - A sentence an observation falsified is cut, never qualified
```

## Refactoring Anti-Patterns

After refactoring, old code is dead code. Delete it.

```
❌ No fallback code after refactoring
   Old implementation should be DELETED, not kept as fallback
   - If new code works, old code is unnecessary
   - If new code doesn't work, fix it - don't keep old code "just in case"

❌ No "use old/legacy" conditionals
   Feature flags for old implementations = incomplete refactoring
   - USE_LEGACY_*, ENABLE_OLD_*, FALLBACK_TO_*
   - if (useLegacy) { oldImplementation() }
   - These should trigger immediate deletion of old code

❌ No backwards compatibility shims (unless external API)
   Internal code doesn't need backwards compatibility
   - Shims for internal callers = incomplete migration
   - Fix all callers, then delete the shim
   - Only external APIs may need temporary backwards compat

❌ No orphaned tests
   Tests must test current functionality, not removed code
   - Tests for deleted functions = orphaned tests
   - Tests importing removed modules = orphaned tests
   - Delete or update these tests

❌ No deprecation markers without timeline
   Either remove now or propose a forge issue with a removal date
   - @deprecated without action = "keep forever"
   - Every @deprecated needs: forge issue reference + removal date
   - If no external consumers, just delete it now

❌ No "V2" without removing V1
   Version suffixes = incomplete migration
   - authenticateV2() means authenticate() is dead
   - Rename V2 to the canonical name after migration
   - Delete all Vn-1 variants
```

## Project-Specific Additions

Each project may have additional anti-patterns. Check CLAUDE.md for:
- Project-specific code patterns to avoid
- Custom linting rules
- Framework-specific anti-patterns
- Team conventions
