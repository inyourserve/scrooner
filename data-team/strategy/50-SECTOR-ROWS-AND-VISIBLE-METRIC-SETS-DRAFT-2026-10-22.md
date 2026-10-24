# 50. Sector rows and visible metric sets per group: PROPOSAL v0 (Ritwik, Head of Data Product, 2026-10-22)

Status: DRAFT proposal, not approved. Delivered to the Standardization Lead and the Data Chief ahead of G+2 (Sector Analyst condition 1; plan doc 49 section 2.1 and 7.9). Purpose: give D1 (template cells) a catalog that contains the rows that DEFINE each sector template, so a bank template cannot reach 100% without a net-interest-income cell. Product choices are mine to recommend; row formulas and any REPLACED cell need the Standardization Lead and the named accountant; tag candidates are leads for the Tag Expert, unverified. Evidence: R4 section 3/5 (per-family presence rates from FSDS, DATA-INFERRED), S2 (audit, FILING-CHECKED at Popular, Skyward, ESRT, USB), S3, doc 41 section 5.

## 1. Rules for the catalog (so it stays small and testable)
1. **A sector row exists only if it is a face-statement line or an arithmetic combination of face lines** of the group's own statements. Nothing from MD&A, press releases or vendors (no AUM, combined ratio, FFO/AFFO unless presented on the face, same-store, NIM unless average earning assets are filed).
2. **Product guardrail (doc 02):** about 18 visible metrics per group. Sector rows REPLACE the cells that do not apply; they do not add to the visible set beyond 18.
3. **Rule codes:** REQ required; REP replaced by a group definition (accountant); COND applies only when an evidenced condition holds; NIT not in template. A row's tag column is a candidate only.
4. **Every sector row is versioned in `catalog_version`;** D1 is defined over it (doc 49 section 2.1). Rows whose formula needs an accountant ruling stay `definition_pending` and are defects, not blanks, until approved.
5. Rows count about 66 below; the Standardization Lead trims or merges to about 60 by G+3.

