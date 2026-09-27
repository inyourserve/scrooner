"""Module 9 — Retry / Failure Handling (doc 06). Doc 08's Day 4 deliverable.
Owns three related things:

1. Tenacity retry policy for transient SEC/Storage HTTP errors -- a single
   source of truth. Before Day 4, sec_client.py and storage.py each
   defined their own copy of the same `_is_retryable` predicate; that's
   consolidated here now and both import it, per doc 05's "one source of
   truth" principle.

2. Idempotency key. sec_companyfacts/sec_submissions are intentionally
   append-only (Day 3): a genuinely new fetch pass for a company already
   stored is allowed and expected -- that's the lossless-history design,
   not a bug. So the key that identifies "the same fetch, already stored"
   can't be `cik` alone, and can't be "any row for this cik exists" either.
   It has to be (cik, fetched_at[, filename]) -- exactly what storage_path
   already encodes (see db/migrations/0002 and storage.py's path
   convention). storage_path is therefore the idempotency key:
     - Enforced with a unique constraint at the DB level (belt-and-
       suspenders -- even a bug in the checkpoint-skip logic below can't
       produce a duplicate row/object).
     - Used as an application-level skip-check (query which identifiers
       are already stored for this run_id before doing any work), so a
       resumed run doesn't even re-download/re-upload a company already
       done, not just avoid a duplicate row after the fact.

3. Run-level checkpoint/resume + reaping. A logical bootstrap invocation is
   identified by (job, params_key). If a process is killed mid-run, its
   raw.collector_runs row is left status='running', heartbeat_at frozen at
   whenever it died. The next invocation with the SAME job+params_key
   finds that row via `find_resumable_run` and resumes it -- same run_id,
   same fetched_at -- via `start_or_resume_run`. Any OTHER row stuck at
   status='running' whose heartbeat has gone stale gets reaped by
   `reap_stale_runs` (marked 'failed', never deleted, never silently
   rewritten to 'succeeded' -- we don't actually know it finished cleanly)
   so the audit trail survives instead of being erased.

   This targets doc 08 Day 4's example bug: the original stuck row
   (raw.collector_runs id=1, from Day 3, status='running' with finished_at
   NULL) predates this module -- it has no job/params_key/heartbeat_at, so
   `reap_stale_runs` was never going to touch it, and reap would have
   marked it 'failed' regardless, not 'succeeded'. It was corrected as a
   one-off, separate from the general mechanism above: its underlying data
   (raw.sec_companyfacts/sec_submissions rows) had already been
   independently verified complete and correct during Day 3's close-out,
   so it was fixed forward to status='succeeded' with a real finished_at
   -- not deleted, and not something a future abandoned run should expect
   to happen to it automatically. See doc/learnings/day-04-retry-and-resume.md.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx
import psycopg
import structlog
from tenacity import retry_if_exception

logger = structlog.get_logger()

# --- 1. Shared retry predicate --------------------------------------------


def is_retryable_http_error(exc: BaseException) -> bool:
    """True for transient network errors and 429/5xx responses -- the
    doc 07 §3 "retry with backoff, don't alarm immediately" cases. Anything
    else (4xx other than 429, a bad User-Agent causing a 403, etc.) is a
    real failure and should surface, not be swallowed by retries.
    """
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False


HTTP_RETRY = retry_if_exception(is_retryable_http_error)


# --- 2. Idempotency key: checkpoint queries --------------------------------


def already_stored_companyfacts_ciks(conn: psycopg.Connection, run_id: int) -> set[str]:
    """CIKs already stored under this run_id -- the skip-set for a resumed
    companyfacts pass. Keyed on run_id (not fetched_at) since run_id is now
    recorded on every insert going forward; pre-Day-4 rows have run_id NULL
    and are simply outside any resumable run's scope."""
    with conn.cursor() as cur:
        cur.execute("select cik from raw.sec_companyfacts where run_id = %s", (run_id,))
        return {row[0] for row in cur.fetchall()}


