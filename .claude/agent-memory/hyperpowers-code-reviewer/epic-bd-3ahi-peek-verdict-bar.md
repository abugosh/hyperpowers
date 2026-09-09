---
name: epic-bd-3ahi-peek-verdict-bar
description: Epic bd-3ahi (peek verdict bar + forge approval) runs RED/GREEN pressure tests recorded in docs/ledgers/bd-3ahi-pressure-tests.md; GREEN was reduced by user decision to bikeshed x2 + 3 synthesis runs
metadata:
  type: project
---

Epic bd-3ahi gives peek's Important tier a positive bar and lands forge approvals. Its
tasks are graded against pressure-test fixtures whose method of record is the ledger
`docs/ledgers/bd-3ahi-pressure-tests.md` (FIXTURE SCRIPT, RED BASELINE, PRESSURE-TEST
CONTRACT + AMENDMENTS, SYNTHESIS FIXTURES, GREEN block), not the scratchpad.

Task 9 (bd-syo7) passed review 2026-09-09: every GREEN claim reproduced — scanner output
and sentence counts re-derived by re-running the recorded `scan.py`, blob shas and the
five fixture TREE shas re-derived, all quoted Verdict/Direction/`[downgraded:`/
`[lead-added:` strings matched the artefacts byte-for-byte, and all nine synthesis fixture
files still diff clean against the ledger's own record of them.

**Why:** the epic's whole claim is empirical — the prompt edits are hypotheses until the
fixtures return the graded shape — so a ledger claim that does not reproduce from the
artefacts is the failure mode, not prose quality.

**How to apply:** when reviewing a pressure-test task here, re-run the recorded scanner
and re-derive the shas yourself rather than trusting the ledger's pasted numbers; check
that runs used the blobs the header names (a run made before the last prompt commit must
be excluded, as `<sp>/green-cancelled/` was). GREEN scope was reduced by USER DECISION
2026-09-09 on cost: the four inherited fixtures (clean, bad-no-critical, silent-reshape,
missing-aim) were NOT re-run this epic and their rules stand unverified at these blobs —
the contract block's older run counts are stale by design, the ledger appends rather than
rewrites. Related: [[epic-bd-iaem-review-seam-reconciliation]].
