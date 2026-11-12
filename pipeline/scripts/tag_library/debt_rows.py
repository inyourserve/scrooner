"""Debt-lane slot records (Verifier-graded, debt_port_grade_2026-11-02/debt_records.jsonl) -> company_tag_map rows.
No debt rule is retyped here: members, classes, signs and eras come from the lane's records.
Usage: debt_rows.py <debt_records.jsonl> <cohort.csv> <out.csv>"""
import csv
import json
import sys

src, cohort, out = sys.argv[1:4]
co = {r["cik"].zfill(10): r for r in csv.DictReader(open(cohort))}
COLS = ["company_id", "cik", "taxonomy", "tag", "stmt", "decision", "canonical_concept", "parent_concept", "combine_sign",
        "components", "reason_class", "reason", "era_from", "era_to", "evidence_adsh", "evidence_report", "evidence_line",
        "evidence_plabel", "evidence_cal_parent", "decided_by", "rule_id", "rank", "ticker", "lines", "filings"]
rows = []
for ln in open(src):
    r = json.loads(ln)
    c = co.get(r["cik"].zfill(10))
    if not c or r.get("canonical_concept") != "total_debt":
        continue
    base = {"company_id": c["company_id"], "cik": c["cik"], "ticker": c["ticker"], "stmt": "BS", "era_from": r["period_from"],
            "era_to": r["period_to"], "evidence_adsh": r["evidence_accession"], "decided_by": "debt_lane", "rule_id": "debt_lane.slot_record@1"}
    clean = r.get("coverage_clean", False)
    for m in r["members"]:
        x = dict(base, taxonomy="custom" if m.get("custom") else "us-gaap", tag=m["tag"], evidence_cal_parent=m.get("calc_parent", ""))
        if not clean:
            x.update(decision="excluded", reason_class="debt_record_not_clean", reason="debt-lane record has uncovered candidates: held until the lane resolves them")
        elif m["class"] in ("borrowing", "finance_lease"):
            x.update(decision="component", parent_concept="total_debt_resolved", combine_sign="1" if float(m.get("weight", 1)) > 0 else "-1",
                     reason=f"debt-lane member ({m['class']}, {m['side']}); finance leases per doc 02 2026-11-04")
        elif m["class"] == "operating_lease":
            x.update(decision="excluded", reason_class="operating_lease_not_debt", reason="operating lease liability: never debt (doc 02)")
        else:
            x.update(decision="combined", components="total_debt;other", reason_class="line_presented_combined_with_others",
                     reason="debt-lane combined member: a line spanning debt and other liabilities")
        rows.append(x)
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows for", len({r["company_id"] for r in rows}), "companies")
