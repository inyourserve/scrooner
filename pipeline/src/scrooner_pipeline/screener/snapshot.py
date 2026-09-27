"""Stage 5f -- Precomputed screening snapshot (doc/faster-loading/fast.md,
2026-09-10; migration 0061, rebuilt as a wide table 2026-09-20 by
migration 0068). Builds analytics.company_screening_snapshot from
analytics.metric_value, reusing resolve.py's own TTM-preferred/latest-
period_end "most recent value" rule unchanged -- this module runs that
rule once for every metric, instead of once per request.

Root cause this closes, measured live before writing any of this (not
assumed from fast.md's own guess of "recomputing from raw filing
tables" -- that guess was wrong): EXPLAIN ANALYZE on the exact query
resolve_most_recent_values runs showed the real cost is a Bitmap Heap
Scan against metric_value (11M rows across 82 metrics) touching ~16,000
cold heap pages to pull ~205K raw rows for a SINGLE metric, because rows
for one metric_definition_id are scattered across the table's whole
physical storage -- not an unindexed query. See
doc/learnings/2026-09-10-screener-performance.md.

Rebuilt as a wide (one row per company) shape 2026-09-20 -- see migration
0068's own comment for the full before/after evidence, including a
REJECTED first attempt (a single `metrics jsonb` blob per row) that
measured WORSE than the original EAV table once TOAST decompression cost
was accounted for. Each metric_definition instead gets its own native
columns (`"<name>"`, `"<name>__period_label"`, `"<name>__period_end"`,
`"<name>__formula_version"`), added dynamically by `_ensure_metric_
columns()` below -- `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` is a fast,
metadata-only operation for a nullable column with no default, so a new
metric_definition needs no manual migration, resolving 0061's own
original reason for choosing EAV in the first place without paying its
join-per-predicate cost or the JSONB attempt's parse-per-row cost.

Full rebuild only, no incremental mode -- metric_value itself is only
ever refreshed by a full Mapper run (no incremental reprocessing chain
exists yet, per root CLAUDE.md's "no scheduled reprocessing chain" gap),
so a snapshot rebuild is already at most a once-daily job, cheap
relative to that. One transaction: read the current dataset_version,
insert every row under the NEXT version, bump the counter, prune old
versions, commit together -- a crash mid-build leaves the previous,
fully-served snapshot untouched. Since migration 0074 the table holds
several versions side by side (PK (dataset_version, company_id)); every
reader filters on one dataset_version.
"""

import re

import psycopg
import structlog
from psycopg import sql

from scrooner_pipeline.screener.resolve import resolve_most_recent_values

logger = structlog.get_logger()

INSERT_BATCH_SIZE = 5000

# Snapshot versions retained after a rebuild (~10 MB each). Screen runs
# store only matched company IDs and read values from their own version
# (migration 0074), so a version must outlive the runs that point at it.
KEEP_VERSIONS = 3

# metric_name always comes from this project's own analytics.metric_
# definition registry, never end-user input -- but every value derived
# from it is used to build a SQL identifier below, so it's validated
# defensively anyway rather than trusted implicitly. Every real metric
# name in this codebase already matches this (lowercase snake_case).
_SAFE_METRIC_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _validate_metric_name(name: str) -> str:
    if not _SAFE_METRIC_NAME_RE.match(name):
        raise ValueError(
            f"metric_name {name!r} is not a safe SQL identifier -- refusing to build a column from it"
        )
    return name


def _metric_columns(
    name: str,
) -> tuple[sql.Identifier, sql.Identifier, sql.Identifier, sql.Identifier]:
    """(value, period_label, period_end, formula_version) column
    identifiers for one metric. Double-underscore separator -- every real
    metric_name in this codebase uses single underscores as its own word
    separator, so this can never collide with a real metric's own name."""
    _validate_metric_name(name)
    return (
        sql.Identifier(name),
        sql.Identifier(f"{name}__period_label"),
        sql.Identifier(f"{name}__period_end"),
        sql.Identifier(f"{name}__formula_version"),
    )


def _ensure_metric_columns(conn: psycopg.Connection, metric_names: list[str]) -> None:
    """Idempotent: ADD COLUMN IF NOT EXISTS for every active metric, every
    rebuild. A no-op (metadata-only check) for a column that already
    exists; a fast, metadata-only ALTER for one that doesn't (a nullable
    column with no default never rewrites the table in Postgres) -- this
    is what lets a brand-new metric_definition reach the snapshot with
    zero manual migration, the same guarantee migration 0061's original
    EAV design was built to provide."""
    parts = []
    for name in metric_names:
        value_col, period_label_col, period_end_col, formula_version_col = (
            _metric_columns(name)
        )
        parts.append(sql.SQL("add column if not exists {} numeric").format(value_col))
        parts.append(
            sql.SQL("add column if not exists {} text").format(period_label_col)
        )
        parts.append(sql.SQL("add column if not exists {} date").format(period_end_col))
        parts.append(
            sql.SQL("add column if not exists {} integer").format(formula_version_col)
        )
    if not parts:
        return
    statement = sql.SQL("alter table analytics.company_screening_snapshot {}").format(
        sql.SQL(", ").join(parts)
    )
    with conn.cursor() as cur:
        cur.execute(statement)


