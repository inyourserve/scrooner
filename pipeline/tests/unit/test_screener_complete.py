from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from scrooner_pipeline.screener import query as query_module
from scrooner_pipeline.screener.evaluate import evaluate_between, evaluate_comparison, rank_top_bottom
from scrooner_pipeline.screener.schema import MetricPredicate, PredicateGroup, ScreenQuery


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


def snapshot_rows(companies, resolved, catalog, inactive_ciks=("inactive-cik",)):
    """Shape run_query's single snapshot read returns (_select_snapshot_rows):
    [(company_id, identity, {metric_name: citation})], non-null values only,
    plus inactive companies riding along in the same read."""
    id_to_name = {metric_id: name for name, metric_id in catalog.items()}
    rows = []
    for company_id, identity in companies.items():
        metrics = {
            id_to_name[metric_id]: {k: data[k] for k in ("value", "period_label", "period_end", "formula_version")}
            for (cid, metric_id), data in resolved.items()
            if cid == company_id and data["value"] is not None
        }
        rows.append((company_id, {"sector": None, **identity}, metrics))
    for offset, cik in enumerate(inactive_ciks):
        rows.append((1000 + offset, {"cik": cik, "company_name": cik, "sic_code": None, "sic_description": None,
                                     "sector": None, "status": "inactive", "ticker": None}, {}))
    return rows


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
    rows = snapshot_rows(companies, resolved, {"roe": 10})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", lambda *_args: rows)
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
    rows = snapshot_rows(companies, resolved, {"roe": 10})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", lambda *_args: rows)
    query = ScreenQuery(metric_predicates=[MetricPredicate(metric_name="roe", operator="top_n", n=2)])

    result = query_module.run_query(InactiveConnection(), query)

    assert [row["cik"] for row in result["matched"]] == ["0002", "0003"]


@pytest.mark.unit
def test_boolean_tree_query_still_cites_a_ranked_predicates_own_value(monkeypatch):
    # Found live 2026-09-11: "top 5 by roic excluding financials" correctly
    # excluded Financials-sector companies, but every match showed a null
    # roic value -- metric_names_to_show for the where-tree path only
    # walked query.where (which never contains a ranked predicate, schema.py
    # forbids it) and forgot to union in the ranked predicate's own name.
    surviving = {
        1: {"cik": "0001", "company_name": "A", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "A"},
        2: {"cik": "0002", "company_name": "B", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "B"},
    }
    resolved = {
        (1, 10): resolved_row(Decimal("0.30"), 1),
        (2, 10): resolved_row(Decimal("0.20"), 2),
    }
    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {"roic": 10})
    monkeypatch.setattr(query_module, "get_dataset_version", lambda _conn: 1)
    rows = snapshot_rows(surviving, resolved, {"roic": 10})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", lambda *_args: rows)
    query = ScreenQuery(
        metric_predicates=[MetricPredicate(metric_name="roic", operator="top_n", n=2)],
        where=PredicateGroup(op="not", predicates=[MetricPredicate(metric_name="roic", operator=">", value="999")]),
    )

    result = query_module.run_query(InactiveConnection(), query)

    values = {row["cik"]: row["metrics"]["roic"]["value"] for row in result["matched"]}
    assert values == {"0001": Decimal("0.30"), "0002": Decimal("0.20")}


@pytest.mark.unit
def test_boolean_tree_query_reads_the_snapshot_once_with_the_filter_and_citations(monkeypatch):
    # 2026-09-26: the tree filter, citation columns and the inactive list
    # come from ONE version-scoped read (was three round trips). Citation
    # columns are fetched only for rows the SQL filter already kept
    # (the 2026-09-20 "don't read the whole universe" fix still holds).
    calls = []

    def fake_select(_conn, dataset_version, metric_names, where_clause=None, params=None):
        calls.append((dataset_version, metric_names, where_clause, params))
        return []

    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {"roe": 10})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", fake_select)
    query = ScreenQuery(where=PredicateGroup(op="or", predicates=[MetricPredicate(metric_name="roe", operator=">", value="0.1")]))

    query_module.run_query(InactiveConnection(), query, dataset_version=5)

    assert len(calls) == 1
    dataset_version, metric_names, where_clause, params = calls[0]
    assert dataset_version == 5
    assert metric_names == ["roe"]
    assert where_clause is not None and params == [Decimal("0.1")]


@pytest.mark.unit
def test_passed_catalog_and_version_skip_their_round_trips(monkeypatch):
    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: pytest.fail("catalog refetched"))
    monkeypatch.setattr(query_module, "get_dataset_version", lambda _conn: pytest.fail("version refetched"))
    monkeypatch.setattr(query_module, "_select_snapshot_rows", lambda *_args: [])

    result = query_module.run_query(InactiveConnection(), ScreenQuery(sort_by="roe"), dataset_version=3, catalog={"roe": 10})

    assert result["dataset_version"] == 3


@pytest.mark.unit
def test_stored_run_page_rebuilds_in_stored_order_from_its_own_version(monkeypatch):
    companies = {
        1: {"cik": "0001", "company_name": "A", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "A"},
        2: {"cik": "0002", "company_name": "B", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "B"},
    }
    resolved = {(1, 10): resolved_row(Decimal("0.1"), 1), (2, 10): resolved_row(Decimal("0.9"), 2)}
    captured = {}

    def fake_select(_conn, dataset_version, metric_names, where_clause=None, params=None):
        captured.update(version=dataset_version, params=params)
        return snapshot_rows(companies, resolved, {"roe": 10}, inactive_ciks=())

    monkeypatch.setattr(query_module, "_select_snapshot_rows", fake_select)

    items = query_module.load_screen_result_page(object(), ScreenQuery(sort_by="roe", sort_desc=True), 4, [2, 1])

    assert captured == {"version": 4, "params": [[2, 1]]}, "only the page's own companies, from the run's version"
    assert [row["company_id"] for row in items] == [2, 1], "stored result order, not DB order"
    assert items[0]["metrics"]["roe"]["value"] == Decimal("0.9")


@pytest.mark.unit
def test_stored_run_page_on_a_pruned_version_returns_none(monkeypatch):
    monkeypatch.setattr(query_module, "_select_snapshot_rows", lambda *_args: [])

    assert query_module.load_screen_result_page(object(), ScreenQuery(sort_by="roe"), 1, [5]) is None
    assert query_module.load_screen_result_page(object(), ScreenQuery(sort_by="roe"), 1, []) == []
