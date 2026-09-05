from decimal import Decimal, getcontext

import pytest

from scrooner_pipeline.mapper.calculate import FORMULA_SHAPES, _compute
from scrooner_pipeline.mapper.definitions import METRIC_DEFINITIONS as V1_DEFINITIONS
from scrooner_pipeline.mapper.expanded_definitions import METRIC_DEFINITIONS as EXPANDED_DEFINITIONS


FORMULA_CASES = {
    # sum_diff_ratio (Revenue - Cost of Revenue) / Revenue, not a direct
    # "ratio" over a standalone GrossProfit tag, since 2026-09-02 -- see
    # calculate.py's own FORMULA_SHAPES comment for the real coverage
    # evidence behind this switch.
    "gross_margin": ("sum_diff_ratio", {"add": [Decimal("100")], "subtract": [Decimal("60")], "denominator": [Decimal("100")]}, Decimal("0.4")),
    "operating_margin": ("ratio", {"numerator": [Decimal("30")], "denominator": [Decimal("100")]}, Decimal("0.3")),
    "net_margin": ("ratio", {"numerator": [Decimal("20")], "denominator": [Decimal("100")]}, Decimal("0.2")),
    "roe": ("ratio", {"numerator": [Decimal("20")], "denominator": [Decimal("80")]}, Decimal("0.25")),
    "fcf": ("sum_diff", {"add": [Decimal("35")], "subtract": [Decimal("10")]}, Decimal("25")),
    "fcf_margin": ("sum_diff_ratio", {"add": [Decimal("35")], "subtract": [Decimal("10")], "denominator": [Decimal("100")]}, Decimal("0.25")),
    "debt_to_equity": ("ratio", {"numerator": [Decimal("30")], "denominator": [Decimal("60")]}, Decimal("0.5")),
    "current_ratio": ("ratio", {"numerator": [Decimal("50")], "denominator": [Decimal("25")]}, Decimal("2")),
    "interest_coverage_ratio": ("ratio", {"numerator": [Decimal("30")], "denominator": [Decimal("5")]}, Decimal("6")),
    "roa": ("ratio", {"numerator": [Decimal("20")], "denominator": [Decimal("200")]}, Decimal("0.1")),
    "quick_ratio": ("sum_diff_ratio", {"add": [Decimal("50")], "subtract": [Decimal("10")], "denominator": [Decimal("25")]}, Decimal("1.6")),
    "sbc_pct_revenue": ("ratio", {"numerator": [Decimal("3")], "denominator": [Decimal("100")]}, Decimal("0.03")),
    "ebitda": ("additive", {"add": [Decimal("30"), Decimal("7")]}, Decimal("37")),
    "debtor_days": ("days", {"numerator": [Decimal("50")], "denominator": [Decimal("500")]}, Decimal("36.5")),
    "inventory_days": ("days", {"numerator": [Decimal("100")], "denominator": [Decimal("400")]}, Decimal("91.25")),
    "payables_days": ("days", {"numerator": [Decimal("80")], "denominator": [Decimal("400")]}, Decimal("73")),
    "goodwill_pct_assets": ("ratio", {"numerator": [Decimal("15")], "denominator": [Decimal("100")]}, Decimal("0.15")),
    "eps_dilution_spread": ("sum_diff_ratio", {"add": [Decimal("5")], "subtract": [Decimal("4.5")], "denominator": [Decimal("5")]}, Decimal("0.1")),
    "capex_pct_revenue": ("ratio", {"numerator": [Decimal("10")], "denominator": [Decimal("100")]}, Decimal("0.1")),
    "sga_pct_revenue": ("ratio", {"numerator": [Decimal("20")], "denominator": [Decimal("100")]}, Decimal("0.2")),
    "rnd_intensity": ("ratio", {"numerator": [Decimal("8")], "denominator": [Decimal("100")]}, Decimal("0.08")),
    "net_interest_income": ("sum_diff", {"add": [Decimal("12")], "subtract": [Decimal("5")]}, Decimal("7")),
    "payout_ratio": ("ratio", {"numerator": [Decimal("2")], "denominator": [Decimal("4")]}, Decimal("0.5")),
    "pretax_margin": ("ratio", {"numerator": [Decimal("25")], "denominator": [Decimal("100")]}, Decimal("0.25")),
    "net_cash": ("sum_diff", {"add": [Decimal("50")], "subtract": [Decimal("20")]}, Decimal("30")),
    "net_cash_per_share": ("sum_diff_ratio", {"add": [Decimal("50")], "subtract": [Decimal("20")], "denominator": [Decimal("10")]}, Decimal("3")),
    # Added 2026-09-05 (financials display spec gap-fill).
    "book_value_per_share": ("ratio", {"numerator": [Decimal("80")], "denominator": [Decimal("10")]}, Decimal("8")),
    "working_capital": ("sum_diff", {"add": [Decimal("50")], "subtract": [Decimal("25")]}, Decimal("25")),
    "net_change_in_cash": ("additive", {"add": [Decimal("35"), Decimal("-10"), Decimal("-5")]}, Decimal("20")),
    "ocf_to_net_income": ("ratio", {"numerator": [Decimal("35")], "denominator": [Decimal("20")]}, Decimal("1.75")),
    "cash_returned_to_shareholders": ("additive", {"add": [Decimal("4"), Decimal("6")]}, Decimal("10")),
}

