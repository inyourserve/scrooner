"""Stage 4a-1 -- Identity fields (doc 13). Parses sic/sicDescription/
stateOfIncorporation/entityType/category out of each company's already-
stored raw.sec_submissions base-file payload into core.company. No new SEC
fetch -- these fields are already sitting in Storage, discarded by the
Normalizer's identity.py (Stage 2a), which only ever pulled name/
fiscalYearEnd/tickers/exchanges from the same payload.

Read-only against `raw`, writes only to `core.company` -- same boundary
discipline as every prior phase.
"""

import json

import psycopg
import structlog

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix

logger = structlog.get_logger()


def _latest_base_submission(conn: psycopg.Connection, cik: str) -> str | None:
    """storage_path of the most recent BASE submissions file for this CIK
    (excludes -NNN.json continuation pages, which carry no entity metadata
    -- only filings.recent-style data). Mirrors normalizer/identity.py's own
    _latest_submission_files, narrowed to the one file that has what this
    stage needs."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select storage_path
            from raw.sec_submissions
            where cik = %s
              and fetched_at = (select max(fetched_at) from raw.sec_submissions where cik = %s)
              and storage_path not like '%%-submissions-%%.json'
            order by storage_path
            limit 1
            """,
            (cik, cik),
        )
        row = cur.fetchone()
        return row[0] if row else None


def _load_json(storage: SupabaseStorageClient, storage_path: str) -> dict:
    raw_bytes = storage.download(strip_bucket_prefix(storage_path))
    return json.loads(raw_bytes)


def load_identity_fields(storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str) -> dict | None:
    storage_path = _latest_base_submission(conn, cik)
    if storage_path is None:
        logger.warning("company_master.identity.no_base_submission", cik=cik)
        return None
    payload = _load_json(storage, storage_path)
    return {
        "cik": cik,
        "sic_code": payload.get("sic") or None,
        "sic_description": payload.get("sicDescription") or None,
        "state_of_incorporation": payload.get("stateOfIncorporation") or None,
        "entity_type": payload.get("entityType") or None,
        "filer_category": payload.get("category") or None,
    }


def update_identity_fields(conn: psycopg.Connection, rows: list[dict]) -> int:
    """Batch update -- load-then-write, never a query per company (doc 04's
    correctness controls)."""
    if not rows:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            """
            update core.company
               set sic_code = %(sic_code)s,
                   sic_description = %(sic_description)s,
                   state_of_incorporation = %(state_of_incorporation)s,
                   entity_type = %(entity_type)s,
                   filer_category = %(filer_category)s
             where cik = %(cik)s
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def update_identity(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "no_data": 0}
    rows: list[dict] = []
    with SupabaseStorageClient() as storage:
        for cik in sorted(ciks):
            stats["considered"] += 1
            fields = load_identity_fields(storage, conn, cik)
            if fields is None:
                stats["no_data"] += 1
                continue
            rows.append(fields)
            stats["ok"] += 1
    updated = update_identity_fields(conn, rows)
    logger.info("company_master.identity.done", updated=updated, **stats)
    return stats
