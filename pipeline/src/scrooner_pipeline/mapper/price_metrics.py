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

Trailing-twelve-month reconstruction for revenue/net income/dividends_
per_share/cfo/capex reuses ttm.py's own _trailing_quarters helper --
same (fiscal_year, fiscal_period) arithmetic already proven for TTM
ROIC/ROE, not a second implementation of the same idea.

Per-share rule (2026-10-22, WO-2 RU-1; doc 42, data-team/14): EPS is never
summed over quarters and a DERIVED per-share quarter is never used at all.
Quarterly EPS divides by each quarter's own weighted share count, so four
quarters do not add up to the year (MSFT Q4 FY26 derived 4.80 vs filed
4.81, AAPL Q4 FY25 1.84 vs 1.85, KLAC -22.61 across a split). So:
- The TTM anchor is the company's current quarter: the latest revenue or
  net-income quarter. EPS never sets it (before this change a company that
  had just filed its 10-K, with no Q4 EPS once Q4 EPS stops being derived,
  anchored on Q3 and every TTM went one quarter stale).
- TTM EPS exists only at a Q4 anchor, where the trailing window IS the
  fiscal year: the filed full-year diluted EPS. Elsewhere Trailing P/E is
  market cap / TTM net income (the existing multi-class fallback; basis
  identified by its source_fact_ids: share count + net income facts).
- Dividend yield still sums four quarterly dividends per share, but a
  derived quarter counts as missing, so the yield is blank with
  PER_SHARE_NOT_DERIVED_REASON until the Standardization Lead's definition
  (AC-13) replaces the sum.

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

from scrooner_pipeline.common.derivation_policy import PER_SHARE_NOT_DERIVED_REASON
from scrooner_pipeline.common.rule_flags import rule_enabled
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
# The per-share rule above runs only with this rule ON; OFF keeps the legacy TTM EPS (sum of four quarterly
# diluted EPS, EPS-anchored with the stale-EPS fallback) unchanged.
RULE_PER_SHARE_TTM = "pershare.never_derive_ttm@1"
# EPS whose latest quarter trails the latest revenue quarter by this many
# quarters or more is treated as absent rather than as current (legacy path).
STALE_EPS_QUARTERS = 2


def _quarters_behind(
    older: tuple[int, str] | None, newer: tuple[int, str] | None
) -> int:
    if older is None or newer is None:
        return 0
    index = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    return (newer[0] * 4 + index[newer[1]]) - (older[0] * 4 + index[older[1]])


# TTM inputs that are per-share: a derived quarter of these is never used.
PER_SHARE_TTM_CONCEPTS = {"diluted_eps", "dividends_per_share"}
# A Q4 anchor and the filed FY must end on the same date (52/53-week slack).
ANCHOR_FY_END_SLACK_DAYS = 7


class QuarterFacts(dict):
    """(fiscal_year, fiscal_period) -> (value, fact_ids) for Q1-Q4, plus
    `end_dates` ((fy, fp) -> period end) and `derived_keys` (quarters whose
    canonical value has a derived core.fact source). Plain dicts (tests,
    older callers) behave as "no dates, nothing derived"."""

    end_dates: dict
    derived_keys: set


def _load_quarterly_facts(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> dict:
    """(fiscal_year, fiscal_period) -> (value, fact_ids) for real quarters only (Q1-4) -- same shape as ttm.py's own loader."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.fiscal_year, p.fiscal_period, cf.value, cf.source_fact_ids, p.end_date,
                   exists (select 1 from core.fact f
                           where f.id = any(cf.source_fact_ids) and f.is_derived) as any_derived
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s
              and p.fiscal_period in ('Q1', 'Q2', 'Q3', 'Q4')
            """,
            (company_id, concept_id),
        )
        rows = cur.fetchall()
    out = QuarterFacts(((fy, fp), (val, fids)) for fy, fp, val, fids, _e, _d in rows)
    out.end_dates = {(fy, fp): end for fy, fp, _v, _f, end, _d in rows}
    out.derived_keys = {(fy, fp) for fy, fp, _v, _f, _e, derived in rows if derived}
    return out


