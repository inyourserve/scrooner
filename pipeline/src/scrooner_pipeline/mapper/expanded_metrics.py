"""Expanded price/EBITDA-based metrics (doc 18 Tier A / doc 26, built
2026-08-18): Net Debt/EBITDA, EV/EBITDA, EV/Sales, PEG Ratio, Buyback
Yield, Total Shareholder Yield, Institutional Ownership %, Share Count
Dilution Trend. Separate from price_metrics.py (doc 25's
own 6 locked metrics) because these mix analytics.metric_value inputs
(ebitda, market_cap, trailing_pe, dividend_yield, eps_growth_yoy) with
canonical_fact inputs in ways calculate.py's generic per-concept engine
can't express -- same reasoning as price_metrics.py itself, one level
further removed (this module depends on price_metrics.py's OWN output
existing already; run calculate-price-metrics before this).

Net Debt/EBITDA does NOT require a real price (Net Debt and EBITDA are
both price-independent) -- computed unconditionally. EV/EBITDA, EV/Sales,
PEG, Buyback Yield, and Total Shareholder Yield all genuinely need
Market Cap, so they're null (with a real reason) for any company
price_metrics.py couldn't price.

PEG uses EPS growth as a plain percentage number (e.g. 15, not 0.15) --
the conventional PEG convention (Price/Earnings ÷ Growth Rate). Null,
not a nonsensical negative/near-zero ratio, when growth is zero or
negative -- a shrinking company's PEG isn't a meaningful valuation
signal (same "N/M" treatment doc 10's own study document already flags
as necessary for negative-denominator ratios).

Dilution (for Total Shareholder Yield) is shares outstanding now vs.
~1 year ago (same day-band tolerance periods.py itself uses for a
full-year span, 350-380 days) -- reuses the exact shares_outstanding
value (with company_master's multi-class fallback) price_metrics.py
already resolves, not a second source of truth.
"""

from datetime import date, timedelta
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error
from scrooner_pipeline.mapper.price_metrics import (
    _latest_instant_fact,
    _load_shares_outstanding_fallback,
    _load_quarterly_facts,
    _latest_quarter,
    _ttm_sum,
)

logger = structlog.get_logger()

FULL_YEAR_MIN_DAYS, FULL_YEAR_MAX_DAYS = 350, 380


def _load_concept_ids(conn: psycopg.Connection, names: set[str]) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute("select name, id from analytics.canonical_concept where name = any(%s)", (sorted(names),))
        return dict(cur.fetchall())


def _latest_metric_value(conn: psycopg.Connection, company_id: int, metric_definition_id: int) -> Decimal | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            select value from analytics.metric_value
            where company_id = %s and metric_definition_id = %s and value is not null
            order by (period_label = 'TTM') desc, period_end desc
            limit 1
            """,
            (company_id, metric_definition_id),
        )
        row = cur.fetchone()
        return row[0] if row else None


def _ebitda_ttm(conn: psycopg.Connection, company_id: int, ebitda_metric_id: int) -> Decimal | None:
    """Sum of the 4 most recent quarterly `ebitda` metric_value rows --
    same trailing-quarter idea as price_metrics.py's TTM concepts, but
    over metric_value (ebitda is a metric, not a canonical_fact concept),
    so it needs its own small loader rather than reusing _ttm_sum's
    canonical_fact-shaped input directly."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select mv.value, mv.period_end
            from analytics.metric_value mv
            where mv.company_id = %s and mv.metric_definition_id = %s
              and mv.period_label in ('Q1', 'Q2', 'Q3', 'Q4') and mv.value is not null
            order by mv.period_end desc
            limit 4
            """,
            (company_id, ebitda_metric_id),
        )
        rows = cur.fetchall()
    if len(rows) < 4:
        return None
    return sum(value for value, _end in rows)


def _shares_outstanding_now_and_1y_ago(
    conn: psycopg.Connection, company_id: int, shares_concept_id: int
) -> tuple[Decimal | None, Decimal | None]:
    now_hit = _latest_instant_fact(conn, company_id, shares_concept_id)
    if now_hit is None:
        fallback = _load_shares_outstanding_fallback(conn, company_id)
        now_value, now_end = (fallback[0], None) if fallback else (None, None)
    else:
        now_value, _fids, now_end = now_hit
    if now_value is None or now_end is None:
        return now_value, None

    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.value, p.end_date
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s and p.end_date <= %s
            order by p.end_date desc
            """,
            (company_id, shares_concept_id, now_end - timedelta(days=FULL_YEAR_MIN_DAYS)),
        )
        for value, end in cur.fetchall():
            age_days = (now_end - end).days
            if FULL_YEAR_MIN_DAYS <= age_days <= FULL_YEAR_MAX_DAYS:
                return now_value, value
    return now_value, None


def _institutional_ownership_shares(conn: psycopg.Connection, company_id: int) -> Decimal | None:
    """Sum of Form 13F holdings, deduped per filer -- exact same dedup
    rule as apps/site's getTopInstitutionalHolders (prefer the amendment
    over the original when both exist for the same filer, else latest
    filing_date), so the aggregate % and the "top holders" list on the
    company page are never inconsistent with each other."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select sum(shares) from (
                select distinct on (filer_name) shares
                from core.institutional_ownership
                where company_id = %s
                order by filer_name, is_amendment desc, filing_date desc nulls last
            ) dedup
            """,
            (company_id,),
        )
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else None


