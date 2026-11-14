"""One sign per concept (data-team/tags/line_map/rules/polarity.csv): the serve path and the proof apply the SAME
table (common/polarity.py). VRTX 2021: InterestIncomeExpenseNet printed -61.5M is interest_expense +61.5M."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.common.polarity import apply_polarity, is_fixed_positive
from scrooner_pipeline.mapper.company_tag_map import Fact, MapRow, build_cells
from scrooner_pipeline.proof import prove as pv

from tests.unit.test_cell_proof_claims import ADSH, FY_END, cell, world

IE, TAX, OPEX, NET, CAPEX = 1, 2, 3, 4, 5
INFO = {
    IE: ("interest_expense", "income_statement"),
    TAX: ("income_tax_expense", "income_statement"),
    OPEX: ("operating_expenses", "income_statement"),
    NET: ("net_interest_income", "income_statement"),
    CAPEX: ("capex", "cash_flow"),
}
END = date(2021, 12, 31)
ERA = date(2015, 1, 1)
TAG = "InterestIncomeExpenseNet"


def concept(tag, concept_id, sign=1):
    return MapRow("us-gaap", tag, "IS", "concept", concept_id, None, sign, ERA, None)


def comp(tag, sign):
    return MapRow("us-gaap", tag, "CF", "component", None, CAPEX, sign, ERA, None, "Capex")


def fact(value, fid):
    return Fact(Decimal(value), fid, END, False, 10, "A-10")


@pytest.mark.unit
def test_table_reads_the_ruling_csv():
    assert is_fixed_positive("interest_expense") and is_fixed_positive("sga_expense_resolved")
    assert not is_fixed_positive("income_tax_expense") and not is_fixed_positive("net_interest_income")
    assert not is_fixed_positive("cfo") and not is_fixed_positive("interest_income")
    assert apply_polarity("interest_expense", Decimal("-61.5")) == (Decimal("61.5"), True)
    assert apply_polarity("interest_expense", Decimal("61.5")) == (Decimal("61.5"), False)
    assert apply_polarity("income_tax_expense", Decimal("-5")) == (Decimal("-5"), False)


@pytest.mark.unit
def test_serve_path_flips_a_single_element_expense_and_keeps_signed_concepts():
    rows = [concept(TAG, IE), concept("IncomeTaxExpenseBenefit", TAX), concept("NetInt", NET)]
    facts = {
        ("us-gaap", TAG): {7: fact("-61500000", 1)},
        ("us-gaap", "IncomeTaxExpenseBenefit"): {7: fact("-5", 2)},
        ("us-gaap", "NetInt"): {7: fact("-61500000", 3)},
    }
    cells, _ = build_cells(rows, facts, INFO, {}, {})
    by = {c["canonical_concept_id"]: c for c in cells}
    assert by[IE]["value"] == Decimal("61500000")
    assert "polarity_flip" in by[IE]["serve_note"] and "-61500000" in by[IE]["serve_note"]
    assert by[IE]["source_fact_ids"] == [1]  # the raw fact stays the lineage
    assert by[TAX]["value"] == Decimal("-5") and by[TAX]["serve_note"] is None  # a benefit is a real negative
    assert by[NET]["value"] == Decimal("-61500000")  # net interest stays signed
    cells, _ = build_cells([concept(TAG, IE)], {("us-gaap", TAG): {7: fact("61500000", 1)}}, INFO, {}, {})
    assert cells[0]["value"] == Decimal("61500000") and cells[0]["serve_note"] is None


@pytest.mark.unit
def test_a_row_sign_that_already_negates_is_not_flipped_twice():
    cells, _ = build_cells(
        [concept(TAG, IE, sign=-1)], {("us-gaap", TAG): {7: fact("-61500000", 1)}}, INFO, {}, {}
    )
    assert cells[0]["value"] == Decimal("61500000") and cells[0]["serve_note"] is None


@pytest.mark.unit
def test_a_component_sum_with_minus_weights_keeps_its_computed_sign():
    # parts carry their own weights: 10 - 30 = -20 is a real negative sum, never flipped
    rows = [comp("A", 1), comp("B", -1)]
    facts = {("us-gaap", "A"): {7: fact("10", 1)}, ("us-gaap", "B"): {7: fact("30", 2)}}
    arcs = {"A-10": {("Capex", "A"), ("Capex", "B")}}
    cells, _ = build_cells(rows, facts, INFO, arcs, {})
    assert [c["value"] for c in cells] == [Decimal("-20")]


@pytest.mark.unit
def test_the_proof_applies_the_same_table_vrtx_2021_interest_expense_proves():
    claim = pv.Claim("concept", "IS", tags=(TAG,))
    s = world(TAG, "USD", "-61500000", -5)
    ok = pv.prove_cell(cell("interest_expense_resolved", "61500000", claim), s, "2025q4")
    assert ok.verdict == pv.PROVEN and ok.position_value == Decimal("61500000")
    bad = pv.prove_cell(cell("interest_expense_resolved", "-61500000", claim), s, "2025q4")
    assert bad.verdict == pv.DISAGREE  # the fixed sign is positive: a negative shown value is wrong
    # a signed concept is proven as printed
    tax = pv.Claim("concept", "IS", tags=("IncomeTaxExpenseBenefit",))
    st = world("IncomeTaxExpenseBenefit", "USD", "-61500000", -5)
    assert pv.prove_cell(cell("income_tax_expense_resolved", "-61500000", tax), st, "2025q4").verdict == pv.PROVEN
    assert ADSH and FY_END
