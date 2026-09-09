# bd-zk46 pressure-test ledger (moved from the epic's bd notes)

Epic bd-zk46 — Peek grades the system (v3.37.0). These blocks were appended to the epic's bd notes during execution on 2026-09-03 and moved here verbatim, in their original order, on 2026-09-04 at finish-branch: with them the epic's line in `.beads/issues.jsonl` was 144,143 bytes, and `bd import` rejects any line over 64KB (`bufio.Scanner: token too long`). The governance blocks (gate-states, lead decisions, SRE verdict, suggestions, the completion marker) remain in the epic's notes with a `LEDGER MOVED` pointer to this file. Fixture repos and transcripts themselves lived in the session scratchpad and were never committed; the fixture script below rebuilds the repos.

---

RED BASELINE (2026-09-03, agents/peek.md @ commit 3251dfa3d766d1d1cf37bca8562b77a619186656 / blob 25f248684472c06de4aa112bea7943106331ab68, skills/peek/SKILL.md @ commit 47645886530b4921b81a553b44beed0f4dfb4a49 / blob fd6e115091ae930768676c4c7802ff5dd5f4826b, repo HEAD 0898f47; fixture tips clean=cf923338253d9a0e8da9bafc50eb8c502fc713b0 bad=f450b76025e1b4023ac8684cd6c9439f482853bd reshape=d807eaf477aef94c8226287cbdc80cbbac69e1e3 missing=80b1c74f50f028f3d34c7fb819ed553bb2635c94; branch TREE shas — the stable anchor, since the idempotent script recreates commits — clean=d1c90ac287781d3834f13042fe733ade63c614f7 bad=9855ad3c050e53b1ac09bf0c128c7a3f5ee96661 reshape=8b97be00b8597600dd37c9e5446baef1c6e48d69 missing=d1c90ac287781d3834f13042fe733ade63c614f7; RECON sonnet, lenses+synthesis opus; every dispatch subagent_type general-purpose, never hyperpowers:peek):
- METHOD (task 10 must replicate this exactly or the GREEN comparison is invalid): the agent body was delivered BY FILE, not typed into the dispatch prompt. `sed -n '7,$p' agents/peek.md > <scratchpad>/peek-grades/agent-body.md` (everything after the frontmatter's closing `---`), and each dispatch prompt's Step 0 read that file in full and named it the agent's operating prompt. Reason: 16 verbatim retypings of a 265-line body is the transcription-drift risk that "verbatim" exists to prevent; a byte-exact extraction from the repo file has zero drift and still never touches the plugin cache. Synthesis was delivered the same way: `sed -n '114,159p' skills/peek/SKILL.md > step6.md`, concatenated with the RECON + three lens returns into `<scratchpad>/peek-grades/synth-input/<fixture>-SYNTH-INPUT.md`. Synthesis was given RECON's return too, not only the three lens returns — Step 6's template requires RECON's Change Inventory and review-history line to open the report. Every dispatch carried "There is no user present. Do not pause for confirmation or ask questions"; no dispatch paused, so no SendMessage resume was needed. Agents wrote their own returns to red/ (outside the reviewed repo and worktree, so Shared Rule 4 holds) and replied with only the path and counts.
- clean: Verdict APPROVE — grading words: [clean x1 — "This is a clean, narrow addition and it should merge", Overall Assessment] observed: [right — "which points the right way"; honest — "The honest limits are worth stating alongside that approval"] — sentences: WTBD=5 AvA=3 OA=12 — findings C/I/S=0/0/1 — stance: fits — aims table: 3 of 3 achieved — the one Suggestion is `[convention]`, test-support structure, explicitly "No change required on this branch"; the pass rule for this fixture cannot be "(none) or Suggestion-only", because RED already returns exactly that (the bd-v5q5 trap, repeated here).
- bad-no-critical: Verdict REQUEST CHANGES — grading words: [(none)] observed: [right — "Its shape is right"; declines — "What it declines is the sourcing"; slip — "not an isolated slip"] — sentences: WTBD=5 AvA=5 OA=7 — findings C/I/S=1/5/4 — stance: fights — aims table: aim1 charge-idempotency MISSING, aim2 refund achieved (untested), aim3 retry achieved (untested) — partial-aim finding: CRITICAL (F1, `[capability]`, Trigger "any repeat of charge() for one logical payment", Consequence "customer debited twice") — shared cause named in OA: YES, and named well — "the fight and the defect share a root", "the headline defect is not an isolated slip but the predictable shape of a client that owns a concern it should be borrowing" — the `Path: rework` scenario landed, but the delivery-class miss was rated production-class Critical on a trigger that exists nowhere in the repo (charge() is never retried; the named trigger is a hypothetical caller).
- silent-reshape: Verdict APPROVE WITH CHANGES — stance: reshapes — reshape as finding: IMPORTANT (twice — "relocates retry ownership out of PaymentClient" at payments/client.py:1,15, and "generic HTTP transport now takes a hard dependency on the payments domain package, inverting the layer order" at http/session.py:10) — grading words: [(none)] observed: [reasonable — "a reasonable thing to want"; right/defensible — "The decision itself may well be right — a single retry policy at the transport is a defensible design. What is not defensible is arriving at it through a commit that says..."] — sentences: WTBD=5 AvA=4 OA=11 — findings C/I/S=0/6/2 — aims table: 1 of 1 achieved, and DELIVERY marked it "Delivered indirectly: no line inside refund changed" — the undeclared service-wide policy move produced only Importants, so six Importants over one undeclared decision derive APPROVE WITH CHANGES; the OA says so itself ("The count of individually-Important findings understates the situation, because all six trace to one decision taken without being declared") and the verdict still cannot express it.
- missing-aim: Verdict REQUEST CHANGES — aims table: aim1 refund achieved, aim2 cancel MISSING — missing-aim finding: IMPORTANT (Finding 2, `[capability]`, explicitly "Not Critical: no caller of cancel exists anywhere in the repo, so no reachable trigger or consequence can be named") — grading words: [(none)] observed: [good case — "Structurally this is the good case"] — sentences: WTBD=10 AvA=5 OA=12 — findings C/I/S=1/1/1 — stance: fits — the Critical is NOT the missing aim; it is a production-class Critical on refund's idempotency key, on code byte-identical to the clean fixture's.
- HEADLINE INSTABILITY (the strongest RED datum, and the reason the two fixtures were built to share a tree): clean and missing-aim have IDENTICAL branch trees (both d1c90ac287781d3834f13042fe733ade63c614f7) — the only difference between the two targets is the commit message, i.e. the stated aims. Same prompts, same lens, same model (opus). CODE on clean returned `- (none)` and routed the idempotency-key concern to Questions for the Author, reasoning "no caller exists in the repo to prove the trigger is reachable". CODE on missing-aim rated the same line Critical, naming a caller-side retry as the Trigger and "the merchant pays the customer twice" as the Consequence. Verdicts diverged accordingly: APPROVE vs REQUEST CHANGES on byte-identical code. Whatever the fix, it must make the severity of a finding a function of the code, not of the aims the branch happens to declare.
- SECOND OBSERVATION: the delivery/production severity boundary is being crossed in both directions and inconsistently. bad-no-critical's missing aim got Critical on a hypothetical caller; missing-aim's missing aim got Important with an explicit "no reachable trigger" argument; missing-aim's CODE lens then used the hypothetical-caller argument the same report had just refused. All three sit in one baseline.
- THIRD OBSERVATION: no report used a `Path:` or `Decision:` line; each Overall Assessment ends in prose that mixes the system consequence with a recommendation ("it should merge", "The fix is either to narrow the diff back to the aim, or to restate the aim", "close the gap before merge in one of two directions"). The recommendation is present but never in a fixed slot a reader can find.
- FOURTH OBSERVATION: only ONE closed-list grading word fired across four reports (clean x1). The open-ended scan found more (right, declines, slip, reasonable, defensible, good case). A prose rule stated as a word blacklist would have scored this baseline near-perfect; a rule stated categorically would not.
- verbatim top layers and full returns (4 fixtures x RECON/CODE/ARCHITECTURE/DELIVERY/REPORT = 20 files): /private/tmp/claude-501/-Users-abugosh-g-hyperpowers/f271442f-9b95-4df3-af96-cc00928b389d/scratchpad/peek-grades/red/
- synthesis inputs (step6.md + RECON + 3 lens returns, concatenated verbatim): .../peek-grades/synth-input/ ; grading-word scanner: .../peek-grades/scan.py
- PRE-FIX RUN (superseded, kept as the evidence that justified one fixture change): .../peek-grades/prefix-run/ holds a complete earlier RECON+3-lens pass over an earlier build of the same four scenarios. In that build clean's and missing-aim's refund key was DERIVED from its own contents ("refund-%s-%s" % (charge_id, amount)). CODE on missing-aim rated it Critical for colliding across two equal partial refunds — a real, reachable, money-impacting defect I had introduced. Per the production-safety rule, the fixture was changed (per-call uuid4 key, plus tests pinning distinct-keys-per-call) and everything was re-run; the scenario shapes were untouched. The replacement then drew a Critical for the OPPOSITE reason (a per-call key means a caller's retry pays twice). Both readings are true of their code and neither is reachable in-repo, since these fixtures contain no caller of PaymentClient at all. That is why the fixture was not iterated a third time: the variance is in the lens, not the code, and chasing it would only move which argument the Critical uses. The earlier pass is also independent confirmation of the headline instability — clean's CODE returned 0 findings on that build too, on the same tree missing-aim's CODE called Critical.

FIXTURE SCRIPT (bd-zk46 task 1): full contents of <scratchpad>/peek-grades/fixtures.sh, fenced below. Idempotent (rm -rf then rebuild; exits 0 on a second run) and content-deterministic — it recreates commits with new SHAs but reproduces the branch TREE shas recorded in the RED BASELINE block above, which is what the RED->GREEN comparison rests on. It builds four git repos under <scratchpad>/peek-grades/repos/ and their detached worktrees under <scratchpad>/peek-grades/wt/, each a tiny Python/unittest project with a main branch and one feature branch and NO remote, so peek runs at degradation rung 3 and the commit messages ARE the stated aims.
```bash
#!/usr/bin/env bash
# Pressure-test fixture builder for epic bd-zk46 (peek grades the system).
# Four tiny Python/unittest repos, each with a main branch and one feature
# branch, no remote (peek runs at degradation rung 3, so the commit messages
# ARE the stated aims). None of the four branches contains a production-class
# defect: any Critical that appears must come from the delivery or structural
# class.
#
# Idempotent: wipes and rebuilds repos/ and wt/ on every run.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS="$ROOT/repos"
WT="$ROOT/wt"

rm -rf "$REPOS" "$WT"
mkdir -p "$REPOS" "$WT"

init_repo() {
  local dir="$1"
  mkdir -p "$dir"
  git init -q -b main "$dir"
  git -C "$dir" config user.name "Fixture Bot"
  git -C "$dir" config user.email "fixture-bot@example.invalid"
  git -C "$dir" config commit.gpgsign false
}

commit_all() {
  local dir="$1"; shift
  git -C "$dir" add -A
  git -C "$dir" commit -q "$@"
}

# =====================================================================
# helpers shared by more than one fixture
# =====================================================================
write_utils_retry() {
  local dir="$1"
  mkdir -p "$dir/utils"
  : > "$dir/utils/__init__.py"
  cat > "$dir/utils/retry.py" <<'PY'
"""Shared retry helper. Every caller that retries a call uses this."""


class TransientError(Exception):
    """Raised by a transport when a call may safely be tried again."""


def with_retry(fn, attempts):
    """Call fn(), retrying TransientError up to `attempts` times.

    Raises ValueError when `attempts` is less than 1, so the loop below
    always runs at least once and `last_error` is always set before the
    final raise.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    last_error = None
    for _ in range(attempts):
        try:
            return fn()
        except TransientError as error:
            last_error = error
    raise last_error
PY
}

write_utils_idempotency() {
  local dir="$1"
  mkdir -p "$dir/utils"
  : > "$dir/utils/__init__.py"
  cat > "$dir/utils/idempotency.py" <<'PY'
"""Idempotency key generation. Every money-moving payload carries one."""

import uuid


def new_key():
    """Return a fresh idempotency key.

    Callers build the payload once and reuse it across retries, so the key
    is stable for a single logical operation.
    """
    return "idem_" + uuid.uuid4().hex
PY
}

# =====================================================================
# FIXTURE 1: clean
#   Branch adds refund() with input validation and honest tests.
#   Commit message matches the code exactly.
# =====================================================================
build_clean_main() {
  local dir="$1"
  init_repo "$dir"
  mkdir -p "$dir/payments" "$dir/tests"
  : > "$dir/payments/__init__.py"
  : > "$dir/tests/__init__.py"
  cat > "$dir/payments/client.py" <<'PY'
"""Payments client. Wraps the payment provider's HTTP API."""

import uuid


def _new_idempotency_key():
    """Return a fresh idempotency key.

    One logical operation gets one key. A caller that retries a single
    operation reuses the payload it already built, so the key is stable
    across attempts of the same operation and distinct between operations.
    """
    return "idem_" + uuid.uuid4().hex


class PaymentClient:
    def __init__(self, transport):
        self._transport = transport

    def _post(self, path, payload):
        """POST `payload` to `path` and return the decoded response body.

        The transport raises on any non-2xx response and otherwise returns
        the decoded JSON body, which carries `id` for every created resource.
        """
        return self._transport.post(path, payload)

    def charge(self, amount):
        """Charge `amount` and return the created charge."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        payload = {
            "amount": amount,
            "idempotency_key": _new_idempotency_key(),
        }
        response = self._post("/charges", payload)
        return {"charge_id": response["id"], "amount": amount}
PY
  cat > "$dir/tests/test_client.py" <<'PY'
import unittest

from payments.client import PaymentClient


class RecordingTransport:
    """Hand-written stub: records calls, returns a fixed response."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, path, payload):
        self.calls.append((path, payload))
        return self.response


class ChargeTest(unittest.TestCase):
    def test_charge_returns_charge_id_and_amount(self):
        client = PaymentClient(RecordingTransport({"id": "ch_1"}))
        self.assertEqual(client.charge(10), {"charge_id": "ch_1", "amount": 10})

    def test_charge_posts_path_amount_and_a_key(self):
        transport = RecordingTransport({"id": "ch_1"})
        PaymentClient(transport).charge(10)
        self.assertEqual(len(transport.calls), 1)
        path, payload = transport.calls[0]
        self.assertEqual(path, "/charges")
        self.assertEqual(payload["amount"], 10)
        self.assertTrue(payload["idempotency_key"].startswith("idem_"))

    def test_two_charges_get_distinct_keys(self):
        transport = RecordingTransport({"id": "ch_1"})
        client = PaymentClient(transport)
        client.charge(10)
        client.charge(10)
        self.assertNotEqual(
            transport.calls[0][1]["idempotency_key"],
            transport.calls[1][1]["idempotency_key"],
        )

    def test_charge_rejects_zero(self):
        client = PaymentClient(RecordingTransport({"id": "ch_1"}))
        with self.assertRaises(ValueError):
            client.charge(0)

    def test_charge_rejects_negative(self):
        client = PaymentClient(RecordingTransport({"id": "ch_1"}))
        with self.assertRaises(ValueError):
            client.charge(-5)


if __name__ == "__main__":
    unittest.main()
PY
  commit_all "$dir" -m "Initial payments client with charge()"
}

write_clean_refund() {
  local dir="$1"
  cat >> "$dir/payments/client.py" <<'PY'

    def refund(self, charge_id, amount):
        """Refund `amount` against `charge_id` and return the refund."""
        if not charge_id:
            raise ValueError("charge_id is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        payload = {
            "charge_id": charge_id,
            "amount": amount,
            "idempotency_key": _new_idempotency_key(),
        }
        response = self._post("/refunds", payload)
        return {
            "refund_id": response["id"],
            "charge_id": charge_id,
            "amount": amount,
        }
PY
  cat > "$dir/tests/test_refund.py" <<'PY'
import unittest

from payments.client import PaymentClient
from tests.test_client import RecordingTransport


class RefundTest(unittest.TestCase):
    def test_refund_returns_refund_id_charge_id_and_amount(self):
        client = PaymentClient(RecordingTransport({"id": "rf_1"}))
        self.assertEqual(
            client.refund("ch_1", 4),
            {"refund_id": "rf_1", "charge_id": "ch_1", "amount": 4},
        )

    def test_refund_posts_path_charge_id_amount_and_a_key(self):
        transport = RecordingTransport({"id": "rf_1"})
        PaymentClient(transport).refund("ch_1", 4)
        self.assertEqual(len(transport.calls), 1)
        path, payload = transport.calls[0]
        self.assertEqual(path, "/refunds")
        self.assertEqual(payload["charge_id"], "ch_1")
        self.assertEqual(payload["amount"], 4)
        self.assertTrue(payload["idempotency_key"].startswith("idem_"))

    def test_two_equal_refunds_of_one_charge_get_distinct_keys(self):
        transport = RecordingTransport({"id": "rf_1"})
        client = PaymentClient(transport)
        client.refund("ch_1", 4)
        client.refund("ch_1", 4)
        self.assertNotEqual(
            transport.calls[0][1]["idempotency_key"],
            transport.calls[1][1]["idempotency_key"],
        )

    def test_refund_rejects_empty_charge_id(self):
        client = PaymentClient(RecordingTransport({"id": "rf_1"}))
        with self.assertRaises(ValueError):
            client.refund("", 4)

    def test_refund_rejects_zero_amount(self):
        client = PaymentClient(RecordingTransport({"id": "rf_1"}))
        with self.assertRaises(ValueError):
            client.refund("ch_1", 0)


if __name__ == "__main__":
    unittest.main()
PY
}

CLEAN="$REPOS/clean"
build_clean_main "$CLEAN"
git -C "$CLEAN" checkout -q -b feature/refund
write_clean_refund "$CLEAN"
commit_all "$CLEAN" -m "Add refund() to payments client" \
  -m "refund(charge_id, amount) validates its inputs and posts a refund carrying an idempotency key. Covered by tests for the happy path and both rejection paths."
git -C "$CLEAN" worktree add -q --detach "$WT/clean" feature/refund

# =====================================================================
# FIXTURE 2: bad-no-critical
#   Three aims. refund() delivered; idempotency-for-charge() partial (key
#   made but never sent); retry delivered by a private loop that duplicates
#   utils/retry.py. Two of the three findings share one cause: local
#   re-implementations of utils/ helpers. Tests are tautological. One
#   camelCase local in an otherwise snake_case file.
#   No production consequence: the refund payload carries its key BEFORE
#   the retry loop, and charge() is never retried.
# =====================================================================
BAD="$REPOS/bad-no-critical"
init_repo "$BAD"
write_utils_retry "$BAD"
write_utils_idempotency "$BAD"
mkdir -p "$BAD/payments" "$BAD/tests"
: > "$BAD/payments/__init__.py"
: > "$BAD/tests/__init__.py"
cat > "$BAD/payments/client.py" <<'PY'
"""Payments client. Wraps the payment provider's HTTP API."""


class PaymentClient:
    def __init__(self, transport):
        self._transport = transport

    def _post(self, path, payload):
        """POST `payload` to `path` and return the decoded response body.

        The transport raises on any non-2xx response and otherwise returns
        the decoded JSON body, which carries `id` for every created resource.
        """
        return self._transport.post(path, payload)

    def charge(self, amount):
        """Charge `amount` and return the created charge."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        response = self._post("/charges", {"amount": amount})
        return {"charge_id": response["id"], "amount": amount}
PY
cat > "$BAD/tests/test_client.py" <<'PY'
import unittest
from unittest.mock import Mock

from payments.client import PaymentClient


class ChargeTest(unittest.TestCase):
    def test_charge_returns_charge_id(self):
        transport = Mock()
        transport.post.return_value = {"id": "ch_1"}
        result = PaymentClient(transport).charge(10)
        self.assertEqual(result["charge_id"], transport.post.return_value["id"])


if __name__ == "__main__":
    unittest.main()
PY
commit_all "$BAD" -m "Initial payments client with charge()"

git -C "$BAD" checkout -q -b feature/refund-idempotency

# --- commit 1: refund(), using the shared idempotency helper -----------
cat > "$BAD/payments/client.py" <<'PY'
"""Payments client. Wraps the payment provider's HTTP API."""

from utils.idempotency import new_key


class PaymentClient:
    def __init__(self, transport):
        self._transport = transport

    def _post(self, path, payload):
        """POST `payload` to `path` and return the decoded response body.

        The transport raises on any non-2xx response and otherwise returns
        the decoded JSON body, which carries `id` for every created resource.
        """
        return self._transport.post(path, payload)

    def charge(self, amount):
        """Charge `amount` and return the created charge."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        response = self._post("/charges", {"amount": amount})
        return {"charge_id": response["id"], "amount": amount}

    def refund(self, charge_id, amount):
        """Refund `amount` against `charge_id` and return the refund."""
        if not charge_id:
            raise ValueError("charge_id is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        refundAmt = round(amount, 2)
        payload = {
            "charge_id": charge_id,
            "amount": refundAmt,
            "idempotency_key": new_key(),
        }
        response = self._post("/refunds", payload)
        return {"refund_id": response["id"], "amount": refundAmt}
PY
cat > "$BAD/tests/test_refund.py" <<'PY'
import unittest
from unittest.mock import Mock

from payments.client import PaymentClient


class RefundTest(unittest.TestCase):
    def test_refund_returns_refund_id(self):
        transport = Mock()
        transport.post.return_value = {"id": "rf_1"}
        result = PaymentClient(transport).refund("ch_1", 4)
        self.assertEqual(result["refund_id"], transport.post.return_value["id"])


if __name__ == "__main__":
    unittest.main()
PY
commit_all "$BAD" -m "Add refund() to payments client" \
  -m "refund(charge_id, amount) validates its inputs and posts a refund whose payload carries an idempotency key."

# --- commit 2: idempotency for charge(), key made but never sent -------
cat > "$BAD/payments/client.py" <<'PY'
"""Payments client. Wraps the payment provider's HTTP API."""

import uuid

from utils.idempotency import new_key


class PaymentClient:
    def __init__(self, transport):
        self._transport = transport

    def _post(self, path, payload):
        """POST `payload` to `path` and return the decoded response body.

        The transport raises on any non-2xx response and otherwise returns
        the decoded JSON body, which carries `id` for every created resource.
        """
        return self._transport.post(path, payload)

    def _make_key(self):
        return "idem_" + uuid.uuid4().hex

    def charge(self, amount):
        """Charge `amount` and return the created charge."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        key = self._make_key()
        response = self._post("/charges", {"amount": amount})
        return {"charge_id": response["id"], "amount": amount}

    def refund(self, charge_id, amount):
        """Refund `amount` against `charge_id` and return the refund."""
        if not charge_id:
            raise ValueError("charge_id is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        refundAmt = round(amount, 2)
        payload = {
            "charge_id": charge_id,
            "amount": refundAmt,
            "idempotency_key": new_key(),
        }
        response = self._post("/refunds", payload)
        return {"refund_id": response["id"], "amount": refundAmt}
PY
commit_all "$BAD" -m "Add idempotency key to charge()" \
  -m "charge() now generates an idempotency key so a repeated call cannot create a second charge."

# --- commit 3: retry for refund(), via a private parallel loop ---------
cat > "$BAD/payments/client.py" <<'PY'
"""Payments client. Wraps the payment provider's HTTP API."""

import uuid

from utils.idempotency import new_key
from utils.retry import TransientError


class PaymentClient:
    def __init__(self, transport):
        self._transport = transport

    def _post(self, path, payload):
        """POST `payload` to `path` and return the decoded response body.

        The transport raises on any non-2xx response and otherwise returns
        the decoded JSON body, which carries `id` for every created resource.
        """
        return self._transport.post(path, payload)

    def _make_key(self):
        return "idem_" + uuid.uuid4().hex

    def _retry_loop(self, fn):
        last_error = None
        for _ in range(3):
            try:
                return fn()
            except TransientError as error:
                last_error = error
        raise last_error

    def charge(self, amount):
        """Charge `amount` and return the created charge."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        key = self._make_key()
        response = self._post("/charges", {"amount": amount})
        return {"charge_id": response["id"], "amount": amount}

    def refund(self, charge_id, amount):
        """Refund `amount` against `charge_id` and return the refund."""
        if not charge_id:
            raise ValueError("charge_id is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        refundAmt = round(amount, 2)
        payload = {
            "charge_id": charge_id,
            "amount": refundAmt,
            "idempotency_key": new_key(),
        }
        response = self._retry_loop(lambda: self._post("/refunds", payload))
        return {"refund_id": response["id"], "amount": refundAmt}
PY
commit_all "$BAD" -m "Add retry to refund()" \
  -m "A transient failure on the refund call is retried instead of surfacing to the caller. The payload, including its idempotency key, is built once and reused across attempts."
git -C "$BAD" worktree add -q --detach "$WT/bad-no-critical" feature/refund-idempotency

# =====================================================================
# FIXTURE 3: silent-reshape
#   Aim as stated: add retry to the payment client's refund path.
#   Code: retry policy moves OUT of payments/client.py INTO the generic
#   http/session.py, which now imports payments/constants.py. Every Session
#   caller inherits payment-specific retry. No commit message mentions it.
#   No production consequence: the second caller is read-only, and every
#   payments payload carries an idempotency key built before the retry.
# =====================================================================
RESHAPE="$REPOS/silent-reshape"
init_repo "$RESHAPE"
write_utils_retry "$RESHAPE"
write_utils_idempotency "$RESHAPE"
mkdir -p "$RESHAPE/payments" "$RESHAPE/http" "$RESHAPE/reports" "$RESHAPE/tests"
: > "$RESHAPE/payments/__init__.py"
: > "$RESHAPE/http/__init__.py"
: > "$RESHAPE/reports/__init__.py"
: > "$RESHAPE/tests/__init__.py"
cat > "$RESHAPE/payments/constants.py" <<'PY'
"""Tuning constants specific to the payments edge."""

# The provider's refund/charge endpoints are slow to settle, so payments
# retries more aggressively than anything else in this service.
PAYMENT_RETRY_ATTEMPTS = 4
PY
cat > "$RESHAPE/http/session.py" <<'PY'
"""Generic HTTP session wrapper.

Knows nothing about any particular API. Callers layer their own policy
(retries, backoff, auth scopes) on top of these two calls.

The transport raises on any non-2xx response and otherwise returns the
decoded JSON body, which carries `id` for every created resource.
"""


class Session:
    def __init__(self, transport):
        self._transport = transport

    def get(self, path):
        return self._transport.get(path)

    def post(self, path, payload):
        return self._transport.post(path, payload)
PY
cat > "$RESHAPE/payments/client.py" <<'PY'
"""Payments client. Owns the retry policy for the payments edge."""

from payments.constants import PAYMENT_RETRY_ATTEMPTS
from utils.idempotency import new_key
from utils.retry import with_retry


class PaymentClient:
    def __init__(self, session):
        self._session = session

    def charge(self, amount):
        """Charge `amount` and return the created charge."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        payload = {"amount": amount, "idempotency_key": new_key()}
        response = with_retry(
            lambda: self._session.post("/charges", payload),
            PAYMENT_RETRY_ATTEMPTS,
        )
        return {"charge_id": response["id"], "amount": amount}

    def refund(self, charge_id, amount):
        """Refund `amount` against `charge_id` and return the refund."""
        if not charge_id:
            raise ValueError("charge_id is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        payload = {
            "charge_id": charge_id,
            "amount": amount,
            "idempotency_key": new_key(),
        }
        response = self._session.post("/refunds", payload)
        return {"refund_id": response["id"], "amount": amount}
PY
cat > "$RESHAPE/reports/fetch.py" <<'PY'
"""Daily report fetching. A second Session caller; read-only."""


class ReportFetcher:
    def __init__(self, session):
        self._session = session

    def daily_totals(self, day):
        return self._session.get("/reports/daily/%s" % day)
PY
cat > "$RESHAPE/tests/test_client.py" <<'PY'
import unittest

from payments.client import PaymentClient


class RecordingSession:
    """Hand-written stub: records calls, returns a fixed response."""

    def __init__(self, response):
        self.response = response
        self.posts = []

    def post(self, path, payload):
        self.posts.append((path, payload))
        return self.response


class ChargeTest(unittest.TestCase):
    def test_charge_returns_charge_id_and_amount(self):
        client = PaymentClient(RecordingSession({"id": "ch_1"}))
        self.assertEqual(client.charge(10), {"charge_id": "ch_1", "amount": 10})

    def test_charge_sends_an_idempotency_key(self):
        session = RecordingSession({"id": "ch_1"})
        PaymentClient(session).charge(10)
        self.assertIn("idempotency_key", session.posts[0][1])

    def test_charge_rejects_zero(self):
        with self.assertRaises(ValueError):
            PaymentClient(RecordingSession({"id": "ch_1"})).charge(0)


class RefundTest(unittest.TestCase):
    def test_refund_returns_refund_id_and_amount(self):
        client = PaymentClient(RecordingSession({"id": "rf_1"}))
        self.assertEqual(
            client.refund("ch_1", 4), {"refund_id": "rf_1", "amount": 4}
        )

    def test_refund_sends_an_idempotency_key(self):
        session = RecordingSession({"id": "rf_1"})
        PaymentClient(session).refund("ch_1", 4)
        self.assertIn("idempotency_key", session.posts[0][1])

    def test_refund_rejects_empty_charge_id(self):
        with self.assertRaises(ValueError):
            PaymentClient(RecordingSession({"id": "rf_1"})).refund("", 4)


if __name__ == "__main__":
    unittest.main()
PY
commit_all "$RESHAPE" -m "Initial payments client, session wrapper, and report fetcher"

git -C "$RESHAPE" checkout -q -b feature/refund-retry
cat > "$RESHAPE/http/session.py" <<'PY'
"""Generic HTTP session wrapper.

Knows nothing about any particular API. Callers layer their own policy
(retries, backoff, auth scopes) on top of these two calls.

The transport raises on any non-2xx response and otherwise returns the
decoded JSON body, which carries `id` for every created resource.
"""

from payments.constants import PAYMENT_RETRY_ATTEMPTS
from utils.retry import with_retry


class Session:
    def __init__(self, transport):
        self._transport = transport

    def get(self, path):
        return with_retry(
            lambda: self._transport.get(path), PAYMENT_RETRY_ATTEMPTS
        )

    def post(self, path, payload):
        return with_retry(
            lambda: self._transport.post(path, payload), PAYMENT_RETRY_ATTEMPTS
        )
PY
cat > "$RESHAPE/payments/client.py" <<'PY'
"""Payments client."""

from utils.idempotency import new_key


class PaymentClient:
    def __init__(self, session):
        self._session = session

    def charge(self, amount):
        """Charge `amount` and return the created charge."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        payload = {"amount": amount, "idempotency_key": new_key()}
        response = self._session.post("/charges", payload)
        return {"charge_id": response["id"], "amount": amount}

    def refund(self, charge_id, amount):
        """Refund `amount` against `charge_id` and return the refund."""
        if not charge_id:
            raise ValueError("charge_id is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        payload = {
            "charge_id": charge_id,
            "amount": amount,
            "idempotency_key": new_key(),
        }
        response = self._session.post("/refunds", payload)
        return {"refund_id": response["id"], "amount": amount}
PY
commit_all "$RESHAPE" -m "Add retry to the payment client's refund path" \
  -m "A transient failure on the refund call is retried instead of surfacing to the caller."
git -C "$RESHAPE" worktree add -q --detach "$WT/silent-reshape" feature/refund-retry

# =====================================================================
# FIXTURE 4: missing-aim
#   Commit message states two aims (refund and cancel); only refund exists.
#   Main is identical to the clean fixture's main.
# =====================================================================
MISSING="$REPOS/missing-aim"
build_clean_main "$MISSING"
git -C "$MISSING" checkout -q -b feature/refund-cancel
write_clean_refund "$MISSING"
commit_all "$MISSING" -m "Add refund() and cancel() to payments client" \
  -m "refund(charge_id, amount) reverses a settled charge. cancel(charge_id) voids an authorization before it is captured. Both validate their inputs and carry an idempotency key."
git -C "$MISSING" worktree add -q --detach "$WT/missing-aim" feature/refund-cancel

# =====================================================================
# summary
# =====================================================================
printf '%-16s %-26s %s\n' fixture branch tip
for pair in "clean:feature/refund" "bad-no-critical:feature/refund-idempotency" \
            "silent-reshape:feature/refund-retry" "missing-aim:feature/refund-cancel"; do
  name="${pair%%:*}"; branch="${pair#*:}"
  printf '%-16s %-26s %s\n' "$name" "$branch" "$(git -C "$REPOS/$name" rev-parse "$branch")"
done
```

PRODUCTION-SAFETY READ (bd-zk46 task 1, run against each feature branch the way the CODE lens reads it — reachable crash path, injection, data loss, duplicate money movement — before the RED dispatches):
- clean: production-safe because: refund() validates both inputs before any transport call; the idempotency key is a fresh uuid4 per call and no code in the repo retries refund(), so no duplicate money movement is reachable; _post documents that the transport raises on non-2xx and returns a body carrying `id`, so response["id"] has no reachable KeyError; the payload is a dict handed to an injected transport, so there is no interpolation and no injection surface; no file, handle, lock, or shared mutable state exists on any exit path. The only money question a lens can raise — whether a CALLER retrying refund() pays twice — requires a caller, and this repo contains none.
- bad-no-critical: production-safe because: the one retried call is refund's _post, and its payload including new_key() is built ONCE outside _retry_loop, so every attempt sends the identical key and a retried refund cannot pay out twice; _retry_loop hardcodes range(3), so last_error is always bound before `raise last_error` and `raise None` is unreachable; charge()'s generated key is a dead local on a path nothing retries, so the unsent key has no in-repo consequence; round(amount, 2) alters a reported value but cannot crash or move money the caller did not request; utils/retry.with_retry keeps its attempts < 1 guard and is simply left uncalled. The defects here are delivery-class (an aim claimed and not delivered) and structural-class (two local re-implementations of utils/ helpers, the shared cause), which is the scenario's point.
- silent-reshape: production-safe because: every payments payload carries an idempotency key built before the call, so Session.post's newly inherited retry cannot double-move money; the only other Session caller, reports/fetch.py, uses get() and is documented and written as read-only, so its inherited retry costs extra requests and never correctness; with_retry keeps its attempts < 1 guard and PAYMENT_RETRY_ATTEMPTS is the literal 4; http/session.py imports payments/constants.py, which imports nothing, so the new arrow creates no import cycle. Every consequence of this branch is structural — inverted dependency direction, relocated policy ownership, an undeclared second consumer — and none is production.
- missing-aim: production-safe because: its delivered code is byte-identical to the clean fixture's (both branch trees are d1c90ac287781d3834f13042fe733ade63c614f7), so the clean argument holds line for line; the fixture's defect is an aim with NO code, and an absent method has no reachable path of any kind — no caller of cancel() exists to raise AttributeError, confirmed by a repo-wide grep returning zero matches.

RECORD CORRECTION (bd-zk46 task 1, 2026-09-03, immediately after the RED BASELINE block above): the task's own Verification step re-runs fixtures.sh twice, which recreates every commit. The tip SHAs in the RED BASELINE header (clean=cf92333 bad=f450b76 reshape=d807eaf missing=80b1c74) are therefore the tips the RED review actually ran against but no longer exist on disk; the tips now are clean=bfe8c0c90fe5a1d29f264eda215b23549d7493bb bad=01720a0e631d40867e8874f6118c850de7f3d53c reshape=9e0fd406a68785e80f4b48144003daca2ca60731 missing=63f015161ab1bf1fbe6cc733b09610beb5281f51. The four branch TREE shas were re-verified after that rebuild and all four match the ledger exactly (clean and missing-aim both d1c90ac287781d3834f13042fe733ade63c614f7, bad 9855ad3c050e53b1ac09bf0c128c7a3f5ee96661, reshape 8b97be00b8597600dd37c9e5446baef1c6e48d69), so every file:line citation in the 20 transcripts under peek-grades/red/ still resolves against the current worktrees. Same anchor bd-v5q5 recorded: the RED->GREEN comparison rests on identical trees, not identical commits. Task 10 should re-record tips at its own run and compare trees, not commits.

RECORD CORRECTION 2 (lead, 2026-09-03, after Stage 2 of bd-xx94 — two [convention] findings on the ledger itself):
(1) The bad-no-critical line in RED BASELINE quotes F1's Trigger and Consequence in quotation marks but paraphrases them. Verbatim from red/bad-no-critical-REPORT.md lines 46-47:
    Trigger: any duplicate invocation of `charge()` for one logical payment — a caller retry after a timeout or 5xx with the charge already accepted upstream, a double-submitted checkout, a transport- or gateway-level retry, or an at-least-once redelivery from a queue. The stated aim names repeated calls as the exact scenario it defends against, so reachability is the author's own premise.
    Consequence: the provider receives two indistinguishable charge requests with no key to deduplicate against and creates two charges. The customer is billed twice for one purchase and real money moves. Because no key was ever transmitted there is no idempotency record on the provider side to reconcile or void the duplicate against, so recovery is manual refunds and reconciliation rather than a no-op retry.
    Task 10 diffs GREEN against these verbatim lines, not the paraphrase.
(2) The four "tips now" SHAs in RECORD CORRECTION (clean=bfe8c0c bad=01720a0 reshape=9e0fd40 missing=63f0151) were already gone when written — fixtures.sh re-ran after the block was appended, and the task's own Verification re-runs it twice. Strike them: commit SHAs in this ledger are never a stable anchor for these fixtures. The branch TREE SHAs are the anchor and were re-verified at this correction: clean=d1c90ac287781d3834f13042fe733ade63c614f7, bad=9855ad3c050e53b1ac09bf0c128c7a3f5ee96661, reshape=8b97be00b8597600dd37c9e5446baef1c6e48d69, missing=d1c90ac287781d3834f13042fe733ade63c614f7 (clean and missing-aim identical). Every file:line citation in the 20 transcripts resolves against these trees.

PRESSURE-TEST CONTRACT (bd-zk46, 2026-09-03, authored after RED BASELINE):
Grading-word list: SEED (never trimmed) careful, carefully, thoughtful, clean, solid, thorough, well-tested, disciplined, high-quality, great care, sloppy, rushed, careless, lazy — OBSERVED, added from the RED top layers with the fixture and sentence each came from: right [clean OA "the only new arrow in the repository is tests pointing at the payments package, which points the right way"; bad-no-critical OA "Its shape is right — refund sits next to charge on the class that already owns provider calls"; silent-reshape OA "The decision itself may well be right — a single retry policy at the transport is a defensible design"], honest [clean OA "The honest limits are worth stating alongside that approval"], earn [clean AvA narrative "The tests earn their verdicts: assertions land on the client's own mapping and call behavior"], declines [bad-no-critical OA "What it declines is the sourcing: this repo already names owners for both cross-cutting concerns the work needed"], slip [bad-no-critical OA "the headline defect is not an isolated slip but the predictable shape of a client that owns a concern it should be borrowing"], reasonable [silent-reshape AvA narrative "not the retry itself, which is a reasonable thing to want"], defensible [silent-reshape OA "a single retry policy at the transport is a defensible design. What is not defensible is arriving at it through a commit that says..."], good [missing-aim OA "Structurally this is the good case"]. Words that describe system behavior are NOT on this list and never count as hits (idempotent, retries, tautological, missing, partial, fits, fights, reshapes, and the like); a listed word used to describe system behavior rather than to grade is still a hit — the rule is zero occurrences, and the fix is to rewrite the sentence.
Top layer (the region every grading-word rule and every sentence ceiling is measured over — byte-identical to the region RED's scan.py measured, so RED and GREEN compare like with like): the `**Verdict:` line, the whole `### What This Branch Does` section, the `### Aimed vs Achieved` narrative up to the aims table, and the whole `### Overall Assessment` section. Sentence counts are taken on narrative only: WTBD up to the Change Inventory list, AvA up to the aims table, OA with any `Path:` or `Decision:` line removed (those lines are labels, not sentences). Scanner: `<scratchpad>/peek-grades/scan-contract.py <REPORT.md>` — same region and same counter as scan.py, with the full list above; run it on every GREEN report and paste its output into the ledger line.
Grading rule (applies to EVERY scenario; both parts must hold, per the LEAD DECISION of 2026-09-03): (i) the scanner reports zero hits from the closed Grading-word list over the top layer; AND (ii) an open-ended read of the same top layer finds no sentence that grades the work or the author — quality, effort, or diligence, in either direction. Part (ii) exists because RED fired exactly ONE listed word across four reports while six evaluative words slipped past a word list (RED BASELINE, FOURTH OBSERVATION); a report that passes (i) and fails (ii) is a scenario failure, and the new word is added to the list in the same fix round.
Method: fixtures rebuilt by `<scratchpad>/peek-grades/fixtures.sh` (worktrees `<scratchpad>/peek-grades/wt/<fixture>`, no remote so peek runs at degradation rung 3 and the commit messages ARE the stated aims); every dispatch `subagent_type: general-purpose`, never `hyperpowers:peek`; RECON sonnet, CODE / ARCHITECTURE / DELIVERY / synthesis opus; the agent body is delivered BY FILE — `sed -n '7,$p' agents/peek.md > <scratchpad>/peek-grades/agent-body.md`, and each dispatch's Step 0 reads that file in full and names it the agent's operating prompt (never retyped into the prompt); the synthesis text is delivered the same way (`sed -n '<Step 6 line range>p' skills/peek/SKILL.md > step6.md`) and synthesis is given RECON's return PLUS the three lens returns, because Step 6's template needs RECON's Change Inventory and review-history line to open the report; every dispatch carries "There is no user present. Do not pause for confirmation or ask questions"; agents write their own returns under `<scratchpad>/peek-grades/green/` (outside the reviewed repo and worktree, Shared Rule 4) and reply with the path and counts only — exactly as the RED BASELINE's METHOD line records, and task 10 replicates it.
- clean [REPORT unless noted]: (1) opens `**Verdict: APPROVE**`; (2) grading rule (i)+(ii) — (ii) evidence from RED: the four listed hits plus "that is tolerable at two consumers and is recorded below as a note for the next reorganization" (OA); (3) What This Branch Does ≤ 6 sentences, Aimed vs Achieved narrative ≤ 4, Overall Assessment ≤ 4; (4) Overall Assessment carries `Path: fix in place`; (5) Overall Assessment carries `Decision: (none)`; (6) the Findings section is `- (none)` (bare, or the template's `- (none) — the code proves no defect...` rendering) — the strict form, because RED already returned Suggestion-only; (7) no production-class Critical anywhere, and a Critical whose `Trigger:` names a caller or input that does not exist in the reviewed repo fails this rule (regression guard on this tree; the same rule is the discriminator on missing-aim) — RED failed: (2) four hits (clean, right, honest, earn), (3) Overall Assessment ran 12 sentences, (4) and (5) no report in the baseline carried a `Path:` or `Decision:` line at all (RED BASELINE, THIRD OBSERVATION), (6) RED returned one `[convention]` Suggestion.
- bad-no-critical [REPORT unless noted]: (1) opens `**Verdict: APPROVE WITH CHANGES**`; (2) zero Criticals of any class; (3) grading rule (i)+(ii) — (ii) evidence from RED: the three listed hits plus "the reason it was shippable without anyone noticing is the part worth deciding about" (OA); (4) `Path: rework` AND the Overall Assessment names the shared cause in plain language — the cause RED's evidence supports is that the branch re-implements shared `utils/` helpers locally (`_retry_loop` at payments/client.py:24-31 duplicating `utils/retry.py`'s `with_retry`, `_make_key` at payments/client.py:21-22 duplicating `utils/idempotency.py`'s `new_key`), the root RED's own Overall Assessment named ("the fight and the defect share a root", "the predictable shape of a client that owns a concern it should be borrowing"); (5) an Important finding for the charge-idempotency aim, whose aims-table row reads `partial`; (6) a finding naming the tautological tests, citing `tests/test_refund.py` and the testing-anti-patterns failure modes; (7) ceilings 6 / 4 / 4 as in clean rule (3) — RED failed: (1) RED returned REQUEST CHANGES, (2) RED returned one Critical, (3) three hits (right, declines, slip), (4) the Path half — no `Path:` line existed (the shared-cause half RED already met, and is kept as a regression guard), (5) RED graded the aim `missing` and filed a production-class Critical on it, (7) Aimed vs Achieved ran 5 and Overall Assessment 7.
- silent-reshape [ARCHITECTURE return for (1); REPORT otherwise]: (1) the Stance block reads `reshapes` and carries `Declared by: none`; (2) exactly one structural-class Critical — its `Critical class:` line reads `structural`, its `Trigger:` names the move (retry policy relocated out of `payments/client.py` into `http/session.py`, and/or the new `http → payments` import at `http/session.py:10`) and its `Consequence:` names the ownership the merge would decide without a record and what inherits it (`reports/fetch.py`, a caller with no line in the diff); (3) opens `**Verdict: REQUEST CHANGES**`; (4) grading rule (i)+(ii) — (ii) evidence from RED: the four listed hits plus "with a second consumer's runtime behavior changed as a side effect nobody signed off on" (OA); (5) ceilings 6 / 4 / 4; (6) Overall Assessment carries a `Path:` line reading exactly one of `fix in place` / `rework` and a `Decision:` line — RED failed: (1) the stance was `reshapes` but no `Declared by:` line existed in the contract at all, (2) RED filed the move as two Importants and returned zero Criticals, (3) RED returned APPROVE WITH CHANGES and said so itself ("The count of individually-Important findings understates the situation, because all six trace to one decision taken without being declared"), (4) four hits (right, reasonable, defensible x2), (5) Overall Assessment ran 11, (6) no `Path:`/`Decision:` lines.
- missing-aim [DELIVERY return and REPORT for (1); REPORT otherwise]: (1) the aims table row for `cancel()` reads `missing`, in DELIVERY's return and as rendered in the report; (2) exactly one delivery-class Critical — its `Critical class:` line reads `delivery`, its `Trigger:` quotes the aim with its source (the commit message "cancel(charge_id) voids an authorization before it is captured"), its `Consequence:` names the capability the merge record claims and the merge would not ship; (3) opens `**Verdict: REQUEST CHANGES**`; (4) no production-class Critical, and a Critical whose `Trigger:` names a caller or input that does not exist in the reviewed repo fails this rule — the report carries exactly one Critical in total and it is the delivery-class one; (5) grading rule (i)+(ii) — (ii) evidence from RED: the one listed hit plus "What makes it unmergeable is narrower and worse" (OA); (6) ceilings 6 / 4 / 4; (7) Overall Assessment carries `Path:` and `Decision:` lines — RED failed: (2) RED filed the missing aim as Important, arguing "no caller of cancel exists anywhere in the repo, so no reachable trigger or consequence can be named", (4) RED's only Critical was production-class on refund's idempotency key, naming a caller-side retry that exists nowhere in the repo, on code byte-identical to the clean fixture's (RED BASELINE, HEADLINE INSTABILITY), (5) one hit (good), (6) What This Branch Does ran 10 and Overall Assessment 12, (7) no `Path:`/`Decision:` lines.
- synth-old: the reconstructed bd-v5q5 synthesis fixture still yields `**Verdict: APPROVE WITH CHANGES**` with the CODE Critical appearing under Findings as Important marked `[downgraded: no consequence named]`, and NEITHER `[lead-added: aim missing]` NOR `[lead-added: undeclared reshape]` appears — the DELIVERY aims table reads `achieved` on every row and the ARCHITECTURE Stance is `fits` with no `Declared by:` line, so the two new re-check moves have nothing to fire on and the fixture tests only the pre-existing downgrade (REFACTOR: an edit made in a fix round may not break this). Reconstructed at `<scratchpad>/peek-grades/synth-old/` (CODE.md, ARCHITECTURE.md, DELIVERY.md) — branch `feature/report-totals -> main`; the Critical at CODE.md carries no `Trigger:` and no `Consequence:` line, ARCHITECTURE holds one `[convention]` Important, DELIVERY holds one Suggestion, matching bd-jwik step 8's three handcrafted returns.
- synth-new: two Criticals appear, marked `[lead-added: aim missing]` and `[lead-added: undeclared reshape]`, each carrying its `Critical class:` line (delivery and structural) plus both a `Trigger:` and a `Consequence:` — a lead-added Critical missing either line is demoted by the re-check's first rule, and a demotion fails this scenario; the report opens `**Verdict: REQUEST CHANGES**`; the Overall Assessment carries a `Path:` line reading exactly one of `fix in place` / `rework` and a `Decision:` line. Handcrafted at `<scratchpad>/peek-grades/synth-new/` (CODE.md, ARCHITECTURE.md, DELIVERY.md) — branch `feature/digest-unsubscribe -> main`; CODE returns `- (none)`, DELIVERY's aims table carries one `missing` row (`unsubscribe(user_id)`) and files NO finding for it, ARCHITECTURE returns Stance `reshapes` / `Declared by: none` whose reasoning names the move concretely (the digest body builder moved from `notifications/digest.py:22-48` to `email/message.py:31-57` and `email/message.py:8` now imports `notifications.templates`, the repo's only transport-to-domain arrow) and files NO finding — so the lead-added Criticals must draw their Trigger and Consequence from the aims table and the Stance reasoning.
Run counts: fixtures ×2 independent, synthesis ×1. A fixture scenario passes only when BOTH runs pass EVERY rule; between the two runs the worktree is removed and re-added so nothing is shared. Every rule is checked by grep or by reading the named section of the named artefact; the ledger line quotes the verbatim evidence per rule (the Verdict line, the `Path:`/`Decision:` lines, each Critical's `Critical class:` / `Trigger:` / `Consequence:`, the Stance and `Declared by:` line, the scanner output, the three sentence counts).
NOTE (clean, rule 6): RED returned exactly one `[convention]` Suggestion — test-support structure, explicitly "No change required on this branch" — so "`- (none)` or Suggestion-only" cannot discriminate GREEN from RED; that disjunction is the bd-v5q5 trap the RED BASELINE names, and the rule is therefore the strict form. Nothing in tasks 3-8 deletes that Suggestion; what motivates the strict form is task 7's self-check sentence ("An APPROVE with `- (none)` under Findings is a short report; nothing is added to make it look reviewed"). If GREEN's only deviation from the clean rule set is that same Suggestion re-appearing, that is a rule failure to escalate at the fix-round cap, never a rule to relax at grading time.
GAP (recorded per task 2's Boundaries; wants a lead decision before task 10 runs): the bad-no-critical rule set as specified is jointly unsatisfiable if DELIVERY grades aim 1 the way RED graded it. RED's DELIVERY returned `missing` for aim 1 ("charge() now generates an idempotency key so a repeated call cannot create a second charge", fixture commit "Add idempotency key to charge()"), verbatim in the aims table of red/bad-no-critical-REPORT.md and in the RED BASELINE line "aim1 charge-idempotency MISSING". Under the post-edit contract a `missing` row files a mandatory delivery-class Critical (task 6, DELIVERY item 1) and the lead files one if the lens does not (task 7, re-check `[lead-added: aim missing]`), so a `missing` row forces REQUEST CHANGES — contradicting rules (1) and (2) above. Nothing in tasks 3-8 changes how DELIVERY grades a row, so requiring `partial` requires a behavior change no edit motivates (writing-skills testing-methodology: "Do not add doctrine a clean RED cannot motivate"). The fixture code supports either reading and cannot settle it: `payments/client.py:37` does mint a key into a local, and `payments/client.py:38` posts a payload without it, so "generates a key" is literally true and "a repeated call cannot create a second charge" is not delivered at all. Two resolutions, the lead's call: (A) keep the rules exactly as written and accept that the scenario now also tests DELIVERY re-grading that row to `partial` — it fails if GREEN repeats RED's `missing`; (B) re-aim the scenario at `**Verdict: REQUEST CHANGES**` with exactly one delivery-class Critical for aim 1, keeping `Path: rework` with the named shared cause and every other rule unchanged — which tests the Path mechanism and the delivery class together and is satisfiable under either grading of the row. The rules above are written per (A), as this task's spec directs.

CONTRACT AMENDMENT 1 (bd-zk46, 2026-09-03, lead answer to task 2 NEEDS_HELP): supersedes the bad-no-critical rule set of the PRESSURE-TEST CONTRACT block above and adds a seventh scenario. The block above is not rewritten and not deleted; where the two disagree this amendment governs, and every rule of that block not named here stands unchanged.
Row grading settled (the GAP this amendment answers): the fixture mints a key into a local at `payments/client.py:37` and posts a payload without it at `payments/client.py:38`, so none of aim 1's capability functions. The row is `missing`, not `partial` — RED's DELIVERY graded it correctly and the scenario design mislabeled it. Task 6's spec now defines the row verdicts (achieved = the capability is present and functioning; partial = a proper subset of it functions; missing = none of it functions, however much scaffolding is present), so GREEN's DELIVERY grades that row `missing` too. Resolution (B) of the GAP is adopted, plus the synth-rework addition below. The fixture, the RED baseline, and the two-part grading rule are untouched.
- bad-no-critical, AMENDED [DELIVERY return and REPORT for (5); REPORT otherwise]: (1) opens `**Verdict: REQUEST CHANGES**`; (2) exactly one Critical in the whole report and it is delivery-class for aim 1 — its `Critical class:` line reads `delivery`, its `Trigger:` quotes the aim's source verbatim (the fixture commit message "Add idempotency key to charge()", `fixtures.sh` line 449), its `Consequence:` names the capability the merge record claims and the merge would not ship; (3) zero production-class Criticals — a Critical whose `Trigger:` names a caller or input absent from the reviewed repo fails this rule, because under the amended anchor that concern routes to Questions for the Author (the same discriminator the clean and missing-aim rule sets carry); (4) Overall Assessment carries `Path: rework` AND names the shared cause in plain language — the cause RED's evidence supports is that the branch re-implements shared `utils/` helpers locally (`_retry_loop` at payments/client.py:24-31 duplicating `utils/retry.py`'s `with_retry`, `_make_key` at payments/client.py:21-22 duplicating `utils/idempotency.py`'s `new_key`), the root RED's own Overall Assessment named ("the fight and the defect share a root"); (5) the DELIVERY aims-table row for aim 1 reads `missing`, in DELIVERY's return and as rendered in the report; (6) a finding at Important or Suggestion naming the tautological Mock-based tests, citing `tests/test_refund.py` (which builds its assertions on `unittest.mock.Mock`, `fixtures.sh` line 383) and the testing-anti-patterns failure modes; (7) grading rule (i)+(ii) unchanged — (ii) evidence from RED: the three listed hits (right, declines, slip) plus "the reason it was shippable without anyone noticing is the part worth deciding about" (OA); (8) ceilings 6 / 4 / 4 as in clean rule (3) — RED failed: (2) RED's single Critical was production-class rather than delivery-class and carried no `Critical class:` line at all, (3) RED's Critical named a caller-side retry that exists nowhere in the repo as its `Trigger:` (RED BASELINE, HEADLINE INSTABILITY), (4) the `Path:` half — no report in the baseline carried a `Path:` line (RED BASELINE, THIRD OBSERVATION; the shared-cause half RED already met and it is kept as a regression guard), (7) three hits, (8) Aimed vs Achieved ran 5 sentences and Overall Assessment 7. Rules (1) and (5) RED already met; they are regression guards, and the discriminating rules are (2), (3), (4), (7) and (8).
Superseded, for the record: the original bad-no-critical rule set aimed the scenario at `**Verdict: APPROVE WITH CHANGES**` with zero Criticals of any class and a `partial` row for aim 1. That aim was jointly unsatisfiable — a `missing` row files a mandatory delivery-class Critical (task 6, DELIVERY item 1) and the lead files one if the lens does not (task 7, `[lead-added: aim missing]`) — and requiring `partial` would have required a re-grading no edit in tasks 3-8 motivates (writing-skills testing-methodology: do not add doctrine a clean RED cannot motivate). The APPROVE-WITH-CHANGES-with-no-Critical outcome is not dropped from the contract; it moves to synth-rework below.
- synth-rework [REPORT]: (1) opens `**Verdict: APPROVE WITH CHANGES**`; (2) zero Criticals of any class, and no `[lead-added:` mark of either kind appears — the DELIVERY rows all read `achieved` and the ARCHITECTURE Stance is `fights`, so neither re-check move has anything to fire on, and a lead-added Critical here is a scenario failure; (3) Overall Assessment carries `Path: rework` — every finding is individually Important and locally fixable, so the Path line must be reached from the shared cause rather than from severity; (4) the Overall Assessment names that shared cause in plain language: the client stands up private copies of helpers `utils/` already centralizes, so the module runs a second retry, backoff and clock policy alongside the shared one; (5) Overall Assessment carries `Decision: (none)`; (6) grading rule (i)+(ii); (7) ceilings 6 / 4 / 4. This fixture carries the coverage of the "bad branch with no Critical" outcome the live bad-no-critical scenario no longer reaches, and it is the only scenario that tests `Path: rework` reached from a non-blocking verdict. Handcrafted at `<scratchpad>/peek-grades/synth-rework/` (CODE.md, ARCHITECTURE.md, DELIVERY.md) — branch `feature/inventory-reservations -> main`; CODE returns three Important `[capability]` findings at three different sites in one client module (`inventory/client.py:19`, `:34`, `:47`), each carrying an `Evidence:` and a `Direction:` line and NEITHER a `Trigger:` NOR a `Consequence:` line, all three re-implementing a `utils/` helper (`utils/retry.py`'s `with_retry`, `utils/backoff.py`'s `exponential`, `utils/clock.py`'s `now_ms`); DELIVERY returns an aims table whose two rows both read `achieved` and `- (none)` under Findings; ARCHITECTURE returns Stance `fights` with NO `Declared by:` line, whose reasoning names the parallel implementations concretely, and `- (none)` under Findings. The shared cause required by rule (4) is therefore available only from CODE's three findings and the Stance reasoning — synthesis is never handed it pre-named.
Run counts (supersedes the `Run counts` sentence of the block above): fixtures ×2 independent, synthesis ×1 each — synth-old ×1, synth-new ×1, synth-rework ×1. The rest of that line stands unchanged: a fixture scenario passes only when BOTH runs pass EVERY rule; between the two runs the worktree is removed and re-added so nothing is shared; every rule is checked by grep or by reading the named section of the named artefact; the ledger line quotes the verbatim evidence per rule.
Unchanged by this amendment: the clean scenario's strict `- (none)` Findings rule and its recorded NOTE about RED's one `[convention]` Suggestion; the silent-reshape, missing-aim, synth-old and synth-new rule sets; the Grading-word list and its seed; the Top layer definition and scanner; the two-part grading rule; and the Method line.

CONTRACT AMENDMENT 2 (lead, 2026-09-03, after Stage 2 of bd-9rqn — four [convention] findings on the contract text, lead-fixed; appended, nothing above rewritten; where this disagrees with the blocks above, this governs):
(1) silent-reshape gains rule (6): no production-class Critical anywhere in the report, and a Critical whose `Trigger:` names a caller or input absent from the reviewed repo fails this rule. Reason: the fixture mints a per-call key at both charge and refund (wt/silent-reshape/payments/client.py:14,26) — the same code shape RED's CODE lens rated production-Critical on missing-aim — so without this guard the scenario could pass GREEN while the HEADLINE INSTABILITY survived. RED evidence: RED's silent-reshape report carried 0 Criticals, so here the rule is a regression guard; it discriminates on clean, missing-aim, and bad-no-critical.
(2) Scanner sentence corrected: `scan-contract.py` measures the same top-layer REGION as RED's `scan.py`; its Overall Assessment sentence counter differs in one respect — it strips `Path:` and `Decision:` label lines before counting, which `scan.py` does not. No RED report carries those lines, so RED's counts reproduce exactly (5/3/12, 5/5/7, 5/4/11, 10/5/12); GREEN reports will carry them, and the stripped count is the one the ceilings are measured on. "Same region, same counter" in the contract block reads as "same region; counter identical except for stripping the two label lines".
(3) The sentence ceilings — What This Branch Does ≤ 6, Aimed vs Achieved narrative ≤ 4, Overall Assessment ≤ 4 — apply to synth-old and synth-new as well. The synthesis output is the report and the ceilings are Step 6 template ceilings; their absence from those two rule sets was an omission, not a reason.
(4) clean rule (6) is settled now, not at the fix-round cap (LEAD DECISION, same class as bd-v5q5's post-RED tightening): the Findings section is `- (none)`, OR Suggestion-only where every Suggestion names a concrete change and carries a `Direction:` line — a Suggestion that states no change is required on this branch is a rule failure (agents/peek.md Shared Rule 10: a finding exists because the code proves it, never to fill a section). RED fails this rule — its one Suggestion read "No change required on this branch" — while a GREEN report carrying a genuine change-naming Suggestion passes it. The NOTE's pre-routed escalation clause is withdrawn; the rule is now satisfiable and still discriminates RED.
Unchanged: every other rule, the Grading-word list and seed, the Method line, the two-part grading rule, and the run counts as amended by CONTRACT AMENDMENT 1. The one [capability] finding — synth-new/ARCHITECTURE.md lacking its `Declared by: none` line — is routed to the task's re-dispatch, not fixed here.

CONTRACT AMENDMENT 3 (lead, 2026-09-03, after the Stage 2 re-review of bd-9rqn — three [convention] findings on CONTRACT AMENDMENT 2's own text, lead-fixed; appended, nothing above rewritten; where this disagrees with the blocks above, this governs):
(1) Rule numbering: the silent-reshape guard CONTRACT AMENDMENT 2 (1) added is rule (7), not (6). The original silent-reshape rule (6) — the Overall Assessment carries `Path:` and `Decision:` lines — stands unchanged. silent-reshape therefore has rules (1)-(7); task 10 quotes evidence for all seven.
(2) Citation corrected: the silent-reshape fixture mints its per-call key at payments/client.py:14 (charge) and payments/client.py:27 (refund), not :26 — line 26 is `"amount": amount,`. Verified against `git -C repos/silent-reshape show feature/refund-retry:payments/client.py`.
(3) Synthesis fixtures and the RECON input: Step 6's What This Branch Does is rendered from RECON's Change Inventory plus a review-history line, and the synthesis method of record delivers RECON's return alongside the three lens returns. The synthesis fixtures held no RECON.md, so the section would be absent, the scanner would score it 0, and the ≤ 6 ceiling would pass vacuously while the grading region shrank. Resolution: each synthesis fixture (synth-old, synth-new, synth-rework) carries a `RECON.md`, authored by task 10 as a setup step BEFORE any synthesis run and never edited afterwards, with: a `Target:` line consistent with the fixture; `### Stated Aims` — one aim per row of that fixture's DELIVERY aims table, same wording, source "commit message"; `### Change Inventory` — one entry per file the three lens returns cite, all `delta`; `### Surprises` — `(none)`, except synth-new, whose undeclared move (the deleted block at notifications/digest.py:22-48 reappearing at email/message.py:31-57 with the new import at email/message.py:8) is listed because no aim covers it; `### Prior Review` — the rung-3 form (`(unavailable at rung 3 — no forge)`, every other line `(none)`, last review point `(none) — no forge`, inventory split all delta); `### Intent Basis` — rung 3; `### Coverage`. The synthesis dispatch then receives step6.md + RECON.md + the three lens returns, exactly as the live scenarios do. With that input the What This Branch Does ≤ 6 ceiling and the full top-layer grading region apply to all three synthesis fixtures for real. Task 10's spec is amended to carry this setup step and to record each RECON.md verbatim in the GREEN ledger.
Unchanged: everything else in the PRESSURE-TEST CONTRACT, CONTRACT AMENDMENT 1, and CONTRACT AMENDMENT 2.

GREEN (2026-09-03, agents/peek.md @ blob de39f0bd7fbc3f4ecb2a373ac738a7fd7ee18ed5, skills/peek/SKILL.md @ blob d74f188caafe36f213f5699e12b76f7724650896, prose-style.md @ blob d9f14040a0c73413b4bd09bda9aa2e9a771e5e73, pipeline-constants.md @ blob 8750eb4708042b5761ee48beaf439f22a9962ff5 (be38365bc62d24908916b011d9c5566a34e54ce9 before fix round 1); repo HEAD at grading ec661a42b5453e07152384a98cdced3d0f30c25c; fixture tips clean=4ca04ee296fdf6491ce63efeca468172c44f45e8 bad=4599d8ef60c52336be2955458033a046dba1e248 reshape=8f66c2cea5f8b7179db02f9b643b7f6eac343192 missing=11af9e3cd7cba188fd11cd7e7c6585d7d533b3b3 — new commits, as the idempotent script recreates them; branch TREE shas all four reproduce the RED BASELINE exactly (clean=d1c90ac287781d3834f13042fe733ade63c614f7, bad=9855ad3c050e53b1ac09bf0c128c7a3f5ee96661, reshape=8b97be00b8597600dd37c9e5446baef1c6e48d69, missing=d1c90ac287781d3834f13042fe733ade63c614f7), so RED and GREEN reviewed identical trees; RECON sonnet, lenses+synthesis opus; every dispatch subagent_type general-purpose, never hyperpowers:peek, with the repo agent body delivered BY FILE per the RED METHOD line — `sed -n '7,$p' agents/peek.md > peek-grades/agent-body.md` regenerated from this HEAD, each dispatch's Step 0 reading it in full as its operating prompt; synthesis delivered `sed -n '116,170p' skills/peek/SKILL.md > step6.md` the same way, plus RECON's return, the confirmed aims, the Surprises block and the three lens returns verbatim; every dispatch carried "There is no user present. Do not pause for confirmation or ask questions; complete the mode and return." and none paused, so no SendMessage resume was needed; between the two runs of each scenario the worktree was removed with `git worktree remove --force`, pruned, and re-added detached at the branch. Returns and reports: peek-grades/green/ (43 files: 8 fixture runs x 5 + 3 synthesis reports); dispatch inputs: peek-grades/green-lens-input/ and peek-grades/green-synth-input/; the superseded pre-fix bad-no-critical transcripts are kept at peek-grades/green-round0/.
- clean run1: pass — (1) `**Verdict: APPROVE** — the payment client gains a refund operation that validates its inputs and carries a per-request idempotency key, added on top of the existing charge path without moving a responsibility or changing a contract.` — (2) scanner `grading-word hits (0): (none)`; open-ended read of the Verdict line, What This Branch Does, the Aimed vs Achieved narrative and the whole Overall Assessment finds no sentence grading quality, effort or diligence in either direction — the closest, `The two surviving observations are local to the new test module and do not bear on the shipped behavior.`, states where the findings sit, not how well the work was done — (3) `sentences: WTBD=5  AvA=3  OA=4` — (4) `Path: fix in place` — (5) `Decision: (none)` — (6) Findings carries `Critical: - (none)` and `Important: - (none)` and two Suggestions, each naming a concrete change and carrying a Direction line: `Direction: Consider relocating the double to a neutral shared home (a `tests/support.py` or a conftest-style module) and importing it from both suites, so neither test module owns a fixture the other depends on. At two suites this is deferrable; it becomes worth doing at the third.` and `Direction: Mirror the sibling suite's per-branch case split — add a negative-amount rejection case and, if `None` is a reachable caller value, a missing-`charge_id` case alongside the empty-string one.` — neither states that no change is required on this branch, so CONTRACT AMENDMENT 2 (4) is met (RED's Suggestion read "No change required on this branch") — (7) no Critical of any class anywhere in the report; the idempotency-key concern that RED rated production-Critical on the byte-identical missing-aim tree is routed to Questions for the Author with the reason stated: `It stays a question rather than a finding because the Severity Anchor's production class requires a Trigger present in this repo or in a contract it documents, and both lanes independently established that no such caller exists.` — opus
- clean run2: pass — (1) `**Verdict: APPROVE** — the payments client gains a refund operation that rejects invalid input before any network call, carries an idempotency key, and arrives with tests for the success path and both rejections.` — (2) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence; the one comparative sentence, `Two of the five new tests go beyond what the aims claim, pinning the posted path and payload and proving that two equal refunds of one charge receive distinct keys.`, states coverage against the aims, not quality — (3) `sentences: WTBD=5  AvA=3  OA=3` — (4) `Path: fix in place` — (5) `Decision: (none)` — (6) `**Critical** - (none)`, `**Important** - (none)`, two Suggestions each with a Direction naming a concrete change: `Direction: Consider asserting that the transport recorded no call on each rejection path, so the ordering the aim states is pinned by a test rather than by reading the method top to bottom.` and `Direction: Consider adding a negative-amount refund case mirroring `tests/test_client.py:47-50`, and a `None` charge-id case alongside the empty-string one.` — (7) no Critical of any class anywhere — opus
- bad-no-critical run1: pass (this is the post-fix re-run; the pre-fix run failed and is recorded in FIX ROUND 1 below) — (1) `**Verdict: REQUEST CHANGES** — the charge path generates an idempotency key and then sends the provider a request that does not carry it, so a repeated charge still creates a second real charge while the merge record says it cannot.` — (2) exactly one Critical in the whole report and its class line reads `  Critical class: delivery`; `Trigger: The confirmed stated aim "Give `charge()` an idempotency key so a repeated call cannot create a second charge." — source: commit message `6743004` ("Add idempotency key to charge()").` and `Consequence: The merge record claims the payments client sends idempotency-keyed charges; the merged code sends none, so the provider has nothing to deduplicate on and a repeated `charge()` creates a second real charge — duplicate money movement, exactly the outcome the aim names.` — (3) zero production-class Criticals: the report's only Critical is the delivery-class one above — (4) `Path: rework`, and the Overall Assessment names the shared cause in plain language: `The branch takes the repository's shared utility layer on as a dependency and then carries its own copies of the two mechanisms that layer exists to own, so key generation and retry policy each live in two places inside one class, and the shared retry module still has no caller anywhere in the repository.` and `A second cause joins the two duplication findings: the client was given private helpers instead of being routed through the modules that already publish those contracts` — (5) the DELIVERY aims-table row reads `| 2. Give `charge()` an idempotency key so a repeated call cannot create a second charge. | missing |` in the DELIVERY return and as rendered in the report — (6) a Suggestion at `tests/test_refund.py:12` names the Mock-based assertion and cites the skill: `It is the shape `testing-anti-patterns` names as an assertion phrased in terms of the mock rather than the behavior.` — (7) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence — the closest, `The test added with the change asserts one thing: the value refund returns.`, counts assertions rather than grading them — (8) `sentences: WTBD=5  AvA=3  OA=4` — opus
- bad-no-critical run2: pass (post-fix re-run) — (1) `**Verdict: REQUEST CHANGES** — the charge path would merge without the duplicate-charge protection the branch's history says it gained, so a retried or double-submitted charge still bills the customer a second time.` — (2) exactly one Critical, `  Critical class: delivery`; `Trigger: the confirmed aim, quoted — "Make `charge()` idempotent by generating a key so a repeated call cannot create a second charge" — source: commit message 6743004 ("Add idempotency key to charge()").` and `Consequence: The merge record claims `charge()` is protected against duplicate charges, and the merge would ship no such protection.` — (3) zero production-class Criticals — (4) `Path: rework`, shared cause named: `The client now holds its own copies of the two mechanisms the shared utility module owns for money-moving calls, and it runs its two money paths through different copies — the charge path through the private generator, the refund path through the shared one. That split is the one cause beneath the undelivered charge aim and both structural findings` — (5) aims row `| 1. Make `charge()` idempotent by generating a key so a repeated call cannot create a second charge — source: commit 6743004 | missing |` in DELIVERY's return and in the report — (6) an Important at `tests/test_refund.py:8-12`: `Separately, the assertion has the shape `testing-anti-patterns` names as testing the double rather than the unit: the expected value is read back off the mock's own configuration (`transport.post.return_value["id"]`, :12) instead of the independent literal "rf_1" set at :10` — (7) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence — (8) `sentences: WTBD=5  AvA=4  OA=4` — opus
- silent-reshape run1: pass — (1) the ARCHITECTURE return's Stance block opens `**reshapes** — Retry-policy ownership for the payments edge moved out of `payments/client.py`, whose docstring claimed exactly that responsibility` and carries `Declared by: **none** — the one confirmed aim ("Add retry to the payment client's refund path, so a transient failure on the refund call is retried instead of surfacing to the caller", commit 8f66c2c) names the refund feature the move enables; it does not name the relocation of retry ownership, the new `http` → `payments` dependency, or the change to `Session`'s behavior for its other caller.` (the value is `none`; the markdown emphasis is presentation) — (2) exactly one structural-class Critical, `  Critical class: structural`, `Trigger: The move — responsibility for "how aggressively this service retries a call" transferred from `payments/client.py` (declared owner on `main`, client.py:1) to `http/session.py:18-26`, and the package dependency arrow gained a new inward edge from the generic transport layer to the payments domain at `http/session.py:10`, where `http` previously depended on nothing.`, `Consequence: The merge would settle — on the strength of a commit message about refunds — that retry policy in this service is a transport-layer concern rather than a per-caller one, and that `http` may depend on domain packages, with no ADR, issue, or description recording that either decision was made. What inherits it: every present and future `Session` caller silently receives payments' retry policy with no opt-out (`ReportFetcher` already does, `reports/fetch.py:9`)` — (3) `**Verdict: REQUEST CHANGES** — Retry ownership for the payments edge moved into the shared HTTP session, so the merge would settle, on the strength of a commit message about refunds, that call policy in this service is a transport-layer concern and that the transport layer may depend on the payments domain — with a read-only reports caller already inheriting the payments retry budget as a result.` — (4) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence (RED's `right`, `reasonable`, `defensible x2` are all gone) — (5) `sentences: WTBD=6  AvA=4  OA=4` — (6) `Path: rework` and `Decision: whether retry policy belongs in the shared HTTP session at all — accept the relocation and declare it, which then settles where the attempt budget lives and what the session's contract says, or keep policy at the payments edge and give the refund call the retry that charge already had. The findings can be addressed either way; only the reader can choose which.` — (7) no production-class Critical anywhere: the report's only Critical is the structural one; the per-call key at wt/silent-reshape/payments/client.py:14,27 drew none — opus
- silent-reshape run2: pass — (1) ARCHITECTURE Stance `reshapes — retry policy stopped being a per-edge caller policy and became a property of the generic transport` with `Declared by: none — the sole confirmed aim ("A transient failure on the refund call is retried instead of surfacing to the caller," commit 8f66c2c) is a feature the move was made to enable, not a statement of the ownership or dependency-direction change itself.` — (2) exactly one structural-class Critical, `  Critical class: structural`, `Trigger: The move — retry-policy ownership from `PaymentClient` (payments/client.py:1, payments/client.py:15) to `http.Session` (http/session.py:18-26), plus a new dependency arrow from the generic HTTP layer to the payments edge (http/session.py:10 importing `payments.constants`).`, `Consequence: The merge record would decide, without saying so, that retry is a transport-layer concern owned by `Session` and that the generic layer may depend on a specific edge's tuning — reversing the contract `http/session.py:3-4` still states. What inherits it: every present and future `Session` caller acquires four payments-tuned attempts with no opt-out (`reports/fetch.py:8-9` already has)` — (3) `**Verdict: REQUEST CHANGES** — the refund retry arrives by moving retry ownership out of the payments edge into the shared HTTP session and pointing the generic layer at a payments tuning constant, so merging would settle a service-wide policy question that nothing in the change record states.` — (4) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence — (5) `sentences: WTBD=5  AvA=3  OA=4` — (6) `Path: rework` and `Decision: Accept the reshape — retry owned by the shared session, service-wide, at a payments-tuned default — or send it back so retry stays at the payments edge and the refund call is wrapped where the charge call was. Every finding below follows from that call.` — (7) no production-class Critical anywhere — opus
- missing-aim run1: pass — (1) the aims-table row reads `| 2. Add `cancel(charge_id)` that voids an authorization before it is captured, validating its inputs and carrying an idempotency key. — source: commit message `11af9e3` | missing | ... `grep -rniE 'cancel\|void\|authoriz\|capture'` across the whole worktree returns zero matches` in DELIVERY's return and as rendered in the report — (2) exactly one delivery-class Critical, `  Critical class: delivery`, `Trigger: The aim, quoted from its source — commit `11af9e3` ("Add refund() and cancel() to payments client"), whose body states: "cancel(charge_id) voids an authorization before it is captured. Both validate their inputs and carry an idempotency key."`, `Consequence: Merging writes a permanent claim into history — both the subject line "Add refund() and cancel()" and the body sentence describing `cancel`'s behavior — that the payments client can void an uncaptured authorization, while `PaymentClient` exposes no such method.` — (3) `**Verdict: REQUEST CHANGES** — the branch ships the refund path but not the cancel path its merge record announces, so a caller written against that record reaches a method the payments client does not have.` — (4) no production-class Critical: the report carries exactly one Critical in total and it is the delivery-class one; RED's production-class Critical on refund's idempotency key, on code byte-identical to clean's, is gone — (5) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence (RED's `good case` is gone) — (6) `sentences: WTBD=6  AvA=4  OA=4` — (7) `Path: fix in place` and `Decision: whether `cancel()` lands on this branch before merge, or the commit message is amended so the merge record claims only the refund operation and the void operation moves to a follow-up.` — opus
- missing-aim run2: pass — (1) the aims-table row reads `| 2. Add `cancel(charge_id)` to void an authorization before it is captured, validating its inputs and carrying an idempotency key | missing | `payments/client.py:16-55` — `PaymentClient` defines only `__init__`, `_post`, `charge`, `refund`; no `cancel` method exists.` in DELIVERY's return and in the report — (2) exactly one delivery-class Critical, `  Critical class: delivery`, `Trigger: Stated aim 2, quoted from its source — commit `11af9e3` body: "cancel(charge_id) voids an authorization before it is captured. Both validate their inputs and carry an idempotency key." — confirmed at the intent gate as stated aim 2 of 2.`, `Consequence: The merge record claims a capability the merge does not ship. ... a caller reaching for `client.cancel(charge_id)` on the strength of that record gets an `AttributeError` at runtime` — (3) `**Verdict: REQUEST CHANGES** — the branch's merge record announces a pre-capture cancellation capability on the payments client that the merge does not ship, so a caller written against that record hits an `AttributeError` at runtime with no alternative path to void an uncaptured authorization.` — (4) no production-class Critical; one Critical in total, delivery-class — (5) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence — (6) `sentences: WTBD=5  AvA=4  OA=3` — (7) `Path: fix in place` and `Decision: whether `cancel(charge_id)` is implemented on this branch, or the branch's stated scope is amended so the merge record claims only the refund it ships and cancellation is tracked as separate work.` — opus
- synth-old: pass — run once, AFTER the fix-round-1 commit, as the REFACTOR check that the edit did not break the old fixture — (1) `**Verdict: APPROVE WITH CHANGES** — Two defects stand before merge: the average has no defined behavior for an empty series, and the branch introduces a second rounding path alongside the one the codebase already designates.` — (2) CODE's Critical appears under Findings as Important carrying the downgrade mark: `**Important** · `[capability]` · scope: delta · `reports/calc.py:14` · `[downgraded: no consequence named]`` with `Downgrade: filed as Critical without the `Trigger:` and `Consequence:` lines the production class requires (`skills/common-patterns/pipeline-constants.md`, Severity Anchor), so synthesis reduced it to Important.` — (3) `grep -c 'lead-added' synth-old-REPORT.md` returns 0: neither `[lead-added: aim missing]` nor `[lead-added: undeclared reshape]` appears, as the aims table reads `achieved` on both rows and the Stance is `fits` with no `Declared by:` line — (4) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence — (5) `sentences: WTBD=6  AvA=2  OA=3` (CONTRACT AMENDMENT 2 (3) ceilings) — opus
- synth-new: pass — (1) two Criticals appear, `**Critical** `[capability]` — Scope: delta — `notifications/client.py:18-58` — `[lead-added: aim missing]`` with `- Critical class: Delivery`, `- Trigger: stated aim 2, "Add `unsubscribe(user_id)` so a user can stop receiving digests" — source: commit message.` and `- Consequence: the merge record claims a way for a user to stop receiving digests, and the merge would ship none.`; and `**Critical** `[capability]` — Scope: delta — `email/message.py:8,31-57` — `[lead-added: undeclared reshape]`` with `- Critical class: Structural`, `- Trigger: digest body rendering moved out of the notifications domain and into the shared mail transport — the block at `notifications/digest.py:22-48` on base is deleted there and reappears at `email/message.py:31-57`` and `- Consequence: the merge decides, with no record, that the generic mail transport owns message rendering and depends on the notifications domain to do it — the only inward, transport-to-domain dependency in the repository`. Both carry Critical class, Trigger and Consequence, so neither is demoted by the re-check's first rule — (2) `**Verdict: REQUEST CHANGES** — Two consequences decide it: the capability to stop receiving digests that the merge record claims is absent from the code, and the shared mail transport takes over digest rendering — acquiring a dependency on the notifications domain — with no record that the change was intended.` — (3) `Path: fix in place` (exactly one of the two words) and `Decision: Whether the mail transport keeps ownership of digest rendering — accept it and record the rule it establishes, or send the body builder back to the notifications domain — and whether the unsubscribe capability is delivered on this branch or dropped from its record.` — (4) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence — (5) `sentences: WTBD=4  AvA=3  OA=4` — opus
- synth-rework: pass — (1) `**Verdict: APPROVE WITH CHANGES** — The new client carries its own retry, backoff, and clock policy instead of the shared ones every other service client uses, so a future change to any of those policies will reach every client except this one.` — (2) Findings opens `**Critical**` / `- (none)`; the three surviving findings are all Important, and `grep -c 'lead-added' synth-rework-REPORT.md` returns 0 — (3) `Path: rework`, reached from the shared cause rather than from severity, since every finding is individually Important — (4) the Overall Assessment names that cause in plain language: `All three findings have the same cause — the new module reaches for no shared helper at all, so each policy it needed got a local copy — and addressing them one at a time leaves that cause standing until the client is routed through the shared package.` — (5) `Decision: (none)` — (6) scanner `grading-word hits (0): (none)`; open-ended read finds no grading sentence — (7) `sentences: WTBD=5  AvA=4  OA=4` — opus
SYNTHESIS-FIXTURE RECON.md FILES (authored once at setup per CONTRACT AMENDMENT 3, before any synthesis run, and never edited afterwards; recorded here verbatim. Reading note: the amendment says "Change Inventory of every file the three returns cite, all delta". The three returns cite pre-existing modules as context too (utils/money.py in synth-old; utils/retry.py, utils/backoff.py, utils/clock.py, orders/client.py, shipping/client.py, tests/conftest.py in synth-rework; alerts/mailer.py, notifications/templates.py in synth-new), and listing those as delta would have contradicted the returns own statements of what the delta is. Each inventory therefore lists every file the returns cite AS CHANGED BY THE BRANCH, all delta — which is exactly four entries for synth-new, matching that fixture DELIVERY Coverage line "the delta is four files", and two entries each for synth-old and synth-rework, matching their Undeclared Changes lines "the delta is reports/calc.py:12-32 plus tests/test_calc.py" and "the delta is inventory/client.py:1-70 plus tests/test_reserve.py". Flagging the reading for the lead; no rule was relaxed and no lens return was touched.):

--- peek-grades/synth-old/RECON.md ---
Target: `feature/report-totals` -> `main` (forge none, degradation rung 3)

### Stated Aims
1. Add `average(values)` to the report totals module — source: commit message
2. Add `summarize(rows)` returning count, total, and average for a report — source: commit message

### Change Inventory
- `reports/calc.py`: +21/-0 across 1 file — adds `average(values)` (`:12-15`), `summarize(rows)` returning count, total and average (`:22-27`), and a private `_round2()` rounding helper (`:30-32`) — delta
- `tests/test_calc.py`: +31/-0, new file — declares three row fixtures (`:5-7`) and covers `average()` over three values and over one (`:9-14`, `:16-19`) and `summarize()`'s three members against hand-computed values (`:22-31`) — delta

### Surprises
- (none)

### Prior Review
- Review decision: (unavailable at rung 3 — no forge)
- Approvals: (none)
- Settled points: (none)
- Open threads: (none)
- Prior peeks: (none)
- Last review point: (none) — no forge
- Inventory split: previously-reviewed: (none) / delta: all

### Intent Basis
- Degradation rung: 3 — no forge CLI is usable and the repository has no remote, so no merge request, description, linked issue, or review state was reachable; intent comes from `git log main..HEAD` and `git diff --stat main...HEAD` alone.
- Confidence in inferred intent: High — the commit message names both functions and what each returns, and the diff adds exactly those two functions plus the helper they call.
- Prior review basis: no forge and no remote at rung 3, so no approvals, review decision, threads, or prior peek markers exist to read.

### Coverage
- Examined: `git log main..HEAD`, `git diff --stat main...HEAD`, and the full diff; `reports/calc.py` and `tests/test_calc.py` at branch state.
- Not examined / unavailable: merge-request title, description, closing issues, comments, approvals, and review threads — none reachable at rung 3.
- Review state: unavailable at rung 3 (no forge, no remote).
--- peek-grades/synth-new/RECON.md ---
Target: `feature/digest-unsubscribe` -> `main` (forge none, degradation rung 3)

### Stated Aims
1. Add `send_digest(user_id)` to the notifications client so nightly summaries go out through the existing provider seam — source: commit message
2. Add `unsubscribe(user_id)` so a user can stop receiving digests — source: commit message

### Change Inventory
- `notifications/client.py`: +18/-0 across 1 file — adds `send_digest(user_id)` (`:41-58`), which builds the message through `email.message.build_digest` and posts it through the existing `self._transport.send` seam (`:57`) — delta
- `notifications/digest.py`: +0/-27 across 1 file — the digest body-building block that lived at `:22-48` on base is deleted — delta
- `email/message.py`: +28/-0 across 1 file — gains the digest body builder at `:31-57` and a new `from notifications.templates import DIGEST_BODY` at `:8` — delta
- `tests/test_digest.py`: +24/-0, new file — covers `send_digest()` end to end through the transport seam (`:11-24`) — delta

### Surprises
- The digest body builder moved from the notifications domain into the shared mail transport — the block at `notifications/digest.py:22-48` on base is deleted there and reappears at `email/message.py:31-57`, and `email/message.py:8` adds `from notifications.templates import DIGEST_BODY`. No stated aim mentions rendering, `email/message.py`, or a change to the transport's dependencies.

### Prior Review
- Review decision: (unavailable at rung 3 — no forge)
- Approvals: (none)
- Settled points: (none)
- Open threads: (none)
- Prior peeks: (none)
- Last review point: (none) — no forge
- Inventory split: previously-reviewed: (none) / delta: all

### Intent Basis
- Degradation rung: 3 — no forge CLI is usable and the repository has no remote, so no merge request, description, linked issue, or review state was reachable; intent comes from `git log main..HEAD` and `git diff --stat main...HEAD` alone.
- Confidence in inferred intent: High for what the commit message claims — it names both operations by signature and purpose. The message says nothing about the rendering move the diff also contains, which is why that move is listed under Surprises rather than treated as intended.
- Prior review basis: no forge and no remote at rung 3, so no approvals, review decision, threads, or prior peek markers exist to read.

### Coverage
- Examined: `git log main..HEAD`, `git diff --stat main...HEAD`, and the full diff; `notifications/client.py`, `notifications/digest.py`, `notifications/templates.py`, `email/message.py`, and `tests/test_digest.py` at branch state, plus `notifications/digest.py` at base to locate the deleted block.
- Not examined / unavailable: merge-request title, description, closing issues, comments, approvals, and review threads — none reachable at rung 3.
- Review state: unavailable at rung 3 (no forge, no remote).
--- peek-grades/synth-rework/RECON.md ---
Target: `feature/inventory-reservations` -> `main` (forge none, degradation rung 3)

### Stated Aims
1. Add `reserve(sku, qty)` to the inventory client so an order can hold stock before payment — source: commit message
2. Add `release(reservation_id)` so an abandoned cart returns stock — source: commit message

### Change Inventory
- `inventory/client.py`: +70/-0 across 1 file, new module — adds the inventory client with `reserve(sku, qty)` (`:41-56`) and `release(reservation_id)` (`:58-70`), plus the private `_retry()` (`:19-27`), `_backoff_delay()` (`:34-38`) and `_now_ms()` (`:47-49`) helpers those two methods call — delta
- `tests/test_reserve.py`: +55/-0, new file — covers `reserve()` holding stock and returning an id (`:11-24`), its rejection of a quantity above the free count (`:26-33`), the reservation expiry it computes (`:38-44`), and a reserve-then-release round trip returning the free count to its starting value (`:46-55`) — delta

### Surprises
- (none)

### Prior Review
- Review decision: (unavailable at rung 3 — no forge)
- Approvals: (none)
- Settled points: (none)
- Open threads: (none)
- Prior peeks: (none)
- Last review point: (none) — no forge
- Inventory split: previously-reviewed: (none) / delta: all

### Intent Basis
- Degradation rung: 3 — no forge CLI is usable and the repository has no remote, so no merge request, description, linked issue, or review state was reachable; intent comes from `git log main..HEAD` and `git diff --stat main...HEAD` alone.
- Confidence in inferred intent: High — the commit message names both operations and the workflow each serves, and the diff adds exactly those two methods and the helpers they call.
- Prior review basis: no forge and no remote at rung 3, so no approvals, review decision, threads, or prior peek markers exist to read.

### Coverage
- Examined: `git log main..HEAD`, `git diff --stat main...HEAD`, and the full diff; `inventory/client.py` and `tests/test_reserve.py` at branch state.
- Not examined / unavailable: merge-request title, description, closing issues, comments, approvals, and review threads — none reachable at rung 3.
- Review state: unavailable at rung 3 (no forge, no remote).
--- end RECON.md files ---

GREEN RESULT: 11 of 11 runs passed every rule (8 fixture runs + 3 synthesis runs); fix rounds: ec661a42b5453e07152384a98cdced3d0f30c25c (one round, bad-no-critical only; cap of 2 per scenario not reached)

FIX ROUND 1 (bd-zk46 task 10, 2026-09-03, commit ec661a42b5453e07152384a98cdced3d0f30c25c, one bounded wording edit in skills/common-patterns/pipeline-constants.md, the file that owns the Severity Anchor; no requirement changed, no floor added, no owner definition restated at a consumer, no word trimmed from the grading list):
- The failing run: bad-no-critical run 1, pre-fix (transcripts kept at peek-grades/green-round0/). It failed rules (2) and (3) of CONTRACT AMENDMENT 1's amended rule set. Verbatim: the report carried exactly one Critical, but its class line read `  Critical class: delivery + production (one code fact meets both bars; the delivery and production findings returned at this location were the same defect and are merged here)`, with paired `Trigger (delivery):` / `Trigger (production):` and `Consequence (delivery):` / `Consequence (production):` lines. Rule (2) requires the single Critical's class line to read `delivery`; rule (3) requires zero production-class Criticals. Every other rule passed on that run: `**Verdict: REQUEST CHANGES**`, `Path: rework` with the shared cause named, aims row `missing`, the tautological-tests finding, `grading-word hits (0): (none)`, `sentences: WTBD=5  AvA=3  OA=4`.
- The loophole named: the compound class was a synthesis artefact, but its root was upstream in the CODE lens. That lens filed a production-class Critical at payments/client.py:37-38 whose `Trigger:` read `the same logical charge submitted to `/charges` more than once — the retry-of-a-money-moving-call sequence the reviewed repo documents at `utils/idempotency.py:9-11` and `utils/retry.py:1` ("Every caller that retries a call uses this"), implements at `utils/retry.py:8-23`, and runs on the sibling path at `payments/client.py:53`.` No caller of PaymentClient exists anywhere in that repo — the RED BASELINE's HEADLINE INSTABILITY and the LEAD DECISION of 2026-09-03 both settled that this concern routes to Questions for the Author. The permitting sentence was the Severity Anchor's production-class Trigger clause: `it must exist in the reviewed repo or in a contract the repo documents — a caller that would have to exist elsewhere is not a Trigger`. The second disjunct was swallowing the first: a docstring describing how callers are expected to behave was being read as the contract that makes an absent caller a Trigger. Run 2 on the identical tree filed no Critical from CODE at all, which is the instability itself, not a difference in the code.
- The edit (skills/common-patterns/pipeline-constants.md, Severity Anchor, Production class Trigger wording only; the three classes stay three): `in the reviewed repo or in a contract the repo documents — a caller that would have to exist elsewhere is not a Trigger` becomes `in the reviewed repo or in an interface contract the repo publishes to callers outside it — a caller that would have to exist elsewhere is not a Trigger, and a comment or docstring describing how callers are expected to behave is not such a contract`. The legitimate case the disjunct exists for — a library whose published interface contract is the only caller evidence available — is preserved; the docstring-about-absent-callers reading is closed. No other file changed: `grep -rn 'contract the repo documents\|would have to exist' --include='*.md' .` returned the single owning line before the edit, so there was no consumer restatement to keep in step.
- REFACTOR: both runs of bad-no-critical were re-run from scratch (fresh RECON, three lenses, synthesis; worktree removed, pruned and re-added between them) and both passed every rule — evidence in the per-run lines above. synth-old was re-run once after the commit and still yields `**Verdict: APPROVE WITH CHANGES**` with the CODE Critical downgraded to Important marked `[downgraded: no consequence named]` and no lead-added mark, so the edit did not break the old fixture. The clean, silent-reshape and missing-aim runs recorded above all pre-date the commit and were not re-run; the edit only narrows what qualifies as a production-class Trigger, and none of those six runs carried a production-class Critical to lose.
- Verification after the fix: every Verification grep from tasks 3-8 (bd-nghi, bd-lxrd, bd-7p7h, bd-mt9c, bd-a159, bd-cmmt) re-run at this HEAD and all hold — including bd-7p7h's `grep -n 'reviewed repo' skills/common-patterns/pipeline-constants.md`, still exactly 1 hit inside the Production class. Every epic Success Criterion grep that does not depend on task 9 passes; `./hooks/test/contract-test.sh` reports `10 passed, 0 failed`; `git status --porcelain` empty. Two criteria remain open because task 9 owns them: README.md line 40 still reads `harsh-but-fair` (the skills/peek/SKILL.md half of that criterion is already clean at 0 hits), and .claude-plugin/plugin.json is not yet at 3.37.0. One note for the reader: the criterion `grep -n 'any Critical → REQUEST CHANGES; else any Important → APPROVE WITH CHANGES; else APPROVE'` returns 0 only because loop-interfaces.md line-wraps that sentence across lines 116-117; the derivation text itself is unchanged and present.

POINTER (2026-09-09): the fixture script embedded above was extended by epic bd-3ahi (FIXTURE 5, bikeshed). The current script is the copy embedded in docs/ledgers/bd-3ahi-pressure-tests.md; extend that one.
