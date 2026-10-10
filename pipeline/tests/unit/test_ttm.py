import pytest


@pytest.mark.unit
def test_dedupe_ttm_rows_collapses_same_end_date_and_prefers_a_real_value():
    """Vishay (2026-10-03): two Q4 spans ending 2009-01-03 each emitted a TTM
    row for that date; the duplicate aborted the company's whole write."""
    from datetime import date

    from scrooner_pipeline.mapper.ttm import _dedupe_ttm_rows

    d = date(2009, 1, 3)
    base = {
        "company_id": 1,
        "metric_definition_id": 5,
        "period_start": d,
        "period_end": d,
        "period_label": "TTM",
    }
    rows = [
        {
            **base,
            "value": None,
            "is_null_reason": "incomplete:x",
            "source_fact_ids": None,
        },
        {**base, "value": 0.15, "is_null_reason": None, "source_fact_ids": [1]},
        {
            **base,
            "metric_definition_id": 6,
            "value": 0.2,
            "is_null_reason": None,
            "source_fact_ids": [2],
        },
    ]
    out = _dedupe_ttm_rows(rows)
    assert len(out) == 2
    roic = next(r for r in out if r["metric_definition_id"] == 5)
    assert roic["value"] == 0.15