def already_stored_submission_paths(conn: psycopg.Connection, run_id: int) -> set[str]:
    """storage_paths already stored under this run_id -- the skip-set for a
    resumed submissions pass. Per-file, not per-cik, because a large
    filer's continuation pages (doc 08's JPM case: 1 base + 69 continuation
    files) must each be individually checkpointed -- a resume shouldn't
    re-fetch the 50 files already stored just because the 51st wasn't."""
    with conn.cursor() as cur:
        cur.execute(
            "select storage_path from raw.sec_submissions where run_id = %s", (run_id,)
        )
        return {row[0] for row in cur.fetchall()}


# --- 3. Run lifecycle: start/resume, heartbeat, finish, reap ---------------


@dataclass
class RunContext:
    run_id: int
    fetched_at: datetime
    resumed: bool


def make_params_key(
    only_ciks: set[str] | None, limit: int | None, extra: str | None = None
) -> str:
    """Deterministic string identifying an invocation's filters, so a
    resume only ever matches an invocation with the SAME scope -- rerunning
    `companyfacts --ciks A,B` never resumes a stuck `companyfacts` (full
    universe) run and vice versa.

    `extra` (Day 5): lets a caller fold additional scope into the key
    without this function needing to know what job it's for -- e.g.
    `jobs/incremental.py` includes the target date, so re-running for a
    DIFFERENT date never resumes a stuck run left over from a different
    day's index."""
    ciks_part = ",".join(sorted(only_ciks)) if only_ciks else "ALL"
    key = f"ciks={ciks_part}|limit={limit}"
    if extra:
        key = f"{key}|{extra}"
    return key


DEFAULT_STALE_AFTER = timedelta(hours=2)


def reap_stale_runs(
    conn: psycopg.Connection,
    stale_after: timedelta = DEFAULT_STALE_AFTER,
    exclude_run_id: int | None = None,
) -> list[int]:
    """Marks any status='running' row whose heartbeat (or started_at, if it
    never got a heartbeat) is older than `stale_after` as 'failed' with an
    explanatory note in `stats`. Never deletes a row and never guesses
    'succeeded' -- we genuinely don't know whether an abandoned run finished
    cleanly, so 'failed' (this run attempt didn't reach a clean finish) is
    the honest state. The underlying sec_companyfacts/sec_submissions rows
    it already wrote are untouched -- they're valid lossless data regardless
    of whether the bookkeeping row ever closed out.
    """
    threshold = datetime.now(timezone.utc) - stale_after
    with conn.cursor() as cur:
        cur.execute(
            """
            select id from raw.collector_runs
            where status = 'running'
              and coalesce(heartbeat_at, started_at) < %s
              and (%s::bigint is null or id != %s)
            """,
            (threshold, exclude_run_id, exclude_run_id),
        )
        stale_ids = [row[0] for row in cur.fetchall()]
        for run_id in stale_ids:
            cur.execute(
                """
                update raw.collector_runs
                set status = 'failed',
                    finished_at = %s,
                    stats = stats || %s::jsonb
                where id = %s
                """,
                (
                    datetime.now(timezone.utc),
                    json.dumps(
                        {
                            "reaped": True,
                            "reap_reason": (
                                "abandoned: status='running' with no heartbeat/finish "
                                f"within {stale_after}, consistent with the process "
                                "having been killed mid-run"
                            ),
                        }
                    ),
                    run_id,
                ),
            )
    conn.commit()
    if stale_ids:
        logger.warning(
            "collector_runs.reaped", run_ids=stale_ids, stale_after=str(stale_after)
        )
    return stale_ids


