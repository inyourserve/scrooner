"""Stale-cell refusal for an income-statement release package (read-only, one
connection). Run immediately before the flag-gated write; exit 1 refuses the
release. Checks, in order:
  1. the release-1 cells file still has the digest recorded in PACKAGE.json;
  2. every replaced cell's production row (canonical_fact id from the
     before-image) still exists with the before-image's value and sources
     (13 revenue rows were rewritten by a resolver between the 2026-10-31 dry
     run and the package: that is what this catches);
  3. every fill cell still has NO production row for (company, concept, period);
  4. no release cell is already protected by another rule (migration 0113),
     when that table exists.
A refused release is re-cut from a fresh dry run; cells are never dropped here.
usage: DATABASE_URL=... is_release_check.py <package_dir>
"""
import hashlib
import json
import os
import sys
from pathlib import Path

import psycopg


def check_reasons(d, pkg):
    """blank-reason package (OI package 2): digests, reason-only cells still blank,
    would-hide rows unchanged since the before-image."""
    refused = []
    rows = {}
    for st, meta in pkg["strata"].items():
        p = d / meta["file"]
        if hashlib.sha256(p.read_bytes()).hexdigest() != meta["sha256"]:
            print(f"REFUSED: {meta['file']} digest moved")
            return 1
        rows[st] = [json.loads(line) for line in open(p)]
    before = {b["canonical_fact_id"]: b for b in map(json.loads, open(d / pkg["before_image"]["file"]))}
    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20)
    conn.read_only = True
    cur = conn.cursor()
    cur.execute("set statement_timeout = '60s'")
    ids = sorted(before)
    live = {}
    for i in range(0, len(ids), 500):
        cur.execute("select id, value::text, source_fact_ids from analytics.canonical_fact where id = any(%s)", (ids[i:i + 500],))
        live.update({r[0]: (r[1], r[2]) for r in cur.fetchall()})
    for st, rs in rows.items():
        if st == "prod_blank_reason_only":
            continue
        for r in rs:
            b, lv = before.get(r["prod_cf_id"]), live.get(r["prod_cf_id"])
            if b is None or lv is None:
                refused.append((r, "production row gone or not in the before-image"))
            elif lv[0] != b["value_before"] or list(lv[1] or []) != list(b["source_fact_ids_before"] or []):
                refused.append((r, f"production row changed: {lv[0]} vs {b['value_before']}"))
    concept = pkg["family"].split(": ", 1)[1]
    by_cik = {}
    for r in rows.get("prod_blank_reason_only", []):
        by_cik.setdefault(r["cik"], []).append(r)
    for cik, rs in sorted(by_cik.items()):
        cur.execute(
            """
            select p.start_date::text, p.end_date::text, cf.value::text from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.company co on co.id = cf.company_id
            join core.period p on p.id = cf.period_id
            where cc.name = %s and co.cik = %s and p.period_type = 'duration'
            """,
            (concept, cik),
        )
        have = {(s0, e0): v for s0, e0, v in cur.fetchall()}
        for r in rs:
            if (r["period_start"], r["period_end"]) in have:
                refused.append((r, f"reason-only cell now has a production value {have[(r['period_start'], r['period_end'])]}"))
    conn.close()
    n = sum(len(v) for v in rows.values())
    print(f"{pkg['rule_id']}: cells {n} ({', '.join(f'{k} {len(v)}' for k, v in rows.items())})")
    if refused:
        print(f"REFUSED: {len(refused)} stale cells at {len({r['cik'] for r, _ in refused})} companies; re-cut from a fresh dry run")
        for r, why in refused[:20]:
            print(f"  {r['cik']} {r['period_start']}..{r['period_end']}: {why}")
        return 1
    print("OK: no stale cell; release may proceed to the flag-gated write")
    return 0


def main(pkg_dir):
    d = Path(pkg_dir)
    pkg = json.load(open(d / "PACKAGE.json"))
    if pkg.get("kind") == "blank_reasons":
        return check_reasons(d, pkg)
    r1 = pkg["release1"]
    concept = pkg["family"].split(": ", 1)[1]
    refused = []
    digest = hashlib.sha256((d / r1["file"]).read_bytes()).hexdigest()
    if digest != r1["sha256"]:
        print(f"REFUSED: cells digest {digest} != package {r1['sha256']}")
        return 1
    cells = [json.loads(line) for line in open(d / r1["file"])]
    before = {b["canonical_fact_id"]: b for b in map(json.loads, open(d / r1["before_image"]["file"]))}
    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20)
    conn.read_only = True
    cur = conn.cursor()
    cur.execute("set statement_timeout = '60s'")
    ids = sorted(before)
    live = {}
    for i in range(0, len(ids), 500):
        cur.execute("select id, value::text, source_fact_ids from analytics.canonical_fact where id = any(%s)", (ids[i:i + 500],))
        live.update({r[0]: (r[1], r[2]) for r in cur.fetchall()})
    for c in cells:
        if c.get("compare") == "slot_differs":
            b = before.get(c.get("prod_cf_id"))
            lv = live.get(c.get("prod_cf_id"))
            if b is None:
                refused.append((c, "no before-image row"))
            elif lv is None:
                refused.append((c, "production row gone (rewritten since the dry run)"))
            elif lv[0] != b["value_before"] or list(lv[1] or []) != list(b["source_fact_ids_before"] or []):
                refused.append((c, f"production row changed: {lv[0]} vs before-image {b['value_before']}"))
    fills = [c for c in cells if c.get("compare") == "slot_fills_blank"]
    for c in fills:
        cur.execute(
            """
            select cf.value::text from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.company co on co.id = cf.company_id
            join core.period p on p.id = cf.period_id
            where cc.name = %s and co.cik = %s and p.period_type = 'duration'
              and p.start_date = %s and p.end_date = %s
            """,
            (concept, c["cik"], c["start"], c["end"]),
        )
        row = cur.fetchone()
        if row:
            refused.append((c, f"fill cell now has a production value {row[0]}"))
    cur.execute("select to_regclass('analytics.slot_protected_cell') is not null")
    guarded = cur.fetchone()[0]
    if guarded:
        cur.execute(
            """
            select co.cik, p.start_date::text, p.end_date::text, sp.rule_id
            from analytics.slot_protected_cell sp
            join analytics.canonical_concept cc on cc.id = sp.canonical_concept_id
            join core.company co on co.id = sp.company_id
            join core.period p on p.id = sp.period_id
            where cc.name = %s and sp.rule_id <> %s
            """,
            (concept, pkg["rule_id"]),
        )
        other = {(r[0], r[1], r[2]): r[3] for r in cur.fetchall()}
        for c in cells:
            if (c["cik"], c["start"], c["end"]) in other:
                refused.append((c, f"already protected by {other[(c['cik'], c['start'], c['end'])]}"))
    conn.close()
    print(f"{pkg['rule_id']}: cells {len(cells)}, replaced {len(cells) - len(fills)}, fills {len(fills)}, "
          f"guard table {'present' if guarded else 'absent (migration 0113 not applied)'}")
    if refused:
        print(f"REFUSED: {len(refused)} stale cells at {len({c['cik'] for c, _ in refused})} companies; re-cut the package from a fresh dry run")
        for c, why in refused[:20]:
            print(f"  {c['cik']} {c['start']}..{c['end']}: {why}")
        return 1
    print("OK: no stale cell; release may proceed to the flag-gated write")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
