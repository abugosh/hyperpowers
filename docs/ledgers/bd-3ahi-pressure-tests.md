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
