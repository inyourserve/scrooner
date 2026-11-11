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
- **GE: why quarterly revenue is the GE Capital figure.** Frames and companyconcept (undimensioned facts only) return `us-gaap:Revenues` for GE Q2 2015 (2015-04-01..2015-06-30) = 2,690M, frame CY2015Q2, from the FY2016 10-K **0000040545-17-000010**. That filing's R164 "Quarterly Information (Unaudited) (Details)" prints "Total revenues and other income" under `us-gaap:Revenues` with the eight quarterly values 2,649 / 2,600 / 2,771 / 2,885 (2016) and 2,585 / 2,660 / 2,690 / 2,866 (2015), while the 12-month columns of the same row hold the consolidated 123,693M (corrected 2026-10-21: 113,676M is the GE parent section) (2016). The Verifier read 2,690M as the GE Capital figure (0000040545-16-000174 R2: consolidated 29,226M, GE 26,578M, GE Capital 2,690M) [28]. So in that note the quarterly `Revenues` facts are GE Capital's total while the annual facts are consolidated; the consolidated quarterly figure sits under other contexts or tags (that note also uses `SalesRevenueNet` "Sales of goods and services" 30,345M for Q4 2016). A mapper that takes the undimensioned `Revenues` fact for a quarter therefore gets GE Capital. Evidence: FILING-CHECKED for the R164 values and the API fact; the GE Capital identity of the quarterly figures rests on [28]'s R2 cross-check, and I did not inspect the instance's context definition (R-file rendering hides it), so the dimension used was UNVERIFIED here. RESOLVED 2026-10-21 (Verifier file 35, FILING-CHECKED on the instance ge-20161231.xml): the 8 quarterly values are filed twice with identical values, in the GECC-member context AND in the plain undimensioned context, a filer context error; an undimensioned fact can still be a subsidiary's figure. The 2016 revenue/net-income cells GE used also show that GE's older 10-Ks present Consolidated, GE and GECS columns; FY2025's 10-K (me, R3) is a single consolidated column (Revenues 45,855M).

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

- RELAYED (Verifier file 35, FILING-CHECKED by them, not re-opened by me): GE FY2024 10-K 0000040545-25-000015 R161 files RCFC "Sales of equipment and services" (9,879/8,943/8,223/8,076M) AND `Revenues` "Total revenue" (10,812/9,842/9,094/8,955M) undimensioned for the same quarters; an RCFC-first precedence shows the component (excludes insurance revenue). Same-context coexistence must be checked per company.
- NEW (me, 2026-10-21, R2 taxonomy run, FILING-CHECKED): `Revenues` has different perimeters in one industry. XOM 0000034088-26-000045 R3: `Revenues` 332,238M = total revenues AND other income (sales 323,905M, equity-affiliate income 5,064M, other income 3,269M are dimension members of the same tag). COP 0001163165-26-000009 R3: `Revenues` = "Sales and other operating revenues" 58,944M; the total 61,548M is custom `cop_RevenuesAndOtherIncome`. Dillard's 0000028917-26-000006 R4: `Revenues` "Total net sales and service charges and other income" 6,563,336K vs RCFC "Net sales" 6,473,623K. UDR 0000074208-26-000013 R4: RCFC = "Joint venture management and other fees" 11,361K vs `Revenues` 1,712,317K. Boston Beer 0001193125-26-067467 R2: RCFCIncl "Revenue" 2,087,251K (gross of excise), custom `sam_LessExciseTaxes`, `Revenues` "Net revenue" 1,964,994K.
- NEW population (me, FSDS 2025q4+2026q1, FY2025 10-K face, 4,601 filers, DATA-INFERRED): face total tag RCFC 1,732, Revenues 1,333, RCFCIncl 247, utility/insurer/lessor sector totals 89, custom 25; RCFC and Revenues both undimensioned FY and different at 99 filers (face total is `Revenues` in 93 of the 96 where RCFC is smaller). Detail: data-team/strategy/team/R2-tag-expert-heterogeneity-taxonomy.md sec. 3.

