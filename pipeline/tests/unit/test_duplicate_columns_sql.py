"""period.duplicate_column_merge@1 on the REAL migrated schema: plan -> apply (flag ON)
-> rollback, MSFT-shaped (recast: hide) and RBC-shaped (stray context: merge) seeds.
Needs SCROONER_TEST_DATABASE_URL on a migrated database; skips otherwise."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import duplicate_columns as dc

CIK = "0000000921"


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if (
        _one(
            c,
            "select count(*) from information_schema.tables where (table_schema, table_name) in "
            "(('core','fact'), ('analytics','cell_blank_reason'), ('analytics','rule_run'))",
        )
        != 3
    ):
        c.close()
        pytest.skip("needs the migrated schema")
    c.commit = lambda: None  # everything rolled back at the end
    yield c
    c.rollback()
    c.close()


def seed(conn):
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'DUP CO') returning id",
        (CIK,),
    )
    raw = _one(
        conn,
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
        "values (%s, 'test://cf', repeat('2', 64), 'raw/test/d', 200) returning id",
        (CIK,),
    )
    unit = _one(
        conn,
        "insert into core.unit (unit_name) values ('usd') on conflict (unit_name) do update set unit_name = excluded.unit_name returning id",
    )
    rev = _one(
        conn,
        "insert into core.concept (taxonomy, tag) values ('us-gaap', 'Revenues') on conflict (taxonomy, tag) do update set tag = excluded.tag returning id",
    )
    cogs = _one(
        conn,
        "insert into core.concept (taxonomy, tag) values ('us-gaap', 'CostOfRevenue') on conflict (taxonomy, tag) do update set tag = excluded.tag returning id",
    )
    cc = _one(
        conn,
        "insert into analytics.canonical_concept (name, statement, combination_mode) values ('revenue_dup_test', 'income_statement', 'first_match') returning id",
    )
    conn.execute(
        "insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) values (%s, %s, 1, 'approved') on conflict do nothing",
        (cc, rev),
    )
    f1 = _one(
        conn,
        "insert into core.filing (company_id, accession_number, form, filing_date) values (%s, %s, '10-Q', '2016-10-20') returning id",
        (cid, f"{CIK}-16-000001"),
    )
    f2 = _one(
        conn,
        "insert into core.filing (company_id, accession_number, form, filing_date) values (%s, %s, '10-Q', '2017-10-26') returning id",
        (cid, f"{CIK}-17-000001"),
    )

    def period(start, end, fy, fp):
        return _one(
            conn,
            "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
            "values (%s, %s, %s, 'duration', %s, %s) returning id",
            (cid, start, end, fy, fp),
        )

    def fact(concept, period, value, filing, auth=True):
        return _one(
            conn,
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) "
            "values (%s, %s, %s, %s, %s, %s, %s, %s) returning id",
            (cid, concept, unit, period, filing, Decimal(value), auth, raw),
        )

    # MSFT-shaped: Q1 FY2017 spelled 07-01 and 07-02, revenue differs (recast)
    m_can = period("2016-07-01", "2016-09-30", 2017, "Q1")
    m_dup = period("2016-07-02", "2016-09-30", 2017, "Q1")
    m1 = fact(rev, m_can, "20453000000", f1)
    fact(cogs, m_can, "6000000000", f1)
    m2 = fact(rev, m_dup, "21928000000", f2)
    # RBC-shaped: Q2 FY2026 spelled 06-29 and 07-01; the stray row carries one equal copy
    r_can = period("2025-06-29", "2025-09-27", 2026, "Q2")
    r_dup = period("2025-07-01", "2025-09-27", 2026, "Q2")
    r1 = fact(rev, r_can, "1000000000", f1)
    fact(cogs, r_can, "600000000", f1)
    r2 = fact(rev, r_dup, "1000000000", f2)  # equal value, other filing -> repoint
    # FY facts to set the presentation scale (millions)
    fy = period("2016-07-01", "2017-06-30", 2017, "FY")
    fact(rev, fy, "89950000000", f1)
    return {
        "cid": cid,
        "rev": rev,
        "m_can": m_can,
        "m_dup": m_dup,
        "m1": m1,
        "m2": m2,
        "r_can": r_can,
        "r_dup": r_dup,
        "r1": r1,
        "r2": r2,
    }


@pytest.mark.integration
def test_plan_apply_rollback(conn, tmp_path, monkeypatch):
    s = seed(conn)
    plan = dc.plan_company(conn, s["cid"])
    assert plan.scale == 6
    by = {(a.canonical.id, a.action): a for a in plan.actions}
    hide = by[(s["m_can"], dc.HIDE)]
    assert sorted(hide.demote_fact_ids) == sorted([s["m1"], s["m2"]])
    merge = by[(s["r_can"], dc.MERGE)]
    assert merge.repoint_fact_ids == [s["r2"]] and merge.demote_fact_ids == []

    # dry run (flag off): run() writes nothing
    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    totals = dc.run(conn, {CIK}, report_path=tmp_path / "report.jsonl")
    assert totals["mode"] == rf.OFF and totals[dc.HIDE] == 1 and totals[dc.MERGE] == 1
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["m1"],))
        is True
    )
    assert (tmp_path / "report.jsonl").read_text().count("\n") == 2

    # apply refuses off, applies on
    with pytest.raises(RuntimeError):
        dc.apply_company(
            conn, plan, "00000000-0000-0000-0000-000000000000", tmp_path / "img"
        )
    monkeypatch.setenv(rf.ENV_ENABLED, dc.RULE_ID)
    totals = dc.run(conn, {CIK}, backup_dir=tmp_path / "img")
    assert (
        totals[dc.HIDE] == 1
        and totals[dc.MERGE] == 1
        and totals["facts_demoted"] == 2
        and totals["facts_repointed"] == 1
    )
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["m1"],))
        is False
    )
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["m2"],))
        is False
    )
    assert (
        _one(conn, "select period_id from core.fact where id = %s", (s["r2"],))
        == s["r_can"]
    )
    assert (
        _one(conn, "select count(*) from core.period where id = %s", (s["r_dup"],)) == 1
    )  # never deleted
    reasons = conn.execute(
        "select data_point_name, period_start, period_end, reason_code from analytics.cell_blank_reason where company_id = %s",
        (s["cid"],),
    ).fetchall()
    assert (
        len(reasons) == 1
        and reasons[0][0] == "revenue_dup_test"
        and reasons[0][3] == dc.REASON_CODE_DIFFER
    )
    assert str(reasons[0][1]) == "2016-07-01" and str(reasons[0][2]) == "2016-09-30"
    assert (
        _one(
            conn,
            "select count(*) from analytics.rule_run where rule_id = %s",
            (dc.RULE_ID,),
        )
        == 1
    )

    # second apply is a no-op plan (the duplicate rows now carry no live conflict)
    plan2 = dc.plan_company(conn, s["cid"])
    assert all(a.action != dc.MERGE for a in plan2.actions)

    # rollback restores both facts and removes the reason
    out = dc.rollback_run(conn, tmp_path / "img")
    assert out == {"companies": 1, "facts_restored": 3, "reasons_deleted": 1}
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["m1"],))
        is True
    )
    assert (
        _one(conn, "select period_id from core.fact where id = %s", (s["r2"],))
        == s["r_dup"]
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.cell_blank_reason where company_id = %s",
            (s["cid"],),
        )
        == 0
    )
