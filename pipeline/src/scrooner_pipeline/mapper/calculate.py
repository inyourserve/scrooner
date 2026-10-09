"""Stage 3d -- Point-in-time metric calculation (doc 11). Computes
analytics.metric_value for the 10 EDGAR-only, non-growth metrics (of the
12 EDGAR-only metrics in doc 02, Revenue Growth and EPS Growth are
TTM/multi-period by nature -- Stage 3e's job, not this one's; the 6
price-dependent metrics stay undefined here entirely, per requires_price).

Reads only analytics.canonical_fact (Stage 3b's output) plus
analytics.metric_definition/metric_definition_input (Stage 3c's output) --
never reads core.fact directly, so a fact's authoritative/superseded
status is already resolved by the time this stage sees it.

Every metric here is one of three formula shapes (see FORMULA_SHAPES):
- ratio: sum(numerator inputs) / sum(denominator inputs)
- sum_diff: sum(add inputs) - sum(subtract inputs)
- sum_diff_ratio: (sum(add) - sum(subtract)) / sum(denominator)   [fcf_margin]
- roic: the one genuinely custom formula, per Stage 3c's pinned definition

ROIC and ROE are restricted to FY periods only -- Stage 3c found live that
naively computing either from a bare quarter produces a badly misleading
number (AAPL: 127.8% vs a sane 31.95% ROIC, from a single strong quarter
naively annualized). Every other metric here is flow/flow or point-in-
time/point-in-time and has no such restriction.

Duration-vs-instant period matching (found live 2026-08-16, fixed before
any wrong metric_value shipped): a metric mixing a duration concept
(net_income, an income-statement flow) with an instant concept
(stockholders_equity, a balance-sheet snapshot) cannot match them by
period_id -- AAPL's FY2024 net_income has period_id 601
(2023-10-01..2024-09-28, duration) while its FY2024 stockholders_equity
has period_id 797 (2024-09-28..2024-09-28, instant) -- genuinely different
period rows even though both represent "AAPL FY2024." A naive period_id
match made ROE/ROIC silently null even when every input actually existed.
Fixed: for a metric with any duration input, anchor on the duration
period(s) present and look up instant inputs by END DATE matching the
duration period's end_date, not by period_id. core.concept has no
explicit period-type-per-concept flag, but canonical_concept.statement
already encodes it losslessly: 'balance_sheet' is always instant,
'income_statement'/'cash_flow' are always duration -- verified true for
all 17 canonical concepts, used directly rather than adding a new column.

A metric gets a metric_value row for every period where AT LEAST ONE of
its required inputs resolves -- not literally every period the company
has any data for. If some but not all required inputs are present for
that period, the row is written with value=null and is_null_reason set to
exactly which concept(s) were missing -- a null is a traceable outcome
(doc 04), never silence.

**This module is the orchestration "tree root" only, as of 2026-09-28.**
It has grown to 6 formula shapes since the "three formula shapes" note
above was written (ratio/sum_diff/sum_diff_ratio/additive/days/roic) --
each one's own math now lives in its own module under
`mapper/calculate_shapes/`, one "sub-tree node" per shape, registered in
that package's own SHAPE_REGISTRY. This file itself only: loads which
metrics to compute (`_load_target_metrics`), loads a company's already-
resolved facts (`_load_canonical_facts`), matches duration/instant
periods to each metric's anchor period, dispatches to the right shape
via `_compute()` (a thin re-export of `calculate_shapes.compute`), and
writes the results. See `calculate_shapes/__init__.py`'s own docstring
for the full rationale -- the same "registry, not a hardcoded if/elif
chain a human has to remember to extend" principle already proven for
`CONCEPT_MATERIALITY_FLOORS` (also now in `calculate_shapes/
materiality.py`) and for `mapper/main_calculator.py`'s own
module-level registry (doc 42), applied one layer further in.
"""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback
from scrooner_pipeline.mapper.calculate_shapes import (
    CONCEPT_MATERIALITY_FLOORS,
    compute as _compute,
)

logger = structlog.get_logger()

