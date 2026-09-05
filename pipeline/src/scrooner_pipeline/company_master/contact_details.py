"""Company contact details (2026-08-29 zero-new-fetch coverage pass, items
5/6). Parses ein/addresses.business/phone out of each company's already-
stored raw.sec_submissions base-file payload into core.company -- same
source and same _latest_base_submission lookup as identity.py's
sic/stateOfIncorporation/entityType/category, just reading a few more keys
off the same JSON object already downloaded there. No new SEC fetch.

Checked live before writing this (see 0023_company_contact_details.sql):
dei:EntityTaxIdentificationNumber and the cover-page address/phone dei tags
are NOT in core.fact/core.concept at all -- SEC's bulk Company Facts API
only carries facts with a quantitative unit, and these are unitless text
fields. The real source is this file's own payload (submissions.json), a
genuinely different SEC endpoint from companyfacts.json.

business address preferred over mailing -- checked live, identical for
every golden company that has both (AAPL, MSFT, JPM, GOOGL all show the
same street1/city/state/zip in both), business is the more standard
"registered contact" field for company-identity purposes.

TSM/ENB (foreign private issuers) correctly get ein="000000000" as
submissions.json itself reports it -- a real placeholder EDGAR uses for a
filer with no US EIN, not a parsing bug; left as-is rather than nulled,
same "don't guess, don't silently improve on what the source actually
says" discipline as everywhere else in this project."""

import json

import psycopg
import structlog

from scrooner_pipeline.collector.storage import SupabaseStorageClient, strip_bucket_prefix

logger = structlog.get_logger()


def _latest_base_submission(conn: psycopg.Connection, cik: str) -> str | None:
    """Same lookup as identity.py's _latest_base_submission -- kept as its
    own copy rather than a shared import, matching this project's existing
    pattern of small per-module duplication over a premature shared helper
    (see security_type.py/shares_outstanding_fallback.py, same shape)."""
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


def _extract_contact_fields(cik: str, payload: dict) -> dict:
    """Pure extraction, no DB/storage -- kept separate so it's testable
    directly with a real-shaped payload fragment, same pattern as
    normalizer/identity.py's _parse_filings_block."""
    business = (payload.get("addresses") or {}).get("business") or {}
    return {
        "cik": cik,
        "ein": payload.get("ein") or None,
        "business_address_line1": business.get("street1") or None,
        "business_address_city": business.get("city") or None,
        "business_address_state": business.get("stateOrCountry") or None,
        "business_address_zip": business.get("zipCode") or None,
        "business_phone": payload.get("phone") or None,
    }


def load_contact_fields(storage: SupabaseStorageClient, conn: psycopg.Connection, cik: str) -> dict | None:
    storage_path = _latest_base_submission(conn, cik)
    if storage_path is None:
        logger.warning("company_master.contact_details.no_base_submission", cik=cik)
        return None
    payload = _load_json(storage, storage_path)
    return _extract_contact_fields(cik, payload)


def update_contact_fields(conn: psycopg.Connection, rows: list[dict]) -> int:
    """Batch update -- load-then-write, never a query per company (doc 04's
    correctness controls)."""
    if not rows:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            """
            update core.company
               set ein = %(ein)s,
                   business_address_line1 = %(business_address_line1)s,
                   business_address_city = %(business_address_city)s,
                   business_address_state = %(business_address_state)s,
                   business_address_zip = %(business_address_zip)s,
                   business_phone = %(business_phone)s
             where cik = %(cik)s
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def update_contact_details(conn: psycopg.Connection, ciks: set[str]) -> dict:
    stats = {"considered": 0, "ok": 0, "no_data": 0}
    rows: list[dict] = []
    with SupabaseStorageClient() as storage:
        for cik in sorted(ciks):
            stats["considered"] += 1
            fields = load_contact_fields(storage, conn, cik)
            if fields is None:
                stats["no_data"] += 1
                continue
            rows.append(fields)
            stats["ok"] += 1
    updated = update_contact_fields(conn, rows)
    logger.info("company_master.contact_details.done", updated=updated, **stats)
    return stats
