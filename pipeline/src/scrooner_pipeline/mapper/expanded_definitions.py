"""Expanded metric definitions (doc 18 Tier A / doc 26, built 2026-08-18
to raise data-point coverage). Same additive pattern as
expanded_concepts.py -- new rows only, doc 02's locked 18-metric list
(mapper/definitions.py) is not touched or reordered.

Seven definitions (roa, quick_ratio, sbc_pct_revenue, ebitda, debtor_days,
inventory_days, and payables_days) provide inputs to calculate.py's generic
per-role engine (FORMULA_SHAPES is widened additively there too). Definitions
with no inputs are composite or externally sourced metrics whose calculation
lives in mapper/expanded_metrics.py or mapper/quality_score.py; their inputs
cannot be represented by the generic engine's single-period canonical-concept
model.

net_debt_ebitda does NOT require price (Net Debt and EBITDA are both
price-independent) -- doc 18 already named this distinction; don't
conflate it with the metrics that genuinely need price.

Five more definitions added 2026-08-21, acting on
doc/learnings/core-fact-utilization-study.md's ranked recommendations
(expanded_concepts.py's own docstring has the full concept-level detail,
including why total_debt's alternate widening was reversed rather than
implemented):

- goodwill_pct_assets: real calculate.py-engine input (ratio shape),
  same as roa/quick_ratio.
- eps_dilution_spread: (basic_eps - diluted_eps) / basic_eps, a real
  calculate.py-engine input too -- basic_eps appears TWICE in its own
  inputs list, once as "add" and once as "denominator". Checked before
  relying on this: analytics.metric_definition_input has no unique
  constraint beyond its own surrogate primary key (verified live against
  pg_constraint), and calculate.py's per-period loop iterates each
  (concept, role) input row independently rather than deduping by
  concept_id -- so one concept feeding two different roles for the same
  metric is already safe with zero engine changes, not a new capability
  being assumed.
- ar_change_reconciliation_gap / inventory_change_reconciliation_gap /
  ap_change_reconciliation_gap: documentation-only, computed in the new
  mapper/reconciliation.py (FY-vs-prior-FY balance-sheet delta compared
  against the company's own reported cash-flow-statement change) --
  doesn't fit this engine's single-period model, same reasoning as
  cash_conversion_cycle needing expanded_metrics.py instead.

Two more added same day, acting on doc 28 (Trendlyne gap analysis)
items #1/#4:
- rnd_intensity: R&D / Revenue, real calculate.py-engine input (ratio shape).
- net_interest_income: Interest Income - Interest Expense, real
  calculate.py-engine input (sum_diff shape) -- same shape fcf already uses.

Six more added 2026-08-22 (a P0/coverage execution pass, doc 18 Tier A's
2 still-unbuilt items plus 4 new ones from the utilization-study
backlog):
- capex_pct_revenue, sga_pct_revenue: both real calculate.py-engine
  ratio inputs, zero new logic.
- effective_tax_rate_gap: documentation-only -- compares the company's
  own reported effective_tax_rate_reported against the rate ROIC
  already derives internally (income_tax_expense/income_before_tax), a
  cross-validation signal (doc 18's own #5 ranked idea). Computed in the
  new mapper/tax_reconciliation.py -- needs a metric's own separate
  per-period division that doesn't fit a single canonical-concept role.
- fcf_growth_3y_cagr, fcf_growth_5y_cagr: documentation-only -- FCF is
  itself a computed metric_value (sum_diff of cfo-capex), not a raw
  canonical_fact, so ttm.py's GROWTH_METRICS (which reads canonical_fact
  by concept) can't reach it directly. Computed in the new
  mapper/fcf_growth.py, reusing ttm.py's own _growth_value() function
  unchanged.
- dividend_growth_streak_years: documentation-only -- consecutive most-
  recent FY years with dividends_per_share strictly increasing, same
  "as of latest FY" single-value shape as profitable_streak_years.
  Computed in the new mapper/dividend_streak.py.

Six more added 2026-08-29 (zero-new-fetch coverage pass -- payout ratio,
pretax margin, net cash, dividend growth):
- payout_ratio: Dividends per Share / Diluted EPS, real calculate.py-engine
  ratio input. dividends_per_share and diluted_eps are both already
  canonical concepts (concepts.py, Stage 3a) -- no new concept curation.
- pretax_margin: Income Before Tax / Revenue, real ratio input.
  income_before_tax was already a canonical concept but only ever
  consumed as ROIC's tax_rate_denominator role -- reused here unchanged,
  not recreated.
- net_cash / net_cash_per_share: cash_and_equivalents - total_debt, and
  that same figure / shares_outstanding. All three inputs are already
  canonical concepts, all balance_sheet (instant) -- fits the EXISTING
  sum_diff / sum_diff_ratio shapes exactly (same shapes current_ratio's
  sibling metrics quick_ratio/fcf_margin already use for all-instant or
  mixed instant inputs), so no new formula shape and no expanded_metrics.py
  hardcoded function needed -- checked before assuming either was required.
- dps_growth_yoy / dps_growth_3y_cagr: documentation-only -- computed in
  mapper/ttm.py's GROWTH_METRICS, same purely-additive dict-entry pattern
  as the 5Y/10Y revenue/EPS CAGR additions (2026-08-19). "dps" abbreviation
  matches this file's existing "eps" convention (eps_growth_yoy uses
  concept diluted_eps but is named eps_*, not diluted_eps_*).
"""

