"""yfinance Full Financial Statements fetch (2026-09-08, explicit user
request): fetches yfinance's actual per-line-item QUARTERLY financial
statements (income statement, balance sheet, cash flow) -- a deeper check
than the Data Sanity Layer's `.info()`-based ratio checks (sanity/
yfinance_check.py), which only ever looks at the latest period's
aggregate ratios. This checks every available quarter's individual line
items against our own statement-table values.

yfinance is used ONLY for detection/matching -- see sanity/
tag_investigator.py's module docstring for the full "SEC EDGAR only for
fills/fixes" rule this system obeys. Nothing here ever writes a yfinance
NUMBER into core/analytics; a mismatch found by compare.py feeds into
tag_investigator.investigate() for the actual fix, which is always
sourced from a real core.fact row.

Shares the SAME CrossProcessRateLimiter lock file as yfinance_check.py/
yfinance_industry.py -- but THREE yfinance property accesses per company
(income statement, balance sheet, cash flow), each paced separately since
it's unverified whether a given yfinance version batches them into fewer
real HTTP requests under the hood -- safer to over-pace than assume.  This
is a real 3x higher per-company cost than the Data Sanity Layer's single
`.info()` call, so run this on a deliberately bounded batch, not blindly
at full-population scale before real findings justify the cost.

Real period-alignment gotcha, found live 2026-09-08: yfinance's own
quarterly statement COLUMNS are calendar quarter-ends (2026-06-30), not a
company's actual fiscal quarter-end (AAPL's real Q3 2026 ends 2026-06-27)
-- yfinance rounds to the nearest calendar quarter. compare.py's period
join uses a tolerance window (PERIOD_MATCH_TOLERANCE_DAYS), never an exact
date match.

`paced` (added 2026-09-08, same day, explicit user direction to speed up
the full-population fetch): mirrors company_master/yfinance_industry.py's
own `--no-pacing` "try fast first" idiom exactly. paced=False skips the
shared CrossProcessRateLimiter AND drops the rate-limit retry entirely --
a hit fails that one company immediately (fetch_failed, no 60s wait) so
the loop keeps moving at full speed. A later paced=True (default) run
over whatever's left un-fetched cleans up the stragglers. Never run
paced=False for a from-scratch pass without an intended paced cleanup
pass after it -- see yfinance_industry.py's own module docstring for why."""

from datetime import date, timedelta

import pandas as pd
import psycopg
import structlog
import yfinance as yf
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from yfinance.exceptions import YFRateLimitError

from scrooner_pipeline.common.config import settings
from scrooner_pipeline.common.rate_limiter import CrossProcessRateLimiter
from scrooner_pipeline.company_master.security_type import resolve_primary_tickers
from scrooner_pipeline.company_master.yfinance_industry import (
    DEFAULT_RATE_LIMITER_LOCK_PATH,
)

logger = structlog.get_logger()

AGGREGATE_REQUEST_INTERVAL_SECONDS = (
    1.2  # same shared budget as yfinance_check.py/yfinance_industry.py
)
_rate_limiter = CrossProcessRateLimiter(
    max_per_second=1.0 / AGGREGATE_REQUEST_INTERVAL_SECONDS,
    lock_path=DEFAULT_RATE_LIMITER_LOCK_PATH,
)

STATEMENT_ATTR = {
    "income_statement": "quarterly_income_stmt",
    "balance_sheet": "quarterly_balance_sheet",
    "cash_flow": "quarterly_cashflow",
}

PERIOD_MATCH_TOLERANCE_DAYS = 15


def _fetch_one_statement_once(
    ticker_obj: yf.Ticker, attr: str, paced: bool
) -> pd.DataFrame:
    if paced:
        _rate_limiter.wait()
    return getattr(ticker_obj, attr)


@retry(
    retry=retry_if_exception_type(YFRateLimitError),
    stop=stop_after_attempt(3),
    wait=wait_fixed(60),
    reraise=True,
)
def _fetch_one_statement_paced_with_retry(
    ticker_obj: yf.Ticker, attr: str
) -> pd.DataFrame:
    return _fetch_one_statement_once(ticker_obj, attr, paced=True)


def _fetch_one_statement(
    ticker_obj: yf.Ticker, attr: str, paced: bool = True
) -> pd.DataFrame:
    if paced:
        return _fetch_one_statement_paced_with_retry(ticker_obj, attr)
    # Unpaced "try fast first": no retry at all -- a rate-limit hit here
    # fails immediately (caught by fetch_and_store_statements's own
    # except YFRateLimitError) so the loop keeps moving at full speed.
    return _fetch_one_statement_once(ticker_obj, attr, paced=False)


def _fetch_all_statements(ticker: str, paced: bool = True) -> dict[str, pd.DataFrame]:
    t = yf.Ticker(ticker)
    return {
        statement_type: _fetch_one_statement(t, attr, paced)
        for statement_type, attr in STATEMENT_ATTR.items()
    }


