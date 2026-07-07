#!/usr/bin/env bash
#
# Real-schema contract tests for the two surviving hyperpowers hooks.
#
# Why this file exists (R5 of bd-854): the deleted integration-test.sh fed
# each hook the input shape the hook *assumed*, not the shape Claude Code
# actually sends. That self-confirmation let the hook plane rot invisibly.
# This runner pipes fixture JSON in Claude Code's REAL schema through the
# live hooks and asserts on their REAL output contract:
#
#   PreToolUse stdin  : {tool_name, tool_input:{command}, cwd}
#   PreToolUse deny   : stdout JSON .hookSpecificOutput.permissionDecision=="deny"
#                       (the hook ALWAYS exits 0; allow == no deny output)
#   SessionStart out  : stdout JSON .hookSpecificOutput.additionalContext non-empty
#
# The version-bump-guard is exercised against throwaway git repos built in
# mktemp -d so the hook's real git queries (branch, upstream, diff range,
# origin/HEAD) run against real repository state, not mocked stand-ins.
#
# NEGATIVE CONTROL (run manually, do not automate): temporarily delete the
# line-continuation collapse in 02-version-bump-guard.py
#   command = re.sub(r"\\\r?\n", " ", command)
# and re-run. Fixture (b) "multi-line-continuation-push" must flip to FAIL.
# If it still passes, this runner is not actually testing the Task 3 fix.
#
# Portability: stock macOS bash 3.2 + jq + python3. No GNU-only flags, no
# `date +%s%N`, no bashisms beyond 3.2.

set -uo pipefail   # deliberately NOT -e: every fixture runs; failures tally.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
HOOKS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
GUARD="$HOOKS_DIR/pre-tool-use/02-version-bump-guard.py"
SESSION="$HOOKS_DIR/session-start.sh"

PASS=0
FAIL=0

