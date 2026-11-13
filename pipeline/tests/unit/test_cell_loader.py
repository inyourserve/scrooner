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
        "grain_not_FY_Q_I_TP": _row(period_grain="TTM"),
        # CELL-FORMAT v1.2: TP is a 6/9-month or multi-year span; a quarter's dates are not one
        "tp_span_not_ytd": _row(period_grain="TP"),
        "tp_qtrs_disagree_with_dates": _row(
            period_grain="TP",
            period_start="2024-01-01",
            period_end="2024-06-30",
            qtrs=3,
        ),
        "no_period_key": _row(
            period_grain="TP", period_start=None, period_end=None, fsn_end="2024-06-30"
        ),
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


@pytest.mark.integration
def test_fsn_store_cell_keeps_source_value_ids_as_its_lineage(conn, tmp_path):
    # FSN-STORE-DESIGN §6: a cell from fsn_select carries fsn.value ids; with no core.fact for
    # its tag it still loads valued (not demoted to value_lineage_unresolved)
    cid, pid, _fact, ccid, _cash_id = _seed(conn)
    row = _row(
        company_id=cid,
        period_start=None,
        period_end=None,
        fiscal_year=2024,
        fiscal_period="Q1",
        period_type="duration",
        fsn_end="2024-03-31",
        tag="NoSuchTag",
        source_value_ids=[7001, 7002],
    )
    rep = cl.load(conn, "capex_da_cash_debt", [_write(tmp_path, [row])], apply=True)
    assert rep.valued_written == 1 and rep.lineage_defects == 0
    got = conn.execute(
        "select value, source_fact_ids, source_value_ids from analytics.canonical_fact "
        "where company_id = %s and canonical_concept_id = %s and period_id = %s",
        (cid, ccid, pid),
    ).fetchone()
    assert got == (Decimal("100"), [], [7001, 7002])


class _Backends:
    """A connection whose client-backend count follows a script."""

    def __init__(self, counts):
        self.counts = list(counts)

    def execute(self, sql, *a):
        n = self.counts.pop(0)
        return type("R", (), {"fetchone": lambda self: (n,)})()

    def commit(self):
        pass


@pytest.mark.unit
def test_headroom_waits_while_backends_exceed_the_budget_then_fails_closed(monkeypatch):
    slept = []
    assert cl.wait_for_headroom(_Backends([64, 61, 60]), 60, slept.append) == 2
    assert slept == [cl.HEADROOM_SLEEP_S] * 2
    assert cl.wait_for_headroom(_Backends([10]), 60, slept.append) == 0
    monkeypatch.setattr(cl, "HEADROOM_MAX_WAITS", 3)
    with pytest.raises(RuntimeError):
        cl.wait_for_headroom(_Backends([99] * 5), 60, lambda s: None)


def _before_image(conn, cid, out):
    out.mkdir()
    for table, fname, _ in cl.BEFORE_IMAGE_TABLES:
        with (
            gzip.open(out / fname, "wb") as fh,
            conn.cursor().copy(
                f"copy (select * from {table} where company_id = %s order by 1) to stdout with csv header",
                (cid,),
            ) as cp,
        ):
            for chunk in cp:
                fh.write(bytes(chunk))
    conn.commit()


@pytest.mark.integration
def test_restore_puts_the_before_image_back_for_the_written_data_points(conn, tmp_path):
    cid, pid, fact, ccid, cash_id = _seed(conn)
    snap = "select canonical_concept_id, period_id, value, id from analytics.canonical_fact where company_id = %s order by 1"
    before = conn.execute(snap, (cid,)).fetchall()
    _before_image(conn, cid, tmp_path / "before")
    path = _write(
        tmp_path,
        [
            _row(
                company_id=cid,
                period_start=None,
                period_end=None,
                fiscal_year=2024,
                fiscal_period="Q1",
                period_type="duration",
                fsn_end="2024-03-31",
            ),
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
        ],
    )
    cl.load(conn, "capex_da_cash_debt", [path], apply=True, protect=True)
    after_load = conn.execute(snap, (cid,)).fetchall()
    assert after_load != before
    points = ["capex_resolved", "cash_and_equivalents_resolved"]
    plan = cl.restore(conn, tmp_path / "before", [cid], points, apply=False)
    assert plan["mode"] == "dry_run"
    assert conn.execute(snap, (cid,)).fetchall() == after_load
    rep = cl.restore(conn, tmp_path / "before", [cid], points, apply=True)
    assert rep["companies"][cid]["analytics.canonical_fact.restored"] == len(before)
    assert conn.execute(snap, (cid,)).fetchall() == before
    # the write's protection is gone with it: the restored keys refresh as before the write
    assert (
        _one(
            conn,
            "select count(*) from analytics.slot_protected_cell where company_id = %s",
            (cid,),
        )
        == 0
    )
    assert (
        _one(
            conn,
            "select count(*) from analytics.cell_blank_reason where company_id = %s",
            (cid,),
        )
        == 0
    )


