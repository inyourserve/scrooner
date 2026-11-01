"""Migration 0116 (analytics.fact_authority_retired): the file is the reviewed DDL draft, ends with a semicolon
(scripts/check_migrations.py), and on a real Postgres creates exactly the columns apply_plan / restore use, twice
without error (idempotent)."""

import os
import re
import uuid
from pathlib import Path

import pytest

from scrooner_pipeline.mapper import derived_row_retirement as rr

MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0116_fact_authority_retired.sql"
)
COLUMNS = {"id", "fact_id", "company_id", "rule_id", "reason_code", "run_id", "prior_is_authoritative",
           "retired_at", "restored_at"}  # fmt: skip


def _statements(sql: str) -> str:
    return " ".join(
        line for line in sql.splitlines() if not line.strip().startswith("--")
    ).split()


@pytest.mark.unit
def test_the_migration_is_the_reviewed_ddl_draft_and_ends_with_a_semicolon():
    text = MIGRATION.read_text()
    assert text.rstrip().endswith(";")
    assert _statements(text) == _statements(rr.FACT_AUTHORITY_RETIRED_DDL_DRAFT)


@pytest.mark.unit
def test_apply_and_restore_sql_use_only_columns_the_migration_creates():
    src = " ".join(__import__("inspect").getsource(rr).split())
    # apply_plan's before-image insert (demote and re-promote) and restore's update
    insert = (
        "(fact_id, company_id, rule_id, reason_code, run_id, prior_is_authoritative)"
    )
    assert src.count(f"fact_authority_retired {insert}") == 2
    assert "update {analytics}.fact_authority_retired r set restored_at = now()" in src
    assert set(insert.strip("()").split(", ")) | {"restored_at"} <= COLUMNS


@pytest.mark.integration
def test_on_postgres_the_migration_creates_the_table_and_is_idempotent():
    url = os.environ.get("SCROONER_TEST_DATABASE_URL")
    if not url:
        pytest.skip("SCROONER_TEST_DATABASE_URL is not configured")
    import psycopg

    schema = f"m0116_{uuid.uuid4().hex[:8]}"
    sql = MIGRATION.read_text().replace("analytics.", f"{schema}.")
    with psycopg.connect(url) as c:
        try:
            c.execute(f"create schema {schema}")
            c.execute(sql)
            c.execute(sql)  # if not exists: a second apply is a no-op
            got = {r[0] for r in c.execute(
                "select column_name from information_schema.columns where table_schema = %s and table_name = %s",
                (schema, "fact_authority_retired"))}  # fmt: skip
            assert got == COLUMNS
            c.execute(f"insert into {schema}.fact_authority_retired (fact_id, company_id, rule_id, reason_code, run_id,"
                      " prior_is_authoritative) values (1, 2, 'retire.derived_per_share_cells@1', 'C', 'r1', true)")  # fmt: skip
            assert c.execute(
                f"select restored_at is null from {schema}.fact_authority_retired"
            ).fetchone()[0]
        finally:
            c.rollback()
            c.execute(f"drop schema if exists {schema} cascade")
            c.commit()
