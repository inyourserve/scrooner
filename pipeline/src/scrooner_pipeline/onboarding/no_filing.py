"""Which companies have no 10-K of their own before the template window (replaces the hard-coded NOFILE list in
scripts/top100_flow.sh). DATA-INFERRED rule, built to reproduce the five CIKs the list held for the top 110 on
2026-11-16 (SHOP, GEV, SNDK, ExxonMobil Holdings, BlackRock Inc):

  a company is `no_filing` when
    (a) its first 10-K family filing in core.filing has a period of report on or after `cutoff`
        (SHOP, GEV, SNDK), or
    (b) it has a `predecessor` row in core.company_history_source whose window ends on or after `cutoff`
        (a holding company that re-registered under a new CIK: the years before the window end live under the
        predecessor CIK, so the successor's own CIK has no 10-K before the cutoff).

`cutoff` defaults to 2024-01-01 (an input). A company with no core.filing rows at all is `unknown` and never
no_filing. The rule is a stated assumption, not filing-checked: a company it adds or drops changes the docmap load
for that company, so compare the printed list with the previous one before an apply.

Usage: python -m scrooner_pipeline.onboarding.no_filing --company-ids 1,2,3 [--cutoff 2024-01-01] [--explain]
Prints the comma-separated 10-digit CIKs (an empty line when none) for `--no-filing-ciks`.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date

DEFAULT_CUTOFF = date(2024, 1, 1)
SQL = """
select c.id, c.cik,
       (select min(f.period_of_report) from core.filing f
         where f.company_id = c.id and f.form like '10-K%%' and f.period_of_report is not null) as first_10k_period,
       (select max(h.valid_to) from core.company_history_source h
         where h.company_id = c.id and h.relation = 'predecessor') as predecessor_to,
       (select count(*) from core.filing f where f.company_id = c.id) as n_filings
from core.company c where c.id = any(%s) order by c.id
"""


def classify(row: dict, cutoff: date = DEFAULT_CUTOFF) -> tuple[str, str]:
    """(verdict, why); verdict is `no_filing`, `has_filing` or `unknown`. Pure."""
    if not row.get("n_filings"):
        return "unknown", "no core.filing rows (run step 1 first)"
    pred, first = row.get("predecessor_to"), row.get("first_10k_period")
    if pred is not None and pred >= cutoff:
        return "no_filing", f"predecessor window ends {pred} (on or after {cutoff})"
    if first is None:
        return "no_filing", "no 10-K family filing at all"
    if first >= cutoff:
        return "no_filing", f"first 10-K period {first} (on or after {cutoff})"
    return "has_filing", f"first 10-K period {first}"


def no_filing_ciks(rows: list[dict], cutoff: date = DEFAULT_CUTOFF) -> list[str]:
    return sorted({r["cik"] for r in rows if classify(r, cutoff)[0] == "no_filing"})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--company-ids", required=True)
    ap.add_argument("--cutoff", default=DEFAULT_CUTOFF.isoformat())
    ap.add_argument(
        "--explain", action="store_true", help="one line per company to stderr"
    )
    a = ap.parse_args(argv)
    ids = [int(x) for x in a.company_ids.split(",") if x.strip()]
    if not ids:
        ap.error("--company-ids is empty")
    cutoff = date.fromisoformat(a.cutoff)
    import psycopg

    with psycopg.connect(
        os.environ.get("SCROONER_DATABASE_URL") or os.environ["DATABASE_URL"]
    ) as conn:
        conn.execute("set statement_timeout = '5min'")
        cur = conn.execute(SQL, (ids,))
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    if a.explain:
        for r in rows:
            print(f"{r['id']} {r['cik']} {classify(r, cutoff)}", file=sys.stderr)
    print(",".join(no_filing_ciks(rows, cutoff)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
