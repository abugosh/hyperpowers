# bd Metrics Guide

This guide covers the key metrics for tracking work in bd.

## Cycle Time vs. Lead Time

**Two distinct time measurements:**

### Cycle Time

- **Definition**: Time from "work started" to "work completed"
- **Start**: When task moves to "in progress" status
- **End**: When task moves to "closed" status
- **Measures**: How efficiently work flows through active development
- **Use**: Identify process inefficiencies, improve development speed

> **bd's JSONL backend does not record status-transition timestamps** (`bd history` requires the Dolt backend), so cycle time (in_progress -> closed) cannot be computed from bd data. `updated_at` is not a valid proxy — it moves on any design or notes edit. Use lead time below as the measurable end-to-end metric.

### Lead Time

- **Definition**: Time from "request created" to "delivered to customer"
- **Start**: When task is created (enters backlog)
- **End**: When task is deployed/delivered
- **Measures**: Overall responsiveness to requests
- **Use**: Set realistic expectations, measure total process duration

```bash
# Calculate lead time for completed task
bd show bd-5 --json | jq -r '.[0] | .created_at + " -> " + .closed_at'
```

- `closed_at` exists only on closed issues (`bd show --json` omits null fields).
- Deployment time is not tracked by bd — if you need deploy-inclusive lead time, join against your deploy tooling's records.

### Key Differences

| Metric | Starts | Ends | Includes Waiting? | Measures |
|--------|--------|------|-------------------|----------|
| **Cycle Time** | In progress | Closed | No | Development efficiency |
| **Lead Time** | Created | Deployed | Yes | Total responsiveness |

### Example

```
Task created: Monday 9am (enters backlog)
↓ [waits 2 days]
Task started: Wednesday 9am (moved to in progress)
↓ [active work]
Task completed: Wednesday 5pm (moved to closed)
↓ [waits for deployment]
Task deployed: Thursday 2pm (delivered)

Cycle Time: 8 hours (Wednesday 9am → 5pm)
Lead Time: 3 days, 5 hours (Monday 9am → Thursday 2pm)
```

### Why Both Matter

- **Short cycle time, long lead time**: Work is efficient once started, but tasks wait too long in backlog
  - Fix: Reduce WIP, start fewer tasks, finish faster

- **Long cycle time, short lead time**: Work starts immediately but takes forever to complete
  - Fix: Split tasks smaller, remove blockers, improve focus

- **Both long**: Overall process is slow
  - Fix: Address both backlog management AND development efficiency

### Tracking Over Time

```bash
# Average lead time (manual calculation)
# For each closed task: (closed_at - created_at) — lead time
# Sum and divide by task count

# Trend analysis
# Week 1: Avg lead time = 3 days
# Week 2: Avg lead time = 2 days  ✅ Improving
# Week 3: Avg lead time = 4 days  ❌ Getting worse
```

### Improvement Targets

- **Cycle time**: Reduce by splitting tasks, removing blockers, improving focus
- **Lead time**: Reduce by prioritizing backlog, reducing WIP, faster deployment

## Work in Progress (WIP)

```bash
# All in progress tasks
bd list --status in_progress -n 0

# Count
bd list --status in_progress -n 0 --json | jq length
```

### WIP Limits

Work in Progress limits prevent overcommitment and identify bottlenecks.

**Setting WIP limits:**
- **Personal WIP limit**: 1-2 tasks in progress at a time
- **Team WIP limit**: Depends on team size and workflow stages
- **Rule of thumb**: WIP limit = (Team size ÷ 2) + 1

**Example for individual developer:**
```
✅ Good: 1 task in progress, 0-1 in code review
❌ Bad: 5 tasks in progress simultaneously
```

**Example for team of 6:**
```
Workflow stages and limits:
- Backlog: Unlimited
- Ready: 8 items max
- In Progress: 4 items max  (team size ÷ 2 + 1)
- Code Review: 3 items max
- Testing: 2 items max
- Done: Unlimited
```

### Why WIP Limits Matter

1. **Focus:** Fewer tasks means deeper focus, faster completion
2. **Flow:** Prevents bottlenecks from accumulating
3. **Quality:** Less context switching, fewer mistakes
4. **Visibility:** High WIP indicates blocked work or overcommitment

### Monitoring WIP

```bash
# Check personal WIP
bd list --status in_progress -a <assignee> -n 0 --json | jq length

# If > 2: Focus on finishing before starting new work
```

Assignee is set explicitly via `bd update <id> --assignee <name>` and is distinct from owner; it is unset by default, so this returns 0 until your team assigns issues.

### Red Flags

- WIP consistently at or above limit (need more capacity or smaller tasks)
- WIP growing week-over-week (work piling up, not finishing)
- WIP high but velocity low (tasks blocked or too large)

### Response to High WIP

1. Finish existing tasks before starting new ones
2. Identify and remove blockers
3. Split large tasks
4. Add capacity (if chronically high)

## Bottleneck Identification

```bash
# Find tasks that block the most other tasks (top bottlenecks)
# -t blocks excludes parent-child edges so epics do not dominate the list
bd list --status open -n 0 --json | jq -r '.[].id' | while read t; do
  n=$(bd dep list "$t" --direction=up -t blocks --json | jq length)  # bd dep list has no -n flag (like bd blocked) — full list always
  echo "$t $n"
done | sort -k2 -nr | head
```
