"""Deduplicated screen_result writes (2026-09-12) -- a different user
asking an already-computed query must never write a second copy of the
same matched-company rows, only a thin per-user pointer."""

from contextlib import contextmanager
from decimal import Decimal

import pytest

from routers import screen_runs
from scrooner_pipeline.screener.schema import MetricPredicate, ScreenQuery


class FakeCursor:
    def __init__(self, conflict: bool):
        self.conflict = conflict
        self.executed: list[str] = []
        self.executemany_calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, _params=()):
        normalized = " ".join(sql.split())
        self.executed.append(normalized)
        if normalized.startswith("insert into app.screen_result "):
            self._last = None if self.conflict else ("existing-or-new-screen-result-id",)
        elif normalized.startswith("select id from app.screen_result"):
            self._last = ("existing-screen-result-id",)
        elif normalized.startswith("insert into app.user_screen_run"):
            self._last = ("new-user-screen-run-id",)
        else:
            self._last = None

    def executemany(self, sql, rows):
        self.executemany_calls += 1
        self.executed.append(" ".join(sql.split()))

    def fetchone(self):
        return self._last


class FakeConnection:
    def __init__(self, conflict: bool):
        self.cursor_obj = FakeCursor(conflict)

    def cursor(self):
        return self.cursor_obj

    @contextmanager
    def transaction(self):
        yield


def _query() -> ScreenQuery:
    return ScreenQuery(metric_predicates=[MetricPredicate(metric_name="roe", operator=">", value=Decimal("0.2"))])


def _patch_common(monkeypatch, conn: FakeConnection):
    @contextmanager
    def pooled_connection():
        yield conn

    monkeypatch.setattr(screen_runs, "get_pooled_connection", pooled_connection)
    monkeypatch.setattr(screen_runs, "get_cached_dataset_version", lambda _conn: 1)
    monkeypatch.setattr(screen_runs, "compute_query_hash", lambda _query, _version: "query-hash")
    monkeypatch.setattr(screen_runs, "get_cached_run_id", lambda *_a: None)
    monkeypatch.setattr(screen_runs, "get_cached_result", lambda _hash: None)
    monkeypatch.setattr(screen_runs, "set_cached_result", lambda *_a: None)
    monkeypatch.setattr(screen_runs, "set_cached_run_id", lambda *_a: None)
    monkeypatch.setattr(screen_runs, "set_cached_run_page", lambda *_a: None)
    matches = [{"company_id": 1, "cik": "0001", "metrics": {}}]
    monkeypatch.setattr(
        screen_runs,
        "run_query",
        lambda *_a, **_k: {"matched": matches, "excluded_missing_data": [], "excluded_inactive": []},
    )


@pytest.mark.unit
def test_first_writer_creates_the_screen_result_and_its_items(monkeypatch):
    conn = FakeConnection(conflict=False)
    _patch_common(monkeypatch, conn)

    screen_runs.create_run_from_query("roe above 20%", _query(), "user-a")

    cur = conn.cursor_obj
    assert cur.executemany_calls == 1, "the first writer must insert screen_result_item rows"
    assert not any(s.startswith("select id from app.screen_result") for s in cur.executed), (
        "the first writer already has the id from the INSERT ... RETURNING, no extra SELECT needed"
    )


@pytest.mark.unit
def test_second_writer_reuses_the_existing_screen_result_without_reinserting_items(monkeypatch):
    conn = FakeConnection(conflict=True)
    _patch_common(monkeypatch, conn)

    screen_runs.create_run_from_query("roe above 20%", _query(), "user-b")

    cur = conn.cursor_obj
    assert cur.executemany_calls == 0, "a conflicting (already-computed) screen_result must never re-insert its items"
    assert any(s.startswith("select id from app.screen_result") for s in cur.executed), (
        "must look up the existing screen_result's id after the conflict"
    )
    assert any(s.startswith("insert into app.user_screen_run") for s in cur.executed), (
        "every caller, including a reuse, still gets its own per-user pointer row"
    )
