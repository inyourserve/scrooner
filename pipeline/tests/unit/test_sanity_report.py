import pytest

from scrooner_pipeline.sanity.report import render_markdown, should_fail_ci


def _summary(by_metric_severity):
    return {
        "companies_checked": 5,
        "oldest_checked_at": "2026-09-01",
        "newest_checked_at": "2026-09-08",
        "by_metric_severity": by_metric_severity,
        "worst_rows": [],
    }


@pytest.mark.unit
class TestShouldFailCi:
    def test_any_critical_fails(self):
        summary = _summary({"revenue_zero_check": {"critical": 1}})
        assert should_fail_ci(summary) is True

    def test_few_majors_do_not_fail(self):
        summary = _summary({"market_cap": {"major": 3}})
        assert should_fail_ci(summary, max_major=10) is False

    def test_many_majors_fail(self):
        summary = _summary({"market_cap": {"major": 11}})
        assert should_fail_ci(summary, max_major=10) is True

    def test_clean_summary_does_not_fail(self):
        summary = _summary({"market_cap": {"ok": 100}})
        assert should_fail_ci(summary) is False


@pytest.mark.unit
class TestRenderMarkdown:
    def test_no_findings_message(self):
        summary = _summary({"market_cap": {"ok": 5}})
        markdown = render_markdown(summary)
        assert "No critical or major findings." in markdown

    def test_worst_rows_rendered(self):
        summary = _summary({"market_cap": {"major": 1}})
        summary["worst_rows"] = [
            {
                "company_name": "Acme Corp", "ticker": "ACME", "metric_name": "market_cap",
                "our_value": 100, "external_value": 150, "pct_diff": -33.3, "note": None, "checked_at": "2026-09-08",
            }
        ]
        markdown = render_markdown(summary)
        assert "Acme Corp" in markdown
        assert "-33.3%" in markdown

    def test_investigation_outcomes_rendered(self):
        summary = _summary({"market_cap": {"ok": 5}})
        summary["investigation_counts"] = {"auto_fixed": 1, "needs_review": 2, "no_match_found": 3}
        summary["investigation_rows"] = [
            {
                "company_name": "Flowserve Corp", "ticker": "FLS", "concept_name": "revenue",
                "candidate_taxonomy": "us-gaap", "candidate_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "candidate_value": 3944850000, "external_value": 3939697000, "pct_diff": 0.1, "outcome": "auto_fixed",
                "note": "",
            }
        ]
        markdown = render_markdown(summary)
        assert "Auto-fixed: **1**" in markdown
        assert "Flowserve Corp" in markdown

    def test_no_investigation_section_when_nothing_investigated_yet(self):
        summary = _summary({"market_cap": {"ok": 5}})
        markdown = render_markdown(summary)
        assert "Investigation outcomes" not in markdown
