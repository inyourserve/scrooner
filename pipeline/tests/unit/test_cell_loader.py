"""Cell loader: row validation (pure) and a real-schema round trip (plan writes nothing, apply writes, reload idempotent)."""

from __future__ import annotations

import gzip
import json
from datetime import date
from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.normalizer import cell_loader as cl

POINTS = {"capex_resolved", "cash_and_equivalents_resolved", "revenue_sanity_resolved"}


def _row(**over):
    base = {
        "company_id": 1,
        "data_point_name": "capex_resolved",
        "period_grain": "Q",
        "period_start": "2024-01-01",
        "period_end": "2024-03-31",
        "basis": "latest",
        "state": "value",
        "value": "100",
        "unit": "USD",
        "decimals": -6,
        "source_fact_ids": [],
        "accession": "0000000001-24-000001",
        "tag": "PaymentsToAcquirePropertyPlantAndEquipment",
        "rule_id": "slot.capex@1",
        "evidence_level": "FILING-CHECKED",
    }
    base.update(over)
    return base


@pytest.mark.unit
def test_parse_row_accepts_a_valued_cell_and_names_every_rejection():
    r = cl.parse_row(1, _row(), POINTS)
    assert isinstance(r, cl.CellRow) and r.value == Decimal("100") and r.exact_dates
    cases = {
        "unknown_data_point_name": _row(data_point_name="quick_ratio"),
        "grain_not_FY_Q_I": _row(period_grain="TP"),
        "state_outside_contract": _row(state="held"),
        "no_period_key": _row(period_start=None, period_end=None),
        "grain_period_type_mismatch": _row(period_grain="I", period_type="duration"),
        "period_before_history_floor": _row(
            period_start="2013-01-01", period_end="2013-03-31"
        ),
        "valued_state_without_value": _row(value=None),
        "unit_missing_or_unknown": _row(unit="millions"),
        "derived_without_derivation": _row(state="derived"),
        "blank_state_with_value": _row(state="not_presented", reason_code="x"),
        "blank_without_reason_code": _row(state="not_presented", value=None),
        "bad_rule_id": _row(rule_id="capex"),
        "bad_evidence_level": _row(evidence_level="GUESSED"),
        "defect_fields_inconsistent": _row(
            state="defect", value=None, reason_code="x", defect_class="period"
        ),
    }
    assert {why: cl.parse_row(1, row, POINTS) for why, row in cases.items()} == {
        w: w for w in cases
    }
    # fiscal binding key instead of exact dates
    fb = cl.parse_row(
        2,
        _row(
            period_start=None,
            period_end=None,
            fiscal_year=2024,
            fiscal_period="Q1",
            period_type="duration",
            fsn_end="2024-03-31",
        ),
        POINTS,
    )
    assert (
        isinstance(fb, cl.CellRow)
        and not fb.exact_dates
        and fb.fsn_end == date(2024, 3, 31)
    )


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if (
        _one(
            c,
            "select count(*) from information_schema.tables where (table_schema, table_name) in (('analytics','canonical_fact'), ('analytics','cell_blank_reason'))",
        )
        != 2
    ):
        c.close()
        pytest.skip("needs the migrated schema")
    yield c
    c.close()


def _seed(conn):
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0000000001', 'LOADER TEST') returning id",
    )
    conn.execute(
        "insert into core.unit (unit_name) values ('usd') on conflict do nothing"
    )
    uid = _one(conn, "select id from core.unit where unit_name = 'usd'")
    for name in ("capex_resolved", "cash_and_equivalents_resolved"):
        conn.execute(
            "insert into analytics.canonical_concept (name, statement, combination_mode) values (%s, 'cash_flow', 'first_match') on conflict (name) do nothing",
            (name,),
        )
    ccid = _one(
        conn, "select id from analytics.canonical_concept where name = 'capex_resolved'"
    )
    cash_id = _one(
        conn,
        "select id from analytics.canonical_concept where name = 'cash_and_equivalents_resolved'",
    )
    pid = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) values (%s, '2024-01-01', '2024-04-02', 'duration', 2024, 'Q1') returning id",
        (cid,),
    )
    fid = _one(
        conn,
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) values (%s, '0000000001-24-000001', '10-Q', '2024-05-01', '2024-04-02') returning id",
        (cid,),
    )
    conn.execute(
        "insert into core.concept (taxonomy, tag) values ('us-gaap', 'PaymentsToAcquirePropertyPlantAndEquipment') on conflict do nothing"
    )
    coid = _one(
        conn,
        "select id from core.concept where tag = 'PaymentsToAcquirePropertyPlantAndEquipment'",
    )
    raw_id = _one(
        conn,
        "insert into raw.sec_companyfacts (cik, source_url, sha256, storage_path, http_status, fetched_at) values ('0000000001', 'test://x', 'abc', 'test/x', 200, now()) returning id",
    )
    fact = _one(
        conn,
        "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_derived, is_authoritative, raw_object_id) values (%s, %s, %s, %s, %s, 100, false, true, %s) returning id",
        (cid, coid, uid, pid, fid, raw_id),
    )
    # a stale old value the reload must remove
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, 999, '{}')",
        (cid, cash_id, pid),
    )
    conn.commit()
    return cid, pid, fact, ccid, cash_id


