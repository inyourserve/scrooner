"""Scale/unit publish guard (WO-27, RF-18). Real stored values (DATA-INFERRED, 2026-10-22):
MOS dividends_per_share 220,000 / 440,000 / derived Q4 -219,999.34 beside the correct 0.22 / 0.88."""

from __future__ import annotations

from datetime import date
from decimal import Decimal as D

import pytest

from scrooner_pipeline.common.cell_blank_reason import InMemoryBlankReasonStore
from scrooner_pipeline.mapper import scale_unit_guard as g

ON = {"SCROONER_RULES_ENABLED": g.RULE_ID}


@pytest.mark.parametrize("v", ["220000", "440000", "-219999.34", "1000", "-1000"])
def test_mos_style_dps_is_implausible(v):
    assert g.implausible("dps", D(v))


@pytest.mark.parametrize("v", ["0.22", "0.88", "0", "12.5", "999.99", "-0.5"])
def test_genuine_dps_is_kept(v):
    assert not g.implausible("dps", D(v))


@pytest.mark.parametrize(
    ("v", "bad"),
    [
        ("999999", True),
        ("1000000", False),
        ("10000000000000", False),
        ("10000000000001", True),
        ("31000000000000000000", True),
        ("608000000", False),
    ],
)
def test_public_float_bounds(v, bad):
    assert g.implausible("public_float", D(v)) is bad


class _Cur:
    def __init__(self, c):
        self.c, self.res = c, []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        sql = " ".join(sql.split())
        self.c.sql.append((sql, params))
        if sql.startswith("select id from core.company"):
            self.res = [(4647,)]
        elif sql.startswith("select id, name from analytics.canonical_concept"):
            self.res = [
                (1, "dividends_per_share"),
                (2, "dividends_per_share_resolved"),
                (3, "public_float"),
            ]
        elif "from analytics.canonical_fact cf" in sql:
            q3 = (date(2025, 7, 1), date(2025, 9, 30))
            q4 = (date(2025, 10, 1), date(2025, 12, 31))
            fy = (date(2025, 1, 1), date(2025, 12, 31))
            cik = "0001285785"
            self.res = [
                (4647, 11, "dividends_per_share", D("220000"), *q3, cik),
                (4647, 11, "dividends_per_share_resolved", D("220000"), *q3, cik),
                (4647, 12, "dividends_per_share_resolved", D("-219999.34"), *q4, cik),
                (4647, 13, "dividends_per_share_resolved", D("0.88"), *fy, cik),
                (
                    4647,
                    14,
                    "public_float",
                    D("608000000"),
                    date(2025, 6, 30),
                    date(2025, 6, 30),
                    cik,
                ),
            ]
        else:
            self.res = []

    def fetchall(self):
        return self.res


class _Conn:
    def __init__(self):
        self.sql = []

    def cursor(self):
        return _Cur(self)

    def commit(self):
        pass

    def writes(self):
        return [s for s, _ in self.sql if s.startswith(("delete", "insert"))]


def test_flag_off_noop():
    c = _Conn()
    assert (
        g.apply_scale_unit_guard(c, environ={})["skipped"] == "rule_off" and c.sql == []
    )


def test_dry_run_reports_three_mos_cells_and_writes_nothing():
    c = _Conn()
    out = g.apply_scale_unit_guard(c, dry_run=True, environ={})
    assert c.writes() == []
    assert out["dps"] == 3 and out["public_float"] == 0 and out["cells_hidden"] == 3
    assert {p.before for p in out["planned"]} == {D("220000"), D("-219999.34")}


def test_live_hides_whole_family_for_the_bad_period_only():
    c, store = _Conn(), InMemoryBlankReasonStore()
    g.apply_scale_unit_guard(c, environ=ON, reason_store=store, run_id="r1")
    deletes = [(s, p) for s, p in c.sql if s.startswith("delete")]
    assert [p for _, p in deletes] == [
        (4647, [1, 2], [11, 12])
    ]  # periods 13 (0.88) and 14 untouched
    assert {r.reason_code for r in store.all()} == {"guard_hidden"}
    assert len(store.all()) == 3


def test_live_without_store_refuses():
    with pytest.raises(RuntimeError):
        g.apply_scale_unit_guard(_Conn(), environ=ON)
