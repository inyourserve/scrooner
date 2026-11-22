# Card family: Premiums and claims (insurers and managed care) (written 2026-10-22 by the Tag Expert)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Tags: `us-gaap:PremiumsEarnedNet`, `PolicyholderBenefitsAndClaimsIncurredNet`, `PolicyholderBenefitsAndClaimsIncurredHealthCare` (deprecated), `HealthCareOrganizationPremiumRevenue` (not in the 2025/2026 taxonomy), `BenefitsLossesAndExpenses`, `Revenues` at insurers. Investment income is in `investment-income-and-funds.md`.
Asked by: Sector Analyst, SECTOR-ROWS-REVIEW rows I1, I4, M1, M2 and section 8 item 2.
Method: FASB 2026 schema and documentation labels; `sec_tag_library` and `company_sec_tag` (one read-only connection); 2 filings opened (UNH, PGR).

## 1. Official meaning (FASB 2026)
| Tag | Period / balance | Definition | Status |
|---|---|---|---|
| PremiumsEarnedNet | duration / credit | "Amount, after premiums ceded to other entities and premiums assumed by the entity, of premiums earned." | current |
| PolicyholderBenefitsAndClaimsIncurredNet | duration / debit | "Amount, after effects of policies assumed or ceded, of expense related to the provision for policy benefits and costs incurred." | current |
| PolicyholderBenefitsAndClaimsIncurredHealthCare | duration / debit | standard label "Policyholder Benefits and Claims Incurred, Net, Health **(Deprecated 2024)**" | deprecated 2024; still in the 2026 schema as deprecated |
| HealthCareOrganizationPremiumRevenue | n/a | **not an element of the 2025 or 2026 us-gaap schema** (a removed older element: 3 companies, 73 facts, last period 2018-03-31 in `sec_tag_library`, MOH among them; keep for old periods) | removed |

## 2. Who reports it (DATA-INFERRED, read 2026-10-22)
| Tag | Companies (active) | Facts | Last period | Mapping |
|---|---|---|---|---|
| PremiumsEarnedNet | 132 (132) | 8,999 | 2026-09-30 | unmapped |
| PolicyholderBenefitsAndClaimsIncurredNet | 120 (120) | 7,572 | 2026-09-30 | unmapped |
| PolicyholderBenefitsAndClaimsIncurredHealthCare | 8 (8) | 466 | **2024-03-31** | unmapped |
Managed-care filers (UNH, CVS, CI, ELV, HUM, CNC, MOH, OSCR): all 8 have `PremiumsEarnedNet`, `PolicyholderBenefitsAndClaimsIncurredNet` and `Revenues` in their history; 5 also have the deprecated health tag (UNH, CVS, CNC, HUM, MOH), last used 2024-03-31; MOH also has the removed `HealthCareOrganizationPremiumRevenue`.

## 3. How filers use it
| Filing | Rows | Finding |
|---|---|---|
| UNH 10-K 0000731766-26-000062 (unh-20251231.htm) (me) | "Premiums" `PremiumsEarnedNet` 352,229M (FY2025; segment members 332,390M / 19,839M); "Medical costs" `PolicyholderBenefitsAndClaimsIncurredNet` 313,995M; "Total revenues" `Revenues` 447,567M; the deprecated health tag is not used | managed care uses the general insurer tags |
| PGR 10-K 0000080661-26-000086 R3 (me) | "Net premiums earned" `PremiumsEarnedNet` 81,661M; "Losses and loss adjustment expenses" `PolicyholderBenefitsAndClaimsIncurredNet` 53,959M; "Total revenues" `Revenues` 87,671M; "Total expenses" `BenefitsLossesAndExpenses` 73,448M | P&C layout |
| CNC 10-K 0001071739-26-000049 R5 (relayed, Standardization Lead inbox 2026-10-21) | premium revenue filed on `RevenueFromContractWithCustomerExcludingAssessedTax` | a managed-care filer can put premiums on the ASC 606 tag; not re-opened by me |
Sector Analyst face counts (Reader 1, latest 10-K, FC by them): PremiumsEarnedNet 36/40 insurers and 6/7 managed care; PolicyholderBenefitsAndClaimsIncurredNet 33/40 and 6/7 ("Medical costs").

## 4. Siblings and confusables
- `PremiumsEarnedNet` (earned, net of reinsurance) vs `PremiumsWrittenNet` / `PremiumsWrittenGross` / `DirectPremiumsWritten` / `AssumedPremiumsWritten` / `CededPremiumsWritten` (written, not earned: never the revenue line).
- `PolicyholderBenefitsAndClaimsIncurredNet` (net of reinsurance) vs `...Gross` vs `IncurredClaimsPropertyCasualtyAndLiability` vs `BenefitsLossesAndExpenses` (TOTAL expenses at PGR, "Total operating expenses" at some managed-care filers: never the claims line).
- Health premium on `RevenueFromContractWithCustomerExcludingAssessedTax` (CNC, relayed).

