"""Proof rules of the 2026-11-23 close-out (resolver .90): authority_tag_sum, authority_copy_role, printed_zero_note,
element_family. Pure. Each test fails with its rule removed (mutation-checked when added)."""

from datetime import date
from decimal import Decimal

import pytest
from scrooner_pipeline.proof import prove as pv
from scrooner_pipeline.proof import rules
from scrooner_pipeline.proof import shown as sh
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

D = Decimal


@pytest.mark.unit
def test_a_cell_of_several_source_tags_is_judged_as_their_signed_sum():
    # TMO total_debt Dec-2018: DebtCurrent 1,271 + LongTermDebtAndCapitalLeaseObligations 17,719 = 18,990
    srcs = [
        ("DebtCurrent", "A", None, False, D("1271000000")),
        ("LongTermDebtAndCapitalLeaseObligations", "A", None, False, D("17719000000")),
    ]
    assert sh.tag_sum_parts(srcs, D("18990000000")) == (
        (1, "DebtCurrent"),
        (1, "LongTermDebtAndCapitalLeaseObligations"),
    )
    # signed: opex = costs total - cost of revenue
    srcs2 = [("CostsAndExpenses", "A", None, False, D(100)), ("CostOfRevenue", "A", None, False, D(60))]
    assert sh.tag_sum_parts(srcs2, D(40)) == ((-1, "CostOfRevenue"), (1, "CostsAndExpenses"))
    # no sign assignment adds up: no tag-sum authority
    assert sh.tag_sum_parts(srcs2, D(41)) is None
    # the latest filing printing both parts is the sum's authority (the FY2019 10-K restates nothing)
    copies = [
        ("A", D("1271000000"), "DebtCurrent"),
        ("A", D("17719000000"), "LongTermDebtAndCapitalLeaseObligations"),
        ("B", D("1271000000"), "DebtCurrent"),
        ("B", D("17719000000"), "LongTermDebtAndCapitalLeaseObligations"),
    ]
    filed = {"A": date(2019, 2, 27), "B": date(2020, 2, 26)}
    assert sh.component_sum_authority(copies, sh.tag_sum_parts(srcs, D("18990000000")), filed) == (
        "B",
        D("18990000000"),
    )
    shown = pv.Shown(1, "total_debt_resolved", "I", date(2018, 12, 31), date(2018, 12, 31), D(1), ("a", "b"), "A", (1,))
    assert rules._tag_sum(shown)


@pytest.mark.unit
def test_coarser_prints_filer_scale_copies_and_part_lines_are_no_authority():
    # LRCX goodwill FY2024 1,626,528K shown; the FY2025 10-K's narrative copy 1.6B is a coarser print (ruling 15)
    kept, skips = sh.authority_skips(
        [("L25", "1600000000")], D("1626528000"), "goodwill", [("L25", D("1600000000"), "Goodwill")], {}
    )
    assert kept == [] and skips == (("L25", "1600000000", "coarser_print"),)
    # a genuine restatement (1,900 vs 1,626.5M) stays a disagreement
    kept, skips = sh.authority_skips(
        [("L25", "1900000000")], D("1626528000"), "goodwill", [("L25", D("1900000000"), "Goodwill")], {}
    )
    assert kept == [("L25", "1900000000")] and skips == ()
    # STX DPS FY2022 2.77 shown, the FY2024 10-K stores 2,770,000
    kept, skips = sh.authority_skips(
        [("S24", "2770000")], D("2.77"), "dividends_per_share_resolved",
        [("S24", D(2770000), "CommonStockDividendsPerShareDeclared")], {},
    )
    assert skips == (("S24", "2770000", "filer_scale"),)
    # PFE revenue FY2021 81,288 shown; the FY2023 10-K tags 'Product revenues' 73,636 with the element, under its Revenues line
    triples = [
        ("P23", D("73636000000"), "RevenueFromContractWithCustomerExcludingAssessedTax"),
        ("P23", D("81288000000"), "Revenues"),
    ]
    parents = {"RevenueFromContractWithCustomerExcludingAssessedTax": {"Revenues"}}
    kept, skips = sh.authority_skips(
        [("P23", "73636000000")], D("81288000000"), "revenue_sanity_resolved", triples, parents
    )
    assert skips == (("P23", "73636000000", "sub_line"),)
    # without the parent line in that filing the copy is the cell's line and still disagrees
    kept, skips = sh.authority_skips(
        [("P23", "73636000000")], D("81288000000"), "revenue_sanity_resolved", triples[:1], parents
    )
    assert kept == [("P23", "73636000000")]


def _note_structure():
    s = FilingStructure("0000012927-21-000011", "0000012927", "10-K", date(2021, 2, 1), date(2020, 12, 31))
    s.pre.append(PreLine(6, 35, "EQ", "CommonStockDividendsPerShareDeclared", "us-gaap/2020", "Cash dividends declared per share", False))
    s.num[("NetIncomeLoss", date(2020, 12, 31), 4)].append(
        NumValue("NetIncomeLoss", "us-gaap/2020", date(2020, 12, 31), 4, "USD", D(-11873000000), -6)
    )
    return s


@pytest.mark.unit
def test_a_printed_dash_on_the_note_path_proves_a_printed_zero():
    # BA DPS FY2020: the equity statement presents 'Cash dividends declared per share' with a dash for 2020
    claim = pv.Claim("concept", "UN", tags=("CommonStockDividendsPerShareDeclared",))
    base = dict(company_id=1, data_point_name="dividends_per_share_resolved", period_grain="FY", period_start=date(2020, 1, 1),
                period_end=date(2020, 12, 31), tags=(), accession="0000012927-21-000011", source_fact_ids=(), claim=claim)
    zero = pv.Shown(value=D(0), printed_zero=True, **base)
    p = pv.prove_note(zero, _note_structure(), pv.Proof(zero, pv.UNCHECKED))
    assert p.verdict == pv.PROVEN and p.checks["printed_zero_note"]["status"] == "pass"
    assert rules._printed_zero_cell(zero) and "printed_zero_note" in rules.rules_used(zero, p.checks)
    # a nonzero value never: no value for the column
    two = pv.Shown(value=D(2), printed_zero=False, **base)
    q = pv.prove_note(two, _note_structure(), pv.Proof(two, pv.UNCHECKED))
    assert q.verdict == pv.NOT_PRESENTED and q.reason_code == "no_value_for_this_column"


@pytest.mark.unit
def test_interest_income_is_located_by_its_element_family_when_the_claimed_tag_is_not_printed():
    # CRWD FY2023: the map claims InvestmentIncomeInterest, the IS prints 'Interest income' as InterestIncomeOperating
    s = FilingStructure("0001535527-23-000009", "0001535527", "10-K", date(2023, 3, 9), date(2023, 1, 31))
    s.pre.append(PreLine(5, 19, "IS", "InterestIncomeOperating", "us-gaap/2022", "Interest income", False))
    s.num[("InterestIncomeOperating", date(2023, 1, 31), 4)].append(
        NumValue("InterestIncomeOperating", "us-gaap/2022", date(2023, 1, 31), 4, "USD", D(52495000), -3)
    )
    claim = pv.Claim("concept", "IS", tags=("InvestmentIncomeInterest",))
    shown = pv.Shown(1, "interest_income", "FY", date(2022, 2, 1), date(2023, 1, 31), D(52495000), ("InvestmentIncomeInterest",),
                     "0001535527-23-000009", (1,), claim=claim)
    line, why, stmt, used = pv.locate(s, shown)
    assert line is not None and line.tag == "InterestIncomeOperating" and stmt == "IS"
    assert rules._element_family_dp(shown)
