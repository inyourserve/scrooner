"""yfinance sector/industry backfill for core.company.y_sector/y_industry --
a deliberate, explicit-user-directed exception to this project's usual
"yfinance is dev-tool only, never stored" stance (doc/planning/y-finance.md
sec. 4). See doc 02's decision register for the superseding entry and
CLAUDE.md's "Notes for skill / agent authors" for the full history (the SIC
6770/7389 catch-all fix, 2026-09-06, that led here).

Kept in a genuinely separate pair of columns from core.company.sector/
sector_reason (the SIC-range-derived taxonomy, sector_bucket.py) -- this
module never writes those, and sector_bucket.py never reads y_sector/
y_industry. Two independent classifications, not a merge.

yfinance is an unofficial scraper of Yahoo's own internal endpoints with a
real, documented rate limit that tightens with no notice (see the doc's own
research: as few as ~25 tickers in a short window can trigger
YFRateLimitError). This module is written to be paced, resumable, and
tolerant of that -- never a fast bulk job. Resolves each company's ticker via
company_master.security_type.resolve_primary_tickers() (the same real
"most companies have exactly one Common-Stock/ADR listing" mechanism Alpaca's
own price ingestion uses), not a golden-file lookup.

Multi-worker note (2026-09-06, by explicit user direction to speed up the
full-population backfill): pacing is enforced via
common.rate_limiter.CrossProcessRateLimiter, an flock-protected shared state
file -- the SAME fix already proven for the SEC client's own identical bug
(an in-process limiter only caps the rate of ONE process; N parallel workers
each pacing independently multiplies the true aggregate rate by N). Running
several `update-yfinance-industry --ciks <shard>` processes in parallel is
therefore safe against Yahoo's aggregate limit by construction -- they all
wait on the same lock file, so total throughput is bounded by
AGGREGATE_REQUEST_INTERVAL_SECONDS regardless of worker count. Shard the CIK
list across workers (disjoint --ciks chunks) so two workers never fetch the
same company; the resumability logic below makes an accidental overlap
harmless (wasted, not corrupting) but sharding avoids the waste.
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import psycopg
import structlog
import yfinance as yf
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from yfinance.exceptions import YFRateLimitError

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter
from scrooner_pipeline.company_master.security_type import resolve_primary_tickers

logger = structlog.get_logger()

# Aggregate across ALL worker processes, not per-worker -- see the module
# docstring. Raised from an initial single-process-only 2.5s (0.4 req/s) to
# 1.2s (~0.83 req/s) 2026-09-06 to trade some of the original margin for
# real speed, per explicit user direction; the original 2.5s pace ran clean
# with zero rate-limit errors across 200+ real companies before this change,
# so this is a deliberate, evidence-informed step up, not a guess from zero
# data -- if error rates climb once running, the fix is to widen this
# constant back out, not to add more workers on top of it.
AGGREGATE_REQUEST_INTERVAL_SECONDS = 1.2
DEFAULT_RATE_LIMITER_LOCK_PATH = Path(tempfile.gettempdir()) / "scrooner_yfinance_rate_limiter.lock"
COMMIT_EVERY = 25

_rate_limiter = CrossProcessRateLimiter(
    max_per_second=1.0 / AGGREGATE_REQUEST_INTERVAL_SECONDS,
    lock_path=DEFAULT_RATE_LIMITER_LOCK_PATH,
)

# Statuses stored in core.company.y_industry_status.
STATUS_OK = "ok"
STATUS_NO_DATA = "no_data"  # real ticker, Yahoo has no sector/industry for it
STATUS_NOT_FOUND = "not_found"  # Yahoo has no quote at all for this ticker
STATUS_ERROR = "error"  # transient failure -- retried on the next run

# A resumed run only re-attempts these; STATUS_OK/STATUS_NO_DATA are terminal
# unless force=True, so re-running never re-spends budget on companies
# already resolved.
RETRYABLE_STATUSES = (None, STATUS_ERROR)


def _fetch_info_once(ticker: str, paced: bool) -> dict:
    if paced:
        _rate_limiter.wait()
    return yf.Ticker(ticker).get_info()


@retry(
    retry=retry_if_exception_type(YFRateLimitError),
    stop=stop_after_attempt(3),
    wait=wait_fixed(60),
    reraise=True,
)
def _fetch_info_paced_with_retry(ticker: str) -> dict:
    return _fetch_info_once(ticker, paced=True)


def _fetch_info(ticker: str, paced: bool = True) -> dict:
    if paced:
        # Patient: worth waiting 60s and retrying up to 3x, since pacing
        # already means requests are rare enough that a hit is likely
        # transient, not sustained throttling.
        return _fetch_info_paced_with_retry(ticker)
    # Unpaced "try fast first" mode: no retry at all. A rate-limit hit here
    # fails immediately to STATUS_ERROR so the loop keeps moving at full
    # speed onto the next ticker -- retrying with a 60s wait would defeat
    # the entire point of an unthrottled pass. Cleanup happens in a later
    # paced=True run over whatever's left in STATUS_ERROR.
    return _fetch_info_once(ticker, paced=False)


def _classify(ticker: str, paced: bool = True) -> tuple[str | None, str | None, str | None, str | None, str]:
    """Returns (sector, industry, about_text, website, status). paced=False
    skips the shared rate limiter AND the rate-limit retry entirely -- an
    explicit, user-directed "try fast first" pass: run unthrottled, let
    whatever gets rate-limited land in STATUS_ERROR immediately, then
    resume with paced=True (the default, safe path) to clean up only the
    stragglers. Never use paced=False for a from-scratch full-population
    run without an intended paced cleanup pass after it.

    about_text/website (2026-09-06, explicit user direction) are read from
    the SAME get_info() payload as sector/industry -- longBusinessSummary
    and website are already present in it, so this adds zero new requests
    against Yahoo's own tightly-rate-limited endpoint."""
    try:
        info = _fetch_info(ticker, paced=paced)
    except YFRateLimitError:
        logger.warning("yfinance_industry.rate_limited", ticker=ticker)
        return None, None, None, None, STATUS_ERROR
    except Exception as e:  # yfinance's own network/parsing failures are not typed consistently
        logger.warning("yfinance_industry.fetch_failed", ticker=ticker, error=str(e))
        return None, None, None, None, STATUS_ERROR

    if not info or info.get("quoteType") is None:
        return None, None, None, None, STATUS_NOT_FOUND

    sector = info.get("sector")
    industry = info.get("industry")
    about_text = info.get("longBusinessSummary")
    website = info.get("website")
    if sector is None and industry is None and about_text is None and website is None:
        return None, None, None, None, STATUS_NO_DATA
    return sector, industry, about_text, website, STATUS_OK


