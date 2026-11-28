"""Orchestrator (PIPELINE.md M4): event log, planner, sweep, worker, stage runner. DB tests run on Postgres 16
(SCROONER_TEST_DATABASE_URL; CI: postgres:16) over migrations 0135 and 0136 on a throwaway database copy."""

import json
import subprocess
from pathlib import Path

import psycopg
import pytest
from scrooner_pipeline.orchestrator import cohort, planner, producers, stages, store, versions, worker

DB = Path(__file__).parents[2] / "db"
SQL135 = (DB / "pending/0135_exception_queue.sql").read_text()
SQL136 = (DB / "pending/0136_pipeline_event_work_items.sql").read_text()


@pytest.fixture
def conn(isolated_database_url):
    with psycopg.connect(isolated_database_url) as c:
        c.execute("drop schema if exists ops cascade")
        c.execute(SQL135)
        c.execute(SQL136)
        c.commit()
    with psycopg.connect(isolated_database_url, autocommit=True) as c:
        yield c


def ev(conn, cik="1", cause="rule_version", **v):
    assert store.emit_event(conn, cik=cik, cause=cause, versions=v or {"rule": "r1"}, source="test") in (True, False)


def items(conn, where="true"):
    return conn.execute(f"select cik, from_stage, status, causes, dry_run from ops.work_item where {where} order by id").fetchall()


# ---- migration ---------------------------------------------------------------------------------------------------
def test_event_idempotent_and_star_scope(conn):
    assert store.emit_event(conn, cik="1", cause="rule_version", versions={"a": 1}, source="t") is True
    assert store.emit_event(conn, cik="1", cause="rule_version", versions={"a": 1}, source="t") is False
    with pytest.raises(psycopg.errors.CheckViolation):  # new_filing must name a company
        store.emit_event(conn, cik="*", cause="new_filing", versions={"a": 1}, source="t")
    with pytest.raises(ValueError):
        store.emit_event(conn, cik="1", cause="nope", versions={}, source="t")


def test_one_queued_and_one_running_per_company(conn):
    conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash) values ('1',3,'{}','{}',repeat('a',64))")
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash) values ('1',3,'{}','{}',repeat('b',64))")
    with pytest.raises(psycopg.errors.CheckViolation):  # running needs a lease
        conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, status) values ('2',3,'{}','{}',repeat('a',64),'running')")


# ---- planner -----------------------------------------------------------------------------------------------------
def test_duplicate_and_overlapping_events_collapse_to_one_item_with_earliest_stage(conn):
    ev(conn, "1", "rule_version", rule="a")
    ev(conn, "1", "rule_version", rule="a")  # duplicate: the event row is not repeated
    ev(conn, "1", "new_filing", accessions=["x"], from_stage=1)
    rep = planner.plan_events(conn)
    assert rep.events == 2 and rep.queued == 1 and rep.merged == 1
    (row,) = items(conn)
    assert row[1] == 1 and row[2] == "pending" and sorted(row[3]) == ["new_filing", "rule_version"]
    assert conn.execute("select count(*) from ops.work_item_event").fetchone()[0] == 2
    assert planner.plan_events(conn).events == 0  # planned events are not planned again


class Usage:
    def __init__(self, m):
        self.m = m

    def companies(self, rule_id):
        return self.m.get(rule_id)


def test_rule_event_targets_only_affected_companies_and_never_fans_out(conn):
    ev(conn, "*", "rule_version", rule="R1")
    ev(conn, "*", "rule_version", rule="R2")
    rep = planner.plan_events(conn, Usage({"R1": ["10", "20"], "R2": None}))
    assert items(conn) == [("10", 3, "pending", ["rule_version"], False), ("20", 3, "pending", ["rule_version"], False)]
    assert rep.unscoped == 1  # R2: the index cannot say, so nothing is queued for anyone
    assert conn.execute("select plan_outcome from ops.pipeline_event where versions->>'rule'='R2'").fetchone()[0] == "unscoped"


