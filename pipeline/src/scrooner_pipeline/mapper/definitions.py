"""Stage 3c -- Metric formula definitions (doc 11). Seeds
analytics.metric_definition + metric_definition_input for doc 02's 18
locked V1 metrics (20 DB rows -- Revenue Growth and EPS Growth each split
into separate YoY / 3Y-CAGR metric_definition rows, since they produce
distinct values needing independent storage/versioning; still 18 product-
facing metrics per doc 02's guardrail, not a scope expansion).

ROIC's formula (left open in doc 02, explicitly assigned to this stage to
pin down "with a version number") is resolved here:

    NOPAT = Operating Income x (1 - Income Tax Expense / Income Before Tax)
    Invested Capital = Total Debt + Stockholders' Equity - Cash & Equivalents
    ROIC = NOPAT / Invested Capital

Verified live 2026-08-16 against AAPL Q1 FY2026 (the only period on hand
with all six inputs simultaneously authoritative) before locking this in:
tax_rate=17.46%, invested_capital=$131.4B, single-quarter NOPAT/invested
capital = 31.95%. Also checked -- and rejected -- naive x4 quarterly
annualization: it gives 127.8% ROIC, implausible, because AAPL's Q1 (the
holiday quarter) is its seasonally strongest by far, so scaling one
quarter's operating income by 4 badly overstates the year. Same structural
problem exists for ROE (net income, a flow, over stockholders' equity, a
point-in-time stock) -- Interest Coverage Ratio does NOT have this issue
(operating income and interest expense are both flows over the same
period, no stock/flow mismatch), nor do the margin ratios (all flow/flow)
or Debt/Equity and Current Ratio (both point-in-time/point-in-time).

Consequence for Stage 3d: ROIC and ROE compute directly on FY periods
(where the income-statement figure already naturally represents a full
year, no distortion) but are deliberately NOT computed from a bare
quarterly period until Stage 3e's TTM windows exist to do it properly.
Every other metric in this list is fine on any period basis its inputs
resolve for.
"""

import psycopg
import structlog

logger = structlog.get_logger()

# (metric_name, formula_description, requires_price, quarterly_needs_ttm, inputs)
# inputs: list of (canonical_concept_name, role)
METRIC_DEFINITIONS: list[tuple[str, str, bool, bool, list[tuple[str, str]]]] = [
    ("gross_margin", "Gross Profit / Revenue", False, False,
     [("gross_profit", "numerator"), ("revenue", "denominator")]),
    ("operating_margin", "Operating Income / Revenue", False, False,
     [("operating_income", "numerator"), ("revenue", "denominator")]),
    ("net_margin", "Net Income / Revenue", False, False,
     [("net_income", "numerator"), ("revenue", "denominator")]),
    ("roe", "Net Income / Stockholders' Equity", False, True,
     [("net_income", "numerator"), ("stockholders_equity", "denominator")]),
    ("roic",
     "NOPAT / Invested Capital, where NOPAT = Operating Income x (1 - Income Tax Expense / Income Before Tax) "
     "and Invested Capital = Total Debt + Stockholders' Equity - Cash & Equivalents. v1 formula, pinned 2026-08-16 "
     "with real evidence -- see module docstring.",
     False, True,
     [("operating_income", "nopat_base"), ("income_tax_expense", "tax_rate_numerator"),
      # total_debt_resolved, not total_debt, per doc 40 (2026-09-02).
      ("income_before_tax", "tax_rate_denominator"), ("total_debt_resolved", "invested_capital_add"),
      ("stockholders_equity", "invested_capital_add"), ("cash_and_equivalents", "invested_capital_subtract")]),
    ("revenue_growth_yoy", "(Revenue[t] - Revenue[t-1]) / Revenue[t-1], same fiscal_period year over year", False, False,
     [("revenue", "base")]),
    ("revenue_growth_3y_cagr", "(Revenue[t] / Revenue[t-3]) ^ (1/3) - 1, FY periods", False, False,
     [("revenue", "base")]),
    ("eps_growth_yoy", "(Diluted EPS[t] - Diluted EPS[t-1]) / Diluted EPS[t-1], same fiscal_period year over year", False, False,
     [("diluted_eps", "base")]),
    ("eps_growth_3y_cagr", "(Diluted EPS[t] / Diluted EPS[t-3]) ^ (1/3) - 1, FY periods", False, False,
     [("diluted_eps", "base")]),
    ("fcf", "Cash from Operations - CapEx", False, False,
     [("cfo", "add"), ("capex", "subtract")]),
    ("fcf_margin", "(Cash from Operations - CapEx) / Revenue", False, False,
     [("cfo", "add"), ("capex", "subtract"), ("revenue", "denominator")]),
    # total_debt_resolved, not total_debt, per doc 40 (2026-09-02).
    ("debt_to_equity", "Total Debt / Stockholders' Equity", False, False,
     [("total_debt_resolved", "numerator"), ("stockholders_equity", "denominator")]),
    ("current_ratio", "Current Assets / Current Liabilities", False, False,
     [("current_assets", "numerator"), ("current_liabilities", "denominator")]),
    ("interest_coverage_ratio", "Operating Income / Interest Expense", False, False,
     [("operating_income", "numerator"), ("interest_expense", "denominator")]),
    # Price-dependent (doc 02): formula-defined now, not computed until Company Master
    # supplies a price source. EDGAR-derivable inputs listed; "price"/"market cap" are
    # not canonical_concept rows (not XBRL-derivable) -- requires_price flags the gap.
    ("market_cap", "Shares Outstanding x Price", True, False,
     [("shares_outstanding", "multiplicand")]),
    ("trailing_pe", "Price / Diluted EPS (TTM)", True, False,
     [("diluted_eps", "denominator_ttm")]),
    ("price_to_sales", "Market Cap / Revenue (TTM)", True, False,
     [("shares_outstanding", "market_cap_component"), ("revenue", "denominator_ttm")]),
    ("price_to_book", "Market Cap / Stockholders' Equity", True, False,
     [("shares_outstanding", "market_cap_component"), ("stockholders_equity", "denominator")]),
    ("dividend_yield", "Dividends per Share (TTM) / Price", True, False,
     [("dividends_per_share", "numerator_ttm")]),
    ("fcf_yield", "FCF (TTM) / Market Cap", True, False,
     [("cfo", "add"), ("capex", "subtract"), ("shares_outstanding", "market_cap_component")]),
]


def seed(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute("select id, name from analytics.canonical_concept")
        concept_id_by_name = {name: cid for cid, name in cur.fetchall()}

    stats = {"considered": len(METRIC_DEFINITIONS), "defined": 0, "inputs_linked": 0}
    with conn.cursor() as cur:
        for metric_name, formula_description, requires_price, _quarterly_needs_ttm, inputs in METRIC_DEFINITIONS:
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
    logger.info("definitions.seeded", **stats)
    return stats