def _load_all_metric_definitions(conn: psycopg.Connection) -> dict[int, str]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, metric_name from analytics.metric_definition where status = 'active'"
        )
        return dict(cur.fetchall())


def _load_company_identity(conn: psycopg.Connection) -> dict[int, dict]:
    """Every company (active and inactive) -- an inactive one still needs a
    row so `include_inactive=True` queries and `excluded_inactive` reporting
    keep working exactly as before. The ticker subquery runs once per
    rebuild here, not once per screen request -- the whole point of this
    module existing."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.id, c.cik, c.company_name, c.sic_code, c.sic_description, c.sector, c.status,
                   (select l.ticker from core.listing l where l.company_id = c.id
                    and l.effective_to is null order by l.id limit 1) as ticker
            from core.company c
            """
        )
        rows = cur.fetchall()
    return {
        row[0]: {
            "cik": row[1],
            "company_name": row[2],
            "sic_code": row[3],
            "sic_description": row[4],
            "sector": row[5],
            "status": row[6],
            "ticker": row[7],
        }
        for row in rows
    }


def _next_dataset_version(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "select version from analytics.screening_dataset_version where id = true"
        )
        (current,) = cur.fetchone()
    return current + 1


def _prune_old_versions(cur: psycopg.Cursor, current_version: int) -> int:
    """Delete snapshot versions no screen run can still need: keep the
    latest KEEP_VERSIONS plus every version a saved screen's last run was
    computed on (a saved screen must keep rendering the exact values it
    matched on). An unsaved run on a pruned version returns 410 and is
    simply rerun (apps/backend/routers/screen_runs.py)."""
    cur.execute(
        """
        delete from analytics.company_screening_snapshot s
        where s.dataset_version <= %s
          and s.dataset_version not in (
              select r.dataset_version
              from app.saved_screen saved
              join app.user_screen_run u on u.id = saved.last_run_id
              join app.screen_result r on r.id = u.screen_result_id
          )
        """,
        (current_version - KEEP_VERSIONS,),
    )
    return cur.rowcount


def build_snapshot(conn: psycopg.Connection) -> dict:
    id_to_name = _load_all_metric_definitions(conn)
    metric_names = sorted(id_to_name.values())
    _ensure_metric_columns(conn, metric_names)

    resolved = resolve_most_recent_values(conn, list(id_to_name.keys()))
    identity = _load_company_identity(conn)
    dataset_version = _next_dataset_version(conn)

    metrics_by_company: dict[int, dict[str, dict]] = {}
    for (company_id, metric_id), data in resolved.items():
        metrics_by_company.setdefault(company_id, {})[id_to_name[metric_id]] = data

    identity_columns = [
        sql.Identifier("company_id"),
        sql.Identifier("cik"),
        sql.Identifier("company_name"),
        sql.Identifier("sic_code"),
        sql.Identifier("sic_description"),
        sql.Identifier("sector"),
        sql.Identifier("status"),
        sql.Identifier("ticker"),
        sql.Identifier("dataset_version"),
    ]
    metric_column_list: list[sql.Identifier] = []
    for name in metric_names:
        metric_column_list.extend(_metric_columns(name))

    all_columns = identity_columns + metric_column_list
    placeholders = sql.SQL(", ").join(sql.Placeholder() * len(all_columns))
    insert_statement = sql.SQL(
        "insert into analytics.company_screening_snapshot ({}) values ({})"
    ).format(sql.SQL(", ").join(all_columns), placeholders)

    rows = []
    for company_id, info in identity.items():
        row = [
            company_id,
            info["cik"],
            info["company_name"],
            info["sic_code"],
            info["sic_description"],
            info["sector"],
            info["status"],
            info["ticker"],
            dataset_version,
        ]
        company_metrics = metrics_by_company.get(company_id, {})
        for name in metric_names:
            data = company_metrics.get(name)
            if data is None:
                row.extend([None, None, None, None])
            else:
                row.extend(
                    [
                        data["value"],
                        data["period_label"],
                        data["period_end"],
                        data["formula_version"],
                    ]
                )
        rows.append(tuple(row))

    with conn.cursor() as cur:
        # Rows for this exact version can only exist from an earlier,
        # crashed-then-committed attempt; clearing them keeps a rerun safe.
        cur.execute(
            "delete from analytics.company_screening_snapshot where dataset_version = %s",
            (dataset_version,),
        )
        for start in range(0, len(rows), INSERT_BATCH_SIZE):
            cur.executemany(insert_statement, rows[start : start + INSERT_BATCH_SIZE])
        cur.execute(
            "update analytics.screening_dataset_version set version = %s, updated_at = now() where id = true",
            (dataset_version,),
        )
        pruned = _prune_old_versions(cur, dataset_version)
    conn.commit()

    logger.info(
        "screener.snapshot.built",
        metric_count=len(id_to_name),
        row_count=len(rows),
        dataset_version=dataset_version,
        pruned_rows=pruned,
    )
    return {
        "dataset_version": dataset_version,
        "row_count": len(rows),
        "metric_count": len(id_to_name),
    }


def get_dataset_version(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "select version from analytics.screening_dataset_version where id = true"
        )
        (version,) = cur.fetchone()
    return version
