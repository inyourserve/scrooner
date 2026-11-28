"""Exceptions queue (0135, PIPELINE.md M5): loader sources, idempotency, close constraint, reopen, report.

Pure tests build the sources in a tmp tree; DB tests apply the migration as written to an isolated Postgres clone
(CI: postgres:16) and drive the loader/close/report functions and the CLI the way a human runs them."""

import csv
import subprocess
import sys
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.certification import exception_queue as eq

ROOT = Path(__file__).resolve().parents[3]
SQL = next(iter((ROOT / "pipeline" / "db").glob("*/0135_*.sql"))).read_text()

COV_HEAD = "rank,ticker,company_id,data_point,fiscal_year,period_end,class,reason_code,reason,shown_value,proof_verdict,verdict,accession,r_page,locator_source,evidence,tag,value_source,docmap_status,parts,display,hide_class,stated_zero,text_stated\n"


def _cov(display, cls, code, dp="revenue", fy="2020", ticker="AAA", cid="7", val=""):
    return f"1,{ticker},{cid},{dp},{fy},{fy}-12-31,{cls},{code},,{val},,,0001-20-1,R4.htm,,,,,,,{display},,,\n"


def _tree(tmp_path, cov_rows, registry=None, reads=None, drill=None, status=None, failures=None):
    def w(rel, text):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    w(eq.COVERAGE, COV_HEAD + "".join(cov_rows))
    w(eq.REGISTRY, registry or "ticker,date,verdict,coverage_sha256,seed,n,errors,upper_bound_95,approver\n")
    w(eq.STATUS, status or "proposal_file,rule_id,status,backtest_delta,date,note\n")
    w(eq.DRILL, drill or "rule_id,version,namespace,data_point,scope,era,kind,when,then,precedence,evidence,author,date,note,proposed_by,finding\n")
    (tmp_path / eq.READS).mkdir(parents=True, exist_ok=True)
    for name, text in (reads or {}).items():
        w(f"{eq.READS}/{name}", text)
    (tmp_path / eq.FAILURES).mkdir(parents=True, exist_ok=True)
    for name, text in (failures or {}).items():
        w(f"{eq.FAILURES}/{name}", text)
    return tmp_path


def test_sources_map_to_kinds_families_owners_and_keys(tmp_path):
    reg = (
        "ticker,date,verdict,coverage_sha256,seed,n,errors,upper_bound_95,approver\n"
        "QQQ,2026-11-01,FAIL,aaa,s1,32,0,0.089368,r\n"
        "XYZ,2026-11-01,FAIL,zzz,s0,32,0,0.089368,r\n"
        "XYZ,2026-11-05,PASS,bbb,s2,199,0,0.0149,r\n"  # a later PASS: no exception
        "WWW,2026-11-02,FAIL,ccc,s3,32,2,0.2,r\n"
    )
    reads = {
        "AAA-0123456789ab.csv": "data_point,fiscal_year,verdict,reader,evidence\nrevenue,2020,MATCH,x,e\ncapex,2021,NEEDS_READ,x,note fact\nsbc,2021,MISMATCH,x,e2\n",
        "AAA-0123456789ab-audit.csv": "data_point,fiscal_year,verdict,reader,evidence\nfoo,2020,NEEDS_READ,x,e\n",
    }
    drill = (
        "rule_id,version,namespace,data_point,scope,era,kind,when,then,precedence,evidence,author,date,note,proposed_by,finding\n"
        "drill.ap.1,,drill,ap,all,,proposal_open,,,,drills:f,a,d,rule_gap|proof_disagree element=AccountsPayableCurrent companies=2 cells=8 days=1,a,f\n"
        "drill.ap.2,,drill,ap,all,,proposal_open,,,,drills:f,a,d,rule_gap|x element=E cells=2,a,f\n"
    )
    status = "proposal_file,rule_id,status,backtest_delta,date,note\nf,drill.ap.1,open,,d,\nf,drill.ap.2,accepted v1,,d,\n"
    fail = {"2026-11-22-run1.md": "# Resolver data refresh refused\n\n- line_map tests failed\n\nScope: BMY, LLY\n\nCompanies whose rows would change: BMY, LLY; values that would change: 10.\n"}
    cov = [
        _cov("OPEN", "UNCHECKED", "no_proof_row"),
        _cov("OPEN", "DISAGREE", "identity_break", dp="cogs", val="1500.50"),
        _cov("SHOWN_VALUE", "PROVEN", "", dp="ok"),
        _cov("HIDDEN_ROW", "REASON", "structural_not_presented", dp="hid"),
    ]
    rows = eq.build(_tree(tmp_path, cov, reg, reads, drill, status, fail))
    by = {r.idempotency_key: r for r in rows}
    assert len(rows) == len(by) == 8
    o = by["OPEN|7|revenue|2020|2020-12-31"]
    assert (o.kind, o.owner_lane, o.root_cause_family, o.ticker, o.company_id) == ("OPEN", "resolver", "UNCHECKED:no_proof_row", "AAA", 7)
    d = by["DISAGREE|7|cogs|2020|2020-12-31"]
    assert (d.owner_lane, d.root_cause_family) == ("proof", "identity_break") and "shown_value=1500.50" in d.detail
    s = by["SAMPLE_FAIL|QQQ|aaa|unrecorded"]
    assert (s.owner_lane, s.root_cause_family, s.judge_version, s.source_sha) == ("verifier", "bound_above_1.5pct", "unrecorded", "aaa")
    assert by["SAMPLE_FAIL|WWW|ccc|unrecorded"].root_cause_family == "sampled_errors"
    assert not any(k.startswith("SAMPLE_FAIL|XYZ") for k in by)
    nr = by["NEEDS_READ|AAA|0123456789ab|unrecorded|capex|2021"]
    assert nr.owner_lane == "approver" and nr.judge_version == "unrecorded"
    assert by["SAMPLE_FAIL|AAA|0123456789ab|unrecorded|sbc|2021"].root_cause_family == "read_mismatch"
    dm = by["DRILL_MISS|drill.ap.1"]
    assert (dm.cells_affected, dm.owner_lane, dm.root_cause_family) == (8, "tag_expert", "rule_gap|proof_disagree:AccountsPayableCurrent")
    assert "DRILL_MISS|drill.ap.2" not in by  # accepted
    dl = by["DEAD_LETTER|refresh|2026-11-22-run1.md"]
    assert (dl.cells_affected, dl.ticker, dl.owner_lane) == (10, "BMY", "data_engineer")
    assert "refresh_refused:line_map tests failed" == dl.root_cause_family
    text = eq.format_counts(rows)
    assert "kind OPEN: 1" in text and "DISAGREE | identity_break | 1 | 1" in text