def calculate_expanded_metrics_for_company(conn: psycopg.Connection, company_id: int, metric_ids: dict[str, int], concept_ids: dict[str, int]) -> dict:
    # These are all "as of now" composite metrics (some price-dependent,
    # some not) -- anchored on today's date, same "as-of" framing
    # price_metrics.py uses its own price_date for. metric_value's
    # period_start/period_end are NOT NULL (found live: the first
    # version passed None and hit a real constraint violation).
    as_of = date.today()

    def _row(metric_name: str, value: Decimal | None, reason: str | None) -> dict:
        return {
            "company_id": company_id,
            "metric_definition_id": metric_ids[metric_name],
            "period_start": as_of,
            "period_end": as_of,
            "period_label": "TTM",
            "value": value,
            "is_null_reason": reason,
            "source_fact_ids": None,
        }

    rows: list[dict] = []

    total_debt_hit = _latest_instant_fact(conn, company_id, concept_ids["total_debt"]) if "total_debt" in concept_ids else None
    cash_hit = _latest_instant_fact(conn, company_id, concept_ids["cash_and_equivalents"]) if "cash_and_equivalents" in concept_ids else None
    ebitda_ttm = _ebitda_ttm(conn, company_id, metric_ids["ebitda"])
    market_cap = _latest_metric_value(conn, company_id, metric_ids["market_cap"])

    # Net Debt / EBITDA -- price-independent
    if total_debt_hit is None or cash_hit is None:
        rows.append(_row("net_debt_ebitda", None, "missing:total_debt_or_cash"))
    elif ebitda_ttm is None:
        rows.append(_row("net_debt_ebitda", None, "missing:ebitda_ttm"))
    elif ebitda_ttm == 0:
        rows.append(_row("net_debt_ebitda", None, "zero_denominator"))
    else:
        net_debt = total_debt_hit[0] - cash_hit[0]
        rows.append(_row("net_debt_ebitda", net_debt / ebitda_ttm, None))

    # Institutional Ownership % -- price-independent, needs shares_outstanding
    # (same instant-fact + cover-page-fallback resolution price_metrics.py
    # already uses for shares_outstanding elsewhere in this module).
    inst_shares = _institutional_ownership_shares(conn, company_id)
    shares_out_value = None
    if "shares_outstanding" in concept_ids:
        shares_out_hit = _latest_instant_fact(conn, company_id, concept_ids["shares_outstanding"])
        shares_out_value = shares_out_hit[0] if shares_out_hit else None
        if shares_out_value is None:
            fallback = _load_shares_outstanding_fallback(conn, company_id)
            shares_out_value = fallback[0] if fallback else None
    if inst_shares is None:
        rows.append(_row("institutional_ownership_pct", None, "missing:institutional_holdings"))
    elif shares_out_value is None:
        rows.append(_row("institutional_ownership_pct", None, "missing:shares_outstanding"))
    elif shares_out_value == 0:
        rows.append(_row("institutional_ownership_pct", None, "zero_denominator"))
    else:
        rows.append(_row("institutional_ownership_pct", inst_shares / shares_out_value, None))

    # Share Count Dilution Trend -- price-independent, reused below for
    # Total Shareholder Yield rather than recomputed a second time.
    shares_now, shares_1y_ago = (None, None)
    if "shares_outstanding" in concept_ids:
        shares_now, shares_1y_ago = _shares_outstanding_now_and_1y_ago(conn, company_id, concept_ids["shares_outstanding"])
    dilution = None
    if shares_now is not None and shares_1y_ago not in (None, 0):
        dilution = (shares_now - shares_1y_ago) / shares_1y_ago
    if shares_now is None:
        rows.append(_row("share_dilution_trend", None, "missing:shares_outstanding"))
    elif dilution is None:
        rows.append(_row("share_dilution_trend", None, "missing:share_count_1y_ago"))
    else:
        rows.append(_row("share_dilution_trend", dilution, None))

    # Everything below genuinely needs Market Cap (price-dependent)
    if market_cap is None:
        for m in ("ev_ebitda", "ev_sales", "peg_ratio", "buyback_yield", "total_shareholder_yield"):
            rows.append(_row(m, None, "missing:market_cap"))
    else:
        enterprise_value = market_cap
        if total_debt_hit is not None:
            enterprise_value += total_debt_hit[0]
        if cash_hit is not None:
            enterprise_value -= cash_hit[0]
        ev_reason = None if (total_debt_hit is not None and cash_hit is not None) else "partial:missing_debt_or_cash"

        # EV/EBITDA
        if ebitda_ttm is None:
            rows.append(_row("ev_ebitda", None, "missing:ebitda_ttm"))
        elif ebitda_ttm == 0:
            rows.append(_row("ev_ebitda", None, "zero_denominator"))
        else:
            rows.append(_row("ev_ebitda", enterprise_value / ebitda_ttm, ev_reason))

        # EV/Sales -- reuses the same TTM-revenue reconstruction price_metrics.py uses
        revenue_q = _load_quarterly_facts(conn, company_id, concept_ids["revenue"]) if "revenue" in concept_ids else {}
        anchor = _latest_quarter(revenue_q)
        revenue_ttm, _fids = _ttm_sum(revenue_q, *anchor) if anchor else (None, [])
        if revenue_ttm is None:
            rows.append(_row("ev_sales", None, "missing:revenue_ttm"))
        elif revenue_ttm == 0:
            rows.append(_row("ev_sales", None, "zero_denominator"))
        else:
            rows.append(_row("ev_sales", enterprise_value / revenue_ttm, ev_reason))

        # PEG = Trailing P/E / EPS Growth Rate (as a percentage number)
        trailing_pe = _latest_metric_value(conn, company_id, metric_ids["trailing_pe"])
        eps_growth = _latest_metric_value(conn, company_id, metric_ids["eps_growth_yoy"])
        if trailing_pe is None:
            rows.append(_row("peg_ratio", None, "missing:trailing_pe"))
        elif eps_growth is None:
            rows.append(_row("peg_ratio", None, "missing:eps_growth_yoy"))
        elif eps_growth <= 0:
            rows.append(_row("peg_ratio", None, "non_positive_growth_not_meaningful"))
        else:
            rows.append(_row("peg_ratio", trailing_pe / (eps_growth * 100), None))

        # Buyback Yield = Share Buybacks (TTM) / Market Cap
        buybacks_q = _load_quarterly_facts(conn, company_id, concept_ids["share_buybacks"]) if "share_buybacks" in concept_ids else {}
        anchor_bb = _latest_quarter(buybacks_q)
        buybacks_ttm, _fids = _ttm_sum(buybacks_q, *anchor_bb) if anchor_bb else (None, [])
        buyback_yield = None
        if buybacks_ttm is None:
            rows.append(_row("buyback_yield", None, "missing:share_buybacks_ttm"))
        elif market_cap == 0:
            rows.append(_row("buyback_yield", None, "zero_denominator"))
        else:
            buyback_yield = buybacks_ttm / market_cap
            rows.append(_row("buyback_yield", buyback_yield, None))

        # Total Shareholder Yield = Dividend Yield + Buyback Yield - Dilution
        # (dilution already computed above, price-independent, reused here)
        dividend_yield = _latest_metric_value(conn, company_id, metric_ids["dividend_yield"])
        if dividend_yield is None or buyback_yield is None:
            rows.append(_row("total_shareholder_yield", None, "missing:dividend_yield_or_buyback_yield"))
        elif dilution is None:
            rows.append(_row("total_shareholder_yield", None, "missing:share_count_1y_ago"))
        else:
            rows.append(_row("total_shareholder_yield", dividend_yield + buyback_yield - dilution, None))

    with conn.cursor() as cur:
        target_ids = list(metric_ids.values())
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s) and period_label = 'TTM'",
            (company_id, target_ids),
        )
        cur.executemany(
            """
            insert into analytics.metric_value
                (company_id, metric_definition_id, period_start, period_end, period_label,
                 value, is_null_reason, source_fact_ids)
            values
                (%(company_id)s, %(metric_definition_id)s, %(period_start)s, %(period_end)s, %(period_label)s,
                 %(value)s, %(is_null_reason)s, %(source_fact_ids)s)
            """,
            rows,
        )
        conn.commit()

    computed = sum(1 for r in rows if r["value"] is not None)
    null = sum(1 for r in rows if r["value"] is None)
    logger.info("expanded_metrics.company_done", company_id=company_id, computed=computed, null=null)
    return {"computed": computed, "null": null}


