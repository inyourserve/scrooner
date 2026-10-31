"""mapper/slot_is_not_presented.py: the blank-reason write path for
slot.is_operating_income_not_presented@1. File-only refusals are unit tests;
apply / stale refusal / restore run on REAL SQL in an isolated test database
(migration 0098's archive table and 0100's rule_run / cell_blank_reason DDL are
read from the migrations themselves, foreign keys stripped; the 0113 guard
table is created inline with 0114's nullable value; one test re-applies
0113's NOT NULL to prove the 0114 refusal)."""

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.mapper import slot_is_not_presented as np

MIG = Path(__file__).parents[2] / "db" / "migrations"
ON = {"SCROONER_RULES_ENABLED": np.RULE_ID}


def _write_pkg(tmp: Path, reason_only, would_hide, q4, before) -> str:
    strata = {}
    for name, rows in (
        ("prod_blank_reason_only", reason_only),
        ("prod_has_value_would_hide", would_hide),
        ("q4_prod_has_value_would_hide", q4),
    ):
        p = tmp / f"is_oi_not_presented_{name}.jsonl"
        p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
        strata[name] = {
            "file": p.name,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "cells": len(rows),
        }
    bi = tmp / "is_oi_not_presented_before_image.jsonl"
    bi.write_text("".join(json.dumps(b, sort_keys=True) + "\n" for b in before))
    meta = {
        "rule_id": np.RULE_ID,
        "kind": "blank_reasons",
        "strata": strata,
        "before_image": {
            "file": bi.name,
            "sha256": hashlib.sha256(bi.read_bytes()).hexdigest(),
        },
    }
    (tmp / "PACKAGE.json").write_text(json.dumps(meta))
    return np.package_digest(meta)


def _cell(cik, start, end, grain, prod_cf_id=None, prod_value=None):
    return {
        "cik": cik,
        "data_point_name": "operating_income",
        "period_grain": grain,
        "period_start": start,
        "period_end": end,
        "basis": "latest",
        "state": "not_presented",
        "rule_id": np.RULE_ID,
        "reason_code": np.REASON_CODE,
        "reason_text": "no operating line",
        "stratum": "x",
        "input_refs": {
            "accession": "0000000001-24-000001",
            "form": "10-K",
            "face_report": 2,
            "shape": "commercial",
        },
        "prod_cf_id": prod_cf_id,
        "prod_value": prod_value,
    }


# ------------------------------------------------------------------ file-only
@pytest.mark.unit
def test_wrong_digest_refuses_before_any_db_access(tmp_path):
    _write_pkg(
        tmp_path, [_cell("0000000001", "2024-01-01", "2024-12-31", "FY")], [], [], []
    )
    with pytest.raises(np.ReleaseRefused, match="digest"):
        np.load_package(tmp_path, "0" * 64)


@pytest.mark.unit
def test_tampered_stratum_refuses(tmp_path):
    d = _write_pkg(
        tmp_path, [_cell("0000000001", "2024-01-01", "2024-12-31", "FY")], [], [], []
    )
    p = tmp_path / "is_oi_not_presented_prod_blank_reason_only.jsonl"
    p.write_text(p.read_text().replace("2024-12-31", "2023-12-31"))
    with pytest.raises(np.ReleaseRefused, match="sha256"):
        np.load_package(tmp_path, d)


@pytest.mark.unit
def test_hide_cell_without_before_image_row_refuses(tmp_path):
    d = _write_pkg(
        tmp_path,
        [],
        [_cell("0000000001", "2024-01-01", "2024-12-31", "FY", 7, "5")],
        [],
        [],
    )
    with pytest.raises(np.ReleaseRefused, match="before-image"):
        np.load_package(tmp_path, d)


@pytest.mark.unit
def test_flag_off_and_bad_token_refuse_without_touching_the_connection(tmp_path):
    d = _write_pkg(
        tmp_path, [_cell("0000000001", "2024-01-01", "2024-12-31", "FY")], [], [], []
    )
    pkg = np.load_package(tmp_path, d)
    with pytest.raises(np.ReleaseRefused, match="not ON"):
        np.apply(None, pkg, confirm=np.CONFIRM_TOKEN, environ={})
    with pytest.raises(np.ReleaseRefused, match="confirm"):
        np.apply(None, pkg, confirm="yes", environ=ON)


