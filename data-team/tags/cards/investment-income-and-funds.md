# Card family: Investment income (insurers, BDCs, funds) and fund net assets (written 2026-10-22 by the Tag Expert)

Tags: `us-gaap:NetInvestmentIncome`, `GrossInvestmentIncomeOperating`, `InvestmentIncomeInvestmentExpense`, `InvestmentIncomeNet`, `InvestmentIncomeOperatingAfterExpenseAndTax`, `InvestmentIncomeOperatingTaxExpenseBenefit`, `AssetsNet`, `StockholdersEquity` (as BDC net assets), `NetAssetValuePerShare`, `InvestmentOwnedAtFairValue`.
Asked by: Sector Analyst, SECTOR-ROWS-REVIEW section 8 items 2-3 (branch work/sector-analyst/groups) and inbox line 2026-10-22 "concept bdc_total_investment_income".
Method: FASB 2026 taxonomy files (`elts/us-gaap-2026.xsd`, `us-gaap-doc-2026.xml`, `All_Traits_Dictionary.csv`, read 2026-10-22); one read-only DB connection (client backends 8-11, statement_timeout 20 s): `analytics.concept_mapping`, `canonical_fact`, `sec_tag_library`, `company_sec_tag`, and `core.fact` pairs chunked 40 companies at a time, periods from 2015-01-01, authoritative only, undimensioned only (companyfacts carries no dimensions); 6 filings opened (iXBRL primary document or R-file, declared User-Agent, <= 2 req/s). SIC families: insurer = 6300-6399; "null-SIC" = no SIC code, which is where BDCs sit in `core.company` (42 of the 118 filers of the gross tag; ARCC, MAIN, FSK, OBDC, ...).

## 1. Official meaning (FASB 2026)
| Tag | Period / balance / type | Definition (documentation label) | Traits |
|---|---|---|---|
| GrossInvestmentIncomeOperating | duration / credit / monetary | "Amount, **before investment expense**, of income earned from investments in securities and real estate. Includes ... real estate investment, policy loans, dividends, and interest. Excludes realized gain (loss) on investments." | Operating, Revenue |
| InvestmentIncomeInvestmentExpense | duration / debit / monetary | "Amount of expenses related to the generation of investment income." | Expense |
| NetInvestmentIncome | duration / credit / monetary | "Amount, **after investment expense**, of income earned from investments in securities and real estate. Includes ... policy loans, dividends, and interest. Excludes realized gain (loss) on investments." | Revenue |
| InvestmentIncomeNet | duration / credit / monetary | "Amount after accretion (amortization) of discount (premium), and investment expense, of interest income and dividend income on **nonoperating** securities." | Nonoperating, Revenue |
| InvestmentIncomeOperatingAfterExpenseAndTax | duration / credit / monetary | "Amount, after expense and tax, of investment income classified as operating. Excludes realized and unrealized gain (loss) on investment." | Operating, Revenue |
| InvestmentIncomeOperatingTaxExpenseBenefit | duration / debit / monetary | "Amount of tax expense (benefit) on investment income classified as operating ..." | Expense, Operating |
| AssetsNet | instant / debit / monetary | "Amount of net assets (liabilities)." | (not in the traits file) |
| StockholdersEquity | instant / credit / monetary | "Amount of equity (deficit) attributable to parent. Excludes temporary equity and equity attributable to noncontrolling interest." | Equity |
| NetAssetValuePerShare | instant / no balance / perShareItemType | "Net asset value per share or per unit of investments in certain entities that calculate net asset value per share ..." (written for investees measured at NAV, also filed by funds for their own NAV) | (not in the traits file) |
| InvestmentOwnedAtFairValue | instant / debit / monetary | "Fair value of investment in security owned." | Fair Value |
None is deprecated in 2026. The definition of `NetInvestmentIncome` is the insurer meaning (investment income net of INVESTMENT expense). A BDC that files its pre-tax operating result (income minus all fund expenses, including interest and management fees) on it stretches "investment expense" to every expense. The taxonomy itself gives BDCs `InvestmentIncomeOperatingAfterExpenseAndTax` for the after-tax line.

