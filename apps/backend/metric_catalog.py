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
    "revenue_growth_5y_cagr": MetricPresentation("Revenue growth (5Y CAGR)", "Compound annual revenue growth over five fiscal years.", "Growth", "percentage"),
    "revenue_growth_10y_cagr": MetricPresentation("Revenue growth (10Y CAGR)", "Compound annual revenue growth over ten fiscal years.", "Growth", "percentage"),
    "eps_growth_5y_cagr": MetricPresentation("EPS growth (5Y CAGR)", "Compound annual diluted EPS growth over five fiscal years.", "Growth", "percentage"),
    "eps_growth_10y_cagr": MetricPresentation("EPS growth (10Y CAGR)", "Compound annual diluted EPS growth over ten fiscal years.", "Growth", "percentage"),
    "fcf_growth_3y_cagr": MetricPresentation("FCF growth (3Y CAGR)", "Compound annual free-cash-flow growth over three fiscal years.", "Growth", "percentage"),
    "fcf_growth_5y_cagr": MetricPresentation("FCF growth (5Y CAGR)", "Compound annual free-cash-flow growth over five fiscal years.", "Growth", "percentage"),
    "capex_pct_revenue": MetricPresentation("Capital expenditure as % of revenue", "Capital expenditure relative to revenue.", "Capital allocation", "percentage"),
    "rnd_intensity": MetricPresentation("R&D as % of revenue", "Research and development expense relative to revenue.", "Capital allocation", "percentage"),
    "sga_pct_revenue": MetricPresentation("SG&A as % of revenue", "Selling, general and administrative expense relative to revenue.", "Profitability", "percentage"),
    "goodwill_pct_assets": MetricPresentation("Goodwill as % of assets", "Goodwill relative to total assets.", "Financial strength", "percentage"),
    "eps_dilution_spread": MetricPresentation("EPS dilution spread", "Difference between basic and diluted EPS relative to basic EPS.", "Capital allocation", "percentage"),
    "net_interest_income": MetricPresentation("Net interest income", "Interest income less interest expense.", "Profitability", "currency"),
    "debtor_days": MetricPresentation("Debtor days", "Accounts receivable relative to annual revenue, expressed in days.", "Operating efficiency", "number"),
    "inventory_days": MetricPresentation("Inventory days", "Inventory relative to annual cost of revenue, expressed in days.", "Operating efficiency", "number"),
    "payables_days": MetricPresentation("Payables days", "Accounts payable relative to annual cost of revenue, expressed in days.", "Operating efficiency", "number"),
    "cash_conversion_cycle": MetricPresentation("Cash conversion cycle", "Debtor days plus inventory days less payables days.", "Operating efficiency", "number"),
    "ar_change_reconciliation_gap": MetricPresentation("Receivables reconciliation gap", "Difference between the balance-sheet receivables movement and the cash-flow disclosure.", "Accounting quality", "currency"),
    "inventory_change_reconciliation_gap": MetricPresentation("Inventory reconciliation gap", "Difference between the balance-sheet inventory movement and the cash-flow disclosure.", "Accounting quality", "currency"),
    "ap_change_reconciliation_gap": MetricPresentation("Payables reconciliation gap", "Difference between the balance-sheet payables movement and the cash-flow disclosure.", "Accounting quality", "currency"),
    "effective_tax_rate_gap": MetricPresentation("Effective tax-rate gap", "Difference between the reported effective tax rate and the rate derived from tax expense.", "Accounting quality", "percentage"),
    "piotroski_f_score": MetricPresentation("Piotroski F-Score", "Nine-test financial-strength and operating-quality score from 0 to 9.", "Accounting quality", "number"),
    "fcf_gt_net_income": MetricPresentation("FCF exceeds net income", "Binary flag: 1 when free cash flow exceeds net income; otherwise 0.", "Accounting quality", "number"),
    "margin_expanding_3yr": MetricPresentation("Gross margin expanding (3Y)", "Binary flag: 1 when gross margin increased across three consecutive fiscal years.", "Accounting quality", "number"),
    "zero_debt": MetricPresentation("Zero debt", "Binary flag: 1 when reported total debt is zero; otherwise 0.", "Financial strength", "number"),
    "profitable_streak_years": MetricPresentation("Profitable-year streak", "Consecutive latest fiscal years with positive net income.", "Profitability", "number"),
    "dividend_growth_streak_years": MetricPresentation("Dividend-growth streak", "Consecutive latest fiscal years with increasing dividends per share.", "Capital allocation", "number"),
}

OPERATOR_ORDER = [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"]


def presentation_for(metric_name: str) -> MetricPresentation:
    return METRIC_PRESENTATION.get(
        metric_name,
        MetricPresentation(metric_name.replace("_", " ").title(), "Defined Scrooner metric.", "Other", "number"),
    )
