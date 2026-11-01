"""Apply migration 0117 exactly as on origin/main, then post-check. RUN ONLY AFTER THE FOUNDER'S TYPED GO-AHEAD.

Usage: apply_0117.py <path to 0117 sql extracted from origin/main> <expected sha256 prefix>
One connection. lock_timeout 5s per attempt so the ALTER never queues ahead of live writers; up to 12 attempts.
"""
import hashlib
import os
import sys
import time

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
                conn.execute("set local statement_timeout='15min'")
                conn.execute(sql)
            print(f"APPLIED 0117_canonical_fact_provenance sha {sha[:16]} attempt {attempt} at {time.strftime('%H:%M:%S', time.gmtime())} UTC")
            break
        except psycopg.errors.LockNotAvailable:
            print(f"attempt {attempt}: lock busy, retry in 20s")
            time.sleep(20)
    else:
        sys.exit("NOT APPLIED: canonical_fact lock never free in 12 attempts")

    # Post-check
    cols = conn.execute("""select column_name, data_type, is_nullable from information_schema.columns
        where table_schema='analytics' and table_name='canonical_fact' and column_name in ('rule_run_id','family')
        order by 1""").fetchall()
    fk = conn.execute("""select conname from pg_constraint where conrelid='analytics.canonical_fact'::regclass
        and contype='f' and confrelid='analytics.rule_run'::regclass""").fetchall()
    idx = conn.execute("""select indexname, indexdef from pg_indexes
        where indexname='idx_canonical_fact_family_company'""").fetchall()
    valid = conn.execute("""select indisvalid from pg_index
        where indexrelid='analytics.idx_canonical_fact_family_company'::regclass""").fetchone()
    trg = conn.execute("""select tgname, tgenabled from pg_trigger
        where tgrelid='analytics.canonical_fact'::regclass and not tgisinternal""").fetchall()
    nn = conn.execute("""select count(*) from analytics.canonical_fact
        where rule_run_id is not null or family is not null""").fetchone()
    print(f"columns: {cols}")
    print(f"fk to rule_run: {fk}")
    print(f"index: {idx} valid={valid}")
    print(f"guard trigger: {trg}")
    print(f"non-null provenance rows (expect 0): {nn[0]}")
    ok = len(cols) == 2 and all(c[2] == "YES" for c in cols) and fk and idx and valid and valid[0] and nn[0] == 0 \
        and ("trg_slot_protected_cell_guard", "O") in trg
    print("POST-CHECK", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
