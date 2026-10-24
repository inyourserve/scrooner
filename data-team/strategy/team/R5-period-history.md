# R5. The HISTORY dimension of tag non-uniformity, top 1,000, 2015-01-01 to date (Period Engineer, 2026-10-21)

Status: PARTIAL. FSDS work and code reading are complete; the database breakdown of `analytics.period_gap` by cause x year was NOT_RUN (pooler at 17-21 connections on every attempt between 01:38 and 02:13 local, above the brief's limit of 14; see section 10). Every count below names its source and evidence class. Read-only: no code, migration or table was changed.

Scope: top 1,000 = `doc/data-moat/team/top1000/shards.csv` (1,014 rows, provisional ranking). Window: periods ending 2015-01-01 or later. Concepts: the 16 in `sanity/period_completeness.py::CHECK_CONCEPTS` plus capex, D&A, cost of revenue, interest expense, leases and credit losses where the era question bites.

## 1. Short answer
1. The history gap is not one problem. It is four, with different owners: (a) pre-2018 vocabulary (era tags we do not map), (b) Q4 and interim derivation that is blocked by input conflicts and by fixed day-bands, (c) recast/restatement basis conflicts concentrated in the 2016-2018 accounting-standard wave, (d) identity breaks (fiscal-year changes, predecessor CIKs).
2. The single biggest history-specific lever found here is cheap and was not on anyone's list: **for fiscal years ending before 2021-08-09, most 10-Ks FILE a discrete Q4** in the Item 302(a) quarterly note. In top-1000 FY2015 10-Ks, 388 of 515 (75%) that tag FY revenue also tag a 3-month Q4 revenue, and 407 of 540 tag a 3-month Q4 diluted EPS. In FY2021 10-Ks this falls to 58 of 655 (9%). So for 2015-2020, Q4 (including Q4 EPS, which we must never derive) can come from a filed fact, and the note gives an independent check on any derived Q4. From FY2021 on, Q4 must be derived. (FSDS, DATA-INFERRED; rule change FILING-CHECKED against SEC Release 33-10890.)
3. Era vocabulary is real and sharply dated for revenue and cost of revenue: in FY2015 10-Ks, 134 of 773 top-1000 filers (17.3%) have no repo-mapped revenue tag on the income statement; from FY2018 on it is 19-21 filers (2.3%). The missing tags are `SalesRevenueGoodsNet` (KO, PFE, JNJ, MRK...), `SalesRevenueServicesNet`, `RealEstateRevenueNet` and lease-revenue tags; their last standard-taxonomy use in FSDS is `us-gaap/2017`.
4. A new era break is happening NOW, not only in 2018: the 2024 taxonomy added `InterestExpenseNonoperating`/`InterestExpenseOperating`. Top-1000 filers presenting `InterestExpense` on the face fell from 571 (2022q1) to 175 (2025q4) while 363 now present `InterestExpenseNonoperating`. Neither new tag is in the repo's `interest_expense` mapping (DB not checked).
5. Derivation needs an allowlist at the canonical-concept level and calendar-aware windows. Today `normalizer/derived.py` subtracts every duration tag except ratio units, per-share tags and `WeightedAverage%`, and uses fixed day-bands (half-year 170-200, nine-month 260-290) that a 12/12/12/16-week calendar cannot satisfy (Costco's 24-week YTD is 167 days, FILING-CHECKED).

## 2. Gap counts by cause (top 1,000, periods since 2015-01-01)
Baseline from data-team/34 (`analytics.period_completeness` / `period_gap`, measured 2026-10-21 by Dhairya, DATA-INFERRED, 15-16 concepts only): 717,052 expected, 25,193 missing.

| Cause (period_gap) | Cells | Owner | What it really is in the history window | Evidence class |
|---|---|---|---|---|
| no_mapped_tag | ~8,600 | Tag Mapper / Tag Expert | Mix of (i) era vocabulary 2015-2017 (section 3), (ii) sector lines that do not exist (banks have no operating income: 200-231 top-1000 filers have no OperatingIncomeLoss on the face in every era), (iii) perimeter variants (cost of revenue excluding D&A). Era share NOT MEASURED (needs DB by year) | DATA-INFERRED (FSDS shape), split NOT_RUN |
| q4_not_derived | 5,801 | Period Engineer | Mostly input conflicts (2026-10-17 census: 65% conflicting FY or 9M, 31% no 9M source, 2% clean; whole population, not top-1000). In 2015-2020 a filed Q4 usually exists in the 10-K note, so a q4 gap there points to a mapping/label problem of the note fact, not to missing arithmetic. By-year split NOT_RUN | DATA-INFERRED |
| quarter_not_derived | 5,345 | Period Engineer | Cash-flow lines are YTD-only in 10-Qs: CFO YTD-only in 82 of 83 (2016q1) and 97 of 99 (2022q1) top-1000 Q2/Q3 10-Qs; capex 62/69 and 79/84; revenue and net income are discrete in all. Calendars outside the fixed day-bands never derive (Costco) | DATA-INFERRED (FSDS num) + code |
| no_line_item_filed | ~1,700 | Verifier (rendered check) | Cannot be called absence without rendered statements (18% false rate known) | per data-team/22 |
| not_in_sec_feed | ~1,500 | Data Engineer (P3) | Feed/ingestion, not history semantics | DATA-INFERRED |
| filing_not_processed | ~850 | Data Engineer | Pipeline | DATA-INFERRED |
| conflict_material | 566 | Period Engineer + resolver | Expected to cluster in FY2016-FY2018 (recast wave, section 5); NOT MEASURED by year | ASSUMED until DB split |
| other (rounding, split, not_resolved) | ~800 by difference | resolver | | DATA-INFERRED |
Sum of named causes is about 24.4k of 25,193; data-team/34 gives approximate figures, so the remainder is not attributed here.

Not counted at all today: concepts outside the 16 (I11 widens to 33). For those, era breaks (leases before ASC 842, CECL allowance tags, cash-change tags before ASU 2016-18) will create thousands of new history "gaps" that are structural, not missing data, unless the reason codes in section 4 exist first.

## 3. Era-scoped tag set per concept (FSDS, top-1000 filers on the face statement)
Method: SEC Financial Statement Data Sets 2016q1 (mostly FY2015 10-Ks), 2019q1 (FY2018), 2022q1 (FY2021) fetched by HTTP range (sub/pre/tag; num for 2016q1 and 2022q1, filtered while streaming), plus the existing 2025q4 extract (mostly 10-Qs). Counts are DISTINCT top-1000 CIKs whose IS/BS/CF presentation (pre.txt) carries the tag, 10-K and 10-Q family. "Std versions" = us-gaap taxonomy versions of the tag used by any filer in that quarter (tag.txt). First/last use years are bracketed by the four samples, not exact. Scripts: section 11. Evidence: DATA-INFERRED; KO row FILING-CHECKED.

| Concept | Tag | 2016q1 | 2019q1 | 2022q1 | 2025q4 | Std versions seen | Era reading | Mapped in repo? |
|---|---|---|---|---|---|---|---|---|
| revenue | SalesRevenueNet | 308 | 18 | 0 | 0 | 2014-2016 / 2017 / none / none | pre-ASC 606, last std 2017 | yes (p3) |
| revenue | SalesRevenueGoodsNet | 167 | 12 | 0 | 0 | same | pre-606; sole top line at KO, PFE, JNJ, MRK, GLW, IFF (48 FY2015 filers goods-only, no mapped tag) | no (0038 rejected it globally) |
| revenue | SalesRevenueServicesNet | 104 | 4 | 0 | 0 | same | pre-606 | no |
| revenue | OtherSalesRevenueNet, RealEstateRevenueNet, OperatingLeasesIncomeStatementLeaseRevenue, TechnologyServicesRevenue, FinancialServicesRevenue, LicensesRevenue | 46, 24, 33, 15, 14, 20 | 1, 3, 34, 0, 0, 1 | 0 | 0 | 2014-2017 | pre-606 / pre-842 lessor | no |
| revenue | RevenueFromContractWithCustomerExcludingAssessedTax | 0 | 390 | 522 | 592 | from 2017-2018 | ASC 606 | yes (p1) |
| revenue | Revenues | 305 | 360 | 349 | 360 | all | all eras | yes (p2) |
| revenue (all) | filers with an IS but no mapped revenue tag | 134 of 773 | 19 of 824 | 21 of 916 | 20 of 988 | | era gap is FY2015-FY2017 | |
| cost_of_revenue | CostOfGoodsSold | 224 | 22 | 0 | 0 | last std 2017 | pre-2018 | yes (0082) |
| cost_of_revenue | CostOfServices | 87 | 6 | 0 | 0 | last std 2017 | pre-2018 | no |
| cost_of_revenue | CostOfGoodsAndServicesSold | 131 | 419 | 457 | 487 | all | successor | yes |
| cost_of_revenue | CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization / CostOfGoodsSoldExcludingDDA | 0 / 10 | 0 / 20 | 52 / 0 | 63 / 0 | | perimeter variant (excludes D&A), both eras | no; needs a perimeter decision, not a synonym mapping |
| interest_expense | InterestExpense | 493 | 521 | 571 | 175 | all | collapsing since the 2024 taxonomy | yes (p1) |
| interest_expense | InterestExpenseNonoperating / InterestExpenseOperating | 0 / 0 | 0 / 0 | 0 / 0 | 363 / 71 | std only from 2024 (earlier only as company extensions) | NEW era | no (and Tag Mapper file 31: nonoperating exceeds InterestExpense in 723 periods, so not a blind synonym) |
| income_before_tax | ...MinorityInterestAndIncomeLossFromEquityMethodInvestments vs ...ExtraordinaryItemsNoncontrollingInterest | 351 vs 368 | 321 vs 448 | 118 vs 729 | 99 vs 804 | | shift, both mapped | yes |
| cfo / cfi | NetCashProvidedByUsedIn...ContinuingOperations | 333 / 330 | 102 / 91 | 53 / 36 | 47 / 30 | | pre-2018 heavy use of the continuing-ops total | yes (p2, 0095) |
| cash change (identity I2) | CashAndCashEquivalentsPeriodIncreaseDecrease | 698 | 396 | 12 | 0 | | pre-ASU 2016-18 (cash excludes restricted) | no concept |
| cash change | CashCashEquivalentsRestrictedCash...PeriodIncreaseDecreaseIncludingExchangeRateEffect | 0 | 327 | 819 | 902 | from 2017 | post-ASU 2016-18 (restricted cash included) | no concept |
| cash change | IncreaseDecreaseInRestrictedCash (CF line) | 154 | 12 | 0 | 0 | | restricted cash was a CF line before 2018: CFI/CFO of 2016-2017 are recast in 2018 filings | n/a |
| current assets/liabs | DeferredTaxAssetsNetCurrent / DeferredTaxLiabilitiesCurrent | 183 / 59 | 1 / 1 | 0 | 0 | | ASU 2015-17: current deferred taxes vanish; current assets of 2015 are not comparable to 2017 | n/a |
| leases | OperatingLeaseRightOfUseAsset / OperatingLeaseLiabilityNoncurrent | 0 / 0 | 5 / 4 | 497 / 448 | 531 / 473 | from 2017-2018 | ASC 842: a lease value before the filer's adoption period does not exist | yes (proposed concepts) |
| leases | CapitalLeaseObligationsNoncurrent -> FinanceLeaseLiabilityNoncurrent | 30 -> 0 | 32 -> 1 | 1 -> 47 | 0 -> 54 | | ASC 842 rename | debt rebuild must carry both |
| bank allowance | LoansAndLeasesReceivableAllowance -> FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest | 40 -> 0 | 40 -> 0 | 22 -> 18 | 1 -> 45 | new from 2021 | CECL | no concept |
| bank provision | ProvisionForLoanAndLeaseLosses (CF) | 28 | 27 | 18 | 0 | | pre-CECL; ProvisionForLoanLeaseAndOtherLosses (26-37) and ProvisionForLoanLossesExpensed (5 -> 20 -> 14) span both; FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal new (7 in 2025q4) | no concept |
| equity securities | AvailableForSaleSecuritiesEquitySecurities -> EquitySecuritiesFvNi | 29 -> 0 | 16 -> 46 | 0 -> 47 | 0 -> 39 | | ASU 2016-01 | n/a |
| insurers | MarketRiskBenefit*, LiabilityForFuturePolicyBenefitRemeasurementGainLoss | 0 | 0 | 0 | 12-13 | | LDTI (ASU 2018-12, 2023, retrospective to 2021) | n/a |
| pension | NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent | 0 | 22 | 30 | 33 | | ASU 2017-07 moved non-service pension cost out of operating income, retrospectively | n/a |

Stable across eras (no history-specific action): NetIncomeLoss/ProfitLoss (1 of 773 lacking in 2016q1), CFO/CFI/CFF totals (0-5 lacking), Assets, StockholdersEquity, EPS diluted (24-30 lacking, almost all IncomeLossFromContinuingOperationsPerDilutedShare filers), income tax expense (33-43 lacking, no family tag: likely banks/REITs/partnerships with no tax line). Capex (`PaymentsToAcquireProductiveAssets` 129-141 every era) and D&A (`Depreciation` 145-167) gaps are flat across eras: they are perimeter problems (R-other), not history problems.

FILING-CHECKED anchor: KO FY2015 10-K 0000021344-16-000050 R2, first row "NET OPERATING REVENUES" 44,294 ($M), bound to `us-gaap_SalesRevenueGoodsNet` (defref in R2).
Trap found: TAP FY2015 (0000024545-16-000054 R2, FSDS pre) presents `SalesRevenueGoodsNet` "Sales" GROSS of excise, then `SalesRevenueGoodsNetExcludingExciseAndSalesTaxes` "Net sales". So "SalesRevenueGoodsNet is total revenue" is only safe when it is the top line AND no net-of-excise line follows (DATA-INFERRED, R2 not opened).

Proposed era-scoped rule (for the Tag Mapper and Standardization Lead, not approved): a tag that is not a global synonym can be a company-period synonym when (1) it is the first revenue line of that filing's income statement (pre.txt line order), (2) no mapped revenue tag exists on that statement, (3) no "...ExcludingExciseAndSalesTaxes"/net line follows it, (4) for the same company, the first year that uses a mapped tag restates the prior year (the 10-K that switches tags carries the comparative year under the new tag) and the two values agree within rounding. Rule (4) is the non-circular proof: in the ASC 606 year the comparatives of the older years appear under the new tag (Apple: `Revenues` FY2018 -> RCFC FY2019, data-team/22), so the old tag can be validated against the new tag on the overlap year, per company. A full or modified-retrospective 606 adopter can show a different number for the overlap year; that is a basis difference to record, not a mismatch to suppress.

## 4. Accounting and rule events that break history (what each does to a 2015+ series)
| Event | Effective (verified where cited) | What it does to stored history | Required handling |
|---|---|---|---|
| ASC 606 revenue | annual periods after 2017-12-15 (EGCs later); Apple FY2019 (data-team/22) | revenue tag changes; full-retrospective adopters recast 2016-2017 revenue (two true values per period) | era-scoped tags (section 3); basis flag per period |
| ASU 2016-18 restricted cash, ASU 2016-15 cash classification | 2018 for calendar filers (ASSUMED from FSDS shape: restricted-cash CF lines 154 -> 12 -> 0) | CFO/CFI/CFF of 2016-2017 recast in 2018 10-Ks; cash definition for the cash-change identity changes | latest-basis pairing (section 6); era-scoped cash tag in identity I2 |
| ASU 2015-17 deferred taxes noncurrent | 2017 (prospective or retrospective) | current assets/liabilities lose deferred taxes; 183 top-1000 filers had current deferred tax assets in FY2015 | current ratio across 2015-2016 is not comparable; record as a basis note, not a gap |
| ASU 2017-07 pension | 2018, retrospective | operating income of 2016-2017 recast (non-service cost moved below operating income) | operating income conflict across vintages is expected, prefer latest basis |
| ASC 842 leases | fiscal years after 2018-12-15 (Apple FY2020; EGC 2022, data-team/22) | ROU/lease liability exist only after adoption; prior periods not restated by most filers | reason `not_applicable_before_adoption` keyed to the filer's own first period with the tag; never a gap |
| CECL (ASC 326) | 2020 / 2023 / CARES deferrals to 2022 (data-team/22) | allowance and provision tags change; pre-CECL allowance is an incurred-loss figure | separate concept or basis flag; never splice silently |
| LDTI (ASU 2018-12) | 2023 with retrospective restatement to 2021 (ASSUMED) | insurers' 2021-2022 results restated | prefer latest basis; keep both |
| Item 302(a) quarterly data eliminated | Release 33-10890, effective 2021-02-10, mandatory for fiscal years ending on or after 2021-08-09 (FILING-CHECKED, release text sec. II.F) | filed discrete Q4 disappears from most 10-Ks after FY2020 | use filed Q4 for FY2015-FY2020; derive only from FY2021 on (section 5) |
| us-gaap 2024 interest tags | 2024 taxonomy (FSDS tag.txt versions) | interest expense moves to new tags in current filings | mapping decision for `interest_expense` now, with the I-2 caveat from file 31 |

## 5. Q4 and quarter derivation: what the data and the code show
5.1 Filed Q4 exists for most 2015-2020 years (FSDS num, top-1000 10-Ks, undimensioned facts, DATA-INFERRED):

| FSDS bucket | 10-Ks with FY value | ...that also file a 3-month Q4 | 4 filed quarters sum to FY within 0.5% | mismatches |
|---|---|---|---|---|
| 2016q1 (FY2015) revenue | 515 | 388 | 384 | 4 |
| 2016q1 net income | 541 | 391 | 381 | 10 |
| 2016q1 diluted EPS | 540 | 407 | n/a (non-additive) | |
| 2016q1 operating income / gross profit | 447 / 202 | 221 / 156 | 220 / 155 | 1 / 1 |
| 2016q1 CFO | 395 | 0 | | |
| 2022q1 (FY2021) revenue | 655 | 58 | 56 | 0 |
| 2022q1 net income | 670 | 60 | 56 | 1 |
| 2022q1 diluted EPS | 686 | 64 | | |
Cash flow never has a filed Q4 in any era: Q4 cash flow is always FY minus 9M YTD.
The mismatches are exactly the failure classes we must catch:
- SUN (Sunoco LP) FY2015 10-K 0001564590-16-013451 R105 "Quarterly Results of Operations (Unaudited) (Details)": Q4 2015 "Total revenues" printed 3,674,623 under a USD column while the FY column prints $16,935,347,000; the quarterly facts are 1,000x too small (FILING-CHECKED). The same page carries a 4-month successor (Sep-Dec 2014) and an 8-month predecessor (Jan-Aug 2014) column: push-down accounting splits one fiscal year into two stub periods.
- MPLX revenue (FY 703M vs quarters 668M), WEX, ELS, SUI, BXP, REXR net income, CZR revenue, XEL FY2021 net income and operating income: quarters do not sum to the FY fact (DATA-INFERRED; likely common-control recasts, attribution to parent vs total, or label errors; not opened).
- IBRX: the four latest 3-month facts end 2014-09-30, 2014-12-31, 2015-03-31, 2015-12-31: a fiscal-year change.
So a filed Q4 is evidence, not truth. It is the same class of fact as the label-shift cases in data-team/22 (SWK, CB, Ford).

5.2 Cumulative YTD vs discrete (FSDS num, top-1000 Q2/Q3 10-Qs, DATA-INFERRED): CFO is YTD-only in 82/83 (2016q1) and 97/99 (2022q1); capex 62/69 and 79/84; SBC 56/70 and 75/89; D&A 37/54 and 47/64; revenue 0 YTD-only; net income 1/73 and 0/90. Every discrete cash-flow quarter after Q1 must be derived. These samples are non-calendar fiscal-year filers only (calendar filers file 10-Qs in other buckets).

5.3 Code facts (`pipeline/src/scrooner_pipeline/normalizer/derived.py`, working tree incl. uncommitted per-share guard; git log 6f3fcd5..e925667 read):
- No additive allowlist. Any authoritative duration fact is subtracted unless its unit is a ratio/`pure`, its tag matches the per-share regex, or `WeightedAverage%` (approximation method). Duration share counts that are NOT flows still get subtracted: `IncrementalCommonSharesAttributableToShareBasedPaymentArrangements` and `AntidilutiveSecuritiesExcludedFromComputationOfEarningsPerShareAmount` (6 top-1000 FY2021 10-Ks each in FSDS). Low reach, but it shows the guard is a denylist.
- Fixed day-bands: `HALF_YEAR` 170-200, `THREE_QUARTER` 260-290, Q4 via YTD 80-100. Costco 10-Q 0000909832-22-000005 R7 is "6 Months Ended Feb. 13, 2022" (24 weeks; fiscal year began 2021-08-30), 167 days, outside the half-year band; its 36-week YTD (about 251 days) is outside the nine-month band; its 16-week Q4 (about 111 days) is outside the Q4 band. So Costco's cash-flow Q2, Q3 and Q4 are never derived by this code (FILING-CHECKED period; the "never derived" is a code inference, DB not checked).
- The chain path (FY - Q1 - Q2 - Q3) checks contiguity but not Q4 length; the YTD path checks Q4 length. Inconsistent but not wrong.
- Inputs must be authoritative: a conflicted 9M or FY blocks derivation (correct default; it is why 65% of Q4 gaps are conflicts).
- Derived Q4 inherits the FY fact's filing_id as lineage; the 9M input fact id is not stored. The role spec requires every input fact id.

## 6. Safe derivation rulebook (PROPOSAL for the Standardization Lead and a named accountant; not approved)
Allowlist by canonical concept, not by tag. A concept may be derived (Q2 = H1 - Q1, Q3 = 9M - H1, Q4 = FY - 9M or FY - Q1 - Q2 - Q3) only if listed here.

| Class | Concepts | Q4 = FY - 9M safe? | Conditions |
|---|---|---|---|
| A. Additive flow, robust to reclassification | net_income (total and attributable), comprehensive_income, cfo, cash_flow_investing, cash_flow_financing, net cash change | yes | same-basis inputs (rule B1); NI total is unchanged by discontinued-ops reclassification, cash totals are unchanged by line moves inside a section |
| B. Additive flow, sensitive to reclassification/recast | revenue, cost_of_revenue, gross_profit, sga, r&d, operating_expenses, operating_income, income_before_tax, income_tax_expense, interest_expense, interest_income, d&a, sbc, capex, dividends_paid, buybacks, interest_paid, taxes_paid, working-capital changes | yes, only with B1 + B2 | these move when discontinued operations, ASU 2017-07, ASC 606 full retrospective or cash-flow reclassifications occur between the 10-Q and the 10-K |
| C. Approximation, separately approved | weighted_avg_shares_basic/diluted | 4*FY - (Q1+Q2+Q3) (founder-adopted 2026-10-17, flagged approximate) | never feeds EPS |
| D. Never derived | basic/diluted EPS, DPS, any per-share or per-unit value, effective tax rate, margins/ratios, incremental and antidilutive share counts, employee count, any instant (balance sheet: Q4 = FY-end instant, already filed) | no | show filed Q4 (10-K note for FY<=2020, or nothing) with the reason "not filed separately" |

Rules:
- B1 same basis: pair FY and 9M from the same presentation vintage. Original pair = FY from the original 10-K + 9M from the original Q3 10-Q. Recast pair = FY as shown in a later 10-K + 9M as shown as the prior-year comparative in the next year's Q3 10-Q. Compute both when both exist. Equal = publish. Different = publish the latest-basis pair only if both its inputs come from the same later vintage; otherwise block with BASIS_CONFLICT. Never mix one original and one recast input (the 2026-10-17 census showed mixed vintages give a third, wrong answer).
- B2 class-B guard: block when the 10-K reports discontinued operations for the year (`...DiscontinuedOperation...` facts in the FY filing) and the 9M comes from a 10-Q filed before the disposal, unless a recast 9M exists.
- B3 calendar: windows come from the company's own fiscal calendar (FY start date and filed period ends), not fixed day-bands: a YTD fact is "cumulative" when it starts on the FY start date and ends on a filed quarter end; its quarter count comes from the order of period ends, not its length. Accept 12/12/12/16 and 16/12/12/12 calendars and 53-week years.
- B4 transition periods: if FY length is outside 350-380 days or the FY start does not equal the prior FY end + 1 day (fiscal-year change, 10-KT, push-down stub), do not derive; reason TRANSITION_PERIOD.
- B5 prefer filed: a filed discrete Q4 (10-K note) beats a derived one when they agree within rounding; when they disagree beyond rounding, neither is published and a finding is raised (the filed note can be wrong: SUN, SWK, CB, Ford).
- B6 lineage: store every input fact id (FY, 9M or Q1-Q3) and the formula id/version on the derived row; today only the FY filing is kept.
- B7 sign and scale: a derived class-A/B value whose sign is impossible for the concept (revenue < 0, capex outflow sign flipped) or that is more than 10x the company's median discrete quarter goes to quarantine, not publication. This is a screen, not proof.

## 7. How structure and identities detect a wrong derivation (non-circular checks)
"Q1 + Q2 + Q3 + Q4 = FY" proves nothing for a derived Q4 (true by construction). Use checks whose inputs are independent of the subtraction:
1. Filed-Q4 cross-check (FY2015-FY2020): compare derived FY - 9M with the 10-K note's own 3-month fact. FSDS shows such a fact for ~75% of top-1000 FY2015 10-Ks. Independent inputs (the note vs the 10-Q YTD).
2. Two-route check: FY - 9M YTD versus FY - (Q1 + Q2 + Q3 discrete income-statement quarters). They use different facts from different filings; disagreement beyond rounding = a basis or label error in one of them.
3. Cash identity with filed instants: derived Q4 (CFO + CFI + CFF + FX effect) must equal cash at FY end minus cash at Q3 end, both FILED balance-sheet instants. Cash definition is era-scoped: CCE (`CashAndCashEquivalentsPeriodIncreaseDecrease` era, before ASU 2016-18) vs cash including restricted cash (CCRC era). This catches CF basis mixing, which is the commonest Q4 cash-flow error.
4. Within-quarter statement identities on derived values: gross profit = revenue - cost of revenue; pre-tax - tax (+ equity method, discontinued ops) = net income including NCI; net income on the IS = net income starting line of the CF. Each side is derived from different tags, so a mixed-vintage input breaks the identity.
5. Calculation tree (FSN `cal.txt`, per filing): the filer's own parent-child weights tell which components sum to the derived total; useful to confirm perimeter of B-class concepts (data-team/22 CVX case).
6. Cross-filing consistency: the same quarter appears as a comparative in the next year's 10-Q (discrete IS quarters) and, before 2021, in the next 10-K's quarterly note. A derived Q4 that disagrees with a later filed comparative is a recast or an error; record it, do not overwrite silently.

## 8. Restatement and recast basis (history-specific)
- Two true values can exist for one period (as-filed and as-recast). The display series must name its basis; this report proposes "latest basis, pairs from one vintage" as the default for display and "as filed" retained for point-in-time use (role spec). Not decided: founder/accountant.
- The 2016-2018 standard wave (606, 2016-18, 2016-15, 2017-07, 2015-17) concentrates recasts of FY2016-FY2017 into FY2018 10-Ks. Expect `conflict_material` and `q4_not_derived` (conflicted inputs) to cluster in those years. NOT MEASURED: needs the DB split by year (section 10).
- Restatement signals to key on: 10-K/A and 10-Q/A (5 top-1000 10-K/A in 2016q1, 5 in 2019q1, 2 in 2022q1 FSDS buckets), 8-K Item 4.02, and an FY value that changes between consecutive 10-Ks. Sign-only conflicts stay quarantined (data-team doc on latest-filed rule).

## 9. Fiscal-year changes and predecessor CIKs
- Fiscal-year end changed across the four FSDS samples for 11 top-1000 CIKs: RGLD (0630 -> 1231), DY (0731 -> 0131), HRB (0430 -> 0630), VFC (1231 -> 0331), JEF (1231 -> 1130), ZWS (0331 -> 1231), GPN (0531 -> 1231), OSK (0930 -> 1231), LHX (0630 -> 1231), ELF (1231 -> 0331), SYM (1231 -> 0930). Each has a transition period (10-KT or a stub in the 10-K) that must get reason TRANSITION_PERIOD, and quarters around it cannot use the generic subtraction (rule B4). DATA-INFERRED (FSDS `fye`); samples miss changes between sampled quarters, so this is a floor.
- Predecessor candidates by same normalized name, different CIK, top-1000 CIK absent from 2016q1 and 2019q1: MRVL (1835632 <- 1058057), DIS (1744489 <- 1001039), STE (1757898 <- 1624899), BLK (2012383 <- 1364742), DKNG (1883685 <- 1772757), NE (1895262 <- 1458891), PNFP (2082866 <- 1115055), BAM (1937926 <- 1001085), CR (1944013 <- 25445), INGM (1897762 <- 1018003), SNDK (2023554 <- 1000180). Not all are predecessors: CR is a spin-off where the old CIK became another company (Crane NXT), SNDK's old CIK is the SanDisk acquired in 2016 (a different company), INGM's old CIK went private in 2016 (history gap 2016-2024), BAM is a split. A link must be FILING-CHECKED (successor-issuer 8-K12B/8-K12G3 or the 10-K's own predecessor statement) before history is joined. 161 top-1000 CIKs had no filing in the 2016q1 or 2019q1 samples; most are later IPOs/spins and get reason "not yet public/registered {date}".
- Push-down/predecessor-successor stubs inside one CIK (SUN 2014: 8 months predecessor + 4 months successor) are a third case: the fiscal year has no 12-month value; reason PREDECESSOR_STUB, never summed.

## 10. Order of work and expected cells
Expected gains are bounded by measured gap counts; none is a forecast. The DB split that would turn these bounds into numbers was NOT_RUN.

| Step | Work | Owner | Gain bound (top-1000, 2015+) | Gate |
|---|---|---|---|---|
| 0 | Run the by-year x cause x concept split of `period_gap` for the top 1,000 (query text in section 11; 4 chunks, 20 s timeout) | Data Engineer / me when the pooler is free | measurement only | pooler <= 14 |
| 1 | Filed-Q4 audit for FY2015-FY2020: how many `q4_not_derived` cells in those years have a 3-month 10-K note fact for the same tag in `core.fact` (authoritative or not). If present but non-authoritative, it is a label/conflict issue; publish only through rule B5 | Period Engineer + Verifier | up to the FY2015-FY2020 share of 5,801 q4 cells; also gives filed Q4 EPS for those years | Verifier sample of 20 incl. SUN, MPLX |
| 2 | Calendar-aware windows (rule B3, B4) in `derived.py` + additive allowlist (section 6) + full input lineage (B6) | Period Engineer (code) | Costco-type calendars and allowlist hygiene; count after step 0 | dry-run table, negative fixtures (12/12/12/16, 53-week, transition, stub) |
| 3 | Same-vintage pairing (B1/B2) for conflicted 9M/FY inputs | Period Engineer + resolver owner | the conflict share (census: ~65%) of 5,801 q4 + part of 5,345 quarter cells | identity checks 2-4 in section 7 pass on the dry-run; Verifier sample zero wrong |
| 4 | Era-scoped revenue/cost tags (section 3 rule) for FY2015-FY2017, company-period scoped, validated on the 606 overlap year | Tag Mapper + Standardization Lead | about 134 top-1000 filers x FY2015-FY2017 (FY + quarters) for revenue; cost: CostOfServices 87 filers | full coexistence check; TAP excise trap fixture |
| 5 | 2024 interest tags decision (`InterestExpenseNonoperating`/`Operating`) | Tag Mapper + Standardization Lead | current periods for up to ~363 filers | file 31 I-2 finding resolved |
| 6 | Reason codes for structural history: not_applicable_before_adoption (842/CECL/LDTI), TRANSITION_PERIOD, PREDECESSOR_STUB, history_at_predecessor_cik, not_yet_public | Data Engineer (I11) | converts unexplained blanks to explained; no values | Verifier sample per code |
| 7 | Predecessor CIK links, filing-checked | Company Master + Verifier | MRVL, DIS, STE, BLK, DKNG, NE, PNFP, ... history before re-registration | 8-K12B or 10-K statement per link |
| 8 | Cash identity (section 7.3) and two-route check added to `scrooner-certify` as invariants over derived quarters | Data Engineer | detection, not cells | none |

## 11. Commands actually run (all read-only)
- `cat`/`sed`/`grep` reads of data-team 20, 21, 22, 14, 34, 03, strategy 38, 39, tag cards revenue/interest/cash, `normalizer/derived.py`, `normalizer/periods.py`, `sanity/period_completeness.py`, migrations 0083, 0090, 0038, mapper `concepts.py`/`expanded_concepts.py`; `git log` on derived.py and period_completeness.py; `git diff` derived.py (uncommitted per-share guard, owned by another session).
- `python3 mind/mind.py search` ("Q4 derivation", "era tag SalesRevenueNet", "period_gap cause").
- `psql ... select count(*) from pg_stat_activity` (results 21, 20, 17, 18, 18 and 17-19 in a 22-minute poll); the period_gap query file `q_pg.sql` was prepared but never executed.
- FSDS fetches by HTTP range with the declared SEC User-Agent (curl, <= 2 req/s): 2016q1, 2019q1, 2022q1 sub/tag/pre (28.5 + 28.3 + 29.3 MB) and num for 2016q1 and 2022q1 streamed through a filter (82.6 + 89.2 MB): 257.9 MB total, under the 300 MB cap. SEC Release 33-10890 PDF (1.4 MB). SEC R-pages: SUN R105, KO R2, Costco R7 and FilingSummary.xml for SUN.
- Scratchpad scripts (python3 -I): `rangezip.py`, `era_tags.py`, `era_scan.py`, `q4_note.py`, `calendar_scan.py`, plus inline checks. Downloaded data deleted after the run.

## 12. Not verified / risks / what would change the conclusions
- No DB numbers: whether KO/PFE/JNJ/MRK FY2015 revenue is already filled by `revenue_resolvers` or a company tag preference is unknown; if it is, step 4's gain shrinks. Whether filed Q4 note facts are already authoritative in `core.fact` for 2015-2020 is unknown; if they are, step 1 is mostly a validation step.
- FSDS 2025q4 is mostly 10-Qs; the 2025 column is not an FY sample. FSDS face-statement presence is not value coverage.
- The 2016-2018 recast clustering of conflicts is ASSUMED until the by-year split runs.
- Era dates for 2016-18/2016-15/2017-07/LDTI are from FSDS shape and general knowledge, not rule text (ASSUMED); 606/842/CECL cases are filing-checked in data-team/22; Item 302 is filing-checked.
- What would change my mind: if the by-year split shows `q4_not_derived` evenly spread over 2015-2025 (not concentrated after FY2020), the filed-note route is weaker than stated; if `no_mapped_tag` revenue cells are not concentrated in FY2015-FY2017, the era-tag route is not the lever and the gap is sector-shaped.
