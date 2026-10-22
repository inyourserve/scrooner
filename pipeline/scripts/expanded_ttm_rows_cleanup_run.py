#!/usr/bin/env python3
"""Apply (or rehearse) the one-time cleanup of superseded expanded_metrics TTM rows
by calling analytics.archive_superseded_expanded_ttm (migration 0107) in
company-id chunks. NOT run by any workflow.

  dry run (default, read-only):  python scripts/expanded_ttm_rows_cleanup_run.py
  apply:                         ... --apply --expected-rows N

--apply is refused unless --expected-rows equals the number of rows the dry-run
count (scripts/expanded_ttm_rows_cleanup_dryrun.py, summed rows_to_archive) says
will move, and the migration must already be applied. Each chunk is its own
transaction with an explicit statement_timeout; the run stops at the first error.
Heavy-job rules apply: ListAgents first, one connection, a heavy slot.
"""

from __future__ import annotations

import argparse
import sys


def plan_chunks(lo: int, hi: int, chunk: int) -> list[tuple[int, int]]:
    return [(s, min(s + chunk, hi + 1)) for s in range(lo, hi + 1, chunk)]


def check_expected(expected: int | None, counted: int) -> None:
    if expected is None or expected != counted:
        raise SystemExit(
            f"refusing to apply: --expected-rows {expected} does not equal the {counted} rows "
            "the current count says would move; re-run the dry-run and review it"
        )


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - database
    import psycopg

    from scrooner_pipeline.common.config import settings
    from scrooner_pipeline.mapper.expanded_metrics import OUTPUT_METRIC_NAMES

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--expected-rows", type=int)
    ap.add_argument("--chunk", type=int, default=100)
    ap.add_argument("--statement-timeout-ms", type=int, default=120000)
    args = ap.parse_args(argv)
    conn = psycopg.connect(
        settings.database_url,
        options=f"-c statement_timeout={args.statement_timeout_ms}",
    )
    cur = conn.cursor()
    cur.execute(
        "select to_regprocedure('analytics.archive_superseded_expanded_ttm(bigint,bigint,bigint[])')"
    )
    if cur.fetchone()[0] is None:
        print("migration 0107 is not applied", file=sys.stderr)
        return 2
    cur.execute(
        "select id from analytics.metric_definition where metric_name = any(%s)",
        (sorted(OUTPUT_METRIC_NAMES),),
    )
    ids = [r[0] for r in cur.fetchall()]
    cur.execute("select min(id), max(id) from core.company")
    lo, hi = cur.fetchone()
    conn.rollback()
    moved_total = 0
    for a, b in plan_chunks(lo, hi, args.chunk):
        if not args.apply:
            cur.execute(
                "select count(*) from analytics.metric_value mv where mv.company_id >= %s and mv.company_id < %s "
                "and mv.period_label = 'TTM' and mv.metric_definition_id = any(%s) and mv.period_end < "
                "(select max(x.period_end) from analytics.metric_value x where x.company_id = mv.company_id "
                "and x.metric_definition_id = mv.metric_definition_id and x.period_label = 'TTM')",
                (a, b, ids),
            )
            moved_total += cur.fetchone()[0]
            conn.rollback()
            continue
        if moved_total == 0 and a == lo:
            check_expected(args.expected_rows, sum_count(conn, ids, lo, hi, args.chunk))
        cur.execute(
            "select analytics.archive_superseded_expanded_ttm(%s, %s, %s)", (a, b, ids)
        )
        moved_total += cur.fetchone()[0]
        conn.commit()
    print(("moved" if args.apply else "would move"), moved_total, "rows")
    return 0


def sum_count(conn, ids, lo, hi, chunk):  # pragma: no cover - database
    cur = conn.cursor()
    total = 0
    for a, b in plan_chunks(lo, hi, chunk):
        cur.execute(
            "select count(*) from analytics.metric_value mv where mv.company_id >= %s and mv.company_id < %s "
            "and mv.period_label = 'TTM' and mv.metric_definition_id = any(%s) and mv.period_end < "
            "(select max(x.period_end) from analytics.metric_value x where x.company_id = mv.company_id "
            "and x.metric_definition_id = mv.metric_definition_id and x.period_label = 'TTM')",
            (a, b, ids),
        )
        total += cur.fetchone()[0]
        conn.rollback()
    return total


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