EXPECTED_EXPANDED_DEFINITIONS = {
    "roa", "quick_ratio", "sbc_pct_revenue", "ebitda", "net_debt_ebitda",
    "ev_ebitda", "ev_sales", "peg_ratio", "buyback_yield",
    "total_shareholder_yield", "institutional_ownership_pct",
    "share_dilution_trend", "debtor_days", "inventory_days", "payables_days",
    "cash_conversion_cycle", "piotroski_f_score",
    "fcf_gt_net_income", "zero_debt", "profitable_streak_years", "margin_expanding_3yr",
    "revenue_growth_5y_cagr", "revenue_growth_10y_cagr", "eps_growth_5y_cagr", "eps_growth_10y_cagr",
    "goodwill_pct_assets", "eps_dilution_spread",
    "ar_change_reconciliation_gap", "inventory_change_reconciliation_gap", "ap_change_reconciliation_gap",
    "rnd_intensity", "net_interest_income",
    "capex_pct_revenue", "sga_pct_revenue", "effective_tax_rate_gap",
    "fcf_growth_3y_cagr", "fcf_growth_5y_cagr", "dividend_growth_streak_years",
    "payout_ratio", "pretax_margin", "net_cash", "net_cash_per_share",
    "dps_growth_yoy", "dps_growth_3y_cagr",
    # Added 2026-09-05 (financials display spec gap-fill).
    "book_value_per_share", "working_capital", "net_change_in_cash", "ocf_to_net_income",
    "cash_returned_to_shareholders", "ebitda_margin", "debt_to_ebitda", "fcf_per_share",
    "share_repurchases_pct_fcf", "dividends_pct_fcf",
    "net_income_growth_yoy", "net_income_growth_3y_cagr", "net_income_growth_5y_cagr", "net_income_growth_10y_cagr",
    "diluted_shares_growth_yoy", "diluted_shares_growth_3y_cagr", "diluted_shares_growth_5y_cagr",
    "fcf_growth_yoy",
}


@pytest.mark.unit
@pytest.mark.parametrize("metric_name", FORMULA_CASES)
def test_generic_metric_formula_positive_cases(metric_name):
    shape, inputs, expected = FORMULA_CASES[metric_name]
    value, reason = _compute(shape, inputs)

    assert FORMULA_SHAPES[metric_name] == shape
    assert value == expected
    assert reason is None


@pytest.mark.unit
@pytest.mark.parametrize("shape,inputs,reason", [
    ("ratio", {"numerator": [Decimal("1")], "denominator": [Decimal("0")]}, "zero_denominator"),
    ("sum_diff", {"add": [Decimal("1")]}, "missing:subtract"),
    ("sum_diff_ratio", {"add": [Decimal("1")], "subtract": [Decimal("1")]}, "missing:denominator"),
    ("additive", {}, "missing:add"),
    ("days", {"numerator": [Decimal("1")], "denominator": [Decimal("0")]}, "zero_denominator"),
    ("roic", {
        "nopat_base": [Decimal("10")], "tax_rate_numerator": [Decimal("1")],
        "tax_rate_denominator": [Decimal("0")], "invested_capital_add": [Decimal("10")],
        "invested_capital_subtract": [Decimal("1")],
    }, "zero_pretax_income"),
])
def test_formula_edge_cases_return_explicit_null_reason(shape, inputs, reason):
    assert _compute(shape, inputs) == (None, reason)


@pytest.mark.unit
def test_roic_formula_and_decimal_precision_are_exact():
    getcontext().prec = 28
    value, reason = _compute(
        "roic",
        {
            "nopat_base": [Decimal("20")],
            "tax_rate_numerator": [Decimal("5")],
            "tax_rate_denominator": [Decimal("25")],
            "invested_capital_add": [Decimal("30"), Decimal("40")],
            "invested_capital_subtract": [Decimal("10")],
        },
    )

    assert value == Decimal(4) / Decimal(15)
    assert reason is None
    assert isinstance(value, Decimal)


@pytest.mark.unit
def test_all_seeded_definitions_are_unique_and_generic_shapes_are_covered():
    v1_names = [row[0] for row in V1_DEFINITIONS]
    expanded_names = [row[0] for row in EXPANDED_DEFINITIONS]
    generic_expanded_names = {row[0] for row in EXPANDED_DEFINITIONS if row[3]}

    assert len(v1_names) == 20
    assert set(expanded_names) == EXPECTED_EXPANDED_DEFINITIONS
    assert len(expanded_names) == len(EXPECTED_EXPANDED_DEFINITIONS)
    assert set(v1_names).isdisjoint(expanded_names)
    assert generic_expanded_names <= set(FORMULA_CASES)
    assert set(FORMULA_CASES) <= set(FORMULA_SHAPES)
