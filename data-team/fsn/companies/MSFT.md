# MSFT: Microsoft Corporation (CIK 789019)

Dossier by the FSN expert, 2026-11-02. Labels:
- **FC (FILING-CHECKED)**: the R page on sec.gov was opened.
- **DI (DATA-INFERRED)**: read from FSN rows (as filed by MSFT) or our tables.
- **TXT**: quoted from MSFT's own text block in FSN `txt`. That is the filer's text, but not a rendered page.

Source: FSN extracts of all 76 sets. MSFT has 65 periodic filings (2009-10 to 2026-07), **52 in scope from the FY2014 Q2 10-Q onward** (0001193125-14-018634 … 0001193125-26-323660). There are no amendments (no 10-K/A or 10-Q/A in FSN).

Tools: the scratchpad scripts `company.py`, `catalog.py`, `series.py` and `calcheck.py`. Their output is reproduced here where it matters.

## 1. Profile
| Item | Value | Evidence |
|---|---|---|
| Sector / template | General operating company (SIC 7372). No sector overlay | DI (sub.sic) |
| Fiscal year | ends **June 30** (`fye` 0630), calendar month ends, no 52/53-week issue. `sub.fy` = the year the FY ends (FY2026 = July 2025–June 2026) | DI (all 65 sub rows) |
| Co-registrants | none (nciks 1 in every filing) | DI |
| Predecessors | none; a single CIK since 2009 | DI |
| Filer agent | 0001193125 (Donnelley) until Q1 FY2017 → 0001564590 (to Q2 FY2023) → 0000950170 (Q3 FY2023 to FY2025) → 0001193125 again from Q1 FY2026 | DI (adsh prefixes) |
| Calc data | full cal in every in-scope filing **except** the FY2024 10-K 0000950170-24-087843 and the Q1 FY2025 10-Q 0000950170-24-118967 (no cal rows in FSN) | DI |
| Segments | to FY2015: Devices and Consumer / Commercial (not studied). **From Q1 FY2016** (0001193125-15-350718): Productivity and Business Processes, Intelligent Cloud, More Personal Computing, with prior periods recast. Further recasts of segment content in Q1 FY2023, Q1 FY2024 and Q1 FY2025 ("recast certain prior period amounts to conform to the way we internally manage") | TXT (SegmentReportingDisclosureTextBlock) |
| Statements per filing | IS, CI, BS, BS (Parenthetical), CF, EQ; CI (Parenthetical) to FY2017 | DI (ren) |
| Quarterly cash flows | **every 10-Q prints 3-month and YTD CF columns** (Q2: qtrs 1 and 2; Q3: qtrs 1 and 3), FY2014–FY2026. Only Q4 CF needs FY − 9M | DI; FC (0001193125-26-027207 R6) |
| Q4 income statement | printed as 3-month values in the 10-K quarterly note **FY2011 to FY2020** (NI, revenue, GP, EPS). **Not printed from FY2021** (first 10-K without it: 0001564590-21-039151) | DI (num qtrs=1 at the FY-end ddate in each 10-K) |

## 2. Lines we care about, per era
Line numbers are the `pre.line` of the main report. "n" = in-scope filings carrying the line. The same tag is used throughout unless an era change is shown. All tags are us-gaap unless marked **custom** (msft).

