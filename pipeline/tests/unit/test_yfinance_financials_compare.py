from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.yfinance_financials.compare import (
    MAJOR_PCT,
    MINOR_PCT,
    SEVERITY_MAJOR,
    SEVERITY_MINOR,
    SEVERITY_OK,
    _closest_period,
    _pct_diff,
    _severity_for,
)


@pytest.mark.unit
class TestPctDiffAndSeverity:
    def test_pct_diff_signed(self):
        assert _pct_diff(Decimal(110), Decimal(100)) == Decimal(10)

    def test_severity_thresholds(self):
        assert _severity_for(Decimal(5)) == SEVERITY_OK
        assert _severity_for(Decimal(MINOR_PCT)) == SEVERITY_MINOR
        assert _severity_for(Decimal(MAJOR_PCT)) == SEVERITY_MAJOR


@pytest.mark.unit
class TestClosestPeriod:
    def test_picks_the_period_within_tolerance(self):
        # Real shape: yfinance rounds AAPL's real fiscal quarter-end
        # (2026-06-27) to the nearest calendar quarter-end (2026-06-30).
        periods = [(1, date(2026, 6, 27), "duration"), (2, date(2026, 3, 28), "duration")]
        result = _closest_period(periods, date(2026, 6, 30), "duration")
        assert result == (1, date(2026, 6, 27))

    def test_none_when_nothing_within_tolerance(self):
        periods = [(1, date(2026, 1, 1), "duration")]
        result = _closest_period(periods, date(2026, 6, 30), "duration")
        assert result is None

    def test_picks_the_truly_closest_when_two_are_in_range(self):
        periods = [(1, date(2026, 6, 20), "duration"), (2, date(2026, 6, 28), "duration")]
        result = _closest_period(periods, date(2026, 6, 30), "duration")
        assert result == (2, date(2026, 6, 28))

    def test_ignores_a_same_date_period_of_the_wrong_type(self):
        # Found live 2026-09-13 verifying Robinhood (HOOD): a real fiscal
        # quarter has BOTH a duration period (income statement/cash flow)
        # and an instant period (balance-sheet snapshot) at the identical
        # end_date -- correct, standard XBRL modeling. Before this fix,
        # the tie-break with no type-awareness silently always preferred
        # whichever row Postgres returned first (in practice, the duration
        # row), so a balance-sheet concept looking for the instant period
        # could get pointed at the duration one instead and find no
        # matching value there -- a false "missing_ours" for real data
        # sitting under a different period_id the whole time. Checked
        # against the full population, not just HOOD: every balance-sheet
        # concept was reporting 99.5-99.9% "missing_ours" before this fix.
        periods = [(1, date(2026, 6, 30), "duration"), (2, date(2026, 6, 30), "instant")]
        assert _closest_period(periods, date(2026, 6, 30), "instant") == (2, date(2026, 6, 30))
        assert _closest_period(periods, date(2026, 6, 30), "duration") == (1, date(2026, 6, 30))

    def test_none_when_only_the_wrong_type_is_in_range(self):
        periods = [(1, date(2026, 6, 30), "duration")]
        assert _closest_period(periods, date(2026, 6, 30), "instant") is None
