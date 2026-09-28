"""Stage 3e -- TTM and growth windows (doc 11). Two independent jobs:

1. Growth metrics (revenue_growth_yoy/3y_cagr, eps_growth_yoy/3y_cagr) --
   deferred from Stage 3d since they compare two different periods of the
   same company, not a single period's inputs. Matches same fiscal_period
   across fiscal years (Q1 vs year-ago Q1, FY vs year-ago FY, etc.) so
   seasonality never distorts the comparison -- this is exactly why the
   comparison is done on matching fiscal_period, not on unrelated periods.

2. Trailing-twelve-month ROIC/ROE for quarterly periods -- Stage 3d
   deliberately left these FY-only, since naively computing them from a
   bare quarter distorts badly (doc 09's Day 3 finding: 127.8% vs a sane
   31.95% for AAPL). Verified live 2026-08-16 before implementing: summing
   AAPL's four quarterly operating_income facts (Q1-Q4 FY2024) reproduces
   the reported FY2024 figure exactly ($123,216,000,000) -- confirms
   trailing-4-quarter reconstruction via fiscal_year/fiscal_period lookup
   is sound, not just theoretically appealing.

TTM period matching uses (fiscal_year, fiscal_period) arithmetic, not raw
date math -- for a target quarter (Y, Q), the trailing 4 quarters are:
    Q4 -> (Y,Q1),(Y,Q2),(Y,Q3),(Y,Q4)         [equals the FY figure -- used as a cross-check]
    Q3 -> (Y-1,Q4),(Y,Q1),(Y,Q2),(Y,Q3)
    Q2 -> (Y-1,Q3),(Y-1,Q4),(Y,Q1),(Y,Q2)
    Q1 -> (Y-1,Q2),(Y-1,Q3),(Y-1,Q4),(Y,Q1)
All 4 must resolve or the TTM value is null with a reason -- same
completeness discipline as Stage 3d's per-role check, not "sum whatever's
available."
"""

from datetime import timedelta
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback

logger = structlog.get_logger()

GROWTH_METRICS = {
    "revenue_growth_yoy": ("revenue", 1),
    "revenue_growth_3y_cagr": ("revenue", 3),
    "eps_growth_yoy": ("diluted_eps", 1),
    "eps_growth_3y_cagr": ("diluted_eps", 3),
    # 5Y/10Y CAGR added 2026-08-19 (doc 26's "what moves the needle
    # next" list) -- purely additive dict entries, zero new code:
    # _growth_value already generalizes to any lag_years via the CAGR
    # branch, and _load_metric_ids/the delete-then-insert scope in
    # _compute_growth_for_company both derive from GROWTH_METRICS' own
    # keys, so nothing else needed changing. Zero-regression verified:
    # the original 4 metrics' values are byte-identical before/after.
    "revenue_growth_5y_cagr": ("revenue", 5),
    "revenue_growth_10y_cagr": ("revenue", 10),
    "eps_growth_5y_cagr": ("diluted_eps", 5),
    "eps_growth_10y_cagr": ("diluted_eps", 10),
    # dps_growth_yoy/3y_cagr added 2026-08-29 -- same purely-additive
    # dict-entry pattern as the 5Y/10Y CAGR additions above; "dps" matches
    # this dict's existing "eps" abbreviation convention.
    "dps_growth_yoy": ("dividends_per_share", 1),
    "dps_growth_3y_cagr": ("dividends_per_share", 3),
    # net_income_growth_*/diluted_shares_growth_* added 2026-09-05
    # (financials display spec) -- same purely-additive dict-entry
    # pattern as every prior GROWTH_METRICS addition. diluted_shares_
    # growth_* uses shares_outstanding (this project has no separate
    # diluted-weighted-average-shares concept yet, see
    # doc/learnings/2026-09-05-financials-spec-gap-plan.md) -- the same
    # concept share_dilution_trend already uses for its own rolling
    # dilution figure, just as a real FY-vs-prior-FY series here instead
    # of a ~1yr-ago comparison anchored on "today."
    "net_income_growth_yoy": ("net_income", 1),
    "net_income_growth_3y_cagr": ("net_income", 3),
    "net_income_growth_5y_cagr": ("net_income", 5),
    "net_income_growth_10y_cagr": ("net_income", 10),
    "diluted_shares_growth_yoy": ("shares_outstanding", 1),
    "diluted_shares_growth_3y_cagr": ("shares_outstanding", 3),
    "diluted_shares_growth_5y_cagr": ("shares_outstanding", 5),
}

