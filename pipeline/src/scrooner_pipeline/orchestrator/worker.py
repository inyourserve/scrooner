"""Worker (PIPELINE.md section 3): one company at a time, per-stage checkpoints, bounded retries, dead letters.

A worker claims a work item (skip locked, a lease), runs its stages in STAGE_ORDER from the item's `from_stage`, and
writes one ops.work_item_stage row per finished stage in the same transaction that extends the lease, so a crash
resumes at the first unfinished stage (a stage already checkpointed done/skipped is never run again). Stage 5 is last
and only FILES a certify request; this module never records a verdict, a registry row or a certificate.

Failures: a Transient error (SEC 5xx, pooler drop, statement timeout ...) puts the item in retry_wait with exponential
backoff; after MAX_ATTEMPTS failures, or on the first Permanent error, the item is dead: an ops.work_dead_letter row
(owner data_engineer) and an ops.exception_queue DEAD_LETTER row. A dead company never blocks another one: the claim
skips it. When a later run of the same company finishes clean, its open dead letter is resolved ("rerun passes").

Shards are company-disjoint (cik modulo the shard count) and `ingest_only` workers (the single SEC-limited process)
take only items still waiting for stage 1.
"""

from __future__ import annotations

import json
import os
import socket
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

import psycopg

from .store import MAX_ATTEMPTS, STAGE_NAMES, STAGE_ORDER, stage_index

LEASE_SECONDS = 1800
BACKOFF_BASE_SECONDS = 60


class StageError(Exception):
    error_class = "error"

    def __init__(
        self, message: str, error_class: str | None = None, stage: int | None = None
    ):
        super().__init__(message)
        if error_class:
            self.error_class = error_class
        self.stage = stage


class Transient(StageError):
    """Retry later (up to MAX_ATTEMPTS): the same input may pass."""

    error_class = "transient"


class Permanent(StageError):
    """Dead-letter at once: retrying the same input cannot help."""

    error_class = "permanent"


class Blocked(StageError):
    """The item cannot run yet and no retry would help: it waits in `status` (blocked_on_ingest | blocked_on_resolver).
    Not a failure: no attempt is counted, no dead letter is written; the planner releases it when its input exists."""

    error_class = "blocked"

    def __init__(self, message: str, status: str = "blocked_on_resolver"):
        super().__init__(message, status)
        self.status = status


@dataclass
class StageResult:
    status: str = "done"  # done | skipped
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class Item:
    id: int
    cik: str
    from_stage: int
    causes: list[str]
    versions: dict[str, Any]
    dry_run: bool
    attempts: int


class Runner(Protocol):
    def run(self, stage: int, item: Item) -> StageResult: ...


CLAIM = """
with c as (
    select w.id from ops.work_item w
    where w.status in ('pending', 'retry_wait') and w.next_attempt_at <= now()
      and w.dry_run = %(dry)s
      and mod(w.cik::bigint, %(n)s) = %(i)s
      and not exists (select 1 from ops.work_dead_letter d where d.cik = w.cik and d.resolved_at is null)
      and not exists (select 1 from ops.work_item r where r.cik = w.cik and r.status = 'running')
      and ({stage_filter})
    order by w.id limit 1 for update skip locked)
update ops.work_item w set status = 'running', locked_by = %(who)s, updated_at = now(),
       lease_expires_at = now() + make_interval(secs => %(lease)s)
from c where w.id = c.id
returning w.id, w.cik, w.from_stage, w.causes, w.versions, w.dry_run, w.attempts
"""
_STAGE1_DONE = "exists (select 1 from ops.work_item_stage s where s.work_item_id = w.id and s.stage = 1)"
FILTER_SHARD = f"w.from_stage <> 1 or {_STAGE1_DONE}"
FILTER_INGEST = f"w.from_stage = 1 and not {_STAGE1_DONE}"


PAUSE_ABOVE = 80  # doc 02 (founder 2026-11-13): pause while pg_stat_activity exceeds this; data loads stay within 70


def backpressure(
    conn,
    *,
    limit: int = PAUSE_ABOVE,
    sleep: Callable[[float], None] = time.sleep,
    wait_s: float = 60,
    max_waits: int = 60,
) -> int:
    """Block (bounded) while client backends exceed the pause threshold. Returns how many waits it took."""
    waits = 0
    while waits < max_waits:
        n = conn.execute(
            "select count(*) from pg_stat_activity where backend_type = 'client backend'"
        ).fetchone()[0]
        if n <= limit:
            break
        waits += 1
        sleep(wait_s)
    return waits


def worker_id() -> str:
    return f"{socket.gethostname()}:{os.getpid()}:{os.environ.get('GITHUB_RUN_ID', 'local')}"


