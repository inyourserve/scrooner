"""Derived 3-month quarters from served year-to-date cells (AAPL-shaped cash flow); EPS never; missing input no cell."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper.derived_quarters import add_derived_quarters

D = date
CFO, EPS = 1, 2
INFO = {
    CFO: ("cfo_resolved", "cash_flow"),
    EPS: ("diluted_eps_resolved", "income_statement"),
}
FY0 = D(2023, 10, 1)
# period id -> (start, end, type)
PERIODS = {
    1: (FY0, D(2023, 12, 30), "duration"),  # Q1
    2: (FY0, D(2024, 3, 30), "duration"),  # 6M
    3: (FY0, D(2024, 6, 29), "duration"),  # 9M
    4: (FY0, D(2024, 9, 28), "duration"),  # FY
    12: (D(2023, 12, 31), D(2024, 3, 30), "duration"),  # Q2
    13: (D(2024, 3, 31), D(2024, 6, 29), "duration"),  # Q3
    14: (D(2024, 6, 30), D(2024, 9, 28), "duration"),  # Q4
}


def _cell(cid, pid, value, fid):
    return {
        "canonical_concept_id": cid,
        "period_id": pid,
        "value": Decimal(value),
        "value_source": "sec_api",
        "source_fact_ids": [fid],
        "source_value_ids": [],
    }


def _stats():
    return {"held": [], "blanks": []}


def _ytd(cid, vals):
    return [_cell(cid, p, v, 100 + p) for p, v in zip((1, 2, 3, 4), vals)]


def test_aapl_shaped_cfo_q2_q3_q4_derived():
    cells = _ytd(CFO, ("39895", "62585", "91443", "118254"))
    assert add_derived_quarters(cells, _stats(), INFO, PERIODS) == 3
    got = {c["period_id"]: c for c in cells if c["period_id"] > 10}
    assert got[12]["value"] == Decimal(22690)
    assert got[13]["value"] == Decimal(28858)
    assert got[14]["value"] == Decimal(26811)
    assert got[14]["value_source"] == "derived_quarter"
    assert got[14]["source_fact_ids"] == [103, 104]


def test_eps_is_never_derived():
    cells = _ytd(EPS, ("1.0", "2.0", "3.0", "4.0"))
    assert add_derived_quarters(cells, _stats(), INFO, PERIODS) == 0
    assert len(cells) == 4


def test_missing_input_gives_no_cell_and_keeps_the_blank():
    cells = [c for c in _ytd(CFO, ("1", "3", "6", "10")) if c["period_id"] != 3]
    stats = _stats()
    stats["blanks"] = [{"canonical_concept_id": CFO, "period_id": 13}]
    assert add_derived_quarters(cells, stats, INFO, PERIODS) == 1  # Q2 only
    assert [c["period_id"] for c in cells if c["period_id"] > 10] == [12]
    assert stats["blanks"] == [{"canonical_concept_id": CFO, "period_id": 13}]


def test_derived_blank_is_replaced_by_the_cell():
    cells = _ytd(CFO, ("1", "3", "6", "10"))
    stats = _stats()
    stats["blanks"] = [{"canonical_concept_id": CFO, "period_id": 14}]
    add_derived_quarters(cells, stats, INFO, PERIODS)
    assert stats["blanks"] == []


def test_component_served_held_and_instant_skipped():
    cells = _ytd(CFO, ("1", "3", "6", "10"))
    cells[0]["_from_components"] = True
    assert add_derived_quarters(cells, _stats(), INFO, PERIODS) == 2  # Q3, Q4 only
    cells = _ytd(CFO, ("1", "3", "6", "10"))
    cells.append(_cell(CFO, 12, "99", 5))  # already served: untouched
    stats = _stats()
    stats["held"] = [{"canonical_concept_id": CFO, "period_id": 13}]
    assert add_derived_quarters(cells, stats, INFO, PERIODS) == 1
    assert next(c for c in cells if c["period_id"] == 12)["value"] == Decimal(99)
    info = {CFO: ("total_assets_resolved", "balance_sheet")}
    assert (
        add_derived_quarters(_ytd(CFO, ("1", "3", "6", "10")), _stats(), info, PERIODS)
        == 0
    )
