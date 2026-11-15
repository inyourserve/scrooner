#!/usr/bin/env python3
"""Extract one company's OPEN shown cells (with the `work` column) from a top100_coverage output dir.

usage: top100_open_shown.py <coverage_dir> <company_id> <out_dir>
Reads <coverage_dir>/top100-open-shown-cells-*.csv (written by top100_coverage next to top100-coverage.csv) and
writes <out_dir>/open-shown.csv (that company's rows, header always) and <out_dir>/open-shown.json
({"ticker", "open": N}). If the export is missing, writes nothing and exits 2, so a publisher never deletes a
file on the strength of a run that produced no export."""

import csv
import json
import sys
from pathlib import Path


def main() -> int:
    cov, cid, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    files = sorted(cov.glob("top100-open-shown-cells-*.csv"))
    summary = cov / "top100-coverage-summary.csv"
    if not files or not summary.exists():
        print("open-shown: no export in", cov)
        return 2
    ticker = None
    with open(summary, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["company_id"] == cid:
                ticker = r["ticker"]
    if not ticker:
        print("open-shown: company", cid, "not in summary")
        return 2
    with open(files[-1], newline="") as fh:
        rd = csv.DictReader(fh)
        fields = rd.fieldnames or []
        rows = [r for r in rd if r.get("company_id") == cid]
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "open-shown.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    (out / "open-shown.json").write_text(json.dumps({"ticker": ticker, "open": len(rows)}))
    print(f"open-shown {ticker}: {len(rows)} OPEN cell(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
