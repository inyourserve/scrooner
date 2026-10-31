"""entity.shared_accession_demote_coregistrant_facts@1 on the REAL migrated schema:
plan -> apply (flag ON) -> rollback. Entergy in miniature: Arkansas (sub) holds
the parent's consolidated facts from the combined 10-K now owned by Entergy."""

from __future__ import annotations

from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import shared_accession_cleanup as sc

PARENT, SUB = "0000000931", "0000000932"
ACC = f"{PARENT}-26-000001"


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    ok = _one(
        c,
        "select count(*) from information_schema.tables where (table_schema, table_name) in "
        "(('core','filing_registrant'), ('analytics','canonical_fact_retired'), ('analytics','rule_run'))",
    )
    if ok != 3:
        c.close()
        pytest.skip("needs the migrated schema (0098, 0100)")
    c.commit = lambda: None
    yield c
    c.rollback()
    c.close()


def seed(conn):
    parent = _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'PARENT') returning id",
        (PARENT,),
    )
    sub = _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'SUB') returning id",
        (SUB,),
    )
    raw = _one(
        conn,
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) values (%s, 'test://cf', repeat('3', 64), 'raw/test/c', 200) returning id",
        (SUB,),
    )
    unit = _one(
        conn,
        "insert into core.unit (unit_name) values ('usd') on conflict (unit_name) do update set unit_name = excluded.unit_name returning id",
    )
    concept = _one(
        conn,
        "insert into core.concept (taxonomy, tag) values ('us-gaap', 'Assets') on conflict (taxonomy, tag) do update set tag = excluded.tag returning id",
    )
    cc = _one(
        conn,
        "insert into analytics.canonical_concept (name, statement, combination_mode) values ('total_assets_cleanup_test', 'balance_sheet', 'first_match') returning id",
    )
    filing = _one(
        conn,
        "insert into core.filing (company_id, accession_number, form, filing_date) values (%s, %s, '10-K', '2026-02-27') returning id",
        (parent, ACC),
    )
    conn.execute(
        "insert into core.filing_registrant (accession_number, registrant_cik, company_id, role, filer_count) values (%s, %s, %s, 'primary', 2), (%s, %s, %s, 'co_registrant', 2)",
        (ACC, PARENT, parent, ACC, SUB, sub),
    )
    own_filing = _one(
        conn,
        "insert into core.filing (company_id, accession_number, form, filing_date) values (%s, %s, '10-Q', '2026-04-30') returning id",
        (sub, f"{SUB}-26-000003"),
    )
    period = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) values (%s, '2025-12-31', '2025-12-31', 'instant', 2025, 'FY') returning id",
        (sub,),
    )
    p2 = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) values (%s, '2026-03-31', '2026-03-31', 'instant', 2026, 'Q1') returning id",
        (sub,),
    )
    bad = _one(
        conn,
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id) values (%s, %s, %s, %s, %s, 71890000000, %s) returning id",
        (sub, concept, unit, period, filing, raw),
    )
    good = _one(
        conn,
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id) values (%s, %s, %s, %s, %s, 12000000000, %s) returning id",
        (sub, concept, unit, p2, own_filing, raw),
    )
    cell_bad = _one(
        conn,
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, 71890000000, %s) returning id",
        (sub, cc, period, [bad]),
    )
    cell_good = _one(
        conn,
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, 12000000000, %s) returning id",
        (sub, cc, p2, [good]),
    )
    return {
        "sub": sub,
        "parent": parent,
        "bad": bad,
        "good": good,
        "cell_bad": cell_bad,
        "cell_good": cell_good,
    }


@pytest.mark.integration
def test_plan_apply_rollback(conn, tmp_path, monkeypatch):
    s = seed(conn)
    plan = sc.plan_company(conn, s["sub"])
    assert plan.fact_ids == [s["bad"]] and [c["id"] for c in plan.cells] == [
        s["cell_bad"]
    ]
    assert list(plan.filings) == [ACC]

    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    totals = sc.run(conn, {SUB})
    assert (
        totals["mode"] == rf.OFF
        and totals["facts_to_demote"] == 1
        and totals["cells_to_archive"] == 1
    )
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["bad"],))
        is True
    )

    monkeypatch.setenv(rf.ENV_ENABLED, sc.RULE_ID)
    totals = sc.run(conn, {SUB}, backup_dir=tmp_path / "img")
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["bad"],))
        is False
    )
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["good"],))
        is True
    )  # own filing untouched
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where id = %s",
            (s["cell_bad"],),
        )
        == 0
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where id = %s",
            (s["cell_good"],),
        )
        == 1
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact_retired where canonical_fact_id = %s and reason_code = %s",
            (s["cell_bad"], sc.REASON_CODE),
        )
        == 1
    )
    r = conn.execute(
        "select data_point_name, period_grain, period_end, reason_code, defect_class from analytics.cell_blank_reason where company_id = %s",
        (s["sub"],),
    ).fetchall()
    assert r == [
        (
            "total_assets_cleanup_test",
            "I",
            __import__("datetime").date(2025, 12, 31),
            sc.REASON_CODE,
            "identity",
        )
    ]
    # second apply: nothing left to do
    plan2 = sc.plan_company(conn, s["sub"])
    assert plan2.fact_ids == [] and plan2.already_demoted == 1 and plan2.cells == []

    out = sc.rollback_run_dir(conn, tmp_path / "img")
    assert out == {
        "companies": 1,
        "facts_restored": 1,
        "cells_restored": 1,
        "reasons_deleted": 1,
    }
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["bad"],))
        is True
    )
    assert _one(
        conn,
        "select value from analytics.canonical_fact where company_id = %s and period_id = (select period_id from analytics.canonical_fact_retired where canonical_fact_id = %s limit 1)",
        (s["sub"], s["cell_bad"]),
    ) == Decimal("71890000000")
    assert (
        _one(
            conn,
            "select count(*) from analytics.cell_blank_reason where company_id = %s",
            (s["sub"],),
        )
        == 0
    )
