# Forge Detection

Single source for how hyperpowers skills detect and talk to a code forge
(GitLab via `glab`, GitHub via `gh`), and how they degrade when no forge is
reachable. Consumers cite this file and use the commands as given — never
restate or reinvent them locally.

## Purpose

Any skill that needs MR/PR metadata or wants to post a comment (e.g. peek)
does host detection once, using the idiom below, then follows the
degradation ladder to decide what's actually available. This keeps forge
commands in one place so they don't drift between skills.

## Detection

```bash
# 1. Get the remote URL — prefer upstream, fall back to origin
url="$(git remote get-url upstream 2>/dev/null || git remote get-url origin 2>/dev/null)"

# If both lookups fail there is no remote configured at all -> no-forge
# path directly (rung 3). This is normal for local-only repos, including
# scratch repos used in pressure testing — not an error condition.
if [ -z "$url" ]; then
  : # no remote configured; no-forge path
fi

# 2. Extract host from the URL and dispatch
case "$url" in
  *github.com*) forge=gh ;;
  *gitlab.com*) forge=glab ;;
  *)
    # Self-hosted: probe auth directly, don't guess from the hostname string.
    # Self-hosted GitLab URLs rarely contain the word "gitlab".
    if glab auth status --hostname "$host" >/dev/null 2>&1; then
      forge=glab
    elif gh auth status --hostname "$host" >/dev/null 2>&1; then
      forge=gh
    else
      forge=none  # no-forge path; ask the user only if they claim an MR exists
    fi
    ;;
esac
```

Do NOT probe with `glab repo view` / `gh repo view` — those make network
calls and conflate "wrong forge" with "not authenticated," which is exactly
the ambiguity the auth-status probe avoids. The auth probe only works for
hosts the user has already run `glab auth login --hostname <host>` against
(upstream limitation: gitlab-org/cli#8010) — a self-hosted host the user has
never authenticated against looks identical to "no forge available."

## Degradation ladder

Consumers must state which rung they ran at — never silently downgrade.

1. **Forge CLI available + MR/PR exists** — full metadata (title,
   description, comments, diff) via the Read commands below.
2. **CLI available, no MR/PR found for the branch** — fall back to commits +
   diff intent (`git log`, `git diff`); note explicitly that no MR/PR was
   found.
3. **No CLI, no auth, or no remote configured** — commits + diff intent
   only; any draft comment becomes copy-paste text for the user to post
   manually rather than an API call.

## Read commands

### GitLab (glab)

```bash
# Full REST MR object: description, title, iid, source_branch, target_branch, web_url
glab mr view [<iid>|<branch>] -F json

# Open (unresolved) discussion threads
glab mr view <iid> --comments --unresolved

# Closing issues — a SEPARATE command, not present in `mr view` output
glab mr issues [<iid>|<branch>]

# Diff
glab mr diff [<iid>|<branch>] --raw
```

### GitHub (gh)

```bash
# No-arg form resolves the current branch's PR
gh pr view [<number>|<url>|<branch>] --json title,body,state,baseRefName,headRefName,closingIssuesReferences,files,commits

# Diff: file list, then the patch itself
gh pr diff [<target>] --name-only
gh pr diff [<target>]
```

`closingIssuesReferences` requires gh >= v2.72.0 (2025-05); on older gh the
field is absent from `--json` output.

## Write commands

Used only after explicit user approval — the approval gate belongs to the
consumer skill, not to this file.

```bash
# GitLab: --unique makes repeated calls idempotent
glab mr note create <iid|branch> -m "<text>" --unique
# Fallback for older glab without the `note create` subcommand:
glab mr note <iid> -m "<text>"

# GitHub: idempotent update via --edit-last, falling back to a new comment
gh pr comment <target> --body "<text>" --edit-last --create-if-none
```

## Unverified caveats

Doc-verified against official docs 2026-07-24; NOT runtime-verified (no
`glab`/`gh` installed on the authoring machine). Each line names what one
live run would settle.

| ID | Caveat | Fallback |
|----|--------|----------|
| C1 | `glab mr view` with no argument resolving to the current branch's MR is documented for `mr diff`/`mr issues` but only implied, not confirmed, for `mr view` | Always pass the branch name explicitly instead of relying on no-arg resolution |
| C2 | Legacy `glab mr note -m` vs. the newer `note create` subcommand restructure — backward compat is promised in gitlab-org/cli#8051 but unconfirmed | Try the `note create` form first; on failure retry with the legacy `mr note` form |
| C3 | `glab auth status --hostname <host>` exit-code contract is undocumented | Treat any non-zero exit or error-shaped output as not-authenticated, not just exit code 1 |
| C4 | Exact element shape of `gh pr view`'s `closingIssuesReferences` array (expected: number/title/url) is unconfirmed | Consumers must not hard-code sub-fields beyond `number` and `title` without checking actual output first |
| C5 | `gh pr view --json` does not expose inline review-thread comments, only top-level issue comments | v1 consumers use top-level comments only; treat inline threads as out of reach |

## Base branch

Use finishing-a-development-branch's base-branch idiom
(`skills/finishing-a-development-branch/SKILL.md`, Step 3): try
`git merge-base HEAD main`, then `git merge-base HEAD master`, then ask the
user. Do not restate the full logic here.
