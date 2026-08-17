"""Stage 4a-3 -- Active/stale/unknown status inference (doc 13, Sec 4).

No EDGAR field says "delisted" -- checked directly, `category` is a
filer-size classification ("Large accelerated filer"), not a listing-status
flag. The only honest, checkable signal available without a new vendor:
how long since the company's most recent 10-K/10-Q filing_date
(core.filing, already populated by the Normalizer).

Three states, deliberately not two:
- active: a 10-K or 10-Q filed within STALE_THRESHOLD_DAYS
- stale: no qualifying filing within that window, reason unconfirmed --
  NEVER 'delisted'. This project has no data source that actually confirms
  delisting, and asserting it anyway would be exactly the wrong-but-
  plausible failure mode Mapper's Day 4 ROIC bug was fixed to prevent.
- unknown: no qualifying filing at all (nothing to judge from)

Threshold: 18 months. SEC requires quarterly (10-Q) financial reporting for
a domestic operating company, so even a company that's badly behind on
filings would need an unusual, specific reason to go this long dark while
still technically active -- a generous margin, not a tight one, chosen to
minimize false 'stale' flags rather than to catch every real gap quickly.
"""

from datetime import date, timedelta

import psycopg
import structlog

logger = structlog.get_logger()

STALE_THRESHOLD_DAYS = 18 * 30  # ~18 months, see module docstring

QUALIFYING_FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A"}


def _load_latest_filing_dates(conn: psycopg.Connection, company_ids: list[int]) -> dict[int, date | None]:
    if not company_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            """
            select company_id, max(filing_date)
            from core.filing
            where company_id = any(%s) and form = any(%s) and filing_date is not null
            group by company_id
            """,
            (company_ids, sorted(QUALIFYING_FORMS)),
        )
        return dict(cur.fetchall())


def compute_status(latest_filing_date: date | None, as_of: date) -> tuple[str, str]:
    if latest_filing_date is None:
        return "unknown", "no_qualifying_filing_on_record"
    age_days = (as_of - latest_filing_date).days
    if age_days <= STALE_THRESHOLD_DAYS:
        return "active", f"filed:{latest_filing_date.isoformat()}"
    return "stale", f"no_filing_since:{latest_filing_date.isoformat()}"


def update_status(conn: psycopg.Connection, ciks: set[str], as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    with conn.cursor() as cur:
        cur.execute("select id, cik from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = {cik: cid for cid, cik in cur.fetchall()}

    company_ids = list(company_id_by_cik.values())
    latest_by_company = _load_latest_filing_dates(conn, company_ids)

    rows = []
    stats = {"considered": 0, "active": 0, "stale": 0, "unknown": 0, "no_company": 0}
    for cik in sorted(ciks):
        stats["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            stats["no_company"] += 1
            continue
        latest = latest_by_company.get(company_id)
        status, reason = compute_status(latest, as_of)
        stats[status] += 1
        rows.append({"company_id": company_id, "status": status, "status_as_of": as_of, "status_reason": reason})

    if rows:
        with conn.cursor() as cur:
            cur.executemany(
                """
                update core.company
                   set status = %(status)s, status_as_of = %(status_as_of)s, status_reason = %(status_reason)s
                 where id = %(company_id)s
                """,
                rows,
            )
        conn.commit()

    logger.info("company_master.status.done", **stats)
    return stats
