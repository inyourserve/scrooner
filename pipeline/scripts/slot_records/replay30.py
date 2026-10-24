"""Replay the 30-company-set slot records against lane 3's before-images.

For every lane 3 total_debt row (cik, period_end, before/after/hold) in the
2015+ data window, compute the slot values from stored facts:
  lease_inclusive = borrowing + combined + finance_lease members
  borrowings_only = lease_inclusive - finance-lease content (explicit members,
                    plus the same-side lease fact inside 'combined' members)
Operating-lease members are excluded from both variants (standardization card).
Values prefer authoritative facts; a non-authoritative fallback is flagged.

Read-only: one DB connection, SELECTs only.
usage: DATABASE_URL=... replay30.py <records.jsonl> <lane3_dir> <out_report.json>
"""
import json
import os
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import psycopg

LEASE_TAGS = {
    "cur": ["FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent"],
    "noncur": ["FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligationsNoncurrent"],
}

records = defaultdict(list)
for line in open(sys.argv[1]):
    r = json.loads(line)
    records[r["cik"]].append(r)

lane3 = []
for fn in Path(sys.argv[2]).glob("debt_v4_MORE*"):
    for line in open(fn):
        r = json.loads(line)
        lane3.append(r)
# one row per (cik, period, variant-file) -> dedupe to (cik, period): keep both variants' before
by_cell = {}
for r in lane3:
    key = (r["cik"], r["period_end"])
    by_cell.setdefault(key, []).append(r)
# Verifier value anchors are evaluated even when lane 3 has no row there.
anchors_path = Path(sys.argv[1]).parent / "results" / "expected_values.json"
if not anchors_path.exists():
    anchors_path = Path(sys.argv[1]).parent / "expected_values.json"
if anchors_path.exists():
    tick2cik = {}
    for recs in records.values():
        for r in recs:
            tick2cik[r["company"]] = r["cik"]
    for a in json.loads(anchors_path.read_text())["anchors"]:
        cik = tick2cik.get(a["ticker"])
        if cik:
            by_cell.setdefault((cik, a["period_end"]), [])

def covering_record(cik, period_end):
    ym = period_end[:7]
    for rec in records.get(cik, []):
        if rec["period_from"][:7] <= ym <= rec["period_to"][:7]:
            return rec
    return None

def fetch_facts(cur, cik, tags):
    # Verifier D2: restrict facts to PERIODIC filings - the non-authoritative
    # fallback once took an 8-K recast copy (GE 2021-12-31: 35,114M from an
    # 8-K vs the 10-K face 35,185M).
    cur.execute(
        """
        select distinct on (co.tag, p.end_date) co.tag, p.end_date::text, f.value::numeric, f.is_authoritative
        from core.fact f
        join core.concept co on co.id = f.concept_id
        join core.period p on p.id = f.period_id
        join core.unit u on u.id = f.unit_id
        join core.company c on c.id = f.company_id
        join core.filing fi on fi.id = f.filing_id
        where c.cik = %s and p.period_type = 'instant' and co.taxonomy = 'us-gaap'
          and u.unit_name = 'usd' and co.tag = any(%s)
          and fi.form in ('10-K','10-Q','10-K/A','10-Q/A')
        order by co.tag, p.end_date, f.is_authoritative desc, f.id desc
        """,
        (cik, list(tags)),
    )
    facts = defaultdict(dict)
    for tag, end_date, value, is_auth in cur.fetchall():
        facts[end_date][tag] = (value, is_auth)
    return facts

report = {"cells": [], "summary": defaultdict(int), "per_company": defaultdict(lambda: defaultdict(int))}
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
for cik in sorted(records):
    tags = set()
    for rec in records[cik]:
        tags.update(m["tag"] for m in rec["members"])
    tags.update(t for side in LEASE_TAGS.values() for t in side)
    facts = fetch_facts(cur, cik, tags)
    cells = [(k, v) for k, v in by_cell.items() if k[0] == cik]
    for (cik_, period_end), rows in sorted(cells):
        ticker = records[cik][0]["company"]
        if period_end < "2015-01-01":
            verdict = "out_of_window_pre2015"
            report["summary"][verdict] += 1
            report["per_company"][ticker][verdict] += 1
            continue
        rec = covering_record(cik, period_end)
        if rec is None:
            verdict = "no_covering_record"
            report["summary"][verdict] += 1
            report["per_company"][ticker][verdict] += 1
            continue
        day = facts.get(period_end, {})
        lease_incl = Decimal(0)
        missing, nonauth = [], []
        combined_sides = set()
        for m in rec["members"]:
            if m["class"] == "operating_lease":
                continue
            if m["class"] == "combined":
                combined_sides.add("cur" if m["side"] == "current" else "noncur")
            if m["tag"] in day:
                v, auth = day[m["tag"]]
                lease_incl += v
                if not auth:
                    nonauth.append(m["tag"])
            else:
                missing.append(m["tag"])
        lease_content = Decimal(0)
        for m in rec["members"]:
            if m["class"] == "finance_lease" and m["tag"] in day:
                lease_content += day[m["tag"]][0]
        for side in combined_sides:
            for lt in LEASE_TAGS[side]:
                if lt in day:
                    lease_content += day[lt][0]
                    break
        borrowings = lease_incl - lease_content
        before_vals = {Decimal(r["before"]) for r in rows if r.get("before")}
        is_hold = any("hold" in (r.get("reason") or "") and not r.get("after") for r in rows)
        # Verifier: a missing member is a HARD STOP, never a silent zero
        # (it hid KO's custom 2014-18 line). Borrowings-only verdicts dropped:
        # the variant does not remove current finance leases inside non-combined
        # short-term lines (CVX 2022, LRCX) - it stays informational only.
        if not rec.get("coverage_clean", True):
            verdict = "not_computable_uncovered_candidates"
        elif missing:
            verdict = "not_computable_missing_member"
        elif not day:
            verdict = "not_computable_no_facts"
        elif before_vals and any(abs(lease_incl - b) <= 1 for b in before_vals):
            verdict = "agrees_lease_inclusive"
        elif before_vals:
            verdict = "DISAGREES_with_lane3"
        else:
            verdict = "lane3_blank_slot_has_value"
        if is_hold and verdict in ("agrees_lease_inclusive", "DISAGREES_with_lane3", "lane3_blank_slot_has_value"):
            report["summary"]["holds_resolved_by_slot"] += 1
            report["per_company"][ticker]["holds_resolved_by_slot"] += 1
        report["summary"][verdict] += 1
        report["per_company"][ticker][verdict] += 1
        report["cells"].append(
            {"ticker": ticker, "cik": cik, "period_end": period_end, "verdict": verdict,
             "slot_lease_inclusive": str(lease_incl), "slot_borrowings": str(borrowings),
             "lane3_before": sorted(str(b) for b in before_vals), "hold": is_hold,
             "missing_members": missing, "nonauth_members": nonauth}
        )
conn.close()
report["summary"] = dict(report["summary"])
report["per_company"] = {k: dict(v) for k, v in report["per_company"].items()}
json.dump(report, open(sys.argv[3], "w"), indent=1)
print(json.dumps(report["summary"], indent=1))
for t in sorted(report["per_company"]):
    print(t, dict(report["per_company"][t]))
