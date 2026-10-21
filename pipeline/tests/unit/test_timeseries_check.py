from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.sanity.timeseries_check import SEVERITY_OK, SEVERITY_OUTLIER, SEVERITY_SIGN_VIOLATION, check_yoy


def _check(current, prior, min_ratio=0.1, max_ratio=10.0, floor=1_000_000, never_negative=False):
    return check_yoy(
        1, 1, 1, date(2026, 3, 31), 2026, "Q1",
        Decimal(current), Decimal(prior) if prior is not None else None,
        min_ratio, max_ratio, floor, never_negative,
    )


@pytest.mark.unit
class TestCheckYoy:
    def test_ok_within_normal_growth(self):
        row = _check(current=110_000_000, prior=100_000_000)
        assert row["severity"] == SEVERITY_OK

    def test_outlier_when_ratio_exceeds_bound(self):
        # 100x growth on a material base -- way outside a 10x max_ratio.
        row = _check(current=10_000_000_000, prior=100_000_000)
        assert row["severity"] == SEVERITY_OUTLIER

    def test_outlier_when_collapsed_below_min_ratio(self):
        row = _check(current=1_000_000, prior=100_000_000, min_ratio=0.1)
        assert row["severity"] == SEVERITY_OUTLIER

    def test_sign_violation_for_never_negative_concept(self):
        # revenue/total_assets/cash should never be negative, regardless
        # of any history -- flagged even with no prior period at all.
        row = _check(current=-5_000_000, prior=None, never_negative=True)
        assert row["severity"] == SEVERITY_SIGN_VIOLATION

    def test_ok_when_no_prior_period_to_compare(self):
        row = _check(current=100_000_000, prior=None)
        assert row["severity"] == SEVERITY_OK
        assert row["yoy_ratio"] is None

    def test_ok_when_prior_base_below_materiality_floor(self):
        # A tiny prior base makes any ratio meaningless -- not flaggable.
        row = _check(current=50_000_000, prior=500, floor=1_000_000)
        assert row["severity"] == SEVERITY_OK

    def test_sign_flip_within_normal_bound_is_ok(self):
        # A real, legitimate turnaround (loss to modest profit) for a
        # concept that can be negative -- not an outlier on its own.
        row = _check(current=5_000_000, prior=-2_000_000, never_negative=False, max_ratio=10.0)
        assert row["severity"] == SEVERITY_OK

    def test_extreme_sign_flip_is_flagged(self):
        # A tiny loss flipping into an enormous profit -- needs a much
        # higher bar than ordinary same-sign growth, but this clears it.
        row = _check(current=500_000_000, prior=-1_000_000, never_negative=False, max_ratio=10.0)
        assert row["severity"] == SEVERITY_OUTLIER

    def test_never_negative_concept_flagged_even_with_normal_looking_history(self):
        row = _check(current=-1_000_000, prior=100_000_000, never_negative=True)
        assert row["severity"] == SEVERITY_SIGN_VIOLATION


class _FakeConn:
    def __init__(self, closed: bool = False) -> None:
        self.closed = closed
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1
        self.closed = True


@pytest.mark.unit
class TestRunAllSurvivesDroppedConnections:
    """2026-10-20 sanity: a socket drop during one concept's write left the caller's
    connection dead and crashed the step on the next concept ("the connection is closed")."""

    def _setup(self, monkeypatch, behaviour):
        import psycopg

        from scrooner_pipeline.sanity import timeseries_check as ts

        used: list[object] = []
        opened: list[_FakeConn] = []
        calls: list[str] = []

        def fake_run_concept(conn, concept_name, *args, **kwargs):
            used.append(conn)
            calls.append(concept_name)
            return behaviour(conn, concept_name, calls)

        def fake_connect(_url):
            fresh = _FakeConn()
            opened.append(fresh)
            return fresh

        monkeypatch.setattr(ts, "run_concept", fake_run_concept)
        monkeypatch.setattr(ts.psycopg, "connect", fake_connect)
        return ts, psycopg, used, opened, calls

    def test_closed_connection_is_replaced_before_the_next_concept(self, monkeypatch):
        original = _FakeConn()

        def behaviour(conn, name, calls):
            if len(calls) == 1:
                original.closed = True  # the pooler dropped it during the first concept's write
            return {"considered": 1, SEVERITY_OK: 1, SEVERITY_OUTLIER: 0, SEVERITY_SIGN_VIOLATION: 0}

        ts, _, used, opened, calls = self._setup(monkeypatch, behaviour)
        totals = ts.run_all(original)

        assert len(calls) == len(ts.CONCEPTS_TO_CHECK)
        assert used[0] is original
        assert all(c is not original for c in used[1:]), "a dead connection must never be reused"
        assert totals["considered"] == len(ts.CONCEPTS_TO_CHECK)
        assert all(o.close_calls == 1 for o in opened), "connections opened by run_all are closed"
        assert original.close_calls == 0, "the caller's connection is never closed here"

    def test_concept_is_retried_on_a_fresh_connection_after_an_operational_error(self, monkeypatch):
        original = _FakeConn()
        state = {"failed": False}

        def behaviour(conn, name, calls):
            if len(calls) == 2 and not state["failed"]:
                state["failed"] = True
                import psycopg

                raise psycopg.OperationalError("SSL SYSCALL error: Connection timed out")
            return {"considered": 1, SEVERITY_OK: 1, SEVERITY_OUTLIER: 0, SEVERITY_SIGN_VIOLATION: 0}

        ts, _, used, opened, calls = self._setup(monkeypatch, behaviour)
        totals = ts.run_all(original)

        assert calls.count(calls[1]) == 2, "the failed concept ran twice"
        assert used[2] is not original and used[2] is opened[0]
        assert totals["considered"] == len(ts.CONCEPTS_TO_CHECK)

    def test_gives_up_after_the_attempt_limit(self, monkeypatch):
        import psycopg

        def behaviour(conn, name, calls):
            raise psycopg.OperationalError("connection refused")

        ts, _, _, opened, calls = self._setup(monkeypatch, behaviour)
        with pytest.raises(psycopg.OperationalError):
            ts.run_all(_FakeConn())
        assert len(calls) == ts.CONCEPT_ATTEMPTS
        assert all(o.close_calls == 1 for o in opened)
