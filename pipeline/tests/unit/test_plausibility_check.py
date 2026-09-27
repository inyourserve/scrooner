from decimal import Decimal

import pytest

from scrooner_pipeline.sanity.plausibility_check import (
    ABSOLUTE_BOUNDS,
    EXACT_SET_METRICS,
    RELATIVE_CHECKS,
    SEVERITY_CRITICAL,
    SEVERITY_OK,
    SEVERITY_WATCH,
    check_absolute,
    check_exact_set,
    check_relative,
)


@pytest.mark.unit
class TestCheckAbsolute:
    def test_ok_within_watch_range(self):
        severity, note = check_absolute(Decimal("0.30"), ABSOLUTE_BOUNDS["roe"])
        assert severity == SEVERITY_OK
        assert note is None

    def test_watch_outside_watch_but_inside_critical(self):
        # roe watch range is [-2, 2]; 3.0 (300%) is outside watch but
        # inside critical [-10, 10] -- a real degenerate-denominator case
        # this project has documented repeatedly, not automatically wrong.
        severity, _note = check_absolute(Decimal("3.0"), ABSOLUTE_BOUNDS["roe"])
        assert severity == SEVERITY_WATCH

    def test_critical_outside_critical_range(self):
        # Real observed live value: roe max 56,600,000% (566000 as a
        # fraction) -- must land critical.
        severity, note = check_absolute(Decimal("566000"), ABSOLUTE_BOUNDS["roe"])
        assert severity == SEVERITY_CRITICAL
        assert "critical range" in note

    def test_current_ratio_negative_is_always_critical(self):
        # Current ratio has a hard floor at 0 -- both inputs are
        # non-negative by accounting definition, so any negative value
        # is a sign/tag bug, never a legitimate extreme case.
        severity, _note = check_absolute(Decimal("-1.27"), ABSOLUTE_BOUNDS["current_ratio"])
        assert severity == SEVERITY_CRITICAL

    def test_dividend_yield_floor_at_zero(self):
        severity, _note = check_absolute(Decimal("-0.01"), ABSOLUTE_BOUNDS["dividend_yield"])
        assert severity == SEVERITY_CRITICAL

    def test_growth_rate_floor_at_minus_one(self):
        # A company cannot lose more than 100% of a positive quantity --
        # anything below -1 (-100%) is a certain formula bug.
        severity, _note = check_absolute(Decimal("-1.5"), ABSOLUTE_BOUNDS["revenue_growth_yoy"])
        assert severity == SEVERITY_CRITICAL

    def test_growth_rate_allows_real_hypergrowth(self):
        # A company recovering from a near-zero base can legitimately
        # post 1000%+ growth -- must not be flagged critical.
        severity, _note = check_absolute(Decimal("5.0"), ABSOLUTE_BOUNDS["revenue_growth_yoy"])
        assert severity != SEVERITY_CRITICAL

    def test_unbounded_side_never_trips(self):
        # sga_pct_revenue's critical ceiling is intentionally loose
        # (1000 = 100,000%) -- a real pre-revenue biotech can legitimately
        # spend many multiples of its tiny revenue on SG&A.
        severity, _note = check_absolute(Decimal("50"), ABSOLUTE_BOUNDS["sga_pct_revenue"])
        assert severity != SEVERITY_CRITICAL


@pytest.mark.unit
class TestCheckExactSet:
    def test_valid_piotroski_score(self):
        severity, note = check_exact_set(Decimal("7"), EXACT_SET_METRICS["piotroski_f_score"])
        assert severity == SEVERITY_OK
        assert note is None

    def test_invalid_piotroski_score(self):
        severity, note = check_exact_set(Decimal("10"), EXACT_SET_METRICS["piotroski_f_score"])
        assert severity == SEVERITY_CRITICAL
        assert "not in the valid set" in note

    def test_boolean_flag_valid(self):
        severity, _note = check_exact_set(Decimal("1"), EXACT_SET_METRICS["zero_debt"])
        assert severity == SEVERITY_OK

    def test_boolean_flag_invalid(self):
        severity, _note = check_exact_set(Decimal("2"), EXACT_SET_METRICS["zero_debt"])
        assert severity == SEVERITY_CRITICAL


@pytest.mark.unit
class TestCheckRelative:
    def test_skips_when_denominator_missing(self):
        concept_name, multiplier, description = RELATIVE_CHECKS["ebitda"]
        assert check_relative(Decimal("1000"), None, multiplier, description) is None

    def test_skips_when_denominator_zero(self):
        _concept_name, multiplier, description = RELATIVE_CHECKS["ebitda"]
        assert check_relative(Decimal("1000"), Decimal("0"), multiplier, description) is None

    def test_ok_within_multiple_of_revenue(self):
        _concept_name, multiplier, description = RELATIVE_CHECKS["ebitda"]
        # EBITDA of $200 against $100 revenue (2x) is within the 3x bound.
        severity, note = check_relative(Decimal("200"), Decimal("100"), multiplier, description)
        assert severity == SEVERITY_OK
        assert note is None

    def test_critical_beyond_multiple_of_revenue(self):
        _concept_name, multiplier, description = RELATIVE_CHECKS["ebitda"]
        severity, note = check_relative(Decimal("500"), Decimal("100"), multiplier, description)
        assert severity == SEVERITY_CRITICAL
        assert "3x TTM revenue" in note

    def test_uses_absolute_value_of_both_sides(self):
        _concept_name, multiplier, description = RELATIVE_CHECKS["net_cash"]
        # A large NEGATIVE net_cash (heavy net debt) relative to a small
        # positive total_assets denominator should still trip critical.
        severity, _note = check_relative(Decimal("-500"), Decimal("100"), multiplier, description)
        assert severity == SEVERITY_CRITICAL


@pytest.mark.unit
def test_every_metric_appears_in_exactly_one_rule_table():
    absolute_names = set(ABSOLUTE_BOUNDS)
    exact_set_names = set(EXACT_SET_METRICS)
    relative_names = set(RELATIVE_CHECKS)
    assert not (absolute_names & exact_set_names)
    assert not (absolute_names & relative_names)
    assert not (exact_set_names & relative_names)


@pytest.mark.unit
def test_every_absolute_bound_is_a_well_ordered_tuple():
    for metric_name, (crit_min, crit_max, watch_min, watch_max) in ABSOLUTE_BOUNDS.items():
        if crit_min is not None and crit_max is not None:
            assert crit_min <= crit_max, metric_name
        if watch_min is not None and watch_max is not None:
            assert watch_min <= watch_max, metric_name
        # WATCH range must sit inside (or equal to) the CRITICAL range --
        # a value can never be "watch" but not also pass the critical gate.
        if crit_min is not None and watch_min is not None:
            assert crit_min <= watch_min, metric_name
        if crit_max is not None and watch_max is not None:
            assert watch_max <= crit_max, metric_name