## 2. Sector rows (ID, group, line, formula or face source, rule, candidate tag lead)
| ID | Group | Row | Formula / face source | Rule | Tag lead (unverified) |
|---|---|---|---|---|---|
| B1 | bank | Net interest income | face line | REQ | InterestIncomeExpenseNet (filed by 343 of 349 banks, R2/Tag Mapper) |
| B2 | bank | Total interest income | face line | REQ | InterestAndDividendIncomeOperating |
| B3 | bank | Total interest expense | face line | REQ | InterestExpense |
| B4 | bank | Noninterest income | face line | REQ | NoninterestIncome |
| B5 | bank | Noninterest expense | face line | REQ | NoninterestExpense |
| B6 | bank | Provision for credit losses | face line | REQ | ProvisionForCreditLosses / ProvisionForLoanLeaseAndOtherLosses (era split) |
| B7 | bank | Bank revenue | B1 + B4 | REP (accountant) | derived |
| B8 | bank | Efficiency ratio | B5 / B7 | REQ after B7 approved | derived |
| B9 | bank | Total deposits | face line | REQ | Deposits |
| B10 | bank | Loans, net | face line | REQ | LoansAndLeasesReceivableNetReportedAmount |
| B11 | bank | Loans to deposits | B10 / B9 | REQ | derived |
| B12 | bank | Allowance for credit losses | face or note | COND (presented) | AllowanceForLoanAndLeaseLosses... |
| B13 | bank | Equity to assets | total equity / total assets | REQ | derived (existing concepts) |
| B14 | bank | Return on assets | net income / average total assets | REQ | derived (existing concepts) |
| B15 | bank | Tangible book value per share | (equity - goodwill - intangibles) / shares | COND (goodwill presented) | derived |
| I1 | insurer | Premiums earned | face line | REQ | PremiumsEarnedNet |
| I2 | insurer | Net investment income | face line | REQ | NetInvestmentIncome |
| I3 | insurer | Total revenues | face line | REQ | Revenues (on the face for 98% of insurers) |
| I4 | insurer | Losses and LAE incurred | face line | REQ | PolicyholderBenefitsAndClaimsIncurredNet / IncurredClaimsPropertyCasualtyAndLiability |
| I5 | insurer | Policy acquisition costs | face line | COND (presented) | DeferredPolicyAcquisitionCostAmortizationExpense |
| I6 | insurer | Reserves for unpaid losses | face line | REQ | LiabilityForClaimsAndClaimsAdjustmentExpense |
| I7 | insurer | Loss ratio | I4 / I1 | COND (P&C and health where both inputs exist) | derived |
| I8 | insurer | Book value per share | equity / shares | REQ | derived (existing) |
| I9 | insurer | Return on equity | existing ROE | REQ | existing |
| M1 | managed care | Premiums revenue | face line | REQ | PremiumsEarnedNet / HealthCarePremiumRevenue... |
| M2 | managed care | Medical costs | face line | REQ | PolicyholderBenefitsAndClaimsIncurredHealthCare... |
| M3 | managed care | Medical loss ratio | M2 / M1 | REQ | derived |
| R1 | equity REIT | Rental revenue | face line | REQ | OperatingLeasesIncomeStatementLeaseRevenue / RealEstateRevenueNet |
| R2 | equity REIT | Property operating expenses | face line | COND (presented) | direct costs of leased property |
| R3 | equity REIT | Net operating income | R1 - R2 | COND (both presented) | derived |
| R4 | equity REIT | Real estate at cost | face or note | REQ | RealEstateInvestmentPropertyAtCost |
| R5 | equity REIT | Accumulated depreciation | face or note | REQ | RealEstateInvestmentPropertyAccumulatedDepreciation |
| R6 | equity REIT | General and administrative | face line | REQ | GeneralAndAdministrativeExpense |
| R7 | equity REIT | Debt to total assets | total debt / total assets | REQ | derived (needs debt definition, AC card) |
| R8 | equity REIT | Capex definition (improvements vs acquisitions) | accountant | REP (accountant) | definition_pending |
| MR1 | mortgage REIT | Interest income | face line | REQ | InterestIncomeOperating / InterestAndDividendIncomeOperating |
| MR2 | mortgage REIT | Interest expense | face line | REQ | InterestExpense |
| MR3 | mortgage REIT | Net interest income | MR1 - MR2 | REQ | derived |
| MR4 | mortgage REIT | Book value per share | equity / shares | REQ | derived |
| MR5 | mortgage REIT | Recourse leverage (repurchase agreements / equity) | face lines | COND (repos presented) | derived |
| MR6 | mortgage REIT | Dividends per share | existing | REQ | existing |
| F1 | BDC / fund | Total investment income | face line | REQ | GrossInvestmentIncomeOperating (78% of BDCs) |
| F2 | BDC / fund | Net investment income | face line | REQ | NetInvestmentIncome |
| F3 | BDC / fund | Net assets | face line | REQ | AssetsNet |
| F4 | BDC / fund | Net asset value per share | face or note | REQ | NetAssetValuePerShare |
| F5 | BDC / fund | Investments at fair value | face line | REQ | InvestmentOwnedAtFairValue |
| F6 | BDC / fund | NII per share | F2 / shares | REQ | derived |
| F7 | BDC / fund | Price to NAV | price / F4 | REQ | derived (price vendor, Alpaca) |
| F8 | BDC / fund | Distributions per share | face or note | REQ | DistributionsPerShare... |
| A1 | asset manager | Management and advisory fees | face line | COND (presented) | InvestmentAdvisoryFees / AssetManagementFees |
| A2 | asset manager | Compensation and benefits | face line | COND (presented) | LaborAndRelatedExpense |
| A3 | asset manager | Compensation ratio | A2 / total revenues | COND | derived |
| A4 | asset manager | Operating margin | existing | REQ | existing |
| BD1 | broker-dealer | Net revenues | face line | COND (presented) | RevenuesNetOfInterestExpense |
| BD2 | broker-dealer | Compensation ratio | compensation / net revenues | COND | derived |
| BD3 | broker-dealer | Return on equity | existing | REQ | existing |
| P1 | pre-revenue overlay | Cash and short-term investments | face lines | REQ | CashCashEquivalentsAndShortTermInvestments (new concept) |
| P2 | pre-revenue overlay | Operating cash burn (TTM) | -(CFO TTM) | REQ | existing |
| P3 | pre-revenue overlay | Runway months | P1 / monthly burn | COND (only if burn > 0, formula disclosed as ours) | derived |
| P4 | pre-revenue overlay | Accumulated deficit | face line | REQ | RetainedEarningsAccumulatedDeficit (new concept) |
| P5 | pre-revenue overlay | R&D expense | existing | REQ | existing |
| P6 | pre-revenue overlay | Share dilution (shares growth YoY) | existing | REQ | existing |
| P7 | pre-revenue overlay | Equity proceeds | cash-flow line | COND (presented) | ProceedsFromIssuanceOfCommonStock (new concept) |
| U1 | utility | Utility plant, net | face line | COND (presented) | PublicUtilitiesPropertyPlantAndEquipmentNet |
| U2 | utility | Regulatory assets | face line | COND (presented) | RegulatoryAssets |
| U3 | utility | Capex intensity | capex / revenue | REQ | existing |
| L1 | MLP / midstream | Partners' capital | face line | REQ | PartnersCapital (vocabulary gap, E5) |
| L2 | MLP / midstream | Distributions per unit | face or note | REQ | DistributionMadeToLimitedPartnerDistributionsPaidPerUnit |
| L3 | MLP / midstream | Payout vs operating cash flow | distributions / CFO | COND | derived (not FFO/DCF) |
Total 66 proposed rows. Excluded by rule 1: combined ratio, NIM (needs average earning assets), FFO/AFFO, AUM, same-store, production volumes, rate base.