## 2. Who reports it (DATA-INFERRED, `analytics.sec_tag_library` / `company_sec_tag`, read 2026-10-22)
| Tag | Companies (active) | Facts | First / last period | Mapping status |
|---|---|---|---|---|
| GrossInvestmentIncomeOperating | 118 (118) | 3,676 | 2011-12-31 / 2026-06-30 | **approved, priority 1 for `bdc_total_investment_income`** (its only tag) |
| NetInvestmentIncome | 268 (268) | 11,101 | 2007-12-31 / 2026-09-30 | unmapped |
| InvestmentIncomeNet | 570 (566) | 18,591 | 2007 / 2026 | unmapped |
| InvestmentIncomeInvestmentExpense | 267 (264) | 7,946 | 2007 / 2026 | unmapped |
| InvestmentIncomeOperatingAfterExpenseAndTax | 49 (49) | 1,021 | **2020-09-30** / 2026 | unmapped |
| AssetsNet | 304 (304) | 3,183 | 2009 / 2026 | unmapped |
| NetAssetValuePerShare | 204 (203) | 3,064 | 2006 / 2026 | unmapped |
| InvestmentOwnedAtFairValue | 322 (320) | 3,854 | 2008 / 2026 | unmapped |

**Who files the gross tag (118 active companies, by SIC): insurers 63xx 47 (AFL, CB, CINF, PGR, PRU, TRV, VOYA, ...); null-SIC BDCs 42; SIC 62xx 12 (staking and commodity ETPs such as GSOL, ETHB, SOLC, plus KKR); SIC 6411 4 (ACT, ARX, BWIN, WTW); bank/credit 60-61 4 (NEWT, FGNX, SNFCA, SUIG); REIT 6798 2 (CMRF, HHH); 7 others (SPAC trust TVAI, BLZE, NXTT, VATE, VNOV, AFCG, HASI).** So only 42 of the 118 (36%) are BDCs. Note in `mapper/expanded_concepts.py` ~line 418: "Verified 2026-09-04 against 118 real active companies (35 of the original 44 hand-sampled BDCs, plus other closed-end funds)". The 118 are NOT BDCs plus closed-end funds; 47 are insurers.
`NetInvestmentIncome` by SIC (active companies with the tag): other 112, insurers 87, null-SIC 51, bank 11, REIT 7. `InvestmentIncomeOperatingAfterExpenseAndTax`: null-SIC 39, other 10 (a BDC/fund tag).

## 3. How filers use it (filings opened by me unless marked)
| Filing | Rows (tag, value) | Finding |
|---|---|---|
| CINF 10-K 0000020286-26-000008 (cinf-20251231.htm, investment income note and income statement) | Note: "Total" `GrossInvestmentIncomeOperating` 1,182M (FY2025), "Less investment expenses" `InvestmentIncomeInvestmentExpense` 17M, "Total" `NetInvestmentIncome` 1,165M; face "Investment income, net of expenses" `NetInvestmentIncome` 1,165M | **insurer: gross = note line before investment expenses; NII = face revenue line** |
| TRV 10-K 0000086312-26-000065 (trv-20251231.htm) | Note rows by investment type on `GrossInvestmentIncomeOperating` with a member (fixed maturities 3,433M, short-term 253M ...); "Investment expenses" 53M; "Net investment income" `NetInvestmentIncome` 3,959M. Stored undimensioned gross 4,012M = 3,959 + 53 | same pattern |
| PRU 10-K 0001137774-26-000048 (pru-20251231.htm) | Gross tag on note rows by type (member); face "Net investment income" `NetInvestmentIncome` 21,473M. Stored gross 22,948M = 21,473 + investment expense 1,475M | same pattern (life insurer) |
| PGR 10-K 0000080661-26-000086 R3 | Face "Investment income" is `InterestAndDividendIncomeOperating` 3,583M; "Investment expenses" `InvestmentIncomeInvestmentExpense` 34M is a face EXPENSE row; "Total net realized gains (losses) on securities" `DebtAndEquitySecuritiesGainLoss` 727M. Stored (not on the face): `GrossInvestmentIncomeOperating` 3,583M, `NetInvestmentIncome` 3,549M (= 3,583 - 34), `InvestmentIncomeNet` 4,276M (= 3,549 + 727) | at PGR `InvestmentIncomeNet` **includes realized gains** (arithmetic exact; where 4,276 is presented was not opened: DATA-INFERRED for the location) |
| ARCC 10-K 0001287750-26-000006 (arcc-20251231.htm) | `GrossInvestmentIncomeOperating` on "Total investment income from ... investments" rows (by affiliate member); **"NET INVESTMENT INCOME BEFORE INCOME TAXES" `NetInvestmentIncome` 1,458M**; "Income tax expense, including excise taxes" `InvestmentIncomeOperatingTaxExpenseBenefit` 43M; **"NET INVESTMENT INCOME" `InvestmentIncomeOperatingAfterExpenseAndTax` 1,415M**; "NET INCREASE IN STOCKHOLDERS' EQUITY RESULTING FROM OPERATIONS" `NetIncomeLoss` 1,299M; "Total stockholders' equity" `StockholdersEquity` 14,318M; `AssetsNet` not used | **BDC: NetInvestmentIncome = pre-tax result after ALL fund expenses**; confirms the Sector Analyst (BXSL 0001736035-26-000004 R5 relayed by them, not re-opened by me) |

