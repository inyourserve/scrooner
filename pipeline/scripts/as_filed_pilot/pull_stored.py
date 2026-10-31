"""Read-only: pull our stored core.fact rows of each pilot company's periodic filings (one connection)."""
import gzip, json, os, sys, time
import psycopg
out = sys.argv[1]
IDS = {3: "AAPL", 4: "MSFT", 9: "GOOG", 666: "LLY", 1321: "MU", 2328: "AMZN", 2733: "NVDA", 4945: "TSLA", 5050: "META", 5116: "AVGO"}
c = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20, options="-c statement_timeout=120000 -c default_transaction_read_only=on")
Q = """select fi.accession_number, fi.form, k.taxonomy, k.tag, u.unit_name, p.start_date, p.end_date, f.value::text,
       f.is_authoritative, f.is_derived, f.id
from core.fact f join core.filing fi on fi.id=f.filing_id join core.concept k on k.id=f.concept_id
join core.unit u on u.id=f.unit_id join core.period p on p.id=f.period_id
where f.company_id=%s and fi.form in ('10-K','10-Q','10-K/A','10-Q/A','10-KT') and p.end_date >= date '2014-06-01'"""
for cid, t in IDS.items():
    s = time.time()
    with c.cursor() as cur, gzip.open(f"{out}/stored_{t}.jsonl.gz", "wt") as o:
        cur.execute(Q, (cid,))
        n = 0
        for r in cur:
            r = list(r); r[5] = str(r[5]); r[6] = str(r[6]); o.write(json.dumps(r) + "\n"); n += 1
    print(t, n, round(time.time() - s, 1), "s", flush=True)