def test_cohort_leaves_other_events_unplanned(conn):
    ev(conn, "1", "rank_change", rank_set="1-2")
    ev(conn, "2", "rank_change", rank_set="1-2")
    planner.plan_events(conn, cohort={"1"})
    assert [r[0] for r in items(conn)] == ["1"]
    assert conn.execute("select count(*) from ops.pipeline_event where planned_at is null").fetchone()[0] == 1
    planner.plan_events(conn, cohort={"2"})
    assert [r[0] for r in items(conn)] == ["1", "2"]


def test_already_done_is_not_planned_again(conn):
    ev(conn, "1", "rule_version", rule="a")
    planner.plan_events(conn)
    conn.execute("update ops.work_item set status='done', finished_at=now()")
    store.emit_event(conn, cik="1", cause="rule_version", versions={"rule": "a", "n": 2}, source="t")
    assert planner.plan_events(conn).queued == 1  # different versions: new work
    conn.execute("update ops.work_item set status='done', finished_at=now() where status='pending'")


def test_sweep_plans_lagging_companies_once(conn):
    cur = {"1": {"d": "v2"}, "2": {"d": "v2"}, "3": {"d": "v2"}}
    for cik in ("2",):  # 2 is served at the current versions
        conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, status, finished_at) "
                     "values (%s,3,'{}','{}',repeat('c',64),'done',now())", (cik,))
        wid = conn.execute("select max(id) from ops.work_item").fetchone()[0]
        conn.execute("insert into ops.company_served_version (cik, versions, versions_hash, work_item_id) values (%s,%s,%s,%s)",
                     (cik, json.dumps(cur[cik]), store.versions_hash(cur[cik]), wid))
    conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, status, finished_at) "
                 "values ('3',3,'{}','{}',repeat('d',64),'dead',now())")
    wid3 = conn.execute("select max(id) from ops.work_item").fetchone()[0]
    conn.execute("insert into ops.work_dead_letter (work_item_id, cik, error_class, error, attempts) values (%s,'3','x','e',3)", (wid3,))
    rep = planner.sweep(conn, cur)
    assert rep.queued == 1
    assert [r[0] for r in items(conn, "status='pending'")] == ["1"]  # 2 is current, 3 waits for its dead letter owner
    assert planner.sweep(conn, cur).queued == 0  # idempotent
    conn.execute("update ops.work_dead_letter set resolved_at = now()")
    assert planner.sweep(conn, cur).queued == 1  # resolving the dead letter re-opens the company to the sweep


# ---- worker ------------------------------------------------------------------------------------------------------
class Fake:
    """Runner double: records the stage order; `plan` maps (stage, call number) -> exception to raise."""

    def __init__(self, plan=None):
        self.calls, self.plan, self.n = [], plan or {}, {}

    def run(self, stage, item):
        self.n[stage] = self.n.get(stage, 0) + 1
        self.calls.append((item.cik, stage))
        exc = self.plan.get((item.cik, stage, self.n[stage]))
        if exc:
            raise exc
        return worker.StageResult("done", {"s": stage})


def queue(conn, cik, from_stage=3, dry=False):
    conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, dry_run) "
                 "values (%s,%s,'{rule_version}','{}',%s,%s)", (cik, from_stage, store.versions_hash({"c": cik}), dry))


def loop(conn, runner, **kw):
    return worker.work_loop(conn, runner, backoff_base=0, idle_wait_s=0, wall_clock_s=30, log=lambda s: None,
                            served_versions=lambda cik: {"served": cik}, **kw)


def test_stages_run_in_order_and_certify_is_last(conn):
    queue(conn, "1", from_stage=1)
    queue(conn, "2", from_stage=3)
    r = Fake()
    assert loop(conn, r, shards=1, ingest_only=False)["done"] == 1  # item 1 still waits for stage 1: a shard leaves it
    assert [c for c in r.calls if c[0] == "2"] == [("2", 3), ("2", 4), ("2", 6), ("2", 5)]
    t = loop(conn, r, ingest_only=True)
    assert t["released"] == 1 and ("1", 1) in r.calls and ("1", 2) not in r.calls
    loop(conn, r)
    assert [c[1] for c in r.calls if c[0] == "1"] == [1, 2, 3, 4, 6, 5]
    assert conn.execute("select count(*) from ops.company_served_version").fetchone()[0] == 2


