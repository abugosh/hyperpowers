# Change History

Single source for reading git history as evidence of how a codebase actually
changes. Consumers: intuition (Pass 7, rate-of-change mismatch) and
fact-or-fiction (hotspot targeting). Both cite this file; neither restates it.

## History depth

The thresholds apply to the commits the count below keeps — N minus the
exclusions on its filtering line:

- Fewer than 10 kept commits: there is no change signal. Say so in the
  report and skip the analysis that needs it.
- Fewer than 100: count anyway and warn that the result may be unreliable
  (a shallow clone, a young repository, or a quiet window).

## Noise filtering

Exclude commits touching 50+ files (bulk renames, migrations), commits whose
message marks a bulk operation, commits that change only generated files,
and commits that change only dependency manifests. The command below applies
all four; it is the recipe, and this sentence describes it.

A file that changes by ritual rather than by design pressure — a version
field bumped every release, a tracker's export, a changelog — is not
evidence of how the design changes. Drop it from the counts.

Report the filtering in one line:
`Analyzed N commits (excluded M bulk, K generated-only, J manifest-only); dropped as ritual: <files, or none>`.

## Counting

The window is the last 6 months. One pass over the log applies the filters
and prints per-file change counts; it runs in well under a second on a
repository with hundreds of commits:

```bash
git log --since=6.months --no-merges --format='@%s' --name-only | awk '
function flush(   i, kept, f, src) {
  if (!have) return
  total++
  if (n >= 50) { bulk++; have=0; return }
  if (tolower(msg) ~ /^(rename|migrate|bulk|refactor all|chore: bump|update deps)/) { bulk++; have=0; return }
  kept=0; src=0
  for (i=1; i<=n; i++) {
    f=files[i]
    if (f ~ /\.lock$|\.generated\.|(^|\/)(dist|build|vendor|node_modules)\//) continue
    keep[++kept]=f
    if (f !~ /(^|\/)(package\.json|Cargo\.toml|go\.mod|go\.sum|requirements\.txt|pyproject\.toml|Gemfile)$/) src=1
  }
  if (kept == 0) { gen++; have=0; return }
  if (!src) { man++; have=0; return }
  for (i=1; i<=kept; i++) count[keep[i]]++
  have=0
}
/^@/ { flush(); msg=substr($0,2); n=0; have=1; next }
NF   { files[++n]=$0 }
END  { flush()
       printf "Analyzed %d commits (excluded %d bulk, %d generated-only, %d manifest-only)\n", total, bulk, gen, man > "/dev/stderr"
       for (f in count) print count[f], f }' | sort -rn
```

Group the per-file counts by whatever boundary the consumer reasons about:
modules for a rate-of-change comparison, files for a hotspot list.
