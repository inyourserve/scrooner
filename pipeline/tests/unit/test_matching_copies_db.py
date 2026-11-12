"""dedupe.matching_copies@1 on a migrated scratch database: copies equal within the coarser copy's rounding
are not a conflict and the most precise copy is authoritative; a real difference stays unresolved.
core.fact stores no `decimals`, so precision is inferred from trailing zeros (normalizer/matching_copies.py)."""

from __future__ import annotations

import psycopg
import pytest

from scrooner_pipeline.normalizer import dedupe


def _build(conn, cik, copies):
    cid = conn.execute("insert into core.company (cik, company_name) values (%s, 'T') returning id", (cik,)).fetchone()[0]
    conn.execute("insert into core.unit (unit_name) values ('usd') on conflict do nothing")
    uid = conn.execute("select id from core.unit where unit_name='usd'").fetchone()[0]
    conn.execute("insert into core.concept (taxonomy, tag) values ('us-gaap', 'Assets') on conflict do nothing")
    kid = conn.execute("select id from core.concept where taxonomy='us-gaap' and tag='Assets'").fetchone()[0]
    pid = conn.execute("insert into core.period (company_id, start_date, end_date, period_type) values (%s,'2024-12-31','2024-12-31','instant') returning id", (cid,)).fetchone()[0]
    rid = conn.execute("insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values (%s,'u','h',%s,200) returning id", (cik, f"raw/{cik}")).fetchone()[0]
    ids = {}
    for accn, form, fdate, value in copies:
        fid = conn.execute("insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) values (%s,%s,%s,%s,'2024-12-31',false) returning id", (cid, f"{cik}-{accn}", form, fdate)).fetchone()[0]
        ids[accn] = conn.execute("insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,false,%s) returning id", (cid, kid, uid, pid, fid, value, rid)).fetchone()[0]
    conn.commit()
    return cid, ids


def _auth(conn, ids):
    inv = {v: k for k, v in ids.items()}
    return sorted(inv[r[0]] for r in conn.execute("select id from core.fact where id = any(%s) and is_authoritative", (list(ids.values()),)))


# ANET Assets 2024-12-31: the original 10-K at decimals -3, four later filings at decimals -5
ANET = [("A1", "10-K", "2025-02-20", 14043921000), ("A2", "10-Q", "2025-05-01", 14043900000),
        ("A3", "10-Q", "2025-08-01", 14043900000), ("A4", "10-Q", "2025-11-01", 14043900000),
        ("A5", "10-K", "2026-02-20", 14043900000)]


@pytest.mark.integration
def test_rounding_only_copies_the_precise_one_is_authoritative(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        cid, ids = _build(conn, "0000000021", ANET)
        dedupe.resolve_authoritative_for_company(conn, cid, matching_copies=True)
        assert _auth(conn, ids) == ["A1"]
        # flag off: today's behaviour, all five unresolved
        cid2, ids2 = _build(conn, "0000000022", ANET)
        dedupe.resolve_authoritative_for_company(conn, cid2, matching_copies=False)
        assert _auth(conn, ids2) == []


@pytest.mark.integration
def test_a_real_difference_beyond_rounding_stays_unresolved(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        cid, ids = _build(conn, "0000000023", [("B1", "10-K", "2025-02-20", 14043921000), ("B2", "10-K", "2026-02-20", 14100000000)])
        dedupe.resolve_authoritative_for_company(conn, cid, matching_copies=True)
        assert _auth(conn, ids) == []
