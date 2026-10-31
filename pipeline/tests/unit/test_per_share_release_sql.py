"""per_share_release.py (Family C) on the REAL migrated schema (CI: SCROONER_TEST_DATABASE_URL), in one transaction
rolled back at the end: a derived Q4 2025 EPS cell is removed (not filed separately), a derived Q4 2019 EPS cell takes
the FSN filed value (empty sources, cell_evidence, slot protection), the derived facts are demoted with before-images;
a second apply is stale; restore puts everything back. Needs migrations 0113 and 0116; skips otherwise."""

from __future__ import annotations

import json
from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.mapper import derived_row_retirement as rr
from scrooner_pipeline.mapper import per_share_release as ps

ON = {rf.ENV_ENABLED: f"{rr.RULE_PER_SHARE},{ps.RULE_PER_SHARE_TTM}"}


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    tables = (
        "fact_authority_retired",
        "slot_protected_cell",
        "cell_evidence",
        "canonical_fact_retired",
        "rule_run",
    )
    have = _one(c, "select count(*) from information_schema.tables where table_schema = 'analytics' and table_name = any(%s)",
                (list(tables),))  # fmt: skip
    if have != len(tables):
        c.close()
        pytest.skip("needs the migrated schema with migrations 0113 and 0116")
    c.commit = lambda: None
    yield c
    c.rollback()
    c.close()


def seed(conn) -> dict:
    cik = "0000000928"
    company = _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'EPSCO') returning id",
        (cik,),
    )
    raw = _one(conn, "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
                     "values (%s, 'test://cf', repeat('4', 64), 'raw/test/eps', 200) returning id", (cik,))  # fmt: skip
    unit = _one(conn, "insert into core.unit (unit_name) values ('usd/shares') on conflict (unit_name) do update "
                      "set unit_name = excluded.unit_name returning id")  # fmt: skip
    concept = _one(conn, "insert into core.concept (taxonomy, tag) values ('us-gaap', 'EarningsPerShareBasic') "
                         "on conflict (taxonomy, tag) do update set tag = excluded.tag returning id")  # fmt: skip
    row = conn.execute(
        "select id from analytics.canonical_concept where name = 'basic_eps'"
    ).fetchone()
    cc = row[0] if row else _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) "
                                       "values ('basic_eps', 'income_statement', 'first_match') returning id")  # fmt: skip
    conn.execute("insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence) "
                 "values (%s, %s, 1, 'approved') on conflict do nothing", (cc, concept))  # fmt: skip
    out = {"company": company, "cik": cik, "cc": cc}
    for key, (start, end, fy, acc, value) in {
        "late": ("2025-10-01", "2025-12-31", 2025, f"{cik}-26-000001", "1.10"),
        "early": ("2019-10-01", "2019-12-31", 2019, f"{cik}-20-000006", "0.95"),
    }.items():
        filing = _one(conn, "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
                            "values (%s, %s, '10-K', %s, %s) returning id", (company, acc, f"{fy + 1}-02-10", end))  # fmt: skip
        period = _one(conn, "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, "
                            "fiscal_period) values (%s, %s, %s, 'duration', %s, 'Q4') returning id",
                      (company, start, end, fy))  # fmt: skip
        fact = _one(conn, "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, "
                          "raw_object_id, is_derived, is_authoritative) values (%s, %s, %s, %s, %s, %s, %s, true, true) "
                          "returning id", (company, concept, unit, period, filing, Decimal(value), raw))  # fmt: skip
        cell = _one(conn, "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, "
                          "source_fact_ids) values (%s, %s, %s, %s, %s) returning id",
                    (company, cc, period, Decimal(value), [fact]))  # fmt: skip
        out[key] = {
            "period": period,
            "fact": fact,
            "cell": cell,
            "start": start,
            "end": end,
        }
    return out


@pytest.mark.integration
def test_plan_apply_protect_stale_restore_round_trip(conn, tmp_path):
    s = seed(conn)
    fsn = [{"canonical_fact_id": s["early"]["cell"], "outcome": "replace_with_fsn_value", "value": "0.9700",
            "accession": f"{s['cik']}-20-000006", "form": "10-K", "filed": "20200210", "start": s["early"]["start"],
            "tag": "EarningsPerShareBasic", "copies": 1, "axis": ""}]  # fmt: skip
    (tmp_path / "fsn.json").write_text(json.dumps(fsn))
    (tmp_path / "company_ids.txt").write_text(f"{s['company']}\n")
    with conn.cursor() as cur:
        plan = ps.build_plan(
            cur, [s["company"]], rr.load_fsn_outcomes(tmp_path / "fsn.json")
        )
    by = {c.canonical_fact_id: (c.action, c.reason_code) for c in plan.cells}
    assert by == {
        s["late"]["cell"]: (rr.ACT_REMOVE, "per_share_not_filed_separately"),
        s["early"]["cell"]: (rr.ACT_REPLACE_FSN, None),
    }
    (tmp_path / "PACKAGE.json").write_text(json.dumps({"digest": plan.digest(), "company_ids_file": "company_ids.txt",
                                                       "fsn_outcomes_file": "fsn.json"}))  # fmt: skip

    out = ps.apply(conn, tmp_path, plan.digest(), ps.CONFIRM_TOKEN, environ=ON)
    assert (
        out["facts_demoted"],
        out["cells_removed"],
        out["protected"],
        out["evidence_rows"],
    ) == (2, 1, 1, 1)
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where id = %s",
            (s["late"]["cell"],),
        )
        == 0
    )
    val, src = conn.execute("select value, source_fact_ids from analytics.canonical_fact where company_id = %s and "
                            "period_id = %s", (s["company"], s["early"]["period"])).fetchone()  # fmt: skip
    assert (val, list(src)) == (Decimal("0.9700"), [])
    assert _one(conn, "select count(*) from core.fact where id = any(%s) and is_authoritative",
                ([s["late"]["fact"], s["early"]["fact"]],)) == 0  # fmt: skip
    assert (
        _one(
            conn,
            "select count(*) from analytics.slot_protected_cell where run_id = %s",
            (out["run_id"],),
        )
        == 1
    )
    assert _one(conn, "select accession from analytics.cell_evidence where company_id = %s and rule_id = %s",
                (s["company"], rr.RULE_PER_SHARE)) == f"{s['cik']}-20-000006"  # fmt: skip

    with pytest.raises(ps.ReleaseRefused, match="stale"):
        ps.apply(conn, tmp_path, plan.digest(), ps.CONFIRM_TOKEN, environ=ON)

    back = ps.restore(conn, out["run_id"], ps.CONFIRM_TOKEN)
    assert back["facts_restored"] == 2 and back["unprotected"] == 1
    got = conn.execute("select period_id, value from analytics.canonical_fact where company_id = %s",
                       (s["company"],)).fetchall()  # fmt: skip
    assert sorted((p, v) for p, v in got) == sorted(
        [
            (s["late"]["period"], Decimal("1.10")),
            (s["early"]["period"], Decimal("0.95")),
        ]
    )
