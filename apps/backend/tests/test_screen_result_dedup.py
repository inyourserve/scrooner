"""Single-round-trip screen_result writes (2026-09-20, replacing 2026-09-12's
cross-user dedup by explicit founder direction: "i chose postgres for the
speed, i dont want unique key or whatever thing"). Measured live before
rewriting: each round trip to this remote Supabase instance costs
0.3-1.7s on its own -- network RTT dominates, not query complexity -- so
the fix is one statement instead of three, not a dedup key. Every call now
gets its own fresh screen_result row; the only shared/reused thing is the
Redis cache that skips recomputing an already-known query's own `matched`
result (unrelated to this write path).

Since migration 0074 (2026-09-26) the write uploads only matched company
IDs and compact exclusions -- no per-company JSONB copy -- and pages are
rebuilt from the run's own snapshot version."""

from contextlib import contextmanager
from decimal import Decimal

import pytest

from routers import screen_runs
from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery


class FakeCursor:
    def __init__(self):
        self.executed: list[tuple[str, dict]] = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.executed.append((" ".join(sql.split()), params))

    def fetchone(self):
        return ("new-run-id",)


class FakeConnection:
    def __init__(self):
        self.cursor_obj = FakeCursor()

    def cursor(self):
        return self.cursor_obj

    @contextmanager
    def transaction(self):
        yield


def _query() -> ScreenQuery:
    return ScreenQuery(metric_predicates=[MetricPredicate(metric_name="roe", operator=">", value=Decimal("0.2"))])


def _patch_common(monkeypatch, conn: FakeConnection, matches=None):
    @contextmanager
    def pooled_connection():
        yield conn

    monkeypatch.setattr(screen_runs, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(screen_runs, "get_cached_dataset_version", lambda _conn: 1)
    monkeypatch.setattr(screen_runs, "get_cached_metric_catalog", lambda _conn: {"roe": 1})
    monkeypatch.setattr(screen_runs, "compute_query_hash", lambda _query, _version: "query-hash")
    monkeypatch.setattr(screen_runs, "get_cached_run_id", lambda *_a: None)
    monkeypatch.setattr(screen_runs, "get_cached_result", lambda _hash: None)
    monkeypatch.setattr(screen_runs, "set_cached_result", lambda *_a: None)
    monkeypatch.setattr(screen_runs, "set_cached_run_id", lambda *_a: None)
    monkeypatch.setattr(screen_runs, "set_cached_run_page", lambda *_a: None)
    monkeypatch.setattr(
        screen_runs,
        "run_query",
        lambda *_a, **_k: {
            "matched": matches if matches is not None else [{"company_id": 1, "cik": "0001", "metrics": {}}],
            "excluded_missing_data": [{"cik": "0009", "company_name": "Nine", "missing_metrics": ["roe", "roic"]}],
            "excluded_inactive": [],
            "dataset_version": 1,
        },
    )


@pytest.mark.unit
def test_the_entire_write_is_a_single_statement(monkeypatch):
    conn = FakeConnection()
    _patch_common(monkeypatch, conn)

    screen_runs.create_run_from_query("roe above 20%", _query(), "user-a")

    cur = conn.cursor_obj
    assert len(cur.executed) == 1, "screen_result and user_screen_run must land in one round trip"
    sql, params = cur.executed[0]
    assert "insert into app.screen_result" in sql
    assert "insert into app.user_screen_run" in sql
    assert "screen_result_item" not in sql, "per-company value copies are no longer stored (migration 0074)"
    assert "on conflict" not in sql, "no dedup key -- every call gets its own fresh screen_result row"


@pytest.mark.unit
def test_two_callers_with_the_identical_query_each_still_get_their_own_write(monkeypatch):
    # No cross-user dedup any more: two independent calls each do their own
    # single-round-trip write, since there is no shared row to reuse.
    conn_a, conn_b = FakeConnection(), FakeConnection()
    _patch_common(monkeypatch, conn_a)
    screen_runs.create_run_from_query("roe above 20%", _query(), "user-a")
    assert len(conn_a.cursor_obj.executed) == 1

    _patch_common(monkeypatch, conn_b)
    screen_runs.create_run_from_query("roe above 20%", _query(), "user-b")
    assert len(conn_b.cursor_obj.executed) == 1


@pytest.mark.unit
def test_only_ids_and_compact_exclusions_are_uploaded(monkeypatch):
    conn = FakeConnection()
    matches = [{"company_id": 7, "cik": "0007", "metrics": {"roe": {"value": Decimal("0.5")}}}, {"company_id": 3, "cik": "0003"}]
    _patch_common(monkeypatch, conn, matches=matches)

    screen_runs.create_run_from_query("roe above 20%", _query(), "user-a")

    _sql, params = conn.cursor_obj.executed[0]
    assert params["company_ids"] == [7, 3], "IDs in result order"
    assert params["missing_ciks"] == ["0009"]
    assert params["missing_metrics"] == ["roe,roic"]
    assert params["dataset_version"] == 1, "the version the result was computed on, so pages read it back"
    assert not any(isinstance(value, str) and '"metrics"' in value for value in params.values()), (
        "no per-company metric payload may be uploaded"
    )
