from datetime import date

import pytest

from scrooner_pipeline.sanity.freshness_check import SEVERITY_OK, SEVERITY_STALE, SEVERITY_UNKNOWN, check_freshness


@pytest.mark.unit
class TestCheckFreshness:
    def test_ok_when_periods_align(self):
        # Real AAPL shape: yfinance's mostRecentQuarter (2026-06-27)
        # exactly matches our own stored fiscal period end.
        row = check_freshness(1, date(2026, 6, 27), date(2026, 6, 27))
        assert row["severity"] == SEVERITY_OK
        assert row["days_stale"] == 0

    def test_ok_within_normal_filing_lag(self):
        # yfinance reports a quarter 60 days after our own latest stored
        # period -- within SEC's real 40/45-day filing window plus buffer,
        # not a real miss.
        row = check_freshness(1, date(2026, 1, 1), date(2026, 3, 2))
        assert row["severity"] == SEVERITY_OK

    def test_stale_when_a_real_quarter_was_missed(self):
        # yfinance's most recent quarter is a full extra cycle (~180+
        # days) past our own latest -- a real, uningested quarter.
        row = check_freshness(1, date(2025, 1, 1), date(2025, 9, 1))
        assert row["severity"] == SEVERITY_STALE
        assert row["days_stale"] == 243

    def test_unknown_when_yfinance_has_no_opinion(self):
        row = check_freshness(1, date(2026, 1, 1), None)
        assert row["severity"] == SEVERITY_UNKNOWN

    def test_unknown_when_we_have_no_data_at_all(self):
        row = check_freshness(1, None, date(2026, 1, 1))
        assert row["severity"] == SEVERITY_UNKNOWN

    def test_ok_when_our_data_is_newer_than_yfinance(self):
        # We're ahead of yfinance (a real, harmless case -- yfinance
        # itself can lag) -- negative days_stale, still 'ok'.
        row = check_freshness(1, date(2026, 6, 27), date(2026, 3, 28))
        assert row["severity"] == SEVERITY_OK
        assert row["days_stale"] == -91
