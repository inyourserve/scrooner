from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from scrooner_pipeline.screener import query as query_module
from scrooner_pipeline.screener.evaluate import evaluate_between, evaluate_comparison, rank_top_bottom
from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery


@pytest.mark.unit
@pytest.mark.parametrize("operator,value,target,expected", [
    (">", "2", "1", True),
    ("<", "1", "2", True),
    (">=", "2", "2", True),
    ("<=", "2", "2", True),
    ("=", "2", "2", True),
    ("!=", "2", "3", True),
])
def test_all_comparison_operators(operator, value, target, expected):
    assert evaluate_comparison(Decimal(value), operator, Decimal(target)) is expected
    assert evaluate_comparison(None, operator, Decimal(target)) is False


@pytest.mark.unit
def test_between_is_inclusive_and_null_safe():
    bounds = (Decimal("1"), Decimal("2"))
    assert evaluate_between(Decimal("1"), bounds) is True
    assert evaluate_between(Decimal("2"), bounds) is True
    assert evaluate_between(Decimal("2.1"), bounds) is False
    assert evaluate_between(None, bounds) is False


@pytest.mark.unit
def test_rank_operators_exclude_nulls_and_break_ties_by_cik():
    candidates = [("0003", Decimal("10")), ("0002", Decimal("10")), ("0001", None), ("0004", Decimal("5"))]

    assert rank_top_bottom(candidates, "top_n", 3) == ["0002", "0003", "0004"]
    assert rank_top_bottom(candidates, "bottom_n", 3) == ["0004", "0002", "0003"]


@pytest.mark.unit
@pytest.mark.parametrize("payload", [
    {"metric_name": "roe", "operator": ">"},
    {"metric_name": "roe", "operator": ">", "value": 1, "n": 5},
    {"metric_name": "roe", "operator": "between"},
    {"metric_name": "roe", "operator": "between", "value_range": [2, 1]},
    {"metric_name": "roe", "operator": "between", "value_range": [1, 2], "value": 1},
    {"metric_name": "roe", "operator": "top_n", "n": 0},
    {"metric_name": "roe", "operator": "top_n", "n": 5, "value": 1},
])
def test_malformed_predicates_are_rejected(payload):
    with pytest.raises(ValidationError):
        MetricPredicate.model_validate(payload)


@pytest.mark.unit
def test_multiple_ranked_predicates_are_rejected():
    with pytest.raises(ValidationError):
        ScreenQuery(
            metric_predicates=[
                MetricPredicate(metric_name="roe", operator="top_n", n=2),
                MetricPredicate(metric_name="roic", operator="bottom_n", n=2),
            ]
        )


@pytest.mark.unit
@pytest.mark.parametrize("limit", [0, -1])
def test_non_positive_result_limit_is_rejected(limit):
    with pytest.raises(ValidationError):
        ScreenQuery(limit=limit)


class InactiveCursor:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, _sql, _params=()):
        pass

    def fetchall(self):
        return [("inactive-cik",)]


class InactiveConnection:
    def cursor(self):
        return InactiveCursor()


def resolved_row(value, row_id):
    return {
        "value": value,
        "period_label": "TTM",
        "period_end": date(2026, 6, 30),
        "formula_version": 1,
        "is_null_reason": None,
        "row_id": row_id,
    }


@pytest.mark.unit
def test_query_output_is_deterministic_includes_sort_lineage_and_keeps_nulls_last(monkeypatch):
    companies = {
        3: {"cik": "0003", "company_name": "C", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "C"},
        1: {"cik": "0001", "company_name": "A", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "A"},
        2: {"cik": "0002", "company_name": "B", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "B"},
        4: {"cik": "0004", "company_name": "D", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "D"},
    }
    resolved = {
        (1, 10): resolved_row(Decimal("0.4"), 1),
        (2, 10): resolved_row(Decimal("0.4"), 2),
        (3, 10): resolved_row(Decimal("0.2"), 3),
        (4, 10): resolved_row(None, 4),
    }
    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {"roe": 10})
    monkeypatch.setattr(query_module, "get_dataset_version", lambda _conn: 1)
    monkeypatch.setattr(query_module, "_load_candidate_companies", lambda _conn, _include: dict(companies))
    monkeypatch.setattr(query_module, "_load_snapshot_values", lambda _conn, _ids, _version: resolved)
    query = ScreenQuery(sort_by="roe", sort_desc=True)

    first = query_module.run_query(InactiveConnection(), query)
    second = query_module.run_query(InactiveConnection(), query)

    assert [row["cik"] for row in first["matched"]] == ["0001", "0002", "0003", "0004"]
    assert first == second
    assert first["matched"][0]["metrics"]["roe"]["value"] == Decimal("0.4")
    assert first["excluded_inactive"] == ["inactive-cik"]


@pytest.mark.unit
def test_ranked_query_returns_rank_order_not_database_order(monkeypatch):
    companies = {
        1: {"cik": "0001", "company_name": "A", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "A"},
        3: {"cik": "0003", "company_name": "C", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "C"},
        2: {"cik": "0002", "company_name": "B", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "B"},
    }
    resolved = {
        (1, 10): resolved_row(Decimal("1"), 1),
        (2, 10): resolved_row(Decimal("3"), 2),
        (3, 10): resolved_row(Decimal("2"), 3),
    }
    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {"roe": 10})
    monkeypatch.setattr(query_module, "get_dataset_version", lambda _conn: 1)
    monkeypatch.setattr(query_module, "_load_candidate_companies", lambda _conn, _include: dict(companies))
    monkeypatch.setattr(query_module, "_load_snapshot_values", lambda _conn, _ids, _version: resolved)
    query = ScreenQuery(metric_predicates=[MetricPredicate(metric_name="roe", operator="top_n", n=2)])

    result = query_module.run_query(InactiveConnection(), query)

    assert [row["cik"] for row in result["matched"]] == ["0002", "0003"]
