"""Apply migration 0121 (core.company_history_source) exactly as on origin/main and seed it from
data-team/47-fsn-store/company_history_sources.csv, in ONE transaction, then post-check.
RUN ONLY AFTER THE FOUNDER'S TYPED GO-AHEAD (given for the XOM history link in scrooner-87, 2026-11-01;
Dhairya asked for the amendment and the full list as one apply).

Usage: apply_0121.py <0121 sql from origin/main> <sha256 prefix> <seed csv>
Rollback: drop table core.company_history_source; drop function core.company_history_source_no_overlap();
"""

import csv
import hashlib
import os
import sys
import time

import psycopg

sql_path, want, seed = sys.argv[1], sys.argv[2], sys.argv[3]
sql = open(sql_path).read()
sha = hashlib.sha256(sql.encode()).hexdigest()
if not sha.startswith(want):
    sys.exit(f"ABORT sha {sha[:16]} != expected {want}")
rows = list(csv.DictReader(open(seed)))

with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
    known = {
        r[0]
        for r in conn.execute(
            "select id from core.company where id = any(%s)",
            (sorted({int(r["company_id"]) for r in rows}),),
        ).fetchall()
    }
    missing = sorted({int(r["company_id"]) for r in rows} - known)
    if missing:
        sys.exit(f"ABORT: company ids not in core.company: {missing}")
    conn.commit()
    with conn.transaction():
        conn.execute("set local lock_timeout = '5s'")
        conn.execute("set local statement_timeout = '5min'")
        conn.execute(sql)
        with conn.cursor() as cur:
            cur.executemany(
                """insert into core.company_history_source
                   (company_id, source_cik, relation, source_name, valid_from, valid_to, reason, evidence)
                   values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                [
                    (
                        int(r["company_id"]),
                        r["source_cik"],
                        r["relation"],
                        r["source_name"],
                        r["valid_from"],
                        r["valid_to"],
                        r["reason"],
                        r["evidence"] or None,
                    )
                    for r in rows
                ],
            )
    print(f"APPLIED 0121_company_history_source sha {sha[:16]} + {len(rows)} rows at {time.strftime('%H:%M:%S', time.gmtime())} UTC")

    n = conn.execute("select count(*) from core.company_history_source").fetchone()[0]
    by = dict(conn.execute("select relation, count(*) from core.company_history_source group by 1").fetchall())
    trg = conn.execute(
        "select tgenabled from pg_trigger where tgname = 'trg_company_history_source_no_overlap'"
    ).fetchone()
    xom = conn.execute(
        """select h.source_cik, h.valid_to from core.company_history_source h join core.company c on c.id = h.company_id
           where c.cik = '0002115436'"""
    ).fetchall()
    # the guard refuses an overlapping predecessor window (rolled back)
    refused = False
    try:
        with conn.transaction():
            conn.execute(
                """insert into core.company_history_source (company_id, source_cik, relation, source_name, valid_from, valid_to, reason)
                   select company_id, '0000000001', 'predecessor', 'overlap probe', valid_from, valid_to, 'probe'
                   from core.company_history_source where relation = 'predecessor' limit 1"""
            )
            raise RuntimeError("probe inserted")
    except psycopg.errors.RaiseException:
        refused = True
    except RuntimeError:
        refused = False
    print(f"rows {n} by relation {by}; overlap trigger enabled {trg}; XOM {xom}; overlap refused {refused}")
    ok = n == len(rows) and trg and trg[0] == "O" and refused and xom
    print("POST-CHECK", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
