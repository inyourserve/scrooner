"""Income-statement absent-line reasons (Dhairya 2026-11-09, queue item a): PR #4's
select.absent_line_cell ported to the income statement with a tag/label line classifier
(pilot.is_line_class, classify_is_filing). A reason is claimed only when the filing's primary
income statement is located and prints no line of the concept's family; any line that may be
the concept blocks the claim. A key that has a cell is never touched (Ritwik C2: the pilot calls
absent_line_cell only when select left the key without a row)."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from scrooner_pipeline.fsn_store import pilot
from scrooner_pipeline.fsn_store import select as sel

FY = date(2024, 12, 31)


def _data(mapped=(), stmts=("IS",)):
    f = {
        1: sel.Filing(1, "0000000001-25-000001", datetime(2025, 2, 1), "10-K", FY, 2024, "FY"),
        2: sel.Filing(2, "0000000001-25-000002", datetime(2025, 5, 1), "10-Q", date(2025, 3, 31), 2025, "Q1"),
    }
    cols = set()
    for st in stmts:
        cols |= {(1, st, FY, 4), (2, st, date(2025, 3, 31), 1)}
    return {"filings": f, "face_cols": cols, "mapped_filings": {c: set(mapped) for c in pilot.IS_ABSENT_CONCEPTS}}


def _rows(*lines, report=2):
    """(report, line, tag, label, custom, negating) of one filing's IS, with a net income anchor."""
    out = [(report, i, t, lab, False, False) for i, (t, lab) in enumerate(lines, 1)]
    out.append((report, 99, "NetIncomeLoss", "Net income", False, False))
    return out


# ---------------------------------------------------------------- the line classifier


@pytest.mark.unit
@pytest.mark.parametrize(
    "concept, tag, label, want",
    [
        ("revenue_sanity_resolved", "Revenues", "Total revenues", "common"),
        ("revenue_sanity_resolved", "acme_ProductSales", "Product sales", "common"),
        ("revenue_sanity_resolved", "CostOfRevenue", "Cost of sales", None),
        ("revenue_sanity_resolved", "acme_CostOfProductsSold", "Cost of sales", None),  # label rule, custom tag
        ("revenue_sanity_resolved", "OperatingExpenses", "Operating expenses", None),
        ("cost_of_revenue_resolved", "CostOfGoodsAndServicesSold", "Cost of goods sold", "common"),
        ("cost_of_revenue_resolved", "acme_CostOfProducts", "Cost of products", "common"),
        ("cost_of_revenue_resolved", "CostsAndExpenses", "Total costs and expenses", "combined"),
        ("cost_of_revenue_resolved", "OperatingExpenses", "Operating expenses", None),
        ("interest_expense_resolved", "InterestExpense", "Total interest expense", "common"),
        ("interest_expense_resolved", "InterestExpenseNonoperating", "Interest expense, net", "common"),
        ("interest_expense_resolved", "InterestIncomeExpenseNet", "Net interest income", "net"),
        ("interest_expense_resolved", "acme_InterestAndOther", "Interest and other, net", "net"),
        ("interest_expense_resolved", "acme_FinancingCosts", "Interest on borrowings", "common"),
        ("interest_expense_resolved", "SellingGeneralAndAdministrativeExpense", "SG&A", None),
        ("net_income_resolved", "ProfitLoss", "Net income including NCI", "common"),
        ("basic_eps_resolved", "EarningsPerShareBasic", "Basic", "common"),
        ("basic_eps_resolved", "acme_Eps", "Net income per common share", "common"),
        ("basic_eps_resolved", "NetIncomeLossPerOutstandingLimitedPartnershipUnitBasicNetOfTax",
         "Net income per limited partner unit", "unresolved"),  # fmt: skip
    ],
)
def test_is_line_class(concept, tag, label, want):
    assert pilot.is_line_class(concept, tag, label) == want


@pytest.mark.unit
def test_classify_reads_only_the_primary_statement_and_skips_shape_rows():
    rows = _rows(("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenue"),
                 ("IncomeStatementAbstract", "Revenue and costs"))  # fmt: skip
    # a second IS report (a segment table) printing a cost line never counts
    rows += [(5, 1, "CostOfRevenue", "Cost of revenue", False, False), (5, 2, "NetIncomeLoss", "Net income", False, False)]
    got = pilot.classify_is_filing(rows)
    assert got["revenue_sanity_resolved"] == ["common"]
    assert got["cost_of_revenue_resolved"] == []  # the shape row "Revenue and costs" is not a line
    assert got["net_income_resolved"] == ["common"]


