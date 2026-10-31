import pytest

from scrooner_pipeline.sanity.report import find_regressions, render_markdown


def _summary(by_metric_severity):
    return {
        "companies_checked": 5,
        "oldest_checked_at": "2026-09-01",
        "newest_checked_at": "2026-09-08",
        "by_metric_severity": by_metric_severity,
        "worst_rows": [],
    }


@pytest.mark.unit
class TestFindRegressions:
    def test_no_baseline_never_fails(self):
        summary = _summary(
            {"revenue_zero_check": {"critical": 14}, "roa": {"major": 2000}}
        )
        assert find_regressions(summary, None) == []

    def test_existing_backlog_at_baseline_passes(self):
        counts = {"revenue_zero_check": {"critical": 14}, "roa": {"major": 2000}}
        assert find_regressions(_summary(counts), counts) == []

    def test_any_critical_increase_fails(self):
        baseline = {"revenue_zero_check": {"critical": 14}}
        summary = _summary({"revenue_zero_check": {"critical": 15}})
        assert find_regressions(summary, baseline) == ["critical: 14 -> 15"]

    def test_critical_in_new_metric_fails_even_if_total_flat(self):
        baseline = {"revenue_zero_check": {"critical": 2}}
        summary = _summary(
            {"revenue_zero_check": {"critical": 1}, "market_cap": {"critical": 1}}
        )
        assert find_regressions(summary, baseline) == [
            "market_cap: new critical findings (1)"
        ]

    def test_major_rotation_noise_within_tolerance_passes(self):
        baseline = {"roa": {"major": 2000}}
        summary = _summary({"roa": {"major": 2100}})  # +5% of 2000 = 100 allowed
        assert find_regressions(summary, baseline) == []

    def test_major_jump_in_one_metric_fails(self):
        baseline = {"roa": {"major": 2000}, "market_cap": {"major": 100}}
        summary = _summary({"roa": {"major": 1900}, "market_cap": {"major": 200}})
        got = find_regressions(summary, baseline)
        assert len(got) == 1 and got[0].startswith("market_cap major: 100 -> 200")

    def test_small_metric_uses_absolute_minimum_tolerance(self):
        baseline = {"trailing_pe": {"major": 4}}
        assert (
            find_regressions(_summary({"trailing_pe": {"major": 29}}), baseline) == []
        )
        assert any(
            r.startswith("trailing_pe major: 4 -> 30")
            for r in find_regressions(
                _summary({"trailing_pe": {"major": 30}}), baseline
            )
        )

    def test_improvement_passes(self):
        baseline = {"revenue_zero_check": {"critical": 14}, "roa": {"major": 2000}}
        summary = _summary(
            {"revenue_zero_check": {"critical": 3}, "roa": {"major": 500}}
        )
        assert find_regressions(summary, baseline) == []


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
                "company_name": "Acme Corp",
                "ticker": "ACME",
                "metric_name": "market_cap",
                "our_value": 100,
                "external_value": 150,
                "pct_diff": -33.3,
                "note": None,
                "checked_at": "2026-09-08",
            }
        ]
        markdown = render_markdown(summary)
        assert "Acme Corp" in markdown
        assert "-33.3%" in markdown

    def test_investigation_outcomes_rendered(self):
        summary = _summary({"market_cap": {"ok": 5}})
        summary["investigation_counts"] = {
            "auto_fixed": 1,
            "needs_review": 2,
            "no_match_found": 3,
        }
        summary["investigation_rows"] = [
            {
                "company_name": "Flowserve Corp",
                "ticker": "FLS",
                "concept_name": "revenue",
                "candidate_taxonomy": "us-gaap",
                "candidate_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "candidate_value": 3944850000,
                "external_value": 3939697000,
                "pct_diff": 0.1,
                "outcome": "auto_fixed",
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


@pytest.mark.unit
class TestMajorRate:
    """The gate counts majors against all rows, so more coverage (fewer missing_ours) reads as a regression; the rate
    among evaluated rows is shown next to the count. The threshold itself is unchanged."""

    def test_rate_excludes_missing_rows(self):
        from scrooner_pipeline.sanity.report import major_rate

        assert (
            major_rate({"major": 20, "ok": 60, "minor": 20, "missing_ours": 900}) == 0.2
        )
        assert major_rate({"missing_ours": 5}) is None

    def test_more_coverage_lowers_the_rate_even_when_the_count_rises(self):
        from scrooner_pipeline.sanity.report import find_regressions

        baseline = {"quick_ratio": {"major": 100, "ok": 300, "missing_ours": 2000}}
        now = {
            "quick_ratio": {"major": 200, "ok": 1900, "minor": 100, "missing_ours": 600}
        }
        out = find_regressions(_summary(now), baseline)
        assert any(
            "quick_ratio major: 100 -> 200" in r and "25.0% -> 9.1%" in r for r in out
        )  # still a gate failure

    def test_gate_threshold_is_unchanged(self):
        baseline = {"roa": {"major": 2000}}
        assert find_regressions(_summary({"roa": {"major": 2100}}), baseline) == []
        assert find_regressions(_summary({"roa": {"major": 2101}}), baseline) != []

    def test_rate_lines_show_count_evaluated_and_baseline(self):
        from scrooner_pipeline.sanity.report import major_rate_lines

        lines = major_rate_lines(
            _summary({"roe": {"major": 10, "ok": 90, "missing_ours": 7}}),
            {"roe": {"major": 5, "ok": 45}},
        )
        assert lines == [
            "roe: major 10 of 100 evaluated (10.0%); baseline 5 of 50 (10.0%)"
        ]


@pytest.mark.unit
class TestMissingOursGate:
    """A coverage loss (missing_ours rising) fails the gate like a new major; 3c42fe1's move has a one-time,
    expiring allowance (report.MISSING_OURS_TRANSITION)."""

    AFTER = __import__("datetime").date(2026, 11, 15)
    DURING = __import__("datetime").date(2026, 11, 1)

    def test_a_coverage_loss_in_one_metric_fails(self):
        baseline = {"roa": {"missing_ours": 100, "ok": 900}}
        now = _summary({"roa": {"missing_ours": 126, "ok": 874}})  # +26 > max(25, 5)
        assert "roa missing_ours (coverage loss): 100 -> 126" in find_regressions(
            now, baseline, today=self.AFTER
        )
        within = _summary({"roa": {"missing_ours": 125, "ok": 875}})
        assert find_regressions(within, baseline, today=self.AFTER) == []

    def test_a_coverage_loss_in_total_fails(self):
        # ten small metrics each within their own minimum tolerance (+25), together past the total's (+50)
        baseline = {f"m{i}": {"missing_ours": 100} for i in range(10)}
        now = _summary({f"m{i}": {"missing_ours": 125} for i in range(10)})
        assert find_regressions(now, baseline, today=self.AFTER) == [
            "missing_ours (all metrics, coverage loss): 1000 -> 1250"
        ]
        ok = _summary({f"m{i}": {"missing_ours": 105} for i in range(10)})  # total +50
        assert find_regressions(ok, baseline, today=self.AFTER) == []

    def test_more_coverage_passes(self):
        baseline = {"roa": {"missing_ours": 600, "ok": 300}}
        assert (
            find_regressions(
                _summary({"roa": {"missing_ours": 100, "ok": 800}}), baseline
            )
            == []
        )

    def test_the_3c42fe1_move_is_allowed_only_until_the_transition_ends(self):
        from scrooner_pipeline.sanity import report

        move = report.MISSING_OURS_TRANSITION[
            "debt_to_equity"
        ]  # 731 rows move over a rotation
        baseline = {"debt_to_equity": {"missing_ours": 689, "major": 2000}}
        now = _summary(
            {"debt_to_equity": {"missing_ours": 689 + move, "major": 2000 - move}}
        )
        assert find_regressions(now, baseline, today=self.DURING) == []
        assert (
            find_regressions(now, baseline, today=report.MISSING_OURS_TRANSITION_UNTIL)
            == []
        )
        assert (
            f"debt_to_equity missing_ours (coverage loss): 689 -> {689 + move}"
            in find_regressions(now, baseline, today=self.AFTER)
        )
        # the allowance never exceeds the measured move: one row more than move + tolerance fails during it too
        over = _summary({"debt_to_equity": {"missing_ours": 689 + move + 35}})
        assert find_regressions(over, baseline, today=self.DURING) != []

    def test_the_allowance_is_the_read_only_count_of_rows_that_move(self):
        from scrooner_pipeline.sanity import report

        assert sum(report.MISSING_OURS_TRANSITION.values()) == 5288
