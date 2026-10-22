"""Read-only dry-run of RF-10 (pershare.balance_sheet_date_anchor@1, W10).

For each company it compares the NEWEST stored row of `book_value_per_share` and
`net_cash_per_share` with the newest row that sits on a balance-sheet date of the
metric's non-share inputs (equity; cash and debt), which is what the metric stage
would leave as the newest row with the flag on. A cell is "fixed" when the newest
row is blank now and valued after. For every fixed value the dry-run lists the
distinct filings behind its source facts, so a value mixing filings is visible
(AT-DE-26: no value pairs shares and equity from different filings).

Nothing is written: read-only session, one connection, explicit statement_timeout,
at most 100 companies per query.

  python -m scrooner_pipeline.mapper.bs_anchor_dryrun --tickers AAPL \
      --out /tmp/w10_aapl.csv --summary /tmp/w10_aapl.json
  python -m scrooner_pipeline.mapper.bs_anchor_dryrun --all --chunk 50 \
      --out /tmp/w10_all.csv --summary /tmp/w10_all.json   # quiet window only
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from scrooner_pipeline.mapper.bs_anchor import LatestEffect, latest_effect

METRIC_ANCHOR_CONCEPTS = {
    "book_value_per_share": ("stockholders_equity",),
    "net_cash_per_share": ("cash_and_equivalents", "total_debt_resolved"),
}
CHUNK_MAX = 100
HORIZON_START = date(2025, 1, 1)
CSV_FIELDS = [
    "company_id",
    "ticker",
    "metric",
    "end_now",
    "value_now",
    "reason_now",
    "end_after",
    "value_after",
    "reason_after",
    "fixes_latest_cell",
    "filings_behind_value",
    "mixes_filings",
]


def classify(effect: LatestEffect) -> str:
    if effect.end_now is None:
        return "no_rows"
    if not effect.changes_latest_row:
        return "unchanged_valued" if effect.value_now is not None else "unchanged_blank"
    if effect.fixes_latest_cell:
        return "fixed"
    if effect.value_now is not None and effect.value_after is None:
        return "valued_now_blank_after"  # would be a regression: must be 0
    return "still_blank_other_reason"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for metric in METRIC_ANCHOR_CONCEPTS:
        sel = [r for r in rows if r["metric"] == metric]
        out[metric] = {
            "companies_with_rows": len(sel),
            "classes": dict(Counter(r["class"] for r in sel)),
            "fixed_cells": sum(1 for r in sel if r["class"] == "fixed"),
            "fixed_companies": len(
                {r["company_id"] for r in sel if r["class"] == "fixed"}
            ),
            "fixed_mixing_filings": sum(
                1 for r in sel if r["class"] == "fixed" and r["mixes_filings"]
            ),
            "still_blank_reasons_after": dict(
                Counter(
                    r["reason_after"] or "none"
                    for r in sel
                    if r["class"] in ("still_blank_other_reason", "unchanged_blank")
                )
            ),
        }
    return out


def _connect(statement_timeout_ms: int) -> Any:  # pragma: no cover - database
    import psycopg

    from scrooner_pipeline.common.config import settings

    return psycopg.connect(
        settings.database_url,
        options=f"-c statement_timeout={statement_timeout_ms} -c default_transaction_read_only=on",
        autocommit=True,
    )


def run(
    conn: Any, ids: list[int], chunk: int, max_chunks: int | None
) -> tuple[list[dict[str, Any]], dict[int, str]]:  # pragma: no cover - database
    with conn.cursor() as cur:
        cur.execute(
            "select metric_name, id from analytics.metric_definition where metric_name = any(%s)",
            (list(METRIC_ANCHOR_CONCEPTS),),
        )
        metric_id = dict(cur.fetchall())
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (sorted({c for cs in METRIC_ANCHOR_CONCEPTS.values() for c in cs}),),
        )
        concept_id = dict(cur.fetchall())
    id_metric = {v: k for k, v in metric_id.items()}
    id_concept = {v: k for k, v in concept_id.items()}
    out: list[dict[str, Any]] = []
    tickers: dict[int, str] = {}
    for n in range(0, len(ids), min(chunk, CHUNK_MAX)):
        if max_chunks is not None and n // min(chunk, CHUNK_MAX) >= max_chunks:
            break
        part = ids[n : n + min(chunk, CHUNK_MAX)]
        with conn.cursor() as cur:
            cur.execute(
                "select id, primary_ticker from core.company where id = any(%s)",
                (part,),
            )
            tickers.update({i: t or "" for i, t in cur.fetchall()})
            cur.execute(
                """
                select mv.company_id, mv.metric_definition_id, mv.period_end, mv.value,
                       mv.is_null_reason, mv.source_fact_ids
                from analytics.metric_value mv
                where mv.company_id = any(%s) and mv.metric_definition_id = any(%s)
                  and mv.period_label in ('FY','Q1','Q2','Q3','Q4') and mv.period_end >= %s
                """,
                (part, list(metric_id.values()), HORIZON_START),
            )
            stored: dict[tuple[int, str], list[tuple[date, Any, Any, Any]]] = {}
            for cid, mid, end, val, reason, sfids in cur.fetchall():
                stored.setdefault((cid, id_metric[mid]), []).append(
                    (end, val, reason, sfids)
                )
            cur.execute(
                """
                select cf.company_id, cf.canonical_concept_id, p.end_date
                from analytics.canonical_fact cf join core.period p on p.id = cf.period_id
                where cf.company_id = any(%s) and cf.canonical_concept_id = any(%s)
                  and p.period_type = 'instant' and p.end_date >= %s
                """,
                (part, list(concept_id.values()), HORIZON_START),
            )
            dates: dict[tuple[int, str], set[date]] = {}
            for cid, conc, end in cur.fetchall():
                dates.setdefault((cid, id_concept[conc]), set()).add(end)
        fixed_fact_ids: dict[tuple[int, str], list[int]] = {}
        pending: list[dict[str, Any]] = []
        for (cid, metric), rows in stored.items():
            anchor = set().union(
                *(dates.get((cid, c), set()) for c in METRIC_ANCHOR_CONCEPTS[metric])
            )
            eff = latest_effect([(e, v, r) for e, v, r, _s in rows], anchor)
            cls = classify(eff)
            row = {
                "company_id": cid,
                "metric": metric,
                "end_now": eff.end_now,
                "value_now": eff.value_now,
                "reason_now": eff.reason_now,
                "end_after": eff.end_after,
                "value_after": eff.value_after,
                "reason_after": eff.reason_after,
                "class": cls,
                "fixes_latest_cell": cls == "fixed",
                "filings_behind_value": "",
                "mixes_filings": False,
            }
            if cls == "fixed":
                sfids = (
                    next((s for e, _v, _r, s in rows if e == eff.end_after), None) or []
                )
                fixed_fact_ids[(cid, metric)] = list(sfids)
            pending.append(row)
        if fixed_fact_ids:
            all_ids = sorted({f for fs in fixed_fact_ids.values() for f in fs})
            with conn.cursor() as cur:
                cur.execute(
                    "select id, filing_id from core.fact where id = any(%s)", (all_ids,)
                )
                filing_of = dict(cur.fetchall())
            for row in pending:
                fs = fixed_fact_ids.get((row["company_id"], row["metric"]))
                if fs is not None:
                    filings = sorted({filing_of[f] for f in fs if f in filing_of})
                    row["filings_behind_value"] = ";".join(str(f) for f in filings)
                    row["mixes_filings"] = len(filings) > 1
        out.extend(pending)
    return out, tickers


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - database
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    scope = ap.add_mutually_exclusive_group(required=True)
    scope.add_argument("--company-ids")
    scope.add_argument("--tickers")
    scope.add_argument("--sample", type=int)
    scope.add_argument("--all", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--max-chunks", type=int)
    ap.add_argument("--statement-timeout-ms", type=int, default=20000)
    ap.add_argument("--max-clients", type=int, default=14)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--summary", required=True, type=Path)
    args = ap.parse_args(argv)
    conn = _connect(args.statement_timeout_ms)
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from pg_stat_activity where backend_type = 'client backend'"
        )
        clients = int(cur.fetchone()[0])
        if clients > args.max_clients:
            print(
                f"abort: {clients} client backends connected (limit {args.max_clients})",
                file=sys.stderr,
            )
            return 2
        if args.company_ids:
            ids = [int(x) for x in args.company_ids.split(",") if x.strip()]
        elif args.tickers:
            cur.execute(
                "select id from core.company where primary_ticker = any(%s)",
                ([t.strip().upper() for t in args.tickers.split(",")],),
            )
            ids = [r[0] for r in cur.fetchall()]
        else:
            cur.execute("select id from core.company order by id")
            ids = [r[0] for r in cur.fetchall()]
            if args.sample:
                random.Random(args.seed).shuffle(ids)
                ids = sorted(ids[: args.sample])
        cur.execute("select now()")
        watermark = cur.fetchone()[0]
    rows, tickers = run(conn, ids, args.chunk, args.max_chunks)
    with args.out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x["metric"], x["company_id"])):
            w.writerow({**r, "ticker": tickers.get(r["company_id"], "")})
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).resolve().parent,
    ).stdout.strip()
    summary = {
        "metrics": summarize(rows),
        "companies_examined": len(ids)
        if args.max_chunks is None
        else min(len(ids), args.max_chunks * min(args.chunk, CHUNK_MAX)),
        "horizon_start": str(HORIZON_START),
        "db_watermark": str(watermark),
        "git_sha": sha,
    }
    args.summary.write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary["metrics"], indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
