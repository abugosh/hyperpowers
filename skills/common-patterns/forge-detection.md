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

if [ -z "$url" ]; then
  # Both lookups failed: there is no remote configured at all, so land on the
  # no-forge path directly (rung 3). Normal for local-only repos, including
  # scratch repos used in pressure testing — not an error condition. Short-
  # circuit here so we never reach the host probes below.
  forge=none
else
  # 2. Derive the host from the URL. git remote get-url returns a full URL,
  #    not a bare host, and it comes in three shapes:
  #      git@host:owner/repo.git        (scp-style SSH)
  #      ssh://git@host/owner/repo.git  (ssh:// URL)
  #      https://host/owner/repo.git    (HTTPS URL)
  #    Strip scheme, then user@, then everything from the first : or / .
  host="$url"
  host="${host#*://}"    # drop scheme:// if present (https://, ssh://)
  host="${host#*@}"      # drop user@ if present (git@, ssh user)
  host="${host%%[:/]*}"  # keep up to the first : or / — the bare host

  # 3. Dispatch on the host
  case "$host" in
    github.com) forge=gh ;;
    gitlab.com) forge=glab ;;
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
fi
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
   description, comments, review state — approvals, decision, resolved and
   open threads — and diff) via the Read commands below.
2. **CLI available, no MR/PR found for the branch** — fall back to commits +
   diff intent (`git log`, `git diff`); note explicitly that no MR/PR was
   found.
3. **No CLI, no auth, or no remote configured** — commits + diff intent
   only; any draft comment becomes copy-paste text for the user to post
   manually rather than an API call.

## Read commands

### GitLab (glab)

```bash
# Full REST MR object: description, title, iid, source_branch, target_branch,
# web_url, and author (the MR's own author — `author.username` on this forge)
glab mr view [<iid>|<branch>] -F json

# Open (unresolved) discussion threads
glab mr view <iid> --comments --unresolved

# Closing issues — a SEPARATE command, not present in `mr view` output
glab mr issues [<iid>|<branch>]

# Diff
glab mr diff [<iid>|<branch>] --raw
```

#### Review state (GitLab)

```bash
# Approvals (Free tier): who approved and when. NO SHA — approved_at is a
# timestamp only, not tied to a commit. `:id` expands to the current
# directory's project; `glab api` has no `--repo` flag, so reviewing another
# project requires the URL-encoded full path in place of `:id`.
glab api projects/:id/merge_requests/<iid>/approvals

# Discussion threads with resolution state: per-note `resolvable`, `resolved`,
# `resolved_by`, `resolved_at`, `author.username` (who wrote that note), and
# `position.new_path`/`new_line`. There is no discussion-level
# resolved flag — a thread counts as settled only when
# every resolvable note in it is resolved. Non-resolvable notes (plain MR
# comments, including a posted peek comment) ride in the same array with
# `resolvable: false`. --paginate walks all pages.
glab api projects/:id/merge_requests/<iid>/discussions --paginate
```

`glab mr view <iid> --comments` is the human-readable alternative (TTY marks
✓ resolved / ⚠ unresolved; add `-F json` for a `Discussions` array, gated to
glab >= v1.37.0; the `--resolved`/`--unresolved` filters are gated to glab >=
v1.88.0). `approval_state` and `glab mr approvers` are Premium/Ultimate-only
and silently omit their data on Free tier — do not use either as the primary
read.

### GitHub (gh)

```bash
# No-arg form resolves the current branch's PR. The trailing `author` field
# is the PR's own author — `author.login` on this forge.
gh pr view [<number>|<url>|<branch>] --json title,body,state,baseRefName,headRefName,closingIssuesReferences,files,commits,author

# Diff: file list, then the patch itself
gh pr diff [<target>] --name-only
gh pr diff [<target>]
```

#### Review state (GitHub)

```bash
# reviews[]: author.login, state (APPROVED/CHANGES_REQUESTED/COMMENTED/
# DISMISSED/PENDING — PENDING entries are unsubmitted, ignore them),
# submittedAt, commit.oid (the SHA the review was submitted against);
# auto-paginates past 100. latestReviews: one per reviewer, no commit.oid.
# reviewDecision: APPROVED/CHANGES_REQUESTED/REVIEW_REQUIRED, nullable.
# comments: conversation comments only (not inline review-thread comments);
# auto-paginated.
gh pr view [<number>|<url>|<branch>] --json reviews,latestReviews,reviewDecision,comments

# Thread resolution is GraphQL-only — REST carries no resolution field.
# The query declares $endCursor and selects reviewThreads(first: 100,
# after: $endCursor) with pageInfo { hasNextPage endCursor }, so --paginate
# is at least well-formed against this connection; whether --paginate walks
# a connection nested under pullRequest (rather than top-level) is
# unconfirmed (see C7). -F owner='{owner}' -F repo='{repo}' has gh
# substitute the placeholders from the current directory's repo.
gh api graphql --paginate -F owner='{owner}' -F repo='{repo}' -F number=<number> -f query='
  query($owner: String!, $repo: String!, $number: Int!, $endCursor: String) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        reviewThreads(first: 100, after: $endCursor) {
          nodes {
            isResolved
            isOutdated
            path
            line
            resolvedBy { login }
            comments(first: 100) {
              nodes { author { login } body path line createdAt }
            }
          }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
  }'
```

