"""Per company and core template concept: sourced (a concept/component row covering the company's whole filing
range), reasoned (an excluded row whose reason says why the point has no source), or GAP. Usage: coverage.py <tag_map.csv>"""
import collections
import csv
import sys

CORE = ["revenue_sanity_resolved", "net_income_resolved", "total_assets_resolved", "stockholders_equity_resolved",
        "cash_and_equivalents_resolved", "cfo_resolved", "cash_flow_investing_resolved", "cash_flow_financing_resolved",
        "basic_eps_resolved", "diluted_eps_resolved", "income_before_tax_resolved", "income_tax_expense_resolved"]
REASONS = {"stockholders_equity_resolved": {"parent_equity_not_printed", "equity_incl_nci"},
           "cash_and_equivalents_resolved": {"bank_cash_perimeter", "cash_incl_short_term_investments"},
           "revenue_sanity_resolved": {"catalog_gap_bank_nii"}}
FEEDS_BOTH = {"EarningsPerShareBasicAndDiluted": ("basic_eps_resolved", "diluted_eps_resolved")}
rows = list(csv.DictReader(open(sys.argv[1])))
span, eras, rc, tick = {}, collections.defaultdict(list), collections.defaultdict(set), {}
for r in rows:
    c = r["company_id"]
    tick[c] = r["ticker"]
    if r["era_from"]:
        lo, hi = span.get(c, (r["era_from"], r["era_to"]))
        span[c] = (min(lo, r["era_from"]), max(hi, r["era_to"]))
    con = r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else ""
    if con:
        eras[(c, con)].append((r["era_from"], r["era_to"]))
    if r["decision"] == "concept" and r["tag"] in FEEDS_BOTH:
        for k in FEEDS_BOTH[r["tag"]]:
            eras[(c, k)].append((r["era_from"], r["era_to"]))
    if r["decision"] == "excluded" and any(r["reason_class"] in v for v in REASONS.values()):
        for k, v in REASONS.items():
            if r["reason_class"] in v:
                eras[(c, k)].append((r["era_from"], r["era_to"]))  # a reasoned point: the hole is explained
    if r["decision"] == "excluded":
        rc[c].add(r["reason_class"])
gaps = 0
for c in sorted(tick, key=lambda c: tick[c]):
    for con in CORE:
        e = sorted(eras.get((c, con), []))
        if not e:
            if REASONS.get(con, set()) & rc[c]:
                continue
            print(f"GAP  {tick[c]:6} {con}: no source and no reason"); gaps += 1
            continue
        # holes between consecutive eras longer than ~4 months, or before/after the company's span
        lo, hi = span[c]
        cur = e[0][1]
        holes = []
        if e[0][0] > lo and e[0][0][:7] > lo[:4] + "-06":
            holes.append(f"starts {e[0][0]} (company from {lo})")
        for a, b in e[1:]:
            if a > cur and (int(a[:4]) * 12 + int(a[5:7])) - (int(cur[:4]) * 12 + int(cur[5:7])) > 4:
                holes.append(f"hole {cur}..{a}")
            cur = max(cur, b)
        if (int(hi[:4]) * 12 + int(hi[5:7])) - (int(cur[:4]) * 12 + int(cur[5:7])) > 4:
            holes.append(f"ends {cur} (company to {hi})")
        if holes:
            print(f"ERA  {tick[c]:6} {con}: {'; '.join(holes)}"); gaps += 1
print("gaps", gaps)
