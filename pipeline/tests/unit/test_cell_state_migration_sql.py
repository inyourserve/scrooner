"""Applies migration 0102 to an isolated PostgreSQL database and exercises its
constraints and views (opt-in via SCROONER_TEST_DATABASE_URL; database name must
contain 'test'). core.company is a one-column stand-in created in the test DB."""

from datetime import date
from pathlib import Path

import psycopg
import pytest
from psycopg import errors

pytestmark = pytest.mark.integration

MIGRATION = (
    Path(__file__).resolve().parents[2] / "db" / "migrations" / "0102_cell_state.sql"
)


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        c.execute(
            "drop schema if exists analytics cascade; drop schema if exists core cascade;"
        )
        c.execute("create schema core; create schema analytics;")
        c.execute("create table core.company (id bigint primary key)")
        c.execute("insert into core.company values (1), (2)")
        c.execute(MIGRATION.read_text())
        yield c


def new_run(conn, expected=None, status="complete", active=False):
    return conn.execute(
        "insert into analytics.cell_state_run (status, is_active, cells_expected) values (%s, %s, %s) returning run_id",
        (status, active, expected),
    ).fetchone()[0]


def put(
    conn,
    run,
    company,
    dp,
    state,
    klass=None,
    owner=None,
    grain="Q",
    start=date(2026, 4, 1),
    end=date(2026, 6, 30),
):
    conn.execute(
        "insert into analytics.cell_state_latest (run_id, company_id, data_point_name, period_grain, period_start,"
        " period_end, state, defect_class, owner) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (run, company, dp, grain, start, end, state, klass, owner),
    )


def test_file_ends_with_semicolon_and_is_idempotent(conn):
    assert MIGRATION.read_text().strip().endswith(";")
    conn.execute(MIGRATION.read_text())  # second apply: no error, no change
    assert (
        conn.execute("select count(*) from analytics.cell_state_run").fetchone()[0] == 0
    )


def test_defect_needs_class_and_owner_and_others_must_not_have_them(conn):
    run = new_run(conn)
    with pytest.raises(errors.CheckViolation):
        put(conn, run, 1, "revenue", "defect")  # no class, no owner
    with pytest.raises(errors.CheckViolation):
        put(conn, run, 1, "revenue", "defect", "period")  # class but no owner
    with pytest.raises(errors.CheckViolation):
        put(
            conn, run, 1, "revenue", "value", "period", "triage"
        )  # class on a non-defect
    put(conn, run, 1, "revenue", "defect", "guard_hidden", "data_engineer_l2")
    put(conn, run, 1, "net_income", "value")


def test_frozen_vocabularies_are_enforced(conn):
    run = new_run(conn)
    for bad in (
        ("made_up", None, None),
        ("defect", "made_up", "triage"),
        ("defect", "period", "made_up"),
    ):
        with pytest.raises(errors.CheckViolation):
            put(conn, run, 1, "revenue", *bad)
    with pytest.raises(errors.CheckViolation):
        put(conn, run, 1, "revenue", "value", grain="Z")


def test_cell_key_uses_dates_and_is_unique_per_run(conn):
    run = new_run(conn)
    put(conn, run, 1, "revenue", "value")
    with pytest.raises(errors.UniqueViolation):
        put(conn, run, 1, "revenue", "derived")  # same key
    put(
        conn, run, 1, "revenue", "value", start=date(2026, 1, 1), end=date(2026, 3, 31)
    )  # other period
    run2 = new_run(conn)
    put(conn, run2, 1, "revenue", "value")  # same key in another run
    cols = {
        r[0]
        for r in conn.execute(
            "select column_name from information_schema.columns where table_name = 'cell_state_latest'"
        )
    }
    assert "period_id" not in cols and "fiscal_year" not in cols


def test_instant_and_date_order_checks(conn):
    run = new_run(conn)
    with pytest.raises(errors.CheckViolation):
        put(
            conn,
            run,
            1,
            "total_assets",
            "value",
            grain="I",
            start=date(2026, 6, 1),
            end=date(2026, 6, 30),
        )
    put(
        conn,
        run,
        1,
        "total_assets",
        "value",
        grain="I",
        start=date(2026, 6, 30),
        end=date(2026, 6, 30),
    )
    with pytest.raises(errors.CheckViolation):
        put(
            conn,
            run,
            1,
            "revenue",
            "value",
            start=date(2026, 7, 1),
            end=date(2026, 6, 30),
        )


def test_only_one_active_run_and_only_complete_runs_can_be_active(conn):
    new_run(conn, active=True)
    with pytest.raises(errors.UniqueViolation):
        new_run(conn, active=True)
    with pytest.raises(errors.CheckViolation):
        new_run(conn, status="building", active=True)


