import psycopg
import pytest

from scrooner_pipeline.db.connection import run_tolerating_exit_commit_failure


class _FakeConnection:
    """Mimics psycopg.Connection's own context-manager protocol: __exit__
    performs an implicit commit, which can itself raise OperationalError
    on a connection that died after the `with` block's body already ran
    fn() to completion -- the exact real-world sequence this helper
    exists to tolerate."""

    def __init__(self, fail_on_exit: bool):
        self.fail_on_exit = fail_on_exit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.fail_on_exit and exc_type is None:
            raise psycopg.OperationalError("server closed the connection unexpectedly")
        return False


@pytest.mark.unit
class TestRunToleratingExitCommitFailure:
    def test_healthy_connection_returns_fns_result(self, monkeypatch):
        monkeypatch.setattr(
            "scrooner_pipeline.db.connection.psycopg.connect",
            lambda _url: _FakeConnection(fail_on_exit=False),
        )
        result = run_tolerating_exit_commit_failure("insider", lambda conn: {"ok": 3})
        assert result == {"ok": 3}

    def test_dead_connection_on_exit_does_not_raise_and_keeps_fns_result(self, monkeypatch):
        """The real 2026-09-16 bug: fn() already completed successfully and
        every company's own work already committed via its own separate
        connection -- only this outer, idle connection's implicit
        commit-on-exit fails. That must not surface as a crash, and the
        caller must still see fn()'s real result."""
        monkeypatch.setattr(
            "scrooner_pipeline.db.connection.psycopg.connect",
            lambda _url: _FakeConnection(fail_on_exit=True),
        )
        result = run_tolerating_exit_commit_failure("insider", lambda conn: {"ok": 3})  # must not raise
        assert result == {"ok": 3}

    def test_connection_dead_before_fn_runs_returns_default(self, monkeypatch):
        def _dying_connect(_url):
            raise psycopg.OperationalError("could not connect")

        monkeypatch.setattr("scrooner_pipeline.db.connection.psycopg.connect", _dying_connect)
        result = run_tolerating_exit_commit_failure("insider", lambda conn: {"ok": 3}, default={"errored": True})
        assert result == {"errored": True}

    def test_non_operational_error_from_fn_still_propagates(self, monkeypatch):
        monkeypatch.setattr(
            "scrooner_pipeline.db.connection.psycopg.connect",
            lambda _url: _FakeConnection(fail_on_exit=False),
        )

        def _fn(_conn):
            raise ValueError("a real bug, not a dead connection")

        with pytest.raises(ValueError):
            run_tolerating_exit_commit_failure("insider", _fn)


class _RetryConn:
    def __init__(self, name):
        self.name = name
        self.closed = False

    def close(self):
        self.closed = True


@pytest.mark.unit
def test_write_retries_on_a_fresh_connection_after_the_pooler_drops_it(monkeypatch):
    """2026-10-09: three nightly jobs died mid bulk-insert with 'SSL SYSCALL
    error: Connection timed out'. The write is repeat-safe, so retry it."""
    import psycopg

    from scrooner_pipeline.db import connection as dbc

    fresh = _RetryConn("fresh")
    monkeypatch.setattr(dbc.psycopg, "connect", lambda *_a, **_k: fresh)
    used = []

    def write(conn):
        used.append(conn.name)
        if len(used) == 1:
            raise psycopg.OperationalError("SSL SYSCALL error: Connection timed out")
        return "ok"

    original = _RetryConn("original")
    assert dbc.run_write_with_reconnect(original, write, stage="t") == "ok"
    assert used == ["original", "fresh"]
    assert fresh.closed is True  # a connection the helper opened is always closed
    assert original.closed is False  # the caller's is never closed by it


@pytest.mark.unit
def test_write_gives_up_after_the_attempt_limit_and_leaks_nothing(monkeypatch):
    import psycopg

    from scrooner_pipeline.db import connection as dbc

    opened = []

    def connect(*_a, **_k):
        c = _RetryConn(f"fresh{len(opened)}")
        opened.append(c)
        return c

    monkeypatch.setattr(dbc.psycopg, "connect", connect)

    def always_fails(conn):
        raise psycopg.OperationalError("connection is closed")

    original = _RetryConn("original")
    with pytest.raises(psycopg.OperationalError):
        dbc.run_write_with_reconnect(original, always_fails, stage="t", attempts=3)

    assert len(opened) == 2  # attempt 1 reuses the caller's connection
    assert all(c.closed for c in opened)
    assert original.closed is False


@pytest.mark.unit
def test_write_does_not_retry_errors_that_are_not_a_dead_connection():
    from scrooner_pipeline.db import connection as dbc

    calls = []

    def bad_row(conn):
        calls.append(1)
        raise ValueError("bad row")

    with pytest.raises(ValueError):
        dbc.run_write_with_reconnect(_RetryConn("c"), bad_row, stage="t")
    assert calls == [1]


@pytest.mark.unit
def test_all_three_failing_nightly_writes_go_through_the_reconnecting_helper():
    """Each of these computed for minutes on one connection and then wrote in a
    single transaction; a bare cursor.executemany there is the bug."""
    import inspect

    from scrooner_pipeline.sanity import plausibility_check, timeseries_check
    from scrooner_pipeline.screener import snapshot

    for module in (plausibility_check, timeseries_check, snapshot):
        assert "run_write_with_reconnect(" in inspect.getsource(module), module.__name__
