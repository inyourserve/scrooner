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