def pick_rotation_batch(conn: psycopg.Connection, limit: int) -> list[int]:
    """Coldest-checked-first rotation (2026-09-08, added for the daily
    cron -- fetch_and_store_statements() had no rotation of its own, so
    the only way to run it against the full population was an explicit
    --company-ids list built by hand). Mirrors sanity/yfinance_check.py's
    pick_rotation_batch() exactly -- same rationale, different table
    (yfinance_statement_line.fetched_at instead of data_sanity_check.
    checked_at) since this system tracks its own recency independently."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.id
            from core.company c
            left join (
                select company_id, max(fetched_at) as last_fetched
                from analytics.yfinance_statement_line
                group by company_id
            ) y on y.company_id = c.id
            where c.status = 'active'
            order by y.last_fetched asc nulls first, c.id
            limit %s
            """,
            (limit,),
        )
        return [row[0] for row in cur.fetchall()]


def _flatten(df: pd.DataFrame) -> list[tuple[str, date, float | None]]:
    """One (line_item, period_end, value) tuple per real cell -- skips
    NaN cells (yfinance leaves a line item blank for a period it doesn't
    apply to, e.g. banks have no 'Gross Profit' row at all)."""
    rows = []
    for line_item in df.index:
        for column in df.columns:
            value = df.loc[line_item, column]
            if pd.isna(value):
                continue
            rows.append((str(line_item), column.date(), float(value)))
    return rows


def fetch_and_store_statements(
    conn: psycopg.Connection, company_ids: list[int], paced: bool = True
) -> dict:
    # "ok_but_empty" -- added 2026-09-19, real finding not yet root-caused:
    # the daily cron (GitHub Actions runner IPs) wrote ZERO new rows to
    # analytics.yfinance_statement_line for 5 straight days (2026-09-15
    # through 09-19), yet every fetch logged "ok" (no exception raised --
    # yfinance/Yahoo evidently returns an empty-but-200 response rather
    # than an error under whatever condition is triggering this). The
    # SAME tickers (AAPL, MSFT, GOOGL, JPM, NKE, XOM, KO, PG, T, WMT)
    # fetched real, non-empty quarterly statements when tested from a
    # non-GitHub-Actions IP the same day -- consistent with Yahoo Finance's
    # well-documented tendency to rate-limit/block datacenter IP ranges
    # (including GitHub Actions') more aggressively on the fundamentals/
    # quoteSummary endpoints than on `.info()` (which this cron's sibling
    # sanity/yfinance_check.py step, on the same runner, continues to
    # complete successfully every day). Not fixed here -- this counter
    # exists so the failure is visible in fetch_done's own stats instead
    # of silently blending into "ok" (indistinguishable from a real thin
    # company reporting nothing), for whoever picks this up next.
    stats = {
        "considered": len(company_ids),
        "ok": 0,
        "ok_but_empty": 0,
        "no_ticker": 0,
        "fetch_failed": 0,
        "rows_written": 0,
    }
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik from core.company where id = any(%s)", (company_ids,)
        )
        cik_by_company = dict(cur.fetchall())
    ticker_by_cik = resolve_primary_tickers(conn, set(cik_by_company.values()))

    for company_id in company_ids:
        cik = cik_by_company.get(company_id)
        ticker = ticker_by_cik.get(cik) if cik else None
        if ticker is None:
            stats["no_ticker"] += 1
            continue
        try:
            statements = _fetch_all_statements(ticker, paced=paced)
        except YFRateLimitError:
            logger.warning("yfinance_financials.rate_limited", ticker=ticker)
            stats["fetch_failed"] += 1
            continue
        except Exception as e:
            logger.warning(
                "yfinance_financials.fetch_failed", ticker=ticker, error=str(e)
            )
            stats["fetch_failed"] += 1
            continue

        rows = []
        for statement_type, df in statements.items():
            for line_item, period_end, value in _flatten(df):
                rows.append(
                    {
                        "company_id": company_id,
                        "statement_type": statement_type,
                        "frequency": "quarterly",
                        "line_item": line_item,
                        "period_end": period_end,
                        "value": value,
                    }
                )
        _write_batch(conn, rows)
        stats["ok"] += 1
        if not rows:
            stats["ok_but_empty"] += 1
        stats["rows_written"] += len(rows)

    logger.info("yfinance_financials.fetch_done", **stats)
    return stats


_UPSERT_SQL = """
    insert into analytics.yfinance_statement_line
        (company_id, statement_type, frequency, line_item, period_end, value, fetched_at)
    values (%(company_id)s, %(statement_type)s, %(frequency)s, %(line_item)s, %(period_end)s, %(value)s, now())
    on conflict (company_id, statement_type, frequency, line_item, period_end) do update
        set value = excluded.value, fetched_at = now()
"""


def _write_batch(conn: psycopg.Connection, rows: list[dict]) -> None:
    if not rows:
        return
    try:
        with conn.cursor() as cur:
            cur.executemany(_UPSERT_SQL, rows)
        conn.commit()
    except psycopg.OperationalError:
        logger.warning(
            "yfinance_financials.connection_dropped_reconnecting", rows=len(rows)
        )
        fresh_conn = psycopg.connect(settings.database_url)
        with fresh_conn.cursor() as cur:
            cur.executemany(_UPSERT_SQL, rows)
        fresh_conn.commit()
        fresh_conn.close()
