# Card family: Revenue (written 2026-10-19 by the Tag Expert)

Tags: `us-gaap:Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax` (RCFC), `RevenueFromContractWithCustomerIncludingAssessedTax`, `SalesRevenueNet`, `SalesRevenueGoodsNet`, `SalesRevenueServicesNet`, `InterestAndDividendIncomeOperating` (IADIO), `InterestIncomeOperating`, `RevenuesNetOfInterestExpense` (RNIE), plus the sector totals met in filings: `RegulatedAndUnregulatedOperatingRevenue`, `GrossInvestmentIncomeOperating`, `PremiumsEarnedNet`.

## Method and limits (read first)
- Taxonomy text and period/balance types: read 2026-10-19 from `https://xbrl.fasb.org/us-gaap/2025/elts/us-gaap-doc-2025.xml` and `us-gaap-2025.xsd` (HTTP 200, no 403). dei text came from the definition blocks embedded in a filing R-file (the dei doc URL returned 404).
- Counts below are SEC XBRL Frames (`data.sec.gov/api/xbrl/frames`, CY2013 and CY2023, one value per filer per calendar period). Scope: ALL SEC filers that filed that tag, not our active population, and not split by SIC. **"bank-like" = the same filer also files `NoninterestExpense` in the same frame** (a proxy; SIC 6000-6199 over-counts banks, see inbox). Evidence class for every count: DATA-INFERRED.
- DB reads (`analytics.sec_tag_library`, `company_sec_tag`, SIC split) were SKIPPED: `pg_stat_activity` showed 14-18 connections, above the 12 limit, on every attempt during this run. File 31 reports library counts as read 2026-10-19 (DATA-INFERRED): none for the revenue tags.
- Filing evidence: R-files opened by me this run are marked "me"; bank R-files from the Verifier's cache (data-team/32) are marked [32].

## 1. Official meaning (taxonomy 2025)
| Tag | Period / balance | Definition (shortened) | Status |
|---|---|---|---|
| Revenues | duration / credit | Revenue from goods sold, services rendered, insurance premiums or other earning activities. "Includes ... investment and interest income **before deduction of interest expense** when recognized as a component of revenue, and sales and trading gain (loss)." | current |
| RevenueFromContractWithCustomerExcludingAssessedTax | duration / credit | Revenue from satisfying a performance obligation (ASC 606), excluding sales/use/VAT/excise collected from the customer | current; exists only from the ASC 606 era (no CY2013 frame, 404) |
| RevenueFromContractWithCustomerIncludingAssessedTax | duration / credit | Same, including the tax | current; CY2013 frame 404 |
| SalesRevenueNet / SalesRevenueGoodsNet / SalesRevenueServicesNet | duration / credit | Pre-ASC 606 sales lines | **absent from the 2021, 2024 and 2025 taxonomy files** (present in 2017, 2019, 2020 files; the 2018 file check was inconclusive). No CY2023 frame (404). |
| InterestAndDividendIncomeOperating | duration / credit | Total interest and dividend income earned from loans/leases, securities, fed funds, repos, CDs, dividends and other investments | current |
| InterestIncomeOperating | duration / credit | "Operating interest income, including amortization and accretion of premiums and discounts" | current |
| RevenuesNetOfInterestExpense | duration / credit | Same words as Revenues but "investment and interest income **after** deduction of interest expense" | current |
| RegulatedAndUnregulatedOperatingRevenue | duration / credit | "Total amount of operating revenues recognized during the period" (utilities) | current |
| GrossInvestmentIncomeOperating | duration / credit | Income from securities and real estate before investment expense, excludes realized gains | current |
| PremiumsEarnedNet | duration / credit | Premiums earned after cessions and assumptions | current |

## 2. Who reports it (Frames, all SEC filers, DATA-INFERRED)
| Tag | CY2013 filers (bank-like) | CY2023 filers (bank-like) |
|---|---|---|
| Revenues | 3,751 (62) | 2,679 (74) |
| RCFC | n/a (tag did not exist) | 3,142 (85) |
| RCFC including tax | n/a | 781 (37) |
| SalesRevenueNet | 2,271 (1) | n/a (retired) |
| SalesRevenueGoodsNet / ServicesNet | 1,275 (1) / 834 (0) | n/a |
| InterestAndDividendIncomeOperating | 708 (576) | 479 (388) |
| InterestIncomeOperating | 304 (52) | 334 (54) |
| RevenuesNetOfInterestExpense | 28 (10) | 64 (25) |

Era effect (ASC 606, 2018 for public companies): the same company moves between tags. 2023: 796 filers carry BOTH Revenues and RCFC, 2,346 only RCFC, 1,883 only Revenues; 5,344 distinct filers carry at least one of the three. 2013: 568 carry both Revenues and SalesRevenueNet; 5,454 carry at least one. **No single revenue tag covers more than 59% of filers in either era.**
Revenue tags among bank-like filers in 2023: Revenues 74, RCFC 85, RNIE 25 of 443 bank-like filers; most banks present no total revenue line at all (see section 3).
SIC-family split (banks/insurers/REITs/utilities/energy/pharma): NOT DONE for lack of DB access; the observed family behaviour below is from named filings.

