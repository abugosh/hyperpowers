---
description: Close epic and integrate branch after manual validation complete
---

Use the hyperpowers:finishing-a-development-branch skill exactly as written.

**When to use:** After automated review passes (`/hyperpowers:review-implementation`) and you've completed your manual validation/testing.

**What it does:**
1. Closes the bd epic
2. Verifies tests pass
3. Presents integration options (merge locally, create MR, keep as-is, discard)
4. Executes your choice
5. Cleans up worktree as appropriate

**Prerequisite:** Epic should have all tasks closed and automated review should have passed.
