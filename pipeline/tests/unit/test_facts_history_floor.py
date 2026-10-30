"""Facts that end before 2014-01-01 are never stored (founder decision 2026-10-25, floor moved from 2015 to 2014; see common/history_floor.py)."""

from datetime import date

from scrooner_pipeline.normalizer import facts


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

    def commit(self):
        pass


def _row(end, accn="a-1"):
    return {
        "taxonomy": "us-gaap",
        "tag": "Revenues",
        "raw_unit": "USD",
        "start": None,
        "end": end,
        "val": 5,
        "accn": accn,
    }


def test_pre_2014_facts_are_skipped_and_2015_kept(monkeypatch):
    conn = _Conn()
    monkeypatch.setattr(facts, "_get_company_id", lambda c, cik: 1)
    monkeypatch.setattr(facts, "_latest_companyfacts_object", lambda c, cik: (9, "p"))
    monkeypatch.setattr(facts, "_load_json", lambda s, p: {})
    monkeypatch.setattr(facts, "_load_filing_lookup", lambda c, i: {"a-1": 3})
    monkeypatch.setattr(
        facts,
        "_load_period_lookup",
        lambda c, i: {
            (date(2013, 12, 31), date(2013, 12, 31), "instant"): 10,
            (date(2014, 1, 1), date(2014, 1, 1), "instant"): 11,
        },
    )
    monkeypatch.setattr(facts, "_load_unit_lookup", lambda c: {"usd": 1})
    monkeypatch.setattr(
        facts, "upsert_concepts", lambda c, pairs: {("us-gaap", "Revenues"): 7}
    )
    monkeypatch.setattr(
        facts,
        "extract_fact_rows",
        lambda payload: [_row("2013-12-31"), _row("2014-01-01")],
    )
    out = facts.normalize_facts_for_cik(None, conn, "0000000001")
    assert out["skipped_before_history_floor"] == 1
    assert out["written"] == 1
    assert [r["period_id"] for r in conn.rows] == [11]
