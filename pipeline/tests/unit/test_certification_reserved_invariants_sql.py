"""Real SQL: migration 0097 stores I12/I13 findings and refuses X1 (AT-1.9c).
Opt-in via SCROONER_TEST_DATABASE_URL (database name must contain 'test')."""

from pathlib import Path

import psycopg
import pytest
from psycopg import errors

pytestmark = pytest.mark.integration

MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0097_certification_tables.sql"
)


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        c.execute(
            "drop schema if exists analytics cascade; drop schema if exists core cascade;"
        )
        c.execute("create schema core; create schema analytics;")
        c.execute(
            "create table core.company (id bigint primary key); insert into core.company values (1)"
        )
        c.execute(MIGRATION.read_text())
        yield c


def insert(conn, invariant):
    conn.execute(
        "insert into analytics.certification_finding (company_id, invariant, severity, data_point_name)"
        " values (1, %s, 'review', 'revenue')",
        (invariant,),
    )


def test_reserved_ids_can_be_stored_and_non_ids_cannot(conn):
    for ok in ("I1", "I11", "I12", "I13"):
        insert(conn, ok)
    for bad in ("X1", "i12", "I", "12"):
        with pytest.raises(errors.CheckViolation):
            insert(conn, bad)