@pytest.mark.unit
def test_a_filing_without_an_anchored_statement_claims_nothing():
    got = pilot.classify_is_filing([(2, 1, "Revenues", "Revenues", False, False)])
    assert set(got) == set(pilot.IS_ABSENT_CONCEPTS)
    assert all(v == ["no_statement"] for v in got.values())
    assert sel.absent_line_cell("cost_of_revenue_resolved", "FY", FY, _data(), {1: ["no_statement"]}, stmt="IS") is None


# ---------------------------------------------------------------- the absent-line cell on the income statement


@pytest.mark.unit
@pytest.mark.parametrize(
    "concept, lines, state, reason",
    [
        # a services company prints revenue and operating expenses, no cost-of-revenue line at all
        ("cost_of_revenue_resolved", [("Revenues", "Revenues"), ("OperatingExpenses", "Operating expenses")],
         "not_presented", "line_not_presented_in_filing"),  # fmt: skip
        # only a total costs line spans cost of revenue and the other costs
        ("cost_of_revenue_resolved", [("Revenues", "Revenues"), ("CostsAndExpenses", "Costs and expenses")],
         "not_presented", "line_presented_combined_with_others"),  # fmt: skip
        # a bank printing net interest income only
        ("interest_expense_resolved", [("InterestIncomeExpenseNet", "Net interest income")],
         "defect", "perimeter_line_unresolved"),  # fmt: skip
        ("interest_expense_resolved", [("Revenues", "Revenues")], "not_presented", "line_not_presented_in_filing"),
        # a partnership printing per-unit earnings, not per-share
        ("basic_eps_resolved", [("NetIncomeLossPerOutstandingLimitedPartnershipUnitBasicNetOfTax",
                                 "Net income per limited partner unit")], "defect", "perimeter_line_unresolved"),  # fmt: skip
    ],
)
def test_is_absent_line_reasons(concept, lines, state, reason):
    classes = pilot.classify_is_filing(_rows(*lines))[concept]
    c = sel.absent_line_cell(concept, "FY", FY, _data(), {1: classes}, stmt="IS")
    assert c is not None and (c.state, c.reason_code, c.value) == (state, reason, None)
    assert c.input_refs["accessions"] == ["0000000001-25-000001"]


@pytest.mark.unit
def test_no_is_claim_when_a_line_may_be_the_concept_or_maps_or_only_cf_columns():
    common = pilot.classify_is_filing(_rows(("acme_FinancingCosts", "Interest on borrowings")))
    assert sel.absent_line_cell("interest_expense_resolved", "FY", FY, _data(),
                                {1: common["interest_expense_resolved"]}, stmt="IS") is None  # fmt: skip
    # a line maps in that filing: select owns the key
    assert sel.absent_line_cell("cost_of_revenue_resolved", "FY", FY, _data(mapped=[1]), {1: []}, stmt="IS") is None
    # cash-flow face columns are not evidence about the income statement
    assert sel.absent_line_cell("cost_of_revenue_resolved", "FY", FY, _data(stmts=("CF",)), {1: []}, stmt="IS") is None
    # the cash-flow default is unchanged
    assert sel.absent_line_cell("cost_of_revenue_resolved", "FY", FY, _data(stmts=("CF",)), {1: []}) is not None


@pytest.mark.unit
def test_q_key_uses_the_quarter_filing():
    c = sel.absent_line_cell("cost_of_revenue_resolved", "Q", date(2025, 3, 31), _data(), {2: []}, stmt="IS")
    assert c is not None and c.qtrs == 1 and c.input_refs["accessions"] == ["0000000001-25-000002"]


@pytest.mark.unit
@pytest.mark.parametrize("classes", [[], ["combined"], ["net"], ["unresolved"]])
def test_the_cell_loader_accepts_every_is_absent_line_row(classes):
    from scrooner_pipeline.normalizer import cell_loader

    c = sel.absent_line_cell("cost_of_revenue_resolved", "FY", FY, _data(), {1: classes}, stmt="IS")
    got = cell_loader.parse_row(1, sel.to_row(c, 1, _data()["filings"]), {"cost_of_revenue_resolved"})
    assert not isinstance(got, str), got


@pytest.mark.unit
def test_report_company_routes_is_concepts_to_the_income_statement():
    src = open(pilot.__file__).read()
    assert 'stmt="IS" if concept in IS_ABSENT_CONCEPTS else "CF"' in src
    assert "**is_line_classes(conn, company_id)" in src
