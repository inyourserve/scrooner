"""Local read cache for the big, repeated FSN row sets (egress fix, founder 2026-11-28).

Two readers pulled the same rows from the shared Supabase on every job: the per-company coverage export
(mapper/top100_coverage._locator_index: every statement line + report title of the cited filings) and
common/authority.load_face_indexes (every face line + value of a company). The CI flow runs ONE company per job and
many jobs per day, so the repeat is per job, not per accession inside a job.

Rows are kept on local disk under pipeline/.cache/ (gitignored), one pickle per key, and reused only while the filing's
fsn.filing.src_sha256 (the SHA-256 of the FSN source the filing was loaded from) is unchanged: a reload with different
source bytes changes the fingerprint and the entry is ignored and refetched. A filing with no src_sha256 is never cached.
The stored value is the exact row list the query returned, so callers build byte-identical results from it.

SCROONER_FSN_CACHE=0 turns it off; SCROONER_FSN_CACHE_DIR moves it. Any read or write problem falls back to the DB.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any

_DEFAULT_DIR = Path(__file__).resolve().parents[3] / ".cache" / "fsn_reads"


def enabled() -> bool:
    return os.environ.get("SCROONER_FSN_CACHE", "1") != "0"


def cache_dir() -> Path:
    return Path(os.environ.get("SCROONER_FSN_CACHE_DIR") or _DEFAULT_DIR)


def _path(kind: str, key: str) -> Path:
    return cache_dir() / kind / (hashlib.sha256(key.encode()).hexdigest() + ".pkl")


def get(kind: str, key: str, fingerprint: str) -> Any | None:
    if not enabled():
        return None
    try:
        with open(_path(kind, key), "rb") as fh:
            fp, value = pickle.load(fh)
    except Exception:
        return None
    return value if fp == fingerprint else None


def put(kind: str, key: str, fingerprint: str, value: Any) -> None:
    if not enabled():
        return
    try:
        p = _path(kind, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=p.parent, suffix=".tmp")
        with os.fdopen(fd, "wb") as fh:
            pickle.dump((fingerprint, value), fh, protocol=4)
        os.replace(tmp, p)
    except Exception:
        pass


def filing_shas(conn: Any, accessions: list[str]) -> dict[str, str | None]:
    """accession -> fsn.filing.src_sha256 (None when the filing has none); absent accessions are absent."""
    out: dict[str, str | None] = {}
    for i in range(0, len(accessions), 1000):
        for acc, sha in conn.execute(
            "select accession, src_sha256 from fsn.filing where accession = any(%s)",
            (accessions[i : i + 1000],),
        ).fetchall():
            out[acc] = sha
    return out


def company_shas(conn: Any, company_ids: list[int]) -> dict[int, str | None]:
    """company_id -> fingerprint of all its fsn.filing rows (None if any filing has no src_sha256 or it has no filing)."""
    rows: dict[int, list[tuple[str, str | None]]] = {}
    for cid, acc, sha in conn.execute(
        "select company_id, accession, src_sha256 from fsn.filing where company_id = any(%s)",
        (company_ids,),
    ).fetchall():
        rows.setdefault(cid, []).append((acc, sha))
    out: dict[int, str | None] = {}
    for cid, lst in rows.items():
        if any(s is None for _, s in lst):
            out[cid] = None
        else:
            out[cid] = hashlib.sha256(repr(sorted(lst)).encode()).hexdigest()
    return out
