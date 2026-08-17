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
"""

import psycopg
import structlog

logger = structlog.get_logger()

_ERROR_TABLES = {"core.normalizer_error", "analytics.mapper_error"}


def log_error(conn: psycopg.Connection, table: str, cik: str, stage: str, exc: Exception) -> None:
    assert table in _ERROR_TABLES, f"unknown error table {table!r}"
    conn.rollback()
    logger.exception(f"{stage}.company_failed", cik=cik, stage=stage)
    with conn.cursor() as cur:
        cur.execute(
            f"insert into {table} (cik, stage, error_type, message) values (%s, %s, %s, %s)",
            (cik, stage, type(exc).__name__, str(exc)[:2000]),
        )
    conn.commit()
