---
description: Orchestrate plan execution via executor teammate
---

Use the hyperpowers:executing-plans skill exactly as written.

**Delegation model:** This command creates an agent team. The lead (main context) orchestrates while an executor teammate implements tasks with TDD. The lead validates proposals against epic requirements and dispatches a reviewer for final verification.

**Resumption:** If a team already exists from a previous session, the skill resumes from bd and team state automatically.
