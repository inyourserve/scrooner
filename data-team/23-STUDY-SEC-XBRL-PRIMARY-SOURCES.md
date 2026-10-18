# Study: SEC / XBRL / FASB primary sources for the Scrooner data agents

Status: v1, written 2026-10-18. Every "Read" date below is 2026-10-18 (the session date). Scope: topics 1-5 of the study brief. Only sec.gov, fasb.org (including xbrl.fasb.org and storage.fasb.org), xbrl.us and eCFR were used. Where a page could not be fetched as text, the PDF was downloaded and converted locally; that is stated.

How to read this file:
- "Verified" = text read in the cited source. "Observed" = I queried the live SEC API once and looked at the raw rows (AAPL NetIncomeLoss companyconcept, section 1.6). "Not confirmed" = see section 7.
- The source label is given as `[S#]` and expanded in the Source index at the bottom.
- Other files were not edited and the database was not touched.

---

## 1. EDGAR Filer Manual, EDGAR XBRL Guide, phase-in dates, amendments, API behaviour

### 1.1 Where the technical XBRL rules now live
- Filer Manual Volume II version 78 (dated September 14, 2026) removed the technical XBRL submission rules from Chapter 6 and moved them to the EDGAR XBRL Guide (August 2026). Inline XBRL details of Chapter 5.2.5 also point to the Guide. [S1] (read 2026-10-18)
- Consequence: older citations "EFM 6.x.x" are renumbered. The Guide marks each rule "Formerly EFM v68 § 6.6.xx". Example: sign rule is Guide 6.5.4, formerly EFM v68 § 6.6.30. [S2]
- Filer Manual version history seen: v77 (March 16, 2026), v78 (September 14, 2026). [S1]

### 1.2 XBRL phase-in dates (original XBRL, Release 33-9002, Jan 2009)
Verified in the release text and in the adopted rule text (Item 601(b)(101)). [S3] (read 2026-10-18)

| Cohort | First required in | Fiscal period trigger |
|---|---|---|
| US GAAP large accelerated filers with worldwide common equity float above $5 billion (end of Q2 of last completed FY) | 10-Q (or 20-F/40-F) | financial statements for a fiscal period ending on or after **June 15, 2009** |
| All other US GAAP large accelerated filers | 10-Q | fiscal period ending on or after **June 15, 2010** |
| All remaining filers: other US GAAP filers including smaller reporting companies, and IFRS-as-issued-by-IASB foreign private issuers (20-F/40-F) | 10-Q (FPIs: annual report) | fiscal period ending on or after **June 15, 2011** |

Details from the same release:
- The first XBRL submission is a 10-Q (or the first periodic report with a period past the trigger), not necessarily a 10-K. So a Dec-FYE company in the 2011 cohort had no XBRL until its 10-Q for the quarter ended June 30, 2011; its FY2011 10-K (filed early 2012) was the first annual XBRL, carrying FY2010 comparatives.
- Year 1 of a filer's own phase-in: footnotes may be block-tagged. "In year two, a filer will have a similar 30 day grace period for its first interactive data exhibit that includes detailed tagging of its footnotes and schedules." So detail-tagged (Level 4) notes start in a filer's second year, i.e. 2010 (cohort 1), 2011 (cohort 2), 2012 (cohort 3). [S3]
- 30-day grace: the initial interactive data exhibit may be submitted within 30 days after the earlier of the due date or filing date of the related report. [S3]
- Asset-backed and investment company filings were not covered. [S3]
- Original data: SEC Financial Statement Data Sets begin with submissions from 4/15/2009 ("2009q1.zip" is intentionally empty). [S4]

### 1.3 Inline XBRL phase-in (Release 33-10514, effective September 17, 2018)
Verified from the release PDF (downloaded, text-extracted). [S5] (read 2026-10-18)

| Operating company cohort | Inline XBRL compliance |
|---|---|
| Large accelerated filers using US GAAP | fiscal periods ending on or after **June 15, 2019** |
| Accelerated filers using US GAAP | fiscal periods ending on or after **June 15, 2020** |
| All other filers | fiscal periods ending on or after **June 15, 2021** |

- Footnote 151 of the release: a Form 10-Q filer is not subject to Inline XBRL for a 10-K "until after they have been required to comply with the Inline XBRL requirements for their first Form 10-Q for a fiscal period ending on or after the applicable compliance date." So a Dec-FYE large accelerated filer's first iXBRL filing was the 10-Q for the quarter ended June 30, 2019; its first iXBRL 10-K was FY2019 (filed early 2020).
- Funds had separate later dates (large fund groups Sep 17, 2020; small Sep 17, 2021). IFRS foreign private issuers were handled separately. [S5]
- Inline XBRL means the XBRL is embedded in the HTML filing itself; the EDGAR XBRL Guide (Aug 2026) is "the technical specification document containing detailed information regarding the submission of Inline XBRL documents". [S1][S2]
- Voluntary early iXBRL existed before these dates (the release refers to an Exemptive Order and voluntary filings). [S5] So "first iXBRL date" is a cohort floor, not a guarantee for each filer.
- Cover page tagging: see section 7 (not confirmed from the text read).

