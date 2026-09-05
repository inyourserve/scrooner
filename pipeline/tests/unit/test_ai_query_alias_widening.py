import pytest

from scrooner_pipeline.ai_query.aliases import METRIC_ALIASES

# doc/status/DATA_COVERAGE.md's "what moves the needle next" flagged the
# alias table's real coverage gap (14 of the real metric_definition
# catalog) as the largest remaining product gap. This locks in a
# representative sample of the 2026-08-31 widening so a future refactor
# can't silently drop coverage without a test failing.


@pytest.mark.unit
@pytest.mark.parametrize(
    "phrase,expected_metric",
    [
        ("pe ratio", "trailing_pe"),
        ("p/e", "trailing_pe"),
        ("market cap", "market_cap"),
        ("peg ratio", "peg_ratio"),
        ("ev/ebitda", "ev_ebitda"),
        ("piotroski score", "piotroski_f_score"),
        ("zero debt", "zero_debt"),
        ("quick ratio", "quick_ratio"),
        ("cash conversion cycle", "cash_conversion_cycle"),
        ("institutional ownership", "institutional_ownership_pct"),
        ("shareholder yield", "total_shareholder_yield"),
        ("net debt to ebitda", "net_debt_ebitda"),
    ],
)
def test_widened_alias_resolves_to_real_metric_name(phrase, expected_metric):
    assert METRIC_ALIASES[phrase] == expected_metric


@pytest.mark.unit
def test_original_pre_2026_08_31_aliases_still_present():
    """Regression guard: the widening pass must be purely additive."""
    assert METRIC_ALIASES["roe"] == "roe"
    assert METRIC_ALIASES["return on invested capital"] == "roic"
    assert METRIC_ALIASES["debt to equity"] == "debt_to_equity"
    assert METRIC_ALIASES["eps cagr"] == "eps_growth_3y_cagr"


@pytest.mark.unit
def test_no_alias_maps_to_a_reconciliation_diagnostic_metric():
    """Deliberately unaliased: internal Mapper QA metrics have no natural
    investor phrase and must not be reachable via plain English."""
    diagnostic_metrics = {
        "ar_change_reconciliation_gap",
        "ap_change_reconciliation_gap",
        "inventory_change_reconciliation_gap",
        "effective_tax_rate_gap",
        "eps_dilution_spread",
    }
    assert not (set(METRIC_ALIASES.values()) & diagnostic_metrics)