### Income statement (R2)
| Line | Tag | Printed label | Calc parent (weight) | Era (first … last accession) |
|---|---|---|---|---|
| Revenue (total) | `SalesRevenueNet` | "Revenue"; "Total revenue" from FY2016 10-K | GrossProfit (+1) | … to Q3 FY2018 0001564590-18-009307 |
| | `RevenueFromContractWithCustomerExcludingAssessedTax` | "Revenue" (total, dimn 0) | GrossProfit (+1) | FY2018 10-K 0001564590-18-019062 … FY2026 10-K |
| Revenue components | `SalesRevenueGoodsNet` "Product"; **custom** `SalesRevenueServicesAndOtherNet` "Service and other" | | SalesRevenueNet (+1) | FY2016 10-K 0001193125-16-662209 … Q3 FY2018 |
| | the same total tag on `ProductOrServiceAxis` = ProductMember / ServiceOtherMember (**dimensional face rows**) | "Product", "Service and Other" | — | FY2018 10-K … now |
| Cost of revenue | `CostOfRevenue` → `CostOfGoodsAndServicesSold` | "Cost of revenue" / "Total cost of revenue" | GrossProfit (−1) | switch at FY2018 10-K, same as revenue. Components `CostOfGoodsSold` + **custom** `CostOfServicesAndOther` FY2016 10-K … Q3 FY2018 |
| Gross profit | `GrossProfit` | "Gross margin" | OperatingIncomeLoss (+1) | all |
| R&D, S&M, G&A | `ResearchAndDevelopmentExpense`, `SellingAndMarketingExpense`, `GeneralAndAdministrativeExpense` | | OperatingIncomeLoss (−1) | all |
| Impairment/restructuring | `GoodwillImpairmentLoss` (FY2014 10-K only), `BusinessCombinationIntegrationRelatedCosts` (FY2014–Q3 FY2015), **custom** `ImpairmentIntegrationAndRestructuringExpenses` (FY2015 10-K … FY2017 10-K), **custom** `ImpairmentAndRestructuringExpenses` (FY2018 10-K), `RestructuringCharges` (FY2019 10-K) | | OperatingIncomeLoss (−1) | short-lived lines. The FY2014 10-K line carries FY2012's goodwill impairment 6,193 in its third column; the custom line holds FY2015's 10,011 (DI) |
| Operating income | `OperatingIncomeLoss` | "Operating income" | pretax (+1) | all |
| Other income | `NonoperatingIncomeExpense` | "Other income (expense), net" (4 label variants) | pretax (+1) | all. **Interest expense is inside this line**; see §4 |
| Pretax | `IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments` | "Income before income taxes" | NetIncomeLoss (+1) | … to Q1 FY2022 0001564590-21-051992 |
| | `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` | same label | NetIncomeLoss (+1) | Q2 FY2022 0001564590-22-002324 … now. **Tag switch with no change in meaning** |
| Tax | `IncomeTaxExpenseBenefit` | "Provision for income taxes" | NetIncomeLoss (−1) | all |
| Net income (= attributable; no NCI) | `NetIncomeLoss` | "Net income"; "Net income (loss)" from Q2 FY2018 | CFO (+1), CI (+1) | all |
| EPS basic / diluted | `EarningsPerShareBasic` / `EarningsPerShareDiluted` | "Basic" / "Diluted" | — | all; uom USD |
| Weighted shares | `WeightedAverageNumberOfSharesOutstandingBasic` / `WeightedAverageNumberOfDilutedSharesOutstanding` | | basic → diluted (+1), with an incomplete tree (the dilutive effect is a note fact) | all |
| DPS declared | `CommonStockDividendsPerShareDeclared` | "Cash dividends declared per common share" | — | **face only to Q1 FY2019** 0001564590-18-024893; afterwards in the notes/EQ |

FY2026 10-K R2 (FC, 0001193125-26-323660): revenue 331,839; COR 106,374; GP 225,465; OI 155,237; other income 10,697; pretax 165,934; tax 32,185; NI 133,749; EPS 18.00 / 17.95; shares 7,429 / 7,453 (millions). All equal FSN num.

