# US public-company filings: domain reference for every data role

Status: v1.1, 2026-10-18, written by Dhairya from SEC rules and repo-verified cases; the former [VERIFY] items were checked against SEC rule text and real filings (data-team/25) and corrected above. Remaining [VERIFY] items are still unconfirmed. Items marked [VERIFY] are stated from general knowledge and must be confirmed against a live filing or sec.gov rule text before an agent relies on them for a decision. Add confirmed items to `22-FILING-LESSONS-LEDGER.md` with the accession that proved them.

## 1. Who files what
- **Domestic issuers:** 10-K (annual), 10-Q (Q1-Q3 only), 8-K (events), 10-K/A and 10-Q/A (amendments). **There is no Q4 10-Q.** Q4 flow figures are not filed as such; they are derived (FY minus 9-month YTD) or taken from the earnings release.
- **Foreign private issuers:** 20-F / 40-F / 6-K. Outside V1 operating scope (doc 02). Do not mix into denominators.
- **Other forms that change meaning:** 10-KT (transition period, different length), NT 10-K / NT 10-Q (late-filing notices), Form 15 (deregistration), 8-K Item 2.02 + Exhibit 99.1 (earnings release), 8-K Item 4.02 (non-reliance on prior financials = a restatement warning), S-1 / 424B (IPO).
- **Filer categories** (large accelerated, accelerated, non-accelerated, smaller reporting company, emerging growth) change deadlines and which disclosures exist. Smaller reporting companies may omit items and present two years of income statements instead of three, so a "missing" earlier year can be legitimate.
- **XBRL phase-in (verified 2026-10-18, doc 25):** three cohorts keyed to fiscal period end, starting with a 10-Q: large accelerated filers with over $5B float from 2009-06-15; other large accelerated filers from 2010-06-15; all others including small companies from 2011-06-15 (Release 33-9002). Footnotes were fully tagged one year after each start. Inline XBRL: 2019, 2020, 2021 by cohort (Release 33-10514). Full coverage is reliable from about 2011. Earlier comparison periods (1-3 years) appear in the first XBRL filings, but only as re-presented there, never as originally filed.

## 2. Periods and fiscal calendars
- Fiscal year end is company-specific; fiscal year label (`dei:DocumentFiscalYearFocus`) is not the calendar year and is sometimes wrong. Trust actual period start/end dates over labels.
- 52/53-week years end on a weekday near a month end; a 53rd week makes a year ~371 days. A 52-week year is 364 days and a 53-week year is 371, so an exact 365-day test rejects both (Apple FY2022 = 364, FY2023 = 371). Quarters are 91 days; in a 53-week year only ONE quarter gets the extra week (98 days; Apple puts it in Q1), and year-to-date periods after it lengthen (Apple 9M = 280 days vs 273). Not every non-December filer is 52/53-week: Nike's year always ends May 31.
- **Flow vs instant:** income-statement and cash-flow items are durations; balance-sheet items are instants. Mixing them is a classification error.
- **10-Q cash-flow statements are cumulative year-to-date** (6 and 9 months), not discrete quarters. Discrete Q2 = 6M YTD minus 3M YTD. Income statements in 10-Qs show both the quarter and YTD.
- **Q4 = FY minus 9M YTD** only for additive flows with same-basis inputs. Not valid for: EPS (never subtract), weighted-average shares, ratios, or any item restated between the two filings. Restated prior periods must use same-vintage inputs.
- Transition periods (10-KT), fiscal-year-end changes and short first years break any "full-year = 12 months" assumption.

