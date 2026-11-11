# Card family: Balance-sheet liabilities and equity, read from FSN (written 2026-11-11 by the Tag Expert)

This card follows the founder order of 2026-11-11: "FSN FOR LEARNING - which tag is what. SEC FOR MAPPING." It covers 33 us-gaap tags, all among the top 140 tags in the top-1,000 cohort. The machine-readable verdicts are in `data-team/tags/library/fsn-balance-sheet-liabilities-equity.csv`. This card extends `cards/debt.md` and does not contradict it.

## Method and scope

- **Population.** The FSN store (`fsn.*`) holds the 1,000 companies in `fsn.company_load`. `fsn.filing` has 1,001 company ids. Counts are distinct companies with at least one presentation line (`fsn.line`) for the tag in a filing with fy >= 2015, on any statement. A second count is "latest 10-K": the latest 10-K per company with fy >= 2023, which gives 999 filings.
  - "Undimensioned value" means an `fsn.value` row with `dim_id = 0`, `coreg = ''`, `ddate =` the filing period and `qtrs = 0`.
  - Label counts are case-folded `plabel` strings, given as (companies, lines).
  - Calc parents come from `fsn.calc_arc` over the latest 10-Ks ("latest") and the FY2016 10-Ks (819 filings, "fy16").
- **Official meaning.** The definition, balance and period type of each tag were read from the element-definition blocks in the SEC R pages of the filings below (sec.gov, read 2026-11-11). Those blocks carry the FASB documentation label and the element's Details.
- **Filings opened on sec.gov** (R page of the balance sheet, plus the parenthetical page where there is one):
  - AAPL 0000320193-25-000079 R5/R6
  - JPM 0001628280-25-048859 R4/R5 (10-Q)
  - CVX 0000093410-26-000078 R5/R6
  - PGR 0000080661-26-000086 R4/R5
  - PLD 0001193125-26-051453 R2
  - MCK 0000927653-26-000069
  - MET 0001099219-26-000013 R3/R4
  - DHI 0000882184-25-000081 R2/R3
  - PCAR 0001193125-26-057025 R4/R5
  - LH 0000920148-24-000118 R2/R3 (10-Q)
  - MUR 0000717423-20-000008 R2
  - LW 0001558370-17-000080 R4 (10-Q)
  - WFRD 0001603923-19-000095 R4 (10-Q)
  - Wisconsin Electric Power (CIK 107815, a WEC subsidiary that is **not** in the cohort; used as a layout example only) 0000107815-26-000003 R4/R5
- **Database access.** Read-only, one connection at a time, `statement_timeout` 90 to 120 s as the brief allowed. `pg_stat_activity` showed 15 to 16 backends, but only about 5 were client sessions; the rest were Supabase system workers.
- **Binding rulings used** (relayed by the coordinator on 2026-11-11, not heard from the founder by me):
  1. VZ and T print no parent-equity line, so their stockholders' equity is a blank with a reason.
  2. Equity including NCI is the source where parent equity is not printed and there is no NCI.
  3. No derived instants. This matches doc 02, founder decision of 2026-11-01, item 4: "EPS and instants are never derived".

## Headline numbers (latest 10-K, 999 companies, DATA-INFERRED)