# Re-exported for backward compatibility -- existing callers/tests that
# import CONCEPT_MATERIALITY_FLOORS or _compute directly from this
# module keep working unchanged. The real source of truth for both is
# now mapper/calculate_shapes/ (see that package's own __init__.py
# docstring for the 2026-09-28 "one sub-tree node per formula shape"
# refactor rationale) -- this module is the orchestration "tree root"
# only: loading targets/facts, period matching, dispatching to the
# right shape via _compute(), and writing analytics.metric_value.

# Growth metrics are TTM/multi-period -- Stage 3e's job. Price-dependent
# metrics are excluded via metric_definition.requires_price, not this list.
DEFERRED_TO_STAGE_3E = {
    "revenue_growth_yoy",
    "revenue_growth_3y_cagr",
    "eps_growth_yoy",
    "eps_growth_3y_cagr",
    # 5Y/10Y CAGR added 2026-08-19 -- same Stage 3e (ttm.py) computation
    # path as the original 4, just wider GROWTH_METRICS lag_years.
    "revenue_growth_5y_cagr",
    "revenue_growth_10y_cagr",
    "eps_growth_5y_cagr",
    "eps_growth_10y_cagr",
    # dps_growth_yoy/3y_cagr added 2026-08-29 -- same ttm.py GROWTH_METRICS mechanism.
    "dps_growth_yoy",
    "dps_growth_3y_cagr",
    # net_income_growth_*/diluted_shares_growth_* added 2026-09-05
    # (financials display spec) -- same ttm.py GROWTH_METRICS mechanism,
    # net_income and shares_outstanding are both real canonical_fact
    # concepts so this needed zero new logic, only new dict entries.
    "net_income_growth_yoy",
    "net_income_growth_3y_cagr",
    "net_income_growth_5y_cagr",
    "net_income_growth_10y_cagr",
    "diluted_shares_growth_yoy",
    "diluted_shares_growth_3y_cagr",
    "diluted_shares_growth_5y_cagr",
}

# net_debt_ebitda is requires_price=false (it genuinely doesn't need
# price) but its denominator (ebitda) lives in analytics.metric_value,
# not canonical_fact -- this engine can't reach it, so it's computed in
# mapper/expanded_metrics.py instead. Found live 2026-08-18: without this
# exclusion, _load_target_metrics picks it up (matches the
# requires_price=false filter) and crashes with KeyError on
# FORMULA_SHAPES[metric_name] for every company, since it deliberately
# has no shape entry and zero metric_definition_input rows.
DEFERRED_TO_EXPANDED_METRICS = {
    "net_debt_ebitda",
    "institutional_ownership_pct",
    "cash_conversion_cycle",
    "share_dilution_trend",
    "piotroski_f_score",
    "fcf_gt_net_income",
    "zero_debt",
    "profitable_streak_years",
    "margin_expanding_3yr",
    # These 3 are actually computed in mapper/reconciliation.py, not
    # expanded_metrics.py -- grouped into this same set anyway since its
    # real meaning is "not handled by this engine's FORMULA_SHAPES", not
    # literally "lives in expanded_metrics.py". Added 2026-08-21 in the
    # SAME edit as their metric_definition rows (expanded_definitions.py)
    # -- this project has hit the "forgot to defer, next calculate() run
    # crashes with a bare KeyError" bug twice already (net_debt_ebitda,
    # share_dilution_trend), see pipeline/CLAUDE.md.
    "ar_change_reconciliation_gap",
    "inventory_change_reconciliation_gap",
    "ap_change_reconciliation_gap",
    # Added 2026-08-22 (P0/coverage execution pass) -- computed in
    # mapper/tax_reconciliation.py, mapper/fcf_growth.py, and
    # mapper/dividend_streak.py respectively, same "same-edit as the
    # metric_definition row" rule as above.
    "effective_tax_rate_gap",
    "fcf_growth_3y_cagr",
    "fcf_growth_5y_cagr",
    "dividend_growth_streak_years",
    # Added 2026-09-05 (financials display spec gap-fill), same edit as
    # their metric_definition rows. ebitda_margin/debt_to_ebitda/
    # fcf_per_share/share_repurchases_pct_fcf/dividends_pct_fcf all need
    # ebitda or fcf as an input, which live in metric_value not
    # canonical_fact -- computed in expanded_metrics.py. fcf_growth_yoy
    # is computed in mapper/fcf_growth.py (same reasoning as
    # fcf_growth_3y_cagr/5y_cagr above).
    "ebitda_margin",
    "debt_to_ebitda",
    "fcf_per_share",
    "share_repurchases_pct_fcf",
    "dividends_pct_fcf",
    "fcf_growth_yoy",
}

