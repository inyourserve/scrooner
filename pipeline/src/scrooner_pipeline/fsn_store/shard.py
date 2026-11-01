"""Shard the fsn-notes bucket extracts into company directories (FORMATS-v1 §1).

Streams one period at a time: download sub/pre/num/cal/ren/tag/dim of the
period into a cache, filter to the target companies (a filing belongs to its
`cik` and to every co-registrant in `aciks`), append the rows to each
company's `<table>.tsv.zst` as an independent zstd frame (frames concatenate,
`zstd -dc` reads them as one stream), delete the download, repeat. Memory is
bounded by FLUSH_ROWS per table; disk by FLOOR_GB (the run stops cleanly
below it and resumes from the next period: `progress.json` names the periods
done). `finalize` writes each manifest.json (row counts, per-file sha256,
input_sha256).

usage (CLI): scrooner-fsn shard --out companies --ciks ... [--periods 2014q1,...]
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import structlog

from scrooner_pipeline.fsn_store.company_dir import (
    NO_DIM,
    PERIODIC_FORMS,
    STATEMENT_STMTS,
    TABLES,
    zst_rows,
)

logger = structlog.get_logger()
BUCKET = "fsn-notes"
FLUSH_ROWS = 150_000
FLOOR_GB = 4.0
HEADERS = {
    "sub": None,  # from the file, with fsn_set prepended
}


def _storage() -> tuple[str, dict[str, str]]:
    base = os.environ["SUPABASE_URL"].rstrip("/") + "/storage/v1"
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return base, {"Authorization": f"Bearer {key}", "apikey": key}


def list_periods() -> list[str]:
    base, h = _storage()
    r = httpx.post(
        f"{base}/object/list/{BUCKET}",
        headers=h,
        json={"prefix": "", "limit": 500},
        timeout=60,
    )
    r.raise_for_status()
    return sorted(x["name"] for x in r.json() if x["name"][:4].isdigit())


def download(period: str, table: str, cache: Path) -> Path:
    base, h = _storage()
    target = cache / period / f"{period}_{table}.tsv.zst"
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".part")
    with httpx.stream(
        "GET",
        f"{base}/object/{BUCKET}/{period}/{period}_{table}.tsv.zst",
        headers=h,
        timeout=900,
    ) as resp:
        if resp.status_code != 200:
            raise FileNotFoundError(f"{period}/{table}: HTTP {resp.status_code}")
        with tmp.open("wb") as fh:
            for chunk in resp.iter_bytes():
                fh.write(chunk)
    tmp.rename(target)
    return target


def free_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / 1e9


class Writer:
    """Appends rows to companies/<cik>/<table>.tsv.zst as zstd frames; header once."""

    def __init__(self, out: Path):
        self.out = out
        self.buf: dict[tuple[str, str], list[list[str]]] = defaultdict(list)
        self.headers: dict[str, list[str]] = {}
        self.counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.n = 0

    def add(self, cik: str, table: str, header: list[str], row: list[str]) -> None:
        self.headers.setdefault(table, header)
        self.buf[(cik, table)].append(row)
        self.counts[cik][table] += 1
        self.n += 1
        if self.n >= FLUSH_ROWS:
            self.flush()

    def flush(self) -> None:
        for (cik, table), rows in self.buf.items():
            if not rows:
                continue
            d = self.out / cik
            d.mkdir(parents=True, exist_ok=True)
            f = d / f"{table}.tsv.zst"
            text = io.StringIO()
            w = csv.writer(
                text,
                delimiter="\t",
                quoting=csv.QUOTE_NONE,
                quotechar="",
                escapechar="\\",
                lineterminator="\n",
            )
            if not f.exists():
                w.writerow(self.headers[table])
            w.writerows(rows)
            frame = subprocess.run(
                ["zstd", "-q", "-c", "-3"],
                input=text.getvalue().encode(),
                capture_output=True,
                check=True,
            ).stdout
            with f.open("ab") as fh:
                fh.write(frame)
        self.buf.clear()
        self.n = 0


def shard_period(
    period: str, targets: set[str], cache: Path, writer: Writer
) -> dict[str, int]:
    """One period: filter the seven tables to the targets' filings and append."""
    stats: dict[str, int] = defaultdict(int)
    paths = {t: download(period, t, cache) for t in TABLES}
    # sub: which filings, and whose
    owners: dict[str, list[str]] = {}
    sub_header: list[str] | None = None
    for r in zst_rows(paths["sub"]):
        if sub_header is None:
            sub_header = ["fsn_set", *r.keys()]
        if r.get("form") not in PERIODIC_FORMS:
            continue
        ciks = {r["cik"].zfill(10)} | {
            c.zfill(10) for c in (r.get("aciks") or "").split() if c
        }
        mine = sorted(ciks & targets)
        if not mine:
            continue
        owners[r["adsh"]] = mine
        for c in mine:
            writer.add(c, "sub", sub_header, [period, *r.values()])
        stats["filings"] += 1
    if not owners:
        return stats
    adshs = set(owners)
    # pre: statement rows; remember (adsh, tag, version) on statements for num's dimensional filter
    on_stmt: set[tuple[str, str, str]] = set()
    refs_tag: dict[str, set[tuple[str, str]]] = defaultdict(set)
    refs_dim: dict[str, set[str]] = defaultdict(set)
    header = None
    for r in zst_rows(paths["pre"]):
        header = header or list(r.keys())
        if r["adsh"] not in adshs or r.get("stmt") not in STATEMENT_STMTS:
            continue
        on_stmt.add((r["adsh"], r["tag"], r["version"]))
        for c in owners[r["adsh"]]:
            writer.add(c, "pre", header, list(r.values()))
            refs_tag[c].add((r["tag"], r["version"]))
        stats["pre"] += 1
    header = None
    for r in zst_rows(paths["num"]):
        header = header or list(r.keys())
        a = r["adsh"]
        if a not in adshs:
            continue
        if r["dimh"] != NO_DIM and (a, r["tag"], r["version"]) not in on_stmt:
            stats["num_dropped_dim_note"] += 1
            continue
        for c in owners[a]:
            writer.add(c, "num", header, list(r.values()))
            refs_tag[c].add((r["tag"], r["version"]))
            if r["dimh"] != NO_DIM:
                refs_dim[c].add(r["dimh"])
        stats["num"] += 1
    header = None
    for r in zst_rows(paths["cal"]):
        header = header or list(r.keys())
        a = r["adsh"]
        if a not in adshs:
            continue
        for c in owners[a]:
            writer.add(c, "cal", header, list(r.values()))
            refs_tag[c].add((r["ptag"], r["pversion"]))
            refs_tag[c].add((r["ctag"], r["cversion"]))
        stats["cal"] += 1
    header = None
    for r in zst_rows(paths["ren"]):
        header = header or list(r.keys())
        if r["adsh"] not in adshs:
            continue
        for c in owners[r["adsh"]]:
            writer.add(c, "ren", header, list(r.values()))
        stats["ren"] += 1
    # tag and dim: only what this period's kept rows reference, per company
    want_tag: dict[tuple[str, str], list[str]] = defaultdict(list)
    for c, pairs in refs_tag.items():
        for p in pairs:
            want_tag[p].append(c)
    header = None
    for r in zst_rows(paths["tag"]):
        header = header or list(r.keys())
        cs = want_tag.get((r["tag"], r["version"]))
        if not cs:
            continue
        for c in cs:
            writer.add(c, "tag", header, list(r.values()))
        stats["tag"] += 1
    want_dim: dict[str, list[str]] = defaultdict(list)
    for c, hs in refs_dim.items():
        for h in hs:
            want_dim[h].append(c)
    header = None
    for r in zst_rows(paths["dim"]):
        header = header or list(r.keys())
        cs = want_dim.get(r["dimhash"])
        if not cs:
            continue
        for c in cs:
            writer.add(c, "dim", header, list(r.values()))
        stats["dim"] += 1
    writer.flush()
    shutil.rmtree(cache / period, ignore_errors=True)
    return stats


