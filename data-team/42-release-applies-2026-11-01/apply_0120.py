"""Apply migration 0120 exactly as on origin/main (founder's typed go-ahead in scrooner-87, 2026-11-01), then post-check."""
import hashlib, os, sys, time
import psycopg
path, want = sys.argv[1], sys.argv[2]
sql = open(path).read()
sha = hashlib.sha256(sql.encode()).hexdigest()
if not sha.startswith(want):
    sys.exit(f"ABORT sha {sha[:16]} != expected {want}")
with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    for attempt in range(1, 13):
        try:
            with conn.transaction():
                conn.execute("set local lock_timeout='5s'")
                conn.execute("set local statement_timeout='5min'")
                conn.execute(sql)
            print(f"APPLIED 0120_company_data_point_template sha {sha[:16]} attempt {attempt} at {time.strftime('%H:%M:%S', time.gmtime())} UTC")
            break
        except psycopg.errors.LockNotAvailable:
            print(f"attempt {attempt}: lock busy, retry in 20s"); time.sleep(20)
    else:
        sys.exit("NOT APPLIED: lock never free")
    cols = conn.execute("select count(*) from information_schema.columns where table_schema='analytics' and table_name='company_data_point_template'").fetchone()[0]
    rows = conn.execute("select count(*) from analytics.company_data_point_template").fetchone()[0]
    pk = conn.execute("select count(*) from pg_constraint where conrelid='analytics.company_data_point_template'::regclass and contype in ('p','c','f')").fetchone()[0]
    idx = conn.execute("select indisvalid from pg_index where indexrelid='analytics.idx_company_data_point_template_effective'::regclass").fetchone()
    print(f"columns {cols} (expect 9), rows {rows} (expect 0), pk/check/fk constraints {pk}, index valid {idx}")
    ok = cols == 9 and rows == 0 and pk >= 3 and idx and idx[0]
    print("POST-CHECK", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
