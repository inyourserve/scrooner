"""Rebuild data-team/strategy/top100-coverage.csv and top100-coverage-summary.csv (read-only on the database).

usage (repo root): PYTHONPATH=pipeline/src python3 pipeline/scripts/top100_coverage.py [out_dir]
Per-company mode (resumable, shardable; one CSV per company, queries filter by company_id only):
  ... top100_coverage.py --company-ids 12,34 [--per-company-dir D]     writes D/<id>.csv + D/<id>.json
  ... top100_coverage.py --merge [out_dir] [--per-company-dir D]       builds the two CSVs from D, no database
Logic and class definitions: scrooner_pipeline/mapper/top100_coverage.py."""

import argparse
import sys
from pathlib import Path

from scrooner_pipeline.mapper.top100_coverage import (
    PER_COMPANY_SUBDIR,
    main,
    main_company,
    main_merge,
)

SHARDS = Path("doc/data-moat/team/top1000/shards.csv")
READS = Path("data-team/companies/reads")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", nargs="?", default="data-team/strategy")
    ap.add_argument("--company-ids", default="")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--per-company-dir", default=None)
    a = ap.parse_args()
    out = Path(a.out_dir)
    per = Path(a.per_company_dir) if a.per_company_dir else out / PER_COMPANY_SUBDIR
    if a.company_ids:
        ids = [int(x) for x in a.company_ids.split(",") if x.strip()]
        sys.exit(main_company(per, SHARDS, READS, ids))
    if a.merge:
        sys.exit(main_merge(out, per, SHARDS))
    sys.exit(main(out, SHARDS, READS))
