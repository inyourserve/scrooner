"""CLI: python -m scrooner_pipeline.orchestrator <command>   (DATABASE_URL; one autocommit connection per process)

plan    --ranks 1-100 [--base SHA --head SHA] [--dry-run]
          emit the events (new_filing, rank_change, rule_version from a git range) and plan them, then the catch-up
          sweep; prints the matrix of shard indexes for the workers as JSON on the last line
ingest  --ranks 1-100            the single SEC-limited process: stage 1 for items still waiting for it
work    --shard I --shards N     one company-disjoint shard: stages 2-6, then files the certify request
report                           queue depth, dead letters, inflow/outflow, served-lag (stdout)
resolve-dead-letter --id N --by WHO --note TEXT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg

from . import cohort, planner, producers, stages, versions, worker


def connect(timeout_ms: int = 120_000) -> psycopg.Connection:
    url = os.environ.get("SCROONER_DATABASE_URL") or os.environ["DATABASE_URL"]
    c = psycopg.connect(url, autocommit=True, connect_timeout=30)
    c.execute(f"set statement_timeout = {timeout_ms}")
    return c


def cmd_plan(a, conn) -> int:
    members = cohort.resolve(conn, a.ranks)
    out: dict = {"cohort": len(members), "ranks": a.ranks}
    out["templates"] = producers.seed_templates(conn, members, write=not a.dry_run)
    out["new_filing_events"] = producers.new_filings(conn, members)
    out["rank_change_events"] = producers.rank_changes(conn, members, a.ranks)
    if a.base and a.head:
        out["rule_changes"] = producers.rule_changes(conn, members, a.base, a.head)
    ciks = {m.cik for m in members}
    rep = planner.plan_events(
        conn, planner.DbRuleUsage(conn), cohort=ciks, dry_run=a.dry_run
    )
    out["planned"] = {
        k: getattr(rep, k)
        for k in (
            "events",
            "queued",
            "merged",
            "already_done",
            "unscoped",
            "no_companies",
            "blocked_on_ingest",
        )
    }
    sw = planner.sweep(conn, versions.current(conn, members), dry_run=a.dry_run)
    out["sweep"] = {
        "queued": sw.queued,
        "merged": sw.merged,
        "already_done": sw.already_done,
    }
    out["pending_items"] = conn.execute(
        "select count(*) from ops.work_item where status in ('pending','retry_wait') and dry_run = %s",
        (a.dry_run,),
    ).fetchone()[0]
    out["matrix"] = {"shard": list(range(min(a.shards, max(out["pending_items"], 1))))}
    print(json.dumps(out))
    return 0


def _runner(a, conn, members):
    return stages.FlowRunner(
        conn,
        {m.cik: m for m in members},
        Path(a.out),
        run_url=os.environ.get("RUN_URL", ""),
    )


def cmd_work(a, conn, ingest: bool = False) -> int:
    members = cohort.resolve(conn, a.ranks)
    runner = _runner(a, conn, members)
    by_cik = {m.cik: m for m in members}

    def served(cik: str):
        return versions.current(conn, [by_cik[cik]])[cik]

    tally = worker.work_loop(
        conn,
        runner,
        shard=0 if ingest else a.shard,
        shards=1 if ingest else a.shards,
        ingest_only=ingest,
        dry_run=a.dry_run,
        served_versions=served,
        wall_clock_s=a.wall_clock,
    )
    print(json.dumps({"tally": tally, "shard": a.shard, "ingest": ingest}))
    return 0


def cmd_report(a, conn) -> int:
    q = lambda sql: conn.execute(sql).fetchall()  # noqa: E731
    print(
        "work items by status:",
        dict(q("select status, count(*) from ops.work_item group by 1")),
    )
    print(
        "done in last 24h:",
        q(
            "select count(*) from ops.work_item where status='done' and finished_at > now() - interval '24 hours'"
        )[0][0],
    )
    dl = q(
        "select id, cik, stage, error_class, attempts, created_at::date from ops.work_dead_letter where resolved_at is null order by id"
    )
    print(f"open dead letters: {len(dl)}")
    for r in dl:
        print("  ", *r)
    print(
        "certify requests filed:", q("select count(*) from ops.certify_request")[0][0]
    )
    print(
        "served companies:", q("select count(*) from ops.company_served_version")[0][0]
    )
    print(
        "dead letters older than 24h (SLO 0):",
        q(
            "select count(*) from ops.work_dead_letter where resolved_at is null and created_at < now() - interval '24 hours'"
        )[0][0],
    )
    return 0


def cmd_resolve(a, conn) -> int:
    n = conn.execute(
        "update ops.work_dead_letter set resolved_at = now(), resolution = %s where id = %s and resolved_at is null",
        (f"{a.by}: {a.note}", a.id),
    ).rowcount
    print("resolved" if n else "no open dead letter with that id")
    return 0 if n else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="orchestrator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "ingest", "work"):
        p = sub.add_parser(name)
        p.add_argument("--ranks", default="1-100")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--shards", type=int, default=8)
        p.add_argument("--shard", type=int, default=0)
        p.add_argument("--base")
        p.add_argument("--head")
        p.add_argument("--out", default=".runs/orchestrator")
        p.add_argument("--wall-clock", type=int, default=19000)
    sub.add_parser("report")
    r = sub.add_parser("resolve-dead-letter")
    r.add_argument("--id", type=int, required=True)
    r.add_argument("--by", required=True)
    r.add_argument("--note", required=True)
    a = ap.parse_args(argv)
    conn = connect()
    if a.cmd == "plan":
        return cmd_plan(a, conn)
    if a.cmd == "ingest":
        return cmd_work(a, conn, ingest=True)
    if a.cmd == "work":
        return cmd_work(a, conn)
    if a.cmd == "report":
        return cmd_report(a, conn)
    return cmd_resolve(a, conn)


if __name__ == "__main__":
    sys.exit(main())
