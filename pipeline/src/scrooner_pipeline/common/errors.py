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

logger = structlog.get_logger()

_ERROR_TABLES = {"core.normalizer_error", "analytics.mapper_error"}


def log_error(conn: psycopg.Connection, table: str, cik: str, stage: str, exc: Exception) -> None:
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
