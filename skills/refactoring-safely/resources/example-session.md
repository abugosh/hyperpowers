## Example: Complete Refactoring Session

**Goal:** Extract validation logic from UserService

**Precondition:** the refactor bd issue `<refactor-id>` already exists with both `## Diagnosis Report` and `## Refactor Design Spec` sections (created by refactoring-diagnosis, appended by refactoring-design).

**Time: 60 minutes**

### Minutes 0-5: Verify Tests Pass
```bash
Dispatch hyperpowers:test-runner: "Run: cargo test"
Result: ✓ 234 tests pass
```

### Minutes 5-10: Confirm the Refactor Issue and Start Work
```bash
bd show <refactor-id>
# Gate (Step 0): design field must contain both "## Diagnosis Report"
# and "## Refactor Design Spec" — created upstream, not here
bd update <refactor-id> --status in_progress
```

### Minutes 10-15: Step 1 - Extract email validation function
```rust
// Extract validate_email()
```
```bash
Dispatch hyperpowers:test-runner: "Run: cargo test"
Result: ✓ 234 tests pass
git commit -m "refactor(<refactor-id>): extract email validation"
```

### Minutes 15-20: Step 2 - Extract name validation function
```rust
// Extract validate_name()
```
```bash
Dispatch hyperpowers:test-runner: "Run: cargo test"
Result: ✓ 234 tests pass
git commit -m "refactor(<refactor-id>): extract name validation"
```

### Minutes 20-25: Step 3 - Create UserValidator struct
```rust
struct UserValidator { /* empty */ }
impl UserValidator { /* empty */ }
```
```bash
Dispatch hyperpowers:test-runner: "Run: cargo test"
Result: ✓ 234 tests pass
git commit -m "refactor(<refactor-id>): create UserValidator struct"
```

### Minutes 25-35: Steps 4-6 - Move validations to UserValidator
Each step: move one method, test, commit

### Minutes 35-45: Step 7 - Update UserService to use validator
```rust
// Use UserValidator instead of inline validation
```
```bash
Dispatch hyperpowers:test-runner: "Run: cargo test"
Result: ✓ 234 tests pass
git commit -m "refactor(<refactor-id>): use UserValidator in UserService"
```

### Minutes 45-55: Step 8 - Remove duplication from other services
Each service: one change, test, commit

### Minutes 55-60: Final verification and close
```bash
Dispatch hyperpowers:test-runner: "Run: cargo test"
Result: ✓ 234 tests pass

Dispatch hyperpowers:test-runner: "Run: cargo clippy"
Result: ✓ No warnings

# Re-emit both artifact sections + ## Completed in the design field (Step 7), then:
bd close <refactor-id>
```

**Result:** Refactoring complete, 8 safe commits, all tests green throughout.