def reap_expired(conn: psycopg.Connection) -> int:
    """A running item whose lease ran out (crashed worker) counts as one failed attempt and goes back to the queue."""
    cur = conn.execute(
        """update ops.work_item set
              status = case when attempts + 1 >= %s then 'dead' else 'retry_wait' end,
              attempts = attempts + 1, locked_by = null, lease_expires_at = null, updated_at = now(),
              last_error = 'lease expired (worker crashed or timed out)', error_class = 'lease_expired',
              next_attempt_at = now()
           where status = 'running' and lease_expires_at < now() returning id, cik, status, attempts""",
        (MAX_ATTEMPTS,),
    )
    rows = cur.fetchall()
    for wid, cik, status, attempts in rows:
        if status == "dead":
            _dead_letter(
                conn,
                wid,
                cik,
                None,
                "lease_expired",
                "lease expired (worker crashed or timed out)",
                attempts,
            )
    conn.commit()
    return len(rows)


def _need_autocommit(conn) -> None:
    # every function here runs its own `with conn.transaction()` blocks and single statements; an implicit outer
    # transaction would turn them into savepoints that never commit
    if not conn.autocommit:
        raise RuntimeError("the orchestrator needs an autocommit connection")


def claim(
    conn,
    *,
    who: str,
    shard: int = 0,
    shards: int = 1,
    ingest_only: bool = False,
    dry_run: bool = False,
    lease_s: int = LEASE_SECONDS,
) -> Item | None:
    _need_autocommit(conn)
    reap_expired(conn)
    sql = CLAIM.format(stage_filter=FILTER_INGEST if ingest_only else FILTER_SHARD)
    row = conn.execute(
        sql, {"dry": dry_run, "n": shards, "i": shard, "who": who, "lease": lease_s}
    ).fetchone()
    conn.commit()
    if row is None:
        return None
    return Item(*row)


def _checkpoint(
    conn, item: Item, stage: int, res: StageResult, lease_s: int = LEASE_SECONDS
) -> None:
    with conn.transaction():
        conn.execute(
            """insert into ops.work_item_stage (work_item_id, stage, stage_name, status, attempt, detail)
               values (%s, %s, %s, %s, %s, %s::jsonb)
               on conflict (work_item_id, stage) do update set status = excluded.status, attempt = excluded.attempt,
                    detail = excluded.detail, finished_at = now()""",
            (
                item.id,
                stage,
                STAGE_NAMES[stage],
                res.status,
                item.attempts,
                json.dumps(res.detail, default=str),
            ),
        )
        conn.execute(
            "update ops.work_item set lease_expires_at = now() + make_interval(secs => %s), updated_at = now() where id = %s",
            (lease_s, item.id),
        )


def _done_stages(conn, item: Item) -> set[int]:
    return {
        r[0]
        for r in conn.execute(
            "select stage from ops.work_item_stage where work_item_id = %s", (item.id,)
        )
    }


def _dead_letter(
    conn,
    wid: int,
    cik: str,
    stage: int | None,
    error_class: str,
    error: str,
    attempts: int,
) -> None:
    conn.execute(
        """insert into ops.work_dead_letter (work_item_id, cik, stage, error_class, error, attempts, owner)
           values (%s, %s, %s, %s, %s, %s, 'data_engineer') on conflict (work_item_id) do nothing""",
        (wid, cik, stage, error_class, error[:4000], attempts),
    )


def _queue_row(
    conn, wid: int, cik: str, stage: int | None, error_class: str, error: str
) -> None:
    from scrooner_pipeline.certification import exception_queue as eq

    tk = None
    try:  # the ticker is a convenience; the orchestrator tests run without core.company
        r = conn.execute(
            "select primary_ticker from core.company where cik = %s", (cik,)
        ).fetchone()
        tk = r[0] if r else None
    except psycopg.Error:
        conn.rollback()
    eq.load(
        conn,
        [
            eq.Row(
                idempotency_key=f"DEAD_LETTER|{cik}|{wid}",
                kind="DEAD_LETTER",
                cell_key=f"cik:{cik}",
                root_cause_family=f"orchestrator:{error_class}",
                owner_lane="data_engineer",
                cik=cik,
                ticker=tk,
                detail=f"work item {wid}, stage {stage}: {error[:500]}",
            )
        ],
        True,
    )


def fail(
    conn,
    item: Item,
    exc: Exception,
    stage: int | None,
    *,
    backoff_base: int = BACKOFF_BASE_SECONDS,
) -> str:
    """Record a failed attempt. Returns 'retry_wait' or 'dead'."""
    attempts = item.attempts + 1
    cls = getattr(exc, "error_class", "error")
    transient = isinstance(exc, Transient)
    dead = (not transient) or attempts >= MAX_ATTEMPTS
    status = "dead" if dead else "retry_wait"
    delay = backoff_base * 4 ** (attempts - 1)
    conn.rollback()
    conn.execute(
        """update ops.work_item set status = %s, attempts = %s, last_error = %s, error_class = %s, locked_by = null,
              lease_expires_at = null, updated_at = now(), finished_at = case when %s then now() else null end,
              next_attempt_at = now() + make_interval(secs => %s) where id = %s""",
        (status, attempts, str(exc)[:4000], cls, dead, delay, item.id),
    )
    if dead:
        _dead_letter(conn, item.id, item.cik, stage, cls, str(exc), attempts)
    conn.commit()
    if dead:
        _queue_row(conn, item.id, item.cik, stage, cls, str(exc))
    return status


