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
    "greater than": ">",
    "above": ">",
    "over": ">",
    "more than": ">",
    ">=": ">=",
    "at least": ">=",
    "less than": "<",
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
