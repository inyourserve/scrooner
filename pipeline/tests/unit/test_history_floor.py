"""Storage history floor (2014-01-01): boundary, facts, periods, idempotency."""

from datetime import date

from scrooner_pipeline.common import history_floor
from scrooner_pipeline.common.history_floor import HISTORY_FLOOR, is_before_floor
from scrooner_pipeline.normalizer import facts as facts_mod
from scrooner_pipeline.normalizer import periods as periods_mod


def test_floor_is_2014_not_the_display_floor():
    assert HISTORY_FLOOR == date(2014, 1, 1)


def test_boundary_decided_on_end_date():
    assert is_before_floor(date(2013, 12, 31))  # the 2013-12-31 instant goes
    assert not is_before_floor(date(2014, 1, 1))
    assert not is_before_floor(date(2014, 6, 30))  # straddling duration ends here


PAYLOAD = {
    "facts": {
        "us-gaap": {
            "Revenues": {
                "units": {
                    "USD": [
                        {"accn": "A1", "start": "2013-01-01", "end": "2013-12-31", "val": 1},
                        {"accn": "A1", "start": "2013-07-01", "end": "2014-06-30", "val": 2},
                        {"accn": "A2", "start": "2015-01-01", "end": "2015-12-31", "val": 3},
                    ]
                }
            },
            "Assets": {
                "units": {
                    "USD": [
                        {"accn": "A1", "end": "2013-12-31", "val": 10},
                        {"accn": "A2", "end": "2014-12-31", "val": 11},
                    ]
                }
            },
        }
    }
}


class _Cur:
    def __init__(self, sink):
        self.sink = sink

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def executemany(self, sql, rows):
        self.sink.extend(rows)

    def execute(self, *a, **k):
        pass


class _Conn:
    def __init__(self):
        self.rows = []

    def cursor(self):
        return _Cur(self.rows)

    def commit(self):
        pass


def _patch_facts(monkeypatch):
    all_keys = {}
    n = 0
    for r in facts_mod.extract_fact_rows(PAYLOAD):
        start = facts_mod._parse_date(r["start"]) if r["start"] else facts_mod._parse_date(r["end"])
        end = facts_mod._parse_date(r["end"])
        key = (start, end, "duration" if r["start"] else "instant")
        if key not in all_keys:
            n += 1
            all_keys[key] = n
    monkeypatch.setattr(facts_mod, "_get_company_id", lambda c, k: 1)
    monkeypatch.setattr(facts_mod, "_latest_companyfacts_object", lambda c, k: (5, "raw/x.json"))
    monkeypatch.setattr(facts_mod, "_load_json", lambda s, p: PAYLOAD)
    monkeypatch.setattr(facts_mod, "_load_filing_lookup", lambda c, i: {"A1": 1, "A2": 2})
    monkeypatch.setattr(facts_mod, "_load_period_lookup", lambda c, i: all_keys)
    monkeypatch.setattr(facts_mod, "_load_unit_lookup", lambda c: {"USD": 1})
    monkeypatch.setattr(
        facts_mod, "upsert_concepts", lambda c, pairs: {p: i for i, p in enumerate(sorted(pairs), 1)}
    )
    monkeypatch.setattr(facts_mod, "canonicalize_unit", lambda u: u)


def test_facts_before_floor_are_not_written_and_straddling_is_kept(monkeypatch):
    _patch_facts(monkeypatch)
    conn = _Conn()
    stats = facts_mod.normalize_facts_for_cik(None, conn, "0000000001")
    assert stats["skipped_before_history_floor"] == 2  # 2013 duration, 2013-12-31 instant
    assert stats["written"] == 3
    assert stats["skipped_period_not_found"] == 0
    assert {r["value"] for r in conn.rows} == {2, 3, 11}  # straddling 2, FY2015 3, 2014-12-31 11


def test_facts_rerun_is_idempotent(monkeypatch):
    _patch_facts(monkeypatch)
    a, b = _Conn(), _Conn()
    facts_mod.normalize_facts_for_cik(None, a, "0000000001")
    facts_mod.normalize_facts_for_cik(None, b, "0000000001")
    assert a.rows == b.rows and a.rows  # identical, never a pre-floor row


def test_periods_filtered_after_anchors_and_labels_unchanged(monkeypatch):
    # fiscal years ending 2012-12-31 ... 2015-12-31, all FY-tagged
    payload = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        {"start": f"{y}-01-01", "end": f"{y}-12-31", "val": 1, "accn": "A", "fp": "FY"}
        for y in (2012, 2013, 2014, 2015)
    ] + [{"start": "2014-01-01", "end": "2014-03-31", "val": 1, "accn": "A", "fp": "Q1"}]}}}}}
    captured = {}
    monkeypatch.setattr(periods_mod, "_get_company", lambda c, k: (1, "1231"))
    monkeypatch.setattr(periods_mod, "_latest_companyfacts_object", lambda c, k: (5, "raw/x.json"))
    monkeypatch.setattr(periods_mod, "_load_json", lambda s, p: payload)
    monkeypatch.setattr(periods_mod, "upsert_periods", lambda c, i, rows: captured.setdefault("rows", rows) and len(rows))
    periods_mod.normalize_periods_for_cik(None, None, "0000000001")
    rows = captured["rows"]
    assert all(r["end_date"] >= HISTORY_FLOOR for r in rows)
    assert {r["end_date"].year for r in rows} == {2014, 2015}
    q1 = [r for r in rows if r["end_date"] == date(2014, 3, 31)][0]
    assert (q1["fiscal_year"], q1["fiscal_period"]) == (2014, "Q1")  # label needs the old anchors
