"""52/53-week year ends against fsn.filing.period (the SEC's month-end rounding), NVDA/AAPL trace 2026-11-16."""

from datetime import date

from scrooner_pipeline.mapper import top100_coverage as t100


def test_own_year_page_matches_a_52_53_week_end_to_the_month_end_key():
    pages = {(1, date(2026, 1, 31), "IS"): ("ACC", "R4.htm")}
    # NVDA true year end 2026-01-25; fsn.filing.period is the month end 2026-01-31
    assert t100.own_year_page(pages, 1, date(2026, 1, 25), "IS") == ("ACC", "R4.htm")
    # AAPL true end 2026-09-26 against 2026-09-30
    p2 = {(2, date(2026, 9, 30), "BS"): ("A2", "R2.htm")}
    assert t100.own_year_page(p2, 2, date(2026, 9, 26), "BS") == ("A2", "R2.htm")
    # the indexed path agrees
    idx = t100.stmt_pages_by_company(p2)
    assert t100.own_year_page(p2, 2, date(2026, 9, 26), "BS", idx) == ("A2", "R2.htm")
    # another statement, another company, or a different year never matches
    assert t100.own_year_page(pages, 1, date(2026, 1, 25), "BS") == ("", "")
    assert t100.own_year_page(pages, 9, date(2026, 1, 25), "IS") == ("", "")
    assert t100.own_year_page(pages, 1, date(2025, 1, 26), "IS") == ("", "")


def test_eligible_filings_and_reason_stay_verified_for_a_52_53_week_year():
    # Kroger-style mid-month end 2015-08-15 is 16 days from the month-end key 2015-07-31
    filings = [(date(2015, 7, 31), "K1")]
    assert t100.eligible_filings(filings, date(2015, 8, 15), False) == {"K1"}
    assert t100.own_period_reason(
        "REASON", "x", "K1", filings, date(2015, 8, 15), False, date(2015, 1, 1)
    ) == ("REASON", "x")
    # a different year is still not eligible
    assert t100.eligible_filings(filings, date(2012, 8, 15), False) == set()
    assert t100.reached_by_filing(date(2015, 8, 15), filings, date(2026, 1, 1))
