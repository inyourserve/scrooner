"""Expanded metric definitions (doc 18 Tier A / doc 26, built 2026-08-18
to raise data-point coverage). Same additive pattern as
expanded_concepts.py -- new rows only, doc 02's locked 18-metric list
(mapper/definitions.py) is not touched or reordered.

Four of these (roa, quick_ratio, sbc_pct_revenue, ebitda) are real inputs
for calculate.py's generic per-role engine (FORMULA_SHAPES widened
additively there too). The other five (net_debt_ebitda, ev_ebitda,
ev_sales, peg_ratio, buyback_yield, total_shareholder_yield) are
documentation-only rows here -- their actual computation lives in
mapper/expanded_metrics.py, the same "hardcoded Python, not the generic
engine" pattern price_metrics.py's own doc-02 price metrics already use,
because their inputs mix canonical_fact AND analytics.metric_value
(ebitda, market_cap) in ways the concept-only engine can't express.

net_debt_ebitda does NOT require price (Net Debt and EBITDA are both
price-independent) -- doc 18 already named this distinction; don't
conflate it with the 6 metrics that genuinely need price.
"""

import psycopg
import structlog

logger = structlog.get_logger()

# (metric_name, formula_description, requires_price, inputs)
# inputs only matter for the 4 calculate.py-engine metrics; the other 6
# get an empty list (documentation-only row, real logic in expanded_metrics.py).
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
