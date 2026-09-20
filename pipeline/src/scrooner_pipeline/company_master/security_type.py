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
from datetime import datetime, timezone

import httpx
import psycopg
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"
# "REIT" and "MLP" added 2026-09-06, same "verify live, then widen" discipline
# as the original ADR addition: chasing why 782 of 928 companies missing
# yfinance sector/industry data had NO ticker resolved at all (root cause:
# multiple listings, none OpenFIGI-classified, so resolve_primary_tickers()
# had nothing to pick from) surfaced that real, well-known operating
# companies -- Global Net Lease, Public Storage, Hudson Pacific Properties,
# Enterprise Products Partners -- classify as "REIT"/"MLP" under OpenFIGI,
# never "Common Stock", even though Yahoo (and every other market-data
# source) tracks them as ordinary tradeable primary securities. An 80-company
# live sample of this same population: 58 Common Stock, 7 ETP (real
# funds/ETFs, correctly NOT added here), 6 REIT, 1 Equity WRT (a warrant,
# correctly NOT added here) -- REIT/MLP were the only two real gaps.
#
# "Tracking Stk" and "Ltd Part" added 2026-09-06, same discipline, chasing
# the *next* layer of the same root cause: Liberty Media Corp (FWONA/FWONK)
# has NO separate common-stock ticker at all -- its tracking stocks (each
# tracking a specific business, e.g. Formula One) ARE its only class of
# stock, same for Liberty Broadband; Empire State Realty OP, L.P. and
# Restaurant Brands International Limited Partnership are real, large
# operating businesses trading as LP units, not passive investment vehicles.
# Confirmed live before adding: unlike ETP/Equity WRT/Right/Unit (correctly
# still excluded -- funds and SPAC-merger-artifact securities with no real
# underlying business), both of these types are a company's genuine primary
# tradeable equity, not a derivative/secondary instrument.
PRIMARY_SECURITY_TYPES = {"Common Stock", "ADR", "REIT", "MLP", "Tracking Stk", "Ltd Part"}

# Confirmed live 2026-08-17: unauthenticated OpenFIGI's real per-minute
# burst limit is much tighter than the ~5,000/day headline figure
# suggests -- a 0.3s pace (200/min) hit real HTTP 429s; 1.5s (40/min) was
# believed safe at golden-10 scale but silently wasn't. Corrected 2026-09-06,
# with real evidence this time instead of an empirical guess: a live 429
# response's own headers give the exact policy -- `ratelimit-policy: 25;w=60`
# (25 requests per 60 seconds). 1.5s pace is 40 req/min, 60% over that real
# ceiling -- explains why a ~2,300-listing run stalled for minutes with zero
# progress (burning the retry budget on sustained 429s, not a hang). Fixed to
# 2.5s (24 req/min), just under the published limit.
REQUEST_INTERVAL_SECONDS = 2.5
COMMIT_EVERY = 25


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


def _try_classify(client: httpx.Client, ticker: str) -> tuple[str | None, str | None]:
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


def _classify_ticker(client: httpx.Client, ticker: str) -> tuple[str | None, str | None]:
    """Returns (security_type, name) or (None, None) if OpenFIGI has no
    match under a plain US exchCode query -- inconclusive, not negative.

    Slash fallback added 2026-09-06: OpenFIGI doesn't recognize the SEC/
    EDGAR hyphenated share-class ticker format at all (confirmed live --
    "BRK-A" is NO_MATCH, "BRK/A" is a real "Common Stock" hit). This is a
    real, common pattern for dual/multi-class common stock (Berkshire
    Hathaway's BRK-A/BRK-B among them), not just preferred shares -- and it
    was the reason `resolve_primary_tickers()` returned nothing for
    Berkshire at all despite both listings existing. Confirmed live this
    can't produce a false positive: genuine preferred/unit/warrant tickers
    (e.g. "GNL-PE") still correctly return NO_MATCH under the slash form
    too, so trying it only ever helps, never wrongly classifies something
    that was correctly inconclusive."""
    security_type, name = _try_classify(client, ticker)
    if security_type is None and "-" in ticker:
        time.sleep(REQUEST_INTERVAL_SECONDS)  # the fallback call itself also spends rate-limit budget
        security_type, name = _try_classify(client, ticker.replace("-", "/"))
    return security_type, name


