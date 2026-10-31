"""Package split re-base release 1 (split.event_basis@1 with pershare.never_derive@1)
from a cohort dry-run cells file (split_rebase_cohort_dryrun.py). No database:
the dry run already recorded production's value (old_value) beside the pass's
value (new_value) for every cell.

The package is every cell the phase-1 write would CHANGE (share_basis.
cells_to_write / cells_to_remove): a shown value that differs from production
or fills a blank, and a hidden cell whose production row would be removed.
`other_changed` cells are not written in phase 1 and stay out. Each row
carries the release marker column `release`. scripts/split_release_apply.py
replays the pass with this package; a company that no longer matches its
packaged cells is refused (share_basis.package_mismatches). Rollback:
canonical_archive.restore_run(<run_id>) restores every row the write archived.
usage: split_release_package.py <dryrun_cells.csv.gz> [<more.csv.gz> ...] -o <out_dir>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

RELEASE = "split_release_1"
WRITTEN_CLASSES = {
    "was_unadjusted",
    "was_double_divided",
    "share_count_rebased",
    "rounding_only",
    "new_value",
}


def main(argv: list[str]) -> int:
    out = Path(argv[argv.index("-o") + 1])
    sources = argv[: argv.index("-o")]
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in sources:
        with gzip.open(src, "rt") as fh:
            for r in csv.DictReader(fh):
                shown = r["status"] == "shown"
                if shown and r["class"] in WRITTEN_CLASSES:
                    op = "write"
                elif not shown and r["old_value"] not in ("", None):
                    op = "remove"
                else:
                    continue
                rows.append(
                    {
                        "release": RELEASE,
                        "op": op,
                        "company_id": int(r["company_id"]),
                        "ticker": r["ticker"],
                        "concept": r["concept"],
                        "period_id": int(r["period_id"]),
                        "start": r["start"],
                        "end": r["end"],
                        "old_value": r["old_value"] or None,
                        "new_value": r["new_value"] or None,
                        "status": r["status"],
                        "class": r["class"],
                        "chosen_accession": r.get("chosen_accession") or None,
                        "note": r.get("note") or "",
                    }
                )
    rows.sort(key=lambda r: (r["company_id"], r["concept"], r["period_id"]))
    body = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    with gzip.open(
        out / f"{RELEASE}_cells.jsonl.gz", "wt"
    ) as fo:  # digest is over the uncompressed rows
        fo.write(body)
    digest = hashlib.sha256(body.encode()).hexdigest()
    (out / f"{RELEASE}_cells.sha256").write_text(f"{digest}  {RELEASE}_cells.jsonl\n")
    (out / f"{RELEASE}_companies.txt").write_text(
        "".join(f"{c}\n" for c in sorted({r["company_id"] for r in rows}))
    )
    plan = {
        "release": RELEASE,
        "rules": ["split.event_basis@1", "pershare.never_derive@1"],
        "cells": len(rows),
        "companies": len({r["company_id"] for r in rows}),
        "cells_sha256": digest,
        "by_op": dict(Counter(r["op"] for r in rows)),
        "by_class": dict(
            Counter(
                r["class"] if r["op"] == "write" else "remove:" + r["status"]
                for r in rows
            ).most_common()
        ),
        "by_concept": dict(Counter(r["concept"] for r in rows).most_common()),
        "periods_2015_plus": sum(1 for r in rows if r["end"] >= "2015-01-01"),
    }
    (out / f"{RELEASE}_plan.json").write_text(json.dumps(plan, indent=1))
    print(json.dumps(plan, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
