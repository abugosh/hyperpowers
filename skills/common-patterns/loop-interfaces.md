# Loop Interfaces

Single source of truth for the artifacts that cross the boundary between a
working session and its governor (the human rotating across parallel lanes),
and between per-repo sessions and a shared planning layer. Skills reference
these formats instead of restating them.

## Gate-State Block

Emitted whenever a session pauses at a user gate (approval, escalation,
completion, handoff) — AND persisted to the epic's bd notes (`bd update
<epic-id> --notes`), so a fresh session reconstructs the gate from bd alone.
A stalled lane is acceptable only when the stall is visible on return.

Format (three sections, always in this order):

```
GATE STATE (<date>, <context>):
Where we are: <one or two sentences — phase, what is complete, what is in flight>
Decided: <decisions taken since the last gate, including async-veto items>
Needs you: <the specific decision(s) or confirmation(s) the gate is waiting on;
  or "nothing — informational" for completion states>
```

Gate questions must be answerable in durable prose — never only via an
expiring interactive element. The governor may return hours later.

## Plan-Impact Notice

Emitted when per-repo work invalidates or constrains an assumption in a
shared planning layer (a phase document in a planning repo). Sessions NEVER
write the shared docs — the notice is carried upward and applied by the user.

Persist to bd (epic notes, prefixed `PLAN-IMPACT:`) and include in the
gate-state block's Decided or Needs-you section.

Format:

```
PLAN-IMPACT: <one-line title>
Assumption affected: <what the plan doc asserts, with file/section if known>
What was learned: <the evidence from this repo's work>
Siblings likely affected: <which other services/epics care, or "none known">
Proposed edit: <concrete wording or diff for the planning-repo doc — the
  user applies it at the base view>
```

## Signal Policy (pushed vs pulled)

**Pushed to the user** (surface immediately in the gate-state block and,
where it exists, the lane's final message): plan-impact notices, provenance
drift flags (a cited plan doc changed since the epic recorded its SHA),
escalations, and lane-completion gate-states. These are drift-tier or
blocking — the costs the governor ranks highest.

**Pulled on demand** (recorded in bd, never volunteered): executor churn
statistics, token burn, and progress rollups. These are noise-tier — bd
holds them for whoever asks.
