# bd Command Reference

Common bd commands used across multiple skills. Reference this instead of duplicating.

Never Read/Grep `.beads/issues.jsonl` directly — the bd CLI is the only interface (direct access bypasses validation and usually fails on file size).

## Reading Issues

```bash
# Show single issue with full design
bd show bd-3

# List all open issues
bd list --status open -n 0

# List closed issues
bd list --status closed -n 0

# List ALL child tasks of an epic (full tree: include closed, no limit)
# (bd dep tree does not enumerate an epic's children in bd 0.50.x)
bd list --parent bd-1 --all -n 0

# Find issues ready to work on — no blocking dependencies. Surfaces epics as well as tasks (no type filter); defaults to -n 10
bd ready

# Open tasks only (default status filter)
bd list --parent bd-1

# bd children bd-1 is an alias for bd list --parent bd-1 — it inherits the open-only default and the list limit; prefer the explicit form with --all -n 0
```

**bd list defaults to -n 50 and silently truncates.** Use -n 0 on every enumeration or counting command. bd ready defaults to -n 10.

## Creating Issues

```bash
# Create epic
bd create "Epic: Feature Name" \
  --type epic \
  --priority [0-4] \
  --description "[One-line summary for bd list views]" \
  --design "## Goal
[Epic description]

## Success Criteria
- [ ] All phases complete
..."

# Create feature/phase
bd create "Phase 1: Phase Name" \
  --type feature \
  --priority [0-4] \
  --description "[One-line summary]" \
  --design "[Phase design]"

# Create task
bd create "Task Name" \
  --type task \
  --priority [0-4] \
  --description "[One-line summary]" \
  --design "[Task design]"
```

## Updating Issues

```bash
# Update issue design (detailed description)
bd update bd-3 --design "$(cat <<'EOF'
[Complete updated design]
EOF
)"
```

**IMPORTANT**: Provide BOTH on create — `--description` is the one-line summary shown in list views (bd warns when it is missing); `--design` carries the full detailed spec. Never put the full spec in `--description`.

## Managing Status

```bash
# Start working on task
bd update bd-3 --status in_progress

# Complete task
bd close bd-3

# Reopen task
bd update bd-3 --status open
```

**Common Mistakes:**
```bash
# ❌ WRONG - bd status shows database overview, doesn't change status
bd status bd-3 --status in_progress

# ✅ CORRECT - use bd update to change status
bd update bd-3 --status in_progress

# ❌ WRONG - using hyphens in status values (bd rejects this outright)
bd update bd-3 --status in-progress
# Error updating bd-3: validate field update: invalid status: in-progress

# ❌ WRONG - 'done' is not a valid status (also rejected)
bd update bd-3 --status done
# Error updating bd-3: validate field update: invalid status: done

# ✅ CORRECT - use underscores and a valid value, or bd close to complete
bd update bd-3 --status in_progress
bd close bd-3
```

**bd 0.50.3 validates status on write and rejects invalid values with a CLI error — it does NOT silently store them.** A failed `bd update --status` call leaves the issue's status unchanged; recover with `bd update bd-3 --status <valid value>` (or `bd close bd-3` to complete). The error is printed but the command still exits 0 — check output, not exit codes.

**Valid status values:** `open`, `in_progress`, `blocked`, `closed`

## Managing Dependencies

```bash
# Add blocking dependency (LATER depends on EARLIER)
# Syntax: bd dep add <dependent> <dependency>
bd dep add bd-3 bd-2  # bd-3 depends on bd-2 (do bd-2 first)

# Add parent-child relationship
# Syntax: bd dep add <child> <parent> --type parent-child
bd dep add bd-3 bd-1 --type parent-child  # bd-3 is child of bd-1

# List an epic's children
# (bd dep tree does not enumerate an epic's children in bd 0.50.x)
bd list --parent bd-1 --all -n 0
```

## Commit Message Format

Reference bd task IDs in commits (use hyperpowers:test-runner agent):

```bash
# Use test-runner agent to keep verbose output out of context
Dispatch hyperpowers:test-runner agent: "Run: git add <files> && git commit -m 'feat(bd-3): implement feature

Implements step 1 of bd-3: Task Name
'"
```

## Common Queries

```bash
# Check if all tasks in epic are closed
bd list --status open --parent bd-1 -n 0
# Output: [empty] = all closed

# See what's blocking current work
bd ready  # Shows only unblocked tasks

# Find all in-progress work
bd list --status in_progress -n 0
```

Native date filters exist for time-windowed queries: --created-after, --closed-after, --closed-before (see the managing-bd-tasks metrics guide).