## 3. Visible metric set per group (recommendation; the ~18 guardrail holds)
Core cells shown for every group where they apply: market cap, P/E (trailing, only on positive earnings), P/B, ROE, EPS growth (annual or TTM only), dividend yield (COND payers, else evidenced "No dividend"), revenue growth, net margin.
| Group | Visible set (recommended) | Not in template |
|---|---|---|
| Corporate (utility, energy, midstream variants) | the 18 V1 metrics (doc 02), plus utility U3 and MLP L1-L3 where applicable | none |
| Bank | market cap, P/E, P/B, ROE, ROA, EPS growth, dividend yield, bank revenue, revenue growth, net margin on bank revenue, NII, noninterest income, efficiency ratio, loans to deposits, equity to assets, tangible book value per share, allowance (COND), provision | gross and operating margin, ROIC, current ratio, inventory, FCF family, interest coverage, EBITDA family |
| Insurer | market cap, P/E, P/B, ROE, EPS growth, dividend yield, total revenues, revenue growth, net margin, premiums earned, net investment income, loss ratio (COND), reserves, book value per share | gross margin, operating margin, current ratio, inventory, FCF family |
| Managed care | corporate set + premiums revenue, medical loss ratio | gross margin where the cost line is medical costs |
| Equity REIT | market cap, P/B, ROE, EPS growth, dividend yield, rental revenue, NOI (COND), debt to total assets, net margin, revenue growth, G&A, real estate at cost, accumulated depreciation | current ratio, inventory, R&D, gross margin |
| Mortgage REIT | market cap, P/B, book value per share, dividend yield, ROE, interest income, net interest income, recourse leverage (COND) | gross/operating margin, ROIC, coverage, current ratio |
| BDC / fund | market cap, price to NAV, NAV per share, NII per share, total investment income, net investment income, distributions per share, dividend yield | gross margin, ROIC, FCF family, current ratio |
| Asset manager / broker-dealer / exchange | corporate set minus gross margin, plus fees and compensation ratio (COND) | gross margin; exchanges follow corporate |
| Pre-revenue overlay | cash and short-term investments, cash burn, runway (COND), accumulated deficit, R&D, share dilution, equity proceeds (COND), market cap | every revenue-denominated ratio; exits the overlay the first fiscal year revenue is presented |
| Non-screener (SPAC, trust, ABS) | one stated reason + trust assets | all |

