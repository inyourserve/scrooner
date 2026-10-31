"""Face sums for the revenue sibling holds (stdlib, run with -I; no database).
Verifier 2026-10-31: a hold that leaves a known-wrong production value is not
neutral (Snap-on Q2 2018: production 949.2M, face 954.6 + 82.0 = 1,036.6M).

For every held cell, the printed lines (root + siblings) are read from the
filer's OWN instance facts in the FSN num file of that filing (undimensioned,
no co-registrant, same end date and number of quarters), custom lines
included (companyfacts never carries those). Then:
  sum_ties_tagged_total   a standard revenue total the filer TAGGED in the same
                          filing and column (not printed) equals the face sum:
                          the filer's own arithmetic -> release candidate
  sum_no_tagged_total     no tagged total; the face sum is the only reading
  sum_not_computable      a printed line has no undimensioned value in num
and production is compared with the face sum (equal -> production right).
usage: is_sibling_sums.py <sibling_holds.jsonl> <is_fsn_dir> <fsn_root> <out.jsonl>
"""
import csv
import glob
import gzip
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

csv.field_size_limit(1 << 24)
REV_TOTAL = ("Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
             "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet", "RegulatedAndUnregulatedOperatingRevenue")


def unit(v):
    u = Decimal(10) ** 11
    while u > 1 and v % u != 0:
        u /= 10
    return u


def main(holds_path, is_fsn, fsn_root, out_path):
    holds = [json.loads(line) for line in open(holds_path)]
    accs = {h["accession"] for h in holds}
    period_of = {}
    for p in sorted(glob.glob(f"{is_fsn}/*_is_pre.jsonl.gz")):
        per = Path(p).name.split("_")[0]
        for line in gzip.open(p, "rt"):
            a = line[line.find('"adsh": "') + 9:][:20]
            if a in accs:
                period_of.setdefault(a, per)
    by_period = defaultdict(set)
    for a in accs:
        if a in period_of:
            by_period[period_of[a]].add(a)
    facts = defaultdict(dict)  # (adsh, ddate, qtrs) -> {tag: value}
    for per, want in sorted(by_period.items()):
        proc = subprocess.Popen(["zstd", "-dc", f"{fsn_root}/{per}/{per}_num.tsv.zst"], stdout=subprocess.PIPE)
        rd = csv.DictReader(io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace", newline=""),
                            delimiter="\t", quoting=csv.QUOTE_NONE)
        for r in rd:
            if r["adsh"] in want and r["dimn"] == "0" and not r["coreg"] and r["iprx"] == "0" and r["uom"] == "USD" and r["value"]:
                facts[(r["adsh"], r["ddate"], r["qtrs"])].setdefault(r["tag"], Decimal(r["value"]))
        proc.wait()
    out, stats = [], Counter()
    for h in holds:
        s0, e0 = date.fromisoformat(h["start"]), date.fromisoformat(h["end"])
        key = (h["accession"], e0.strftime("%Y%m%d"), str(round(((e0 - s0).days + 1) / 91.3)))
        f = facts.get(key, {})
        members = [h["root_tag"]] + [x["tag"] for x in h["siblings"]]
        vals = {t: f.get(t) for t in members}
        rec = dict(h, member_values={t: (str(v) if v is not None else None) for t, v in vals.items()})
        if any(v is None for v in vals.values()):
            rec["sum_class"] = "sum_not_computable"
        else:
            total = sum(vals.values())
            rec["face_sum"] = str(total)
            tagged = {t: f[t] for t in REV_TOTAL if t in f and t not in members}
            tie = [t for t, v in tagged.items() if abs(v - total) * 2 <= max(unit(v), unit(total))]
            rec["tagged_totals"] = {t: str(v) for t, v in tagged.items()}
            rec["sum_class"] = "sum_ties_tagged_total" if tie else "sum_no_tagged_total"
            if tie:
                rec["tie_tag"] = tie[0]
        pv = Decimal(h["prod_value"]) if h.get("prod_value") else None
        if "face_sum" in rec and pv is not None:
            fs = Decimal(rec["face_sum"])
            rec["prod_vs_face_sum"] = "equal" if abs(fs - pv) * 2 <= max(unit(fs), unit(pv)) else "differs"
        else:
            rec["prod_vs_face_sum"] = "unknown" if pv is not None else "prod_blank"
        stats[(rec["sum_class"], rec["prod_vs_face_sum"])] += 1
        out.append(rec)
    with open(out_path, "w") as fh:
        for r in out:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    for k, v in sorted(stats.items()):
        print(v, k)
    print("companies", len({r["cik"] for r in out}), "accessions without FSN num rows", len(accs - set(period_of)))


if __name__ == "__main__":
    main(*sys.argv[1:5])
