from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from scrooner_pipeline.screener import query as query_module
from scrooner_pipeline.screener.evaluate import evaluate_between, evaluate_comparison, rank_top_bottom
from scrooner_pipeline.screener.schema import (
    CategoricalPredicate,
    MetricPredicate,
    PredicateGroup,
    ScreenQuery,
)


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


# ---------------------------------------------------------------------------
# Flat-AND SQL pre-filter (2026-10-02, doc/learnings/2026-10-02-screener-
# flat-and-prefilter.md). Correctness against the real snapshot table was
# verified by running the pre-change and post-change run_query side by
# side against the live dev database for 10 real queries covering every
# branch below (byte-identical output, see that learnings doc) -- these
# tests lock in the wiring and the one genuinely subtle case offline.
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_flat_and_query_pushes_a_safe_prefilter_into_the_snapshot_read(monkeypatch):
    calls = []

    def fake_select(_conn, dataset_version, metric_names, where_clause=None, params=None):
        calls.append((metric_names, where_clause, params))
        return []

    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {"roe": 10, "debt_to_equity": 11})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", fake_select)
    query = ScreenQuery(metric_predicates=[
        MetricPredicate(metric_name="roe", operator=">", value="0.3"),
        MetricPredicate(metric_name="debt_to_equity", operator="<", value="0.5"),
    ])

    query_module.run_query(InactiveConnection(), query, dataset_version=1)

    assert len(calls) == 1
    _metric_names, where_clause, params = calls[0]
    assert where_clause is not None, "a flat-AND query with real predicates must push a pre-filter"
    assert params == [Decimal("0.3"), Decimal("0.5")], "full_match params, in predicate order"


@pytest.mark.unit
def test_flat_and_query_with_no_predicates_skips_the_prefilter(monkeypatch):
    calls = []

    def fake_select(_conn, dataset_version, metric_names, where_clause=None, params=None):
        calls.append((where_clause, params))
        return []

    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", fake_select)

    query_module.run_query(InactiveConnection(), ScreenQuery(), dataset_version=1)

    assert calls == [(None, None)]


@pytest.mark.unit
def test_pure_ranked_query_with_no_other_predicate_skips_the_prefilter(monkeypatch):
    # Ranking needs full visibility of every candidate's own missing-data
    # status (query.py's own existing, unchanged logic) -- there is no
    # column value to push down for a bare top_n/bottom_n, so this must
    # stay a full, unfiltered read, exactly like before this change.
    calls = []

    def fake_select(_conn, dataset_version, metric_names, where_clause=None, params=None):
        calls.append((where_clause, params))
        return []

    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {"roic": 10})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", fake_select)
    query = ScreenQuery(metric_predicates=[MetricPredicate(metric_name="roic", operator="top_n", n=20)])

    query_module.run_query(InactiveConnection(), query, dataset_version=1)

    assert calls == [(None, None)]


@pytest.mark.unit
def test_categorical_only_query_pushes_a_prefilter(monkeypatch):
    calls = []

    def fake_select(_conn, dataset_version, metric_names, where_clause=None, params=None):
        calls.append((where_clause, params))
        return []

    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {})
    monkeypatch.setattr(query_module, "_select_snapshot_rows", fake_select)
    query = ScreenQuery(categorical_predicates=[CategoricalPredicate(field="sector", operator="=", value="Technology")])

    query_module.run_query(InactiveConnection(), query, dataset_version=1)

    assert calls == [calls[0]]
    where_clause, params = calls[0]
    assert where_clause is not None and params == ["Technology"]


