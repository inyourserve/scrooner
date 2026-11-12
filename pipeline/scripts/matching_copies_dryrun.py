"""READ-ONLY dry run of dedupe.matching_copies@1 over the top-1,000 cohort (doc/data-moat/team/top1000/shards.csv).

One connection (default_transaction_read_only, explicit statement_timeout), company by company, the SAME pure
planner the production stage runs (normalizer/dedupe.plan_authority), once with the rule off and once on.
A group "gains" an authoritative fact when the rule resolves it and the stored state had none.
Writes only summary.json under --out-dir.

  cd pipeline && PYTHONPATH=src python scripts/matching_copies_dryrun.py --out-dir <dir> [--ciks a,b] [--max-companies N]
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.normalizer.dedupe import (
    CLASS_MATCHING_COPIES_RESOLVED,
    _load_fact_rows,
    plan_authority,
)

SHARDS = Path(__file__).resolve().parents[2] / "doc/data-moat/team/top1000/shards.csv"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--ciks")
    ap.add_argument("--max-companies", type=int, default=0)
    ap.add_argument("--statement-timeout-ms", type=int, default=60000)
    args = ap.parse_args(argv)
    ciks = [c for c in (args.ciks or "").split(",") if c] or sorted(
        {r["cik"] for r in csv.DictReader(SHARDS.open()) if not r.get("excluded")}
    )
    if args.max_companies:
        ciks = ciks[: args.max_companies]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    per_company: Counter = Counter()
    names: dict[str, str] = {}
    gained = changed = errors = 0
    with psycopg.connect(settings.database_url, autocommit=False) as conn:
        conn.execute("set default_transaction_read_only = on")
        conn.execute(f"set statement_timeout = {int(args.statement_timeout_ms)}")
        for cik in ciks:
            row = conn.execute("select id, coalesce(display_name, company_name) from core.company where cik = %s", (cik,)).fetchone()
            if not row:
                continue
            cid, name = row
            names[cik] = name
            try:
                rows = _load_fact_rows(conn, cid)
                plan = plan_authority(rows, matching_copies=True, collect_changes=True)
            except psycopg.Error as exc:
                errors += 1
                conn.rollback()
                print(f"error {cik}: {exc}")
                continue
            for klass, _c, _u, _p, before, after, _f in plan.changes:
                if klass != CLASS_MATCHING_COPIES_RESOLVED:
                    continue
                if not before and after:
                    gained += 1
                    per_company[cik] += 1
                else:
                    changed += 1
            conn.rollback()
    top = [{"cik": c, "name": names[c], "groups_gained": n} for c, n in per_company.most_common(20)]
    summary = {
        "companies_scanned": len(ciks), "errors": errors,
        "groups_gaining_an_authoritative_fact": gained,
        "companies_with_a_gain": len(per_company),
        "matching_resolved_but_already_had_an_authoritative_copy": changed,
        "top20_by_company": top,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
