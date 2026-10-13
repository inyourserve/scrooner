"""Applicability probe: for a stratified sample of real operating companies, does
the company's OWN latest filing show a line for each concept -- and does our data
have it? Separates "this line does not exist for this kind of company" from
"it is in the filing and we failed to extract it", which the coverage score
cannot tell apart (87% of absent cells carry no recorded reason).

Independent of our extraction: it reads the filing's rendered balance sheet and
income statement (FilingSummary.xml -> R*.htm), the same source the revenue and
cost-of-revenue parsers use, and checks row labels with a per-concept pattern.
No yfinance, nothing is stored; output is a JSON report plus a printed summary.

  uv run python pipeline/scripts/applicability_probe.py --per-sector 20 --out /tmp/probe.json
  uv run python pipeline/scripts/applicability_probe.py --ciks 0000320193,0000019617   # calibration
"""

import argparse
import collections
import json
import random
import re
import sys

import psycopg
import structlog

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.parsers.revenue_parser import (
    _CELL,
    _ROW,
    INCOME_STATEMENT_TITLE_PATTERN,
    PARENTHETICAL_SUFFIX_PATTERN,
    _cell_text,
)
from scrooner_pipeline.segments.segment_revenue import (
    _filing_summary_reports,
    _latest_10q_or_10k,
)

logger = structlog.get_logger()

BALANCE_SHEET_TITLE = re.compile(
    r"balance\s+sheets?|statements?\s+of\s+(consolidated\s+)?financial\s+(condition|position)"
    r"|statements?\s+of\s+(net\s+)?assets",
    re.IGNORECASE,
)
EARNINGS_TITLE = re.compile(
    r"statements?\s+of\s+(consolidated\s+)?(earnings|profit|comprehensive\s+(income|loss))"
    r"|\bincome\s+statements?\b",
    re.IGNORECASE,
)
# Rendered reports embed a hidden "- Definition ..." popup row under many line
# items; those are documentation, not statement lines (Apple's "goodwill" match).
_DEFINITION_ROW = re.compile(r"^\s*-\s*(definition|details?)\b", re.IGNORECASE)

# concept -> (statement, label pattern). Patterns are deliberately about the
# LINE a reader would see; "present in filing" means such a row exists.
SPECS: dict[str, tuple[str, re.Pattern]] = {
    "inventory": ("BS", re.compile(r"\binventor(y|ies)\b", re.I)),
    "accounts_receivable": (
        "BS",
        re.compile(r"(account|trade|customer)s?\s*(and\s+[\w\s]+?)?receivable|^\s*receivables?\b", re.I),
    ),
    "accounts_payable": (
        "BS",
        re.compile(r"(account|trade)s?\s*(and\s+[\w\s]+?)?payable|^\s*payables?\b", re.I),
    ),
    "goodwill": ("BS", re.compile(r"\bgoodwill\b", re.I)),
    "cost_of_revenue": (
        "IS",
        re.compile(r"\bcosts?\s+of\s+(net\s+)?(revenues?|sales|goods|products?|services|operations)\b", re.I),
    ),
    "gross_profit": ("IS", re.compile(r"\bgross\s+(profit|margin|income)\b", re.I)),
    "research_and_development": (
        "IS",
        re.compile(r"research\s*(and|&)\s*development|product\s+development|technology\s+and\s+development", re.I),
    ),
    "interest_income": (
        "IS",
        re.compile(r"interest\s+(income|and\s+(dividend|other|investment)\s+income)|investment\s+income|interest\s+and\s+other\s+income", re.I),
    ),
    "operating_expenses": (
        "IS",
        re.compile(r"total\s+(operating\s+)?(costs?\s+and\s+)?expenses|total\s+operating\s+costs|operating\s+expenses,?\s+total", re.I),
    ),
}


def _labels(html: str) -> list[str]:
    out = []
    for _cls, inner in _ROW.findall(html):
        cells = _CELL.findall(inner)
        if cells:
            text = _cell_text(cells[0]).strip()
            if text and not _DEFINITION_ROW.search(text):
                out.append(text)
    return out