### Balance sheet (R4)
| Line | Tag | Label | Era |
|---|---|---|---|
| Cash and equivalents | `CashAndCashEquivalentsAtCarryingValue` | "Cash and cash equivalents" | all |
| Short-term investments | `AvailableForSaleSecuritiesCurrent` → `ShortTermInvestments` | | switch at Q1 FY2019 0001564590-18-024893 (ASU 2016-01) |
| Cash + ST investments | `CashCashEquivalentsAndShortTermInvestments` | "Total cash, cash equivalents, and short-term investments" | all; a subtotal, **not cash** |
| Current assets / liabilities | `AssetsCurrent` / `LiabilitiesCurrent` | | all |
| Short-term debt | `ShortTermBorrowings` "Short-term debt" | | … to the FY2018 10-K (FY2018 value 0) |
| | `CommercialPaper` "**Short-term debt**" | | Q1 FY2024 0000950170-23-054855 … FY2025 10-K (FY2024 6,693; FY2025 0); absent from FY2026 filings |
| Current LTD | `LongTermDebtCurrent` "Current portion of long-term debt" | | all |
| Long-term debt | `LongTermDebtNoncurrent` "Long-term debt" | | all |
| Finance leases | **not on the face.** In "Other current liabilities" and "Other long-term liabilities" (TXT: LesseeLeasesPolicyTextBlock, 0001564590-17-020171). Note total `FinanceLeaseLiability` | | from Q1 FY2018 (ASC 842 early adoption) |
| Operating lease liabilities | `OperatingLeaseLiabilityNoncurrent` "Operating lease liabilities" (current part inside other current liabilities); ROU asset `OperatingLeaseRightOfUseAsset` | | from Q1 FY2018 |
| Unearned revenue | `DeferredRevenueCurrent/Noncurrent` → `ContractWithCustomerLiabilityCurrent/Noncurrent` | | switch at the FY2018 10-K |
| Deferred taxes | `DeferredTaxAssetsLiabilitiesNetCurrent` (to Q3 FY2016), `DeferredTaxLiabilitiesNoncurrent` → `DeferredIncomeTaxLiabilitiesNet` (Q1 FY2020) | | |
| Totals | `Assets`, `Liabilities`, `StockholdersEquity`, `LiabilitiesAndStockholdersEquity` | | all; no NCI, no temporary equity |
| Equity components | `CommonStocksIncludingAdditionalPaidInCapital`, `RetainedEarningsAccumulatedDeficit`, `AccumulatedOtherComprehensiveIncomeLossNetOfTax` | | all |

FY2026 10-K R4 (FC): debt = current portion 9,227 + long-term 31,067 = 40,294; no short-term debt line. FY2024 10-K R4 (FC, 0000950170-24-087843): **Short-term debt 6,693** + current portion 2,249 + long-term 42,688 = **51,630**.

### Cash flow statement (R6)
| Line | Tag | Label | Era |
|---|---|---|---|
| CFO | `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations` | "Net cash from operations" | Q2 FY2014 … Q1 FY2018 0001564590-17-020171 |
| | `NetCashProvidedByUsedInOperatingActivities` | same | Q2 FY2018 … now (and before 2014) |
| CFI / CFF | same pattern (`…ContinuingOperations` in the same era) | | |
| D&A | **custom `DepreciationAmortizationAndOther`** "Depreciation, amortization, and other" | | all. **Combined line** (D&A plus "other"); composition changed in FY2026, see §3 |
| SBC | `AllocatedShareBasedCompensationExpense` → `ShareBasedCompensation` | "Stock-based compensation expense" | switch at the FY2017 10-K |
| Gains/losses | **custom `GainLossOnInvestmentsAndDerivativeInstruments`** "Net recognized losses (gains) on investments and derivatives" | | all; **stored as a gain (credit); printed negated** (FC: stored −2,136, printed 2,136, 0001193125-26-027207 R6) |
| Deferred tax | `DeferredIncomeTaxExpenseBenefit` → `DeferredIncomeTaxesAndTaxCredits` | "Deferred income taxes" | switch at Q3 FY2026 0001193125-26-191507 |
| Capex | `PaymentsToAcquirePropertyPlantAndEquipment` | "Additions to property and equipment" | **all 54 filings**; the only capex line. Finance-lease additions are non-cash (not on the CF) |
| Acquisitions | **custom** `AcquisitionsNetOfCashAcquiredAndPurchasesOfIntangibleAndOtherAssets` (two spellings: `…Netof…Intangibleand…` to Q1 FY2017) | | |
| Dividends paid | `PaymentsOfDividendsCommonStock` | "Common stock cash dividends paid" | all |
| Buybacks | `PaymentsForRepurchaseOfCommonStock` | "Common stock repurchased" | all |
| Debt flows | `ProceedsFromDebtMaturingInMoreThanThreeMonths`, `RepaymentsOfDebtMaturingInMoreThanThreeMonths`, `ProceedsFromRepaymentsOfShortTermDebtMaturingInThreeMonthsOrLess`; 2023/2026 one-off tags `ProceedsFromShortTermDebtMaturingInThreeMonthsOrLess`, `RepaymentsOfShortTermDebtMaturingInThreeMonthsOrLess` | | |
| FX effect | `EffectOfExchangeRateOnCashAndCashEquivalents` | | … to Q3 FY2022 0001564590-22-015675 |
| | **`EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations`** | "Effect of foreign exchange rates on cash and cash equivalents" | FY2022 10-K 0001564590-22-026876 … now |
| Net change in cash | `CashAndCashEquivalentsPeriodIncreaseDecrease` → `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect` | "Net change in cash and cash equivalents" | switch at Q1 FY2020 0001564590-19-037549 (ASU 2016-18); the label still says plain cash |
| Opening/closing cash | `CashAndCashEquivalentsAtCarryingValue` → `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` | | same switch; equals BS cash (MSFT has no material restricted cash) |

