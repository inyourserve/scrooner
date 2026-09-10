"""Stage 5f -- Precomputed screening snapshot (doc/faster-loading/fast.md,
2026-09-10; migration 0061). Builds analytics.company_screening_snapshot
from analytics.metric_value, reusing resolve.py's own TTM-preferred/
latest-period_end "most recent value" rule unchanged -- this module runs
that rule once for every metric, instead of once per request.

Root cause this closes, measured live before writing any of this (not
assumed from fast.md's own guess of "recomputing from raw filing
tables" -- that guess was wrong): EXPLAIN ANALYZE on the exact query
resolve_most_recent_values runs showed the real cost is a Bitmap Heap
Scan against metric_value (11M rows across 82 metrics) touching ~16,000
cold heap pages to pull ~205K raw rows for a SINGLE metric, because rows
for one metric_definition_id are scattered across the table's whole
physical storage -- not an unindexed query. See
doc/learnings/2026-09-10-screener-performance.md.

Full rebuild only, no incremental mode -- metric_value itself is only
ever refreshed by a full Mapper run (no incremental reprocessing chain
exists yet, per root CLAUDE.md's "no scheduled reprocessing chain" gap),
so a snapshot rebuild is already at most a once-daily job, cheap
relative to that. One transaction: read the current dataset_version,
delete-then-reinsert every row under the NEXT version, bump the counter,
commit together -- a crash mid-build leaves the previous, fully-served
snapshot untouched (same all-or-nothing shape as every other
delete-then-reinsert writer in this codebase).
"""

import psycopg
import structlog

from scrooner_pipeline.screener.resolve import resolve_most_recent_values

logger = structlog.get_logger()

INSERT_BATCH_SIZE = 5000


def _load_all_metric_definition_ids(conn: psycopg.Connection) -> list[int]:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.metric_definition where status = 'active'")
        return [row[0] for row in cur.fetchall()]


def _next_dataset_version(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("select version from analytics.screening_dataset_version where id = true")
        (current,) = cur.fetchone()
    return current + 1


def build_snapshot(conn: psycopg.Connection) -> dict:
    metric_ids = _load_all_metric_definition_ids(conn)
    resolved = resolve_most_recent_values(conn, metric_ids)
    dataset_version = _next_dataset_version(conn)

    rows = [
        (
            company_id,
            metric_id,
            data["value"],
            data["period_label"],
            data["period_end"],
            data["formula_version"],
            dataset_version,
        )
        for (company_id, metric_id), data in resolved.items()
    ]

    with conn.cursor() as cur:
        cur.execute("delete from analytics.company_screening_snapshot")
        for start in range(0, len(rows), INSERT_BATCH_SIZE):
            cur.executemany(
                """
                insert into analytics.company_screening_snapshot
                    (company_id, metric_definition_id, value, period_label,
                     period_end, formula_version, dataset_version)
                values (%s, %s, %s, %s, %s, %s, %s)
                """,
                rows[start : start + INSERT_BATCH_SIZE],
            )
        cur.execute(
            "update analytics.screening_dataset_version set version = %s, updated_at = now() where id = true",
            (dataset_version,),
        )
    conn.commit()

    logger.info(
        "screener.snapshot.built",
        metric_count=len(metric_ids),
        row_count=len(rows),
        dataset_version=dataset_version,
    )
    return {"dataset_version": dataset_version, "row_count": len(rows), "metric_count": len(metric_ids)}


def get_dataset_version(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("select version from analytics.screening_dataset_version where id = true")
        (version,) = cur.fetchone()
    return version
