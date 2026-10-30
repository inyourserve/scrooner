"""Count the cohort cells the same-vintage Q4 hold would catch. Writes NOTHING.

For every top-1000 company (doc/data-moat/team/top1000/shards.csv) it runs the
real derive_q4_for_company with rule period.same_vintage_derivation@1 in
dry_run mode inside a transaction that is rolled back per company, so the
holds reported are exactly the cells derive_q4 would refuse with the rule ON
(same chain logic, same evaluator verdicts). Output: one CSV row per held cell
(company, concept tag, canonical names, Q4 span, category, block reason, the
FY and YTD accessions and values) and a summary JSON.

One connection; statement_timeout per company set by derive_q4 itself (30min).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import psycopg

from scrooner_pipeline.common import rule_flags as rf
from scrooner_pipeline.normalizer import derived, q4_vintage_hold as vh

SHARDS = Path(__file__).resolve().parents[3] / "doc/data-moat/team/top1000/shards.csv"


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--shards", default=str(SHARDS))
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    os.environ[rf.ENV_DRYRUN] = vh.RULE_ID
    os.environ.pop(rf.ENV_ENABLED, None)
    assert rf.rule_mode(vh.RULE_ID) == rf.DRY_RUN

    companies = []
    with open(args.shards, newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("excluded"):
                continue
            companies.append(
                (int(row["company_id"]), row["cik"], row["ticker"], row["shard"])
            )
    if args.limit:
        companies = companies[: args.limit]
    log(f"{len(companies)} cohort companies")

    conn = psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=30)
    conn.commit = lambda: None  # type: ignore[method-assign]  # every company is rolled back
    done_path = out / "cells.csv"
    seen: set[int] = set()
    if done_path.exists():
        with done_path.open(newline="") as fh:
            seen = {int(r["company_id"]) for r in csv.DictReader(fh)}
    progress_path = out / "progress.jsonl"
    if progress_path.exists():
        seen |= {json.loads(l)["company_id"] for l in progress_path.open()}
    fields = [
        "shard",
        "company_id",
        "cik",
        "ticker",
        "concept_id",
        "tag",
        "canonical_names",
        "q4_start",
        "q4_end",
        "category",
        "block_reason",
        "fy_value",
        "ytd_value",
        "fy_accessions",
        "ytd_accessions",
        "fy_fact_ids",
        "ytd_fact_ids",
        "derived_without_hold",
    ]
    new_file = not done_path.exists()
    with done_path.open("a", newline="") as fh, progress_path.open("a") as prog:
        w = csv.DictWriter(fh, fieldnames=fields)
        if new_file:
            w.writeheader()
        for i, (cid, cik, ticker, shard) in enumerate(companies, 1):
            if cid in seen:
                continue
            holds: list[vh.Hold] = []
            t = time.time()
            try:
                stats = derived.derive_q4_for_company(conn, cid, holds_out=holds)
                tags = dict(
                    conn.execute(
                        "select id, tag from core.concept where id = any(%s)",
                        ([h.concept_id for h in holds] or [0],),
                    ).fetchall()
                )
                names = vh.canonical_names_by_concept(
                    conn, {h.concept_id for h in holds}
                )
            finally:
                conn.rollback()
            for h in holds:
                w.writerow(
                    {
                        "shard": shard,
                        "company_id": cid,
                        "cik": cik,
                        "ticker": ticker,
                        "concept_id": h.concept_id,
                        "tag": tags.get(h.concept_id, "?"),
                        "canonical_names": ";".join(names.get(h.concept_id, [])),
                        "q4_start": h.q4_start,
                        "q4_end": h.q4_end,
                        "category": h.category,
                        "block_reason": h.block_reason,
                        "fy_value": h.fy_value,
                        "ytd_value": h.ytd_value,
                        "fy_accessions": ";".join(h.fy_accessions),
                        "ytd_accessions": ";".join(h.ytd_accessions),
                        "fy_fact_ids": ";".join(map(str, h.fy_fact_ids)),
                        "ytd_fact_ids": ";".join(map(str, h.ytd_fact_ids)),
                        "derived_without_hold": stats["derived"],
                    }
                )
            fh.flush()
            prog.write(
                json.dumps(
                    {
                        "company_id": cid,
                        "ticker": ticker,
                        "derived": stats["derived"],
                        "held_mixed_vintage": stats["held_mixed_vintage"],
                        "held_sign_conflict": stats["held_sign_conflict"],
                        "secs": round(time.time() - t, 1),
                    }
                )
                + "\n"
            )
            prog.flush()
            if i % 25 == 0:
                log(f"{i}/{len(companies)} companies")
    conn.close()

    # summary
    rows = list(csv.DictReader(done_path.open(newline="")))
    prog_rows = [json.loads(l) for l in progress_path.open()]
    by_cat = Counter(r["category"] for r in rows)
    by_name: Counter = Counter()
    for r in rows:
        for n in (
            r["canonical_names"].split(";")
            if r["canonical_names"]
            else ["(unmapped tag)"]
        ):
            by_name[n] += 1
    by_company: dict[str, int] = defaultdict(int)
    for r in rows:
        by_company[r["ticker"]] += 1
    summary = {
        "companies_evaluated": len(prog_rows),
        "q4_cells_derived_without_hold": sum(p["derived"] for p in prog_rows),
        "cells_held": len(rows),
        "companies_with_a_hold": len(by_company),
        "by_category": dict(by_cat),
        "by_canonical_name": dict(by_name.most_common()),
        "top_companies": dict(Counter(by_company).most_common(15)),
        "mapped_statement_cells_held": sum(1 for r in rows if r["canonical_names"]),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    log(
        f"summary: {json.dumps({k: v for k, v in summary.items() if k not in ('by_canonical_name', 'top_companies')})}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
