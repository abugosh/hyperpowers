---
description: Execute a wave of parallel tasks using agent teams
---

Use the hyperpowers:team-executing-plans skill exactly as written.

**Resumption:** This command supports explicit resumption. Run it multiple times to continue execution:

1. First run: Spawns teammates for first wave → STOP at wave boundary
2. User reviews wave results, clears context
3. Next run: Resumes from bd state, executes next wave → STOP
4. Repeat until epic complete

**Checkpoints:** Each wave execution ends with a STOP checkpoint. User must run this command again to continue.
