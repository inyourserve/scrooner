"""Propose core.company_history_source rows for a list of companies, from SEC data. Proposals only: the output is a
reviewable CSV (same columns as data-team/47-fsn-store/company_history_sources.csv, plus `status`/`confidence`),
never a database write. A person or agent reviews it, fills `klass` (A/B/C) and commits it; `history_apply` applies
the committed file (dry run by default).

Detection, in order (all DATA-INFERRED until a reviewer opens the filing):
  1. The company's own submissions (data.sec.gov, <= the shared limiter): every 8-K12B / 8-K12G3 filing
     (successor-issuer notices under Exchange Act rule 12g-3 / 12b) is a succession event.
  2. The event's index header (`<acc>-index-headers.html`) lists every filer on that accession; each filer CIK
     other than the company's own is a predecessor candidate (EDGAR co-registrant = the predecessor issuer).
     LIVE LIMIT (2026-11-16): the 8-K12B headers of ExxonMobil Holdings (0001193125-26-291990) and BlackRock Inc
     (0001193125-24-229601) list only the successor, so step 2 proposes nothing for those two and the event goes
     to the review queue (`successor_notice_without_predecessor_cik`). Co-filer detection covers only filings that
     do list the predecessor; the rest still needs a reader.
  3. The candidate's own submissions give its periodic filings (10-K, 10-Q, 20-F, 40-F and amendments). The proposed
     window is valid_from = 2014-01-01 (the storage floor) to the month end of the candidate's last periodic report
     date; `filings` counts the periodic filings inside the window. A candidate with no periodic filing in the
     window is dropped (reported in the review queue).
  4. `formerNames` (names, not CIKs) are written into `evidence` as context only; they never create a row.
A company whose own first periodic filing is later than 2015-12-31 and for which nothing was found goes to the
review queue with reason `late_first_filing_no_predecessor_found`: detection that is not certain is queued, not
guessed. Existing rows in core.company_history_source are skipped by the caller (--existing).

Usage: python -m scrooner_pipeline.onboarding.predecessors --company-ids 1,2 --out-dir out/ [--cache DIR]
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Callable

SUCCESSOR_FORMS = {"8-K12B", "8-K12G3", "8-K12B/A", "8-K12G3/A"}
PERIODIC = {
    "10-K",
    "10-Q",
    "10-K/A",
    "10-Q/A",
    "10-KT",
    "10-QT",
    "10-KT/A",
    "20-F",
    "20-F/A",
    "40-F",
    "40-F/A",
}
FLOOR = date(2014, 1, 1)
LATE_FIRST = date(2015, 12, 31)
COLUMNS = [
    "company_id",
    "source_cik",
    "relation",
    "source_name",
    "valid_from",
    "valid_to",
    "reason",
    "evidence",
    "klass",
    "filings",
    "status",
    "confidence",
]
QUEUE_COLUMNS = ["company_id", "cik", "reason", "detail"]


def month_end(d: date) -> date:
    return date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])


def flatten(payload: dict) -> list[dict]:
    """Submissions payload (base file with filings.recent, or a continuation page) -> one dict per filing. Pure."""
    block = payload["filings"]["recent"] if "filings" in payload else payload
    keys = ("accessionNumber", "form", "filingDate", "reportDate")
    cols = [block.get(k, []) for k in keys]
    return [dict(zip(keys, vals)) for vals in zip(*cols)]


def succession_events(filings: list[dict]) -> list[dict]:
    return [f for f in filings if f.get("form") in SUCCESSOR_FORMS]


def periodic_dates(filings: list[dict]) -> list[date]:
    return sorted(
        {
            date.fromisoformat(f["reportDate"])
            for f in filings
            if f.get("form") in PERIODIC and f.get("reportDate")
        }
    )


def header_filers(header_html: str, own_cik: str) -> list[str]:
    """Every filer CIK in an EDGAR index header except the company's own, in order, 10 digits. Pure."""
    t = re.sub(r"<[^>]+>", " ", header_html)
    ciks = [c.zfill(10) for c in re.findall(r"CENTRAL INDEX KEY:\s*(\d+)", t)]
    return [c for c in dict.fromkeys(ciks) if c != own_cik.zfill(10)]


def propose_row(
    company_id: int,
    cand_cik: str,
    cand_name: str,
    cand_filings: list[dict],
    event: dict,
    former_names: list[str],
) -> dict | None:
    """One proposed predecessor row, or None when the candidate filed no periodic report inside the window. Pure."""
    dates = [d for d in periodic_dates(cand_filings) if d >= FLOOR]
    if not dates:
        return None
    return {
        "company_id": company_id,
        "source_cik": cand_cik.zfill(10),
        "relation": "predecessor",
        "source_name": cand_name or "",
        "valid_from": FLOOR.isoformat(),
        "valid_to": month_end(dates[-1]).isoformat(),
        "reason": f"history filed under predecessor CIK: successor notice {event['form']} names it as a co-filer",
        "evidence": f"{event['form']} {event['accessionNumber']} filed {event['filingDate']}"
        + (f"; former names {'|'.join(former_names)}" if former_names else ""),
        "klass": "",
        "filings": str(len(dates)),
        "status": "PROPOSED_REVIEW",
        "confidence": "DATA-INFERRED",
    }


