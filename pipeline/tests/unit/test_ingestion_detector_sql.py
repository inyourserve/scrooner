"""Runs the detector's real SQL on synthetic rows in an isolated PostgreSQL
database (opt-in via SCROONER_TEST_DATABASE_URL; the database name must contain
'test'). Tables are minimal copies of the columns the detector reads; schemas
core/raw are created inside the test database only."""

from datetime import date, datetime, timezone

import psycopg
import pytest

from scrooner_pipeline.sanity import ingestion_detector as d

pytestmark = pytest.mark.integration

SCHEMA = """
drop schema if exists core cascade; drop schema if exists raw cascade;
create schema core; create schema raw;
create table core.company (id bigint primary key, cik text, primary_ticker text, status text);
create table core.filing (id bigint primary key, company_id bigint, accession_number text unique,
    form text, filing_date date, period_of_report date, created_at timestamptz default now());
create table core.fact (id bigserial primary key, filing_id bigint);
create index on core.fact (filing_id);
create table raw.sec_companyfacts (id bigserial primary key, cik text, fetched_at timestamptz,
    storage_path text, http_status int);
create table raw.sec_filing_documents (cik text, accession_number text, form text,
    filing_date date, report_date date, primary key (cik, accession_number));
"""

KO_FETCHED = datetime(2026, 9, 29, 12, tzinfo=timezone.utc)


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        c.execute(SCHEMA)
        c.execute(
            "insert into core.company values (1,'0000021344','KO','active'),(2,'0000029534','DG','active'),"
            "(3,'0000000003','OLD','inactive'),(4,'0000000004','OK','active')"
        )
        c.execute(
            "insert into core.filing (id, company_id, accession_number, form, filing_date, period_of_report) values "
            "(10,1,'KO-10Q-NEW','10-Q','2026-07-29','2026-07-03'),"  # zero facts: KO
            "(11,1,'KO-10Q-OLD','10-Q','2026-04-30','2026-04-03'),"  # has facts
            "(12,1,'KO-8K','8-K','2026-08-01',null),"  # not periodic
            "(13,3,'OLD-10Q','10-Q','2026-07-29',null),"  # inactive company
            "(14,4,'OK-10Q','10-Q','2026-07-29',null),"  # has facts
            "(15,4,'OK-10Q-BEFORE','10-Q','2026-05-01',null)"  # before 'since', zero facts
        )
        c.execute("insert into core.fact (filing_id) values (11),(11),(14)")
        c.execute(
            "insert into raw.sec_companyfacts (cik, fetched_at, storage_path, http_status) values "
            "('0000021344','2026-08-01T00:00:00Z','raw/old.json',200),('0000021344',%s,'raw/new.json',200),"
            "('0000021344','2026-10-01T00:00:00Z',null,404)",
            (KO_FETCHED,),
        )
        c.execute(
            "insert into raw.sec_filing_documents values "
            "('0000029534','DG-10Q-NEW','10-Q','2026-08-27','2026-08-01'),"  # not in core.filing: DG
            "('0000029534','DG-8K','8-K','2026-08-27',null),"  # not periodic
            "('0000021344','KO-10Q-NEW','10-Q','2026-07-29','2026-07-03'),"  # already indexed
            "('0000000003','OLD-X','10-Q','2026-08-27',null)"  # inactive
        )
        yield c


def test_zero_fact_filings_real_sql(conn):
    zero = d.detect_zero_fact_filings(conn, date(2026, 7, 1), today=date(2026, 10, 22))
    assert [(z.ticker, z.accession, z.cause) for z in zero] == [
        ("KO", "KO-10Q-NEW", d.CAUSE_CHECK)
    ]
    assert (
        zero[0].companyfacts_fetched_at == KO_FETCHED
    )  # newest object with a storage path
    assert zero[0].companyfacts_storage_path == "raw/new.json"
    assert (
        conn.execute("show statement_timeout").fetchone()[0] != "20s"
    )  # caller's value restored


def test_unindexed_filings_real_sql(conn):
    got = d.detect_unindexed_filings(conn, date(2026, 7, 1))
    assert [(u.ticker, u.accession, u.form) for u in got] == [
        ("DG", "DG-10Q-NEW", "10-Q")
    ]
    assert (
        got[0].latest_core_periodic_date is None
    )  # DG has no core.filing rows in this fixture


def test_since_window_is_respected(conn):
    assert (
        d.detect_zero_fact_filings(conn, date(2026, 8, 1), today=date(2026, 10, 22))
        == []
    )
    wide = d.detect_zero_fact_filings(conn, date(2026, 1, 1), today=date(2026, 10, 22))
    assert {z.accession for z in wide} == {"KO-10Q-NEW", "OK-10Q-BEFORE"}