def test_resume_runs_only_unfinished_stages(conn):
    queue(conn, "1")
    r1 = Fake({("1", 6, 1): worker.Transient("pooler dropped")})
    loop(conn, r1, max_items=1)
    assert [c[1] for c in r1.calls] == [3, 4, 6]
    assert conn.execute("select status, attempts from ops.work_item").fetchone() == ("retry_wait", 1)
    r2 = Fake()
    assert loop(conn, r2)["done"] == 1
    assert [c[1] for c in r2.calls] == [6, 5]  # 3 and 4 were checkpointed and are not run again


def test_transient_retried_three_times_then_dead_lettered_with_queue_row(conn):
    queue(conn, "1")
    queue(conn, "2")
    fails = {("1", 3, n): worker.Transient("503 Service Unavailable") for n in (1, 2, 3)}
    r = Fake(fails)
    t = loop(conn, r)
    assert conn.execute("select status, attempts, error_class from ops.work_item where cik='1'").fetchone() == ("dead", 3, "transient")
    assert [c for c in r.calls if c[0] == "1"] == [("1", 3)] * 3  # tried exactly 3 times
    assert conn.execute("select status from ops.work_item where cik='2'").fetchone()[0] == "done"  # never blocked
    assert t["dead"] == 1 and t["done"] == 1
    dl = conn.execute("select cik, stage, owner, resolved_at from ops.work_dead_letter").fetchall()
    assert dl == [("1", 3, "data_engineer", None)]
    q = conn.execute("select kind, owner_lane, root_cause_family from ops.exception_queue").fetchall()
    assert q == [("DEAD_LETTER", "data_engineer", "orchestrator:transient")]


def test_permanent_error_dead_letters_at_once_and_rerun_resolves(conn):
    queue(conn, "1")
    loop(conn, Fake({("1", 3, 1): worker.Permanent("exit 31", "exit_31")}))
    assert conn.execute("select status, attempts from ops.work_item").fetchone() == ("dead", 1)
    queue(conn, "1")  # a rerun is planned while the dead letter is open: the claim skips it
    assert loop(conn, Fake())["done"] == 0
    conn.execute("update ops.work_dead_letter set resolved_at = now(), resolution = 'fixed rule'")
    assert loop(conn, Fake())["done"] == 1
    assert conn.execute("select count(*) from ops.work_dead_letter where resolved_at is null").fetchone()[0] == 0


def test_clean_rerun_auto_resolves_the_dead_letter(conn):
    queue(conn, "1")
    loop(conn, Fake({("1", 4, 1): worker.Permanent("x", "exit_31")}))
    conn.execute("update ops.work_dead_letter set resolved_at = null")
    # a run that finishes clean resolves it
    conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, status, locked_by, lease_expires_at) "
                 "values ('1',3,'{}','{}',repeat('e',64),'running','w',now()+interval '1 hour') returning id")
    wid = conn.execute("select max(id) from ops.work_item").fetchone()[0]
    worker.finish(conn, worker.Item(wid, "1", 3, [], {}, False, 0), {"v": 1})
    assert conn.execute("select resolution, resolved_at is not null from ops.work_dead_letter").fetchone() == ("rerun_passed", True)


def test_expired_lease_is_reaped_and_counts_an_attempt(conn):
    conn.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, status, locked_by, lease_expires_at, attempts) "
                 "values ('1',3,'{}','{}',repeat('a',64),'running','w',now()-interval '1 minute',2)")
    assert worker.reap_expired(conn) == 1
    assert conn.execute("select status, attempts from ops.work_item").fetchone() == ("dead", 3)
    assert conn.execute("select error_class from ops.work_dead_letter").fetchone()[0] == "lease_expired"


