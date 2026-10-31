"""tax_rate_release.py on the REAL migrated schema (CI: SCROONER_TEST_DATABASE_URL), inside one transaction rolled
back at the end: a derived Q4 effective tax rate (PGR shape: FY rate minus 9M rate = -0.404) is planned, applied
(cell archived and removed, fact demoted with a before-image) and restored exactly. Needs migration 0116
(analytics.fact_authority_retired); skips without it or without the test database."""

from __future__ import annotations

import json
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.mapper import derived_row_retirement as rr
from scrooner_pipeline.mapper import tax_rate_release as tr

ON = {rf.ENV_ENABLED: rr.RULE_RATIO}


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


def _get_or_create(conn, select_sql, insert_sql, params):
    row = conn.execute(select_sql, params).fetchone()
    return row[0] if row else _one(conn, insert_sql, params)


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    tables = (
        "fact_authority_retired",
        "canonical_fact_retired",
        "rule_run",
        "canonical_fact",
    )
    have = _one(c, "select count(*) from information_schema.tables where table_schema = 'analytics' and table_name = any(%s)",
                (list(tables),))  # fmt: skip
    if have != len(tables):
        c.close()
        pytest.skip("needs the migrated schema with migration 0116")
    c.commit = lambda: None  # the release commits; the test rolls everything back
    yield c
    c.rollback()
    c.close()


def seed(conn) -> dict[str, int]:
    company = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000000926', 'TAXCO') returning id",
    )
    raw = _one(conn, "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
                     "values ('0000000926', 'test://cf', repeat('2', 64), 'raw/test/tax', 200) returning id")  # fmt: skip
    unit = _one(conn, "insert into core.unit (unit_name) values ('pure') on conflict (unit_name) do update "
                      "set unit_name = excluded.unit_name returning id")  # fmt: skip
    concept = _one(conn, "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) on conflict (taxonomy, tag) "
                         "do update set tag = excluded.tag returning id", (rr.TAX_RATE_TAG,))  # fmt: skip
    filing = _one(conn, "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
                        "values (%s, '0000000926-24-000007', '10-K', '2024-02-27', '2023-12-31') returning id", (company,))  # fmt: skip
    period = _one(conn, "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) "
                        "values (%s, '2023-10-01', '2023-12-31', 'duration', 2023, 'Q4') returning id", (company,))  # fmt: skip
    fact = _one(conn, "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id, "
                      "is_derived, is_authoritative) values (%s, %s, %s, %s, %s, -0.404, %s, true, true) returning id",
                (company, concept, unit, period, filing, raw))  # fmt: skip
    cc = _get_or_create(
        conn,
        "select id from analytics.canonical_concept where name = %s",
        "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'income_statement', 'first_match') returning id",
        (rr.TAX_RATE_CANONICAL,),
    )
    conn.execute("insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
                 "values (%s, %s, 1, 'approved') on conflict do nothing", (cc, concept))  # fmt: skip
    cell = _one(conn, "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
                      "values (%s, %s, %s, -0.404, %s) returning id", (company, cc, period, [fact]))  # fmt: skip
    return {"company": company, "fact": fact, "cc": cc, "period": period, "cell": cell}


@pytest.mark.integration
def test_plan_apply_restore_round_trip(conn, tmp_path):
    s = seed(conn)
    with conn.cursor() as cur:
        plan = tr.build_plan(cur, [s["company"]])
    assert [(c.canonical_fact_id, c.action, c.reason_code) for c in plan.cells] == [
        (s["cell"], rr.ACT_REMOVE, "ratio_derived_no_filed_value")
    ]
    (tmp_path / "company_ids.txt").write_text(f"{s['company']}\n")
    (tmp_path / "PACKAGE.json").write_text(
        json.dumps({"digest": plan.digest(), "company_ids_file": "company_ids.txt"})
    )

    with pytest.raises(tr.ReleaseRefused, match="not ON"):
        tr.apply(conn, tmp_path, plan.digest(), tr.CONFIRM_TOKEN, environ={})
    out = tr.apply(conn, tmp_path, plan.digest(), tr.CONFIRM_TOKEN, environ=ON)
    assert out["cells_removed"] == 1 and out["facts_demoted"] == 1
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where id = %s",
            (s["cell"],),
        )
        == 0
    )
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["fact"],))
        is False
    )
    assert _one(conn, "select prior_is_authoritative from analytics.fact_authority_retired where run_id = %s",
                (out["run_id"],)) is True  # fmt: skip
    assert (
        _one(
            conn,
            "select mode from analytics.rule_run where run_id = %s::uuid",
            (out["run_id"],),
        )
        == "apply"
    )

    # a second apply of the same reviewed plan is stale now: the cell is gone
    with pytest.raises(tr.ReleaseRefused, match="stale"):
        tr.apply(conn, tmp_path, plan.digest(), tr.CONFIRM_TOKEN, environ=ON)

    back = tr.restore(conn, out["run_id"], tr.CONFIRM_TOKEN)
    assert back["facts_restored"] == 1
    assert (
        _one(conn, "select is_authoritative from core.fact where id = %s", (s["fact"],))
        is True
    )
    assert _one(conn, "select value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s "
                      "and period_id = %s", (s["company"], s["cc"], s["period"])) == Decimal("-0.404")  # fmt: skip
