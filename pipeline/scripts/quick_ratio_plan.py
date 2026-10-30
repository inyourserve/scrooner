"""Dry-run plan for rule quick_ratio.inventory_evidence@1 over the top-1000 cohort (writes nothing to the database).

  1. the cohort's periodic accessions (core.filing) and the accessions of its AssetsCurrent facts, grouped by the
     FSN period of their filing date (quarters to 2025q3, then months: 2025m10 ...);
  2. per period: <period>_pre.tsv.zst and <period>_num.tsv.zst from the private bucket ``fsn-notes`` (no SEC request),
     read with ``quick_ratio_face.fsn_balance_sheet_faces``, appended to the face JSONL, then deleted unless
     --keep-files (a period already in the JSONL is skipped, so a rerun resumes);
  3. ``plan_quick_ratio`` + ``plan_materials_by_face`` on ONE read-only connection with a statement timeout.

    pipeline/.venv/bin/python pipeline/scripts/quick_ratio_plan.py --out-dir <scratch> --env-file pipeline/.env
        [--since 2014-01-01] [--until <date>] [--company-ids 3325,1560]

The bucket extracts hold the team's cohort filings only: an accession absent from them is "not in the data set" (the
value stays, flagged), exactly as for an FSDS gap. Outputs in --out-dir: qr_face.jsonl, quick_ratio_plan.json (every
planned cell), quick_ratio_plan_summary.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import urllib.error
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


def fsn_period(filed: date) -> str:
    """The FSN data set holding a filing: quarterly to 2025q3, monthly from October 2025."""
    if filed < date(2025, 10, 1):
        year, q = qf.quarter_of(filed)
        return f"{year}q{q}"
    return f"{filed.year}m{filed.month:02d}"


def accessions_by_period(
    conn: psycopg.Connection,
    company_ids: list[int],
    since: date,
    until: date,
    chunk: int = 100,
) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for i in range(0, len(company_ids), chunk):
        part = company_ids[i : i + chunk]
        rows = conn.execute(
            """select accession_number, filing_date from core.filing
               where company_id = any(%s) and form = any(%s) and filing_date between %s and %s
               union
               select distinct fl.accession_number, fl.filing_date
               from core.fact f join core.concept k on k.id = f.concept_id join core.filing fl on fl.id = f.filing_id
               where f.company_id = any(%s) and k.taxonomy = 'us-gaap' and k.tag = 'AssetsCurrent'
                 and fl.filing_date between %s and %s""",
            (part, list(PERIODIC), since, until, part, since, until),
        ).fetchall()
        for acc, filed in rows:
            out.setdefault(fsn_period(filed), set()).add(acc)
    return out


def _fetch(period: str, dest: Path) -> None:
    base = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    dest.mkdir(parents=True, exist_ok=True)
    for table in ("pre", "num"):
        f = dest / f"{period}_{table}.tsv.zst"
        if f.exists():
            continue
        req = urllib.request.Request(
            f"{base}/storage/v1/object/fsn-notes/{period}/{f.name}",
            headers={"Authorization": f"Bearer {key}", "apikey": key},
        )
        with urllib.request.urlopen(req, timeout=600) as r, f.open("wb") as out:
            shutil.copyfileobj(r, out)


def build_face(
    by_period: dict[str, set[str]], out_dir: Path, keep: bool
) -> tuple[Path, Counter[str]]:
    path = out_dir / "qr_face.jsonl"
    done = set()
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["source"])
    coverage: Counter[str] = Counter()
    for period in sorted(by_period):
        source = f"fsn:{period}"
        wanted = by_period[period]
        if source in done:
            continue
        if shutil.disk_usage(out_dir).free < DISK_FLOOR_BYTES:
            raise SystemExit("disk below the 4 GB floor: stopping")
        pdir = out_dir / "fsn" / period
        try:
            _fetch(period, pdir)
        except urllib.error.HTTPError as e:
            print(
                f"{source}: HTTP {e.code}, not in the bucket; {len(wanted)} accessions unread"
            )
            coverage["accessions_period_missing"] += len(wanted)
            continue
        found = qf.fsn_balance_sheet_faces(pdir, wanted)
        qf.write_jsonl(path, found, source)
        # a marker line so a period with no matching accession is not read again on a rerun
        with path.open("a") as f:
            f.write(json.dumps({"accession": f"done:{source}", "statement_dates": [],
                                "inventory_dates": [], "materials_dates": [], "source": source}) + "\n")  # fmt: skip
        coverage["accessions_wanted"] += len(wanted)
        coverage["accessions_read"] += len(found)
        print(f"{source}: {len(found)} of {len(wanted)} accessions read")
        if not keep:
            shutil.rmtree(pdir, ignore_errors=True)
    return path, coverage


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--since", type=date.fromisoformat, default=date(2014, 1, 1))
    ap.add_argument("--until", type=date.fromisoformat, default=date.today())
    ap.add_argument("--company-ids", default="")
    ap.add_argument("--keep-files", action="store_true")
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
    by_period = accessions_by_period(conn, ids, args.since, args.until)
    face_path, coverage = build_face(by_period, args.out_dir, args.keep_files)
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
        "accessions_with_face": sum(not a.startswith("done:") for a in face),
        "sec_requests": 0,
        **coverage,
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
