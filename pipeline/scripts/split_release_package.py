"""Package split re-base release 1 (split.event_basis@1 with pershare.never_derive@1)
from a cohort dry-run cells file (split_rebase_cohort_dryrun.py). No database:
the dry run recorded production's value (old_value) beside the pass's value
(new_value) for every cell; the read-only inputs below come from
split_release_derived_keys.py, which calls the write's own functions.

The package is every cell the phase-1 write would CHANGE (share_basis.
cells_to_write / cells_to_remove): a shown value that differs from production
or fills a blank, and a hidden cell whose production row would be removed.
`other_changed` cells are not written in phase 1 and stay out. A
no_filed_source cell production still holds goes to exactly one bucket:
  held_basis_stale  its value sits on an old share basis (--stale-keys):
                    removed (share_basis.load_held_basis_stale)
  derived share count (--derived-keys): removed
  derived DPS       kept (founder 2026-11-04: FY - 9M on one basis is allowed);
                    one whose inputs are not on one basis is stale (above)
  derived EPS       Family C's (retire.derived_per_share_cells@1)
  anything else     production has a FILED source: held, kept
Each row carries the release marker column `release`.
scripts/split_release_apply.py replays the pass with this package; a company
that no longer matches its packaged cells is refused. Rollback:
canonical_archive.restore_run(<run_id>).
usage: split_release_package.py <dryrun_cells.csv.gz> --derived-keys <d.csv> --stale-keys <s.csv> -o <out_dir>
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from scrooner_pipeline.corporate_actions import share_basis as sb

RELEASE = "split_release_1"
WRITTEN_CLASSES = {
    "was_unadjusted",
    "was_double_divided",
    "share_count_rebased",
    "rounding_only",
    "new_value",
}


def _keys(path: str) -> set[tuple[int, str, int]]:
    with open(path) as fh:
        return {
            (int(r["company_id"]), r["concept"], int(r["period_id"]))
            for r in csv.DictReader(fh)
        }


def _bucket(r: dict, derived: set, stale: set) -> str:
    """remove | stratum | family_c | held for a no_filed_source cell."""
    key = (int(r["company_id"]), r["concept"], int(r["period_id"]))
    if key in stale:
        return "remove"
    if key not in derived:
        return "held"
    if r["concept"] == "dividends_per_share_resolved":
        return "kept"
    if r["concept"] in sb.DERIVED_REMOVAL_CONCEPTS:
        return "remove"
    return "family_c"


def main(argv: list[str]) -> int:
    out = Path(argv[argv.index("-o") + 1])
    derived = _keys(argv[argv.index("--derived-keys") + 1])
    stale = _keys(argv[argv.index("--stale-keys") + 1])
    sources = argv[
        : min(argv.index(a) for a in ("-o", "--derived-keys", "--stale-keys"))
    ]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    left_out: Counter = Counter()
    for src in sources:
        with gzip.open(src, "rt") as fh:
            for r in csv.DictReader(fh):
                shown = r["status"] == "shown"
                status = r["status"]
                if shown and r["class"] in WRITTEN_CLASSES:
                    op = "write"
                elif not shown and r["old_value"] not in ("", None):
                    op = "remove"
                    if status == sb.HIDE_NO_FILED_SOURCE:
                        b = _bucket(r, derived, stale)
                        if b == "kept":
                            left_out["derived_dps_kept_founder_ruling"] += 1
                            continue
                        if b == "family_c":
                            left_out["derived_eps_owned_by_family_c"] += 1
                            continue
                        if b == "held":
                            left_out["held_production_has_a_filed_source"] += 1
                            continue
                        if (
                            int(r["company_id"]),
                            r["concept"],
                            int(r["period_id"]),
                        ) in stale:
                            status = "held_basis_stale"
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
                        # the pass's own status: the stale guard compares it on replay
                        "status": r["status"],
                        "reason": status,
                        "class": r["class"],
                        "chosen_accession": r.get("chosen_accession") or None,
                        "note": r.get("note") or "",
                    }
                )
    rows.sort(key=lambda r: (r["company_id"], r["concept"], r["period_id"]))
    body = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    with gzip.open(
        out / f"{RELEASE}_cells.jsonl.gz", "wt"
    ) as fo:  # digest over the rows
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
                r["class"] if r["op"] == "write" else "remove:" + r["reason"]
                for r in rows
            ).most_common()
        ),
        "by_concept": dict(Counter(r["concept"] for r in rows).most_common()),
        "periods_2015_plus": sum(1 for r in rows if r["end"] >= "2015-01-01"),
        "left_out": dict(left_out),
    }
    (out / f"{RELEASE}_plan.json").write_text(json.dumps(plan, indent=1))
    print(json.dumps(plan, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
