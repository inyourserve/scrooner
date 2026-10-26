"""DRY-RUN: slot-record total liabilities vs production, every cohort cell.
Reads the per-cell replay reports (bs_replay_*.json, which hold the published
slot value or None per instant) and production's `total_liabilities_resolved`
canonical facts; writes a summary and a cells file for the Verifier and the
Release Manager. Writes NOTHING to the database (doc 49 step: dry-run before
any value-changing release). One read-only connection.
usage: DATABASE_URL=... bs_dryrun_compare.py <out_prefix> <report1.json> [report2.json ...]
States per cell: agree | slot_differs (production value differs: wrong-value
candidate) | slot_fills_blank | slot_holds_prod_has_value (we would HIDE a shown
value: needs_instance_reader / not computable / withheld) | both_blank.
"""
import json
import os
import sys
from collections import Counter, defaultdict
from decimal import Decimal

import psycopg

out_prefix = sys.argv[1]
cells = {}
for path in sys.argv[2:]:
    r = json.load(open(path))
    for c in r.get("cells", []):
        cells[(c["cik"], c["end"])] = c  # later reports override earlier ones
    # held cells are not in 'cells' (they were skipped before the identity): count them from per_company
    held_counts = r.get("per_company", {})
ciks = sorted({k[0] for k in cells})
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
summary = Counter()
per_company = defaultdict(Counter)
diffs = []
for cik in ciks:
    cur.execute(
        """
        select p.end_date::text, cf.value::numeric
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        join core.period p on p.id = cf.period_id
        join core.company c on c.id = cf.company_id
        where c.cik = %s and cc.name = 'total_liabilities_resolved' and p.period_type = 'instant' and p.end_date >= '2015-01-01'
        """,
        (cik,),
    )
    prod = {e: v for e, v in cur.fetchall()}
    ends = {k[1] for k in cells if k[0] == cik} | set(prod)
    for end in sorted(ends):
        c = cells.get((cik, end))
        slot = Decimal(c["total_liabilities"]) if c and c.get("total_liabilities") else None
        pv = prod.get(end)
        if slot is not None and pv is not None:
            state = "agree" if abs(slot - pv) <= 1 else "slot_differs"
        elif slot is not None:
            state = "slot_fills_blank"
        elif pv is not None:
            state = "slot_holds_prod_has_value" if c else "no_slot_cell_prod_has_value"
        else:
            state = "both_blank"
        summary[state] += 1
        per_company[cik][state] += 1
        if state in ("slot_differs", "slot_holds_prod_has_value"):
            diffs.append({"cik": cik, "end": end, "state": state, "slot": str(slot) if slot is not None else None,
                          "production": str(pv) if pv is not None else None,
                          "rule": c.get("rule") if c else None, "reading": c.get("reading") if c else None,
                          "accession": c.get("accession") if c else None, "identity": c.get("identity") if c else None})
conn.close()
json.dump({"summary": dict(summary), "companies": len(ciks),
           "companies_with_a_difference": sum(1 for v in per_company.values() if v.get("slot_differs")),
           "per_company": {k: dict(v) for k, v in per_company.items()}}, open(out_prefix + "_summary.json", "w"), indent=1)
with open(out_prefix + "_cells.jsonl", "w") as f:
    for d in diffs:
        f.write(json.dumps(d) + "\n")
print(json.dumps(dict(summary), indent=1))
print("companies", len(ciks), "with a slot_differs cell:", sum(1 for v in per_company.values() if v.get("slot_differs")))
