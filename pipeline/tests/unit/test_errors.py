import pytest

from scrooner_pipeline.common.errors import log_error


class _Cursor:
    def __init__(self, fail_execute):
        self._fail_execute = fail_execute

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, *_args, **_kwargs):
        if self._fail_execute:
            raise RuntimeError("connection is lost")


class _Connection:
    def __init__(self, fail_rollback=False, fail_execute=False, fail_commit=False):
        self.fail_rollback = fail_rollback
        self.fail_execute = fail_execute
        self.fail_commit = fail_commit
        self.rolled_back = False
        self.committed = False

    def rollback(self):
        if self.fail_rollback:
            raise RuntimeError("connection is lost")
        self.rolled_back = True

    def cursor(self):
        return _Cursor(self.fail_execute)

    def commit(self):
        if self.fail_commit:
            raise RuntimeError("connection is lost")
        self.committed = True


@pytest.mark.unit
class TestLogError:
    def test_happy_path_rolls_back_logs_and_commits(self):
        conn = _Connection()
        log_error(conn, "analytics.mapper_error", "0000000001", "calculate", ValueError("boom"))
        assert conn.rolled_back is True
        assert conn.committed is True

    def test_dead_connection_rollback_failure_does_not_raise(self):
        """The real 2026-09-02 bug: a connection that died BEFORE log_error
        was called must not crash the caller's loop when rollback() itself
        also fails -- this is the exact traceback cascade found live during
        a full-population rerun (calculate.py's per-company loop aborting
        the whole remaining batch)."""
        conn = _Connection(fail_rollback=True)
        log_error(conn, "analytics.mapper_error", "0000000001", "calculate", ValueError("boom"))  # must not raise

    def test_dead_connection_insert_failure_does_not_raise(self):
        conn = _Connection(fail_execute=True)
        log_error(conn, "analytics.mapper_error", "0000000001", "calculate", ValueError("boom"))  # must not raise

    def test_dead_connection_commit_failure_does_not_raise(self):
        conn = _Connection(fail_commit=True)
        log_error(conn, "analytics.mapper_error", "0000000001", "calculate", ValueError("boom"))  # must not raise

    def test_unknown_table_still_asserts(self):
        conn = _Connection()
        with pytest.raises(AssertionError):
            log_error(conn, "not.a.real.table", "0000000001", "calculate", ValueError("boom"))