## 6. Mapping verdict
- `Revenues` for non-banks: **safe per company-period only**; it is the total for most filers but is a component or a different entity at GE (quarterly) and a segment at some conglomerates; evidence FILING-CHECKED on 6 filers above, DATA-INFERRED beyond. Never mix with RCFC in a precedence list without checking that the company does not report both (796 filers in CY2023 do).
- RCFC: **safe as total revenue only when no `Revenues`/other total exists and the filer is not a bank/insurer/REIT/utility**; subset at ANDE and the banks. FILING-CHECKED (AAPL, BBW) / counterexamples ANDE, DCOM, MRBK, AX.
- `SalesRevenueNet` family: safe only for periods before ASC 606 adoption, per company. FILING-CHECKED (GE R164 still uses it in FY2016), DATA-INFERRED for the rest.
- Banks: **do not map any single tag**; compute NII + noninterest income (data-team/32 recommendation, supported by Citigroup (me) and 5 of 5 total-revenue presenters). `Revenues` is NEVER safe for banks. IADIO/RNIE: usable only as labelled bank components.
- IADIO outside banks: NEVER (PGR).
- `Revenues` perimeter (added 2026-10-21): includes other income / equity-affiliate income at XOM, CVX and Dillard's, but not at COP; a screener 'revenue' built on `Revenues` needs a label or calc-children check for 'other income' (FILING-CHECKED XOM, COP, DDS).
- Evidence class: FILING-CHECKED for the named filings, DATA-INFERRED for populations. Verified by: Tag Expert (me) plus Verifier [32].

## 7. FSN-era identification and inbox relays (Tag Expert, 2026-11-09)
Playbook with counts: [`../playbooks/revenue.md`](../playbooks/revenue.md). The FSN store maps face lines (`is.revenue_total@1`: RCFC-ExcludingAssessedTax, RCFC-IncludingAssessedTax, Revenues, RegulatedAndUnregulatedOperatingRevenue, all p10), so the note-fact traps below (relays) mostly do not reach the FSN write. The face-line traps do.

**NEW, measured (production fsn.*, latest 10-K, DATA-INFERRED): 33 companies have two mapped revenue lines with different FY values in the same filing**: a component on an RCFC tag plus the `Revenues` total, or an excise pair. `select.select_concept` blanks such a key as `conflicting_values_in_filing`. Examples: GM 1467858 "Automotive" 167,971M vs "Total net sales and revenue" 185,019M; Welltower 766704 "Resident fees and services" 8,453M vs 10,838M; Healthpeak/DOC 765880 604M vs 2,822M; WMT 104169 "Net sales" 706,413M vs "Total revenues" 713,163M; CVX 93410 184,432M vs "Total Revenues and Other Income" 189,031M; fee lines of a few million at 4457, 74208, 920522, 1289490, 1571283. Excise pairs: 14693 "Sales" 5,082M (IncludingAssessedTax) vs "Net sales" 3,928M (Excluding), likewise 24545, 16918. Sent to the mapping builder 2026-11-09. **FILING-CHECKED 2026-11-09**: GM 0001467858-26-000013 R3 Automotive 167,971 + GM Financial 17,048 = Total 185,019; WMT 0000104169-26-000055 R3 Net sales 706,413 + Membership and other income 6,750 = Total revenues 713,163; Welltower 0000766704-26-000010 R4 Resident fees 8,452,996 inside Total revenues 10,838,034. Rule implied by the cases: **within one IS report, a later "Total…" `Revenues` line is the total and an earlier RCFC line is a component; in an excise pair, take "Net sales" (Excluding)**. The "Revenues and other income" perimeter (CVX, 717423, 315852, 893538) is a separate perimeter ruling (§5: XOM includes other income, COP does not).

