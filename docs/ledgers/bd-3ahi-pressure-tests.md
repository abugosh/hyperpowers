# bd-3ahi pressure-test ledger

Epic bd-3ahi — Harsh but fair: peek verdict bar and forge approval. The four
inherited fixtures (clean, bad-no-critical, silent-reshape, missing-aim) and
the GREEN rules that govern them live in `docs/ledgers/bd-zk46-pressure-tests.md`
(PRESSURE-TEST CONTRACT plus CONTRACT AMENDMENTS 1-3); nothing here rewrites or
supersedes that file. This ledger carries the fifth fixture (bikeshed), this
epic's RED baseline, its contract, its synthesis-fixture records, and its GREEN.
Fixture repos, worktrees, and agent returns live in the session scratchpad and
are never committed; the fixture script below rebuilds all five repos.

---

FIXTURE SCRIPT (bd-3ahi task 1): full contents of <sp>/fixtures.sh, fenced below, where <sp> is this session's scratchpad root `.../scratchpad/peek-bar/`. It is the bd-zk46 script (that ledger's fenced block, lines 23-770) with FIXTURE 5 spliced in ahead of the summary, `"bikeshed:feature/refund"` added to the summary loop, and the file header's "Four ... repos" corrected to five; the four inherited fixtures are byte-for-byte unchanged and reproduce their recorded branch TREE shas exactly (clean d1c90ac287781d3834f13042fe733ade63c614f7, bad-no-critical 9855ad3c050e53b1ac09bf0c128c7a3f5ee96661, silent-reshape 8b97be00b8597600dd37c9e5446baef1c6e48d69, missing-aim d1c90ac287781d3834f13042fe733ade63c614f7, all re-verified after the header correction). The header correction landed after the RED dispatches; it is a comment, changes no built tree, and every tree above plus bikeshed's was re-verified across two further runs, so the RED baseline below stands against the script as printed here. Idempotent (rm -rf then rebuild; exits 0 on a second run) and content-deterministic — it recreates commits with new SHAs but reproduces the branch TREE shas, which is what the RED->GREEN comparison rests on. It builds five git repos under <sp>/repos/ and their detached worktrees under <sp>/wt/, each a tiny Python/unittest project with a main branch and one feature branch and NO remote, so peek runs at degradation rung 3 and the commit messages ARE the stated aims. bikeshed's main is byte-identical to clean's main (both trees 5e6db6c5a7638de51ec93d678d96222269de4d50) and its branch tree is 9bbf96732a24bde4fd7ee4f26a57738162efb8c2, which differs from clean's — the delivered behavior is the same refund(), written with the four bikeshedable surfaces the epic commissioned.
```bash
#!/usr/bin/env bash
# Pressure-test fixture builder for epic bd-zk46 (peek grades the system),
# extended by epic bd-3ahi (harsh but fair), which adds FIXTURE 5.
# Five tiny Python/unittest repos, each with a main branch and one feature
# branch, no remote (peek runs at degradation rung 3, so the commit messages
# ARE the stated aims). None of the five branches contains a production-class
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
# FIXTURE 5: bikeshed
#   Main is byte-identical to clean's main. The branch adds the same
#   refund() as clean, with the same commit message, written the way a
#   reviewer would want to tidy: one inline method, short locals, a few
#   narrating step comments, and tests whose setup is copy-pasted per
#   test. No defect that names who is hit or a cost the next change
#   pays: inputs validated, per-call key from main's own helper, honest
#   assertions, nothing duplicated that must stay in sync.
# =====================================================================
write_bikeshed_refund() {
  local dir="$1"
  cat >> "$dir/payments/client.py" <<'PY'

    def refund(self, charge_id, amount):
        """Refund `amount` against `charge_id` and return the refund."""
        # check the charge id
        cid = charge_id
        if not cid:
            raise ValueError("charge_id is required")
        # check the amount
        amt = amount
        if amt <= 0:
            raise ValueError("amount must be positive")
        # build the payload
        payload = {}
        payload["charge_id"] = cid
        payload["amount"] = amt
        payload["idempotency_key"] = _new_idempotency_key()
        # post it and map the response
        resp = self._post("/refunds", payload)
        result = {}
        result["refund_id"] = resp["id"]
        result["charge_id"] = cid
        result["amount"] = amt
        return result
PY
  cat > "$dir/tests/test_refund.py" <<'PY'
import unittest

from payments.client import PaymentClient
from tests.test_client import RecordingTransport


class RefundTest(unittest.TestCase):
    def test_refund_returns_refund_id_charge_id_and_amount(self):
        transport = RecordingTransport({"id": "rf_1"})
        client = PaymentClient(transport)
        self.assertEqual(
            client.refund("ch_1", 4),
            {"refund_id": "rf_1", "charge_id": "ch_1", "amount": 4},
        )

    def test_refund_posts_path_charge_id_amount_and_a_key(self):
        transport = RecordingTransport({"id": "rf_1"})
        client = PaymentClient(transport)
        client.refund("ch_1", 4)
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
        transport = RecordingTransport({"id": "rf_1"})
        client = PaymentClient(transport)
        with self.assertRaises(ValueError):
            client.refund("", 4)

    def test_refund_rejects_zero_amount(self):
        transport = RecordingTransport({"id": "rf_1"})
        client = PaymentClient(transport)
        with self.assertRaises(ValueError):
            client.refund("ch_1", 0)


if __name__ == "__main__":
    unittest.main()
PY
}

BIKESHED="$REPOS/bikeshed"
build_clean_main "$BIKESHED"
git -C "$BIKESHED" checkout -q -b feature/refund
write_bikeshed_refund "$BIKESHED"
commit_all "$BIKESHED" -m "Add refund() to payments client" \
  -m "refund(charge_id, amount) validates its inputs and posts a refund carrying an idempotency key. Covered by tests for the happy path and both rejection paths."
git -C "$BIKESHED" worktree add -q --detach "$WT/bikeshed" feature/refund

# =====================================================================
# summary
# =====================================================================
printf '%-16s %-26s %s\n' fixture branch tip
for pair in "clean:feature/refund" "bad-no-critical:feature/refund-idempotency" \
            "silent-reshape:feature/refund-retry" "missing-aim:feature/refund-cancel" \
            "bikeshed:feature/refund"; do
  name="${pair%%:*}"; branch="${pair#*:}"
  printf '%-16s %-26s %s\n' "$name" "$branch" "$(git -C "$REPOS/$name" rev-parse "$branch")"
done
```

