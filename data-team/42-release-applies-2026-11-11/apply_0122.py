"""Apply migration 0122 (analytics.company_tag_map, analytics.company_combined_line, five catalog concepts) exactly as
on origin/main, in ONE transaction, then post-check. RUN ONLY AFTER THE FOUNDER'S TYPED GO-AHEAD (founder order
2026-11-11 "FSN for learning, SEC for mapping"; go-ahead typed in the Engineering session).

Usage: apply_0122.py pipeline/db/migrations/0122_company_tag_map.sql cc327c745863f3fc   (sha of 0122 on main 9fa1016)
Rollback: drop table analytics.company_combined_line; drop table analytics.company_tag_map;
          drop function analytics.company_tag_map_no_overlap();
          delete from analytics.canonical_concept where name in ('weighted_basic_shares', 'weighted_diluted_shares',
            'net_interest_income', 'cash_paid_for_interest', 'cash_paid_for_income_taxes')
            (only if nothing references them yet)
"""

import hashlib
import os
import sys
import time

import psycopg

NEW_CONCEPTS = (
    "weighted_basic_shares",
    "weighted_diluted_shares",
    "net_interest_income",
    "cash_paid_for_interest",
    "cash_paid_for_income_taxes",
)

sql_path, want = sys.argv[1:3]
sql = open(sql_path).read()
sha = hashlib.sha256(sql.encode()).hexdigest()
if not sha.startswith(want):
    sys.exit(f"ABORT sha {sha[:16]} != expected {want}")

with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    pre = conn.execute(
        "select to_regclass('analytics.company_tag_map'), to_regclass('analytics.company_combined_line')"
    ).fetchone()
    if any(pre):
        sys.exit(f"ABORT: already present {pre}")
    before = conn.execute("select count(*) from analytics.canonical_concept").fetchone()[0]
    conn.commit()
    with conn.transaction():
        conn.execute("set local lock_timeout = '5s'")
        conn.execute("set local statement_timeout = '5min'")
        conn.execute(sql)
        tables = conn.execute(
            "select to_regclass('analytics.company_tag_map') is not null, "
            "to_regclass('analytics.company_combined_line') is not null"
        ).fetchone()
        trg = conn.execute(
            "select tgenabled from pg_trigger where tgname = 'trg_company_tag_map_no_overlap'"
        ).fetchone()
        have = {
            r[0]
            for r in conn.execute(
                "select name from analytics.canonical_concept where name = any(%s)", (list(NEW_CONCEPTS),)
            ).fetchall()
        }
        after = conn.execute("select count(*) from analytics.canonical_concept").fetchone()[0]
        ok = all(tables) and trg and trg[0] == "O" and have == set(NEW_CONCEPTS)
        print(
            f"tables {tables}; overlap trigger {trg}; new concepts {sorted(have)}; "
            f"canonical_concept {before} -> {after}"
        )
        if not ok:
            raise SystemExit("POST-CHECK (0122) FAIL: rolled back")
    print(f"APPLIED 0122_company_tag_map sha {sha[:16]} at {time.strftime('%H:%M:%S', time.gmtime())} UTC")
    print("POST-CHECK (0122) PASS")