import psycopg
import structlog

logger = structlog.get_logger()

# (metric_name, formula_description, requires_price, inputs)
# Non-empty inputs identify definitions handled by calculate.py's generic
# engine. Empty inputs identify composite or externally sourced definitions
# whose implementation lives in a dedicated mapper.
METRIC_DEFINITIONS: list[tuple[str, str, bool, list[tuple[str, str]]]] = [
    (
        "roa",
        "Net Income / Total Assets",
        False,
        [("net_income", "numerator"), ("total_assets", "denominator")],
    ),
    (
        "quick_ratio",
        "(Current Assets - Inventory) / Current Liabilities",
        False,
        [
            ("current_assets", "add"),
            ("inventory", "subtract"),
            ("current_liabilities", "denominator"),
        ],
    ),
    (
        "sbc_pct_revenue",
        "Stock-Based Compensation / Revenue",
        False,
        [("sbc", "numerator"), ("revenue", "denominator")],
    ),
    (
        "ebitda",
        "Operating Income + Depreciation & Amortization",
        False,
        # Reads the *_resolved concepts (strictly a superset of the raw
        # ones via baseline-passthrough/fallback merges), not the raw
        # operating_income/depreciation_and_amortization tags directly --
        # found live 2026-10-05 (doc/planning/51 Finding 22): a real,
        # confirmed gap (SITE Centers Corp's raw operating_income
        # canonical_fact genuinely missing at a period where
        # operating_income_resolved has the real, conflict-filled value)
        # was silently nulling ebitda for every company whose
        # operating_income/D&A only exists via a fallback mechanism.
        [
            ("operating_income_resolved", "add"),
            ("depreciation_and_amortization_resolved", "add"),
        ],
    ),
    (
        "net_debt_ebitda",
        "(Total Debt - Cash & Equivalents) / EBITDA (TTM). Computed in expanded_metrics.py "
        "-- EBITDA lives in metric_value, not canonical_fact, so calculate.py's generic engine can't reach it.",
        False,
        [],
    ),
    (
        "ev_ebitda",
        "(Market Cap + Total Debt - Cash & Equivalents) / EBITDA (TTM)",
        True,
        [],
    ),
    (
        "ev_sales",
        "(Market Cap + Total Debt - Cash & Equivalents) / Revenue (TTM)",
        True,
        [],
    ),
    (
        "peg_ratio",
        "Trailing P/E / EPS Growth Rate (YoY, as a percentage number, e.g. 15 not 0.15)",
        True,
        [],
    ),
    ("buyback_yield", "Share Buybacks (TTM) / Market Cap", True, []),
    (
        "total_shareholder_yield",
        "Dividend Yield + Buyback Yield - Dilution (share-count growth, TTM)",
        True,
        [],
    ),
    (
        "institutional_ownership_pct",
        "Sum of Form 13F-reported institutional holdings (deduped per filer, "
        "amendment preferred over original -- same dedup as apps/site's getTopInstitutionalHolders) / Shares Outstanding. "
        "Does NOT require price -- computed in expanded_metrics.py.",
        False,
        [],
    ),
    (
        "share_dilution_trend",
        "(Shares Outstanding now - Shares Outstanding ~1yr ago) / Shares Outstanding ~1yr ago. "
        "Same dilution figure already folded into total_shareholder_yield, exposed here as its own visible data point "
        "-- e.g. a buyback-yield-positive company can still be net-diluting via SBC issuance, which total_shareholder_yield "
        "alone hides. Does NOT require price -- computed in expanded_metrics.py.",
        False,
        [],
    ),
    (
        "debtor_days",
        "(Accounts Receivable / Revenue) x 365, FY only",
        False,
        [("accounts_receivable", "numerator"), ("revenue", "denominator")],
    ),
    (
        "inventory_days",
        "(Inventory / Cost of Revenue) x 365, FY only",
        False,
        [("inventory", "numerator"), ("cost_of_revenue", "denominator")],
    ),
    (
        "payables_days",
        "(Accounts Payable / Cost of Revenue) x 365, FY only",
        False,
        [("accounts_payable", "numerator"), ("cost_of_revenue", "denominator")],
    ),
    (
        "cash_conversion_cycle",
        "Debtor Days + Inventory Days - Payables Days, most recent FY each. Computed in "
        "expanded_metrics.py -- combines three METRIC outputs, not raw concepts, same pattern as net_debt_ebitda.",
        False,
        [],
    ),
    (
        "piotroski_f_score",
        "Standard 9-test Piotroski F-Score (0-9), FY vs prior FY. Computed in "
        "mapper/quality_score.py -- a composite requiring 9 raw concepts across 2 fiscal years each, doesn't fit "
        "this engine's single-period per-role model. Null for financial institutions by design (Piotroski's own "
        "methodology needs a classified current/non-current balance sheet + gross margin, which banks don't report).",
        False,
        [],
    ),
    (
        "fcf_gt_net_income",
        "1 if (CFO - CapEx) > Net Income for the fiscal year, else 0. Computed in "
        "mapper/quality_flags.py, per FY year.",
        False,
        [],
    ),
    (
        "zero_debt",
        "1 if total_debt == 0 for the fiscal year, else 0; null (not 0) if total_debt wasn't reported "
        "at all that year -- absence is not evidence of debt-free status. Computed in mapper/quality_flags.py, per FY year.",
        False,
        [],
    ),
    (
        "profitable_streak_years",
        "Consecutive most-recent FY years with positive net income, counted backward "
        "from the latest year until a non-positive or missing year breaks the streak. Computed in "
        "mapper/quality_flags.py, one value as of the latest FY only (not a per-year series).",
        False,
        [],
    ),
    (
        "margin_expanding_3yr",
        "1 if gross margin strictly increased across the 3 most recent CONSECUTIVE FY years, "
        "else 0; null if fewer than 3 consecutive years of data exist. Computed in mapper/quality_flags.py, one "
        "value as of the latest FY only.",
        False,
        [],
    ),
    (
        "revenue_growth_5y_cagr",
        "(Revenue[t] / Revenue[t-5]) ^ (1/5) - 1, same fiscal_period. Computed in "
        "mapper/ttm.py -- a purely additive GROWTH_METRICS entry, same mechanism as the locked 3Y CAGR.",
        False,
        [],
    ),
    (
        "revenue_growth_10y_cagr",
        "(Revenue[t] / Revenue[t-10]) ^ (1/10) - 1, same fiscal_period. Computed in "
        "mapper/ttm.py.",
        False,
        [],
    ),
    (
        "eps_growth_5y_cagr",
        "(Diluted EPS[t] / Diluted EPS[t-5]) ^ (1/5) - 1, same fiscal_period. Computed in "
        "mapper/ttm.py.",
        False,
        [],
    ),
    (
        "eps_growth_10y_cagr",
        "(Diluted EPS[t] / Diluted EPS[t-10]) ^ (1/10) - 1, same fiscal_period. Computed in "
        "mapper/ttm.py.",
        False,
        [],
    ),
    (
        "goodwill_pct_assets",
        "Goodwill / Total Assets",
        False,
        [("goodwill", "numerator"), ("total_assets", "denominator")],
    ),
    (
        "eps_dilution_spread",
        "(Basic EPS - Diluted EPS) / Basic EPS -- a dilution-quality signal distinct from "
        "share_dilution_trend (which tracks share-COUNT change, not the basic-vs-diluted EPS gap itself)",
        False,
        [
            ("basic_eps", "add"),
            ("diluted_eps", "subtract"),
            ("basic_eps", "denominator"),
        ],
    ),
    (
        "ar_change_reconciliation_gap",
        "(Accounts Receivable[FY] - Accounts Receivable[FY-1]) - the company's own "
        "reported cash-flow-statement IncreaseDecreaseInAccountsReceivable[FY]. A quality-of-earnings cross-check, "
        "not a locked ratio -- a large gap flags AR movement the cash-flow statement's own adjustment doesn't "
        "explain (e.g. an acquisition/divestiture, reclassification), not necessarily an error. Computed in "
        "mapper/reconciliation.py -- needs a prior-FY balance-sheet lookup this engine's single-period model can't "
        "express.",
        False,
        [],
    ),
    (
        "inventory_change_reconciliation_gap",
        "Same cross-check as ar_change_reconciliation_gap, for Inventory. "
        "Computed in mapper/reconciliation.py.",
        False,
        [],
    ),
    (
        "ap_change_reconciliation_gap",
        "Same cross-check as ar_change_reconciliation_gap, for Accounts Payable. "
        "Computed in mapper/reconciliation.py.",
        False,
        [],
    ),
    (
        "rnd_intensity",
        "R&D Expense / Revenue",
        False,
        [("research_and_development", "numerator"), ("revenue", "denominator")],
    ),
    (
        "net_interest_income",
        "Interest Income - Interest Expense",
        False,
        [("interest_income", "add"), ("interest_expense", "subtract")],
    ),
    (
        "capex_pct_revenue",
        "CapEx / Revenue",
        False,
        [("capex", "numerator"), ("revenue", "denominator")],
    ),
    (
        "sga_pct_revenue",
        "SG&A Expense / Revenue",
        False,
        [("sga_expense", "numerator"), ("revenue", "denominator")],
    ),
    (
        "effective_tax_rate_gap",
        "Reported Effective Tax Rate - (Income Tax Expense / Income Before Tax). A "
        "cross-validation signal for ROIC's own internally-derived tax rate -- a large gap flags a company "
        "with material discrete tax items (one-time credits/charges) that year, not necessarily an error in "
        "either figure. Computed in mapper/tax_reconciliation.py.",
        False,
        [],
    ),
    (
        "fcf_growth_3y_cagr",
        "(FCF[t] / FCF[t-3]) ^ (1/3) - 1, FY only. Computed in mapper/fcf_growth.py -- "
        "FCF is a computed metric_value, not a raw canonical_fact, so ttm.py's generic growth engine can't "
        "reach it directly.",
        False,
        [],
    ),
    (
        "fcf_growth_5y_cagr",
        "Same as fcf_growth_3y_cagr, 5-year lag. Computed in mapper/fcf_growth.py.",
        False,
        [],
    ),
    (
        "dividend_growth_streak_years",
        "Consecutive most-recent FY years with dividends_per_share strictly "
        "increasing, counted backward from the latest year until a flat/decreasing year breaks the streak. "
        "Null (not 0) for a company with no dividend history at all. Computed in mapper/dividend_streak.py, "
        "one value as of the latest FY only.",
        False,
        [],
    ),
    (
        "payout_ratio",
        "Dividends per Share / Diluted EPS",
        False,
        [("dividends_per_share", "numerator"), ("diluted_eps", "denominator")],
    ),
    (
        "pretax_margin",
        "Income Before Tax / Revenue",
        False,
        [("income_before_tax", "numerator"), ("revenue", "denominator")],
    ),
    # total_debt_resolved, not total_debt, per doc 40 (2026-09-02) -- see
    # that doc / mapper/concept_fallback.py for why.
    (
        "net_cash",
        "Cash & Equivalents - Total Debt",
        False,
        [("cash_and_equivalents", "add"), ("total_debt_resolved", "subtract")],
    ),
    (
        "net_cash_per_share",
        "(Cash & Equivalents - Total Debt) / Shares Outstanding",
        False,
        [
            ("cash_and_equivalents", "add"),
            ("total_debt_resolved", "subtract"),
            ("shares_outstanding", "denominator"),
        ],
    ),
    (
        "dps_growth_yoy",
        "(Dividends per Share[t] - Dividends per Share[t-1]) / Dividends per Share[t-1], same "
        "fiscal_period year over year. Computed in mapper/ttm.py -- a purely additive GROWTH_METRICS entry, same "
        "mechanism as the locked revenue/EPS growth metrics.",
        False,
        [],
    ),
    (
        "dps_growth_3y_cagr",
        "(Dividends per Share[t] / Dividends per Share[t-3]) ^ (1/3) - 1, FY periods. "
        "Computed in mapper/ttm.py.",
        False,
        [],
    ),
    # Added 2026-09-05, doc/Frontend/financials/scrooner-financials-display-spec-final.md's
    # Financial Overview/Balance Sheet/Cash Flow Investor View rows -- all reuse
    # calculate.py's existing generic-engine shapes, zero new formula logic.
    (
        "book_value_per_share",
        "Stockholders' Equity / Shares Outstanding",
        False,
        [("stockholders_equity", "numerator"), ("shares_outstanding", "denominator")],
    ),
    (
        "working_capital",
        "Current Assets - Current Liabilities",
        False,
        [("current_assets", "add"), ("current_liabilities", "subtract")],
    ),
    (
        "net_change_in_cash",
        "Cash from Operations + Cash from Investing + Cash from Financing -- the period's "
        "own bottom-line cash movement, distinct from net_cash (a balance-sheet POSITION: Cash - Total Debt).",
        False,
        [
            ("cfo", "add"),
            ("cash_flow_investing", "add"),
            ("cash_flow_financing", "add"),
        ],
    ),
    (
        "ocf_to_net_income",
        "Cash from Operations / Net Income -- an earnings-quality signal (a real, cash-backed "
        "profit should track CFO closely; a large or growing gap flags aggressive accrual accounting).",
        False,
        [("cfo", "numerator"), ("net_income", "denominator")],
    ),
    (
        "cash_returned_to_shareholders",
        "Dividends Paid + Share Buybacks -- the total cash actually distributed "
        "to shareholders in the period, before relating it to Market Cap (that ratio is total_shareholder_yield's "
        "job) or to Free Cash Flow (see share_repurchases_pct_fcf/dividends_pct_fcf, computed in expanded_metrics.py).",
        False,
        [("dividends_paid", "add"), ("share_buybacks", "add")],
    ),
    # ebitda_margin/debt_to_ebitda/fcf_per_share/share_repurchases_pct_fcf/
    # dividends_pct_fcf all need ebitda or fcf as an input -- both live in
    # analytics.metric_value, not canonical_fact, so this engine's
    # single-period per-role model can't reach them (the exact same reason
    # net_debt_ebitda/cash_conversion_cycle are documentation-only here).
    # Computed in expanded_metrics.py instead.
    (
        "ebitda_margin",
        "EBITDA (TTM) / Revenue (TTM). Computed in expanded_metrics.py.",
        False,
        [],
    ),
    (
        "debt_to_ebitda",
        "Total Debt / EBITDA (TTM) -- gross leverage, distinct from net_debt_ebitda (which "
        "nets out Cash & Equivalents first). Computed in expanded_metrics.py.",
        False,
        [],
    ),
    (
        "fcf_per_share",
        "Free Cash Flow (TTM) / Shares Outstanding. Computed in expanded_metrics.py.",
        False,
        [],
    ),
    (
        "share_repurchases_pct_fcf",
        "Share Buybacks (TTM) / Free Cash Flow (TTM) -- what fraction of real cash "
        "generation went to buybacks, distinct from buyback_yield (which relates buybacks to Market Cap, not FCF). "
        "Computed in expanded_metrics.py.",
        False,
        [],
    ),
    (
        "dividends_pct_fcf",
        "Dividends Paid (TTM) / Free Cash Flow (TTM) -- a cash-based payout coverage check, "
        "distinct from payout_ratio (Dividends per Share / Diluted EPS, an earnings-based payout ratio -- the two "
        "can diverge meaningfully whenever CFO and Net Income diverge). Computed in expanded_metrics.py.",
        False,
        [],
    ),
    # Growth/CAGR extensions to ttm.py's existing GROWTH_METRICS mechanism
    # (revenue/EPS/DPS already use this unchanged engine) -- net_income and
    # diluted_shares_outstanding are both real canonical_fact concepts, so
    # these need zero new logic, only new GROWTH_METRICS dict entries.
    (
        "net_income_growth_yoy",
        "(Net Income[t] - Net Income[t-1]) / Net Income[t-1], same fiscal_period year "
        "over year. Computed in mapper/ttm.py.",
        False,
        [],
    ),
    (
        "net_income_growth_3y_cagr",
        "(Net Income[t] / Net Income[t-3]) ^ (1/3) - 1, same fiscal_period. Computed "
        "in mapper/ttm.py.",
        False,
        [],
    ),
    (
        "net_income_growth_5y_cagr",
        "(Net Income[t] / Net Income[t-5]) ^ (1/5) - 1, same fiscal_period. Computed "
        "in mapper/ttm.py.",
        False,
        [],
    ),
    (
        "net_income_growth_10y_cagr",
        "(Net Income[t] / Net Income[t-10]) ^ (1/10) - 1, same fiscal_period. "
        "Computed in mapper/ttm.py.",
        False,
        [],
    ),
    (
        "diluted_shares_growth_yoy",
        "(Shares Outstanding[t] - Shares Outstanding[t-1]) / Shares Outstanding[t-1]. "
        "Uses the same shares_outstanding concept as share_dilution_trend (this project has no separate "
        "diluted-weighted-average-shares concept yet -- see doc/learnings/2026-09-05-financials-spec-gap-plan.md); "
        "unlike share_dilution_trend (a rolling ~1yr comparison anchored on 'today'), this is a real FY-vs-prior-FY "
        "series. Computed in mapper/ttm.py.",
        False,
        [],
    ),
    (
        "diluted_shares_growth_3y_cagr",
        "(Shares Outstanding[t] / Shares Outstanding[t-3]) ^ (1/3) - 1, same "
        "fiscal_period. Computed in mapper/ttm.py.",
        False,
        [],
    ),
    (
        "diluted_shares_growth_5y_cagr",
        "(Shares Outstanding[t] / Shares Outstanding[t-5]) ^ (1/5) - 1, same "
        "fiscal_period. Computed in mapper/ttm.py.",
        False,
        [],
    ),
    (
        "fcf_growth_yoy",
        "(FCF[t] - FCF[t-1]) / FCF[t-1], FY only. Computed in mapper/fcf_growth.py -- same "
        "reasoning as fcf_growth_3y_cagr/5y_cagr (FCF is a computed metric_value, not a raw canonical_fact).",
        False,
        [],
    ),
]