# debtor_days/inventory_days/payables_days added to FY_ONLY_METRICS
# 2026-08-18 for the same reason roic/roe are: a "days" formula
# multiplies by 365, so a quarterly denominator (roughly 1/4 of an
# annual one) would inflate every quarterly row ~4x for the same
# balance -- the exact same annualization trap already documented above
# for ROIC, not a new one.
# roa added 2026-09-08, Data Sanity Layer finding: the exact same
# annualization trap as roic/roe above, just never given the same
# protection. AAPL's own quarterly roa rows (Net Income / Total Assets,
# one quarter's income over a full balance-sheet snapshot) sat at 7-11%
# while its FY row -- using a real full year's net income -- correctly
# landed at 31.2%, close to yfinance's independently-reported 27.1%. A
# quarterly denominator understates roa ~4x for the same reason it
# inflates a "days" metric ~4x: the numerator is a period FLOW, the
# denominator a point-in-time STOCK, and only an annual flow is the right
# scale to divide by an annual-scale balance.
FY_ONLY_METRICS = {
    "roic",
    "roe",
    "roa",
    "debtor_days",
    "inventory_days",
    "payables_days",
}

# gross_margin switched from "ratio" (a direct GrossProfit tag) to
# "sum_diff_ratio" (Revenue - CostOfRevenue, 2026-09-01) -- checked live
# first: the direct `gross_profit` canonical_fact covered only 2,525 of
# 5,024 companies, while `revenue` (4,500) and `cost_of_revenue` (3,025)
# are each individually more widely tagged -- many filers report
# revenue and COGS separately without ever tagging a standalone
# GrossProfit fact. Verified the derivation is exact, not approximate,
# against a real company across 3 periods (Apple: Revenue - CostOfRevenue
# equals its own reported GrossProfit to the dollar in every period
# checked) before switching, not assumed to generalize. doc 02's own
# locked formula ("Gross Profit / Revenue") is unchanged -- only how
# Gross Profit itself is sourced changed, from a single required tag to
# a derived value from two more commonly-tagged inputs.
FORMULA_SHAPES = {
    "gross_margin": "sum_diff_ratio",
    "operating_margin": "ratio",
    "net_margin": "ratio",
    "roe": "ratio",
    "fcf": "sum_diff",
    "fcf_margin": "sum_diff_ratio",
    "debt_to_equity": "ratio",
    "current_ratio": "ratio",
    "interest_coverage_ratio": "ratio",
    "roic": "roic",
    # Additive widening, 2026-08-18 (doc 26's coverage push) -- new
    # entries only, doc 02's locked 18 above are untouched. Verified
    # zero regression: rerunning calculate() for the full golden-10
    # reproduced byte-identical values for all 10 original metrics
    # before this addition was trusted.
    "roa": "ratio",
    "quick_ratio": "sum_diff_ratio",
    "sbc_pct_revenue": "ratio",
    "ebitda": "additive",
    # net_debt_ebitda is NOT here -- its denominator (ebitda) lives in
    # analytics.metric_value, not canonical_fact, so this engine's
    # per-concept-role model can't express it. Computed separately in
    # mapper/expanded_metrics.py instead, alongside the price-dependent
    # EBITDA-based ratios that need the same TTM EBITDA reconstruction.
    # debtor_days/inventory_days/payables_days added 2026-08-18 -- new
    # "days" shape, FY-only (see FY_ONLY_METRICS comment above).
    # cash_conversion_cycle is NOT here -- it combines these three
    # METRICS' own outputs (debtor + inventory - payables), not raw
    # concepts, so it's computed in mapper/expanded_metrics.py instead,
    # same "combines other metrics' output" pattern as net_debt_ebitda.
    "debtor_days": "days",
    "inventory_days": "days",
    "payables_days": "days",
    # Added 2026-08-21 (core-fact-utilization-study.md #1/#4). Both reuse
    # existing shapes unchanged -- eps_dilution_spread's basic_eps
    # appearing in two roles (add + denominator) needed zero engine
    # changes, see expanded_definitions.py's module docstring for why
    # that's safe.
    "goodwill_pct_assets": "ratio",
    "eps_dilution_spread": "sum_diff_ratio",
    # Added 2026-08-21 (doc 28, Trendlyne gap analysis #1/#4).
    "rnd_intensity": "ratio",
    "net_interest_income": "sum_diff",
    # Added 2026-08-22 (P0/coverage execution pass).
    "capex_pct_revenue": "ratio",
    "sga_pct_revenue": "ratio",
    # Added 2026-08-29 (zero-new-fetch coverage pass). payout_ratio/
    # pretax_margin reuse dividends_per_share/diluted_eps/income_before_tax/
    # revenue, all already canonical concepts. net_cash/net_cash_per_share
    # combine cash_and_equivalents/total_debt/shares_outstanding -- all
    # balance_sheet (instant) -- fitting the EXISTING sum_diff/
    # sum_diff_ratio shapes exactly, no new shape needed.
    "payout_ratio": "ratio",
    "pretax_margin": "ratio",
    "net_cash": "sum_diff",
    "net_cash_per_share": "sum_diff_ratio",
    # Added 2026-09-05 (financials display spec gap-fill). All reuse
    # existing shapes unchanged -- see expanded_definitions.py's own
    # entries for the exact formula each represents.
    "book_value_per_share": "ratio",
    "working_capital": "sum_diff",
    "net_change_in_cash": "additive",
    "ocf_to_net_income": "ratio",
    "cash_returned_to_shareholders": "additive",
}

