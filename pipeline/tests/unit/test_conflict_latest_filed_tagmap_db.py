"""Latest accepted filing wins for EVERY tag of a tag-map company (Ritwik 2026-11-12, option b); other companies
keep the six-tag rule. Real SQL on a migrated scratch database (CI: Postgres 16)."""

from __future__ import annotations

import psycopg
import pytest

from scrooner_pipeline.normalizer import conflict_latest_filed as clf

# us-gaap:Assets is not one of the six (or ten) validated tags
TAG = ("us-gaap", "Assets")


def _build(conn, cik, tag_map, copies):
    """copies: [(accession, form, filing_date, value)] -> one period, all copies NON-authoritative
    (the state Stage 2e leaves a disagreeing group in). Returns {accession: fact_id}."""
    cid = conn.execute("insert into core.company (cik, company_name) values (%s, 'T') returning id", (cik,)).fetchone()[0]
    if tag_map:
        conn.execute(
            """insert into analytics.company_tag_map
               (company_id, cik, taxonomy, tag, stmt, decision, reason_class, era_from, decided_by, rule_id)
               values (%s, %s, 'us-gaap', 'Assets', 'BS', 'excluded', 'test', '2010-01-01', 'test', 'a.b@1')""", (cid, cik))
    conn.execute("insert into core.unit (unit_name) values ('usd') on conflict do nothing")
    uid = conn.execute("select id from core.unit where unit_name='usd'").fetchone()[0]
    conn.execute("insert into core.concept (taxonomy, tag) values (%s, %s) on conflict do nothing", TAG)
    kid = conn.execute("select id from core.concept where taxonomy=%s and tag=%s", TAG).fetchone()[0]
    pid = conn.execute("insert into core.period (company_id, start_date, end_date, period_type) values (%s,'2014-12-31','2014-12-31','instant') returning id", (cid,)).fetchone()[0]
    rid = conn.execute("insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values (%s,'u','h',%s,200) returning id", (cik, f"raw/{cik}")).fetchone()[0]
    out = {}
    for accn, form, fdate, value in copies:
        fid = conn.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
            "values (%s,%s,%s,%s,'2014-12-31',%s) returning id", (cid, accn, form, fdate, form.endswith("/A"))).fetchone()[0]
        out[accn] = conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) "
            "values (%s,%s,%s,%s,%s,%s,false,%s) returning id", (cid, kid, uid, pid, fid, value, rid)).fetchone()[0]
    conn.commit()
    return out


def _auth(conn, ids):
    got = conn.execute("select id from core.fact where id = any(%s) and is_authoritative", (list(ids.values()),)).fetchall()
    inv = {v: k for k, v in ids.items()}
    return sorted(inv[r[0]] for r in got)


@pytest.mark.integration
def test_tag_map_company_latest_restated_copy_wins_for_any_tag(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        ids = _build(conn, "0000000011", True, [("X1", "10-K", "2015-02-20", 100), ("X2", "10-K", "2016-02-20", 98)])
        clf.resolve_latest_filed(conn, {"0000000011"})
        assert _auth(conn, ids) == ["X2"]  # predecessor 100 vs later restated 98 -> 98; the older stays non-authoritative


@pytest.mark.integration
def test_later_no_statement_amendment_never_wins(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        ids = _build(conn, "0000000012", True, [("X1", "10-K", "2015-02-20", 100), ("X3", "10-K/A", "2017-01-01", 95)])
        clf.resolve_latest_filed(conn, {"0000000012"})
        assert _auth(conn, ids) == ["X1"]  # the amendment (no IS/BS/CF/CI lines) is a copy but never the winner


@pytest.mark.integration
def test_non_tag_map_company_keeps_the_six_tag_rule(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        for taxonomy, tag in clf.VALIDATED_TAGS:  # so the six-tag path really runs (it exits early with no concepts)
            conn.execute("insert into core.concept (taxonomy, tag) values (%s, %s) on conflict do nothing", (taxonomy, tag))
        ids = _build(conn, "0000000013", False, [("X1", "10-K", "2015-02-20", 100), ("X2", "10-K", "2016-02-20", 98)])
        clf.resolve_latest_filed(conn, {"0000000013"})
        assert _auth(conn, ids) == []  # Assets is outside the six validated tags: unchanged, still unresolved