QUARTER_ORDER = ["Q1", "Q2", "Q3", "Q4"]


# Materiality floors for the growth-rate engine -- added 2026-09-27 root-
# causing plausibility_check.py's net_income_growth_yoy/eps_growth_yoy/
# fcf_growth_yoy cluster (894/702/524 critical violations respectively).
# Traced a top offender (Infleqtion, Inc., CIK 0002007825) to a real,
# generalizable structural cause, not a mapping or arithmetic bug: a
# de-SPAC business-combination discontinuity. Infleqtion's Q1-Q3 2024
# `core.fact` rows are the PRE-MERGER BLANK-CHECK SHELL's own separately-
# filed 10-Qs (net_income as small as -$69 for Q3 2024 -- a real,
# correctly-extracted value for that real filing), while its FY2024 10-K
# (filed post-merger) uses reverse-merger accounting to report the real
# OPERATING COMPANY's full-year financials (~-$55.7M) -- and post-merger
# quarters (Q3 2025: -$33.4M) are the real operating company too. Verified
# against yfinance before concluding this: Yahoo's own quarterly series
# for INFQ starts only at 2025-03-31 (the first clean post-merger quarter)
# with 2024-12-31 returned as NaN -- Yahoo's own data provider evidently
# can't/doesn't produce a comparable pre-merger quarterly figure either,
# independently corroborating that Q3 2024's tiny shell value isn't a
# meaningful economic "prior year" for this company at all. The correct
# general fix generalizes doc's existing `sanity/timeseries_check.py`
# materiality-floor idiom (already applied to CONCEPT-level checks) to
# the growth-rate CALCULATION itself: when the prior-period base is too
# small to be a real operating-scale figure for a mapped concept, a YoY/
# CAGR ratio off it is mathematically well-defined but economically
# meaningless (483,836.84% for Infleqtion) -- correctly null it, the same
# "don't guess, exclude" discipline this project applies everywhere else,
# rather than storing a technically-correct but garbage number.
CONCEPT_MATERIALITY_FLOORS: dict[str, Decimal] = {
    "revenue": Decimal("1000000"),
    "net_income": Decimal("1000000"),
    "diluted_eps": Decimal("0.01"),
    "dividends_per_share": Decimal("0.01"),
    "shares_outstanding": Decimal("10000"),
}


def _growth_value(
    value_t: Decimal,
    value_prior: Decimal,
    lag_years: int,
    materiality_floor: Decimal = Decimal("0"),
) -> tuple[Decimal | None, str | None]:
    """Pure growth calculation shared by the SQL-backed growth job and its
    regression tests. Returns a value or an explicit null reason.
    `materiality_floor` (see CONCEPT_MATERIALITY_FLOORS) guards against a
    tiny/near-zero prior-period base producing a mathematically-correct
    but economically-meaningless ratio -- e.g. a pre-merger SPAC shell's
    trivial quarter used as the "prior year" for a real operating
    company's post-merger quarter."""
    if value_prior == 0:
        return None, "zero_base_value"
    if abs(value_prior) < materiality_floor:
        return None, "immaterial_prior_base"
    if lag_years == 1:
        return (value_t - value_prior) / value_prior, None
    ratio = value_t / value_prior
    if ratio < 0:
        return None, "negative_ratio_undefined_cagr"
    return ratio ** (Decimal(1) / Decimal(lag_years)) - 1, None


def _trailing_quarters(fiscal_year: int, fiscal_period: str) -> list[tuple[int, str]]:
    idx = QUARTER_ORDER.index(fiscal_period)
    seq: list[tuple[int, str]] = []
    y, i = fiscal_year, idx
    for _ in range(4):
        seq.append((y, QUARTER_ORDER[i]))
        i -= 1
        if i < 0:
            i = 3
            y -= 1
    return list(reversed(seq))


def _load_metric_ids(conn: psycopg.Connection) -> dict[str, int]:
    # Widened 2026-09-13 to include the 3 margin names too (MARGIN_CONCEPTS,
    # defined further below) -- purely additive, existing callers
    # (compute_growth/compute_ttm_returns) just get a couple of extra,
    # unused keys in the returned dict.
    with conn.cursor() as cur:
        cur.execute(
            "select metric_name, id from analytics.metric_definition where metric_name = any(%s)",
            (
                list(GROWTH_METRICS)
                + ["roic", "roe", "gross_margin", "operating_margin", "net_margin"],
            ),
        )
        return dict(cur.fetchall())


