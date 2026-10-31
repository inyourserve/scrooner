"""Release package for slot.cash_and_equivalents@1 (flag-gated, registered OFF; NOTHING applied).

Verifier V-cash-v1 (17/17 incl. fills and bank ties). Release 1 = every published cash cell whose
production value DIFFERS (updates) plus the published cells where production is BLANK (fills,
packaged by fills_release_package.py in instant mode). Updates: one production instant per cell
(month-end rounded; two in one month = ambiguous, excluded), before-image with canonical_fact ids,
generated rollback, and a STALE REFUSAL: stale_check.sql returns every target row whose current
value no longer equals its before-image value; the write proceeds only on zero rows.
One read-only connection, statement_timeout 60s.
usage: DATABASE_URL=... cash_release_package.py <cells.jsonl.gz> <out_dir>
"""
import gzip
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg

RULE = "slot.cash_and_equivalents@1"
CONCEPT = "cash_and_equivalents_resolved"
cells_path, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)


def month_end(d):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1)).isoformat()
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).isoformat()


def runit(v, cap=Decimal(1000000)):
    unit = cap
    while unit > 1 and v % unit != 0:
        unit /= 10
    return unit


upd, fills = [], []
for line in gzip.open(cells_path, "rt"):
    c = json.loads(line)
    if c["value"] is None:
        continue
    v = Decimal(c["value"])
    row = {"cik": c["cik"], "ticker": c["ticker"], "end": c["end"], "qtrs": 0, "accession": c["accession"], "form": c["form"],
           "value": str(v), "prod_value": c["prod_value"], "members": c["members"], "cf_ending": c["cf_ending"]}
    if c["prod_value"] is None:
        fills.append(dict(row, state="slot_fills_blank"))
    elif Decimal(c["prod_value"]) != v:
        p = Decimal(c["prod_value"])
        upd.append(dict(row, state="slot_differs", difference_class="rounding_only" if abs(p - v) <= max(runit(p), runit(v)) else "material"))

want = {(r["cik"], r["end"]) for r in upd}
ciks = sorted({r["cik"] for r in upd})
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
cur.execute("set default_transaction_read_only = on")
before = []
for i in range(0, len(ciks), 50):
    cur.execute(
        """
        select cf.id, c.id, c.cik, cf.canonical_concept_id, cf.period_id, p.end_date::text, cf.value::text
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        join core.period p on p.id = cf.period_id
        join core.company c on c.id = cf.company_id
        where c.cik = any(%s) and cc.name = %s and p.end_date >= '2014-12-01'
        """,
        ([f"{x:010d}" for x in ciks[i:i + 50]], CONCEPT),
    )
    for fid, company_id, cik, concept_id, period_id, e, val in cur.fetchall():
        if (int(cik), month_end(e)) in want:
            before.append({"canonical_fact_id": fid, "company_id": company_id, "cik": int(cik), "canonical_concept_id": concept_id,
                           "period_id": period_id, "end": e, "value_before": val})
    conn.rollback()
conn.close()
dup = Counter((b["cik"], month_end(b["end"])) for b in before)
amb = {k for k, n in dup.items() if n > 1}
amb_rows = [r for r in upd if (r["cik"], r["end"]) in amb]
upd = [r for r in upd if (r["cik"], r["end"]) not in amb]
before = [b for b in before if (b["cik"], month_end(b["end"])) not in amb]
assert len(before) == len(upd), (len(before), len(upd))

data = "".join(json.dumps(r, sort_keys=True) + "\n" for r in upd).encode()
(out / "cash_release1_updates.jsonl").write_bytes(data)
digest = hashlib.sha256(data).hexdigest()
(out / "cash_release1_updates.sha256").write_text(f"{digest}  cash_release1_updates.jsonl\n")
fdata = "".join(json.dumps(r, sort_keys=True) + "\n" for r in fills)
(out / "cash_release1_fill_candidates.jsonl").write_text(fdata)
json.dump([dict(r, reason="ambiguous_period_match") for r in amb_rows], open(out / "cash_release1_updates_excluded.json", "w"), indent=1)
with open(out / "cash_release1_updates_before_image.jsonl", "w") as f:
    for b in before:
        f.write(json.dumps(b, sort_keys=True) + "\n")
with open(out / "cash_release1_updates_rollback.sql", "w") as f:
    f.write(f"-- ROLLBACK for {RULE} release 1 updates: restore production {CONCEPT} values. Generated, NOT executed; Release Manager only.\n")
    f.write("begin;\n")
    for b in before:
        f.write(f"update analytics.canonical_fact set value = {b['value_before']} where id = {b['canonical_fact_id']};\n")
    f.write("commit;\n")
with open(out / "cash_release1_updates_stale_check.sql", "w") as f:
    f.write(f"-- STALE REFUSAL for {RULE} release 1 updates: run immediately before the write; proceed only on ZERO rows.\n")
    f.write("-- Any row = a target's production value changed after packaging (or the row is gone); refuse and rebuild.\n")
    f.write("with b(id, value_before) as (values\n")
    f.write(",\n".join(f"  ({b['canonical_fact_id']}, {b['value_before']}::numeric)" for b in before))
    f.write("\n)\nselect b.id, b.value_before, cf.value from b left join analytics.canonical_fact cf on cf.id = b.id\n"
            "where cf.id is null or cf.value <> b.value_before;\n")
(out / "cash_release1_updates_touched_ciks.txt").write_text("".join(f"{c:010d}\n" for c in sorted({r['cik'] for r in upd})))
pkg = {
    "rule_id": RULE, "registered": "OFF",
    "family": f"balance sheet: {CONCEPT}",
    "source_cells": {"file": cells_path, "sha256": hashlib.sha256(open(cells_path, "rb").read()).hexdigest()},
    "verifier": "verify/capex-v18-cash-v1-partial-2026-11-03: cash v1 17/17 (incl. 5 fills, 3 bank ties)",
    "updates": {"cells_file": "cash_release1_updates.jsonl", "sha256": digest, "cells": len(upd), "companies": len({r["cik"] for r in upd}),
                "by_difference_class": dict(Counter(r["difference_class"] for r in upd)),
                "before_image": f"cash_release1_updates_before_image.jsonl ({len(before)} canonical_fact rows)",
                "rollback": "cash_release1_updates_rollback.sql (generated, never executed)",
                "stale_refusal": "cash_release1_updates_stale_check.sql must return zero rows immediately before the write",
                "excluded_ambiguous_period_match": len(amb_rows)},
    "flag": {"line": f"SCROONER_RULES_ENABLED={RULE}", "default": "OFF",
             "note": "the write goes through the existing flag / cell_store contract; this package supplies cells, evidence, before-image"},
}
json.dump(pkg, open(out / "PACKAGE.json", "w"), indent=1)
print(json.dumps(pkg["updates"], indent=1), "fill candidates:", len(fills))