def test_shards_are_company_disjoint_and_dry_run_is_not_served(conn):
    for c in ("10", "11", "12", "13"):
        queue(conn, c)
    a, b = Fake(), Fake()
    loop(conn, a, shard=0, shards=2)
    loop(conn, b, shard=1, shards=2)
    assert {c for c, _ in a.calls} == {"10", "12"} and {c for c, _ in b.calls} == {"11", "13"}
    queue(conn, "20", dry=True)
    d = Fake()
    assert loop(conn, d, dry_run=True)["done"] == 1
    assert conn.execute("select count(*) from ops.company_served_version where cik='20'").fetchone()[0] == 0


def test_worker_bug_is_dead_lettered_not_raised(conn):
    queue(conn, "1")
    loop(conn, Fake({("1", 3, 1): KeyError("boom")}))
    assert conn.execute("select error_class from ops.work_item").fetchone()[0] == "worker_bug"


def test_autocommit_is_required(isolated_database_url, conn):
    with psycopg.connect(isolated_database_url) as c:
        with pytest.raises(RuntimeError):
            worker.claim(c, who="w")


def test_backpressure_waits_while_connections_exceed_the_threshold(conn):
    slept = []
    assert worker.backpressure(conn, limit=10_000, sleep=slept.append) == 0
    n = worker.backpressure(conn, limit=0, sleep=slept.append, max_waits=3)  # always above: bounded, never forever
    assert n == 3 and len(slept) == 3


# ---- stage runner --------------------------------------------------------------------------------------------------
def test_classify_transient_vs_permanent():
    assert isinstance(stages.classify(31, "psycopg.OperationalError: server closed the connection unexpectedly", 4), worker.Transient)
    assert isinstance(stages.classify(1, "HTTP 503 Service Unavailable from sec.gov", 1), worker.Transient)
    p = stages.classify(11, "KeyError: 'cik'", 3)
    assert isinstance(p, worker.Permanent) and p.error_class == "exit_11"
    assert stages.classify(90, "zstd missing", 3).error_class == "zstd_missing"


def _gate_repo(tmp_path, decision="PASS"):
    """A fake repo root: summary file, flow result line, and a run_cmd double that writes the gate's files."""
    (tmp_path / "data-team/strategy").mkdir(parents=True)
    (tmp_path / "data-team/strategy/top100-coverage-summary.csv").write_text("rank,ticker,company_id\n1,AAA,7\n")
    (tmp_path / ".runs/top100_flow").mkdir(parents=True)
    (tmp_path / ".runs/top100_flow/flow_results.tsv").write_text("10:00Z\t7\tAAA shown 5/5 100 open=0 GATE_READY\n")
    (tmp_path / "pipeline/src/scrooner_pipeline/proof").mkdir(parents=True)
    (tmp_path / "pipeline/src/scrooner_pipeline/proof/prove.py").write_text('DETECTOR_VERSION = "dv1"\n')
    cmds = []

    def run_cmd(cmd, *, log, env=None, cwd=None, timeout=0):
        cmds.append(cmd)
        if "top100_gate.py" in " ".join(cmd):
            pub = Path(cmd[cmd.index("--out-dir") + 1])
            (pub / "gate.json").write_text(json.dumps({"decision": decision, "reason": "r"}))
            if decision == "PASS":
                (pub / "AAA-coverage-2026-11-29.csv").write_text("a,b\n1,2\n")
                (pub / "AAA-request-2026-11-29.md").write_text("# req\n")
            return (0 if decision == "PASS" else 1), ""
        return 0, ""

    return cmds, run_cmd


def _runner(conn, tmp_path, run_cmd):
    m = cohort.Member(1, "AAA", 7, "1")
    return stages.FlowRunner(conn, {"1": m}, tmp_path / "out", root=tmp_path, run=run_cmd)


def _stage4_row(conn, wid, detail):
    conn.execute("insert into ops.work_item_stage (work_item_id, stage, stage_name, status, attempt, detail) values (%s,4,'prove','done',0,%s::jsonb)",
                 (wid, json.dumps(detail)))