def test_active_view_follows_the_active_run_and_rollback_is_a_repoint(conn):
    a = new_run(conn, active=True)
    put(conn, a, 1, "revenue", "value")
    b = new_run(conn)
    put(conn, b, 1, "revenue", "defect", "ingestion", "data_engineer_l2")
    assert conn.execute("select state from analytics.cell_state_active").fetchall() == [
        ("value",)
    ]
    conn.execute(
        "update analytics.cell_state_run set is_active = false where run_id = %s", (a,)
    )
    conn.execute(
        "update analytics.cell_state_run set is_active = true where run_id = %s", (b,)
    )
    assert conn.execute("select state from analytics.cell_state_active").fetchall() == [
        ("defect",)
    ]
    assert conn.execute(
        "select defect_class, owner from analytics.defect_register"
    ).fetchall() == [("ingestion", "data_engineer_l2")]
    conn.execute(
        "update analytics.cell_state_run set is_active = false where run_id = %s", (b,)
    )
    conn.execute(
        "update analytics.cell_state_run set is_active = true where run_id = %s", (a,)
    )  # rollback
    assert (
        conn.execute("select count(*) from analytics.defect_register").fetchone()[0]
        == 0
    )


def test_k2_reasonless_counts_unclassified_plus_missing(conn):
    run = new_run(conn, expected=5, active=True)
    put(conn, run, 1, "revenue", "value")
    put(conn, run, 1, "net_income", "defect", "unclassified", "triage")
    put(conn, run, 2, "revenue", "defect", "period", "period_engineer")
    row = conn.execute(
        "select cells_expected, cells_written, unclassified, cells_missing, reasonless from analytics.cell_state_k2"
    ).fetchone()
    assert row == (5, 3, 1, 2, 3)
    # complete and classified -> 0
    put(conn, run, 2, "net_income", "value")
    put(conn, run, 2, "assets", "value")
    conn.execute(
        "update analytics.cell_state_latest set defect_class = 'vocabulary', owner = 'tag_mapper' where state = 'defect' and defect_class = 'unclassified'"
    )
    assert conn.execute(
        "select reasonless from analytics.cell_state_k2"
    ).fetchone() == (0,)


def test_k2_is_unknown_not_zero_when_cells_expected_is_missing_and_empty_without_active_run(
    conn,
):
    assert (
        conn.execute("select count(*) from analytics.cell_state_k2").fetchone()[0] == 0
    )
    run = new_run(conn, expected=None, active=True)
    put(conn, run, 1, "revenue", "value")
    assert conn.execute(
        "select cells_missing, reasonless from analytics.cell_state_k2"
    ).fetchone() == (None, None)


def test_migration_touches_nothing_outside_its_objects(conn):
    created = {
        r[0]
        for r in conn.execute(
            "select table_name from information_schema.tables where table_schema = 'analytics'"
        )
    }
    assert created == {
        "cell_state_run",
        "cell_state_latest",
        "cell_state_active",
        "defect_register",
        "cell_state_k2",
    }
    assert conn.execute("select count(*) from core.company").fetchone()[0] == 2


def test_defect_with_owner_but_no_class_is_rejected(conn):
    run = new_run(conn)
    with pytest.raises(errors.CheckViolation):
        put(conn, run, 1, "revenue", "defect", None, "triage")


def test_all_eight_states_are_accepted(conn):
    run = new_run(conn)
    for i, state in enumerate(
        (
            "value",
            "derived",
            "evidenced_zero",
            "undefined_by_math",
            "history_horizon",
            "not_presented",
            "not_in_template",
        )
    ):
        put(conn, run, 1, f"dp{i}", state)
    put(conn, run, 1, "dp_defect", "defect", "unclassified", "triage")
    assert (
        conn.execute("select count(*) from analytics.cell_state_latest").fetchone()[0]
        == 8
    )


def test_a_ten_kt_stub_and_a_full_year_with_the_same_end_date_are_distinct_cells(conn):
    run = new_run(conn)
    put(
        conn,
        run,
        1,
        "revenue",
        "value",
        grain="TP",
        start=date(2025, 7, 1),
        end=date(2025, 12, 31),
    )
    put(
        conn,
        run,
        1,
        "revenue",
        "value",
        grain="TP",
        start=date(2025, 1, 1),
        end=date(2025, 12, 31),
    )


def test_basis_is_latest_or_as_filed_only(conn):
    run = new_run(conn)
    conn.execute(
        "insert into analytics.cell_state_latest (run_id, company_id, data_point_name, period_grain, period_start,"
        " period_end, basis, state) values (%s, 1, 'revenue', 'Q', '2026-04-01', '2026-06-30', 'as_filed', 'value')",
        (run,),
    )
    with pytest.raises(errors.CheckViolation):
        conn.execute(
            "insert into analytics.cell_state_latest (run_id, company_id, data_point_name, period_grain, period_start,"
            " period_end, basis, state) values (%s, 1, 'revenue', 'Q', '2026-04-01', '2026-06-30', 'other', 'value')",
            (run,),
        )


def test_defect_register_lists_only_defects(conn):
    run = new_run(conn, active=True)
    put(conn, run, 1, "revenue", "value")
    put(conn, run, 1, "net_income", "not_presented")
    put(conn, run, 1, "assets", "defect", "composition", "standardization_lead")
    assert conn.execute(
        "select data_point_name from analytics.defect_register"
    ).fetchall() == [("assets",)]
