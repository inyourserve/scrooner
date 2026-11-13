"""DQC checks (mapper/dqc_checks.py): CSV parsing, identity / sign / preference evaluation over served cells, and the
report-only versus hold behaviour of the tagmap-plan stage (DB part: CI Postgres 16)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper import company_tag_map_plan as plan
from scrooner_pipeline.mapper import dqc_checks as dqc
from tests.unit.test_company_tag_map_db import _one, _seed

D = Decimal
END = date(2018, 12, 31)


def _check(check_id="DQC4-01", on_fail="hold the cell (identity failure); NEVER derive a missing instant from it", ctype="equality"):
    return dqc.Check(check_id, "r", ctype, ("total_assets",), "c", on_fail, "s")


def _fact(value, pid=1):
    return ctm.Fact(D(value), 1, END, False, 1, "a")


def _ctx(served: dict[str, str], facts: dict[str, str]) -> dqc.Ctx:
    ctx = dqc.Ctx(7)
    for i, (dp, v) in enumerate(served.items()):
        cell = dqc.Cell(dp, 100 + i, 1, date(2018, 12, 31), END, "instant", D(v))
        ctx.cell_by_name[(dp, 1)] = cell
        ctx.by_dp.setdefault(dp, {}).setdefault(1, []).append(cell)
    for tag, v in facts.items():
        ctx.facts[tag] = {1: _fact(v)}
    return ctx


def test_shipped_csv_parses_and_every_row_is_implemented_or_unsupported_with_a_reason():
    checks = dqc.load_checks()
    assert len(checks) >= 40
    impl, unsupported = dqc.split_checks(checks)
    assert len(impl) + len(unsupported) == len(checks)
    assert {c.check_id for c in impl}.isdisjoint(unsupported)
    # nothing is silently unsupported: a stated reason for each
    assert "no evaluator registered" not in unsupported.values()
    # every DQC15 / SEC-NEG row is a sign check that is implemented
    assert all(c.check_id.startswith(("DQC15-", "SEC-NEG")) for c in impl if c.check_type == "non_negative")
    assert {c.check_id for c in checks if c.check_type == "non_negative"} <= {c.check_id for c in impl}


def test_load_checks_parses_columns_and_rejects_duplicate_ids(tmp_path: Path):
    head = "check_id,source_rule,check_type,data_points,condition,on_fail,source\n"
    f = tmp_path / "c.csv"
    f.write_text(head + 'A-1,r,equality,total_assets;current_assets,"x, y",hold the cell (z),u\n')
    (c,) = dqc.load_checks(f)
    assert c.data_points == ("total_assets", "current_assets") and c.hold and c.condition == "x, y"
    f.write_text(head + "A-1,r,equality,a,c,flag,u\nA-1,r,equality,a,c,flag,u\n")
    with pytest.raises(ValueError, match="duplicate"):
        dqc.load_checks(f)
    f.write_text(head + "A-2,r,equality,a,c,flag; hold the cell later,u\n")
    assert not dqc.load_checks(f)[0].hold  # only an on_fail STARTING with 'hold the cell' holds


def test_tolerance_is_half_a_rounding_unit_per_operand():
    assert dqc.tolerance([D("5")]) == D("0.5")
    assert dqc.tolerance([D("1234000"), D("2000000")]) == D("500") + D("500000")  # 10^3/2 + 10^6/2
    assert dqc.tolerance([D("5000000000000")]) == D(10) ** 9 / 2  # capped at 10^9


def test_identity_failure_is_a_hold_hit_and_a_rounding_difference_is_not():
    chk = _check()
    bad = dqc._eval_4_01(_ctx({"total_assets": "1234567000"}, {"LiabilitiesAndStockholdersEquity": "1334567000"}), chk)
    assert [(h.check_id, h.data_point, h.hold) for h in bad] == [("DQC4-01", "total_assets", True)]
    assert bad[0].values["diff"] == "-100000000" and bad[0].period_end == END
    ok = dqc._eval_4_01(_ctx({"total_assets": "1234567000"}, {"LiabilitiesAndStockholdersEquity": "1234567500"}), chk)
    assert ok == []  # 500 off: within half a unit of each operand (500 + 50)


def test_a_missing_operand_never_derives_or_hits():
    chk = _check("DQC4-02")
    # AssetsNoncurrent is not printed: the identity is not evaluated, nothing is derived from it
    ctx = _ctx({"total_assets": "1000000", "current_assets": "400000"}, {"AssetsCurrent": "400000"})
    assert dqc._eval_4_02(ctx, chk) == []
    # no served cell: nothing to hold even if the facts disagree
    ctx = _ctx({}, {"LiabilitiesAndStockholdersEquity": "5"})
    assert dqc._eval_4_01(ctx, _check()) == []


def test_identity_hit_names_every_served_data_point_it_lists():
    chk = _check("DQC4-02")
    ctx = _ctx({"total_assets": "1234567", "current_assets": "400007"}, {"AssetsCurrent": "400007", "AssetsNoncurrent": "100001"})
    assert sorted(h.data_point for h in dqc._eval_4_02(ctx, chk)) == ["current_assets", "total_assets"]


def test_sign_check_hits_only_negative_facts_behind_a_served_cell_and_flags_without_hold():
    chk = dqc.Check("DQC15-Goodwill", "r", "non_negative", ("(any using Goodwill)",), "c", "sign error: serve abs(value), flag filer_sign_error", "s")
    ctx = _ctx({"goodwill": "100"}, {})
    cell = ctx.cell_by_name[("goodwill", 1)]
    ctx.sources = [("goodwill", 1, "Goodwill", D("-100"), 9), ("goodwill", 1, "Goodwill", D("-100"), 9), ("goodwill", 1, "OtherTag", D("-1"), 10)]
    hits = dqc.evaluator(chk)(ctx, chk)
    assert len(hits) == 1 and hits[0].values["tag"] == "Goodwill" and not hits[0].hold and hits[0].canonical_concept_id == cell.canonical_concept_id
    ctx.sources = [("goodwill", 1, "Goodwill", D("100"), 9)]
    assert dqc.evaluator(chk)(ctx, chk) == []


def test_preference_and_share_checks():
    ctx = _ctx({"cash_paid_for_interest": "5", "shares_outstanding": "3000000"}, {"CommonStockSharesIssued": "2000000", "CommonStockSharesAuthorized": "1000000"})
    ctx.src_tags[("cash_paid_for_interest", 1)] = {"InterestPaid"}
    assert len(dqc._eval_65(ctx, _check("DQC65-01", "flag"))) == 1
    ctx.src_tags[("cash_paid_for_interest", 1)] = {"InterestPaidNet"}
    assert dqc._eval_65(ctx, _check("DQC65-01", "flag")) == []
    notes = sorted(h.values["note"] for h in dqc._eval_9_01(ctx, _check("DQC9-01", "flag")))
    assert notes == ["issued > authorized", "outstanding > issued"]


def test_cover_count_ratio_flags_a_thousand_fold_scale_error():
    ctx = _ctx({"shares_outstanding": "5000"}, {})
    ctx.facts["EntityCommonStockSharesOutstanding"] = {2: ctm.Fact(D("5000000"), 2, date(2019, 2, 1), False, 1, "a")}
    (h,) = dqc._eval_shr(ctx, _check("SEC-SHR-01", "flag"))
    assert h.values["ratio"] == "0.0010" and not h.hold


# --------------------------------------------------------------------------------------------------------------
# DB: served cells through check_company, and the plan stage (report-only vs hold)
# --------------------------------------------------------------------------------------------------------------
def _db_setup(conn):
    x = _seed(conn)
    co, per, fil, fact = x["company"]("0000002001", True)
    ta = _one(conn, "insert into analytics.canonical_concept (name, statement, combination_mode) values ('total_assets','balance_sheet','first_match') returning id")
    for t in ("Assets", "LiabilitiesAndStockholdersEquity"):
        x["tags"][t] = _one(conn, "insert into core.concept (taxonomy, tag) values ('us-gaap', %s) returning id", t)
    inst = _one(conn, "insert into core.period (company_id, start_date, end_date, period_type) values (%s,'2018-12-31','2018-12-31','instant') returning id", co)
    for tag, v in (("Assets", "1234567000"), ("LiabilitiesAndStockholdersEquity", "1334567000")):
        conn.execute(
            "insert into core.fact (company_id, concept_id, unit_id, period_id, filing_id, value, is_authoritative, raw_object_id) values (%s,%s,%s,%s,%s,%s,true,%s)",
            (co, x["tags"][tag], x["unit"], inst, fil["new"], D(v), x["raw"]),
        )
    conn.execute(
        "insert into analytics.company_tag_map (company_id, taxonomy, tag, stmt, decision, canonical_concept_id, era_from, decided_by, rule_id) values (%s,'us-gaap','Assets','BS','concept',%s,'2015-01-01','t','tm.r@1')",
        (co, ta),
    )
    conn.commit()
    return co, ta, inst


@pytest.mark.integration
def test_check_company_reads_served_cells_and_the_plan_reports_without_holding(isolated_database_url, tmp_path):
    checks = [c for c in dqc.load_checks() if c.check_id in ("DQC4-01", "DQC15-Assets")]
    with psycopg.connect(isolated_database_url) as conn:
        co, ta, inst = _db_setup(conn)
        conn.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s,%s,%s,%s,'{}')", (co, ta, inst, D("1234567000")))
        conn.commit()
        hits = dqc.check_company(conn, co, checks)
        assert [(h.check_id, h.data_point, h.hold) for h in hits] == [("DQC4-01", "total_assets", True)]
        out = tmp_path / "r.csv"
        dqc.write_report(hits, out)
        assert out.read_text().splitlines()[0].startswith("check_id,company_id,data_point,period_end,values,on_fail,hold")
        # plan, report only: the hit is reported, the value is served (plan rolls back anyway)
        rep = plan.run(conn, [co], {}, apply=True, dqc_checks=checks)
        assert "error" not in rep[co], rep[co]
        assert [h.check_id for h in rep[co]["dqc_hits"]] == ["DQC4-01"] and rep[co]["dqc_held"] == 0
        assert _one(conn, "select value from analytics.canonical_fact where company_id = %s", co) == D("1234567000")


@pytest.mark.integration
def test_plan_hold_flag_removes_the_cell_and_writes_a_visible_reason(isolated_database_url):
    checks = [c for c in dqc.load_checks() if c.check_id == "DQC4-01"]
    with psycopg.connect(isolated_database_url) as conn:
        co, ta, inst = _db_setup(conn)
        rep = plan.run(conn, [co], {}, apply=True, dqc_checks=checks, dqc_hold=True)
        assert "error" not in rep[co], rep[co]
        assert rep[co]["dqc_held"] == 1
        assert conn.execute("select count(*) from analytics.canonical_fact where company_id = %s and canonical_concept_id = %s", (co, ta)).fetchone()[0] == 0
        assert conn.execute(
            "select state, defect_class, owner, reason_code, rule_id from analytics.cell_blank_reason where company_id = %s and data_point_name = 'total_assets'", (co,)
        ).fetchall() == [("defect", "identity", "verifier", "dqc_dqc4_01", "dqc.checks@1")]
        # a value is never derived from the identity: no other cell appeared
        assert _one(conn, "select count(*) from analytics.canonical_fact where company_id = %s", co) == 0
        # the held key is protected with a null value, not with the old value
        assert conn.execute("select value from analytics.slot_protected_cell where company_id = %s", (co,)).fetchall() in ([(None,)], [])
