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
    # Added 2026-09-10, alongside widening the Screener's catalog past
    # `requires_price = false` -- these 34 metrics were already computed
    # and already screenable-by-name, but fell back to an auto-generated
    # label/"Other" category before this (see presentation_for() below).
    "market_cap": MetricPresentation("Market cap", "Shares outstanding multiplied by price.", "Valuation", "currency"),
    "trailing_pe": MetricPresentation("Price / Earnings (P/E)", "Price divided by trailing twelve-month diluted EPS.", "Valuation", "multiple"),
    "price_to_sales": MetricPresentation("Price / Sales", "Market cap relative to trailing twelve-month revenue.", "Valuation", "multiple"),
    "price_to_book": MetricPresentation("Price / Book", "Market cap relative to stockholders' equity.", "Valuation", "multiple"),
    "ev_ebitda": MetricPresentation("EV / EBITDA", "Enterprise value relative to trailing twelve-month EBITDA.", "Valuation", "multiple"),
    "ev_sales": MetricPresentation("EV / Sales", "Enterprise value relative to trailing twelve-month revenue.", "Valuation", "multiple"),
    "peg_ratio": MetricPresentation("PEG ratio", "Trailing P/E divided by year-over-year EPS growth.", "Valuation", "multiple"),
    "dividend_yield": MetricPresentation("Dividend yield", "Trailing twelve-month dividends per share divided by price.", "Shareholder returns", "percentage"),
    "fcf_yield": MetricPresentation("FCF yield", "Trailing twelve-month free cash flow relative to market cap.", "Valuation", "percentage"),
    "buyback_yield": MetricPresentation("Buyback yield", "Trailing twelve-month share buybacks relative to market cap.", "Shareholder returns", "percentage"),
    "total_shareholder_yield": MetricPresentation("Total shareholder yield", "Dividend yield plus buyback yield, less share-count dilution.", "Shareholder returns", "percentage"),
    "payout_ratio": MetricPresentation("Dividend payout ratio", "Dividends per share relative to diluted EPS.", "Shareholder returns", "percentage"),
    "dividends_pct_fcf": MetricPresentation("Dividends as % of FCF", "Dividends paid relative to trailing twelve-month free cash flow.", "Shareholder returns", "percentage"),
    "share_repurchases_pct_fcf": MetricPresentation("Buybacks as % of FCF", "Share buybacks relative to trailing twelve-month free cash flow.", "Shareholder returns", "percentage"),
    "cash_returned_to_shareholders": MetricPresentation("Cash returned to shareholders", "Dividends paid plus share buybacks for the period.", "Shareholder returns", "currency"),
    "dps_growth_yoy": MetricPresentation("Dividend growth (YoY)", "Change in dividends per share versus the same fiscal period one year earlier.", "Shareholder returns", "percentage"),
    "dps_growth_3y_cagr": MetricPresentation("Dividend growth (3Y CAGR)", "Compound annual growth in dividends per share over three fiscal years.", "Shareholder returns", "percentage"),
    "pretax_margin": MetricPresentation("Pretax margin", "Income before tax as a share of revenue.", "Profitability", "percentage"),
    "ebitda_margin": MetricPresentation("EBITDA margin", "Trailing twelve-month EBITDA as a share of revenue.", "Profitability", "percentage"),
    "book_value_per_share": MetricPresentation("Book value per share", "Stockholders' equity divided by shares outstanding.", "Financial strength", "currency"),
    "net_cash": MetricPresentation("Net cash", "Cash and equivalents less total debt.", "Financial strength", "currency"),
    "net_cash_per_share": MetricPresentation("Net cash per share", "Net cash divided by shares outstanding.", "Financial strength", "currency"),
    "working_capital": MetricPresentation("Working capital", "Current assets less current liabilities.", "Financial strength", "currency"),
    "debt_to_ebitda": MetricPresentation("Debt / EBITDA", "Total debt relative to trailing twelve-month EBITDA.", "Financial strength", "multiple"),
    "fcf_per_share": MetricPresentation("Free cash flow per share", "Trailing twelve-month free cash flow divided by shares outstanding.", "Cash flow", "currency"),
    "fcf_growth_yoy": MetricPresentation("FCF growth (YoY)", "Change in free cash flow versus the same fiscal year one year earlier.", "Growth", "percentage"),
    "net_change_in_cash": MetricPresentation("Net change in cash", "The period's total cash movement across operating, investing, and financing activities.", "Cash flow", "currency"),
    "ocf_to_net_income": MetricPresentation("Cash conversion (CFO / Net income)", "Cash from operations relative to net income -- an earnings-quality signal.", "Accounting quality", "multiple"),
    "net_income_growth_yoy": MetricPresentation("Net income growth (YoY)", "Change in net income versus the same fiscal period one year earlier.", "Growth", "percentage"),
    "net_income_growth_3y_cagr": MetricPresentation("Net income growth (3Y CAGR)", "Compound annual net income growth over three fiscal years.", "Growth", "percentage"),
    "net_income_growth_5y_cagr": MetricPresentation("Net income growth (5Y CAGR)", "Compound annual net income growth over five fiscal years.", "Growth", "percentage"),
    "net_income_growth_10y_cagr": MetricPresentation("Net income growth (10Y CAGR)", "Compound annual net income growth over ten fiscal years.", "Growth", "percentage"),
    "diluted_shares_growth_yoy": MetricPresentation("Share count growth (YoY)", "Change in diluted shares outstanding versus the same fiscal period one year earlier.", "Capital allocation", "percentage"),
    "diluted_shares_growth_3y_cagr": MetricPresentation("Share count growth (3Y CAGR)", "Compound annual growth in diluted shares outstanding over three fiscal years.", "Capital allocation", "percentage"),
    "diluted_shares_growth_5y_cagr": MetricPresentation("Share count growth (5Y CAGR)", "Compound annual growth in diluted shares outstanding over five fiscal years.", "Capital allocation", "percentage"),
}

OPERATOR_ORDER = [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"]


def presentation_for(metric_name: str) -> MetricPresentation:
    return METRIC_PRESENTATION.get(
        metric_name,
        MetricPresentation(metric_name.replace("_", " ").title(), "Defined Scrooner metric.", "Other", "number"),
    )
