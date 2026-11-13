"""Face-column eligibility (tagmap-authority v2): a filing may be the authoritative copy of a period only when it
prints that period as a face column. Pure."""

from __future__ import annotations

from datetime import date, timedelta

from scrooner_pipeline.common.authority import face_column_eligible

END = date(2015, 2, 1)


def at(days):
    return END + timedelta(days=days)


def test_instant_windows_for_annual_and_quarterly_filings():
    assert face_column_eligible(
        "10-K", at(365), END, "instant"
    )  # next year's 10-K prints it as the prior column
    assert face_column_eligible("10-Q", at(400), END, "instant")
    assert not face_column_eligible(
        "10-K", at(401), END, "instant"
    )  # HD FY2017 10-K: a note, not a face column
    assert not face_column_eligible(
        "10-K", at(1463), END, "instant"
    )  # HD FY2018 10-K (period 2019-02-03)
    assert not face_column_eligible("10-Q/A", at(500), END, "instant")


def test_duration_ten_k_prints_three_years_ten_q_only_400_days():
    assert face_column_eligible("10-K", at(730 + 10), END, "duration")
    assert not face_column_eligible("10-K", at(730 + 11), END, "duration")
    assert face_column_eligible("10-Q", at(400), END, "duration")
    assert not face_column_eligible("10-Q", at(401), END, "duration")
    assert not face_column_eligible(
        "10-Q", at(700), END, "duration"
    )  # a 10-Q window never borrows the 10-K's 3 years
    assert face_column_eligible(
        "10-K/A", at(700), END, "duration"
    )  # amendments: same window on their own period


def test_the_original_filing_is_always_eligible():
    for ptype in ("instant", "duration"):
        for form in ("10-K", "10-Q", "10-K/A", "10-Q/A"):
            assert face_column_eligible(form, at(0), END, ptype)
            assert face_column_eligible(form, at(10), END, ptype)
    assert face_column_eligible(
        "10-K", at(-30), END, "instant"
    )  # period_of_report before the end date


def test_non_periodic_forms_never_and_unknown_period_of_report_judged_by_form_only():
    assert not face_column_eligible("DEF 14A", at(0), END, "instant")
    assert not face_column_eligible("8-K", None, END, "instant")
    assert face_column_eligible("10-K", None, END, "instant")
