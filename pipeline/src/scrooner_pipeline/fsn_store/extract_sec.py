"""Extract one SEC Financial Statement and Notes set for extra CIKs into the fsn-notes bucket.

The bucket's period extracts were cut to the cohort's CIKs, so a predecessor registrant's history
(Exxon Mobil Corp 0000034088, whose successor ExxonMobil Holdings Corp is the cohort company) is not
in them. This module downloads the SEC zip for one set (one request, sec.gov only, the declared
User-Agent), keeps the rows of the given CIKs' filings byte for byte (SEC columns and values
untouched), and uploads them to `predecessors/<set>/<set>_<table>.tsv.zst`, beside the cohort
extract it does not touch. fsn_store.shard reads that folder too.

Tables kept (the seven the shard reads): sub (the CIKs' filings, as registrant or co-registrant),
pre, num, cal, ren (those filings' rows), tag (every (tag, version) the kept pre/num/cal rows name)
and dim (every dimension hash the kept num rows name).
"""

from __future__ import annotations

import os
import subprocess
import zipfile
from collections.abc import Iterator
from pathlib import Path

import httpx

TABLES = ("sub", "pre", "num", "cal", "ren", "tag", "dim")
SEC_BASE = "https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets"
PREFIX = "predecessors/"


def sec_url(fsn_set: str) -> str:
    """'2024q1' -> 2024q1_notes.zip; '2025m01' -> 2025_01_notes.zip (monthly sets)."""
    if "m" in fsn_set:
        year, month = fsn_set.split("m")
        return f"{SEC_BASE}/{year}_{month}_notes.zip"
    return f"{SEC_BASE}/{fsn_set}_notes.zip"


class NotPublished(Exception):
    """SEC has not published this FSN set (404 on its zip URL)."""


def download_zip(fsn_set: str, dest: Path, user_agent: str) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with httpx.stream(
        "GET",
        sec_url(fsn_set),
        headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
        timeout=1800,
        follow_redirects=False,
    ) as resp:
        if resp.status_code == 404:
            raise NotPublished(fsn_set)
        resp.raise_for_status()
        with tmp.open("wb") as fh:
            for chunk in resp.iter_bytes(1 << 20):
                fh.write(chunk)
    tmp.rename(dest)
    return dest


def _member(zf: zipfile.ZipFile, table: str) -> str:
    for name in (f"{table}.tsv", f"{table}.txt"):
        if name in zf.namelist():
            return name
    raise KeyError(f"{table} not in {zf.namelist()}")


def _rows(zf: zipfile.ZipFile, table: str) -> Iterator[list[bytes]]:
    """Header first, then every row, as raw byte fields (byte-exact, no decoding)."""
    with zf.open(_member(zf, table)) as raw:
        for line in raw:  # ZipExtFile is buffered; lines are read as they decompress
            yield line.rstrip(b"\r\n").split(b"\t")


