---
description: Close epic and integrate branch after manual validation complete
---

Use the hyperpowers:finishing-a-development-branch skill exactly as written.

**When to use:** After the end-of-epic reviewer gate passes (executing-plans completion) and you've completed your manual validation/testing.

**What it does:**
1. Verifies all epic tasks are closed
2. Verifies tests pass
3. Presents integration options (merge locally, create MR, keep as-is, discard)
4. Executes your choice — merge/MR/keep close the epic; discard records a note and leaves it open
5. Cleans up worktree as appropriate

**Prerequisite:** Epic should have all tasks closed and automated review should have passed.
