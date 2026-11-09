"""Fetch one filing's XBRL inputs from EDGAR for fsn_store.xbrl_fsn (sec.gov only).

Per filing, about 10-20 requests: the directory index (index.json), the index headers (acceptance
time, form, period, filer CIKs), FilingSummary.xml, MetaLinks.json, the instance, the filer's
schema(s) and separate linkbases, and the R pages of the cover and the statements (FSN `pre` mirrors
what the renderer shows on them). Doc 07 access rules: the declared User-Agent, at most
MAX_REQUESTS_PER_SECOND across processes (the shared SECClient limiter, held at 4/s here whatever
the setting), retry with backoff on 429/5xx. Files are kept byte for byte; nothing is parsed beyond
what is needed to decide which files to fetch.
"""

from __future__ import annotations

import re
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

import structlog

from scrooner_pipeline.fsn_store.xbrl_fsn import FilingFiles

logger = structlog.get_logger()
ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
MAX_REQUESTS_PER_SECOND = 4.0
LINKBASE = re.compile(r"_(pre|cal|lab|def)\.xml$")
RENDERED_MENUS = ("Cover", "Statements")


class Getter(Protocol):
    def get(self, url: str) -> Any: ...


class EdgarClient:
    """httpx with the declared User-Agent, the shared cross-process SEC limiter (the same lock file as
    common.sec_client, so this and any other SEC job on the machine share one budget) at 4 requests/s,
    and retry with backoff on 429/5xx/transport errors (collector.retry.HTTP_RETRY)."""

    def __init__(
        self, user_agent: str, max_per_second: float = MAX_REQUESTS_PER_SECOND
    ):
        import httpx

        from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter

        if not user_agent or "@" not in user_agent:
            raise ValueError("SEC_USER_AGENT must declare a contact (doc 07)")
        # the lock file of common.sec_client (DEFAULT_RATE_LIMITER_LOCK_PATH), without importing the
        # settings that module needs: one budget for every SEC job on the machine
        self._limiter = CrossProcessRateLimiter(
            min(max_per_second, MAX_REQUESTS_PER_SECOND),
            Path(tempfile.gettempdir()) / "scrooner_sec_rate_limiter.lock",
        )
        self._client = httpx.Client(
            headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
            timeout=60.0,
            follow_redirects=False,
        )

    def get(self, url: str) -> Any:
        from tenacity import retry, stop_after_attempt, wait_exponential

        from scrooner_pipeline.collector.retry import HTTP_RETRY

        if not url.startswith("https://www.sec.gov/"):
            raise ValueError(f"sec.gov only: {url}")

        @retry(
            retry=HTTP_RETRY,
            stop=stop_after_attempt(5),
            wait=wait_exponential(min=2, max=30),
            reraise=True,
        )
        def once() -> Any:
            self._limiter.wait()
            resp = self._client.get(url)
            resp.raise_for_status()
            return resp

        return once()

    def close(self) -> None:
        self._client.close()


def filing_base(cik: str | int, adsh: str) -> str:
    return f"{ARCHIVES}/{int(cik)}/{adsh.replace('-', '')}"


def parse_header(text: str) -> dict[str, Any]:
    """The EDGAR index header -> accepted ('YYYY-MM-DD HH:MM:SS.0', FSN form), filed (YYYYMMDD),
    form, period, registrant cik (the first FILER) and co-registrant ciks (the other FILERs)."""
    t = re.sub(r"<[^>]+>", " ", text).replace("&lt;", "<").replace("&gt;", ">")
    out: dict[str, Any] = {}
    m = re.search(r"<ACCEPTANCE-DATETIME>\s*(\d{14})", t)
    if m:
        # FSN sub.accepted is rounded to the minute (TSLA 20:12:41 -> 20:13:00, BAC 17:04:27 -> 17:04:00)
        t0 = datetime.strptime(m.group(1), "%Y%m%d%H%M%S")
        t0 = t0.replace(second=0) + timedelta(minutes=1 if t0.second >= 30 else 0)
        out["accepted"] = t0.strftime("%Y-%m-%d %H:%M:%S.0")
    for key, pat in (
        ("form", r"CONFORMED SUBMISSION TYPE:\s*(\S+)"),
        ("period", r"CONFORMED PERIOD OF REPORT:\s*(\d{8})"),
        ("filed", r"FILED AS OF DATE:\s*(\d{8})"),
    ):
        m = re.search(pat, t)
        if m:
            out[key] = m.group(1)
    names = re.findall(r"COMPANY CONFORMED NAME:\s*(.+)", t)
    ciks = re.findall(r"CENTRAL INDEX KEY:\s*(\d+)", t)
    if ciks:
        out["cik"] = ciks[0]
        out["aciks"] = [c for c in dict.fromkeys(ciks[1:]) if c != ciks[0]]
    if names:
        out["name"] = names[0].strip().replace("&amp;", "&")
    if out.get("period"):
        p = out["period"]
        out["period"] = f"{p[:4]}-{p[4:6]}-{p[6:8]}"
    return out


def wanted_files(names: list[str]) -> list[str]:
    """The XBRL inputs among a filing directory's files (no exhibits, no rendered HTML yet)."""
    want = [
        n
        for n in names
        if n in ("FilingSummary.xml", "MetaLinks.json")
        or n.endswith(".xsd")
        or n.endswith("_htm.xml")
        or LINKBASE.search(n)
    ]
    if not any(n.endswith("_htm.xml") for n in want):  # a plain (non-inline) instance
        want += [
            n
            for n in names
            if n.endswith(".xml")
            and n not in want
            and n != "FilingSummary.xml"
            and not n.startswith("Financial_Report")
        ]
    return want


def rendered_pages(filing_summary: bytes) -> list[str]:
    """The R pages of the cover and the statements."""
    out = []
    for r in ET.fromstring(filing_summary).iter("Report"):
        if (r.findtext("MenuCategory") or "").strip() in RENDERED_MENUS:
            name = (r.findtext("HtmlFileName") or "").strip()
            if re.match(r"R\d+\.htm$", name):
                out.append(name)
    return out


def fetch_filing(
    client: Getter, cik: str | int, adsh: str, fsn_set: str
) -> FilingFiles:
    """Every file xbrl_fsn.convert needs for one accession, plus the header it puts in `sub`."""
    base = filing_base(cik, adsh)
    index = client.get(f"{base}/index.json").json()
    names = [i["name"] for i in index["directory"]["item"]]
    files: dict[str, bytes] = {}
    for n in wanted_files(names):
        files[n] = client.get(f"{base}/{n}").content
    if "FilingSummary.xml" in files:
        for n in rendered_pages(files["FilingSummary.xml"]):
            if n in names:
                files[n] = client.get(f"{base}/{n}").content
    header = parse_header(client.get(f"{base}/{adsh}-index-headers.html").text)
    header["fsn_set"] = fsn_set
    logger.info("fsn_edgar.fetched", cik=str(cik), adsh=adsh, files=len(files))
    return FilingFiles(adsh, files, header)
