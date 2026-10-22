"""Lane 2's reason sink: pure behaviour, and the mapping into lane 1's
analytics.cell_blank_reason on REAL SQL (migration 0100 applied to scratch
schemas, opt-in via SCROONER_TEST_DATABASE_URL)."""

import re
from datetime import date
from pathlib import Path

import pytest

from scrooner_pipeline.mapper.reason_store import (
    CELL_KEY_FIELDS,
    BlankReason,
    DbReasonSink,
    InMemoryReasonSink,
    NullReasonSink,
)

TTM_DAY = date(2026, 10, 22)


def reason(**kw):
    base = dict(
        company_id=1,
        data_point_name="ebitda",
        period_grain="TTM",
        period_start=TTM_DAY,
        period_end=TTM_DAY,
        rule_id="ttm.consecutive_window@1",
        reason_code="non_contiguous_ttm_window",
    )
    return BlankReason(**{**base, **kw})


def test_key_is_the_frozen_cell_key_and_defaults_are_guard_hidden():
    r = reason()
    assert CELL_KEY_FIELDS == (
        "company_id",
        "data_point_name",
        "period_grain",
        "period_start",
        "period_end",
        "basis",
    )
    assert r.key() == (1, "ebitda", "TTM", TTM_DAY, TTM_DAY, "latest")
    assert (r.state, r.defect_class, r.owner) == (
        "defect",
        "guard_hidden",
        "data_engineer_l2",
    )


def test_null_and_memory_sinks():
    NullReasonSink().add(reason())
    mem = InMemoryReasonSink()
    mem.add(reason())
    assert len(mem.rows) == 1


def test_db_sink_refuses_a_reason_without_dates():
    with pytest.raises(ValueError):
        DbReasonSink(object(), "run").add(reason(period_start=None))


psycopg = pytest.importorskip("psycopg")
MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0100_cell_evidence_reason_registrant_audit.sql"
)
A, C = "l2rs_a", "l2rs_c"


def rw(sql: str) -> str:
    return sql.replace("analytics.", f"{A}.").replace("core.", f"{C}.")


class _Cur:
    def __init__(self, cur):
        self._c = cur

    def __enter__(self):
        self._c.__enter__()
        return self

    def __exit__(self, *a):
        return self._c.__exit__(*a)

    def execute(self, sql, params=None):
        self._c.execute(rw(sql), params)
        return self

    def executemany(self, sql, params):
        self._c.executemany(rw(sql), params)

    def fetchone(self):
        return self._c.fetchone()

    @property
    def rowcount(self):
        return self._c.rowcount


class _Conn:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return _Cur(self._conn.cursor())

    def commit(self):
        self._conn.commit()