@pytest.mark.unit
def test_compile_flat_prefilter_sql_shape_is_the_safe_superset_form():
    # Render the generated SQL.Composable directly (no live connection
    # needed -- as_string(None) works for plain ASCII identifiers) and
    # check its literal shape: "(full_match) or (any_missing)" with
    # params in full_match's own predicate order, categorical equality
    # clauses first and unrelaxed. This is what actually proves the
    # tricky "missing on A, present-and-failing on B" case stays kept --
    # the OR is across the two WHOLE sub-expressions, never a per-
    # predicate `(col is null or comparison)` AND'd together (that
    # independent form is exactly what would wrongly drop that row).
    clause, params = query_module._compile_flat_prefilter(
        [
            MetricPredicate(metric_name="roe", operator=">", value="0.2"),
            MetricPredicate(metric_name="debt_to_equity", operator="<", value="1"),
        ],
        [CategoricalPredicate(field="sector", operator="=", value="Technology")],
        {"roe": 10, "debt_to_equity": 11},
    )

    text = clause.as_string(None)
    assert text == (
        '"sector" = %s and '
        '((("roe" is not null and "roe" > %s) and '
        '("debt_to_equity" is not null and "debt_to_equity" < %s)) '
        'or ("roe" is null or "debt_to_equity" is null))'
    )
    assert params == ["Technology", Decimal("0.2"), Decimal("1")]


@pytest.mark.unit
def test_compile_flat_prefilter_vacuous_case_returns_none():
    assert query_module._compile_flat_prefilter([], [], {}) == (None, None)


@pytest.mark.unit
def test_compile_flat_prefilter_between_operator():
    clause, params = query_module._compile_flat_prefilter(
        [MetricPredicate(metric_name="roic", operator="between", value_range=("0.1", "0.3"))],
        [],
        {"roic": 10},
    )

    assert clause.as_string(None) == (
        '((("roic" is not null and "roic" between %s and %s)) or ("roic" is null))'
    )
    assert params == [Decimal("0.1"), Decimal("0.3")]


@pytest.mark.unit
def test_prefilter_keeps_a_company_missing_an_earlier_predicate_that_would_also_fail_a_later_one(monkeypatch):
    # The one genuinely subtle case this design has to get right (see
    # _compile_flat_prefilter's own module docstring): a company missing
    # metric A (so Python's sequential loop tags it excluded_missing_data
    # on A and never even checks B) must still be fetched, even though it
    # ALSO has a present-but-failing value for B -- an independent,
    # per-predicate `(col IS NULL OR comparison)` AND across predicates
    # would wrongly drop this row before Python ever saw it.
    companies = {
        1: {"cik": "0001", "company_name": "Missing-A-fails-B", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "A"},
        2: {"cik": "0002", "company_name": "Passes-both", "sic_code": "1", "sic_description": "X", "status": "active", "ticker": "B"},
    }
    resolved = {
        (1, 10): resolved_row(None, 1),  # roe missing
        (1, 11): resolved_row(Decimal("2"), 2),  # debt_to_equity present, fails < 1
        (2, 10): resolved_row(Decimal("0.5"), 3),
        (2, 11): resolved_row(Decimal("0.2"), 4),
    }
    monkeypatch.setattr(query_module, "load_screenable_metric_catalog", lambda _conn: {"roe": 10, "debt_to_equity": 11})
    monkeypatch.setattr(query_module, "get_dataset_version", lambda _conn: 1)
    rows = snapshot_rows(companies, resolved, {"roe": 10, "debt_to_equity": 11}, inactive_ciks=())
    monkeypatch.setattr(query_module, "_select_snapshot_rows", lambda *_args, **_kwargs: rows)
    query = ScreenQuery(metric_predicates=[
        MetricPredicate(metric_name="roe", operator=">", value="0.2"),
        MetricPredicate(metric_name="debt_to_equity", operator="<", value="1"),
    ])

    result = query_module.run_query(InactiveConnection(), query)

    assert [row["cik"] for row in result["matched"]] == ["0002"]
    missing = {row["cik"]: row["missing_metrics"] for row in result["excluded_missing_data"]}
    assert missing == {"0001": ["roe"]}, "tagged only on the first missing predicate, never checked against B"


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
