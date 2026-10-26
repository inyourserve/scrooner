"""Before-image for the flag-gated total-liabilities release (doc 49 step):
export production's current `total_liabilities_resolved` canonical facts for
every cell the dry-run would change or hide, with the canonical_fact ids, so
the Release Manager can roll back by restoring exactly these rows. Read-only;
the rollback SQL is WRITTEN as a file, never executed here.
usage: DATABASE_URL=... bs_before_image.py <dryrun_cells.jsonl> <keep_list.json|-> <out_prefix>
  keep_list: cells (cik, end) the Verifier confirmed production RIGHT (kept, not touched)
"""
import json
import os
import sys
from collections import Counter

import psycopg

cells_path, keep_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
keep = set()
if keep_path != "-":
    keep = {(k["cik"], k["end"]) for k in json.load(open(keep_path))}
touch = []
for line in open(cells_path):
    c = json.loads(line)
    if c["state"] in ("slot_differs", "slot_fills_blank", "slot_holds_prod_has_value") and (c["cik"], c["end"]) not in keep:
        touch.append(c)
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
by_cik = Counter(c["cik"] for c in touch)
before = []
for cik in sorted(by_cik):
    ends = [c["end"] for c in touch if c["cik"] == cik]
    cur.execute(
        """
        select cf.id, c.id, cf.canonical_concept_id, cf.period_id, p.end_date::text, cf.value::text
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        join core.period p on p.id = cf.period_id
        join core.company c on c.id = cf.company_id
        where c.cik = %s and cc.name = 'total_liabilities_resolved' and p.period_type = 'instant' and p.end_date::text = any(%s)
        """,
        (cik, ends),
    )
    for fid, company_id, concept_id, period_id, end, value in cur.fetchall():
        before.append({"canonical_fact_id": fid, "company_id": company_id, "cik": cik, "canonical_concept_id": concept_id,
                       "period_id": period_id, "end": end, "value_before": value})
conn.close()
with open(out + "_before_image.jsonl", "w") as f:
    for b in before:
        f.write(json.dumps(b, sort_keys=True) + "\n")
with open(out + "_rollback.sql", "w") as f:
    f.write("-- ROLLBACK for rule slot.bs_total_liabilities@1: restore production total_liabilities_resolved values from the before-image.\n")
    f.write("-- Generated, NOT executed. Run inside one transaction by the Release Manager only.\n")
    f.write("begin;\n")
    for b in before:
        f.write(f"update analytics.canonical_fact set value = {b['value_before']} where id = {b['canonical_fact_id']};\n")
    f.write("commit;\n")
plan = {
    "rule_id": "slot.bs_total_liabilities@1",
    "touched_cells": len(touch), "touched_companies": len(by_cik),
    "by_state": dict(Counter(c["state"] for c in touch)),
    "kept_verified_right": len(keep),
    "before_image_rows": len(before),
    "cells_without_production_row": sum(1 for c in touch if c["state"] == "slot_fills_blank"),
}
json.dump(plan, open(out + "_plan.json", "w"), indent=1)
print(json.dumps(plan, indent=1))
