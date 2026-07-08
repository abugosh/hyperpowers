---
description: Orchestrate plan execution via executor subagents (one per task)
---

Use the hyperpowers:executing-plans skill exactly as written.

**Delegation model:** This command uses blocking subagent dispatch. The lead reads a pre-planned task list and dispatches a fresh executor subagent (Sonnet by default, promotable per skills/common-patterns/pipeline-constants.md) per task via the Agent tool. The executor returns a one-liner (DONE:, BLOCKED:, or NEEDS_HELP:). The lead runs two-stage per-task review (Stage 1: epic-coherence check by the lead; Stage 2: spec-match + code quality by a fresh reviewer), then proceeds to the next task. A reviewer subagent validates the assembled whole at the end.

**Resumption:** If work was previously started, the skill resumes from bd state — use `bd list --parent <epic-id>` to find remaining tasks.
