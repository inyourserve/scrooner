"""A component sum with a custom (fsn_xbrl) part takes ALL parts from the latest filing that prints every part,
not from the filing the custom part came from (MSFT opex FY2016/17: served 32,358 / 33,363 from the FY2016/17 10-Ks,
the FY2018 10-K restates them 32,296 / 33,285; it prints the impairment line under a renamed custom tag)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from scrooner_pipeline.mapper.company_tag_map import (
    Fact,
    MapRow,
    _single_source_parts,
    build_cells,
)


def _fact(vid, acc, filed, value):
    return Fact(
        Decimal(value),
        vid,
        date(2016, 6, 30),
        False,
        vid,
        acc,
        filed,
        source="fsn_xbrl",
    )


def _row(tax, tag):
    return MapRow(tax, tag, "IS", "component", None, 1, 1, date(2015, 1, 1), None)


OLD, NEW = "0001564590-17-014900", "0001564590-18-019062"
D_OLD, D_NEW = date(2017, 8, 2), date(2018, 8, 3)
OLD_TAG = "ImpairmentIntegrationAndRestructuringExpenses"
NEW_TAG = "ImpairmentAndRestructuringExpenses"


def _world():
    vint = {
        ("us-gaap", "ResearchAndDevelopmentExpense"): {
            1: [_fact(2, NEW, D_NEW, 11988), _fact(1, OLD, D_OLD, 11988)]
        },
        ("us-gaap", "SellingAndMarketingExpense"): {
            1: [_fact(4, NEW, D_NEW, 14635), _fact(3, OLD, D_OLD, 14697)]
        },
        ("custom", OLD_TAG): {1: [_fact(5, OLD, D_OLD, 1110)]},
        ("custom", NEW_TAG): {1: [_fact(6, NEW, D_NEW, 1110)]},
    }
    comps = [
        (_row("us-gaap", "ResearchAndDevelopmentExpense"), vint[("us-gaap", "ResearchAndDevelopmentExpense")][1][1]),
        (_row("us-gaap", "SellingAndMarketingExpense"), vint[("us-gaap", "SellingAndMarketingExpense")][1][1]),
        (_row("custom", OLD_TAG), vint[("custom", OLD_TAG)][1][0]),
    ]
    return comps, vint


def test_parts_come_from_the_latest_filing_printing_all_parts_through_a_renamed_tag():
    comps, vint = _world()
    got = _single_source_parts(comps, vint, 1)
    assert got is not None
    assert {f.accession for _, f in got} == {NEW}
    assert sum(f.value for _, f in got) == Decimal(11988 + 14635 + 1110)


def test_without_the_later_print_the_custom_filing_is_used():
    comps, vint = _world()
    vint = {k: v for k, v in vint.items() if k != ("custom", NEW_TAG)}
    got = _single_source_parts(comps, vint, 1)
    assert got is not None and {f.accession for _, f in got} == {OLD}


# ---- S9: a face-line sum with no single calc parent (cash-flow D&A = Depreciation + Amortization) --------------------
DA_ID = 31
DA_INFO = {DA_ID: ("depreciation_and_amortization", "cash_flow")}


def _da(arcs):
    def f(v, i):
        return Fact(Decimal(v), i, date(2023, 12, 31), False, 10, "A-10")

    rows = [
        MapRow("us-gaap", "Dep", "CF", "component", None, DA_ID, 1, date(2015, 1, 1), None, "P1"),
        MapRow("us-gaap", "Amort", "CF", "component", None, DA_ID, 1, date(2015, 1, 1), None, "P2"),
    ]
    facts = {("us-gaap", "Dep"): {7: f("700", 1)}, ("us-gaap", "Amort"): {7: f("66", 2)}}
    return build_cells(rows, facts, DA_INFO, arcs, {})


def test_face_line_sum_without_single_calc_parent_is_served_for_any_concept():
    cells, stats = _da({"A-10": {("P1", "Dep"), ("P2", "Amort")}})
    assert [c["value"] for c in cells] == [Decimal("766")] and stats["held"] == []
    cells, stats = _da({"A-10": {("P1", "Dep")}})  # Amort is no line of the filing's statements
    assert cells == [] and stats["held"][0]["reason"] == "components_without_single_calc_parent"


# ---- S12: operating expenses from cost of revenue to operating income (no gross profit line) ----------------------
ERA = date(2015, 1, 1)
OPEX_ID, REV_ID, COR_ID, OI_ID = 21, 22, 23, 24
INFO = {
    OPEX_ID: ("operating_expenses_resolved", "income_statement"),
    REV_ID: ("revenue_sanity_resolved", "income_statement"),
    COR_ID: ("cost_of_revenue", "income_statement"),
    OI_ID: ("operating_income", "income_statement"),
}


def _no_gp(revenue, cor, a, b, oi):
    def f(v, i):
        return Fact(Decimal(v), i, date(2023, 12, 31), False, 10, "A-10")

    rows = [
        MapRow("us-gaap", "Revenues", "IS", "concept", REV_ID, None, 1, ERA, None),
        MapRow("us-gaap", "CostOfRevenue", "IS", "concept", COR_ID, None, 1, ERA, None),
        MapRow("us-gaap", "OperatingIncomeLoss", "IS", "concept", OI_ID, None, 1, ERA, None),
        MapRow("us-gaap", "M", "IS", "component", None, OPEX_ID, 1, ERA, None, "P1"),
        MapRow("us-gaap", "G", "IS", "component", None, OPEX_ID, 1, ERA, None, "P2"),
    ]
    facts = {
        ("us-gaap", "Revenues"): {7: f(revenue, 1)},
        ("us-gaap", "CostOfRevenue"): {7: f(cor, 2)},
        ("us-gaap", "OperatingIncomeLoss"): {7: f(oi, 3)},
        ("us-gaap", "M"): {7: f(a, 4)},
        ("us-gaap", "G"): {7: f(b, 5)},
    }
    arcs = {"A-10": {("P1", "M"), ("P2", "G")}}  # no single parent
    return build_cells(rows, facts, INFO, arcs, {})


def test_opex_without_gross_profit_ties_from_cost_of_revenue_to_operating_income():
    cells, stats = _no_gp("1000", "600", "150", "100", "150")  # 1000-600-250 = 150
    got = {c["canonical_concept_id"]: c["value"] for c in cells}
    assert got[OPEX_ID] == Decimal("250") and stats["held"] == []
    cells, stats = _no_gp("1000", "600", "150", "100", "140")  # a line between COR and OI is missing
    assert OPEX_ID not in {c["canonical_concept_id"] for c in cells}
    assert "opex_components_do_not_tie_gross_profit_to_operating_income" in {
        h["reason"] for h in stats["held"]
    }
