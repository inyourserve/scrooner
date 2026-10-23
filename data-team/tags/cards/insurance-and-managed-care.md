# Card family: Premiums and claims (insurers and managed care) (written 2026-10-22 by the Tag Expert)

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
