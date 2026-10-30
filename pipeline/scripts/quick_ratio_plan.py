"""Dry-run plan for rule quick_ratio.inventory_evidence@1 over the top-1000 cohort (writes nothing to the database).

  1. the cohort's periodic accessions (core.filing) and the accessions of its AssetsCurrent facts, grouped by the
     FSDS quarter of their filing date;
  2. per quarter: the SEC Financial Statement Data Set zip (sec.gov only, SEC_USER_AGENT, one request per quarter,
     at most 4/s), read with ``quick_ratio_face.balance_sheet_faces``, appended to the face JSONL, zip deleted unless
     --keep-zips (a quarter already in the JSONL is skipped, so a rerun resumes);
  3. ``plan_quick_ratio`` + ``plan_materials_by_face`` on ONE read-only connection with a statement timeout.

    python pipeline/scripts/quick_ratio_plan.py --out-dir <scratch> [--since 2014-01-01] [--until <date>] [--company-ids 1302,3325]

Outputs in --out-dir: qr_face.jsonl, quick_ratio_plan.json (every planned cell), quick_ratio_plan_summary.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import time
import urllib.request
from collections import Counter
from dataclasses import asdict
from datetime import date
from pathlib import Path

import psycopg

from scrooner_pipeline.mapper import quick_ratio_evidence as qe
from scrooner_pipeline.mapper import quick_ratio_face as qf

PERIODIC = ("10-K", "10-Q", "10-K405", "10-KT", "10-KSB", "10-QSB")
DISK_FLOOR_BYTES = 4 * 10**9
COHORT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv"
)


def cohort_company_ids(path: Path = COHORT_FILE) -> list[int]:
    """The frozen top-1000 cohort (v1.1); the file is read from origin/main when this checkout lacks it."""
    if path.exists():
        text = path.read_text()
    else:
        import subprocess

        text = subprocess.run(
            ["git", "show", "origin/main:data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv"],
            capture_output=True, text=True, check=True, cwd=Path(__file__).parent,
        ).stdout  # fmt: skip
    return sorted(int(r["company_id"]) for r in csv.DictReader(text.splitlines()))


def _env(env: Path) -> None:
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def _connect() -> psycopg.Connection:
    conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)
    conn.execute("set statement_timeout = '120s'")
    conn.execute("set default_transaction_read_only = on")
    return conn


def accessions_by_quarter(
    conn: psycopg.Connection, company_ids: list[int], since: date, until: date
) -> dict[tuple[int, int], set[str]]:
    out: dict[tuple[int, int], set[str]] = {}
    rows = conn.execute(
        """select accession_number, filing_date from core.filing
           where company_id = any(%s) and form = any(%s) and filing_date >= %s and filing_date <= %s
           union
           select distinct fl.accession_number, fl.filing_date
           from core.fact f join core.concept k on k.id = f.concept_id join core.filing fl on fl.id = f.filing_id
           where f.company_id = any(%s) and k.taxonomy = 'us-gaap' and k.tag = 'AssetsCurrent'
             and fl.filing_date >= %s and fl.filing_date <= %s""",
        (company_ids, list(PERIODIC), since, until, company_ids, since, until),
    ).fetchall()
    for acc, filed in rows:
        out.setdefault(qf.quarter_of(filed), set()).add(acc)
    return out


def _download(year: int, q: int, dest: Path) -> bool:
    req = urllib.request.Request(
        qf.FSDS_URL.format(year=year, q=q),
        headers={"User-Agent": os.environ["SEC_USER_AGENT"]},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r, dest.open("wb") as f:
            shutil.copyfileobj(r, f)
        return True
    except urllib.error.HTTPError as e:
        print(f"fsds {year}q{q}: HTTP {e.code}, skipped")
        dest.unlink(missing_ok=True)
        return False


def build_face(
    by_quarter: dict[tuple[int, int], set[str]], out_dir: Path, keep: bool
) -> tuple[Path, int]:
    path = out_dir / "qr_face.jsonl"
    done = set()
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["source"])
    requests = 0
    for year, q in sorted(by_quarter):
        source = f"fsds:{year}q{q}"
        if source in done:
            continue
        if shutil.disk_usage(out_dir).free < DISK_FLOOR_BYTES:
            raise SystemExit("disk below the 4 GB floor: stopping")
        z = out_dir / f"{year}q{q}.zip"
        if not z.exists():
            time.sleep(0.25)  # at most 4 requests per second
            requests += 1
            if not _download(year, q, z):
                continue
        found = qf.balance_sheet_faces(z, by_quarter[(year, q)])
        # a marker line so a quarter with no matching accession is not fetched again on a rerun
        qf.write_jsonl(path, found, source)
        if not found:
            with path.open("a") as f:
                f.write(json.dumps({"accession": f"none:{source}", "statement_dates": [],
                                    "inventory_dates": [], "materials_dates": [], "source": source}) + "\n")  # fmt: skip
        print(f"{source}: {len(found)} of {len(by_quarter[(year, q)])} accessions read")
        if not keep:
            z.unlink(missing_ok=True)
    return path, requests


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--since", type=date.fromisoformat, default=date(2014, 1, 1))
    ap.add_argument("--until", type=date.fromisoformat, default=date.today())
    ap.add_argument("--company-ids", default="")
    ap.add_argument("--keep-zips", action="store_true")
    ap.add_argument(
        "--env-file", type=Path, default=Path(__file__).resolve().parents[1] / ".env"
    )
    args = ap.parse_args()
    _env(args.env_file)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ids = (
        [int(x) for x in args.company_ids.split(",") if x]
        if args.company_ids
        else cohort_company_ids()
    )
    conn = _connect()
    by_quarter = accessions_by_quarter(conn, ids, args.since, args.until)
    face_path, requests = build_face(by_quarter, args.out_dir, args.keep_zips)
    face = qf.load_jsonl(face_path)
    cells = qe.plan_quick_ratio(conn, ids, face=face)
    seen = {(c.company_id, c.period_end) for c in cells}
    cells += [
        c
        for c in qe.plan_materials_by_face(conn, ids, face)
        if (c.company_id, c.period_end) not in seen
    ]
    (args.out_dir / "quick_ratio_plan.json").write_text(
        json.dumps([asdict(c) for c in cells], indent=0)
    )
    summary = {
        "companies": len(ids),
        "accessions_with_face": len(face),
        "sec_requests": requests,
        "cells": len(cells),
        "companies_touched": len({c.company_id for c in cells}),
        "by_reason_outcome": {
            f"{r}|{o}": n
            for (r, o), n in sorted(
                Counter((c.reason, c.outcome) for c in cells).items()
            )
        },
    }
    (args.out_dir / "quick_ratio_plan_summary.json").write_text(
        json.dumps(summary, indent=1)
    )
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
