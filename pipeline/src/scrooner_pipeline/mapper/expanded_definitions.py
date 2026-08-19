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
