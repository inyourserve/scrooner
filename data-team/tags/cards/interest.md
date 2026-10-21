# Card family: Net interest income, interest income and interest expense (written 2026-10-19 by the Tag Expert)

Tags: `us-gaap:InterestIncomeExpenseNet`, `InterestRevenueExpenseNet`, `InterestExpense`, `InterestExpenseOperating`, `InterestExpenseNonoperating`, `InterestExpenseDebt`, `InterestIncomeExpenseNonoperatingNet`, `InvestmentIncomeInterest`; related bank lines `InterestAndDividendIncomeOperating`, `InterestIncomeOperating`, `InterestExpenseDeposits`, `InterestExpenseBorrowings`, `InterestExpenseOther`, `InterestAndFeeIncomeLoansAndLeases`, `InterestIncomeExpenseAfterProvisionForLoanLoss`, the provision tags, `NoninterestIncome`, `NoninterestExpense`.
Method and limits: as in `revenue.md` (Frames = all SEC filers; "bank-like" = also files `NoninterestExpense`; DB reads skipped, connections 14-18 > 12). SIC 6000-6199 over-counts banks (crypto miners and fintech sit in it), so the Frames proxy is used instead.

## 1. Official meaning (taxonomy 2025, read 2026-10-19)
| Tag | Period / balance | Definition | Status |
|---|---|---|---|
| InterestIncomeExpenseNet | duration / credit | "Amount of interest income (expense) classified as **operating**." | current |
| InterestRevenueExpenseNet | duration / credit | Interest income (expense) classified as operating **and nonoperating**. (Calc parent of the previous one, per the inbox, FILING-CHECKED in the FASB linkbases by the sources run.) | current |
| InterestExpense | duration / debit | "Interest expense classified as **operating and nonoperating**. Includes cost of borrowing accounted for as interest expense." | current |
| InterestExpenseOperating | duration / debit | Interest expense classified as operating | current |
| InterestExpenseNonoperating | duration / debit | Interest expense classified as nonoperating | current |
| InterestExpenseDebt | duration / debit | Cost of borrowed funds accounted for as interest expense for debt | current |
| InterestIncomeExpenseNonoperatingNet | duration / credit | Interest income (expense) classified as nonoperating | current |
| InvestmentIncomeInterest | duration / credit | "Amount **before accretion (amortization) of purchase discount (premium)** of interest income on **nonoperating securities**." | current |
| InterestAndDividendIncomeOperating | duration / credit | Total of interest and dividend income from loans, securities, fed funds, repos, CDs, dividends, other investments | current |
| InterestIncomeOperating | duration / credit | Operating interest income incl. amortization/accretion | current |
| InterestIncomeExpenseAfterProvisionForLoanLoss | duration / credit | Interest income or expense after the provisions | current |
| ProvisionForLoanLeaseAndOtherLosses (PLLOL) | duration / debit | Expense for loan, lease, other credit losses | current |
| FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal | duration / debit | Credit loss expense on financing receivables, excludes net investment in lease | current |
| ProvisionForLoanLossesExpensed | duration / debit | Credit loss expense for financing receivable | current |
| ProvisionForOtherCreditLosses | duration / debit | Credit loss from transactions other than loans and leases | current |
| ProvisionForLoanAndLeaseLosses | duration / debit | Estimated loss from loan and lease transactions (pre-CECL wording) | current |
| NoninterestIncome / NoninterestExpense | duration / credit, debit | total noninterest income (fees, premiums, gains ...) / total noninterest expense | current |
Note: `data.sec.gov` Frames/companyconcept return an outdated description for InterestIncomeExpenseNet ("net amount of operating interest"); cite the FASB text, not the API label (inbox line, accepted).

