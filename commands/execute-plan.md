---
description: Orchestrate plan execution via executor teammates (one per task)
---

Use the hyperpowers:executing-plans skill exactly as written.

**Delegation model:** This command creates an agent team. The lead (main context) orchestrates while a fresh executor teammate implements each individual task with TDD. After each task, the executor writes learnings to project memory and idles out naturally; the lead spawns a fresh executor for the next task. The lead validates proposals against epic requirements and dispatches a reviewer for final verification.

**Resumption:** If a team already exists from a previous session, the skill resumes from bd, team state, and project memory automatically.
