# Verifier: GE quarterly revenue root cause + headline-cell certification trial (2026-10-21)

Role: Data Verifier (data-team/16). Read-only (no DB writes). Status: COMPLETE. Also appended 4 lines to tags/feedback-inbox.md and 4 rows to 22-FILING-LESSONS-LEDGER.md (standing rule).
SEC access: curl with the declared `SEC_USER_AGENT` (read from pipeline/.env, not printed), one process, >= 0.6 s between requests, cached in the session scratchpad.
Evidence labels: FILING-CHECKED (filing opened, locator cited), DATA-INFERRED (our tables only), ASSUMED.

## Part 1. GE quarterly revenue

### 1a. The FY2016 10-K instance (FILING-CHECKED)
Filing: GE 10-K FY2016, accession 0000040545-17-000010, instance `ge-20161231.xml` (13,513,787 bytes; 1,208 contexts), report R164 "402900 - Disclosure - Quarterly Information (Unaudited) (Details)", role `http://www.ge.com/role/QuarterlyInformationUnauditedDetails`.

R164 renders three sections: no dimension (consolidated), `dei:LegalEntityAxis = GE`, `dei:LegalEntityAxis = GE Capital`. The row "Total revenues and other income" (`us-gaap:Revenues`):

| Section | 3-month columns (Q4 16, Q3 16, Q2 16, Q1 16, Q4 15, Q3 15, Q2 15, Q1 15), $M | 12-month 2016 / 2015 / 2014 |
|---|---|---|
| No dimension | 2,649 / 2,600 / 2,771 / 2,885 / 2,585 / 2,660 / 2,690 / 2,866 | 123,693 / 117,386 / 117,184 |
| LegalEntityAxis = GE | (none) | 113,676 / 100,700 / 109,546 |
| LegalEntityAxis = GE Capital | 2,649 / 2,600 / 2,771 / 2,885 / 2,585 / 2,660 / 2,690 / 2,866 | 10,905 / 10,801 / 11,320 |

Instance contexts (parsed from `ge-20161231.xml`):
- Each of the eight 3-month `us-gaap:Revenues` values is filed TWICE with identical value and decimals -6: once in context `FROM_<start>_TO_<end>_Entity_0000040545` (no segment, i.e. the consolidated entity), and once in `..._dei_LegalEntityAxis_ge_SubsidiariesGeccMember` (member `ge:SubsidiariesGeccMember`, GE Capital). Example: `FROM_Apr01_2015_TO_Jun30_2015_Entity_0000040545` = 2,690,000,000 and `FROM_Apr01_2015_TO_Jun30_2015_Entity_0000040545_dei_LegalEntityAxis_ge_SubsidiariesGeccMember` = 2,690,000,000.
- The same double-tagging affects `us-gaap:IncomeLossFromContinuingOperations` in all eight quarters (e.g. Q1 2015 undimensioned = GECC = -5,721M). Those two tags are the only ones in the filing where an undimensioned 3-month fact equals the GECC-member fact for the same period.
- The annual facts are separated correctly: undimensioned 12-month Revenues 2016 = 123,693M (consolidated), GE member (`us-gaap:SubsidiariesMember`) 113,676M, GECC member 10,905M. **Correction to the revenue tag card**: it says the 12-month column holds 113,676M; that figure is the LegalEntityAxis = GE section, not the consolidated (undimensioned) one, which is 123,693M.
- The only consolidated quarterly revenue fact in this note is `us-gaap:SalesRevenueNet` "Sales of goods and services" (undimensioned; Q2 2015 26,141M, Q4 2016 30,345M), which is a component (excludes GE Capital revenues and other income). No undimensioned 3-month fact carries consolidated total revenues in this filing. Other 3-month Revenues facts: `us-gaap:VariableInterestEntityPrimaryBeneficiaryMember` 714M (Q4 2015) and 0 (Q4 2016), dimensional, not totals.

