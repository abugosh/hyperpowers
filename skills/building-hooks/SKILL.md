---
name: building-hooks
description: Use when creating Claude Code hooks - covers the keep-criterion for whether a hook should exist, real hook events and schemas, the two hook jobs (context injection, PreToolUse enforcement), and mandatory contract testing
---

<skill_overview>
Claude Code hooks do exactly two jobs:

1. **Context injection** — `SessionStart` / `UserPromptSubmit` return
   `additionalContext` that reaches the model. They inform; they cannot deny.
2. **Enforcement** — `PreToolUse` returns a `permissionDecision` of `deny`
   and stops a tool call before it runs. This is the *only* place in the
   plugin where a hook actually blocks an action.

Before either job matters, the **keep-criterion** decides whether a hook
should exist at all. Most "make Claude stop doing X" requests are not hook
material — they belong in a skill or `CLAUDE.md`. Reach for a hook only when
the failure is mechanically checkable at a tool boundary, recurs despite
prompt-level instruction, and is cheap to verify against Claude Code's real
I/O contract.
</skill_overview>

<rigidity_level>
MEDIUM FREEDOM — two things are non-negotiable: (1) run the keep-criterion
before building any hook, and (2) ship contract-test fixtures written against
Claude Code's real schema, with a green `./hooks/test/contract-test.sh` run,
before wiring the hook. Implementation patterns (language, structure, log
format) adapt to the job.
</rigidity_level>

