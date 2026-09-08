from decimal import Decimal

import pytest

from scrooner_pipeline.sanity.yfinance_check import (
    SEVERITY_CRITICAL,
    SEVERITY_MAJOR,
    SEVERITY_MINOR,
    SEVERITY_MISSING_OURS,
    SEVERITY_OK,
    _check_metric,
    _check_revenue_zero,
    _pct_diff,
    _severity_for,
)


@pytest.mark.unit
class TestPctDiffAndSeverity:
    def test_pct_diff_signed(self):
        assert _pct_diff(Decimal(110), Decimal(100)) == Decimal(10)
        assert _pct_diff(Decimal(90), Decimal(100)) == Decimal(-10)

    def test_pct_diff_guards_against_zero_external(self):
        # external_value == 0 would divide-by-zero without the guard --
        # falls back to a denominator of 1 rather than crashing.
        assert _pct_diff(Decimal(50), Decimal(0)) == Decimal(5000)

    def test_severity_thresholds_per_metric(self):
        assert _severity_for("shares_outstanding", Decimal(1)) == SEVERITY_OK
        assert _severity_for("shares_outstanding", Decimal(5)) == SEVERITY_MINOR
        assert _severity_for("shares_outstanding", Decimal(20)) == SEVERITY_MAJOR
        # market_cap has a wider tolerance than shares_outstanding -- the
        # same 5% that's "minor" for shares_outstanding is "ok" for market_cap.
        assert _severity_for("market_cap", Decimal(5)) == SEVERITY_OK

    def test_severity_uses_absolute_value(self):
        assert _severity_for("trailing_pe", Decimal(-50)) == SEVERITY_MAJOR


@pytest.mark.unit
class TestNormalization:
    """Two real unit-scale traps found live 2026-09-08 checking an actual
    AAPL yfinance payload before trusting any pairing: yfinance's
    dividendYield/debtToEquity are on a whole-percentage scale (0.34
    meaning 0.34%, 78.445 meaning a 0.78 ratio) while our own
    dividend_yield/debt_to_equity are plain fractions/ratios."""

    def test_dividend_yield_normalizes_our_fraction_to_match_yfinance_percentage(self):
        # Real AAPL values: ours = 0.003390..., yfinance's dividendYield = 0.34
        row = _check_metric(1, "dividend_yield", Decimal("0.003390487261455003390487261455"), 0.34)
        assert row["our_value"] == Decimal("0.339048726145500339048726145500")
        assert row["external_value"] == Decimal("0.34")
        assert row["severity"] == SEVERITY_OK

    def test_debt_to_equity_normalizes_yfinance_percentage_to_match_our_ratio(self):
        # Real AAPL values: ours = 0.7654..., yfinance's debtToEquity = 78.445
        row = _check_metric(1, "debt_to_equity", Decimal("0.7654389880952380952380952381"), 78.445)
        assert row["external_value"] == Decimal("0.78445")
        assert row["severity"] == SEVERITY_OK

    def test_metrics_without_a_normalizer_are_compared_directly(self):
        row = _check_metric(1, "operating_margin", Decimal("0.3262"), 0.3262)
        assert row["our_value"] == Decimal("0.3262")
        assert row["external_value"] == Decimal("0.3262")
        assert row["severity"] == SEVERITY_OK


@pytest.mark.unit
class TestCheckMetric:
    def test_no_row_when_external_missing(self):
        assert _check_metric(1, "market_cap", Decimal(100), None) is None

    def test_no_row_and_no_crash_when_external_is_infinite(self):
        """Real crash found live 2026-09-08, first full-population sanity
        run: yfinance genuinely returns inf for trailingPE when a
        company's trailing earnings are ~zero (a real, not-rare case, not
        malformed data). `_pct_diff`'s subtract-then-divide-by-abs(external)
        can produce Decimal('Infinity') / Decimal('Infinity') even from a
        single infinite input, which raises decimal.InvalidOperation, not
        a quiet NaN the way plain float arithmetic would -- this crashed
        the entire batch instead of skipping one company's one metric."""
        assert _check_metric(1, "trailing_pe", Decimal(20), float("inf")) is None
        assert _check_metric(1, "trailing_pe", Decimal(20), float("-inf")) is None

    def test_no_row_and_no_crash_when_external_is_nan(self):
        assert _check_metric(1, "trailing_pe", Decimal(20), float("nan")) is None

    def test_degenerate_ratio_is_skipped_not_flagged(self):
        """Real finding, first full-population run 2026-09-08: a
        microcap/shell company's near-zero revenue can make net_margin
        blow up to an absurd magnitude (a real case: -480,577, i.e.
        -48 MILLION percent) while yfinance reports a plain 0.0 -- the
        exact ROE/ROIC/margin degeneracy this project already guards
        against elsewhere (expanded_metrics.py's peer-comparison ranking).
        Must be skipped as "not a meaningful comparison", never flagged
        critical/major just because the percentage diff looks enormous."""
        assert _check_metric(1, "net_margin", Decimal("-480577"), 0.0) is None

    def test_ordinary_ratio_within_bound_still_compared(self):
        row = _check_metric(1, "net_margin", Decimal("0.15"), 0.14)
        assert row is not None
        assert row["severity"] == "ok"

    def test_missing_ours_when_we_have_no_value(self):
        row = _check_metric(1, "market_cap", None, 1000)
        assert row["severity"] == SEVERITY_MISSING_OURS
        assert row["our_value"] is None

    def test_ok_within_tolerance(self):
        row = _check_metric(1, "market_cap", Decimal(1000), 1050)
        assert row["severity"] == SEVERITY_OK


@pytest.mark.unit
class TestCheckRevenueZero:
    def test_silent_when_no_revenue_history_at_all(self):
        """Calibrated live 2026-09-08: TSM, Enbridge, and Ares Capital (a
        BDC -- revenue isn't even the right concept for its business
        model) all have ZERO revenue canonical_fact rows ever, a real
        structural absence, not the resolve() authoritative-$0 bug this
        check targets. All three fired as false-positive 'critical'
        findings on the first real test run before this guard existed."""
        row = _check_revenue_zero(1, None, has_revenue_history=False, external_total_revenue=50_000_000_000)
        assert row is None

    def test_fires_when_history_exists_but_latest_is_zero(self):
        """The actual Flowserve-shaped bug: revenue history exists, but
        the current/latest value has resolved to a spurious $0 while an
        independent source shows a real, material figure."""
        row = _check_revenue_zero(1, Decimal(0), has_revenue_history=True, external_total_revenue=4_000_000_000)
        assert row is not None
        assert row["severity"] == SEVERITY_CRITICAL

    def test_silent_when_external_revenue_immaterial(self):
        row = _check_revenue_zero(1, Decimal(0), has_revenue_history=True, external_total_revenue=100)
        assert row is None

    def test_silent_when_our_revenue_is_real(self):
        row = _check_revenue_zero(1, Decimal(5_000_000_000), has_revenue_history=True, external_total_revenue=4_800_000_000)
        assert row is None

    def test_silent_when_external_missing(self):
        row = _check_revenue_zero(1, Decimal(0), has_revenue_history=True, external_total_revenue=None)
        assert row is None
