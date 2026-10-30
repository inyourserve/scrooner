"""Shared-accession rule on REAL SQL (opt-in isolated database, schema `core`
created from scratch; the core.filing_registrant DDL is cut verbatim from
migration 0100 so the shipped CHECK/UNIQUE constraints are what is exercised).

Scenario = the Entergy defect: Entergy Arkansas (id 142) was normalized first and
owns the combined 10-K; Entergy Corp (id 694) is the primary and its own
companyfacts carry the facts.
"""

from datetime import date
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.company_master import status as st
from scrooner_pipeline.common import staleness
from scrooner_pipeline.normalizer import facts as facts_mod
from scrooner_pipeline.normalizer import identity as ident
from scrooner_pipeline.normalizer import shared_accession as sa

MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "migrations"
    / "0100_cell_evidence_reason_registrant_audit.sql"
)
ETR, ARK = "0000065984", "0000007323"
ACC = "0000065984-26-000012"  # combined 10-K
ACC_OWN = "0000007323-26-000003"  # Arkansas-only 10-Q


def _registrant_ddl() -> str:
    sql = MIGRATION.read_text()
    start = sql.index("create table if not exists core.filing_registrant")
    end = sql.index("-- 5. Identity audit")
    return sql[start:end]


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists core cascade")
        c.execute("create schema core")
        c.execute("create table core.company (id bigint primary key, cik text unique)")
        c.execute(
            """create table core.filing (
                 id bigserial primary key,
                 company_id bigint not null references core.company(id),
                 accession_number text not null unique, form text,
                 filing_date date, period_of_report date,
                 is_amendment boolean default false, items text,
                 raw_submission_id bigint)"""
        )
        c.execute(_registrant_ddl())
        c.execute("insert into core.company values (142, %s), (694, %s)", (ARK, ETR))
        # legacy state: Arkansas claimed both accessions first
        c.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) values "
            "(142, %s, '10-K', '2026-02-27', '2025-12-31'), (142, %s, '10-Q', '2026-04-30', '2026-03-31')",
            (ACC, ACC_OWN),
        )
        c.commit()
        yield c
        c.rollback()
        c.execute("drop schema if exists core cascade")
        c.commit()


def _row(acc):
    return {
        "company_id": 694,
        "accession_number": acc,
        "form": "10-K",
        "filing_date": date(2026, 2, 27),
        "period_of_report": date(2025, 12, 31),
        "is_amendment": False,
        "items": None,
        "raw_submission_id": 1,
    }


def _owner(conn, acc):
    return conn.execute(
        "select company_id from core.filing where accession_number=%s", (acc,)
    ).fetchone()[0]


@pytest.mark.integration
def test_legacy_first_claimant_keeps_accession_flag_off(conn, monkeypatch):
    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    conn.execute(ident._filing_upsert_sql(), _row(ACC))
    assert _owner(conn, ACC) == 142  # the defect, reproduced
    assert facts_mod._load_filing_lookup(conn, 694) == {}  # parent sees no filing


@pytest.mark.integration
def test_flag_on_link_apply_and_fact_lookup_and_status(conn, monkeypatch):
    monkeypatch.setenv(rf.ENV_ENABLED, sa.RULE_ID)
    d = sa.decide(ACC, [ARK, ETR], [ETR], "10-K", ETR)
    out = sa.apply_decisions(conn, [d], {ETR: 694, ARK: 142})
    assert out["registrant_rows"] == 2
    roles = dict(
        (cid, r)
        for cid, r in conn.execute(
            "select company_id, role from core.filing_registrant where accession_number=%s",
            (ACC,),
        ).fetchall()
    )
    assert roles == {694: "primary", 142: "co_registrant"}
    assert _owner(conn, ACC) == 694  # re-attributed to the primary
    assert _owner(conn, ACC_OWN) == 142  # single-registrant accession untouched
    # parent now resolves its combined filing for fact attribution
    assert ACC in facts_mod._load_filing_lookup(conn, 694)
    # co-registrant keeps its own filing and sees the shared one via the link
    ids = [142, 694]
    latest = st._load_latest_filing_dates(conn, ids)
    assert latest[694] == date(2026, 2, 27)
    assert latest[142] == date(2026, 4, 30)  # own 10-Q, not lost
    # exactly one primary per accession (unique index from 0100)
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(
            "insert into core.filing_registrant (accession_number, registrant_cik, role, filer_count) "
            "values (%s, %s, 'primary', 2)",
            (ACC, "0000000999"),
        )
    conn.rollback()


@pytest.mark.integration
def test_upsert_follows_primary_regardless_of_normalization_order(conn, monkeypatch):
    monkeypatch.setenv(rf.ENV_ENABLED, sa.RULE_ID)
    conn.execute(
        "insert into core.filing_registrant (accession_number, registrant_cik, company_id, role, filer_count) "
        "values (%s, %s, 694, 'primary', 2), (%s, %s, 142, 'co_registrant', 2)",
        (ACC, ETR, ACC, ARK),
    )
    conn.execute(ident._filing_upsert_sql(), {**_row(ACC), "company_id": 694})
    assert _owner(conn, ACC) == 694
    # the co-registrant re-running identity must not take it back
    conn.execute(ident._filing_upsert_sql(), {**_row(ACC), "company_id": 142})
    assert _owner(conn, ACC) == 694


@pytest.mark.integration
def test_stale_guard_union_via_registrant_when_owner_differs(conn, monkeypatch):
    monkeypatch.setenv(rf.ENV_ENABLED, sa.RULE_ID)
    # no re-own: link only (owner stays 142); parent must still be 'active'
    conn.execute(
        "insert into core.filing_registrant (accession_number, registrant_cik, company_id, role, filer_count) "
        "values (%s, %s, 694, 'primary', 2), (%s, %s, 142, 'co_registrant', 2)",
        (ACC, ETR, ACC, ARK),
    )
    assert st._load_latest_filing_dates(conn, [694])[694] == date(2026, 2, 27)
    with conn.cursor() as cur:
        got = staleness.load_latest_filed_periods(cur, [694])
    assert got[694] == date(2025, 12, 31)