@pytest.mark.unit
def test_rule_is_registered_and_off_by_default():
    from scrooner_pipeline.common.rule_flags import RULES, rule_mode

    assert np.RULE_ID in RULES and RULES[np.RULE_ID].dry_run
    assert rule_mode(np.RULE_ID, {}) == "off"


# ------------------------------------------------------------------ real SQL
def _ddl(path: str, table: str) -> str:
    sql = (MIG / path).read_text()
    ddl = sql[sql.index(f"create table if not exists {table}") :]
    ddl = ddl[: ddl.index(");") + 2]
    return re.sub(r"references \w+\.\w+ \(\w+\)", "", ddl)


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute(
            "drop schema if exists analytics cascade; drop schema if exists core cascade"
        )
        c.execute("create schema core; create schema analytics")
        c.execute("create table core.company (id bigint primary key, cik text unique)")
        # core.period is PER COMPANY in production (unique company, start, end, type)
        c.execute(
            "create table core.period (id bigint primary key, company_id bigint not null, period_type text, "
            "start_date date, end_date date, unique (company_id, start_date, end_date, period_type))"
        )
        c.execute(
            "create table analytics.canonical_concept (id bigint primary key, name text)"
        )
        c.execute(
            """create table analytics.canonical_fact (
                 id bigint generated always as identity primary key, company_id bigint not null,
                 canonical_concept_id bigint not null, period_id bigint not null, value numeric not null,
                 source_fact_ids bigint[] not null, resolved_at timestamptz not null default now(),
                 unique (company_id, canonical_concept_id, period_id))"""
        )
        c.execute(
            _ddl(
                "0098_per_share_gap_cause_and_canonical_fact_retired.sql",
                "analytics.canonical_fact_retired",
            )
        )
        c.execute(
            _ddl("0100_cell_evidence_reason_registrant_audit.sql", "analytics.rule_run")
        )
        c.execute(
            _ddl(
                "0100_cell_evidence_reason_registrant_audit.sql",
                "analytics.cell_blank_reason",
            )
        )
        c.execute(
            """create table analytics.slot_protected_cell (
                 company_id bigint not null, canonical_concept_id bigint not null, period_id bigint not null,
                 rule_id text not null, value numeric, run_id text not null, package_sha256 text not null,
                 protected_at timestamptz not null default now(),
                 primary key (company_id, canonical_concept_id, period_id))"""
        )
        c.execute(
            "insert into core.company values (1, '0000000001'), (2, '0000000002')"
        )
        # company 1 owns 20/22, company 2 owns 10/11; a cross-company period match would protect the wrong key
        c.execute(
            "insert into core.period values (10, 2, 'duration', '2024-01-01', '2024-12-31'), "
            "(11, 2, 'duration', '2024-10-01', '2024-12-31'), (20, 1, 'duration', '2024-01-01', '2024-12-31'), "
            "(22, 1, 'duration', '2023-01-01', '2023-12-31')"
        )
        c.execute(
            "insert into analytics.canonical_concept values (5, 'operating_income_resolved')"
        )
        c.execute(
            "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
            "values (2, 5, 10, 900, '{41,42}'), (2, 5, 11, 200, '{43}')"
        )
        c.commit()
        yield c
        c.rollback()
        c.execute(
            "drop schema if exists analytics cascade; drop schema if exists core cascade"
        )
        c.commit()


def _pkg_for(db, tmp_path):
    rows = {
        r[0]: r
        for r in db.execute(
            "select id, company_id, value::text, source_fact_ids, resolved_at::text, period_id from analytics.canonical_fact"
        ).fetchall()
    }
    before = [
        {
            "canonical_fact_id": i,
            "company_id": r[1],
            "cik": "0000000002",
            "canonical_concept_id": 5,
            "period_id": r[5],
            "start": "",
            "end": "",
            "value_before": r[2],
            "source_fact_ids_before": r[3],
            "resolved_at_before": r[4],
        }
        for i, r in rows.items()
    ]
    ids = {r[5]: i for i, r in rows.items()}
    d = _write_pkg(
        tmp_path,
        # the third cell's dates exist only as company 2's period 11: it must stay unprotected
        [
            _cell("0000000001", "2024-01-01", "2024-12-31", "FY"),
            _cell("0000000001", "2023-01-01", "2023-12-31", "FY"),
            _cell("0000000001", "2024-10-01", "2024-12-31", "Q"),
        ],
        [_cell("0000000002", "2024-01-01", "2024-12-31", "FY", ids[10], "900")],
        [_cell("0000000002", "2024-10-01", "2024-12-31", "Q", ids[11], "200")],
        before,
    )
    return np.load_package(tmp_path, d)