Relayed lessons processed (FILING-CHECKED by the named role unless marked; not re-opened by me):
- **RCFC can be larger than the face total** (gross before contra-revenue): MA gross revenue 29,845 vs net 18,884 (0001141391-22-000023 R61); WMB 17,773 vs 10,965; FCX 18,945 vs 18,628; DVN 13,750 vs 12,206 (0001564590-22-005321 R2); THC pre-606 gross patient revenue 20,613 vs 19,179. It is also used for non-606 streams (CNC premium revenue) and filed as 0.0 in pre-adoption comparatives (Standardization Lead; **corrects §6 "safe as total only when no Revenues exists"**: also not safe when larger than the face total). Coexistence: both undimensioned in 10,142 top-1000 company-periods, differing by more than 1% in 4,479 (201 of 467 companies) (Tag Mapper, DATA-INFERRED). No fixed priority between the two is right; the face position decides.
- **RCFC as a partial line**: DOC "Resident fees and services" 297,782K of total revenues 1,397,237K (0001628280-25-036063 R4); a gross profit built from it is negative. At lessors RCFC excludes rental revenue: never a REIT revenue total (Standardization Lead). At banks it is a partial fee line (Popular "Net fees", 0001193125-26-085756 R5); 44% of 331 banks print RCFC, 2% print `Revenues` (Sector Analyst).
- **Undimensioned `Revenues` that is not the company total**, outside any statement: BLK related-party 12,794 (R135); EMR 10-Q acquisition narrative 1,660 (R41, an acquired target's revenue on EMR's own context); FLS intersegment 0; NTAP Hybrid Cloud segment 6,237 vs face 6,925 (0001193125-26-259683); GIS joint ventures at 100% basis 2,189.2 (Standardization Lead, Verifier). The FSN note fill does not read revenue from notes (NOTE_TAGS holds interest only), so these do not reach the FSN write; the old mapper served NTAP's and EMR's.
- SNA labels its face `Revenues` total "Net sales" (5,156.1 = products 4,743.2 + financial services 412.9): a label match would misread it as product sales (0000091440-26-000045 R3).
- `RegulatedAndUnregulatedOperatingRevenue`: the right face total at NJR (2,036,412K = utility + nonutility, 0000356309-25-000093 R3), but it mixes segment values elsewhere (Alliant); accept only as the face total line (Data Verifier). The FSN rule maps face lines only: consistent.
- **Dimension-only totals**: RBA cost of revenue only under ProductOrServiceAxis members (0001628280-26-011682 R3), AMP LongTermDebt only under ConsolidatedEntitiesAxis members, TXT AssetsCurrent only in the Manufacturing group block: no undimensioned total (Data Verifier). In FSN these face lines carry no `dim_id = 0` value, so the cell is blank; it needs a member-sum rule or a reason.
- **Recast for discontinued operations**: Teleflex's FY2025 10-K prints FY2024 RCFC 1,699.5M vs 3,047.3M in the FY2024 10-K, while the Q3 2025 10-Q 9M (2,394.6M) is on the old basis; FY2025 1,992.7M minus that 9M gives -401.9M. The same 10-K prints Q4 2025 = 568.984M directly (Ritwik, FSN num). A prior-year column that changed between vintages is the witness that FY and 9M are on different bases (the store's `mixed_vintage_inputs` / `no_basis_witness`).
- Status relay (Data Chief, 2026-10-22): no revenue-total disagreement guard existed in the old pipeline. The FSN store's conflict blank is the first such guard, and it is too blunt (above).
- **Cost of revenue**: TSLA FY2017 `CostOfGoodsSold` = "Cost of revenues - Automotive sales" 6,724,480K, a component; the total is `CostOfRevenue` 9,536,264K (0001564590-18-002956 R4) (Data Verifier). The FSN rule maps neither `CostOfGoodsSold` nor components: consistent. SPGI's only cost line "Operating-related expenses" (expenses by nature) is restated between 10-Q vintages (Q1 2024 1,120 → 1,111) while revenue is unchanged (0000064040-24-000125 vs -25-000126 R2): a vintage break for gross profit. At HCP/DOC `OperatingExpenses` is the "Operating" property-expense line (179,080K inside total costs 463,934K, 0001628280-17-007720 R4): revenue minus it is NOI.

## 8. Folded in from the FSN-expert per-tag cards (2026-11-10)
- **`SalesRevenueGoodsNet` is usually a COMPONENT** ("Product" 181, "Product sales" 83, "Products" 76, "Sales" 60 labels; 39 top-100 names, 2009-2019): MSFT FY2016 10-K 0001193125-16-662209 … Q3 FY2018 prints "Product" (`SalesRevenueGoodsNet`) + custom "Service and other" = "Total revenue" (`SalesRevenueNet`), calc weight +1 each. The FSN pilot (run 41490670432) treated it as a second total, so MSFT FY2014-FY2017 were blanked `conflicting_values_in_filing` (FY2014 72,948 vs 86,833). It is the pre-606 twin of the 33-company RCFC-component finding in §7. **One rule covers both: a revenue candidate that is a calc child of another revenue candidate in the same filing is a component, never the total** (FSN-expert PROPOSALS P-2). At a goods-only company labelled "Sales" it can be the total; only the calc tree tells.

## 9. Relays 2026-11-11
- AT&T 10-Q 0000732717-26-000297 R2 l11-12: `CostOfGoodsAndServicesSold` labelled "Equipment" carries only a member value; with "Other cost of revenues" there is no total cost line: cost of revenue = sum of the cost lines (excluding D&A perimeter) (cash-flow lane I6; Ritwik cloud).

## 10. Ranks 1-50 relay (Ritwik relay 2026-11-11, work/tag-library/ranks-1-50 aea0cf4 data-team/47-fsn-store/company_tag_map/ranks_1_50.csv (evidence_adsh + label per row); DATA-INFERRED, not yet filing-checked by the Verifier)
- AMGN: product sales on `RevenueFromContractWithCustomerIncludingAssessedTax`, TOTAL revenues on `…ExcludingAssessedTax`: never pick by the Including/Excluding name; pick the calc top of the revenue block.
- TSLA: `RevenueFromContractWithCustomerExcludingAssessedTax` is a calc CHILD of `Revenues` until 2023, then the top line: the same tag changes role across eras.
- XOM pre-2018: custom `xom:SalesAndOtherOperatingRevenueIncludingSalesBasedTaxes` is the revenue line (custom tag in a standard position).
- MS, WFC: revenue = `RevenuesNetOfInterestExpense` ("Net revenues" / "Total revenue").

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.
