"""Metric Plausibility Check (2026-09-27) -- the code-side implementation
of doc/reference/47_Scrooner_Metric_Plausibility_Gates.md. Zero external
calls (same family as sanity/timeseries_check.py) -- checks each
company's MOST RECENT value per metric against a CRITICAL/WATCH range
grounded in the real, live distribution of that metric across the whole
population (the percentile query preserved in doc/learnings/
2026-09-27-metric-plausibility-gates.md).

Three kinds of check, matching doc 47's own §1-§8 structure:

1. ABSOLUTE_BOUNDS -- most metrics (margins, returns, multiples, yields,
   per-share figures, growth rates): a fixed (critical_min, critical_max,
   watch_min, watch_max) range. `None` on either side means unbounded
   there. Deliberately wide on CRITICAL (a real distressed or
   hyper-growth company must never trip it) and narrower on WATCH
   (statistically unusual, worth a look, not necessarily wrong).
2. EXACT_SET_METRICS -- Piotroski score and the 3 boolean quality flags:
   valid values are a small fixed set (or null, always allowed). Any
   OTHER value is a code bug, not a data question.
3. RELATIVE_CHECKS -- doc 47 §6: metrics with no safe universal number
   (aggregate dollar amounts, reconciliation gaps) are checked against
   the SAME company's own Revenue or Total Assets instead of a fixed
   constant -- a magnitude only makes sense relative to company size.

Never writes back a "fix" -- same observer role as every other checker
in sanity/. A violation means "go look at this company's filing," never
"clamp or discard the value.\""""

from decimal import Decimal, InvalidOperation

import psycopg
import structlog

logger = structlog.get_logger()

SEVERITY_OK = "ok"
SEVERITY_WATCH = "watch"
SEVERITY_CRITICAL = "critical"