def update_security_types(conn: psycopg.Connection, ciks: set[str], force: bool = False) -> dict:
    """Resumable as of 2026-09-06 (previously a single end-of-run commit with
    no skip logic -- fine at golden-10 scale, a real risk at the ~1,000-listing
    scale this now runs at: killing the job partway lost everything). Skips
    listings that already have a security_type unless force=True, and commits
    every COMMIT_EVERY listings so a rerun only pays for what's left."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select l.id, l.ticker, l.security_type
            from core.listing l join core.company c on c.id = l.company_id
            where c.cik = any(%s) and l.effective_to is null
            """,
            (sorted(ciks),),
        )
        listings = cur.fetchall()

    target = [(lid, ticker) for lid, ticker, sec_type in listings if force or sec_type is None]
    stats = {
        "considered": len(listings),
        "skipped_already_classified": len(listings) - len(target),
        "classified": 0,
        "no_match": 0,
    }

    pending: list[dict] = []
    with httpx.Client(timeout=15.0) as client:
        for i, (listing_id, ticker) in enumerate(target):
            security_type, _name = _classify_ticker(client, ticker)
            if security_type is None:
                stats["no_match"] += 1
            else:
                pending.append({"listing_id": listing_id, "security_type": security_type})
                stats["classified"] += 1
            time.sleep(REQUEST_INTERVAL_SECONDS)  # every request consumes rate-limit budget, matched or not

            if len(pending) >= COMMIT_EVERY or i == len(target) - 1:
                if pending:
                    with conn.cursor() as cur:
                        cur.executemany(
                            "update core.listing set security_type = %(security_type)s, "
                            "security_type_source = 'openfigi' where id = %(listing_id)s",
                            pending,
                        )
                    conn.commit()
                    pending = []
                logger.info("security_type.progress", done=i + 1, total=len(target))

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
    for.

    Full-population extension (2026-08-24, doc data-moat plan): OpenFIGI
    classification was deliberately not run for the full 5,258-company
    universe (SEC's own submissions.json has no security-type field --
    OpenFIGI was only ever a disambiguation aid for companies with
    MULTIPLE listings, never a requirement for the 83% with exactly one).
    Checked live before adding this: 4,364 of 5,258 companies (83%) have
    exactly one active core.listing row -- for those, no classification
    is needed at all, since there is nothing to disambiguate. Only the
    remaining 894 (17%, genuinely multiple listings) still need
    security_type or a curated fallback; those correctly resolve to
    nothing here if unclassified, per the "never guess" principle --
    this is honest exclusion, not a bug."""
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

        cur.execute(
            """
            select c.cik, l.ticker
            from core.listing l join core.company c on c.id = l.company_id
            where c.cik = any(%s) and l.effective_to is null
            """,
            (sorted(ciks),),
        )
        all_active_by_cik: dict[str, list[str]] = {}
        for cik, ticker in cur.fetchall():
            all_active_by_cik.setdefault(cik, []).append(ticker)

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
        else:
            all_active = all_active_by_cik.get(cik, [])
            if len(all_active) == 1:
                resolved[cik] = all_active[0]
    return resolved


def persist_primary_tickers(conn: psycopg.Connection, ciks: set[str]) -> dict:
    """Writes resolve_primary_tickers()'s output directly onto
    core.company (migration 0069), added 2026-09-20 by direct user
    request: a persisted, queryable "does this company have a ticker"
    marker, instead of every consumer (sanity/yfinance_check.py,
    yfinance_financials/fetch.py, yfinance_industry.py) independently
    recomputing the same core.listing query on every single run.
    `primary_ticker IS NOT NULL` is the boolean the user asked for --
    `primary_ticker_status` carries strictly more information (WHY a
    company has none, mirroring y_industry_status's ok/not_found
    convention) than a bare boolean would, so no separate column."""
    resolved = resolve_primary_tickers(conn, ciks)
    now = datetime.now(timezone.utc)
    rows = [
        {"cik": cik, "ticker": resolved.get(cik), "status": "resolved" if cik in resolved else "no_ticker", "now": now}
        for cik in ciks
    ]
    with conn.cursor() as cur:
        cur.executemany(
            """
            update core.company
               set primary_ticker = %(ticker)s, primary_ticker_status = %(status)s, primary_ticker_updated_at = %(now)s
             where cik = %(cik)s
            """,
            rows,
        )
    conn.commit()
    return {"considered": len(ciks), "resolved": len(resolved), "no_ticker": len(ciks) - len(resolved)}
