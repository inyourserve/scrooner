"""quick_ratio_release.py on the REAL migrated schema (CI: SCROONER_TEST_DATABASE_URL), in one transaction rolled back
at the end: build cuts the package from a plan and the live rows (one planned cell, one kept), apply hides the planned
quick_ratio with its reason, a row recomputed since the cut makes a second package stale, restore puts the value
back. Skips without the test database."""

from __future__ import annotations

from decimal import Decimal

import psycopg
import pytest

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.mapper import quick_ratio_release as qr

ON = {rf.ENV_ENABLED: qr.RULE_ID}
REASON = "incomplete:inventory_value_under_review"


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    have = _one(c, "select count(*) from information_schema.tables where table_schema = 'analytics' "
                   "and table_name in ('metric_value', 'rule_run')")  # fmt: skip
    if have != 2:
        c.close()
        pytest.skip("needs the migrated schema")
    c.commit = lambda: None
    yield c
    c.rollback()
    c.close()


def seed(conn) -> dict:
    company = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000000929', 'QRCO') returning id",
    )
    row = conn.execute(
        "select id from analytics.metric_definition where metric_name = 'quick_ratio'"
    ).fetchone()
    md = row[0] if row else _one(conn, "insert into analytics.metric_definition (metric_name, formula_version, "
                                       "formula_description) values ('quick_ratio', 1, 'test') returning id")  # fmt: skip
    ids = {}
    for label, end, value in (
        ("Q2", "2026-06-30", "2.075"),
        ("Q1", "2026-03-31", "1.9"),
    ):
        ids[label] = _one(conn, "insert into analytics.metric_value (company_id, metric_definition_id, period_start, "
                                "period_end, period_label, value, source_fact_ids, data_as_of) values "
                                "(%s, %s, %s, %s, %s, %s, %s, now()) returning id",
                          (company, md, end, end, label, Decimal(value), [5, 6]))  # fmt: skip
    return {"company": company, **ids}


def _plan(s):
    return [{"company_id": s["company"], "period_end": "2026-06-30", "period_label": "Q2", "stored": "2.075",
             "reason": REASON}]  # fmt: skip


@pytest.mark.integration
def test_build_apply_stale_restore_round_trip(conn, tmp_path):
    s = seed(conn)
    m = qr.build(conn, _plan(s), [s["company"]], tmp_path)
    assert (m["cells"], m["keep_cells"], m["stale_at_build"]) == (1, 1, 0)
    conn.execute("set default_transaction_read_only = off")
    assert (
        qr.dry_run(conn, qr.load_package(tmp_path, m["digest"]))["would_apply"] is True
    )

    out = qr.apply(conn, tmp_path, m["digest"], qr.CONFIRM_TOKEN, environ=ON)
    assert out["hidden"] == 1
    value, reason, src = conn.execute("select value, is_null_reason, source_fact_ids from analytics.metric_value "
                                      "where id = %s", (s["Q2"],)).fetchone()  # fmt: skip
    assert (value, reason, src) == (None, REASON, None)
    assert _one(
        conn, "select value from analytics.metric_value where id = %s", (s["Q1"],)
    ) == Decimal("1.9")

    # the cut is stale for a row the nightly recomputed since: nothing is written
    conn.execute(
        "update analytics.metric_value set value = 1.95 where id = %s", (s["Q1"],)
    )
    stale_dir = tmp_path / "stale"
    plan = [
        {
            "company_id": s["company"],
            "period_end": "2026-03-31",
            "period_label": "Q1",
            "stored": "1.9",
            "reason": REASON,
        }
    ]
    m2 = qr.build(conn, plan, [s["company"]], stale_dir)
    assert (m2["cells"], m2["stale_at_build"]) == (0, 1)

    back = qr.restore(conn, tmp_path, out["run_id"], qr.CONFIRM_TOKEN)
    assert back["restored"] == 1 and back["skipped"] == []
    value, reason, src = conn.execute("select value, is_null_reason, source_fact_ids from analytics.metric_value "
                                      "where id = %s", (s["Q2"],)).fetchone()  # fmt: skip
    assert (value, reason, list(src)) == (Decimal("2.075"), None, [5, 6])