@pytest.fixture
def pg(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        for s in (A, C):
            c.execute(f"drop schema if exists {s} cascade; create schema {s}")
        c.execute(
            f"create table {C}.company (id bigint primary key); insert into {C}.company values (1), (2)"
        )
        c.execute(rw(MIGRATION.read_text()))
        c.commit()
        yield c
        c.rollback()
        for s in (A, C):
            c.execute(f"drop schema if exists {s} cascade")
        c.commit()


def rows(pg):
    return pg.execute(
        f"select company_id, data_point_name, period_grain, period_start, period_end, basis, state, defect_class, owner,"
        f" rule_id, reason_code, input_refs from {A}.cell_blank_reason order by company_id, data_point_name"
    ).fetchall()


@pytest.mark.integration
def test_db_sink_writes_defect_guard_hidden_rows_under_a_rule_run(pg):
    from scrooner_pipeline.common import cell_store as cs

    store = _Conn(pg)
    run = cs.start_rule_run(
        store, "ttm.consecutive_window@1", "dry_run", "off", ["0000000001"]
    )
    sink = DbReasonSink(store, run)
    sink.add(reason(detail={"input": "ebitda", "detail": "gap"}))
    sink.add(reason(data_point_name="net_debt_ebitda"))
    sink.add(reason(company_id=2))
    assert sink.flush() == 3
    got = rows(pg)
    assert len(got) == 3
    c1 = [r for r in got if r[0] == 1 and r[1] == "ebitda"][0]
    assert c1[2:9] == (
        "TTM",
        TTM_DAY,
        TTM_DAY,
        "latest",
        "defect",
        "guard_hidden",
        "data_engineer_l2",
    )
    assert c1[9:11] == ("ttm.consecutive_window@1", "non_contiguous_ttm_window")
    assert c1[11] == {"input": "ebitda", "detail": "gap"}  # detail -> input_refs


@pytest.mark.integration
def test_db_sink_instant_needs_equal_dates_and_flush_is_idempotent_per_company_and_rule(
    pg,
):
    from scrooner_pipeline.common import cell_store as cs

    store = _Conn(pg)
    run = cs.start_rule_run(
        store, "ttm.consecutive_window@1", "dry_run", "off", ["0000000001"]
    )
    bad = DbReasonSink(store, run)
    bad.add(
        reason(
            period_grain="I",
            period_start=date(2026, 6, 1),
            period_end=date(2026, 6, 30),
        )
    )
    with pytest.raises(ValueError, match="instant"):
        bad.flush()
    ok = DbReasonSink(store, run)
    ok.add(
        reason(
            period_grain="I",
            period_start=date(2026, 6, 30),
            period_end=date(2026, 6, 30),
        )
    )
    ok.flush()
    again = DbReasonSink(store, run)
    again.add(
        reason(
            period_grain="I",
            period_start=date(2026, 6, 30),
            period_end=date(2026, 6, 30),
        )
    )
    again.flush()
    assert len(rows(pg)) == 1  # replaced, not duplicated


@pytest.mark.integration
def test_db_sink_never_deletes_another_rule_or_company(pg):
    from scrooner_pipeline.common import cell_store as cs

    store = _Conn(pg)
    run = cs.start_rule_run(
        store, "ttm.consecutive_window@1", "dry_run", "off", ["0000000001"]
    )
    first = DbReasonSink(store, run)
    first.add(reason(rule_id="ttm.consecutive_window@1"))
    first.add(reason(rule_id="ttm.age_guard@2", data_point_name="buyback_yield"))
    first.add(reason(company_id=2))
    first.flush()
    second = DbReasonSink(store, run)
    second.add(reason(rule_id="ttm.consecutive_window@1", data_point_name="ev_ebitda"))
    second.flush()
    got = {(r[0], r[1]) for r in rows(pg)}
    assert got == {(1, "ev_ebitda"), (1, "buyback_yield"), (2, "ebitda")}


@pytest.mark.integration
def test_flush_empties_the_buffer_and_basis_is_latest(pg):
    from scrooner_pipeline.common import cell_store as cs

    store = _Conn(pg)
    run = cs.start_rule_run(
        store, "ttm.consecutive_window@1", "dry_run", "off", ["0000000001"]
    )
    sink = DbReasonSink(store, run)
    sink.add(reason())
    assert sink.flush() == 1
    assert sink.flush() == 0  # nothing left to write twice
    assert {r[5] for r in rows(pg)} == {"latest"}


@pytest.mark.integration
def test_root_cause_class_reaches_the_store(pg):
    from scrooner_pipeline.common import cell_store as cs

    store = _Conn(pg)
    run = cs.start_rule_run(
        store, "composite.unknown_not_zero@1", "dry_run", "off", ["0000000001"]
    )
    sink = DbReasonSink(store, run)
    sink.add(
        reason(
            rule_id="composite.unknown_not_zero@1",
            data_point_name="total_shareholder_yield",
            reason_code="zero_not_proven",
            root_cause_class="evidence_pending",
        )
    )
    sink.flush()
    [(klass, root)] = pg.execute(
        f"select defect_class, root_cause_class from {A}.cell_blank_reason"
    ).fetchall()
    assert (klass, root) == ("guard_hidden", "evidence_pending")
