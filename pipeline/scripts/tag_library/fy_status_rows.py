"""Every FY0/FY-1 template cell that no concept/component row serves gets a TAGLESS status row in the map (Engineering
2026-11-12: the map is the single source; the seeder writes each as a reasoned blank). decision not_in_template (a
template-OUT read, a combined line, a perimeter exclusion) or not_presented (not printed, or held: the reason class and
rule name the hold). One row per cell (era = that period end); open periods already have their own tagless rows and are
skipped. The library's tagged read_status stand-ins (taxonomy 'scrooner') are replaced by these rows.
Usage: fy_status_rows.py <tag_map.csv> <fy_check.csv> <open_periods.csv> <concepts_catalog.csv> <out.csv>"""
import csv
import re
import sys

tm, fy, op, cc, out = sys.argv[1:6]
rows = [r for r in csv.DictReader(open(tm)) if r["decided_by"] not in ("read_status", "fy_status")]  # rerun-safe
cols = list(rows[0])
cat = {r["name"]: r["statement"] for r in csv.DictReader(open(cc))}
STMT = {"income_statement": "IS", "balance_sheet": "BS", "cash_flow": "CF"}
EXTRA_STMT = {"dividends_per_share_resolved": "IS"}
opens = {(r["company_id"], r["concept"].removesuffix("_resolved"), r["period"]) for r in csv.DictReader(open(op))}
meta = {}
for r in rows:
    meta.setdefault(r["company_id"], r)


def name(dp):
    return dp + "_resolved" if dp + "_resolved" in cat else dp


NOT_IN_TEMPLATE = {"combined", "line_presented_combined_with_others", "ppe_incl_operating_lease_rou"}


def classify(status):
    """(decision, reason_class) for a FY status from coverage_full / coverage_fy; None for a served or open cell."""
    s = status.removeprefix("read: ")
    if s.startswith("row: "):  # a status row of an earlier run (coverage_fy over a map that already has them)
        rc = s[5:]
        return ("not_in_template" if rc.startswith("not_in_template") or rc in NOT_IN_TEMPLATE else "not_presented"), rc
    if s in ("served", "GAP") or s.startswith("open:"):  # a GAP stays a gap: never hidden behind a reason row
        return None
    if s.startswith(("read-verified pass of: template-OUT", "combined", "line_presented_combined_with_others", "ppe_incl_operating_lease_rou")):
        return "not_in_template", "not_in_template_read_verified" if "template-OUT" in s else s.split(" (")[0]
    if s.startswith("held_"):  # already a hold reason class
        return "not_presented", s
    if s.startswith("not_presented"):
        return "not_presented", "not_presented_read_verified"
    m = re.match(r"held (C\d+|R\d+)", s)
    if m or s.startswith("held_debt_lane"):
        return "not_presented", "held_" + (m.group(1).lower() if m else "c8")
    m = re.match(r"excluded with point reason \((\w+)\)", s)
    if m:
        return "not_presented", m.group(1)
    slug = re.sub(r"[^a-z0-9]+", "_", s.split(" (")[0].lower()).strip("_")[:60]
    return "not_presented", "held_" + slug  # cover page, tax note, COND template seed, a read under review: held, never a value


new, seen = [], set()
for r in csv.DictReader(open(fy)):
    c, dp, p = r["company_id"], r["data_point"], r["period"]
    k = classify(r["status"])
    if not k or (c, dp, p) in opens or (c, dp, p) in seen:
        continue
    seen.add((c, dp, p))
    con = name(dp)
    m = meta.get(c, {})
    e = {k2: "" for k2 in cols}
    e.update(company_id=c, cik=m.get("cik", ""), rank=m.get("rank", ""), ticker=r["ticker"], stmt=STMT.get(cat.get(con, ""), EXTRA_STMT.get(con, "IS")),
             decision=k[0], canonical_concept=con, reason_class=k[1], era_from=p, era_to=p, decided_by="fy_status",
             rule_id="tagmap.fy_status@1", reason=f"{r['fy']} {p}: {r['status'][:180]}", lines="0", filings="0")
    new.append(e)
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows + new)
print("fy status rows", len(new), "| decisions", {d: sum(1 for e in new if e["decision"] == d) for d in ("not_presented", "not_in_template")})
