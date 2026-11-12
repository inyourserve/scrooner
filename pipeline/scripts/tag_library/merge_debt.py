"""One seed file: the tag map plus the debt lane's rows; a debt-lane row wins over a library 'excluded'/'combined' row for
the same (company, stmt, tag) in an overlapping era (the library row keeps only the era outside it).
Usage: merge_debt.py <tag_map.csv> <debt_rows.csv> <out.csv>"""
import csv
import datetime
import sys

tm, dr, out = sys.argv[1:4]
rows = list(csv.DictReader(open(tm)))
cols = list(rows[0])
in_map = {r["company_id"] for r in rows}
debt = [{**{k: "" for k in cols}, **r} for r in csv.DictReader(open(dr)) if r["company_id"] in in_map]  # only this map's companies
d1 = lambda d, n: (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()
keep = []
for r in rows:
    hits = [d for d in debt if d["company_id"] == r["company_id"] and d["stmt"] == r["stmt"] and d["tag"] == r["tag"]
            and r["decision"] in ("excluded", "combined") and not (r["era_to"] < d["era_from"] or d["era_to"] < r["era_from"])]
    if not hits:
        keep.append(r)
        continue
    lo, hi = min(d["era_from"] for d in hits), max(d["era_to"] for d in hits)
    if r["era_from"] < lo:
        keep.append({**r, "era_to": d1(lo, -1)})
    if r["era_to"] > hi:
        keep.append({**r, "era_from": d1(hi, 1)})
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(keep + debt)
print("library rows", len(rows), "-> kept", len(keep), "+ debt rows", len(debt))