@pytest.mark.integration
def test_apply_writes_reasons_hides_and_protects_then_restore_undoes_it(db, tmp_path):
    pkg = _pkg_for(db, tmp_path)
    res = np.apply(db, pkg, confirm=np.CONFIRM_TOKEN, environ=ON)
    assert (res["reasons"], res["removed"], res["protected"]) == (5, 2, 4)
    assert res["plan"]["reason_only_without_period_row"] == 1
    assert (
        db.execute("select count(*) from analytics.canonical_fact").fetchone()[0] == 0
    )
    assert (
        db.execute(
            "select count(*) from analytics.canonical_fact_retired where action = 'removed'"
        ).fetchone()[0]
        == 2
    )
    assert (
        db.execute(
            "select count(distinct state || reason_code) from analytics.cell_blank_reason"
        ).fetchone()[0]
        == 1
    )
    assert (
        db.execute(
            "select count(*) from analytics.slot_protected_cell where value is null"
        ).fetchone()[0]
        == 4
    )
    # every protected key belongs to its own company's period
    assert (
        db.execute(
            "select count(*) from analytics.slot_protected_cell sp join core.period p on p.id = sp.period_id "
            "where p.company_id <> sp.company_id"
        ).fetchone()[0]
        == 0
    )
    out = np.restore(db, res["run_id"], confirm=np.CONFIRM_TOKEN)
    assert (
        out["restored_rows"],
        out["reasons_deleted"],
        out["protection_removed"],
    ) == (2, 5, 4)
    assert sorted(
        db.execute("select value from analytics.canonical_fact").fetchall()
    ) == [(Decimal(200),), (Decimal(900),)]
    assert db.execute(
        "select array_agg(mode order by started_at) from analytics.rule_run"
    ).fetchone()[0] == ["apply", "rollback"]


@pytest.mark.integration
def test_stale_would_hide_row_refuses_the_whole_run_and_writes_nothing(db, tmp_path):
    pkg = _pkg_for(db, tmp_path)
    db.execute("update analytics.canonical_fact set value = 901 where period_id = 10")
    db.commit()
    with pytest.raises(np.ReleaseRefused, match="STALE"):
        np.apply(db, pkg, confirm=np.CONFIRM_TOKEN, environ=ON)
    assert (
        db.execute("select count(*) from analytics.cell_blank_reason").fetchone()[0]
        == 0
    )
    assert db.execute("select count(*) from analytics.rule_run").fetchone()[0] == 0


@pytest.mark.integration
def test_reason_only_cell_that_gained_a_value_refuses(db, tmp_path):
    pkg = _pkg_for(db, tmp_path)
    db.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) "
        "values (1, 5, 22, 7, '{9}')"
    )
    db.commit()
    with pytest.raises(
        np.ReleaseRefused, match="reason-only cell now has a production value"
    ):
        np.apply(db, pkg, confirm=np.CONFIRM_TOKEN, environ=ON)


@pytest.mark.integration
def test_apply_refuses_while_value_is_not_null_as_0113_shipped_it(db, tmp_path):
    pkg = _pkg_for(db, tmp_path)
    db.execute(
        "alter table analytics.slot_protected_cell alter column value set not null"
    )
    db.commit()
    with pytest.raises(np.ReleaseRefused, match="0114"):
        np.apply(db, pkg, confirm=np.CONFIRM_TOKEN, environ=ON)
    assert (
        db.execute("select count(*) from analytics.canonical_fact").fetchone()[0] == 2
    )


@pytest.mark.integration
def test_apply_refuses_without_the_0113_guard_table(db, tmp_path):
    pkg = _pkg_for(db, tmp_path)
    db.execute("drop table analytics.slot_protected_cell")
    db.commit()
    with pytest.raises(np.ReleaseRefused, match="0113"):
        np.apply(db, pkg, confirm=np.CONFIRM_TOKEN, environ=ON)
    assert (
        db.execute("select count(*) from analytics.canonical_fact").fetchone()[0] == 2
    )
