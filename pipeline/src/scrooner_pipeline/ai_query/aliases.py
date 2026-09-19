"""Stage 6b -- Curated alias tables (doc 15 Sec 2-3, 5). Every entry here
is a deliberate, reviewed addition -- no fuzzy string matching, no
LLM-guessed equivalence, same discipline as Mapper's concept_mapping
(doc 12's reasoning: a wrong auto-accepted mapping would silently corrupt
a real result).

METRIC_ALIASES: phrase -> exact metric_name in the screenable catalog
(analytics.metric_definition where requires_price=false). Sourced from
the real 14-row catalog checked live 2026-08-17 while writing doc 15, not
guessed.

AMBIGUOUS_METRIC_PHRASES: a bare phrase that could plausibly mean more
than one real metric -- checked BEFORE the alias table, so these never
fall through to a silent default. revenue_growth_yoy vs.
revenue_growth_3y_cagr (and the eps equivalent) are both real, separate
screenable metrics -- "revenue growth" alone doesn't unambiguously name
either one.

SECTOR_ALIASES: phrase -> exact sic_code. A small, illustrative list
matching the golden-10's actual observed SIC diversity, not a general
sector taxonomy -- doc 14 already documented SIC's coarseness limitation;
this inherits it rather than pretending to fix it.

SECTOR_BUCKET_ALIASES: phrase -> exact core.company.sector value (doc 10
Sec 12/doc 26 Sec 2.8/doc 28, 2026-08-21) -- the curated SIC-range bucket
built in company_master/sector_bucket.py, e.g. "tech companies" ->
"Technology". Added additively, checked AFTER SECTOR_ALIASES in
rules.py's `_lookup_sector` -- any phrase already in SECTOR_ALIASES
(like "software companies" -> sic_code 7372) keeps its existing, more
precise exact-SIC behavior unchanged; this table only covers NEW,
broader phrases that had no match before, so doc 15's already-verified
test queries can't regress.
"""

