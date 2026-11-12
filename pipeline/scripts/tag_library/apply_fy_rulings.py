"""FY0/FY-1 rulings on cells whose mapped tag has no fact in core.fact (Engineering write-plan gate 2026-11-12), applied to
the map: a status ruling cuts the concept's serving rows over the company's last two 10-K period ends and writes one
tagless row per period (decided_by fy_ruling); a tag ruling swaps the serving tag over those dates.
Usage: apply_fy_rulings.py <tag_map.csv> <fy_periods.csv> <out.csv>"""
import collections
import csv
import datetime
import sys

FY_RULINGS = {
    # IS prints interest expense only by segment (ME&T line; Financial Products line is dimensioned only): no consolidated line
    ("CAT", "interest_expense_resolved"): ("status", "not_presented", "interest_expense_printed_by_segment_only"),
    # D&A sits on the CF face under a custom extension tag; companyfacts carries no extension facts
    ("CRWD", "depreciation_and_amortization_resolved"): ("status", "not_presented", "held_custom_extension_no_fact"),
    # 'Depreciation, amortization and impairment': D&A combined with impairment on one custom line
    ("TSLA", "depreciation_and_amortization_resolved"): ("status", "not_in_template", "line_presented_combined_with_others"),
    # printed per class only on the BS parenthetical; instants are never summed (D3)
    ("MA", "shares_outstanding_resolved"): ("status", "not_presented", "shares_per_class_only"),
    ("META", "shares_outstanding_resolved"): ("status", "not_presented", "shares_per_class_only"),
    # the 10-Ks switched to PaymentsOfDividendsCommonStock from FY2024 (full 10-K read)
    ("COST", "dividends_paid_resolved"): ("tag", "us-gaap", "PaymentsOfDividendsCommonStock"),
}


def day(d, n):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


def apply(rows, fy):
    out, done = [], set()
    for r in rows:
        con = r["canonical_concept"] if r["decision"] == "concept" else r["parent_concept"] if r["decision"] == "component" else ""
        rule = FY_RULINGS.get((r["ticker"], con))
        ps = sorted(fy.get(r["company_id"], []))[-2:]
        if not rule or not ps or r["era_to"] < ps[0] or ps[-1] < r["era_from"]:
            out.append(r)
            continue
        a, b = ps[0], ps[-1]
        if r["era_from"] < a:
            out.append({**r, "era_to": day(a, -1)})
        if r["era_to"] > b:
            out.append({**r, "era_from": day(b, 1)})
        if rule[0] == "tag":  # per serving row: never widened beyond its own era
            out.append({**r, "taxonomy": rule[1], "tag": rule[2], "era_from": max(r["era_from"], a), "era_to": min(r["era_to"], b), "decided_by": "fy_ruling",
                        "reason": f"FY ruling 2026-11-12: the 10-K's printed line is tagged {rule[2]} for these periods"})
        elif (r["company_id"], con) not in done:
            done.add((r["company_id"], con))
            for p in ps:
                e = {k: "" for k in r}
                e.update(company_id=r["company_id"], cik=r["cik"], rank=r["rank"], ticker=r["ticker"], stmt=r["stmt"], decision=rule[1],
                         canonical_concept=con, reason_class=rule[2], era_from=p, era_to=p, decided_by="fy_ruling", rule_id="tagmap.fy_ruling@1",
                         reason=f"FY ruling 2026-11-12 ({rule[2]}): the mapped tag has no fact for this period", lines="0", filings="0")
                out.append(e)
    return out


if __name__ == "__main__":
    tm, fyp, dst = sys.argv[1:4]
    rows = list(csv.DictReader(open(tm)))
    fy = collections.defaultdict(list)
    for r in csv.DictReader(open(fyp)):
        fy[r["company_id"]].append(r["period"])
    out = apply(rows, fy)
    with open(dst, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(out)
    print("rows", len(rows), "->", len(out), "| fy rulings", sum(1 for r in out if r["decided_by"] == "fy_ruling"))
