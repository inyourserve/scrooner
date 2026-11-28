"""M3-cert 2026-11-29 (verifier precheck): PFE gross_profit FY2017/2021-23 locators read 'R3.htm (derived: us-gaap:Revenues - ...)' and
PM other_income_expense_net FY2015 carries the flag 'derived:<registry formula> (registry fallback 4' (label cut at ';'); both were
badged as_printed. Mutation: restore the old locator regex / drop _step_of and each assertion fails."""

from scrooner_pipeline.metrics import registry as reg


def test_derived_prefixed_formula_locator_is_the_derived_step_pfe():
    loc = "R3.htm (derived: us-gaap:Revenues - us-gaap:CostOfGoodsAndServicesSold) of 0000078003-24-000039, read FY2021 10-K"
    row = {
        "decision": "mapped",
        "flags": "core;filing_read;text_stated;replaces:derived;perimeter:total revenues include alliance revenues",
        "nodes": "",
        "locator": loc,
    }
    assert (
        reg.badge_for("gross_profit", "general", row)
        == "derived:revenue-cost_of_revenue"
    )
    # a single element with the derived: prefix is not a computation
    one = dict(row, locator="R5.htm (derived: us-gaap:AccountsReceivableNetCurrent) of X")
    assert reg.badge_for("accounts_receivable", "general", one) == "as_printed"


def test_a_step_flag_with_a_trailing_note_names_the_registry_step_pm():
    step = "derived:income_before_tax-operating_income+interest_expense-interest_income"
    pm = {
        "decision": "mapped",
        "flags": f"roles;filing_read;stated_zero;replaces:not_presented;{step} (registry fallback 4",
        "nodes": "",
        "locator": "R4.htm (derived: us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments - us-gaap:OperatingIncomeLoss + us-gaap:InterestIncomeExpenseNet) of X",
    }
    assert reg.badge_for("other_income_expense_net", "general", pm) == step
