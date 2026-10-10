from contextlib import contextmanager
from typing import Any, Callable, Iterator

import psycopg
import structlog

from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    with psycopg.connect(settings.database_url) as conn:
        yield conn


def run_tolerating_exit_commit_failure(
    stage: str, fn: Callable[[psycopg.Connection], Any], *, default: Any = None
) -> Any:
    """Runs `fn(conn)` inside a fresh `get_connection()`, tolerating the
    connection having gone dead by the time the `with` block's own
    implicit commit/close runs -- AFTER `fn` already completed and
    returned successfully.

    This matters for any CLI command whose `fn` is a long-running batch
    that loops over many companies, each committing through its OWN
    separate connection (see e.g. ownership/insider.py's
    `_run_company_with_timeout`) -- the outer connection this function
    opens sits idle for the entire run, and a Supabase pooler can drop an
    idle connection over a multi-hour job. Without this, psycopg's
    implicit commit-on-exit raises `OperationalError` well after the real
    work already finished cleanly, making a fully-successful run report
    as a crash. Found live 2026-09-16 in ownership/beneficial_ownership.py
    and mapper/concept_fallback.py's CLI wrappers, fixed there by hand
    first; centralized here so a third (or later) long-running command
    gets the same guarantee from one call instead of a third copy of the
    same six lines.

    Returns whatever `fn` returned, or `default` if the connection died
    before `fn` ever got a chance to run.
    """
    result = default
    try:
        with get_connection() as conn:
            result = fn(conn)
    except psycopg.OperationalError:
        logger.warning(f"{stage}.exit_commit_failed", result=result)
    return result


def run_write_with_reconnect(
    conn: psycopg.Connection,
    write: Callable[[psycopg.Connection], Any],
    *,
    stage: str,
    attempts: int = 3,
) -> Any:
    """Runs `write(conn)`, retrying on a FRESH connection if the pooler drops
    the original mid-write.

    For the "compute for minutes, then write everything in one transaction"
    shape: the connection sits idle (or reading) through the computation, and
    by the time the bulk `executemany` runs the pooler has killed it
    ("SSL SYSCALL error: Connection timed out"). Found live 2026-10-09 in
    three nightly jobs at once -- the screener snapshot build, the time-series
    check and the plausibility check -- each of which failed the whole job.

    `write` MUST be safe to repeat: one transaction that clears what it is
    about to insert (all three are delete-then-insert), so a half-finished
    attempt can neither double-write nor leave a partial result behind.
    The caller's connection is used for the first attempt and never closed
    here; connections this function opens are always closed.
    """
    attempt_conn = conn
    for attempt in range(1, attempts + 1):
        try:
            return write(attempt_conn)
        except psycopg.OperationalError as exc:
            logger.warning(
                f"{stage}.write_retry",
                attempt=attempt,
                of=attempts,
                error=str(exc)[:200],
            )
            if attempt == attempts:
                raise
        finally:
            if attempt_conn is not conn:
                try:
                    attempt_conn.close()
                except Exception:
                    pass
        attempt_conn = psycopg.connect(settings.database_url)
    raise AssertionError("unreachable")  # pragma: no cover
