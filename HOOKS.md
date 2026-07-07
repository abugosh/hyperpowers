# Hyperpowers Hooks Documentation

## Overview

Hyperpowers wires exactly two hooks into Claude Code, and they do two
different jobs:

- **Context injection** (`SessionStart`) — adds text to the model's context.
  It cannot block or deny anything; it only informs.
- **Enforcement** (`PreToolUse`) — can deny a tool call outright by returning
  a `permissionDecision`. This is the only place in the plugin where a hook
  actually stops an action.

Everything else that used to look like enforcement (skill suggestions,
edit logging, "blocking" PostToolUse checks, Stop-hook reminders) has been
removed. It never worked: those hooks read fields Claude Code doesn't send,
or emitted `permissionDecision` from event types where that field has no
effect. See **History** below. Behavior those hooks were meant to prevent is
now the job of prompt-level MUST rules in skills and `CLAUDE.md` — see
**The Keep-Criterion** for why that split is deliberate, not a downgrade.

`hooks/hooks.json` is the single source of truth for what's wired:

```json
{
  "hooks": {
    "SessionStart": [{ "matcher": "startup|resume|clear|compact",
      "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh" }] }],
    "PreToolUse": [{ "matcher": "Bash",
      "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/pre-tool-use/02-version-bump-guard.py" }] }]
  }
}
```

## The Hooks

### `hooks/session-start.sh`

- **Event:** `SessionStart`
- **Input:** `{"hook_event_name": "SessionStart", "source": "startup|resume|clear|compact"}`
- **Output:** `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}`

Injects the contents of `skills/using-hyper/SKILL.md` into the model's
context at session start, plus a one-time warning if a legacy
`~/.config/hyperpowers/skills` directory is found. It always exits 0 and
always emits `additionalContext` — there is no decision field, because
`SessionStart` has nothing to deny.

### `hooks/pre-tool-use/02-version-bump-guard.py`

- **Event:** `PreToolUse`, matcher `Bash`
- **Input:** `{"tool_name": "Bash", "tool_input": {"command": "..."}, "cwd": "..."}`
- **Output (deny):** `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`
- **Output (allow):** no output; exit 0

**What it guards:** a `git push` of the repo's default branch (resolved via
`origin/HEAD`, falling back to the literal `main`/`master` names), in a repo
that has `.claude-plugin/plugin.json` at its root, where the outgoing range
touches `skills/`, `agents/`, `commands/`, `hooks/`, `CLAUDE.md`, or
`README.md` but `plugin.json`'s `version` field did not change in that same
range. It denies with a reminder to bump the version. It recognizes the
push regardless of shell line-continuations, and regardless of
`time`/`command`/`env`/`nice`/`nohup` wrapper prefixes, by tokenizing each
shell segment rather than substring-matching on "push".

**Fail-open contract:** every error path — unparseable stdin, git command
failures, no resolvable upstream, no plugin manifest, non-default-branch
push, `--dry-run` — exits 0 and allows the push. A bug in this hook must
never block work; false-allows are acceptable, false-denies are not.

## The Keep-Criterion

A hook earns its place only when the failure is:

> (a) mechanically checkable at a tool boundary, (b) recurrent despite
> prompt-level instruction, and (c) cheap to verify against Claude Code's
> real I/O contract.

`version-bump-guard` passes all three: forgetting the version bump before
the final push is a documented, repeated failure, checkable purely from
`tool_input.command` and git state, and verifiable without any special
setup. `session-start.sh` is not a deny hook and isn't evaluated against
this criterion — it exists to deliver context, not to block a tool call.

Every hook removed in the 2026-07-07 teardown failed at least one leg of
this test. Do not re-add a hook to work around a behavior problem without
checking it against all three legs first — most behavior problems belong in
a skill or in `CLAUDE.md`, not in a hook.

## Testing

Run the contract tests before trusting either hook:

```bash
./hooks/test/contract-test.sh
```

The runner builds throwaway git repos under `mktemp -d` and pipes fixture
JSON through the live hook scripts, asserting on their real output. The
fixtures are written to match **Claude Code's actual hook schemas** —
`tool_name`/`tool_input` for `PreToolUse`, `hookSpecificOutput` wrapping the
output — never the hook's own assumptions about its input. That distinction
is the whole point: the previous test suite encoded each hook's incorrect
assumptions and passed regardless of whether the hook worked against the
real contract. If you change either hook's input/output handling, update
the fixtures only after confirming the new shape against Claude Code's
documented schema, not against what the hook happens to produce.

## History

On 2026-07-07 a six-dimension review found that seven of the plugin's nine
hooks never worked as documented: the skill/agent suggestion hook read a
prompt field Claude Code doesn't send, three "blocking" PostToolUse hooks
emitted a `permissionDecision` field that only has effect on `PreToolUse`
(and so never blocked anything, despite being labeled "(blocking)" in this
file), the Stop-hook reminders read a nonexistent field, and a beads-read
guard and two guards protecting `.git/hooks/` from direct edits had either
no recurrence evidence or a root cause already fixed upstream. All of it
was deleted rather than
repaired — each failed the keep-criterion above, most on more than one
leg — leaving `session-start.sh` and the hardened `version-bump-guard.py`
as the only two hooks in the plane. See epic bd-854 for the full review,
per-hook verdicts, and the reference-graph cleanup that went with it.
