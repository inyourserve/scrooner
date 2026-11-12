"""Full sector-template coverage for the statement data points (catalog concepts in the template).
Every company x in-template concept gets one status; GAP means none applies.
Usage: coverage_full.py <tag_map.csv> <template_points.csv> <concepts.csv> <note_candidates.csv> <out_candidates.csv> <out.csv>"""
import collections
import csv
import sys

tm, tp, cc, nc, oc, out = sys.argv[1:7]
base = lambda c: c[:-9] if c.endswith("_resolved") else c
ALIAS = {"revenue": "revenue_sanity"}
cat = {r["name"] for r in csv.DictReader(open(cc))}
HELD = {"total_debt": "held C8 (debt lane)", "total_debt_split": "held C8", "total_liabilities": "held C8 (BS derive lane)",
        "dividends_per_share": "held C6 (0122)", "shares_outstanding": "held R2 (no BS-parenthetical count; never the dei cover count)"}
OFF = {"employee_count": "cover page / 10-K text", "public_float": "cover page", 
       "effective_tax_rate_reported": "tax note", "collaborative_arrangement_revenue": "template seed: should be COND",
       "net_lease_revenue": "template seed: should be COND"}
m = list(csv.DictReader(open(tm)))
tick = {r["company_id"]: r["ticker"] for r in m}
st = collections.defaultdict(dict)
for r in m:
    c, con = r["company_id"], ""
    if r["decision"] == "concept":
        con = base(r["canonical_concept"])
    elif r["decision"] == "component":
        con = base(r["parent_concept"])
    if con:
        st[c][con] = "sourced"
    if r["decision"] == "concept" and r["tag"] == "EarningsPerShareBasicAndDiluted":
        st[c]["basic_eps"] = st[c]["diluted_eps"] = "sourced"
    if r["decision"] == "combined":
        for k in (r["components"] or "").split(";"):
            st[c].setdefault(base(k), "combined (reasoned blank)")
POINT_REASON = {"nonoperating_total_incl_interest": "other_income_expense_net", "parent_equity_not_printed": "stockholders_equity",
                "bank_cash_perimeter": "cash_and_equivalents", "cash_incl_short_term_investments": "cash_and_equivalents",
                "catalog_gap_bank_nii": "interest_income", "total_costs_incl_cost_of_revenue": "operating_expenses",
                "not_sga_broad_operating_costs": "sga_expense", "cost_of_products_not_total_cor": "cost_of_revenue",
                "component_of_unprinted_total": "cost_of_revenue", "d_and_a_not_presented": "depreciation_and_amortization",
                "bank_interest_income_component": "interest_income",
                "inventory_total_not_printed": "inventory", "ci_incl_nci": "comprehensive_income", "shares_per_class_only": "shares_outstanding",
                "shares_member_column_only": "shares_outstanding", "revenue_incl_other_income": "revenue_sanity", "bank_cash_split_line": "cash_and_equivalents"}
for r in m:
    if r["decision"] == "excluded" and r["reason_class"] in POINT_REASON:
        st[r["company_id"]].setdefault(POINT_REASON[r["reason_class"]], "excluded with point reason (" + r["reason_class"] + ")")
for r in csv.DictReader(open(nc)):
    st[r["company_id"]].setdefault(r["concept"], "note-sourced candidate (Verifier draw)")
for r in csv.DictReader(open(oc)):
    st[r["company_id"]].setdefault(r["data_point"], "template-OUT candidate (Verifier draw)")
if len(sys.argv) > 7:  # per-company full 10-K reads: the source of every note-sourced and OUT status (Dhairya 2026-11-12)
    tick_id = {v: k for k, v in tick.items()}
    for r in csv.DictReader(open(sys.argv[7])):
        c = r["company_id"] or tick_id.get(r["ticker"], "")
        dp = ALIAS.get(base(r["data_point"]), base(r["data_point"]))
        if c and not r["verdict"].startswith(("PASS", "ERA")):
            st[c].setdefault(dp, "read-verified " + r["verdict"].lower())
        elif c and r["verdict"].startswith("PASS") and r["our_status"] and not r["our_status"].startswith(("mapped", "component", "combined")):
            st[c].setdefault(dp, "read-verified pass of: " + r["our_status"][:60])
rows, seen = [], set()
for r in csv.DictReader(open(tp)):
    if r["data_point"] not in cat:
        continue
    c, b = r["company_id"], ALIAS.get(base(r["data_point"]), base(r["data_point"]))
    if (c, b) in seen or c not in tick:
        continue
    seen.add((c, b))
    s = (st[c].get(b) if st[c].get(b) == "sourced" else None) or HELD.get(b) or OFF.get(b) or st[c].get(b) or "GAP"
    rows.append({"company_id": c, "ticker": tick[c], "template": r["template"], "data_point": b, "status": s})
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
cnt = collections.Counter(r["status"].split(" (")[0] for r in rows)
print(len(rows), "points;", dict(cnt))
gaps = [r for r in rows if r["status"] == "GAP"]
for g in gaps[:30]:
    print("GAP", g["ticker"], g["data_point"])
print("gaps", len(gaps))
