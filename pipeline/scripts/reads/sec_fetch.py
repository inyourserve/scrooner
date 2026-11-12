"""Fetch the raw SEC documents for document-first reads (no parsing, no DB). sec.gov hosts only, the User-Agent
from SEC_USER_AGENT (the repo secret, never typed here), at most 0.4 requests per second (founder 2026-11-12).

usage: sec_fetch.py <requests.csv> <out_dir>
  requests.csv columns: cik,ticker[,accession]
    no accession -> the company's latest 10-K (from data.sec.gov submissions) plus submissions.json and
                    companyfacts.json(.gz)
    accession    -> that filing only (an era 10-K)
  per filing: FilingSummary.xml and every R page in MenuCategory Statements / Cover / Parenthetical
  (the face statements, their parentheticals and the cover page). Writes <out_dir>/<cik10>/... and
  <out_dir>/fetch_log.jsonl. Resumable: a file already on disk is not fetched again.
"""

from __future__ import annotations

import csv
import gzip
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

MIN_INTERVAL = 2.5  # seconds: 0.4 requests per second
ALLOWED = ("https://www.sec.gov/", "https://data.sec.gov/")
FORMS = ("10-K", "10-K/A", "10-KT")
_last = [0.0]


def get(client: httpx.Client, url: str, log) -> bytes | None:
    assert url.startswith(ALLOWED), url
    for attempt in range(5):
        wait = MIN_INTERVAL - (time.monotonic() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.monotonic()
        try:
            r = client.get(url)
        except httpx.HTTPError as exc:
            log({"url": url, "error": repr(exc)[:200], "attempt": attempt})
            time.sleep(10 * (attempt + 1))
            continue
        log({"url": url, "status": r.status_code, "bytes": len(r.content)})
        if r.status_code == 200:
            return r.content
        if r.status_code == 404:
            return None
        time.sleep(30 * (attempt + 1))  # 403/429/5xx: back off hard
    return None


def save(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def latest_10k(sub: dict) -> tuple[str, str] | None:
    r = sub.get("filings", {}).get("recent", {})
    for form, acc, date in zip(
        r.get("form", []), r.get("accessionNumber", []), r.get("filingDate", [])
    ):
        if form in ("10-K", "10-KT"):
            return acc, date
    return None


def statement_pages(summary: bytes) -> list[str]:
    root = ET.fromstring(summary)
    out = []
    for rep in root.iter("Report"):
        cat = (rep.findtext("MenuCategory") or "").strip()
        name = (rep.findtext("HtmlFileName") or "").strip()
        if name and cat in ("Statements", "Cover"):
            out.append(name)
    return out


def fetch_filing(client, cik: str, acc: str, out: Path, log) -> dict:
    nodash = acc.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{nodash}/"
    d = out / cik / acc
    fs = d / "FilingSummary.xml"
    if not fs.exists():
        body = get(client, base + "FilingSummary.xml", log)
        if body is None:
            return {"accession": acc, "error": "no FilingSummary.xml"}
        save(fs, body)
    pages = statement_pages(fs.read_bytes())
    for p in pages:
        if not (d / p).exists():
            body = get(client, base + p, log)
            if body is not None:
                save(d / p, body)
    return {"accession": acc, "pages": pages}


def main(argv: list[str]) -> None:
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if not ua:
        sys.exit("SEC_USER_AGENT is not set")
    with open(argv[1]) as fh:
        rows = list(csv.DictReader(fh))
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    logf = (out / "fetch_log.jsonl").open("a")  # noqa: SIM115  (closed at the end of main)

    def log(rec):
        logf.write(json.dumps({"t": round(time.time(), 1), **rec}) + "\n")
        logf.flush()

    summary = []
    with httpx.Client(
        headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"},
        timeout=120,
        follow_redirects=False,
    ) as client:
        for r in rows:
            cik = r["cik"].zfill(10)
            acc = (r.get("accession") or "").strip()
            rec = {"cik": cik, "ticker": r["ticker"]}
            if not acc:
                sp = out / cik / "submissions.json"
                if not sp.exists():
                    body = get(
                        client, f"https://data.sec.gov/submissions/CIK{cik}.json", log
                    )
                    if body is None:
                        rec["error"] = "no submissions"
                        summary.append(rec)
                        continue
                    save(sp, body)
                cf = out / cik / "companyfacts.json.gz"
                if not cf.exists():
                    body = get(
                        client,
                        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                        log,
                    )
                    if body is not None:
                        save(cf, gzip.compress(body))
                found = latest_10k(json.loads(sp.read_text()))
                if found is None:
                    rec["error"] = "no 10-K in recent filings"
                    summary.append(rec)
                    continue
                acc, rec["filed"] = found
            rec.update(fetch_filing(client, cik, acc, out, log))
            summary.append(rec)
            print(json.dumps(rec)[:300], flush=True)
    logf.close()
    (out / "fetch_summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv)
