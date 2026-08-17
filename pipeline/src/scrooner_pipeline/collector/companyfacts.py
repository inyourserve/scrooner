"""Module 3 — SEC Company Facts Collector (doc 06). Bootstraps from the
bulk companyfacts.zip (doc 07 §5) rather than one HTTP call per CIK, per
doc 07's "prefer bulk over per-company hammering" rule. Streams the zip to
disk (never holds the ~1.4GB archive in memory) and streams each company's
JSON out to Supabase Storage one at a time — doc 08's Day 3 practical note.

Stores exactly what SEC published, byte for byte. No parsing of `facts`,
no picking a taxonomy, no deciding what a tag means — that's the
Normalizer's job, not this one.

Verified live against the real archive 2026-08-14: every member is named
CIK##########.json (10-digit, zero-padded), one file per CIK, no
pagination (contrast with submissions.zip — see submissions.py).

Day 4: `fetched_at` and `run_id` are supplied by the caller (from
collector.retry.start_or_resume_run) rather than computed here, so a
resumed run reuses the exact same fetched_at -- and therefore the exact
same storage_path per company -- as the run it's continuing. Before doing
any work, the set of CIKs already stored under this run_id is fetched and
skipped entirely (no re-download, no re-upload, no re-insert) -- that's
the actual checkpoint. See collector/retry.py for why storage_path (not
just `cik`) is the right idempotency key given the append-only design.
"""

import hashlib
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import psycopg
import structlog

from scrooner_pipeline.collector.retry import HeartbeatTicker, already_stored_companyfacts_ciks
from scrooner_pipeline.collector.storage import SupabaseStorageClient
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

BULK_URL = "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"
_MEMBER_RE = re.compile(r"^CIK(\d{10})\.json$")


def _iter_members(zip_path: Path) -> Iterator[tuple[str, bytes]]:
    """Yields (cik, raw_bytes) for every company in the bulk archive."""
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            m = _MEMBER_RE.match(name)
            if not m:
                # Not expected as of 2026-08-14 (every member checked
                # matches CIK##########.json) but don't silently skip
                # something unrecognized — a future SEC format change
                # should be visible, not quietly drop companies.
                logger.warning("companyfacts.unrecognized_member", name=name)
                continue
            yield m.group(1), zf.read(name)


def bootstrap_companyfacts(
    conn: psycopg.Connection,
    fetched_at: datetime,
    run_id: int,
    only_ciks: set[str] | None = None,
    limit: int | None = None,
) -> dict:
    """Downloads companyfacts.zip once, then for every company (or every
    company in only_ciks, if given — used for golden-company/sample runs,
    not a scope reduction of what this collector supports) stores the raw
    payload to Supabase Storage and records metadata + SHA-256 in
    raw.sec_companyfacts. Append-only across genuinely separate runs: a
    fresh run_id/fetched_at always inserts new rows even for a company
    already stored under a DIFFERENT run. Within THIS run_id, already-
    stored CIKs are checkpointed and skipped -- that's what makes a
    kill-and-resume of the same invocation safe.

    run_id is always required now (Day 4) -- every insert records which run
    produced it, both for checkpointing and for provenance (doc 05's
    traceability principle: know exactly which run wrote which row).
    """
    stats = {"considered": 0, "stored": 0, "skipped": 0, "errors": 0, "not_in_archive": 0}
    already_done = already_stored_companyfacts_ciks(conn, run_id)
    if already_done:
        logger.info("companyfacts.resume.checkpoint", run_id=run_id, already_done=len(already_done))

    seen_ciks: set[str] = set()

    with SECClient() as sec:
        zip_path = sec.get_cached_bulk_zip(BULK_URL, cache_name="companyfacts")
    logger.info("companyfacts.zip_ready", path=str(zip_path), size_bytes=zip_path.stat().st_size)

    fetched_at_iso = fetched_at.isoformat()
    heartbeat = HeartbeatTicker(conn, run_id)

    with SupabaseStorageClient() as storage, conn.cursor() as cur:
        for cik, payload in _iter_members(zip_path):
            if only_ciks is not None and cik not in only_ciks:
                continue
            seen_ciks.add(cik)
            stats["considered"] += 1
            if limit is not None and stats["stored"] >= limit:
                break
            if cik in already_done:
                stats["skipped"] += 1
                continue
            try:
                sha256 = hashlib.sha256(payload).hexdigest()
                object_path = f"sec/companyfacts/{cik}/{fetched_at_iso}.json"
                storage_path = storage.upload(object_path, payload)
                cur.execute(
                    """
                    insert into raw.sec_companyfacts
                        (cik, fetched_at, source_url, sha256, storage_path, http_status, run_id)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    on conflict (storage_path) do nothing
                    """,
                    (cik, fetched_at, BULK_URL, sha256, storage_path, 200, run_id),
                )
                conn.commit()
                stats["stored"] += 1
                heartbeat.tick()
            except Exception as exc:
                conn.rollback()
                stats["errors"] += 1
                logger.exception("companyfacts.store_failed", cik=cik)
                cur.execute(
                    """
                    insert into raw.collector_errors
                        (run_id, cik, source, error_type, message)
                    values (%s, %s, %s, %s, %s)
                    """,
                    (run_id, cik, "companyfacts", type(exc).__name__, str(exc)[:2000]),
                )
                conn.commit()

        # A requested CIK that never appeared in the archive at all must
        # not be silently invisible -- doc 08 Day 4's "zero lost
        # companies" bar means every requested CIK is accounted for
        # somewhere (stored, skipped, errored, or explicitly here), not
        # that every request necessarily has machine-readable facts.
        if only_ciks is not None:
            missing = only_ciks - seen_ciks
            for cik in missing:
                stats["not_in_archive"] += 1
                logger.warning("companyfacts.cik_not_in_archive", cik=cik, run_id=run_id)
                cur.execute(
                    """
                    insert into raw.collector_errors
                        (run_id, cik, source, error_type, message)
                    values (%s, %s, %s, %s, %s)
                    """,
                    (
                        run_id,
                        cik,
                        "companyfacts",
                        "NotInBulkArchive",
                        f"CIK {cik} requested but not present in companyfacts.zip as of {fetched_at_iso}",
                    ),
                )
            conn.commit()
    heartbeat.flush()
    logger.info("companyfacts.bootstrap.done", **stats)
    return stats