### Comprehensive income and equity
CI (R3): NetIncomeLoss → OCI components → `OtherComprehensiveIncomeLossNetOfTax` (to the FY2016 10-K) / `…PortionAttributableToParent` (from Q1 FY2017) → `ComprehensiveIncomeNetOfTax`.

EQ (R7): fully on `StatementEquityComponentsAxis`. It **prints restated opening balances**: the FY2018 10-K equity statement gives StockholdersEquity at 2016-06-30 = **83,090** (ASC 606 restated), while every balance sheet that printed that date gave 71,997.

## 3. Restatements and recasts (each changes a printed prior period)
Each row lists the filing that first prints the new basis and what changed. Values are in millions. "TXT" means MSFT's own explanation in that filing.

**R1. FY2015 10-Qs and 10-K (0001193125-15-020351, -15-144151, -15-272806): cost reclassified from G&A into cost of revenue.**
- Q2 FY2014: COR 8,284 → 8,322 and G&A 1,235 → 1,197 (equal and opposite, 38).
- FY2014: COR 26,934 → 27,078 and G&A 4,821 → 4,677.
- Gross profit falls by the same amount; OI and NI are unchanged.
- TXT: "We have recast certain prior period amounts to conform to the current period presentation, with no impact on consolidated net income or cash flows" (0001193125-15-272806). Which costs moved is DI.

**R2. Q1 FY2016 (0001193125-15-350718): new segments**, with prior periods recast (TXT). Segment-level only; no face change.

**R3. Q3 FY2016 (0001193125-16-550254): ASU 2016-09 (share-based payment) early-adopted, effective July 1, 2015.**
- Q1 FY2016: tax 893 → 611; NI 4,620 → 4,902; diluted EPS 0.57 → 0.61.
- Q2 FY2016: tax 857 → 837; NI 4,998 → 5,018.
- Diluted shares changed.
- Cash flows: excess tax benefits moved from financing to operations for all periods: 9M FY2015 CFO 22,264 → 22,819.
- TXT gives the "As reported / As adjusted" table, matching FSN exactly.

**R4. FY2016 10-K (0001193125-16-662209): ASU 2015-17 (all deferred taxes noncurrent), early-adopted and applied retrospectively.**
- 2015-06-30: assets 176,223 → 174,472; current assets 124,712 → 122,797; deferred tax liabilities noncurrent 2,835 → 1,295 (TXT).
- The same 10-K also recasts FY2014/FY2015 CFO: FY2015 29,080 → 29,668 (the ASU 2016-09 cash-flow presentation of R3).

**R5. Q1 FY2017 (0001193125-16-742796): debt issuance costs netted from debt** (ASU 2015-03 pattern).
- 2016-06-30: long-term debt 40,783 → 40,557; other long-term assets 3,642 → 3,416; assets 193,694 → 193,468.
- DI: equal amounts, 226; the text was not located.

