"""Read-only. Build per-10-K face-line extract (stmt, report, line, tag, version, label, negating, FY/instant value) from FSDS.
Usage: python3 -I extract.py FSDS_DIR OUT_JSON"""
import csv, json, sys, os, collections
d, out = sys.argv[1], sys.argv[2]
rd = lambda n: csv.DictReader(open(os.path.join(d, n), newline="", encoding="utf-8", errors="replace"), delimiter="\t")
sub = {r["adsh"]: r for r in rd("sub.txt") if r["form"] in ("10-K", "10-Q")}
pre = collections.defaultdict(list); keys = set()
for r in rd("pre.txt"):
    if r["adsh"] in sub and r["stmt"] in ("IS", "CF", "BS"):
        pre[r["adsh"]].append((r["stmt"], int(r["report"]), int(r["line"]), r["tag"], r["version"], r["plabel"], r["negating"], r["inpth"]))
        keys.add((r["adsh"], r["tag"], r["version"]))
val = {}
for r in rd("num.txt"):
    a = r["adsh"]
    if a not in sub or (a, r["tag"], r["version"]) not in keys: continue
    if r["uom"] != "USD" or r["segments"] or r["coreg"] or not r["value"]: continue
    if r["ddate"] != sub[a]["period"]: continue
    pass
    val.setdefault((a, r["tag"], r["version"]), {})[r["qtrs"]] = r["value"]
res = {}
for a, rows in pre.items():
    s = sub[a]
    lines = []
    for stmt, rep, ln, tag, ver, lab, neg, inpth in sorted(rows, key=lambda x: (x[1], x[2])):
        if inpth == "1": continue
        v = val.get((a, tag, ver))
        lines.append([stmt, rep, ln, tag, ver.split("/")[0], lab, neg, v])
    res[a] = {"name": s["name"], "cik": s["cik"], "sic": s["sic"], "period": s["period"], "fy": s["fy"], "form": s["form"], "lines": lines}
json.dump(res, open(out, "w"))
print(len(res), "filings")