def calculate_expanded_metrics(conn: psycopg.Connection, ciks: set[str]) -> dict:
    metric_names = ["net_debt_ebitda", "ev_ebitda", "ev_sales", "peg_ratio", "buyback_yield", "total_shareholder_yield",
                     "institutional_ownership_pct", "share_dilution_trend",
                     "ebitda", "market_cap", "trailing_pe", "eps_growth_yoy", "dividend_yield"]
    with conn.cursor() as cur:
        cur.execute("select metric_name, id from analytics.metric_definition where metric_name = any(%s)", (metric_names,))
        metric_ids = dict(cur.fetchall())
    concept_ids = _load_concept_ids(
        conn, {"total_debt", "cash_and_equivalents", "revenue", "share_buybacks", "shares_outstanding"}
    )

    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    output_metric_ids = {k: v for k, v in metric_ids.items()
                          if k in ("net_debt_ebitda", "ev_ebitda", "ev_sales", "peg_ratio", "buyback_yield",
                                   "total_shareholder_yield", "institutional_ownership_pct", "share_dilution_trend")}

    totals = {"considered": 0, "ok": 0, "no_company": 0, "errored": 0, "computed": 0, "null": 0}
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = calculate_expanded_metrics_for_company(conn, company_id, {**metric_ids, **output_metric_ids}, concept_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "expanded_metrics", exc)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]

    logger.info("expanded_metrics.done", **totals)
    return totals
