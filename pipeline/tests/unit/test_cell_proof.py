"""Cell proof verdicts on a synthetic filing structure (pure)."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

ADSH = "0000320193-25-000073"
FY_END = date(2025, 9, 27)
DDATE = date(2025, 9, 30)  # FSN rounds period ends to the month end


def structure():
    s = FilingStructure(ADSH, "0000320193", "10-K", date(2025, 10, 31), FY_END)
    pre = [
        ("IS", 1, "RevenueFromContractWithCustomerExcludingAssessedTax", "Net sales"),
        ("IS", 2, "CostOfGoodsAndServicesSold", "Cost of sales"),
        ("IS", 3, "GrossProfit", "Gross margin"),
        ("IS", 4, "OperatingExpenses", "Total operating expenses"),
        ("IS", 5, "OperatingIncomeLoss", "Operating income"),
        ("IS", 6, "NetIncomeLoss", "Net income"),
        ("IS", 7, "EarningsPerShareDiluted", "Diluted"),
        ("BS", 1, "AssetsCurrent", "Total current assets"),
        ("BS", 2, "Assets", "Total assets"),
        ("BS", 3, "Liabilities", "Total liabilities"),
        ("BS", 4, "StockholdersEquity", "Total shareholders' equity"),
        (
            "BS",
            5,
            "LiabilitiesAndStockholdersEquity",
            "Total liabilities and shareholders' equity",
        ),
    ]
    for stmt, line, tag, label in pre:
        s.pre.append(
            PreLine(
                2 if stmt == "IS" else 4, line, stmt, tag, "us-gaap/2025", label, False
            )
        )
    # calc: gross profit = revenue - cost; operating income = gross profit - opex; L&SE = L + SE
    s.calc_children["GrossProfit"] = [
        ("RevenueFromContractWithCustomerExcludingAssessedTax", False),
        ("CostOfGoodsAndServicesSold", True),
    ]
    s.calc_children["OperatingIncomeLoss"] = [
        ("GrossProfit", False),
        ("OperatingExpenses", True),
    ]
    s.calc_children["LiabilitiesAndStockholdersEquity"] = [
        ("Liabilities", False),
        ("StockholdersEquity", False),
    ]
    for parent, kids in s.calc_children.items():
        for k, _ in kids:
            s.calc_parents[k].add(parent)
    vals = {
        ("RevenueFromContractWithCustomerExcludingAssessedTax", 4): "416161000000",
        ("CostOfGoodsAndServicesSold", 4): "220000000000",
        ("GrossProfit", 4): "196161000000",
        ("OperatingExpenses", 4): "62000000000",
        ("OperatingIncomeLoss", 4): "134161000000",
        ("NetIncomeLoss", 4): "112010000000",
        ("AssetsCurrent", 0): "150000000000",
        ("Assets", 0): "359241000000",
        ("Liabilities", 0): "285000000000",
        ("StockholdersEquity", 0): "74241000000",
        ("LiabilitiesAndStockholdersEquity", 0): "359241000000",
    }
    for (tag, q), v in vals.items():
        s.num[(tag, DDATE, q)].append(
            NumValue(tag, "us-gaap/2025", DDATE, q, "USD", Decimal(v), -6)
        )
    s.num[("EarningsPerShareDiluted", DDATE, 4)].append(
        NumValue(
            "EarningsPerShareDiluted",
            "us-gaap/2025",
            DDATE,
            4,
            "USD",
            Decimal("7.46"),
            2,
        )
    )
    return s


def shown(name, value, grain="FY", tags=("x",), end=FY_END, derived=False):
    start = date(2024, 9, 29) if grain != "I" else end
    return pv.Shown(
        3, name, grain, start, end, Decimal(value), tuple(tags), ADSH, (1,), derived, 6
    )


@pytest.mark.unit
def test_total_proven_with_components_and_identity():
    p = pv.prove_cell(
        shown("total_assets_resolved", "359241000000", "I"), structure(), "2025q4"
    )
    assert p.verdict == pv.PROVEN
    assert p.position_tag == "Assets" and p.checks["identity_tie"]["status"] == "pass"
    assert (
        p.checks["components_sum"]["status"] == "n/a"
    )  # Assets has no calc children here


@pytest.mark.unit
def test_gross_profit_components_sum_passes_and_opex_component_is_not_a_total_problem():
    p = pv.prove_cell(
        shown("gross_profit_resolved", "196161000000"), structure(), "2025q4"
    )
    assert p.verdict == pv.PROVEN and p.checks["components_sum"]["status"] == "pass"
    # a value a million off is within the filer's dcml -6 slack (1.5M)
    p2 = pv.prove_cell(
        shown("gross_profit_resolved", "196162000000"), structure(), "2025q4"
    )
    assert p2.verdict == pv.PROVEN


@pytest.mark.unit
def test_wrong_shown_value_disagrees_with_a_reason_and_both_tags_recorded():
    p = pv.prove_cell(
        shown("net_income_resolved", "99000000000", tags=("ProfitLoss",)),
        structure(),
        "2025q4",
    )
    assert (
        p.verdict == pv.DISAGREE and p.reason_code == "shown_differs_from_printed_line"
    )
    row = p.row()
    assert row["shown_tag"] == "ProfitLoss" and row["position_tag"] == "NetIncomeLoss"
    assert "99000000000" in p.reason_text and "112010000000" in p.reason_text


@pytest.mark.unit
def test_component_concept_is_proven_without_being_a_total():
    p = pv.prove_cell(
        shown("cost_of_revenue_resolved", "220000000000"), structure(), "2025q4"
    )
    assert p.verdict == pv.PROVEN and p.fsn_calc_parent == "GrossProfit"


@pytest.mark.unit
def test_missing_line_is_not_presented_and_wrong_duration_disagrees():
    p = pv.prove_cell(
        shown("interest_expense_resolved", "1000000"), structure(), "2025q4"
    )
    assert (
        p.verdict == pv.NOT_PRESENTED
        and p.reason_code == "line_not_presented_on_statement"
    )
    q = pv.prove_cell(
        shown("net_income_resolved", "28000000000", grain="Q"), structure(), "2025q4"
    )
    assert q.verdict == pv.DISAGREE and q.reason_code == "period_length_mismatch"


@pytest.mark.unit
def test_identity_failure_blocks_proof_even_when_values_match():
    s = structure()
    s.num[("LiabilitiesAndStockholdersEquity", DDATE, 0)] = [
        NumValue(
            "LiabilitiesAndStockholdersEquity",
            "us-gaap/2025",
            DDATE,
            0,
            "USD",
            Decimal("300000000000"),
            -6,
        )
    ]
    p = pv.prove_cell(
        shown("total_liabilities_resolved", "285000000000", "I"), s, "2025q4"
    )
    assert p.verdict == pv.DISAGREE and p.reason_code == "check_failed:identity_tie"


@pytest.mark.unit
def test_per_share_uses_usd_per_share_and_dcml_precision():
    p = pv.prove_cell(
        shown("diluted_eps_resolved", "7.46", tags=("EarningsPerShareDiluted",)),
        structure(),
        "2025q4",
    )
    assert p.verdict == pv.PROVEN and p.checks["unit_scale"]["uom"] == "USD"
    p2 = pv.prove_cell(shown("diluted_eps_resolved", "7.50"), structure(), "2025q4")
    assert p2.verdict == pv.DISAGREE  # 0.04 apart on a 2-decimal figure (slack 0.015)


@pytest.mark.unit
def test_unchecked_cases():
    assert (
        pv.prove_cell(shown("net_income_resolved", "1"), None, None).verdict
        == pv.UNCHECKED
    )
    assert (
        pv.prove_cell(
            shown("net_income_resolved", "1", derived=True), structure(), "x"
        ).verdict
        == pv.UNCHECKED
    )
    assert (
        pv.prove_cell(shown("total_debt_resolved", "1", "I"), structure(), "x").verdict
        == pv.UNCHECKED
    )


@pytest.mark.unit
def test_total_under_a_non_candidate_total_is_component_only_and_equity_keeps_its_definition():
    s = structure()
    # revenue presented only as a component of a CUSTOM "Total revenues" line
    s.calc_parents["RevenueFromContractWithCustomerExcludingAssessedTax"] = {
        "abc_TotalRevenues"
    }
    s.custom_parents["RevenueFromContractWithCustomerExcludingAssessedTax"] = {
        "abc_TotalRevenues"
    }
    line, why = pv.select_position(s, "revenue_sanity_resolved")
    assert line is None and why == "component_only"
    # a us-gaap parent outside the listed chain is a higher aggregate, not a component
    s3 = structure()
    s3.calc_parents["OperatingIncomeLoss"] = {
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
    }
    line3, _ = pv.select_position(s3, "operating_income_resolved")
    assert line3 is not None and line3.tag == "OperatingIncomeLoss"
    # equity: StockholdersEquity sits under the total incl. NCI (a candidate): still the expected line
    s2 = structure()
    s2.pre.append(
        PreLine(
            4,
            6,
            "BS",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "us-gaap/2025",
            "Total equity",
            False,
        )
    )
    s2.calc_children[
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
    ] = [("StockholdersEquity", False), ("MinorityInterest", False)]
    s2.calc_parents["StockholdersEquity"] = {
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
    }
    line2, _ = pv.select_position(s2, "stockholders_equity_resolved")
    assert line2 is not None and line2.tag == "StockholdersEquity"


@pytest.mark.unit
def test_fsn_ddate_rounds_to_the_nearest_month_end():
    from scrooner_pipeline.proof.fsn import fsn_ddate

    assert fsn_ddate(date(2025, 9, 27)) == date(2025, 9, 30)
    assert fsn_ddate(date(2024, 1, 2)) == date(2023, 12, 31)
    assert fsn_ddate(date(2024, 12, 31)) == date(2024, 12, 31)
    assert fsn_ddate(date(2024, 6, 29)) == date(2024, 6, 30)


@pytest.mark.unit
def test_components_sum_is_checked_per_calc_group_not_across_groups():
    s = structure()
    ibt = "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"
    s.pre.append(
        PreLine(
            2,
            8,
            "IS",
            ibt,
            "us-gaap/2025",
            "Income before provision for income taxes",
            False,
        )
    )
    s.calc_groups[ibt]["4"] = [
        ("OperatingIncomeLoss", False),
        ("NonoperatingIncomeExpense", False),
    ]
    s.calc_groups[ibt]["9"] = [
        ("IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic", False),
        ("IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign", False),
    ]
    s.calc_children[ibt] = s.calc_groups[ibt]["4"] + s.calc_groups[ibt]["9"]
    for tag, v in (
        ("NonoperatingIncomeExpense", "1000000000"),
        (ibt, "135161000000"),
        ("IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic", "100000000000"),
        ("IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign", "35161000000"),
    ):
        s.num[(tag, DDATE, 4)].append(
            NumValue(tag, "us-gaap/2025", DDATE, 4, "USD", Decimal(v), -6)
        )
    p = pv.prove_cell(shown("income_before_tax_resolved", "135161000000"), s, "2025q4")
    assert p.verdict == pv.PROVEN and p.checks["components_sum"]["status"] == "pass"
    s.num[("NonoperatingIncomeExpense", DDATE, 4)] = [
        NumValue(
            "NonoperatingIncomeExpense",
            "us-gaap/2025",
            DDATE,
            4,
            "USD",
            Decimal("5000000000"),
            -6,
        )
    ]
    assert (
        pv.prove_cell(
            shown("income_before_tax_resolved", "135161000000"), s, "2025q4"
        ).verdict
        == pv.PROVEN
    )


def _q3_structure():
    s = FilingStructure(
        "0000320193-25-000073",
        "0000320193",
        "10-Q",
        date(2025, 8, 1),
        date(2025, 6, 28),
    )
    s.pre.append(
        PreLine(2, 6, "IS", "NetIncomeLoss", "us-gaap/2025", "Net income", False)
    )
    d = date(2025, 6, 30)  # FSN month end of 2025-06-28
    s.num[("NetIncomeLoss", d, 3)].append(
        NumValue(
            "NetIncomeLoss", "us-gaap/2025", d, 3, "USD", Decimal("84000000000"), -6
        )
    )
    return s


@pytest.mark.unit
def test_derived_q4_is_proven_through_the_two_year_to_date_lines():
    fy = structure()  # NetIncomeLoss FY = 112,010M at 2025-09-30
    q4 = pv.Shown(
        3,
        "net_income_resolved",
        "Q",
        date(2025, 6, 29),
        FY_END,
        Decimal("28010000000"),
        ("NetIncomeLoss",),
        ADSH,
        (9,),
        True,
        6,
    )
    p = pv.prove_cell(q4, fy, "2025q4", _q3_structure())
    assert (
        p.verdict == pv.PROVEN
        and p.position_source == "derived_inputs"
        and p.position_value == Decimal("28010000000")
    )
    wrong = pv.Shown(
        3,
        "net_income_resolved",
        "Q",
        date(2025, 6, 29),
        FY_END,
        Decimal("26000000000"),
        ("NetIncomeLoss",),
        ADSH,
        (9,),
        True,
        6,
    )
    p2 = pv.prove_cell(wrong, fy, "2025q4", _q3_structure())
    assert (
        p2.verdict == pv.DISAGREE
        and p2.reason_code == "derived_quarter_differs_from_inputs"
    )
    p3 = pv.prove_cell(q4, fy, "2025q4", None)
    assert p3.verdict == pv.UNCHECKED and "prior filing not loaded" in p3.reason_text
