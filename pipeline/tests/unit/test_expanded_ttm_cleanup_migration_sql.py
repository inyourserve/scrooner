"""Migration 0107 on a scratch PostgreSQL (opt-in via SCROONER_TEST_DATABASE_URL)."""

import importlib.util
from pathlib import Path

import psycopg
import pytest

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "db" / "migrations" / "0107_expanded_ttm_rows_cleanup.sql"


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "cleanup_run", ROOT / "scripts" / "expanded_ttm_rows_cleanup_run.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        c.execute("drop schema if exists analytics cascade; create schema analytics;")
        c.execute(
            "create table analytics.metric_value (id bigserial primary key, company_id bigint, metric_definition_id bigint,"
            " period_start date, period_end date, period_label text, value numeric, data_as_of timestamptz default now(),"
            " is_null_reason text, source_fact_ids bigint[], created_at timestamptz default now())"
        )
        c.execute(MIGRATION.read_text())
        rows = []
        for cid in (1, 2, 5):
            for mid in (10, 11):  # owned metrics
                for d in ("2026-10-19", "2026-10-20", "2026-10-21"):
                    rows.append((cid, mid, d, d, "TTM", 1))
        rows += [
            (1, 99, "2026-10-19", "2026-10-19", "TTM", 7),
            (1, 99, "2026-10-20", "2026-10-20", "TTM", 7),
        ]  # not owned
        rows += [(1, 10, "2026-04-01", "2026-06-30", "Q2", 3)]  # other label
        rows += [
            (1, 10, "2025-12-31", "2026-12-31", "FY", 4)
        ]  # later non-TTM row of an owned metric
        for r in rows:
            c.execute(
                "insert into analytics.metric_value (company_id, metric_definition_id, period_start, period_end, period_label, value) values (%s,%s,%s,%s,%s,%s)",
                r,
            )
        yield c


def count(c, where="true"):
    return c.execute(
        f"select count(*) from analytics.metric_value where {where}"
    ).fetchone()[0]


def test_file_ends_with_semicolon_and_is_idempotent(conn):
    assert MIGRATION.read_text().strip().endswith(";")
    conn.execute(MIGRATION.read_text())
    assert count(conn) == 18 + 2 + 2  # applying changes no existing row


def test_function_keeps_newest_row_and_archives_the_rest_for_owned_metrics_in_range(
    conn,
):
    moved = conn.execute(
        "select analytics.archive_superseded_expanded_ttm(1, 3, array[10,11])"
    ).fetchone()[0]
    assert moved == 8  # companies 1 and 2 x 2 metrics x 2 old days
    left = conn.execute(
        "select company_id, metric_definition_id, period_end::text from analytics.metric_value where period_label='TTM' and metric_definition_id in (10,11) order by 1,2,3"
    ).fetchall()
    assert [r for r in left if r[0] in (1, 2)] == [
        (c, m, "2026-10-21") for c in (1, 2) for m in (10, 11)
    ]
    assert count(conn, "company_id = 5") == 6  # outside the range: untouched
    assert (
        count(conn, "metric_definition_id = 99") == 2
    )  # not an owned metric: untouched
    assert count(conn, "period_label in ('Q2', 'FY')") == 2  # other labels untouched
    arch = conn.execute(
        "select count(*), count(distinct id), min(archive_reason) from analytics.metric_value_ttm_archive"
    ).fetchone()
    assert arch == (8, 8, "superseded_expanded_ttm_row")


def test_second_call_moves_nothing_and_archive_can_restore(conn):
    conn.execute("select analytics.archive_superseded_expanded_ttm(1, 6, array[10,11])")
    assert (
        conn.execute(
            "select analytics.archive_superseded_expanded_ttm(1, 6, array[10,11])"
        ).fetchone()[0]
        == 0
    )
    conn.execute(
        "insert into analytics.metric_value (id, company_id, metric_definition_id, period_start, period_end, period_label, value, data_as_of, is_null_reason, source_fact_ids, created_at)"
        " select id, company_id, metric_definition_id, period_start, period_end, period_label, value, data_as_of, is_null_reason, source_fact_ids, created_at from analytics.metric_value_ttm_archive"
    )
    assert count(conn, "metric_definition_id in (10,11) and period_label='TTM'") == 18


def test_runner_guards():
    r = load_runner()
    assert r.plan_chunks(1, 250, 100) == [(1, 101), (101, 201), (201, 251)]
    with pytest.raises(SystemExit):
        r.check_expected(None, 5)
    with pytest.raises(SystemExit):
        r.check_expected(4, 5)
    r.check_expected(5, 5)
