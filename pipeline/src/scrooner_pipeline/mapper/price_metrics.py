"""Stage 3h (doc 25 follow-on) -- the 6 price-dependent metrics doc 02
locked from day one: Market Cap, Trailing P/E, Price/Sales, Price/Book,
Dividend Yield, FCF Yield. Unblocked now that Company Master ingests a
real price (core.market_price_alpaca, doc 25) -- this stage does the
actual calculation, per doc 13's own locked boundary rule (Company
Master ingests, Mapper calculates; never the other way around).

Reads core.market_price_alpaca ONLY -- never core.market_price (Company
Master 4b's mock data). There's no runtime is_mock check needed here
because this stage has no code path that can even reach the mock table;
a metric computed from a mock price could never be silently
indistinguishable from a real one, by construction, not by a flag.

Trailing-twelve-month reconstruction for diluted_eps/revenue/dividends_
per_share/cfo/capex reuses ttm.py's own _trailing_quarters helper --
same (fiscal_year, fiscal_period) arithmetic already proven for TTM
ROIC/ROE, not a second implementation of the same idea. TTM EPS sums
the four quarterly diluted_eps values as reported (the standard TTM-EPS
convention), not net income re-divided by a blended share count.

period_label='TTM' for all 6 rows -- a price-dependent ratio is
inherently "as of now" combined with trailing fundamentals, not a
single historical fiscal period, the same framing ttm.py already uses
for TTM ROIC/ROE.

Null discipline unchanged from every other stage: a company with no
dividends_per_share TTM data (e.g. genuinely never tagged a dividend,
or simply doesn't pay one) gets dividend_yield = null with a reason,
never silently defaulted to 0 -- this project can't reliably distinguish
"paid zero" from "never disclosed" from XBRL facts alone, so it doesn't
guess.
"""

from datetime import date
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback
from scrooner_pipeline.mapper.ttm import _trailing_quarters

logger = structlog.get_logger()

# metric_name -> which TTM/point-in-time inputs it needs
# A price older than this is not "current" for valuation. Alpaca still
# returns a latest bar for tickers that stopped trading (delisted,
# acquired, moved to grey market) -- 2026-09-27 found 131 companies whose
# newest bar was 1 month to 5 years old, e.g. a 2021 bar feeding a
# "current" market cap. 14 calendar days covers any exchange holiday run.
MAX_PRICE_AGE_DAYS = 14

TTM_CONCEPTS = {
    "diluted_eps",
    "revenue",
    "dividends_per_share",
    "cfo",
    "capex",
    "net_income",
}
INSTANT_CONCEPTS = {"shares_outstanding", "stockholders_equity"}


def _load_concept_ids(conn: psycopg.Connection, names: set[str]) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (sorted(names),),
        )
        return dict(cur.fetchall())


def _load_quarterly_facts(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> dict:
    """(fiscal_year, fiscal_period) -> (value, fact_ids) for real quarters only (Q1-4) -- same shape as ttm.py's own loader."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.fiscal_year, p.fiscal_period, cf.value, cf.source_fact_ids
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s
              and p.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4')
            """,
            (company_id, concept_id),
        )
        return {(fy, fp): (val, fids) for fy, fp, val, fids in cur.fetchall()}


