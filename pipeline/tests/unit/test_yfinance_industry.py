"""Unit tests for company_master/yfinance_industry.py's status classification
-- the part most likely to silently misclassify a real outcome (not_found vs.
no_data vs. ok vs. a transient error worth retrying)."""

from unittest.mock import MagicMock, patch

import psycopg
import pytest
from yfinance.exceptions import YFRateLimitError

from scrooner_pipeline.company_master.yfinance_industry import (
    STATUS_ERROR,
    STATUS_NO_DATA,
    STATUS_NOT_FOUND,
    STATUS_OK,
    _classify,
    _fetch_info,
    _write_batch,
)


def test_ok_when_sector_and_industry_present():
    with patch(
        "scrooner_pipeline.company_master.yfinance_industry._fetch_info",
        return_value={"quoteType": "EQUITY", "sector": "Technology", "industry": "Consumer Electronics"},
    ):
        assert _classify("AAPL") == ("Technology", "Consumer Electronics", None, None, STATUS_OK)


def test_ok_captures_about_text_and_website_from_the_same_fetch():
    # Added 2026-09-06 -- about_text/website ride along on the SAME
    # get_info() payload as sector/industry, no second Yahoo request.
    with patch(
        "scrooner_pipeline.company_master.yfinance_industry._fetch_info",
        return_value={
            "quoteType": "EQUITY", "sector": "Technology", "industry": "Consumer Electronics",
            "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones.",
            "website": "https://www.apple.com",
        },
    ):
        assert _classify("AAPL") == (
            "Technology", "Consumer Electronics",
            "Apple Inc. designs, manufactures, and markets smartphones.", "https://www.apple.com",
            STATUS_OK,
        )


def test_not_found_when_no_quote_type():
    # Real yfinance behavior for an invalid ticker: no exception, a near-empty
    # dict with quoteType absent (checked live 2026-09-06).
    with patch("scrooner_pipeline.company_master.yfinance_industry._fetch_info", return_value={"trailingPegRatio": None}):
        assert _classify("ZZZZZZINVALID") == (None, None, None, None, STATUS_NOT_FOUND)


def test_not_found_when_info_empty():
    with patch("scrooner_pipeline.company_master.yfinance_industry._fetch_info", return_value={}):
        assert _classify("ZZZZZZINVALID") == (None, None, None, None, STATUS_NOT_FOUND)


def test_no_data_when_real_quote_but_no_classification():
    # e.g. some funds/ETFs/instruments have a real Yahoo quote but no sector/industry/about/website.
    with patch(
        "scrooner_pipeline.company_master.yfinance_industry._fetch_info",
        return_value={"quoteType": "ETF", "sector": None, "industry": None},
    ):
        assert _classify("SPY") == (None, None, None, None, STATUS_NO_DATA)


def test_error_on_rate_limit_after_retries_exhausted():
    with patch(
        "scrooner_pipeline.company_master.yfinance_industry._fetch_info",
        side_effect=YFRateLimitError(),
    ):
        assert _classify("AAPL") == (None, None, None, None, STATUS_ERROR)


def test_error_on_unexpected_exception():
    with patch(
        "scrooner_pipeline.company_master.yfinance_industry._fetch_info",
        side_effect=RuntimeError("boom"),
    ):
        assert _classify("AAPL") == (None, None, None, None, STATUS_ERROR)


def test_unpaced_skips_rate_limiter_wait():
    with patch("scrooner_pipeline.company_master.yfinance_industry._rate_limiter") as mock_limiter, patch(
        "scrooner_pipeline.company_master.yfinance_industry.yf.Ticker"
    ) as mock_ticker:
        mock_ticker.return_value.get_info.return_value = {"quoteType": "EQUITY", "sector": "Technology", "industry": "X"}
        _fetch_info("AAPL", paced=False)
        mock_limiter.wait.assert_not_called()


def test_paced_calls_rate_limiter_wait():
    with patch("scrooner_pipeline.company_master.yfinance_industry._rate_limiter") as mock_limiter, patch(
        "scrooner_pipeline.company_master.yfinance_industry.yf.Ticker"
    ) as mock_ticker:
        mock_ticker.return_value.get_info.return_value = {"quoteType": "EQUITY", "sector": "Technology", "industry": "X"}
        _fetch_info("AAPL", paced=True)
        mock_limiter.wait.assert_called_once()


def test_unpaced_rate_limit_fails_fast_without_retry():
    # The whole point of --no-pacing: a rate-limit hit must NOT trigger the
    # paced path's 60s-wait retry, or the "fast" pass isn't actually fast.
    with patch(
        "scrooner_pipeline.company_master.yfinance_industry._fetch_info_once",
        side_effect=YFRateLimitError(),
    ) as mock_fetch_once:
        assert _classify("AAPL", paced=False) == (None, None, None, None, STATUS_ERROR)
        mock_fetch_once.assert_called_once()  # exactly one attempt, no retry sleep


_ROW = {"company_id": 1, "sector": "Technology", "industry": "X", "about_text": "About X", "website": "https://x.com", "status": STATUS_OK}


def test_write_batch_returns_same_connection_on_success():
    conn = MagicMock()
    result = _write_batch(conn, [_ROW])
    assert result is conn
    conn.commit.assert_called_once()


def test_write_batch_empty_rows_is_a_noop():
    conn = MagicMock()
    result = _write_batch(conn, [])
    assert result is conn
    conn.cursor.assert_not_called()


def test_write_batch_reconnects_and_retries_on_dropped_connection():
    """Real crash found live 2026-09-06 (full-population backfill,
    'server closed the connection unexpectedly' after a long fetch loop
    with slow/rate-limited yfinance calls between writes): a dead
    connection must not lose the whole in-flight batch's already-fetched
    (rate-limited!) results, and the caller must get back a live
    connection to keep using for subsequent batches."""
    dead_conn = MagicMock()
    dead_conn.cursor.side_effect = psycopg.OperationalError("server closed the connection unexpectedly")

    fresh_conn = MagicMock()
    with patch("scrooner_pipeline.company_master.yfinance_industry.psycopg.connect", return_value=fresh_conn) as mock_connect:
        result = _write_batch(dead_conn, [_ROW])

    assert result is fresh_conn
    mock_connect.assert_called_once()
    fresh_conn.commit.assert_called_once()


def test_write_batch_raises_if_reconnect_write_also_fails():
    # The retry is a single attempt, not an infinite loop -- a second
    # real failure should surface, not be silently swallowed.
    dead_conn = MagicMock()
    dead_conn.cursor.side_effect = psycopg.OperationalError("first failure")

    also_dead_conn = MagicMock()
    also_dead_conn.cursor.side_effect = psycopg.OperationalError("second failure")

    with patch("scrooner_pipeline.company_master.yfinance_industry.psycopg.connect", return_value=also_dead_conn):
        with pytest.raises(psycopg.OperationalError):
            _write_batch(dead_conn, [_ROW])