@pytest.mark.integration
def test_protected_write_survives_a_non_slot_writer_update_which_is_logged(
    conn, tmp_path
):
    cid, pid, fact, ccid, cash_id = _seed(conn)
    path = _write(
        tmp_path,
        [
            _row(
                company_id=cid,
                period_start=None,
                period_end=None,
                fiscal_year=2024,
                fiscal_period="Q1",
                period_type="duration",
                fsn_end="2024-03-31",
            ),
            # a reasoned blank: protected with value null (0115)
            _row(
                company_id=cid,
                data_point_name="capex_resolved",
                period_grain="Q",
                period_start="2023-10-01",
                period_end="2023-12-31",
                fiscal_year=2023,
                fiscal_period="Q4",
                state="not_presented",
                value=None,
                unit=None,
                accession=None,
                tag=None,
                reason_code="line_not_presented_in_filing",
                reason_text="not in the cash flow statement",
                rule_id="slot.capex@1",
                evidence_level="DATA-INFERRED",
            ),
        ],
    )
    rep = cl.load(conn, "capex_da_cash_debt", [path], apply=True, protect=True)
    assert rep.protected == 2
    got = conn.execute(
        "select p.end_date, s.value, s.run_id from analytics.slot_protected_cell s join core.period p on p.id = s.period_id where s.company_id = %s and s.canonical_concept_id = %s order by 1",
        (cid, ccid),
    ).fetchall()
    assert got == [
        (date(2023, 12, 31), None, rep.run_id),
        (date(2024, 4, 2), Decimal("100"), rep.run_id),
    ]
    # the nightly cannot insert an old value under the protected blank
    blank_pid = _one(
        conn,
        "select id from core.period where company_id = %s and end_date = '2023-12-31'",
        (cid,),
    )
    conn.execute(
        "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s, %s, %s, 7, '{}')",
        (cid, ccid, blank_pid),
    )
    conn.commit()
    assert (
        _one(
            conn,
            "select count(*) from analytics.canonical_fact where company_id = %s and period_id = %s",
            (cid, blank_pid),
        )
        == 0
    )
    # the nightly mapper is not the slot writer: its update is skipped and logged
    conn.execute(
        "update analytics.canonical_fact set value = 555 where company_id = %s and canonical_concept_id = %s",
        (cid, ccid),
    )
    conn.commit()
    assert (
        _one(
            conn,
            "select value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s",
            (cid, ccid),
        )
        == 100
    )
    assert conn.execute(
        "select operation, attempted_value from analytics.slot_protected_write_skipped where company_id = %s and canonical_concept_id = %s order by id",
        (cid, ccid),
    ).fetchall() == [("INSERT", Decimal("7")), ("UPDATE", Decimal("555"))]
    # an unprotected family key of the same company still refreshes (cash was not written here)
    conn.execute(
        "update analytics.canonical_fact set value = 1000 where company_id = %s and canonical_concept_id = %s",
        (cid, cash_id),
    )
    conn.commit()
    assert (
        _one(
            conn,
            "select value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s",
            (cid, cash_id),
        )
        == 1000
    )