def test_certify_stage_files_one_request_and_never_a_verdict(conn, tmp_path):
    cmds, run_cmd = _gate_repo(tmp_path)
    queue(conn, "1")
    wid = conn.execute("select id from ops.work_item").fetchone()[0]
    item = worker.Item(wid, "1", 3, [], {}, False, 0)
    _stage4_row(conn, wid, {"held": None})
    r = _runner(conn, tmp_path, run_cmd)
    res = r.stage5(item)
    assert res.detail["filed"] is True and res.detail["request_path"].endswith("AAA-request-2026-11-29.md")
    assert r.stage5(item).detail["filed"] is False  # same ticker + coverage sha + judge: filed once
    assert conn.execute("select ticker, judge_version from ops.certify_request").fetchall() == [("AAA", "dv1+gate@1")]
    # read-only: the only commands are the open-shown extract and the gate; nothing records a verdict or a certificate
    assert all(("certify_display" not in " ".join(c) and "record_verdict" not in " ".join(c)) for c in cmds)
    tables = {t for (t,) in conn.execute("select table_name from information_schema.tables where table_schema='ops'")}
    assert not any("certificate" in t or "verdict" in t or "registry" in t for t in tables)


def test_certify_stage_files_nothing_on_gate_fail_or_held_or_dry_run(conn, tmp_path):
    cmds, run_cmd = _gate_repo(tmp_path, "FAIL")
    queue(conn, "1")
    wid = conn.execute("select id from ops.work_item").fetchone()[0]
    r = _runner(conn, tmp_path, run_cmd)
    _stage4_row(conn, wid, {"held": None})
    assert r.stage5(worker.Item(wid, "1", 3, [], {}, False, 0)).detail["filed"] is False
    assert r.stage5(worker.Item(wid, "1", 3, [], {}, True, 0)).status == "skipped"
    conn.execute("update ops.work_item_stage set detail = '{\"held\": \"HELD_CERTIFIED\"}'")
    assert r.stage5(worker.Item(wid, "1", 3, [], {}, False, 0)).status == "skipped"
    assert conn.execute("select count(*) from ops.certify_request").fetchone()[0] == 0


def test_flow_stage_refuses_a_company_outside_the_summary_file(conn, tmp_path):
    cmds, run_cmd = _gate_repo(tmp_path)
    r = stages.FlowRunner(conn, {"9": cohort.Member(150, "ZZZ", 999, "9")}, tmp_path / "out", root=tmp_path, run=run_cmd)
    with pytest.raises(worker.Permanent) as e:
        r.stage3(worker.Item(1, "9", 3, [], {}, False, 0))
    assert e.value.error_class == "cohort_unsupported" and not cmds


def test_flow_stage_maps_exit_codes_to_stage_and_class(conn, tmp_path):
    _, _ = _gate_repo(tmp_path)

    def bad(cmd, *, log, env=None, cwd=None, timeout=0):
        return 31, "proof failed: server closed the connection unexpectedly"

    r = _runner(conn, tmp_path, bad)
    with pytest.raises(worker.Transient) as e:
        r.stage3(worker.Item(1, "1", 3, [], {}, False, 0))
    assert e.value.stage == 4


def test_ingest_sets_one_request_per_second(conn, tmp_path):
    seen = []

    def run_cmd(cmd, *, log, env=None, cwd=None, timeout=0):
        seen.append((cmd, env))
        return 0, ""

    r = _runner(conn, tmp_path, run_cmd)
    r.stage1(worker.Item(1, "1", 1, [], {}, False, 0))
    assert seen and all(e["SCROONER_EDGAR_MAX_RPS"] == "1" for _, e in seen)


def test_ingest_load_failure_is_classified_not_swallowed(conn, tmp_path):
    def run_cmd(cmd, *, log, env=None, cwd=None, timeout=0):
        if "nightly" in cmd:
            d = Path(cmd[cmd.index("--out") + 1])
            d.mkdir(parents=True, exist_ok=True)
            (d / "ciks.txt").write_text("1")
            return 0, ""
        return 1, "HTTP 503 Service Unavailable"

    with pytest.raises(worker.Transient) as e:
        _runner(conn, tmp_path, run_cmd).stage1(worker.Item(1, "1", 1, [], {}, False, 0))
    assert e.value.stage == 1


