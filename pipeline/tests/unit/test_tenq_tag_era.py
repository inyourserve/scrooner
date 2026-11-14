"""Rule 2 (Dhairya 2026-11-14): tag eras per filing, per period type. HD cash taxes: the 10-K prints the note tag
IncomeTaxesPaidNet from the switch year, the 10-Qs of that year still print the face tag IncomeTaxesPaid. A quarter
fact printed in an original 10-Q is judged by its own 10-Q's tag; the fiscal-year cell by the 10-K's."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper.company_tag_map import Fact, MapRow, build_cells

CP_ID = 40
INFO = {CP_ID: ("cash_paid_for_income_taxes", "cash_flow")}
Q1_END = date(2025, 5, 4)
FY_END = date(2026, 2, 1)


def _rows():
    old = MapRow(
        "us-gaap",
        "IncomeTaxesPaid",
        "CF",
        "concept",
        CP_ID,
        None,
        1,
        date(2024, 2, 4),
        date(2025, 2, 2),
    )
    new = MapRow(
        "us-gaap",
        "IncomeTaxesPaidNet",
        "UN",
        "concept",
        CP_ID,
        None,
        1,
        date(2025, 2, 3),
        None,
    )
    return [old, new]


def _facts(form: str):
    q = Fact(Decimal("900"), 1, Q1_END, False, 10, "Q-10", form=form, por=Q1_END)
    fy = Fact(Decimal("4848"), 2, FY_END, False, 11, "K-11", form="10-K", por=FY_END)
    return {
        ("us-gaap", "IncomeTaxesPaid"): {7: q},
        ("us-gaap", "IncomeTaxesPaidNet"): {8: fy},
    }


def test_quarter_keeps_the_tag_its_own_10q_prints_and_fy_takes_the_10k_tag():
    cells, _ = build_cells(_rows(), _facts("10-Q"), INFO, {}, {})
    got = {c["period_id"]: c["value"] for c in cells}
    assert got == {7: Decimal("900"), 8: Decimal("4848")}


def test_a_non_10q_fact_outside_the_row_era_is_not_admitted():
    cells, _ = build_cells(_rows(), _facts("10-K"), INFO, {}, {})
    assert {c["period_id"] for c in cells} == {8}