<quick_reference>
**Keep-criterion (all three legs, or it's not a hook):**
- (a) mechanically checkable at a tool boundary
- (b) recurrent despite prompt-level instruction
- (c) cheap to verify against Claude Code's real I/O contract

**The two jobs:** context injection (`SessionStart` / `UserPromptSubmit`
`additionalContext`) · enforcement (`PreToolUse` `permissionDecision: deny`).

**Canon examples — the only two hooks this plugin ships:**
- `hooks/session-start.sh` — context injection (see HOOKS.md).
- `hooks/pre-tool-use/02-version-bump-guard.py` — the one enforcement hook.

**MUST:** no new hook ships without contract-test fixtures against the real
schema and a green `./hooks/test/contract-test.sh` run.
</quick_reference>

<when_to_use>
Use a hook for:
- **Context injection** — deliver text into the model's context at session
  start or prompt submit (skill routing, project state, reminders).
- **Tool-call enforcement** — deny a specific, mechanically detectable tool
  call that keeps slipping past prompt-level rules (the version-bump guard).

**Never use hooks for:**
- **Behavior problems that fail the keep-criterion** — "Claude keeps doing X"
  where X isn't checkable at a tool boundary, or where a MUST rule in a skill
  or `CLAUDE.md` would work. That's a prompt-level fix, not a hook.
- **Anything needing LLM reasoning** — hooks are deterministic scripts.
- **Slow operations that stall the workflow** — hooks run on the critical path.
- **"Enforcement" on events that can't enforce** — a `PostToolUse` or `Stop`
  hook emitting `permissionDecision` blocks nothing (see Blocking facts).
</when_to_use>

<keep_criterion>
A hook earns its place only when the failure is (quoted from HOOKS.md, the
source of truth, lines 71-88):

> (a) mechanically checkable at a tool boundary, (b) recurrent despite
> prompt-level instruction, and (c) cheap to verify against Claude Code's
> real I/O contract.

**Passing example — `version-bump-guard`.** Forgetting the `plugin.json`
version bump before the final push is (a) checkable purely from
`tool_input.command` plus git state, (b) a documented, repeated failure, and
(c) verified end-to-end by the contract tests. All three legs pass, so the
hook is justified.

**Failing example — the torn-out edit-log → Stop-reminder pipeline.** Per
HOOKS.md History (lines 109-123), the 2026-07-07 teardown deleted seven of
nine hooks. The edit-logging + Stop-reminder chain failed the keep-criterion
because it read fields Claude Code does not send and emitted
`permissionDecision` from event types where that field has no effect — so it
never blocked anything despite being labeled "(blocking)". It was deleted,
not repaired. Do not reproduce its design; treat it as the archetype of a
hook that fails legs (a) and (c).

When a behavior problem arrives, run all three legs first. Most fail leg (a)
or (b) and belong in a skill or `CLAUDE.md`, not in a hook.
</keep_criterion>

<two_jobs>
**Job 1 — Context injection.** `SessionStart` and `UserPromptSubmit` return
`hookSpecificOutput.additionalContext`, a string that is appended to the
model's context. These hooks *inform*: they cannot deny, block, or veto.
`session-start.sh` is this job's canon example.

**Job 2 — Enforcement.** `PreToolUse` returns
`hookSpecificOutput.permissionDecision` — `allow`, `deny`, or `ask`. `deny`
stops the tool call before it runs. This is the only enforcement surface the
plugin's keep-criterion has ever justified, and `version-bump-guard` is its
only instance.

<blocking_facts>
Four facts govern what can and cannot block. All four are load-bearing:

(a) **`PreToolUse` `permissionDecision: deny` is the only way to block a tool
    call before it runs** — and the only enforcement mechanism this plugin's
    keep-criterion has ever justified.

(b) **The platform does offer blocking on other events** — exit code 2, or a
    top-level `decision: "block"`. A `Stop` hook can prevent Claude from
    stopping; a `UserPromptSubmit` hook can block a prompt. This skill
    *deliberately teaches none of those as patterns* — one-line capability
    acknowledgments only, because none has passed the keep-criterion here.

(c) **Exit code 1 NEVER blocks anything.** Only exit code 2 is a blocking
    error. Exit 1 is a non-blocking error: the message is surfaced and
    execution proceeds. A hook that does `... || exit 1` to "enforce" a rule
    enforces nothing.

(d) **`permissionDecision` has no effect outside `PreToolUse`.** Emitting it
    from `PostToolUse`, `Stop`, or anywhere else is inert — the tool already
    ran (or the field is simply ignored). This is the exact failure class the
    2026-07-07 teardown removed.
</blocking_facts>
</two_jobs>

<hook_events>
The events below are the ones worth knowing. Capability facts are what the
event can and cannot do — verified against Claude Code's contract.

| Event | Fires | Capability |
|-------|-------|------------|
| SessionStart | session begins/resumes (source: startup / resume / clear / compact) | cannot block; stdout / `additionalContext` reaches context |
| UserPromptSubmit | before Claude processes a prompt | can block (`decision: "block"` erases the prompt) — this plugin does not use it; stdout becomes context; 30s default timeout |
| PreToolUse | before a tool call | THE tool-call gate: `hookSpecificOutput.permissionDecision` allow/deny/ask; matcher = tool name |
| PermissionRequest | when a permission dialog would appear | can allow/deny via `hookSpecificOutput.decision` |
| PostToolUse | after a tool call succeeds | cannot block (tool already ran); `decision: "block"` only feeds a reason back to Claude |
| PostToolUseFailure | after a tool call fails | the real failure event; the "tool-error" event some old hooks assumed does not exist; cannot block |
| Stop | when Claude finishes responding | can prevent stopping (exit 2 / `decision: "block"`; `stop_hook_active` guard, hard cutoff after 8 consecutive blocks) — this plugin does not use it |
| SubagentStop | subagent finishes | as Stop, for subagents |
| PreCompact | before context compaction | can block compaction; rarely needed |
| SessionEnd | session terminates | cannot block; 1.5s default timeout |

This is **not** the full contract — roughly 30 events exist. Full reference:
https://code.claude.com/docs/en/hooks (the older documentation URLs now
redirect here). Verify any event you use against that page before writing a
fixture for it.
</hook_events>

<schemas>
Hooks receive JSON on **stdin** and (for the two jobs above) return JSON on
**stdout**. Fields below are the real ones — write fixtures against these,
never against what a hook assumes.

**Common stdin fields (every event):**
- `session_id` — the session's id
- `cwd` — working directory when the hook fires
- `hook_event_name` — e.g. `"PreToolUse"`

