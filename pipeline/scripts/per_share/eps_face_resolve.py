"""Resolve Family C 'copies disagree' EPS cells by the face of the cell's own periodic filing (Dhairya 2026-10-31:
"when one copy equals the periodic filing's face, keep it"). Read-only; rewrites the scan outcomes file.

Input: nc_fsn_outcomes.json (eps_fsn_scan.py) and face_read.json (the face read: per cell, the values printed in the
cell's own 10-K quarterly-data note or 10-Q income statement R page, 3-month column). A cell becomes
replace_with_fsn_value only when exactly ONE distinct copy value equals a printed face value; that copy (earliest
filed) is the witness and the face read is recorded with it. Otherwise it stays fsn_copies_disagree (hidden).
usage: eps_face_resolve.py <outcomes.json> <face_read.json> <copies.json>
"""

import json
import sys
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal


def month_end(d: date) -> date:
    this = date(d.year, d.month, monthrange(d.year, d.month)[1])
    prev = d.replace(day=1) - timedelta(days=1)
    return this if (this - d) <= (d - prev) else prev


def main(outcomes_path: str, face_path: str, copies_path: str) -> None:
    outcomes = json.load(open(outcomes_path))
    faces = {f["canonical_fact_id"]: f for f in json.load(open(face_path))}
    copies = json.load(open(copies_path))
    resolved = 0
    for x in outcomes:
        f = faces.get(x["canonical_fact_id"])
        if x["outcome"] != "fsn_copies_disagree" or not f or not f.get("face"):
            continue
        printed = {Decimal(h["value"]) for h in f["face"]}
        matching = [
            v
            for v in x["values"]
            if any(abs(Decimal(v) - p) <= Decimal("0.005") for p in printed)
        ]
        if len(matching) != 1:
            continue
        end, start = date.fromisoformat(x["end"]), date.fromisoformat(x["start"])
        ddate = month_end(end).strftime("%Y%m%d")
        q = str(round((end - start).days / 91.3))
        dd = None  # the witness copy: the cell's tag order, its exact FSN key, the matching value, earliest filed
        for tag in x["tags"]:
            rows = [r for r in copies.get(f"{x['cik']}|{tag}|{ddate}|{q}", [])
                    if abs(Decimal(r[0]) - Decimal(matching[0])) <= Decimal("0.005")]  # fmt: skip
            if rows:
                dd = (tag, min(rows, key=lambda r: (r[3], r[1])))
                break
        if dd is None:
            continue
        tag, (v, acc, form, filed, axis) = dd
        hit = next(
            h
            for h in f["face"]
            if abs(Decimal(h["value"]) - Decimal(matching[0])) <= Decimal("0.005")
        )
        x.update({"outcome": "replace_with_fsn_value", "value": str(Decimal(v)), "accession": acc, "form": form,
                  "filed": filed, "tag": tag, "axis": axis, "copies": len(x["values"]),
                  "face_check": {"accession": f["accession"], "report": hit["report"], "label": hit["label"],
                                 "value": hit["value"]}})  # fmt: skip
        resolved += 1
    json.dump(outcomes, open(outcomes_path, "w"), indent=0)
    print(json.dumps({"resolved_by_face": resolved}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