## 3. XBRL mechanics that cause wrong numbers
- A fact = concept + period + unit + dimensions. **No-dimension facts are the consolidated total**; dimensional facts are segments, classes or components and must never be read as the total.
- **Duplicates are normal:** the same fact appears in many filings (each 10-K repeats prior years). Restated values appear with a later filing date; the latest-filed figure for a period is the current one unless policy says otherwise.
- **Decimals/precision:** the same figure can be reported as 3,372,772K and 3,372.8M. Equal within rounding is not a conflict.
- **Scale and sign:** values are stored in full units; a displayed-in-thousands error is a x1000 bug. Sign follows the tag's balance type and the `negated` label flag; check it, do not assume.
- **Units:** `USD`, `shares`, `USD/shares`, `pure`. A tag filed in a foreign currency or wrong unit is a data error (repo example: `dei:EntityPublicFloat` unit-scale bug, eBay at $31 quintillion).
- **Tag taxonomy drift:** the same economic line is filed under different tags over time and across companies (repo example: AAPL revenue under 3 tags). Mappings must be scoped by period and company, and new tags enter yearly via the us-gaap taxonomy; old ones are deprecated [VERIFY per release].
- **Custom (extension) tags:** company-specific, prefix is the ticker/CIK-style namespace. The SEC's published average for 2018-2020 is 16-21% of tagged values using extension tags; our own 9.2% of face lines (doc 56, one quarter) uses a different denominator, so state the denominator before quoting either; they are not comparable across companies without a definition check.
- **Combined lines** ("Accounts payable and accrued liabilities") must never be mapped as one of their components.
- **Share classes:** one issuer can have several securities (GOOG/GOOGL, preferreds, ETNs sharing a CIK, e.g. JPM has 9 listings). Identity is issuer (CIK) first, security second; per-share data may be per-class.
- The SEC companyfacts/frames APIs **strip dimensional data**; segment and geography need the filing's own XBRL instance.

## 4. Accounting changes that create structural breaks
- Adoption year depends on fiscal year end and filer type; never assume one break year (verified, doc 25). ASC 606: annual periods beginning after 2017-12-15 (Apple adopted FY2019; emerging growth companies can be later); revenue tag moved to `RevenueFromContractWithCustomerExcludingAssessedTax` at adoption. ASC 842 leases: fiscal years beginning after 2018-12-15 (Apple FY2020; an emerging growth company adopted 2022-01-01). CECL: 2020 for SEC filers not eligible as smaller reporting companies, 2023 for smaller reporting companies and others; banks could defer to as late as 2022-01-01 under the CARES Act; CECL also applies outside banks. FASB's own text was not openable by automated fetch; dates rest on issuer 10-Ks.
- **Restatements** (10-K/A, 10-Q/A, 8-K Item 4.02; Item 4.02 can cover interim statements, e.g. Calumet Q1/Q2 2025 cash flows) change prior-period values; "as originally reported" and "as restated" are both real, so a metric must name its basis.
- **Discontinued operations** are re-presented in prior periods, so growth rates can use different perimeters across filings.
- Stock splits and dividends retroactively change per-share and share-count data; stored older filings keep pre-split values (repo: retroactive split-adjustment stage; basic vs diluted EPS adjustment can differ).

## 5. Sector templates (a blank is often correct)
- **Banks / thrifts (SIC 60xx-61xx):** no gross profit, no current/non-current balance sheet; interest income and expense, net interest income, provision for credit losses, noninterest expense. Efficiency ratio, NIM, Tier 1 capital are bank-specific; FDIC data is a labelled secondary source for the top banks (decisions.md 2026-10-18).
- **Insurers (63xx):** premiums, losses and loss adjustment expenses, no gross margin; investment-heavy balance sheets.
- **REITs (SIC 6798 and real-estate):** FFO/AFFO are non-GAAP and not in XBRL face statements; depreciation is large and operating-income comparisons mislead.
- **Utilities, airlines, hotels, rental, pipelines, shells/SPACs, pre-revenue biotech:** often no cost of revenue or no gross profit line; unclassified balance sheets have no current/non-current split, so current ratio is correctly "not reported".
- A template is a hypothesis; confirm on the actual filing before classifying a blank as not-applicable.

## 6. Source hierarchy and what can prove what
1. The filing itself (HTML/iXBRL, R-files, the instance) is the evidence. 2. SEC structured APIs and Financial Statement Data Sets are derived from it: same values, useful for ranking and cross-checks, not independent proof. 3. Earnings release (8-K Item 2.02, usually Ex. 99.1 by convention, "furnished" not "filed"): headline figures, may be non-GAAP; the 8-K's XBRL covers only the cover page, so these numbers are NOT in XBRL or companyfacts. 4. Vendors (yfinance etc.) are comparison signals only and can never classify a blank or verify a value.
- **"Not in the XBRL" is not "not in the filing."** 18% of a rendered-statement sample showed a line that the XBRL lacked, so absence needs the rendered statement, not just a tag query.
- SEC fair-access rules: declared User-Agent, rate limits (doc 07). Never exceed them.

## 7. How roles should use this
- Before proposing, ask: which filing form, which period type, which dimension, which vintage (original or restated), which unit and scale, which sector template, which share class?
- Write down which assumption from this file your conclusion depends on. If it is [VERIFY], verify it first and record the proof in the ledger.