def test_extra_csv_carries_census_fail_and_rejects_bad_rows(tmp_path):
    p = tmp_path / "x.csv"
    head = ",".join(eq.COLUMNS)
    good = {c: "" for c in eq.COLUMNS}
    good.update(idempotency_key="CENSUS_FAIL|AAA|sha|j1|badge", kind="CENSUS_FAIL", cell_key="AAA:sha:j1:badge",
               root_cause_family="badge", owner_lane="resolver", ticker="AAA", source_sha="sha", judge_version="j1", cells_affected="4")
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=eq.COLUMNS)
        w.writeheader()
        w.writerow(good)
    (r,) = eq.extra_rows(p)
    assert (r.kind, r.cells_affected, r.company_id) == ("CENSUS_FAIL", 4, None)
    p.write_text(head + "\n" + ",".join(["k", "BOGUS", "c", "f", "resolver"] + [""] * (len(eq.COLUMNS) - 5)) + "\n")
    with pytest.raises(ValueError):
        eq.extra_rows(p)


@pytest.fixture
def db(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists ops cascade")
        c.execute(SQL)
        c.commit()
    with psycopg.connect(isolated_database_url) as c:
        yield c


def _row(**kw):
    base = dict(idempotency_key="OPEN|1|a|2020|2020-12-31", kind="OPEN", cell_key="a|2020|2020-12-31",
                root_cause_family="UNCHECKED:x", owner_lane="resolver", ticker="AAA", company_id=1)
    base.update(kw)
    return eq.Row(**base)


def _count(c, where="true"):
    return c.execute(f"select count(*) from ops.exception_queue where {where}").fetchone()[0]


def test_load_is_idempotent_and_dry_run_writes_nothing(db):
    rows = [_row(), _row(idempotency_key="DISAGREE|1|b|2020|2020-12-31", kind="DISAGREE", cell_key="b", owner_lane="proof")]
    assert eq.load(db, rows, apply=False) == {"rows": 2, "new": 2, "existing": 0}
    assert _count(db) == 0
    assert eq.load(db, rows, apply=True)["new"] == 2
    assert eq.load(db, rows, apply=True) == {"rows": 2, "new": 0, "existing": 2}
    assert _count(db) == 2
    # a reload updates the evidence in place, same row
    eq.load(db, [_row(source_sha="new", cells_affected=3)], apply=True)
    assert db.execute("select source_sha, cells_affected from ops.exception_queue where kind='OPEN'").fetchone() == ("new", 3)


def test_batches_more_than_one_chunk(db):
    rows = [_row(idempotency_key=f"OPEN|1|c{i}", cell_key=f"c{i}") for i in range(eq.CHUNK + 5)]
    eq.load(db, rows, apply=True)
    assert _count(db) == eq.CHUNK + 5


def test_close_needs_rule_and_test_or_evidenced_hide(db):
    eq.load(db, [_row()], apply=True)
    key = "OPEN|1|a|2020|2020-12-31"
    for kw in ({}, {"rule_id": "r1"}, {"test_path": "t.py"}, {"hide_class": "h"}, {"evidence": "e"}):
        with pytest.raises(psycopg.errors.CheckViolation):
            eq.close_item(db, key, "me", **kw)
        db.rollback()
    assert _count(db, "closed_at is not null") == 0
    with pytest.raises(psycopg.errors.CheckViolation):  # blank strings are not a rule id
        db.execute("update ops.exception_queue set closed_at=now(), closed_by='x', close_rule_id=' ', close_test_path='t'")
    db.rollback()
    assert eq.close_item(db, key, "me", rule_id="rule.x.v1", test_path="pipeline/tests/t.py")
    assert not eq.close_item(db, key, "me", rule_id="rule.x.v1", test_path="p")  # already closed
    eq.load(db, [_row(idempotency_key="OPEN|1|b", cell_key="b")], apply=True)
    assert eq.close_item(db, "OPEN|1|b", "me", hide_class="not_presented", evidence="0001-20-1 R4.htm")


def test_table_rejects_bad_rows(db):
    def bad(**kw):
        with pytest.raises(psycopg.errors.CheckViolation):
            eq.load(db, [_row(**kw)], apply=True)
        db.rollback()

    bad(kind="BOGUS")
    bad(owner_lane="nobody")
    bad(cells_affected=0)
    bad(ticker=None, company_id=None)
    bad(kind="NEEDS_READ", owner_lane="resolver", judge_version="j", source_sha="s")
    bad(kind="SAMPLE_FAIL", owner_lane="verifier", judge_version=None, source_sha="s")  # stage 5 key needs judge + sha
    bad(kind="CENSUS_FAIL", owner_lane="resolver", judge_version="j", source_sha=None)
    eq.load(db, [_row(ticker=None, company_id=None, kind="DRILL_MISS", owner_lane="tag_expert", idempotency_key="DRILL_MISS|r")], apply=True)


def test_reopen_only_for_cell_kinds(db):
    cell, drill = _row(), _row(kind="DRILL_MISS", owner_lane="tag_expert", idempotency_key="DRILL_MISS|r", ticker=None, company_id=None)
    eq.load(db, [cell, drill], apply=True)
    for k in (cell.idempotency_key, drill.idempotency_key):
        assert eq.close_item(db, k, "me", rule_id="r", test_path="t")
    eq.load(db, [cell, drill], apply=True)
    got = dict(db.execute("select kind, closed_at is null from ops.exception_queue").fetchall())
    assert got == {"OPEN": True, "DRILL_MISS": False}
    assert db.execute("select reopened_count, close_rule_id from ops.exception_queue where kind='OPEN'").fetchone() == (1, None)


def test_report_flow_and_ranking(db):
    rows = [
        _row(idempotency_key="D|1", kind="DRILL_MISS", owner_lane="tag_expert", cell_key="1", ticker=None, root_cause_family="famA", cells_affected=9),
        _row(idempotency_key="O|1", cell_key="1", root_cause_family="famB"),
        _row(idempotency_key="O|2", cell_key="2", root_cause_family="famB", ticker="BBB", company_id=2),
        _row(idempotency_key="O|3", cell_key="3", root_cause_family="famC"),
    ]
    eq.load(db, rows, apply=True)
    eq.close_item(db, "O|3", "me", rule_id="r", test_path="t")
    db.execute("update ops.exception_queue set opened_at = now() - interval '2 days' where idempotency_key = 'O|1'")
    db.commit()
    text = eq.report(db, days=3, top=10)
    lines = text.splitlines()
    assert lines[0] == "open items: 3"
    assert "last 3 days: inflow 4, outflow 1 (INFLOW EXCEEDS OUTFLOW)" in text
    fam = lines[lines.index("family | kind | owner | items | cells_affected | companies") + 1 :]
    assert fam[0].startswith("famA | DRILL_MISS | tag_expert | 1 | 9") and fam[1].startswith("famB | OPEN | resolver | 2 | 2 | 2")
    assert not any(x.startswith("famC") for x in fam)


def test_cli_dry_run_and_apply_like_a_human(db, isolated_database_url, tmp_path):
    root = _tree(tmp_path, [_cov("OPEN", "BLANK", "era_unmapped"), _cov("OPEN", "DISAGREE", "identity_break", dp="x")])
    env = {"PYTHONPATH": str(ROOT / "pipeline" / "src"), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    base = [sys.executable, "-m", "scrooner_pipeline.certification.exception_queue", "load", "--root", str(root)]
    r = subprocess.run(base + ["--dry-run"], capture_output=True, text=True, env=env, check=True)
    assert "kind OPEN: 1" in r.stdout and "kind DISAGREE: 1" in r.stdout and "OPEN | BLANK:era_unmapped | 1 | 1" in r.stdout
    assert _count(db) == 0
    subprocess.run(base + ["--apply", "--db-url", isolated_database_url], capture_output=True, text=True, env=env, check=True)
    subprocess.run(base + ["--apply", "--db-url", isolated_database_url], capture_output=True, text=True, env=env, check=True)
    db.rollback()
    assert _count(db) == 2
    rep = subprocess.run([sys.executable, "-m", "scrooner_pipeline.certification.exception_queue", "report", "--db-url", isolated_database_url],
                         capture_output=True, text=True, env=env, check=True)
    assert "open items: 2" in rep.stdout