**Root cause (FILING-CHECKED):** a filer tagging error. In the quarterly note GE tagged its GE Capital rows with the GECC-member context and ALSO with the plain (no-dimension) context. Under XBRL convention a no-dimension fact is the consolidated entity, so the companyfacts API (which keeps only undimensioned facts) publishes GE Capital's quarterly revenue (about 2.6-2.9B) as GE's consolidated quarterly revenue (about 27-33B). It is not a dimension the API failed to strip: the wrong value genuinely sits in the consolidated context. Any reader of undimensioned facts (companyfacts, frames, our Normalizer) inherits it. The guard that catches it: a quarterly value must be consistent with the same filing's annual undimensioned value (four quarters summing to 10,905 vs FY 123,693 is a 91% shortfall), and a quarterly fact that duplicates a dimensional member's value in the same filing is a context-error signal.

### 1b. Is the contamination still in what SEC serves? (FILING-CHECKED via SEC companyconcept, us-gaap/Revenues, CIK 40545)
Undimensioned 3-month `Revenues` facts per quarter (all values ever filed, $M):
- 2015 Q1 {2,866 GECC, 26,239, 29,356}; Q2 {2,690 GECC, 29,226, 32,754}; Q3 {2,660 GECC, 28,028, 31,680}; **Q4 2015 {2,585} only, GECC**; 2016 Q1 {2,885 GECC, 27,845}; Q2 {2,771 GECC, 33,494}; Q3 {2,600 GECC, 29,266}; **Q4 2016 {2,649} only, GECC**. The GECC values all come from 0000040545-17-000010 (filed 2017-02-24). For Q1-Q3 2016 a later 10-Q (2017) re-presents a consolidated value with a later filing date; for 2015 Q1-Q3 the GECC value is the LATEST filed copy; for Q4 2015 and Q4 2016 it is the only copy.
- So a "latest filed wins" rule picks GE Capital for 2015 Q1-Q4 and 2016 Q4; a "single value = authoritative" rule picks GE Capital for Q4 2015 and Q4 2016. The correct consolidated Q4 values are FY minus 9M from the same vintage (not computed here; outside the latest-8 window, see 1d).
- Later multi-valued quarters (2017-2023) are legitimate re-presentations (discontinued operations: GE HealthCare spin 2023-01, GE Vernova spin 2024-04; 8-K 0000040545-23-000137 recast), not this error.

### 1c. GE latest eight quarters, filed values (FILING-CHECKED)
| Quarter | Total revenue ($M) | Source and locator |
|---|---|---|
| Q3 2026 (Jul-Sep) | 14,118 | 10-Q 0000040545-26-000064 R2 "Total revenue" (us-gaap:Revenues), 3 months |
| Q2 2026 | 13,349 | 10-Q 0000040545-26-000049 R2 |
| Q1 2026 | 12,392 | 10-Q 0000040545-26-000027 R2 |
| Q4 2025 | 12,717 (derived) | FY2025 45,855 (10-K 0000040545-26-000008 R3) minus 9M 2025 33,138 (10-Q 0000040545-25-000132 R2; same 33,138 re-presented in 0000040545-26-000064 R2). No 3-month Q4 2025 fact is filed |
| Q3 2025 | 12,181 | 10-Q 0000040545-25-000132 R2 (re-presented unchanged in -26-000064 R2) |
| Q2 2025 | 11,023 | 10-Q 0000040545-25-000111 R2 (unchanged in -26-000049) |
| Q1 2025 | 9,935 | 10-Q 0000040545-25-000062 R2 (unchanged in -26-000027) |
| Q4 2024 | 10,812 | Filed as a 3-month fact in 10-K 0000040545-25-000015 (companyconcept); equals FY2024 38,702 (same 10-K, R-statement) minus 9M 2024 27,890 (10-Q 0000040545-24-000200 R2) |
Each of these eight quarters has exactly one filed undimensioned value in companyconcept, so the GE Capital error cannot reach them from SEC data.

