"""Read-only: stored canonical (analytics.canonical_fact) cells for the pilot companies, a few headline concepts."""
import gzip, json, os, sys
import psycopg
out = sys.argv[1]
IDS = {3: "AAPL", 4: "MSFT", 9: "GOOG", 666: "LLY", 1321: "MU", 2328: "AMZN", 2733: "NVDA", 4945: "TSLA", 5050: "META", 5116: "AVGO"}
NAMES = ["revenue", "revenue_resolved", "diluted_eps", "diluted_eps_resolved", "basic_eps", "total_debt", "total_debt_resolved", "total_assets", "net_income", "cfo", "total_liabilities", "operating_income"]
c = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20, options="-c statement_timeout=120000 -c default_transaction_read_only=on")
Q = """select cc.name, p.start_date, p.end_date, p.fiscal_year, p.fiscal_period, cf.value::text, cf.source_fact_ids
from analytics.canonical_fact cf join analytics.canonical_concept cc on cc.id=cf.canonical_concept_id
join core.period p on p.id=cf.period_id where cf.company_id=%s and cc.name = any(%s) and p.end_date >= date '2014-06-01'"""
for cid, t in IDS.items():
    with c.cursor() as cur, gzip.open(f"{out}/canon_{t}.jsonl.gz", "wt") as o:
        cur.execute(Q, (cid, NAMES)); n = 0
        for r in cur:
            r = list(r); r[1] = str(r[1]); r[2] = str(r[2]); o.write(json.dumps(r) + "\n"); n += 1
    print(t, n, flush=True)