@pytest.mark.integration
def test_a_blank_bound_by_fiscal_label_is_stored_on_its_true_period(conn, tmp_path):
    # MDT 2026-11-09: every Q reason was stored as (fsn_end, fsn_end), so none sat on its quarter (R3)
    cid, pid, fact, ccid, cash_id = _seed(conn)
    path = _write(
        tmp_path,
        [
            _row(
                company_id=cid,
                period_start=None,
                period_end=None,
                fiscal_year=2024,
                fiscal_period="Q1",
                period_type="duration",
                fsn_end="2024-03-31",
                state="not_presented",
                value=None,
                unit=None,
                accession=None,
                tag=None,
                reason_code="not_filed_separately",
                reason_text="no separate Q1 column",
                evidence_level="DATA-INFERRED",
            ),
            # a valued key so the family is loaded (a family with no valued cell is rejected)
            _row(
                company_id=cid,
                period_start="2023-10-01",
                period_end="2023-12-31",
                fiscal_year=2023,
                fiscal_period="Q4",
            ),
        ],
    )
    cl.load(conn, "capex_da_cash_debt", [path], apply=True)
    got = conn.execute(
        "select period_grain, period_start, period_end from analytics.cell_blank_reason where company_id = %s and reason_code = 'not_filed_separately'",
        (cid,),
    ).fetchall()
    assert got == [("Q", date(2024, 1, 1), date(2024, 4, 2))]
    assert (
        _one(
            conn,
            "select count(*) from analytics.cell_blank_reason where company_id = %s and period_grain <> 'I' and period_start = period_end",
            (cid,),
        )
        == 0
    )


# --- CELL-FORMAT v1.2: grain TP (printed 6/9-month year-to-date spans) ------------------------------------------


def _tp_row(cid=1, **over):
    """A TP row the way fsn_store.select.to_row writes it: no fiscal period, the FSN end and the column length."""
    base = dict(
        company_id=cid,
        period_grain="TP",
        period_start=None,
        period_end=None,
        fiscal_year=2024,
        fiscal_period=None,
        period_type="duration",
        fsn_end="2024-06-30",
        qtrs=2,
    )
    base.update(over)
    return _row(**base)


class _Periods:
    """A connection whose cursor answers bind_periods' one read with fixed core.period rows."""

    def __init__(self, rows):
        self.rows = rows

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, *_a):
        return None

    def fetchall(self):
        return self.rows


@pytest.mark.unit
def test_a_tp_row_binds_by_end_and_duration_class_never_by_a_quarter_label():
    periods = [
        (11, date(2024, 1, 1), date(2024, 3, 30), "duration", 2024, "Q1"),
        (12, date(2024, 3, 31), date(2024, 6, 29), "duration", 2024, "Q2"),
        (
            13,
            date(2024, 1, 1),
            date(2024, 6, 29),
            "duration",
            None,
            None,
        ),  # 6-month YTD
        (
            14,
            date(2024, 1, 1),
            date(2024, 9, 28),
            "duration",
            None,
            None,
        ),  # 9-month YTD
        (15, date(2023, 12, 31), date(2024, 12, 28), "duration", 2024, "FY"),
    ]
    rows = [
        cl.parse_row(1, _tp_row(), POINTS),
        cl.parse_row(2, _tp_row(fsn_end="2024-09-30", qtrs=3), POINTS),
        # a TP row that carries a quarter label anyway is still bound by its class, not by the label
        cl.parse_row(
            3,
            _tp_row(data_point_name="revenue_sanity_resolved", fiscal_period="Q2"),
            POINTS,
        ),
        cl.parse_row(
            4,
            _tp_row(
                period_start="2024-01-01",
                period_end="2024-09-28",
                qtrs=None,
                fsn_end=None,
            ),
            POINTS,
        ),
    ]
    assert all(isinstance(r, cl.CellRow) for r in rows), rows
    bound, bad, created = cl.bind_periods(_Periods(periods), 1, rows, create=False)
    assert bad == [] and created == 0
    assert [r.period_id for r in bound] == [13, 14, 13, 14]
    assert (bound[0].key.period_start, bound[0].key.period_end) == (
        date(2024, 1, 1),
        date(2024, 6, 29),
    )
    # two 6-month periods at the same nearest end: ambiguous, listed, never guessed
    twin = periods + [
        (16, date(2023, 12, 31), date(2024, 6, 29), "duration", None, None)
    ]
    bound, bad, _ = cl.bind_periods(
        _Periods(twin), 1, [cl.parse_row(1, _tp_row(), POINTS)], create=False
    )
    assert bound == [] and [why for _r, why in bad] == ["tp_period_ambiguous"]
    # no YTD period and no exact dates: unresolvable (a period is created only from exact dates)
    bound, bad, _ = cl.bind_periods(
        _Periods(periods[:2]), 1, [cl.parse_row(1, _tp_row(), POINTS)], create=True
    )
    assert bound == [] and [why for _r, why in bad] == ["period_unresolvable"]
    # exact dates not stored yet and a quarter label on the row: never sent to the 3-month Q2 period by the label
    labelled = _tp_row(
        period_start="2024-01-01", period_end="2024-06-29", fiscal_period="Q2"
    )
    bound, bad, _ = cl.bind_periods(
        _Periods(periods[:2]), 1, [cl.parse_row(1, labelled, POINTS)], create=False
    )
    assert bound == [] and [why for _r, why in bad] == ["period_unresolvable"]