## Part 2. Headline-cell trial: filed values (FILING-CHECKED)
Companies: the five largest top-1000 companies whose headline cells had no filing check (S001 was DATA-INFERRED only): NVDA, AAPL, GOOG, MSFT, AMZN. META was the sixth and is not in this trial. Values $M except EPS ($) and shares (millions). Statement R-files from each filing's FilingSummary.xml; footnote cells dropped; one regex parser (mine), no independent second parser.

| Company | Filing | Revenue | Op income | Net income | Diluted EPS | Total assets | Equity (parent) | CFO | Capex (as filed, outflow) | Cover shares | Interest-bearing debt (components) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NVDA | 10-K FY2026 (to 2026-01-25) 0001045810-26-000021 R3/R5/R9/R1 | 215,938 (Revenues) | 130,387 | 120,067 | 4.90 | 206,803 | 157,293 | 102,718 | (6,042) PaymentsToAcquireProductiveAssets "property and equipment and intangible assets" | 24.3B (rounded on cover) | 999 DebtCurrent + 7,469 LTD noncurrent = 8,468 |
| NVDA | 10-Q Q2 FY2027 (to 2026-07-26) 0001045810-26-000075 R2/R4/R7/R1 | 96,221 | 63,734 | 59,688 | 2.46 | 320,272 | 228,984 | 6M 74,421; Q2 = 74,421 - 50,344 (Q1 10-Q 0001045810-26-000052 R7) = 24,077 | 6M (4,434); Q2 = 2,677 | 24.1B | 1,000 + 32,366 = 33,366 |
| AAPL | 10-K FY2025 (to 2025-09-27) 0000320193-25-000079 R3/R5/R8/R1 | 416,161 (RCFC) | 133,050 | 112,010 | 7.46 | 359,241 | 73,733 | 111,482 | (12,715) | 14,776.353 | CP 7,979 + term current 12,350 + term noncurrent 78,328 = 98,657 |
| AAPL | 10-Q Q3 FY2026 (to 2026-06-27) 0000320193-26-000020 R2/R4/R7/R1 | 109,417 | 35,695 | 29,789 | 2.02 | 383,266 | 107,520 | 9M 116,996; Q3 = 116,996 - 82,627 (0000320193-26-000013 R7) = 34,369 | 9M (6,799); Q3 = 2,455 | 14,594.180 | 1,997 + 11,007 + 71,340 = 84,344 |
| GOOG | 10-K FY2025 0001652044-26-000018 R5/R3/R10/R1 | 402,836 (Revenues) | 129,039 | 132,170 | 10.81 | 595,281 | 415,265 | 164,713 | (91,447) | A 5,822 + C 5,438 + B 837 = 12,097 (class-dimensioned only) | LTD noncurrent 46,547 + current 1,996 (R67) = 48,543; CP 0 (R66) |
| GOOG | 10-Q Q2 2026 0001652044-26-000071 R4/R2/R9/R1 | 119,796 | 40,770 | 112,193 | 9.11 | 921,983 | 640,480 | 6M 84,859; Q2 = 84,859 - 45,790 (0001652044-26-000048 R9) = 39,069 | 6M (80,598); Q2 = 44,924 | A 5,868 + C 5,527 + B 835 = 12,230 | 98,165 + 1,999 (R62) = 100,164; CP 0; also LineOfCredit 1.3B outstanding (R61), not shown as a separate balance-sheet line |
| MSFT | 10-K FY2026 (to 2026-06-30) 0001193125-26-323660 R2/R4/R6/R1 | 331,839 (RCFC) | 155,237 | 133,749 | 17.95 | 758,376 | 442,387 | 182,935 | (115,948) | 7,425.545 | 9,227 + 31,067 = 40,294 |
| MSFT | 10-Q Q3 FY2026 (to 2026-03-31) 0001193125-26-191507 R2/R4/R6/R1 | 82,886 | 38,398 | 31,778 | 4.27 | 694,228 | 414,367 | 3M 46,679 (filed as 3 months) | 3M (30,876) | 7,428.435 | 8,839 + 31,423 = 40,262 |
| MSFT | Q4 FY2026 derived (10-K minus 9M of -26-191507) | 90,007 | 40,603 | 35,766 | not derivable (EPS) | | | 55,441 | 35,802 | | |
| AMZN | 10-K FY2025 0001018724-26-000004 R4/R7/R3/R1 | 716,924 (RCFC) | 79,975 | 77,670 | 7.17 | 818,042 | 411,065 | 139,514 | (131,819) PaymentsToAcquireProductiveAssets | 10,734.921 | R69: LongTermDebt 68,836 is FACE value incl. current 2,748; carrying 65,648 + 2,748 = 68,396; ShortTermBorrowings 455 (R68) |
| AMZN | 10-Q Q2 2026 0001018724-26-000026 R3/R6/R2/R1 | 200,606 | 27,461 | 62,647 | 5.75 | 1,095,689 | 551,620 | 3M 45,387 | 3M (54,208) | 10,786.314 | R45: face 132,995 incl. current 3,330; carrying 128,894 + 3,330 = 132,224; ShortTermBorrowings 325 (R44) |

