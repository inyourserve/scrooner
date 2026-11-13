"""Shared authority helpers for periodic-filing copies of one fact.

face_column_eligible is the minimal version written by the cell-proof work (R13, 2026-11-13) so the
proof and the authority rule judge the same thing: a copy of a fact counts as a candidate for
"the latest filed authoritative copy" only if its filing can print the period as a face column of a
statement. The authority-rule agent (latest_filed_tagmap_v2) reuses and may extend this function.
"""

from __future__ import annotations

from datetime import date, timedelta

PERIODIC_10K = ("10-K", "10-K/A", "10-KT", "10-KT/A")
PERIODIC_10Q = ("10-Q", "10-Q/A", "10-QT", "10-QT/A")

INSTANT_MAX_AGE = timedelta(
    days=400
)  # 10-K and 10-Q: the balance sheet date and the prior year end
DURATION_10K_MAX_AGE = timedelta(
    days=2 * 365 + 10
)  # a 10-K prints up to three annual columns
DURATION_10Q_MAX_AGE = timedelta(days=400)


def face_column_eligible(
    *,
    form: str | None,
    period_type: str,
    end_date: date,
    period_of_report: date | None,
    is_original: bool = False,
) -> bool:
    """Does the filing print this period as a face column? Measured as period_of_report - end_date.
    Instants: 10-K/10-Q <= 400 days. Durations: 10-K <= 2 years + 10 days, 10-Q <= 400 days.
    The original filing of the period (is_original) is always eligible; a copy with no
    period_of_report cannot be judged and stays eligible."""
    if is_original or period_of_report is None:
        return True
    age = period_of_report - end_date
    f = (form or "").upper()
    if period_type == "instant":
        return age <= INSTANT_MAX_AGE
    if f in PERIODIC_10K:
        return age <= DURATION_10K_MAX_AGE
    return age <= DURATION_10Q_MAX_AGE
