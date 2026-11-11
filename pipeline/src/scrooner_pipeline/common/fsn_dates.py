"""FSN dates against true period ends.

The SEC Financial Statement and Notes data sets store `num.ddate` (and `sub.period`) ROUNDED TO THE NEAREST MONTH
END. A true period end in mid-month (52/53-week or 12/16-week calendars: Kroger's Q2 ends 2015-08-15, stored as
2015-07-31) is then 13-16 days from its FSN date, outside a plain +-10-day match, and the key reads as a gap
although the value is stored (FSN missing-quarter review, 2026-11-09)."""

from datetime import date, timedelta


def _last_day(year: int, month: int) -> date:
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    return nxt - timedelta(days=1)


def nearest_month_ends(d: date) -> set[date]:
    """The month end(s) nearest to d: the end of d's month or of the month before (both on a tie)."""
    cur = _last_day(d.year, d.month)
    prev = date(d.year, d.month, 1) - timedelta(days=1)
    a, b = (cur - d).days, (d - prev).days
    if a < b:
        return {cur}
    if b < a:
        return {prev}
    return {cur, prev}


def fsn_end_matches(fsn_end: date, true_end: date, days: int = 10) -> bool:
    """True when an FSN date stands for a true period end: within `days`, or the SEC's month-end rounding of it."""
    return abs((fsn_end - true_end).days) <= days or fsn_end in nearest_month_ends(
        true_end
    )
