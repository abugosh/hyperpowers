#!/usr/bin/env python3
"""
PreToolUse hook: block `git push` from Claude-plugin repos when watched
paths changed without a plugin.json version bump.

Scope guard: only fires when .claude-plugin/plugin.json exists at the repo
root — inert everywhere else.

Fail-open design: every error path (unparseable input, git failures,
missing upstream, unexpected state) exits 0 and allows the push. A hook bug
must never block work. False-allows are acceptable; false-denies are not.

Q6 governor prosthetic (RW4 → RW6a): version-bump-before-push is the
single most-dropped step in plugin development.
"""

import json
import os
import re
import subprocess
import sys

WATCHED = ("skills/", "agents/", "commands/", "hooks/", "CLAUDE.md", "README.md")
PLUGIN_MANIFEST = os.path.join(".claude-plugin", "plugin.json")


def run_git(args, cwd):
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def main():
    input_data = json.load(sys.stdin)

    if input_data.get("tool_name", "") != "Bash":
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")
    if not re.search(r"\bgit\b[^\n;|&]*\bpush\b", command):
        sys.exit(0)
    if "--dry-run" in command:
        sys.exit(0)

    cwd = input_data.get("cwd") or os.getcwd()

    repo_root = run_git(["rev-parse", "--show-toplevel"], cwd)
    if not repo_root:
        sys.exit(0)

    # Scope guard: only plugin repos.
    if not os.path.isfile(os.path.join(repo_root, PLUGIN_MANIFEST)):
        sys.exit(0)

    # Only guard pushes of the default branch — the version-bump rule targets
    # the final push. Mid-epic feature-branch pushes stay free (false-deny bias).
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    if branch not in ("main", "master") and not re.search(
        r"\b(main|master)\b", command
    ):
        sys.exit(0)

    # Base for the outgoing range: upstream of HEAD, else origin/main.
    base = run_git(["rev-parse", "--abbrev-ref", "@{u}"], repo_root)
    if not base:
        if run_git(["rev-parse", "--verify", "origin/main"], repo_root):
            base = "origin/main"
        else:
            sys.exit(0)  # cannot judge the range; allow

    changed = run_git(["diff", f"{base}...HEAD", "--name-only"], repo_root)
    if changed is None:
        sys.exit(0)
    changed_files = [f for f in changed.split("\n") if f]

    watched_hits = [
        f for f in changed_files
        if f.startswith(("skills/", "agents/", "commands/", "hooks/"))
        or f in ("CLAUDE.md", "README.md")
    ]
    if not watched_hits:
        sys.exit(0)

    manifest_diff = run_git(
        ["diff", f"{base}...HEAD", "--", PLUGIN_MANIFEST], repo_root
    )
    if manifest_diff is None:
        sys.exit(0)
    if re.search(r'^[+-].*"version"', manifest_diff, re.MULTILINE):
        sys.exit(0)  # version bumped in the outgoing range

    shown = ", ".join(watched_hits[:5])
    more = f" (+{len(watched_hits) - 5} more)" if len(watched_hits) > 5 else ""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "🚫 PUSH BLOCKED: plugin.json version not bumped\n\n"
                f"Outgoing commits (vs {base}) change plugin content:\n"
                f"  {shown}{more}\n\n"
                "but .claude-plugin/plugin.json's version is unchanged.\n\n"
                "Per CLAUDE.md: always bump the version before the final push of\n"
                "any change touching skills/, agents/, commands/, hooks/,\n"
                "CLAUDE.md, or README.md — patch (x.y.Z) for fixes, minor (x.Y.0)\n"
                "for features/rewrites.\n\n"
                "Bump the version, commit, then retry the push."
            ),
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail-open: a hook bug must never block work
