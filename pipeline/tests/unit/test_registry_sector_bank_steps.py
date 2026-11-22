"""Sector rows for the shown bank-face and REIT values (2026-11-22): open-shown export cells with reason
'badge_undecided: <dp>/<sector>: not_applicable is a cell state' now take a registry badge from their own resolver row.

Rows are the resolver output's decision/flags/nodes for FY2024 (data-team/tags/line_map/resolver/<TICKER>.csv); the
printed labels are the fsn.line plabels of the same 10-K. A REIT's derived gross profit stays not applicable: WELL prints
no gross profit, and 'Total revenues' - 'Property operating expenses' is not one."""

from __future__ import annotations

import pytest
from scrooner_pipeline.mapper.sector_templates import sic_group
from scrooner_pipeline.metrics import registry as reg

DPS = reg.load_data_points()

# (ticker, cik, sic, data_point, resolver decision, flags, nodes, badge)
CELLS = [
    ("AXP", "0000004962", 6199, "deposits", "mapped", "roles", "Deposits=139413000000.0000 [R6.htm:22] | why: BS face Deposits", "as_printed"),
    ("AXP", "0000004962", 6199, "loans_net", "mapped", "roles", "LoansAndLeasesReceivableNetReportedAmount=143033000000.0000 [R6.htm:9] | why: BS face", "as_printed"),
    ("AXP", "0000004962", 6199, "net_interest_income", "mapped", "roles", "InterestIncomeExpenseNet=15543000000.0000 [R3.htm:26] | why: IS face InterestIncomeExpenseNet", "as_printed"),
    ("AXP", "0000004962", 6199, "noninterest_expense", "mapped", "roles", "NoninterestExpense=47869000000.0000 [R3.htm:38] | why: IS face NoninterestExpense", "as_printed"),
    ("AXP", "0000004962", 6199, "noninterest_income", "mapped", "roles", "NoninterestIncome=50406000000.0000 [R3.htm:16] | why: IS face NoninterestIncome", "as_printed"),
    ("AXP", "0000004962", 6199, "provision_for_credit_losses", "mapped", "roles", "ProvisionForLoanLossesExpensed=5185000000.0000 [R3.htm:29] | why: IS face", "as_printed"),
    ("AXP", "0000004962", 6199, "total_interest_income", "mapped", "roles", "InterestAndDividendIncomeOperating=23795000000.0000 [R3.htm:21] | why: IS face", "as_printed"),
    ("BAC", "0000070858", 6021, "operating_expenses", "mapped", "core", "NoninterestExpense=66812000000.0000 [R3.htm:20] | why: bank IS: the noninterest expense total (ruling: bank opex = NoninterestExpense)", "as_printed"),
    ("C", "0000831001", 6021, "operating_expenses", "mapped", "core", "NoninterestExpense=55132000000.0000 [R3.htm:29] | why: bank IS: the noninterest expense total (ruling: bank opex = NoninterestExpense)", "as_printed"),
    ("JPM", "0000019617", 6021, "operating_expenses", "mapped", "core", "NoninterestExpense=91797000000.0000 [R3.htm:24] | why: bank IS: the noninterest expense total (ruling: bank opex = NoninterestExpense)", "as_printed"),
    ("C", "0000831001", 6021, "capex", "mapped", "cf_family", "PaymentsToAcquirePropertyPlantAndEquipment=6500000000.0000 [R9.htm:37] | why: CF investing section: capital-purchase line(s) (register 2026-11-04 item 3)", "as_printed"),
    ("MS", "0000895421", 6211, "net_interest_income", "mapped", "roles", "InterestIncomeExpenseNet=8611000000.0000 [R3.htm:11] | why: IS face InterestIncomeExpenseNet", "as_printed"),
    ("WELL", "0000766704", 6798, "capex", "component_sum", "cf_family", "PaymentsForCapitalImprovements=857546000.0000 [R6.htm:23]; PaymentsForConstructionInProcess=827900000.0000 [R6.htm:24] | why: CF investing section: capital-purchase line(s) (register 2026-11-04 item 3); sum of 2", "derived:sum(printed capex lines)"),
]


@pytest.mark.parametrize("ticker,cik,sic,dp,decision,flags,nodes,badge", CELLS, ids=[f"{c[0]}-{c[3]}" for c in CELLS])
def test_shown_value_takes_its_registry_step(ticker, cik, sic, dp, decision, flags, nodes, badge):
    sector = sic_group(cik, sic)
    row = {"decision": decision, "flags": flags, "nodes": nodes}
    assert reg.badge_for(dp, sector, row, DPS) == badge


def test_axp_is_a_lender_by_company_assignment_not_general():
    # SECTOR-TEMPLATES-2026-11-01 s1 lists AXP in the lender row; SIC 6199 alone falls to general
    assert sic_group("0000004962", 6199) == "lender"
    assert sic_group("0000000001", 6199) == "general"


def test_bank_data_points_stay_out_of_the_general_template():
    for dp in ("deposits", "loans_net", "net_interest_income", "noninterest_expense", "noninterest_income",
               "provision_for_credit_losses", "total_interest_income"):
        assert not DPS[(dp, "general")].applies


def test_reit_derived_gross_profit_stays_not_applicable():
    row = {
        "decision": "derived_not_printed",
        "flags": "core;rule:not_printed_statement_role;derived_not_printed",
        "nodes": "Revenues=7991118000.0000 [R4.htm:6]; -CostOfGoodsAndServicesSold=4830211000.0000 [R4.htm:8] | why: the income statement prints no gross profit",
    }
    with pytest.raises(reg.BadgeUndecided, match="not_applicable"):
        reg.badge_for("gross_profit", sic_group("0000766704", 6798), row, DPS)