**R6. Q1 FY2018 (0001564590-17-020171) through the FY2019 10-K: ASC 606 (full retrospective) and ASC 842 (leases), both early-adopted July 1, 2017. This is the big one.**
- FY2016 revenue 85,320 → 91,154; NI 16,798 → 20,539; diluted EPS 2.10 → 2.56.
- FY2017 revenue 89,950 → 96,571; NI 21,204 → 25,489; diluted EPS 2.71 → 3.25.
- Q1 FY2017 revenue 20,453 → 21,928 (FC: 0001564590-17-020171 R2); NI 4,690 → 5,667; EPS 0.60 → 0.72.
- 2017-06-30 balance sheet: equity 72,394 → 87,711; unearned revenue current 34,102 → 24,013.
- TXT: "We elected to early adopt the standard effective July 1, 2017, using the full retrospective method, which required us to restate each prior reporting period presented."
- Basis gap: **the FY2016 quarters were never restated.** FY2016 annual values are on the ASC 606 basis, but its four quarters are legacy basis: the legacy quarters sum to NI 16,798, while the restated year is 20,539.
- The restated FY2016 values are printed only in the FY2018 10-K (FY2016 column).

**R7. Q2 FY2018 (0001564590-18-001129) and Q3 FY2018 (-18-009307): TCJA recast of tax liabilities**, and securities lending payable folded into other current liabilities. `DepositsReceivedForSecuritiesLoanedAtCarryingValue` leaves the face after Q2 FY2018 (TXT).

**R8. Q1 FY2019 (0001564590-18-024893): ASU 2016-01 (financial instruments).**
- Investments recast; `AvailableForSaleSecuritiesCurrent` → `ShortTermInvestments`.
- Two CF working-capital lines for Q1 FY2018 restated (other current liabilities −1,962 → −2,164; other long-term liabilities 813 → 354) (TXT).

**R9. Q2 FY2026 (0001193125-26-027207), Q3 FY2026 (-26-191507), FY2026 10-K (-26-323660): CF recast between two custom adjustment lines.**
- Moved from "Depreciation, amortization, and other" into "Net recognized losses (gains) on investments and derivatives":

| FY2025 period | "Depreciation, amortization, and other", first filed → recast |
|---|---|
| Q2 (3 months) | 6,827 → 5,667 |
| 6 months | 14,210 → 12,383 |
| 9 months | 22,950 → 20,116 |
| Full year | 34,153 → 29,433 |

- FY2024: 22,287 → 20,958.
- CFO is unchanged. TXT: "We have recast certain prior period amounts on our consolidated cash flows statements … no impact on … net cash from (used in) operations, investing, or financing" (FC: R6 of 0001193125-26-027207 prints the recast 5,667 and 2,136).
- DI (not stated by MSFT): the timing matches the October 2025 OpenAI recapitalisation; equity-method results appear to have moved into the investments line.
- **Any D&A series built on this custom line breaks here.**

## 4. Lines MSFT does not present, and combined lines
| Concept | What MSFT prints | Consequence |
|---|---|---|
| Interest expense | **not on the face**; it sits inside "Other income (expense), net". Note fact `InterestExpense` FY2014–FY2024 10-K (FY2024 2,935), then **`InterestExpenseNonoperating` from the Q1 FY2025 10-Q 0000950170-24-118967** (FY2025 2,385, FY2026 3,051) | face = `line_not_presented`; a note-sourced value needs the 2024-taxonomy tag |
| D&A | only the combined custom line "Depreciation, amortization, and other"; notes give rounded `Depreciation` (FY2026 34.3B, 0.1B precision) and `AmortizationOfIntangibleAssets` | `combined`, never D&A; EBITDA from the CF is not computable without a definition decision |
| Finance lease liabilities | inside other current and long-term liabilities; note total `FinanceLeaseLiability` (FY2026 66,594; FY2024 27,145) | debt **including** finance leases needs the note value; the face gives debt excluding leases |
| Gross profit | printed ("Gross margin") | — |
| NCI / preferred | none | NI = NI attributable |
| Q4 income statement | printed in the 10-K note to FY2020, absent from FY2021 | Q4 EPS: printed FY2014–FY2020 (diluted 0.55, −0.40, 0.39, 0.83, 1.14, 1.71, 1.46); `not_filed_separately` from FY2021 |

