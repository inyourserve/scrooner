"""Compare CFO / buyback replay cells with production (information only; a
verdict never depends on production). Read-only, one connection, 60s timeout.

A production row matches a cell when its end date is within +-10 days (52/53-
week filers: FSN ddate is the month end, the filer's end is e.g. 2024-03-29)
and its duration is within 20 days of the cell's (qtrs x 91.25 days plus the
FSN duration offset). Verifier run 1 found most exact-date "blanks" had a
production value a few days away.
usage: DATABASE_URL=... cf_prod_compare.py <cohort.csv> <run_dir>
"""
import csv
import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg

cohort_csv, run_dir = sys.argv[1], Path(sys.argv[2])
coh = {r["cik"]: (int(r["company_id"]), r["ticker"]) for r in csv.DictReader(open(cohort_csv))}
conn = psycopg.connect(os.environ["DATABASE_URL"], application_name="cf_prod_compare")
conn.execute("set statement_timeout = '60s'")
conn.execute("set default_transaction_read_only = on")
prod = defaultdict(lambda: defaultdict(list))  # concept -> company_id -> [(end, days, value)]
ids = sorted(v[0] for v in coh.values())
for i in range(0, len(ids), 100):
    for name, cid, s, e, v in conn.execute(
        """select cc.name, cf.company_id, p.start_date, p.end_date, cf.value
           from analytics.canonical_fact cf
           join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
           join core.period p on p.id = cf.period_id
           where cf.company_id = any(%s) and cc.name in ('cfo_resolved', 'share_buybacks_resolved')
             and p.end_date >= '2014-12-01' and p.start_date is not null""",
        (ids[i:i + 100],),
    ):
        prod[name][cid].append((e, (e - s).days, v))
conn.close()


def match(rows, end, days):
    best = None
    for e, d, v in rows:
        if abs((e - end).days) <= 10 and abs(d - days) <= 20:
            if best is None or abs((e - end).days) < best[0]:
                best = (abs((e - end).days), v)
    return None if best is None else best[1]


out = {}
for fam, concept in (("cfo", "cfo_resolved"), ("buybacks", "share_buybacks_resolved")):
    k, holds, differs, new = Counter(), Counter(), [], []
    for line in gzip.open(run_dir / f"{fam}_cells.jsonl.gz", "rt"):
        r = json.loads(line)
        if r["verdict"] == "not_a_face_column":
            continue
        cid, ticker = coh[r["cik"]]
        end = date.fromisoformat(r["end"])
        days = round(r["months"] / 3 * 91.25 + (r.get("durp") or 0) * 91.25)
        pv = match(prod[concept][cid], end, days)
        if r["verdict"] != "publishable":
            holds[r["verdict"]] += 1
            k["held_prod_has_value" if pv is not None else "held_prod_blank"] += 1
            continue
        v = Decimal(r["value"])
        if pv is None:
            k["publishable_prod_blank"] += 1
            new.append([ticker, r["end"], r["months"], r["value"], r["accession"]])
        elif abs(pv - v) <= 1:
            k["publishable_agree"] += 1
        else:
            k["publishable_differ"] += 1
            differs.append([ticker, r["end"], r["months"], r["value"], str(pv), r["accession"]])
    json.dump(differs, open(run_dir / f"{fam}_prod_differs.json", "w"))
    json.dump(new, open(run_dir / f"{fam}_prod_blank.json", "w"))
    out[fam] = {"vs_production": dict(k), "held_by_reason": dict(holds.most_common())}
    print(fam, json.dumps(out[fam]))
json.dump(out, open(run_dir / "prod_compare.json", "w"), indent=1)
