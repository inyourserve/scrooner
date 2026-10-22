#!/usr/bin/env python3
"""The valued-cells-with-a-reason list (K2c, review finding F6) for the Verifier: cells that the
coverage table says HAVE a value yet carry a gap_reason (partial:missing_debt_or_cash on ev_sales and
ev_ebitda: an enterprise value shown while debt or cash is missing; W13 candidate, not FILING-CHECKED).

usage: list_valued_with_reason.py [--cells PATH] --out FILE
Columns: company_id, ticker, name, shard_rank, mcap_bn, group_draft, data_point_name, gap_reason,
         total_debt_resolved_cell, cash_and_equivalents_cell (the blank/valued state of the two named inputs in the same extract).
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sb_lib as L  # noqa: E402


def build(ext: L.Extract):
    ids, cohort = L.load_cohort()
    gmap = {
        int(r["company_id"]): r["group"]
        for r in csv.DictReader(open(L.GROUPS_DRAFT, newline=""))
    }
    rows = []
    for (cid, dp), c in sorted(ext.cells.items()):
        if c["has_value"] and c["reason"]:
            co = cohort.get(cid, {})

            def st(n):
                x = ext.cells.get((cid, n))
                return (
                    "absent"
                    if x is None
                    else (
                        "valued"
                        if x["has_value"]
                        else "blank:" + (x["reason"] or "(none)")
                    )
                )

            rows.append(
                [
                    cid,
                    co.get("ticker", ""),
                    co.get("name", ""),
                    co.get("rank", ""),
                    co.get("mcap_bn", ""),
                    gmap.get(cid, ""),
                    dp,
                    c["reason"],
                    st("total_debt_resolved"),
                    st("cash_and_equivalents"),
                ]
            )
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    rows = build(L.Extract(a.cells))
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(
            [
                "company_id",
                "ticker",
                "name",
                "shard_rank",
                "mcap_bn",
                "group_draft",
                "data_point_name",
                "gap_reason",
                "total_debt_resolved_cell",
                "cash_and_equivalents_cell",
            ]
        )
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
