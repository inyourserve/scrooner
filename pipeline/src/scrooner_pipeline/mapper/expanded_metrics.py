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

# The 9 metrics this module actually WRITES -- everything else in the
# metric_ids dict passed into calculate_expanded_metrics_for_company()
# (ebitda, market_cap, trailing_pe, eps_growth_yoy, dividend_yield,
# debtor_days, inventory_days, payables_days) is a dependency this module
# only READS, computed and owned by price_metrics.py/calculate.py. Found
# live 2026-09-03: the per-company delete used to scope by
# `metric_ids.values()` (the FULL dict, reads included), silently wiping
# those 7 dependency metrics' real, already-computed TTM rows on every
# calculate-expanded-metrics run, with no reinsert to replace them (this
# module has no code path that recomputes market_cap et al). Every rerun
# made the problem worse, not better -- market_cap/trailing_pe/
# dividend_yield ended up at a genuine 0% company-wide after several
# reruns today, even though calculate-price-metrics had computed them
# correctly hours earlier. The delete must only ever touch this set.
OUTPUT_METRIC_NAMES = frozenset({
    "net_debt_ebitda", "ev_ebitda", "ev_sales", "peg_ratio", "buyback_yield",
    "total_shareholder_yield", "institutional_ownership_pct", "share_dilution_trend",
    "cash_conversion_cycle",
    # Added 2026-09-05 (financials display spec gap-fill).
    "ebitda_margin", "debt_to_ebitda", "fcf_per_share", "share_repurchases_pct_fcf", "dividends_pct_fcf",
    # Added 2026-09-08 (Data Sanity Layer finding): a TTM `ebitda` row,
    # NOT a new dependency conflict with the comment above -- `ebitda`'s
    # Q1-Q4/FY rows (calculate.py's own output) are untouched, since the
    # delete below is scoped to period_label='TTM' only, which no other
    # writer has ever produced for this metric_definition_id. Real bug
    # found live: yfinance's ebitda ($168.0B for AAPL) matched
    # _ebitda_ttm()'s own already-correct sum of 4 quarters ($167.96B)
    # almost exactly, but that sum was never persisted anywhere reachable
    # -- every other consumer (and the sanity layer's "most recent
    # period" query) could only see a single quarter's ebitda ($39.0B),
    # a ~4x understatement that looked like a data bug but was actually
    # a missing row. See doc/learnings/2026-09-08-data-sanity-layer.md.
    "ebitda",
})


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