### 1d. Correct consolidated values for the contaminated quarters still inside the display window (HISTORY_FLOOR = 2015-01-01 in apps/app/lib/company/db.ts)
| Quarter | GE Capital value SEC serves (undimensioned) | Correct consolidated total revenues ($M) | Evidence |
|---|---|---|---|
| Q1 2015 | 2,866 (latest filed) | 26,239 | companyconcept: 10-Q 0000040545-16-000152 and recast 8-K 0000040545-16-000163 (API value; R-file not opened) |
| Q2 2015 | 2,690 (latest filed) | 29,226 | 10-Q 0000040545-16-000174 (R2 per tag card [28]; API value agrees) |
| Q3 2015 | 2,660 (latest filed) | 28,028 | 10-Q 0000040545-16-000195 R2 "Total revenues and other income", 3 months to 2015-09-30 (FILING-CHECKED this run) |
| Q4 2015 | 2,585 (only copy) | 33,892 = 117,386 - 83,494 | FY2015 117,386: 0000040545-17-000010 R164 12-month column (and 8-K recast 0000040545-16-000162, API); 9M 2015 83,494: 0000040545-16-000195 R2 (FILING-CHECKED). Same June-2016 recast basis: Q1+Q2+Q3 = 83,493 |
| Q4 2016 | 2,649 (only copy) | 33,089 = 123,693 - 90,604 | FY2016 123,693: 0000040545-17-000010 R164; 9M 2016 90,604: 0000040545-16-000195 R2 (FILING-CHECKED). Check: 27,845 + 33,494 + 29,266 = 90,605 |
Note: the FY2018 10-K (0000040545-19-000014) re-presents FY2016 at 119,469 (another recast), so a 2016 series must use one vintage throughout.
Q1-Q3 2016: the GECC copies (2,885 / 2,771 / 2,600) are older than the 2017 10-Q re-presentations (27,845 / 33,494 / 29,266), so latest-filed is correct there; a "mark all conflicting copies non-authoritative" rule blanks them instead.

## Part 1 (cont.). What we STORE and SHOW for GE quarterly revenue
DB access: one connection per query batch, `set transaction read only`, `statement_timeout = 20s`. Gate: `pg_stat_activity` showed 17-19 rows throughout; 8-9 of those are Postgres server processes (checkpointer, walwriter, autovacuum launcher, pg_cron, pg_net, etc.) and client backends were 9-10, Supavisor pooler sessions 5 including mine. I gated on client backends (<= 14), not on all rows; the literal "total rows > 14" gate would never open on this instance. ListAgents was not available in this session.
The page's quarterly "Revenue" row is `analytics.statement_line` (income_statement, order 1) -> `revenue_sanity_resolved` in `analytics.canonical_fact` (apps/app/lib/company/db.ts getStatement; HISTORY_FLOOR 2015-01-01). GE = company_id 608.

