"""Module 10 -- Collection Logs (doc 06). Doc 08's Day 6 deliverable,
paired with collector/integrity.py.

Doc 06 describes this module's job as "records what happened, when, and to
what." That recording already happens, twice over, before this file exists:

1. structlog gives every Collector module structured, timestamped event
   logs at the moment something happens (see common/sec_client.py,
   collector/retry.py, jobs/bootstrap.py, etc.) -- console output today,
   trivially redirectable to a file/aggregator later without touching a
   single call site, since every module already goes through
   `structlog.get_logger()`.
2. raw.collector_runs / raw.collector_errors are the durable, queryable
   record of the same facts, written by collector/retry.py's run
   lifecycle functions (start_or_resume_run/finish_run) and each
   collector module's own error-insert calls -- this is what survives
   past terminal scrollback and is what doc 05's traceability principle
   actually needs (every row's run_id ties back to exactly which run
   produced it).

Building a second, parallel logging system on top of either of those
would be redundant, not additive -- doc 08's Day 6 practical note says as
much directly. What was actually missing, checked against what a human
(or the next agent) doing this work would need: a human-readable REPORT
over what's already being recorded, so "what happened in run N" or "what
happened recently" doesn't require hand-writing SQL against
raw.collector_runs/raw.collector_errors every single time -- which is
exactly what Day 3-5's learnings entries show happening ad hoc, session
after session (e.g. day-04-retry-and-resume.md's verification queries).

So this module is read-only query + formatting functions over those two
existing tables, exposed via jobs/report.py's Typer CLI (`runs`, `run
<id>` commands). It never writes to raw.collector_runs/raw.collector_errors
-- that stays retry.py's job, per doc 05's "one source of truth" per
concern.
"""

from dataclasses import dataclass, field
from datetime import datetime

import psycopg


@dataclass
class RunRecord:
    id: int
    run_type: str
    job: str | None
    params_key: str | None
    status: str
    started_at: datetime
    finished_at: datetime | None
    heartbeat_at: datetime | None
    stats: dict

    @property
    def duration_seconds(self) -> float | None:
        if self.finished_at is None:
            return None
        return (self.finished_at - self.started_at).total_seconds()


@dataclass
class ErrorRecord:
    id: int
    run_id: int | None
    cik: str | None
    source: str | None
    error_type: str
    message: str
    occurred_at: datetime
    resolved: bool


@dataclass
class RunDetail:
    run: RunRecord
    errors: list[ErrorRecord] = field(default_factory=list)


_RUN_COLUMNS = "id, run_type, job, params_key, status, started_at, finished_at, heartbeat_at, stats"
_ERROR_COLUMNS = "id, run_id, cik, source, error_type, message, occurred_at, resolved"


def _row_to_run(cur: psycopg.Cursor, row: tuple) -> RunRecord:
    cols = [d.name for d in cur.description]
    return RunRecord(**dict(zip(cols, row)))


def _row_to_error(cur: psycopg.Cursor, row: tuple) -> ErrorRecord:
    cols = [d.name for d in cur.description]
    return ErrorRecord(**dict(zip(cols, row)))


def get_recent_runs(conn: psycopg.Connection, limit: int = 20, job: str | None = None) -> list[RunRecord]:
    """Most recent runs first -- the default view for "what's been
    happening lately," e.g. after a scheduled job to confirm it actually
    ran and finished cleanly."""
    with conn.cursor() as cur:
        if job is not None:
            cur.execute(
                f"select {_RUN_COLUMNS} from raw.collector_runs where job = %s order by started_at desc limit %s",
                (job, limit),
            )
        else:
            cur.execute(f"select {_RUN_COLUMNS} from raw.collector_runs order by started_at desc limit %s", (limit,))
        return [_row_to_run(cur, row) for row in cur.fetchall()]


def get_run(conn: psycopg.Connection, run_id: int) -> RunRecord | None:
    with conn.cursor() as cur:
        cur.execute(f"select {_RUN_COLUMNS} from raw.collector_runs where id = %s", (run_id,))
        row = cur.fetchone()
        return _row_to_run(cur, row) if row is not None else None


def get_errors_for_run(conn: psycopg.Connection, run_id: int) -> list[ErrorRecord]:
    with conn.cursor() as cur:
        cur.execute(
            f"select {_ERROR_COLUMNS} from raw.collector_errors where run_id = %s order by occurred_at", (run_id,)
        )
        return [_row_to_error(cur, row) for row in cur.fetchall()]


def get_run_detail(conn: psycopg.Connection, run_id: int) -> RunDetail | None:
    run = get_run(conn, run_id)
    if run is None:
        return None
    return RunDetail(run=run, errors=get_errors_for_run(conn, run_id))


def format_recent_runs(runs: list[RunRecord]) -> str:
    if not runs:
        return "no runs recorded in raw.collector_runs"
    header = f"{'id':>5}  {'job':<14} {'run_type':<12} {'status':<10} {'started_at':<26} {'duration_s':>10}  stats"
    lines = [header, "-" * len(header)]
    for r in runs:
        duration = f"{r.duration_seconds:.1f}" if r.duration_seconds is not None else "-"
        lines.append(
            f"{r.id:>5}  {(r.job or '-'):<14} {r.run_type:<12} {r.status:<10} "
            f"{r.started_at.isoformat():<26} {duration:>10}  {r.stats}"
        )
    return "\n".join(lines)


def format_run_detail(detail: RunDetail) -> str:
    r = detail.run
    duration = f"{r.duration_seconds:.1f}s" if r.duration_seconds is not None else "still running / never finished"
    lines = [
        f"run_id={r.id}  job={r.job}  run_type={r.run_type}  status={r.status}",
        f"params_key={r.params_key}",
        f"started_at={r.started_at.isoformat()}",
        f"finished_at={r.finished_at.isoformat() if r.finished_at else '-'}  duration={duration}",
        f"heartbeat_at={r.heartbeat_at.isoformat() if r.heartbeat_at else '-'}",
        f"stats={r.stats}",
        f"errors: {len(detail.errors)}",
    ]
    for e in detail.errors:
        lines.append(
            f"  [{e.occurred_at.isoformat()}] cik={e.cik} source={e.source} type={e.error_type} "
            f"resolved={e.resolved}: {e.message}"
        )
    return "\n".join(lines)