## 5. Quirks and filer issues
- **Missing cal:** FY2024 10-K 0000950170-24-087843 and Q1 FY2025 10-Q 0000950170-24-118967 have no cal rows in FSN, so calc-based mapping fails for exactly these two filings. The earlier mind entry says the MSFT 2024+ calc is embedded in the .xsd; FSN has it again from Q2 FY2025.
- **Negated custom line:** `GainLossOnInvestmentsAndDerivativeInstruments` is a gain that prints negated (§2 CF).
- **Pretax tag switch** at Q2 FY2022, with no change in meaning.
- **One label, two tags:** "Short-term debt" is `ShortTermBorrowings` to FY2018 and `CommercialPaper` from FY2024.
- **No `menucat S` reports** for the Q1 FY2014 10-Q 0001193125-13-409855 (pre-scope).
- **Instant at the FY2016 year end:** two vintages, the legacy BS 71,997 and the ASC 606 EQ statement 83,090.

## 6. What Scrooner must do for MSFT
1. **Revenue / COR:** map the **total** only.
   - FY2016 10-K … Q3 FY2018: `SalesRevenueNet` / `CostOfRevenue`. Never `SalesRevenueGoodsNet` or `CostOfGoodsSold`; they are its calc children "Product".
   - FY2018 10-K on: RCFC / `CostOfGoodsAndServicesSold` at dimn 0.
2. **Pretax:** both tags (era switch at 0001564590-22-002324).
3. **CFO / CFI / CFF:** both tag families; `…ContinuingOperations` for Q2 FY2014–Q1 FY2018.
4. **Cash identity:** recognise the FX tag `…IncludingDisposalGroupAndDiscontinuedOperations`; without it every CF column from the FY2022 10-K fails.
5. **Capex:** `PaymentsToAcquirePropertyPlantAndEquipment`, all periods.
6. **Cash:** `CashAndCashEquivalentsAtCarryingValue` (BS).
7. **Total debt (face, excl. leases):** `ShortTermBorrowings` | `CommercialPaper` + `LongTermDebtCurrent` + `LongTermDebtNoncurrent`.
   - FY values 2014–2026: 22,645 / 35,292 / 53,461 / 86,194 / 76,240 / 72,178 / 63,327 / 58,146 / 49,781 / 47,237 / **51,630** / 43,151 / 40,294.
   - Including finance leases: add `FinanceLeaseLiability` (note) from FY2018, as a separate, labelled component.
8. **Interest expense:** face blank `line_not_presented` (inside other income). If note values are allowed: `InterestExpense` to FY2024, `InterestExpenseNonoperating` from Q1 FY2025.
9. **D&A:** `combined` (custom "Depreciation, amortization, and other"); never map it as D&A. Flag the R9 composition break if anyone uses it.
10. **EPS:** printed only. Q4 FY2014–FY2020 from the 10-K quarterly note (printed, not derived); Q4 FY2021+ `not_filed_separately`.
11. **Q4 flows:** FY2014–FY2020 printed in the 10-K note (route a). FY2021+ FY − 9M; the SAME_BASIS witness holds (each 10-K reprints the prior years).
12. **FY2016:** annual values from the FY2018 10-K (ASC 606) do not equal the sum of the FY2016 quarters (legacy). Do not derive Q4 FY2016 from the ASC 606 FY minus the legacy 9M; that is exactly the mixed-vintage case.
13. **Instants on the EQ statement:** decide whether a restated EQ-statement opening balance (2016-06-30 equity 83,090) outranks the balance-sheet print (71,997). Proposal P-6.

## 7. Comparison with our store (2026-11-02)
Sources:
- production `analytics.canonical_fact` (company_id 4), read-only;
- the FSN pilot artifact from run 41490670432 (branch work/engineering/fsn-pilot, 74a5f5a; `cells/*/cells.jsonl.gz`, `gaps.csv`, `report.json`);
- `fsn.*` in Supabase: empty (0 company_load rows).

