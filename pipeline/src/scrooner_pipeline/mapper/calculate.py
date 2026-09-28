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
"""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback

logger = structlog.get_logger()

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

# Materiality floors, keyed by DENOMINATOR CONCEPT NAME -- refactored
# 2026-09-27 from an earlier per-metric-name-allowlist design (kept in
# git history) after a direct follow-up question ("why so big? find the
# real root cause and fix at root level so it never arises again"). The
# original design (three separate `{"operating_margin", "net_margin",
# ...}`-style sets) required a human to notice a new violating metric and
# manually add its name to a list -- exactly the kind of per-symptom
# patching that let this gap accumulate silently across months of Mapper
# builds in the first place (see doc/learnings/2026-09-27-plausibility-
# gates-root-cause-fixes.md's "why this was so big" analysis). This
# table is keyed by CONCEPT instead: every ratio/sum_diff_ratio/days-
# shaped metric in FORMULA_SHAPES automatically inherits the correct
# floor for whatever concept it actually divides by, current AND future
# -- a metric added next month with `revenue` as its denominator role
# needs zero changes here to be protected.
#
# A concept appears here ONLY when real data confirmed a near-zero value
# is a shell/pass-through-entity signal, never a legitimate business
# state -- concepts where near-zero is a real, meaningful state (equity,
# for a leveraged/distressed company; current_assets/price, not yet
# checked) are deliberately absent, so metrics denominating on THEM
# (roe, price_to_book, debt_to_equity) are correctly unaffected. Every
# floor value is sized from real company data for that specific
# concept, not one universal number -- see each entry's own evidence.
CONCEPT_MATERIALITY_FLOORS: dict[str, Decimal] = {
    # Confirmed on Inhibikase Therapeutics: real, authoritative $1 TTM
    # revenue (a genuine tiny licensing payment) against real ~$20M
    # operating losses produced a -2,006,393,700% operating_margin.
    "revenue": Decimal("1000000"),
    # Confirmed on Appsoft Technologies, Inc.: real, authoritative
    # FY2025 total_assets = $7 (a real near-defunct shell) against a
    # real -$93,642 net loss produced a -1,337,700% ROA. 142 of 175
    # roa critical violations were under this exact $1M threshold.
    "total_assets": Decimal("1000000"),
    # Confirmed on Invesco CurrencyShares Euro Trust: real, authoritative
    # current_liabilities of $155,864 (a pass-through currency trust's
    # genuine near-zero management-fee accrual) against $219.7M current
    # assets produced a 1,409x current_ratio -- one of several Invesco
    # CurrencyShares trusts (Swiss Franc/Yen/Pound/AUD) hitting the same
    # shape, all real commodity/currency pass-through structures with no
    # real operating liabilities, not a bug.
    "current_liabilities": Decimal("1000000"),
    # Confirmed on Dermata Therapeutics, Inc.: real, authoritative Q4
    # 2021 interest_expense = $4 (four dollars) produced a multi-
    # million-percent interest_coverage_ratio, despite that metric's
    # already-wide doc-47 bound of +/-5000 (500,000%). Floor set lower
    # than revenue/assets/current_liabilities -- a real early-stage
    # company's genuine interest expense can legitimately be a few
    # thousand dollars a quarter (Dermata's own real Q2 2021: $1,823,
    # Q1 2021: $43,135 -- both real, both correctly left uncapped by
    # this lower floor), unlike revenue/assets/liabilities where
    # anything under $1M for an operating company is itself already a
    # strong shell-company signal.
    "interest_expense": Decimal("10000"),
    # Deliberately NOT here, checked against real data before excluding,
    # not assumed: `stockholders_equity` (roe/price_to_book/debt_to_
    # equity's denominator) -- near-zero or negative equity is a real,
    # common, already-accepted leverage story for a distressed or heavy-
    # buyback company, not a shell-company signal; debt_to_equity (same
    # denominator) already shows ZERO critical findings in the live
    # data, confirming this concept genuinely doesn't need a floor.
    # cost_of_revenue (inventory_days/payables_days' denominator) and
    # current_assets/price were checked for evidence of the same pattern
    # and none was found this pass -- not added without evidence, same
    # "verify before trusting" discipline as every concept_mapping
    # addition in this project.
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


def _materiality_floor_violation(
    denominator_concept_names: frozenset[str], denom_sum: Decimal
) -> str | None:
    """Checked by every ratio-shaped formula branch below against
    CONCEPT_MATERIALITY_FLOORS (see that dict's own module-level
    docstring for the 2026-09-27 root-cause/design rationale) --
    returns an explicit null reason naming whichever concept's floor
    was breached, or None if the denominator is material by every
    concept it's actually built from. A composite denominator role
    (e.g. roic's invested_capital, which sums total_debt AND
    stockholders_equity) checks each concept independently -- any one
    of them being genuinely immaterial is enough to null the metric."""
    for concept_name in denominator_concept_names:
        floor = CONCEPT_MATERIALITY_FLOORS.get(concept_name)
        if floor is not None and abs(denom_sum) < floor:
            return f"immaterial_{concept_name}_base"
    return None


def _compute(
    shape: str,
    values_by_role: dict[str, list[Decimal]],
    denominator_concept_names: frozenset[str] = frozenset(),
) -> tuple[Decimal | None, str | None]:
    if shape == "ratio":
        num = values_by_role.get("numerator")
        denom = values_by_role.get("denominator")
        if num is None:
            return None, "missing:numerator"
        if denom is None:
            return None, "missing:denominator"
        denom_sum = sum(denom)
        if denom_sum == 0:
            return None, "zero_denominator"
        floor_violation = _materiality_floor_violation(
            denominator_concept_names, denom_sum
        )
        if floor_violation is not None:
            return None, floor_violation
        return sum(num) / denom_sum, None

    if shape == "additive":
        # All "add"-role inputs, summed -- no subtraction, unlike
        # sum_diff. New 2026-08-18 for ebitda (operating_income +
        # depreciation_and_amortization): these are two genuinely
        # different concepts being added, not alternates for the same
        # thing (that's what depreciation_and_amortization's own
        # first_match resolution already handles, one layer down).
        add = values_by_role.get("add")
        if add is None:
            return None, "missing:add"
        return sum(add), None

    if shape == "days":
        # (numerator / denominator) x 365 -- Debtor/Inventory/Payables
        # Days. FY-only (see FY_ONLY_METRICS), same annualization
        # reasoning as roic/roe: a quarterly denominator would inflate
        # the day-count ~4x for the same balance-sheet snapshot.
        num = values_by_role.get("numerator")
        denom = values_by_role.get("denominator")
        if num is None:
            return None, "missing:numerator"
        if denom is None:
            return None, "missing:denominator"
        denom_sum = sum(denom)
        if denom_sum == 0:
            return None, "zero_denominator"
        floor_violation = _materiality_floor_violation(
            denominator_concept_names, denom_sum
        )
        if floor_violation is not None:
            return None, floor_violation
        return (sum(num) / denom_sum) * 365, None

    if shape == "sum_diff":
        add = values_by_role.get("add")
        subtract = values_by_role.get("subtract")
        if add is None:
            return None, "missing:add"
        if subtract is None:
            return None, "missing:subtract"
        return sum(add) - sum(subtract), None

    if shape == "sum_diff_ratio":
        add = values_by_role.get("add")
        subtract = values_by_role.get("subtract")
        denom = values_by_role.get("denominator")
        if add is None:
            return None, "missing:add"
        if subtract is None:
            return None, "missing:subtract"
        if denom is None:
            return None, "missing:denominator"
        denom_sum = sum(denom)
        if denom_sum == 0:
            return None, "zero_denominator"
        floor_violation = _materiality_floor_violation(
            denominator_concept_names, denom_sum
        )
        if floor_violation is not None:
            return None, floor_violation
        return (sum(add) - sum(subtract)) / denom_sum, None

    if shape == "roic":
        nopat_base = values_by_role.get("nopat_base")
        tax_num = values_by_role.get("tax_rate_numerator")
        tax_denom = values_by_role.get("tax_rate_denominator")
        ic_add = values_by_role.get("invested_capital_add")
        ic_sub = values_by_role.get("invested_capital_subtract")
        if nopat_base is None:
            return None, "missing:nopat_base"
        if tax_num is None:
            return None, "missing:tax_rate_numerator"
        if tax_denom is None:
            return None, "missing:tax_rate_denominator"
        if ic_add is None:
            return None, "missing:invested_capital_add"
        if ic_sub is None:
            return None, "missing:invested_capital_subtract"
        tax_denom_sum = sum(tax_denom)
        if tax_denom_sum == 0:
            return None, "zero_pretax_income"
        tax_rate = sum(tax_num) / tax_denom_sum
        nopat = sum(nopat_base) * (1 - tax_rate)
        invested_capital = sum(ic_add) - sum(ic_sub)
        if invested_capital == 0:
            return None, "zero_invested_capital"
        return nopat / invested_capital, None

    raise ValueError(f"unknown formula shape: {shape}")


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
        for _name, concept_id, role, _is_instant in inputs:
            expected_concepts_by_role.setdefault(role, set()).add(concept_id)

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
            incomplete_role = None
            for role, expected in expected_concepts_by_role.items():
                if found_concepts_by_role.get(role, set()) != expected:
                    incomplete_role = role
                    values_by_role.pop(role, None)
                    break

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
