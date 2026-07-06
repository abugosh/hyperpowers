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
import shlex
import subprocess
import sys

WATCHED = ("skills/", "agents/", "commands/", "hooks/", "CLAUDE.md", "README.md")
PLUGIN_MANIFEST = os.path.join(".claude-plugin", "plugin.json")

# git global options that consume the following token
GIT_OPTS_WITH_ARG = ("-C", "-c", "--git-dir", "--work-tree", "--exec-path", "--namespace")


def run_git(args, cwd):
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def parse_push_invocations(command):
    """Return a list of positional-arg lists, one per actual `git ... push`
    invocation in the command. Substring mentions of "push" (echoed text,
    commit messages, grep patterns) never match: each shell segment is
    shlex-tokenized and `push` must be git's subcommand token.

    Returns [] when no real push invocation exists. Raises on untokenizable
    input (caller fails open)."""
    invocations = []
    for segment in re.split(r"(?:&&|\|\||[;|&\n])", command):
        segment = segment.strip()
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            continue  # unparseable segment: fail open for this segment
        # skip leading env assignments (VAR=value git push ...)
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens = tokens[1:]
        if not tokens or os.path.basename(tokens[0]) != "git":
            continue
        rest = tokens[1:]
        # consume git global options to find the subcommand
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok in GIT_OPTS_WITH_ARG:
                i += 2
                continue
            if tok.startswith("-"):
                i += 1
                continue
            break
        if i >= len(rest) or rest[i] != "push":
            continue
        invocations.append(rest[i + 1:])
    return invocations


def push_targets_default_branch(push_args, current_branch):
    """True when this push touches main/master: explicit refspec destinations
    are checked by literal equality; without refspecs the current branch is
    what gets pushed."""
    positionals = [t for t in push_args if not t.startswith("-")]
    refspecs = positionals[1:]  # first positional is the remote
    if not refspecs:
        return current_branch in ("main", "master")
    for spec in refspecs:
        dest = spec.split(":", 1)[1] if ":" in spec else spec
        dest = dest.strip("+")
        if dest.startswith("refs/heads/"):
            dest = dest[len("refs/heads/"):]
        if dest == "HEAD":
            dest = current_branch
        if dest in ("main", "master"):
            return True
    return False


def main():
    input_data = json.load(sys.stdin)

    if input_data.get("tool_name", "") != "Bash":
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")
    if "git" not in command or "push" not in command:
        sys.exit(0)  # cheap pre-filter only; real detection is structural

    push_invocations = parse_push_invocations(command)
    if not push_invocations:
        sys.exit(0)
    if any("--dry-run" in args for args in push_invocations):
        sys.exit(0)

    cwd = input_data.get("cwd") or os.getcwd()

    repo_root = run_git(["rev-parse", "--show-toplevel"], cwd)
    if not repo_root:
        sys.exit(0)

    # Scope guard: only plugin repos.
    if not os.path.isfile(os.path.join(repo_root, PLUGIN_MANIFEST)):
        sys.exit(0)

    # Only guard pushes that touch the default branch — the version-bump rule
    # targets the final push. Mid-epic feature-branch pushes stay free
    # (false-deny bias). Branch and refspec checks are literal equality on
    # parsed tokens, never substring scans.
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root) or ""
    if not any(
        push_targets_default_branch(args, branch) for args in push_invocations
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