def _load_annual_facts(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> dict[int, tuple[Decimal, list[int], date]]:
    """fiscal_year -> (value, fact_ids, period end) for FY rows whose sources
    are all filed (not derived). Used for TTM EPS at a Q4 anchor."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.fiscal_year, cf.value, cf.source_fact_ids, p.end_date
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s
              and p.fiscal_period = 'FY'
              and not exists (select 1 from core.fact f
                              where f.id = any(cf.source_fact_ids) and f.is_derived)
            """,
            (company_id, concept_id),
        )
        return {fy: (val, list(fids), end) for fy, val, fids, end in cur.fetchall()}


def _without_derived(by_quarter: dict) -> tuple[dict, bool]:
    """The quarters minus any whose value comes from a derived fact, and
    whether any was dropped. Belt and braces for RU-1: derived per-share rows
    written before the guard stay in core.fact until the reviewed retirement
    runs, and must never feed a TTM meanwhile."""
    derived: set = getattr(by_quarter, "derived_keys", set())
    if not derived:
        return by_quarter, False
    kept = {k: v for k, v in by_quarter.items() if k not in derived}
    return kept, len(kept) != len(by_quarter)


def _per_share_window_blocked(
    original: dict, kept: dict, anchor: tuple[int, str] | None
) -> bool:
    """True when the per-share TTM window at `anchor` is incomplete because
    of the no-derivation rule, not because the company has no such values:
    a window quarter was dropped as derived, or the window's Q4 is absent
    while another window quarter is filed (Q4 per-share values are almost
    never filed separately). Drives the reason text, never a value."""
    if anchor is None:
        return False
    window = _trailing_quarters(*anchor)
    if any(k in original and k not in kept for k in window):
        return True
    has_filed = any(k in kept for k in window)
    q4_missing = any(k[1] == "Q4" and k not in kept for k in window)
    return has_filed and q4_missing


def _current_quarter(*series: dict) -> tuple[int, str] | None:
    """The company's current quarter for TTM purposes: the latest quarter of
    the given (additive) series. Per-share series are never passed here."""
    anchors = [a for a in (_latest_quarter(s) for s in series) if a is not None]
    if not anchors:
        return None
    order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    return max(anchors, key=lambda k: (k[0], order[k[1]]))


def _anchor_end(anchor: tuple[int, str], *series: dict) -> date | None:
    for s in series:
        end = getattr(s, "end_dates", {}).get(anchor)
        if end is not None:
            return end
    return None


def _ttm_eps_at_anchor(
    anchor: tuple[int, str] | None,
    anchor_end: date | None,
    annual_eps: dict,
) -> tuple[Decimal | None, list[int]]:
    """Filed full-year diluted EPS when the anchor is a Q4 (the trailing
    window is that fiscal year), else (None, []). Never a sum of quarters."""
    if anchor is None or anchor[1] != "Q4":
        return None, []
    hit = annual_eps.get(anchor[0])
    if hit is None:
        return None, []
    value, fids, fy_end = hit
    if (
        anchor_end is not None
        and fy_end is not None
        and abs((fy_end - anchor_end).days) > ANCHOR_FY_END_SLACK_DAYS
    ):
        return None, []  # labels disagree with dates: do not pair them
    return value, list(fids)


def _load_concept_ids(conn: psycopg.Connection, names: set[str]) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            "select name, id from analytics.canonical_concept where name = any(%s)",
            (sorted(names),),
        )
        return dict(cur.fetchall())


def _latest_instant_fact(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> tuple[Decimal, list[int], date | None] | None:
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


def _latest_quarter(by_quarter: dict) -> tuple[int, str] | None:
    if not by_quarter:
        return None
    order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    return max(by_quarter, key=lambda k: (k[0], order[k[1]]))


def _load_latest_price(
    conn: psycopg.Connection, company_id: int
) -> tuple[Decimal, date] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select price, price_date from core.market_price_alpaca where company_id = %s order by price_date desc limit 1",
            (company_id,),
        )
        row = cur.fetchone()
        return (row[0], row[1]) if row else None


