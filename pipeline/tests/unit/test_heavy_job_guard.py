import pytest

from scrooner_pipeline.db.heavy_job_guard import (
    HeavyJobGateRefused,
    evaluate_gate,
    require_heavy_job_gate,
)


@pytest.mark.unit
class TestEvaluateGate:
    def test_quiet_database_is_allowed(self):
        assert evaluate_gate(4, []).allowed

    def test_too_many_connections_refuses(self):
        r = evaluate_gate(17, [])
        assert not r.allowed and "17 connections" in r.reasons[0]

    def test_connections_at_the_limit_are_allowed(self):
        assert evaluate_gate(10, []).allowed

    def test_long_running_other_query_refuses(self):
        r = evaluate_gate(3, [(99, 42.0, "insert into analytics.canonical_fact ...")])
        assert not r.allowed and "pid 99" in r.reasons[0]

    def test_short_queries_are_ignored(self):
        assert evaluate_gate(3, [(99, 0.5, "select 1")]).allowed


class _Cur:
    def __init__(self, conns, running):
        self.conns, self.running, self.last = conns, running, None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=()):
        self.last = sql

    def fetchone(self):
        return (self.conns,)

    def fetchall(self):
        return self.running


class _Conn:
    def __init__(self, conns, running):
        self.args = (conns, running)

    def cursor(self):
        return _Cur(*self.args)


@pytest.mark.unit
class TestRequire:
    def test_raises_when_busy(self):
        with pytest.raises(HeavyJobGateRefused):
            require_heavy_job_gate(_Conn(17, []), job="recompute")

    def test_force_proceeds_but_reports_not_allowed(self):
        r = require_heavy_job_gate(_Conn(17, []), job="recompute", force=True)
        assert not r.allowed

    def test_open_when_quiet(self):
        assert require_heavy_job_gate(_Conn(3, []), job="recompute").allowed
