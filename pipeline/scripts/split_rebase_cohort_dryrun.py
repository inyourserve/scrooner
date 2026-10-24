"""Read-only cohort dry-run of the split re-base pass with RU-1 classification
(split.event_basis@1 in dry_run + pershare.never_derive@1 for classification
only). Nothing is written to the database: every connection is set
read-only, statement_timeout is explicit, and the run refuses a chunk when
pooler/app backends (grouped by application_name, platform roles excluded)
plus this run's own connections would exceed --team-cap.

    uv run python scripts/split_rebase_cohort_dryrun.py \
        --cohort cohort.csv --out-cells cells.csv.gz --out-summary summary.json
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import psycopg
from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.rule_flags import ENV_DRYRUN, ENV_ENABLED
from scrooner_pipeline.corporate_actions import share_basis as sb

APP = "split_rebase_cohort_dryrun"
PLATFORM_ROLES = (
    "supabase_storage_admin",
    "authenticator",
    "supabase_admin",
    "pgbouncer",
)
ENV = {ENV_DRYRUN: sb.RULE_ID, ENV_ENABLED: sb.RU1_RULE_ID}
_lock = threading.Lock()


def _connect(timeout: str) -> psycopg.Connection:
    conn = psycopg.connect(
        settings.database_url, connect_timeout=15, application_name=APP
    )
    conn.execute(f"set statement_timeout = '{timeout}'")
    conn.execute("set default_transaction_read_only = on")
    conn.commit()
    return conn


def _backends(conn) -> tuple[int, dict[str, int]]:
    rows = conn.execute(
        "select coalesce(nullif(application_name, ''), usename), count(*)"
        " from pg_stat_activity where backend_type = 'client backend'"
        " and usename <> all(%s) group by 1 order by 2 desc",
        (list(PLATFORM_ROLES),),
    ).fetchall()
    conn.commit()
    by_app = {a: n for a, n in rows}
    return sum(by_app.values()), by_app


def _run_chunk(chunk_no, ids, mapped, concept_ids, args, log):
    out = []
    conn = _connect(args.timeout)
    try:
        total, by_app = _backends(conn)
        mine = by_app.get(APP, 0)
        with _lock:
            log(
                f"chunk {chunk_no}: {len(ids)} ids; pooler/app backends {total} (this run {mine}) {by_app}"
            )
        if total > args.team_cap:
            raise RuntimeError(f"team cap exceeded: {total} > {args.team_cap}")
        for cid in ids:
            for attempt in (1, 2):
                try:
                    facts = sb.load_company_facts(conn, cid, concept_ids)
                    res = sb.compute_company(cid, facts, mapped)
                    current = sb.load_current_cells(conn, cid)
                    conn.commit()
                    out.append((cid, res, current, None))
                    break
                except psycopg.errors.QueryCanceled as exc:
                    conn.rollback()
                    if attempt == 2:
                        out.append((cid, None, None, f"timeout: {exc}".splitlines()[0]))
                except psycopg.OperationalError as exc:
                    conn = _connect(args.timeout)
                    if attempt == 2:
                        out.append(
                            (cid, None, None, f"connection: {exc}".splitlines()[0])
                        )
    finally:
        conn.close()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--out-cells", required=True)
    ap.add_argument("--out-summary", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--timeout", default="20s")
    ap.add_argument("--team-cap", type=int, default=30)
    args = ap.parse_args(argv)
    if args.workers > 6 or args.chunk > 100:
        print("limits: workers <= 6, chunk <= 100", file=sys.stderr)
        return 2

    def log(msg):
        print(time.strftime("%H:%M:%S"), msg, flush=True)

    with open(args.cohort) as fh:
        cohort = list(csv.DictReader(fh))
    ticker = {int(r["company_id"]): r["ticker"] for r in cohort}
    ids = list(ticker)
    conn = _connect(args.timeout)
    total, by_app = _backends(conn)
    log(f"start: {len(ids)} companies; pooler/app backends {total} {by_app}")
    if total + args.workers > args.team_cap:
        print("refusing: team cap", file=sys.stderr)
        return 2
    mapped = sb.load_mapped_tags(conn)
    concept_ids = sb.load_concept_ids(conn, sb.all_input_tags(mapped))
    split_table = defaultdict(list)
    for cid, eff, ratio in conn.execute(
        "select company_id, effective_date, ratio from analytics.company_stock_split"
        " where company_id = any(%s) order by 1, 2",
        (ids,),
    ).fetchall():
        split_table[cid].append((eff.isoformat(), str(ratio)))
    conn.commit()
    conn.close()

    chunks = [ids[i : i + args.chunk] for i in range(0, len(ids), args.chunk)]
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {
            pool.submit(_run_chunk, n, c, mapped, concept_ids, args, log): n
            for n, c in enumerate(chunks)
        }
        for fut in as_completed(futs):
            results.extend(fut.result())
            log(f"done chunk {futs[fut]} ({len(results)}/{len(ids)})")

    # Period dates for the cell table, chunked.
    period_ids = sorted(
        {c.period_id for _, r, cur, _ in results if r for c in r.cells}
        | {k[1] for _, r, cur, _ in results if cur for k in cur}
    )
    periods = {}
    conn = _connect(args.timeout)
    for i in range(0, len(period_ids), 20000):
        for pid, s, e in conn.execute(
            "select id, start_date, end_date from core.period where id = any(%s)",
            (period_ids[i : i + 20000],),
        ).fetchall():
            periods[pid] = (s, e)
        conn.commit()
    conn.close()

    summary = summarize(results, ticker, split_table, periods)
    with gzip.open(args.out_cells, "wt", newline="") as fh:
        write_cells(csv.writer(fh), results, ticker, periods)
    with open(args.out_summary, "w") as fh:
        json.dump(summary, fh, indent=1, default=str)
    log(f"wrote {args.out_cells} and {args.out_summary}")
    return 0


def _row_class(old, cell):
    return sb.classify_change(old, cell, ru1_on=True)


def write_cells(w, results, ticker, periods) -> None:
    w.writerow(
        ["ticker", "company_id", "concept", "period_id", "start", "end", "old_value",
         "new_value", "class", "status", "factor", "chosen_fact_id", "chosen_accession",
         "chosen_as_filed", "n_candidates", "candidates", "source_fact_ids"]
    )  # fmt: skip
    for cid, res, current, _err in results:
        if res is None:
            continue
        keys = set()
        for c in res.cells:
            keys.add((c.concept, c.period_id))
            old = current.get((c.concept, c.period_id))
            old_v = old[1] if old else None
            s, e = periods.get(c.period_id, (None, None))
            w.writerow(
                [ticker[cid], cid, c.concept, c.period_id, s, e, old_v, c.value,
                 _row_class(old_v, c), c.status, c.factor,
                 c.chosen.fact_id if c.chosen else None,
                 c.chosen.accession if c.chosen else None,
                 c.chosen.value if c.chosen else None, len(c.candidates),
                 ";".join(f"{i}:{a}:{v}@f{f}={cv}" for i, a, v, f, cv in c.candidates),
                 list(c.source_fact_ids)]
            )  # fmt: skip
        for key, (_i, v, _s) in current.items():
            if key not in keys:
                s, e = periods.get(key[1], (None, None))
                w.writerow([ticker[cid], cid, key[0], key[1], s, e, v, v,
                            "untouched_no_mapped_fact", "untouched", None, None, None,
                            None, 0, "", []])  # fmt: skip


def _magnitude(old: Decimal, new: Decimal) -> Decimal:
    if old == 0 or new == 0:
        return abs(old - new)
    r = abs(old / new)
    return r if r >= 1 else 1 / r


def _distinct(changes, *, per_share: bool) -> list[dict]:
    seen, out = set(), []
    for m, t, c, e, o, n, a, f, k in changes:
        if (c == "shares_outstanding_resolved") == per_share or t in seen:
            continue
        seen.add(t)
        out.append({"magnitude": str(m), "ticker": t, "concept": c, "period_end": e,
                    "old": str(o), "new": str(n), "accession": a, "factor": f, "class": k})  # fmt: skip
        if len(out) == 20:
            break
    return out


def summarize(results, ticker, split_table, periods) -> dict:
    classes_all: Counter[str] = Counter()
    classes_win: Counter[str] = Counter()
    per_company = {}
    events_status: Counter[str] = Counter()
    events_kinds: Counter[str] = Counter()
    invariant, failures, changes = [], [], []
    detected_only, table_only, both = [], [], []
    for cid, res, current, err in results:
        t = ticker[cid]
        if res is None:
            failures.append({"ticker": t, "company_id": cid, "error": err})
            continue
        cc: Counter[str] = Counter()
        for c in res.cells:
            old = current.get((c.concept, c.period_id))
            old_v = old[1] if old else None
            cls = _row_class(old_v, c)
            if cls == sb.NOW_HIDDEN:
                cls = f"hidden:{c.status}"
            cc[cls] += 1
            classes_all[cls] += 1
            end = periods.get(c.period_id, (None, None))[1]
            if end is not None and end.isoformat() >= "2015-01-01":
                classes_win[cls] += 1
            if (
                c.status == sb.SHOWN
                and old_v is not None
                and cls not in (sb.UNCHANGED, sb.ROUNDING_ONLY)
            ):
                changes.append(
                    (_magnitude(old_v, c.value), t, c.concept, end, old_v, c.value,
                     c.chosen.accession if c.chosen else None, str(c.factor), cls)
                )  # fmt: skip
        evs = [
            {"ratio": str(e.ratio), "status": e.status, "basis_date": e.basis_date,
             "kinds": e.kinds, "pairs": len(e.pairs), "steps": len(e.steps),
             "disclosures": len(e.disclosures), "note": e.note}
            for e in res.events
        ]  # fmt: skip
        for e in res.events:
            events_status[e.status] += 1
            if e.status == "confirmed":
                events_kinds["+".join(sorted(e.kinds))] += 1
        if res.violations:
            invariant.append(
                {"ticker": t, "company_id": cid, "violating_pairs": len(res.violations),
                 "example": [
                     {"tag": p.tag, "old": str(p.old.value), "old_acc": p.old.accession,
                      "new": str(p.new.value), "new_acc": p.new.accession,
                      "expected_ratio": str(x)}
                     for p, x in res.violations[:3]
                 ]}
            )  # fmt: skip
        conf = [e for e in res.events if e.status == "confirmed"]
        tbl = split_table.get(cid, [])
        entry = {"ticker": t, "company_id": cid, "split_table": tbl,
                 "confirmed": [(str(e.ratio), e.basis_date.isoformat()) for e in conf]}  # fmt: skip
        if conf and tbl:
            both.append(entry)
        elif conf:
            detected_only.append(entry)
        elif tbl:
            table_only.append(entry)
        per_company[t] = {"company_id": cid, "events": evs, "classes": dict(cc),
                          "invariant_violations": len(res.violations),
                          "basis_status": dict(Counter(b.status for b in res.basis.values()))}  # fmt: skip
    changes.sort(key=lambda x: (x[0], abs(x[4] - x[5])), reverse=True)
    return {
        "companies_ok": len(per_company),
        "companies_failed": failures,
        "cells_by_class_all_periods": dict(classes_all),
        "cells_by_class_periods_ending_2015_plus": dict(classes_win),
        "events_by_status": dict(events_status),
        "confirmed_events_by_kinds": dict(events_kinds),
        "invariant_companies": invariant,
        "top20_per_share_one_per_company": _distinct(changes, per_share=True),
        "top20_shares_one_per_company": _distinct(changes, per_share=False),
        "top20_changes": [
            {
                "magnitude": str(m),
                "ticker": t,
                "concept": c,
                "period_end": e,
                "old": str(o),
                "new": str(n),
                "accession": a,
                "factor": f,
                "class": k,
            }
            for m, t, c, e, o, n, a, f, k in changes[:20]
        ],
        "splits_in_table_and_detected": both,
        "splits_detected_only_from_filings": detected_only,
        "splits_in_table_not_confirmed": table_only,
        "per_company": per_company,
    }


if __name__ == "__main__":
    raise SystemExit(main())