## 4. Open questions for the Standardization Lead and the Chief (smallest set)
1. Hybrid-precedence rule for companies with two shapes (CVS, PCAR, KKR, APO, AMP, BRK-A, captive finance CAT/DE/F/GM): template by dominant face shape, overlay rows for the second shape; confirm.
2. $1M revenue floor for the pre-revenue overlay (Sector Analyst): confirm or replace by "no revenue line on the face".
3. New concepts needed (no existing canonical concept): cash and short-term investments, accumulated deficit, equity proceeds, partners' capital; confirm names and period basis.
4. B7 bank revenue, R8 capex, R7 debt definition, I-row composition: REP rows need the accountant; until named they are `definition_pending` defects, not blanks.
5. Tag Expert: single-tag candidates for each row (including the tag that feeds `bdc_total_investment_income` at 24 insurers, which my draft BDC rule mistook as a BDC signal).

---
## v1 CORRECTIONS (2026-10-23, Ritwik) from the Sector Analyst's review of this draft
Source: the one-paragraph summary in `doc/data-moat/team/PLAN.md` (line 244, "D. Doc 50 review (team/SECTOR-ROWS-REVIEW.md)"). **The review file itself is not in my tree; I applied only what that summary states. Nothing below is verified by me against a filing, and the catalog stays NOT FINAL until the Sector Analyst re-reviews it** (Dhairya excluded it from the freeze-register approval for this reason). Row IDs refer to section 2 above.
1. **Four groups had no defining sector row:** non-bank lender, crypto/digital, exchange, insurance broker. They get NO rows in this draft; the Sector Analyst and Tag Expert define face-line rows for them. Candidates must be face lines or arithmetic on face lines; the review says asset-manager fee, exchange clearing and broker fiduciary lines exist only as extension tags (filing-instance capture or `data_limit`), so they cannot be required rows until capture exists.
2. **Tag leads withdrawn or changed (all were leads, never verified):**
   - B3 total interest expense: my lead `InterestExpense` is replaced by `InterestExpenseOperating` (per the review).
   - B10 loans, net: the lead is wrong after CECL (post-CECL net-loan presentation differs); lead withdrawn until the Tag Expert gives the post-CECL tag.
   - B12 allowance: the allowance name appears on the face of 0 of 1,027 filers; B12 becomes note-sourced only, not a face row, so it is `COND` on a note capture and not required.
   - F2 BDC net investment income: `NetInvestmentIncome` is the PRE-tax BDC line (ARCC 0001287750-26-000006 R5: 1,458.0M vs after-tax 1,415.0M) and the same tag name carries an insurer's investment return at 35 of 40 insurers: two meanings. F2 must state which BDC measure it is; the lead is withdrawn until the definition is chosen. This probably also explains why 24 insurers fed `bdc_total_investment_income` (hypothesis; not queried; Tag Expert).
   - F3 net assets: `AssetsNet` appears on 0 of 2 BDCs; lead withdrawn.
   - U2 regulatory assets: plain `RegulatoryAssets` on 0 of 32 utilities; lead withdrawn.
   - M1/M2 managed care: managed care uses the insurer tags; the managed-care lead rows are withdrawn and the group reuses insurer rows I1-I4 where the face shows them.
   - Crypto/digital: the lead should be the `CryptoAssetFairValue*` family (no row defined yet).
3. **Collision:** the existing registry row `net_interest_income` (mapped to `InvestmentIncomeInterest`) collides with the new bank NII row B1 (`InterestIncomeExpenseNet`). One of them is renamed before B1 is created; the Standardization Lead decides.
4. **Effect on the catalog:** rows B10, B12, F2, F3, U2, M1, M2 are not required until re-defined; the proposed count of 66 is therefore overstated by at least those seven rows plus any row the four new groups need. The visible metric sets in section 3 that cite those rows are provisional.
Owner of the next version: the Sector Analyst with the Tag Expert and the Standardization Lead; me for the visible metric sets. This correction closes blocker-list item PR1 only after that re-review.
