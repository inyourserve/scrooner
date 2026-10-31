"""Release package for slot.d_and_a@1 (flag-gated; NOTHING applied here).

Release 1 = only the classes that passed every Verifier round (Dhairya 2026-11-02): cells whose
value is the income statement's printed D&A (da_class is_anchor) and single-line cash-flow D&A
(single_line_ties_is, single_line_clean), where production DIFFERS. Production-blank cells of the
same classes are written separately (fills, counted, not in release 1). Every other published
cell that differs (multi-member compositions) is release 2, waiting on its own Verifier rounds.
Same contract as capex_release_package.py: one production row per cell (ambiguous periods
excluded), before-image with canonical_fact ids, generated rollback (never executed), CIK list.
One read-only connection, statement_timeout 60s.
usage: DATABASE_URL=... da_release_package.py <cells.jsonl.gz> <out_dir>
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

RULE = "slot.d_and_a@1"
CONCEPT = "depreciation_and_amortization_resolved"
R1_CLASSES = {"is_anchor", "single_line_ties_is", "single_line_clean"}
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


r1, fills, r2 = [], [], []
for line in gzip.open(cells_path, "rt"):
    c = json.loads(line)
    if c["family"] != "d_and_a" or c["value"] is None:
        continue
    v = Decimal(c["value"])
    row = {"cik": c["cik"], "ticker": c["ticker"], "end": c["end"], "qtrs": c["qtrs"], "accession": c["accession"], "form": c["form"],
           "value": str(v), "prod_value": c["prod_value"], "da_class": c["da_class"], "is_da_total": c.get("is_da_total"),
           "members": [{"tag": x["tag"], "label": x["label"], "nature": x["nature"], "value": x["value"]} for x in c["lines"]]}
    if c["prod_value"] is None:
        (fills if c["da_class"] in R1_CLASSES else r2).append(dict(row, state="slot_fills_blank"))
        continue
    p = Decimal(c["prod_value"])
    if p == v:
        continue
    row["state"] = "slot_differs"
    row["difference_class"] = "rounding_only" if abs(p - v) <= max(runit(p), runit(v)) else "material"
    (r1 if c["da_class"] in R1_CLASSES else r2).append(row)

want = {(r["cik"], r["end"], r["qtrs"]) for r in r1}
ciks = sorted({r["cik"] for r in r1})
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
cur.execute("set default_transaction_read_only = on")
before = []
for i in range(0, len(ciks), 50):
    cur.execute(
        """
        select cf.id, c.id, c.cik, cf.canonical_concept_id, cf.period_id, p.start_date::text, p.end_date::text, cf.value::text
        from analytics.canonical_fact cf
        join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
        join core.period p on p.id = cf.period_id
        join core.company c on c.id = cf.company_id
        where c.cik = any(%s) and cc.name = %s and p.end_date >= '2015-01-01'
        """,
        ([f"{x:010d}" for x in ciks[i:i + 50]], CONCEPT),
    )
    for fid, company_id, cik, concept_id, period_id, s, e, val in cur.fetchall():
        q = round((date.fromisoformat(e) - date.fromisoformat(s)).days / 91.3)
        if (int(cik), month_end(e), q) in want:
            before.append({"canonical_fact_id": fid, "company_id": company_id, "cik": int(cik), "canonical_concept_id": concept_id,
                           "period_id": period_id, "start": s, "end": e, "qtrs": q, "value_before": val})
    conn.rollback()
conn.close()
dup = Counter((b["cik"], month_end(b["end"]), b["qtrs"]) for b in before)
ambiguous = {k for k, n in dup.items() if n > 1}
amb_rows = [r for r in r1 if (r["cik"], r["end"], r["qtrs"]) in ambiguous]
r1 = [r for r in r1 if (r["cik"], r["end"], r["qtrs"]) not in ambiguous]
before = [b for b in before if (b["cik"], month_end(b["end"]), b["qtrs"]) not in ambiguous]
matched = {(b["cik"], month_end(b["end"]), b["qtrs"]) for b in before}
missing = [r for r in r1 if (r["cik"], r["end"], r["qtrs"]) not in matched]
assert not missing, f"{len(missing)} release cells without a production row"
assert len(before) == len(r1), (len(before), len(r1))


def write_rows(name, rows):
    data = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
    (out / name).write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    (out / (name.rsplit(".", 1)[0] + ".sha256")).write_text(f"{digest}  {name}\n")
    return digest


d1 = write_rows("da_release1_cells.jsonl", r1)
df = write_rows("da_release1_class_fills.jsonl", fills)
d2 = write_rows("da_release2_cells.jsonl", r2)
json.dump([dict(r, reason="ambiguous_period_match") for r in amb_rows], open(out / "da_release1_excluded_ambiguous.json", "w"), indent=1)
ciks = sorted({r["cik"] for r in r1})
(out / "release1_touched_ciks.txt").write_text("".join(f"{c:010d}\n" for c in ciks))
with open(out / "da_release1_before_image.jsonl", "w") as f:
    for b in before:
        f.write(json.dumps(b, sort_keys=True) + "\n")
with open(out / "da_release1_rollback.sql", "w") as f:
    f.write(f"-- ROLLBACK for rule {RULE} release 1: restore production {CONCEPT} values from the before-image.\n")
    f.write("-- Generated, NOT executed. Run inside one transaction by the Release Manager only.\n")
    f.write("begin;\n")
    for b in before:
        f.write(f"update analytics.canonical_fact set value = {b['value_before']} where id = {b['canonical_fact_id']};\n")
    f.write("commit;\n")
pkg = {
    "rule_id": RULE,
    "family": f"cash flow: {CONCEPT} (feeds EBITDA, EBITDA margin, net debt/EBITDA, EV/EBITDA, debt/EBITDA)",
    "source_cells": {"file": cells_path, "sha256": hashlib.sha256(open(cells_path, "rb").read()).hexdigest()},
    "selection": "release 1 = da_class in {is_anchor, single_line_ties_is, single_line_clean} AND production differs; "
                 "the classes that passed every Verifier round (IS anchors 5/5 in V14; single-line differences)",
    "release1": {"cells_file": "da_release1_cells.jsonl", "sha256": d1, "cells": len(r1), "companies": len(ciks),
                 "by_class": dict(Counter(r["da_class"] for r in r1)),
                 "by_difference_class": dict(Counter(r["difference_class"] for r in r1)),
                 "before_image": f"da_release1_before_image.jsonl ({len(before)} canonical_fact rows)",
                 "excluded_ambiguous_period_match": len(amb_rows),
                 "rollback": "da_release1_rollback.sql (generated, run in one transaction by the Release Manager only)",
                 "touched_ciks": "release1_touched_ciks.txt"},
    "release1_class_fills": {"cells_file": "da_release1_class_fills.jsonl", "sha256": df, "cells": len(fills),
                             "by_class": dict(Counter(r["da_class"] for r in fills)),
                             "status": "production blank, same classes; needs a fill stratum before shipping"},
    "release2": {"cells_file": "da_release2_cells.jsonl", "sha256": d2, "cells": len(r2),
                 "by_class": dict(Counter(r["da_class"] for r in r2)),
                 "status": "multi-member compositions (and their fills): held for their own Verifier rounds"},
    "flag": {"convention": "SCROONER_RULES_ENABLED (comma list) with SCROONER_RULES_DRYRUN; default OFF",
             "line": f"SCROONER_RULES_ENABLED={RULE}",
             "note": "the write goes through the existing flag / cell_store contract; this package supplies cells, evidence and before-image"},
    "post_write": "certify rerun on release1_touched_ciks.txt; EBITDA-family metrics recompute for the touched companies; any new finding blocks",
}
json.dump(pkg, open(out / "PACKAGE.json", "w"), indent=1)
print(json.dumps({k: pkg[k] for k in ("release1", "release1_class_fills", "release2")}, indent=1))