# metric_name -> (critical_min, critical_max, watch_min, watch_max), all
# Decimal or None (unbounded on that side). Transcribed directly from
# doc 47's §1-§5, §7, §8 tables -- keep in sync if that doc's numbers
# change; this dict is the executable source of truth going forward,
# the doc is the evidence/rationale for how each number was picked.
_D = Decimal
ABSOLUTE_BOUNDS: dict[
    str, tuple[Decimal | None, Decimal | None, Decimal | None, Decimal | None]
] = {
    # -- Section 1: margins and returns --
    "gross_margin": (_D("-10"), _D("2"), _D("-2"), _D("1.05")),
    "operating_margin": (_D("-20"), _D("5"), _D("-5"), _D("1")),
    "net_margin": (_D("-30"), _D("10"), _D("-10"), _D("2")),
    "pretax_margin": (_D("-30"), _D("10"), _D("-10"), _D("2")),
    "ebitda_margin": (_D("-30"), _D("10"), _D("-5"), _D("2")),
    "fcf_margin": (_D("-30"), _D("10"), _D("-5"), _D("2")),
    "roe": (_D("-10"), _D("10"), _D("-2"), _D("2")),
    "roa": (_D("-5"), _D("5"), _D("-1"), _D("1")),
    "roic": (_D("-10"), _D("10"), _D("-2"), _D("2")),
    "interest_coverage_ratio": (_D("-5000"), _D("5000"), _D("-500"), _D("500")),
    # -- Section 2: liquidity and leverage --
    "current_ratio": (_D("0"), _D("1000"), _D("0.1"), _D("50")),
    "quick_ratio": (_D("0"), _D("1000"), _D("0.1"), _D("20")),
    "debt_to_equity": (_D("-2000"), _D("2000"), _D("-50"), _D("50")),
    "debt_to_ebitda": (_D("-2000"), _D("2000"), _D("-50"), _D("50")),
    "net_debt_ebitda": (_D("-2000"), _D("2000"), _D("-50"), _D("50")),
    # -- Section 3: valuation multiples --
    "trailing_pe": (_D("-2000"), _D("2000"), _D("-200"), _D("200")),
    "price_to_book": (_D("-10000"), _D("10000"), _D("-500"), _D("500")),
    "price_to_sales": (_D("0"), _D("10000"), _D("0"), _D("200")),
    "ev_ebitda": (_D("-10000"), _D("10000"), _D("-500"), _D("500")),
    "ev_sales": (_D("-500"), _D("10000"), _D("0"), _D("300")),
    "peg_ratio": (_D("-500"), _D("500"), _D("-50"), _D("50")),
    # -- Section 4: yield / capital-return ratios --
    "dividend_yield": (_D("0"), _D("1"), _D("0"), _D("0.20")),
    "fcf_yield": (_D("-10"), _D("10"), _D("-1"), _D("1")),
    "buyback_yield": (_D("-10"), _D("10"), _D("-1"), _D("1")),
    "total_shareholder_yield": (_D("-20"), _D("20"), _D("-2"), _D("2")),
    "institutional_ownership_pct": (_D("0"), _D("1"), _D("0"), _D("0.98")),
    # -- Section 5: expense ratios, dilution, per-share --
    "sga_pct_revenue": (_D("-1"), _D("1000"), _D("0"), _D("5")),
    "rnd_intensity": (_D("-1"), _D("1000"), _D("0"), _D("5")),
    "capex_pct_revenue": (_D("-1"), _D("1000"), _D("0"), _D("5")),
    "sbc_pct_revenue": (_D("-1"), _D("1000"), _D("0"), _D("5")),
    "goodwill_pct_assets": (_D("0"), _D("1"), _D("0"), _D("0.85")),
    "eps_dilution_spread": (_D("-2"), _D("1"), _D("-0.1"), _D("0.5")),
    "share_dilution_trend": (_D("-1"), _D("20"), _D("-0.5"), _D("3")),
    "diluted_shares_growth_yoy": (_D("-1"), _D("20"), _D("-0.5"), _D("3")),
    "book_value_per_share": (_D("-100000"), _D("100000"), _D("-1000"), _D("1000")),
    "fcf_per_share": (_D("-100000"), _D("100000"), _D("-1000"), _D("1000")),
    "net_cash_per_share": (_D("-100000"), _D("100000"), _D("-1000"), _D("1000")),
    # market_cap has no relative denominator issue (it IS the denominator
    # for several other ratios) -- a flat ceiling is the real-world
    # anchor doc 47 §6 names (no US company has exceeded ~$6T as of
    # 2026); floor excludes exactly $0 for an active, trading company.
    "market_cap": (_D("0.01"), _D("6000000000000"), _D("1000000"), _D("4000000000000")),
    # -- Section 7: growth rates / CAGRs, one shared rule --
    # Hard floor -100% (-1): a company cannot lose more than 100% of a
    # positive quantity, so anything below -1 is a certain formula bug,
    # never a real result, regardless of how extreme a real turnaround
    # or hyper-growth swing can legitimately be on the upside.
    **{
        name: (_D("-1"), _D("1000"), _D("-0.9"), _D("20"))
        for name in (
            "revenue_growth_yoy",
            "revenue_growth_3y_cagr",
            "revenue_growth_5y_cagr",
            "revenue_growth_10y_cagr",
            "eps_growth_yoy",
            "eps_growth_3y_cagr",
            "eps_growth_5y_cagr",
            "eps_growth_10y_cagr",
            "net_income_growth_yoy",
            "net_income_growth_3y_cagr",
            "net_income_growth_5y_cagr",
            "net_income_growth_10y_cagr",
            "fcf_growth_yoy",
            "fcf_growth_3y_cagr",
            "fcf_growth_5y_cagr",
            "dps_growth_yoy",
            "dps_growth_3y_cagr",
            "diluted_shares_growth_3y_cagr",
            "diluted_shares_growth_5y_cagr",
        )
    },
    # -- Section 8: streaks --
    # ORIGINAL bound here was (0, 15, 0, 12), based on a wrong assumption
    # that fundamentals data is bounded by doc 38's 2015-01-01 floor.
    # That floor is specific to OWNERSHIP data (Form 13F/13G refiling
    # cadence reasoning) -- fundamentals (core.fact/canonical_fact) are
    # NOT bounded there at all. Found live 2026-09-27, first real run:
    # 348 "critical" violations were EVERY major stable blue-chip
    # (Procter & Gamble, Apple, IBM, Kimberly-Clark, Hershey, Abbott,
    # Colgate-Palmolive...) -- confirmed Apple's own real net_income data
    # runs FY2007-FY2025 (19 real years), and 1,611 companies population-
    # wide have real FY data before 2010, some back to 1992. A 19-21
    # year unbroken profitable streak for one of these companies is a
    # real, correct number, not a bug -- these are exactly the
    # companies famous for decades of uninterrupted profitability.
    # Real observed max across the population is exactly 20 (percentile_
    # cont 99.9% = 19) -- widened critical to 40 (double the real max,
    # generous headroom for a company with even older data) and watch to
    # 22 (just above the real max, so THIS population's own longest real
    # streaks don't sit right at the edge of "worth a look").
    "profitable_streak_years": (_D("0"), _D("40"), _D("0"), _D("22")),
    "dividend_growth_streak_years": (_D("0"), _D("40"), _D("0"), _D("22")),
}

# Exact-set metrics: any value outside this set (besides null, always
# allowed -- a real, meaningful "insufficient data" state per each
# module's own docstring) is CRITICAL, no WATCH tier.
EXACT_SET_METRICS: dict[str, set[Decimal]] = {
    "piotroski_f_score": {Decimal(i) for i in range(10)},
    "fcf_gt_net_income": {Decimal(0), Decimal(1)},
    "zero_debt": {Decimal(0), Decimal(1)},
    "margin_expanding_3yr": {Decimal(0), Decimal(1)},
}

