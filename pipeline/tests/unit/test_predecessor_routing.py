"""Predecessor routing (core.company_history_source): the predecessor CIK's payload is attributed to
the successor company, only for periods inside the window (normalizer/predecessors.py)."""

from datetime import date
from decimal import Decimal

from scrooner_pipeline.jobs.bootstrap import _with_predecessors
from scrooner_pipeline.normalizer import facts
from scrooner_pipeline.normalizer.predecessors import Route

WIN = Route(5351, date(2014, 1, 1), date(2026, 3, 31))


def test_route_contains_is_inclusive_and_none_safe():
    assert WIN.contains(date(2014, 1, 1)) and WIN.contains(date(2026, 3, 31))
    assert not WIN.contains(date(2026, 4, 1)) and not WIN.contains(None)


class _Res:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


class _Cur:
    def __init__(self, sink):
        self.sink = sink

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def executemany(self, sql, rows):
        self.sink.extend(rows)


class _Conn:
    def __init__(self):
        self.rows = []

    def cursor(self):
        return _Cur(self.rows)

    def execute(self, sql, params=None):
        return _Res([("acc-old", 77)] if "core.filing" in sql else [])

    def commit(self):
        pass


def _setup(monkeypatch):
    monkeypatch.setattr(facts, "_load_filing_lookup", lambda c, cid: {})
    monkeypatch.setattr(facts, "upsert_concepts", lambda c, p: {("us-gaap", "Revenues"): 1})
    monkeypatch.setattr(facts, "_load_unit_lookup", lambda c: {"usd": 2})
    periods = {
        (date(2024, 12, 31), date(2024, 12, 31), "instant"): 10,
        (date(2026, 6, 30), date(2026, 6, 30), "instant"): 11,
    }
    monkeypatch.setattr(facts, "_load_period_lookup", lambda c, cid: periods)


def _payload():
    e = lambda end: {"accn": "acc-old", "end": end, "val": Decimal(5)}
    return {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [e("2024-12-31"), e("2026-06-30")]}}}}}


def test_window_writes_successor_rows_inside_window_only(monkeypatch):
    _setup(monkeypatch)
    conn = _Conn()
    out = facts.normalize_payload(conn, 5351, "0000034088", _payload(), 9, window=WIN)
    assert [(r["company_id"], r["period_id"], r["filing_id"]) for r in conn.rows] == [(5351, 10, 77)]
    assert out["skipped_outside_window"] == 1


def test_no_window_unchanged(monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(facts, "_load_filing_lookup", lambda c, cid: {"acc-old": 77})
    conn = _Conn()
    facts.normalize_payload(conn, 5351, "x", _payload(), 9)
    assert len(conn.rows) == 2


def test_collector_cik_selection(monkeypatch):
    import scrooner_pipeline.jobs.bootstrap as b

    monkeypatch.setattr(b, "predecessor_source_ciks", lambda c: {"0000034088"})

    class _CM:
        def __enter__(self):
            return None

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(b, "get_connection", lambda: _CM())
    assert _with_predecessors(None, False, False) is None
    assert _with_predecessors({"0000000001"}, True, False) == {"0000000001", "0000034088"}
    assert _with_predecessors({"0000000001"}, False, True) == {"0000034088"}
