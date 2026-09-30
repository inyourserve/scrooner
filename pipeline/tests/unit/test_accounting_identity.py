from decimal import Decimal as D

from scrooner_pipeline.sanity.accounting_identity import (
    IDENTITIES,
    evaluate,
    _layer_concept_name,
)

BY_NAME = {i.name: i for i in IDENTITIES}


def test_balance_sheet_passes_within_tolerance():
    r = evaluate(
        BY_NAME["balance_sheet"],
        {"total_assets": D("1000"), "total_liabilities": D("600"), "stockholders_equity": D("395")},
    )
    assert r.passed and not r.used_adjustments


def test_balance_sheet_closes_with_noncontrolling_interest():
    values = {"total_assets": D("1000"), "total_liabilities": D("600"), "stockholders_equity": D("300")}
    assert not evaluate(BY_NAME["balance_sheet"], values).passed
    r = evaluate(BY_NAME["balance_sheet"], values, {"MinorityInterest": D("100")})
    assert r.passed and r.used_adjustments


def test_balance_sheet_scale_error_fails():
    # Real shape (Spectral Capital 2017-03-31): assets 7,520 vs liabilities 779,811.
    r = evaluate(
        BY_NAME["balance_sheet"],
        {"total_assets": D("7520"), "total_liabilities": D("779811"), "stockholders_equity": D("-553369")},
    )
    assert not r.passed and r.rel_gap > 1


def test_failure_reports_closest_candidate():
    values = {"total_assets": D("1000"), "total_liabilities": D("600"), "stockholders_equity": D("100")}
    r = evaluate(BY_NAME["balance_sheet"], values, {"MinorityInterest": D("250")})
    assert not r.passed and r.used_adjustments and r.rel_gap == D("0.05")


def test_gross_profit_tolerance_is_relative_to_revenue():
    ident = BY_NAME["gross_profit"]
    ok = {"gross_profit": D("400"), "revenue": D("1000"), "cost_of_revenue": D("595")}
    bad = {"gross_profit": D("400"), "revenue": D("1000"), "cost_of_revenue": D("500")}
    assert evaluate(ident, ok).passed
    assert not evaluate(ident, bad).passed


def test_net_income_adjustment_signs():
    ident = BY_NAME["net_income"]
    values = {"net_income": D("70"), "income_before_tax": D("100"), "income_tax_expense": D("20")}
    # 100 - 20 - NCI 10 = 70
    r = evaluate(ident, values, {"NetIncomeLossAttributableToNoncontrollingInterest": D("10")})
    assert r.passed and r.used_adjustments


def test_at_most_allows_equal_and_below():
    ident = BY_NAME["current_assets_within_total"]
    assert evaluate(ident, {"current_assets": D("100"), "total_assets": D("100")}).passed
    assert evaluate(ident, {"current_assets": D("50"), "total_assets": D("100")}).passed
    assert not evaluate(ident, {"current_assets": D("150"), "total_assets": D("100")}).passed


def test_revenue_nonnegative():
    ident = BY_NAME["revenue_nonnegative"]
    assert evaluate(ident, {"revenue": D("0")}).passed
    assert not evaluate(ident, {"revenue": D("-5")}).passed


def test_zero_basis_does_not_divide_by_zero():
    r = evaluate(
        BY_NAME["balance_sheet"],
        {"total_assets": D("0"), "total_liabilities": D("0"), "stockholders_equity": D("0")},
    )
    assert r.passed


def test_layer_concept_names():
    known = {"revenue", "revenue_sanity_resolved", "net_income", "net_income_resolved", "total_liabilities"}
    assert _layer_concept_name("revenue", "display", known) == "revenue_sanity_resolved"
    assert _layer_concept_name("net_income", "display", known) == "net_income_resolved"
    assert _layer_concept_name("total_liabilities", "display", known) == "total_liabilities"
    assert _layer_concept_name("net_income", "raw", known) == "net_income"
