"""Split the total-liabilities dry-run into release 1 and release 2 (Dhairya
2026-10-26). Stratum per cell, by comparison with the Verifier-sampled
population (the cells file committed at 8fdb9ca):
  sampled        same (cik, end), same slot value, same rule as the sampled file
  changed_rule   present in the sampled file, slot value or rule differs now
  new_since_fill not in the sampled file (became computable after the FSN fill)
  fill_prefill   slot_fills_blank with no instance/FSN fill (existed before the fill)
  fill_new       slot_fills_blank that needed a fill
  hold_custom_subtotal  would-hide where a filled custom line made the identity fail
  hold_other     other would-hide
Release 1 = sampled differences + fill_prefill fills + the Verifier-confirmed
wrong would-hide cells (hide list) minus the keep-list. Release 2 = everything
else that changes a shown value. Writes both cell files, their digests and a
strata count file. Nothing touches the database.
usage: bs_release_strata.py <sampled_cells.jsonl> <current_cells.jsonl> <keep_list.json> <hide_confirmed.json> <out_prefix>
"""
import hashlib
import json
import sys
from collections import Counter

sampled_path, current_path, keep_path, hide_path, out = sys.argv[1:6]
sampled = {}
for line in open(sampled_path):
    c = json.loads(line)
    sampled[(c["cik"], c["end"])] = c
keep = {(k["cik"], k["end"]) for k in json.load(open(keep_path))}
hide_ok = {(k["cik"], k["end"]) for k in json.load(open(hide_path))}
# per-cell replay details (instance fills) come from the replay reports; the
# comparison carried 'reading' and 'rule' only, so a fill is 'prefill' when the
# cell has no FSN/instance evidence in the current replay reports
filled = set()
gapinfo = {}
from decimal import Decimal
import glob
import os
for rep in glob.glob(os.path.join(os.path.dirname(current_path), "bs_replay_*_report.json")):
    try:
        r = json.load(open(rep))
    except Exception:  # noqa: BLE001
        continue
    for c in r.get("cells", []):
        if c.get("instance_filled"):
            filled.add((c["cik"], c["end"]))
        gapinfo[(c["cik"], c["end"])] = (abs(Decimal(c.get("gap", "0"))), Decimal(c.get("unit", c.get("tol", "1"))), c.get("rule"))
rel1, rel2, strata = [], [], Counter()
for line in open(current_path):
    c = json.loads(line)
    key = (c["cik"], c["end"])
    st = c["state"]
    if st == "slot_differs":
        s = sampled.get(key)
        if s and s["state"] == "slot_differs" and s["slot"] == c["slot"] and s["rule"] == c["rule"]:
            stratum = "sampled"
        elif s and s["state"] == "slot_differs":
            stratum = "changed_rule"
        else:
            stratum = "new_since_fill"
    elif st == "slot_fills_blank":
        stratum = "fill_new" if key in filled else "fill_prefill"
    elif st == "slot_holds_prod_has_value":
        stratum = "hold_custom_subtotal" if key in filled else "hold_other"
    else:
        stratum = st
    c["stratum"] = stratum
    strata[stratum] += 1
    if key in keep:
        c["release"] = "kept_verified_right"
        continue
    g = gapinfo.get(key)
    exact = g is not None and (g[2] == "printed_total" or g[0] <= g[1])  # face sum ties within ONE printed unit (Verifier release-1 rule)
    if stratum in ("sampled", "fill_prefill") and g is None:
        stratum = c["stratum"] = "no_committed_replay_row"; strata[stratum] += 1
    if stratum in ("sampled", "fill_prefill") and not exact:
        stratum = c["stratum"] = "gap_within_tolerance_not_exact"; strata[stratum] += 1
    if stratum in ("sampled", "fill_prefill") or (stratum.startswith("hold") and key in hide_ok):
        c["release"] = "1"
        rel1.append(c)
    elif stratum in ("gap_within_tolerance_not_exact", "no_committed_replay_row"):
        c["release"] = "2"
        rel2.append(c)
    elif stratum in ("changed_rule", "new_since_fill", "fill_new"):
        c["release"] = "2"
        rel2.append(c)
    elif stratum.startswith("hold"):
        c["release"] = "not_hidden_production_stays"
for name, rows in (("release1", rel1), ("release2", rel2)):
    p = f"{out}_{name}_cells.jsonl"
    with open(p, "w") as f:
        for c in rows:
            f.write(json.dumps(c, sort_keys=True) + "\n")
    d = hashlib.sha256(open(p, "rb").read()).hexdigest()
    open(f"{out}_{name}_cells.sha256", "w").write(d + "\n")
    print(f"{name}: {len(rows)} cells, by stratum {dict(Counter(c['stratum'] for c in rows))}, sha256 {d[:16]}...")
json.dump({"strata": dict(strata), "release1_cells": len(rel1), "release2_cells": len(rel2),
           "kept_verified_right": len(keep), "hide_confirmed_wrong": len(hide_ok)}, open(f"{out}_strata.json", "w"), indent=1)
print("strata:", dict(strata))
