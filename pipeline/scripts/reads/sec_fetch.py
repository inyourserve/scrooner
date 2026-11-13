"""Fetch the raw SEC documents for document-first reads (no parsing, no DB). sec.gov hosts only, the User-Agent
from SEC_USER_AGENT (the repo secret, never typed here), at most 0.4 requests per second (founder 2026-11-12).

usage: sec_fetch.py <requests.csv> <out_dir>
  requests.csv columns: cik,ticker[,accession,statements,extras,pages]
    no accession -> the company's latest 10-K (from data.sec.gov submissions) plus submissions.json and
                    companyfacts.json(.gz)
    accession    -> that filing only (an era 10-K)
    statements=0 -> skip FilingSummary + statement pages (already fetched)
    extras=1     -> also index.json, MetaLinks.json and the XBRL instance (gzip on disk): the whole-filing check
                    (Dhairya 2026-11-12: not_presented only when absent from face AND notes, checked in the XBRL)
    pages=R12.htm;R40.htm -> those R pages too (note pages that print a data point)
  per filing: FilingSummary.xml and every R page in MenuCategory Statements / Cover / Parenthetical
  (the face statements, their parentheticals and the cover page). Writes <out_dir>/<cik10>/... and
  <out_dir>/fetch_log.jsonl. Resumable: a file already on disk is not fetched again.
"""

from __future__ import annotations

import csv
import gzip
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

# seconds between requests: 0.4 req/s by default; SEC_MIN_INTERVAL overrides (Dhairya 2026-11-13: 2 req/s for the
# red-cell job). Never below 0.25 s (4 req/s, CLAUDE.md).
MIN_INTERVAL = max(0.25, float(os.environ.get("SEC_MIN_INTERVAL") or 2.5))
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


# Some filings put a primary statement in MenuCategory "Uncategorized" (e.g. NEE and PEP FY2021 10-K R3 "Consolidated
# Statement(s) of Income"); such a page is taken when its title names a primary statement.
STATEMENT_TITLE = re.compile(
    r"statements? of (consolidated )?(income|operations|earnings|comprehensive|cash flows?|financial (position|condition)|"
    r"(stockholders|shareholders|shareowners)|changes in equity)|balance sheets?"
)


def statement_pages(summary: bytes) -> list[str]:
    root = ET.fromstring(summary)
    out = []
    for rep in root.iter("Report"):
        cat = (rep.findtext("MenuCategory") or "").strip()
        name = (rep.findtext("HtmlFileName") or "").strip()
        title = (rep.findtext("ShortName") or rep.findtext("LongName") or "").lower()
        if name and (
            cat in ("Statements", "Cover")
            or (cat == "Uncategorized" and STATEMENT_TITLE.search(title))
        ):
            out.append(name)
    return out


INSTANCE_SKIP = ("_cal.xml", "_def.xml", "_lab.xml", "_pre.xml", "FilingSummary.xml")


def instance_name(index: dict) -> str | None:
    items = index.get("directory", {}).get("item", [])
    names = [
        i["name"]
        for i in items
        if i["name"].endswith(".xml") and not i["name"].endswith(INSTANCE_SKIP)
    ]
    htm = [n for n in names if n.endswith("_htm.xml")]
    if htm:
        return htm[0]

    def size(n):
        it = next(i for i in items if i["name"] == n)
        return int(it.get("size") or 0)

    return max(names, key=size) if names else None


def fetch_extras(client, cik: str, acc: str, out: Path, log) -> dict:
    nodash = acc.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{nodash}/"
    d = out / cik / acc
    rec: dict = {}
    ip = d / "index.json"
    if not ip.exists():
        body = get(client, base + "index.json", log)
        if body is None:
            return {"extras_error": "no index.json"}
        save(ip, body)
    name = instance_name(json.loads(ip.read_text()))
    for fn in ("MetaLinks.json", name):
        if not fn:
            rec["extras_error"] = "no instance in index.json"
            continue
        target = d / (fn + ".gz")
        if not target.exists():
            body = get(client, base + fn, log)
            if body is not None:
                save(target, gzip.compress(body))
    rec["instance"] = name
    return rec


def fetch_pages(
    client, cik: str, acc: str, pages: list[str], out: Path, log
) -> list[str]:
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/"
    got = []
    for p in pages:
        if not (out / cik / acc / p).exists():
            body = get(client, base + p, log)
            if body is not None:
                save(out / cik / acc / p, body)
                got.append(p)
    return got


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
    logf = (out / "fetch_log.jsonl").open("a")  # closed at the end of main

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
            if (r.get("statements") or "1").strip() != "0":
                rec.update(fetch_filing(client, cik, acc, out, log))
            else:
                rec["accession"] = acc
            if (r.get("extras") or "").strip() == "1":
                rec.update(fetch_extras(client, cik, acc, out, log))
            pages = [p for p in (r.get("pages") or "").split(";") if p.strip()]
            if pages:
                rec["note_pages"] = fetch_pages(client, cik, acc, pages, out, log)
            summary.append(rec)
            print(json.dumps(rec)[:300], flush=True)
    logf.close()
    (out / "fetch_summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv)
