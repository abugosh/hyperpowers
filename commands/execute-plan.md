---
description: Orchestrate plan execution via executor subagents (one per task)
---

Use the hyperpowers:executing-plans skill exactly as written.

**Delegation model:** This command uses blocking subagent dispatch. The lead (main context) dispatches a fresh executor subagent per task via the Agent tool, blocking until the executor returns structured output. After each task, the executor writes learnings to project memory and returns; the lead processes the result and dispatches a fresh executor for the next task. The lead validates proposals against epic requirements and dispatches a reviewer for final verification.

**Resumption:** If work was previously started, the skill resumes from bd state and project memory automatically.
