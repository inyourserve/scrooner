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
"""

import psycopg
import structlog

logger = structlog.get_logger()

# (metric_name, formula_description, requires_price, inputs)
# Non-empty inputs identify definitions handled by calculate.py's generic
# engine. Empty inputs identify composite or externally sourced definitions
# whose implementation lives in a dedicated mapper.
METRIC_DEFINITIONS: list[tuple[str, str, bool, list[tuple[str, str]]]] = [
    ("roa", "Net Income / Total Assets", False,
     [("net_income", "numerator"), ("total_assets", "denominator")]),
    ("quick_ratio", "(Current Assets - Inventory) / Current Liabilities", False,
     [("current_assets", "add"), ("inventory", "subtract"), ("current_liabilities", "denominator")]),
    ("sbc_pct_revenue", "Stock-Based Compensation / Revenue", False,
     [("sbc", "numerator"), ("revenue", "denominator")]),
    ("ebitda", "Operating Income + Depreciation & Amortization", False,
     [("operating_income", "add"), ("depreciation_and_amortization", "add")]),
    ("net_debt_ebitda", "(Total Debt - Cash & Equivalents) / EBITDA (TTM). Computed in expanded_metrics.py "
     "-- EBITDA lives in metric_value, not canonical_fact, so calculate.py's generic engine can't reach it.",
     False, []),
    ("ev_ebitda", "(Market Cap + Total Debt - Cash & Equivalents) / EBITDA (TTM)", True, []),
    ("ev_sales", "(Market Cap + Total Debt - Cash & Equivalents) / Revenue (TTM)", True, []),
    ("peg_ratio", "Trailing P/E / EPS Growth Rate (YoY, as a percentage number, e.g. 15 not 0.15)", True, []),
    ("buyback_yield", "Share Buybacks (TTM) / Market Cap", True, []),
    ("total_shareholder_yield", "Dividend Yield + Buyback Yield - Dilution (share-count growth, TTM)", True, []),
    ("institutional_ownership_pct", "Sum of Form 13F-reported institutional holdings (deduped per filer, "
     "amendment preferred over original -- same dedup as apps/site's getTopInstitutionalHolders) / Shares Outstanding. "
     "Does NOT require price -- computed in expanded_metrics.py.", False, []),
    ("share_dilution_trend", "(Shares Outstanding now - Shares Outstanding ~1yr ago) / Shares Outstanding ~1yr ago. "
     "Same dilution figure already folded into total_shareholder_yield, exposed here as its own visible data point "
     "-- e.g. a buyback-yield-positive company can still be net-diluting via SBC issuance, which total_shareholder_yield "
     "alone hides. Does NOT require price -- computed in expanded_metrics.py.", False, []),
    ("debtor_days", "(Accounts Receivable / Revenue) x 365, FY only", False,
     [("accounts_receivable", "numerator"), ("revenue", "denominator")]),
    ("inventory_days", "(Inventory / Cost of Revenue) x 365, FY only", False,
     [("inventory", "numerator"), ("cost_of_revenue", "denominator")]),
    ("payables_days", "(Accounts Payable / Cost of Revenue) x 365, FY only", False,
     [("accounts_payable", "numerator"), ("cost_of_revenue", "denominator")]),
    ("cash_conversion_cycle", "Debtor Days + Inventory Days - Payables Days, most recent FY each. Computed in "
     "expanded_metrics.py -- combines three METRIC outputs, not raw concepts, same pattern as net_debt_ebitda.",
     False, []),
    ("piotroski_f_score", "Standard 9-test Piotroski F-Score (0-9), FY vs prior FY. Computed in "
     "mapper/quality_score.py -- a composite requiring 9 raw concepts across 2 fiscal years each, doesn't fit "
     "this engine's single-period per-role model. Null for financial institutions by design (Piotroski's own "
     "methodology needs a classified current/non-current balance sheet + gross margin, which banks don't report).",
     False, []),
    ("fcf_gt_net_income", "1 if (CFO - CapEx) > Net Income for the fiscal year, else 0. Computed in "
     "mapper/quality_flags.py, per FY year.", False, []),
    ("zero_debt", "1 if total_debt == 0 for the fiscal year, else 0; null (not 0) if total_debt wasn't reported "
     "at all that year -- absence is not evidence of debt-free status. Computed in mapper/quality_flags.py, per FY year.",
     False, []),
    ("profitable_streak_years", "Consecutive most-recent FY years with positive net income, counted backward "
     "from the latest year until a non-positive or missing year breaks the streak. Computed in "
     "mapper/quality_flags.py, one value as of the latest FY only (not a per-year series).", False, []),
    ("margin_expanding_3yr", "1 if gross margin strictly increased across the 3 most recent CONSECUTIVE FY years, "
     "else 0; null if fewer than 3 consecutive years of data exist. Computed in mapper/quality_flags.py, one "
     "value as of the latest FY only.", False, []),
    ("revenue_growth_5y_cagr", "(Revenue[t] / Revenue[t-5]) ^ (1/5) - 1, same fiscal_period. Computed in "
     "mapper/ttm.py -- a purely additive GROWTH_METRICS entry, same mechanism as the locked 3Y CAGR.", False, []),
    ("revenue_growth_10y_cagr", "(Revenue[t] / Revenue[t-10]) ^ (1/10) - 1, same fiscal_period. Computed in "
     "mapper/ttm.py.", False, []),
    ("eps_growth_5y_cagr", "(Diluted EPS[t] / Diluted EPS[t-5]) ^ (1/5) - 1, same fiscal_period. Computed in "
     "mapper/ttm.py.", False, []),
    ("eps_growth_10y_cagr", "(Diluted EPS[t] / Diluted EPS[t-10]) ^ (1/10) - 1, same fiscal_period. Computed in "
     "mapper/ttm.py.", False, []),
    ("goodwill_pct_assets", "Goodwill / Total Assets", False,
     [("goodwill", "numerator"), ("total_assets", "denominator")]),
    ("eps_dilution_spread", "(Basic EPS - Diluted EPS) / Basic EPS -- a dilution-quality signal distinct from "
     "share_dilution_trend (which tracks share-COUNT change, not the basic-vs-diluted EPS gap itself)", False,
     [("basic_eps", "add"), ("diluted_eps", "subtract"), ("basic_eps", "denominator")]),
    ("ar_change_reconciliation_gap", "(Accounts Receivable[FY] - Accounts Receivable[FY-1]) - the company's own "
     "reported cash-flow-statement IncreaseDecreaseInAccountsReceivable[FY]. A quality-of-earnings cross-check, "
     "not a locked ratio -- a large gap flags AR movement the cash-flow statement's own adjustment doesn't "
     "explain (e.g. an acquisition/divestiture, reclassification), not necessarily an error. Computed in "
     "mapper/reconciliation.py -- needs a prior-FY balance-sheet lookup this engine's single-period model can't "
     "express.", False, []),
    ("inventory_change_reconciliation_gap", "Same cross-check as ar_change_reconciliation_gap, for Inventory. "
     "Computed in mapper/reconciliation.py.", False, []),
    ("ap_change_reconciliation_gap", "Same cross-check as ar_change_reconciliation_gap, for Accounts Payable. "
     "Computed in mapper/reconciliation.py.", False, []),
    ("rnd_intensity", "R&D Expense / Revenue", False,
     [("research_and_development", "numerator"), ("revenue", "denominator")]),
    ("net_interest_income", "Interest Income - Interest Expense", False,
     [("interest_income", "add"), ("interest_expense", "subtract")]),
]


def seed(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("select id, name from analytics.canonical_concept")
        concept_id_by_name = {name: cid for cid, name in cur.fetchall()}

    stats = {"considered": len(METRIC_DEFINITIONS), "defined": 0, "inputs_linked": 0}
    with conn.cursor() as cur:
        for metric_name, formula_description, requires_price, inputs in METRIC_DEFINITIONS:
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

            cur.execute("delete from analytics.metric_definition_input where metric_definition_id = %s", (metric_definition_id,))
            for canonical_concept_name, role in inputs:
                cur.execute(
                    """
                    insert into analytics.metric_definition_input (metric_definition_id, canonical_concept_id, role)
                    values (%s, %s, %s)
                    """,
                    (metric_definition_id, concept_id_by_name[canonical_concept_name], role),
                )
                stats["inputs_linked"] += 1
    conn.commit()
    logger.info("expanded_definitions.seeded", **stats)
    return stats