## 3. How filers use it (filings opened)
| Family | Filing | Statement and row | What the tag is |
|---|---|---|---|
| Large tech, ASC 606 | AAPL 0000320193-25-000079 R3 (me) | "Net sales" | RCFC 416,161M FY2025 (the FY2018 10-K 0000320193-18-000145 used `Revenues`; ledger 22) |
| Conglomerate | GE 0000040545-26-000008 R3 (me) | "Total revenue" 45,855M | `Revenues` (FY2025 consolidated); "Sales" row below it is RCFC 12,159M = a component |
| Grain/ethanol merchandiser | ANDE 0000821026-26-000010 R3 (me) | "Sales and merchandising revenues" 11,008,928K | `Revenues` is the total; RCFC elsewhere in the filing is the 606 subset (1.40B vs 11.26B per [28]) |
| Homebuilder | DHI 0000882184-25-000081 R4 (me) | "Revenues" 34,250.4M | `Revenues`; no OperatingIncomeLoss and no CostsAndExpenses on the face |
| Retailer | BBW 0001437749-26-012501 R4 (me) | "Revenue" 529,832K | RCFC |
| Utility | DUK 0001326160-26-000014 R3 (me) | "Total operating revenues" 32,237M | `RegulatedAndUnregulatedOperatingRevenue`, components regulated electric/gas |
| Industrial REIT | PLD 0001193125-26-051453 R4 (me) | "Total revenues" 8,790,1xxK | `Revenues`, components are custom (pld_RentalRevenue ...) |
| P&C insurer | PGR 0000080661-26-000086 R3 (me) | "Total revenues" 87,671M | `Revenues`; premiums `PremiumsEarnedNet`; **its "Investment income" row is tagged `InterestAndDividendIncomeOperating`** (3,583M), the bank interest-income tag |
| BDC | ARCC 0001287750-26-000006 R5 (me) | "Total investment income" 3,052M | `GrossInvestmentIncomeOperating`; **no `Revenues` line on the statement** |
| Rental/finance | HTZ 0001657853-26-000008 R7 (me) | "Revenues" 8,504M | `Revenues`; interest expense inside costs |
| Bank, net presenter | JPM 0001628280-26-008131 [32] | "Total net revenue" | RNIE (interest income is `InterestIncomeOperating`) |
| Bank, net presenter | BAC 0000070858-26-000157 R3 [32] and Citigroup 0000831001-25-000154 R2 (me, 10-Q) | "Total revenue, net of interest expense" | **`Revenues`** = NII + noninterest income. Citigroup 9M 2025: 44,127 + 21,227 = 65,354 (checked by me). Contradicts the definition (gross) |
| Bank, no total | USB, ZION, PEBO, FHN etc. [32] | none presented | stored "revenue" is whatever tag exists (IADIO, RCFC subset or Revenues) |
| Thrift | TFSL 0001381668-25-000106 [32] | Interest income 76x,xxxK | IADIO; no revenue total |

### Required answers
- **Which companies report net interest income, total interest income, provision for credit losses and under which tags** (face statements): 
  - Large and mid banks: NII = `InterestIncomeExpenseNet` (JPM, BAC, Citigroup R2 me, TFSL, FLG R4 me); total interest income = `InterestAndDividendIncomeOperating` (BAC, Citigroup, FLG, TFSL, 27 of the 30-bank cohort) or `InterestIncomeOperating` (JPM, FHN, BANR; 3 of 30 [32]); provision = no single tag: `ProvisionForLoanLeaseAndOtherLosses` (JPM, FLG: "Provision (benefit) for credit losses"), `FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal` (Citigroup "Provision for credit losses on loans", ZION), `ProvisionForLoanLossesExpensed` (TFSL), custom (BAC).
  - Thrifts: same tags (TFSL).
  - Insurers: no NII. PGR (me): "Investment income" = `InterestAndDividendIncomeOperating`, "Interest expense" = `InterestExpenseDebt`, no provision for credit losses; premiums `PremiumsEarnedNet`.
  - BDCs: no NII and no provision. ARCC (me): total investment income `GrossInvestmentIncomeOperating` (with components `InterestIncomeOperatingPaidInKind`, `DividendIncomeOperatingPaidInKind`), `NetInvestmentIncome` after expenses, interest/credit facility fees in `InterestExpense` (793M), no provision.
  - Frames CY2023 counts for the bank tags: see the interest card.