### 1e. Latest eight stored quarters vs filings
| Quarter | Shown (revenue_sanity_resolved, $M) | Source fact / tag / accession | Filed total revenue ($M) | Verdict |
|---|---|---|---|---|
| Q3 2026 | (not stored) | - | 14,118 (0000040545-26-000064 R2, filed 2026-10-20) | not yet ingested (filed yesterday); freshness, not a value error |
| Q2 2026 | 13,349 | 12914564 Revenues 0000040545-26-000049 | 13,349 | MATCH |
| Q1 2026 | 12,392 | 12914562 Revenues 0000040545-26-000027 | 12,392 | MATCH |
| Q4 2025 | 12,716 | 77421194 Revenues, derived, 0000040545-26-000008 | 12,717 = 45,855 - 33,138 (9M YTD as filed) | precision-consistent: 12,716 = FY - (9,935 + 11,023 + 12,181 = 33,139), i.e. three rounded quarters instead of the filed 9M YTD. Both lie in the rounding interval [12,716, 12,718]. Propose FY minus filed 9M YTD (12,717); not counted as a wrong value |
| Q3 2025 | 12,181 | 12914560 Revenues 0000040545-25-000132 | 12,181 | MATCH |
| Q2 2025 | 11,023 | 12914557 Revenues 0000040545-25-000111 | 11,023 | MATCH |
| Q1 2025 | 9,935 | 12914553 Revenues 0000040545-25-000062 | 9,935 | MATCH |
| Q4 2024 | **9,879** | 12914189 RevenueFromContractWithCustomerExcludingAssessedTax 0000040545-25-000015 | **10,812** (0000040545-25-000015 R161 "Total revenue") | **WRONG**: shows "Sales of equipment and services" (RCFC), which excludes insurance revenue |
| Q3 2024 | **8,943** | 12914188 RCFC 0000040545-25-000015 | **9,842** (R161; also 10-Q 0000040545-24-000200 R2) | **WRONG**, same cause |
| (Q2 2024, 9th) | **8,223** | 12914187 RCFC | **9,094** (R161) | WRONG, same cause |
| (Q1 2024, 10th) | **8,076** | 12914186 RCFC | **8,955** (R161) | WRONG, same cause |
FY2024 shown 38,702 (Revenues) MATCHES the 10-K, so the 2024 quarters sum to 35,121, 3,581 below the year shown beside them.

**Root cause of the wrong 2024 quarters (FILING-CHECKED + DATA-INFERRED):** the `revenue` concept is first_match with `RevenueFromContractWithCustomerExcludingAssessedTax` at priority 1 and `Revenues` at priority 2 (`analytics.concept_mapping`). GE's FY2024 10-K quarterly note (0000040545-25-000015 R161) files BOTH undimensioned for every quarter: "Total revenue" (`Revenues` 10,812 / 9,842 / 9,094 / 8,955) and "Sales of equipment and services" (RCFC 9,879 / 8,943 / 8,223 / 8,076). RCFC wins, so the component is shown. 2025-2026 quarters are right only because GE's 10-Q RCFC facts are dimensioned (two "Sales" rows), leaving `Revenues` as the only undimensioned candidate. This is exactly the revenue card's warning ("never mix with RCFC in a precedence list without checking that the company does not report both"); GE is a live counterexample to RCFC-first.

