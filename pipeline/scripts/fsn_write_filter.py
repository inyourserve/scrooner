"""The FSN write's cell filter (pipeline-fsn-write.yml, select_write): keep a select row only when its
(company_id, data_point_name) pair passed the done gate (out/done_pairs.tsv, ruling RULING-DONE-GATE-C4-2026-11-09
C1) and its data point is in the dispatched list. All or nothing per pair: every row of a done pair is kept,
no row of any other pair (the loader replaces a pair's rows as a whole, cell_loader ~l.954).

usage: python3 pipeline/scripts/fsn_write_filter.py <src cells.jsonl.gz> <dst cells.jsonl.gz> <data_points csv> <done_pairs.tsv>
Writes <dst> and manifest.json beside it. Stdlib only.
"""

import csv
import gzip
import json
import sys
from pathlib import Path


def done_pairs(path: Path) -> set[tuple[int, str]]:
    with path.open() as fh:
        return {
            (int(r["company_id"]), r["data_point"])
            for r in csv.DictReader(fh, delimiter="\t")
        }


def keep(row: dict, allowed: set[str], pairs: set[tuple[int, str]]) -> bool:
    return (
        row["data_point_name"] in allowed
        and (int(row["company_id"]), row["data_point_name"]) in pairs
        # operating income is never note-sourced (Ritwik 2026-11-03); select never emits it, refuse it here too
        and not (
            row["data_point_name"] == "operating_income_resolved"
            and (row.get("input_refs") or {}).get("source") == "note"
        )
    )


def main(src: str, dst: str, data_points: str, pairs_path: str) -> None:
    allowed = {s for s in data_points.split(",") if s}
    pairs = done_pairs(Path(pairs_path))
    with gzip.open(src, "rt") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    kept = [r for r in rows if keep(r, allowed, pairs)]
    with gzip.open(dst, "wt") as fh:
        for r in kept:
            fh.write(json.dumps(r) + "\n")
    Path(dst).with_name("manifest.json").write_text(
        json.dumps(
            {
                "family": Path(src).parent.name,
                "rule_id": "fsn.select@1",
                "rows": len(kept),
                "data_points": sorted({r["data_point_name"] for r in kept}),
                "pairs": len(
                    {(int(r["company_id"]), r["data_point_name"]) for r in kept}
                ),
                "period_floor": "2014-01-01",
            }
        )
    )
    print(f"{src}: {len(kept)} of {len(rows)} rows ({len(pairs)} done pairs)")


if __name__ == "__main__":
    main(*sys.argv[1:5])
