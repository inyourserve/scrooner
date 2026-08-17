"""Module 4 — SEC Submissions Collector (doc 06). Bootstraps from the bulk
submissions.zip, same "prefer bulk" rationale as companyfacts.py.

Verified live against the real archive 2026-08-14: unlike companyfacts.zip,
SEC splits a large filer's history across multiple files per CIK — a base
CIK##########.json plus numbered continuation pages
CIK##########-submissions-NNN.json, referenced by the base file's own
`filings.files` array. Confirmed on JPMorgan Chase (CIK 0000019617): 1 base
file + 69 continuation pages. A recent IPO (Reddit, CIK 0001713445) has
only the base file — no continuation pages, as expected for a short filing
history.

Each SEC-published file is its own fetch: one row, one Storage object, one
SHA-256. Merging a company's base file and continuation pages into one
payload would mean reshaping what SEC actually published — that crosses
into interpretation, which this Collector must not do.

Day 4: same checkpoint/resume pattern as companyfacts.py, but keyed on
storage_path (not cik) since one CIK can own many files in a single run --
a resume must skip the 50 continuation pages already stored without
skipping the 51st that wasn't, see collector/retry.py.
"""

import hashlib
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import psycopg
import structlog

from scrooner_pipeline.collector.retry import HeartbeatTicker, already_stored_submission_paths
from scrooner_pipeline.collector.storage import SupabaseStorageClient
from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

BULK_URL = "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip"
_MEMBER_RE = re.compile(r"^CIK(\d{10})(-submissions-\d+)?\.json$")


def _iter_members(zip_path: Path) -> Iterator[tuple[str, str, bytes]]:
    """Yields (cik, filename, raw_bytes) for every submissions file in the
    bulk archive — base file and every numbered continuation page."""
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            m = _MEMBER_RE.match(name)
            if not m:
                logger.warning("submissions.unrecognized_member", name=name)
                continue
            yield m.group(1), name, zf.read(name)


def bootstrap_submissions(
    conn: psycopg.Connection,
    fetched_at: datetime,
    run_id: int,
    only_ciks: set[str] | None = None,
    limit: int | None = None,
) -> dict:
    """Downloads submissions.zip once, then for every submissions file
    belonging to a company in only_ciks (or every company, if only_ciks is
    None) stores the raw payload to Supabase Storage and records metadata +
    SHA-256 in raw.sec_submissions. Append-only across separate runs, same
    as companyfacts; within THIS run_id, files already stored (by
    storage_path, which encodes cik+fetched_at+filename) are checkpointed
    and skipped.

    `limit`, when only_ciks is None, caps on distinct CIKs *represented so
    far* — approximate for a filer whose continuation pages are scattered
    through the zip's member order (they aren't sorted), since a CIK only
    counts once its first file has been stored. For a precise, complete
    fetch of a specific company's full submissions history, pass its CIK
    via only_ciks instead of relying on limit.

    run_id is always required now (Day 4) -- see companyfacts.py's
    docstring for the same provenance/checkpointing rationale.
    """
    stats = {"considered": 0, "stored": 0, "skipped": 0, "errors": 0, "not_in_archive": 0}
    already_done_paths = already_stored_submission_paths(conn, run_id)
    if already_done_paths:
        logger.info(
            "submissions.resume.checkpoint", run_id=run_id, already_done=len(already_done_paths)
        )

    with SECClient() as sec:
        zip_path = sec.get_cached_bulk_zip(BULK_URL, cache_name="submissions")
    logger.info("submissions.zip_ready", path=str(zip_path), size_bytes=zip_path.stat().st_size)

    fetched_at_iso = fetched_at.isoformat()
    # Distinct CIKs represented in already_done_paths, for `limit`'s
    # semantics (a resumed pass shouldn't re-count a CIK's `limit`
    # budget for files it already stored before the kill).
    # storage_path shape: raw/sec/submissions/{cik}/{fetched_at_iso}/{filename}
    stored_ciks: set[str] = {p.split("/")[3] for p in already_done_paths if p.count("/") >= 5}
    heartbeat = HeartbeatTicker(conn, run_id)
    seen_ciks: set[str] = set()

    with SupabaseStorageClient() as storage, conn.cursor() as cur:
        for cik, filename, payload in _iter_members(zip_path):
            if only_ciks is not None and cik not in only_ciks:
                continue
            seen_ciks.add(cik)
            if limit is not None and len(stored_ciks) >= limit and cik not in stored_ciks:
                continue
            stats["considered"] += 1
            # Nested under a fetched_at folder (not a single
            # {fetched_at}.json leaf like companyfacts) because one
            # CIK can own multiple SEC-published files in a single
            # fetch — a flat path would let a large filer's
            # continuation pages overwrite each other in Storage.
            object_path = f"sec/submissions/{cik}/{fetched_at_iso}/{filename}"
            storage_path = f"raw/{object_path}"
            if storage_path in already_done_paths:
                stats["skipped"] += 1
                continue
            try:
                sha256 = hashlib.sha256(payload).hexdigest()
                storage_path = storage.upload(object_path, payload)
                cur.execute(
                    """
                    insert into raw.sec_submissions
                        (cik, fetched_at, source_url, sha256, storage_path, http_status, run_id)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    on conflict (storage_path) do nothing
                    """,
                    (cik, fetched_at, BULK_URL, sha256, storage_path, 200, run_id),
                )
                conn.commit()
                stats["stored"] += 1
                stored_ciks.add(cik)
                heartbeat.tick()
            except Exception as exc:
                conn.rollback()
                stats["errors"] += 1
                logger.exception("submissions.store_failed", cik=cik, filename=filename)
                cur.execute(
                    """
                    insert into raw.collector_errors
                        (run_id, cik, source, error_type, message)
                    values (%s, %s, %s, %s, %s)
                    """,
                    (
                        run_id,
                        cik,
                        "submissions",
                        type(exc).__name__,
                        f"{filename}: {str(exc)[:2000]}",
                    ),
                )
                conn.commit()

        # Same rationale as companyfacts.py: a requested CIK with no
        # file at all in submissions.zip must be recorded, not silently
        # absent, even though "no submissions files" can be legitimate.
        if only_ciks is not None:
            missing = only_ciks - seen_ciks
            for cik in missing:
                stats["not_in_archive"] += 1
                logger.warning("submissions.cik_not_in_archive", cik=cik, run_id=run_id)
                cur.execute(
                    """
                    insert into raw.collector_errors
                        (run_id, cik, source, error_type, message)
                    values (%s, %s, %s, %s, %s)
                    """,
                    (
                        run_id,
                        cik,
                        "submissions",
                        "NotInBulkArchive",
                        f"CIK {cik} requested but no file present in submissions.zip as of {fetched_at.isoformat()}",
                    ),
                )
            conn.commit()
    heartbeat.flush()
    logger.info("submissions.bootstrap.done", **stats)
    return stats
