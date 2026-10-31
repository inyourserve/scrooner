"""Removal-only revision of a capex release package: drop the listed cells from the release-1
cells file, before-image, rollback and touched-CIK list; cells whose production value equals the
filer's figure go to the keep-list (with the evidence), the rest to a hold list. Asserts the result
is a subset of the input with identical values. Never adds or changes a cell. Nothing applied.
usage: capex_release_remove.py <package_dir> <removals.json> <label>
"""
import hashlib
import json
import sys
from pathlib import Path

d, removals, label = Path(sys.argv[1]), json.load(open(sys.argv[2])), sys.argv[3]
key = lambda x: (x["cik"], x["end"], x["qtrs"])  # noqa: E731
drop = {key(x) for x in removals}
cells_in = [json.loads(x) for x in open(d / "capex_release1_cells.jsonl")]
cells = [c for c in cells_in if key(c) not in drop]
assert len(cells_in) - len(cells) == len(drop), "a removal is not in the release"
data = "".join(json.dumps(c, sort_keys=True) + "\n" for c in cells).encode()
(d / "capex_release1_cells.jsonl").write_bytes(data)
digest = hashlib.sha256(data).hexdigest()
(d / "capex_release1_cells.sha256").write_text(f"{digest}  capex_release1_cells.jsonl\n")
keep_ids = {(c["cik"], c["end"], c["qtrs"]) for c in cells}
before_in = [json.loads(x) for x in open(d / "capex_release1_before_image.jsonl")]
dropped_cells = [c for c in cells_in if key(c) in drop]
# the before-image row of a dropped cell is the production row the cell would have replaced
drop_fact = set()
for c in dropped_cells:
    for b in before_in:
        if b["cik"] == c["cik"] and b["value_before"] == str(c["prod_value"]) and b["end"][:7] == c["end"][:7] and b["qtrs"] == c["qtrs"]:
            drop_fact.add(b["canonical_fact_id"])
before = [b for b in before_in if b["canonical_fact_id"] not in drop_fact]
assert len(before_in) - len(before) == len(drop) and len(before) == len(cells), (len(before_in), len(before), len(cells))
with open(d / "capex_release1_before_image.jsonl", "w") as f:
    for b in before:
        f.write(json.dumps(b, sort_keys=True) + "\n")
roll = [x for x in open(d / "capex_release1_rollback.sql") if not any(f"where id = {i};" in x for i in drop_fact)]
open(d / "capex_release1_rollback.sql", "w").writelines(roll)
ciks = sorted({c["cik"] for c in cells})
(d / "release1_touched_ciks.txt").write_text("".join(f"{c:010d}\n" for c in ciks))
keep = json.load(open(d / "capex_release_keep_list.json"))
keep += [x for x in removals if x["to"] == "keep_list"]
json.dump(keep, open(d / "capex_release_keep_list.json", "w"), indent=1)
holds = [x for x in removals if x["to"] != "keep_list"]
json.dump(holds, open(d / f"capex_release1_held_{label}.json", "w"), indent=1)
pkg = json.load(open(d / "PACKAGE.json"))
r1 = pkg["release1"]
r1.update({"sha256": digest, "cells": len(cells), "companies": len(ciks),
           "before_image": f"capex_release1_before_image.jsonl ({len(before)} canonical_fact rows)",
           "keep_list": f"capex_release_keep_list.json ({len(keep)} cells where production equals the filer's own total; untouched)"})
r1.setdefault("removals", []).append({"label": label, "removed": len(drop), "to_keep_list": len(drop) - len(holds), "to_hold": len(holds),
                                      "rule": "a filer-printed capex total below the investing section differs from the release value (filer's total is the anchor)"})
json.dump(pkg, open(d / "PACKAGE.json", "w"), indent=1)
# subset check against the input
idx = {key(c): c for c in cells_in}
assert all(idx[key(c)]["value"] == c["value"] for c in cells)
print(f"removed {len(drop)} -> release 1 {len(cells)} cells at {len(ciks)} companies; keep-list {len(keep)}; held {len(holds)}; sha256 {digest}")