def _pick(reports: list[dict], pattern: re.Pattern, extra: re.Pattern | None = None) -> dict | None:
    for r in reports:
        if PARENTHETICAL_SUFFIX_PATTERN.search(r["title"]):
            continue
        if pattern.search(r["title"]) or (extra and extra.search(r["title"])):
            return r
    return None


def probe_company(client: SECClient, cik: str) -> dict:
    filing = _latest_10q_or_10k(client, cik)
    if filing is None:
        return {"status": "no_filing"}
    reports = _filing_summary_reports(client, int(cik), filing["accession_number"])
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{filing['accession_number'].replace('-', '')}/"
    bs = _pick(reports, BALANCE_SHEET_TITLE)
    inc = _pick(reports, INCOME_STATEMENT_TITLE_PATTERN, EARNINGS_TITLE)
    labels = {"BS": [], "IS": []}
    if bs:
        labels["BS"] = _labels(client.get(base + bs["html_file"]).text)
    if inc:
        labels["IS"] = _labels(client.get(base + inc["html_file"]).text)
    found = {}
    for concept, (stmt, pat) in SPECS.items():
        if stmt == "BS" and not bs or stmt == "IS" and not inc:
            found[concept] = None  # statement not located: no evidence either way
            continue
        hit = next((l for l in labels[stmt] if pat.search(l)), None)
        found[concept] = hit or False
    return {
        "status": "ok",
        "form": filing["form"],
        "bs_found": bool(bs),
        "is_found": bool(inc),
        "line": found,
    }


def sample_companies(conn, per_sector: int, seed: int) -> list[tuple[int, str, str]]:
    rows = conn.execute(
        """
        select c.id, c.cik, coalesce(c.sector, '(none)')
        from core.company c
        join analytics.company_population p on p.company_id = c.id and p.population_name = 'real_operating_company'
        where c.status = 'active'
        """
    ).fetchall()
    by_sector = collections.defaultdict(list)
    for r in rows:
        by_sector[r[2]].append(r)
    rng = random.Random(seed)
    out = []
    for sector, items in sorted(by_sector.items()):
        out.extend(rng.sample(items, min(per_sector, len(items))))
    return out


def our_data(conn, company_ids: list[int]) -> dict[tuple[int, str], bool]:
    rows = conn.execute(
        """
        select company_id, data_point_name, has_value
        from analytics.company_data_point_coverage
        where company_id = any(%s) and data_point_name = any(%s)
        """,
        (company_ids, list(SPECS)),
    ).fetchall()
    return {(c, n): bool(h) for c, n, h in rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-sector", type=int, default=20)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--ciks", help="comma-separated CIKs (calibration run; skips sampling)")
    ap.add_argument("--out", default="/tmp/applicability_probe.json")
    args = ap.parse_args()

    with psycopg.connect(settings.database_url) as conn:
        conn.execute("set statement_timeout='100s'")
        if args.ciks:
            wanted = [c.strip().zfill(10) for c in args.ciks.split(",")]
            sample = [
                (r[0], r[1], r[2] or "(none)")
                for r in conn.execute(
                    "select id, cik, sector from core.company where cik = any(%s)", (wanted,)
                ).fetchall()
            ]
        else:
            sample = sample_companies(conn, args.per_sector, args.seed)
        ours = our_data(conn, [s[0] for s in sample])

    results = []
    with SECClient() as client:
        for i, (cid, cik, sector) in enumerate(sample, 1):
            try:
                res = probe_company(client, cik)
            except Exception as exc:  # one company's fetch failure must not stop the sample
                res = {"status": f"error:{type(exc).__name__}"}
            res.update({"company_id": cid, "cik": cik, "sector": sector})
            res["ours"] = {c: ours.get((cid, c)) for c in SPECS}
            results.append(res)
            if i % 25 == 0:
                print(f"  probed {i}/{len(sample)}", file=sys.stderr, flush=True)

    json.dump(results, open(args.out, "w"))
    ok = [r for r in results if r["status"] == "ok"]
    print(f"probed {len(results)} companies; filing statements read for {len(ok)}")
    print(f"statuses: {dict(collections.Counter(r['status'] for r in results))}")


if __name__ == "__main__":
    main()
