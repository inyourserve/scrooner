"""Real security-type classification for core.listing, sourced from
OpenFIGI (free, unauthenticated), NOT Alpaca -- deliberate: Alpaca is
this project's price vendor (doc 25), and using it for identity/
classification purposes would blur that boundary. OpenFIGI was already
proven for exactly this kind of free security-metadata lookup during
Ownership Stage 4's CUSIP crosswalk (doc/learnings/form-13f-cusip-
crosswalk.md).

Why this exists: SEC's own submissions.json carries no security-type
field at all (checked live -- `tickers`/`exchanges` are the only
per-ticker arrays). A company can have many listings that are NOT its
primary common stock -- confirmed live across the full golden-10 before
writing this: JPM has 5 preferred-share classes plus 2 ETNs sharing its
CIK ("Alerian MLP Index ETNs", "Inverse VIX...ETNs"), Enbridge has 13
OTC Canadian preferred-share variants, Block has an Australian CDI
(CHESS Depositary Interest). `market_price_alpaca.py` originally worked
around this with a golden_companies.json curated-ticker stopgap; this
replaces that with a real, general classification.

One real nuance found only by checking the FULL golden-10, not a
sample: TSM's own actual working ticker classifies as "ADR" (American
Depositary Receipt), NOT "Common Stock" -- a naive Common-Stock-only
filter would have wrongly excluded the one ticker this pipeline
actually needs. `PRIMARY_SECURITY_TYPES` includes both.
"""

import time

import httpx
import psycopg
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"
PRIMARY_SECURITY_TYPES = {"Common Stock", "ADR"}

# Confirmed live 2026-08-17: unauthenticated OpenFIGI's real per-minute
# burst limit is much tighter than the ~5,000/day headline figure
# suggests -- a 0.3s pace (200/min) hit real HTTP 429s. ~1 req/1.5s
# stays comfortably under it; retry below handles any residual burst.
REQUEST_INTERVAL_SECONDS = 1.5


@retry(
    retry=lambda retry_state: isinstance(retry_state.outcome.exception(), httpx.HTTPStatusError)
    and retry_state.outcome.exception().response.status_code == 429,
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=2, max=20),
    reraise=True,
)
def _post_with_retry(client: httpx.Client, ticker: str) -> httpx.Response:
    response = client.post(OPENFIGI_URL, json=[{"idType": "TICKER", "idValue": ticker, "exchCode": "US"}])
    response.raise_for_status()
    return response


def _classify_ticker(client: httpx.Client, ticker: str) -> tuple[str | None, str | None]:
    """Returns (security_type, name) or (None, None) if OpenFIGI has no
    match under a plain US exchCode query -- inconclusive, not negative."""
    try:
        response = _post_with_retry(client, ticker)
    except httpx.HTTPError:
        logger.warning("security_type.openfigi_fetch_failed", ticker=ticker)
        return None, None
    row = response.json()[0]
    data = row.get("data")
    if not data:
        return None, None
    return data[0].get("securityType"), data[0].get("name")


def update_security_types(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            select l.id, l.ticker
            from core.listing l join core.company c on c.id = l.company_id
            where c.cik = any(%s) and l.effective_to is null
            """,
            (sorted(ciks),),
        )
        listings = cur.fetchall()

    stats = {"considered": len(listings), "classified": 0, "no_match": 0}
    rows = []
    with httpx.Client(timeout=15.0) as client:
        for listing_id, ticker in listings:
            security_type, _name = _classify_ticker(client, ticker)
            if security_type is None:
                stats["no_match"] += 1
            else:
                rows.append({"listing_id": listing_id, "security_type": security_type})
                stats["classified"] += 1
            time.sleep(REQUEST_INTERVAL_SECONDS)  # every request consumes rate-limit budget, matched or not

    if rows:
        with conn.cursor() as cur:
            cur.executemany(
                "update core.listing set security_type = %(security_type)s, security_type_source = 'openfigi' "
                "where id = %(listing_id)s",
                rows,
            )
        conn.commit()

    logger.info("security_type.done", **stats)
    return stats


def resolve_primary_tickers(
    conn: psycopg.Connection, ciks: set[str], fallback_ticker_by_cik: dict[str, str] | None = None
) -> dict[str, str]:
    """cik -> primary ticker, using the real classification above instead
    of a curated file. Confirmed live across the full golden-10 before
    trusting this as the default rule: 8 of 10 companies have exactly one
    Common-Stock/ADR-classified listing (unambiguous); 2 (Alphabet's dual
    share classes, TSM's ADR-vs-underlying-ordinary-shares) have more
    than one *legitimately valid* primary candidate, not a data error --
    `fallback_ticker_by_cik` (golden_companies.json's own curated choice)
    breaks that tie when provided, rather than picking arbitrarily. A
    company with zero classified listings yet (OpenFIGI coverage gap, or
    update-security-types hasn't run for it) also falls back, so this
    never just silently drops a company the caller expected a ticker
    for."""
    fallback_ticker_by_cik = fallback_ticker_by_cik or {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.cik, l.ticker
            from core.listing l join core.company c on c.id = l.company_id
            where c.cik = any(%s) and l.effective_to is null and l.security_type = any(%s)
            """,
            (sorted(ciks), sorted(PRIMARY_SECURITY_TYPES)),
        )
        candidates_by_cik: dict[str, list[str]] = {}
        for cik, ticker in cur.fetchall():
            candidates_by_cik.setdefault(cik, []).append(ticker)

    resolved: dict[str, str] = {}
    for cik in ciks:
        candidates = candidates_by_cik.get(cik, [])
        fallback = fallback_ticker_by_cik.get(cik)
        if len(candidates) == 1:
            resolved[cik] = candidates[0]
        elif fallback and (not candidates or fallback in candidates):
            resolved[cik] = fallback
        elif candidates:
            resolved[cik] = sorted(candidates)[0]
    return resolved