def _write(tmp_path, rows):
    p = tmp_path / "cells.jsonl.gz"
    p.write_bytes(gzip.compress("\n".join(json.dumps(r) for r in rows).encode()))
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "family": "capex_da_cash_debt",
                "rule_id": "slot.capex@1",
                "data_points": ["capex_resolved", "cash_and_equivalents_resolved"],
            }
        )
    )
    return p


@pytest.mark.integration
def test_plan_writes_nothing_apply_writes_and_reload_is_idempotent(conn, tmp_path):
    cid, pid, fact, ccid, cash_id = _seed(conn)
    rows = [
        # fiscal binding: FSN month-end 03-31 binds to the real period ending 04-02; fact resolved by accession+tag
        _row(
            company_id=cid,
            period_start=None,
            period_end=None,
            fiscal_year=2024,
            fiscal_period="Q1",
            period_type="duration",
            fsn_end="2024-03-31",
        ),
        # instant blank with a reason (new period, exact dates -> created)
        _row(
            company_id=cid,
            data_point_name="cash_and_equivalents_resolved",
            period_grain="I",
            period_type="instant",
            period_start="2024-04-02",
            period_end="2024-04-02",
            state="not_presented",
            value=None,
            unit=None,
            accession=None,
            tag=None,
            reason_code="line_not_presented_in_filing",
            reason_text="not on the balance sheet",
            rule_id="slot.cash_and_equivalents@1",
            evidence_level="DATA-INFERRED",
        ),
        # a filed value that resolves to no fact and has no FSN set: rejected, listed
        _row(
            company_id=cid,
            period_start="2023-10-01",
            period_end="2023-12-31",
            period_grain="Q",
            fiscal_year=2023,
            fiscal_period="Q4",
            tag="NoSuchTag",
        ),
    ]
    path = _write(tmp_path, rows)
    plan = cl.load(conn, "capex_da_cash_debt", [path], apply=False)
    assert (
        plan.mode == "dry_run"
        and plan.valued_written == 1
        and plan.reasons_written == 1
    )
    assert plan.rejected == {"data_point_has_no_valued_cells": 1}
    assert (
        plan.lineage_defects == 1
    )  # the NoSuchTag value is kept as an explained blank
    assert (
        _one(
            conn,
            "select value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s",
            (cid, cash_id),
        )
        == 999
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.cell_blank_reason where company_id = %s",
            (cid,),
        )
        == 0
    )
    assert (
        _one(conn, "select count(*) from core.period where company_id = %s", (cid,))
        == 1
    )  # plan mode: both created periods rolled back
    for _ in range(2):
        rep = cl.load(conn, "capex_da_cash_debt", [path], apply=True)
        assert (
            rep.valued_written == 1
            and rep.reasons_written == 1
            and rep.deleted == (0 if _ == 0 else 1)
        )
        got = conn.execute(
            "select canonical_concept_id, period_id, value, source_fact_ids from analytics.canonical_fact where company_id = %s order by 1",
            (cid,),
        ).fetchall()
        # capex bound to the real 04-02 period with the resolved fact; cash untouched by the guard
        assert sorted(got) == sorted(
            [(ccid, pid, Decimal("100"), [fact]), (cash_id, pid, Decimal("999"), [])]
        )
        assert (
            _one(
                conn,
                "select count(*) from analytics.cell_blank_reason where company_id = %s and run_id = %s::uuid and reason_code = 'line_not_presented_in_filing'",
                (cid, rep.run_id),
            )
            == 0
        )
        assert (
            _one(
                conn,
                "select mode from analytics.rule_run where run_id = %s::uuid",
                (rep.run_id,),
            )
            == "apply"
        )


@pytest.mark.unit
def test_defect_overrides_turn_named_cells_into_period_defects():
    c = cl.parse_row(1, _row(state="derived", derivation={"formula": "x"}), POINTS)
    assert isinstance(c, cl.CellRow)
    n = cl.apply_defect_overrides(
        [c],
        [
            {
                "company_id": 1,
                "data_point_name": "capex_resolved",
                "period_grain": "Q",
                "period_start": "2024-01-01",
                "period_end": "2024-03-31",
                "why": ["inputs_filed_2plus_years_apart"],
                "input_accessions": ["a", "b"],
            }
        ],
        "mixed_vintage_inputs",
        "cells.x_override@1",
    )
    assert (
        n == 1
        and c.state == "defect"
        and c.value is None
        and c.reason_code == "mixed_vintage_inputs"
    )
    assert (
        c.defect_class == "period"
        and c.owner == "period_engineer"
        and "a, b" in c.reason_text
    )
    cl.to_reason(c)  # passes the contract
