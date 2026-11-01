"""Apply migrations 0118 and 0119 exactly as on origin/main, then post-check. RUN ONLY AFTER THE FOUNDER'S TYPED GO-AHEAD
(given 2026-11-01 in scrooner-87, the engineering session).

Usage: apply_0118_0119.py <0118 sql> <sha256 prefix> <0119 sql> <sha256 prefix>
One connection. Each migration is one transaction; lock_timeout 5s per attempt so an ALTER never queues ahead of live
writers; up to 12 attempts each. 0118 adds canonical_fact.source_value_ids with a constant default (no table rewrite).
"""

import hashlib
import os
import sys
import time

import psycopg

args = sys.argv[1:]
migrations = [(args[i], args[i + 1]) for i in range(0, len(args), 2)]

with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    conn.execute("set statement_timeout = '10min'")
    rows_before = conn.execute("select count(*) from analytics.canonical_fact").fetchone()[0]
    conn.commit()
    for path, want in migrations:
        sql = open(path).read()
        sha = hashlib.sha256(sql.encode()).hexdigest()
        if not sha.startswith(want):
            sys.exit(f"ABORT {path}: sha {sha[:16]} != expected {want}")
        for attempt in range(1, 13):
            try:
                with conn.transaction():
                    conn.execute("set local lock_timeout='5s'")
                    conn.execute("set local statement_timeout='15min'")
                    conn.execute(sql)
                print(f"APPLIED {os.path.basename(path)} sha {sha[:16]} attempt {attempt} at {time.strftime('%H:%M:%S', time.gmtime())} UTC")
                break
            except psycopg.errors.LockNotAvailable:
                print(f"{os.path.basename(path)} attempt {attempt}: lock busy, retry in 20s")
                time.sleep(20)
        else:
            sys.exit(f"NOT APPLIED {path}: lock never free in 12 attempts")

    # Post-check
    tables = conn.execute(
        "select table_name from information_schema.tables where table_schema = 'fsn' order by 1"
    ).fetchall()
    dim0 = conn.execute("select id, dimh from fsn.dim where id = 0").fetchall()
    col = conn.execute(
        """select data_type, is_nullable, column_default from information_schema.columns
        where table_schema = 'analytics' and table_name = 'canonical_fact' and column_name = 'source_value_ids'"""
    ).fetchall()
    trg = conn.execute(
        "select tgname, tgenabled from pg_trigger where tgrelid = 'analytics.canonical_fact'::regclass and not tgisinternal order by 1"
    ).fetchall()
    owners = conn.execute("select count(*) from analytics.company_value_owner").fetchone()[0]
    rows_after = conn.execute("select count(*) from analytics.canonical_fact").fetchone()[0]
    nonempty = conn.execute(
        "select count(*) from analytics.canonical_fact where source_value_ids <> '{}'"
    ).fetchone()[0]
    print(f"fsn tables ({len(tables)}): {[t[0] for t in tables]}")
    print(f"fsn.dim id 0: {dim0}")
    print(f"canonical_fact.source_value_ids: {col}")
    print(f"triggers: {trg}")
    print(f"company_value_owner rows (expect 0, guard inert): {owners}")
    print(f"canonical_fact rows before/after: {rows_before}/{rows_after}; non-empty source_value_ids (expect 0): {nonempty}")
    ok = (
        len(tables) == 11
        and dim0 == [(0, "0x00000000")]
        and col
        and col[0][1] == "NO"
        and ("trg_slot_protected_cell_guard", "O") in trg
        and ("trg_company_value_owner_guard", "O") in trg
        and owners == 0
        and rows_before == rows_after
        and nonempty == 0
    )
    print("POST-CHECK", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