`reviews`/`reviewDecision`/`comments` require gh >= v1.9.0; `latestReviews`
requires gh >= v2.5.0. REST endpoints (`/pulls/{n}/reviews`,
`/pulls/{n}/comments`) carry no resolution field — thread resolution is
reachable only through the GraphQL query above.

`closingIssuesReferences` requires gh >= v2.72.0 (2025-05); on older gh the
field is absent from `--json` output.

### Author fields

An identity comparison — is this comment mine? did a reviewer speak after my
last reply? — needs two operands, and each forge names them differently. Both
come from reads already listed above; no extra call is needed.

| | The target's own author | The author of one comment/note |
|---|---|---|
| GitHub | `author.login`, from the `gh pr view --json ...,author` read | `author.login`, on `reviews[]` and on every `reviewThreads` comment node in the GraphQL query |
| GitLab | `author.username`, from `glab mr view -F json` | `author.username`, on every note from `discussions --paginate` |

Match on the login/username, never on the display `name` beside it — display
names are user-editable and need not be unique.

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

Doc-verified against official docs 2026-07-24 (C1-C5) and 2026-08-26 (C6-C9;
gh v2.98.0, glab v1.115.0); NOT runtime-verified (no `glab`/`gh` installed on
the authoring machine). Each line names what one live run would settle.

| ID | Caveat | Fallback |
|----|--------|----------|
| C1 | `glab mr view` with no argument resolving to the current branch's MR is documented for `mr diff`/`mr issues` but only implied, not confirmed, for `mr view` | Always pass the branch name explicitly instead of relying on no-arg resolution |
| C2 | Legacy `glab mr note -m` vs. the newer `note create` subcommand restructure — backward compat is promised in gitlab-org/cli#8051 but unconfirmed | Try the `note create` form first; on failure retry with the legacy `mr note` form |
| C3 | `glab auth status --hostname <host>` exit-code contract is undocumented | Treat any non-zero exit or error-shaped output as not-authenticated, not just exit code 1 |
| C4 | Exact element shape of `gh pr view`'s `closingIssuesReferences` array (expected: number/title/url) is unconfirmed | Consumers must not hard-code sub-fields beyond `number` and `title` without checking actual output first |
| C5 | `gh pr view --json` does not expose inline review-thread comments, only top-level issue comments | Read threads via the GraphQL reviewThreads query under Review state (GitHub); pr view --json comments stays top-level only |
| C6 | GitLab `/approvals` carries `approved_at` but no SHA — how well a last review point mapped from `approved_at` / `resolved_at` onto commit times survives rebase or force-push is unconfirmed | Consumers mark it "approximate (timestamp-mapped)"; when no current commit predates the newest approval, treat every change as delta and say so. Settled by: approve an MR, rebase and force-push it, re-read `/approvals` and compare `approved_at` against the rewritten commit times |
| C7 | Whether `gh api graphql --paginate` walks the `reviewThreads` connection nested under `pullRequest` (its documented support is for the query's paginated connection with `$endCursor`) is unconfirmed beyond 100 threads | Read the first 100 threads; when `pageInfo.hasNextPage` is true, name the gap in Coverage. Settled by: run the query with `--paginate` against a PR carrying more than 100 review threads and count the nodes returned |
| C8 | Whether `glab api` resolves `:id` from a subdirectory of the repo, and whether `glab mr view --comments` walks every discussion page, are unconfirmed | Run `glab api` from the repo root; read threads via `discussions --paginate`, never via `mr view --comments`. Settled by: from a subdirectory, run `glab api projects/:id` and `glab mr view <iid> --comments -F json` against an MR with more than 20 discussions and compare the count to `discussions --paginate` |
| C9 | `glab mr view --resolved` / `--unresolved` exist only on glab >= v1.88.0; their behavior (error vs silent ignore) on older glab is unconfirmed | Fold resolution per note from `discussions --paginate`; never rely on the filters. Settled by: run `glab mr view <iid> --resolved` on a glab older than v1.88.0 and record whether it errors or ignores the flag |

## Base branch

Use finishing-a-development-branch's base-branch idiom
(`skills/finishing-a-development-branch/SKILL.md`, Step 3): try
`git merge-base HEAD main`, then `git merge-base HEAD master`, then ask the
user. Do not restate the full logic here.
