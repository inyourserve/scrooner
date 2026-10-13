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
import sys

import psycopg

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.sec_client import SECClient
from scrooner_pipeline.parsers.filing_line_evidence import SPECS, read_filing
from scrooner_pipeline.segments.segment_revenue import _latest_10q_or_10k

CONCEPTS = [spec.concept for spec in SPECS]


def probe_company(client: SECClient, cik: str) -> dict:
    """Reads one company's latest filing via the shared module (patterns live in
    parsers/filing_line_evidence.py, the single source of truth). 'line' maps each
    concept to the matched label, False (statement read, no such line) or None (no
    evidence); a combined line is shown with a '(combined)' suffix."""
    filing = _latest_10q_or_10k(client, cik)
    if filing is None:
        return {"status": "no_filing"}
    rows = read_filing(client, cik, filing["accession_number"])
    if rows is None:
        return {"status": "no_reports", "form": filing["form"]}
    line = {}
    for r in rows:
        if r["line_present"] is None:
            line[r["data_point"]] = None
        elif not r["line_present"]:
            line[r["data_point"]] = False
        else:
            line[r["data_point"]] = r["matched_label"] + (" (combined)" if r["combined"] else "")
    return {"status": "ok", "form": filing["form"], "line": line}


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
        (company_ids, CONCEPTS),
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
            res["ours"] = {c: ours.get((cid, c)) for c in CONCEPTS}
            results.append(res)
            if i % 25 == 0:
                print(f"  probed {i}/{len(sample)}", file=sys.stderr, flush=True)

    json.dump(results, open(args.out, "w"))
    ok = [r for r in results if r["status"] == "ok"]
    print(f"probed {len(results)} companies; filing statements read for {len(ok)}")
    print(f"statuses: {dict(collections.Counter(r['status'] for r in results))}")


if __name__ == "__main__":
    main()