## 2. Who reports it (Frames, all SEC filers, DATA-INFERRED)
| Tag | CY2013 (bank-like) | CY2023 (bank-like) |
|---|---|---|
| InterestIncomeExpenseNet | 1,450 (617) | 1,191 (423) |
| InterestExpense | 5,326 (616) | 3,612 (421) |
| InterestExpenseOperating | none | 15 (3) |
| InterestExpenseNonoperating | none | 156 (0) |
| InterestExpenseDebt | 810 (24) | 877 (34) |
| InterestIncomeExpenseNonoperatingNet | 449 (1) | 884 (4) |
| InvestmentIncomeInterest | 2,112 (21) | 1,747 (13) |
| InterestAndDividendIncomeOperating | 708 (576) | 479 (388) |
| InterestIncomeOperating | 304 (52) | 334 (54) |
| InterestAndFeeIncomeLoansAndLeases | 567 (521) | 380 (338) |
| InterestExpenseDeposits | 503 (484) | 352 (335) |
| InterestIncomeExpenseAfterProvisionForLoanLoss | 624 (593) | 416 (398) |
| ProvisionForLoanLeaseAndOtherLosses | 391 (270) | 402 (235) |
| ProvisionForLoanAndLeaseLosses | 678 (519) | 104 (79) |
| NoninterestIncome | 631 (601) | 436 (412) |
| NoninterestExpense | 634 (634) | 443 (443) |
Findings from the counts:
- **`InterestIncomeExpenseNet` is not a bank-only tag**: 1,191 CY2023 filers, 423 bank-like; the other 768 by this proxy are non-banks. (The sources run counted 246 non-bank CIKs that print it as "interest expense, net" in the Q4-2025 data set; the two methods differ, both say a large non-bank population exists. Inbox line, accepted: **the "safe single tag" verdict is bank-only.**)
- `InterestExpense` is overwhelmingly a non-bank tag (3,612 filers, 421 bank-like) while `InterestExpenseOperating` has 15 filers (3 bank-like). Banks print "Total interest expense" under either; only 26 + 4 of the 30-cohort (26 `InterestExpenseOperating`, 4 `InterestExpense`) [32].
- Nonoperating interest tags (`InterestExpenseNonoperating`, `InterestIncomeExpenseNonoperatingNet`) exist from the 2018-era taxonomy on (no CY2013 frame) and have essentially no bank filers.
- `InvestmentIncomeInterest` is a non-bank tag too: 1,747 filers, 13 bank-like. Of the CY2023 filers, 1,589 also file `OperatingIncomeLoss`.
- `ProvisionForLoanAndLeaseLosses` collapsed 678 -> 104 filers after CECL (2020-2023); `ProvisionForLoanLeaseAndOtherLosses` stayed at ~400; the CECL-era tags (`FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal`, `ProvisionForLoanLossesExpensed`, `ProvisionForOtherCreditLosses`) took the rest in the 30-bank cohort (counts in the required-answers table).

## 3. How filers use it (filings opened)
| Filing | Statement and rows | Finding |
|---|---|---|
| Citigroup 0000831001-25-000154 R2, 10-Q (me) | Interest income `InterestAndDividendIncomeOperating` 106,215M (9M); Interest expense `InterestExpenseOperating` 62,088M; "Net interest income" `InterestIncomeExpenseNet` 44,127M; provision for credit losses on loans = `FinancingReceivableExcludingAccruedInterestCreditLossExpenseReversal` 7,297M; total provisions = custom `c_ProvisionForCreditLossBenefitsAndClaimsExpenseReversal` | classic bank layout; NII tag as expected |
| Flushing Financial 0001104659-25-106961 R4, 10-Q (me) | "Interest and fees on loans" `InterestAndFeeIncomeLoansAndLeases` 283,007K; **"Interest" `InvestmentIncomeInterest` 61,384K** (securities interest), + Dividends + other = "Total interest and dividend income" `InterestAndDividendIncomeOperating` 350,407K; "Total interest expense" `InterestExpenseOperating` 190,381K; NII `InterestIncomeExpenseNet` 160,026K; provision `ProvisionForLoanLeaseAndOtherLosses` 10,043K | confirms the inbox lead: FLG uses `InvestmentIncomeInterest` for the SECURITIES interest line only (94,970 + 19,785 + 29 + 1,685 = 116,469, quarter), NOT total interest income. Four-bank list of securities-line users is now CCB, SFNC, CARV, FLG |
| JPM 0001628280-26-008131 [32] | Interest income = `InterestIncomeOperating`; expense = `InterestExpenseOperating`; NII `InterestIncomeExpenseNet` 95,443M; provision PLLOL 14,212M | |
| BAC 0000070858-26-000157 R3 [32] | IADIO 138,566M; `InterestExpenseOperating`; NII `InterestIncomeExpenseNet` 60,096M; provision custom (bac:) | |
| TFSL 0001381668-25-000106 [32] | IADIO; `InterestExpenseOperating`; NII `InterestIncomeExpenseNet`; provision `ProvisionForLoanLossesExpensed` | thrift |
| EWBC 0001069157-26-000009 [32] | NII; IADIO; provision PLLOL; FHLB interest `InterestExpenseFederalHomeLoanBankAndFederalReserveBankAdvancesLongTerm` | |
| PGR 0000080661-26-000086 R3 (me) | insurer: "Investment income" `InterestAndDividendIncomeOperating` 3,583M; "Interest expense" `InterestExpenseDebt` 278M inside `BenefitsLossesAndExpenses` | no NII; no provision |
| ARCC 0001287750-26-000006 R5 (me) | BDC: `GrossInvestmentIncomeOperating` 3,052M; "Interest and credit facility fees" = `InterestExpense` 793M; net investment income | no NII; interest expense is a cost line |
| AMZN 0001018724-26-000004 R4 (me) | "Interest income" = `InvestmentIncomeInterest`; "Interest expense" = `InterestExpenseNonoperating`; both below operating income | the tag meaning (nonoperating securities interest) fits |
| PLD 0001193125-26-051453 R4 (me) | "Interest expense" = `InterestExpenseNonoperating` | below operating income |
| HTZ 0001657853-26-000008 R7 (me) | "Interest expense, net" = `InterestExpenseOperating` 1,077M | operating interest for a rental company; 608M of it is vehicle interest |
| CVX 0000093410-26-000078 R3 (me) / AJG 0001628280-26-008662 R3 (me) | "Interest and debt expense" = `InterestExpenseDebt` / "Interest" = `InterestExpense`, both inside `CostsAndExpenses` | |
| ANDE 0000821026-26-000010 R3 (me) | "Interest expense, net" = **`InterestIncomeExpenseNet`** (non-bank) | stored XBRL value is **-47,159,000** (companyconcept, FY2025) while the R-file prints 47,159: R-file shows the negated presentation, the fact is signed credit-positive |
| BBW 0001437749-26-012501 R4 (me) | "Interest income, net" = `InterestIncomeExpenseNonoperatingNet`; stored **+801,000** while the R-file prints (801) | negated label again |
| Mortgage/other non-banks | Universal Health Realty 0001193125-25-272382 R2; Turtle Beach 0001193125-25-270035 R2 (inbox, DATA-INFERRED from the SEC data set; not opened by me) | non-banks printing `InterestIncomeExpenseNet` as interest expense, net |