## 5. Known misuses and quirks
- None found on the two tags in the filings opened. CNC (relayed) is a tag-choice quirk, not a misuse of these tags.

## 6. Mapping verdict
- `PremiumsEarnedNet` -> `sr.ins.premiums_earned` (insurer and managed care): **safe single tag where filed** for current periods (UNH, PGR FILING-CHECKED; 36/40 + 6/7 face counts by the Sector Analyst). Managed-care history before 2024 can sit on removed or deprecated health tags (MOH): period-scoped alternates are needed for the 2015+ window.
- `PolicyholderBenefitsAndClaimsIncurredNet` -> `sr.ins.benefits_claims_incurred`: **safe single tag where filed** (UNH "Medical costs", PGR "Losses and LAE" FILING-CHECKED). Before 2024, `PolicyholderBenefitsAndClaimsIncurredHealthCare` is the managed-care alternate (5 of 8 filers, DATA-INFERRED). Never `BenefitsLossesAndExpenses`.
- The draft leads M1/M2 (`HealthCarePremium...`, `...IncurredHealthCare`) are correct only for history: one is not an element, the other was deprecated in 2024. Confirms the Sector Analyst's merge of M1/M2 into I1/I4 for current periods.
- Verified by: Tag Expert (me), 2026-10-22.

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.91). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.91. 6 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `Revenues`
- **Meaning:** Revenues (us-gaap, duration, credit). Amount of revenue recognized from goods sold, services rendered, insurance premiums, or other activities that constitute an earning process. Includes, but is not limited to, investment and interest income before deduction of interest expens...
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** revenue; gross_profit
- **Rules:** X123
- **Evidence:** 69 companies, 708 served, 12391 proven, 34 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToRevenueNet@2013; CashFlowHedgeGainReclassifiedToRevenue@2013; CashFlowHedgeLossReclassifiedToRevenue@2013; DevelopmentStageEnterpriseCumulativeRevenue@2012 (+10 more)

### `RevenueFromContractWithCustomerExcludingAssessedTax`
- **Meaning:** Revenue from Contract with Customer, Excluding Assessed Tax (us-gaap, duration, credit). Amount, excluding tax collected from customer, of revenue from satisfaction of performance obligation by transferring promised good or service to customer. Tax collected from customer is tax assessed by governmental authority that is both i...
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** revenue; gross_profit
- **Rules:** none
- **Evidence:** 64 companies, 650 served, 16994 proven, 75 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InitialFranchiseFees@2026; PropertyManagementFeeRevenue@2026; RevenueRecognitionMilestoneMethodRevenueRecognized@2026

### `BenefitsLossesAndExpenses`
- **Meaning:** Benefits, Losses and Expenses (us-gaap, duration, debit). The total amount of expense recognized during the period for future policy benefits, claims and claims adjustment costs, and for selling, general and administrative costs.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#2
- **Rules:** I14; I09; I10; I11; I12; I13
- **Evidence:** 2 companies, 24 served, 101 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `PolicyholderBenefitsAndClaimsIncurredHealthCare`
- **Meaning:** Policyholder Benefits and Claims Incurred, Net, Health (Deprecated 2024) (us-gaap, duration, debit). Amount, after effect of policies assumed or ceded, of expense related to provision for policy benefits and costs incurred for health insurance contracts.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]
- **Data point:** operating_expenses
- **Rules:** none
- **Evidence:** 2 companies, 15 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaced by PolicyholderBenefitsAndClaimsIncurredNet@2024; [HealthInsuranceProductLineMember@2024; srt:ProductOrServiceAxis@2024; srt:ProductsAndServicesDomain]@2024

### `PolicyholderBenefitsAndClaimsIncurredNet`
- **Meaning:** Policyholder Benefits and Claims Incurred, Net (us-gaap, duration, debit). Amount, after effects of policies assumed or ceded, of expense related to the provision for policy benefits and costs incurred.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]
- **Data point:** operating_expenses
- **Rules:** none
- **Evidence:** 2 companies, 5 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces IncurredClaimsFinancialGuaranteeInsuranceContracts@2024; IncurredClaimsPropertyCasualtyAndLiability@2024; PolicyholderBenefitsAndClaimsIncurredHealthCare@2024; PolicyholderBenefitsAndClaimsIncurredLifeAndAnnuity@2024 (+2 more)

### `PremiumsWrittenNet`
- **Meaning:** Premiums Written, Net (us-gaap, duration, credit). Amount, after premiums ceded to other entities and premiums assumed by the entity, of premiums written.
- **Data point definition:** revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances;  excise follows the filer's own presentation (X56).
- **Data point:** revenue
- **Rules:** none
- **Evidence:** 1 companies, 1 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces PremiumsWrittenNetAccidentAndHealth@2013; PremiumsWrittenNetFinancialGuaranteeInsuranceContracts@2013; PremiumsWrittenNetLife@2013; PremiumsWrittenNetOtherInsurance@2013 (+1 more)
<!-- END GENERATED: tag library rows -->