### 1f. Older displayed quarters (inside HISTORY_FLOOR, beyond the latest 8): DATA-INFERRED trace, spot FILING-CHECKED
The GE Capital values (2,866 / 2,690 / 2,585 / 2,649) are in base `revenue` (Q1, Q2, Q4 2015; Q4 2016) but are NOT what the page shows: `revenue_sanity_resolved` replaces 2015-Q1 2018 with `SalesRevenueNet` ("Sales of goods and services", a component excluding GE Capital revenues and other income), and 2018 Q2 - 2024 with RCFC/RCFC-including-tax components. Examples, FILING-CHECKED: Q3 2015 shown 25,527 (SalesRevenueNet, 0000040545-16-000195) vs total 28,028 (same filing R2); Q4 2015 shown 30,614 vs total 33,892; Q4 2016 shown 30,345 vs total 33,089; Q2 2023 shown 7,907 (RCFC) vs total 8,755 (R161). The annual rows FY2015-FY2018 also show components (FY2015 105,809 vs 117,386; FY2016 110,391 vs 123,693; FY2018 113,543 RCFC). Quarterly 2020 (RCFC from the 2022 10-K vintage) and FY2020 (58,025 from the 2023 recast 8-K) mix vintages. Scope of wrong GE revenue cells: about 34 quarterly and 4 annual cells 2015-2024 by this trace (DATA-INFERRED count; each value not individually filing-checked).

## Part 2 (cont.). Stored and shown vs filed, per cell
Stored = `analytics.canonical_fact` for the concepts the page renders (`*_resolved`, `revenue_sanity_resolved`); market cap = `analytics.metric_value` market_cap (TTM, 2026-10-20) and `core.market_price_alpaca`. Signs: capex is stored positive (payment tag); filings print it in parentheses. Magnitude match = match (rule 11).

| Company | Period | Rev | OI | NI | Dil EPS | Assets | Equity | CFO | Capex | Shares | Total debt |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NVDA | FY2026 | M | M | M | M | M | M | M | M | M 24,304 (10-K R5 label) | M 8,468 |
| NVDA | Q2 FY27 | M | M (stored via Revenues - CostOfRevenue - OperatingExpenses, not the filed OperatingIncomeLoss; same value) | M | M | M | M | M 24,077 | M 2,677 | **X** no Q2 value; page shows 24,304 (2026-01-25); filed 24,147 at 2026-07-26 (10-Q R5 equity statement, `CommonStockSharesOutstanding` with the equity-component column dimension, so absent from companyfacts) | M 33,366 |
| AAPL | FY2025 | M | M | M | M | M | M | M | M | M 14,773.260 (R5 parenthetical/label) | M 98,657 |
| AAPL | Q3 FY26 | M | M | M | M | M | M | M 34,369 | M 2,455 | M 14,608.963 (R4 label) | **X** 84,297 stored = LongTermDebt 82,300 + CP 1,997; 82,300 is the debt note's narrative "fixed-rate notes, aggregate carrying amount" rounded to $0.1B (R38); balance sheet 11,007 + 71,340 + 1,997 = 84,344 |
| GOOG | FY2025 | M | M | M | M | M | M | M | M | M 12,088 (R3 label) | **X** 49,085 stored (LongTermDebt + CP 0) is FACE value; carrying 46,547 + 1,996 = 48,543 (R3, R67; 542 unamortized discount) |
| GOOG | Q2 2026 | M | M | M | M | M | M | M 39,069 | M 44,924 | M 12,230 (R2 label) | M 100,164 (carrying). Open: LineOfCredit 1.3B outstanding (R61) is not in it |
| MSFT | FY2026 | M | M | M | M | M | M | M | M | M 7,427 (R4 label) | M 40,294 |
| MSFT | Q3 FY26 (10-Q) | M | M | M | M | M | M | M | M | M 7,429 (R4 label) | M 40,262 |
| MSFT | Q4 FY26 (latest quarter shown; derived) | M 90,007 | M 40,603 | M 35,766 | **X** 4.80 stored (core.fact 341935, is_derived) vs **4.81** filed (8-K 0001193125-26-323632 Ex. 99.1 income statement, three months ended 2026-06-30) | n/a | n/a | M 55,441 (Ex. 99.1) | M 35,802 (Ex. 99.1) | | |
| AMZN | FY2025 | M | M | M | M | M | M | M | M | M 10,731 (R8) | **X** 69,291 stored = LongTermDebt 68,836 (FACE, R69) + ST borrowings 455; carrying 65,648 + 2,748 + 455 = 68,851 |
| AMZN | Q2 2026 | M | M | M | M | M | M | M 45,387 | M 54,208 | M 10,783 (R7) | **X** 133,320 stored = face 132,995 + 325; carrying 128,894 + 3,330 + 325 = 132,549 (R45, R44) |
M = match, X = mismatch. Values not repeated in a cell are the filed values in the Part 2 table above, which equal the stored ones exactly.

