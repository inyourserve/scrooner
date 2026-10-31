"""Changed cells between two Family C dry runs (C_per_share_derived_cells.csv), keyed by canonical_fact_id.

usage: famc_changed_cells.py <old_cells.csv> <new_cells.csv> <out.csv>
A row is written for every cell whose action, reason, replacement value, replacement accession or note differs, or
that is in only one run; the summary counts transitions (old action/reason -> new action/reason).
"""

import csv
import json
import sys
from collections import Counter

FIELDS = ("action", "reason_code", "replacement_value", "replacement_accession", "note")


def load(path: str) -> dict[str, dict[str, str]]:
    with open(path, newline="") as fh:
        return {r["canonical_fact_id"]: r for r in csv.DictReader(fh)}


def label(r: dict[str, str] | None) -> str:
    return "-" if r is None else f"{r['action']}:{r['reason_code'] or ''}"


def main(old_path: str, new_path: str, out_path: str) -> None:
    old, new = load(old_path), load(new_path)
    changed = []
    for cid in sorted(set(old) | set(new), key=int):
        a, b = old.get(cid), new.get(cid)
        if a is not None and b is not None and all(a[f] == b[f] for f in FIELDS):
            continue
        ref = b or a
        assert ref is not None
        changed.append({"canonical_fact_id": cid, "company_id": ref["company_id"], "concept": ref["concept"],
                        "period_end": ref["period_end"], "stored_value": ref["stored_value"],
                        "old": label(a), "new": label(b),
                        "old_replacement": "" if a is None else a["replacement_value"],
                        "new_replacement": "" if b is None else b["replacement_value"],
                        "new_accession": "" if b is None else b["replacement_accession"],
                        "new_note": "" if b is None else b["note"]})  # fmt: skip
    with open(out_path, "w", newline="") as fh:
        w = csv.DictWriter(
            fh, fieldnames=list(changed[0]) if changed else ["canonical_fact_id"]
        )
        w.writeheader()
        w.writerows(changed)
    print(json.dumps({"changed": len(changed),
                      "transitions": dict(Counter(f"{c['old']} -> {c['new']}" for c in changed).most_common())},
                     indent=1))  # fmt: skip


if __name__ == "__main__":
    main(*sys.argv[1:4])
