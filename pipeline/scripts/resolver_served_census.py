"""Census: served cells (analytics.canonical_fact) of the top-100 template companies whose value differs from the
structural resolver's value for the same (concept, period) key. That count is the wrong-value exposure that
structural_direct.enforce_resolver closes on the next rebuild (Dhairya 2026-11-21: STX dividends_per_share FY2022,
MRVL total_debt). Read-only: one connection, statement_timeout per statement, no writes.

    python pipeline/scripts/resolver_served_census.py --out <dir>   [--company-ids 1,2]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import Counter
from decimal import Decimal
from pathlib import Path

import psycopg

from scrooner_pipeline.mapper import company_tag_map as ctm
from scrooner_pipeline.mapper import structural_direct as sd
from scrooner_pipeline.mapper import top100_coverage as tc

ROOT = Path(__file__).resolve().parents[2]
SHARDS = ROOT / "doc/data-moat/team/top1000/shards.csv"
READS = ROOT / "data-team/companies/reads"


def census_company(
    conn, co, concept_info, deadline: float, rounding: Counter
) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("select cik from core.company where id = %s", (co.company_id,))
        cik = cur.fetchone()[0]
        rows = ctm._load_rows(conn, co.company_id)
        periods = ctm._load_periods(conn, co.company_id)
        _cells, st = sd.direct_cells(
            conn, co.company_id, cik, rows, periods, concept_info
        )
        want = {
            (r["canonical_concept_id"], r["period_id"]): r
            for r in st["resolver_values"]
        }
        cur.execute(
            "select canonical_concept_id, period_id, value, source_fact_ids, source_value_ids "
            "from analytics.canonical_fact where company_id = %s",
            (co.company_id,),
        )
        out = []
        for cid, pid, value, fids, vids in cur.fetchall():
            r = want.get((cid, pid))
            if r is None:
                continue
            if Decimal(value) != r["value"] and sd.agrees(Decimal(value), r["value"]):
                rounding[co.ticker] += 1
                continue
            if Decimal(value) == r["value"]:
                continue
            s, e, _t = periods[pid]
            out.append(
                {
                    "ticker": co.ticker,
                    "company_id": co.company_id,
                    "concept": r["concept"],
                    "period_start": s,
                    "period_end": e,
                    "served": value,
                    "resolver": r["value"],
                    "resolver_accession": r["accession"],
                    "shape": sd.shape(Decimal(value), r["value"]),
                    "source_fact_ids": " ".join(map(str, fids or [])),
                    "source_value_ids": " ".join(map(str, vids or [])),
                }
            )
        fids = sorted({int(i) for d in out for i in d["source_fact_ids"].split()})
        accs = sorted({d["resolver_accession"] for d in out})
        cur.execute(
            "select f.id, fl.accession_number, fl.filing_date, fl.form from core.fact f "
            "join core.filing fl on fl.id = f.filing_id where f.id = any(%s)",
            (fids,),
        )
        by_fact = {i: (a, d, fm) for i, a, d, fm in cur.fetchall()}
        cur.execute(
            "select accession_number, filing_date from core.filing where accession_number = any(%s)",
            (accs,),
        )
        rdate = dict(cur.fetchall())
    for d in out:
        src = [
            by_fact[int(i)] for i in d["source_fact_ids"].split() if int(i) in by_fact
        ]
        d["served_filings"] = " ".join(sorted({f"{a}:{fm}" for a, _d, fm in src}))
        rd = rdate.get(d["resolver_accession"])
        sd_ = max((x[1] for x in src), default=None)
        d["filing_order"] = (
            "no_core_lineage"
            if sd_ is None or rd is None
            else "later_filing"
            if sd_ > rd
            else "same_filing"
            if sd_ == rd
            else "earlier_filing"
        )
        # enforce_resolver's decision: a later filing's restated column stays (authority v2); every other copy is held
        d["would_hold"] = not (
            d["filing_order"] == "later_filing" and d["shape"] == "other"
        )
    if time.monotonic() > deadline:
        raise SystemExit("wall-clock cap reached")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--company-ids", default="")
    ap.add_argument("--wall-seconds", type=int, default=3600)
    a = ap.parse_args()
    deadline = time.monotonic() + a.wall_seconds
    ids = {int(x) for x in a.company_ids.split(",") if x}
    companies = [
        c
        for c in tc.load_top(SHARDS, 100)
        if not c.excluded
        and tc.load_docmap(READS, c.ticker)
        and (not ids or c.company_id in ids)
    ]
    a.out.mkdir(parents=True, exist_ok=True)
    diffs: list[dict] = []
    rounding: Counter = Counter()
    with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
        conn.execute("set statement_timeout = '120s'")
        conn.execute("set default_transaction_read_only = on")
        concept_info = ctm.load_concept_info(conn)
        for co in companies:
            diffs += census_company(conn, co, concept_info, deadline, rounding)
    fields = list(diffs[0]) if diffs else ["ticker"]
    with (a.out / "resolver_served_diffs.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(diffs)
    summary = {
        "companies": len(companies),
        "differing_served_cells": len(diffs),
        "rounding_only_agree": sum(rounding.values()),
        "would_hold": sum(d["would_hold"] for d in diffs),
        "would_hold_by_company": dict(
            Counter(d["ticker"] for d in diffs if d["would_hold"]).most_common()
        ),
        "by_shape": dict(Counter(d["shape"] for d in diffs)),
        "by_filing_order": dict(Counter(d["filing_order"] for d in diffs)),
        "by_order_and_shape": dict(
            Counter(f"{d['filing_order']}/{d['shape']}" for d in diffs).most_common()
        ),
        "by_company": dict(Counter(d["ticker"] for d in diffs).most_common()),
        "by_concept": dict(Counter(d["concept"] for d in diffs).most_common()),
    }
    (a.out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
