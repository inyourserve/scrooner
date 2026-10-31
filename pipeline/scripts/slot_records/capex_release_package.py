"""Release package for slot.capex@1 (flag-gated; NOTHING applied here).

Release 1 = the population the Verifier sampled (VERIFY-DA-CAPEX-V10-2026-11-01: capex 15/15
right, drawn from published cells with no perimeter case that differ from production by any
nonzero amount): published capex cells (interim value, no hold reason; so no perimeter case,
no real-estate line, no unresolved line) whose production value differs. Release 2 = published
cells where production is BLANK (fills): not sampled, so they wait for their own Verifier stratum.
Cells the Verifier found production right are kept (keep-list) and never touched.

Before-image: production's capex_resolved canonical_fact rows for every release-1 cell, with
ids; rollback SQL generated from it (never executed here). One read-only connection,
statement_timeout 60s.
usage: DATABASE_URL=... capex_release_package.py <cells.jsonl.gz> <keep_list.json|-> <out_dir>
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

RULE = "slot.capex@1"
cells_path, keep_path, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
keep = set()
if keep_path != "-":
    keep = {(k["cik"], k["end"], k["qtrs"]) for k in json.load(open(keep_path))}


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


r1, r2, kept = [], [], []
for line in gzip.open(cells_path, "rt"):
    c = json.loads(line)
    if c["family"] != "capex" or c["interim"] is None or c["interim_reason"]:
        continue
    key = (c["cik"], c["end"], c["qtrs"])
    v = Decimal(c["interim"])
    row = {"cik": c["cik"], "ticker": c["ticker"], "end": c["end"], "qtrs": c["qtrs"], "accession": c["accession"],
           "form": c["form"], "value": str(v), "prod_value": c["prod_value"],
           "members": [{"tag": x["tag"], "label": x["label"], "nature": x["nature"], "value": x["value"]} for x in c["lines"]]}
    if key in keep:
        kept.append(row)
        continue
    if c["prod_value"] is None:
        r2.append(dict(row, state="slot_fills_blank"))
        continue
    p = Decimal(c["prod_value"])
    if p != v:
        row["state"] = "slot_differs"
        row["difference_class"] = "rounding_only" if abs(p - v) <= max(runit(p), runit(v)) else "material"
        r1.append(row)


def write_cells(name, rows):
    data = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows).encode()
    (out / name).write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    (out / (name.rsplit(".", 1)[0] + ".sha256")).write_text(f"{digest}  {name}\n")
    return digest


d1 = write_cells("capex_release1_cells.jsonl", r1)
d2 = write_cells("capex_release2_fills.jsonl", r2)
json.dump(kept, open(out / "capex_release_keep_list.json", "w"), indent=1)
ciks = sorted({r["cik"] for r in r1})
(out / "release1_touched_ciks.txt").write_text("".join(f"{c:010d}\n" for c in ciks))

# before-image: production rows for every release-1 cell, matched like the dry run
# (rounded month end of the period end, duration in quarters)
want = {(r["cik"], r["end"], r["qtrs"]) for r in r1}
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
        where c.cik = any(%s) and cc.name = 'capex_resolved' and p.end_date >= '2015-01-01'
        """,
        ([f"{x:010d}" for x in ciks[i:i + 50]],),
    )
    for fid, company_id, cik, concept_id, period_id, s, e, v in cur.fetchall():
        q = round((date.fromisoformat(e) - date.fromisoformat(s)).days / 91.3)
        if (int(cik), month_end(e), q) in want:
            before.append({"canonical_fact_id": fid, "company_id": company_id, "cik": int(cik), "canonical_concept_id": concept_id,
                           "period_id": period_id, "start": s, "end": e, "qtrs": q, "value_before": v})
    conn.rollback()