pass() { printf 'PASS  %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf 'FAIL  %s\n        -> %s\n' "$1" "$2"; FAIL=$((FAIL + 1)); }

# --- fixtures -----------------------------------------------------------

TMPROOT="$(mktemp -d "${TMPDIR:-/tmp}/hp-contract.XXXXXXXX")"
trap 'rm -rf "$TMPROOT"' EXIT

# make_repo <dir> <default_branch> <state:unbumped|bumped|feature>
#
# Builds a scratch plugin repo: base commit (plugin.json v1.0.0 + a watched
# skills/ file), a bare local origin holding the base commit, then a second
# "watched-path" commit that changes a watched path. The origin ref stays at
# the base commit, so the hook's outgoing range (origin/<branch>...HEAD) sees
# exactly the watched change -- with a version bump only when state=bumped.
make_repo() {
    local dir="$1" def="$2" state="$3"
    local origin="${dir}.origin.git"
    mkdir -p "$dir"
    git -C "$dir" init -q -b "$def"
    git -C "$dir" config user.email tester@example.com
    git -C "$dir" config user.name Tester
    git -C "$dir" config commit.gpgsign false
    mkdir -p "$dir/.claude-plugin" "$dir/skills/foo"
    printf '{\n  "version": "1.0.0"\n}\n' > "$dir/.claude-plugin/plugin.json"
    printf 'base\n' > "$dir/skills/foo/SKILL.md"
    git -C "$dir" add -A
    git -C "$dir" commit -q -m "base commit"

    git init -q --bare "$origin"
    git -C "$dir" remote add origin "$origin"
    git -C "$dir" push -q -u origin "$def"
    # Non-default-branch repos: make origin/HEAD resolve to the real default
    # so the hook must consult origin/HEAD (not the literal main/master set).
    if [ "$def" != "main" ] && [ "$def" != "master" ]; then
        git -C "$dir" remote set-head origin "$def"
    fi

    # watched-path commit
    if [ "$state" = "feature" ]; then
        git -C "$dir" checkout -q -b feature/x
    fi
    printf 'changed\n' >> "$dir/skills/foo/SKILL.md"
    if [ "$state" = "bumped" ]; then
        printf '{\n  "version": "1.0.1"\n}\n' > "$dir/.claude-plugin/plugin.json"
    fi
    git -C "$dir" add -A
    git -C "$dir" commit -q -m "watched-path change"
}

# stdin_json <command> <cwd> -> PreToolUse stdin in Claude Code's real schema
stdin_json() {
    jq -n --arg cmd "$1" --arg cwd "$2" \
        '{tool_name: "Bash", tool_input: {command: $cmd}, cwd: $cwd}'
}

# run_guard <stdin> -> sets globals OUT and EC
run_guard() {
    OUT="$(printf '%s' "$1" | python3 "$GUARD" 2>/dev/null)"
    EC=$?
}

guard_decision() {
    printf '%s' "$1" | jq -r '.hookSpecificOutput.permissionDecision // empty' 2>/dev/null || true
}

assert_deny() {  # <name> <stdin>
    run_guard "$2"
    if [ "$EC" -ne 0 ]; then fail "$1" "exit $EC, expected 0"; return; fi
    if [ "$(guard_decision "$OUT")" = "deny" ]; then
        pass "$1"
    else
        fail "$1" "expected permissionDecision=deny; stdout=[$OUT]"
    fi
}

assert_allow() {  # <name> <stdin>
    run_guard "$2"
    if [ "$EC" -ne 0 ]; then fail "$1" "exit $EC, expected 0"; return; fi
    if [ "$(guard_decision "$OUT")" = "deny" ]; then
        fail "$1" "expected allow but hook denied; stdout=[$OUT]"
    else
        pass "$1"
    fi
}

# --- version-bump-guard contract ---------------------------------------

REPO_MAIN="$TMPROOT/main"        # main, watched change, NO bump  -> deny
REPO_BUMPED="$TMPROOT/bumped"    # main, watched change + bump    -> allow
REPO_FEATURE="$TMPROOT/feature"  # feature branch, watched change -> allow
REPO_TRUNK="$TMPROOT/trunk"      # non-main default (trunk)       -> deny

make_repo "$REPO_MAIN" main unbumped
make_repo "$REPO_BUMPED" main bumped
make_repo "$REPO_FEATURE" main feature
make_repo "$REPO_TRUNK" trunk unbumped

# (a) single-line unbumped push to main -> DENIED
assert_deny "single-line-unbumped-push-to-main" \
    "$(stdin_json 'git push' "$REPO_MAIN")"

# (b) multi-line continuation push -> DENIED (guards the Task 3 fix)
assert_deny "multi-line-continuation-push" \
    "$(stdin_json "$(printf 'git push \\\n  origin main')" "$REPO_MAIN")"

# (c) wrapper-prefixed pushes, one per epic SC3 wrapper form -> all DENIED
assert_deny "wrapper-time-push" \
    "$(stdin_json 'time git push origin main' "$REPO_MAIN")"
assert_deny "wrapper-command-push" \
    "$(stdin_json 'command git push origin main' "$REPO_MAIN")"
assert_deny "wrapper-env-push" \
    "$(stdin_json 'env VAR=x git push origin main' "$REPO_MAIN")"

# (d) feature-branch push -> ALLOWED
assert_allow "feature-branch-push" \
    "$(stdin_json 'git push origin feature/x' "$REPO_FEATURE")"

# (e) push with version bump in range -> ALLOWED
assert_allow "bumped-push-to-main" \
    "$(stdin_json 'git push origin main' "$REPO_BUMPED")"

# (f) malformed stdin -> fail-open, exit 0, no deny -> ALLOWED
assert_allow "malformed-stdin-fail-open" \
    'this is not valid json {{{'

# (g) non-main default branch (origin/HEAD -> trunk) -> DENIED.
#     `git push origin trunk` only denies if the hook resolved trunk as the
#     default via origin/HEAD; a fallback to {main,master} would allow it, so
#     this fixture proves the origin/HEAD resolution path.
assert_deny "trunk-default-branch-push" \
    "$(stdin_json 'git push origin trunk' "$REPO_TRUNK")"

# --- session-start contract --------------------------------------------

SESSION_OUT="$(printf '%s' '{"hook_event_name":"SessionStart","source":"startup"}' \
    | bash "$SESSION" 2>/dev/null)"
SESSION_EC=$?
if [ "$SESSION_EC" -ne 0 ]; then
    fail "session-start-additional-context" "exit $SESSION_EC, expected 0"
else
    CTX="$(printf '%s' "$SESSION_OUT" \
        | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null || true)"
    if [ -n "$CTX" ]; then
        pass "session-start-additional-context"
    else
        fail "session-start-additional-context" \
            "expected non-empty .hookSpecificOutput.additionalContext; stdout=[$SESSION_OUT]"
    fi
fi

# --- tally --------------------------------------------------------------

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -eq 0 ]; then
    exit 0
else
    exit 1
fi