def finalize(
    out: Path,
    cik: str,
    company_id: int | None,
    periods: list[str],
    shard_commit: str | None,
    bucket_manifest_sha: str | None = None,
) -> dict[str, Any]:
    """Dedupe tag/dim rows (a tag referenced in many periods was appended once per period), then manifest.json."""
    d = out / cik
    for table, keycols in (("tag", ("tag", "version")), ("dim", ("dimhash",))):
        f = d / f"{table}.tsv.zst"
        if not f.exists():
            continue
        seen: set[tuple] = set()
        rows, header = [], None
        for r in zst_rows(f):
            header = header or list(r.keys())
            k = tuple(r[c] for c in keycols)
            if k in seen:
                continue
            seen.add(k)
            rows.append(list(r.values()))
        text = io.StringIO()
        w = csv.writer(
            text,
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
            quotechar="",
            escapechar="\\",
            lineterminator="\n",
        )
        w.writerow(header or [])
        w.writerows(rows)
        f.write_bytes(
            subprocess.run(
                ["zstd", "-q", "-c", "-3"],
                input=text.getvalue().encode(),
                capture_output=True,
                check=True,
            ).stdout
        )
    counts, shas, accessions, sets = {}, {}, set(), set()
    for t in TABLES:
        f = d / f"{t}.tsv.zst"
        if not f.exists():
            counts[t] = 0
            shas[t] = ""
            continue
        n = 0
        for r in zst_rows(f):
            n += 1
            if t == "sub":
                accessions.add(r["adsh"])
                sets.add(r["fsn_set"])
        counts[t] = n
        shas[t] = hashlib.sha256(f.read_bytes()).hexdigest()
    manifest = {
        "cik": cik,
        "company_id": company_id,
        "fsn_sets": sorted(sets),
        "periods_scanned": periods,
        "accessions": sorted(accessions),
        "row_counts": counts,
        "file_sha256": shas,
        "input_sha256": hashlib.sha256(
            "\n".join(shas[t] for t in TABLES).encode()
        ).hexdigest(),
        "shard_commit": shard_commit,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bucket_manifest": bucket_manifest_sha,
    }
    (d / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return manifest


def run(
    out: Path,
    targets: dict[str, int | None],
    periods: list[str] | None,
    cache: Path,
    *,
    floor_gb: float = FLOOR_GB,
    shard_commit: str | None = None,
) -> dict[str, Any]:
    """targets: cik -> company_id. Resumable: progress.json lists finished periods."""
    out.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    periods = periods or list_periods()
    prog_path = out / "progress.json"
    prog = (
        json.loads(prog_path.read_text())
        if prog_path.exists()
        else {"done": [], "stats": {}}
    )
    writer = Writer(out)
    for p in periods:
        if p in prog["done"]:
            continue
        if free_gb(out) < floor_gb:
            logger.warning(
                "fsn_shard.disk_floor", free_gb=round(free_gb(out), 2), stopped_before=p
            )
            prog["stopped_before"] = p
            break
        t0 = time.time()
        stats = shard_period(p, set(targets), cache, writer)
        prog["done"].append(p)
        prog["stats"][p] = {**stats, "seconds": round(time.time() - t0, 1)}
        prog_path.write_text(json.dumps(prog, indent=1))
        logger.info(
            "fsn_shard.period", period=p, **stats, seconds=round(time.time() - t0, 1)
        )
    complete = all(p in prog["done"] for p in periods)
    manifests = {}
    if complete:
        for cik, cid in targets.items():
            if (out / cik).exists():
                manifests[cik] = finalize(out, cik, cid, periods, shard_commit)
        prog["finalized"] = sorted(manifests)
        prog_path.write_text(json.dumps(prog, indent=1))
    return {
        "periods": len(periods),
        "done": len(prog["done"]),
        "complete": complete,
        "companies": len(manifests),
        "stopped_before": prog.get("stopped_before"),
    }
