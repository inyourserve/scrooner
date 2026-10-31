"""Calc-structure test for the revenue sibling holds (stdlib, run with -I; no
database). Manager rule 2026-10-31: a sibling is ADDITIVE only when it is a
calc child (weight +1) of the same revenue parent as the root in that filing's
own FSN cal tree; subtotals, gains and expenses fail that test by construction.

Per held cell (face values from is_sibling_sums.py):
  resolves_to_sum   a revenue-named parent (printed or not; never gross profit /
                    operating income) whose children are EXACTLY the root plus
                    the additive siblings, all +1; value = root + additive
                    siblings; the parent's own tagged value, if any, must tie
  resolves_to_root  no sibling is a +1 child of a revenue parent of the root:
                    the root is the only revenue line; value = root
  unresolved        a revenue parent of the root has other children too, a
                    weight is not +1, a needed value is missing, or the parent's
                    tagged value does not tie
Direction = production vs the resolved value (equal / differs / prod_blank).
usage: is_sibling_calc.py <sibling_holds_face_sums.jsonl> <is_fsn_dir> <out.jsonl>
"""
import glob
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

REV_PARENT_RX = re.compile(r"Revenue|Sales")
NOT_REV_PARENT_RX = re.compile(r"Cost|Expense|Profit|Margin|OperatingIncome|IncomeLoss|Gain")


def unit(v):
    u = Decimal(10) ** 11
    while u > 1 and v % u != 0:
        u /= 10
    return u


def main(sums_path, is_fsn, out_path):
    cells = [json.loads(line) for line in open(sums_path)]
    accs = {c["accession"] for c in cells}
    arcs = defaultdict(lambda: defaultdict(dict))  # adsh -> parent -> {child: weight}
    for p in sorted(glob.glob(f"{is_fsn}/*_cal.jsonl.gz")):
        for line in gzip.open(p, "rt"):
            a = json.loads(line)
            if a["adsh"] in accs:
                arcs[a["adsh"]][a["p"]][a["c"]] = Decimal(a["w"])
    out, stats = [], Counter()
    for c in cells:
        root = c["root_tag"]
        sibs = [s["tag"] for s in c["siblings"]]
        tree = arcs.get(c["accession"], {})
        parents = {p: kids for p, kids in tree.items() if root in kids and kids[root] == 1
                   and REV_PARENT_RX.search(p) and not NOT_REV_PARENT_RX.search(p)}
        additive = sorted({s for p, kids in parents.items() for s in sibs if kids.get(s) == 1})
        vals = c.get("member_values") or {}
        res, value, detail = None, None, {}
        if not tree:
            res = "unresolved"; detail["why"] = "no calc arcs for this filing"
        elif not additive:
            if vals.get(root) is not None:
                res, value = "resolves_to_root", Decimal(vals[root])
                detail["why"] = "no sibling is a +1 child of a revenue parent of the root" + ("" if parents else " (root has no revenue parent)")
            else:
                res = "unresolved"; detail["why"] = "root value missing"
        else:
            exact = [p for p, kids in parents.items() if set(kids) == {root, *additive} and all(w == 1 for w in kids.values())]
            if not exact:
                res = "unresolved"; detail["why"] = "revenue parent has other children or non-+1 weights"
                detail["parents"] = {p: sorted(k) for p, k in parents.items()}
            elif any(vals.get(t) is None for t in [root, *additive]):
                res = "unresolved"; detail["why"] = "a member value is missing"
            else:
                value = sum(Decimal(vals[t]) for t in [root, *additive])
                p = exact[0]
                detail["parent"] = p
                tagged = (c.get("tagged_totals") or {}).get(p)
                if tagged is not None and abs(Decimal(tagged) - value) * 2 > max(unit(Decimal(tagged)), unit(value)):
                    res = "unresolved"; detail["why"] = f"parent {p} tagged {tagged} does not tie the sum {value}"
                else:
                    res = "resolves_to_sum"
                    detail["parent_tagged_value"] = tagged
        detail["additive"] = additive
        detail["non_additive"] = [s for s in sibs if s not in additive]
        pv = Decimal(c["prod_value"]) if c.get("prod_value") else None
        if value is None:
            direction = "n/a"
        elif pv is None:
            direction = "prod_blank"
        else:
            direction = "equal" if abs(pv - value) * 2 <= max(unit(pv), unit(value)) else "differs"
        stats[(res, direction)] += 1
        out.append({**{k: c[k] for k in ("cik", "start", "end", "accession", "hold_code", "root_tag", "prod_value")},
                    "resolution": res, "resolved_value": str(value) if value is not None else None,
                    "prod_vs_resolved": direction, **detail})
    with open(out_path, "w") as fh:
        for r in out:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    for k, v in sorted(stats.items()):
        print(v, k)


if __name__ == "__main__":
    main(*sys.argv[1:4])
