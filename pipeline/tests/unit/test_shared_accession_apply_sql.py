"""shared_accession_apply.py: backup -> apply -> (simulated re-normalize) -> rollback
on the REAL migrated schema, inside one transaction that is rolled back at the end.

Scenario = the Entergy defect in miniature: the subsidiary owns the combined 10-K
and holds the parent's consolidated facts; the parent is the primary.

Needs SCROONER_TEST_DATABASE_URL on a migrated database (CI: repository-integrity
job); skips otherwise.
"""

from __future__ import annotations

import importlib.util
import sys
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import shared_accession as sa

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load_apply_module():
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(
        "shared_accession_apply", SCRIPTS / "shared_accession_apply.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PARENT, SUB = "0000000911", "0000000912"
ACC = f"{PARENT}-26-000001"


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    ok = _one(
        c,
        "select count(*) from information_schema.tables where (table_schema, table_name) in "
        "(('core','filing_registrant'), ('core','fact'), ('analytics','canonical_fact'))",
    )
    if ok != 3:
        c.close()
        pytest.skip("needs the migrated schema")
    c.commit = lambda: (
        None
    )  # the script's module functions commit; we roll back everything
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
    raw_id = _one(
        conn,
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status) "
        "values (%s, 'test://cf', repeat('1', 64), 'raw/test/x', 200) returning id",
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
    filing = _one(
        conn,
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) "
        "values (%s, %s, '10-K', '2026-02-27', '2025-12-31') returning id",
        (sub, ACC),
    )
    period = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type) values (%s, '2025-12-31', '2025-12-31', 'instant') returning id",
        (sub,),
    )
    fact = _one(
        conn,
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id) "
        "values (%s, %s, %s, %s, %s, %s, %s) returning id",
        (sub, concept, unit, period, filing, Decimal("71890000000"), raw_id),
    )
    cc = _one(
        conn,
        "insert into analytics.canonical_concept (name, statement, combination_mode) values ('total_assets_test', 'balance_sheet', 'first_match') returning id",
    )
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, %s, %s)",
        (sub, cc, period, Decimal("71890000000"), [fact]),
    )
    return {
        "parent": parent,
        "sub": sub,
        "filing": filing,
        "fact": fact,
        "period": period,
        "raw": raw_id,
        "unit": unit,
        "concept": concept,
    }


def make_plan(mod, s):
    d = sa.decide(
        ACC, [PARENT, SUB], [SUB], "10-K", PARENT
    )  # header+prefix beat the carrier
    assert d.primary_cik == PARENT and sa.carrier_conflict(d)
    moves = [(ACC, s["filing"], s["sub"], s["parent"], d.basis)]
    return mod.Plan(
        [d],
        moves,
        {PARENT: s["parent"], SUB: s["sub"]},
        [s["parent"]],
        [s["sub"]],
        {ACC: (s["filing"], s["sub"])},
    )


@pytest.mark.integration
def test_backup_apply_rollback_round_trip(conn, tmp_path, monkeypatch):
    mod = _load_apply_module()
    s = seed(conn)
    plan = make_plan(mod, s)

    img = mod.before_image(conn, plan)
    assert (
        len(img["filing"]) == 1
        and len(img["fact"]) == 1
        and len(img["canonical_fact"]) == 1
    )
    manifest = mod.write_backup(tmp_path, plan, img)
    assert set(manifest["tables"]) == {
        "filing",
        "filing_registrant",
        "fact",
        "canonical_fact",
    }

    # apply refuses with the flag OFF, applies with it ON
    monkeypatch.delenv(rf.ENV_ENABLED, raising=False)
    with pytest.raises(SystemExit):
        mod.apply(conn, plan, manifest)
    monkeypatch.setenv(rf.ENV_ENABLED, sa.RULE_ID)
    out = mod.apply(conn, plan, manifest)
    assert out["filings_now_owned_by_primary"] == 1
    assert (
        _one(
            conn,
            "select company_id from core.filing where accession_number = %s",
            (ACC,),
        )
        == s["parent"]
    )
    roles = dict(
        conn.execute(
            "select registrant_cik, role from core.filing_registrant where accession_number = %s",
            (ACC,),
        ).fetchall()
    )
    assert roles == {PARENT: "primary", SUB: "co_registrant"}

    # a second apply must refuse: the live rows no longer match the before-image
    with pytest.raises(SystemExit):
        mod.apply(conn, plan, manifest)

    # simulate the follow-on re-normalize: the sub loses the parent's fact, the parent gains one
    conn.execute(
        "delete from analytics.canonical_fact where company_id = %s", (s["sub"],)
    )
    conn.execute("delete from core.fact where id = %s", (s["fact"],))
    p_period = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type) values (%s, '2025-12-31', '2025-12-31', 'instant') returning id",
        (s["parent"],),
    )
    conn.execute(
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, raw_object_id) values (%s, %s, %s, %s, %s, 1, %s)",
        (s["parent"], s["concept"], s["unit"], p_period, s["filing"], s["raw"]),
    )

    stats = mod.rollback(conn, tmp_path)  # includes the post-rollback digest check
    assert (
        stats["filings_restored"] == 1
        and stats["facts_restored"] == 1
        and stats["canonical_facts_restored"] == 1
    )
    assert (
        _one(
            conn,
            "select company_id from core.filing where accession_number = %s",
            (ACC,),
        )
        == s["sub"]
    )
    assert (
        _one(
            conn,
            "select count(*) from core.filing_registrant where accession_number = %s",
            (ACC,),
        )
        == 0
    )
    assert (
        _one(conn, "select id from core.fact where company_id = %s", (s["sub"],))
        == s["fact"]
    )  # original id kept
    assert (
        _one(
            conn, "select count(*) from core.fact where company_id = %s", (s["parent"],)
        )
        == 0
    )
    assert mod.live_digests(conn, manifest) == {
        k: v["sha256"] for k, v in manifest["tables"].items()
    }


@pytest.mark.integration
def test_rollback_refuses_a_tampered_backup(conn, tmp_path):
    mod = _load_apply_module()
    s = seed(conn)
    plan = make_plan(mod, s)
    mod.write_backup(tmp_path, plan, mod.before_image(conn, plan))
    path = tmp_path / "fact.jsonl"
    path.write_text(path.read_text().replace("71890000000", "71890000001"))
    with pytest.raises(SystemExit):
        mod.read_backup(tmp_path)
