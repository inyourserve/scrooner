"""Insider Ownership & Transactions aggregate summary
(doc/scoping/insider_info.md), built 2026-08-29. Pure computation over
core.insider_transaction (Stage 2, already fully populated across the
full ~5,160-company population -- Form 4, last 12 months) -- no new SEC
fetches, no dependency on Stage 3/4/mutual-fund work in progress
elsewhere.

Writes a precomputed summary (db/migrations/0025_insider_ownership_summary.sql --
renumbered from an original 0024 after a real concurrent-session collision:
another session's own institutional_ownership_summary work independently
claimed 0024 for a different table at nearly the same timestamp; no DB
conflict resulted since both created distinct, additively-created tables,
but the filename was renumbered to keep migration numbers unique)
rather than exposing a view: a live company-page load recomputing 3
rolling-window aggregates per request across a 500K+-row table is real,
avoidable query cost -- confirmed live before choosing this shape (a
single-company, all-rows fetch for AAPL, its heaviest real case at 6,803
rows, took ~84ms; batching that per-company query across ~5,160 companies
is a few minutes of batch-job time, not a per-page-load cost).

One query per company loads ALL of that company's insider_transaction
rows (already bounded to the trailing 12 months by insider.py's own
MIN_FILING_DATE), then every aggregate -- current ownership %, and each
of the 3, 6, 12-month rolling windows -- is computed in pure Python over
that one in-memory list. This is deliberately NOT 3 separate windowed SQL
queries per company: the 12-month window is a superset of 6 and 3 months,
so slicing in Python after one fetch avoids the same "one round trip per
candidate" shape pipeline/CLAUDE.md already flags as a recurring bug
pattern (Normalizer Day 7's N+1, restatements.py's 2026-08-26 repeat).

Current insider ownership % reuses mapper/price_metrics.py's EXACT
shares_outstanding resolution (instant fact + cover-page fallback for
Block/Reddit-style multi-class gaps) -- so this can never silently
disagree with how shares_outstanding is resolved for Market Cap or
Institutional Ownership % (mapper/expanded_metrics.py's own
institutional_ownership_pct, doc's explicit requirement). The numerator
is the sum of shares_owned_following from each unique reporting owner's
OWN most recent transaction (never summed across all of an owner's own
rows -- shares_owned_following is already a running post-transaction
balance per SEC's own Form 4 schema, so summing every row would multiply-
count one person's holding by their own transaction count).

Reporting owners are deduplicated by reporting_owner_cik when present,
falling back to reporting_owner_name only when it's genuinely absent --
mirrors the same "prefer a stable identifier, fall back to name" caution
already documented for institutional 13F filer dedup (apps/site's
getTopInstitutionalHolders/expanded_metrics.py's own
_institutional_ownership_shares), just applied to insiders instead of
institutions.

transaction_classification is NOT a stored column -- it's a pure function
of transaction_code (ownership/transaction_codes.py), always computed on
read from the single already-stored source column, so it can never drift
out of sync with a separately-cached label. apps/site's own TypeScript
layer, when this renders on the company page, should port that same
mapping rather than re-derive it independently (same cross-language
"one source of truth for a classification rule" discipline already kept
for the 13F filer-dedup SQL).
"""

import calendar
from datetime import date, timedelta
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.mapper.price_metrics import _latest_instant_fact, _load_shares_outstanding_fallback

logger = structlog.get_logger()

WINDOW_MONTHS = (3, 6, 12)


def _months_ago(months: int, from_date: date | None = None) -> date:
    """Real calendar-month subtraction (not a fixed day-count
    approximation) -- clamps the day-of-month to the target month's own
    length (e.g. Aug 31 minus 6 months -> Feb 28/29), stdlib only."""
    anchor = from_date or date.today()
    total_months = anchor.year * 12 + (anchor.month - 1) - months
    year, month0 = divmod(total_months, 12)
    month = month0 + 1
    day = min(anchor.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _owner_key(row: dict) -> str:
    return row["reporting_owner_cik"] or row["reporting_owner_name"]


def _load_concept_id(conn: psycopg.Connection, name: str) -> int | None:
    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (name,))
        row = cur.fetchone()
        return row[0] if row else None