conn.close()
dup = Counter((b["cik"], month_end(b["end"]), b["qtrs"]) for b in before)
# FSN dates are month-end rounded: a cell that matches two production periods (predecessor
# entity or 52/53-week duplicate: ONTO, JCI, KDP, RBC, Z) cannot say which row it replaces.
# Such cells leave release 1 entirely (cells, before-image, CIK list).
ambiguous = {k for k, n in dup.items() if n > 1}
amb_rows = [r for r in r1 if (r["cik"], r["end"], r["qtrs"]) in ambiguous]
r1 = [r for r in r1 if (r["cik"], r["end"], r["qtrs"]) not in ambiguous]
before = [b for b in before if (b["cik"], month_end(b["end"]), b["qtrs"]) not in ambiguous]
want -= ambiguous
matched = {(b["cik"], month_end(b["end"]), b["qtrs"]) for b in before}
d1 = write_cells("capex_release1_cells.jsonl", r1)
json.dump([dict(r, reason="ambiguous_period_match") for r in amb_rows], open(out / "capex_release1_excluded_ambiguous.json", "w"), indent=1)
ciks = sorted({r["cik"] for r in r1})
(out / "release1_touched_ciks.txt").write_text("".join(f"{c:010d}\n" for c in ciks))
with open(out / "capex_release1_before_image.jsonl", "w") as f:
    for b in before:
        f.write(json.dumps(b, sort_keys=True) + "\n")
with open(out / "capex_release1_rollback.sql", "w") as f:
    f.write(f"-- ROLLBACK for rule {RULE} release 1: restore production capex_resolved values from the before-image.\n")
    f.write("-- Generated, NOT executed. Run inside one transaction by the Release Manager only.\n")
    f.write("begin;\n")
    for b in before:
        f.write(f"update analytics.canonical_fact set value = {b['value_before']} where id = {b['canonical_fact_id']};\n")
    f.write("commit;\n")
pkg = {
    "rule_id": RULE,
    "family": "cash flow: capex_resolved (feeds FCF, FCF yield, capex % revenue, FCF per share, buybacks and dividends % FCF)",
    "source_cells": {"file": cells_path, "sha256": hashlib.sha256(open(cells_path, "rb").read()).hexdigest()},
    "verifier": "VERIFY-DA-CAPEX-V10-2026-11-01.md (origin/verify/da-capex-v10-2026-11-01 02c61c6): capex YES, 15 of 15 right; production wrong or only rounded in every drawn cell",
    "release1": {
        "cells_file": "capex_release1_cells.jsonl", "sha256": d1, "cells": len(r1), "companies": len(ciks),
        "by_difference_class": dict(Counter(r["difference_class"] for r in r1)),
        "before_image": f"capex_release1_before_image.jsonl ({len(before)} canonical_fact rows)",
        "cells_without_before_image_row": len(want - matched),
        "excluded_ambiguous_period_match": f"capex_release1_excluded_ambiguous.json ({len(amb_rows)} cells match two production periods; not written)",
        "rollback": "capex_release1_rollback.sql (generated, run in one transaction by the Release Manager only)",
        "keep_list": f"capex_release_keep_list.json ({len(kept)} cells the Verifier found production right; untouched)",
        "touched_ciks": "release1_touched_ciks.txt",
    },
    "release2": {"cells_file": "capex_release2_fills.jsonl", "sha256": d2, "cells": len(r2),
                 "status": "production blank: not in the Verifier's sampled population; needs its own fill stratum before shipping"},
    "not_in_any_release": "held cells (perimeter_line_unresolved, other_capex_lines_outside_ruling, no_continuing_capex_line): production stays as is until the founder's capex answer and a real-estate ruling",
    "flag": {"convention": "SCROONER_RULES_ENABLED (comma list) with SCROONER_RULES_DRYRUN; default OFF",
             "line": f"SCROONER_RULES_ENABLED={RULE}",
             "note": "the write goes through the existing flag / cell_store contract; this package supplies cells, evidence and before-image, not a new write path"},
    "post_write": "certify rerun on release1_touched_ciks.txt; FCF and dependent metrics recompute for the touched companies; any new finding blocks",
    "evidence_per_cell": "accession, face members (tag, label, nature, value) from the FSN pre/num rows of that filing; same accession by construction",
}
json.dump(pkg, open(out / "PACKAGE.json", "w"), indent=1)
print(json.dumps(pkg, indent=1))
