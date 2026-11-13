"""Which copy of a fact may be the authoritative one: the face-column eligibility rule (Dhairya 2026-11-13,
tagmap-authority v2). ONE definition; the normalizer (conflict_latest_filed) and the proof (R13) both import it.

Why: a filing carries a period as a copy for many reasons. HD Goodwill at 2015-02-01 is 1,353M in seven filings
(FY2014 10-K, 10-Qs, FY2015 and FY2017 10-Ks); the FY2018 10-K printed 2,102M for that date from a note rollforward
context and won as "latest filed". A filing speaks for a period only when it PRINTS that period as a face column,
which its own period_of_report bounds:

  instant   10-K / 10-Q (and amendments): period_of_report - end_date <= 400 days (current and prior year-end)
  duration  10-K family: <= 2 years + 10 days (the income statement and cash flow print three fiscal years)
            10-Q family: <= 400 days
  The original filing (period_of_report within 10 days of the end date) is always eligible, so every period keeps
  an eligible copy. An amendment takes the same windows on its own period_of_report. Forms that are not periodic
  reports are never eligible. An unknown period_of_report cannot be judged and is treated as eligible (no evidence
  it is a far-later filing); the form test still applies.

Eligible copies compete (latest filed wins, ties to the lower accession); an ineligible copy is history only.
"""

from __future__ import annotations

from datetime import date

from scrooner_pipeline.common.periodic_forms import (
    ANNUAL_FORMS_ALL,
    PERIODIC_FORMS_ALL,
)

ORIGINAL_WINDOW_DAYS = 10
INSTANT_WINDOW_DAYS = 400
QUARTERLY_DURATION_WINDOW_DAYS = 400
ANNUAL_DURATION_WINDOW_DAYS = 2 * 365 + 10


def face_column_eligible(
    form: str,
    period_of_report: date | None,
    end_date: date,
    period_type: str,
) -> bool:
    """True when `form`'s filing (period_of_report) prints the period ending end_date as a face column."""
    if form not in PERIODIC_FORMS_ALL:
        return False
    if period_of_report is None:
        return True
    days = (period_of_report - end_date).days
    if days <= ORIGINAL_WINDOW_DAYS:
        return True
    if period_type == "instant":
        return days <= INSTANT_WINDOW_DAYS
    if form in ANNUAL_FORMS_ALL:
        return days <= ANNUAL_DURATION_WINDOW_DAYS
    return days <= QUARTERLY_DURATION_WINDOW_DAYS
