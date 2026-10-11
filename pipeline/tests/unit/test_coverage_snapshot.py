from datetime import date
from decimal import Decimal

import pytest

from scrooner_pipeline.mapper.coverage_snapshot import (
    CORE_V1_METRIC_NAMES,
    compute_snapshot,
)


class _FakeCursor:
    def __init__(self, total_active, concept_rows, metric_rows):
        self._total_active = total_active
        self._concept_rows = concept_rows
        self._metric_rows = metric_rows
        self._last_result = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        s = sql.strip()
        if "count(*) from core.company" in s:
            self._last_result = ("scalar", self._total_active)
        elif "company_population" in s:
            self._last_result = ("rows", getattr(self, "_population_rows", []))
        elif "canonical_concept" in s:
            self._last_result = ("rows", self._concept_rows)
        elif "metric_definition" in s:
            self._last_result = ("rows", self._metric_rows)

    def fetchone(self):
        kind, value = self._last_result
        return (value,) if kind == "scalar" else None

    def fetchall(self):
        _kind, value = self._last_result
        return value


class _FakeConnection:
    def __init__(self, total_active, concept_rows, metric_rows, population_rows=None):
        self._total_active = total_active
        self._concept_rows = concept_rows
        self._metric_rows = metric_rows
        self._population_rows = population_rows or []

    def cursor(self):
        cur = _FakeCursor(self._total_active, self._concept_rows, self._metric_rows)
        cur._population_rows = self._population_rows
        return cur


@pytest.mark.unit
class TestComputeSnapshot:
    def test_coverage_pct_computed_correctly_per_item(self):
        conn = _FakeConnection(
            total_active=100,
            concept_rows=[("revenue", 90), ("goodwill", 60)],
            metric_rows=[("roic", 50)],
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        by_name = {(r["item_type"], r["item_name"]): r for r in result["rows"]}
        assert by_name[("concept", "revenue")]["coverage_pct"] == Decimal("90.00")
        assert by_name[("concept", "goodwill")]["coverage_pct"] == Decimal("60.00")
        assert by_name[("metric", "roic")]["coverage_pct"] == Decimal("50.00")

    def test_avg_scores_are_unweighted_means(self):
        conn = _FakeConnection(
            total_active=100,
            concept_rows=[("a", 90), ("b", 10)],
            metric_rows=[("x", 100), ("y", 0), ("z", 50)],
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        assert result["avg_concept_coverage_score"] == Decimal("50.00")
        assert result["avg_metric_coverage_score"] == Decimal("50.00")

    def test_zero_total_active_companies_does_not_divide_by_zero(self):
        conn = _FakeConnection(
            total_active=0, concept_rows=[("a", 0)], metric_rows=[("x", 0)]
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        assert result["avg_concept_coverage_score"] == Decimal("0.00")
        assert result["avg_metric_coverage_score"] == Decimal("0.00")

    def test_score_rows_included_with_correct_item_type(self):
        conn = _FakeConnection(
            total_active=10, concept_rows=[("a", 5)], metric_rows=[("x", 5)]
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        score_rows = [r for r in result["rows"] if r["item_type"] == "score"]
        names = {r["item_name"] for r in score_rows}
        assert names == {
            "avg_concept_coverage_score",
            "avg_metric_coverage_score",
            "avg_core_v1_metric_coverage_score",
        }

    def test_core_v1_score_only_averages_the_20_locked_v1_metric_names(self):
        """CORE_V1_METRIC_NAMES is sourced directly from mapper/definitions.py
        -- this test picks 2 real locked names (guaranteed present) plus 2
        made-up non-locked names, and confirms only the real ones count."""
        locked = sorted(CORE_V1_METRIC_NAMES)[:2]
        conn = _FakeConnection(
            total_active=100,
            concept_rows=[("a", 50)],
            metric_rows=[
                (locked[0], 100),
                (locked[1], 0),
                ("totally_not_a_locked_metric", 40),
                ("also_not_locked", 60),
            ],
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        assert result["avg_core_v1_metric_coverage_score"] == Decimal("50.00")
        assert result["avg_metric_coverage_score"] == Decimal("50.00")

    def test_core_v1_score_is_zero_when_none_of_the_metrics_are_locked(self):
        conn = _FakeConnection(
            total_active=100, concept_rows=[("a", 50)], metric_rows=[("not_locked", 90)]
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        assert result["avg_core_v1_metric_coverage_score"] == Decimal("0.00")

    def test_dividend_metric_uses_dividend_payer_denominator_not_total_active(self):
        # Found live 2026-10-03, direct user report: dividend_yield showed
        # 22.32% coverage against ALL 5,216 active companies, which looks
        # like a huge gap but is mostly "most companies never pay a
        # dividend." 50 companies covered out of a 1,000-company active
        # population is a misleading 5% -- but against the real
        # dividend_payer population (200, in this test), it's a correct 25%.
        conn = _FakeConnection(
            total_active=1000,
            concept_rows=[],
            metric_rows=[("dividend_yield", 50)],
            population_rows=[("dividend_payer", 200), ("real_operating_company", 900)],
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        by_name = {(r["item_type"], r["item_name"]): r for r in result["rows"]}
        row = by_name[("metric", "dividend_yield")]
        assert row["total_active_companies"] == 200
        assert row["coverage_pct"] == Decimal("25.00")

    def test_non_family_metric_uses_real_operating_company_denominator(self):
        # A metric with no named family (e.g. roic) should default to
        # real_operating_company, not raw total_active -- the same
        # corrected-denominator reasoning this project already applied to
        # revenue (2026-09-12), generalized here to every concept/metric.
        conn = _FakeConnection(
            total_active=1000,
            concept_rows=[],
            metric_rows=[("roic", 450)],
            population_rows=[("real_operating_company", 900)],
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        by_name = {(r["item_type"], r["item_name"]): r for r in result["rows"]}
        row = by_name[("metric", "roic")]
        assert row["total_active_companies"] == 900
        assert row["coverage_pct"] == Decimal("50.00")

    def test_score_rows_report_real_total_active_not_item_count(self):
        # Found live 2026-10-03: avg_metric_coverage_score's own row used
        # to set total_active_companies = the METRIC count (e.g. 82), not
        # a real company count -- misread out of context as "only 82
        # active companies." Must now show the real total_active value.
        conn = _FakeConnection(
            total_active=5216,
            concept_rows=[("a", 50)],
            metric_rows=[("x", 10), ("y", 20)],
        )
        result = compute_snapshot(conn, as_of=date(2026, 9, 2))
        by_name = {(r["item_type"], r["item_name"]): r for r in result["rows"]}
        score_row = by_name[("score", "avg_metric_coverage_score")]
        assert score_row["total_active_companies"] == 5216
        assert score_row["companies_covered"] == 2  # 2 metrics averaged, not companies
