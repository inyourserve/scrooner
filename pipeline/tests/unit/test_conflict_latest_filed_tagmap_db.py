"""Latest accepted filing wins for EVERY tag of a tag-map company (Ritwik 2026-11-12, option b); other companies
keep the six-tag rule. Real SQL on a migrated scratch database (CI: Postgres 16)."""

from __future__ import annotations

import psycopg
import pytest

from scrooner_pipeline.normalizer import conflict_latest_filed as clf

# us-gaap:Assets is not one of the six (or ten) validated tags
TAG = ("us-gaap", "Assets")


@pytest.fixture(autouse=True)
def _flag_on(monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")


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


@pytest.mark.integration
def test_flag_off_a_tag_map_company_keeps_the_six_tag_behaviour(isolated_database_url, monkeypatch):
    monkeypatch.delenv("SCROONER_RULES_ENABLED", raising=False)
    with psycopg.connect(isolated_database_url) as conn:
        for taxonomy, tag in clf.VALIDATED_TAGS:
            conn.execute("insert into core.concept (taxonomy, tag) values (%s, %s) on conflict do nothing", (taxonomy, tag))
        ids = _build(conn, "0000000014", True, [("X1", "10-K", "2015-02-20", 100), ("X2", "10-K", "2016-02-20", 98)])
        clf.resolve_latest_filed(conn, {"0000000014"})
        assert _auth(conn, ids) == []  # tag-map rows exist but the flag is off: nothing flips


@pytest.mark.integration
def test_fsn_accepted_orders_ahead_of_filing_date(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        ids = _build(conn, "0000000015", True, [("X1", "10-K", "2016-02-20", 100), ("X2", "10-K", "2016-02-20", 98)])
        for accn, ts in (("X1", "2016-02-20 18:00+00"), ("X2", "2016-02-20 09:00+00")):  # X1 accepted LATER, same filing_date
            conn.execute("insert into fsn.filing (accession, cik, form, fsn_set, accepted) values (%s, '0000000015', '10-K', 't', %s)", (accn, ts))
        conn.commit()
        clf.resolve_latest_filed(conn, {"0000000015"})
        assert _auth(conn, ids) == ["X1"]  # without accepted the fact-id tiebreak would pick X2


@pytest.mark.integration
def test_same_day_original_beats_amendment_when_both_carry_statements(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        ids = _build(conn, "0000000016", True, [("X1", "10-K", "2016-02-20", 100), ("X2", "10-K/A", "2016-02-20", 98)])
        fid = conn.execute("insert into fsn.filing (accession, cik, form, fsn_set, amendment) values ('X2', '0000000016', '10-K/A', 't', true) returning id").fetchone()[0]
        tid = conn.execute("insert into fsn.tag (tag, version) values ('Assets', 't') returning id").fetchone()[0]
        conn.execute("insert into fsn.line (filing_id, report, line, stmt, tag_id) values (%s, 2, 1, 'BS', %s)", (fid, tid))
        conn.commit()
        clf.resolve_latest_filed(conn, {"0000000016"})
        assert _auth(conn, ids) == ["X1"]  # equal day, no accepted: original periodic form, then (not reached) higher fact id


def _fsn_print(conn, cik, accession, value, dcml):
    fid = conn.execute(
        "insert into fsn.filing (accession, cik, form, fsn_set) values (%s, %s, '10-K', 't') returning id", (accession, cik)
    ).fetchone()[0]
    conn.execute("insert into fsn.tag (tag, version) values ('Assets', 'us-gaap/2015') on conflict do nothing")
    tid = conn.execute("select id from fsn.tag where tag = 'Assets' order by id limit 1").fetchone()[0]
    conn.execute(
        "insert into fsn.value (filing_id, tag_id, ddate, qtrs, uom, dim_id, value, dcml) "
        "values (%s, %s, '2014-12-31', 0, 'USD', 0, %s, %s)",
        (fid, tid, value, dcml),
    )


@pytest.mark.integration
def test_rounding_class_the_more_precise_older_copy_wins_over_a_later_rounded_print(isolated_database_url):
    # PANW-style: 27,023,000 printed at -3 (2015) vs 27,000,000 at -6 (2016): one value at two precisions
    with psycopg.connect(isolated_database_url) as conn:
        ids = _build(conn, "0000000015", True, [("X1", "10-K", "2015-02-20", 27023000), ("X2", "10-K", "2016-02-20", 27000000)])
        _fsn_print(conn, "0000000015", "X1", 27023000, -3)
        _fsn_print(conn, "0000000015", "X2", 27000000, -6)
        conn.commit()
        clf.resolve_latest_filed(conn, {"0000000015"})
        assert _auth(conn, ids) == ["X1"]
        rule = conn.execute(
            "select rule from core.fact_conflict_resolution where fact_id = %s", (ids["X1"],)
        ).fetchone()[0]
        assert rule == clf.RULE_TAGMAP_PRECISION