### 1.4 Validation consequences: errors strip the XBRL, not the filing
Verified in Guide 1.6 (Errors, Suspension, Rendering). [S2]
- "If validation of an instance produces an 'XBRL Error,' it is considered an EDGAR warning, and all the file attachments comprising that instance are normally removed." The rest of the submission is accepted. Whether suspension results depends on the instance type.
- So a 10-K can sit on EDGAR with its HTML but without XBRL financial data. "No XBRL fact" can mean "XBRL was stripped for an error", not "the filer did not tag".
- Warnings ("W" in the Guide's tables) do not suspend. Many dei checks are warnings (e.g. a missing `dei:EntityPublicFloat`).

### 1.5 Duplicate facts, decimals, scale, sign (Guide chapters 6 and 9)
Verified. [S2] (read 2026-10-18)
- **No scale in values (6.6.1):** "The content of a numeric fact never has a scale factor." Twenty thousand is 20000, never 20. 20% is 0.2, never 20. Units cannot imply scale on a currency (6.6.2): only `iso4217:USD`, never "thousands of USD".
- **Decimals is precision, not scale (6.6.4):** "The decimals attribute is not a scale factor." INF = exact; -3 = rounded to thousands; -6 = millions.
- **Duplicates (9.10):** an instance must not have more than one fact with equal concept, context and unit unless values are consistent. For numerics "all such values must be consistent with having been rounded from a single value." Method: a closed interval of size 10^n (n = decimals) around each value; intervals must overlap. Example: 500 at decimals -2 gives 450-550; 550 at decimals -1 gives 545-555; consistent. Consistent duplicates are consolidated into one fact "having the value of the fact with the maximum specified decimals value". Inconsistent duplicates are an XBRL Error. "The values of the id attributes are not relevant."
- Rendering (7.3.4): the same net income appears on the income statement and in the cash flow statement; "the duplicated numeric fact having the most significant digits will be selected for rendering".
- **Sign (6.5.4):** "Invert the sign of a numeric fact whose element has an i:balance value that is inconsistent with the reporting concept being reported. Often, this means entering a negative value into the instance, irrespective of whether that negative value will subsequently be rendered without brackets by applying a negating label." The element's balance is assigned "from the perspective of the income statement and balance sheet where the amount is positive" and may disagree with the cash flow presentation. Registrants "should not create a new element if an element in a standard taxonomy namespace is consistent with the financial concept reported in all respects except i:balance."
- **Negated labels (6.5.5):** display-only. Example: `us-gaap:TreasuryStockValue` (debit) with `negatedLabel` shows "(Less) Treasury Stock". The stored value is the economic value.
- **Period type (6.3.1):** an element used for amounts must have the periodType (instant or duration) of the amounts. The same element can be a beginning or ending balance; "The differentiating factor is the point in time, which is identified in the instance document and not the taxonomy."
- **Periods are dates, not times (6.3.2):** a period begins 00:00:00 of its first day and ends 24:00:00 of its last day.
- **Non-currency units (6.6.3):** one implicit power-of-ten scale factor per instance (e.g. MBoe). Another source of scale bugs.

### 1.6 What companyfacts / companyconcept / frames contain
Verified on the SEC API page [S6] (read 2026-10-18) and observed on one live response [S7] (2026-10-18).

From [S6]:
- Included: "Facts that use a non-custom taxonomy (us-gaap, ifrs-full, dei, or srt) and apply to the entire filing entity." Excluded: custom (extension) taxonomy facts.
- The page never uses the word "dimension". "Apply to the entire filing entity" is the only statement. The effect is that segment, product, geography and class-of-share facts (they need an axis/member) are absent. This matches doc 21; the SEC text is just less explicit than doc 21 implies.
- companyconcept: "A separate array of facts for each unit of measure the company disclosed, such as USD and CAD."
- frames: "One fact per reporting entity for a given concept and period. Each entity's fact is the last one filed that most closely fits the requested period." Forms covered: 10-Q, 10-K, 8-K, 20-F, 40-F, 6-K and variants.
- Frame period rules: annual `CY####` = 365 days +/-30; quarterly `CY####Q#` = 91 days +/-30; instantaneous `CY####Q#I`. "Periods are assembled from the dates that best align with a calendar quarter or year... users should check the start and end dates."
- Units in frames: numerator and denominator joined with "-per-" (USD-per-shares); default unit is "pure".
- Latency: XBRL APIs usually under a minute after dissemination; `companyfacts.zip` republished nightly about 3:00 a.m. ET. No API key. Bulk ZIPs recommended for volume.

Observed on `companyconcept/CIK0000320193/us-gaap/NetIncomeLoss.json` ([S7], one request, SEC-compliant User-Agent):
- Row keys are exactly: `start, end, val, accn, fy, fp, form, filed` (+ `frame` on some rows). There is no dimension, no decimals, no tag version, no restated/original flag.
- The same fact (FY ended 2022-09-24, 99,803,000,000) appears three times, from accessions 0000320193-22-000108 (fy 2022), -23-000106 (fy 2023) and -24-000123 (fy 2024). `frame: CY2022` is attached to only one of the three rows (the latest). So `fy`/`fp` are the fiscal focus of the FILING that carried the fact, not of the fact's period, and `frame` is a label placed on one chosen duplicate.
- Frame label for an Apple September-FYE year is `CY2022` (calendar-aligned), not a fiscal label.
- Form mix in the row set: 10-K 139, 10-Q 174, 8-K 22, 10-K/A 3. So 8-K-sourced and 10-K/A-sourced facts are in companyfacts.
- The 8-K rows (accession 0001193125-13-170623 filed 2013-04-24, and 0001193125-15-023732 filed 2015-01-28) contain recast quarterly and annual values; the first has `fy=2012, fp=FY` on rows whose periods are single quarters, the second has `fy=None, fp=None`. So `fp='FY'` does not guarantee a full-year duration and `fy`/`fp` can be null.
- 10-K/A accession 0001193125-10-012091 (filed 2010-01-25) carries three fiscal years (2007-2009) with `fy=2009`.

### 1.7 Amendments in the XBRL
- `dei:AmendmentFlag` is expected on all instances except one type; "This is not the same as the '/A' indicator on an EDGAR submission type; it is possible for an '/A' submission to amend only material that was not XBRL tagged content." `dei:AmendmentDescription` is expected when the flag is true. [S2, Guide 3.1.6]
- `dei:DocumentFiscalPeriodFocus` allowed values: `Q1|Q2|Q3|FY`. "FY for an annual report that includes the 4th quarter, or for a transition report such as a 10-KT." There is no `Q4` value. [S2, 3.1.8]
- Flags: `dei:DocumentAnnualReport`, `DocumentTransitionReport`, `DocumentQuarterlyReport`, `DocumentShellCompanyReport` (booleans). [S2, 3.1.23.1]
- Annual reports are expected to carry `dei:DocumentFinStmtErrorCorrectionFlag` (is there an error correction in the statements) and, if true, `dei:DocumentFinStmtRestatementRecoveryAnalysisFlag` (did the restatement trigger a compensation recovery analysis). Validation severity is a warning ("W"). [S2, 3.1.23.2] This is a machine-readable restatement signal inside the 10-K itself.
- `dei:EntityFilerCategory` values: `Large Accelerated Filer | Accelerated Filer | Non-accelerated Filer` (case-sensitive). [S2, 3.1.13]
- `dei:EntityPublicFloat`: "A filer having no common shares outstanding will have a $0 public float fact, not nil." Instant context. A negative public float is an example of a validation failure. [S2, 3.1.15]
- `dei:EntityCommonStockSharesOutstanding` has three permitted layouts: (1) one fact with no dimensions, (2) at least two facts under `StatementClassOfStockAxis`, (3) at least two under `ClassesOfShareCapitalAxis`. "The cases are mutually exclusive." [S2, 3.2.3] So for multi-class issuers there is NO undimensioned total.
- Auditor name, location and PCAOB firm ID are three required facts for annual statements for periods ending after 12/31/2020. [S2, 3.1.16]
- Subsequent-event context in the Guide = instant, no taxonomy-defined dimensions, date on or after the end of the required context. [S2, 3.1.15]

### 1.8 Custom (extension) taxonomy rules relevant to us
[S2, chapter 5] (read 2026-10-18)
- 5.6.1 Do not duplicate pre-existing concept declarations. 5.6.2 Avoid changes in declarations from period to period. 5.10.1 Do not duplicate numeric concepts.
- 6.5.7: a company's extension schema changes with each submission and the `versionDate` in its targetNamespace must change; so a custom tag's namespace is filing-specific. A custom element is therefore identified (in the Financial Statement Data Sets) by tag + `version = adsh`, not by name alone. [S4]
- DQC_0215 (effective Dec 15, 2025) flags an extension element whose name matches a us-gaap element. [S8]

### 1.9 Consolidated vs dimensional contexts
[S2, 6.2.x] (read 2026-10-18)
- A context may name an entity with subsidiaries via `ConsolidatedEntitiesAxis`; "Facts in a consolidating instance with a context that names an entity with subsidiaries applies collectively to subsidiaries within that subset."
- Multiple co-registrants (dual registrants) share one instance; the Financial Statement Data Sets have `nciks`, `aciks` and a `coreg` column ("NULL indicates the consolidated entity"). [S4]

---

## 2. XBRL US Data Quality Committee (DQC)

### 2.1 What the rule list is
- The approved-rules page lists rules from DQC_0001 to DQC_0252 (numbers are not contiguous), and references "Approved Rules v31.0.0". Rules 0245-0252 were approved October 7, 2026. [S8] (read 2026-10-18)
- Deprecated per the page: 0082 (after 2022), 0083 (after 2020), 0086 (after 2025), 0100 (after 2023), 0158 (after 2025). 0011 "To be superseded by 0182" (dimensional equivalents using the meta taxonomy). [S8]
- DQC rules are embedded in the FASB taxonomy as a "DQC Rules Taxonomy" (2026 release notes section 2.7). [S9]
- EDGAR runs a subset of the rules as XBRL warnings: "The SEC's EDGAR Release 21.1 said EDGAR would support XBRL US DQC rules in the US GAAP 2021 Taxonomy... EDGAR will inform filers of certain quality defects via warning messages. The example given is a negative value used to tag accounts payable or compensation expense" (search-result summary of [S10]). XBRL US also says the SEC test-filing negative-values check "does not consider all the exclusions that should be allowed." [S10]
- Therefore a DQC rule hit is evidence of a filer tagging problem, but a value that passes these checks is not verified.

### 2.2 Rules grouped by error type (rule IDs and effective dates as listed on [S8])
Descriptions are the page's own short descriptions. I opened the individual rule pages only for those marked (page).

**Sign errors / negative values**
- DQC_0015 Negative Values (US GAAP), effective Jan 1, 2016, v24 June 2024 (page). Logic: a fact for an element on the "should not be negative" list with value < 0 is flagged, unless a member that allows negatives is present (exclusion spreadsheet; examples: `AdjustmentsForChangeInAccountingPrincipleAxis`, ASC 606 transition difference members). "A value shown in parentheses in the HTML should still be positive in the XBRL. A negated label can display it in parentheses, so the fact itself should not be made negative." Basis: "The US GAAP Taxonomy is designed so that the majority of elements have a positive value." The list is ordered by error frequency; elements were dropped over time (six dropped in March 2017 after FASB clarified they can be negative). Sample tested elements include Accrued Liabilities and Other Liabilities, Deferred Tax Assets Valuation Allowance, Extinguishment of Debt Amount, Derivative Notional Amount, Cash Acquired in Excess of Payments to Acquire Business. [S11]
- DQC_0013 "Negative values with dependence" and DQC_0014 "Negative values, no dimensions", both effective Jan 1, 2017 (names as in [S8]'s table; a separate search-result summary swapped the names, see section 7).
- DQC_0080 Negative values (IFRS only). DQC_0174 Conditional non-negatives (Dec 1, 2023). DQC_0125 Lease cost cannot be negative (May 1, 2022). DQC_0194 Negative values for equity components axis members (Apr 14, 2025). DQC_0147 Incorrect sign of elimination items (Apr 1, 2023). DQC_0008 Reversed calculation (an extension reverses a base-taxonomy calc relationship; page). [S8]

**Scale errors**
- DQC_0095 Scale, common stock outstanding, effective Sep 1, 2020 (page): compares `dei:EntityCommonStockSharesOutstanding` with `us-gaap:CommonStockSharesOutstanding`; error if one is "more than 100 times larger" than the other (strictly greater). Example 9,076,832 vs 9,076 (about 1000x). [S12]
- DQC_0192 Balance sheet numerical scaling, effective Nov 30, 2024 (page): large accelerated and accelerated filers only; error if no monetary balance sheet value exceeds 1,000,000 USD (example: largest value 123,000 with inline scale 3). Purpose: "an incorrect scale for the entire filing". [S13]
- DQC_0222 Scaling error in `dei:EntityPublicFloat`, effective Dec 15, 2025 (page): standard filer error if float > $10 trillion or < $1 million (plus a $2.5 billion bound when revenue suggests a smaller filer); small business (`dei:EntitySmallBusiness` true) error if > $250 million or < $1,000; exception for small filers with revenue < $100 million and float between $250M and $700M. [S14]
- DQC_0139 Bank ratios, scale issues (Dec 1, 2022); DQC_0157 Bank measures under one percent (Sep 1, 2023); DQC_0091 Invalid value for percentage items (Sep 1, 2020); DQC_0198 Income tax reconciliation percentages (Apr 14, 2025). [S8]

**Balance / calculation errors**
- DQC_0004 Assets equal liabilities plus equity, effective Jan 1, 2016, v9 July 2019 (page). Checks accounting constants (Assets = LiabilitiesAndStockholdersEquity; rules 9280-9291 cover subtotals, comprehensive income, cash-flow totals). Runs across every dimension. Compared "at the lowest decimal precision of the facts". Tolerance listed as 2 on the page but not explained. A missing non-required component is treated as zero. [S15]
- DQC_0009 Element A <= Element B (page): shares outstanding <= issued <= authorized (common and preferred), pension subset <= total, ABO <= PBO. [S16]
- DQC_0043-0049, 0057, 0061, 0062 cash flow structure; DQC_0126 FS calc check with non-dimensional data; DQC_0117/0118 FS tables dimensional cross check and calc check; DQC_0167 inconsistent calculation roots; DQC_0187 PP&E calculation; DQC_0213/0214 missing calc children / equity in balance sheet calc; DQC_0227 Calculated ratio consistency (Jun 1, 2026). [S8]
- DQC_0228 "Other" concept should not exceed aggregate; DQC_0230/0231 "Other" concepts in calculation networks (Jun 1, 2026). [S8]

**Duplicate / consistency across time and dimensions**
- DQC_0108 Fact value consistency over time, effective Sep 1, 2021 (page): for monetary duration concepts "expected to get larger over a reporting period" a shorter-period value must not exceed a longer-period value for the same concept; excludes names containing "average", "maximum", "minimum" and two capex-accrual concepts; no numeric tolerance beyond decimals. Example: goodwill impairment for a segment, 92-day value 2.1B vs 366-day value 1.319B. [S17]
- DQC_0011 Dimensional equivalents (to be superseded by 0182); DQC_0128 Dimensional values larger than default (May 1, 2022); DQC_0161/0189 single member disaggregation; DQC_0137 location axis with single member. [S8]
- EFM duplicate-fact rule (section 1.5) is the structural duplicate check inside one filing.

**Wrong period / context dates**
- DQC_0005 Context dates after period end (page): the date of `dei:EntityCommonStockSharesOutstanding` must be on or after the period end; subsequent-event-axis facts and forecast-scenario facts must have dates after the period end. Not run on S-1/S-3/S-4/etc. [S18]
- DQC_0033 Document period end date context; DQC_0036 Period end context / fact value check; DQC_0006 DEI and block tag date contexts. [S8]
- DQC_0146 Incorrect period reported (page), effective Mar 31, 2023: for a 10-K or 20-F, flags a filing where the majority of income statement values are for a period other than a year; excludes transition reports, year of inception, successor/predecessor. [S19]

**Dimension / member misuse**
- DQC_0001 Axes with inappropriate members; 0051-0055 member/axis rules; 0127 incorrect dimensional item on FS; 0216 improper use of extension geography members; 0250 members used across incompatible dimension classes. [S8]

**Presence / structure rules relevant to financial statements**
- DQC_0099 FS with no associated calculation; DQC_0159 FS abstract concepts; DQC_0144 No balance attribute in FS; DQC_0145 Inappropriate cash flow presentation; DQC_0192 Balance sheet numeric scaling; DQC_0212 Missing shares issued/authorized when shares outstanding reported (Dec 15, 2025); DQC_0221 Missing NumberOfReportableSegments. [S8]

### 2.3 Typical errors the rules exist to catch (as stated by the rule pages)
1. Parenthesized values entered as negatives (DQC_0015 basis text).
2. Whole filing tagged at the wrong scale (DQC_0192, DQC_0222, DQC_0095 examples above).
3. Cover-page shares tagged in thousands while the balance sheet is in units (DQC_0095).
4. Annual-labelled values that are not annual durations (DQC_0146).
5. Quarter-to-date value larger than year-to-date for a monotonic concept (DQC_0108).
6. Extension reversing a base-taxonomy calc relationship so totals "compute" (DQC_0008).
7. Subsequent-event or forecast axis used with a date at or before the period end (DQC_0005).

---

## 3. US-GAAP taxonomy: yearly change, deprecation, accounting-standard effective dates

### 3.1 Annual release mechanics
- FASB releases an annual taxonomy; SEC staff accept it in EDGAR on a published schedule. Example: EDGAR Release 26.1 went live March 16, 2026 and accepts the 2026 versions of US-GAAP, US-GAAP-EBP and SRT. The 2026 US GAAP taxonomy is the version FASB made available December 15, 2025. EDGAR accepts either 2026 or 2025; "Each 2026 taxonomy is compatible only with other 2026 taxonomies." (search-result summary of SEC what's-new pages [S20]; the staff announcement itself was not opened). A July 8, 2026 staff notice says "only annual compilations of the US GAAP Financial Reporting Taxonomy specified on the Commission's website may be used" (same source, not opened).
- 2026 release notes [S9] (downloaded and text-extracted, read 2026-10-18):
  - "For elements that existed in the 2025 FASB GAAP Taxonomies, the element names are unchanged, so they do not adversely affect year-to-year comparability."
  - Deprecation rule: "Deprecated elements remain in two annual updates to satisfy legacy and conversion requirements but should not be used in filings. After remaining in two annual updates, they are removed and are no longer available for use."
  - 2026 deprecations: GRT 564 (ASU/SEC 337; topical and reference projects 130; public comments and internal analyses 97), SRT 38, EBPT 1. Replacement relationships: no relationship 518; one-to-one dep-concept 66; aggregate 0.
  - Deprecation reasons: "superseded guidance of amendments in previously issued ASUs and the removal of redundant elements, low-use elements, and elements no longer needed after modeling improvements." Not all deprecated elements have a replacement.
  - Section 4.10: "As a result of the EDGAR Release 25.2, the 2023 GRT is no longer supported and 2023 deprecated elements no longer appear in the 2026 GRT." 266 elements deprecated in 2023 were removed.
  - Replacement can change the period type (instant to duration is the stated example of a one-to-one replacement).
- FASB taxonomy FAQ (via search summary, page not opened): once deprecated an element is not restored; FASB creates a new element instead. [S21]
- Implication for us: a filing from year Y uses year-Y (or Y-1) taxonomy. A tag present in a 2019 filing may not exist in the current taxonomy yet is still a valid historical tag in companyfacts. Mappings must be keyed by tag name with no assumption that the tag is in the current taxonomy.

### 3.2 Revenue (ASC 606, ASU 2014-09 / 2015-14)
- ASU 2014-09 set the PBE effective date at annual periods beginning after December 15, 2016; ASU 2015-14 deferred it one year for all entities. Public business entities: annual periods beginning after **December 15, 2017**, including interim periods in those years. Other entities: annual periods beginning after December 15, 2018 and interim periods after December 15, 2019. [S22] (search summary of FASB-hosted PDFs; the PDFs were not text-extracted. See section 7 for the second-hand status of the "other entities" interim date.)
- Fiscal-year effect: a Sep-FYE PBE adopted October 1, 2018 (one filer's note quoted in the search result). Calendar-year PBE adopted January 1, 2018.
- Modified-retrospective adoption means FY2018 revenue may be on a different basis than FY2017 comparatives in the same filing. Elements such as the ASC 606 transition difference members are allowed negative in DQC_0015's exclusions [S11].
- The specific tag `RevenueFromContractWithCustomerExcludingAssessedTax` is named in doc 21; its taxonomy introduction year was not checked. See section 7.

### 3.3 Leases (ASC 842, ASU 2016-02)
- Verified in the ASU text (downloaded, extracted): effective for fiscal years beginning after **December 15, 2018**, including interim periods, for (1) a public business entity, (2) a NFP with exchange-traded securities, (3) an employee benefit plan filing with the SEC. All other entities: fiscal years beginning after December 15, 2019 and interim after December 15, 2020 (as originally issued). Early application permitted for all entities. [S23]
- FASB's leases summary page states that for all other organizations the date is fiscal years beginning after December 15, 2021 (ASU 2020-05 deferral). [S24] (search-result excerpt; ASU 2020-05 text not read).
- DQC lease rules: 0087 operating lease liabilities across FS line items, 0088 operating lease cost and expense (Dec 1, 2023), 0090 lease liability payments due, 0124 lease liabilities and assets breakdown, 0125 lease cost cannot be negative, 0131 lease allocation in balance sheet, 0132 operating lease amortization. [S8]

### 3.4 Credit losses (CECL, ASC 326, ASU 2016-13 / 2019-10)
Verified in ASU 2019-10 (downloaded, extracted). [S25]
- ASU 2016-13 original schedule: SEC filers: fiscal years beginning after December 15, 2019; other PBEs after December 15, 2020; all other entities after December 15, 2021.
- ASU 2019-10 revised schedule: "Public business entities that meet the definition of an SEC filer, excluding entities eligible to be smaller reporting companies as defined by the SEC" fiscal years beginning after **December 15, 2019**; **all other entities** (including SRC SEC filers) after **December 15, 2022**. Early application permitted for fiscal years beginning after December 15, 2018.
- The SRC eligibility test for this purpose: "a one-time determination... based on an entity's most recent determination as of November 15, 2019, in accordance with SEC regulations."
- Practical read: calendar-year large and accelerated non-SRC banks adopted for FY2020; SRC-eligible banks and most small filers for FY2023. Between those years the same company may switch from incurred-loss concepts to CECL concepts. Doc 21's "2020+ for large filers" is right for non-SRC SEC filers only.
- DQC_0171 (ASU 2016-13 transition elements, effective Dec 31, 2024) and the 2026 taxonomy's ASU 2025-08 content name "Credit Losses-Purchased Loans" confirm continued evolution. [S8][S9]

### 3.5 Newer standards that will add line items soon
- ASU 2024-03 (income statement expense disaggregation, Subtopic 220-40): public business entities, annual periods beginning after **December 15, 2026**, interim periods within annual periods beginning after **December 15, 2027**. ASU 2025-01 clarified that non-calendar-year entities also first apply it in an annual period. [S26] (search-result summary of FASB documents; the ASU PDFs were not text-extracted). The 2026 taxonomy lists both ASUs (the 2025 release notes introduced the elements). [S9]
- DQC_0150/0163 segment reporting rules (Sep 1 and Dec 1, 2023) and DQC_0221 (missing `NumberOfReportableSegments`, Dec 15, 2025) relate to the segment disclosure expansion. [S8]
- Effect for us: new cost-line elements will begin to appear in notes (not in face statements) for FY2027 10-Ks. Do not treat a new tag as a mapping gap until the company's effective period is known.

---

## 4. SEC Financial Statement Data Sets and Financial Statement and Notes Data Sets

### 4.1 Financial Statement Data Sets (FSDS)
Sources: web page [S27] and the "Financial Statements Data" PDF (downloaded, text-extracted) [S4], both read 2026-10-18.

Scope:
- Numeric data from the **primary financial statements as rendered by the Commission** (Balance Sheet, Income Statement, Cash Flows, Changes in Equity, Comprehensive Income) and page footnotes on those statements. From XBRL submissions that have rendered financial statements (10-K, 10-Q, 20-F, 40-F). Submitted from 4/15/2009 through the cutoff date; quarterly ZIPs 2009 Q1 (empty) through 2026 Q3.
- Quarterly posting: documents filed after the quarter's last business day appear in the next posting. "All numeric data is 'as filed'." It "may contain redundancies, inconsistencies, and discrepancies relative to other publication formats" and "uncorrected" amendments are included. The December 2024 reprocessing added a "segments" field to NUM (per the web page; the PDF lists `segments` as part of the NUM key, so the field has a documented definition).
- Not included: disclosures outside the face statements (that is the Notes data set); some filing metadata. The disclaimer says the SEC "cannot guarantee the accuracy"; "not a substitute" for the filings.
- Tab-delimited UTF-8, first line lowercase column names.

Four tables:
- **SUB** (one row per submission; key `adsh`). Fields: adsh, cik, name, sic, countryba, stprba, cityba, zipba, bas1, bas2, baph, countryma, stprma, cityma, zipma, mas1, mas2, countryinc, stprinc, ein, former, changed, afs, wksi, fye, form, period, fy, fp, filed, accepted, prevrpt, detail, instance, nciks, aciks.
  - `afs` = filer status at submission: 1-LAF, 2-ACC, 3-SRA (smaller reporting accelerated), 4-NON, 5-SML (smaller reporting filer), NULL.
  - `fye` = fiscal year end "rounded to nearest month-end" (mmdd). `period` = balance sheet date "rounded to nearest month-end". `fy`/`fp` = the EDGAR XBRL Guide 3.1.8 focus values (FY, Q1-Q3, never Q4).
  - `prevrpt` = TRUE if the submission "was subsequently amended". `detail` = TRUE if the XBRL contains quantitative disclosures within footnotes and schedules at the required detail level.
  - EDGAR-sourced fields (sic, name, countries, etc.) "represent the most recent EDGAR assignment as of a given filing's submission date and do not necessarily represent the most current assignments." So `sic` and `name` in SUB are as of filing, not current.
- **TAG**: key (tag, version). `version` = taxonomy identifier for standard tags, **accession number for custom tags**. Fields: custom (1 if tag is custom), abstract, datatype, iord (I instant / D duration), crdr (natural balance C/D), tlabel, doc.
- **NUM**: key (adsh, tag, version, ddate, qtrs, uom, segments, coreg). Fields: ddate (end date "rounded to the nearest month end"), qtrs ("count of the number of quarters represented... rounded to the nearest whole number. '0' indicates it is a point-in-time value"), uom, segments (axis/member text, up to 1024 chars), coreg (NULL = consolidated entity), value (NUMERIC(28,4), "not scaled, it is as found in the Interactive Data file, but is limited to four digits to the right of the decimal point"), footnote (truncated to 512 characters).
- **PRE**: key (adsh, report, line). Fields: stmt (BS, IS, CF, EQ, CI, SI, UN), inpth (value presented parenthetically), rfile (H or X), tag, version, plabel, negating (whether plabel is negating). The same tag can appear on several lines/statements, so more than one PRE row per NUM row.

Facts that matter for our data:
- `qtrs` rounds durations (so a 14-week quarter and a 13-week quarter both give qtrs=1; a 52- and 53-week year both give qtrs=4); `ddate` and `fye` round to month end (a Saturday-nearest-month-end FYE is shown as a month end). FSDS is therefore NOT a source for exact period dates; it is for ranking and cross-check only. Use companyfacts `start`/`end` or the filing instance for exact dates.
- Face statements only: a company whose XBRL does not render a face statement properly (see 1.4) can be absent.
- Dimensional rows are present in NUM through `segments` when presented on the face (e.g. equity-component rows); an unconditional filter `segments IS NULL` is needed to get consolidated totals. `coreg IS NULL` is needed to exclude co-registrants/guarantors.
- Value precision is limited to 4 decimals (per-share values are fine; rates in decimals like 0.0123 are fine).

### 4.2 Financial Statement and Notes Data Sets
[S28] (read 2026-10-18; the PDF named in the page was not extracted)
- Contains text and detailed numeric information from financial statements **and notes**, Jan 2009 through Sep 2026; "significantly more disclosure data" than FSDS (which is "more compact and include only numeric data from the face financials").
- Updated monthly (before November 2020 quarterly). Filings after 5:30 PM ET on the last day of a month appear in the next posting. From March 2024, monthly files are consolidated into quarterly files after a year.
- Same disclaimers as FSDS. The table layout was not read from the PDF; do not assume it matches FSDS.

### 4.3 Comparison to companyfacts
| Aspect | companyfacts / frames | FSDS |
|---|---|---|
| Statements covered | all non-custom facts for the whole entity (face and notes) | face statements only, as rendered |
| Dimensions | excluded | `segments` text on face rows |
| Custom tags | excluded | included (version = accession) |
| Period precision | exact start/end | month-rounded ddate; qtrs rounded |
| Latency | under a minute (API), nightly zip | quarterly |
| Duplicates | same fact repeats per filing (observed) | one row per filing |

---

## 5. Restatements, non-reliance, 10-K/A, 10-KT, 52/53-week years, S-K/S-X line-item rules

### 5.1 Item 4.02 (Form 8-K) non-reliance
Sources: Form 8-K PDF [S29], Financial Reporting Manual (FRM, revisions to June 29, 2026) [S30], Form 8-K C&DIs [S31]; read 2026-10-18.
- Trigger (Item 4.02(a)): the board, a board committee, or the authorized officer(s) conclude that previously issued financial statements "should no longer be relied upon because of an error in such financial statements as addressed in FASB ASC Topic 250." Required content: date of conclusion and identification of statements/periods; brief description of the facts; whether the audit committee discussed it with the independent accountant. [S29]
- Deadline: general four business days after the triggering event (General Instruction B.1). [S29, S31] (search summary of the 2004 release plus the Form 8-K text; the Instruction B.1 sentence is at the form's start).
- Item 4.02(b): the auditor advises that action is needed to prevent future reliance on an audit report or completed interim review. No second 8-K is needed if 4.02(a) was already filed unless the auditor's conclusion concerns a different error. [S29, S31 Q115.01; FRM 4610.3]
- Not sufficient to report only in a periodic report: C&DI 215.01 states "It is not sufficient to report the event in a periodic report." [S31]
- Not triggered by errors in pro forma information (Q115.02; FRM 4640.1). [S31, S30]
- Not triggered by an error only in the Interactive Data File when the financial statements remain reliable: "There is no requirement to provide disclosure under Item 4.02(a) of Form 8-K when a material error is discovered in the Interactive Data File while the financial statements upon which they are based do not contain an error and may continue to be relied on." A filer may voluntarily disclose under Item 7.01 or 8.01. A material error in the data file still needs an amendment. [S30 FRM 4640.2; S31 Q115.03]
- After a restatement: management may need to reevaluate ICFR and DCP conclusions and revise disclosures; example in FRM 4310.17: a 10-K/A restating the statements and changing the disclosure-controls conclusion to "not effective". [S30]
- Item 4.02 filings are 8-K (and 8-K/A) only. The restated financial statements themselves come in a 10-K/A, a later periodic report, or both; the 8-K does not carry restated numbers by itself.

### 5.2 Error flag inside the 10-K XBRL
- `dei:DocumentFinStmtErrorCorrectionFlag` and `dei:DocumentFinStmtRestatementRecoveryAnalysisFlag` are expected on annual reports (warning-level checks). [S2 3.1.23.2] The flag does not distinguish a restatement from an immaterial revision; read the filing.

### 5.3 10-K/A and amendments in the API
- Observed (section 1.6): companyfacts includes 10-K/A rows and 8-K rows. The 10-K/A in the sample restated three fiscal years under one accession.
- `dei:AmendmentFlag` true with a description marks an amended XBRL; an "/A" form may contain no XBRL at all (Guide 3.1.6).
- SEC 10-K/A form-level rules (Part III only, restated financials, etc.) were not read; see section 7.

### 5.4 10-KT, transition periods, fiscal-year changes
- Exchange Act Rule 13a-10 (eCFR, summarized by the fetch tool, read 2026-10-18) [S32]:
  - A transition report is required when the fiscal closing date changes, covering the period between the last fiscal year end and the start of the new fiscal year; it "cannot cover 12 or more months."
  - Use the annual-report form (10-K, labeled 10-KT in EDGAR) with audited transition-period statements. If the transition period is under six months, a 10-Q may be used (unaudited), with separate audited income and cash flow statements for the period filed with the first annual report of the new fiscal year. One month or less: no separate report is needed if the first annual report covers it (conditions apply).
  - Due dates for annual-form transition reports measured from the later of period end or the decision date: 60 days (large accelerated), 75 days (accelerated), 90 days (others). For 10-Q-form reports: 40 days (large accelerated and accelerated), 45 days (others). An Item 5.03 8-K is also required.
- Regulation S-X Rule 3-06 (eCFR) [S33]: for a single-year requirement, a 9-to-12-month period satisfies a one-year requirement when the issuer changed its fiscal year (or for certain acquisitions or by SEC permission). For multi-year requirements the 9-12 month period counts as one year only in those cases and full fiscal years are needed for the rest.
- FRM 1365.x [S30]: transition reports must include prior-year information comparable to the transition period; no audited reporting period "under any circumstances" may exceed 12 months for domestic issuers (1365.3); examples: March-FYE to December: a 9-month transition period satisfies one year, so the 10-KT shows the 9-month period plus the two prior fiscal years (three years total); June-FYE to December: a 6-month period does not satisfy a year, so three full fiscal years are required in addition. Balance sheets: end of each of the two most recent fiscal years plus the transition date.
- XBRL treatment: transition reports use `dei:DocumentFiscalPeriodFocus = FY` and `dei:DocumentTransitionReport = true` (Guide 3.1.8/3.1.23.1). DQC_0146 exempts them from the "annual period" test. [S2, S19]
- Companies may recast prior-period financials to the new year-end but need not (FRM 1365.6). [S30]

### 5.5 52/53-week fiscal years
- FRM 1365.7 (last updated 9/30/2010): "A change from a fiscal year ending as of the last day of the month to a 52-53 week fiscal year commencing within seven days of the month end (or vice-versa) is not deemed a change in fiscal year-end if the new fiscal year commences with the end of the old fiscal year. A transition report would not be required." [S30]
- Rule 12b-2 definition of "fiscal year": the annual accounting period; if none adopted, the calendar year ending December 31. [S34]
- Companies describe the convention in their own 10-K (examples from search results, not SEC rules): Apple "52- or 53-week period that ends on the last Saturday of September"; Gap and Burlington: Saturday closest to January 31. [S35]
- SEC API frame rules assign annual frames with a 365 +/-30 day window and quarterly frames 91 +/-30, which tolerate 371-day years and 98-day quarters. [S6]
- FSDS rounds period end and `fye` to month end and `qtrs` to whole quarters. [S4]
- I did not find any SEC rule text defining 52/53-week presentation (beyond the FRM and Rule 12b-2). The convention is the filer's own and is disclosed in its first accounting-policies note.

### 5.6 Regulation S-X / S-K: which periods and items a filer presents
- **Periods (S-X 3-02):** audited statements of comprehensive income and cash flows for **three** fiscal years (a shorter life if existing less). An emerging growth company may present two fiscal years in an IPO registration statement. [S36, eCFR 210.3-02]
- **Smaller reporting companies (S-X Article 8, 8-02):** audited balance sheets for each of the **two** most recent fiscal years; audited statements of comprehensive income, cash flows and changes in stockholders' equity for **two** fiscal years. [S37, eCFR 210.8-02] FRM 1365.2 repeats "two most recent fiscal years for Smaller Reporting Companies" for transition reports. [S30]
- **SRC definition (Rule 12b-2 and S-K Item 10(f)):** not an investment company, ABS issuer or majority-owned subsidiary of a non-SRC; public float < $250 million, **or** annual revenues < $100 million and public float either zero or < $700 million. Public float measured on the last business day of the second fiscal quarter; revenue from the most recent audited fiscal year. Re-qualification after losing status: public float < $200 million, or the chart combinations (for example $560 million float with revenue < $100 million). After a de-SPAC the status is re-determined from the target's revenue, effective 45 days after consummation. [S34, S38]
- **Accelerated filer:** float >= $75 million and < $700 million, at least 12 months of reporting, at least one annual report, and not eligible for the SRC revenue test. Exit below $60 million float or if SRC revenue test eligible. **Large accelerated filer:** float >= $700 million; exit below $560 million. [S34]
- **Emerging growth company:** total annual gross revenues below **$1,235,000,000** in the most recent fiscal year; ends at the earliest of the first fiscal year with revenues of that amount or more, the fiscal year after the fifth anniversary of the first registered common-equity sale, more than $1 billion non-convertible debt issued in three years, or becoming a large accelerated filer. [S34]
- **S-K Item 10(f):** an SRC "may comply with either the requirements applicable to smaller reporting companies" for each item unless the SRC requirements are mandatory. Items with SRC-specific requirements: 101, 201, 302, 305, 402, 404, 407, 503, 504, 601. [S38] (the fetch summary does not say which disclosures are omitted; do not infer more).
- **Practical consequence:** For an SRC, the 10-K carries only two years of income statement, cash flow and equity. The third prior year does not exist in that filing. It can still exist in an earlier 10-K from when the company was not an SRC. A missing third year is not a data gap by itself.

---

## 6. Findings that change what agents do

### 6.1 Corrections to data-team/21 (Section-by-section)
Format: item in doc 21 -> verdict -> evidence.

C1. Section 1, "XBRL phase-in: large filers from 2009, others 2010-2011; iXBRL 2019-2021; reliable full coverage starts around 2011 [VERIFY exact cohort dates]". **Imprecise; now exact.** Three cohorts, fiscal periods ending on/after June 15, 2009 (US GAAP large accelerated with float > $5B), June 15, 2010 (other large accelerated), June 15, 2011 (all remaining including SRCs and IFRS FPIs). The first XBRL document is a 10-Q for that period, and detail-tagged notes start a year later. The "2011" statement is right for annual data of small companies: their first annual XBRL is the FY2011 10-K (filed 2012) with FY2010 comparatives. [S3]

C2. Section 1, iXBRL "2019-2021". **Confirmed and made exact:** periods ending on/after June 15, 2019 (large accelerated, US GAAP), 2020 (accelerated), 2021 (all others); first iXBRL is the 10-Q, the 10-K follows only after the first iXBRL 10-Q. [S5]

C3. Section 1, "There is no Q4 10-Q. Q4 flow figures are not filed as such". **Confirmed.** `DocumentFiscalPeriodFocus` allows only `Q1|Q2|Q3|FY`; FY is used for 10-K and 10-KT. [S2 3.1.8]

C4. Section 1, filer categories change deadlines and disclosure. **Confirmed; thresholds added** (accelerated $75M-<$700M, large accelerated >= $700M, SRC revenue test removes accelerated status; EGC revenue < $1.235B; SRC float < $250M or revenue < $100M and float < $700M). Doc 21 should list them. [S34]

C5. Section 1, SRC "two years of income statements instead of three". **Confirmed with the rule:** S-X 8-02 requires two years of income, cash flow and equity statements and two balance sheets for SRCs (3-02 requires three for others). [S37, S36]

C6. Section 1, "10-KT (transition period, different length)". **Confirmed and made exact:** Rule 13a-10, cannot be 12+ months; a 9-12 month transition period satisfies one year under S-X 3-06; XBRL uses FY and `DocumentTransitionReport=true`. [S32, S33, S2]

C7. Section 1, "8-K Item 4.02 = a restatement warning". **Confirmed with limits:** (a) the trigger is a non-reliance conclusion by the board/committee/authorized officer, 4 business days; (b) it does not apply to errors only in the XBRL data file or to pro forma information; (c) it is not satisfied by disclosure in a periodic report. An error in XBRL alone therefore has no Item 4.02 signal. [S29, S30, S31]

C8. Section 2, "dei:DocumentFiscalYearFocus is not the calendar year and is sometimes wrong. Trust actual period dates". **Confirmed and extended:** also true of `fy`/`fp` in companyfacts, which describe the filing, not the fact (same fact appears under fy 2022, 2023 and 2024; null `fy`/`fp` on 8-K rows; `fp=FY` on single-quarter rows from 8-K accession 0001193125-13-170623). [S7 observed]

C9. Section 2, 52/53-week "a 365-day duration test will wrongly reject them; quarters about 91 days (13 weeks), 14 in a 53-week year". **Confirmed for the 365-day point; the SEC's own frame window is 365 +/-30 and 91 +/-30.** The "14 weeks in a 53-week year" is the typical practice but was not verified in a rule (the placement of the extra week is a company choice). Add: FSDS rounds `qtrs` and `ddate`. [S6, S4]

C10. Section 2, "10-Q cash-flow statements are cumulative year-to-date". **Confirmed structurally:** FSDS `qtrs` carries 2 and 3 for six and nine months (rounded count of quarters). [S4] (Whether a particular company tags discrete or cumulative is still a per-filing matter.)

C11. Section 3, "No-dimension facts are the consolidated total". **Imprecise.** (a) For `dei:EntityCommonStockSharesOutstanding` of multi-class issuers the Guide permits ONLY dimensioned facts (cases 2 and 3), so no undimensioned fact exists. (b) FSDS `coreg` is NULL for the consolidated entity but co-registrant rows exist. (c) Consolidating instances use `ConsolidatedEntitiesAxis`. Rule: undimensioned = whole-entity default context; absence of an undimensioned fact is not an error. [S2 3.2.3, 6.2.x; S4]

C12. Section 3, "Duplicates are normal... latest-filed figure for a period is the current one unless policy says otherwise". **Imprecise.** The SEC's frames API itself uses "the last one filed that most closely fits the requested period", but (a) the last filing can be an 8-K recast or an amendment that carries different perimeter, and (b) `frame` is stamped on one row only. Policy needs a form filter. [S6, S7]

C13. Section 3, "Decimals/precision: ... equal within rounding is not a conflict". **Confirmed and formalized** by the EFM interval rule (closed interval 10^decimals around each value, overlap = consistent, keep the max-decimals value). Inconsistent duplicates inside one instance are an XBRL error. [S2 9.10]

C14. Section 3, "Scale and sign: ... Sign follows the tag's balance type and the `negated` label flag; check it, do not assume." **Wrong as stated.** The stored value carries the economic sign of the concept; the filer is told to invert a value (put a negative in the instance) when the element's balance attribute disagrees with the concept being reported (EFM 6.5.4). Negating labels are display-only (6.5.5). The balance type does not determine the sign. FSDS exposes `crdr` (TAG) and `negating` (PRE) for display research, not for sign correction. DQC_0015 treats a negative on its list as a probable error. Replace with: "Value sign = economic sign as filed; balance type and negated labels explain presentation only; a negative on a DQC_0015-listed element is a tagging error candidate, not a reason to flip." [S2, S11, S4]

C15. Section 3, "Units: ... A tag filed in a foreign currency or wrong unit is a data error". **Imprecise.** companyconcept returns one array per unit and names "USD and CAD" as normal. A non-USD unit is legal XBRL; it is a data problem only when it is applied to a concept we treat as USD. Scale errors on dei facts have a published rule (DQC_0222 with thresholds). The eBay float example matches the rule's class of error. [S6, S14]

C16. Section 3, "Tag taxonomy drift... new tags enter yearly; old ones deprecated [VERIFY per release]". **Verified.** Element names do not change between years; deprecated elements stay two annual updates and are then removed; a deprecated tag is never revived; EDGAR drops support for old taxonomies (2023 GRT removed with EDGAR 25.2; 266 elements removed). Historical filings keep using the old names. [S9]

C17. Section 3, "Custom (extension) tags... About 9% of face lines use them". **Add the API consequence:** custom facts are excluded from companyfacts/frames entirely, so any custom face line is invisible there; they exist only in the filing instance and in FSDS (TAG `custom=1`, version = accession). The 9% figure is not in any SEC source read here; treat as our own measurement. [S6, S4]

C18. Section 3, "The SEC companyfacts/frames APIs strip dimensional data". **Confirmed in effect, imprecise in wording:** the SEC states the APIs include non-custom-taxonomy facts "that apply to the entire filing entity"; the word "dimension" is not on the page. Also covered taxonomies: us-gaap, ifrs-full, dei, srt. [S6]

C19. Section 4, "ASC 606 revenue recognition (effective 2018 public)". **Right for calendar-year PBEs; imprecise otherwise.** PBEs: annual periods beginning after December 15, 2017 (a Sep-FYE company adopted October 1, 2018); other entities one year later. [S22]

C20. Section 4, "ASC 842 leases (2019)". **Right for calendar-year PBEs:** fiscal years beginning after December 15, 2018; other entities originally 2019/2020 interim 2020/2021, later deferred (FASB summary page states fiscal years beginning after December 15, 2021). [S23, S24]

C21. Section 4, "CECL credit-loss accounting (2020+ for large filers) [VERIFY dates per filer category]". **Verified and refined:** SEC filers that are not SRC-eligible (SRC test frozen at November 15, 2019): fiscal years beginning after December 15, 2019. All others including SRCs: after December 15, 2022. [S25]

C22. Section 4, "Restatements (10-K/A, 8-K Item 4.02) change prior-period values; 'as originally reported' and 'as restated' are both real". **Confirmed in effect but incomplete:** companyfacts holds both versions as separate accession rows; there is no restated flag in the API; restatement can also appear in a later 10-K's comparatives with no 10-K/A and no 4.02 (immaterial revisions); the 10-K's `DocumentFinStmtErrorCorrectionFlag` is the only structured signal. [S7, S2]

C23. Section 6, "Financial Statement Data Sets... same values, useful for ranking and cross-checks, not independent proof". **Confirmed** (derived from the same XBRL, "as filed", disclaimed). Add its limits: face statements only, month-rounded dates, 4-decimal values, SUB identity fields as of filing date. [S4, S27]

C24. Section 6, "'Not in the XBRL' is not 'not in the filing'". **Confirmed with a mechanical cause:** an XBRL Error strips the whole instance from the accepted submission while the HTML filing stays (Guide 1.6). A material XBRL error without a financial-statement error does not even trigger Item 4.02 (FRM 4640.2). [S2, S30]

C25. Section 3, "Share classes: one issuer can have several securities... per-share data may be per-class". **Confirmed** by the dei rule: multi-class issuers report shares outstanding only under StatementClassOfStockAxis / ClassesOfShareCapitalAxis. Two addenda: cover-page shares are an instant on/after the period end (DQC_0005) and often differ from balance-sheet shares; the 100x scale cross-check (DQC_0095) compares them. [S2, S12, S18]

C26. Section 1, "Foreign private issuers 20-F/40-F/6-K. Outside V1". **Confirmed**; note that companyfacts/frames include 20-F, 40-F, 6-K and ifrs-full facts in the same endpoints, so a form filter is needed. [S6]

Tally: 26 items checked. 1 wrong as stated (C14). 11 imprecise and should be reworded in doc 21 (C1, C4, C8, C11, C12, C15, C17, C18, C19, C20, C21). 14 confirmed as written or only made exact (C2, C3, C5, C6, C7, C9, C10, C13, C16, C22, C23, C24, C25, C26).

### 6.2 New rules our agents should follow
1. Never use `fy`/`fp` from companyfacts to place a fact in a period. Use `start`/`end` and the fact's own duration. `fy`/`fp` can be null, can be `FY` on a quarter row, and describe the filing. [S7]
2. Always filter companyfacts rows by `form` before choosing "latest filed": decide explicitly whether 10-K/A and 8-K rows are allowed. 8-K and 10-K/A rows exist and can be recasts or three-year bundles. [S7]
3. Treat the `frame` field as a label on one duplicate, not as the definition of the fact's period; frames are calendar-aligned (annual 365 +/-30 days, quarter 91 +/-30 days). [S6, S7]
4. Value sign is the economic sign as filed. Do not flip a sign using a label or the balance type. A negative on a DQC_0015-listed element (payables, lease cost, valuation allowance, extinguishment of debt, etc.) is a tagging-error candidate: quarantine, do not correct. [S2, S11]
5. Within a single filing, two numeric facts with the same concept/context/unit must be consistent with one rounded value; if their decimals-intervals do not overlap it is a filer error (the filing would have drawn an XBRL Error). Prefer the one with the larger `decimals`. [S2 9.10]
6. Run cheap scale tests on every number set: `dei:EntityPublicFloat` outside $1 million - $10 trillion (SRC outside $1,000 - $250 million, with the revenue exception in DQC_0222); cover-page shares vs balance-sheet shares ratio > 100x (DQC_0095); a balance sheet whose largest monetary value is under $1 million for a large/accelerated filer (DQC_0192). [S12, S13, S14]
7. Before saying "the filer did not report X", check whether the XBRL was stripped: an XBRL Error removes the instance but not the filing. Missing XBRL for a whole filing is a collection fact, not an accounting fact. [S2 1.6]
8. Do not require an undimensioned `EntityCommonStockSharesOutstanding`: multi-class issuers have only dimensioned facts. Sum or keep per-class; never pick one class as the issuer's total. [S2 3.2.3]
9. Keep every tag that was ever valid: deprecated elements remain two annual updates, then are removed from the current taxonomy, but historical filings still carry them. Mapping tables keyed by name must not drop a tag because it is missing from the latest taxonomy. [S9]
10. Never interpret custom (extension) face lines through companyfacts: those facts are not there. A custom face line must be read from the filing instance (or FSDS TAG with `custom=1`, version = accession). Identify a custom tag by (name, accession), not by name. [S6, S4]
11. Treat SRC status as a time-varying attribute: determine per filing from `dei:EntitySmallBusiness` / filer category as of that filing; an SRC 10-K has two years of income statement and cash flow, so a missing third year is expected. [S37, S2]
12. For CECL, ASC 842 and ASC 606, compute the adoption year per company from its fiscal-year start and SRC status, not from a single calendar year. A step change in a bank's credit-loss lines in a given year is first an accounting-standard break. [S22, S23, S25]
13. For 10-KT filings, expect a non-12-month duration labelled `FY` in `DocumentFiscalPeriodFocus`; do not use it as a full year, and do not compute YoY across it. [S2, S32]
14. A restatement signal has four independent sources: Item 4.02 8-K, a 10-K/A, `DocumentFinStmtErrorCorrectionFlag` on a later 10-K, and a value difference between two accession rows for the same period. Record which source supports a restated basis; none alone proves it. An XBRL-only error never produces an Item 4.02. [S29, S30, S2, S7]
15. FSDS is for ranking and cross-checking only: dates are rounded to month end, `qtrs` is rounded, `sic`/`name` are as of filing date, only face statements are included, dimension rows require `segments` handling. [S4]
16. Duration sanity: for monotonic duration concepts (revenue, impairment, interest expense, etc.) a shorter-period value larger than the longer-period value in the same filing is a DQC_0108-class error; check before using either. [S17]
17. 52/53-week handling: accept 364-371 day annual durations and 91-98 day quarters; do not use a 365-day test; use the company's disclosed convention only for labelling. [S6, S30]
18. A "Q4" must be derived (FY minus 9-month YTD for additive flows) and is never a filed XBRL period (`fp` never equals Q4). [S2]
19. A ratio, per-share value or weighted-average count never gets derived by subtraction; this stays as doc 21 states, and the FSDS `qtrs` rounding is another reason not to infer a quarter from `qtrs`. [S4]
20. When a deprecated tag disappears from a company's recent filings, check the FASB deprecation relationship (essence-alias, one-to-one replacement possibly changing period type) before calling it a coverage loss. [S9]

---

## 7. Could not confirm

1. **Cover-page XBRL tagging phase-in dates.** The Release 33-10514 text read contains no cover-page tagging rule that my keyword search found (the only "cover page" hit was an unrelated paper-format provision). Cover-page tagging applies via the Guide's dei chapter; its start dates were not sourced.
2. **IFRS foreign private issuer iXBRL dates** under 33-10514 (the release has a separate treatment; the exact dates were not read).
3. **Big R vs little R** (restatement vs revision), SAB 99 and SAB 108: the search found no SEC text on these. Not sourced.
4. **Form 10-K/A rules** (what a 10-K/A must contain, Part III-only amendments, full-document restatements): not read.
5. **Whether companyfacts/frames exclude 10-K/A or 8-K facts**: the SEC page lists 8-K and "variants" for frames; the observed companyconcept response included 10-K/A and 8-K rows. Whether the nightly bulk zip is identical to the API was not tested.
6. **DQC_0013 vs DQC_0014 names.** The approved-rules page's table gave 0013 "Negative values with dependence" and 0014 "Negative values, no dimensions"; one search-result summary swapped them (and also called the IFRS rule 0018). The rule pages for 0013/0014/0018 were not opened.
7. **DQC rules not individually read:** only 0004, 0005, 0008, 0009, 0015, 0095, 0108, 0146, 0192, 0222 were opened. All other descriptions come from the list page's short text. The page itself says some rule descriptions are truncated or duplicated (rules 0245-0252 carry identical boilerplate that does not match their titles).
8. **Which DQC rules EDGAR actually enforces as warnings** beyond the example (negative values) in the Filer Manual / SEC statement: not enumerated.
9. **ASU 2020-05 text.** The December 15, 2021 date for "all other entities" under ASC 842 comes from a FASB summary page seen in a search excerpt, not from the ASU. ASU 2014-09/2015-14 and ASU 2024-03/2025-01 dates come from search-result summaries of FASB PDFs; I did not extract those PDFs.
10. **Revenue tag history.** The year the taxonomy added `RevenueFromContractWithCustomerExcludingAssessedTax` and which older tags it replaced was not checked in release notes.
11. **CARES Act option** that let some large banks delay CECL adoption: not researched. The ASU 2019-10 dates above are the baseline.
12. **S-K Item 302 / SRC-specific omissions:** the eCFR fetch gave the list of items with SRC-specific requirements but not the content (e.g. whether quarterly data are required).
13. **Whether a 53-week year places the extra week in Q4** and the length of quarters in such years: company-specific, not stated in a rule read.
14. **EDGAR taxonomy-support calendar:** only the 2026 and the 2023-removal facts were seen (search summaries of SEC what's-new pages, pages not opened). The full list of supported years was not retrieved.
15. **The 9% custom-tag figure and 18% rendered-statement figure in doc 21 / ledger** are repo measurements, not in SEC text.
16. **Financial Statement and Notes data set table layout** (the PDF) was not extracted.
17. **FASB taxonomy FAQ** ("no undeprecation") and EDGAR Release 21.1 DQC statement come from search-result summaries, not opened pages.

---

## Source index (all read 2026-10-18)
- [S1] EDGAR Filer Manual Vol. II v78 (Sep 14, 2026): https://www.sec.gov/files/edgar/filermanual/edgarfm-vol2-v78.pdf (downloaded, updates section read)
- [S2] EDGAR XBRL Guide, August 2026: https://www.sec.gov/files/edgar/xbrl-guide.pdf (downloaded; sections 1.6, 3.1.x, 3.2.3, 5, 6.x, 7.3, 9.10)
- [S3] Release 33-9002 Interactive Data to Improve Financial Reporting: https://www.sec.gov/rules/final/2009/33-9002.pdf (downloaded and text-extracted)
- [S4] Financial Statement Data Sets documentation PDF: https://www.sec.gov/files/financial-statement-data-sets.pdf (downloaded and text-extracted)
- [S5] Release 33-10514 Inline XBRL Filing of Tagged Data: https://www.sec.gov/files/rules/final/2018/33-10514.pdf (downloaded and text-extracted)
- [S6] EDGAR APIs page: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- [S7] Live API response: https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/NetIncomeLoss.json
- [S8] XBRL US approved DQC rules: https://xbrl.us/data-quality/rules-guidance/
- [S9] 2026 FASB GAAP Taxonomies Release Notes: https://xbrl.fasb.org/resources/annualrelease/2026/GAAP_Financial_Reporting_Taxonomy_Release_Notes.pdf (downloaded and text-extracted)
- [S10] XBRL US test-filing warnings Q&A: https://xbrl.us/home/priorities/data-quality/filing-results/test-filing-warnings/ (search excerpt only) and https://xbrl.us/news/sec-efm-cites-dqc-rules/ (search excerpt only)
- [S11] DQC_0015: https://xbrl.us/data-rule/dqc_0015/
- [S12] DQC_0095: https://xbrl.us/data-rule/dqc_0095/
- [S13] DQC_0192: https://xbrl.us/data-rule/dqc_0192/
- [S14] DQC_0222: https://xbrl.us/data-rule/dqc_0222/
- [S15] DQC_0004: https://xbrl.us/data-rule/dqc_0004/
- [S16] DQC_0009: https://xbrl.us/data-rule/dqc_0009/
- [S17] DQC_0108: https://xbrl.us/data-rule/dqc_0108/
- [S18] DQC_0005: https://xbrl.us/data-rule/dqc_0005/
- [S19] DQC_0146: https://xbrl.us/data-rule/dqc_0146/ (and DQC_0008: https://xbrl.us/data-rule/dqc_0008/)
- [S20] SEC what's-new pages on 2026 taxonomies: https://www.sec.gov/newsroom/whats-new/2603-2026-xbrl-taxonomies-update ; https://www.sec.gov/newsroom/whats-new/260915-edgar-263-release-xbrl-taxonomies-update (search excerpts only)
- [S21] FASB taxonomy FAQ: https://xbrl.fasb.org/resources/taxonomyfaq.pdf (search excerpt only)
- [S22] ASU 2015-14: https://storage.fasb.org/ASU%202015-14.pdf ; ASU 2014-09: https://storage.fasb.org/ASU%202014-09_Section%20A.pdf (search excerpts only)
- [S23] ASU 2016-02 Section A: https://storage.fasb.org/ASU%202016-02_Section%20A.pdf (downloaded and text-extracted)
- [S24] FASB leases post-issuance summary: https://www.fasb.org/Page/PageContent?pageId=/projects/recentlycompleted/leases-post-issuance-summary.html (search excerpt only)
- [S25] ASU 2019-10: https://storage.fasb.org/ASU%202019-10.pdf (downloaded and text-extracted)
- [S26] ASU 2025-01: https://storage.fasb.org/ASU%202025-01.pdf ; FASB In Focus DISE: https://storage.fasb.org/FASB%20In%20Focus%20Disaggregation%20of%20Income%20Statement%20Expenses.pdf (search excerpts only)
- [S27] Financial Statement Data Sets page: https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets
- [S28] Financial Statement and Notes Data Sets page: https://www.sec.gov/data-research/sec-markets-data/financial-statement-notes-data-sets
- [S29] Form 8-K: https://www.sec.gov/files/form8-k.pdf (downloaded and text-extracted; Item 4.02 and General Instruction B.1)
- [S30] SEC Corporation Finance Financial Reporting Manual (revisions to June 29, 2026): https://www.sec.gov/files/cf-frm.pdf (downloaded; sections 1365, 4310, 4610, 4640)
- [S31] Exchange Act Form 8-K C&DIs: https://www.sec.gov/rules-regulations/staff-guidance/compliance-disclosure-interpretations/exchange-act-form-8-k
- [S32] 17 CFR 240.13a-10: https://www.ecfr.gov/current/title-17/section-240.13a-10
- [S33] 17 CFR 210.3-06: https://www.ecfr.gov/current/title-17/section-210.3-06
- [S34] 17 CFR 240.12b-2: https://www.ecfr.gov/current/title-17/section-240.12b-2
- [S35] Company 10-K examples (illustrative, not rules): Apple https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm ; Gap https://www.sec.gov/Archives/edgar/data/39911/000003991125000029/gap-20250201.htm ; Burlington https://www.sec.gov/Archives/edgar/data/1579298/000119312514124097/d667477d10k.htm (search excerpts only)
- [S36] 17 CFR 210.3-02: https://www.ecfr.gov/current/title-17/section-210.3-02
- [S37] 17 CFR 210.8-02: https://www.ecfr.gov/current/title-17/section-210.8-02
- [S38] 17 CFR 229.10(f): https://www.ecfr.gov/current/title-17/section-229.10
