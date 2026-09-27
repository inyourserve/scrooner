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