def find_resumable_run(
    conn: psycopg.Connection, job: str, params_key: str
) -> tuple[int, datetime] | None:
    """A running row for the exact same (job, params_key) is resumable
    regardless of age -- if you're rerunning the identical command, you
    want to continue that exact logical unit of work. (A stray second
    concurrent invocation of the same command is a known, accepted
    limitation for a solo-operator CLI tool -- see
    doc/learnings/day-04-retry-and-resume.md.)"""
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, fetched_at from raw.collector_runs
            where job = %s and params_key = %s and status = 'running'
            order by id desc
            limit 1
            """,
            (job, params_key),
        )
        row = cur.fetchone()
        return (row[0], row[1]) if row else None


def start_or_resume_run(
    conn: psycopg.Connection,
    job: str,
    only_ciks: set[str] | None = None,
    limit: int | None = None,
    force_fresh: bool = False,
    stale_after: timedelta = DEFAULT_STALE_AFTER,
    run_type: str = "bootstrap",
    extra_params: str | None = None,
) -> RunContext:
    """Entry point for every bootstrap/incremental sub-command. Order matters:

    1. Look for a resumable row for this exact job+params. If found (and
       not force_fresh), resume it -- reuse run_id and fetched_at so any
       company this pass re-touches gets the same storage_path as before.
    2. Otherwise, reap anything ELSE stuck at 'running' past the staleness
       threshold (cleans up abandoned rows that will never be resumed
       because nobody will invoke their exact params again).
    3. Start a fresh row.

    `run_type` (Day 5): raw.collector_runs.run_type is constrained to
    'bootstrap'|'incremental' (db/migrations/0001_raw_schema.sql). Every
    Day 2-4 caller is a bootstrap job, so this defaults to 'bootstrap' for
    them unchanged; jobs/incremental.py is the first caller to pass
    'incremental'. `extra_params` folds into the resume key via
    make_params_key -- e.g. the target date, so incremental runs for
    different dates never resume each other's row.
    """
    params_key = make_params_key(only_ciks, limit, extra=extra_params)
    if not force_fresh:
        found = find_resumable_run(conn, job, params_key)
        if found:
            run_id, fetched_at = found
            _touch_heartbeat(conn, run_id)
            logger.info(
                "collector_runs.resumed", run_id=run_id, job=job, params_key=params_key
            )
            return RunContext(run_id=run_id, fetched_at=fetched_at, resumed=True)

    reap_stale_runs(conn, stale_after=stale_after)

    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.collector_runs
                (run_type, started_at, status, job, params_key, fetched_at, heartbeat_at, stats)
            values (%s, %s, 'running', %s, %s, %s, %s, '{}'::jsonb)
            returning id
            """,
            (run_type, now, job, params_key, now, now),
        )
        run_id = cur.fetchone()[0]
    conn.commit()
    logger.info(
        "collector_runs.started",
        run_id=run_id,
        job=job,
        params_key=params_key,
        run_type=run_type,
    )
    return RunContext(run_id=run_id, fetched_at=now, resumed=False)


def _touch_heartbeat(conn: psycopg.Connection, run_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "update raw.collector_runs set heartbeat_at = %s where id = %s",
            (datetime.now(timezone.utc), run_id),
        )
    conn.commit()


class HeartbeatTicker:
    """Touches the run's heartbeat every `every_n` successfully stored
    items, so `reap_stale_runs` can tell "still actively making progress"
    apart from "died N hours into a long full-universe pass". Every-N
    rather than every-item to avoid an extra UPDATE per company on an
    ~8,000-company run."""

    def __init__(self, conn: psycopg.Connection, run_id: int, every_n: int = 10):
        self._conn = conn
        self._run_id = run_id
        self._every_n = every_n
        self._count = 0

    def tick(self) -> None:
        self._count += 1
        if self._count % self._every_n == 0:
            _touch_heartbeat(self._conn, self._run_id)

    def flush(self) -> None:
        _touch_heartbeat(self._conn, self._run_id)


def finish_run(conn: psycopg.Connection, run_id: int, status: str, stats: dict) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            update raw.collector_runs
            set finished_at = %s, status = %s, stats = stats || %s::jsonb
            where id = %s
            """,
            (datetime.now(timezone.utc), status, json.dumps(stats), run_id),
        )
    conn.commit()