def update_yfinance_industry(
    conn: psycopg.Connection, ciks: set[str], force: bool = False, paced: bool = True
) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik, y_industry_status from core.company where cik = any(%s)",
            (sorted(ciks),),
        )
        rows = cur.fetchall()

    by_cik = {cik: (company_id, status) for company_id, cik, status in rows}
    target_ciks = {
        cik
        for cik in ciks
        if cik in by_cik and (force or by_cik[cik][1] in RETRYABLE_STATUSES)
    }

    stats: dict[str, int] = {
        "considered": len(ciks),
        "no_company": len([c for c in ciks if c not in by_cik]),
        "skipped_already_resolved": len(ciks) - len(target_ciks) - len([c for c in ciks if c not in by_cik]),
        STATUS_OK: 0,
        STATUS_NO_DATA: 0,
        STATUS_NOT_FOUND: 0,
        STATUS_ERROR: 0,
    }
    if not target_ciks:
        logger.info("yfinance_industry.done", **stats)
        return stats

    ticker_by_cik = resolve_primary_tickers(conn, target_ciks)

    pending: list[dict] = []
    for i, cik in enumerate(sorted(target_ciks)):
        company_id, _ = by_cik[cik]
        ticker = ticker_by_cik.get(cik)
        if ticker is None:
            stats[STATUS_NOT_FOUND] += 1
            pending.append(
                {
                    "company_id": company_id, "sector": None, "industry": None,
                    "about_text": None, "website": None, "status": STATUS_NOT_FOUND,
                }
            )
        else:
            sector, industry, about_text, website, status = _classify(ticker, paced=paced)
            stats[status] += 1
            pending.append(
                {
                    "company_id": company_id, "sector": sector, "industry": industry,
                    "about_text": about_text, "website": website, "status": status,
                }
            )

        if len(pending) >= COMMIT_EVERY or i == len(target_ciks) - 1:
            # Found live 2026-09-06: a long-running loop with slow/rate-
            # limited yfinance fetches between writes can leave this
            # connection idle long enough for Supabase's pooler to drop it
            # (the same class of "server closed the connection
            # unexpectedly" issue this project has hit before with other
            # long-running batch jobs). _write_batch reconnects once and
            # returns the live connection to use from here on, rather than
            # losing this whole batch's already-fetched (rate-limited!)
            # results and crashing the entire remaining population.
            conn = _write_batch(conn, pending)
            logger.info("yfinance_industry.progress", done=i + 1, total=len(target_ciks))
            pending = []

    logger.info("yfinance_industry.done", **stats)
    return stats


_UPDATE_SQL = """
    update core.company
    set y_sector = %(sector)s,
        y_industry = %(industry)s,
        y_about_text = %(about_text)s,
        y_website = %(website)s,
        y_industry_status = %(status)s,
        y_industry_updated_at = %(updated_at)s
    where id = %(company_id)s
"""


def _write_batch(conn: psycopg.Connection, rows: list[dict]) -> psycopg.Connection:
    """Returns the connection to keep using -- normally the same one
    passed in, but a fresh reconnect if the original was found dead (see
    the call site's own comment for why this happens on a long-running
    fetch loop). The caller must reassign its own `conn` variable to this
    return value, or a reconnect here won't actually help subsequent
    batches."""
    if not rows:
        return conn
    now = datetime.now(timezone.utc)
    params = [{**row, "updated_at": now} for row in rows]
    try:
        with conn.cursor() as cur:
            cur.executemany(_UPDATE_SQL, params)
        conn.commit()
        return conn
    except psycopg.OperationalError:
        logger.warning("yfinance_industry.connection_dropped_reconnecting", rows=len(rows))
        fresh_conn = psycopg.connect(settings.database_url)
        with fresh_conn.cursor() as cur:
            cur.executemany(_UPDATE_SQL, params)
        fresh_conn.commit()
        return fresh_conn