def filter_set(
    zf: zipfile.ZipFile, ciks: set[str], *, registrant_only: bool = True
) -> dict[str, list[list[bytes]]]:
    """table -> [header, rows...] for the CIKs' filings (cik values compared without leading zeros).
    registrant_only (default): only filings whose registrant (sub.cik) is one of the CIKs. A
    predecessor that still co-files with its successor (Southwest Gas Corp, Dow Chemical) appears in
    the successor's filings via aciks; those are already in the cohort extract and must not repeat."""
    want = {c.lstrip("0").encode() for c in ciks}
    out: dict[str, list[list[bytes]]] = {}
    it = _rows(zf, "sub")
    header = next(it)
    i_adsh, i_cik = header.index(b"adsh"), header.index(b"cik")
    i_aciks = header.index(b"aciks") if b"aciks" in header else None
    sub = [header]
    adshs: set[bytes] = set()
    for r in it:
        mine = r[i_cik].lstrip(b"0") in want or (
            not registrant_only
            and i_aciks is not None
            and any(a.lstrip(b"0") in want for a in r[i_aciks].split())
        )
        if mine:
            sub.append(r)
            adshs.add(r[i_adsh])
    out["sub"] = sub
    tags: set[tuple[bytes, bytes]] = set()
    dims: set[bytes] = set()
    for table in ("pre", "num", "cal", "ren"):
        it = _rows(zf, table)
        header = next(it)
        ia = header.index(b"adsh")
        kept = [header]
        for r in it:
            if r[ia] not in adshs:
                continue
            kept.append(r)
            if table in ("pre", "num"):
                tags.add((r[header.index(b"tag")], r[header.index(b"version")]))
            if table == "num" and b"dimh" in header:
                dims.add(r[header.index(b"dimh")])
            if table == "cal":
                tags.add((r[header.index(b"ptag")], r[header.index(b"pversion")]))
                tags.add((r[header.index(b"ctag")], r[header.index(b"cversion")]))
        out[table] = kept
    it = _rows(zf, "tag")
    header = next(it)
    it_, iv = header.index(b"tag"), header.index(b"version")
    out["tag"] = [header, *(r for r in it if (r[it_], r[iv]) in tags)]
    it = _rows(zf, "dim")
    header = next(it)
    ih = header.index(b"dimhash")
    out["dim"] = [header, *(r for r in it if r[ih] in dims)]
    return out


def write_zst(rows: list[list[bytes]], path: Path) -> Path:
    body = b"".join(b"\t".join(r) + b"\n" for r in rows)
    path.write_bytes(
        subprocess.run(
            ["zstd", "-q", "-19", "-c"], input=body, capture_output=True, check=True
        ).stdout
    )
    return path


def upload(fsn_set: str, table: str, path: Path, prefix: str = PREFIX) -> str:
    base = os.environ["SUPABASE_URL"].rstrip("/") + "/storage/v1"
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    obj = f"{prefix}{fsn_set}/{fsn_set}_{table}.tsv.zst"
    resp = httpx.post(
        f"{base}/object/fsn-notes/{obj}",
        headers={
            "Authorization": f"Bearer {key}",
            "apikey": key,
            "Content-Type": "application/octet-stream",
            "x-upsert": "true",
        },
        content=path.read_bytes(),
        timeout=600,
    )
    resp.raise_for_status()
    return obj


# where a set's rows go: the predecessor folder beside the cohort sets (default), or "" for a NEW cohort set at the
# bucket's top level (<set>/<set>_<table>.tsv.zst, the layout fsn_pilot.py / fsn_upload.py gave every cohort set):
# fsn_store.shard lists sets from the top level only and reads predecessors/<set> only for a set listed there
PREFIXES = (PREFIX, "")


def run_set(
    fsn_set: str,
    ciks: set[str],
    work: Path,
    user_agent: str,
    *,
    apply: bool,
    prefix: str = PREFIX,
) -> dict[str, int]:
    """Download, filter, write (and with apply, upload) one set; the zip is deleted after use.
    A set SEC has not published yet returns {"published": 0} and writes nothing."""
    if prefix not in PREFIXES:
        raise ValueError(f"prefix must be one of {PREFIXES}, not {prefix!r}")
    try:
        zpath = download_zip(fsn_set, work / f"{fsn_set}.zip", user_agent)
    except NotPublished:
        return {"published": 0}
    try:
        with zipfile.ZipFile(zpath) as zf:
            tables = filter_set(zf, ciks)
    finally:
        zpath.unlink(missing_ok=True)
    counts = {t: len(rows) - 1 for t, rows in tables.items()}
    if counts["sub"] == 0:
        return counts
    out = work / fsn_set
    out.mkdir(parents=True, exist_ok=True)
    for t, rows in tables.items():
        p = write_zst(rows, out / f"{fsn_set}_{t}.tsv.zst")
        if apply:
            upload(fsn_set, t, p, prefix)
    return counts
