"""Rank set as an input (PIPELINE.md section 5 cohort ladder): which companies a run covers.

`--ranks 1-100` (default), `101-500`, `1-5000`. Ranks 1..N of the rank source
(doc/data-moat/team/top1000/shards.csv, the rank source top100_coverage takes by default; its `--rank-source` takes another) come from that file;
beyond it the order is market cap in the latest analytics.company_screening_snapshot dataset (DATA-INFERRED ranking,
read-only). The cohort only decides WHICH companies are planned; every stage still takes a company id, so the rank set
does not change a stage. top100_coverage takes any rank set (b2d3956f5, scrooner-f1) from the same rank source; a company
outside it fails fast with a named dead letter (`cohort_unsupported`) instead of exporting nothing.
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SUMMARY = "doc/data-moat/team/top1000/shards.csv"  # the rank source top100_coverage reads by default (ranks 1-1014)


@dataclass(frozen=True)
class Member:
    rank: int
    ticker: str
    company_id: int
    cik: str


def parse_ranks(text: str) -> tuple[int, int]:
    m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", text or "")
    if not m:
        raise ValueError(f"ranks must look like 1-100, got {text!r}")
    lo, hi = int(m.group(1)), int(m.group(2))
    if lo < 1 or hi < lo or hi > 5000:
        raise ValueError(f"bad rank range {lo}-{hi} (1 <= lo <= hi <= 5000)")
    return lo, hi


def summary_members(root: Path = ROOT) -> list[tuple[int, str, int]]:
    out = []
    src = os.environ.get("TOP100_RANK_SOURCE") or str(root / SUMMARY)
    with Path(src).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["rank"].isdigit() and r["company_id"].isdigit():
                out.append((int(r["rank"]), r["ticker"].strip(), int(r["company_id"])))
    return sorted(out)


def resolve(conn, ranks: str = "1-100", root: Path = ROOT) -> list[Member]:
    lo, hi = parse_ranks(ranks)
    base = [m for m in summary_members(root) if lo <= m[0] <= hi]
    rows: list[tuple[int, str, int]] = list(base)
    top_file = max((m[0] for m in summary_members(root)), default=0)
    if hi > top_file:
        have = {m[2] for m in summary_members(root)}
        conn.execute("set statement_timeout = '60s'")
        extra = conn.execute(
            """select s.company_id, s.ticker from analytics.company_screening_snapshot s
               where s.dataset_version = (select max(dataset_version) from analytics.company_screening_snapshot)
                 and s.market_cap is not null order by s.market_cap desc, s.company_id"""
        ).fetchall()
        r = top_file
        for cid, tk in extra:
            if cid in have:
                continue
            r += 1
            if lo <= r <= hi:
                rows.append((r, tk or "", int(cid)))
    ids = [r[2] for r in rows]
    ciks = dict(
        conn.execute(
            "select id, cik from core.company where id = any(%s)", (ids,)
        ).fetchall()
    )
    return [Member(r, t, c, ciks[c]) for r, t, c in sorted(rows) if c in ciks]


def in_rank_source(company_id: int, root: Path = ROOT) -> bool:
    return any(m[2] == company_id for m in summary_members(root))