def detect_company(
    company_id: int,
    cik: str,
    load_submissions: Callable[[str], list[dict]],
    load_header: Callable[[str, str], str],
    former_names: list[str],
    cand_name: Callable[[str], str] = lambda c: "",
) -> tuple[list[dict], list[dict]]:
    """(proposed rows, review-queue rows) for one company. The loaders are injected (SEC in production). Pure
    apart from them."""
    own = load_submissions(cik)
    rows: list[dict] = []
    queue: list[dict] = []
    seen: set[str] = set()
    for ev in succession_events(own):
        cands = header_filers(load_header(cik, ev["accessionNumber"]), cik)
        if not cands:
            # live 2026-11-16: the 8-K12B headers of ExxonMobil Holdings and BlackRock Inc list only the successor,
            # so the predecessor is named only in the filing text. Not guessed: a reviewer names it.
            queue.append(
                {
                    "company_id": company_id,
                    "cik": cik,
                    "reason": "successor_notice_without_predecessor_cik",
                    "detail": f"{ev['form']} {ev['accessionNumber']} filed {ev['filingDate']} lists no other filer; "
                    f"name the predecessor from the filing text; formerNames {'|'.join(former_names) or 'none'}",
                }
            )
        for cand in cands:
            if cand in seen:
                continue
            seen.add(cand)
            row = propose_row(
                company_id,
                cand,
                cand_name(cand),
                load_submissions(cand),
                ev,
                former_names,
            )
            if row:
                rows.append(row)
            else:
                queue.append(
                    {
                        "company_id": company_id,
                        "cik": cik,
                        "reason": "candidate_without_periodic_filing_in_window",
                        "detail": f"{cand} named by {ev['form']} {ev['accessionNumber']}",
                    }
                )
    own_dates = periodic_dates(own)
    if not rows and not queue and own_dates and own_dates[0] > LATE_FIRST:
        queue.append(
            {
                "company_id": company_id,
                "cik": cik,
                "reason": "late_first_filing_no_predecessor_found",
                "detail": f"first periodic report {own_dates[0]}; no 8-K12B/8-K12G3 co-filer found; formerNames {'|'.join(former_names) or 'none'}",
            }
        )
    return rows, queue


def drop_existing(rows: list[dict], existing: set[tuple[int, str]]) -> list[dict]:
    """Skip proposals whose (company_id, source_cik) already has a row in the table. Pure."""
    return [r for r in rows if (int(r["company_id"]), r["source_cik"]) not in existing]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--company-ids", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--cache", default=".cache/onboard-submissions")
    a = ap.parse_args(argv)
    ids = [int(x) for x in a.company_ids.split(",") if x.strip()]
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cache = Path(a.cache)
    cache.mkdir(parents=True, exist_ok=True)

    import psycopg

    from scrooner_pipeline.fsn_store import edgar_fetch

    # data.sec.gov is not on the sec.gov-only EdgarClient allowlist, so submissions go through a thin client that
    # shares the same limiter lock file (one budget per machine) and the same declared User-Agent.
    ua = os.environ.get("SEC_USER_AGENT", "")
    edgar = edgar_fetch.EdgarClient(ua)

    def get_text(url: str) -> str:
        from tenacity import retry, stop_after_attempt, wait_exponential

        from scrooner_pipeline.collector.retry import HTTP_RETRY

        if not (
            url.startswith("https://www.sec.gov/")
            or url.startswith("https://data.sec.gov/")
        ):
            raise ValueError(f"sec.gov only: {url}")

        @retry(
            retry=HTTP_RETRY,
            stop=stop_after_attempt(5),
            wait=wait_exponential(min=2, max=30),
            reraise=True,
        )
        def once() -> str:
            edgar._limiter.wait()
            r = edgar._client.get(url)
            r.raise_for_status()
            return r.text

        return once()

    def cached(name: str, url: str) -> str:
        p = cache / name
        if not p.exists():
            p.write_text(get_text(url))
        return p.read_text()

    def load_submissions(cik: str) -> list[dict]:
        payload = json.loads(
            cached(f"CIK{cik}.json", f"https://data.sec.gov/submissions/CIK{cik}.json")
        )
        filings = flatten(payload)
        for f in payload["filings"].get("files", []):
            filings += flatten(
                json.loads(
                    cached(f["name"], f"https://data.sec.gov/submissions/{f['name']}")
                )
            )
        return filings

    def cand_name(cik: str) -> str:
        return json.loads(
            cached(f"CIK{cik}.json", f"https://data.sec.gov/submissions/CIK{cik}.json")
        ).get("name", "")

    def load_header(cik: str, adsh: str) -> str:
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}"
        return cached(f"hdr-{adsh}.html", f"{base}/{adsh}-index-headers.html")

    rows: list[dict] = []
    queue: list[dict] = []
    with psycopg.connect(
        os.environ.get("SCROONER_DATABASE_URL") or os.environ["DATABASE_URL"]
    ) as conn:
        conn.execute("set statement_timeout = '2min'")
        companies = conn.execute(
            "select id, cik from core.company where id = any(%s) order by id", (ids,)
        ).fetchall()
        existing = {
            (int(c), s)
            for c, s in conn.execute(
                "select company_id, source_cik from core.company_history_source where company_id = any(%s)",
                (ids,),
            ).fetchall()
        }
    missing = set(ids) - {c[0] for c in companies}
    for cid in sorted(missing):
        queue.append(
            {
                "company_id": cid,
                "cik": "",
                "reason": "no_core_company",
                "detail": "run the identity workflow first",
            }
        )
    for cid, cik in companies:
        payload = json.loads(
            cached(f"CIK{cik}.json", f"https://data.sec.gov/submissions/CIK{cik}.json")
        )
        former = [n.get("name", "") for n in payload.get("formerNames") or []]
        r, q = detect_company(
            cid, cik, load_submissions, load_header, former, cand_name
        )
        rows += r
        queue += q
    rows = drop_existing(rows, existing)
    with (out / "proposed_history_sources.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with (out / "review_queue.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=QUEUE_COLUMNS)
        w.writeheader()
        w.writerows(queue)
    print(
        f"predecessors: {len(rows)} proposed rows, {len(queue)} review-queue rows for {len(companies)} companies"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