def _fcf_ttm(conn: psycopg.Connection, company_id: int, fcf_metric_id: int) -> Decimal | None:
    """Sum of the 4 most recent quarterly `fcf` metric_value rows --
    identical shape to _ebitda_ttm above (fcf is also a metric, not a
    canonical_fact concept), added 2026-09-05 for fcf_per_share/
    share_repurchases_pct_fcf/dividends_pct_fcf."""
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
            (company_id, fcf_metric_id),
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
    """Sum of Form 13F holdings for the single most recent reporting
    window, deduped per FILER (by filer_cik, not filer_name text) and
    per FILING (by accession_number, preferring an amendment over the
    original) -- but SUMMING every row within whichever one filing is
    chosen, not picking a single row.

    Found live 2026-09-05, a real, serious undercounting bug: the
    original query deduped with `distinct on (filer_name)` with no
    scoping at all beyond company_id (silently blending rows from
    every stored reporting window together) and kept only ONE row per
    filer. A single Form 13F filing can legitimately report the SAME
    security across MULTIPLE separate INFOTABLE rows for one filer
    (different investment-discretion/managed-account categories) --
    confirmed live for AAPL: "BlackRock, Inc." reports 25 separate
    rows, all is_amendment=false, all under the SAME accession_number,
    summing to ~$1.1B of AAPL's real ~5.5B-share institutional total in
    the most recent window alone. `distinct on (filer_name)` kept only
    ONE of those 25 rows (the largest at $423.9M), discarding the other
    24 -- the same undercounting shape for every large multi-fund
    manager (Vanguard's various sub-manager entities showed the same
    pattern). This alone explained most of the gap between the
    originally-reported ~36% and AAPL's real, publicly-known
    institutional ownership (~60%).

    Distinguishing a genuine multi-row filing (sum all of them) from a
    genuine amendment (use only the newer one, not both) requires two
    different keys: filer_cik identifies WHO, accession_number
    identifies WHICH FILING -- an amendment is a different
    accession_number for the same filer_cik (verified live: Vanguard
    Capital Management LLC's original and amendment shared the same
    953,847,648-share value under two different accession numbers),
    while BlackRock's 25 rows all share one accession_number (a real
    multi-line position within one filing, not duplicates)."""
    with conn.cursor() as cur:
        # source_zip is a bulk-download filename, not a sortable date --
        # picking the window with the latest real filing_date is the
        # robust way to find "the most recent reporting window",
        # instead of a fragile string comparison over source_zip itself.
        cur.execute(
            """
            select source_zip from core.institutional_ownership
            where company_id = %s
            group by source_zip
            order by max(filing_date) desc nulls last
            limit 1
            """,
            (company_id,),
        )
        row = cur.fetchone()
        latest_window = row[0] if row else None
        if latest_window is None:
            return None
        cur.execute(
            """
            select sum(io.shares)
            from core.institutional_ownership io
            join (
                select distinct on (filer_cik) filer_cik, accession_number
                from core.institutional_ownership
                where company_id = %s and source_zip = %s
                order by filer_cik, is_amendment desc, filing_date desc nulls last
            ) chosen_filing
              on chosen_filing.filer_cik = io.filer_cik
             and chosen_filing.accession_number = io.accession_number
            where io.company_id = %s and io.source_zip = %s
            """,
            (company_id, latest_window, company_id, latest_window),
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

    # total_debt_resolved (doc 40, 2026-09-02), not total_debt directly --
    # prefers the combined LongTermDebt tag, falls back to the summed
    # split tags (LongTermDebtCurrent+LongTermDebtNoncurrent) when the
    # combined tag is absent. See mapper/concept_fallback.py.
    total_debt_hit = _latest_instant_fact(conn, company_id, concept_ids["total_debt_resolved"]) if "total_debt_resolved" in concept_ids else None
    cash_hit = _latest_instant_fact(conn, company_id, concept_ids["cash_and_equivalents"]) if "cash_and_equivalents" in concept_ids else None
    ebitda_ttm = _ebitda_ttm(conn, company_id, metric_ids["ebitda"])
    market_cap = _latest_metric_value(conn, company_id, metric_ids["market_cap"])

    # Persist the TTM sum itself (2026-09-08) -- previously computed fresh
    # every call but never stored, so any OTHER reader (the Data Sanity
    # Layer, a future feature, a human debugging) could only see a single
    # quarter's ebitda via metric_value's own "most recent period" rule.
    rows.append(_row("ebitda", ebitda_ttm, None if ebitda_ttm is not None else "missing:4_consecutive_quarters"))

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

    # Revenue/FCF/Buybacks/Dividends TTM, computed once here (all
    # price-independent) and reused below by both the price-independent
    # rows in this block (ebitda_margin, debt_to_ebitda, fcf_per_share,
    # share_repurchases_pct_fcf, dividends_pct_fcf, added 2026-09-05) and
    # the price-dependent ev_sales/buyback_yield rows further down --
    # revenue_q/buybacks_q used to be computed twice (once here
    # implicitly via duplication, once inside the price-dependent block);
    # consolidated into one fetch each to avoid the drift risk of two
    # separate queries silently disagreeing.
    revenue_q = _load_quarterly_facts(conn, company_id, concept_ids["revenue"]) if "revenue" in concept_ids else {}
    revenue_anchor = _latest_quarter(revenue_q)
    revenue_ttm, _revenue_fids = _ttm_sum(revenue_q, *revenue_anchor) if revenue_anchor else (None, [])
    fcf_ttm = _fcf_ttm(conn, company_id, metric_ids["fcf"]) if "fcf" in metric_ids else None
    buybacks_q = _load_quarterly_facts(conn, company_id, concept_ids["share_buybacks"]) if "share_buybacks" in concept_ids else {}
    buybacks_anchor = _latest_quarter(buybacks_q)
    buybacks_ttm, _buybacks_fids = _ttm_sum(buybacks_q, *buybacks_anchor) if buybacks_anchor else (None, [])
    dividends_q = _load_quarterly_facts(conn, company_id, concept_ids["dividends_paid"]) if "dividends_paid" in concept_ids else {}
    dividends_anchor = _latest_quarter(dividends_q)
    dividends_ttm, _dividends_fids = _ttm_sum(dividends_q, *dividends_anchor) if dividends_anchor else (None, [])

    # EBITDA Margin = EBITDA (TTM) / Revenue (TTM)
    if ebitda_ttm is None:
        rows.append(_row("ebitda_margin", None, "missing:ebitda_ttm"))
    elif revenue_ttm is None:
        rows.append(_row("ebitda_margin", None, "missing:revenue_ttm"))
    elif revenue_ttm == 0:
        rows.append(_row("ebitda_margin", None, "zero_denominator"))
    else:
        rows.append(_row("ebitda_margin", ebitda_ttm / revenue_ttm, None))

    # Debt / EBITDA -- gross leverage (unlike net_debt_ebitda above, does
    # NOT net out cash first).
    if total_debt_hit is None:
        rows.append(_row("debt_to_ebitda", None, "missing:total_debt"))
    elif ebitda_ttm is None:
        rows.append(_row("debt_to_ebitda", None, "missing:ebitda_ttm"))
    elif ebitda_ttm == 0:
        rows.append(_row("debt_to_ebitda", None, "zero_denominator"))
    else:
        rows.append(_row("debt_to_ebitda", total_debt_hit[0] / ebitda_ttm, None))

    # Cash Conversion Cycle = Debtor Days + Inventory Days - Payables
    # Days -- combines three ALREADY-COMPUTED metric outputs (each its
    # own FY-only "days" shape row in calculate.py), not raw concepts,
    # same "combines other metrics' output" pattern as net_debt_ebitda.
    # Uses each metric's own most-recent-FY value independently (same
    # _latest_metric_value helper as everywhere else in this module) --
    # not guaranteed to be the exact same fiscal year across all three
    # if one input is missing for the latest year but present for an
    # earlier one; is_null_reason below flags exactly which is missing.
    debtor_days = _latest_metric_value(conn, company_id, metric_ids["debtor_days"]) if "debtor_days" in metric_ids else None
    inventory_days = _latest_metric_value(conn, company_id, metric_ids["inventory_days"]) if "inventory_days" in metric_ids else None
    payables_days = _latest_metric_value(conn, company_id, metric_ids["payables_days"]) if "payables_days" in metric_ids else None
    if debtor_days is None:
        rows.append(_row("cash_conversion_cycle", None, "missing:debtor_days"))
    elif inventory_days is None:
        rows.append(_row("cash_conversion_cycle", None, "missing:inventory_days"))
    elif payables_days is None:
        rows.append(_row("cash_conversion_cycle", None, "missing:payables_days"))
    else:
        rows.append(_row("cash_conversion_cycle", debtor_days + inventory_days - payables_days, None))

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
    elif inst_shares > shares_out_value:
        # Institutional ownership can never exceed 100% by definition --
        # a result over that is proof the denominator is wrong (a stale
        # or wrong shares_outstanding resolution), not evidence of real
        # ownership. Found live 2026-09-05: NIKE's shares_outstanding
        # has had no real authoritative EntityCommonStockSharesOutstanding
        # fact since 2015-07-17 (almost certainly the same dimensional/
        # multi-class-share stripping this project already documented for
        # Block/Reddit) -- with the institutional-dedup bug fixed the same
        # day (see _institutional_ownership_shares's own docstring), the
        # real 961M-share institutional total correctly exceeded NIKE's
        # stale ~868M-share denominator, producing an impossible 110.6%.
        # Null with a clear, distinct reason rather than silently show a
        # number that's definitionally impossible -- the shares_outstanding
        # resolution gap itself is a separate, not-yet-fixed problem.
        rows.append(_row("institutional_ownership_pct", None, "implausible:institutional_shares_exceed_shares_outstanding"))
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

    # FCF Per Share = Free Cash Flow (TTM) / Shares Outstanding (reuses
    # shares_now, already resolved above for share_dilution_trend).
    if fcf_ttm is None:
        rows.append(_row("fcf_per_share", None, "missing:fcf_ttm"))
    elif shares_now is None:
        rows.append(_row("fcf_per_share", None, "missing:shares_outstanding"))
    elif shares_now == 0:
        rows.append(_row("fcf_per_share", None, "zero_denominator"))
    else:
        rows.append(_row("fcf_per_share", fcf_ttm / shares_now, None))

    # Share Repurchases % of FCF -- what fraction of real cash generation
    # went to buybacks, distinct from buyback_yield (buybacks / Market Cap).
    if buybacks_ttm is None:
        rows.append(_row("share_repurchases_pct_fcf", None, "missing:share_buybacks_ttm"))
    elif fcf_ttm is None:
        rows.append(_row("share_repurchases_pct_fcf", None, "missing:fcf_ttm"))
    elif fcf_ttm == 0:
        rows.append(_row("share_repurchases_pct_fcf", None, "zero_denominator"))
    else:
        rows.append(_row("share_repurchases_pct_fcf", buybacks_ttm / fcf_ttm, None))

    # Dividends % of FCF -- a cash-based payout coverage check, distinct
    # from payout_ratio (Dividends per Share / Diluted EPS, earnings-based).
    if dividends_ttm is None:
        rows.append(_row("dividends_pct_fcf", None, "missing:dividends_paid_ttm"))
    elif fcf_ttm is None:
        rows.append(_row("dividends_pct_fcf", None, "missing:fcf_ttm"))
    elif fcf_ttm == 0:
        rows.append(_row("dividends_pct_fcf", None, "zero_denominator"))
    else:
        rows.append(_row("dividends_pct_fcf", dividends_ttm / fcf_ttm, None))

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

        # EV/Sales -- reuses revenue_ttm, already computed price-independently above.
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

        # Buyback Yield = Share Buybacks (TTM) / Market Cap -- reuses
        # buybacks_ttm, already computed price-independently above.
        buyback_yield = None
        if buybacks_ttm is None:
            rows.append(_row("buyback_yield", None, "missing:share_buybacks_ttm"))
        elif market_cap == 0:
            rows.append(_row("buyback_yield", None, "zero_denominator"))
        else:
            buyback_yield = buybacks_ttm / market_cap
            rows.append(_row("buyback_yield", buyback_yield, None))

        # Total Shareholder Yield = Dividend Yield + Buyback Yield - Dilution
        # (dilution already computed above, price-independent, reused here).
        # Found live 2026-09-05: gating this on dividend_yield AND buyback_
        # yield both being non-null (the original logic) nulled the whole
        # metric for the common case of a company that pays no dividend but
        # does buy back stock, or vice versa -- 11.33% company coverage,
        # LOWER than either individual component. A company with no
        # dividends_ttm/buybacks_ttm fact genuinely reported none for the
        # period (not an unknown value) -- dividends_paid's own concept
        # coverage (41.45%, ~2,162 companies) already closely matches the
        # known ~1,979-company dividend-paying population, confirming
        # capture is complete for payers, not partially missing. Computed
        # directly from dividends_ttm/buybacks_ttm here (not the separately-
        # computed dividend_yield/buyback_yield metric_value rows) so a
        # missing one can default to $0 without disturbing those metrics'
        # own, still-conservative, independent null behavior.
        # Found live 2026-09-05 (real DivisionByZero crash, CIK 0001800227):
        # market_cap can be exactly Decimal("0") even when not None (a
        # genuine degenerate case, e.g. zero shares_outstanding captured).
        # buyback_yield above already guards this with market_cap == 0 --
        # this direct division needs the same guard, not just a None check.
        if market_cap == 0:
            rows.append(_row("total_shareholder_yield", None, "zero_denominator"))
        elif dilution is None:
            rows.append(_row("total_shareholder_yield", None, "missing:share_count_1y_ago"))
        else:
            dividend_contribution = (dividends_ttm / market_cap) if dividends_ttm is not None else Decimal("0")
            buyback_contribution = (buybacks_ttm / market_cap) if buybacks_ttm is not None else Decimal("0")
            rows.append(_row("total_shareholder_yield", dividend_contribution + buyback_contribution - dilution, None))

    with conn.cursor() as cur:
        # Upsert, not delete-then-insert -- found live 2026-09-09/10: this
        # module's rows are all anchored on period_start=period_end=
        # date.today() (an "as of now" composite), so two concurrent
        # invocations for the SAME company on the SAME calendar day (e.g.
        # a manual run overlapping the daily cron, or two dev sessions on
        # this shared environment) target the identical primary key and
        # can race -- one process's INSERT landing between another's
        # DELETE and its own INSERT raises a real UniqueViolation
        # (metric_value_company_id_metric_definition_id_period_start_p_key),
        # confirmed live: 6 real companies hit exactly this in one ~16-
        # minute window. Safe to upsert instead of delete-first here
        # specifically because `rows` always contains a full entry for
        # every OUTPUT_METRIC_NAMES metric on every call (never a partial
        # subset short-circuited early) -- so there's no "stale row from a
        # metric this run didn't recompute" case an upsert would leave
        # behind. ON CONFLICT is atomic per row, so it can't race with
        # itself the way delete-then-insert could.
        cur.executemany(
            """
            insert into analytics.metric_value
                (company_id, metric_definition_id, period_start, period_end, period_label,
                 value, is_null_reason, source_fact_ids)
            values
                (%(company_id)s, %(metric_definition_id)s, %(period_start)s, %(period_end)s, %(period_label)s,
                 %(value)s, %(is_null_reason)s, %(source_fact_ids)s)
            on conflict (company_id, metric_definition_id, period_start, period_end, period_label)
            do update set
                value = excluded.value,
                is_null_reason = excluded.is_null_reason,
                source_fact_ids = excluded.source_fact_ids
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
                     "institutional_ownership_pct", "share_dilution_trend", "cash_conversion_cycle",
                     "debtor_days", "inventory_days", "payables_days",
                     "ebitda", "market_cap", "trailing_pe", "eps_growth_yoy", "dividend_yield",
                     # Added 2026-09-05 (financials display spec gap-fill): fcf (input,
                     # via _fcf_ttm) plus the 5 new output metrics.
                     "fcf", "ebitda_margin", "debt_to_ebitda", "fcf_per_share",
                     "share_repurchases_pct_fcf", "dividends_pct_fcf"]
    with conn.cursor() as cur:
        cur.execute("select metric_name, id from analytics.metric_definition where metric_name = any(%s)", (metric_names,))
        metric_ids = dict(cur.fetchall())
    concept_ids = _load_concept_ids(
        conn, {"total_debt_resolved", "cash_and_equivalents", "revenue", "share_buybacks", "shares_outstanding",
               "dividends_paid"}
    )

    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    output_metric_ids = {k: v for k, v in metric_ids.items() if k in OUTPUT_METRIC_NAMES}

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