def finish(conn, item: Item, served_versions: dict[str, Any] | None) -> None:
    """Mark done; a real (non-dry) run records the versions it served and resolves an open dead letter."""
    from .store import versions_hash

    with conn.transaction():
        conn.execute(
            """update ops.work_item set status = 'done', finished_at = now(), updated_at = now(), locked_by = null,
                  lease_expires_at = null where id = %s""",
            (item.id,),
        )
        if not item.dry_run:
            if served_versions is not None:
                conn.execute(
                    """insert into ops.company_served_version (cik, versions, versions_hash, work_item_id)
                       values (%s, %s::jsonb, %s, %s)
                       on conflict (cik) do update set versions = excluded.versions, versions_hash = excluded.versions_hash,
                            work_item_id = excluded.work_item_id, served_at = now()""",
                    (
                        item.cik,
                        json.dumps(served_versions, sort_keys=True),
                        versions_hash(served_versions),
                        item.id,
                    ),
                )
            conn.execute(
                """update ops.work_dead_letter set resolved_at = now(), resolution = 'rerun_passed'
                   where cik = %s and resolved_at is null""",
                (item.cik,),
            )


def run_item(
    conn,
    item: Item,
    runner: Runner,
    served_versions: Callable[[str], dict[str, Any]] | None = None,
    *,
    only_through: int | None = None,
    backoff_base: int = BACKOFF_BASE_SECONDS,
) -> str:
    """Run one claimed item. Returns done | released | retry_wait | dead."""
    order = STAGE_ORDER[stage_index(item.from_stage) :]
    done = _done_stages(conn, item)
    stage = None
    try:
        for stage in order:
            if stage not in done:
                try:
                    res = runner.run(stage, item)
                except StageError as e:
                    e.stage = e.stage or stage
                    raise
                _checkpoint(conn, item, stage, res)
            if only_through is not None and stage == only_through:
                conn.execute(
                    "update ops.work_item set status = 'pending', locked_by = null, lease_expires_at = null, "
                    "updated_at = now() where id = %s",
                    (item.id,),
                )
                conn.commit()
                return "released"
        finish(conn, item, served_versions(item.cik) if served_versions else None)
        return "done"
    except Blocked as e:
        conn.execute(
            "update ops.work_item set status = %s, locked_by = null, lease_expires_at = null, updated_at = now(), "
            "last_error = %s where id = %s",
            (e.status, str(e)[:4000], item.id),
        )
        return e.status
    except StageError as e:
        return fail(conn, item, e, e.stage or stage, backoff_base=backoff_base)
    except (
        psycopg.OperationalError
    ) as e:  # pooler drop, timeout: the same item may pass later
        return fail(
            conn,
            item,
            Transient(str(e), "db_transient"),
            stage,
            backoff_base=backoff_base,
        )
    except Exception as e:  # noqa: BLE001 - anything else is a bug: dead-letter with its class, never crash the shard
        return fail(
            conn,
            item,
            Permanent(f"{type(e).__name__}: {e}", "worker_bug"),
            stage,
            backoff_base=backoff_base,
        )


def work_loop(
    conn,
    runner: Runner,
    *,
    shard: int = 0,
    shards: int = 1,
    ingest_only: bool = False,
    dry_run: bool = False,
    served_versions: Callable[[str], dict[str, Any]] | None = None,
    wall_clock_s: int = 19000,
    max_items: int | None = None,
    backoff_base: int = BACKOFF_BASE_SECONDS,
    idle_wait_s: int = 30,
    log: Callable[[str], None] = print,
) -> dict[str, int]:
    """Take items until none is due (or the wall clock / item cap ends the loop). Items waiting in retry_wait are
    waited for while the clock allows, so a transient failure is retried within the same run."""
    t0 = time.monotonic()
    tally = {
        "done": 0,
        "released": 0,
        "retry_wait": 0,
        "dead": 0,
        "blocked_on_ingest": 0,
        "blocked_on_resolver": 0,
    }
    who = worker_id()
    n = 0
    while time.monotonic() - t0 < wall_clock_s and (max_items is None or n < max_items):
        backpressure(conn)
        item = claim(
            conn,
            who=who,
            shard=shard,
            shards=shards,
            ingest_only=ingest_only,
            dry_run=dry_run,
        )
        if item is None:
            nxt = conn.execute(
                """select extract(epoch from min(next_attempt_at) - now()) from ops.work_item
                   where status = 'retry_wait' and dry_run = %s and mod(cik::bigint, %s) = %s""",
                (dry_run, shards, shard),
            ).fetchone()[0]
            conn.commit()
            if (
                nxt is None
                or time.monotonic() - t0 + max(float(nxt), 0) >= wall_clock_s
            ):
                break
            time.sleep(max(float(nxt), 0) + 1 if nxt > 0 else idle_wait_s)
            continue
        n += 1
        out = run_item(
            conn,
            item,
            runner,
            served_versions,
            only_through=1 if ingest_only else None,
            backoff_base=backoff_base,
        )
        tally[out] += 1
        log(f"work item {item.id} cik {item.cik}: {out}")
    return tally
