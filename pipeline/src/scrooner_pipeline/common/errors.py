"""Per-company dead-letter logging shared by the Normalizer (core.normalizer_error)
and Mapper (analytics.mapper_error) -- see db/migrations/0014_pipeline_error_logs.sql.

Lives in common/ (not normalizer/ or mapper/) because it's operational
plumbing, not transformation/mapping logic -- reusing it across both layers
doesn't blur doc 04's boundary table, the same way structlog or sec_client
are already shared without either layer inheriting the other's
responsibilities.

Mirrors collector/companyfacts.py's own per-CIK try/except pattern: on
failure, roll back the poisoned transaction, log structurally, insert one
dead-letter row, commit, and let the caller continue to the next company --
one company's exception must never abort the batch.

That contract has a real gap, found live 2026-09-02: none of the 20
call sites across the Normalizer and Mapper wrap this call in its own
try/except, so when the ORIGINAL failure is the connection itself dying
(a real, intermittent Supabase pooler timeout -- see pipeline/CLAUDE.md's
"Connection reliability, Supabase side" section), this function's own
rollback()/insert/commit also raise, and that second exception was never
caught -- silently violating the "must never abort the batch" contract
this docstring already promised, crashing the entire remaining batch (up
to 15 companies) instead of just skipping the one that failed. Fixed here,
once, at the shared helper -- not at each of the 20 call sites -- so every
caller gets the real guarantee. If the connection truly is dead, every
subsequent company in the same batch will still fail (nothing here can
fix a dead connection), but each one now correctly increments the
caller's own `errored` counter and the loop keeps going, instead of one
company's failure taking the whole batch down with it.
"""

import psycopg
import structlog

from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()

_ERROR_TABLES = {"core.normalizer_error", "analytics.mapper_error"}


def log_error(
    conn: psycopg.Connection, table: str, cik: str, stage: str, exc: Exception
) -> None:
    assert table in _ERROR_TABLES, f"unknown error table {table!r}"
    logger.exception(f"{stage}.company_failed", cik=cik, stage=stage)
    try:
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute(
                f"insert into {table} (cik, stage, error_type, message) values (%s, %s, %s, %s)",
                (cik, stage, type(exc).__name__, str(exc)[:2000]),
            )
        conn.commit()
    except Exception:
        logger.warning(f"{stage}.log_error_itself_failed", cik=cik, stage=stage)


def safe_rollback(
    conn: psycopg.Connection, *, stage: str, cik: str = ""
) -> psycopg.Connection:
    """Roll back a poisoned transaction, tolerating a dead connection.

    `conn.rollback()` itself raises `psycopg.OperationalError` when the
    ORIGINAL failure that triggered this call was the connection dying (a
    real, recurring Supabase pooler drop -- see pipeline/CLAUDE.md's
    "Connection reliability, Supabase side" section) -- so a plain
    `except Exception: ... conn.rollback()` around one company's work in a
    batch loop can itself raise a SECOND, uncaught exception and crash
    every remaining company in the batch instead of just skipping the one
    that failed. Found and fixed inline, by hand, twice already
    (mapper/concept_fallback.py, ownership/beneficial_ownership.py, both
    2026-09-15/16) -- centralized here so every per-company/per-row loop
    gets the same guarantee from one call, instead of a third copy of the
    same fix.

    Returns the connection to keep using: the same one if rollback
    succeeded, or a brand-new one if the old one was dead. The caller MUST
    reassign its own `conn` variable to the return value
    (`conn = safe_rollback(conn, stage=..., cik=cik)`) -- this function
    cannot mutate a caller's local binding for it.
    """
    try:
        conn.rollback()
        return conn
    except psycopg.OperationalError:
        logger.warning(f"{stage}.connection_dropped_reconnecting", cik=cik)
        return psycopg.connect(settings.database_url)
