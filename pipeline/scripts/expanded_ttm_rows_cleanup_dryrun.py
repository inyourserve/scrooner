#!/usr/bin/env python3
"""Read-only dry-run for the one-time cleanup of superseded expanded_metrics TTM
rows (migration 0107). Counts, in chunks of company ids with a 20 s statement
timeout and one connection, the TTM rows of the metrics expanded_metrics.py
writes, split into the row to KEEP per (company, metric) (the newest period_end)
and the rows the migration would archive and delete.

Output CSV: metric_name, period_end, rows, rows_to_archive. Run from pipeline/:
  python scripts/expanded_ttm_rows_cleanup_dryrun.py --out counts.csv [--chunk 100]
Nothing is written to the database.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

OUTPUTS = (
    "net_debt_ebitda",
    "ev_ebitda",
    "ev_sales",
    "peg_ratio",
    "buyback_yield",
    "total_shareholder_yield",
    "institutional_ownership_pct",
    "share_dilution_trend",
    "cash_conversion_cycle",
    "ebitda_margin",
    "debt_to_ebitda",
    "fcf_per_share",
    "share_repurchases_pct_fcf",
    "dividends_pct_fcf",
    "ebitda",
)  # = expanded_metrics.OUTPUT_METRIC_NAMES (a test pins the equality)


def tally(rows: list[tuple]) -> tuple[Counter, Counter]:
    """rows: (company_id, metric_name, period_end) of TTM rows. Returns
    (rows by (metric, period_end), rows_to_archive by (metric, period_end)):
    everything except each (company, metric)'s newest period_end is archived."""
    newest: dict[tuple, object] = {}
    for cid, metric, end in rows:
        k = (cid, metric)
        if k not in newest or end > newest[k]:
            newest[k] = end
    total: Counter = Counter()
    archive: Counter = Counter()
    for cid, metric, end in rows:
        total[(metric, end)] += 1
        if end != newest[(cid, metric)]:
            archive[(metric, end)] += 1
    return total, archive


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - database
    import psycopg

    from scrooner_pipeline.common.config import settings

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--chunk", type=int, default=100)
    ap.add_argument("--max-clients", type=int, default=14)
    args = ap.parse_args(argv)
    conn = psycopg.connect(
        settings.database_url,
        options="-c statement_timeout=20000 -c default_transaction_read_only=on",
        autocommit=True,
    )
    cur = conn.cursor()
    cur.execute(
        "select count(*) from pg_stat_activity where backend_type = 'client backend'"
    )
    if cur.fetchone()[0] > args.max_clients:
        print("abort: too many client backends", file=sys.stderr)
        return 2
    cur.execute(
        "select id, metric_name from analytics.metric_definition where metric_name = any(%s)",
        (list(OUTPUTS),),
    )
    names = dict(cur.fetchall())
    cur.execute("select min(id), max(id) from core.company")
    lo, hi = cur.fetchone()
    total: Counter = Counter()
    archive: Counter = Counter()
    for start in range(lo, hi + 1, args.chunk):
        cur.execute(
            "select company_id, metric_definition_id, period_end from analytics.metric_value "
            "where company_id >= %s and company_id < %s and period_label = 'TTM' "
            "and metric_definition_id = any(%s)",
            (start, start + args.chunk, list(names)),
        )
        t, a = tally([(c, names[m], e) for c, m, e in cur.fetchall()])
        total.update(t)
        archive.update(a)
    with args.out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["metric_name", "period_end", "rows", "rows_to_archive"])
        for (metric, end), n in sorted(total.items()):
            w.writerow([metric, end, n, archive.get((metric, end), 0)])
    print(f"rows {sum(total.values())}, to archive {sum(archive.values())}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
