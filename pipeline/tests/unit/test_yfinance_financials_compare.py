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
        periods = [(1, date(2026, 6, 27)), (2, date(2026, 3, 28))]
        result = _closest_period(periods, date(2026, 6, 30))
        assert result == (1, date(2026, 6, 27))

    def test_none_when_nothing_within_tolerance(self):
        periods = [(1, date(2026, 1, 1))]
        result = _closest_period(periods, date(2026, 6, 30))
        assert result is None

    def test_picks_the_truly_closest_when_two_are_in_range(self):
        periods = [(1, date(2026, 6, 20)), (2, date(2026, 6, 28))]
        result = _closest_period(periods, date(2026, 6, 30))
        assert result == (2, date(2026, 6, 28))
