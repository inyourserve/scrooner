"""Read-only: which rows of one rule an --only-rule seed would load or drop (superseded_by_live), each with EVERY live
row of another rule that decides the same concept in an overlapping era (the seeder names only the first). Same match
as company_tag_map_seed.seed. One connection, statement_timeout 60s, read-only transaction.
Usage: superseded_check.py <tag_map.csv> <rule_id> <out.csv>"""
import csv
import os
import sys
from pathlib import Path
from collections import defaultdict

import psycopg

from scrooner_pipeline.mapper.company_tag_map_seed import TAGLESS, normalize, read_rows

tm, rule, out = sys.argv[1:4]
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    conn.execute("set statement_timeout = '60s'")
    conn.execute("set default_transaction_read_only = on")
    company_by_cik = dict(conn.execute("select cik, id from core.company").fetchall())
    names = dict(conn.execute("select id, name from analytics.canonical_concept").fetchall())
    concept_by_name = {v: k for k, v in names.items()}
    mine = [normalize(r, company_by_cik, concept_by_name) for r in read_rows(Path(tm))
            if r.get("decision") and r.get("rule_id") == rule]
    live = defaultdict(list)
    for t in conn.execute("""select company_id, coalesce(canonical_concept_id, parent_concept_id), decision, tag,
                                    era_from, era_to, rule_id from analytics.company_tag_map
                             where company_id = any(%s) and rule_id <> %s""",
                          (sorted({n["company_id"] for n in mine}), rule)).fetchall():
        live[(t[0], t[1])].append(t)


def clash(a_from, a_to, b_from, b_to):
    return (a_to is None or a_to >= b_from) and (b_to is None or b_to >= a_from)


counts = defaultdict(int)
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["company_id", "concept", "era_from", "era_to", "decision", "outcome", "live_decisions", "live_rules",
                "live_tags"])
    for n in mine:
        hits = [x for x in live[(n["company_id"], n["canonical_concept_id"])]
                if x[2] in ("concept", "component", *TAGLESS) and clash(x[4], x[5], n["era_from"], n["era_to"])]
        outcome = "superseded" if n["decision"] in TAGLESS and hits else "load"
        kinds = sorted({x[2] for x in hits})
        counts[(outcome, n["decision"], "+".join(kinds) or "-")] += 1
        w.writerow([n["company_id"], names.get(n["canonical_concept_id"]), n["era_from"], n["era_to"], n["decision"],
                    outcome, "+".join(kinds), "+".join(sorted({x[6] for x in hits})),
                    "+".join(sorted({x[3] for x in hits if x[3]}))])
for k, v in sorted(counts.items()):
    print(v, *k)
