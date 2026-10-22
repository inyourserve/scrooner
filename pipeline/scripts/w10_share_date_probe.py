#!/usr/bin/env python3
"""W10 probe: how is the share count dated relative to the latest balance sheet?

Read-only (session default_transaction_read_only, 20 s statement timeout, one
connection, chunks of at most 100 company ids). For each company in the chosen
population it takes the LATEST stockholders_equity instant (canonical_fact,
period end >= --since) as the balance-sheet date `bs`, then classifies the
company's shares_outstanding canonical facts (since the same date):

  bs_date_count      a shares_outstanding fact dated exactly `bs`
  cover_after_only   no fact on `bs`, but one dated in (bs, bs + 120 days]
  later_only         no fact on `bs` or in that window, but one dated later
  none_at_or_after   no fact dated on or after `bs`

and also reports the book_value_per_share rows (newest row blank / has an older
valued row), the figures quoted in the W10 notes.

Populations (state which one every number is over):
  --sample N --seed S   the SAME draw as bs_anchor_dryrun / ttm_guards_dryrun:
                        all core.company ids ordered by id, shuffled with
                        random.Random(S), first N, sorted. Deterministic.
                        (the 300-company seed-1 sample)
  --legacy-mod25        the first probe of 2026-10-22: active companies with
                        id % 25 = 0, `limit 200` WITHOUT an ORDER BY, so the 200
                        were whichever rows the planner returned; not
                        reproducible, kept only so the old figures can be
                        located. Add --order-by-id to make it deterministic.
  --company-ids a,b,c   an explicit list.
Output: counts on stdout and, with --out, one CSV row per company.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any

COVER_WINDOW_DAYS = 120
CHUNK = 100


def classify(bs: date, share_dates: list[date]) -> str:
    if bs in share_dates:
        return "bs_date_count"
    after = [d for d in share_dates if d > bs]
    if not after:
        return "none_at_or_after"
    if any(d <= bs + timedelta(days=COVER_WINDOW_DAYS) for d in after):
        return "cover_after_only"
    return "later_only"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    with_equity = [r for r in rows if r["bs_date"]]
    return {
        "companies_in_population": len(rows),
        "companies_with_latest_equity_instant": len(with_equity),
        "share_count_class": dict(Counter(r["share_count_class"] for r in with_equity)),
        "bvps_rows_companies": sum(1 for r in rows if r["bvps_latest_end"]),
        "bvps_newest_row_blank": sum(
            1 for r in rows if r["bvps_latest_end"] and not r["bvps_latest_valued"]
        ),
        "bvps_newest_blank_with_older_valued_row": sum(
            1
            for r in rows
            if r["bvps_latest_end"]
            and not r["bvps_latest_valued"]
            and r["bvps_has_older_valued"]
        ),
    }


def _connect(timeout_ms: int) -> Any:  # pragma: no cover - database
    import psycopg

    from scrooner_pipeline.common.config import settings

    return psycopg.connect(
        settings.database_url,
        options=f"-c statement_timeout={timeout_ms} -c default_transaction_read_only=on",
        autocommit=True,
    )


def population(
    cur: Any, args: argparse.Namespace
) -> list[int]:  # pragma: no cover - database
    if args.company_ids:
        return [int(x) for x in args.company_ids.split(",") if x.strip()]
    if args.legacy_mod25:
        order = " order by id" if args.order_by_id else ""
        cur.execute(
            f"select id from core.company where id % 25 = 0 and status = 'active'{order} limit 200"
        )
        return sorted(r[0] for r in cur.fetchall())
    cur.execute("select id from core.company order by id")
    ids = [r[0] for r in cur.fetchall()]
    random.Random(args.seed).shuffle(ids)
    return sorted(ids[: args.sample])


def probe(
    cur: Any, ids: list[int], since: date
) -> list[dict[str, Any]]:  # pragma: no cover - database
    cur.execute(
        "select name, id from analytics.canonical_concept where name in ('stockholders_equity','shares_outstanding')"
    )
    concept = dict(cur.fetchall())
    cur.execute(
        "select id from analytics.metric_definition where metric_name = 'book_value_per_share'"
    )
    bvps_id = cur.fetchone()[0]
    out: list[dict[str, Any]] = []
    for i in range(0, len(ids), CHUNK):
        part = ids[i : i + CHUNK]
        cur.execute(
            """
            select cf.company_id, cf.canonical_concept_id, p.end_date
            from analytics.canonical_fact cf join core.period p on p.id = cf.period_id
            where cf.company_id = any(%s) and cf.canonical_concept_id = any(%s) and p.end_date >= %s
            """,
            (part, list(concept.values()), since),
        )
        equity: dict[int, list[date]] = {}
        shares: dict[int, list[date]] = {}
        for cid, conc, end in cur.fetchall():
            (equity if conc == concept["stockholders_equity"] else shares).setdefault(
                cid, []
            ).append(end)
        cur.execute(
            """
            select company_id, period_end, value from analytics.metric_value
            where company_id = any(%s) and metric_definition_id = %s and period_end >= %s
              and period_label in ('FY','Q1','Q2','Q3','Q4')
            """,
            (part, bvps_id, since),
        )
        bvps: dict[int, list[tuple[date, Any]]] = {}
        for cid, end, val in cur.fetchall():
            bvps.setdefault(cid, []).append((end, val))
        for cid in part:
            bs = max(equity[cid]) if cid in equity else None
            rows = sorted(bvps.get(cid, []))
            newest = rows[-1] if rows else None
            out.append(
                {
                    "company_id": cid,
                    "bs_date": bs,
                    "share_count_class": classify(bs, shares.get(cid, []))
                    if bs
                    else "no_equity_instant",
                    "bvps_latest_end": newest[0] if newest else None,
                    "bvps_latest_valued": bool(newest and newest[1] is not None),
                    "bvps_has_older_valued": any(v is not None for _e, v in rows[:-1]),
                }
            )
    return out


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - database
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    scope = ap.add_mutually_exclusive_group(required=True)
    scope.add_argument("--sample", type=int)
    scope.add_argument("--legacy-mod25", action="store_true")
    scope.add_argument("--company-ids")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--order-by-id", action="store_true")
    ap.add_argument("--since", default="2025-06-01")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    conn = _connect(20000)
    cur = conn.cursor()
    cur.execute(
        "select count(*) from pg_stat_activity where backend_type = 'client backend'"
    )
    if cur.fetchone()[0] > 14:
        print("abort: too many client backends", file=sys.stderr)
        return 2
    ids = population(cur, args)
    rows = probe(cur, ids, date.fromisoformat(args.since))
    print(summarize(rows))
    if args.out:
        with args.out.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