# ---- cohort, versions, producers ----------------------------------------------------------------------------------
def test_parse_ranks():
    assert cohort.parse_ranks("1-100") == (1, 100) and cohort.parse_ranks("101-500") == (101, 500)
    for bad in ("0-5", "5-1", "1-6000", "x", ""):
        with pytest.raises(ValueError):
            cohort.parse_ranks(bad)


def test_resolver_rows_sha_ignores_resolver_version_only(tmp_path):
    d = tmp_path / "data-team/tags/line_map/resolver"
    d.mkdir(parents=True)
    f = d / "AAA.csv"
    f.write_text("ticker,data_point,value,resolver_version\nAAA,x,1,.92\n")
    a = versions.resolver_rows_sha("AAA", tmp_path)
    f.write_text("ticker,data_point,value,resolver_version\nAAA,x,1,.93\n")
    assert versions.resolver_rows_sha("AAA", tmp_path) == a
    f.write_text("ticker,data_point,value,resolver_version\nAAA,x,2,.93\n")
    assert versions.resolver_rows_sha("AAA", tmp_path) != a
    assert versions.resolver_rows_sha("NOPE", tmp_path) == "none"


@pytest.fixture
def lake(conn):
    conn.execute("create schema if not exists core; create schema if not exists fsn;")
    conn.execute("create table core.company (id bigint primary key, cik text, primary_ticker text)")
    conn.execute("create table core.filing (id bigint primary key, company_id bigint, accession_number text, form text, period_of_report date)")
    conn.execute("create table fsn.filing (id bigint primary key, cik text, accession text)")
    conn.execute("insert into core.company values (1,'111','AAA'),(2,'222','BBB')")
    conn.execute("insert into core.filing values (1,1,'a-1','10-K','2024-12-31'),(2,1,'a-2','10-Q','2025-03-31'),"
                 "(3,2,'b-1','10-K','2024-12-31'),(4,2,'b-0','10-K','2010-12-31'),(5,1,'a-3','8-K','2025-04-01')")
    conn.execute("insert into fsn.filing values (1,'111','a-1'),(2,'222','b-1')")
    return conn


def test_new_filing_producer_only_missing_periodic_filings(lake):
    ms = [cohort.Member(1, "AAA", 1, "111"), cohort.Member(2, "BBB", 2, "222")]
    assert producers.new_filings(lake, ms) == 1  # AAA's 10-Q only: 8-K is not periodic, BBB's 2010 10-K is before 2014
    assert producers.new_filings(lake, ms) == 0  # idempotent
    v = lake.execute("select cik, versions from ops.pipeline_event").fetchall()
    assert v == [("111", {"accessions": ["a-2"], "from_stage": 1})]


def test_rank_change_producer_skips_served_companies_and_versions_current(lake):
    ms = [cohort.Member(1, "AAA", 1, "111"), cohort.Member(2, "BBB", 2, "222")]
    lake.execute("insert into ops.work_item (cik, from_stage, causes, versions, versions_hash, status, finished_at) values ('111',3,'{}','{}',repeat('a',64),'done',now())")
    lake.execute("insert into ops.company_served_version (cik, versions, versions_hash, work_item_id) select '111','{}',repeat('a',64),id from ops.work_item")
    assert producers.rank_changes(lake, ms, "1-2") == 1
    assert lake.execute("select cik from ops.pipeline_event").fetchone()[0] == "222"
    fs = versions.filings_sha(lake, ["111", "222", "333"])
    assert fs["333"] == "none" and fs["111"] != fs["222"]


