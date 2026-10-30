"""Release package 1 for one income-statement family (dry-run output in, files
out; read-only, one connection). Nothing is written to the database: the
rollback SQL is WRITTEN as a file, never executed here.

Strata (from is_replay.py cells):
  release1      state slot_value, compare slot_differs or slot_fills_blank
                (a printed-line value from the original filing, every later
                face copy agreeing, that production does not show)
  precision     prod_less_precise / differs_within_rounding: production is a
                rounding of the filed number; not a wrong value, own stratum
  hide          hide_restated_copies_disagree with a production value
                (founder ruling: restated periods whose copies disagree are
                hidden); needs its own Verifier stratum
  holds         production stays (every hold_*, prod_only_*), counted only
The before-image re-reads production's CURRENT canonical_fact rows for the
release-1 differences by id (value, source_fact_ids, resolved_at), so the
rollback restores exactly what was there; fills roll back by deleting the
row the write creates for (company, concept, period).
usage: DATABASE_URL=... is_package.py <family> <is_<family>_cells.jsonl> <out_dir>
"""
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path

import psycopg

PROD = {"revenue": "revenue_sanity_resolved", "operating_income": "operating_income_resolved",
        "net_income": "net_income_resolved"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_cells(path, cells):
    with open(path, "w") as f:
        for c in sorted(cells, key=lambda c: (c["cik"], c["start"], c["end"])):
            f.write(json.dumps(c, sort_keys=True) + "\n")
    return sha(path)


def main(family, cells_path, out_dir):
    rule = f"slot.is_{family}@1"
    concept = PROD[family]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cells = [json.loads(line) for line in open(cells_path)]
    r1 = [c for c in cells if c["state"] == "slot_value" and c.get("compare") in ("slot_differs", "slot_fills_blank")]
    prec = [c for c in cells if c["state"] == "slot_value" and c.get("compare") in ("prod_less_precise", "differs_within_rounding")]
    hide = [c for c in cells if c["state"].startswith("hide") and c.get("prod_value") is not None]
    holds = Counter(c["state"].split(":")[0] for c in cells
                    if c.get("prod_value") is not None and not c["state"].startswith(("slot_value", "hide")))
    files = {}
    for name, cs in (("release1", r1), ("precision", prec), ("hide", hide)):
        p = out / f"is_{family}_{name}_cells.jsonl"
        files[name] = {"file": p.name, "sha256": write_cells(p, cs), "cells": len(cs),
                       "companies": len({c["cik"] for c in cs}),
                       "by_compare": dict(Counter(c.get("compare") for c in cs))}
    ids = sorted(c["prod_cf_id"] for c in r1 if c.get("prod_cf_id"))
    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20)
    conn.read_only = True
    cur = conn.cursor()
    cur.execute("set statement_timeout = '60s'")
    before = []
    for i in range(0, len(ids), 500):
        cur.execute(
            """
            select cf.id, cf.company_id, c.cik, cf.canonical_concept_id, cc.name, cf.period_id,
                   p.start_date::text, p.end_date::text, cf.value::text, cf.source_fact_ids, cf.resolved_at::text
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.company c on c.id = cf.company_id
            join core.period p on p.id = cf.period_id
            where cf.id = any(%s)
            """,
            (ids[i:i + 500],),
        )
        for row in cur.fetchall():
            before.append(dict(zip(("canonical_fact_id", "company_id", "cik", "canonical_concept_id", "concept", "period_id",
                                    "start", "end", "value_before", "source_fact_ids_before", "resolved_at_before"), row)))
    conn.close()
    stale = [c for c in r1 if c.get("prod_cf_id") and not any(b["canonical_fact_id"] == c["prod_cf_id"] and b["value_before"] == c["prod_value"]
                                                              for b in before)]
    bi = out / f"is_{family}_r1_before_image.jsonl"
    with open(bi, "w") as f:
        for b in sorted(before, key=lambda b: b["canonical_fact_id"]):
            f.write(json.dumps(b, sort_keys=True) + "\n")
    rb = out / f"is_{family}_r1_rollback.sql"
    with open(rb, "w") as f:
        f.write(f"-- ROLLBACK for rule {rule}: restore production {concept} from the before-image.\n")
        f.write("-- Generated, NOT executed. Run inside one transaction by the Release Manager only.\n")
        f.write("begin;\n")
        for b in sorted(before, key=lambda b: b["canonical_fact_id"]):
            src = "array[" + ",".join(str(x) for x in (b["source_fact_ids_before"] or [])) + "]::bigint[]"
            f.write(f"update analytics.canonical_fact set value = {b['value_before']}, source_fact_ids = {src}, "
                    f"resolved_at = '{b['resolved_at_before']}' where id = {b['canonical_fact_id']};\n")
        for c in sorted((c for c in r1 if c.get("compare") == "slot_fills_blank"), key=lambda c: (c["cik"], c["start"], c["end"])):
            f.write("delete from analytics.canonical_fact cf using analytics.canonical_concept cc, core.company co, core.period p "
                    f"where cf.canonical_concept_id = cc.id and cc.name = '{concept}' and cf.company_id = co.id and co.cik = '{c['cik']}' "
                    f"and cf.period_id = p.id and p.period_type = 'duration' and p.start_date = '{c['start']}' and p.end_date = '{c['end']}';\n")
        f.write("commit;\n")
    touched = sorted({c["cik"] for c in r1})
    (out / f"is_{family}_r1_touched_ciks.txt").write_text("\n".join(touched) + "\n")
    pkg = {
        "rule_id": rule,
        "family": f"income statement: {concept}",
        "status": "dry run; flag OFF; nothing written to the database",
        "release1": {**files["release1"],
                     "before_image": {"file": bi.name, "rows": len(before), "sha256": sha(bi)},
                     "rollback": {"file": rb.name, "sha256": sha(rb),
                                  "note": "generated, run in one transaction by the Release Manager only"},
                     "stale_vs_live": len(stale),
                     "touched_ciks": f"is_{family}_r1_touched_ciks.txt"},
        "precision_stratum": {**files["precision"], "status": "not wrong values; ship only if the Verifier and founder want full precision"},
        "hide_stratum": {**files["hide"], "status": "founder ruling (restated copies disagree -> hidden); needs its own Verifier stratum"},
        "holds_production_stays": dict(holds.most_common()),
        "flag": {"convention": "SCROONER_RULES_ENABLED (comma list) with SCROONER_RULES_DRYRUN; default OFF",
                 "line": f"SCROONER_RULES_ENABLED={rule}",
                 "note": "the write goes through the existing flag / cell_store contract; this package supplies cells, evidence, before-image and rollback"},
        "evidence_per_cell": "accession (original filing), slot_tag, printed label, gate (G1 printed line | G2 NCI identity | G1b ProfitLoss without NCI), copies agreeing; slot records is_<family>_records.jsonl",
        "post_write": "re-derive production Q4 cells (FY - 9M) for touched companies; certify rerun on touched_ciks",
    }
    json.dump(pkg, open(out / f"PACKAGE_{family}.json", "w"), indent=1)
    print(json.dumps({k: pkg[k] for k in ("rule_id", "release1", "precision_stratum", "hide_stratum", "holds_production_stays")}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