def _latest_instant_fact(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> tuple[Decimal, list[int], object] | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.value, cf.source_fact_ids, p.end_date
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s
            order by p.end_date desc
            limit 1
            """,
            (company_id, concept_id),
        )
        row = cur.fetchone()
        return (row[0], row[1], row[2]) if row else None


def _ttm_sum(
    by_quarter: dict, fiscal_year: int, fiscal_period: str
) -> tuple[Decimal | None, list[int]]:
    total = Decimal(0)
    fact_ids: list[int] = []
    for key in _trailing_quarters(fiscal_year, fiscal_period):
        hit = by_quarter.get(key)
        if hit is None:
            return None, []
        value, fids = hit
        total += value
        fact_ids.extend(fids)
    return total, fact_ids


# EPS whose latest quarter trails the latest revenue quarter by this many
# quarters or more is treated as absent rather than as current.
STALE_EPS_QUARTERS = 2


def _quarters_behind(
    older: tuple[int, str] | None, newer: tuple[int, str] | None
) -> int:
    if older is None or newer is None:
        return 0
    index = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    return (newer[0] * 4 + index[newer[1]]) - (older[0] * 4 + index[older[1]])


def _latest_quarter(by_quarter: dict) -> tuple[int, str] | None:
    if not by_quarter:
        return None
    order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    return max(by_quarter, key=lambda k: (k[0], order[k[1]]))


def _load_latest_price(
    conn: psycopg.Connection, company_id: int
) -> tuple[Decimal, object] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select price, price_date from core.market_price_alpaca where company_id = %s order by price_date desc limit 1",
            (company_id,),
        )
        row = cur.fetchone()
        return (row[0], row[1]) if row else None


def _load_shares_outstanding_fallback(
    conn: psycopg.Connection, company_id: int
) -> tuple[Decimal, list[int]] | None:
    """Real fallback for multi-class share-structure companies (Block,
    Reddit) whose shares outstanding is dimensionally XBRL-tagged and
    stripped by the standard Company Facts API -- see
    company_master/shares_outstanding_fallback.py's module docstring.
    Only consulted when the primary canonical_fact lookup (real XBRL
    data) has nothing; never overrides a working value. No source_fact_ids
    (this isn't sourced from core.fact at all) -- lineage instead is the
    row's own accession_number, inspectable directly in
    core.shares_outstanding_fallback."""
    with conn.cursor() as cur:
        cur.execute(
            "select shares, filing_date from core.shares_outstanding_fallback where company_id = %s",
            (company_id,),
        )
        row = cur.fetchone()
        return (row[0], [], row[1]) if row else None


def _load_latest_diluted_weighted_shares(
    conn: psycopg.Connection, company_id: int
) -> tuple[Decimal, list[int], object] | None:
    """Latest authoritative, positive WeightedAverageNumberOfDilutedShares-
    Outstanding. Multi-class filers (Comcast, UPS, Ford, Mastercard) tag
    their point-in-time share count per class, which the Company Facts API
    strips, but they still file this total undimensioned. Read from
    core.fact (authoritative only) because no canonical concept holds it."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.value, f.id, p.end_date
            from core.fact f
            join core.concept co on co.id = f.concept_id
            join core.period p on p.id = f.period_id
            where f.company_id = %s
              and co.taxonomy = 'us-gaap'
              and co.tag = 'WeightedAverageNumberOfDilutedSharesOutstanding'
              and f.is_authoritative
              and f.value > 0
            order by p.end_date desc
            limit 1
            """,
            (company_id,),
        )
        row = cur.fetchone()
        return (row[0], [row[1]], row[2]) if row else None


# A share count older than this is not current for market cap. Before
# 2026-09-27 the latest instant fact was used at any age: 173 companies'
# market caps used share counts from before 2024 (Visa, Mastercard, UPS,
# Accenture 2010; Ford 2011; Comcast 2009), because multi-class filers
# moved to per-class tagging that the Company Facts API strips.
MAX_SHARES_AGE_DAYS = 480
# Cover-page counts are checked against the diluted weighted average when
# both exist. The cover-page parser can read one class only (Comcast:
# 9.4M Class B instead of ~3.6B total).
COVER_PAGE_MAX_DEVIATION = Decimal("0.25")


def _choose_shares(
    primary: tuple[Decimal, list[int], object] | None,
    weighted_diluted: tuple[Decimal, list[int], object] | None,
    cover_page: tuple[Decimal, list[int], object] | None,
    today: date,
) -> tuple[tuple[Decimal, list[int]] | None, str | None]:
    """Pick the share count for Market Cap. Each input is (value, fact_ids,
    as_of_date) or None. Returns ((value, fact_ids), None) or (None, reason)."""

    def fresh(hit):
        return (
            hit is not None
            and hit[2] is not None
            and (today - hit[2]).days <= MAX_SHARES_AGE_DAYS
        )

    if fresh(primary):
        return (primary[0], list(primary[1])), None
    wavg = weighted_diluted if fresh(weighted_diluted) else None
    cover = cover_page if fresh(cover_page) else None
    if cover is not None and wavg is not None:
        if abs(cover[0] - wavg[0]) <= COVER_PAGE_MAX_DEVIATION * wavg[0]:
            return (cover[0], list(cover[1])), None
        return (wavg[0], list(wavg[1])), None
    if wavg is not None:
        return (wavg[0], list(wavg[1])), None
    if cover is not None:
        return (cover[0], list(cover[1])), None
    if primary is None and weighted_diluted is None and cover_page is None:
        return None, "missing:shares_outstanding"
    return None, "stale:shares_outstanding"


def calculate_price_metrics_for_company(
    conn: psycopg.Connection,
    company_id: int,
    metric_ids: dict[str, int],
    concept_ids: dict[str, int],
) -> dict:
    stats = {"computed": 0, "null": 0}
    price_hit = _load_latest_price(conn, company_id)
    if price_hit is None:
        # No real price for this company (Alpaca coverage gap) -- every
        # one of the 6 metrics is null with the same honest reason, not
        # silently skipped (a company page reading these rows should see
        # WHY, not just absence).
        price, price_date = None, None
        price_reason = "missing:real_price"
    else:
        price, price_date = price_hit
        if (date.today() - price_date).days > MAX_PRICE_AGE_DAYS:
            # Keep the date so the null row still anchors to the real bar.
            price = None
            price_reason = "stale:real_price"
        elif price <= 0:
            # A non-positive equity price is not economically valid for
            # these ratios and makes Dividend Yield divide by zero. Treat a
            # malformed stored/vendor value as unusable input so one bad bar
            # cannot abort all six metrics for the company.
            price = None
            price_reason = "invalid:non_positive_price"
        else:
            price_reason = None

    quarterly = {
        name: _load_quarterly_facts(conn, company_id, concept_ids[name])
        for name in TTM_CONCEPTS
        if name in concept_ids
    }
    diluted_eps_q = quarterly.get("diluted_eps", {})
    revenue_anchor = _latest_quarter(quarterly.get("revenue", {}))
    eps_anchor = _latest_quarter(diluted_eps_q)
    if _quarters_behind(eps_anchor, revenue_anchor) >= STALE_EPS_QUARTERS:
        # Plain EPS stopped years ago (KKR 2018, Hershey 2010: later EPS is
        # tagged per share class and stripped), so anchoring on it made P/E
        # use years-old earnings. Anchor on the current quarter instead;
        # P/E then falls back to market cap / TTM net income.
        quarterly["diluted_eps"] = {}
        eps_anchor = None
    anchor = eps_anchor or revenue_anchor

    ttm: dict[str, tuple[Decimal | None, list[int]]] = {
        name: (None, []) for name in TTM_CONCEPTS
    }
    # metric_value requires non-null period dates even for an honest null.
    # A company with no vendor bar still needs six inspectable null rows, so
    # anchor them to the calculation date rather than attempting to insert
    # NULL dates (a path the all-priced golden set never exercised).
    period_end = price_date or date.today()
    if anchor is not None:
        fy, fp = anchor
        for name, by_quarter in quarterly.items():
            ttm[name] = _ttm_sum(by_quarter, fy, fp)

    primary_shares = (
        _latest_instant_fact(conn, company_id, concept_ids["shares_outstanding"])
        if "shares_outstanding" in concept_ids
        else None
    )
    shares_hit, shares_reason = _choose_shares(
        primary_shares,
        _load_latest_diluted_weighted_shares(conn, company_id),
        _load_shares_outstanding_fallback(conn, company_id),
        date.today(),
    )
    equity_hit = (
        _latest_instant_fact(conn, company_id, concept_ids["stockholders_equity"])
        if "stockholders_equity" in concept_ids
        else None
    )

    def _row(
        metric_name: str, value: Decimal | None, reason: str | None, fact_ids: list[int]
    ) -> dict:
        return {
            "company_id": company_id,
            "metric_definition_id": metric_ids[metric_name],
            "period_start": period_end,
            "period_end": period_end,
            "period_label": "TTM",
            "value": value,
            "is_null_reason": reason,
            "source_fact_ids": fact_ids or None,
        }

    rows: list[dict] = []

    if price is None:
        for m in (
            "market_cap",
            "trailing_pe",
            "price_to_sales",
            "price_to_book",
            "dividend_yield",
            "fcf_yield",
        ):
            rows.append(_row(m, None, price_reason, []))
    else:
        # Market Cap = Shares Outstanding x Price
        if shares_hit is None:
            market_cap, mc_fids, mc_reason = None, [], shares_reason
        else:
            market_cap = shares_hit[0] * price
            mc_fids = list(shares_hit[1])
            mc_reason = None
        rows.append(_row("market_cap", market_cap, mc_reason, mc_fids))

        # Trailing P/E = Price / Diluted EPS (TTM). When no plain diluted EPS
        # is filed, Market Cap / TTM net income -- the same ratio on a total
        # rather than per-share basis. Multi-class filers (Visa, Airbnb,
        # Hershey, Constellation Brands) tag EPS per share class, which the
        # Company Facts API strips, so price / EPS was blank for them.
        eps_ttm, eps_fids = ttm["diluted_eps"]
        ni_ttm, ni_fids = ttm.get("net_income", (None, []))
        if eps_ttm is None and market_cap is not None and ni_ttm:
            rows.append(
                _row("trailing_pe", market_cap / ni_ttm, None, mc_fids + ni_fids)
            )
        elif eps_ttm is None:
            rows.append(_row("trailing_pe", None, "missing:diluted_eps_ttm", []))
        elif eps_ttm == 0:
            rows.append(_row("trailing_pe", None, "zero_denominator", []))
        else:
            rows.append(_row("trailing_pe", price / eps_ttm, None, eps_fids))

        # Price/Sales = Market Cap / Revenue (TTM)
        rev_ttm, rev_fids = ttm["revenue"]
        if market_cap is None:
            rows.append(_row("price_to_sales", None, mc_reason, []))
        elif rev_ttm is None:
            rows.append(_row("price_to_sales", None, "missing:revenue_ttm", []))
        elif rev_ttm == 0:
            rows.append(_row("price_to_sales", None, "zero_denominator", []))
        else:
            rows.append(
                _row("price_to_sales", market_cap / rev_ttm, None, mc_fids + rev_fids)
            )

        # Price/Book = Market Cap / Stockholders' Equity (most recent)
        if market_cap is None:
            rows.append(_row("price_to_book", None, mc_reason, []))
        elif equity_hit is None:
            rows.append(_row("price_to_book", None, "missing:stockholders_equity", []))
        elif equity_hit[0] == 0:
            rows.append(_row("price_to_book", None, "zero_denominator", []))
        else:
            rows.append(
                _row(
                    "price_to_book",
                    market_cap / equity_hit[0],
                    None,
                    mc_fids + list(equity_hit[1]),
                )
            )

        # Dividend Yield = Dividends per Share (TTM) / Price
        dps_ttm, dps_fids = ttm["dividends_per_share"]
        if dps_ttm is None:
            rows.append(
                _row("dividend_yield", None, "missing:dividends_per_share_ttm", [])
            )
        else:
            rows.append(_row("dividend_yield", dps_ttm / price, None, dps_fids))

        # FCF Yield = FCF (TTM) / Market Cap, FCF = CFO - CapEx
        cfo_ttm, cfo_fids = ttm["cfo"]
        capex_ttm, capex_fids = ttm["capex"]
        if market_cap is None:
            rows.append(_row("fcf_yield", None, mc_reason, []))
        elif cfo_ttm is None:
            rows.append(_row("fcf_yield", None, "missing:cfo_ttm", []))
        elif capex_ttm is None:
            rows.append(_row("fcf_yield", None, "missing:capex_ttm", []))
        elif market_cap == 0:
            rows.append(_row("fcf_yield", None, "zero_denominator", []))
        else:
            fcf_ttm = cfo_ttm - capex_ttm
            rows.append(
                _row(
                    "fcf_yield",
                    fcf_ttm / market_cap,
                    None,
                    mc_fids + cfo_fids + capex_fids,
                )
            )

    with conn.cursor() as cur:
        # Scoped to this stage's own 6 metric_definition_ids AND
        # period_label='TTM' only -- these ids are unique to price
        # metrics (no other stage writes market_cap/trailing_pe/etc.),
        # but the period_label scope is kept anyway, matching ttm.py's
        # own established discipline for any TTM-labeled write.
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

    stats["computed"] = sum(1 for r in rows if r["value"] is not None)
    stats["null"] = sum(1 for r in rows if r["value"] is None)
    logger.info("price_metrics.company_done", company_id=company_id, **stats)
    return stats


def calculate_price_metrics(conn: psycopg.Connection, ciks: set[str]) -> dict:
    price_metric_names = [
        "market_cap",
        "trailing_pe",
        "price_to_sales",
        "price_to_book",
        "dividend_yield",
        "fcf_yield",
    ]
    with conn.cursor() as cur:
        cur.execute(
            "select metric_name, id from analytics.metric_definition where metric_name = any(%s)",
            (price_metric_names,),
        )
        metric_ids = dict(cur.fetchall())
    concept_ids = _load_concept_ids(conn, TTM_CONCEPTS | INSTANT_CONCEPTS)

    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "computed": 0,
        "null": 0,
    }
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = calculate_price_metrics_for_company(
                conn, company_id, metric_ids, concept_ids
            )
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "price_metrics", exc)
            conn = safe_rollback(conn, stage="price_metrics", cik=cik)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]

    logger.info("price_metrics.done", **totals)
    return totals
