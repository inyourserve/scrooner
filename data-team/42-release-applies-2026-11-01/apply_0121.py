"""Apply migration 0121 (core.company_history_source) exactly as on origin/main and seed it from
data-team/47-fsn-store/company_history_sources.csv, in ONE transaction, then post-check.
RUN ONLY AFTER THE FOUNDER'S TYPED GO-AHEAD (given for the XOM history link in scrooner-87, 2026-11-01;
Dhairya asked for the amendment and the full list as one apply).

Then (Dhairya ruling 2026-11-01, option a) core.period rows for the history-source companies from
data-team/47-fsn-store/company_history_periods.csv (exact dates from the predecessors' own EDGAR filings,
pipeline/scripts/history_periods.py): one transaction per company, a before-image of the company's
core.period rows first, existing rows win (on conflict do nothing).

Usage: apply_0121.py <0121 sql from origin/main> <sha256 prefix> <seed csv> <periods csv> <before-image dir>
Rollback: delete from core.period where id in (the ids this run logged as created);
          drop table core.company_history_source; drop function core.company_history_source_no_overlap();
"""

import csv
import hashlib
import os
import sys
import time

import psycopg

sql_path, want, seed, periods_csv, before_dir = sys.argv[1:6]
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
    print("POST-CHECK (0121)", "PASS" if ok else "FAIL")
    if not ok:
        sys.exit(1)

    # core.period for the history-source companies, one transaction per company
    periods = list(csv.DictReader(open(periods_csv)))
    by_company: dict[int, list[dict]] = {}
    for r in periods:
        by_company.setdefault(int(r["company_id"]), []).append(r)
    os.makedirs(before_dir, exist_ok=True)
    created_ids: list[int] = []
    for cid, rs in sorted(by_company.items()):
        with conn.cursor() as cur, open(f"{before_dir}/core_period_{cid}.csv", "wb") as fh:
            with cur.copy(
                "copy (select * from core.period where company_id = %s order by id) to stdout with csv header",
                (cid,),
            ) as cp:
                for chunk in cp:
                    fh.write(bytes(chunk))
        conn.commit()
        with conn.transaction():
            conn.execute("set local lock_timeout = '5s'")
            got = conn.execute(
                """insert into core.period (company_id, start_date, end_date, period_type, fiscal_year, fiscal_period)
                   select %s, u.s, u.e, u.t, u.fy, u.fp
                   from unnest(%s::date[], %s::date[], %s::text[], %s::int[], %s::text[]) as u(s, e, t, fy, fp)
                   on conflict (company_id, start_date, end_date, period_type) do nothing
                   returning id""",
                (
                    cid,
                    [r["start_date"] for r in rs],
                    [r["end_date"] for r in rs],
                    [r["period_type"] for r in rs],
                    [int(r["fiscal_year"]) if r["fiscal_year"] else None for r in rs],
                    [r["fiscal_period"] or None for r in rs],
                ),
            ).fetchall()
            new = len(got)
            created_ids.extend(g[0] for g in got)
        print(f"core.period company {cid}: {len(rs)} rows, {new} created")
    open(f"{before_dir}/created_period_ids.txt", "w").write("\n".join(map(str, created_ids)))
    print(f"POST-CHECK (periods): {len(created_ids)} created across {len(by_company)} companies; ids in {before_dir}/created_period_ids.txt")
    sys.exit(0)
