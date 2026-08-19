"""Human-facing metadata for the Screener's validated metric catalog.

The database remains authoritative for which metrics are currently
screenable and for their formula/version. This module only supplies the
presentation fields a user interface needs; a metric absent here still
gets an honest generated label and neutral number formatting.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricPresentation:
    display_name: str
    short_definition: str
    category: str
    value_type: str


METRIC_PRESENTATION: dict[str, MetricPresentation] = {
    "gross_margin": MetricPresentation("Gross margin", "Gross profit as a share of revenue.", "Profitability", "percentage"),
    "operating_margin": MetricPresentation("Operating margin", "Operating income as a share of revenue.", "Profitability", "percentage"),
    "net_margin": MetricPresentation("Net margin", "Net income as a share of revenue.", "Profitability", "percentage"),
    "roe": MetricPresentation("Return on equity (ROE)", "Net income relative to stockholders' equity.", "Returns", "percentage"),
    "roic": MetricPresentation("Return on invested capital (ROIC)", "After-tax operating return on invested capital.", "Returns", "percentage"),
    "roa": MetricPresentation("Return on assets (ROA)", "Net income relative to total assets.", "Returns", "percentage"),
    "revenue_growth_yoy": MetricPresentation("Revenue growth (YoY)", "Revenue growth versus the same fiscal period one year earlier.", "Growth", "percentage"),
    "revenue_growth_3y_cagr": MetricPresentation("Revenue growth (3Y CAGR)", "Compound annual revenue growth over three fiscal years.", "Growth", "percentage"),
    "eps_growth_yoy": MetricPresentation("EPS growth (YoY)", "Diluted EPS growth versus the same fiscal period one year earlier.", "Growth", "percentage"),
    "eps_growth_3y_cagr": MetricPresentation("EPS growth (3Y CAGR)", "Compound annual diluted EPS growth over three fiscal years.", "Growth", "percentage"),
    "fcf": MetricPresentation("Free cash flow (FCF)", "Cash from operations less capital expenditure.", "Cash flow", "currency"),
    "fcf_margin": MetricPresentation("Free cash flow margin", "Free cash flow as a share of revenue.", "Cash flow", "percentage"),
    "debt_to_equity": MetricPresentation("Debt to equity", "Total debt relative to stockholders' equity.", "Financial strength", "multiple"),
    "current_ratio": MetricPresentation("Current ratio", "Current assets relative to current liabilities.", "Financial strength", "multiple"),
    "quick_ratio": MetricPresentation("Quick ratio", "Current assets excluding inventory relative to current liabilities.", "Financial strength", "multiple"),
    "interest_coverage_ratio": MetricPresentation("Interest coverage", "Operating income relative to interest expense.", "Financial strength", "multiple"),
    "ebitda": MetricPresentation("EBITDA", "Operating income plus depreciation and amortization.", "Profitability", "currency"),
    "net_debt_ebitda": MetricPresentation("Net debt / EBITDA", "Debt less cash relative to trailing EBITDA.", "Financial strength", "multiple"),
    "sbc_pct_revenue": MetricPresentation("SBC as % of revenue", "Stock-based compensation as a share of revenue.", "Capital allocation", "percentage"),
    "share_dilution_trend": MetricPresentation("Share-count change (YoY)", "Change in shares outstanding over approximately one year.", "Capital allocation", "percentage"),
    "institutional_ownership_pct": MetricPresentation("Institutional ownership", "Recent Form 13F-reported holdings relative to shares outstanding.", "Ownership", "percentage"),
}

OPERATOR_ORDER = [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"]


def presentation_for(metric_name: str) -> MetricPresentation:
    return METRIC_PRESENTATION.get(
        metric_name,
        MetricPresentation(metric_name.replace("_", " ").title(), "Defined Scrooner metric.", "Other", "number"),
    )
