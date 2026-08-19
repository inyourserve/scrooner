<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Build for decisions, not data dumps

Correct direction. Investors do not need 200 ratios; they need a compact set of datapoints that answer: **business quality, growth durability, financial risk, valuation, and thesis change**. SEC filings are a strong primary source because 10-Ks describe the business, risks, operating results, and management’s discussion; EDGAR’s XBRL APIs provide structured financial-statement facts for calculation.[^1][^2]

For every datapoint, show:

- Current value
- 3–5 year trend
- Sector/industry percentile
- What changed versus last quarter/year
- Formula, source filing, fiscal period, and update date


## The decision dataset

| Decision | Datapoint | Best display |
| :-- | :-- | :-- |
| Is it a good business? | Revenue growth, gross margin, operating margin, free-cash-flow margin, ROIC | 5-year chart + peer percentile |
| Is growth durable? | 3/5-year revenue CAGR, quarterly YoY growth, customer/revenue concentration, recurring-revenue share where disclosed | Trend and acceleration/deceleration flag |
| Does profit become cash? | Operating cash flow, capex, free cash flow, FCF conversion, stock-based compensation as % of revenue | “Earnings quality” panel |
| Is the balance sheet safe? | Cash, total debt, net debt, net debt/EBITDA, interest coverage, current ratio, debt maturities | Debt-risk meter + maturity timeline |
| Is management shareholder-friendly? | Share-count change, buybacks, dilution from SBC, insider ownership, insider buying/selling | Ownership and capital-allocation panel |
| Is the price sensible? | Forward P/E, EV/EBITDA, EV/sales, P/FCF, FCF yield, valuation versus 5-year median and peers | Valuation range, not a single “cheap/expensive” label |
| What could break the thesis? | Top risks from 10-K, revenue/customer concentration, legal/regulatory flags, guidance change, estimate revisions | “Risks and changes” card |
| Is market evidence improving? | 6/12-month relative return vs S\&P 500, drawdown from 52-week high, earnings-day reaction, abnormal volume | Secondary confirmation—not the investment thesis |

## The four most powerful derived metrics

These are more decision-useful than raw numbers alone:

1. **Revenue-growth durability**
Compare 1-year, 3-year, and 5-year revenue CAGR. If growth is persistently falling, the business may be maturing or losing advantage.
2. **Return on invested capital**

$$
\text{ROIC} =
\frac{\text{NOPAT}}{\text{Invested Capital}}
$$

High and stable or rising ROIC is a strong signal that the business earns attractive returns on the capital it uses.
3. **Free-cash-flow conversion**

$$
\text{FCF Conversion} =
\frac{\text{Free Cash Flow}}{\text{Net Income}}
$$

Over multiple years, this tests whether reported profit turns into cash. Show it with a warning where the denominator is negative or unusually small.
4. **Shareholder yield**

$$
\text{Shareholder Yield} =
\text{Dividend Yield} +
\text{Net Buyback Yield}
$$

Net buyback yield must account for new shares issued through stock-based compensation; otherwise, “buybacks” can look better than their actual benefit to owners.

## Datapoints to make mandatory

For each stock detail page and screener result row, prioritize these **15 fields**:

- Market cap
- Revenue growth: TTM and 3-year CAGR
- EPS growth: TTM and 3-year CAGR
- Gross margin
- Operating margin
- Free-cash-flow margin
- ROIC
- Net debt/EBITDA
- Interest coverage
- Free cash flow
- Share-count change over 3 years
- Forward P/E
- EV/EBITDA
- P/FCF or FCF yield
- Next earnings date and latest guidance direction

This gives an investor enough information to decide whether a stock deserves deeper research—without implying that a screen itself is a buy recommendation.

## “Decision cards” on results

Instead of one opaque score, create five explainable cards:

- **Business:** Growth, margins, ROIC.
- **Financial safety:** Cash, leverage, interest coverage, debt due.
- **Valuation:** Multiples versus history and peers.
- **Shareholder alignment:** Dilution, buybacks, dividends, insider ownership.
- **Recent change:** Earnings surprise, guidance, estimate revisions, price reaction.

A final **“Why this passed your screen”** section is critical: list the exact rules met, rules nearly failed, and missing or unreliable datapoints. SEC XBRL facts include historical company concepts and reporting-period metadata, allowing the product to retain source-level traceability rather than presenting unexplained ratios.[^3][^1]

For the first user-facing screen, which investing decision should the product optimize for: **finding high-quality long-term compounders**, **finding undervalued cash-generative companies**, or **finding fast-growing companies before earnings accelerate**?
<span style="display:none">[^10][^11][^12][^13][^14][^15][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

[^2]: https://www.sec.gov/files/reada10k.pdf

[^3]: https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets

[^4]: https://api.ai-analytics.org/datasets/sec-financial-facts

[^5]: https://apis.io/apis/sec-edgar/sec-edgar-xbrl-api/

[^6]: https://tldrfiling.com/blog/sec-edgar-api-guide/

[^7]: https://fundamentalshub.com/blog/sec-edgar-api-complete-guide

[^8]: https://sec-api.io/

[^9]: https://dealcharts.org/blog/sec-edgar-api-guide

[^10]: https://sec-api.io/products/apis

[^11]: https://apify.com/labrat011/sec-edgar-scraper

[^12]: https://sec-api.io/docs/financial-statements

[^13]: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

[^14]: https://xbrl.us/forums/topic/label-in-company-facts-api/

[^15]: https://edgartools.readthedocs.io/en/latest/api/xbrl/