| Measure | Count |
|---|---|
| Undimensioned value present: `LiabilitiesAndStockholdersEquity` | 999 (no gaps) |
| `StockholdersEquity` | 926 |
| `LiabilitiesCurrent` | 823 |
| `Liabilities` | 782 |
| `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` | 499 |
| `MinorityInterest` | 440 |
| `LiabilitiesNoncurrent` | 116 |
| `RedeemableNoncontrollingInterestEquityCarryingAmount` | 94 |
| `TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests` | 28 |
| `TemporaryEquityCarryingAmountAttributableToParent` | 24 |
| **No total-liabilities line (no undimensioned `Liabilities`)** | **217**: Industrials 57, Utilities 34 (of 57 utilities), Consumer Discretionary 30, Technology 24, Materials 19, Healthcare 15, Energy 11, Communication Services 10, Consumer Staples 10, Real Estate 3, Financials 3 (of 151), Other 2. 32 of them carry a temporary-equity or redeemable-NCI value. Examples: ABT, AES, HPQ, FTV, MSI, ITW, AVY, CHTR, VZ, ETR, ADM, TJX, BKR, IP, MCK |
| **No parent-equity line (no undimensioned `StockholdersEquity`)** | **68**. 25 of them print an NCI line and no parent line: ADM, CAT, HAS, ITW, MRSH, BRO, PG, CSX, UNH, VZ, T, RPRX, RKT, CG, CPNG, CNH, CWEN, RIVN, LAMR, TPG, ET, MGY, ASTS, CARR, HOOD. The other 43 print only equity incl. NCI (or partners' capital) with no NCI line, e.g. JNJ, AVGO, V, QCOM, PEG, PPL, WEC, YUM, plus the partnerships MPLX, SUN, EPD, PAA, WES, CQP |

## Total liabilities and total debt: which tags feed them (the two biggest gaps)

**`total_liabilities_resolved`**

1. Source: the undimensioned `us-gaap:Liabilities` fact on the balance-sheet face, from the same filing (dim 0, coreg ''). That covers 782 of 999 latest 10-Ks.
2. When no such line exists (217 companies), the cell is **not presented, with the reason "no total-liabilities line printed"**. Assets minus equity, or a sum of the face liability lines, would be a derived instant, which the ruling forbids. Cloud Ritwik makes the same call for GILD, ADI, VZ, ABT, MCD, TMUS, ETN, ACN and VLO.
   - This conflicts with the live `fsn.concept_rule` rows `bs.liab_zone_after_assets@1`, `bs.liab_cal_child@1` and `bs.liab_cal_child@2` (priority 20-22), which sum liability lines. See Disagreements, D3.
3. Proven traps (FILING-CHECKED):
   - **Tag right, label wrong.** LH 10-Qs (27 filings, 2016-2024) and MUR's FY2019 10-K: the value follows the tag; only the label is off. Do not demote these lines on the label.
   - **Tag used for something smaller than total liabilities.** LW 2017-Q1 (long-term liabilities only) and WFRD 2019 (liabilities not subject to compromise; liabilities subject to compromise of 7,634M sit outside it). Treat these as company-period exceptions: blank, or the face line only by decision.
   - **Segment-only totals.** PCAR prints `Liabilities` only per business segment (Truck, Parts and Other 7,890.9M; Financial Services 17,181.3M). There is no consolidated line. Not presented.
   - **Dimensioned values beside the real one.** VIE or co-registrant members carry `Liabilities` values on the same face: JPM's VIE block 28,837M against the consolidated 4,199,993M; SEIC, AFG and PRU have the same pattern. Only dim 0 and coreg '' are the consolidated figure.
4. Check (not a source): total liabilities + temporary equity + total equity incl. NCI = `LiabilitiesAndStockholdersEquity`.
   - MCK: 83,157 + 943 + (-1,777) = 82,323. Ties.

**`total_debt_resolved`**

- Composition, from this group: `LongTermDebtCurrent` + `LongTermDebtNoncurrent` (slot "borrowing", sign +1). Outside this group: `ShortTermBorrowings`, `CommercialPaper`, `DebtCurrent`, `LongTermDebtAndCapitalLeaseObligations`(+`Current`, +`IncludingCurrentMaturities`), `LongTermDebt` (only where it is the face line), `FinanceLeaseLiability`(+`Current`/`Noncurrent`, included by founder decision 2026-11-04 item 5, doc 02 line 116), `SecuredDebt`, `SubordinatedDebt`, `NotesPayable`, `LineOfCredit` and custom debt lines found by calc position.
- Never include `OperatingLeaseLiability*`, `OtherLiabilities*`, `AccruedLiabilitiesCurrent` or `DeferredIncomeTaxLiabilitiesNet`.
- Debt-like tags on the latest 10-K balance-sheet face (companies, DATA-INFERRED):

  | Tag | Companies |
  |---|---|
  | `OperatingLeaseLiabilityNoncurrent` (not debt) | 480 |
  | `LongTermDebtNoncurrent` | 415 |
  | `OperatingLeaseLiabilityCurrent` (not debt) | 319 |
  | `LongTermDebtCurrent` | 248 |
  | `LongTermDebtAndCapitalLeaseObligations` | 195 |
  | `ShortTermBorrowings` | 146 |
  | `DebtCurrent` | 134 |
  | `LongTermDebtAndCapitalLeaseObligationsCurrent` | 131 |
  | `LongTermDebt` | 87 |
  | `FinanceLeaseLiabilityNoncurrent` | 57 |
  | `FinanceLeaseLiabilityCurrent` | 36 |
  | `SecuredDebt` | 30 |
  | `LineOfCredit` | 26 |
  | Companies with a custom debt-labelled line | 82 |

- So `LongTermDebtCurrent`/`Noncurrent` alone reach fewer than half the cohort. MCK, for example, files its debt on `LongTermDebtAndCapitalLeaseObligations(Current)` with no `LongTermDebtNoncurrent` (FILING-CHECKED).
- In 175 latest 10-Ks, `LongTermDebtNoncurrent` is a calc child of `LongTermDebt`. Taking both from one filing double counts. This repeats debt.md section 6.

---

## Per-tag sections

Each section below is laid out the same way:
- **Official:** the definition text, balance type and period type.
- **FSN:** companies using the tag, the latest-10-K count, statements by company, labels as (companies, lines), and calc parents.
- **Decision**, with **Exceptions**, **Era** and **Evidence**.

### 1. LiabilitiesAndStockholdersEquity

- **Official:** "Amount of liabilities and equity items, including the portion of equity attributable to noncontrolling interests, if any." Credit, instant.
- **FSN:** 1,001 company ids; 998 in the latest BS. Statements: BS 1,001, UN 51.
  - 339 label variants: "total liabilities and equity" (400, 13,163), "...stockholders equity" (337), "...stockholders' equity" (307), "...shareholders' equity" (168), "...deficit" variants (about 140 companies).
  - Labels that name mezzanine: "total liabilities, redeemable noncontrolling interest(s) and equity" (37 companies), "...redeemable convertible preferred stock and..." (11).
  - No calc parent: it is the root.
- **Decision:** excluded as a displayed concept. It is the balance-sheet anchor and identity check; it always equals `Assets`.
- **Exceptions:**
  - The total includes temporary (mezzanine) equity, even though the tag name says "stockholders' equity": MCK "Total liabilities, redeemable noncontrolling interests, and deficit" 82,323M; MET "Total liabilities, mezzanine equity and equity" 745,166M.
  - Never compute liabilities as this tag minus `StockholdersEquity`.
- **Era:** none.
- **Evidence:** FILING-CHECKED (AAPL, JPM, CVX, MCK, MET).

### 2. Liabilities

- **Official:** "Amount of liability recognized for present obligation requiring transfer or otherwise providing economic benefit to others." Credit, instant.
- **FSN:** 792 companies; 782 with an undimensioned latest value. Statements: BS 791, UN 35, BS parenthetical 28.
  - Labels: "total liabilities" (791, 31,417), "liabilities" (40), "liabilities, total" (12).
  - Odd labels: "noncontrolling interest" (LH, 27 lines), "liabilities of consolidated variable interest entity" (GTLB, parenthetical), "liabilities of managed investment entities" (AFG 2020-21), "...consolidated VIEs" (SEIC 2025-26, PRU 2020), "...consolidated sponsored investment portfolios" (TROW 2016), "total long-term liabilities" (LW 2017), "total liabilities not subject to compromise" (WFRD 2019), "total current liabilities associated with assets held for sale" (MUR FY2019).
  - Calc parent: `LiabilitiesAndStockholdersEquity` (783 latest, 568 fy16); `AssetsNet` 7.
- **Decision:** map to `total_liabilities_resolved`. Use the undimensioned value only (dim 0, coreg '').
- **Exceptions:**
  - LH 0000920148-24-000118 R2 (and its 27 10-Qs): the face prints "Noncontrolling interest" against `Liabilities` 10,427.1M. The value is the sum of LH's liability lines (3,412.0 + 5,352.1 + 528.2 + 701.3 + 75.2 + 358.3 = 10,427.1). The labels are shifted one row through the whole statement. **Map it; do not demote on the label.**
  - MUR 0000717423-20-000008 R2: the label reads "Total current liabilities associated with assets held for sale", but the value 5,913,893K = assets 11,718,504K - total equity 5,804,611K. Same label shift: map it.
  - LW 0001558370-17-000080 R4: "Total long-term liabilities" 2,503.7M. The prior column, 300.7M, is smaller than current liabilities alone (409.6M), so the tag holds a long-term subtotal. **Exclude for that period.**
  - WFRD 0001603923-19-000095 R4: "Total Liabilities Not Subject to Compromise" 3,914M, with `LiabilitiesSubjectToCompromise` 7,634M outside it. **Exclude for Chapter 11 periods.** Total liabilities is not presented.
  - PCAR 0001193125-26-057025 R4: `Liabilities` exists only with `StatementBusinessSegmentsAxis` members. Not presented (segment only).
  - JPM 0001628280-25-048859 R4: the VIE block prints "Total liabilities" 28,837M under `ConsolidatedEntitiesAxis`. Ignore the dimensioned value.
  - AFG 0001042046-21-000011 and SEIC 0000350894-26-000013: the odd labels sit on dimensioned values (FSN `fsn.value` read). AFG's undimensioned value is 66,777M. DATA-INFERRED.
  - No line printed: 217 latest 10-Ks. Not presented.
- **Era:** none. Usage grows from 552 companies in FY2015 to 783 in FY2026.
- **Evidence:** FILING-CHECKED (AAPL, JPM, MCK, PCAR, LH, MUR, LW, WFRD).

### 3. LiabilitiesCurrent

- **Official:** "Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer." Credit, instant.
- **FSN:** 829 companies; 823 latest. Statements: BS 829, UN 38.
  - Labels: "total current liabilities" (818), "current liabilities" (10), "liabilities, current" (12), "total" (EOG, ETR).
  - Odd labels: "total truck, parts and other current liabilities" (PCAR), "total current and accrued liabilities" (NFG), "long-term debt, less current portion" (LH, label shift), "operating lease liabilities" (PINS 2019), "total liabilities" (HQY 2015, BMNR 2022), "accounts payable, accrued expenses and other current liabilities" (FOX 2020-21).
  - Calc parent: `Liabilities` 616 and `LiabilitiesAndStockholdersEquity` 224 (the latter where no total-liabilities line exists).
- **Decision:** map to `current_liabilities_resolved` for classified balance sheets. Banks, insurers and other unclassified balance sheets are not in the template, matching both Ritwik files.
- **Exceptions:**
  - PCAR: segment member only. The Truck block's 5,612.1M is not consolidated current liabilities, so not presented.
  - LH: map despite the label (the value ties to its current lines).
  - NFG, PINS 2019, HQY 2015, BMNR 2022, FOX 2020-21: label disagrees with the tag. DATA-INFERRED, not opened; a value check is needed before mapping those periods.
- **Era:** none.
- **Evidence:** FILING-CHECKED (AAPL, CVX, MCK, PCAR, LH).

### 4. RetainedEarningsAccumulatedDeficit

- **Official:** "Amount of accumulated undistributed earnings (deficit)." Credit, instant.
- **FSN:** 972 companies; 964 latest. Statements: BS 971, EQ 53. 65 negating lines.
  - Labels: "retained earnings" (759), "accumulated deficit" (329), "retained earnings (accumulated deficit)" (176), "retained deficit" (42), "accumulated earnings" (25), "reinvested earnings" / "earnings reinvested..." (about 14).
  - Calc parent: `StockholdersEquity` 883, `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` 60.
- **Decision:** excluded. It is a detail of equity, and the catalogue has no concept for it.
- **Exceptions:**
  - PLD "Distributions in excess of net earnings" (-902,427K) is a REIT's deficit on this tag.
  - LH puts this tag on the row labelled "Accumulated other comprehensive income" (label shift).
- **Era:** none.
- **Evidence:** FILING-CHECKED (AAPL, JPM, PLD).

### 5. AccumulatedOtherComprehensiveIncomeLossNetOfTax

- **Official:** "Amount, after tax, of accumulated increase (decrease) in equity from transaction and other event and circumstance from nonowner source." Credit, instant. Losses are negative.
- **FSN:** 955 companies; 925 latest. Statements: BS 954, EQ 28. 415 label variants, nearly all "accumulated other comprehensive (loss) income".
  - "...net of deferred income tax" (EG, ACGL, TFC) is the same concept, not a tax liability.
  - Calc parent: `StockholdersEquity` 846; `PartnersCapital` 15.
- **Decision:** excluded (detail of equity).
- **Exceptions:** PGR prints the AOCI components on separate tags and this tag as the "Total accumulated other comprehensive income (loss)" (103M).
- **Era:** none.
- **Evidence:** FILING-CHECKED (AAPL, JPM, PGR).

### 6. StockholdersEquity

- **Official:** "Amount of equity (deficit) attributable to parent. Excludes temporary equity and equity attributable to noncontrolling interest." Credit, instant.
- **FSN:** 973 companies; 926 latest undimensioned. Statements: BS 969, **EQ 632**.
  - Labels on BS: "total stockholders('/) equity" (611), "total shareholders('/) equity" (311), "total equity" (72), "...(deficit)" (about 190), "stockholders' equity attributable to parent" (59).
  - Labels on EQ: "beginning balance" / "ending balance" (424 each).
  - Calc parents: `LiabilitiesAndStockholdersEquity` 504, `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` 435.
- **Decision:** map to `stockholders_equity_resolved`. BS face only, undimensioned, signed as filed. A deficit is negative: MCK -2,172M, WFRD -5,262M.
- **Exceptions:**
  - Equity-statement roll-forward lines carry the same tag (632 companies). Exclude them; they are not the balance-sheet print.
  - 68 latest 10-Ks print no parent line. See tag 7.
  - Partnerships use `PartnersCapital` (existing rule priority 11).
  - Wisconsin Electric Power (not in cohort) prints common equity on a custom tag, `wep_TotalCommonShareholdersEquity`, with preferred outside it. A utility-subsidiary pattern; check cohort utilities.
- **Era:** none.
- **Evidence:** FILING-CHECKED (AAPL, JPM, CVX, MCK, WFRD).

### 7. StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest

- **Official:** "Amount of equity (deficit) attributable to parent and noncontrolling interest. Excludes temporary equity." Credit, instant.
- **FSN:** 665 companies; 499 latest undimensioned. Statements: BS 626, EQ 654.
  - Labels: "total equity" (395), "total stockholders('/) equity" (244), "total shareholders('/) equity" (138), "stockholders' equity, including portion attributable to noncontrolling interest" (71), EQ "beginning/ending balance" (428).
  - Calc parent: `LiabilitiesAndStockholdersEquity` 496.
- **Decision:** map to `stockholders_equity_resolved` **only** when, in that filing, there is no `StockholdersEquity` line and no `MinorityInterest` line on the BS face. In that case total equity is parent equity, per the ruling and cloud rule 8: COP, MO, QCOM, TJX, VRTX, CB, KLAC, JNJ, AVGO, V. Otherwise excluded: it is total equity incl. NCI, and no catalogue concept exists for that.
- **Exceptions:**
  - An NCI line is printed but no parent line, in 25 latest 10-Ks (list in the headline table): stockholders' equity is **not presented** with a reason. Total minus NCI would be a derived instant.
  - PG 0000080424-26-000103 BS lines 41-42 (FSN): "Noncontrolling interest" then "TOTAL SHAREHOLDERS' EQUITY". DATA-INFERRED.
  - DHI 0000882184-25-000081 R2: the tag is the "EQUITY" heading row, with no value. The total is a second line, "Total equity" 24,742.2M.
  - Equity statements carry the tag with class members. PG has 16 member values at one date; use undimensioned values only.
- **Era:** a company can switch between layouts across filings. The filing-level condition handles it.
  - JNJ: 36 filings with total equity only; 10 filings (2023+) with both lines.
  - AVGO: 30 filings with total equity only; 11 with parent, NCI and total.
- **Evidence:** FILING-CHECKED (CVX, PLD, MCK, MET, DHI). The per-filing combinations are DATA-INFERRED (`fsn.line`).

### 8. MinorityInterest

- **Official:** "Amount of equity (deficit) attributable to noncontrolling interest. Excludes temporary equity." Credit, instant.
- **FSN:** 570 companies; 440 latest. Statements: BS 568, EQ 56.
  - Labels: "noncontrolling interest(s)" (449), "non-controlling interest(s)" (134), "stockholders' equity attributable to noncontrolling interest" (34), "nonredeemable noncontrolling interest(s)" (12+).
  - Calc parent: `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` 438. `LiabilitiesAndStockholdersEquity` in 3 latest and 23 fy16 filings: NCI presented outside equity totals.
- **Decision:** excluded. The catalogue has no NCI concept (proposed key `noncontrolling_interest`). Use it as the gate condition for tag 7 and in the identity check.
- **Exceptions:**
  - Redeemable NCI is a different element and sits outside equity: `RedeemableNoncontrollingInterestEquityCarryingAmount` (MET 241M), `...CommonCarryingAmount` (MCK 943M), custom `lh_NoncontrollingInterestMezzanineEquity` (LH 15.2M).
  - Co-registrants: PLD prints NCI 4,560,830K for Prologis, Inc. and 3,316,713K under the Prologis, L.P. member. Use the undimensioned value.
- **Era:** none.
- **Evidence:** FILING-CHECKED (CVX, PLD, MCK, MET, DHI).

### 9. CommonStockValue

- **Official:** "Aggregate par or stated value of issued nonredeemable common stock (or common stock redeemable solely at the option of the issuer). This item includes treasury stock repurchased by the entity." Credit, instant.
- **FSN:** 916 companies; 863 latest. Statements: BS 914.
  - 23,207 label variants, because most labels embed the share terms. "common stock" (288), "common stock, value, issued" (78), "ordinary shares" (10, foreign-domiciled filers).
  - "#ref!" (7 companies) is a broken company label.
  - Calc parent: `StockholdersEquity` 792.
- **Decision:** excluded (detail of equity).
- **Exceptions:**
  - PGR files `CommonStockValueOutstanding` (586M; issued 798M shares including 212M treasury), not this tag.
  - AAPL files `CommonStocksIncludingAdditionalPaidInCapital` (93,568M).
  - LH puts this tag on the row labelled "Retained earnings" (label shift).
- **Era:** none.
- **Evidence:** FILING-CHECKED (JPM, CVX, MCK, MET, DHI, PLD, PCAR, PGR, AAPL).

### 10-13. CommonStockSharesAuthorized / CommonStockSharesIssued / CommonStockSharesOutstanding / CommonStockParOrStatedValuePerShare

- **Official** (shares and per-share types, no balance, instant):
  - Authorized: "maximum number of common shares permitted to be issued".
  - Issued: "includes common shares that were issued, repurchased and remain in the treasury".
  - Outstanding: "Number of shares of common stock outstanding".
  - Par: "Face amount or stated value per share of common stock".
- **FSN, companies (latest):**
  - Authorized: 941 (902). BS parenthetical 934, BS face 204. Labels "common stock, shares authorized (in shares)" etc.
  - Issued: 938 (902). BS parenthetical 926, EQ 140.
  - Outstanding: 842 (725). BS parenthetical 771, **EQ 497**, BS face 163. EQ labels "beginning/ending balance (in shares)" (about 290). Calc parent `CommonStockSharesIssued` (3 filings: outstanding = issued - treasury).
  - Par: 918 (879). No calc relationships.
- **Decision:**
  - `CommonStockSharesOutstanding`: map to `shares_outstanding_resolved`. Use the BS or BS-parenthetical value at the balance-sheet date. EQ roll-forward lines are the same tag; take one undimensioned value per date.
  - Authorized, Issued and Par: excluded (share terms).
- **Exceptions:**
  - PGR prints issued (798M) and treasury (212M) shares, but no outstanding count on the balance sheet. Outstanding is not presented on the BS (subtracting would be a derived instant); the dei cover count is the alternate source.
  - Multi-class filers (GOOGL, BRK) carry class members (cards/net-income-and-shares.md).
  - AAPL's BS face R5 prints the shares rows under the header "shares in Thousands" (14,773,260), while R6 prints 14,773,260,000. FSN stores the instance value, so do not apply the R-page display scale (mind lesson on EMR).
  - 2026 partial-year counts are lower (852/856/769) because FY2026 10-Ks were still arriving.
- **Era:** none.
- **Evidence:** FILING-CHECKED (AAPL, JPM, PGR, DHI, PCAR).

### 14. PreferredStockValue

- **Official:** "Aggregate par or stated value of issued nonredeemable preferred stock (or preferred stock redeemable solely at the option of the issuer)." Credit, instant.
- **FSN:** 599 companies; 484 latest. Statements: BS 598. 5,698 label variants, often "none issued".
  - Calc parent: `StockholdersEquity` 450. `LiabilitiesAndStockholdersEquity` in 2 latest and 7 fy16 filings: preferred shown outside the equity total.
- **Decision:** excluded as a displayed concept. **Do not use it as the preferred-equity deduction for book value per share without a face check.**
- **Exceptions:**
  - MET 0001099219-26-000013 R3: value 0, while the label states "$2,905 and $3,905, respectively, aggregate liquidation preference". The par of $0.01 rounds to 0, and the preferred sits in APIC.
  - JPM files preferred on `PreferredStockIncludingAdditionalPaidInCapitalNetOfDiscount` (20,045M), not this tag.
  - PLD carries it at the stated liquidation preference (63,948K).
  - Wisconsin Electric Power (not in cohort) shows it outside common equity.
- **Era:** none.
- **Evidence:** FILING-CHECKED (CVX, PLD, MCK, MET, DHI, JPM).

### 15-18. PreferredStockSharesAuthorized / Issued / Outstanding / ParOrStatedValuePerShare

- **FSN** (companies, latest): Authorized 619 (487), Issued 567 (425), Outstanding 484 (345), Par 567 (442). Almost all on the BS parenthetical; some on EQ (Outstanding 57).
- **Decision:** excluded (share terms).
- **Exceptions:** PCAR files `PreferredStockNoParValue` instead of the par tag.
- **Evidence:** FILING-CHECKED for Authorized, Issued and Par (JPM, CVX, DHI, PCAR). **Outstanding is DATA-INFERRED**: none of my opened filings printed it.

### 19. AdditionalPaidInCapital

- **Official:** "Amount of excess of issue price over par or stated value of stock and from other transaction involving stock or stockholder. Includes ... APIC for common and preferred." Credit, instant.
- **FSN:** 484 companies; 412 latest. Statements: BS 484.
  - Labels: "additional paid-in capital" (378), "additional paid in capital" (56), "capital in excess of par value" (18), "paid-in capital" (14), "capital surplus" (12).
  - Calc parent: `StockholdersEquity` 386.
- **Decision:** excluded (detail of equity).
- **Exceptions:** none beyond tag 20.
- **Era:** usage grows from 297 (FY2015) to 413 (FY2025) as some filers move from the common-only tag.
- **Evidence:** FILING-CHECKED (MCK, MET, PLD, PCAR).

### 20. AdditionalPaidInCapitalCommonStock

- **Official:** the same as tag 19, but "Includes only common stock transactions (excludes preferred...)". Credit, instant.
- **FSN:** 544 companies; 490 latest. Labels as tag 19, plus "capital in excess of par value" (48) and "paid-in capital" (33).
- **Decision:** excluded.
- **Exceptions:** LH's shifted statement happens to keep the right label on this row ("Additional paid-in capital", 0 against a prior 38.4M). The rows around it are shifted. Values follow the tag.
- **Evidence:** FILING-CHECKED (JPM, CVX, PGR, DHI).

### 21-23. TreasuryStockValue / TreasuryStockCommonValue / TreasuryStockCommonShares

- **Official:**
  - TreasuryStockCommonValue: "Amount allocated to previously issued common shares repurchased by the issuing entity and held in treasury". Debit, instant.
  - TreasuryStockValue: the same definition for all classes. Debit (read on MET/DHI pages).
  - TreasuryStockCommonShares: shares.
- **FSN** (companies, latest BS):
  - TreasuryStockValue: 528 (221). 16,557 of 17,202 lines negated on the face; calc weight -1 under `StockholdersEquity` (203 latest).
  - TreasuryStockCommonValue: 330 (285).
  - TreasuryStockCommonShares: 513 (444). BS parenthetical 477, EQ 215.
- **Decision:** excluded (detail of equity; not a buyback source). Sign: the stored value is positive, as a debit balance; equity subtracts it.
- **Era break (DATA-INFERRED):** most filers moved from `TreasuryStockValue`/`TreasuryStockShares` to `TreasuryStockCommonValue`/`TreasuryStockCommonShares` in FY2022-2023.
  - TreasuryStockValue: 444 companies (FY2022) to 308 (FY2023) to 221 (FY2026).
  - TreasuryStockCommonValue: 47 (FY2021) to 179 (FY2022) to 298 (FY2026).
  - In FY2016 10-Ks, `TreasuryStockShares` (not in this group) was on 351 balance sheets.
  - A treasury series must read the old and new tags as one period-scoped set.
- **Exceptions:** PGR nets treasury into `CommonStockValueOutstanding`; there is no treasury value line.
- **Evidence:** FILING-CHECKED (MET, DHI for the old tag; JPM, CVX, MCK for the common tags; JPM, PGR, DHI for the shares).

### 24. CommitmentsAndContingencies

- **Official:** "Represents the caption on the face of the balance sheet to indicate that the entity has entered into (1) purchase or supply arrangements ... and (2) is exposed to potential losses..." Credit, instant.
- **FSN:** 806 companies; 756 latest. Labels: "commitments and contingencies (note N)". Calc child of `LiabilitiesAndStockholdersEquity` in 653 latest 10-Ks.
- **Decision:** excluded. It is a caption, normally nil.
- **Exceptions:** when it carries a value, it is not a liability total. A face sum that includes it must treat nil as 0; never treat it as a debt or reserve.
- **Evidence:** FILING-CHECKED (AAPL, JPM, PGR, MCK, MET, DHI: all nil).

### 25. OtherLiabilitiesNoncurrent

- **Official:** "Amount of liabilities classified as other, due after one year..." Credit, instant.
- **FSN:** 778 companies; 740 latest. Labels: "other long-term liabilities" (292), "other liabilities" (233), "other non-current/noncurrent liabilities" (235), "other" (32), "deferred credits and other liabilities" (3+).
  - Calc parents: `Liabilities` 513, `LiabilitiesAndStockholdersEquity` 112, `LiabilitiesNoncurrent` 103, `LiabilitiesOtherThanLongtermDebtNoncurrent` 15.
- **Decision:** excluded. It is a component of total liabilities, and it is never debt.
- **Exceptions:**
  - LH puts this tag on the row labelled "Commitments and contingent liabilities" (528.2M, label shift).
  - In some filers' calc trees it is the parent of `OperatingLeaseLiabilityNoncurrent` (79 latest). A face sum must not add both.
- **Evidence:** FILING-CHECKED (AAPL, MCK, PCAR, MUR, LH).

### 26. AccountsPayableCurrent

- **Official:** "Carrying value ... of liabilities incurred (and for which invoices have typically been received) and payable to vendors for goods and services received ... current portion." Credit, instant.
- **FSN:** 692 companies; 657 latest. Labels: "accounts payable" (642), "trade accounts payable" (22), "trade payables" (9).
  - Combined labels: "accounts payable and accrued liabilities" (3), "accounts and construction payable(s)" (3).
  - Calc parents: `LiabilitiesCurrent` 654, `AccountsPayableAndAccruedLiabilitiesCurrent` 38.
- **Decision:** map to `accounts_payable`. That is the only key in the catalogue; there is no `_resolved` key.
- **Exceptions:**
  - Lines whose label adds accrued liabilities are combined: no plain payables days (sector templates line 74).
  - In the 38 filings where the tag is a calc child of `AccountsPayableAndAccruedLiabilitiesCurrent`, check that the face line is not the combined parent.
  - MCK prints "Drafts and accounts payable" (59,973M) on this tag.
- **Evidence:** FILING-CHECKED (AAPL, CVX, MCK, LH).

### 27. DeferredIncomeTaxLiabilitiesNet

- **Official:** "Amount, after deferred tax asset, of deferred tax liability attributable to taxable differences with jurisdictional netting." Credit, instant.
- **FSN:** 601 companies; 524 latest. Labels: "deferred income taxes" (280), "deferred tax liabilities" (125), "...net" variants (about 140).
  - Calc parents: `Liabilities` 351, `LiabilitiesAndStockholdersEquity` 77, `LiabilitiesNoncurrent` 74. `DeferredTaxAssetsLiabilitiesNet` 43, all at weight -1: these are note calcs.
- **Decision:** excluded (no catalogue concept).
- **Era break (DATA-INFERRED):** FY2015 16 companies, FY2019 311, FY2020 480.
  - FY2016 balance sheets used `DeferredTaxLiabilitiesNoncurrent` (345 companies), as LW's 2017 10-Q still does.
  - A future concept must take the pair as a period-scoped set.
- **Evidence:** FILING-CHECKED (CVX, MCK, MET, MUR; LW for the predecessor).

### 28-29. OperatingLeaseLiabilityNoncurrent / OperatingLeaseLiabilityCurrent

- **Official:** "Present value of lessee's discounted obligation for lease payments from operating lease, classified as noncurrent / current." Credit, instant.
- **FSN:**
  - Noncurrent: 526 companies (480 latest). Labels "operating lease liabilities" (159), "long-term operating lease liabilities" (92), "long-term lease liabilities" (17), "lease liabilities" (12).
  - Current: 359 (319). Labels "operating lease liabilities" (108), "current portion of operating lease liabilities" (69).
  - Calc parents include `OperatingLeaseLiability` (347; the lease-note sum), `OtherLiabilitiesNoncurrent` (79), `AccruedLiabilitiesCurrent` (74) and `OtherLiabilitiesCurrent` (56): often nested inside an "other" or "accrued" line.
- **Decision:** excluded. It is **not debt** (founder 2026-11-01 and 2026-11-04; debt.md). No catalogue concept.
- **Exceptions:**
  - Labels "lease liabilities" / "long-term lease liabilities" may also hold finance leases. ASSUMED, not checked: check for a separate `FinanceLeaseLiability*` line before relying on that.
  - PINS 2019 printed "Operating lease liabilities" against `LiabilitiesCurrent` (DATA-INFERRED).
- **Era:** from FY2019 (ASC 842). Noncurrent: 5 companies in FY2018, 344 in FY2019.
- **Evidence:** FILING-CHECKED (MCK, LH, MUR).

### 30-31. LongTermDebtNoncurrent / LongTermDebtCurrent

- **Official:** "Amount, after deduction of unamortized premium (discount) and debt issuance cost, of long-term debt classified as noncurrent / current. Excludes lease obligation." Credit, instant.
- **FSN:**
  - Noncurrent: 556 companies (416 latest; 415 on the face). Labels "long-term debt" (363), "long-term debt, net" (61), "...less/net of current portion/maturities" (about 125), "long-term borrowings" (12), "debt" (7).
  - Current: 428 (251). Labels "current portion of long-term debt" (209), "current maturities of long-term debt" (77). Also **"short-term debt" (14)**, "short-term borrowings" (4) and "short-term debt and current portion of long-term debt" (5).
  - Calc parents: `Liabilities` / `LiabilitiesCurrent`, plus **`LongTermDebt` (175 / 165 latest)**, `DebtCurrent` (20), `DebtLongtermAndShorttermCombinedAmount` (20).
- **Decision:** map to `total_debt_resolved` as a component of the sum (slot borrowing, sign +1). The CSV writes this as `map` with the sign rule "component sum". It is not `combined` in the FSN sense of a line that spans several concepts.
- **Exceptions:**
  - Never add a `LongTermDebt` fact from the same filing (debt.md).
  - Lines labelled "short-term debt" on `LongTermDebtCurrent` are still debt for the total, but not "current maturities".
  - MCK uses `LongTermDebtAndCapitalLeaseObligations(Current)` instead.
  - LH prints current debt on a custom tag, `lh_CurrentDebtExcludingFinanceLeaseLiability` (1,399.9M), beside separate finance-lease lines.
  - Wisconsin Electric Power (not in cohort) prints `LongTermDebtCurrent`/`Noncurrent` beside `FinanceLeaseLiabilityCurrent`/`Noncurrent`. Both pairs feed total debt.
- **Era:** none.
- **Evidence:** FILING-CHECKED (AAPL, LH; the WEPCo layout example).

### 32. AccruedLiabilitiesCurrent

- **Official:** "Carrying value ... of obligations incurred and payable, pertaining to costs that are statutory in nature, are incurred on contractual obligations, or accumulate over time and for which invoices have not yet been received..." Credit, instant.
- **FSN:** 438 companies; 363 latest. Labels: "accrued liabilities" (148), "accrued expenses" (140). Combined labels: "accrued expenses and other current liabilities" (80), "accrued and other current liabilities" (25). Also "other current liabilities" (5).
  - Calc parents: `LiabilitiesCurrent` 364; `AccountsPayableAndAccruedLiabilitiesCurrent` 13.
- **Decision:** excluded (component; no concept).
- **Exceptions:** the "and other" labels are combined lines, so never pair them with `OtherLiabilitiesCurrent` as a separate "other" amount.
- **Evidence:** FILING-CHECKED (CVX, MCK, LH, LW).

### 33. OtherLiabilitiesCurrent

- **Official:** "Amount of liabilities classified as other, due within one year..." Credit, instant.
- **FSN:** 380 companies; 343 latest. Labels: "other current liabilities" (282), "other" (32), "other accrued liabilities" (18), "accrued expenses and other current liabilities" (12).
  - Calc parents: `LiabilitiesCurrent` 342, `AccruedLiabilitiesCurrent` 15.
- **Decision:** excluded.
- **Exceptions:** AAPL "Other current liabilities" (66,387M) is larger than its payables. It is a large residual; never use it as a debt or accrual concept.
- **Evidence:** FILING-CHECKED (AAPL, WFRD; the WEPCo layout example).

---

## Disagreements with the library

Sources compared:
- Mac Ritwik: `origin/work/tag-library/ranks-1-50` @ aea0cf4, `data-team/47-fsn-store/company_tag_map/ranks_1_50.csv`.
- Cloud Ritwik: `origin/work/ritwik-cloud/tag-decisions-2026-11-11` @ 83bc4988, `data-team/tags/decisions/card-notes-51-100-2026-11-11.md` and `companies-51-100-exceptions-2026-11-11.csv`.

| # | Library row | This card | Evidence |
|---|---|---|---|
| D1 | Mac: `LongTermDebtCurrent` (14 companies) and `LongTermDebtNoncurrent` (29) are `excluded / detail_of_printed_total`. The file has **no `total_debt_resolved` row at all** for ranks 1-50 | They are `total_debt_resolved` components (slot borrowing). Excluding them as "detail of total liabilities" leaves total debt unseeded for the top 50 (AAPL, AMZN, CSCO, MSFT, ...). The other debt lines (ShortTermBorrowings, CommercialPaper, FinanceLeaseLiability*) need the same review | AAPL R5: commercial paper 7,979 + term debt 12,350 + 78,328 is total debt with no total line (debt.md section 3) |
| D2 | Mac: `AccountsPayableCurrent` maps to the legacy `accounts_payable` (concept id 78) while every other BS concept uses a `*_resolved` key | No disagreement on meaning. The catalogue lacks `accounts_payable_resolved`: decide one key before seeding | `analytics.canonical_concept` read 2026-11-11 |
| D3 | Live `fsn.concept_rule` `total_liabilities_resolved` priorities 20-22 (`bs.liab_zone_after_assets@1`, `bs.liab_cal_child@1/@2`) sum face liability lines. Cloud marks companies with no line `not_presented` | Agrees with cloud: under "no derived instants", a face sum is a derived instant and the 217 companies are blank with a reason. **One ruling is needed**: either retire rules 20-22, or rule that a sum of printed face lines is not "derived". The same question applies to `total_debt` (`combination_mode = sum`) | doc 02 (2026-11-01 item 4); `fsn.concept_rule` read 2026-11-11 |
| D4 | Mac: several rows of my tags have an empty decision: `CommitmentsAndContingencies` (AVGO, UNH), `CommonStockValue` BS (GOOG), `LongTermDebtCurrent`/`Noncurrent` (GE), and all EQ/CI rows of `CommonStockSharesOutstanding` (28 companies), `CommonStockSharesIssued` (7), `PreferredStock*` | Every row needs a decision. My verdicts: EQ roll-forward lines excluded (`equity_rollforward_balance`); GE's long-term debt lines are total_debt components; Commitments excluded | FSN statement counts above |
| D5 | Mac: `PreferredStockValue` excluded as a detail (25 companies). Book value per share (mind rule, JPM) needs a preferred deduction | Not a mapping disagreement, but a trap. A future `preferred_equity` concept must not read `PreferredStockValue` at face value: MET shows 0 against a $2,905M liquidation preference, and JPM uses another tag | MET R3; JPM R4 |
| D6 | Mac: `Liabilities` maps to `total_liabilities_resolved` (38 companies) with no stated dimension filter | Agree, provided the rows take undimensioned values only. JPM's VIE "Total liabilities" (28,837M) sits on the same face. ASSUMED that the library filters on dim 0 (not read in library.py) | JPM R4 |
| D7 | Cloud: QCOM `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` maps, "Tag Expert to confirm" | **Confirmed as DATA-INFERRED, not opened.** In 35 QCOM filings (2022 on) there is no `StockholdersEquity` line and no `MinorityInterest` line on the BS. In the 12 earlier filings (2015-2017) all three lines print, so those take `StockholdersEquity` | `fsn.line` per-filing check |
| D8 | Cloud rule 8 and Mac (`parent_equity_not_printed` for CAT, PG, UNH; JNJ, AVGO, V mapped only where no parent line) | Agree. My per-filing check found no JNJ/AVGO/V filing where incl-NCI is the only equity line while an NCI line exists | `fsn.line` per-filing check |
| D9 | Cloud: `not_presented total_liabilities` for GILD, ADI, VZ, ABT, MCD, TMUS, ETN, ACN, VLO | Agree. ABT and VZ are also in my 217 | `fsn.value` latest 10-K |

No disagreement found on: Liabilities and LiabilitiesCurrent as the total keys; `StockholdersEquity` BS-only (Mac excludes the EQ roll-forward rows); the share-terms and equity-detail exclusions.

## Open items

- Value checks for the label-disagreeing `LiabilitiesCurrent` periods (NFG, PINS 2019, HQY 2015, BMNR 2022, FOX 2020-21). The LH and MUR cases show the label can be the thing that is wrong.
- `PreferredStockSharesOutstanding`: open one filing.
- Catalogue: `noncontrolling_interest`, `preferred_equity`, `accounts_payable_resolved` and `deferred_tax_liabilities` are proposals only.
