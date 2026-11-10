"""Validation of the history-source CSVs the tranche-1 apply script inserts (no database)."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("apply_t1", ROOT / "data-team/42-release-applies-2026-11-10/apply_history_tranche1.py")
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)
SRC = list(csv.DictReader(open(ROOT / "data-team/47-fsn-store/company_history_sources.csv")))
PER = list(csv.DictReader(open(ROOT / "data-team/47-fsn-store/company_history_periods.csv")))


@pytest.mark.unit
def test_sources_csv_is_valid_and_holds_40_plus_12():
    new = {ap.key_of(r) for r in SRC[40:]}
    assert len(new) == 12 and ap.validate_sources(SRC, None, new) == []
    assert len(SRC) == ap.EXPECTED_AFTER
    assert {r["company_id"] for r in SRC if r["source_cik"] == "0000909954"} == {"5779"}


@pytest.mark.unit
def test_validation_refuses_overlap_non_month_end_and_missing_company():
    bad = [dict(r) for r in SRC]
    kdp = next(r for r in bad if r["source_cik"] == "0000909954")
    kdp2 = dict(kdp, source_cik="0000000002", valid_from="2015-06-01")
    assert any("overlap" in p for p in ap.validate_sources([*bad, kdp2]))
    kdp["valid_to"] = "2015-12-30"
    assert any("month-end" in p for p in ap.validate_sources(bad, None, {ap.key_of(kdp)}))
    assert any("not in core.company" in p for p in ap.validate_sources(SRC, {1}))
    assert any("missing columns" in p for p in ap.validate_sources([{"company_id": "1"}]))


@pytest.mark.unit
def test_periods_for_the_new_predecessors_are_clean():
    assert ap.validate_periods(PER, {3639, 5779}) == []
    assert {int(r["company_id"]) for r in PER} >= {3639, 5779}
    bad = [dict(r) for r in PER if r["company_id"] == "5779"][:1]
    bad[0]["end_date"] = "2013-12-28"
    assert any("storage floor" in p for p in ap.validate_periods(bad, {5779}))