Population checks (core.fact, same company and period, both authoritative, since 2015, tolerance 0.5%):
| Check | Companies sharing periods | Shared periods | Equal | Differ | Reading |
|---|---|---|---|---|---|
| insurer `GrossInvestmentIncomeOperating` = `NetInvestmentIncome` + `InvestmentIncomeInvestmentExpense` | 46 | 1,683 | 1,528 (91%) | 155 | the identity holds at insurers; UNM differs by a few million (another deduction) |
| insurer `NetInvestmentIncome` vs `InvestmentIncomeNet` | 25 | 778 | 526 | 252 | **not synonyms** (PGR: InvestmentIncomeNet includes gains; 2022 it is -676M against NII 1,236M) |
| null-SIC (BDC) `NetInvestmentIncome` vs `InvestmentIncomeOperatingAfterExpenseAndTax` | 38 | 881 | 436 | 445 | differ exactly where the BDC pays tax/excise tax (ARCC every period): NetInvestmentIncome is the PRE-tax line wherever both are filed |
| null-SIC (BDC) `AssetsNet` vs `StockholdersEquity` | 36 | 568 | 487 (86%) | 81 | both filed by most BDCs (equity 41 of 42, AssetsNet 31 of 42); differences include a constant 50M at company 2797 (a preferred or similar perimeter item, not opened) |

### Answer to the Sector Analyst's ask (a): what feeds `bdc_total_investment_income` for insurers
**Hypothesis REFUTED.** `analytics.concept_mapping` has exactly one row for concept 205 `bdc_total_investment_income`: `us-gaap:GrossInvestmentIncomeOperating`, priority 1, approved (combination_mode first_match). `NetInvestmentIncome` is unmapped everywhere (`sec_tag_library.mapping_status = unmapped`). The 24 insurers of the 40-insurer cohort holding a value (cohort_cells.csv: has_value t 24, f 16): their `canonical_fact` rows (1,099 source facts) come 100% from `GrossInvestmentIncomeOperating` (10-Q 722, 10-K 376, 10-K/A 1). For those insurers the value is the **gross investment income before investment expenses**, a note figure (CINF, TRV, PRU FILING-CHECKED). It is neither the BDC top line nor the insurer's face NII. The tag has two meanings:
- BDC: total investment income, the face top line (ARCC).
- Insurer: the gross line of the net-investment-income note.

`NetInvestmentIncome` also has two meanings (BDC pre-tax operating result; insurer face revenue line), but it does not feed this concept.

