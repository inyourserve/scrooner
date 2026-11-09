"""fsn_store.pilot: sector templates (SECTOR-TEMPLATES-2026-11-01 §1-2) and calendar-key matching."""

from __future__ import annotations

import gzip
from datetime import date

import pytest
from scrooner_pipeline.fsn_store import pilot


@pytest.mark.unit
def test_sector_by_sic_and_template_outs():
    assert [
        pilot.sector_of(s) for s in ("6021", "6331", "6798", "4911", "7372", None)
    ] == [
        "bank",
        "insurer",
        "equity_reit",
        "utility",
        "general",
        "general",
    ]
    bank = pilot.template("bank")
    assert (
        "gross_profit_resolved" not in bank and "operating_income_resolved" not in bank
    )
    assert "net_income_resolved" in bank and "total_assets_resolved" in bank
    assert pilot.template("general") == list(pilot.GENERAL)


@pytest.mark.unit
def test_calendar_keys_and_match_within_ten_days(tmp_path):
    cal = tmp_path / "cal.csv.gz"
    with gzip.open(cal, "wt") as fh:
        fh.write(
            "company_id,cik,fiscal_year,fiscal_period,period_type,period_start,period_end\n"
        )
        fh.write("7,0000000007,2015,Q1,duration,2015-01-01,2015-04-03\n")
        fh.write("7,0000000007,2015,Q1,instant,2015-04-03,2015-04-03\n")
        fh.write(
            "7,0000000007,2014,FY,duration,2014-01-01,2014-12-31\n"
        )  # before the floor
        fh.write("8,0000000008,2015,FY,duration,2015-01-01,2015-12-31\n")
    assert pilot.calendar_keys(cal, 7, "revenue_sanity_resolved") == [
        ("Q", date(2015, 4, 3))
    ]
    assert pilot.calendar_keys(cal, 7, "total_assets_resolved") == [
        ("I", date(2015, 4, 3))
    ]
    rows = [
        {"period_grain": "Q", "fsn_end": "2015-03-31", "id": 1},
        {"period_grain": "FY", "fsn_end": "2015-03-31", "id": 2},
    ]
    assert (
        pilot._match(rows, "Q", date(2015, 4, 3))["id"] == 1
    )  # KO-style 52-53 week end
    assert pilot._match(rows, "Q", date(2015, 6, 30)) is None


@pytest.mark.unit
def test_done_gate_company_criteria_1_2_5_fail_every_pair_of_the_company():
    def rep(cid, cik, loaded=True, derived=None):
        return {
            "company_id": cid,
            "cik": cik,
            "done_criteria": {
                "1_store_loaded": loaded,
                "5_derived_without_same_basis_by_point": derived or {},
            },
            "template_coverage": {"per_data_point": {"revenue_sanity_resolved": {"keys": 4, "valued": 4}}},
        }

    reports = [
        rep(1, "A"),
        rep(2, "B", loaded=False),
        rep(3, "C"),
        rep(4, "D"),
        rep(5, "E", derived={"revenue_sanity_resolved": 2}),
        rep(6, "F"),
        # a derived cell of a data point the write does not switch does not stop the company (criterion 5 scope)
        rep(7, "G", derived={"total_liabilities_resolved": 9}),
    ]
    gaps = [
        {"company_id": "4", "data_point": "revenue_sanity_resolved"},
        # a reasonless key outside the written data points does not stop the switch
        {"company_id": "6", "data_point": "total_debt_resolved"},
    ]
    missing = {"C": [{"accession": "x"}], "A": []}
    got = pilot.done_gate(reports, gaps, missing, {"revenue_sanity_resolved"})
    assert {c: g["company"] for c, g in got.items()} == {
        1: [],
        2: ["1_store_not_loaded"],
        3: ["2_filings_not_stored:1"],
        4: [],
        5: ["5_derived_without_same_basis:2"],
        6: [],
        7: [],
    }
    assert pilot.done_pairs(got) == [
        (1, "revenue_sanity_resolved"),
        (6, "revenue_sanity_resolved"),
        (7, "revenue_sanity_resolved"),
    ]
    assert got[4]["data_points"]["revenue_sanity_resolved"] == ["4_reasonless_keys:1"]
    assert got[3]["data_points"]["revenue_sanity_resolved"] == ["company:2_filings_not_stored:1"]
