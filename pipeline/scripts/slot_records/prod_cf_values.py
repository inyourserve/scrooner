"""Production's shown D&A, capex and CFO values for the cohort, as INFORMATION
for the dry-run counts (a verdict never depends on production's value).
One read-only connection, statement_timeout 60s, chunks of 50 companies.
usage: DATABASE_URL=... prod_cf_values.py <cohort.csv> <out.jsonl.gz>
"""
import csv
import gzip
import json
import os
import sys

import psycopg

CONCEPTS = ["capex_resolved", "depreciation_and_amortization_resolved", "cfo_resolved", "fcf_resolved"]
ids = [int(r["company_id"]) for r in csv.DictReader(open(sys.argv[1]))]
conn = psycopg.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
cur.execute("set statement_timeout = '60s'")
cur.execute("set default_transaction_read_only = on")
cur.execute("select name from analytics.canonical_concept where name = any(%s)", (CONCEPTS,))
found = [r[0] for r in cur.fetchall()]
print("concepts present:", found)
n = 0
with gzip.open(sys.argv[2], "wt") as fo:
    for i in range(0, len(ids), 50):
        cur.execute(
            """
            select c.cik, cc.name, p.start_date::text, p.end_date::text, cf.value::text
            from analytics.canonical_fact cf
            join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
            join core.period p on p.id = cf.period_id
            join core.company c on c.id = cf.company_id
            where cf.company_id = any(%s) and cc.name = any(%s) and p.end_date >= '2015-01-01'
            """,
            (ids[i:i + 50], found),
        )
        for cik, name, s, e, v in cur.fetchall():
            fo.write(json.dumps([int(cik), name, s, e, v]) + "\n")
            n += 1
        conn.rollback()
conn.close()
print("rows", n)
