"""Fill package (production-blank cells) for a slot family release (flag-gated; NOTHING applied).

Input: a release's fills file (cells where production has no value). A fill is an INSERT, so each
cell needs the exact production period: it takes the core.period row of the same company whose
end date rounds to the cell's month-end column and whose length is the cell's quarters (FSN dates
are month-end rounded). Cells with no such period, or with two (predecessor / 52-53-week
duplicates), are excluded and listed.
Stale refusal: the write must refuse if any target cell has gained a value since packaging;
stale_check.sql (generated) returns the offending rows and the write proceeds only on zero rows.
Rollback: delete exactly the inserted (company, concept, period) rows (generated, never executed).
One read-only connection, statement_timeout 60s.
usage: DATABASE_URL=... fills_release_package.py <fills.jsonl> <concept> <rule_id> <release_label> <out_dir>
"""
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

import psycopg

fills_path, concept, rule, label, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], Path(sys.argv[5])
out.mkdir(parents=True, exist_ok=True)
cells = [json.loads(x) for x in open(fills_path)]


def month_end(d):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    if dd < 15:
        return (date(y, m, 1) - timedelta(days=1)).isoformat()
    return (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)).isoformat()


ciks = sorted({c["cik"] for c in cells})
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
cur.execute("set default_transaction_read_only = on")
cur.execute("select id from analytics.canonical_concept where name = %s", (concept,))
concept_id = cur.fetchone()[0]
periods = defaultdict(list)  # (cik, month_end, q) -> [(period_id, company_id, start, end)]
existing = set()  # (company_id, period_id) already carrying the concept
for i in range(0, len(ciks), 50):
    cur.execute(
        """
        select c.cik, c.id, p.id, p.start_date::text, p.end_date::text
        from core.period p join core.company c on c.id = p.company_id
        where c.cik = any(%s) and p.period_type = 'duration' and p.end_date >= '2015-01-01'
        """,
        ([f"{x:010d}" for x in ciks[i:i + 50]],),
    )
    for cik, company_id, pid, s, e in cur.fetchall():
        q = round((date.fromisoformat(e) - date.fromisoformat(s)).days / 91.3)
        if q in (1, 2, 3, 4):
            periods[(int(cik), month_end(e), q)].append((pid, company_id, s, e))
    cur.execute(
        """
        select cf.company_id, cf.period_id from analytics.canonical_fact cf join core.company c on c.id = cf.company_id
        where c.cik = any(%s) and cf.canonical_concept_id = %s
        """,
        ([f"{x:010d}" for x in ciks[i:i + 50]], concept_id),
    )
    existing.update(cur.fetchall())
    conn.rollback()
conn.close()

ok, excluded = [], []
for c in cells:
    ps = periods.get((c["cik"], c["end"], c["qtrs"]), [])
    if len(ps) != 1:
        excluded.append(dict(c, reason="no_production_period" if not ps else "ambiguous_period_match"))
        continue
    pid, company_id, s, e = ps[0]
    if (company_id, pid) in existing:
        excluded.append(dict(c, reason="production_no_longer_blank"))
        continue
    ok.append(dict(c, company_id=company_id, period_id=pid, period_start=s, period_end=e, canonical_concept_id=concept_id))

data = "".join(json.dumps(r, sort_keys=True) + "\n" for r in ok).encode()
name = f"{label}_cells.jsonl"
(out / name).write_bytes(data)
digest = hashlib.sha256(data).hexdigest()
(out / f"{label}_cells.sha256").write_text(f"{digest}  {name}\n")
json.dump(excluded, open(out / f"{label}_excluded.json", "w"), indent=1)
keys = ",\n".join(f"  ({r['company_id']}, {r['period_id']})" for r in ok)
with open(out / f"{label}_stale_check.sql", "w") as f:
    f.write(f"-- STALE REFUSAL for {rule} {label}: run immediately before the write. The write proceeds only if this returns ZERO rows.\n")
    f.write("-- Any row = a target cell gained a production value after packaging; refuse the batch and rebuild.\n")
    f.write(f"select cf.id, cf.company_id, cf.period_id, cf.value from analytics.canonical_fact cf\n"
            f"where cf.canonical_concept_id = {concept_id} and (cf.company_id, cf.period_id) in (\n{keys}\n);\n")
with open(out / f"{label}_rollback.sql", "w") as f:
    f.write(f"-- ROLLBACK for {rule} {label}: delete exactly the inserted rows. Generated, NOT executed; Release Manager only.\n")
    f.write("begin;\n")
    f.write(f"delete from analytics.canonical_fact where canonical_concept_id = {concept_id} and (company_id, period_id) in (\n{keys}\n);\n")
    f.write("commit;\n")
(out / f"{label}_touched_ciks.txt").write_text("".join(f"{c:010d}\n" for c in sorted({r['cik'] for r in ok})))
pkg_path = out / "PACKAGE.json"
pkg = json.load(open(pkg_path)) if pkg_path.exists() else {"rule_id": rule}
pkg[label] = {"cells_file": name, "sha256": digest, "cells": len(ok), "companies": len({r["cik"] for r in ok}),
              "kind": "insert into blank production cells (fills)", "source": fills_path,
              "excluded": f"{label}_excluded.json: " + json.dumps(dict(Counter(x["reason"] for x in excluded))),
              "stale_refusal": f"{label}_stale_check.sql must return zero rows immediately before the write",
              "rollback": f"{label}_rollback.sql (delete the inserted rows; generated, never executed)",
              "touched_ciks": f"{label}_touched_ciks.txt",
              "flag": f"SCROONER_RULES_ENABLED={rule}; default OFF"}
json.dump(pkg, open(pkg_path, "w"), indent=1)
print(json.dumps(pkg[label], indent=1))