def _load_transactions_for_company(conn: psycopg.Connection, company_id: int) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, reporting_owner_cik, reporting_owner_name, transaction_date, filing_date,
                   transaction_code, shares, price_per_share, shares_owned_following
            from core.insider_transaction
            where company_id = %s
            """,
            (company_id,),
        )
        columns = [d.name for d in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def _resolve_shares_outstanding(
    conn: psycopg.Connection, company_id: int, concept_id: int | None
) -> tuple[Decimal, list[int]] | None:
    hit = _latest_instant_fact(conn, company_id, concept_id) if concept_id is not None else None
    if hit is not None:
        return hit[0], hit[1]
    return _load_shares_outstanding_fallback(conn, company_id)


def compute_ownership_pct(rows: list[dict], shares_outstanding: Decimal | None) -> dict:
    """Pure function: rows -> {ownership_pct, shares_owned_by_insiders,
    distinct_insiders_count, is_null_reason}. Sorts each owner's rows by
    (transaction_date, filing_date, id) -- transaction_date can be NULL
    for a real minority of malformed filings (insider.py's own _date()
    docstring); falling back to filing_date, then the row's own
    identity-column id, keeps "most recent" deterministic even then."""
    latest_by_owner: dict[str, dict] = {}
    for row in rows:
        key = _owner_key(row)
        if key is None:
            continue
        sort_key = (row["transaction_date"] or date.min, row["filing_date"] or date.min, row["id"])
        existing = latest_by_owner.get(key)
        if existing is None or sort_key > existing["_sort_key"]:
            latest_by_owner[key] = {**row, "_sort_key": sort_key}

    shares_owned_by_insiders = Decimal(0)
    distinct_insiders_count = 0
    for latest in latest_by_owner.values():
        if latest["shares_owned_following"] is not None:
            shares_owned_by_insiders += latest["shares_owned_following"]
            distinct_insiders_count += 1

    if distinct_insiders_count == 0:
        return {
            "ownership_pct": None,
            "shares_owned_by_insiders": None,
            "distinct_insiders_count": 0,
            "is_null_reason": "missing:shares_owned_following",
        }
    if shares_outstanding is None:
        return {
            "ownership_pct": None,
            "shares_owned_by_insiders": shares_owned_by_insiders,
            "distinct_insiders_count": distinct_insiders_count,
            "is_null_reason": "missing:shares_outstanding",
        }
    if shares_outstanding == 0:
        return {
            "ownership_pct": None,
            "shares_owned_by_insiders": shares_owned_by_insiders,
            "distinct_insiders_count": distinct_insiders_count,
            "is_null_reason": "zero_denominator",
        }
    return {
        "ownership_pct": shares_owned_by_insiders / shares_outstanding,
        "shares_owned_by_insiders": shares_owned_by_insiders,
        "distinct_insiders_count": distinct_insiders_count,
        "is_null_reason": None,
    }


CLUSTER_WINDOW_DAYS = 7
CLUSTER_LOOKBACK_MONTHS = 12


def compute_cluster_signal(rows: list[dict], window_days: int = CLUSTER_WINDOW_DAYS, as_of: date | None = None) -> dict:
    """Pure function: rows -> {cluster_buy_max_insiders, cluster_buy_window_start,
    cluster_buy_window_end}. doc/audit/2026-08-29_ownership_insider_data_audit.md's
    #3 "missing" finding: "multiple insiders buying in the same short
    window is one of the most reliable documented insider signals,
    stronger than any single transaction."

    Finds the largest number of DISTINCT reporting owners who each placed
    at least one open-market buy (transaction_code 'P') with a
    transaction_date falling inside some single `window_days`-day span,
    within the trailing CLUSTER_LOOKBACK_MONTHS (12) months of `as_of`.

    This function applies its OWN recency filter rather than trusting
    `rows` to already be scoped -- a real, live-checked finding
    (2026-08-29): `_load_transactions_for_company`'s own docstring claims
    core.insider_transaction is "already bounded to the trailing 12
    months by insider.py's own MIN_FILING_DATE", but checking the live
    table found 47% of all rows have a filing_date older than 12 months
    (oldest: 2003), plus one malformed transaction_date ("0015-11-11",
    a real year-digit parsing artifact). `compute_window_summary` above
    already defends against this with its own `_months_ago` cutoff (and
    apps/site's `getRecentInsiderTransactions` has its own SQL-level date
    filter) -- this function needed the same defense, not a trust of the
    docstring's claim. Without it, a company with no genuinely recent
    buying could surface a decades-old coincidence as if it were a live
    signal, which is worse than showing no signal at all.

    Classic two-pointer sliding window over buy dates sorted ascending:
    advance the window's left edge whenever its span would exceed
    `window_days`, tracking the distinct-owner count at each right-edge
    position -- O(n) rather than checking every pair of transactions.
    Ties (multiple windows reaching the same max count) keep the FIRST
    one found (earliest) -- a deterministic, arbitrary-but-stable
    tiebreak, same discipline as every other "pick one of several
    equally-valid answers" case in this project (doc 04's determinism
    requirement).

    NULL (not 0) when a company has zero open-market buys at all in the
    window -- "we checked and found no cluster" (0) is a different,
    stronger claim than "there was nothing to check," the same
    null-vs-zero distinction insider.py's own zero_debt flag already
    documents elsewhere in this project.
    """
    cutoff = _months_ago(CLUSTER_LOOKBACK_MONTHS, as_of)
    buys = sorted(
        (
            (row["transaction_date"], _owner_key(row))
            for row in rows
            if row["transaction_code"] == "P"
            and row["transaction_date"] is not None
            and row["transaction_date"] >= cutoff
            and _owner_key(row) is not None
        ),
        key=lambda pair: pair[0],
    )
    if not buys:
        return {"cluster_buy_max_insiders": None, "cluster_buy_window_start": None, "cluster_buy_window_end": None}

    best_count = 0
    best_start: date | None = None
    best_end: date | None = None
    left = 0
    max_span = timedelta(days=window_days - 1)
    for right in range(len(buys)):
        while buys[right][0] - buys[left][0] > max_span:
            left += 1
        distinct_owners = len({owner for _d, owner in buys[left : right + 1]})
        if distinct_owners > best_count:
            best_count = distinct_owners
            best_start = buys[left][0]
            best_end = buys[right][0]

    return {
        "cluster_buy_max_insiders": best_count,
        "cluster_buy_window_start": best_start,
        "cluster_buy_window_end": best_end,
    }


def compute_window_summary(rows: list[dict], window_months: int, as_of: date | None = None) -> dict:
    """Pure function: rows (already loaded for one company) -> one
    window's aggregate dict. Open-market buys/sells only (transaction_code
    'P'/'S' respectively per doc's own scope -- grants/exercises/gifts/tax
    disposals are display classifications, not counted as "buying" or
    "selling" volume). Sums/counts are always real integers/decimals (0 is
    a true, meaningful answer for a company with Form 4 data but no
    matching transactions in the window -- never a null-reason case, since
    the underlying data already covers the full window for every company
    this runs against). Largest purchase/sale are genuinely NULL when no
    such transaction exists in the window."""
    cutoff = _months_ago(window_months, as_of)
    in_window = [r for r in rows if r["transaction_date"] is not None and r["transaction_date"] >= cutoff]

    buys = [r for r in in_window if r["transaction_code"] == "P"]
    sells = [r for r in in_window if r["transaction_code"] == "S"]

    shares_bought = sum((r["shares"] for r in buys if r["shares"] is not None), Decimal(0))
    shares_sold = sum((r["shares"] for r in sells if r["shares"] is not None), Decimal(0))

    def _priced_value(r: dict) -> Decimal | None:
        if r["shares"] is None or r["price_per_share"] is None:
            return None
        return r["shares"] * r["price_per_share"]

    buy_values = [(r, _priced_value(r)) for r in buys]
    buy_values = [(r, v) for r, v in buy_values if v is not None]
    sell_values = [(r, _priced_value(r)) for r in sells]
    sell_values = [(r, v) for r, v in sell_values if v is not None]

    buy_dollar_volume = sum((v for _r, v in buy_values), Decimal(0))
    sell_dollar_volume = sum((v for _r, v in sell_values), Decimal(0))

    insiders_buying_count = len({_owner_key(r) for r in buys if _owner_key(r) is not None})
    insiders_selling_count = len({_owner_key(r) for r in sells if _owner_key(r) is not None})

    def _largest(values: list[tuple[dict, Decimal]], prefix: str) -> dict:
        if not values:
            return {
                f"largest_{prefix}_owner_name": None, f"largest_{prefix}_date": None,
                f"largest_{prefix}_shares": None, f"largest_{prefix}_price": None, f"largest_{prefix}_value": None,
            }
        row, value = max(values, key=lambda pair: pair[1])
        return {
            f"largest_{prefix}_owner_name": row["reporting_owner_name"],
            f"largest_{prefix}_date": row["transaction_date"],
            f"largest_{prefix}_shares": row["shares"],
            f"largest_{prefix}_price": row["price_per_share"],
            f"largest_{prefix}_value": value,
        }

    result = {
        "window_months": window_months,
        "shares_bought": shares_bought,
        "shares_sold": shares_sold,
        "buy_dollar_volume": buy_dollar_volume,
        "sell_dollar_volume": sell_dollar_volume,
        "insiders_buying_count": insiders_buying_count,
        "insiders_selling_count": insiders_selling_count,
    }
    result.update(_largest(buy_values, "purchase"))
    result.update(_largest(sell_values, "sale"))
    return result


def update_insider_summary_for_company(conn: psycopg.Connection, company_id: int, shares_outstanding_concept_id: int | None) -> dict:
    rows = _load_transactions_for_company(conn, company_id)
    shares_out_hit = _resolve_shares_outstanding(conn, company_id, shares_outstanding_concept_id)
    shares_outstanding = shares_out_hit[0] if shares_out_hit else None

    ownership = compute_ownership_pct(rows, shares_outstanding)
    windows = [compute_window_summary(rows, months) for months in WINDOW_MONTHS]
    cluster = compute_cluster_signal(rows)

    with conn.cursor() as cur:
        cur.execute("delete from core.insider_ownership_summary where company_id = %s", (company_id,))
        cur.execute(
            """
            insert into core.insider_ownership_summary
                (company_id, ownership_pct, shares_owned_by_insiders, shares_outstanding,
                 distinct_insiders_count, is_null_reason,
                 cluster_buy_max_insiders, cluster_buy_window_start, cluster_buy_window_end)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                company_id, ownership["ownership_pct"], ownership["shares_owned_by_insiders"],
                shares_outstanding, ownership["distinct_insiders_count"], ownership["is_null_reason"],
                cluster["cluster_buy_max_insiders"], cluster["cluster_buy_window_start"], cluster["cluster_buy_window_end"],
            ),
        )
        cur.execute("delete from core.insider_window_summary where company_id = %s", (company_id,))
        cur.executemany(
            """
            insert into core.insider_window_summary
                (company_id, window_months, shares_bought, shares_sold, buy_dollar_volume, sell_dollar_volume,
                 insiders_buying_count, insiders_selling_count,
                 largest_purchase_owner_name, largest_purchase_date, largest_purchase_shares,
                 largest_purchase_price, largest_purchase_value,
                 largest_sale_owner_name, largest_sale_date, largest_sale_shares,
                 largest_sale_price, largest_sale_value)
            values
                (%(company_id)s, %(window_months)s, %(shares_bought)s, %(shares_sold)s, %(buy_dollar_volume)s, %(sell_dollar_volume)s,
                 %(insiders_buying_count)s, %(insiders_selling_count)s,
                 %(largest_purchase_owner_name)s, %(largest_purchase_date)s, %(largest_purchase_shares)s,
                 %(largest_purchase_price)s, %(largest_purchase_value)s,
                 %(largest_sale_owner_name)s, %(largest_sale_date)s, %(largest_sale_shares)s,
                 %(largest_sale_price)s, %(largest_sale_value)s)
            """,
            [{**w, "company_id": company_id} for w in windows],
        )
        conn.commit()

    return {
        "transactions_considered": len(rows),
        "ownership_pct": ownership["ownership_pct"],
        "windows_written": len(windows),
    }


