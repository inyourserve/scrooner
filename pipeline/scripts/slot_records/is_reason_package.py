"""Package a blank-reason release (OI package 2, rule
slot.is_operating_income_not_presented@1) for the flag-gated write; read-only,
one connection, nothing written to the database.

Strata files (is_oi_not_presented.py): reason-only (production blank), would-hide
(production has a derived value the face does not support) and Q4 would-hide.
The before-image re-reads production's CURRENT canonical_fact rows of every
would-hide cell by id; the rollback restores them (writer bypass, migration
0113 aware) and deletes this rule's cell_blank_reason rows.
usage: DATABASE_URL=... is_reason_package.py [family=gross_profit|cost_of_revenue] <package_dir> <verifier_note>
"""
import hashlib
import json
import os
import sys
from pathlib import Path

import psycopg

RULE = "slot.is_operating_income_not_presented@1"
CONCEPT = "operating_income_resolved"
PREFIX = "is_oi_not_presented"
STRATA = ("prod_blank_reason_only", "prod_has_value_would_hide", "q4_prod_has_value_would_hide")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(pkg_dir, verifier_note):
    d = Path(pkg_dir)
    files, hide = {}, []
    for st in STRATA:
        p = d / f"{PREFIX}_{st}.jsonl"
        rows = [json.loads(line) for line in open(p)]
        files[st] = {"file": p.name, "sha256": sha(p), "cells": len(rows), "companies": len({r["cik"] for r in rows})}
        if st != "prod_blank_reason_only":
            hide += rows
    ids = sorted(r["prod_cf_id"] for r in hide)
    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20)
    conn.read_only = True
    cur = conn.cursor()
    cur.execute("set statement_timeout = '60s'")
    before = []
    for i in range(0, len(ids), 500):
        cur.execute(
            """
            select cf.id, cf.company_id, c.cik, cf.canonical_concept_id, cf.period_id, p.start_date::text,
                   p.end_date::text, cf.value::text, cf.source_fact_ids, cf.resolved_at::text
            from analytics.canonical_fact cf
            join core.company c on c.id = cf.company_id
            join core.period p on p.id = cf.period_id
            where cf.id = any(%s)
            """,
            (ids[i:i + 500],),
        )
        for row in cur.fetchall():
            before.append(dict(zip(("canonical_fact_id", "company_id", "cik", "canonical_concept_id", "period_id", "start", "end",
                                    "value_before", "source_fact_ids_before", "resolved_at_before"), row)))
    conn.close()
    bi = d / f"{PREFIX}_before_image.jsonl"
    with open(bi, "w") as f:
        for b in sorted(before, key=lambda b: b["canonical_fact_id"]):
            f.write(json.dumps(b, sort_keys=True) + "\n")
    rb = d / f"{PREFIX}_rollback.sql"
    with open(rb, "w") as f:
        f.write(f"-- ROLLBACK for rule {RULE}: re-insert the hidden {CONCEPT} rows from the before-image and drop this rule's blank reasons.\n")
        f.write("-- Generated, NOT executed. Run inside one transaction by the Release Manager only.\n")
        f.write("begin;\nset local scrooner.slot_writer = 'on';\n")
        for b in sorted(before, key=lambda b: b["canonical_fact_id"]):
            src = "array[" + ",".join(str(x) for x in (b["source_fact_ids_before"] or [])) + "]::bigint[]"
            f.write("insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids, resolved_at) "
                    f"values ({b['company_id']}, {b['canonical_concept_id']}, {b['period_id']}, {b['value_before']}, {src}, '{b['resolved_at_before']}') "
                    f"on conflict (company_id, canonical_concept_id, period_id) do update set value = excluded.value, "
                    f"source_fact_ids = excluded.source_fact_ids, resolved_at = excluded.resolved_at;\n")
        f.write(f"delete from analytics.cell_blank_reason where rule_id = '{RULE}';\n")
        f.write("do $$ begin if to_regclass('analytics.slot_protected_cell') is not null then "
                f"delete from analytics.slot_protected_cell where rule_id = '{RULE}'; end if; end $$;\n")
        f.write("commit;\n")
    pkg = {
        "rule_id": RULE, "kind": "blank_reasons", "family": f"income statement: {CONCEPT}",
        "status": "dry run; flag OFF; nothing written to the database",
        "verifier": {"verdict": "YES", "draw": verifier_note},
        "strata": files,
        "cells": sum(v["cells"] for v in files.values()),
        "companies": len({r["cik"] for st in STRATA for r in map(json.loads, open(d / files[st]["file"]))}),
        "before_image": {"file": bi.name, "rows": len(before), "sha256": sha(bi), "expected_rows": len(ids)},
        "rollback": {"file": rb.name, "sha256": sha(rb), "note": "re-inserts hidden rows (new ids, same key/value/sources); runs with or without migration 0113"},
        "write_contract": "per cell one analytics.cell_blank_reason row (state not_presented, reason line_not_presented_in_filing, "
                          "input_refs with the accession). Would-hide strata also: archive the canonical_fact row to canonical_fact_retired, "
                          "delete it under set local scrooner.slot_writer = 'on', and (once 0113 exists) insert a slot_protected_cell row for "
                          "the key (value column = the hidden production value, for audit) so no nightly resolver re-derives it",
        "stale_cell_refusal": "is_release_check.py <this dir>: refuses if any stratum digest moved, a reason-only cell now has a production row, "
                              "or a would-hide row's value/sources differ from the before-image",
        "flag": {"line": f"SCROONER_RULES_ENABLED={RULE}", "default": "OFF"},
    }
    json.dump(pkg, open(d / "PACKAGE.json", "w"), indent=1)
    print(json.dumps({k: pkg[k] for k in ("rule_id", "cells", "companies", "strata", "before_image")}, indent=1))


if __name__ == "__main__":
    # optional: family=<gross_profit|cost_of_revenue> (default operating income)
    args = sys.argv[1:]
    if args and args[0].startswith("family="):
        fam = args.pop(0).split("=", 1)[1]
        RULE, CONCEPT, PREFIX = f"slot.is_{fam}_not_presented@1", f"{fam}_resolved", f"is_{fam}_not_presented"
    main(args[0], args[1])