def test_rule_changes_emits_only_changed_companies(lake, tmp_path):
    root = Path(__file__).parents[3]
    # a throwaway git repo with the real script: AAA's resolver rows change in the second commit, BBB's do not
    r = tmp_path / "r"
    (r / "scripts/ci").mkdir(parents=True)
    (r / "scripts/ci/top100_changed.py").write_text((root / "scripts/ci/top100_changed.py").read_text())
    (r / "data-team/strategy").mkdir(parents=True)
    (r / "data-team/strategy/top100-coverage-summary.csv").write_text("rank,ticker,company_id\n1,AAA,1\n2,BBB,2\n")
    rd = r / "data-team/tags/line_map/resolver"
    rd.mkdir(parents=True)
    hdr = "cik,ticker,data_point,period_end,grain,value,resolver_version\n"
    (rd / "AAA.csv").write_text(hdr + "111,AAA,x,2024-12-31,FY,1,.92\n")
    (rd / "BBB.csv").write_text(hdr + "222,BBB,x,2024-12-31,FY,1,.92\n")
    g = lambda *a: subprocess.run(["git", *a], cwd=r, check=True, capture_output=True, text=True).stdout.strip()  # noqa: E731
    g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
    g("add", "-A"); g("commit", "-qm", "a")
    base = g("rev-parse", "HEAD")
    (rd / "AAA.csv").write_text(hdr + "111,AAA,x,2024-12-31,FY,2,.93\n")  # value change
    (rd / "BBB.csv").write_text(hdr + "222,BBB,x,2024-12-31,FY,1,.93\n")  # version bump only
    g("add", "-A"); g("commit", "-qm", "b")
    ms = [cohort.Member(1, "AAA", 1, "111"), cohort.Member(2, "BBB", 2, "222")]
    out = producers.rule_changes(lake, ms, base, g("rev-parse", "HEAD"), r)
    assert out["company_events"] == 1
    assert lake.execute("select cik from ops.pipeline_event").fetchall() == [("111",)]