METRIC_ALIASES: dict[str, str] = {
    "roe": "roe",
    "return on equity": "roe",
    "roic": "roic",
    "return on invested capital": "roic",
    "net margin": "net_margin",
    "net profit margin": "net_margin",
    "profit margin": "net_margin",
    "gross margin": "gross_margin",
    "operating margin": "operating_margin",
    "fcf": "fcf",
    "free cash flow": "fcf",
    "fcf margin": "fcf_margin",
    "free cash flow margin": "fcf_margin",
    "current ratio": "current_ratio",
    "debt to equity": "debt_to_equity",
    "debt-to-equity": "debt_to_equity",
    "debt/equity": "debt_to_equity",
    "d/e": "debt_to_equity",
    "interest coverage": "interest_coverage_ratio",
    "interest coverage ratio": "interest_coverage_ratio",
    "revenue growth yoy": "revenue_growth_yoy",
    "yoy revenue growth": "revenue_growth_yoy",
    "revenue growth year over year": "revenue_growth_yoy",
    "revenue growth 3y cagr": "revenue_growth_3y_cagr",
    "3 year revenue growth": "revenue_growth_3y_cagr",
    "3y revenue cagr": "revenue_growth_3y_cagr",
    "revenue cagr": "revenue_growth_3y_cagr",
    "eps growth yoy": "eps_growth_yoy",
    "yoy eps growth": "eps_growth_yoy",
    "eps growth 3y cagr": "eps_growth_3y_cagr",
    "3 year eps growth": "eps_growth_3y_cagr",
    "eps cagr": "eps_growth_3y_cagr",

    # Widened 2026-08-31: doc/status/DATA_COVERAGE.md's own "what moves
    # the needle next" flagged this table's 14-of-45-then-64-metric
    # coverage as the single largest remaining product gap -- the company
    # page visibly surfaces every metric_definition row, so a user who
    # tries to screen on one they just saw (Piotroski F-Score, EV/EBITDA,
    # PEG) got an honest "unsupported phrase" that was really just an
    # unfilled alias, not a real limitation. Checked live against the
    # real current catalog (`select metric_name from
    # analytics.metric_definition`, 64 rows, not assumed from an old
    # doc) before writing these. Deliberately NOT aliased: the 5 internal
    # reconciliation/diagnostic metrics (ar/ap/inventory_change_
    # reconciliation_gap, effective_tax_rate_gap, eps_dilution_spread) --
    # no natural investor phrase names these, they exist for the Mapper's
    # own QA, not for screening.
    "pe": "trailing_pe",
    "p/e": "trailing_pe",
    "pe ratio": "trailing_pe",
    "price to earnings": "trailing_pe",
    "price/earnings": "trailing_pe",
    "trailing pe": "trailing_pe",
    "market cap": "market_cap",
    "market capitalization": "market_cap",
    "price to book": "price_to_book",
    "p/b": "price_to_book",
    "price/book": "price_to_book",
    "price to sales": "price_to_sales",
    "p/s": "price_to_sales",
    "price/sales": "price_to_sales",
    "peg ratio": "peg_ratio",
    "peg": "peg_ratio",
    "ev/ebitda": "ev_ebitda",
    "ev to ebitda": "ev_ebitda",
    "enterprise value to ebitda": "ev_ebitda",
    "ev/sales": "ev_sales",
    "ev to sales": "ev_sales",
    "enterprise value to sales": "ev_sales",
    "dividend yield": "dividend_yield",
    "buyback yield": "buyback_yield",
    "share buyback yield": "buyback_yield",
    "shareholder yield": "total_shareholder_yield",
    "total shareholder yield": "total_shareholder_yield",
    "fcf yield": "fcf_yield",
    "free cash flow yield": "fcf_yield",
    "roa": "roa",
    "return on assets": "roa",
    "quick ratio": "quick_ratio",
    "acid test ratio": "quick_ratio",
    "ebitda": "ebitda",
    "net debt to ebitda": "net_debt_ebitda",
    "net debt/ebitda": "net_debt_ebitda",
    "net cash": "net_cash",
    "net cash per share": "net_cash_per_share",
    "net interest income": "net_interest_income",
    "payout ratio": "payout_ratio",
    "dividend payout ratio": "payout_ratio",
    "pretax margin": "pretax_margin",
    "pre-tax margin": "pretax_margin",
    "cash conversion cycle": "cash_conversion_cycle",
    "ccc": "cash_conversion_cycle",
    "debtor days": "debtor_days",
    "days sales outstanding": "debtor_days",
    "dso": "debtor_days",
    "inventory days": "inventory_days",
    "days inventory outstanding": "inventory_days",
    "dio": "inventory_days",
    "payables days": "payables_days",
    "days payable outstanding": "payables_days",
    "dpo": "payables_days",
    "capex to revenue": "capex_pct_revenue",
    "capex percent of revenue": "capex_pct_revenue",
    "capital expenditure percentage": "capex_pct_revenue",
    "sbc percent of revenue": "sbc_pct_revenue",
    "stock based compensation percent of revenue": "sbc_pct_revenue",
    "sga percent of revenue": "sga_pct_revenue",
    "sg&a percentage": "sga_pct_revenue",
    "rnd intensity": "rnd_intensity",
    "r&d intensity": "rnd_intensity",
    "research and development intensity": "rnd_intensity",
    "goodwill percent of assets": "goodwill_pct_assets",
    "goodwill to assets": "goodwill_pct_assets",
    "institutional ownership": "institutional_ownership_pct",
    "institutional ownership percentage": "institutional_ownership_pct",
    "share dilution": "share_dilution_trend",
    "share count dilution": "share_dilution_trend",
    "dividend growth streak": "dividend_growth_streak_years",
    "consecutive years of dividend growth": "dividend_growth_streak_years",
    "dividend per share growth": "dps_growth_yoy",
    "dps growth": "dps_growth_yoy",
    "dps growth 3 year": "dps_growth_3y_cagr",
    "dividend per share growth 3y cagr": "dps_growth_3y_cagr",
    "revenue growth 5 year": "revenue_growth_5y_cagr",
    "5 year revenue cagr": "revenue_growth_5y_cagr",
    "revenue growth 10 year": "revenue_growth_10y_cagr",
    "10 year revenue cagr": "revenue_growth_10y_cagr",
    "eps growth 5 year": "eps_growth_5y_cagr",
    "5 year eps cagr": "eps_growth_5y_cagr",
    "eps growth 10 year": "eps_growth_10y_cagr",
    "10 year eps cagr": "eps_growth_10y_cagr",
    "fcf growth 3 year": "fcf_growth_3y_cagr",
    "free cash flow growth 3y cagr": "fcf_growth_3y_cagr",
    "fcf growth 5 year": "fcf_growth_5y_cagr",
    "piotroski score": "piotroski_f_score",
    "piotroski f-score": "piotroski_f_score",
    "f score": "piotroski_f_score",
    "zero debt": "zero_debt",
    "debt free": "zero_debt",
    "no debt": "zero_debt",
    "profitable streak": "profitable_streak_years",
    "years profitable": "profitable_streak_years",
    "consecutive profitable years": "profitable_streak_years",
    "margin expanding": "margin_expanding_3yr",
    "expanding margins": "margin_expanding_3yr",
    "fcf greater than net income": "fcf_gt_net_income",
    "cash flow exceeds net income": "fcf_gt_net_income",
}