@pytest.mark.integration
def test_tp_cells_load_onto_the_existing_ytd_periods_by_exact_dates_and_end(
    conn, tmp_path
):
    """The loader accepts grain TP: a select row (FSN end + qtrs) binds to the company's existing 6/9-month period,
    an exact-dated TP blank binds by its dates or creates its period once (fiscal period null); no duplicate YTD
    period is made, a reload creates nothing, and the 3-month Q2 period is never taken."""
    cid, pid, fact, ccid, cash_id = _seed(conn)
    h1 = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type) values (%s, '2024-01-01', '2024-06-29', 'duration') returning id",
        (cid,),
    )
    q2 = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period) values (%s, '2024-04-03', '2024-06-29', 'duration', 2024, 'Q2') returning id",
        (cid,),
    )
    m9 = _one(
        conn,
        "insert into core.period (company_id, start_date, end_date, period_type) values (%s, '2024-01-01', '2024-09-28', 'duration') returning id",
        (cid,),
    )
    conn.commit()
    blank = dict(state="defect", value=None, unit=None, accession=None, tag=None, reason_code="hybrid_gap_unresolved",
                 reason_text="not printed", defect_class="unclassified", owner="triage", evidence_level="DATA-INFERRED")  # fmt: skip
    path = _write(
        tmp_path,
        [
            _tp_row(cid, source_fact_ids=[fact]),  # 6 months, valued
            _tp_row(cid, fsn_end="2024-09-30", qtrs=3, **blank),  # 9 months, blank
            _tp_row(
                cid,
                period_start="2021-10-01",
                period_end="2024-09-28",
                qtrs=12,
                fsn_end="2024-09-30",
                **blank,
            ),  # multi-year, exact dates  # fmt: skip
            _row(
                company_id=cid, period_start="2024-01-01", period_end="2024-04-02"
            ),  # Q1 by exact dates
        ],
    )
    periods_before = _one(
        conn, "select count(*) from core.period where company_id = %s", (cid,)
    )
    rep = cl.load(conn, "capex_da_cash_debt", [path], apply=True)
    # the manifest's cash point has no valued cell in this file (rejected as a whole, as always); no TP row is
    assert set(rep.rejected) <= {"data_point_has_no_valued_cells"}, rep.as_dict()
    assert rep.periods_created == 1  # the multi-year period only
    valued = conn.execute(
        "select period_id, value from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s order by period_id",
        (cid, ccid),
    ).fetchall()
    assert valued == [(pid, Decimal("100")), (h1, Decimal("100"))] and q2 not in [
        v[0] for v in valued
    ]
    reasons = conn.execute(
        "select data_point_name, period_grain, period_start, period_end from analytics.cell_blank_reason where company_id = %s order by period_end, period_start",
        (cid,),
    ).fetchall()
    assert reasons == [
        ("capex_resolved", "TP", date(2021, 10, 1), date(2024, 9, 28)),
        ("capex_resolved", "TP", date(2024, 1, 1), date(2024, 9, 28)),
    ]
    assert (
        _one(
            conn,
            "select fiscal_period from core.period where company_id = %s and start_date = '2021-10-01'",
            (cid,),
        )
        is None
    )
    assert (
        _one(
            conn,
            "select count(*) from core.period where company_id = %s and end_date = '2024-09-28' and start_date = '2024-01-01'",
            (cid,),
        )
        == 1
    )
    assert m9 is not None
    cl.load(
        conn, "capex_da_cash_debt", [path], apply=True
    )  # idempotent: no new period on a reload
    assert (
        _one(conn, "select count(*) from core.period where company_id = %s", (cid,))
        == periods_before + 1
    )
