"""History tranche 1: 12 approved rows into core.company_history_source (live 40 -> 52), then core.period rows
for the two companies that gain a predecessor (MDT <- 0000064670, KDP <- 0000909954). NO DDL: the table and its
overlap trigger exist (migration 0121). Approved by the independent Verifier (FILING-CHECKED) and release approver
Ritwik 2026-11-10; window ends are FSN month-ends (fsn.filing.period).
RUN ONLY AFTER THE FOUNDER'S TYPED GO-AHEAD.

Usage (from the repo root, DATABASE_URL set to the dev database):
    DATABASE_URL=... python3 data-team/42-release-applies-2026-11-10/apply_history_tranche1.py \
        data-team/47-fsn-store/company_history_sources.csv data-team/47-fsn-store/company_history_periods.csv <before-image dir>
    add --check to validate the CSVs and the live table and write nothing.

Steps: (1) validate CSVs, refuse unless the live table holds exactly 40 rows and every one of them is in the CSV
(the CSV's other 12 are the new rows); (2) one transaction inserts the 12, post-checks count 52, trigger enabled,
an overlap probe refused; (3) per company with a new predecessor: before-image of its core.period rows, then one
transaction inserting the periods CSV rows (existing rows win), created ids logged to <dir>/created_period_ids.txt.

Rollback: delete from core.period where id in (the ids in created_period_ids.txt);
          delete from core.company_history_source where (company_id, source_cik, valid_from) in
          ((3639,'0000064670','2014-01-01'),(3639,'0001613103','2014-01-01'),(5779,'0001418135','2013-01-01'),
           (5779,'0000909954','2013-01-01'),(1938,'0000924805','2013-01-01'),(4744,'0001701605','2014-01-01'),
           (5306,'0001748790','2014-01-01'),(4814,'0001705696','2014-01-01'),(2323,'0001818874','2014-01-01'),
           (4398,'0001674101','2014-01-01'),(2370,'0001819994','2014-01-01'),(5018,'0001326110','2014-01-01'));
          (the table must be back to 40 rows.)
"""

from __future__ import annotations

import calendar
import csv
import os
import sys
import time
from datetime import date

EXPECTED_LIVE = 40
EXPECTED_NEW = 12
EXPECTED_AFTER = 52
HISTORY_FLOOR = date(2014, 1, 1)  # core.period storage floor (common/history_floor.py)


def _month_end(d: date) -> bool:
    return d.day == calendar.monthrange(d.year, d.month)[1]


def validate_sources(rows: list[dict], known_company_ids: set[int] | None = None, month_end_keys: set[tuple] | None = None) -> list[str]:
    """Problems with the sources CSV (empty list = valid; the month-end rule applies to month_end_keys, default all rows,
    because the 40 seeded rows predate the rule): columns, relation, CIK shape, month-end valid_to,
    valid_from <= valid_to, non-empty reason, duplicate keys, overlapping predecessor windows per company."""
    problems: list[str] = []
    need = {"company_id", "source_cik", "relation", "source_name", "valid_from", "valid_to", "reason", "evidence", "klass", "filings"}
    if not rows:
        return ["no rows"]
    if need - set(rows[0]):
        return [f"missing columns {sorted(need - set(rows[0]))}"]
    keys: set[tuple] = set()
    preds: dict[str, list[tuple[date, date, str]]] = {}
    for i, r in enumerate(rows, 2):
        try:
            f, t = date.fromisoformat(r["valid_from"]), date.fromisoformat(r["valid_to"])
        except ValueError:
            problems.append(f"line {i}: bad date")
            continue
        if f > t:
            problems.append(f"line {i}: valid_from after valid_to")
        if not _month_end(t) and (month_end_keys is None or (int(r["company_id"]), r["source_cik"], r["valid_from"]) in month_end_keys):
            problems.append(f"line {i}: valid_to {t} is not a month-end")
        if r["relation"] not in ("predecessor", "exclude"):
            problems.append(f"line {i}: relation {r['relation']!r}")
        if not (len(r["source_cik"]) == 10 and r["source_cik"].isdigit()):
            problems.append(f"line {i}: source_cik {r['source_cik']!r}")
        if not r["reason"].strip():
            problems.append(f"line {i}: empty reason")
        if r["klass"] not in ("A", "B", "C"):
            problems.append(f"line {i}: klass {r['klass']!r}")
        if r["relation"] == "predecessor" and not r["filings"].isdigit():
            problems.append(f"line {i}: predecessor without a filings count")
        k = (r["company_id"], r["source_cik"], r["valid_from"])
        if k in keys:
            problems.append(f"line {i}: duplicate key {k}")
        keys.add(k)
        if known_company_ids is not None and int(r["company_id"]) not in known_company_ids:
            problems.append(f"line {i}: company {r['company_id']} not in core.company")
        if r["relation"] == "predecessor":
            preds.setdefault(r["company_id"], []).append((f, t, r["source_cik"]))
    for cid, ws in preds.items():
        ws.sort()
        for a, b in zip(ws, ws[1:]):
            if b[0] <= a[1]:
                problems.append(f"company {cid}: predecessor windows overlap ({a[2]} {a[0]}..{a[1]} vs {b[2]} {b[0]}..{b[1]})")
    return problems


