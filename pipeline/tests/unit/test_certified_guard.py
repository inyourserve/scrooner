"""certified-guard (pure + CLI exit code) and restore-before-image (DB-backed, CI: Postgres 16)."""

from __future__ import annotations

import csv
from decimal import Decimal

import psycopg
import pytest
from typer.testing import CliRunner

from scrooner_pipeline.jobs import map as map_job
from scrooner_pipeline.mapper import certified_guard as cg
from scrooner_pipeline.mapper import company_tag_map_plan as plan
from tests.unit.test_company_tag_map_db import _one, _seed

COLS = ["company_id", "data_point", "fiscal_year", "class", "reason_code", "reason",
        "shown_value", "proof_verdict", "verdict", "evidence"]


def _csv(path, rows):
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({"company_id": 7, "reason_code": "", "reason": "", "proof_verdict": "", "verdict": "", "evidence": "", **r})
    return path


def _row(dp, fy, cls, val):
    return {"data_point": dp, "fiscal_year": fy, "class": cls, "shown_value": val}


CERT = [_row("revenue", 2024, "PROVEN", "100"), _row("cash", 2024, "REASON", ""), _row("x", 2024, "BLANK", "")]


def _run(tmp_path, new_rows):
    cert = _csv(tmp_path / "cert.csv", CERT)
    new = _csv(tmp_path / "new.csv", new_rows)
    rep = tmp_path / "rep.csv"
    res = CliRunner().invoke(map_job.app, ["certified-guard", "--company-id", "7", "--certified-csv", str(cert), "--coverage-csv", str(new), "--report", str(rep)])
    return res, rep


@pytest.mark.unit
def test_guard_passes_when_certified_cells_hold_and_numeric_equal_value(tmp_path):
    res, rep = _run(tmp_path, [_row("revenue", 2024, "PROVEN", "100.0"), _row("cash", 2024, "REASON", ""), _row("x", 2024, "DISAGREE", "5"), _row("new_dp", 2024, "BLANK", "")])
    assert res.exit_code == 0, res.output
    assert not rep.exists()


@pytest.mark.unit
@pytest.mark.parametrize("new_rows,kind", [
    ([_row("revenue", 2024, "PROVEN", "101"), _row("cash", 2024, "REASON", "")], "value_changed"),
    ([dict(_row("revenue", 2024, "DISAGREE", "100"), reason_code="rc"), _row("cash", 2024, "REASON", "")], "class_left_ok"),
    ([_row("cash", 2024, "REASON", "")], "missing"),
])
def test_guard_fails_and_reports_cause(tmp_path, new_rows, kind):
    res, rep = _run(tmp_path, new_rows)
    assert res.exit_code == 1, res.output
    got = list(csv.DictReader(rep.open()))
    assert [(g["data_point"], g["regression"]) for g in got] == [("revenue", kind)]
    if kind == "class_left_ok":
        assert got[0]["reason_code"] == "rc" and got[0]["new_class"] == "DISAGREE"


@pytest.mark.unit
def test_guard_ignores_other_companies_rows(tmp_path):
    other = dict(_row("revenue", 2024, "PROVEN", "1"), company_id=8)
    res, _ = _run(tmp_path, [_row("revenue", 2024, "PROVEN", "100"), _row("cash", 2024, "REASON", ""), other])
    assert res.exit_code == 0


def _state(conn, co):
    out = {}
    for t, order in (("canonical_fact", "canonical_concept_id, period_id"), ("cell_blank_reason", "data_point_name, period_end"), ("slot_protected_cell", "canonical_concept_id, period_id")):
        out[t] = conn.execute(f"select * from analytics.{t} where company_id = %s order by {order}", (co,)).fetchall()
    return out


def _seed_state(conn):
    x = _seed(conn)
    co, per, _, _ = x["company"]("0000007001", True)
    co2, per2, _, _ = x["company"]("0000007002", True)
    run = _one(conn, "insert into analytics.rule_run (rule_id, rule_version, mode, flag_name, flag_state) values ('t.r@1',1,'apply','f','on') returning run_id")
    conn.execute("set local scrooner.slot_writer = 'on'")
    for c, p in ((co, per), (co2, per2)):
        conn.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids, rule_run_id) values (%s,%s,%s,%s,'{}',%s)", (c, x["rev"], p["in"], Decimal("110"), run))
        conn.execute("insert into analytics.cell_blank_reason (run_id, company_id, data_point_name, period_grain, period_start, period_end, state, rule_id, reason_code) values (%s,%s,'tm_opex','FY','2018-01-01','2018-12-31','not_presented','t.r@1','np')", (run, c))
        conn.execute("insert into analytics.slot_protected_cell (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256) values (%s,%s,%s,'t.r@1',110,'r','s')", (c, x["rev"], p["in"]))
    conn.commit()
    return x, co, co2, per, run


def _damage(conn, x, co, per):
    conn.execute("set local scrooner.writer = 'company_tag_map'")
    conn.execute("set local scrooner.slot_writer = 'on'")
    conn.execute("delete from analytics.cell_blank_reason where company_id = %s", (co,))
    conn.execute("delete from analytics.slot_protected_cell where company_id = %s", (co,))
    conn.execute("update analytics.canonical_fact set value = 999 where company_id = %s", (co,))
    conn.execute("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids) values (%s,%s,%s,5,'{}')", (co, x["opex"], per["out"]))
    conn.commit()


@pytest.mark.integration
def test_restore_puts_exact_rows_back_only_for_that_company_and_is_idempotent(isolated_database_url, tmp_path):
    with psycopg.connect(isolated_database_url) as conn:
        x, co, co2, per, run = _seed_state(conn)
        before, other_before = _state(conn, co), _state(conn, co2)
        plan.write_before_image(conn, [co, co2], tmp_path / "bi")  # the image also holds the other company
        _damage(conn, x, co, per)
        conn.execute("set local scrooner.slot_writer = 'on'")
        conn.execute("update analytics.canonical_fact set value = 5 where company_id = %s", (co2,))
        conn.commit()
        other_damaged = _state(conn, co2)
        assert _state(conn, co) != before
        rep = cg.restore_before_image(conn, co, tmp_path / "bi", apply=False)
        assert rep["mode"] == "dry_run" and _state(conn, co) != before  # dry run changes nothing
        rep = cg.restore_before_image(conn, co, tmp_path / "bi", apply=True)
        assert rep["counts"]["canonical_fact.restored"] == 1
        assert _state(conn, co) == before  # ids, values, run ids: exact
        assert _state(conn, co2) == other_damaged != other_before  # another company untouched
        cg.restore_before_image(conn, co, tmp_path / "bi", apply=True)
        assert _state(conn, co) == before  # idempotent
