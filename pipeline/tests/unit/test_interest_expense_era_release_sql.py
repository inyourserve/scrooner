"""interest_expense_era_release.py on the REAL migrated schema (CI: SCROONER_TEST_DATABASE_URL), in one transaction
rolled back at the end: build -> dry run -> apply (two canonical rows from the filed fact, slot protection, evidence,
a hold reason) -> a nightly-style delete of the protected row is skipped by the 0113 guard -> a second apply is stale
-> restore removes rows, protection and reasons. Skips without the test database or migration 0113."""

from __future__ import annotations

import psycopg
import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.mapper import interest_expense_era_release as ie

ON = {rf.ENV_ENABLED: ie.RULE_ID}


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


def _concept(conn, name):
    row = conn.execute(
        "select id from analytics.canonical_concept where name = %s", (name,)
    ).fetchone()
    if row:
        return row[0]
    return _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) "
                      "values (%s, 'income_statement', 'first_match') returning id", (name,))  # fmt: skip


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    tables = (
        "slot_protected_cell",
        "cell_blank_reason",
        "cell_evidence",
        "canonical_fact_retired",
        "rule_run",
    )
    have = _one(c, "select count(*) from information_schema.tables where table_schema = 'analytics' and table_name = any(%s)",
                (list(tables),))  # fmt: skip
    if have != len(tables):
        c.close()
        pytest.skip("needs the migrated schema with migration 0113")
    c.commit = lambda: None
    yield c
    c.rollback()
    c.close()


def seed(conn) -> dict:
    company = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000000927', 'IECO') returning id",
    )
    raw = _one(conn, "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
                     "values ('0000000927', 'test://cf', repeat('3', 64), 'raw/test/ie', 200) returning id")  # fmt: skip
    unit = _one(conn, "insert into core.unit (unit_name) values ('usd') on conflict (unit_name) do update "
                      "set unit_name = excluded.unit_name returning id")  # fmt: skip
    concept = _one(conn, "insert into core.concept (taxonomy, tag) values ('us-gaap', 'InterestExpenseNonoperating') "
                         "on conflict (taxonomy, tag) do update set tag = excluded.tag returning id")  # fmt: skip
    filing = _one(conn, "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
                        "values (%s, '0000000927-25-000053', '10-Q', '2025-04-25', '2025-03-31') returning id", (company,))  # fmt: skip
    p_fill = _one(conn, "insert into core.period (company_id, start_date, end_date, period_type) "
                        "values (%s, '2025-01-01', '2025-03-31', 'duration') returning id", (company,))  # fmt: skip
    p_hold = _one(conn, "insert into core.period (company_id, start_date, end_date, period_type) "
                        "values (%s, '2025-04-01', '2025-06-30', 'duration') returning id", (company,))  # fmt: skip
    fact = _one(conn, "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id) "
                      "values (%s, %s, %s, %s, %s, 67000000, %s) returning id",
                (company, concept, unit, p_fill, filing, raw))  # fmt: skip
    return {"company": company, "fact": fact, "p_fill": p_fill, "p_hold": p_hold,
            "cc": {n: _concept(conn, n) for n in ie.CONCEPTS}}  # fmt: skip


def _plan_rows(s):
    common = {"cik": "0000000927", "bank": "False", "tag": "InterestExpenseNonoperating",
              "accession": "0000000927-25-000053", "company_id": str(s["company"]), "months": "3"}  # fmt: skip
    return [
        {**common, "period_id": str(s["p_fill"]), "start": "2025-01-01", "end": "2025-03-31", "value": "67000000",
         "fact_id": str(s["fact"]), "outcome": "fill", "label_check": "gross_label", "label": "Interest expense"},
        {**common, "period_id": str(s["p_hold"]), "start": "2025-04-01", "end": "2025-06-30", "value": "70000000",
         "fact_id": "0", "outcome": "hold_net_label", "label_check": "net_label", "label": "Interest expense, net"},
    ]  # fmt: skip


@pytest.mark.integration
def test_build_apply_guard_stale_restore_round_trip(conn, tmp_path):
    s = seed(conn)
    m = ie.build(_plan_rows(s), tmp_path)
    cells, holds = ie.load_package(tmp_path, m["digest"]), ie.load_holds(tmp_path)
    assert ie.dry_run(conn, cells, holds)["would_apply"] is True
    conn.execute("set default_transaction_read_only = off")

    out = ie.apply(conn, tmp_path, m["digest"], ie.CONFIRM_TOKEN, environ=ON)
    assert (out["inserted"], out["protected"], out["hold_reasons"]) == (2, 2, 1)
    rows = conn.execute("select canonical_concept_id, value, source_fact_ids from analytics.canonical_fact "
                        "where company_id = %s order by 1", (s["company"],)).fetchall()  # fmt: skip
    assert {(r[0], int(r[1]), tuple(r[2])) for r in rows} == {
        (cc, 67000000, (s["fact"],)) for cc in s["cc"].values()
    }
    assert (
        _one(
            conn,
            "select count(*) from analytics.slot_protected_cell where run_id = %s",
            (out["run_id"],),
        )
        == 2
    )
    assert _one(conn, "select count(*) from analytics.cell_evidence where company_id = %s and rule_id = %s",
                (s["company"], ie.RULE_ID)) == 1  # fmt: skip
    assert _one(conn, "select reason_code from analytics.cell_blank_reason where run_id = %s::uuid",
                (out["run_id"],)) == "hold_net_label"  # fmt: skip

    # a nightly resolver's delete-then-insert of a protected cell is skipped by the 0113 guard
    # (here the release's batches are savepoints of the test's transaction, so its SET LOCAL slot_writer = 'on' is
    # still in force: a nightly session never has it, so switch it off the way that session would be)
    conn.execute("set local scrooner.slot_writer = 'off'")
    conn.execute(
        "delete from analytics.canonical_fact where company_id = %s", (s["company"],)
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where company_id = %s",
            (s["company"],),
        )
        == 2
    )

    with pytest.raises(ie.ReleaseRefused, match="stale"):
        ie.apply(conn, tmp_path, m["digest"], ie.CONFIRM_TOKEN, environ=ON)

    back = ie.restore(conn, out["run_id"], ie.CONFIRM_TOKEN)
    assert (back["unprotected"], back["hold_reasons_deleted"]) == (2, 1)
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where company_id = %s",
            (s["company"],),
        )
        == 0
    )