# Found live 2026-10-05 (cockpit triage, doc/planning/51): quick_ratio was
# blocking 2,604 companies (50% of the active population) from a full-metric
# Screener query -- the single biggest individual blocker found. Root cause:
# quick_ratio's "subtract" role (inventory) was treated by the generic
# "every role-concept must resolve" rule (see the 2026-08-16 ROIC comment
# below) exactly like a REQUIRED input -- but unlike total_debt/
# stockholders_equity in that ROIC case, a missing `inventory` fact is, for
# most real companies (software, services, most financials), the CORRECT
# signal that the company genuinely holds none, not a data gap. The same
# bug class already fixed once for total_shareholder_yield (2026-09-06,
# doc/learnings): "a composite metric that sums multiple optional
# components must treat a genuinely-absent component as $0, never require
# ALL components non-null."
#
# Scoped PER METRIC, not per shape -- `sum_diff_ratio` is shared by 5
# metrics (gross_margin, fcf_margin, quick_ratio, eps_dilution_spread,
# net_cash_per_share), and verified live that this fix must NOT generalize
# blindly: gross_margin's own "subtract" role (cost_of_revenue) is a real,
# almost-universal line item whose absence is overwhelmingly a genuine
# data gap, not a correct zero (doc/planning/51's Finding 13 table).
# net_cash_per_share (total_debt_resolved) and fcf_margin (capex) were
# explicitly left out here too -- flagged as "ambiguous, needs its own
# verification" in that same finding, not assumed safe by analogy.
ZERO_WHEN_ABSENT_CONCEPTS: dict[str, frozenset[str]] = {
    "quick_ratio": frozenset({"inventory"}),
}


def _load_target_metrics(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, metric_name from analytics.metric_definition where requires_price = false"
        )
        rows = cur.fetchall()
        targets = []
        with conn.cursor() as cur2:
            for metric_id, metric_name in rows:
                if (
                    metric_name in DEFERRED_TO_STAGE_3E
                    or metric_name in DEFERRED_TO_EXPANDED_METRICS
                ):
                    continue
                cur2.execute(
                    """
                    select cc.name, cc.id, mdi.role, cc.statement
                    from analytics.metric_definition_input mdi
                    join analytics.canonical_concept cc on cc.id = mdi.canonical_concept_id
                    where mdi.metric_definition_id = %s
                    """,
                    (metric_id,),
                )
                # (concept_name, concept_id, role, is_instant)
                inputs = [
                    (name, cid, role, statement == "balance_sheet")
                    for name, cid, role, statement in cur2.fetchall()
                ]
                targets.append({"id": metric_id, "name": metric_name, "inputs": inputs})
    return targets