# ---- publish script ----------------------------------------------------------------------------------------------
def _load_publish():
    import importlib.util

    spec = importlib.util.spec_from_file_location("orchestrator_publish", Path(__file__).parents[3] / "scripts/ci/orchestrator_publish.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_publish_commits_only_named_files_and_retries_the_push(tmp_path):
    pub_mod = _load_publish()
    g = lambda cwd, *a: subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()  # noqa: E731
    bare = tmp_path / "origin.git"
    g(tmp_path, "init", "-q", "--bare", "-b", "main", str(bare))
    repo = tmp_path / "repo"
    g(tmp_path, "clone", "-q", str(bare), str(repo))
    g(repo, "config", "user.email", "t@t"); g(repo, "config", "user.name", "t")
    (repo / "scripts/ci").mkdir(parents=True)
    root = Path(__file__).parents[3]
    (repo / "scripts/ci/top100_coverage_merge.py").write_text((root / "scripts/ci/top100_coverage_merge.py").read_text())
    (repo / "keep.txt").write_text("unrelated")
    g(repo, "add", "-A"); g(repo, "commit", "-qm", "base"); g(repo, "push", "-q", "origin", "HEAD:main")
    parts = tmp_path / "parts/orch-shard-0/.runs/top100_flow/publish_c7"
    parts.mkdir(parents=True)
    (parts / "gate.json").write_text(json.dumps({"decision": "PASS"}))
    (parts / "AAA-coverage-2026-11-29.csv").write_text("a\n1\n")
    (parts / "AAA-request-2026-11-29.md").write_text("# req\n")
    (parts / "open-shown.json").write_text(json.dumps({"ticker": "AAA", "open": 1}))
    (parts / "open-shown.csv").write_text("cell\nx\n")
    (repo / "stray.txt").write_text("must not be committed")
    # a competing push lands between our fetch and push: the first attempt is rejected, the retry resets and re-applies
    other = tmp_path / "other"
    g(tmp_path, "clone", "-q", str(bare), str(other)); g(other, "config", "user.email", "t@t"); g(other, "config", "user.name", "t")
    calls = {"n": 0}
    real_git = pub_mod.git

    def racing_git(repo_, *a, check=True):
        if a[:1] == ("add",):  # an unrelated untracked file is present at every attempt (a reset removes the committed copy)
            (repo / "stray.txt").write_text("must not be committed")
        if a[:1] == ("push",) and calls["n"] == 0:
            calls["n"] += 1
            (other / "race.txt").write_text("x"); g(other, "add", "-A"); g(other, "commit", "-qm", "race"); g(other, "push", "-q", "origin", "HEAD:main")
        return real_git(repo_, *a, check=check)

    pub_mod.git = racing_git
    out = pub_mod.publish(repo, tmp_path / "parts", "run-url", retries=3, sleep=lambda s: None)
    assert out == "pushed" and calls["n"] == 1
    files = g(other, "pull", "-q", "origin", "main") or g(other, "ls-tree", "-r", "--name-only", "HEAD").split("\n")
    assert "data-team/strategy/certification/AAA-coverage-2026-11-29.csv" in files
    assert "data-team/strategy/approvals/requests/AAA-request-2026-11-29.md" in files
    assert "data-team/strategy/open-shown/AAA.csv" in files and "stray.txt" not in files


# ---- blocked_on_ingest and template seeding (scrooner-36, M6-PREP-NO-FSN-PROOF-2026-11-29) ----------------------------
def test_company_without_fsn_is_blocked_not_run_or_dead_lettered_and_unblocks(lake):
    ev(lake, "333", "rank_change", rank_set="1-9")  # no fsn.filing row for 333
    ev(lake, "111", "rank_change", rank_set="1-9")  # 111 has one
    rep = planner.plan_events(lake)
    assert rep.blocked_on_ingest == 1 and rep.queued == 1
    assert items(lake, "cik='333'") == [("333", 3, "blocked_on_ingest", ["rank_change"], False)]
    r = Fake()
    t = loop(lake, r)  # the worker claims only the runnable one
    assert {c for c, _ in r.calls} == {"111"} and t["done"] == 1
    assert lake.execute("select count(*) from ops.work_dead_letter").fetchone()[0] == 0
    # a new_filing event (stage 1: ingest can fix it) moves the blocked item to pending at stage 1
    ev(lake, "333", "new_filing", accessions=["z-1"], from_stage=1)
    planner.plan_events(lake)
    assert items(lake, "cik='333'")[0][1:3] == (1, "pending")
    # and when filings simply appear, a blocked item is unblocked by the planner
    lake.execute("update ops.work_item set status='blocked_on_ingest', from_stage=3 where cik='333'")
    lake.execute("insert into fsn.filing values (99,'333','z-1')")
    planner.plan_events(lake)
    assert items(lake, "cik='333'")[0][2] == "pending"


@pytest.fixture
def tmpl(lake, tmp_path):
    lake.execute("alter table core.company add column sic_code text")
    lake.execute("update core.company set sic_code = '3571' where id = 1")
    lake.execute("create schema if not exists analytics")
    lake.execute("create table analytics.company_data_point_template (company_id bigint, data_point text, in_template boolean, "
                 "reason text, effective_from date, template text, source text, template_version text, "
                 "seeded_at timestamptz default now())")
    cat = tmp_path / "data-team/47-fsn-store/company_tag_map"
    cat.mkdir(parents=True)
    (cat / "concepts_catalog.csv").write_text("name\nrevenue\ntotal_assets\n")
    return lake, tmp_path


def test_seed_templates_seeds_only_missing_companies_and_is_idempotent(tmpl):
    lake, root = tmpl
    ms = [cohort.Member(1, "AAA", 1, "111"), cohort.Member(2, "BBB", 2, "222")]
    lake.execute("insert into analytics.company_data_point_template (company_id, data_point, in_template, effective_from, template, source, template_version) "
                 "values (2,'revenue',true,'2026-11-13','x','y','z')")
    dry = producers.seed_templates(lake, ms, root, write=False)
    assert dry["missing"] == 1 and dry["seeded"] == 0
    assert lake.execute("select count(*) from analytics.company_data_point_template where company_id = 1").fetchone()[0] == 0
    out = producers.seed_templates(lake, ms, root)
    assert out["seeded"] == 1 and out["events"] == 1 and not out["failed"]
    assert lake.execute("select count(*), min(source) from analytics.company_data_point_template where company_id = 1").fetchone() == (2, "sector_default")
    assert lake.execute("select count(*) from analytics.company_data_point_template where company_id = 2").fetchone()[0] == 1  # untouched
    again = producers.seed_templates(lake, ms, root)
    assert again["missing"] == 0 and again["events"] == 0