def update_insider_summary(conn: psycopg.Connection, ciks: set[str] | None) -> dict:
    """Default (ciks=None) runs against every company that already has ANY
    core.insider_transaction row -- deliberately NOT the golden-10 default
    the other 4 ownership CLI commands use. The underlying data is already
    fully populated across ~5,160 companies with zero new SEC fetches
    needed, so there's no reason to hold this stage back the way
    Institutional/Mutual-Fund ownership currently must (doc's own
    instruction).

    Opens a FRESH connection per company (via get_connection(), imported
    lazily below to avoid a circular import at module load time) rather
    than reusing the caller's `conn` for the whole run -- found live
    2026-08-29 running this against the full ~4,305-company population: a
    single shared connection held open across the entire batch hit a real
    dropped-connection failure partway through (499/4,305 done, no
    traceback surfaced -- structlog's buffered output was lost with the
    connection), losing nothing already committed but aborting every
    company after it. This mirrors ownership/insider.py's own
    `_run_company_with_timeout`, which already gives each company its own
    connection for exactly this reason ("an abandoned...connection never
    touches the connection the main loop keeps using for every other
    company") -- same fix, same rationale, applied here. The caller's
    `conn` is still used for the cheap one-time lookups above (company
    list, concept id) since those are a single fast round trip each, not
    the multi-minute-batch shape that motivated the per-company change."""
    from scrooner_pipeline.db.connection import get_connection

    with conn.cursor() as cur:
        if ciks:
            cur.execute(
                """
                select distinct c.cik, c.id
                from core.company c
                join core.insider_transaction it on it.company_id = c.id
                where c.cik = any(%s)
                """,
                (sorted(ciks),),
            )
        else:
            cur.execute(
                """
                select distinct c.cik, c.id
                from core.company c
                join core.insider_transaction it on it.company_id = c.id
                """
            )
        company_id_by_cik = dict(cur.fetchall())

    shares_outstanding_concept_id = _load_concept_id(conn, "shares_outstanding")

    totals = {"considered": 0, "ok": 0, "errored": 0, "computed_pct": 0, "null_pct": 0}
    for cik in sorted(company_id_by_cik):
        totals["considered"] += 1
        company_id = company_id_by_cik[cik]
        try:
            with get_connection() as company_conn:
                stats = update_insider_summary_for_company(company_conn, company_id, shares_outstanding_concept_id)
        except Exception:
            logger.exception("insider_summary.company_failed", cik=cik)
            totals["errored"] += 1
            continue
        totals["ok"] += 1
        if stats["ownership_pct"] is not None:
            totals["computed_pct"] += 1
        else:
            totals["null_pct"] += 1
        if totals["considered"] % 250 == 0:
            logger.info("insider_summary.progress", **totals)

    logger.info("insider_summary.done", **totals)
    return totals