### Required answers (net interest income, total interest income, provision; banks, thrifts, insurers, BDCs)
| Concept | Banks and thrifts (face) | Insurers | BDCs |
|---|---|---|---|
| Net interest income | `InterestIncomeExpenseNet` (29 of 30 cohort [32]; Citigroup, FLG, JPM, BAC, TFSL); ACNB uses `InterestRevenueExpenseNet` | not reported (PGR) | not reported; "net investment income" `NetInvestmentIncome` after fees (ARCC) |
| Total interest income | `InterestAndDividendIncomeOperating` (27 of 30) or `InterestIncomeOperating` (3 of 30) | investment income row may use IADIO (PGR) | `GrossInvestmentIncomeOperating` (ARCC) |
| Total interest expense | `InterestExpenseOperating` (26 of 30, Citigroup, FLG) or `InterestExpense` (4 of 30) | `InterestExpenseDebt` (PGR) | `InterestExpense` (ARCC) |
| Provision for credit losses | no single tag, 7 tags across 30 [32]: PLLOL 12, FinancingReceivable...CreditLossExpenseReversal 6, ProvisionForLoanLossesExpensed 5, ProvisionForOtherCreditLosses 3, custom 3, none 1 | none | none |

## 4. Siblings and confusables
- `InterestIncomeExpenseNet` (operating, bank NII) vs `InterestRevenueExpenseNet` (operating+nonoperating; equals NII only where the bank has no nonoperating interest; 11 non-banks use it as net financing interest per the inbox: TJX 0000109198-25-000061 R2, Nucor 0001193125-25-276207 R2, DATA-INFERRED) vs `InterestIncomeExpenseNonoperatingNet` (nonoperating) vs `NonoperatingIncomeExpense` (broader bucket, can differ in sign; expanded_concepts.py note).
- `InterestExpense` (operating+nonoperating) vs `InterestExpenseOperating` vs `InterestExpenseNonoperating` vs `InterestExpenseDebt` (debt only; 467 filers carry both `InterestExpense` and `InterestExpenseDebt` in CY2023) vs `InterestExpenseDeposits/Borrowings/Other` (components) vs `InterestCostsIncurred` (before capitalisation).
- `InvestmentIncomeInterest` (securities interest, nonoperating) vs `InterestAndDividendIncomeOperating` (total) vs `InterestIncomeOperating` (total).
- The word "net" in the row label does not identify the tag: ANDE "Interest expense, net" is `InterestIncomeExpenseNet`, HTZ's is `InterestExpenseOperating`, BBW's "Interest income, net" is `InterestIncomeExpenseNonoperatingNet`.