def _load_concept_id(conn: psycopg.Connection, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.canonical_concept where name = %s", (name,)
        )
        return cur.fetchone()[0]


class FactsByPeriod(dict):
    """(fiscal_year, fiscal_period) -> (value, fact_ids, period_start,
    period_end), plus `durations`: every duration fact for the concept,
    including the unlabeled 6-/9-month year-to-date spans the dict can't
    key. _ttm_sum's YTD fallback reads `durations`; any plain dict (other
    modules' own loaders) simply has no fallback."""

    durations: list[tuple]  # (start, end, value, fact_ids, source_concept_id)


def _load_company_facts(
    conn: psycopg.Connection, company_id: int, concept_id: int
) -> FactsByPeriod:
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.fiscal_year, p.fiscal_period, cf.value, cf.source_fact_ids, p.start_date, p.end_date,
                   (select f.concept_id from core.fact f where f.id = cf.source_fact_ids[1]) as source_concept_id
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s and cf.canonical_concept_id = %s
            """,
            (company_id, concept_id),
        )
        rows = cur.fetchall()
    out = FactsByPeriod(
        ((fy, fp), (val, fids, start, end))
        for fy, fp, val, fids, start, end, _src in rows
        if fp is not None
    )
    out.durations = [
        (start, end, val, fids, src)
        for _fy, _fp, val, fids, start, end, src in rows
        if (end - start).days >= YTD_MIN_SPAN_DAYS
    ]
    return out


def _compute_growth_for_company(
    conn: psycopg.Connection, company_id: int, metric_ids: dict[str, int]
) -> dict:
    rows: list[dict] = []
    for metric_name, (concept_name, lag_years) in GROWTH_METRICS.items():
        concept_id = _load_concept_id(conn, concept_name)
        by_period = _load_company_facts(conn, company_id, concept_id)
        materiality_floor = CONCEPT_MATERIALITY_FLOORS.get(concept_name, Decimal("0"))
        for (fy, fp), (value_t, fids_t, start_t, end_t) in by_period.items():
            prior_key = (fy - lag_years, fp)
            prior = by_period.get(prior_key)
            if prior is None:
                rows.append(
                    {
                        "company_id": company_id,
                        "metric_definition_id": metric_ids[metric_name],
                        "period_start": start_t,
                        "period_end": end_t,
                        "period_label": fp,
                        "value": None,
                        "is_null_reason": f"missing:prior_period({prior_key[0]}_{fp})",
                        "source_fact_ids": None,
                    }
                )
                continue
            value_prior, fids_prior, _s, _e = prior
            growth, growth_reason = _growth_value(
                value_t, value_prior, lag_years, materiality_floor
            )
            if growth_reason is not None:
                rows.append(
                    {
                        "company_id": company_id,
                        "metric_definition_id": metric_ids[metric_name],
                        "period_start": start_t,
                        "period_end": end_t,
                        "period_label": fp,
                        "value": None,
                        "is_null_reason": growth_reason,
                        "source_fact_ids": None,
                    }
                )
                continue
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_ids[metric_name],
                    "period_start": start_t,
                    "period_end": end_t,
                    "period_label": fp,
                    "value": growth,
                    "is_null_reason": None,
                    "source_fact_ids": list(fids_t) + list(fids_prior),
                }
            )

    with conn.cursor() as cur:
        metric_id_list = [metric_ids[m] for m in GROWTH_METRICS]
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s)",
            (company_id, metric_id_list),
        )
        if rows:
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
    return {
        "computed": sum(1 for r in rows if r["value"] is not None),
        "null": sum(1 for r in rows if r["value"] is None),
    }


def compute_growth(conn: psycopg.Connection, ciks: set[str]) -> dict:
    metric_ids = _load_metric_ids(conn)
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
            stats = _compute_growth_for_company(conn, company_id, metric_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "growth", exc)
            # safe_rollback() tolerates a dead connection (a real,
            # confirmed cascade found live 2026-09-27: a mid-batch
            # connection drop otherwise fails EVERY remaining company in
            # this call, not just one -- same class of bug already fixed
            # in concept_fallback.py/beneficial_ownership.py etc.).
            conn = safe_rollback(conn, stage="growth", cik=cik)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
        logger.info(
            "ttm.growth_done", cik=cik, computed=stats["computed"], null=stats["null"]
        )

    logger.info("ttm.growth.done", **totals)
    return totals


# --- TTM ROIC/ROE for quarterly periods ---

ROIC_CONCEPTS = {
    "operating_income": "nopat_base",
    "income_tax_expense": "tax_rate_numerator",
    "income_before_tax": "tax_rate_denominator",
}
ROE_CONCEPTS = {"net_income": "numerator"}
INSTANT_CONCEPTS = {
    "total_debt_resolved": "invested_capital_add",
    "stockholders_equity": ("invested_capital_add", "denominator"),
    "cash_and_equivalents": "invested_capital_subtract",
}


# YTD-based TTM (2026-09-29, founder suggestion). The four-quarter sum
# needs every discrete quarter, including a derived Q4 that only exists
# when FY and Q1-Q3 (or the 9-month YTD) are all authoritative. The
# standard alternative uses only as-filed cumulative figures:
#   TTM = latest YTD + prior full year - prior year's same-span YTD
# e.g. at Q3 FY2026: 9M FY2026 + FY2025 - 9M FY2025. Symbotic restated all
# of FY2025, so its FY2025 Q4 can never be derived, yet FY2025 and both
# 9-month spans exist. Used only when the four-quarter chain fails.
# All three pieces must come from the same XBRL tag: Plains GP's FY2025
# net income resolved from ProfitLoss ($1,686M, incl. noncontrolling
# interests) while its quarters and YTDs came from NetIncomeLoss ($259M
# for the year), so mixing them gave a $1,980M TTM against a real ~$554M.
YTD_MIN_SPAN_DAYS = 80  # durations only; instants (start == end) excluded
FULL_YEAR_SPAN_DAYS = (350, 380)
DATE_SLACK_DAYS = 3
PRIOR_YEAR_SLACK_DAYS = 8  # 52/53-week calendars shift a year by up to a week


def _one_value(candidates: list[tuple]) -> tuple | None:
    """The single (value, fact_ids) when every candidate agrees, else None."""
    if not candidates or len({c[0] for c in candidates}) != 1:
        return None
    return candidates[0]


def _ttm_from_ytd(
    durations: list[tuple], anchor_end
) -> tuple[Decimal | None, list[int]]:
    def near(a, b, days):
        return abs((a - b).days) <= days

    full_years = [
        d
        for d in durations
        if FULL_YEAR_SPAN_DAYS[0] <= (d[1] - d[0]).days <= FULL_YEAR_SPAN_DAYS[1]
    ]
    # A Q4 anchor's TTM is the fiscal year that ends with it.
    fy_now = _one_value(
        [
            (v, f, t)
            for s, e, v, f, t in full_years
            if near(e, anchor_end, DATE_SLACK_DAYS)
        ]
    )
    if fy_now is not None:
        return fy_now[0], list(fy_now[1])

    prior = [fy for fy in full_years if fy[1] < anchor_end]
    if not prior:
        return None, []
    p_start, p_end = max(prior, key=lambda fy: fy[1])[:2]
    if (anchor_end - p_end).days > FULL_YEAR_SPAN_DAYS[1]:
        return None, []
    prior_fy = _one_value(
        [(v, f, t) for s, e, v, f, t in full_years if s == p_start and e == p_end]
    )
    ytd = _one_value(
        [
            (v, f, t)
            for s, e, v, f, t in durations
            if near(s, p_end + timedelta(days=1), DATE_SLACK_DAYS)
            and near(e, anchor_end, DATE_SLACK_DAYS)
        ]
    )
    prior_ytd = _one_value(
        [
            (v, f, t)
            for s, e, v, f, t in durations
            if near(s, p_start, DATE_SLACK_DAYS)
            and near(e, anchor_end - timedelta(days=365), PRIOR_YEAR_SLACK_DAYS)
            and e < p_end
        ]
    )
    if prior_fy is None or ytd is None or prior_ytd is None:
        return None, []
    if len({prior_fy[2], ytd[2], prior_ytd[2]}) != 1:
        return None, []  # pieces from different XBRL tags don't subtract
    return (
        ytd[0] + prior_fy[0] - prior_ytd[0],
        list(ytd[1]) + list(prior_fy[1]) + list(prior_ytd[1]),
    )


def _ttm_sum(
    by_period: dict, fiscal_year: int, fiscal_period: str
) -> tuple[Decimal | None, list[int]]:
    needed = _trailing_quarters(fiscal_year, fiscal_period)
    total = Decimal(0)
    fact_ids: list[int] = []
    for key in needed:
        hit = by_period.get(key)
        if hit is None:
            break
        value, fids, _s, _e = hit
        total += value
        fact_ids.extend(fids)
    else:
        return total, fact_ids

    durations = getattr(by_period, "durations", None)
    anchor = by_period.get((fiscal_year, fiscal_period))
    if durations and anchor is not None:
        return _ttm_from_ytd(durations, anchor[3])
    return None, []


# --- TTM margins (2026-09-13) ---
#
# Found live doing a "close the saga" sanity sweep of the locked screener
# metrics against yfinance: net_margin sat at a 20% match rate, debt_to_
# equity-adjacent margins similarly poor -- not because net_income/revenue
# were wrong (both independently verified correct earlier the same day),
# but because net_margin/gross_margin/operating_margin were NEVER computed
# as a rolling trailing-twelve-month figure at all, only as a raw single-
# quarter ratio (calculate.py's generic engine, no FY_ONLY_METRICS entry).
# yfinance's own margin fields are always TTM. Confirmed by hand before
# building this: computing TTM net_income/revenue directly from our own
# already-verified canonical_fact data and dividing reproduced yfinance's
# reported margin almost exactly for several real companies (TOMI
# Environmental, RELIABILITY INC, ADM TRONICS -- all matched to 4+ decimal
# places), proving the underlying DATA was never the problem.
#
# Modeled directly on compute_ttm_returns (ROIC/ROE) above -- the identical
# shape of bug, already fixed once for those two metrics. Deliberately
# does NOT add net_margin/gross_margin/operating_margin to calculate.py's
# FY_ONLY_METRICS (unlike ROIC/ROE, a single quarter's margin is still a
# legitimate, real number worth showing on a quarterly-results trend --
# ROIC/ROE's quarterly figures are the ones that are genuinely nonsensical,
# an annualization-scale mismatch, not just "noisier than TTM"). Adding a
# TTM row is sufficient on its own: screener/resolve.py's existing
# TTM-preferred/latest-period_end rule already prefers it automatically
# the moment it exists, without needing the quarterly rows removed.
#
# Uses the *_resolved concepts (revenue_sanity_resolved, gross_profit_
# resolved, operating_income_resolved, net_income_resolved) -- the same
# ones verified/improved earlier the same session -- for the widest safe
# coverage, not the raw first_match/sum concepts calculate.py's own
# quarterly margins read.
MARGIN_CONCEPTS: dict[str, tuple[str, str]] = {
    "gross_margin": ("gross_profit_resolved", "revenue_sanity_resolved"),
    "operating_margin": ("operating_income_resolved", "revenue_sanity_resolved"),
    "net_margin": ("net_income_resolved", "revenue_sanity_resolved"),
}


def _compute_ttm_margins_for_company(
    conn: psycopg.Connection,
    company_id: int,
    metric_ids: dict[str, int],
    concept_ids: dict[str, int],
) -> dict:
    by_concept = {
        name: _load_company_facts(conn, company_id, cid)
        for name, cid in concept_ids.items()
    }
    revenue_by_period = by_concept["revenue_sanity_resolved"]

    quarter_keys: set[tuple[int, str]] = set()
    for numerator_name, _ in MARGIN_CONCEPTS.values():
        quarter_keys |= {k for k in by_concept[numerator_name] if k[1] in QUARTER_ORDER}

    rows: list[dict] = []
    # Found live 2026-09-13/14, the first population run: a real, if rare,
    # instance of the "two quarters share an end_date" trap this whole
    # session has hit repeatedly elsewhere (Nike's FY/Q4, MSGS's
    # overlapping durations) -- TRANSCAT INC has a genuine Q1 2012
    # (2012-01-01 to 2012-03-31) AND a genuine Q4 2012 (2011-12-25 to
    # 2012-03-31), both real, both ending 2012-03-31, from a fiscal-
    # calendar realignment. metric_value's unique constraint is on
    # (company_id, metric_definition_id, period_start, period_end,
    # period_label), not fiscal_year/fiscal_period, so inserting a TTM row
    # for both crashed with a duplicate-key violation and silently
    # stranded the whole company (errored=1, zero margin rows) rather than
    # writing anything. Iterate a sorted, deterministic key order and skip
    # a (fy, fp) whose (metric_definition_id, period_end) was already
    # claimed by an earlier key in this same pass -- the same "keep one,
    # don't crash" idiom already used for metric_value's own historical
    # duplicate-row cleanup (see pipeline/CLAUDE.md's 2026-08-31 entry).
    claimed_period_ends: set[tuple[int, object]] = set()
    for fy, fp in sorted(quarter_keys):
        end_date = None
        for numerator_name, _ in MARGIN_CONCEPTS.values():
            hit = by_concept[numerator_name].get((fy, fp))
            if hit is not None:
                end_date = hit[3]
                break
        start_date = end_date

        for metric_name, (numerator_name, _denominator_name) in MARGIN_CONCEPTS.items():
            metric_id = metric_ids[metric_name]
            claim_key = (metric_id, end_date)
            if claim_key in claimed_period_ends:
                continue
            claimed_period_ends.add(claim_key)

            ttm_numerator, fids_num = _ttm_sum(by_concept[numerator_name], fy, fp)
            ttm_revenue, fids_rev = _ttm_sum(revenue_by_period, fy, fp)
            if ttm_numerator is None or ttm_revenue is None:
                missing = (
                    numerator_name
                    if ttm_numerator is None
                    else "revenue_sanity_resolved"
                )
                value, reason, fids = None, f"incomplete:{missing}", None
            elif ttm_revenue == 0:
                value, reason, fids = None, "zero_denominator", None
            else:
                value = ttm_numerator / ttm_revenue
                reason, fids = None, fids_num + fids_rev
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_id,
                    "period_start": start_date,
                    "period_end": end_date,
                    "period_label": "TTM",
                    "value": value,
                    "is_null_reason": reason,
                    "source_fact_ids": fids,
                }
            )

    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s) and period_label = 'TTM'",
            (company_id, [metric_ids[m] for m in MARGIN_CONCEPTS]),
        )
        if rows:
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
    return {
        "computed": sum(1 for r in rows if r["value"] is not None),
        "null": sum(1 for r in rows if r["value"] is None),
    }


def compute_ttm_margins(conn: psycopg.Connection, ciks: set[str]) -> dict:
    metric_ids = _load_metric_ids(conn)
    concept_names = {name for pair in MARGIN_CONCEPTS.values() for name in pair}
    concept_ids = {name: _load_concept_id(conn, name) for name in concept_names}
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
            stats = _compute_ttm_margins_for_company(
                conn, company_id, metric_ids, concept_ids
            )
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "ttm_margins", exc)
            conn = safe_rollback(conn, stage="ttm_margins", cik=cik)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]

    logger.info("ttm.margins.done", **totals)
    return totals


def _compute_ttm_returns_for_company(
    conn: psycopg.Connection,
    company_id: int,
    metric_ids: dict[str, int],
    concept_ids: dict[str, int],
) -> dict:
    by_concept = {
        name: _load_company_facts(conn, company_id, cid)
        for name, cid in concept_ids.items()
    }
    # Instant facts indexed by end_date for matching against a quarter's own balance-sheet date.
    instant_by_end_date = {}
    for name in ("total_debt_resolved", "stockholders_equity", "cash_and_equivalents"):
        instant_by_end_date[name] = {
            end: (val, fids)
            for (_fy, _fp), (val, fids, _s, end) in by_concept[name].items()
        }

    # Every (fiscal_year, Q1-4) this company has ANY operating_income or net_income for.
    quarter_keys = {
        k for k in by_concept["operating_income"] if k[1] in QUARTER_ORDER
    } | {k for k in by_concept["net_income"] if k[1] in QUARTER_ORDER}

    rows: list[dict] = []
    for fy, fp in quarter_keys:
        end_date = (
            by_concept["operating_income"].get((fy, fp))
            or by_concept["net_income"].get((fy, fp))
        )[3]
        start_date = end_date  # TTM window end; period_start intentionally same as end for a "TTM as of" marker

        # ROIC (TTM)
        ttm_op_income, fids_op = _ttm_sum(by_concept["operating_income"], fy, fp)
        ttm_tax_num, fids_tax_num = _ttm_sum(by_concept["income_tax_expense"], fy, fp)
        ttm_tax_denom, fids_tax_denom = _ttm_sum(
            by_concept["income_before_tax"], fy, fp
        )
        debt_hit = instant_by_end_date["total_debt_resolved"].get(end_date)
        equity_hit = instant_by_end_date["stockholders_equity"].get(end_date)
        cash_hit = instant_by_end_date["cash_and_equivalents"].get(end_date)

        if None in (ttm_op_income, ttm_tax_num, ttm_tax_denom) or None in (
            debt_hit,
            equity_hit,
            cash_hit,
        ):
            missing = []
            if ttm_op_income is None:
                missing.append("ttm_operating_income")
            if ttm_tax_num is None:
                missing.append("ttm_income_tax_expense")
            if ttm_tax_denom is None:
                missing.append("ttm_income_before_tax")
            if debt_hit is None:
                missing.append("total_debt_resolved")
            if equity_hit is None:
                missing.append("stockholders_equity")
            if cash_hit is None:
                missing.append("cash_and_equivalents")
            roic_value, roic_reason, roic_fids = (
                None,
                f"incomplete:{','.join(missing)}",
                None,
            )
        else:
            tax_rate = ttm_tax_num / ttm_tax_denom if ttm_tax_denom != 0 else None
            if tax_rate is None:
                roic_value, roic_reason, roic_fids = None, "zero_pretax_income", None
            else:
                nopat = ttm_op_income * (1 - tax_rate)
                invested_capital = debt_hit[0] + equity_hit[0] - cash_hit[0]
                if invested_capital == 0:
                    roic_value, roic_reason, roic_fids = (
                        None,
                        "zero_invested_capital",
                        None,
                    )
                else:
                    roic_value = nopat / invested_capital
                    roic_reason = None
                    roic_fids = (
                        fids_op
                        + fids_tax_num
                        + fids_tax_denom
                        + list(debt_hit[1])
                        + list(equity_hit[1])
                        + list(cash_hit[1])
                    )

        rows.append(
            {
                "company_id": company_id,
                "metric_definition_id": metric_ids["roic"],
                "period_start": start_date,
                "period_end": end_date,
                "period_label": "TTM",
                "value": roic_value,
                "is_null_reason": roic_reason,
                "source_fact_ids": roic_fids,
            }
        )

        # ROE (TTM)
        ttm_net_income, fids_ni = _ttm_sum(by_concept["net_income"], fy, fp)
        if ttm_net_income is None or equity_hit is None:
            roe_value = None
            roe_reason = (
                "incomplete:ttm_net_income"
                if ttm_net_income is None
                else "incomplete:stockholders_equity"
            )
            roe_fids = None
        elif equity_hit[0] == 0:
            roe_value, roe_reason, roe_fids = None, "zero_denominator", None
        else:
            roe_value = ttm_net_income / equity_hit[0]
            roe_reason = None
            roe_fids = fids_ni + list(equity_hit[1])

        rows.append(
            {
                "company_id": company_id,
                "metric_definition_id": metric_ids["roe"],
                "period_start": start_date,
                "period_end": end_date,
                "period_label": "TTM",
                "value": roe_value,
                "is_null_reason": roe_reason,
                "source_fact_ids": roe_fids,
            }
        )

    with conn.cursor() as cur:
        cur.execute(
            """
                delete from analytics.metric_value
                where company_id = %s and metric_definition_id = any(%s) and period_label = 'TTM'
                """,
            (company_id, [metric_ids["roic"], metric_ids["roe"]]),
        )
        if rows:
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
    return {
        "computed": sum(1 for r in rows if r["value"] is not None),
        "null": sum(1 for r in rows if r["value"] is None),
    }


def compute_ttm_returns(conn: psycopg.Connection, ciks: set[str]) -> dict:
    metric_ids = _load_metric_ids(conn)
    concept_ids = {
        name: _load_concept_id(conn, name)
        for name in (
            "operating_income",
            "income_tax_expense",
            "income_before_tax",
            "net_income",
            "total_debt_resolved",
            "stockholders_equity",
            "cash_and_equivalents",
        )
    }
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
            stats = _compute_ttm_returns_for_company(
                conn, company_id, metric_ids, concept_ids
            )
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "ttm_returns", exc)
            conn = safe_rollback(conn, stage="ttm_returns", cik=cik)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]
        logger.info(
            "ttm.returns_done", cik=cik, computed=stats["computed"], null=stats["null"]
        )

    logger.info("ttm.returns.done", **totals)
    return totals
