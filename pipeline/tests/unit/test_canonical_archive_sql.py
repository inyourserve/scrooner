"""mapper/canonical_archive.py on real SQL in an isolated database. The archive
table DDL is read from migration 0098 itself (schema rewritten to rtest,
foreign keys stripped), so the tests also pin the migration's columns."""

import re
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.mapper import canonical_archive as ca
from scrooner_pipeline.mapper.canonical_archive import CanonicalRow

pytestmark = pytest.mark.integration

MIGRATION = Path(__file__).parents[2] / (
    "db/migrations/0098_per_share_gap_cause_and_canonical_fact_retired.sql"
)


def _archive_ddl() -> str:
    sql = MIGRATION.read_text()
    ddl = sql[
        sql.index("create table if not exists analytics.canonical_fact_retired") :
    ]
    ddl = ddl[: ddl.index(");") + 2]
    ddl = re.sub(r"references \w+\.\w+ \(id\)", "", ddl)
    return ddl.replace("analytics.", "rtest.")


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists rtest cascade")
        c.execute("create schema rtest")
        c.execute(
            """
            create table rtest.canonical_fact (
                id bigint generated always as identity primary key,
                company_id bigint not null, canonical_concept_id bigint not null,
                period_id bigint not null, value numeric not null,
                source_fact_ids bigint[] not null,
                resolved_at timestamptz not null default now(),
                unique (company_id, canonical_concept_id, period_id))
            """
        )
        c.execute(_archive_ddl())
        yield c
        c.rollback()
        c.execute("drop schema if exists rtest cascade")
        c.commit()


def _put(c, company, concept, period, value, sources):
    return c.execute(
        "insert into rtest.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)"
        " values (%s, %s, %s, %s, %s) returning id",
        (company, concept, period, Decimal(value), sources),
    ).fetchone()[0]


def _state(c):
    return sorted(
        c.execute(
            "select company_id, canonical_concept_id, period_id, value, source_fact_ids from rtest.canonical_fact"
        ).fetchall()
    )


def test_ru1_retirement_archives_then_removes_and_restores(conn):
    # MSFT Q4 FY26 diluted_eps_resolved from the derived 4.80 (core.fact 341935).
    keep = _put(conn, 4, 17, 404, "17.95", [341900])
    bad = _put(conn, 4, 17, 405, "4.80", [341935])
    before = _state(conn)
    with conn.cursor() as cur:
        n = ca.archive_and_remove(
            cur,
            [bad, 999999],
            reason_code="ru1_derived_per_share",
            run_id="ru1-test",
            schema="rtest",
        )
    assert n == 1
    assert [r[2] for r in _state(conn)] == [404]
    arch = conn.execute(
        "select action, canonical_fact_id, value, reason_code from rtest.canonical_fact_retired"
    ).fetchall()
    assert arch == [("removed", bad, Decimal("4.80"), "ru1_derived_per_share")]
    with conn.cursor() as cur:
        assert ca.restore_run(cur, "ru1-test", schema="rtest") == 1
    assert _state(conn) == before
    with conn.cursor() as cur:
        assert (
            ca.restore_run(cur, "ru1-test", schema="rtest") == 0
        )  # second restore is a no-op
    assert _state(conn) == before
    assert keep  # untouched row kept its id


def test_split_rebase_replace_is_idempotent_and_fully_reversible(conn):
    # AAPL FY2018 diluted EPS stored unadjusted 11.91; current basis 2.98 (4:1 in 2020).
    _put(conn, 3, 17, 2018, "11.91", [1001])
    _put(conn, 3, 17, 2019, "2.97", [1002])  # already on the current basis
    before = _state(conn)
    rows = [
        CanonicalRow(3, 17, 2018, Decimal("2.9775"), (1001,)),
        CanonicalRow(3, 17, 2019, Decimal("2.97"), (1002,)),
        CanonicalRow(3, 17, 2017, Decimal("2.30"), (1000,)),  # key not filled before
    ]
    with conn.cursor() as cur:
        first = ca.replace_rows(
            cur,
            rows,
            reason_code="split_rebase",
            run_id="sb-1",
            basis_version="b1",
            schema="rtest",
        )
    assert first == {"unchanged": 1, "replaced": 1, "inserted": 1}
    with conn.cursor() as cur:
        second = ca.replace_rows(
            cur,
            rows,
            reason_code="split_rebase",
            run_id="sb-2",
            basis_version="b1",
            schema="rtest",
        )
    assert second == {"unchanged": 3, "replaced": 0, "inserted": 0}  # idempotent
    actions = sorted(
        r[0]
        for r in conn.execute(
            "select action from rtest.canonical_fact_retired where run_id = 'sb-1'"
        )
    )
    assert actions == ["inserted", "replaced"]
    with conn.cursor() as cur:
        ca.restore_run(cur, "sb-1", schema="rtest")
    assert _state(conn) == before  # the insert is gone, 11.91 is back


def test_duplicate_keys_are_refused(conn):
    rows = [
        CanonicalRow(1, 1, 1, Decimal("1"), (1,)),
        CanonicalRow(1, 1, 1, Decimal("2"), (2,)),
    ]
    with conn.cursor() as cur, pytest.raises(ValueError):
        ca.replace_rows(cur, rows, reason_code="x", run_id="r", schema="rtest")


def test_archive_check_rejects_a_before_image_without_values(conn):
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute(
            "insert into rtest.canonical_fact_retired (action, canonical_fact_id, company_id, canonical_concept_id,"
            " period_id, reason_code, run_id) values ('replaced', 1, 1, 1, 1, 'x', 'r')"
        )
