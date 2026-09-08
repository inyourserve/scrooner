"""Clean company display name for UI, kept separate from core.company.
company_name (the SEC source of truth, never overwritten -- same "new
column, don't touch the authoritative field" discipline as y_sector/
y_industry and y_about_text/y_website). Targets active companies whose
company_name carries a raw EDGAR disambiguation suffix -- e.g. "COSTCO
WHOLESALE CORP /NEW", "TUCOWS INC /PA/" -- EDGAR's own convention for
tagging a state-of-incorporation or re-registration marker onto a company
name to disambiguate it from an older CIK of the same name. Found live
2026-09-07: 140 active companies carry this pattern.

Resolution order, best/most consumer-friendly first:
  1. yfinance longName/shortName (real, properly-cased legal name)
  2. OpenFIGI name (ALL-CAPS but suffix-free)
  3. a deterministic regex strip of the EDGAR suffix off company_name
     itself -- always succeeds, so display_name is never left null for a
     company this module was asked to fix.

Fast-then-paced discipline mirrors yfinance_industry.py, by explicit user
direction: at this population size (a few hundred at most), an unpaced
first pass alone should stay comfortably under Yahoo's real throttle
threshold (empirically ~1,800-2,000 requests in quick succession, found
live 2026-09-06 building that module) -- run paced=False first, no cleanup
pass is usually needed at this scale.
"""

import re
import time

import httpx
import psycopg
import structlog
import yfinance as yf

from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter
from scrooner_pipeline.company_master.security_type import OPENFIGI_URL, resolve_primary_tickers
from scrooner_pipeline.company_master.yfinance_industry import (
    AGGREGATE_REQUEST_INTERVAL_SECONDS,
    DEFAULT_RATE_LIMITER_LOCK_PATH,
)

logger = structlog.get_logger()

# Matches a trailing "/XX/", "/XX", or "/NEW/"-style EDGAR suffix, with or
# without a preceding space ("CSP INC /MA/" and "ITG, Inc./DE/" both
# occur in real data). 2-4 letters covers state abbreviations (MA, DE) and
# markers like NEW/OLD/DEL.
EDGAR_SUFFIX_RE = re.compile(r"\s*/[A-Za-z]{2,4}/?\s*$")

# Same corrected, evidence-based pace as security_type.py (OpenFIGI's own
# published `ratelimit-policy: 25;w=60` header).
OPENFIGI_PACE_SECONDS = 2.5

# Points at the SAME lock file yfinance_industry.py uses, so this module's
# yfinance calls correctly share Yahoo's real aggregate rate budget with any
# other job hitting yfinance concurrently -- coordination is via the shared
# file on disk, not shared Python state, so a separate instance here is
# exactly the intended cross-process pattern, not a duplicate/competing one.
_yfinance_rate_limiter = CrossProcessRateLimiter(
    max_per_second=1.0 / AGGREGATE_REQUEST_INTERVAL_SECONDS,
    lock_path=DEFAULT_RATE_LIMITER_LOCK_PATH,
)


def strip_edgar_suffix(name: str) -> str:
    return EDGAR_SUFFIX_RE.sub("", name).strip()


def _yfinance_name(ticker: str, paced: bool) -> str | None:
    if paced:
        _yfinance_rate_limiter.wait()
    try:
        info = yf.Ticker(ticker).get_info()
    except Exception as e:  # yfinance's own failures are not typed consistently
        logger.warning("display_name.yfinance_fetch_failed", ticker=ticker, error=str(e))
        return None
    name = info.get("longName") or info.get("shortName")
    return name.strip() if name else None


def _openfigi_name(ticker: str) -> str | None:
    time.sleep(OPENFIGI_PACE_SECONDS)
    try:
        response = httpx.post(
            OPENFIGI_URL, json=[{"idType": "TICKER", "idValue": ticker, "exchCode": "US"}], timeout=15.0
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("display_name.openfigi_fetch_failed", ticker=ticker, error=str(e))
        return None
    data = response.json()[0].get("data")
    if not data:
        return None
    name = data[0].get("name")
    return name.strip() if name else None


def resolve_display_name(ticker: str | None, company_name: str, paced: bool = True) -> tuple[str, str]:
    """Returns (display_name, source). Always returns a real name --
    the suffix-strip fallback guarantees this never leaves a company
    without a usable display name, unlike y_industry's honest-null design
    (that problem has genuine "no data exists" cases; this one doesn't --
    company_name always has SOME real name to clean up)."""
    if ticker:
        name = _yfinance_name(ticker, paced=paced)
        if name:
            return name, "yfinance"
        name = _openfigi_name(ticker)
        if name:
            return name, "openfigi"
    return strip_edgar_suffix(company_name), "suffix_stripped"


def update_display_names(
    conn: psycopg.Connection, ciks: set[str], paced: bool = True, force: bool = False
) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik, company_name, display_name from core.company where cik = any(%s)",
            (sorted(ciks),),
        )
        rows = cur.fetchall()

    target = [(cid, cik, name) for cid, cik, name, existing in rows if force or existing is None]
    stats = {
        "considered": len(rows),
        "skipped_already_resolved": len(rows) - len(target),
        "yfinance": 0,
        "openfigi": 0,
        "suffix_stripped": 0,
    }
    if not target:
        logger.info("display_name.done", **stats)
        return stats

    ticker_by_cik = resolve_primary_tickers(conn, {cik for _, cik, _ in target})

    updates = []
    for company_id, cik, company_name in target:
        display_name, source = resolve_display_name(ticker_by_cik.get(cik), company_name, paced=paced)
        stats[source] += 1
        updates.append({"company_id": company_id, "display_name": display_name, "source": source})

    with conn.cursor() as cur:
        cur.executemany(
            "update core.company set display_name = %(display_name)s, "
            "display_name_source = %(source)s, display_name_updated_at = now() "
            "where id = %(company_id)s",
            updates,
        )
    conn.commit()

    logger.info("display_name.done", **stats)
    return stats
