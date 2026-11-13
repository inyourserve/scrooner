"""tagmap-authority v2 on a migrated scratch database: the latest ELIGIBLE (face-column) copy is authoritative; a far-later
note copy (HD Goodwill 2015-02-01) is history. Real SQL (CI: Postgres 16)."""

from __future__ import annotations

import psycopg
import pytest

from scrooner_pipeline.normalizer import conflict_latest_filed as clf

TAG = ("us-gaap", "Goodwill")


@pytest.fixture(autouse=True)
def _flag_on(monkeypatch):
    monkeypatch.setenv("SCROONER_RULES_ENABLED", "company_tag_map.select@1")


def _build(conn, cik, copies, *, ptype="instant", start="2015-02-01", end="2015-02-01", auth=()):
    """copies: [(accession, form, filing_date, period_of_report, value)] -> one period. Accessions in `auth`
    start authoritative, all others non-authoritative. Returns (company_id, {accession: fact_id})."""
    cid = conn.execute("insert into core.company (cik, company_name) values (%s, 'T') returning id", (cik,)).fetchone()[0]
    conn.execute("insert into core.unit (unit_name) values ('usd') on conflict do nothing")
    uid = conn.execute("select id from core.unit where unit_name='usd'").fetchone()[0]
    conn.execute("insert into core.concept (taxonomy, tag) values (%s, %s) on conflict do nothing", TAG)
    kid = conn.execute("select id from core.concept where taxonomy=%s and tag=%s", TAG).fetchone()[0]
    pid = conn.execute(
        "insert into core.period (company_id, start_date, end_date, period_type) values (%s,%s,%s,%s) returning id",
        (cid, start, end, ptype),
    ).fetchone()[0]
    rid = conn.execute(
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values (%s,'u','h',%s,200) returning id",
        (cik, f"raw/{cik}"),
    ).fetchone()[0]
    out = {}
    for accn, form, fdate, por, value in copies:
        fid = conn.execute(
            "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report, is_amendment) "
            "values (%s,%s,%s,%s,%s,%s) returning id", (cid, accn, form, fdate, por, form.endswith("/A"))).fetchone()[0]
        out[accn] = conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) "
            "values (%s,%s,%s,%s,%s,%s,%s,%s) returning id", (cid, kid, uid, pid, fid, value, accn in auth, rid)).fetchone()[0]
    conn.commit()
    return cid, out


def _auth(conn, ids):
    got = conn.execute("select id from core.fact where id = any(%s) and is_authoritative", (list(ids.values()),)).fetchall()
    inv = {v: k for k, v in ids.items()}
    return sorted(inv[r[0]] for r in got)


def _run(conn, cid):
    plan = clf.plan_tag_map_promotions(conn, [cid])
    clf.apply_tag_map_promotions(conn, plan)
    conn.commit()
    return plan


# HD Goodwill 2015-02-01: original FY2014 10-K, FY2015 10-K, FY2017 10-K say 1,353; FY2018 10-K (note) says 2,102
HD = [
    ("A14", "10-K", "2015-03-30", "2015-02-01", 1353),
    ("A15", "10-K", "2016-03-30", "2016-01-31", 1353),
    ("A17", "10-K", "2018-03-30", "2018-02-04", 1353),
    ("A18", "10-K", "2019-03-29", "2019-02-03", 2102),
]