### Production canonical_fact, FY and FY-end instants
| Concept | Finding | Evidence |
|---|---|---|
| revenue, net_income, operating_income, capex, dividends_paid, share_buybacks, cash_and_equivalents | **agree** with the FSN latest print, FY2014–FY2026 | §6 series |
| **total_debt FY2016** | prod **12,904** = short-term debt only; face total **53,461** | FY2017 10-K BS |
| **total_debt FY2024** | prod **44,937** misses the "Short-term debt" `CommercialPaper` 6,693; face total **51,630** | FC 0000950170-24-087843 R4 |
| total_debt FY2014 / 2015 / 2017 / 2018 | prod 22,600 / 35,285 / 86,172 / 76,200 vs face 22,645 / 35,292 / 86,194 / 76,240. Prod looks like a note figure (rounded or principal) | DI |
| total_debt FY2019 | prod missing; face 72,178 | |
| **interest_expense FY2025, FY2026** | prod missing (stops at 2024-06-30); MSFT switched to `InterestExpenseNonoperating` (2,385 / 3,051) | DI |
| diluted_eps, income_before_tax FY2016, FY2017 | prod missing; FSN latest print 2.56 / 3.25 and 25,639 / 29,901 (first print 2.10 / 2.71) | |
| cfo FY2014, FY2015 | prod missing; FSN 32,502 / 29,668 (latest; first 32,231 / 29,080) | |
| depreciation_and_amortization | prod has no FY rows: consistent with the combined line | |

### FSN pilot (run 41490670432)
- MSFT: 1,214 template keys, 795 valued (65.5%), 154 reasoned, 265 gaps.
- **195 of 196 FY/instant values agree with my FSN series.**

| Pilot cell(s) | Pilot says | Should be | Root cause |
|---|---|---|---|
| stockholders_equity 2016-06-30 | 71,997 (FY2017 10-K BS) | 83,090 is the latest print (FY2018 10-K equity statement, ASC 606) **or** 71,997 by a BS-only rule: a policy gap | instants are read from BS columns only; P-6 |
| cfo / dividends_paid / share_buybacks FY2020–FY2026 and quarters FY2022+ (22 each) | defect `latest_copy_fails_identity` | values; the CF ties when FX is included (FY2025: 11,864 + 63 = 11,927) | `fsn_store/checks.py` `CF_FX` lacks the `…IncludingDisposalGroupAndDiscontinuedOperations` FX tag (CODE-CHECKED, origin/main). P-1 |
| revenue / cost_of_revenue FY2014–FY2017 (10 each) | defect `conflicting_values_in_filing`, e.g. (72,948, 86,833) for FY2014 | 86,833 (`SalesRevenueNet`) | the std_tag rule takes `SalesRevenueGoodsNet` ("Product", a calc child) as a revenue total. P-2 |
| depreciation_and_amortization, all 50 | defect `conflicting_values_in_filing`, e.g. (−5,329, 29,433) for FY2025 | `combined` / `line_presented_combined_with_others` | two custom CF adjustments land in the D&A slot (custom calc-position rule too loose), and the D&A line is itself combined. P-3 |
| capex (59) | `no_mapped_line` | values: `PaymentsToAcquirePropertyPlantAndEquipment` in 54 of 54 filings; prod agrees | no capex concept_rule in the pilot (the pilot reports capex as not G2-eligible). P-4 |
| cash_and_equivalents (47) | `no_concept_rule` | values (prod agrees) | missing rule. P-4 |
| total_debt (47) | `no_mapped_line` | the face sum (§6.7) | missing rule incl. `CommercialPaper`. P-4 |
| interest_expense (59) | `no_mapped_line` | `line_not_presented` (or a note value) | reason class. P-5 |
| diluted/basic EPS Q4 FY2014–FY2020 (7 each) | `not_presented / not_filed_separately` | printed in the 10-K quarterly note (e.g. FY2019 Q4 diluted 1.71) | note-sourced Q4 (design §4 route a) not used for per-share. P-7 |
| net_income etc. Q4 FY2014–FY2020 | `derived` (YTD4 − YTD3), values equal the printed note values | printed (route a) | derivation chosen over a print. P-7 |
