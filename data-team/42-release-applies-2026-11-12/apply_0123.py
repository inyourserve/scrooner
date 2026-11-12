"""Apply migration 0123 (company_value_owner accepts the tag-map writer; company_tag_map.scale) exactly as on
origin/main, in ONE transaction, then post-check. RUN ONLY AFTER THE FOUNDER'S TYPED GO-AHEAD.

Usage: apply_0123.py pipeline/db/migrations/0123_company_value_owner_tag_map_writer.sql 9c9ef8e51922b65a
Rollback: alter table analytics.company_tag_map drop column scale;
          restore the 0119 guard function and the check (owner = 'fsn_cells') from 0119_*.sql
          (only while analytics.company_value_owner holds no 'company_tag_map' rows).
"""

import hashlib
import os
import sys
import time

import psycopg

sql_path, want = sys.argv[1:3]
sql = open(sql_path).read()
sha = hashlib.sha256(sql.encode()).hexdigest()
if not sha.startswith(want):
    sys.exit(f"ABORT sha {sha[:16]} != expected {want}")

with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    has_scale = conn.execute(
        "select 1 from information_schema.columns where table_schema = 'analytics' "
        "and table_name = 'company_tag_map' and column_name = 'scale'"
    ).fetchone()
    if has_scale:
        sys.exit("ABORT: company_tag_map.scale already present")
    conn.commit()
    with conn.transaction():
        conn.execute("set local lock_timeout = '5s'")
        conn.execute("set local statement_timeout = '5min'")
        conn.execute(sql)
        check = conn.execute(
            "select pg_get_constraintdef(oid) from pg_constraint "
            "where conname = 'company_value_owner_owner_check'"
        ).fetchone()
        func = conn.execute(
            "select prosrc from pg_proc where proname = 'company_value_owner_guard'"
        ).fetchone()
        scale = conn.execute(
            "select column_default from information_schema.columns where table_schema = 'analytics' "
            "and table_name = 'company_tag_map' and column_name = 'scale'"
        ).fetchone()
        ok = (
            check is not None
            and "company_tag_map" in check[0]
            and func is not None
            and "company_tag_map" in func[0]
            and scale is not None
        )
        print(f"owner check: {check}; guard accepts company_tag_map: {bool(func and 'company_tag_map' in func[0])}; scale default: {scale}")
        if not ok:
            raise SystemExit("POST-CHECK (0123) FAIL: rolled back")
    print(f"APPLIED 0123_company_value_owner_tag_map_writer sha {sha[:16]} at {time.strftime('%H:%M:%S', time.gmtime())} UTC")
    print("POST-CHECK (0123) PASS")
