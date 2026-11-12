"""FY0 / FY-1 check: every in-template statement concept must, at each company's last two 10-K period ends, be served by a
concept/component row whose era covers that date, or carry a status (combined, a point reason, held, off-statement,
open-period not-printed, or a read-verified status). A tag switch in the latest 10-K must never leave the cell blank.
Usage: coverage_fy.py <tag_map.csv> <coverage_full.csv> <fy_periods.csv> <open_periods.csv> <out.csv>"""
import collections
import csv
import sys

tm, cov, fy, op, out = sys.argv[1:6]
base = lambda c: c[:-9] if c.endswith("_resolved") else c
rows = list(csv.DictReader(open(tm)))
stat = collections.defaultdict(list)  # (company, concept) -> [(from, to, status)]
serve = collections.defaultdict(list)  # (company, concept) -> [(from, to)]
for r in rows:
    con = r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else ""
    if con:
        serve[(r["company_id"], base(con))].append((r["era_from"], r["era_to"]))
    if r["decision"] in ("not_presented", "not_in_template"):  # a tagless status row (fy_status_rows.py)
        stat[(r["company_id"], base(r["canonical_concept"]))].insert(0, (r["era_from"], r["era_to"], r["reason_class"]))  # the cell's own status row first
    if r["decided_by"] == "read_status":  # an FY status from the full 10-K read (not printed, held, combined, perimeter)
        stat[(r["company_id"], base(r["components"]))].append((r["era_from"], r["era_to"], r["reason_class"]))
    if r["decision"] == "combined":
        for k in (r["components"] or "").split(";"):
            if k and k != "other":
                stat[(r["company_id"], base(k))].append((r["era_from"], r["era_to"], "combined"))
    if r["decision"] == "concept" and r["tag"] == "EarningsPerShareBasicAndDiluted":
        for k in ("basic_eps", "diluted_eps"):
            serve[(r["company_id"], k)].append((r["era_from"], r["era_to"]))
periods = collections.defaultdict(list)
for r in csv.DictReader(open(fy)):
    periods[r["company_id"]].append(r["period"])
opens = {(r["company_id"], base(r["concept"]), r["period"]) for r in csv.DictReader(open(op))}
res, gaps = [], 0
for r in csv.DictReader(open(cov)):
    c, dp, st = r["company_id"], r["data_point"], r["status"]
    for i, p in enumerate(sorted(periods.get(c, []), reverse=True)[:2]):
        label = "FY0" if i == 0 else "FY-1"
        if st == "sourced":
            ok = any(a <= p <= b for a, b in serve.get((c, dp), []))
            why = next((w for a, b, w in stat.get((c, dp), []) if a <= p <= b), "")
            s = "served" if ok else ("read: " + why if why else "open: not printed in that filing" if (c, dp, p) in opens else "GAP")
        else:
            why = next((w for a, b, w in stat.get((c, dp), []) if a <= p <= b), "")
            s = "row: " + why if why else st
        if s == "GAP":
            gaps += 1
        res.append({"company_id": c, "ticker": r["ticker"], "data_point": dp, "fy": label, "period": p, "status": s})
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(res[0]))
    w.writeheader()
    w.writerows(res)
for g in [x for x in res if x["status"] == "GAP"][:40]:
    print("GAP", g["ticker"], g["data_point"], g["fy"], g["period"])
print("fy cells", len(res), "gaps", gaps)