- **GE: why quarterly revenue is the GE Capital figure.** Frames and companyconcept (undimensioned facts only) return `us-gaap:Revenues` for GE Q2 2015 (2015-04-01..2015-06-30) = 2,690M, frame CY2015Q2, from the FY2016 10-K **0000040545-17-000010**. That filing's R164 "Quarterly Information (Unaudited) (Details)" prints "Total revenues and other income" under `us-gaap:Revenues` with the eight quarterly values 2,649 / 2,600 / 2,771 / 2,885 (2016) and 2,585 / 2,660 / 2,690 / 2,866 (2015), while the 12-month columns of the same row hold the consolidated 123,693M (corrected 2026-10-21: 113,676M is the GE parent section) (2016). The Verifier read 2,690M as the GE Capital figure (0000040545-16-000174 R2: consolidated 29,226M, GE 26,578M, GE Capital 2,690M) [28]. So in that note the quarterly `Revenues` facts are GE Capital's total while the annual facts are consolidated; the consolidated quarterly figure sits under other contexts or tags (that note also uses `SalesRevenueNet` "Sales of goods and services" 30,345M for Q4 2016). A mapper that takes the undimensioned `Revenues` fact for a quarter therefore gets GE Capital. Evidence: FILING-CHECKED for the R164 values and the API fact; the GE Capital identity of the quarterly figures rests on [28]'s R2 cross-check, and I did not inspect the instance's context definition (R-file rendering hides it), so the dimension used is UNVERIFIED. The 2016 revenue/net-income cells GE used also show that GE's older 10-Ks present Consolidated, GE and GECS columns; FY2025's 10-K (me, R3) is a single consolidated column (Revenues 45,855M).

## 4. Siblings and confusables
- `Revenues` vs RCFC: RCFC is only the ASC 606 revenue; other revenue (interest, leases, insurance, derivative gains) is excluded. ANDE: RCFC 1.40B vs Revenues 11.26B. For banks RCFC is a fee subset (DCOM, MRBK, AX [32]).
- `Revenues` vs RNIE vs IADIO: three different perimeters for banks (gross, net of interest expense, interest only). Definition says gross; BAC, PNC, Citigroup, FHN, CASH tag net under `Revenues`; GABC and ACNB tag gross [32].
- IADIO vs `InterestIncomeOperating` vs `InvestmentIncomeInterest`: totals vs the nonoperating securities line. 38 filers carry both IADIO and InterestIncomeOperating in 2023.
- RCFC including vs excluding tax: 781 vs 3,142 filers in 2023; different numbers when excise or VAT is collected.
- `SalesRevenueNet` (pre-2018) is the old counterpart of RCFC/Revenues; a company's series often splits across tags at the ASC 606 year (AAPL).

## 5. Known misuses and quirks (carried from company-quirks.md plus new)
- ANDE, DCOM, MRBK, AX: RCFC is a subset (carried).
- GE quarterly `Revenues` = GE Capital (explained above).
- NEW (me): PGR tags insurance "Investment income" with the bank total-interest tag IADIO. Any bank rule keyed on IADIO would include insurers; 479 CY2023 filers carry it, 388 of them bank-like, so about 91 are not.
- NEW (me): ARCC and other BDCs present no revenue tag at all; "revenue" for a BDC is `GrossInvestmentIncomeOperating`.
- NEW (me): Citigroup's `Revenues` is NET of interest expense (confirms a fourth net-revenue bank; inbox line processed).
- USB `Revenues` 28,656M is not a face line [32].
- RELAYED (shards S016, FILING-CHECKED by them, not re-opened by me): RCFC is not a safe subset in either direction. At lessors it omits lease revenue (AMT Q2-2026 211.1M vs Revenues 2,749.1M, 0001053507-26-000133 R4) and at WMB it is LARGER than the face total (+11% Q2, +56% Q1; 0000107263-26-000026 R2). Prefer the face total for the same context; a "606 <= total" assumption fails.

## 6. Mapping verdict
- `Revenues` for non-banks: **safe per company-period only**; it is the total for most filers but is a component or a different entity at GE (quarterly) and a segment at some conglomerates; evidence FILING-CHECKED on 6 filers above, DATA-INFERRED beyond. Never mix with RCFC in a precedence list without checking that the company does not report both (796 filers in CY2023 do).
- RCFC: **safe as total revenue only when no `Revenues`/other total exists and the filer is not a bank/insurer/REIT/utility**; subset at ANDE and the banks. FILING-CHECKED (AAPL, BBW) / counterexamples ANDE, DCOM, MRBK, AX.
- `SalesRevenueNet` family: safe only for periods before ASC 606 adoption, per company. FILING-CHECKED (GE R164 still uses it in FY2016), DATA-INFERRED for the rest.
- Banks: **do not map any single tag**; compute NII + noninterest income (data-team/32 recommendation, supported by Citigroup (me) and 5 of 5 total-revenue presenters). `Revenues` is NEVER safe for banks. IADIO/RNIE: usable only as labelled bank components.
- IADIO outside banks: NEVER (PGR).
- Evidence class: FILING-CHECKED for the named filings, DATA-INFERRED for populations. Verified by: Tag Expert (me) plus Verifier [32].