def _load_canonical_facts(conn: psycopg.Connection, company_id: int) -> dict:
    """by_period_id: concept_id -> period_id -> (value, fact_ids) -- for duration lookups.
    by_end_date: concept_id -> end_date -> (value, fact_ids) -- for instant lookups, keyed
    by date so they can be matched against a duration period's end_date, not its period_id.
    periods: period_id -> (start, end, fiscal_period)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select cf.canonical_concept_id, cf.period_id, cf.value, cf.source_fact_ids,
                   p.start_date, p.end_date, p.fiscal_period, p.period_type
            from analytics.canonical_fact cf
            join core.period p on p.id = cf.period_id
            where cf.company_id = %s
            """,
            (company_id,),
        )
        by_period_id: dict[int, dict[int, tuple]] = {}
        by_end_date: dict[int, dict] = {}
        periods: dict[int, tuple] = {}
        for (
            concept_id,
            period_id,
            value,
            fact_ids,
            start,
            end,
            fiscal_period,
            period_type,
        ) in cur.fetchall():
            by_period_id.setdefault(concept_id, {})[period_id] = (value, fact_ids)
            if period_type == "instant":
                by_end_date.setdefault(concept_id, {})[end] = (value, fact_ids)
            periods[period_id] = (start, end, fiscal_period)
    return {
        "by_period_id": by_period_id,
        "by_end_date": by_end_date,
        "periods": periods,
    }