PRODUCTION-SAFETY READ (run against each feature branch the way the CODE lens reads it — reachable crash path, injection, data loss, duplicate money movement — before the RED dispatches). The first four lines are verbatim from `docs/ledgers/bd-zk46-pressure-tests.md` (that ledger's PRODUCTION-SAFETY READ block) and are reproduced here because this ledger carries the whole five-fixture script; the fifth is bd-3ahi task 1's own read of bikeshed:
- clean: production-safe because: refund() validates both inputs before any transport call; the idempotency key is a fresh uuid4 per call and no code in the repo retries refund(), so no duplicate money movement is reachable; _post documents that the transport raises on non-2xx and returns a body carrying `id`, so response["id"] has no reachable KeyError; the payload is a dict handed to an injected transport, so there is no interpolation and no injection surface; no file, handle, lock, or shared mutable state exists on any exit path. The only money question a lens can raise — whether a CALLER retrying refund() pays twice — requires a caller, and this repo contains none.
- bad-no-critical: production-safe because: the one retried call is refund's _post, and its payload including new_key() is built ONCE outside _retry_loop, so every attempt sends the identical key and a retried refund cannot pay out twice; _retry_loop hardcodes range(3), so last_error is always bound before `raise last_error` and `raise None` is unreachable; charge()'s generated key is a dead local on a path nothing retries, so the unsent key has no in-repo consequence; round(amount, 2) alters a reported value but cannot crash or move money the caller did not request; utils/retry.with_retry keeps its attempts < 1 guard and is simply left uncalled. The defects here are delivery-class (an aim claimed and not delivered) and structural-class (two local re-implementations of utils/ helpers, the shared cause), which is the scenario's point.
- silent-reshape: production-safe because: every payments payload carries an idempotency key built before the call, so Session.post's newly inherited retry cannot double-move money; the only other Session caller, reports/fetch.py, uses get() and is documented and written as read-only, so its inherited retry costs extra requests and never correctness; with_retry keeps its attempts < 1 guard and PAYMENT_RETRY_ATTEMPTS is the literal 4; http/session.py imports payments/constants.py, which imports nothing, so the new arrow creates no import cycle. Every consequence of this branch is structural — inverted dependency direction, relocated policy ownership, an undeclared second consumer — and none is production.
- missing-aim: production-safe because: its delivered code is byte-identical to the clean fixture's (both branch trees are d1c90ac287781d3834f13042fe733ade63c614f7), so the clean argument holds line for line; the fixture's defect is an aim with NO code, and an absent method has no reachable path of any kind — no caller of cancel() exists to raise AttributeError, confirmed by a repo-wide grep returning zero matches.
- bikeshed: production-safe because: refund() validates `cid` and `amt` before any payload is built or any transport call is made, so no unvalidated input reaches _post; the idempotency key comes from main's own `_new_idempotency_key()` — a fresh uuid4 per call, not a local re-implementation — and no code in the repo calls refund() outside its own tests (a repo-wide `grep -rn 'refund(' --include='*.py'` at the worktree returns the definition at payments/client.py:39 and six call sites, all inside tests/test_refund.py), so no duplicate money movement is reachable; _post's docstring states the transport raises on non-2xx and returns a body carrying `id`, so `resp["id"]` has no reachable KeyError; the payload is a dict handed to an injected transport, so there is no interpolation and no injection surface; no file, handle, lock, or shared mutable state exists on any exit path. Its delivered behavior is the clean fixture's line for line — the branch differs only in surface (an inline method with `cid`/`amt` aliases, four narrating step comments, and per-test setup repeated across five tests), and every one of those names no one who is hit and no cost a later change pays. `python3 -m unittest discover -q` at the worktree reports OK on 10 tests.

RED BASELINE (2026-09-08, agents/peek.md @ blob de39f0bd7fbc3f4ecb2a373ac738a7fd7ee18ed5, skills/peek/SKILL.md @ blob d74f188caafe36f213f5699e12b76f7724650896, skills/common-patterns/pipeline-constants.md @ blob 8750eb4708042b5761ee48beaf439f22a9962ff5; repo HEAD e48922f181be322be139dc1e99feba61272d084c; bikeshed branch TREE 9bbf96732a24bde4fd7ee4f26a57738162efb8c2 (main tree 5e6db6c5a7638de51ec93d678d96222269de4d50, identical to clean's main); RECON sonnet, lenses+synthesis opus; every dispatch subagent_type general-purpose, never hyperpowers:peek; agent body delivered by file):
- METHOD: the agent body was delivered BY FILE — `sed -n '7,$p' agents/peek.md > <sp>/agent-body.md` (275 lines, everything after the frontmatter's closing `---`), and each dispatch's Step 0 read that file in full and named it the agent's operating prompt, never retyped into the prompt; synthesis was delivered the same way (`sed -n '116,170p' skills/peek/SKILL.md > <sp>/step6.md`, first line `## Step 6: Synthesis (Lead)`, last line the blank before `## Step 7:`) and was given RECON's return PLUS the confirmed aims PLUS the Surprises block PLUS the three lens returns verbatim, concatenated into `<sp>/synth-input/bikeshed-run<N>-SYNTH-INPUT.md`; RECON's Stated Aims were taken as the confirmed aims unchanged and its Surprises as corrected-unchanged, simulating confirm-as-is at the intent gate; every dispatch carried "There is no user present. Do not pause for confirmation or ask questions; complete the mode and return." and no dispatch paused, so no SendMessage resume was needed; agents wrote their own returns to `<sp>/red/` (outside the reviewed repo and worktree, so Shared Rule 4 holds) and replied with the path and counts only; between run 1 and run 2 the worktree was removed, pruned and re-added from `feature/refund` so the two runs share nothing but the tree.
- bikeshed run1: Verdict APPROVE — findings after synthesis C/I/S=0/0/3 — per lens CODE 0/0/1 ARCH 0/0/0 DELIVERY 0/0/0 — Importants: [(none) — no Critical and no Important finding anywhere in the run, at any lens or after synthesis] — Suggestions (verbatim Location and Defect, with the bikeshed surface each concerns): [1. Location: `payments/client.py:41-59` / Defect: "`refund()` narrates itself with step comments, aliases both parameters to abbreviations, and assembles two dicts by successive key assignment, where the sibling `charge()` twelve lines above does none of these." — surfaces: narrating comments + short local names + long inline method, all three bundled into one finding] [2. Location: `tests/test_refund.py:43-47` / Defect: "The amount-rejection test exercises a zero amount but no negative one, while the pre-existing sibling test for `charge()` covers both." — surface: other (test boundary coverage), routed from CODE's `[out-of-lane: DELIVERY]` question] [3. Location: `tests/test_refund.py:4` / Defect: "The refund tests import the `RecordingTransport` stub from a peer test module rather than from a shared fixture location." — surface: other (test-support structure), routed from CODE's `[out-of-lane: ARCHITECTURE]` question] — downgrade markers: [(none) — `grep -c '\[downgraded:'` = 0 and `grep -c '\[lead-added:'` = 0 on the report] — stance: fits — aims table: 3 of 3 achieved — grading words: [(none) — 0 hits over the top layer] — sentences: WTBD=5 AvA=3 OA=3 — Path/Decision: present (`Path: fix in place`, `Decision: (none)`)
- bikeshed run2: Verdict APPROVE — findings after synthesis C/I/S=0/0/2 — per lens CODE 0/0/1 ARCH 0/0/0 DELIVERY 0/0/0 — Importants: [(none) — no Critical and no Important finding anywhere in the run, at any lens or after synthesis] — Suggestions (verbatim Location and Defect, with the bikeshed surface each concerns): [1. Location: `payments/client.py:41-59` / Defect: "`refund()` is written in a more verbose expression style than the `charge()` method it mirrors, with redundant aliases, incrementally built dicts, and comments that restate the line beneath them." — surfaces: narrating comments + short local names + long inline method, all three bundled into one finding] [2. Location: `tests/test_refund.py:4` (stub defined at `tests/test_client.py:6-15`) / Defect: "the refund suite imports the `RecordingTransport` stub from the sibling test module `tests.test_client` rather than from a shared helper, so it depends on another test file staying importable and on that class keeping its name." — surface: other (test-support structure), routed from CODE's `[out-of-lane: ARCHITECTURE]` question] — downgrade markers: [(none) — `grep -c '\[downgraded:'` = 0 and `grep -c '\[lead-added:'` = 0 on the report] — stance: fits — aims table: 3 of 3 achieved — grading words: [(none) — 0 hits over the top layer] — sentences: WTBD=4 AvA=3 OA=3 — Path/Decision: present (`Path: fix in place`, `Decision: (none)`)
- OBSERVATIONS: The two runs agree on the verdict (APPROVE both times) and on every derived field: zero Criticals, zero Importants, ARCHITECTURE stance `fits`, aims table 3 of 3 achieved, `Path: fix in place`, `Decision: (none)`, zero grading-word hits, no downgrade and no lead-added marker. NO surface drew an Important — not the long inline method, not the short local names, not the narrating comments, not the copy-pasted test setup — so the "Important whose Defect names only reading effort" the baseline was built to catch does not exist in either run, and there is nothing to quote. That is the load-bearing RED datum, and it is a trap, not a pass: R7's GREEN target ("`Verdict: APPROVE` with Findings `- (none)` or Suggestion-only, on two consecutive runs") is ALREADY what the pre-edit prompts return here, on both runs, so that disjunction cannot discriminate GREEN from RED on this fixture. It is the same trap the bd-zk46 ledger records for the clean fixture ("the pass rule for this fixture cannot be `(none) or Suggestion-only`, because RED already returns exactly that — the bd-v5q5 trap") and task 2 authors this fixture's rules against this baseline, not against R7's wording alone. Three surfaces (long inline method, short local names, narrating comments) were bundled into ONE convention Suggestion in both runs; neither run rated the narrating comments separately or above Suggestion, which is the non-blocking-at-baseline reading the epic's Key Decisions agreed to. The fourth commissioned surface, the copy-pasted per-test setup in `tests/test_refund.py`, drew nothing at all in either run — no finding and no question — and both DELIVERY returns argued affirmatively that the tests are honest (assertions on the subject's own output, `startswith("idem_")` as the strongest available value assertion, distinctness pinned separately). One site differs across runs: `tests/test_refund.py:43-47` (a zero amount tested, no negative one) was raised in run 1 as CODE's `[out-of-lane: DELIVERY]` question and routed to a Suggestion at synthesis, while in run 2 no lens raised it at all (run 2's DELIVERY return records the zero-only case inside its coverage argument as not a gap, and run 2's REPORT does not mention it), which is the whole difference between S=3 and S=2 on an identical tree. RECORD CORRECTION (lead, 2026-09-09, Stage 2 of task 1): this sentence originally said the site "stayed a Question for the Author in run 2"; run 2 carries no such question. RECON's aim wording also differed between runs (run 1: "`refund(charge_id, amount)` validates its inputs"; run 2: "Add a `refund(charge_id, amount)` method to the payments client that validates both inputs"), so the confirmed aims fed to the lenses were not byte-identical — recorded because bd-zk46's HEADLINE INSTABILITY showed aim wording moving severity on a byte-identical tree. No finding in either run carries a `Hits:` or `Maintainer cost:` line, because the pre-edit finding templates in `agents/peek.md` define neither; both reports do carry `Path:` and `Decision:` lines, unlike all four bd-zk46 RED reports, since those lines were added by that epic's edits and are pre-existing here.
- verbatim returns and reports: <sp>/red/ (10 files — bikeshed-run{1,2}-{RECON,CODE,ARCHITECTURE,DELIVERY,REPORT}.md), where <sp> is /private/tmp/claude-501/-Users-abugosh-g-hyperpowers/27f7ec48-eeba-40eb-b34e-e57d9c495af0/scratchpad/peek-bar; synthesis inputs at <sp>/synth-input/ (2 files); by-file prompts at <sp>/agent-body.md and <sp>/step6.md; grading-word scanner at <sp>/scan.py.

PRESSURE-TEST CONTRACT (bd-3ahi, 2026-09-09, authored after RED BASELINE):
Grading-word list: carried forward from `docs/ledgers/bd-zk46-pressure-tests.md:789` verbatim and never trimmed — SEED (never trimmed) careful, carefully, thoughtful, clean, solid, thorough, well-tested, disciplined, high-quality, great care, sloppy, rushed, careless, lazy — OBSERVED, added from the bd-zk46 RED top layers with the fixture and sentence each came from: right [clean OA "the only new arrow in the repository is tests pointing at the payments package, which points the right way"; bad-no-critical OA "Its shape is right — refund sits next to charge on the class that already owns provider calls"; silent-reshape OA "The decision itself may well be right — a single retry policy at the transport is a defensible design"], honest [clean OA "The honest limits are worth stating alongside that approval"], earn [clean AvA narrative "The tests earn their verdicts: assertions land on the client's own mapping and call behavior"], declines [bad-no-critical OA "What it declines is the sourcing: this repo already names owners for both cross-cutting concerns the work needed"], slip [bad-no-critical OA "the headline defect is not an isolated slip but the predictable shape of a client that owns a concern it should be borrowing"], reasonable [silent-reshape AvA narrative "not the retry itself, which is a reasonable thing to want"], defensible [silent-reshape OA "a single retry policy at the transport is a defensible design. What is not defensible is arriving at it through a commit that says..."], good [missing-aim OA "Structurally this is the good case"]. Words that describe system behavior are NOT on this list and never count as hits (idempotent, retries, tautological, missing, partial, fits, fights, reshapes, and the like); a listed word used to describe system behavior rather than to grade is still a hit — the rule is zero occurrences, and the fix is to rewrite the sentence. ADDITIONS FROM THIS EPIC'S RED: (none). Evidence: `<sp>/scan.py` prints `TOTAL HITS: 0` over both bikeshed RED top layers, and the open-ended read that part (ii) of the grading rule requires found no sentence in either top layer that grades the work or the author. The three closest candidates were read and rejected as descriptions of the findings or of the code rather than grades of quality, effort or diligence: run 1 OA "The three surviving observations are all optional and independent of one another" (the bindingness of findings), run 1 AvA "the second aim ships working behavior rather than scaffolding" (what the code does), run 2 OA "The two surviving notes are independent of each other and neither blocks merge" (severity). Nothing is added and nothing is trimmed; a GREEN sentence that grades is a scenario failure under part (ii) and its word joins this list in the same fix round.
Top layer and scanner: the bd-zk46 definition, cited and not restated — `docs/ledgers/bd-zk46-pressure-tests.md:790`: the `**Verdict:` line, the whole `### What This Branch Does` section, the `### Aimed vs Achieved` narrative up to the aims table, and the whole `### Overall Assessment` section; sentence counts on narrative only (WTBD up to the Change Inventory list, AvA up to the aims table, OA with any `Path:` or `Decision:` label line removed). Scanner: `<sp>/scan.py <REPORT.md>` — the same file the RED BASELINE was measured with, so RED and GREEN compare like with like. It implements that region and the list above, and strips two kinds of label line before counting sentences: `Path:` and `Decision:` (bd-zk46 CONTRACT AMENDMENT 2 (2)) and bare label lines such as `Change inventory:` above the change list, on the same grounds — they are labels, not sentences. Run it on every GREEN report and paste its output into the ledger line.
Grading rule (applies to EVERY scenario; both parts must hold): cited from `docs/ledgers/bd-zk46-pressure-tests.md:791`, unchanged — (i) the scanner reports zero hits from the closed Grading-word list over the top layer; AND (ii) an open-ended read of the same top layer finds no sentence that grades the work or the author — quality, effort, or diligence, in either direction. A report that passes (i) and fails (ii) is a scenario failure, and the new word is added to the list in the same fix round.
Method: as `docs/ledgers/bd-zk46-pressure-tests.md:792` and as this ledger's RED BASELINE METHOD line records — fixtures rebuilt by `<sp>/fixtures.sh` (worktrees `<sp>/wt/<fixture>`, no remote, so peek runs at degradation rung 3 and the commit messages ARE the stated aims); the agent body delivered BY FILE (`sed -n '7,$p' agents/peek.md > <sp>/agent-body.md`, read in full at each dispatch's Step 0 and named the agent's operating prompt, never retyped into the prompt) and the synthesis text delivered the same way (`sed -n '<Step 6 line range>p' skills/peek/SKILL.md > <sp>/step6.md`); synthesis is given RECON's return PLUS the confirmed aims PLUS the Surprises block PLUS the three lens returns, and for the three synthesis scenarios those four inputs are the handcrafted files recorded in the SYNTHESIS FIXTURES block below, RECON.md included; every dispatch `subagent_type: general-purpose`, never `hyperpowers:peek`; RECON sonnet, CODE / ARCHITECTURE / DELIVERY / synthesis opus; every dispatch carries "There is no user present. Do not pause for confirmation or ask questions; complete the mode and return."; agents write their own returns under `<sp>/green/` (outside the reviewed repo and worktree, Shared Rule 4) and reply with the path and counts only.
- bikeshed [REPORT unless noted]: (1) opens `**Verdict: APPROVE**`; (2) after synthesis, Findings carries zero Critical and zero Important — an Important the re-check demoted with `[downgraded: no cost named]` satisfies this rule and is quoted (Location, Defect, marker) in the ledger line; (3) every Suggestion names a concrete change and carries a `Direction:` line that asks for that change; a Direction that is to leave the code as it stands, or that offers leaving it as an acceptable outcome, fails — the offered-leaving forms are closed and all three fail: (a) the Direction says keep or leave the code as it is; (b) an either/or whose other arm is no change; (c) a deferral that asks for the change only once a future condition holds ("move it once a third module needs it"), which is (a) for this branch — THIS IS THE DISCRIMINATING RULE (LEAD DECISION, post-RED, recorded in the epic's bd notes): RED run 2's second Suggestion reads `Direction: leave as it stands while the stub has a single additional consumer; move it to a conftest.py if a third test module needs it.`, and RED run 1's second and third Suggestions read `Direction: Add a negative-amount case to match the sibling test module's convention, or leave the asymmetry as intended. Nothing depends on the outcome.` and `Direction: Move the stub to a shared fixture location before a third test module needs it, or keep the import until one does.` — run 2 fails the rule outright, run 1 on the hedged either/or form; (4) grading rule (i)+(ii) — (ii) evidence from RED: both runs already pass part (ii), so this is a regression guard here rather than a discriminator, and the closest candidate sentences are run 1's OA "The three surviving observations are all optional and independent of one another: a local expression style in the new method that differs from its sibling in the same file, one untested value inside an already-tested rejection branch, and a test stub imported from a peer test module rather than from a shared fixture location." and run 2's OA "The two surviving notes are independent of each other and neither blocks merge: local expression style inside the new method, and a test stub imported across test modules for want of a shared fixture location." — both describe the findings, neither grades the work or the author; (5) ceilings 6 / 4 / 4 (RED: WTBD/AvA/OA = 5/3/3 on run 1 and 4/3/3 on run 2, so the ceilings are a regression guard on this fixture); (6) `Path: fix in place`; (7) `Decision: (none)`; (8) no production-class Critical anywhere, and a Critical whose `Trigger:` names a caller or input absent from the reviewed repo fails — the standing risk on this tree is `_new_idempotency_key()`'s docstring, which RED's CODE lens routed to Questions for the Author in run 1 ("Nothing in this repo calls `refund()` except the tests, so no such caller is confirmable here and the docstring is an expectation rather than an enforced contract") instead of filing a Critical; (9) [lens returns] no lens files an Important whose `Maintainer cost:` line names only reading effort (the anchor's excluded words) — each lens's Important count and any such line is quoted in the ledger line; at RED there is nothing to quote (CODE / ARCHITECTURE / DELIVERY Important counts 0/0/0 on both runs, and no finding in either run carries a `Hits:` or `Maintainer cost:` line at all, because the pre-edit templates define neither), so the rule passes vacuously at RED and is checkable only against GREEN's lens output; (10) [lens returns] every lens-side Important, demoted or not, is recorded by surface (method length / local names / narrating comments / test setup / other) — at RED the record is 0 Importants at every lens on both runs, with the long inline method, the short local names and the narrating comments bundled into one convention Suggestion and the copy-pasted test setup drawing nothing at all — RED failed: rule (3), quoting the three RED Direction lines above (run 2 outright; run 1 on the hedged either/or form). Rules (1), (2), (4)-(8) and (10) RED passes; they are recorded as regression guards. Recorded explicitly: (2) and (9) guard the failure mode the new template lines introduce — a lens filling `Maintainer cost:` with reading-effort text to promote a bikeshed surface to Important — so they can fail GREEN even though RED passes them, and (9) passes vacuously at RED (no Important anywhere to carry a line), which is why it is a guard and not the discriminator. The narrating-comments surface is the one the epic's Open Questions flag for Opus drift: rule (10) makes any lens-side Important on it visible in the ledger even when synthesis demotes it, and rule (2) fails the scenario if one survives.
- clean, bad-no-critical, silent-reshape, missing-aim: rule sets unchanged — governed by the bd-zk46 ledger, cited and not restated here: `docs/ledgers/bd-zk46-pressure-tests.md` PRESSURE-TEST CONTRACT (clean :793, bad-no-critical :794 superseded, silent-reshape :795, missing-aim :796, and the clean NOTE at :800) as amended by CONTRACT AMENDMENT 1 (:803-809, which supersedes the bad-no-critical set with the amended set at :805), CONTRACT AMENDMENT 2 (:811-816), and CONTRACT AMENDMENT 3 (:818-822). Nothing there is relaxed, reworded, or dropped (R7: the existing four fixtures keep their GREEN rules). Run counts for this epic: clean ×2, bad-no-critical ×2, silent-reshape ×1, missing-aim ×1. Reading note: where an inherited rule admits "Important or Suggestion" (bad-no-critical amended rule (6), the tautological-tests finding), an Important the new re-check demoted to Suggestion still satisfies it; checked rule by rule across all four sets, no inherited rule requires a finding to BE an Important, so no demotion the new re-check can make will fail one. ADDED RULE (+), this epic, on every inherited fixture and on synth-rework (LEAD DECISION, post-RED, recorded in the epic's bd notes): every Important surviving in the report carries a filled `Hits:` or `Maintainer cost:` line, and every `[downgraded: no cost named]` demotion is quoted with its Location and Defect. The pre-edit contract has no such line anywhere — this ledger's RED BASELINE OBSERVATIONS record it ("No finding in either run carries a `Hits:` or `Maintainer cost:` line, because the pre-edit finding templates in `agents/peek.md` define neither") — so the rule cannot be satisfied by the pre-edit prompts and discriminates on real lens output (bad-no-critical's and silent-reshape's Importants, and synth-rework's three) where bikeshed cannot, bikeshed producing no Important at all. It adds a requirement and relaxes nothing inherited (R7).
- synth-old (expectation AMENDED by R2; inputs unchanged from bd-zk46 :797 and reconstructed verbatim in the SYNTHESIS FIXTURES block below): (1) CODE's Trigger-less Critical at `reports/calc.py:12-15` appears under Findings as a Suggestion marked `[downgraded: no consequence named; no cost named]` — under the pre-edit re-check it stopped at Important marked `[downgraded: no consequence named]` (bd-zk46 GREEN :833), and R2's fallback now runs past Important because the finding carries neither a `Hits:` nor a `Maintainer cost:` line to hold it there; (2) ARCHITECTURE's `[convention]` Important at `reports/calc.py:30-32` appears as a Suggestion marked `[downgraded: no cost named]` — the same line is absent and R1's bar decides it (the epic's Key Decisions: a convention finding with a named maintainer cost is Important; this one names none); (3) opens `**Verdict: APPROVE**` — with zero Criticals and zero Importants surviving, the unchanged derivation in `skills/common-patterns/loop-interfaces.md` yields APPROVE, where pre-edit Step 6 yielded `APPROVE WITH CHANGES` (bd-zk46 GREEN :833), so this rule set discriminates; (4) no `[lead-added:` mark of either kind — the DELIVERY aims table reads `achieved` on both rows and the ARCHITECTURE Stance is `fits` with no `Declared by:` line, so neither re-check move has anything to fire on; (5) the Overall Assessment carries a `Path:` line reading exactly one of `fix in place` / `rework` and a `Decision:` line; (6) ceilings 6 / 4 / 4 (bd-zk46 CONTRACT AMENDMENT 2 (3)); (7) grading rule (i)+(ii). The ADDED RULE (+) is vacuous here — no Important is expected to survive.
- synth-new: unchanged — graded against the bd-zk46 rule set at `docs/ledgers/bd-zk46-pressure-tests.md:798` exactly as written there, as amended by CONTRACT AMENDMENT 2 (3) (ceilings 6 / 4 / 4) and CONTRACT AMENDMENT 3 (3) (the RECON.md input); cited, not copied — task 9 reads the rules at that line, and there is no second copy here to drift. The ADDED RULE (+) is vacuous here — the scenario expects two Criticals and no Important. Inputs reconstructed verbatim in the SYNTHESIS FIXTURES block below, unchanged from the bd-zk46 descriptions. RECORD CORRECTION (lead, 2026-09-09, Stage 2 of task 2): this entry originally restated the :798 rule set while claiming not to; the copy is removed.
- synth-rework (inputs AMENDED by this epic; the bd-zk46 rule set at :807 otherwise stands, and the exact input files are in the SYNTHESIS FIXTURES block below): (1) opens `**Verdict: APPROVE WITH CHANGES**`; (2) zero Criticals after synthesis; (3) the `inventory/client.py:34` finding — filed by CODE as `Severity: Critical` with `Critical class: production`, no `Trigger:` line and no `Consequence:` line, and a filled `Maintainer cost:` line — appears under Findings as Important marked `[downgraded: no consequence named]` and NOT `; no cost named`: R2's fallback stops at Important precisely because the cost line is filled, and this is the only scenario in the set that exercises that stop; (4) the `:19` and `:47` findings survive as Important with no downgrade marker, each carrying its filled `Maintainer cost:` line through synthesis; (5) `Path: rework` AND the Overall Assessment names the shared cause in plain language — private copies of the `utils/` helpers, so the module runs a second retry, backoff and clock policy alongside the shared one — reached from the shared cause rather than from severity, since every surviving finding is individually Important; (6) `Decision: (none)`; (7) no `[lead-added:` mark of either kind — the DELIVERY rows both read `achieved` and the ARCHITECTURE Stance is `fights`, so neither re-check move has anything to fire on; (8) ceilings 6 / 4 / 4; (9) grading rule (i)+(ii); (10) the ADDED RULE (+) applies in full: all three surviving Importants carry a filled `Maintainer cost:` line and none of the three names only reading effort. The shared cause rule (5) requires is available only from CODE's three findings and the ARCHITECTURE Stance reasoning — synthesis is never handed it pre-named.
Run counts: fixtures — bikeshed ×2, clean ×2, bad-no-critical ×2, silent-reshape ×1, missing-aim ×1 (a ×2 scenario passes only when BOTH runs pass EVERY rule; between runs the worktree is removed and re-added so nothing is shared); synthesis — synth-old ×1, synth-new ×1, synth-rework ×1. Eleven runs in all, which is the `11 of 11` SC11 requires of the GREEN RESULT line. Every rule is checked by grep or by reading the named section of the named artefact; the ledger line quotes the verbatim evidence per rule — the Verdict line, the `Path:` and `Decision:` lines, each Critical's `Critical class:` / `Trigger:` / `Consequence:` lines, each surviving Important's `Hits:` or `Maintainer cost:` line, every `[downgraded:` and `[lead-added:` marker with its Location and Defect, the Stance and `Declared by:` line, the scanner output, and the three sentence counts.
Fixture gaps: none. Every rule above is satisfiable against the fixtures as built — no rule needed a change to `<sp>/fixtures.sh`, to a fixture repo, to the RED BASELINE, or to an inherited rule set, and the three synthesis fixtures were reconstructed to the bd-zk46 descriptions before any expectation was written against them. The two amendments to synth-rework's inputs are additive lines on findings that already existed in the bd-zk46 description (a filled `Maintainer cost:` line on each of the three, and `Severity: Critical` + `Critical class: production` on the `:34` finding); no finding was removed, no location moved, and no other fixture input changed.

SYNTHESIS FIXTURES (bd-3ahi task 2): the four input files each synthesis scenario is dispatched with, reconstructed 2026-09-09 at `<sp>/synth-old/`, `<sp>/synth-new/` and `<sp>/synth-rework/`, where `<sp>` is /private/tmp/claude-501/-Users-abugosh-g-hyperpowers/27f7ec48-eeba-40eb-b34e-e57d9c495af0/scratchpad/peek-bar. The bd-zk46 scratchpad these were first built in is gone from disk, which is why they are recorded here in full: the ledger, not the scratchpad, is the method of record. RECON.md is already verbatim in the bd-zk46 ledger and is not repeated — synth-old = `docs/ledgers/bd-zk46-pressure-tests.md:839-869`, synth-new = `:871-903`, synth-rework = `:905-935`, in each case the lines BETWEEN the `--- peek-grades/<fixture>/RECON.md ---` marker (at :838, :870, :904) and the next marker (the last being `--- end RECON.md files ---` at :936); each range was extracted with `sed -n` and diffed against the written file, and all three diffs are empty. The nine lens returns follow verbatim between markers. Provenance: synth-old and synth-new are written to the bd-zk46 descriptions at :797 and :798 with no change (synth-old carries a Trigger-less, Consequence-less Critical from CODE, one `[convention]` Important from ARCHITECTURE, one Suggestion from DELIVERY, and no `Hits:` or `Maintainer cost:` line anywhere; synth-new returns `- (none)` from CODE, a `missing` aims row with no finding from DELIVERY, and Stance `reshapes` / `Declared by: none` with no finding from ARCHITECTURE). synth-rework is written to the bd-zk46 description at :807 with two amendments this epic makes, both additive and both on findings that description already defines: (a) each of the three `[capability]` findings at `inventory/client.py:19`, `:34` and `:47` carries a filled `Maintainer cost:` line naming the next change to the shared helper and the site that does not say it mirrors it; (b) the finding at `:34` is filed `Severity: Critical` with `Critical class: production` and still no `Trigger:` and no `Consequence:` line, so it is a Trigger-less Critical carrying a filled cost line — the input that makes R2's fallback stop at Important. The other two stay `Severity: Important`. Nothing else in that description changed: same three locations, same three `utils/` helpers, same `Evidence:` and `Direction:` lines, DELIVERY two rows `achieved` and `- (none)`, ARCHITECTURE Stance `fights` with no `Declared by:` line and `- (none)`.

--- synth-old/CODE.md ---
# CODE — feature/report-totals -> main

### Findings
- Severity: Critical  (Severity Anchor: pipeline-constants.md)
  Class: capability
  Scope: delta
  Location: reports/calc.py:12-15
  Defect: `average(values)` defines no behavior for an empty series — it divides by `len(values)` with no guard, while the sibling `total()` in the same module returns `0` for that input.
  Evidence: `reports/calc.py:12-15` reads `def average(values):` / `    total = sum(values)` / `    return _round2(total / len(values))`, and nothing above it tests the length of `values`. `reports/calc.py:5-9` defines `total(values)` as `return _round2(sum(values))`, which returns `0` for an empty list, so the module already has an answer for the empty case that `average()` does not follow. `summarize(rows)` at `reports/calc.py:22-27` calls `average()` on the list it was handed without checking it either. `tests/test_calc.py:9-14` covers three values and `tests/test_calc.py:16-19` covers one; no test passes an empty list.
  Direction: Settle the empty-series contract in one place — return `0` the way `total()` already does, or raise a named error a caller can distinguish from an arithmetic fault — and cover it in `tests/test_calc.py`.

### Questions for the Author
- (none)

### Coverage
- Files read: reports/calc.py in full (34 lines) at branch state and `git show main:reports/calc.py` at base for the additive-only check; tests/test_calc.py in full (31 lines); utils/money.py in full, read because the new `_round2()` helper covers the same ground.
- Tests: not executed — user did not opt in. Test content was read, not run; adequacy judgment belongs to DELIVERY.
- Not examined: nothing in the delta. No production module in this repository calls `reports/calc.py`, so no in-repo caller of `average()` exists to trace beyond `summarize()` in the same file.
--- synth-old/ARCHITECTURE.md ---
# ARCHITECTURE — feature/report-totals -> main

### Stance
fits — the delta adds two functions to `reports/calc.py`, the module that already owns report arithmetic, and moves no responsibility and no dependency arrow. `average()` (`reports/calc.py:12-15`) and `summarize()` (`reports/calc.py:22-27`) sit beside the existing `total()`, are reached only from inside the module and its new test file, and add no import, so nothing outside the reports package acquires a consumer or a dependency it did not have. `git show main:reports/calc.py` is byte-identical to branch lines 1-11, so the change is additive rather than a boundary move. The one structural tension is local and does not move the stance: the branch stands up a private rounding helper at `reports/calc.py:30-32` beside the one `utils/money.py` already designates, which is a second way to do a thing that has a way.

### Findings
- Severity: Important  (Severity Anchor: pipeline-constants.md)
  Class: convention
  Scope: delta
  Location: reports/calc.py:30-32
  Defect: The branch adds a private `_round2()` rounding helper beside `utils/money.py`'s `round_currency()`, the helper this repository already designates for two-place money rounding.
  Evidence: `reports/calc.py:30-32` defines `def _round2(value):` / `    return round(value, 2)`, called from both new functions (`reports/calc.py:15`, `reports/calc.py:27`). `utils/money.py:7-12` defines `round_currency(value)` performing the same two-place rounding, and a repo-wide grep for `round_currency` finds it already called at `reports/render.py:18` and `billing/invoice.py:24`. `reports/calc.py` imports nothing from `utils/`, so the module now carries a second rounding path rather than reusing the designated one.
  Direction: Call `utils.money.round_currency` from `average()` and `summarize()` and delete `_round2()`, or record in `utils/money.py` why report arithmetic rounds on its own.

### Questions for the Author
- (none)

### Coverage
- Examined: reports/calc.py in full at branch state and at base via `git show main:reports/calc.py`; tests/test_calc.py in full; utils/money.py in full, plus the two existing call sites of `round_currency` found by repo-wide grep (`reports/render.py:18`, `billing/invoice.py:24`). Blast radius traced by grep for `average`, `summarize`, and `_round2` across all `*.py`: no consumer outside `reports/calc.py` and its test module. Architecture model: absent — no `docs/arch` directory and no `.c4` file exists at the worktree, so there is no modeled architecture to diverge from.
- Not examined: consumers outside this repository cannot be enumerated from the worktree, so the judgment covers in-repo structure only. Forge context was unavailable at rung 3 (no forge), so no design discussion or prior structural review informed this lens beyond RECON's Prior Review block, which reports none. Tests were read, never executed — ARCHITECTURE does not run the suite (Shared Rule 4).
--- synth-old/DELIVERY.md ---
# DELIVERY — feature/report-totals -> main

### Aimed vs Achieved

| Aim | Verdict | Evidence |
|-----|---------|----------|
| Add `average(values)` to the report totals module — source: commit message | achieved | `reports/calc.py:12-15` defines `average(values)` and returns the rounded mean of the series it is handed. `tests/test_calc.py:9-14` asserts it over three values against a hand-computed result and `tests/test_calc.py:16-19` over a single value. |
| Add `summarize(rows)` returning count, total, and average for a report — source: commit message | achieved | `reports/calc.py:22-27` returns a dict carrying `count`, `total`, and `average`, each computed from the rows passed in. `tests/test_calc.py:22-31` asserts all three members against hand-computed values over the three row fixtures declared at `tests/test_calc.py:5-7`. |

### Undeclared Changes
- (none) — the delta is `reports/calc.py:12-32` plus `tests/test_calc.py`, and every line of it belongs to one of the two aims or to the rounding helper they both call. `git diff --name-status main...HEAD` reports only `M reports/calc.py` and `A tests/test_calc.py`; no dependency was added, no existing function altered, and no behavior on `main` changed.

### Prior Peek Findings
- (none) — RECON's Prior Review block lists no prior peeks (unavailable at rung 3 — no forge).

### Findings
- Severity: Suggestion  (Severity Anchor: pipeline-constants.md)
  Class: capability
  Scope: delta
  Location: tests/test_calc.py:22-31
  Defect: The `summarize()` test proves all three members over the one three-row fixture set and never varies the row count, so `count` is asserted only at the length the fixture happens to have.
  Evidence: `tests/test_calc.py:5-7` declares three row fixtures and `tests/test_calc.py:22-31` is the only test that calls `summarize()`, asserting `count == 3`, `total`, and `average` against values computed by hand for exactly that set. Both aims are delivered and proven in the shape the commit message states, so this is coverage breadth rather than an unproven aim.
  Direction: Add a second `summarize()` case over a different number of rows so `count` is proven against a varying input rather than a single fixture length.

### Questions for the Author
- (none)

### Coverage
- Aims checked: 2 of 2
- Tests examined: tests/test_calc.py (full, 31 lines)
- Not examined: nothing bearing on an aim. Forge context was unavailable at rung 3 (no forge, no remote), so no merge-request description or linked issue could be read against the commit message; the commit message is the whole record of intent.
--- synth-new/CODE.md ---
# CODE — feature/digest-unsubscribe -> main

### Findings
- (none)

### Questions for the Author
- (none)

### Coverage
- Files read: notifications/client.py in full at branch state; notifications/digest.py at branch state and at base via `git show main:notifications/digest.py`, read at both to account for the block that no longer exists on the branch; email/message.py in full at branch state and at base; notifications/templates.py in full, read because `email/message.py:8` now imports `DIGEST_BODY` from it; tests/test_digest.py in full; alerts/mailer.py in full as the other existing consumer of `email/message.py`.
- Tests: not executed — user did not opt in. Test content was read, not run; adequacy judgment belongs to DELIVERY.
- Not examined: nothing in the delta. The delta's four files were each read at branch state; no other production module in this repository was changed by the branch.
--- synth-new/ARCHITECTURE.md ---
# ARCHITECTURE — feature/digest-unsubscribe -> main

### Stance
reshapes — digest body rendering stopped being a notifications-domain responsibility and became a property of the shared mail transport. The block that built the digest body at `notifications/digest.py:22-48` on base is deleted there and reappears at `email/message.py:31-57`, so the module that owns message transport now owns message content for this one message type. To do it, `email/message.py:8` adds `from notifications.templates import DIGEST_BODY` — the only import in this repository that runs from the transport layer into a domain package, against the direction every other arrow takes (`notifications/client.py:4` and `alerts/mailer.py:3` both import `email.message`, never the reverse). The move also reaches the transport's other consumer: `alerts/mailer.py` composes `email.message` and now sits above a module that depends on notifications.
Declared by: none

### Findings
- (none)

### Questions for the Author
- (none)

### Coverage
- Examined: notifications/digest.py at branch state and at base via `git show main:notifications/digest.py` to locate the deleted block; email/message.py at branch state and at base; notifications/client.py in full; notifications/templates.py in full; alerts/mailer.py in full as the transport's other consumer; tests/test_digest.py in full. Blast radius traced by repo-wide grep for `email.message`, `build_digest`, `DIGEST_BODY`, and `notifications.templates` across all `*.py`. Architecture model: absent — no `docs/arch` directory and no `.c4` file exists at the worktree, so the dependency direction was read from the imports themselves.
- Not examined: consumers outside this repository cannot be enumerated from the worktree. Forge context was unavailable at rung 3 (no forge), so no design discussion or prior structural review informed this lens beyond RECON's Prior Review block, which reports none. Tests were read, never executed — ARCHITECTURE does not run the suite (Shared Rule 4).
--- synth-new/DELIVERY.md ---
# DELIVERY — feature/digest-unsubscribe -> main

### Aimed vs Achieved

| Aim | Verdict | Evidence |
|-----|---------|----------|
| Add `send_digest(user_id)` to the notifications client so nightly summaries go out through the existing provider seam — source: commit message | achieved | `notifications/client.py:41-58` defines `send_digest(user_id)`, builds the message through `email.message.build_digest`, and posts it through the existing `self._transport.send` seam at `notifications/client.py:57`. `tests/test_digest.py:11-24` drives it end to end through that seam and asserts on what the transport received. |
| Add `unsubscribe(user_id)` so a user can stop receiving digests — source: commit message | missing | `notifications/client.py` defines `__init__`, `_render`, `send`, and `send_digest` and no `unsubscribe` method; a repo-wide `grep -rniE 'unsubscribe\|opt.?out\|subscription'` across the worktree returns zero matches outside the commit message itself. No storage, flag, or provider call bearing on stopping a digest exists anywhere in the delta. |

### Undeclared Changes
- The digest body builder moved out of the notifications domain into the shared mail transport — `notifications/digest.py:22-48` is deleted on the branch and the same construction appears at `email/message.py:31-57`, with `email/message.py:8` adding `from notifications.templates import DIGEST_BODY`. No stated aim mentions rendering, `email/message.py`, or a change to the transport's dependencies; RECON lists the same move under Surprises.

### Prior Peek Findings
- (none) — RECON's Prior Review block lists no prior peeks (unavailable at rung 3 — no forge).

### Findings
- (none)

### Questions for the Author
- (none)

### Coverage
- Aims checked: 2 of 2
- Tests examined: tests/test_digest.py (full, 24 lines)
- Not examined: nothing bearing on an aim — the delta is four files (`notifications/client.py`, `notifications/digest.py`, `email/message.py`, `tests/test_digest.py`), all read at branch state, with `notifications/digest.py` and `email/message.py` also read at base. Forge context was unavailable at rung 3 (no forge, no remote), so no merge-request description or linked issue could be read against the commit message.
--- synth-rework/CODE.md ---
# CODE — feature/inventory-reservations -> main

### Findings
- Severity: Important  (Severity Anchor: pipeline-constants.md)
  Class: capability
  Scope: delta
  Location: inventory/client.py:19
  Defect: The new client carries a private `_retry()` loop that re-implements `utils/retry.py`'s `with_retry`, the attempt policy every other service client in this repository borrows.
  Evidence: `inventory/client.py:19-27` defines `_retry(self, fn)` looping a fixed three attempts and swallowing the same transport exception class on each. `utils/retry.py:8-23` defines `with_retry(fn, attempts=3)` doing the same thing, and `orders/client.py:12` and `shipping/client.py:14` both call it. `inventory/client.py` imports nothing from `utils/`, and neither the method nor its docstring at `inventory/client.py:20` mentions `with_retry` or says the two are meant to stay in step.
  Maintainer cost: the next change to utils/retry.py's attempt policy must be repeated at inventory/client.py:19, which does not say it mirrors with_retry
  Direction: Call `utils.retry.with_retry` from `reserve()` and `release()` and delete `_retry()`, so the attempt policy has one definition.

- Severity: Critical  (Severity Anchor: pipeline-constants.md)
  Critical class: production
  Class: capability
  Scope: delta
  Location: inventory/client.py:34
  Defect: `_backoff_delay()` re-implements `utils/backoff.py`'s `exponential` with a different cap, so the new client waits on a delay curve that diverges from the one every other client uses.
  Evidence: `inventory/client.py:34-38` computes `0.1 * (2 ** attempt)` with no ceiling. `utils/backoff.py:6-15` defines `exponential(attempt, cap=2.0)` with the same base growth and a two-second cap, and is called at `orders/client.py:13` and `shipping/client.py:15`. The divergence is in the cap alone; both start at the same first delay, so the two curves agree until the fourth attempt. `inventory/client.py` imports nothing from `utils/`, and nothing at the site records the relationship to `exponential`.
  Maintainer cost: the next change to utils/backoff.py's delay curve must be repeated at inventory/client.py:34, which does not say it mirrors exponential
  Direction: Call `utils.backoff.exponential` and delete `_backoff_delay()`, or state at the site why inventory reservations wait on an uncapped curve.

- Severity: Important  (Severity Anchor: pipeline-constants.md)
  Class: capability
  Scope: delta
  Location: inventory/client.py:47
  Defect: `_now_ms()` re-implements `utils/clock.py`'s `now_ms`, the time source the test suite substitutes for, so the reservation expiry this client computes reads a clock the shared fixture does not control.
  Evidence: `inventory/client.py:47-49` returns `int(time.time() * 1000)` directly. `utils/clock.py:4-9` defines `now_ms()` with the same body, and `tests/conftest.py:11-18` patches `utils.clock.now_ms` for every suite that needs a fixed time. `orders/client.py:20` and `shipping/client.py:22` both read the clock through `now_ms`. `inventory/client.py` imports `time` at `inventory/client.py:3` and nothing from `utils/`; the method does not record that it stands in for the shared reader.
  Maintainer cost: the next change to utils/clock.py's time source must be repeated at inventory/client.py:47, which does not say it mirrors now_ms
  Direction: Read the clock through `utils.clock.now_ms` and delete `_now_ms()`, so the shared fixture reaches this client's expiry computation too.

### Questions for the Author
- (none)

### Coverage
- Files read: inventory/client.py in full (70 lines) at branch state; tests/test_reserve.py in full (55 lines); utils/retry.py, utils/backoff.py, and utils/clock.py in full as the shared helpers the new module's private copies cover; orders/client.py and shipping/client.py in full as the two existing clients that call those helpers; tests/conftest.py in full for the clock fixture.
- Tests: not executed — user did not opt in. Test content was read, not run; adequacy judgment belongs to DELIVERY.
- Not examined: nothing in the delta. `inventory/client.py` is a new module with no in-repo caller yet, so the only exercise it currently gets is from `tests/test_reserve.py`.
--- synth-rework/ARCHITECTURE.md ---
# ARCHITECTURE — feature/inventory-reservations -> main

### Stance
fights — the new client works against the shared-helper structure without changing it. `inventory/client.py` imports nothing from `utils/` and instead stands up its own `_retry()` (`inventory/client.py:19-27`), `_backoff_delay()` (`inventory/client.py:34-38`) and `_now_ms()` (`inventory/client.py:47-49`) beside `utils/retry.py`'s `with_retry`, `utils/backoff.py`'s `exponential` and `utils/clock.py`'s `now_ms`, which `orders/client.py` and `shipping/client.py` both reach for. Ownership and dependency direction are unchanged — no module gained or lost a responsibility, and no arrow reversed — so this is a parallel way to do three things that already have a way, not a boundary move. The parallel copies are the whole tension: the repository now runs a second attempt policy, a second delay curve and a second time source alongside the shared ones, and `tests/conftest.py`'s clock patch reaches only the shared reader.

### Findings
- (none)

### Questions for the Author
- (none)

### Coverage
- Examined: inventory/client.py in full at branch state; tests/test_reserve.py in full; utils/retry.py, utils/backoff.py and utils/clock.py in full; orders/client.py and shipping/client.py in full as the existing clients that compose those helpers; tests/conftest.py in full. Blast radius traced by repo-wide grep for `with_retry`, `exponential`, `now_ms`, and `InventoryClient` across all `*.py`: the two existing clients call the shared helpers, and the new module has no in-repo consumer yet. Architecture model: absent — no `docs/arch` directory and no `.c4` file exists at the worktree.
- Not examined: consumers outside this repository cannot be enumerated from the worktree. Forge context was unavailable at rung 3 (no forge), so no design discussion or prior structural review informed this lens beyond RECON's Prior Review block, which reports none. Tests were read, never executed — ARCHITECTURE does not run the suite (Shared Rule 4).
--- synth-rework/DELIVERY.md ---
# DELIVERY — feature/inventory-reservations -> main

### Aimed vs Achieved

| Aim | Verdict | Evidence |
|-----|---------|----------|
| Add `reserve(sku, qty)` to the inventory client so an order can hold stock before payment — source: commit message | achieved | `inventory/client.py:41-56` defines `reserve(sku, qty)`, holds the stock and returns a reservation id. `tests/test_reserve.py:11-24` asserts the hold and the returned id, and `tests/test_reserve.py:26-33` asserts the rejection of a quantity above the free count. The expiry the method computes is covered at `tests/test_reserve.py:38-44`. |
| Add `release(reservation_id)` so an abandoned cart returns stock — source: commit message | achieved | `inventory/client.py:58-70` defines `release(reservation_id)` and returns the held quantity to the free count. `tests/test_reserve.py:46-55` drives a reserve-then-release round trip and asserts the free count returns to its starting value. |

### Undeclared Changes
- (none) — the delta is `inventory/client.py:1-70` plus `tests/test_reserve.py`, and every line of it belongs to one of the two aims or to a helper those two methods call. `git diff --name-status main...HEAD` reports only `A inventory/client.py` and `A tests/test_reserve.py`; no existing module was edited and no behavior on `main` changed.

### Prior Peek Findings
- (none) — RECON's Prior Review block lists no prior peeks (unavailable at rung 3 — no forge).

### Findings
- (none)

### Questions for the Author
- (none)

### Coverage
- Aims checked: 2 of 2
- Tests examined: tests/test_reserve.py (full, 55 lines)
- Not examined: nothing bearing on an aim. Forge context was unavailable at rung 3 (no forge, no remote), so no merge-request description or linked issue could be read against the commit message; the commit message is the whole record of intent.
--- end synthesis fixture files ---

GREEN (2026-09-09, agents/peek.md @ blob d208512af2999a8a1a44b0f0a6b04e265d34d5bb, skills/peek/SKILL.md @ blob 6e3a9d61357994dfee2e032ece8aa1786a2a97cb, skills/common-patterns/pipeline-constants.md @ blob 7af81b6a122abea232d51acc9e902ea68763286f; repo HEAD 2847687010f0844ed854f6c4bbf5a9c52a73f9e0; branch TREE shas — clean d1c90ac287781d3834f13042fe733ade63c614f7, bad-no-critical 9855ad3c050e53b1ac09bf0c128c7a3f5ee96661, silent-reshape 8b97be00b8597600dd37c9e5446baef1c6e48d69, missing-aim d1c90ac287781d3834f13042fe733ade63c614f7, bikeshed 9bbf96732a24bde4fd7ee4f26a57738162efb8c2 (bikeshed main tree 5e6db6c5a7638de51ec93d678d96222269de4d50, identical to clean's main); RECON sonnet, lenses+synthesis opus; every dispatch subagent_type general-purpose, never hyperpowers:peek; agent body delivered by file):
- METHOD: as the PRESSURE-TEST CONTRACT Method line and the RED BASELINE METHOD line specify. Fixtures rebuilt by `<sp>/fixtures.sh` before the first dispatch; all five branch TREE shas reproduced exactly (the four inherited ones match the bd-zk46 record, bikeshed's matches the RED BASELINE). The agent body was delivered BY FILE — `sed -n '7,$p' agents/peek.md > <sp>/agent-body.md` (281 lines, everything after the frontmatter's closing `---`) — and each lens/RECON dispatch's Step 0 read that file in full and named it the agent's operating prompt, never retyped into the prompt; synthesis was delivered the same way (`sed -n '116,170p' skills/peek/SKILL.md > <sp>/step6.md`, 55 lines, first line `## Step 6: Synthesis (Lead)`, last line the blank before `## Step 7:` — the range was re-located with `grep -n '^## Step 6\|^## Step 7'` at this HEAD, where Step 7 now opens at :171). Every dispatch carried "There is no user present. Do not pause for confirmation or ask questions; complete the mode and return."; no dispatch paused, so no SendMessage resume was needed. Agents wrote their own returns under `<sp>/green/` (outside the reviewed repo and worktree, Shared Rule 4) and replied with the path and counts only. No lens returned an `ERROR: <MODE> dispatch missing <input>` line, so no run was discarded for dispatch shape. RUN ORDER, per the task spec: the three synthesis fixtures first, then bikeshed run 1, then bikeshed run 2 — so both bikeshed runs were measured at the header's blob shas, which no fix round changed (there were none). BIKESHED DISPATCH SHAPE: fresh worktree per run (`git worktree remove --force`, `git worktree prune`, `git worktree add --detach <sp>/wt/bikeshed feature/refund`, run between run 1 and run 2 as well, so the two runs share nothing but the tree); RECON first; RECON's Stated Aims taken as the confirmed aims unchanged and its Surprises as corrected-unchanged, simulating confirm-as-is at the intent gate; then CODE, ARCHITECTURE and DELIVERY dispatched in one message, each carrying the full required-input set of `agents/peek.md` Mode Detection — target identity, worktree path, forge+rung (no forge, rung 3), the confirmed aims, RECON's change inventory, RECON's Prior Review block verbatim to all three, and RECON's Surprises to DELIVERY and ARCHITECTURE (CODE may ignore it per that section) — with "Do not run the test suite (the user did not opt in)" in every lens prompt; then synthesis, given RECON's return PLUS the confirmed aims PLUS the Surprises block PLUS the three lens returns verbatim, concatenated into `<sp>/synth-input/bikeshed-green-run<N>-SYNTH-INPUT.md` (RED's `bikeshed-run<N>-SYNTH-INPUT.md` files are left untouched). SYNTHESIS-FIXTURE DISPATCH SHAPE: one opus `general-purpose` dispatch each, given `<sp>/step6.md` plus `<sp>/synth-input/<fixture>-SYNTH-INPUT.md`, itself the concatenation of the confirmed aims (the aims exactly as written in that fixture's DELIVERY aims table), the Surprises block (exactly as written in that fixture's RECON.md), that fixture's `RECON.md`, and its `CODE.md`, `ARCHITECTURE.md` and `DELIVERY.md` verbatim — the four files recorded in the SYNTHESIS FIXTURES block above, none of them edited. No worktree was offered for the three synthesis runs and each dispatch was told the lens returns and RECON's return are the whole record; every file:line and every helper each report cites was checked back to those returns, and all three cite nothing that is not in them.
- bikeshed run1: pass — all ten rules. (1) opens `**Verdict: APPROVE** — The payments client gains a refund operation that validates its inputs and posts with an idempotency key through the same seam the charge operation already uses, adding no new outbound path and no second key source.` (2) Findings after synthesis C/I/S = 0/0/3: no finding is filed Critical or Important, `grep -c '\[downgraded:'` = 0 and `grep -c '\[lead-added:'` = 0, so no demotion was needed to reach zero and there is nothing to quote under the demotion clause. (3) three Suggestions, each naming a concrete change, with these `Direction:` lines verbatim — [`Direction: drop the four comments; the guards, the payload, and the mapping already read as what they are.`] [`Direction: use `charge_id` and `amount` directly and build both dicts as literals, matching `charge()`.`] [`Direction: give the stub a neutral home that both test modules import, rather than having one test module own a fixture the other depends on.`] — none says keep or leave the code as it is, none is an either/or whose other arm is no change, and none defers the change until a future condition holds; this is the discriminating rule, and RED failed it on both runs (RED run 2's `Direction: leave as it stands while the stub has a single additional consumer; move it to a conftest.py if a third test module needs it.` and RED run 1's two hedged either/or forms). (4) grading rule (i) `<sp>/scan.py` prints `TOTAL HITS: 0` over the top layer; (ii) open-ended read found no sentence that grades the work or the author — the three closest candidates were read and rejected as descriptions of the code or of the findings: WTBD "No production caller of the client exists anywhere in the repository, so the widened class surface is observed only by the tests." (a fact about the repo), OA "The one structural move the branch does make is in the tests: the new test module depends on the older one for its transport stub, which makes a test suite double as the package's shared fixture home and sets the precedent the next test module will follow." (a finding), OA "The three open items are local, and each is addressed where it stands." (the bindingness of findings). No word is added to the Grading-word list. (5) sentence counts WTBD=5 AvA=3 OA=3 against ceilings 6 / 4 / 4. (6) `Path: fix in place`. (7) `Decision: (none)`. (8) no Critical of any class anywhere in the run (lens counts C/I/S — CODE 0/0/2, ARCHITECTURE 0/0/1, DELIVERY 0/0/0 — and 0 Criticals after synthesis), and the standing risk on this tree, `_new_idempotency_key()`'s docstring, was routed to Questions for the Author rather than filed: "`refund()` mints its idempotency key inside the call (`payments/client.py:53`) and neither accepts one nor returns it, so a caller whose call times out after the provider recorded the refund can only retry by calling `refund()` again — which mints a new key and posts a second refund. … `charge()` has the same shape, so this reads as a client-wide contract question rather than something this branch introduced; no caller exists in the repository to settle it, and the docstring is the only statement of the expectation." (9) [lens returns] Important counts CODE 0 / ARCHITECTURE 0 / DELIVERY 0, and `grep -c 'Severity: Important\|Maintainer cost:\|Hits:'` = 0 on each of the three return files, so no lens filed an Important at all and there is no `Maintainer cost:` line naming reading effort to quote. (10) [lens returns] lens-side Importants by surface: method length 0, local names 0, narrating comments 0, test setup 0, other 0 — zero at every lens on every surface. Where each commissioned surface landed instead: narrating comments → CODE Suggestion 1 (`payments/client.py:41, 45, 49, 54`, "Four comments narrate the lines beneath them instead of stating anything the code does not."); short local names AND long inline method → bundled into CODE Suggestion 2 (`payments/client.py:42-59`, "The method restates in longhand what its sibling states directly — two alias variables for its own parameters, and two dicts assembled key by key."); copy-pasted per-test setup → nothing at any lens, no finding and no question; test-support structure (not a commissioned surface) → ARCHITECTURE Suggestion (`tests/test_refund.py:4`). Derived fields: ARCHITECTURE Stance `fits`, DELIVERY aims table 4 of 4 `achieved`, RECON Surprises `(none)`, degradation rung 3.
- bikeshed run2: pass — all ten rules. (1) opens `**Verdict: APPROVE** — The payment client gains a refund operation that validates its inputs and reaches the provider through the same transport seam and key helper the existing charge operation uses, and all four stated aims are delivered with tests covering them.` (2) Findings after synthesis C/I/S = 0/0/3: `grep -c 'Severity: Critical'` = 0, `grep -c 'Severity: Important'` = 0, `grep -c '\[downgraded:'` = 0, `grep -c '\[lead-added:'` = 0. (3) three Suggestions, each naming a concrete change, with these `Direction:` lines verbatim — [`Direction: Drop the four comments; the guards and the payload keys already state what they do.`] [`Direction: Use `charge_id` and `amount` directly and build both dicts as literals, matching `charge()`.`] [`Direction: Give the stub its own home — a test-support module or a conftest fixture that both test modules import — so neither test module owns the other's fixture.`] — none of the three offered-leaving forms appears; in particular the test-stub Suggestion, which is the exact finding RED run 2 hedged, now asks for the move outright with no "while"/"if a third test module needs it" clause. (4) grading rule (i) `TOTAL HITS: 0`; (ii) open-ended read found no grading sentence — closest candidates read and rejected: OA "The three findings are all Suggestions on surfaces that do not change what the code does: how one method spells out its steps, and which module owns a shared test stub." (severity and subject of the findings), OA "One question stands open on idempotency-key reuse, and it can only be answered by callers outside this repository." (what is unresolved and why), WTBD "The change is additive across two files with no deletions." (the shape of the diff). No word is added to the Grading-word list. (5) sentence counts WTBD=5 AvA=2 OA=4 against ceilings 6 / 4 / 4. (6) `Path: fix in place`. (7) `Decision: (none)`. (8) no Critical of any class anywhere in the run (lens counts — CODE 0/0/2, ARCHITECTURE 0/0/1, DELIVERY 0/0/0 — and 0 after synthesis), and the `_new_idempotency_key()` docstring risk was again routed to Questions for the Author rather than filed as a production Critical: "`refund()` mints a fresh idempotency key on every call (payments/client.py:53), so two calls for one logical refund carry two keys and the provider would settle them as two refunds. The key helper's docstring (payments/client.py:7-12) places retry-stability on the caller … and this repository contains no caller of `refund()` outside the two test modules. Is there a caller outside this repository that retries by re-invoking `refund()`, and if so where does its stable key come from?" (9) [lens returns] Important counts CODE 0 / ARCHITECTURE 0 / DELIVERY 0, and `grep -c 'Severity: Important\|Maintainer cost:\|Hits:'` = 0 on each of the three return files — no Important anywhere, so no cost line to quote. (10) [lens returns] lens-side Importants by surface: method length 0, local names 0, narrating comments 0, test setup 0, other 0. Where each surface landed: narrating comments → CODE Suggestion 1 (`payments/client.py:41, 45, 49, 54`); short local names AND long inline method → bundled into CODE Suggestion 2 (`payments/client.py:42-59`, "`refund()` copies both parameters into short-name locals and fills its two dicts key-by-key, where the sibling method in the same file uses its parameter directly and builds dict literals."); copy-pasted per-test setup → nothing at any lens; test-support structure → ARCHITECTURE Suggestion (`tests/test_refund.py:4`). ARCHITECTURE's Stance reasoning routes the three code surfaces away from the structural lane in its own words: "Where `refund()` diverges from `charge()` — incremental dict assembly, alias locals, narrating comments — the divergence is local expression inside one method rather than a parallel mechanism, so it is routed to the code lens rather than filed here." Derived fields: Stance `fits`, DELIVERY aims table 4 of 4 `achieved`, RECON Surprises `(none)`, degradation rung 3. Both bikeshed runs therefore agree on the verdict and on every derived field, and both were measured at the header's blob shas.
- clean, bad-no-critical, silent-reshape, missing-aim: NOT RUN this epic (USER DECISION 2026-09-09, cost). Their rule sets — the bd-zk46 PRESSURE-TEST CONTRACT sets as amended by CONTRACT AMENDMENTS 1-3, plus this contract's ADDED RULE (+) — stand unchanged and unverified at these blobs; nothing above relaxes, rewords or drops one, and a later epic may re-run them. The four inherited branch TREE shas were still verified against the bd-zk46 record at this GREEN (header line), so the fixtures they would run against are unchanged.
- synth-old: pass — all seven rules. (1) CODE's Trigger-less Critical at `reports/calc.py:12-15` appears under Findings as `- Severity: Suggestion  `[downgraded: no consequence named; no cost named]`  (Severity Anchor: pipeline-constants.md)` with Location `reports/calc.py:12-15` and Defect "`average(values)` defines no behavior for an empty series — it divides by `len(values)` with no guard, while the sibling `total()` in the same module returns `0` for that input.", and the report states the basis in its own words: "raised as Critical with no `Trigger:` and no `Consequence:` line, and with neither a `Hits:` nor a `Maintainer cost:` line to hold it at Important, so it lands at Suggestion" — R2's fallback ran past Important, where the pre-edit re-check stopped at Important (bd-zk46 GREEN :833). (2) ARCHITECTURE's `[convention]` Important at `reports/calc.py:30-32` appears as `- Severity: Suggestion  `[downgraded: no cost named]`` with Class `convention` and Defect "The branch adds a private `_round2()` rounding helper beside `utils/money.py`'s `round_currency()`, the helper this repository already designates for two-place money rounding.", basis "raised as Important with neither a `Hits:` nor a `Maintainer cost:` line, so it lands at Suggestion". (3) opens `**Verdict: APPROVE** — the report totals module gains a mean and a per-report summary, both reachable only from inside the reports package, with no contract change and no new dependency anywhere else.` — zero Criticals and zero Importants survive, so loop-interfaces' unchanged derivation yields APPROVE where pre-edit Step 6 yielded APPROVE WITH CHANGES; the rule discriminates. (4) `grep -c '\[lead-added:'` = 0 — the DELIVERY table reads `achieved` on both rows and the ARCHITECTURE Stance is `fits`, so neither re-check move had anything to fire on. (5) `Path: fix in place` and `Decision: (none)`. (6) sentence counts WTBD=5 AvA=3 OA=3 against ceilings 6 / 4 / 4. (7) grading rule (i) `TOTAL HITS: 0`; (ii) open-ended read found no grading sentence — closest candidates read and rejected: WTBD "The change is additive — the module's pre-existing lines are byte-identical to the base." (a fact about the diff), OA "One local tension stands: the branch stands up its own two-place rounding helper beside the one this repository already designates for money rounding, so report arithmetic now carries a second rounding path." (a finding). The ADDED RULE (+) is vacuous here as the contract predicts: no Important survives. Third Suggestion (DELIVERY's, undemoted) carried through unchanged at `tests/test_calc.py:22-31`.
- synth-new: pass — graded against `docs/ledgers/bd-zk46-pressure-tests.md:798` as amended by CONTRACT AMENDMENT 2 (3) and CONTRACT AMENDMENT 3 (3). Two Criticals appear and no more: `- Severity: Critical  `[lead-added: aim missing]`` with `Critical class: delivery`, `Trigger: The aim "Add `unsubscribe(user_id)` so a user can stop receiving digests" — source: commit message.` and `Consequence: The merge record states that a user can stop receiving digests, and the merge ships a nightly send path with no operation that stops one. Whoever reads the history for how a digest is stopped — the operator handling a stop request, and any later branch that calls the operation because the commit message says it exists — finds nothing to call.`; and `- Severity: Critical  `[lead-added: undeclared reshape]`` with `Critical class: structural`, `Trigger: Message-content ownership for the digest moves from `notifications/digest.py:22-48` into `email/message.py:31-57`, and a new dependency arrow runs from `email/message.py:8` into `notifications.templates`, against the direction of every other import between these layers.` and `Consequence: The merge decides that the mail transport may own message content and may depend on the domain packages it serves, with no aim, description, or recorded discussion behind that choice. `alerts/mailer.py`, the transport's other consumer, inherits a path to notifications through `email.message`, and every later change to either layer is made against the reversed arrow with no record of why it points that way.` Both carry both lines, so the re-check's first rule demoted neither: `grep -c '\[downgraded:'` = 0, and a demotion would have failed this scenario. Report opens `**Verdict: REQUEST CHANGES** — the merge would claim an unsubscribe capability the branch does not contain, and would settle a reversed dependency between the mail transport and the notifications domain with nothing on record that chose it.` Overall Assessment carries `Path: fix in place` and `Decision: Whether digest rendering belongs in the mail transport — accept the reversed dependency and record the move in the branch description, or return the body builder to the notifications domain and pass a rendered body to the transport. Separately, whether the unsubscribe operation is implemented on this branch or dropped from the commit message.` Ceilings (AMENDMENT 2 (3)): WTBD=5 AvA=3 OA=4 against 6 / 4 / 4. Grading rule (i) `TOTAL HITS: 0`; (ii) open-ended read found no grading sentence — closest candidates read and rejected: AvA "One of the two stated aims lands: the digest send path exists and a test exercises it through the transport seam." (a delivery fact) and OA "Merging as it stands settles that direction with nothing on record that chose it." (a consequence). Findings carry `**Important** - (none)` and `**Suggestions** - (none)`, so the ADDED RULE (+) is vacuous here as the contract predicts. The RECON.md input required by AMENDMENT 3 (3) was supplied and its Change Inventory is rendered in What This Branch Does, so the ≤ 6 ceiling and the full top-layer region applied for real.
- synth-rework: pass — all ten rules. (1) opens `**Verdict: APPROVE WITH CHANGES** — The new inventory client stands up its own attempt policy, delay curve, and time source beside the shared ones, so the repository now runs a second copy of each and the suite's fixed-clock fixture does not reach this client's expiry computation.` (2) `**Critical**` reads `- (none)` — zero Criticals after synthesis. (3) the `inventory/client.py:34` finding appears as `- **Important** `[downgraded: no consequence named]` — `[capability]` — Scope: delta — `inventory/client.py:34`` — the marker is `[downgraded: no consequence named]` and NOT `; no cost named`, and the report states why in its own `Downgrade basis:` line: "returned as a production-class Critical with no `Trigger:` and no `Consequence:` line; the filled `Maintainer cost:` line lands it at Important (`skills/common-patterns/pipeline-constants.md`, Severity Anchor)." This is the only scenario in the set that exercises R2's stop-at-Important, and it stopped. (4) the `:19` and `:47` findings survive as Important with no downgrade marker — `- **Important** — `[capability]` — Scope: delta — `inventory/client.py:19` `[fix-proposed]`` and `- **Important** — `[capability]` — Scope: delta — `inventory/client.py:47` `[fix-proposed]`` — each carrying its filled cost line through synthesis: `Maintainer cost: the next change to `utils/retry.py`'s attempt policy must be repeated at `inventory/client.py:19`, which does not say it mirrors `with_retry`.` and `Maintainer cost: the next change to `utils/clock.py`'s time source must be repeated at `inventory/client.py:47`, which does not say it mirrors `now_ms`.` (5) `Path: rework`, and the Overall Assessment names the shared cause in plain language, reached from the cause rather than from severity: "The new client works against the shared-helper structure without changing it, and one cause sits under all three findings: the module imports nothing from the shared helper package and stands up private copies of three helpers instead. … The consequences are a second attempt policy, a delay curve that diverges from the shared one once a fourth attempt is reached, and an expiry computation the suite's fixed-clock fixture cannot control. Addressing the three sites one at a time leaves that cause standing, since each private copy exists for the same reason." Synthesis was never handed that cause pre-named — CODE's three findings and the ARCHITECTURE Stance reasoning are its only source. (6) `Decision: (none)`. (7) `grep -c '\[lead-added:'` = 0 — DELIVERY's two rows both read `achieved` and the Stance is `fights`, so neither re-check move had anything to fire on. (8) sentence counts WTBD=5 AvA=3 OA=4 against ceilings 6 / 4 / 4. (9) grading rule (i) `TOTAL HITS: 0`; (ii) open-ended read found no grading sentence — closest candidates read and rejected: OA "No responsibility moved and no dependency reversed, so this is a parallel way to do three things that already have a way, not a boundary change." (a structural fact) and WTBD "The suite's fixed-clock fixture patches the shared time reader, so it reaches the two existing clients and not this one." (a fact about the tests). (10) ADDED RULE (+) in full: all three surviving Importants carry a filled `Maintainer cost:` line (the two quoted under (4) plus `Maintainer cost: the next change to `utils/backoff.py`'s delay curve must be repeated at `inventory/client.py:34`, which does not say it mirrors `exponential`.` on the `:34` finding), and none of the three names only reading effort — each names a specific future edit at a named file:line and the fact that site does not itself state, none uses "confusing", "unclear", "harder to read", "surprising" or a synonym.
GREEN RESULT: 5 of 5 runs passed every rule (2 bikeshed runs + 3 synthesis runs; the four inherited fixtures were not run, per the user's 2026-09-09 cost decision, and their rules stand unchanged); fix rounds: none — no rule failed, so no loophole was named and no wording edit was made, and both bikeshed runs stand at the header's blob shas. Verbatim returns and reports: `<sp>/green/` (13 files — bikeshed-run{1,2}-{RECON,CODE,ARCHITECTURE,DELIVERY,REPORT}.md and synth-{old,new,rework}-REPORT.md), where `<sp>` is /private/tmp/claude-501/-Users-abugosh-g-hyperpowers/27f7ec48-eeba-40eb-b34e-e57d9c495af0/scratchpad/peek-bar; synthesis inputs at `<sp>/synth-input/` (bikeshed-green-run{1,2}- and synth-{old,new,rework}-SYNTH-INPUT.md); by-file prompts at `<sp>/agent-body.md` and `<sp>/step6.md`; scanner at `<sp>/scan.py`. `<sp>/green-cancelled/` holds the transcripts of an earlier attempt that was stopped before grading; it is not part of this record.
