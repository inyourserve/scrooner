"""The nightly reprocess cohort: recent 10-K/10-Q filers capped newest-first, backlog unchanged
(scrooner_pipeline/common/reprocess_cohort.py; runs 42280766413, 42398026264, 42507618224 crossed the 7,000 s budget
with 1,366-1,635 companies and skipped every map stage)."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.common import reprocess_cohort as rc

ROOT = Path(__file__).resolve().parents[3]
TODAY = date.today()


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    yield c
    c.rollback()
    c.close()


def _company(conn, cik, status="active"):
    return conn.execute(
        "insert into core.company (cik, company_name, status) values (%s, %s, %s) returning id",
        (cik, f"TEST {cik}", status),
    ).fetchone()[0]


def _raw_filing(conn, cik, days_ago, form="10-Q", n=1):
    conn.execute(
        "insert into raw.sec_filing_documents (cik, accession_number, form, filing_date, source_url) "
        "values (%s, %s, %s, %s, 'test')",
        (cik, f"{cik}-{days_ago}-{form}-{n}", form, TODAY - timedelta(days=days_ago)),
    )


@pytest.mark.integration
def test_recent_filers_are_capped_newest_first(conn):
    for i in range(6):
        cik = f"00000900{i:02d}"
        _company(conn, cik)
        _raw_filing(conn, cik, days_ago=i)  # 0000090000 filed today ... 0000090005 five days ago
    ciks, n = rc.reprocess_cohort(conn, lookback_days=4, filer_limit=3, backlog_limit=150)
    assert ciks == ["0000090000", "0000090001", "0000090002"]  # the newest three; day 4 is deferred, day 5 is out
    assert (n["recent_filers"], n["recent_selected"], n["recent_deferred"]) == (5, 3, 2)


@pytest.mark.integration
def test_zero_limit_restores_the_uncapped_selection(conn):
    for i in range(5):
        cik = f"00000910{i:02d}"
        _company(conn, cik)
        _raw_filing(conn, cik, days_ago=i)
    ciks, n = rc.reprocess_cohort(conn, lookback_days=4, filer_limit=0, backlog_limit=150)
    assert len(ciks) == 5 and n["recent_deferred"] == 0


@pytest.mark.integration
def test_only_active_companies_and_periodic_forms_count(conn):
    _company(conn, "0000092001")
    _raw_filing(conn, "0000092001", 1, form="8-K")
    _company(conn, "0000092002", status="delisted")
    _raw_filing(conn, "0000092002", 1)
    _company(conn, "0000092003")
    _raw_filing(conn, "0000092003", 1, form="10-K/A")
    _raw_filing(conn, "0000092003", 2, form="10-Q", n=2)  # one company, two filings: selected once
    ciks, n = rc.reprocess_cohort(conn, lookback_days=4, filer_limit=450, backlog_limit=150)
    assert ciks == ["0000092003"] and n["recent_filers"] == 1


@pytest.mark.integration
def test_the_backlog_is_added_on_top_of_the_cap(conn):
    """A company whose latest 10-Q has no core.fact rows although companyfacts was fetched after it is reprocessed
    even when the recent-filer cap is full: a deferred filing is never lost."""
    for i in range(3):
        cik = f"00000930{i:02d}"
        _company(conn, cik)
        _raw_filing(conn, cik, days_ago=i)
    cid = _company(conn, "0000093099")
    conn.execute(
        "insert into core.filing (company_id, accession_number, form, filing_date) values (%s, 'bl-1', '10-Q', %s)",
        (cid, TODAY - timedelta(days=20)),
    )
    conn.execute(
        "insert into raw.sec_companyfacts (cik, fetched_at, source_url, sha256, storage_path, http_status) "
        "values ('0000093099', now(), 'test', 'x', 'x', 200)"
    )
    ciks, n = rc.reprocess_cohort(conn, lookback_days=4, filer_limit=2, backlog_limit=150)
    assert ciks == ["0000093000", "0000093001", "0000093099"]
    assert (n["recent_selected"], n["backlog"], n["total"]) == (2, 1, 3)


@pytest.mark.unit
def test_the_nightly_script_selects_through_the_capped_function():
    script = (ROOT / "pipeline" / "scripts" / "reprocess_recent_filers.sh").read_text()
    assert "from scrooner_pipeline.common.reprocess_cohort import" in script
    assert 'os.environ.get("FILER_LIMIT", FILER_LIMIT)' in script
    # the old uncapped inline query (its 10-K/10-Q form filter) is gone from the script
    assert "and d.form in ('10-K', '10-K/A', '10-Q', '10-Q/A')" not in script
    assert rc.FILER_LIMIT + rc.BACKLOG_LIMIT <= 650  # the measured per-night capacity at 4 shards
