"""Capex release 2a cell list: cells the founder rulings of 2026-11-04 newly publish (published in the
ruled run, held or valued differently in the previous run), classed by the ruling that changed them.
Dry run, for the Verifier draw; the package (before-image, rollback, stale refusal) comes after it passes.
usage: capex_release2a_cut.py <prev_cells.jsonl.gz> <ruled_cells.jsonl.gz> <out_dir>
"""
import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

prev_path, new_path, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)


def load(p):
    d = {}
    for line in gzip.open(p, "rt"):
        c = json.loads(line)
        if c["family"] == "capex":
            d[(c["cik"], c["end"], c["qtrs"])] = c
    return d


prev, new = load(prev_path), load(new_path)
rows = []
for k, c in sorted(new.items()):
    if c["interim"] is None:
        continue
    p = prev.get(k)
    if p and p["interim"] == c["interim"] and not p["interim_reason"]:
        continue  # unchanged by the rulings
    classes = []
    classes += [x for x in c["cases"]]  # leased / software / discontinued
    if c.get("maintenance_lines") or any(re.search(r"turnaround|major (repairs|maintenance)|catalyst|dry.?dock", x["label"], re.I) for x in c["lines"]):
        classes.append("turnaround")
    if any(re.search(r"tenant improvement|construction in progress", x["label"], re.I) for x in c["lines"]):
        classes.append("ti_cip")
    if c.get("exclusion_note"):
        # acquisition lines are not capex (founder ruling for O&G property/acreage; Dhairya 2026-11-04: the same
        # rule for every acquisition line, as in the release-1 removals RYAN/LNTH/QXO)
        classes.append("acquisition_exclusion")
    rows.append({"cik": c["cik"], "ticker": c["ticker"], "end": c["end"], "qtrs": c["qtrs"], "accession": c["accession"],
                 "value": c["interim"], "previous": (p["interim"] if p else None), "previous_reason": (p["interim_reason"] if p else "no_cell"),
                 "classes": classes or ["other_changed"], "prod_value": c["prod_value"],
                 "members": [{"tag": x["tag"], "label": x["label"], "nature": x["nature"], "value": x["value"]} for x in c["lines"]],
                 "exclusion_note": "acquisitions_excluded" if c.get("exclusion_note") else None,
                 "acquisition_lines_excluded": c.get("og_property_acquisitions") or []})
data = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
(out / "capex_release2a_cells.jsonl").write_bytes(data)
by = Counter(cl for r in rows for cl in r["classes"])
summary = {"cells": len(rows), "companies": len({r["cik"] for r in rows}), "sha256": hashlib.sha256(data).hexdigest(),
           "by_class": dict(by), "prod_blank": sum(1 for r in rows if r["prod_value"] is None),
           "companies_by_class": {cl: sorted({r["ticker"] for r in rows if cl in r["classes"]}) for cl in by}}
json.dump(summary, open(out / "SUMMARY.json", "w"), indent=1)
print(json.dumps({k: summary[k] for k in ("cells", "companies", "by_class", "prod_blank")}, indent=1))