AMBIGUOUS_METRIC_PHRASES: dict[str, list[str]] = {
    "revenue growth": ["revenue_growth_yoy", "revenue_growth_3y_cagr"],
    "eps growth": ["eps_growth_yoy", "eps_growth_3y_cagr"],
}

SECTOR_ALIASES: dict[str, str] = {
    "banks": "6021",
    "banking": "6021",
    "software": "7372",
    "software companies": "7372",
    "semiconductors": "3674",
    "semiconductor companies": "3674",
    "footwear": "3021",
    "pipelines": "4610",
    "computer hardware": "3571",
}

SECTOR_BUCKET_ALIASES: dict[str, str] = {
    "tech": "Technology",
    "tech companies": "Technology",
    "technology": "Technology",
    "technology companies": "Technology",
    "financial": "Financials",
    "financials": "Financials",
    "financial companies": "Financials",
    "healthcare": "Healthcare",
    "healthcare companies": "Healthcare",
    "health care companies": "Healthcare",
    "energy": "Energy",
    "energy companies": "Energy",
    "utility": "Utilities",
    "utilities": "Utilities",
    "utility companies": "Utilities",
    "industrial": "Industrials",
    "industrials": "Industrials",
    "industrial companies": "Industrials",
    "real estate": "Real Estate",
    "real estate companies": "Real Estate",
    "reits": "Real Estate",
    "consumer staples": "Consumer Staples",
    "consumer discretionary": "Consumer Discretionary",
    "materials companies": "Materials",
    "communication services": "Communication Services",
}

OPERATOR_ALIASES: dict[str, str] = {
    "not greater than": "<=",
    "no greater than": "<=",
    "no more than": "<=",
    "not above": "<=",
    "maximum of": "<=",
    "maximum": "<=",
    "not less than": ">=",
    "no less than": ">=",
    "not below": ">=",
    "minimum of": ">=",
    "minimum": ">=",
    "greater than": ">",
    "higher than": ">",
    "above": ">",
    "over": ">",
    "more than": ">",
    ">=": ">=",
    "at least": ">=",
    "less than": "<",
    "lower than": "<",
    "fewer than": "<",
    "below": "<",
    "under": "<",
    "<=": "<=",
    "at most": "<=",
    "not equal to": "!=",
    "not equal": "!=",
    "!=": "!=",
    "is not": "!=",
    "equal to": "=",
    "equals": "=",
    "is": "=",
    "=": "=",
    ">": ">",
    "<": "<",
}