# doc 47 §6: metric_name -> (denominator_concept_name, multiplier,
# description). Denominator is the LATEST canonical_fact value under
# that *_resolved concept for the same company -- if the denominator
# itself is missing/zero, the check is skipped (silent, not a finding --
# an implausible-ratio-of-nothing is not a meaningful signal either way,
# same reasoning as sanity/yfinance_check.py's own DEGENERACY_GUARD).
RELATIVE_CHECKS: dict[str, tuple[str, Decimal, str]] = {
    "ebitda": ("revenue_sanity_resolved", _D("3"), "> 3x TTM revenue"),
    "fcf": ("revenue_sanity_resolved", _D("3"), "> 3x TTM revenue"),
    "net_interest_income": ("revenue_sanity_resolved", _D("1"), "> 1x TTM revenue"),
    "cash_returned_to_shareholders": (
        "revenue_sanity_resolved",
        _D("1"),
        "> 1x TTM revenue",
    ),
    "working_capital": ("total_assets_resolved", _D("2"), "> 2x total assets"),
    "net_cash": ("total_assets_resolved", _D("2"), "> 2x total assets"),
    "net_change_in_cash": ("total_assets_resolved", _D("2"), "> 2x total assets"),
    "ar_change_reconciliation_gap": (
        "revenue_sanity_resolved",
        _D("0.10"),
        "> 10% of TTM revenue",
    ),
    "ap_change_reconciliation_gap": (
        "revenue_sanity_resolved",
        _D("0.10"),
        "> 10% of TTM revenue",
    ),
    "inventory_change_reconciliation_gap": (
        "revenue_sanity_resolved",
        _D("0.10"),
        "> 10% of TTM revenue",
    ),
}
# effective_tax_rate_gap is already a plain fraction (not a dollar
# amount), so it gets a normal ABSOLUTE_BOUNDS entry instead of a
# relative one.
ABSOLUTE_BOUNDS["effective_tax_rate_gap"] = (_D("-5"), _D("5"), _D("-0.5"), _D("0.5"))


def check_absolute(value: Decimal, bounds: tuple) -> tuple[str, str | None]:
    """Pure, no DB access -- unit-testable in isolation."""
    crit_min, crit_max, watch_min, watch_max = bounds
    if (crit_min is not None and value < crit_min) or (
        crit_max is not None and value > crit_max
    ):
        return (
            SEVERITY_CRITICAL,
            f"value {value} outside critical range [{crit_min}, {crit_max}]",
        )
    if (watch_min is not None and value < watch_min) or (
        watch_max is not None and value > watch_max
    ):
        return (
            SEVERITY_WATCH,
            f"value {value} outside typical range [{watch_min}, {watch_max}]",
        )
    return SEVERITY_OK, None


def check_exact_set(value: Decimal, valid: set[Decimal]) -> tuple[str, str | None]:
    if value in valid:
        return SEVERITY_OK, None
    return SEVERITY_CRITICAL, f"value {value} not in the valid set {sorted(valid)}"


def check_relative(
    value: Decimal, denominator: Decimal | None, multiplier: Decimal, description: str
) -> tuple[str, str | None] | None:
    """Returns None (skip, not a finding) when the denominator itself is
    missing or zero -- an implausible-ratio-of-nothing isn't a meaningful
    signal, same reasoning as the DEGENERACY_GUARD in yfinance_check.py."""
    if denominator is None or denominator == 0:
        return None
    if abs(value) > multiplier * abs(denominator):
        return (
            SEVERITY_CRITICAL,
            f"abs(value)={abs(value)} exceeds {description} (denominator={denominator})",
        )
    return SEVERITY_OK, None


def _load_latest_metric_values(
    conn: psycopg.Connection, metric_names: list[str]
) -> list[tuple]:
    """(company_id, metric_definition_id, metric_name, period_label,
    period_end, value) for the MOST RECENT non-null value per (company,
    metric) -- TTM-preferred/latest-period_end, the same rule
    screener/resolve.py and apps/app's own getLatestMetrics already use.
    One bulk query, not a query per company (pipeline/CLAUDE.md's own
    N+1 lesson)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with ranked as (
                select mv.company_id, mv.metric_definition_id, md.metric_name,
                       mv.period_label, mv.period_end, mv.value,
                       row_number() over (
                           partition by mv.company_id, mv.metric_definition_id
                           order by (mv.period_label = 'TTM') desc, mv.period_end desc
                       ) as rn
                from analytics.metric_value mv
                join analytics.metric_definition md on md.id = mv.metric_definition_id
                where mv.value is not null and md.metric_name = any(%s)
            )
            select company_id, metric_definition_id, metric_name, period_label, period_end, value
            from ranked where rn = 1
            """,
            (metric_names,),
        )
        return cur.fetchall()


