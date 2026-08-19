# SEC EDGAR Opportunity and Recommendations

> **Status:** Consultant recommendation  
> **Date:** 2026-08-18  
> **Authority:** Advisory only. `doc/foundational/02_Scrooner_Decision_Register.md`, `doc/status/PROGRESS.md`, and the current execution backlog remain canonical.

## Executive recommendation

Scrooner can build most of its differentiated fundamental dataset from free, official SEC sources. The opportunity is not merely to collect more filings or add hundreds of ratios. The defensible product is:

> Broad company coverage + reliable security identity + normalized disclosures + decision-oriented signals + transparent source lineage.

The most important next data investment is to move from the golden-company validation set to a useful production universe without weakening the correctness standards already established. In parallel, Scrooner should complete the Screener and AI Query interfaces so the existing data and backend become usable by customers.

Recommended allocation of the next major data effort:

| Area | Suggested share |
|---|---:|
| Widen and harden the company/security universe | 45% |
| Dimensional XBRL and selected footnotes | 25% |
| Filing-event and capital-allocation signals | 20% |
| N-PORT, proxy, and specialized enrichment | 10% |

## Free official SEC sources

SEC EDGAR data is public and does not require a paid subscription. The public data APIs do not require API keys. Automated access must follow the SEC fair-access policy; the SEC currently states a maximum of 10 requests per second in aggregate. Scrooner's existing internal ceiling of 8 requests per second is appropriate.

| Source | Contents | Recommended use |
|---|---|---|
| Submissions API | Filing history, accession numbers, forms, names, former names, tickers, and exchanges | Company discovery and incremental filing updates |
| Company Facts API | Standard, entity-wide XBRL facts for one filer | Fast company-level financial ingestion |
| Company Concept API | History for one company and taxonomy concept | Debugging and targeted refreshes |
| Frames API | One standardized concept across companies for a calendar period | Discovery and broad comparisons, not final fiscal-period calculations |
| EDGAR filing archives | Complete filing HTML, text, XML, inline XBRL, exhibits, and headers | Authoritative detailed extraction and verification |
| `companyfacts.zip` | Nightly bulk Company Facts data | Efficient market-wide bootstrap |
| `submissions.zip` | Nightly bulk filing histories | Efficient universe and filing bootstrap |
| Financial Statement Data Sets | Flattened primary-statement XBRL data | Bulk research and independent validation |
| Financial Statement and Notes Data Sets | Numeric facts, text, dimensions, rendering, presentation, and calculation relationships | Segments, footnotes, extensions, and deeper disclosures |
| Insider Transactions Data Sets | Flattened Forms 3, 4, and 5 | Backfill and validation of insider activity |
| Form 13F Data Sets | Institutional holdings | Institutional ownership and changes |
| Form N-PORT Data Sets | Registered-fund portfolios | Mutual-fund and ETF ownership |
| Other DERA data sets | Form D, N-CEN, N-MFP, Regulation A, crowdfunding, and fund prospectus data | Specialized later products |

Primary references:

- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC Developer Resources](https://www.sec.gov/about/developer-resources)
- [Accessing EDGAR Data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)
- [SEC DERA Data Library](https://www.sec.gov/about/divisions-offices/division-economic-risk-analysis/dera-data-library)
- [Financial Statement and Notes Data Sets specification](https://www.sec.gov/dera/data/fsnds.pdf)
- [Insider Transactions Data Sets](https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets)

## Important SEC data boundary

The Company Facts API is convenient but incomplete for deeper research. It aggregates facts that use a standard taxonomy and apply to the whole reporting entity. It does not preserve all company extensions, footnote text, or dimensional detail.

Scrooner should therefore use a layered approach:

1. Bulk Submissions and Company Facts for efficient discovery and baseline facts.
2. Complete filing XBRL for authoritative contexts, extensions, dimensions, and lineage.
3. SEC quarterly data sets for bulk enrichment and independent reconciliation.
4. Filing HTML and exhibits for information that is not reliably structured.

## What Scrooner can achieve

### 1. A production-scale fundamental universe

The largest immediate opportunity is to expand the verified pipeline from the golden set to several thousand eligible US-listed operating companies.

This enables:

- Useful market-wide screens
- Sector and industry comparisons
- Percentile rankings
- Multi-year consistency screens
- Coverage and freshness scores
- Substantially broader company-page inventory

The company universe must distinguish:

- Companies from traded securities
- Common stocks from preferred shares, warrants, units, debt, funds, and shells
- Primary listings from secondary or historical symbols
- Multiple share classes
- Active, acquired, deregistered, and delisted issuers
- Domestic issuers from ADRs and foreign private issuers
- General operating companies from banks, insurers, REITs, and BDCs

One CIK can have several securities, and one economic company can have multiple traded classes. A first-class `security` model should therefore remain separate from the `company` model.

### 2. Segment and geographic financials

Dimensional XBRL is one of the strongest potential data moats. It can describe facts by:

- Product or service
- Geography
- Operating segment
- Legal entity
- Debt instrument
- Share class
- Customer
- Maturity bucket

Potential queries include:

- Companies whose international revenue is growing faster than domestic revenue
- Companies with material revenue exposure to a selected geography
- Companies whose fastest-growing segment exceeds a threshold
- Companies becoming less dependent on one segment

Start with revenue by operating segment and revenue by geography. Preserve the complete XBRL context and dimensions rather than forcing every fact into one company-period value.

### 3. Financial-statement notes

High-value disclosures available in structured, dimensional, or semi-structured form include:

- Debt maturities and interest rates
- Lease obligations
- Stock-based compensation
- Share repurchases
- Revenue disaggregation
- Customer concentration
- Geographic exposure
- Remaining performance obligations
- Acquisition consideration and goodwill
- Pension obligations
- Effective-tax-rate reconciliation
- Legal contingencies
- Restructuring costs
- Related-party transactions

Every extracted value should carry a source and extraction class:

1. Standard XBRL fact
2. Dimensional or extension XBRL fact
3. Text-extracted disclosure with citation and confidence

A text-derived value must not silently appear equivalent to a directly tagged fact.

### 4. Filing-event intelligence

Scrooner can convert filings into a normalized, source-linked event timeline:

- Earnings release
- Executive appointment or departure
- Auditor change
- Material agreement
- Acquisition or disposition
- Bankruptcy or restructuring
- Impairment or restatement
- Delisting notice
- Cybersecurity incident
- Debt or equity issuance
- Tender offer or going-private process
- Late filing
- Registration withdrawal

Each event should include its type, event date, affected company/security, factual summary, source filing, relevant section, and extraction confidence. An LLM may propose an extraction, but deterministic validation and source citation should govern what is published.

### 5. Insider analytics

Forms 3, 4, and 5 can support:

- Net insider buying over 30, 90, and 365 days
- Open-market purchases separated from grants, exercises, and tax withholding
- Cluster buying by several insiders
- Insider ownership changes
- 10b5-1 versus discretionary activity
- Transaction value relative to the insider's previous holdings
- Officer and director role normalization

Raw sales should not automatically be presented as bearish. Transaction codes, ownership form, exercise activity, tax withholding, and planned-sale flags must be interpreted first.

### 6. Institutional and fund ownership

Combining Forms 13F and N-PORT can produce:

- Institutional ownership estimates
- Quarter-over-quarter changes
- New and exited positions
- Top-holder concentration
- Mutual-fund versus other institutional ownership
- Number of reporting funds holding a security
- Portfolio-weight-based conviction approximations
- Ownership crowding indicators

Every output must show report date and filing date. Neither source represents current, complete ownership, and 13F does not reveal a manager's full economic portfolio.

### 7. Governance and compensation

DEF 14A proxy statements can support executive compensation, CEO pay versus performance, board composition and tenure, auditor fees, related-party transactions, shareholder proposals, voting results, and dual-class governance analysis.

This is useful but substantially harder than financial XBRL, Form 4, or Form 13F processing. It should follow production-universe coverage and the core application interface.

### 8. Capital-allocation analytics

EDGAR can support decision-oriented measures such as:

- Share-count growth and dilution
- Stock-based compensation burden
- Share repurchases and buyback yield
- Dividends
- Capital expenditure
- Debt issuance and repayment
- Acquisitions and goodwill growth
- Cash retained versus distributed

Examples of valuable screens:

- FCF-positive companies reducing their share count
- Companies where stock compensation is high relative to operating cash flow
- Companies issuing shares despite positive free cash flow
- Serial acquirers with rapidly growing goodwill
- Companies directing most free cash flow toward repurchases

## What EDGAR cannot provide well

EDGAR should not be treated as a complete market-data platform. It generally does not provide:

- Reliable current and historical traded prices
- Intraday quotes or market volume
- Analyst estimates and consensus
- Earnings-call transcripts
- General news and sentiment
- Complete short-interest data
- Options data
- Real-time fund flows
- Point-in-time index membership
- A clean commercial industry classification equivalent to GICS
- A universally reliable security master

Alpaca or another properly licensed market-data source remains necessary for current price-dependent calculations. SEC-reported public float is not a substitute for current market capitalization.

## Other free official sources

Other official sources can complement EDGAR after the core company pipeline is production-ready:

| Source | Potential use |
|---|---|
| Federal Reserve and FRED | Interest rates, credit conditions, monetary and macroeconomic series |
| US Treasury | Treasury yield curves and reference rates |
| Bureau of Labor Statistics | Inflation, employment, wages, and industry labor data |
| Bureau of Economic Analysis | GDP, industry output, income, and economic accounts |
| Census Bureau | Trade, manufacturing, retail, and industry data |
| FDIC | Bank identity, financial, deposit, and branch information |
| FINRA | Selected OTC, short-volume, and market-transparency data |

These should be treated as separate, dated data domains rather than mixed into authoritative company filings without provenance.

## Recommended execution order

### Priority 1 — Scale and harden the existing core

Build a production company/security universe, explicit eligibility rules, coverage scores, freshness monitoring, sector-aware definitions, incremental scheduling, failure queues, reconciliation, and point-in-time preservation.

This produces more user value than adding many niche metrics to a tiny company set.

### Priority 2 — Complete the user-facing product

Complete the Screener UI and plain-English Query UI over the already-verified backend. Show:

- The interpreted query before execution
- Pass/fail reasons
- Data dates
- Metric definitions
- Filing lineage
- Coverage and missing-data warnings

Additional data has limited commercial value until customers can use the existing engine.

### Priority 3 — Add decision-oriented metrics

Prioritize:

- Share-count growth and dilution
- Stock-based compensation burden
- Net cash and net debt
- Buyback yield
- FCF growth and consistency
- Gross-margin trend
- Operating leverage
- Accrual and cash-conversion quality
- Debt-maturity pressure
- Revenue concentration
- Segment growth
- Capital-allocation history

Avoid expanding to hundreds of undifferentiated ratios.

### Priority 4 — Build a disclosure-event layer

Normalize important 8-K and other filing events into a traceable timeline. Begin with item codes and structured fields, then add carefully validated text extraction.

### Priority 5 — Add dimensions and notes selectively

Recommended initial order:

1. Segment revenue
2. Geographic revenue
3. Share repurchases and dilution
4. Debt maturities
5. Stock-based compensation
6. Customer concentration

## Product guardrails

- Preserve raw filings and immutable provenance.
- Treat each published metric as a versioned definition.
- Store both filing date and financial period date.
- Prevent look-ahead bias in historical screens.
- Expose null reasons rather than guessing missing data.
- Keep standard facts, extension facts, and text extractions distinguishable.
- Show the original filing for every material signal.
- Measure coverage by metric, company type, fiscal period, and source—not only total row count.
- Maintain sector-specific definitions where a universal formula would be misleading.
- Perform a legal and data-licensing review before public launch and redistribution.

## Final conclusion

Free official SEC data is sufficient for Scrooner to become a broad, defensible fundamental research and screening product. The best path is not maximum ingestion. It is to transform official disclosures into a smaller number of reliable, decision-relevant facts and signals across a genuinely useful company universe, while preserving enough lineage for users to verify every important result.