def seed(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("select id, name from analytics.canonical_concept")
        concept_id_by_name = {name: cid for cid, name in cur.fetchall()}

    stats = {"considered": len(METRIC_DEFINITIONS), "defined": 0, "inputs_linked": 0}
    with conn.cursor() as cur:
        for (
            metric_name,
            formula_description,
            requires_price,
            inputs,
        ) in METRIC_DEFINITIONS:
            cur.execute(
                """
                insert into analytics.metric_definition
                    (metric_name, formula_version, formula_description, requires_price, status)
                values (%s, 1, %s, %s, 'active')
                on conflict (metric_name, formula_version) do update
                    set formula_description = excluded.formula_description,
                        requires_price = excluded.requires_price
                returning id
                """,
                (metric_name, formula_description, requires_price),
            )
            metric_definition_id = cur.fetchone()[0]
            stats["defined"] += 1

            cur.execute(
                "delete from analytics.metric_definition_input where metric_definition_id = %s",
                (metric_definition_id,),
            )
            for canonical_concept_name, role in inputs:
                cur.execute(
                    """
                    insert into analytics.metric_definition_input (metric_definition_id, canonical_concept_id, role)
                    values (%s, %s, %s)
                    """,
                    (
                        metric_definition_id,
                        concept_id_by_name[canonical_concept_name],
                        role,
                    ),
                )
                stats["inputs_linked"] += 1
    conn.commit()
    logger.info("expanded_definitions.seeded", **stats)
    return stats