**Per-event stdin additions:**
- `PreToolUse` — `tool_name`, `tool_input`, `tool_use_id`
- `PostToolUse` — the `PreToolUse` fields plus `tool_response`
- `UserPromptSubmit` — `prompt`
- `SessionStart` — `source` (`startup` / `resume` / `clear` / `compact`)

**Output wrapper.** Both jobs return their result under `hookSpecificOutput`:
- Context: `{"hookSpecificOutput": {"hookEventName": "...", "additionalContext": "..."}}`
- Enforcement: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`

**Fail-open convention.** Every error path exits 0 with no output — which
Claude Code reads as "allow". `version-bump-guard` follows this rigorously:
unparseable stdin, git failures, missing manifest, unexpected state all exit
0 and allow. A bug in a hook must never block work; false-allows are
acceptable, false-denies are not.
</schemas>

<worked_example_session_start>
`hooks/session-start.sh` — **context injection.**

- **Event:** `SessionStart`, matcher `startup|resume|clear|compact`.
- **Reads:** `skills/using-hyper/SKILL.md` from the plugin root, plus a
  one-time legacy-directory warning.
- **Emits:** one JSON object with
  `hookSpecificOutput.additionalContext` containing the escaped skill text.
- **Always exits 0. There is no decision field** — `SessionStart` has nothing
  to deny, so the hook's entire job is to deliver text into context. It is not
  a deny hook and is not evaluated against the keep-criterion (HOOKS.md).

The shape it emits is the canonical context-injection output; any new
`SessionStart` or `UserPromptSubmit` hook copies this wrapper exactly.
</worked_example_session_start>

<worked_example_version_guard>
`hooks/pre-tool-use/02-version-bump-guard.py` — **enforcement.**

**What it guards:** a `git push` of the repo's default branch (resolved via
`origin/HEAD`, falling back to literal `main`/`master`), in a repo with
`.claude-plugin/plugin.json` at its root, where the outgoing range touches a
watched path (`skills/`, `agents/`, `commands/`, `hooks/`, `CLAUDE.md`,
`README.md`) but the manifest's `version` field did not change in that same
range. On that exact condition it denies with a reminder to bump the version.

**Deny output shape:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "🚫 PUSH BLOCKED: plugin.json version not bumped\n..."
  }
}
```

**Fail-open contract.** Every error path — unparseable stdin, git command
failure, no resolvable upstream, no plugin manifest, non-default-branch push,
`--dry-run` — exits 0 and allows the push. False-allows are acceptable;
false-denies are not. A `try/except` around `main()` catches any unhandled
exception and exits 0.

**Robustness.** It recognizes the push regardless of shell line-continuations
(`git push \` + newline is collapsed first) and regardless of
`time`/`command`/`env`/`nice`/`nohup` wrapper prefixes, by shlex-tokenizing
each shell segment and requiring `push` to be git's subcommand token — never
substring-matching on the word "push" (so an echoed or grep'd "push" never
trips it).

**Contract tests.** `hooks/test/contract-test.sh` exercises it with 9
fixtures against throwaway git repos: single-line unbumped push (deny),
multi-line continuation push (deny), three wrapper-prefixed pushes —
time/command/env (deny), feature-branch push (allow), bumped push (allow),
malformed stdin (fail-open allow), and a non-main default branch resolved via
`origin/HEAD` (deny). A 10th fixture covers `session-start.sh`. Fixtures use
the real `PreToolUse` schema — `{tool_name, tool_input:{command}, cwd}` — not
the hook's own assumptions.
</worked_example_version_guard>

<building_a_new_hook>
1. **Run the keep-criterion.** Check all three legs (HOOKS.md, lines 71-88).
   Most behavior problems fail leg (a) or (b) and belong in a skill or
   `CLAUDE.md`. If any leg fails, stop — do not build a hook.
2. **Design fail-open.** Decide the allow default; make every error path exit
   0 with no output. A hook bug must never block work.
3. **Write `contract-test.sh` fixtures FIRST**, against the official schema
   (see `<schemas>` and https://code.claude.com/docs/en/hooks) — never against
   the hook's own assumptions about its input.
4. **Implement** the hook to satisfy those fixtures.
5. **Wire it** into `hooks/hooks.json` (matcher + `hooks` array).
6. **Document it** in HOOKS.md (event, input, output, what it guards,
   fail-open contract).
7. **Run `./hooks/test/contract-test.sh`** and confirm it is green.

**MUST:** no new hook ships without fixtures against the real schema and a
green contract-test run. A hook that "works when I try it manually" but has no
fixture is not done.
</building_a_new_hook>

<testing>
**The harness.** `./hooks/test/contract-test.sh` is the source of truth for
hook correctness. It builds throwaway git repos under `mktemp -d`, pipes
fixture JSON in Claude Code's real schema through the live hook scripts, and
asserts on their real output. Run it before trusting any hook change — this is
a MUST, not a suggestion.

**Manual isolation.** Pipe a fixture into the script directly and inspect
stdout and exit code:
```bash
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"git push"},"cwd":"/path/to/repo"}' \
  | python3 hooks/pre-tool-use/02-version-bump-guard.py; echo "exit=$?"
