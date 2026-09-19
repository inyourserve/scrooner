from contextlib import contextmanager

import pytest

from routers import screen_runs
from scrooner_pipeline.screener.schema import ScreenQuery


@pytest.mark.unit
def test_read_page_uses_user_scoped_cache_without_database(monkeypatch):
    expected = {"run_id": "run-1", "items": []}
    monkeypatch.setattr(
        screen_runs,
        "get_cached_run_page",
        lambda user_id, run_id, page_size, cursor: expected
        if (user_id, run_id, page_size, cursor) == ("user-a", "run-1", 50, None)
        else None,
    )

    class NoDatabaseAccess:
        def cursor(self):
            raise AssertionError("cached page should not query Postgres")

    assert screen_runs._read_page(NoDatabaseAccess(), "run-1", "user-a", 50, None) == expected


@pytest.mark.unit
def test_repeat_query_reuses_existing_immutable_run(monkeypatch):
    connection = object()

    @contextmanager
    def pooled_connection():
        yield connection

    expected = {"run_id": "run-1", "query_text": "ROE above 20%", "items": []}
    monkeypatch.setattr(screen_runs, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(screen_runs, "get_cached_dataset_version", lambda _conn: 7)
    monkeypatch.setattr(screen_runs, "compute_query_hash", lambda _query, _version: "query-hash")
    monkeypatch.setattr(
        screen_runs,
        "get_cached_run_id",
        lambda user_id, query_hash, text: "run-1"
        if (user_id, query_hash, text) == ("user-a", "query-hash", "ROE above 20%")
        else None,
    )
    monkeypatch.setattr(
        screen_runs,
        "_read_page",
        lambda conn, run_id, user_id, page_size, cursor: expected,
    )
    monkeypatch.setattr(screen_runs, "run_query", lambda *_args, **_kwargs: pytest.fail("query should be reused"))

    query = ScreenQuery(
        metric_predicates=[{"metric_name": "roe", "operator": ">", "value": "0.2"}],
    )
    assert screen_runs.create_run_from_query("ROE above 20%", query, "user-a") == expected


@pytest.mark.unit
@pytest.mark.parametrize("operator", [">", ">=", "<", "<="])
def test_default_sort_uses_market_cap_for_a_stable_comparison_view(operator):
    query = ScreenQuery(
        metric_predicates=[
            {"metric_name": "market_cap", "operator": ">", "value": "500"},
            {"metric_name": "roic", "operator": operator, "value": "0.2"},
        ],
    )

    sorted_query = screen_runs._apply_default_sort(query)

    assert sorted_query.sort_by == "market_cap"
    assert sorted_query.sort_desc is True


@pytest.mark.unit
def test_explicit_sort_is_never_replaced():
    query = ScreenQuery(
        metric_predicates=[{"metric_name": "roic", "operator": ">", "value": "0.2"}],
        sort_by="market_cap",
        sort_desc=False,
    )

    assert screen_runs._apply_default_sort(query) == query
