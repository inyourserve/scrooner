from datetime import date

import pytest

from scrooner_pipeline.incidents.verifier import diff_state


def _row(source, metric, severity, period_end=None):
    return {"source_system": source, "metric_or_concept": metric, "severity": severity, "period_end": period_end}


@pytest.mark.unit
class TestDiffState:
    def test_resolved_when_bad_then_ok(self):
        before = [_row("timeseries", "revenue", "outlier", date(2026, 3, 31))]
        after = [_row("timeseries", "revenue", "ok", date(2026, 3, 31))]
        diff = diff_state(before, after)
        assert len(diff["resolved"]) == 1
        assert diff["resolved"][0]["before"] == "outlier"
        assert diff["regressed"] == []
        assert diff["still_open"] == []

    def test_resolved_when_row_disappears_entirely(self):
        before = [_row("data_sanity", "revenue_zero_check", "critical")]
        after = []
        diff = diff_state(before, after)
        assert len(diff["resolved"]) == 1

    def test_regressed_when_new_bad_row_appears(self):
        before = [_row("timeseries", "net_income", "ok", date(2026, 3, 31))]
        after = [_row("timeseries", "net_income", "sign_violation", date(2026, 3, 31))]
        diff = diff_state(before, after)
        assert len(diff["regressed"]) == 1
        assert diff["resolved"] == []

    def test_still_open_when_bad_both_times_same_severity(self):
        before = [_row("sec_frames", "revenue", "major", date(2026, 3, 31))]
        after = [_row("sec_frames", "revenue", "major", date(2026, 3, 31))]
        diff = diff_state(before, after)
        assert len(diff["still_open"]) == 1

    def test_still_open_when_bad_both_times_different_severity(self):
        before = [_row("data_sanity", "market_cap", "critical")]
        after = [_row("data_sanity", "market_cap", "minor")]
        diff = diff_state(before, after)
        assert len(diff["still_open"]) == 1
        assert diff["still_open"][0]["before"] == "critical"
        assert diff["still_open"][0]["after"] == "minor"

    def test_unchanged_ok_not_reported_but_counted(self):
        before = [_row("timeseries", "revenue", "ok", date(2026, 3, 31))]
        after = [_row("timeseries", "revenue", "ok", date(2026, 3, 31))]
        diff = diff_state(before, after)
        assert diff["resolved"] == diff["regressed"] == diff["still_open"] == []
        assert diff["unchanged_ok_count"] == 1

    def test_different_periods_tracked_independently(self):
        before = [
            _row("timeseries", "revenue", "outlier", date(2026, 3, 31)),
            _row("timeseries", "revenue", "ok", date(2025, 12, 31)),
        ]
        after = [
            _row("timeseries", "revenue", "ok", date(2026, 3, 31)),
            _row("timeseries", "revenue", "outlier", date(2025, 12, 31)),
        ]
        diff = diff_state(before, after)
        assert len(diff["resolved"]) == 1
        assert len(diff["regressed"]) == 1
