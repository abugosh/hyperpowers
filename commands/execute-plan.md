---
description: Orchestrate plan execution via executor subagents (one per task)
---

Use the hyperpowers:executing-plans skill exactly as written.

**Delegation model:** This command uses blocking subagent dispatch. The lead reads a pre-planned task list and dispatches a fresh executor subagent (Sonnet by default, promotable per skills/common-patterns/pipeline-constants.md) per task via the Agent tool. The executor returns one status line (DONE:, BLOCKED:, or NEEDS_HELP:), a DONE optionally followed by RED/FLAG report lines. The lead runs two-stage per-task review (Stage 1: epic-coherence check by the lead; Stage 2: an outcome check by a fresh code-reviewer that answers the lead's questions, at full depth on pattern-setting tasks), then proceeds to the next task. A reviewer subagent validates the assembled whole at the end.

**Resumption:** If work was previously started, the skill resumes from bd state — use `bd list --parent <epic-id>` to find remaining tasks.