def _load_shares_outstanding_fallback(
    conn: psycopg.Connection, company_id: int
) -> tuple[Decimal, list[int], date] | None:
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
) -> tuple[Decimal, list[int], date | None] | None:
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
    primary: tuple[Decimal, list[int], date | None] | None,
    weighted_diluted: tuple[Decimal, list[int], date | None] | None,
    cover_page: tuple[Decimal, list[int], date | None] | None,
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

    if primary is not None and fresh(primary):
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

    never_derive = rule_enabled(RULE_PER_SHARE_TTM)
    per_share_original: dict[str, dict] = {}
    if never_derive:
        # Quarterly diluted EPS is not loaded at all: it is never summed and
        # never sets the anchor (TTM EPS comes from the filed FY, below).
        quarterly = {
            name: _load_quarterly_facts(conn, company_id, concept_ids[name])
            for name in TTM_CONCEPTS
            if name in concept_ids and name != "diluted_eps"
        }
        # Per-share quarters: a derived value is never used (treated as missing).
        per_share_original = {
            name: quarterly[name] for name in PER_SHARE_TTM_CONCEPTS & set(quarterly)
        }
        for name, series in per_share_original.items():
            quarterly[name], _dropped = _without_derived(series)

        # The anchor is the company's current quarter from the additive series
        # (revenue, net income), never from EPS: KKR (EPS stopped in 2018) and a
        # company that has just filed its 10-K (no Q4 EPS) both stay current.
        revenue_q = quarterly.get("revenue", {})
        net_income_q = quarterly.get("net_income", {})
        anchor = _current_quarter(revenue_q, net_income_q)
    else:
        quarterly = {
            name: _load_quarterly_facts(conn, company_id, concept_ids[name])
            for name in TTM_CONCEPTS
            if name in concept_ids
        }
        diluted_eps_q = quarterly.get("diluted_eps", {})
        revenue_q = quarterly.get("revenue", {})
        net_income_q = quarterly.get("net_income", {})
        revenue_anchor = _latest_quarter(revenue_q)
        eps_anchor = _latest_quarter(diluted_eps_q)
        if _quarters_behind(eps_anchor, revenue_anchor) >= STALE_EPS_QUARTERS:
            # Plain EPS stopped years ago (KKR 2018, Hershey 2010): anchor on the
            # current quarter; P/E then falls back to market cap / TTM net income.
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
    per_share_window_blocked = {
        name: _per_share_window_blocked(series, quarterly[name], anchor)
        for name, series in per_share_original.items()
    }
    if anchor is not None:
        fy, fp = anchor
        for name, by_quarter in quarterly.items():
            ttm[name] = _ttm_sum(by_quarter, fy, fp)
        if never_derive and "diluted_eps" in concept_ids:
            ttm["diluted_eps"] = _ttm_eps_at_anchor(
                anchor,
                _anchor_end(anchor, revenue_q, net_income_q),
                _load_annual_facts(conn, company_id, concept_ids["diluted_eps"]),
            )

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

        # Trailing P/E = Price / filed FY diluted EPS at a Q4 anchor. Anywhere
        # else (Q1-Q3 anchors: the trailing window contains a Q4 whose EPS is
        # not filed separately; multi-class filers whose EPS is per class and
        # stripped by the Company Facts API: Visa, Airbnb, Hershey) it is
        # Market Cap / TTM net income -- the same ratio on a total basis.
        eps_ttm, eps_fids = ttm["diluted_eps"]
        ni_ttm, ni_fids = ttm.get("net_income", (None, []))
        if not never_derive:
            # legacy order: price / TTM EPS, else market cap / TTM net income
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
        elif eps_ttm is not None:
            if eps_ttm == 0:
                rows.append(_row("trailing_pe", None, "zero_denominator", []))
            else:
                rows.append(_row("trailing_pe", price / eps_ttm, None, eps_fids))
        elif market_cap is None:
            rows.append(_row("trailing_pe", None, mc_reason, []))
        elif ni_ttm is None:
            rows.append(_row("trailing_pe", None, "missing:net_income_ttm", []))
        elif ni_ttm == 0:
            rows.append(_row("trailing_pe", None, "zero_denominator", []))
        else:
            rows.append(
                _row("trailing_pe", market_cap / ni_ttm, None, mc_fids + ni_fids)
            )

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
        # Quarters are filed values only (derived ones were dropped above).
        # If the window failed while the company does report quarterly DPS,
        # the gap is the unfiled Q4, not an absent dividend: say so.
        dps_ttm, dps_fids = ttm["dividends_per_share"]
        if dps_ttm is None and per_share_window_blocked.get("dividends_per_share"):
            rows.append(_row("dividend_yield", None, PER_SHARE_NOT_DERIVED_REASON, []))
        elif dps_ttm is None:
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