def calculate_for_company(
    conn: psycopg.Connection, company_id: int, targets: list[dict]
) -> dict:
    facts = _load_canonical_facts(conn, company_id)
    by_period_id, by_end_date, periods = (
        facts["by_period_id"],
        facts["by_end_date"],
        facts["periods"],
    )

    stats = {"computed": 0, "null": 0}
    rows: list[dict] = []

    for target in targets:
        metric_id, metric_name, inputs = target["id"], target["name"], target["inputs"]
        shape = FORMULA_SHAPES[metric_name]
        fy_only = metric_name in FY_ONLY_METRICS
        denominator_concept_names = frozenset(
            name for name, _cid, role, _is_instant in inputs if role == "denominator"
        )

        duration_inputs = [i for i in inputs if not i[3]]
        instant_inputs = [i for i in inputs if i[3]]

        # Anchor on duration periods when any exist (the "reporting period" a
        # mixed metric conceptually belongs to); pure-instant metrics
        # (current_ratio, debt_to_equity) anchor on their own instant periods
        # instead, matched by period_id as before -- both concepts in those
        # metrics are always dated as of the same balance-sheet date.
        anchor_inputs = duration_inputs or instant_inputs
        anchor_concept_ids = {cid for _name, cid, _role, _is_instant in anchor_inputs}
        anchor_period_ids: set[int] = set()
        for concept_id in anchor_concept_ids:
            anchor_period_ids.update(by_period_id.get(concept_id, {}).keys())

        # A role can have MORE THAN ONE expected concept (roic's
        # invested_capital_add covers both total_debt and
        # stockholders_equity). Found live 2026-08-16: checking only
        # "did this role get at least one value" silently drops a missing
        # summand instead of nulling the whole metric -- for AAPL FY2024,
        # total_debt was genuinely unresolved (a real Stage 2e conflict) but
        # stockholders_equity wasn't, so ROIC silently computed using equity
        # alone as "invested capital," reporting 346% instead of null. A
        # role is only usable if EVERY concept mapped to it resolved.
        expected_concepts_by_role: dict[str, set[int]] = {}
        concept_id_to_name: dict[int, str] = {}
        for name, concept_id, role, _is_instant in inputs:
            expected_concepts_by_role.setdefault(role, set()).add(concept_id)
            concept_id_to_name[concept_id] = name
        zero_when_absent_ids = {
            cid
            for cid, name in concept_id_to_name.items()
            if name in ZERO_WHEN_ABSENT_CONCEPTS.get(metric_name, frozenset())
        }

        for period_id in anchor_period_ids:
            start, end, fiscal_period = periods[period_id]
            if fiscal_period is None:
                # Non-standard duration Stage 2b deliberately left unclassified
                # (e.g. a 6-month YTD span) -- doesn't fit the FY/Q1-4/TTM
                # period_label model this table requires, so it gets no
                # point-in-time metric row at all. Not a bug: doc 09's own
                # Normalizer design already chose not to force a label here.
                continue
            if fy_only and fiscal_period != "FY":
                continue

            values_by_role: dict[str, list[Decimal]] = {}
            found_concepts_by_role: dict[str, set[int]] = {}
            source_fact_ids: list[int] = []

            for _concept_name, concept_id, role, is_instant in duration_inputs:
                hit = by_period_id.get(concept_id, {}).get(period_id)
                if hit is not None:
                    value, fact_ids = hit
                    values_by_role.setdefault(role, []).append(value)
                    found_concepts_by_role.setdefault(role, set()).add(concept_id)
                    source_fact_ids.extend(fact_ids)

            for _concept_name, concept_id, role, is_instant in instant_inputs:
                # Matched by END DATE against the anchor period's end, not
                # period_id -- see module docstring.
                hit = by_end_date.get(concept_id, {}).get(end)
                if hit is not None:
                    value, fact_ids = hit
                    values_by_role.setdefault(role, []).append(value)
                    found_concepts_by_role.setdefault(role, set()).add(concept_id)
                    source_fact_ids.extend(fact_ids)

            # Drop any role where not every expected concept resolved --
            # a partial summand list must null the whole metric, never
            # silently compute from whichever subset happened to resolve.
            # Exception, scoped per metric via ZERO_WHEN_ABSENT_CONCEPTS
            # above: a missing concept that's verified-safe to treat as a
            # genuine zero (not a data gap) doesn't block the role -- it
            # simply contributes nothing to the sum, same as if it had
            # resolved to Decimal(0). Still requires every OTHER (non-
            # zero-safe) expected concept in that role to resolve.
            incomplete_role = None
            for role, expected in expected_concepts_by_role.items():
                missing = expected - found_concepts_by_role.get(role, set())
                if missing and not missing <= zero_when_absent_ids:
                    incomplete_role = role
                    values_by_role.pop(role, None)
                    break
                if missing:
                    values_by_role.setdefault(role, [])

            if incomplete_role is not None:
                value, null_reason = None, f"incomplete:{incomplete_role}"
            else:
                value, null_reason = _compute(
                    shape, values_by_role, denominator_concept_names
                )
            rows.append(
                {
                    "company_id": company_id,
                    "metric_definition_id": metric_id,
                    "period_start": start,
                    "period_end": end,
                    "period_label": fiscal_period,
                    "value": value,
                    "is_null_reason": null_reason,
                    "source_fact_ids": source_fact_ids or None,
                }
            )
            stats["computed" if value is not None else "null"] += 1

    target_ids = [t["id"] for t in targets]
    with conn.cursor() as cur:
        # Scoped to only the metric_definition_ids this stage owns AND
        # excluding period_label='TTM' -- an unscoped delete here (found
        # live 2026-08-16) wiped out Stage 3e's growth/TTM rows for the
        # company too, since metric_value is a shared table across stages.
        # Scoping by metric_definition_id alone still wasn't enough: roic
        # and roe share the same metric_definition_id between this stage's
        # FY rows and Stage 3e's TTM rows (compute_ttm_returns in ttm.py),
        # distinguished only by period_label. This stage never writes
        # period_label='TTM' (fiscal_period is always FY/Q1-4), so
        # excluding it here mirrors ttm.py's own TTM-scoped delete and
        # keeps the two stages' writes fully partitioned. See mapper-day-06
        # learnings.
        cur.execute(
            "delete from analytics.metric_value where company_id = %s and metric_definition_id = any(%s) and period_label != 'TTM'",
            (company_id, target_ids),
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
    logger.info("calculate.company_done", company_id=company_id, **stats)
    return stats


def calculate(conn: psycopg.Connection, ciks: set[str]) -> dict:
    targets = _load_target_metrics(conn)
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
            stats = calculate_for_company(conn, company_id, targets)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "calculate", exc)
            conn = safe_rollback(conn, stage="calculate", cik=cik)
            continue
        totals["ok"] += 1
        totals["computed"] += stats["computed"]
        totals["null"] += stats["null"]

    logger.info("calculate.done", **totals)
    return totals
