"""B9 instance fallback: payload builder (pure) and a real-schema round trip."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import psycopg
import pytest
from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import instance_fallback as ib
from scrooner_pipeline.proof.fsn import FilingStructure, NumValue, PreLine

ACC = "0001403161-26-000104"


def _structure():
    # Visa-shaped Q3 FY2026 10-Q: period 2026-06-30, fiscal year from 2025-10-01
    s = FilingStructure(
        ACC, "0001403161", "10-Q", date(2026, 7, 29), date(2026, 6, 30), 2026, "Q3"
    )
    for stmt, tag in (
        ("IS", "Revenues"),
        ("IS", "NetIncomeLoss"),
        ("IS", "EarningsPerShareDiluted"),
        ("BS", "Assets"),
        ("CF", "NetCashProvidedByUsedInOperatingActivities"),
    ):
        s.pre.append(PreLine(2, 1, stmt, tag, "us-gaap/2025", tag, False))
    d = date(2026, 6, 30)
    rows = [
        ("Revenues", d, 1, "USD", "10000000000", "us-gaap/2025"),
        ("Revenues", d, 3, "USD", "29000000000", "us-gaap/2025"),
        (
            "Revenues",
            date(2025, 6, 30),
            1,
            "USD",
            "9000000000",
            "us-gaap/2025",
        ),  # comparative: skipped
        ("NetIncomeLoss", d, 1, "USD", "5000000000", "us-gaap/2025"),
        ("EarningsPerShareDiluted", d, 1, "USD", "2.50", "us-gaap/2025"),
        ("Assets", d, 0, "USD", "95000000000", "us-gaap/2025"),
        (
            "NetCashProvidedByUsedInOperatingActivities",
            d,
            3,
            "USD",
            "15000000000",
            "us-gaap/2025",
        ),
        (
            "NetCashProvidedByUsedInOperatingActivities",
            d,
            1,
            "USD",
            "5000000000",
            "us-gaap/2025",
        ),  # 3-month CF: note, skipped
        (
            "v_CustomThing",
            d,
            1,
            "USD",
            "1",
            "0001403161-26-000104",
        ),  # custom taxonomy: skipped
    ]
    for tag, dd, q, uom, val, ver in rows:
        s.num[(tag, dd, q)].append(NumValue(tag, ver, dd, q, uom, Decimal(val), -6))
    return s


def _filing():
    return ib.MissingFiling(
        5718,
        "0001403161",
        ACC,
        "10-Q",
        date(2026, 7, 29),
        date(2026, 6, 30),
        date(2025, 10, 1),
        date(2026, 3, 31),
    )


@pytest.mark.unit
def test_payload_has_only_current_face_columns_with_the_right_spans_and_units():
    plan = ib.payload_from_structure(_filing(), _structure())
    entries = {(e["tag"], e["start"], e["end"]): e for e in plan.entries}
    assert (
        "Revenues",
        date(2026, 4, 1),
        date(2026, 6, 30),
    ) in entries  # 3-month from the prior quarter end
    assert (
        "Revenues",
        date(2025, 10, 1),
        date(2026, 6, 30),
    ) in entries  # year-to-date from the FY start
    assert ("Assets", date(2026, 6, 30), date(2026, 6, 30)) in entries
    assert (
        "NetCashProvidedByUsedInOperatingActivities",
        date(2025, 10, 1),
        date(2026, 6, 30),
    ) in entries
    assert not any(
        e["tag"] == "NetCashProvidedByUsedInOperatingActivities"
        and e["start"] == date(2026, 4, 1)
        for e in plan.entries
    )
    assert (
        entries[("EarningsPerShareDiluted", date(2026, 4, 1), date(2026, 6, 30))]["uom"]
        == "USD/shares"
    )
    assert plan.skipped == {
        "comparative_column": 1,
        "cf_three_month_note": 1,
        "custom_taxonomy": 1,
    }
    assert sorted(plan.periods_to_create) == [
        (date(2025, 10, 1), date(2026, 6, 30), "duration", 2026, None),
        (date(2026, 4, 1), date(2026, 6, 30), "duration", 2026, "Q3"),
        (date(2026, 6, 30), date(2026, 6, 30), "instant", 2026, "Q3"),
    ]
    units = plan.payload["facts"]["us-gaap"]["EarningsPerShareDiluted"]["units"]
    assert (
        list(units) == ["USD/shares"]
        and units["USD/shares"][0]["accn"] == ACC
        and units["USD/shares"][0]["fp"] == "Q3"
    )


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if (
        _one(
            c,
            "select count(*) from information_schema.tables where (table_schema, table_name) in (('core','fact'), ('raw','sec_companyfacts'))",
        )
        != 2
    ):
        c.close()
        pytest.skip("needs the migrated schema")
    c.commit = lambda: None
    yield c
    c.rollback()
    c.close()


@pytest.mark.integration
def test_apply_writes_through_facts_py_with_lineage_and_rollback_removes_it(
    conn, tmp_path, monkeypatch
):
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values (%s, 'VISA TEST') returning id",
        ("0001403161",),
    )
    _one(
        conn,
        "insert into core.unit (unit_name) values ('usd') on conflict (unit_name) do update set unit_name = excluded.unit_name returning id",
    )
    _one(
        conn,
        "insert into core.unit (unit_name) values ('usd/shares') on conflict (unit_name) do update set unit_name = excluded.unit_name returning id",
    )
    conn.execute(
        "insert into core.filing (company_id, accession_number, form, filing_date, period_of_report) values (%s, %s, '10-Q', '2026-07-29', '2026-06-30')",
        (cid, ACC),
    )
    f = ib.MissingFiling(
        cid,
        "0001403161",
        ACC,
        "10-Q",
        date(2026, 7, 29),
        date(2026, 6, 30),
        date(2025, 10, 1),
        date(2026, 3, 31),
    )
    plan = ib.payload_from_structure(f, _structure())
    plan.fsn_set = "2026m07"
    with pytest.raises(RuntimeError):
        ib.apply_plan(conn, plan, tmp_path)
    monkeypatch.setenv(rf.ENV_ENABLED, ib.RULE_ID)
    out = ib.apply_plan(conn, plan, tmp_path)
    assert out["periods_created"] == 3 and out["written"] == 6
    raw_id = out["raw_object_id"]
    assert _one(
        conn, "select source_url from raw.sec_companyfacts where id = %s", (raw_id,)
    ).startswith("fsn://fsn-notes/2026m07/")
    assert (
        _one(conn, "select count(*) from core.fact where raw_object_id = %s", (raw_id,))
        == 6
    )
    assert (
        _one(
            conn,
            "select fiscal_period from core.period where company_id = %s and start_date = '2026-04-01'",
            (cid,),
        )
        == "Q3"
    )
    r = ib.rollback_run_dir(conn, tmp_path)
    assert r == {"filings": 1, "facts_deleted": 6, "periods_deleted": 3}
    assert (
        _one(conn, "select count(*) from core.fact where company_id = %s", (cid,)) == 0
    )


@pytest.mark.unit
def test_columns_ending_before_the_history_floor_are_skipped():
    # a FY2013 10-K: current columns end 2013-12-31, before HISTORY_FLOOR (2014-01-01)
    s = FilingStructure(
        "0000320193-14-000001",
        "0000320193",
        "10-K",
        date(2014, 2, 1),
        date(2013, 12, 31),
        2013,
        "FY",
    )
    s.pre.append(PreLine(1, 1, "IS", "Revenues", "us-gaap/2013", "Revenues", False))
    s.num[("Revenues", date(2013, 12, 31), 4)].append(
        NumValue(
            "Revenues", "us-gaap/2013", date(2013, 12, 31), 4, "USD", Decimal("5"), -6
        )
    )
    f = ib.MissingFiling(
        1,
        "0000320193",
        s.adsh,
        "10-K",
        date(2014, 2, 1),
        date(2013, 12, 31),
        date(2013, 1, 1),
        date(2013, 9, 30),
    )
    plan = ib.payload_from_structure(f, s)
    assert plan.entries == [] and plan.skipped == {"column_before_history_floor": 1}


@pytest.mark.unit
def test_filings_without_xbrl_are_classified_and_get_one_reason_per_statement_cell(
    tmp_path, monkeypatch
):
    f10q = ib.MissingFiling(
        7,
        "0001287750",
        "0001104659-14-034914",
        "10-Q",
        date(2014, 5, 6),
        date(2014, 3, 31),
        date(2014, 1, 1),
        date(2013, 12, 31),
    )
    f10k = ib.MissingFiling(
        7,
        "0001287750",
        "0001104659-15-012345",
        "10-K",
        date(2015, 2, 25),
        date(2014, 12, 31),
        date(2014, 1, 1),
        date(2014, 9, 30),
    )
    fx = ib.MissingFiling(
        8,
        "0000037996",
        "0000037996-16-000098",
        "10-K/A",
        date(2016, 3, 1),
        date(2015, 12, 31),
        date(2015, 1, 1),
        date(2015, 9, 30),
    )

    def fake_load_quarter(
        root, period, accs
    ):  # 2014q2 present (without these accessions), 2015q1/2016q1 absent locally
        if period == "2014q2":
            return {}
        raise FileNotFoundError(period)

    monkeypatch.setattr(ib, "load_quarter", fake_load_quarter)
    plans = ib.plan_filings(
        [f10q, f10k, fx],
        tmp_path,
        {f10q.accession: False, f10k.accession: False, fx.accession: True},
    )
    assert [dict(p.skipped) for p in plans] == [
        {"filing_has_no_xbrl": 1},
        {"fsn_set_missing": 1},  # 2015q1 set absent locally: not classified
        {"fsn_set_missing": 1},
    ]
    plans[2].skipped.clear()
    plans[2].edgar_isxbrl = True
    q = ib.no_xbrl_reasons(plans[0])
    assert len(q) == len(ib.NO_XBRL_DATA_POINTS) == 25
    keys = {
        (
            r.key.data_point_name,
            r.key.period_grain,
            r.key.period_start,
            r.key.period_end,
        )
        for r in q
    }
    assert ("revenue_sanity_resolved", "Q", date(2014, 1, 1), date(2014, 3, 31)) in keys
    assert ("total_assets_resolved", "I", date(2014, 3, 31), date(2014, 3, 31)) in keys
    assert {r.reason_code for r in q} == {"filing_has_no_xbrl"} and {
        r.rule_id for r in q
    } == {ib.RULE_ID}
    assert all(r.state == "defect" and r.defect_class == "ingestion" for r in q)
    k = ib.no_xbrl_reasons(plans[1])
    assert any(
        r.key.period_grain == "FY" and r.key.period_start == date(2014, 1, 1) for r in k
    )
    assert ib.no_xbrl_reasons(plans[2]) == []  # XBRL exists: not this reason