## 5. Known misuses and quirks
Carried from company-quirks.md: `InvestmentIncomeInterest` = securities interest at CCB, SFNC, CARV; total interest income at BANR (2023, 0000946673-24-000008 R5) and FCCO (2021, 0001552781-21-000789 R4); net interest income itself at PEBK (Q2-23, 0001654954-23-010250 R4) [32]. New this run:
- **FLG: `InvestmentIncomeInterest` = securities interest line (me, 0001104659-25-106961 R4)** -> inbox lead closed: it is NOT total interest income.
- **ANDE: `InterestIncomeExpenseNet` for non-bank interest expense, net (me).** Existing mapping code lists `InterestIncomeExpenseNet` as a fallback of `other_income_expense_net` (`mapper/tag_candidates.py` line ~100) and the NII formula uses `InvestmentIncomeInterest` minus interest expense (`net_interest_income`, doc 32 section 2d). Both are repo facts I read, not DB facts.
- **R-file sign trap**: ANDE shows 47,159 and BBW shows (801) in the rendered statements, but the stored facts are -47,159K and +801K. A verifier comparing a rendered number with a stored fact must apply the row's negation, otherwise it will report a sign error that is not there (and miss a real one).
- Insurers can use IADIO for investment income (PGR), so IADIO does not identify a bank.
- Provision tag switches between filings of the same bank: CCB (10-K ProvisionForOtherCreditLosses vs 10-Q PLLOL) [32]; pre-CECL `ProvisionForLoanAndLeaseLosses` still used (104 CY2023 filers).

- NEW (me, 2026-10-21, FILING-CHECKED): Agree Realty 0000917251-26-000013 R5 puts the gross tag `InterestExpenseNonoperating` on "Interest expense, net" (134,612K); AAON 0000824142-26-000005 R4 puts the net tag `InterestIncomeExpenseNet` on a plain "Interest expense" row, rendered (17,726), stored -17,726K. Population (non-bank FY2025 10-K face, DATA-INFERRED): gross tags 2,379 line-tags, net tags 569, gross tag on a "net" label 388 (284 with no interest-income row), net tag on a plain expense label 57, stored negative on a gross expense tag 19, interest only in notes 44. Banks: `InterestExpenseOperating` 298 of 317, `InterestExpense` 14. Detail: R2 report sec. 9.

## 6. Mapping verdict
- `InterestIncomeExpenseNet`: **safe single tag for BANK net interest income only** (29 of 30 banks FILING-CHECKED [32]; Citigroup and FLG added by me). **Never use it for non-banks** as NII or as interest expense without the sign and meaning checked (ANDE, 768 non-bank-like CY2023 filers). Needs the full-population check (not done).
- `InterestRevenueExpenseNet`: NOT an exact synonym; map only after a per-company check that no nonoperating interest exists (ACNB); definition FILING-CHECKED (official), usage DATA-INFERRED.
- `InterestAndDividendIncomeOperating`, `InterestIncomeOperating`: safe bank total interest income (30/30 [32]); not safe as a bank detector (PGR).
- `InterestExpenseOperating` / `InterestExpense`: safe bank total interest expense (30/30); for non-banks `InterestExpense` covers operating+nonoperating, `InterestExpenseNonoperating` and `InterestExpenseDebt` are narrower. Per company only.
- `InvestmentIncomeInterest`: **NEVER bank interest income** (CCB, SFNC, CARV, FLG, BANR, FCCO, PEBK = three different meanings across seven banks). For non-banks it is the nonoperating interest income line (AMZN FILING-CHECKED) and is acceptable as "interest income" there.
- `InterestExpenseNonoperating`: conditional on the operating-income check (data-team/27 I-2). Frames: 156 filers, 0 bank-like, essentially a non-bank, below-the-line tag (PLD, AMZN FILING-CHECKED).
- Provision for credit losses: **no safe single tag**; per-company, period-scoped tag set with a perimeter label.
- Evidence: FILING-CHECKED where named; populations DATA-INFERRED. Verified by: Tag Expert (me), Verifier [32].
