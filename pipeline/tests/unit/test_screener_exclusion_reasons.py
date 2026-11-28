"""Whole-company exclusion reasons on snapshot rows (SYSTEMS.md #17)."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.screener import snapshot as snap


def _info(status):
    return {
        "cik": "1",
        "company_name": "X",
        "sic_code": "1",
        "sic_description": "d",
        "sector": "Technology",
        "status": status,
        "ticker": "X",
    }


VALUE = {
    "value": Decimal("1"),
    "period_label": "FY2024",
    "period_end": date(2024, 12, 31),
    "formula_version": 1,
}


@pytest.mark.unit
def test_reason_for_each_kind_of_company():
    assert snap.exclusion_reason("active", 3) is None
    assert snap.exclusion_reason("inactive", 3) == snap.EXCLUDED_INACTIVE
    assert snap.exclusion_reason(None, 3) == snap.EXCLUDED_INACTIVE
    assert snap.exclusion_reason("active", 0) == snap.EXCLUDED_NO_METRIC_VALUES
    # inactive wins: it is the reason the default screen leaves it out
    assert snap.exclusion_reason("inactive", 0) == snap.EXCLUDED_INACTIVE


@pytest.mark.unit
def test_rows_carry_the_reason_in_column_order_and_nothing_is_unexplained():
    identity = {1: _info("active"), 2: _info("active"), 3: _info("delisted")}
    metrics = {1: {"roe": VALUE}}
    rows, reasons = snap._company_rows(identity, metrics, ["roe"], 7, True)
    by_id = {r[0]: r for r in rows}
    # (..., ticker, exclusion_reason, dataset_version, roe x4)
    assert by_id[1][8:10] == (None, 7) and by_id[1][10] == Decimal("1")
    assert by_id[2][8:10] == (snap.EXCLUDED_NO_METRIC_VALUES, 7)
    assert by_id[3][8:10] == (snap.EXCLUDED_INACTIVE, 7)
    assert reasons.get(snap.UNEXPLAINED, 0) == 0
    assert reasons[snap.EXCLUDED_NO_METRIC_VALUES] == 1

    without, _ = snap._company_rows(identity, metrics, ["roe"], 7, False)
    assert without[0][8] == 7  # no reason column before the migration is applied


@pytest.mark.unit
def test_a_company_with_no_value_and_no_reason_is_counted_unexplained(monkeypatch):
    monkeypatch.setattr(snap, "exclusion_reason", lambda status, n: None)
    _, reasons = snap._company_rows({1: _info("active")}, {}, ["roe"], 1, True)
    assert reasons[snap.UNEXPLAINED] == 1
