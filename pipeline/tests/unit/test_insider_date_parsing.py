"""Regression test for the malformed-transactionDate bug found live 2026-08-29:
a minority of filers' Form 4 XML appends a spurious UTC-offset suffix to
transactionDate/value (e.g. "2026-05-21-05:00"), which Postgres's `date`
column rejects outright. _date() keeps only the leading YYYY-MM-DD."""

from scrooner_pipeline.ownership.insider import _date


def test_date_plain():
    assert _date("2026-05-21") == "2026-05-21"


def test_date_strips_utc_offset_suffix():
    assert _date("2026-05-21-05:00") == "2026-05-21"


def test_date_none_passthrough():
    assert _date(None) is None


def test_date_malformed_returns_none():
    assert _date("not-a-date") is None