**Second-order effect (CODE-READ, `mapper/coverage_matrix.py` ~line 344 and 418-423):** the coverage population `bdc_company` is defined as "has any canonical_fact for bdc_total_investment_income". It therefore contains 47 insurers, 12 ETPs, KKR, SPAC trusts and others: 118 companies, of which 42 are BDCs. Line ~205 uses the same test (with a null-SIC condition) to set the gap reason `bdc_reports_investment_income_not_revenue`; insurers have a SIC code, so that branch does not fire for them. Routed to the Data Engineer / lane B and the Sector Analyst (inbox).

## 4. Siblings and confusables
- `GrossInvestmentIncomeOperating` (before investment expense) vs `NetInvestmentIncome` (after investment expense) vs `InvestmentIncomeInvestmentExpense` (the difference). Insurer identity: gross - expense = net (91% of shared periods).
- `NetInvestmentIncome` (insurer face line, or BDC pre-tax result) vs `InvestmentIncomeOperatingAfterExpenseAndTax` (BDC after-tax NII, from 2020-09) vs `InvestmentIncomeNet` (nonoperating securities income by definition; at PGR includes realized gains) vs `InterestAndDividendIncomeOperating` (PGR's face "Investment income") vs `InvestmentIncomeInterest` (nonoperating interest; see interest.md).
- BDC net assets: `StockholdersEquity` (face at ARCC, BXSL) vs `AssetsNet` (filed by 31 of 42 BDCs, usually equal). The BDC earnings line "net increase in net assets from operations" is filed on `NetIncomeLoss` (ARCC).

## 5. Known misuses and quirks
- Insurers' gross note line sits in a concept named and described as the BDC top line (`bdc_total_investment_income`), for 47 SIC-63xx companies (24 of the 40-insurer cohort). FILING-CHECKED meaning (CINF, TRV, PRU); population DATA-INFERRED.
- The 2026-09-04 note in `expanded_concepts.py` ("118 real active companies ... BDCs, plus other closed-end funds") is false as a description of the population: 47 are insurers. It was a values-plausibility check, not a population check.
- PGR: the gross tag's 3,583M equals the face "Investment income" that PGR tags `InterestAndDividendIncomeOperating`; `InvestmentIncomeNet` 4,276M includes realized gains.
- ARCC: `NetInvestmentIncome` = pre-tax (1,458M); after-tax NII 1,415M is `InvestmentIncomeOperatingAfterExpenseAndTax`.
- `InvestmentIncomeOperatingAfterExpenseAndTax` exists only from 2020-09-30 in our data, so pre-2020 BDC NII sits on `NetInvestmentIncome` (pre-tax or after-tax not checked for that era: ASSUMED, open).

## 6. Mapping verdict
- `GrossInvestmentIncomeOperating` -> `bdc_total_investment_income`: **safe only for BDCs (null-SIC fund filers), NEVER for insurers, ETPs, KKR or SPACs.** As mapped today it puts insurer gross investment income into a BDC concept and makes 76 non-BDCs part of the BDC population. FILING-CHECKED (ARCC for BDC; CINF, TRV, PRU for insurer). A group gate (group = bdc) is needed on the concept and on the `bdc_company` population; this is a proposal for the Tag Mapper and Standardization Lead, not an approval.
- `NetInvestmentIncome`: **two concepts, one tag.** Insurer `sr.ins.net_investment_income`: safe as the insurer face NII (CINF, TRV, PRU FILING-CHECKED; 87 insurer filers). BDC: it is the PRE-tax line where `InvestmentIncomeOperatingAfterExpenseAndTax` coexists (445 of 881 shared periods differ). The BDC after-tax NII row must use `InvestmentIncomeOperatingAfterExpenseAndTax` first. Never pool the two groups under one concept.
- `InvestmentIncomeNet`: **not a synonym** of insurer NII (252 of 778 differ; includes gains at PGR). Do not map it as NII.
- BDC net assets: `StockholdersEquity` first (face at ARCC, BXSL), `AssetsNet` as a per-company alternate after an equality check (86% equal; DATA-INFERRED, no AssetsNet filing opened). The Sector Analyst's "AssetsNet is on 0/2" holds for the face of those two filers only; 31 of 42 BDCs file AssetsNet somewhere.
- Evidence classes: as stated per line. Verified by: Tag Expert (me), 2026-10-22.
