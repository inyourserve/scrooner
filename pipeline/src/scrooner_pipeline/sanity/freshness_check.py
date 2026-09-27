"""Data freshness/staleness check (doc 45 P0, 2026-09-08) -- a genuinely
NEW sanity dimension, distinct from every other check this project has
built so far. sanity/yfinance_check.py and yfinance_financials/compare.py
both ask "is the VALUE right" for whatever our latest data happens to be.
This asks a different question: "is our latest data actually current, or
has a real, already-reported quarter simply never been ingested." A
metric can be perfectly, correctly computed and still be two quarters
stale -- no existing check would catch that, since a stale value isn't
necessarily a WRONG value, just an old one presented as current.

Costs ZERO additional yfinance requests: `info['mostRecentQuarter']` is
already present in the exact same `.info()` payload sanity/
yfinance_check.py already fetches for its ratio checks -- this just reads
one more key out of a payload already in hand. Verified live against a
real AAPL value before trusting the field: `mostRecentQuarter` (a Unix
timestamp) converts to 2026-06-27, exactly matching AAPL's own real Q3
2026 fiscal period end date already stored in `core.period` -- confirms
the field means what its name says, not assumed from yfinance's own docs.

Same rule as every other 2026-09-08 system: this has nothing to "fix" in
the SEC-tag sense -- a stale finding means "go run the incremental
pipeline for this company," not a tag mapping problem. It complements
`scrooner-operations --fail-on-alert` (this project's existing pipeline-
wide freshness gate) with a company-level, INDEPENDENTLY-SOURCED signal:
operations.py knows what the pipeline thinks it last did; this knows what
an external source says has actually been reported."""

from datetime import date, timedelta

import psycopg
import structlog

logger = structlog.get_logger()

SEVERITY_OK = "ok"
SEVERITY_STALE = "stale"
SEVERITY_UNKNOWN = "unknown"

# Real quarterly cadence is ~90 days between period ends, but SEC gives
# filers up to 40/45 days after quarter-end to actually FILE a 10-Q/10-K
# (doc 07) -- a tight threshold would flag every company as "stale" for
# several weeks after every single quarter-end, which isn't a real
# problem, just normal filing lag. 120 days gives real filing lag room
# without masking a genuinely missed quarter (a true miss means we're
# behind by a FULL cycle, ~180+ days past yfinance's own reported date).
STALE_THRESHOLD_DAYS = 120


def check_freshness(
    company_id: int,
    our_latest_period_end: date | None,
    yfinance_most_recent_quarter: date | None,
) -> dict:
    """Pure, no DB access -- unit-testable in isolation."""
    if yfinance_most_recent_quarter is None or our_latest_period_end is None:
        return {
            "company_id": company_id,
            "our_latest_period_end": our_latest_period_end,
            "yfinance_most_recent_quarter": yfinance_most_recent_quarter,
            "days_stale": None,
            "severity": SEVERITY_UNKNOWN,
        }
    days_stale = (yfinance_most_recent_quarter - our_latest_period_end).days
    severity = SEVERITY_STALE if days_stale > STALE_THRESHOLD_DAYS else SEVERITY_OK
    return {
        "company_id": company_id,
        "our_latest_period_end": our_latest_period_end,
        "yfinance_most_recent_quarter": yfinance_most_recent_quarter,
        "days_stale": days_stale,
        "severity": severity,
    }


MIN_FACTS_FOR_REAL_PERIOD = 10


def load_our_latest_period_ends(
    conn: psycopg.Connection, company_ids: list[int]
) -> dict[int, date]:
    """One bulk query for the whole batch -- never a query per company,
    same discipline as every other loader in this codebase.

    Requires at least MIN_FACTS_FOR_REAL_PERIOD facts, not just "any"
    fact. Real bug found live 2026-09-08, first company checked (AAPL):
    a single-fact `instant` period (`shares_outstanding` only, dated
    2026-07-17 -- 20 days AFTER AAPL's real Q3 2026 quarter-end of
    2026-06-27) was being picked as "our latest period", when it's
    actually the well-known "shares-outstanding-as-of-10-Q-filing-date"
    cover-page snapshot this project has already documented elsewhere
    (a metadata artifact, not a new reporting period). A real quarterly
    or FY reporting period has dozens to hundreds of facts; this
    threshold cleanly separates the two without hardcoding a fragile
    "is this the specific known artifact" check.

    Written as a CTE that filters `canonical_fact` by `company_id` FIRST
    (its own indexed leading column, `canonical_fact_company_id_..._key`)
    and aggregates by `period_id` in one bounded pass -- NOT a correlated
    subquery re-evaluated per `core.period` row, which timed out live
    2026-09-08 even against a single company: `canonical_fact` has no
    index with `period_id` as a usable leading column, so `where
    cf.period_id = p.id` run once per candidate period row forces a scan
    each time against a genuinely large table (8M+ rows). Same lesson as
    every other "index the actual access pattern, don't assume a
    correlated subquery is cheap" finding already in this project's
    history, just caught before it shipped instead of after."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with period_fact_counts as (
                select period_id, count(*) as fact_count
                from analytics.canonical_fact
                where company_id = any(%(company_ids)s)
                group by period_id
            )
            select p.company_id, max(p.end_date)
            from core.period p
            join period_fact_counts pfc on pfc.period_id = p.id
            where p.company_id = any(%(company_ids)s) and p.fiscal_period is not null
              and pfc.fact_count >= %(min_facts)s
            group by p.company_id
            """,
            {"company_ids": company_ids, "min_facts": MIN_FACTS_FOR_REAL_PERIOD},
        )
        return dict(cur.fetchall())


_UPSERT_SQL = """
    insert into analytics.data_freshness_check
        (company_id, our_latest_period_end, yfinance_most_recent_quarter, days_stale, severity, checked_at)
    values (%(company_id)s, %(our_latest_period_end)s, %(yfinance_most_recent_quarter)s, %(days_stale)s, %(severity)s, now())
    on conflict (company_id) do update
        set our_latest_period_end = excluded.our_latest_period_end,
            yfinance_most_recent_quarter = excluded.yfinance_most_recent_quarter,
            days_stale = excluded.days_stale, severity = excluded.severity, checked_at = now()
"""


def write_freshness_checks(conn: psycopg.Connection, rows: list[dict]) -> None:
    if not rows:
        return
    with conn.cursor() as cur:
        cur.executemany(_UPSERT_SQL, rows)
    conn.commit()