```

**Execution facts (verified against the contract, not folklore):**
- The default hook timeout is **600 seconds** (`UserPromptSubmit` is 30s,
  `SessionEnd` 1.5s) — not the ten-second value older docs claimed.
- **All matching hooks run in parallel.** There is no filename-order execution
  and no numeric-prefix ordering — a `10-`/`20-` filename prefix does not
  sequence hooks. If one hook depends on another's output, combine them or
  share state through a file; do not rely on ordering.

Deep dive: `resources/testing-hooks.md` (4-level strategy: unit, integration
with mock events, manual, regression) — its integration section points back
at `contract-test.sh` as the worked, executable model.
</testing>

<security>
**Hooks run with your credentials and have full system access.**

## Best Practices
1. **Review code carefully** — hooks execute any command.
2. **Use absolute paths** — don't rely on `PATH`.
3. **Validate inputs** — don't trust stdin fields blindly.
4. **Limit scope** — only touch what the hook needs (the version guard is
   inert outside plugin repos — it checks for `.claude-plugin/plugin.json`).
5. **Log actions** — track what hooks do, without leaking secrets.
6. **Test thoroughly** — especially enforcement hooks, via contract fixtures.

## Dangerous Patterns
The model's tool input is untrusted data. Inspect it — never execute it.

❌ **Don't** — `eval` a field from stdin:
```bash
stdin=$(cat)
cmd=$(printf '%s' "$stdin" | jq -r '.tool_input.command')
eval "$cmd"   # DANGEROUS: runs whatever the model produced
```

✅ **Do** — read the field as data and decide:
```bash
stdin=$(cat)
cmd=$(printf '%s' "$stdin" | jq -r '.tool_input.command')
case "$cmd" in
  *"rm -rf /"*)
    jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "refuses to run a destructive command"}}'
    ;;
  *) exit 0 ;;  # allow: no output