Market cap (one cell per company): stored = Alpaca price 2026-10-20 x latest cover-page shares, exactly (AAPL 14,594,180,000 (10-Q R1); MSFT 7,425,545,491 (10-K R1); GOOG 12,230M = A + B + C (10-Q R1); AMZN 10,786,313,572 (10-Q R1); NVDA 24,100,000,000 (10-Q R1, filer-rounded to 0.1B; the 2026-07-26 balance in R5 is 24,147M, so the NVDA input carries up to about 0.2% rounding, and 24,147M x 216.54 = 5,228.8B vs stored 5,218.6B)). Shares input FILING-CHECKED; the price is DATA-INFERRED (no filing carries it). GOOG applies the GOOGL (class A) price to classes B and C, a policy choice, not checked here.

### Tally
- Cells checked: 5 companies x 2 periods x 10 headline items = 100, plus MSFT's derived Q4 (6 flow cells), plus 5 market-cap share inputs = 111 cells. Matches 104; mismatches 7 headline cells:
  1. MSFT Q4 FY26 diluted EPS 4.80 vs 4.81 (EPS derived arithmetically, against the never-subtract rule).
  2. AAPL Q3 FY26 total debt 84,297 vs 84,344 (rounded narrative tag preferred over the exact split tags).
  3. GOOG FY2025 total debt 49,085 vs 48,543 (face value, not carrying).
  4. AMZN FY2025 total debt 69,291 vs 68,851 (face value).
  5. AMZN Q2 2026 total debt 133,320 vs 132,549 (face value).
  6. NVDA Q2 FY27 shares: none stored, page shows the January count 24,304 vs filed 24,147.
  7. NVDA market cap input: filer-rounded 24.1B; informational (precision of the filed input), not counted as a wrong value if policy accepts cover shares.
  Counted strictly as wrong displayed values: 1-6.
- Extra, outside the headline window: AAPL Q4 FY25 diluted EPS shown 1.84 vs **1.85** filed (8-K 0000320193-25-000077 Ex. 99.1). Together with MSFT this shows the derived-Q4 EPS cells are systematically unsafe. GOOG 2.82, AMZN 1.95, NVDA 1.76 Q4 EPS were not checked against releases.
- Total debt: 4 of 10 debt cells wrong, 3 of them because `LongTermDebt` is face value at AMZN and GOOG (and a rounded narrative at AAPL). The `concept_mapping` note for LongTermDebt ("equals LongTermDebtCurrent + LongTermDebtNoncurrent exactly whenever both are reported") is false at AMZN (R69) and GOOG (R67).

### Untested scope / limits
- One parser (my regex over R-files, footnote cells dropped); no independent second parser. GOOG/AMZN debt read from note R-files; FX-denominated notes not re-added.
- Prices not verifiable from filings. GE Q3 2026 freshness not re-checked after tonight's nightly.
- Derived Q4 flow cells for NVDA, AAPL, GOOG and AMZN (not the latest quarter) were not filing-checked.
- GE 1f counts are DATA-INFERRED from the trace; only 4 older cells were opened.

Status: COMPLETE for the requested scope.
