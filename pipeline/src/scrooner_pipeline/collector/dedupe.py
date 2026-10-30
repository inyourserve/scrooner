"""Hash-dedupe for companyfacts uploads (storage audit 2026-10-24, lever 1).

92% of a measured 9-day window of companyfacts fetches were byte-identical to
the previous payload of the same CIK, and each one cost ~1.9 MB of Storage
(94 GB bucket, growing 7-10 GB/week). SEC publishes ONE bulk archive, so there
is no per-CIK request to avoid; what is avoided is the redundant upload and
the redundant raw.sec_companyfacts row. Equal sha256 of the whole payload
means equal bytes, so immutability holds: the earlier object IS this payload.

Rules (all pure, DB access only in the two helpers at the bottom):
  * compare against the CIK's LATEST stored row only. A payload equal to an
    older, non-latest version is still stored (conservative, keeps history of
    a revert);
  * nothing is ever overwritten or deleted here;
  * an unchanged fetch is recorded in raw.sec_companyfacts_unchanged_fetch so
    "we looked at fetched_at, nothing changed" stays auditable and per-CIK
    freshness is not lost (migration 0111);
  * if the migration is not applied yet the dedupe switches itself off and
    the collector behaves exactly as before.
"""

import hashlib

import psycopg

Item = tuple[str, str, bytes]  # (cik, object_path, payload)


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def partition_unchanged(
    batch: list[Item], latest: dict[str, tuple[int, str]]
) -> tuple[list[Item], list[tuple[str, str, int]]]:
    """Split a batch into (items to upload, [(cik, sha256, kept_raw_id)] unchanged).

    `latest` maps cik -> (raw_id, sha256) of the newest stored row."""
    to_upload: list[Item] = []
    unchanged: list[tuple[str, str, int]] = []
    for item in batch:
        cik, _path, payload = item
        digest = sha256_hex(payload)
        prior = latest.get(cik)
        if prior is not None and prior[1] == digest:
            unchanged.append((cik, digest, prior[0]))
        else:
            to_upload.append(item)
    return to_upload, unchanged


def dedupe_enabled(conn: psycopg.Connection) -> bool:
    with conn.cursor() as cur:
        cur.execute("select to_regclass('raw.sec_companyfacts_unchanged_fetch') is not null")
        row = cur.fetchone()
    conn.rollback()
    return bool(row and row[0])


def latest_stored(conn: psycopg.Connection, ciks: list[str]) -> dict[str, tuple[int, str]]:
    if not ciks:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (cik) cik, id, sha256
            from raw.sec_companyfacts
            where cik = any(%s)
            order by cik, fetched_at desc, id desc
            """,
            (ciks,),
        )
        out = {cik: (rid, sha) for cik, rid, sha in cur.fetchall()}
    conn.rollback()
    return out


def unchanged_ciks_for_run(conn: psycopg.Connection, run_id: int) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select cik from raw.sec_companyfacts_unchanged_fetch where run_id = %s",
            (run_id,),
        )
        out = {r[0] for r in cur.fetchall()}
    conn.rollback()
    return out
