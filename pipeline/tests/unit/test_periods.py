from datetime import date

import pytest

from scrooner_pipeline.normalizer.periods import (
    build_fye_anchors,
    classify_period,
    extract_distinct_periods,
)


@pytest.mark.unit
def test_period_extraction_and_non_calendar_fiscal_classification(companyfacts_payload):
    periods = extract_distinct_periods(companyfacts_payload)
    assert periods == {("2025-09-27", "2024-09-29")}

    # Apple-style September fiscal year: Q1 belongs to fiscal 2025 even
    # though its end date is in calendar 2024.
    anchors = build_fye_anchors(
        {
            ("2024-09-28", "2023-10-01"),
            ("2025-09-27", "2024-09-29"),
        }
    )
    q1 = classify_period("2024-12-28", "2024-09-29", anchors, (9, 27))

    assert q1 == {
        "start_date": date(2024, 9, 29),
        "end_date": date(2024, 12, 28),
        "period_type": "duration",
        "fiscal_year": 2025,
        "fiscal_period": "Q1",
    }


@pytest.mark.unit
def test_instant_full_year_and_unclassified_ytd_spans_are_distinct():
    anchors = [date(2024, 9, 28), date(2025, 9, 27)]

    instant = classify_period("2025-09-27", None, anchors, (9, 27))
    half_year_ytd = classify_period("2025-03-29", "2024-09-29", anchors, (9, 27))

    assert instant["period_type"] == "instant"
    assert instant["start_date"] == instant["end_date"]
    assert instant["fiscal_period"] == "FY"
    assert half_year_ytd["period_type"] == "duration"
    assert half_year_ytd["fiscal_year"] == 2025
    assert half_year_ytd["fiscal_period"] is None


@pytest.mark.unit
def test_full_year_anchor_uses_observed_dates_not_nominal_month_day():
    periods = {
        ("2023-06-30", "2022-07-01"),
        ("2024-06-30", "2023-07-01"),
        ("2024-03-31", "2024-01-01"),
    }

    assert build_fye_anchors(periods) == [date(2023, 6, 30), date(2024, 6, 30)]


@pytest.mark.unit
def test_feb_29_fye_anchor_extrapolates_without_crashing():
    """Found live 2026-09-03 (MannKind, CIK 0000899460): a company with an
    observed Feb 29 fiscal-year-end anchor crashed _bracket_fye's plain
    date(candidate.year +/- 1, ...) step the moment it needed to
    extrapolate into a non-leap year (nearly every year). Feb 29 rolls to
    Feb 28 in a non-leap target year instead of raising ValueError."""
    anchors = [date(2020, 2, 29)]

    # Extrapolate forward past the single observed leap-year anchor --
    # 2021/2022/2023 are all non-leap, only 2024 has a real Feb 29.
    forward = classify_period("2023-05-15", "2023-02-16", anchors, (2, 29))
    assert forward["period_type"] == "duration"

    # Extrapolate backward the same way.
    backward = classify_period("2019-05-15", "2019-02-16", anchors, (2, 29))
    assert backward["period_type"] == "duration"