def validate_periods(rows: list[dict], company_ids: set[int]) -> list[str]:
    problems = []
    seen = set()
    for i, r in enumerate(rows, 2):
        if int(r["company_id"]) not in company_ids:
            continue
        s, e = date.fromisoformat(r["start_date"]), date.fromisoformat(r["end_date"])
        if e < HISTORY_FLOOR:
            problems.append(f"line {i}: period ends {e}, before the storage floor")
        if r["period_type"] == "instant" and s != e:
            problems.append(f"line {i}: instant with a span")
        if s > e:
            problems.append(f"line {i}: start after end")
        k = (r["company_id"], r["start_date"], r["end_date"], r["period_type"])
        if k in seen:
            problems.append(f"line {i}: duplicate period {k}")
        seen.add(k)
    return problems


def key_of(r: dict) -> tuple[int, str, str]:
    return int(r["company_id"]), r["source_cik"], r["valid_from"]


def main() -> None:
    import psycopg

    args = [a for a in sys.argv[1:] if a != "--check"]
    check_only = "--check" in sys.argv[1:]
    seed, periods_csv, before_dir = args
    rows = list(csv.DictReader(open(seed)))
    periods = list(csv.DictReader(open(periods_csv)))
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=20) as conn:
        conn.execute("set statement_timeout = '60s'")
        known = {r[0] for r in conn.execute("select id from core.company where id = any(%s)", (sorted({int(r["company_id"]) for r in rows}),)).fetchall()}
        new_keys = {key_of(r) for r in rows} - {(int(c), s, f) for c, s, f in conn.execute("select company_id, source_cik, valid_from::text from core.company_history_source").fetchall()}
        problems = validate_sources(rows, known, new_keys)
        live = conn.execute("select company_id, source_cik, valid_from::text from core.company_history_source").fetchall()
        live_keys = {(int(c), s, f) for c, s, f in live}
        csv_keys = {key_of(r) for r in rows}
        new = [r for r in rows if key_of(r) not in live_keys]
        if len(live) != EXPECTED_LIVE:
            problems.append(f"live row count {len(live)} != {EXPECTED_LIVE}")
        if live_keys - csv_keys:
            problems.append(f"live rows missing from the CSV: {sorted(live_keys - csv_keys)}")
        if len(new) != EXPECTED_NEW:
            problems.append(f"{len(new)} new rows, expected {EXPECTED_NEW}")
        new_pred_companies = {int(r["company_id"]) for r in new if r["relation"] == "predecessor"}
        problems += validate_periods(periods, new_pred_companies)
        if problems:
            sys.exit("ABORT:\n  " + "\n  ".join(problems))
        print(f"CHECK ok: live {len(live)}, new {len(new)}, periods for companies {sorted(new_pred_companies)}")
        if check_only:
            return
        conn.commit()
        with conn.transaction():
            conn.execute("set local lock_timeout = '5s'")
            conn.execute("set local statement_timeout = '5min'")
            with conn.cursor() as cur:
                cur.executemany(
                    """insert into core.company_history_source
                       (company_id, source_cik, relation, source_name, valid_from, valid_to, reason, evidence)
                       values (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    [(int(r["company_id"]), r["source_cik"], r["relation"], r["source_name"], r["valid_from"], r["valid_to"], r["reason"], r["evidence"] or None) for r in new],
                )
        print(f"INSERTED {len(new)} rows at {time.strftime('%H:%M:%S', time.gmtime())} UTC")
        n = conn.execute("select count(*) from core.company_history_source").fetchone()[0]
        trg = conn.execute("select tgenabled from pg_trigger where tgname = 'trg_company_history_source_no_overlap'").fetchone()
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
        print(f"rows {n}; overlap trigger enabled {trg}; overlap refused {refused}")
        ok = n == EXPECTED_AFTER and trg and trg[0] == "O" and refused
        print("POST-CHECK (sources)", "PASS" if ok else "FAIL")
        if not ok:
            sys.exit(1)

        by_company: dict[int, list[dict]] = {}
        for r in periods:
            if int(r["company_id"]) in new_pred_companies:
                by_company.setdefault(int(r["company_id"]), []).append(r)
        os.makedirs(before_dir, exist_ok=True)
        created: list[int] = []
        for cid, rs in sorted(by_company.items()):
            with conn.cursor() as cur, open(f"{before_dir}/core_period_{cid}.csv", "wb") as fh:
                with cur.copy("copy (select * from core.period where company_id = %s order by id) to stdout with csv header", (cid,)) as cp:
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
            created.extend(g[0] for g in got)
            print(f"core.period company {cid}: {len(rs)} rows, {len(got)} created")
        open(f"{before_dir}/created_period_ids.txt", "w").write("\n".join(map(str, created)))
        print(f"POST-CHECK (periods): {len(created)} created across {len(by_company)} companies; ids in {before_dir}/created_period_ids.txt")


if __name__ == "__main__":
    main()