def _load_latest_concept_values(
    conn: psycopg.Connection, concept_names: list[str]
) -> dict[tuple[int, str], Decimal]:
    """(company_id, concept_name) -> latest canonical_fact value -- the
    denominator lookup for RELATIVE_CHECKS. Same latest-period_end rule,
    concept side (no TTM label to prefer -- canonical_fact is point-in-time
    by period, not a metric_value row)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with ranked as (
                select cf.company_id, cc.name as concept_name, cf.value,
                       row_number() over (
                           partition by cf.company_id, cc.name order by p.end_date desc
                       ) as rn
                from analytics.canonical_fact cf
                join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
                join core.period p on p.id = cf.period_id
                where cc.name = any(%s)
            )
            select company_id, concept_name, value from ranked where rn = 1
            """,
            (concept_names,),
        )
        return {
            (company_id, concept_name): value
            for company_id, concept_name, value in cur.fetchall()
        }


_UPSERT_SQL = """
    insert into analytics.metric_plausibility_check
        (company_id, metric_definition_id, period_label, period_end, value, severity, note, checked_at)
    values (%(company_id)s, %(metric_definition_id)s, %(period_label)s, %(period_end)s, %(value)s, %(severity)s, %(note)s, now())
    on conflict (company_id, metric_definition_id) do update
        set period_label = excluded.period_label, period_end = excluded.period_end,
            value = excluded.value, severity = excluded.severity, note = excluded.note, checked_at = now()
"""


def run_all(conn: psycopg.Connection) -> dict:
    """Checks every metric this module has a rule for (ABSOLUTE_BOUNDS +
    EXACT_SET_METRICS + RELATIVE_CHECKS), full active population, one
    pass. Pure local SQL -- no external calls, safe to run daily against
    everyone (same reasoning as timeseries_check.py's own run_all)."""
    stats = {
        "considered": 0,
        SEVERITY_OK: 0,
        SEVERITY_WATCH: 0,
        SEVERITY_CRITICAL: 0,
        "skipped_no_denominator": 0,
    }

    all_metric_names = (
        list(ABSOLUTE_BOUNDS) + list(EXACT_SET_METRICS) + list(RELATIVE_CHECKS)
    )
    rows = _load_latest_metric_values(conn, all_metric_names)

    # Scoped to every metric_definition_id this module checks AT ALL
    # (not just ones with a row this run) -- otherwise a metric that
    # happens to have zero non-null values in one run would leave its
    # OWN stale prior-run findings un-deleted, the same "shared-table
    # delete must be scoped identically to what could have been written"
    # trap pipeline/CLAUDE.md documents repeatedly (resolve.py, Mapper
    # Day 6, timeseries_check.py's own company_id-scoping fix).
    with conn.cursor() as cur:
        cur.execute(
            "select id from analytics.metric_definition where metric_name = any(%s)",
            (all_metric_names,),
        )
        all_metric_definition_ids = [r[0] for r in cur.fetchall()]

    denominators: dict[tuple[int, str], Decimal] = {}
    if RELATIVE_CHECKS:
        concept_names = sorted({c for c, _m, _d in RELATIVE_CHECKS.values()})
        denominators = _load_latest_concept_values(conn, concept_names)

    findings = []
    for (
        company_id,
        metric_definition_id,
        metric_name,
        period_label,
        period_end,
        value,
    ) in rows:
        stats["considered"] += 1
        try:
            value = Decimal(value)
        except (InvalidOperation, TypeError):
            continue  # not a finite, comparable number -- nothing to check

        if metric_name in EXACT_SET_METRICS:
            result = check_exact_set(value, EXACT_SET_METRICS[metric_name])
        elif metric_name in RELATIVE_CHECKS:
            concept_name, multiplier, description = RELATIVE_CHECKS[metric_name]
            denominator = denominators.get((company_id, concept_name))
            result = check_relative(value, denominator, multiplier, description)
            if result is None:
                stats["skipped_no_denominator"] += 1
                continue
        else:
            result = check_absolute(value, ABSOLUTE_BOUNDS[metric_name])

        severity, note = result
        stats[severity] += 1
        findings.append(
            {
                "company_id": company_id,
                "metric_definition_id": metric_definition_id,
                "period_label": period_label,
                "period_end": period_end,
                "value": value,
                "severity": severity,
                "note": note,
            }
        )

    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.metric_plausibility_check where metric_definition_id = any(%s)",
            (all_metric_definition_ids,),
        )
        if findings:
            cur.executemany(_UPSERT_SQL, findings)
    conn.commit()

    logger.info("plausibility_check.done", **stats)
    return stats