@pytest.mark.integration
def test_hd_shape_far_later_note_copy_loses_and_is_demoted(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        cid, ids = _build(conn, "0000000101", HD, auth=("A18",))
        conn.execute(
            "insert into core.fact_conflict_resolution (fact_id, rule, group_size, value_min, value_max) values (%s,'latest_filed_tagmap_v1',4,1353,2102)",
            (ids["A18"],),
        )
        conn.commit()
        _run(conn, cid)
        assert _auth(conn, ids) == ["A15"]  # latest ELIGIBLE copy (<=400 days); the 2,102 note copy is history
        rule = conn.execute("select rule from core.fact_conflict_resolution where fact_id=%s", (ids["A15"],)).fetchone()[0]
        assert rule == "latest_filed_tagmap_v2"  # the audit rule id is versioned
        # audit history stays: the demoted copy's old row still exists, marked as demoted with the old rule kept
        old = conn.execute("select rule, value_min, value_max from core.fact_conflict_resolution where fact_id=%s", (ids["A18"],)).fetchone()
        assert old is not None
        assert old[0] == clf.DEMOTED_RULE + " (was latest_filed_tagmap_v1)"
        assert (old[1], old[2]) == (1353, 2102)


@pytest.mark.integration
def test_a_demoted_copy_without_an_old_audit_row_gets_a_demotion_row(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        cid, ids = _build(conn, "0000000108", HD, auth=("A18",))
        _run(conn, cid)
        rule = conn.execute("select rule from core.fact_conflict_resolution where fact_id=%s", (ids["A18"],)).fetchone()[0]
        assert rule == clf.DEMOTED_RULE


@pytest.mark.integration
def test_next_ten_k_comparative_restatement_wins_over_the_original(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        copies = [
            ("A14", "10-K", "2015-03-30", "2015-02-01", 1353),
            ("A15", "10-K", "2016-03-30", "2016-01-31", 1400),  # restated comparative in the next 10-K
            ("A18", "10-K", "2019-03-29", "2019-02-03", 2102),
        ]
        cid, ids = _build(conn, "0000000102", copies)
        _run(conn, cid)
        assert _auth(conn, ids) == ["A15"]


@pytest.mark.integration
def test_the_original_stays_authoritative_when_every_later_copy_is_out_of_window(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        copies = [("A14", "10-K", "2015-03-30", "2015-02-01", 1353), ("A18", "10-K", "2019-03-29", "2019-02-03", 2102)]
        cid, ids = _build(conn, "0000000103", copies, auth=("A18",))
        _run(conn, cid)
        assert _auth(conn, ids) == ["A14"]


@pytest.mark.integration
def test_duration_ten_k_prints_three_years_but_a_ten_q_does_not(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        # FY2013 flow (ended 2014-02-02): the FY2015 10-K (por 2016-01-31, 728 days) prints it as the oldest column
        copies = [
            ("D13", "10-K", "2014-03-30", "2014-02-02", 100),
            ("D15", "10-K", "2016-03-30", "2016-01-31", 101),
            ("D17", "10-K", "2018-03-30", "2018-02-04", 102),
        ]
        cid, ids = _build(conn, "0000000104", copies, ptype="duration", start="2013-02-04", end="2014-02-02")
        _run(conn, cid)
        assert _auth(conn, ids) == ["D15"]
    with psycopg.connect(isolated_database_url) as conn:
        copies = [
            ("Q1", "10-Q", "2014-06-30", "2014-05-04", 50),
            ("Q2", "10-Q", "2015-06-30", "2015-05-03", 51),  # 364 days later: prints the prior-year column
            ("Q3", "10-Q", "2016-06-30", "2016-05-01", 52),  # 728 days later: a 10-Q never prints it
        ]
        cid, ids = _build(conn, "0000000105", copies, ptype="duration", start="2014-02-03", end="2014-05-04")
        _run(conn, cid)
        assert _auth(conn, ids) == ["Q2"]


@pytest.mark.integration
def test_rerun_is_idempotent_and_dedupe_keeps_zero_duplicate_groups(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        cid, ids = _build(conn, "0000000106", HD, auth=("A18",))
        _run(conn, cid)
        first = _auth(conn, ids)
        assert _run(conn, cid) == []  # nothing left to promote or demote
        assert _auth(conn, ids) == first == ["A15"]
        clf.resolve_duplicate_authoritative(conn, [cid])
        conn.commit()
        dup = conn.execute(
            "select count(*) from (select 1 from core.fact where company_id=%s and is_authoritative "
            "group by concept_id, unit_id, period_id having count(*) > 1) d", (cid,)).fetchone()[0]
        assert dup == 0 and _auth(conn, ids) == first


@pytest.mark.integration
def test_dedupe_never_lets_an_ineligible_copy_win_a_duplicate_group(isolated_database_url):
    with psycopg.connect(isolated_database_url) as conn:
        cid, ids = _build(conn, "0000000107", HD, auth=("A14", "A18"))
        clf.resolve_duplicate_authoritative(conn, [cid])
        conn.commit()
        assert _auth(conn, ids) == ["A14"]