esac
```
</security>

<examples>
<example>
<scenario>Developer "enforces" a coding standard with a PostToolUse hook that emits permissionDecision, plus a Stop hook that uses exit 1 to "block" until the standard is met.</scenario>

<code>
# PostToolUse hook — author believes this denies the edit
jq -n '{hookSpecificOutput: {hookEventName: "PostToolUse", permissionDecision: "deny", permissionDecisionReason: "fix the standard first"}}'

# Stop hook — author believes exit 1 stops Claude
run_standard_check || exit 1
</code>

<why_it_fails>
- `permissionDecision` has no effect outside `PreToolUse` — the `PostToolUse`
  hook fires *after* the tool already ran, and the field is inert there. It
  denies nothing.
- `exit 1` NEVER blocks anything. Only `exit 2` is a blocking error; exit 1 is
  a non-blocking error and execution proceeds. The Stop hook stops nothing.
- Neither hook ever worked — this is the exact 2026-07-07 teardown failure
  class (HOOKS.md History): fields read/emitted where they have no effect.
</why_it_fails>

<correction>
Run the keep-criterion first. Is the standard violation (a) checkable at a
tool boundary, (b) recurrent despite prompt-level instruction, and (c) cheap
to verify against the real contract?

- **If all three legs pass:** implement it as a `PreToolUse` hook returning
  `permissionDecision: deny` — the *only* surface that blocks a tool call
  before it runs — and write contract-test fixtures against the real
  `PreToolUse` schema before wiring it.
- **If any leg fails** (most standards fail (a) — they need judgment, not a
  mechanical check): write the rule into the governing skill or `CLAUDE.md` as
  a MUST. That is not a downgrade; it is where behavior rules belong.

Explicitly: `permissionDecision` outside `PreToolUse` does nothing, and
`exit 1` does not block — the two claims the original design rested on are
both false.
</correction>
</example>
</examples>

<critical_rules>
## Rules That Have No Exceptions
1. **Run the keep-criterion before any hook** — all three legs, or it's a
   prompt-level fix, not a hook.
2. **Write fixtures against the real schema** — never against the hook's own
   assumptions; a self-confirming test lets the hook rot invisibly.
3. **Design enforcement hooks fail-open** — every error path exits 0 (allow);
   false-allows acceptable, false-denies not.
4. **Never claim a blocking capability the contract does not grant** —
   `permissionDecision` only works in `PreToolUse`; `exit 1` never blocks.
5. **Keep hooks fast** — they run on the critical path (default timeout 600
   seconds, but a slow hook stalls the workflow long before that).

## Common Excuses
Each of these means: **STOP and check the real contract.**
- "This behavior problem needs a hook" → Check the keep-criterion first; most
  fail leg (a) or (b) and belong in a skill or `CLAUDE.md`.
- "The hook is simple, skip the fixtures" → No fixture, no ship.
- "I'll make it block with exit 1" → Exit 1 never blocks; only exit 2 does.
- "I'll deny from PostToolUse" → `permissionDecision` is inert outside
  `PreToolUse`; the tool already ran.
- "I'll order hooks by filename prefix" → Matching hooks run in parallel;
  prefixes don't sequence anything.
</critical_rules>

<verification_checklist>
Before wiring a hook:
- [ ] Keep-criterion legs (a), (b), (c) documented — the hook passes all three
- [ ] Contract-test fixtures added against the real schema
- [ ] `./hooks/test/contract-test.sh` green
- [ ] Wired in `hooks/hooks.json` (matcher + `hooks` array)
- [ ] Entry written in HOOKS.md (event, I/O, what it guards, fail-open)
- [ ] Fail-open verified — every error path exits 0 and allows

**Can't check all boxes?** It's not ready. Return to `<building_a_new_hook>`.
</verification_checklist>

<integration>
**This skill covers:** whether a hook should exist, the real event/schema
contract, and how to build and test one.

**Source of truth:** HOOKS.md — the two-hook inventory, the keep-criterion,
and the 2026-07-07 teardown History. When this skill and HOOKS.md disagree,
HOOKS.md wins; update it when you add or change a hook.

**Related skills:**
- hyperpowers:using-hyper — the routing skill injected into context by
  `hooks/session-start.sh` (see HOOKS.md).
- hyperpowers:verification-before-completion — a hook is not done until its
  contract tests are green; this is that principle applied to hooks.
- hyperpowers:testing-anti-patterns — the self-confirming fixture (testing the
  hook's assumptions instead of the real schema) is the anti-pattern to avoid.
</integration>

<resources>
**Detailed guides:**
- [resources/hook-examples.md](resources/hook-examples.md) — 6 complete worked
  examples across events (Example 6 is the only enforcement one, a `PreToolUse`
  `permissionDecision` deny).
- [resources/hook-patterns.md](resources/hook-patterns.md) — 14 reusable
  technique patterns (path validation, project-root detection, caching,
  parallel execution, etc.; the only blocking one is "Conditional Blocking",
  a `PreToolUse` deny).
- [resources/testing-hooks.md](resources/testing-hooks.md) — 4-level testing
  strategy (unit, integration with mock events, manual, regression), pointing
  back at `contract-test.sh`.

**Official documentation:** https://code.claude.com/docs/en/hooks
</resources>
