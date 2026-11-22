# Card family: Net interest income, interest income and interest expense (written 2026-10-19 by the Tag Expert)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

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
- **CORRECTED 2026-10-22: the Frames count for `InterestExpenseOperating` (15 in CY2023, 56 in CY2025) is an artefact of the Frames endpoint, not the population.** `analytics.sec_tag_library`: 545 companies (538 active), first period 2021-09-30; 308 of 326 active banks (SIC 6021/6022/6029/6035/6036) file it, 307 currently. EFSC's companyconcept facts carry `frame: CY2025` (0001025835-26-000058), yet the CY2025 frames response omits EFSC. Frames under-reports this tag by about 10x; the bank-like CY2023 count above is wrong by the same cause. **Era rule (banks):** `InterestExpense` was the bank total through about 2021-2023 (295 banks; median last period 2024-03-31; 26 still current), `InterestExpenseOperating` from 2021-09 (median first period 2022-12-31). In 2,254 shared bank periods (282 banks) the two are equal in 2,222 (98.6%). The 32 differences are filing-vintage differences, not meaning: CIVB 2022 total interest expense is 11,049K in the FY2022 10-K/A (`InterestExpense`, 0000950170-23-011581) and 15,951K in the FY2024 10-K (`InterestExpenseOperating`, 0000950170-25-035961 R4, which ties to that filing's 126,155K interest income less 110,204K NII).
- ~~Nonoperating interest tags (`InterestExpenseNonoperating`, `InterestIncomeExpenseNonoperatingNet`) exist from the 2018-era taxonomy on (no CY2013 frame) and have essentially no bank filers.~~ **CORRECTED 2026-10-24 (Tag Expert, open-sources run, FILING-CHECKED against the FASB schemas):** `InterestIncomeExpenseNonoperatingNet` is in the 2015 schema, but `InterestExpenseNonoperating` AND `InterestExpenseOperating` first appear in the **us-gaap 2024** schema (absent from 2015, 2019, 2022 and 2023 `elts/us-gaap-*.xsd`, present in 2024 and 2026; FASB 2026 calc: both are children of `InterestExpense`). Earlier period ends in our data (IEN 2020-12-31, IEO 2021-09-30 in `sec_tag_library`) are comparatives re-tagged inside 2024+ filings, not the date filers switched. EFSC's first IEO filing is 2025-08-01 (companyconcept, earliest period 2023-12-31). FSDS 2025q4 num: IEN 11,295 facts, all `us-gaap/2024` or `/2025`. Reach is not small: 2,017 active companies (`sec_tag_library` 2026-10-23), 1,898 filings in FSDS 2025q4 print it on the income statement, 1,469 of them as plain "Interest expense". The Frames count (156) was a lower bound (same cause as the 2026-10-22 IEO correction).
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
| Net interest income | `InterestIncomeExpenseNet` (29 of 30 cohort [32]; Citigroup, FLG, JPM, BAC, TFSL); ACNB uses `InterestRevenueExpenseNet` | not reported (PGR) | not reported; `NetInvestmentIncome` at ARCC is "NET INVESTMENT INCOME BEFORE INCOME TAXES" (1,458M); the after-tax NII (1,415M) is `InvestmentIncomeOperatingAfterExpenseAndTax` (CORRECTED 2026-10-22, was "after fees"; see investment-income-and-funds.md) |
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
- REFINED 2026-10-24: "period-scoped" below is the wrong key. `InterestExpenseOperating` does not exist before the us-gaap 2024 taxonomy, so the switch happens by FILING (taxonomy vintage), and a period before the switch can carry both tags (original filing on `InterestExpense`, later comparative on IEO). Choose per period by filing policy, not by a date cut-over; the 98.6% equality in shared periods is what makes either copy usable.
- `InterestExpenseOperating` / `InterestExpense`: safe bank total interest expense **as a period-scoped pair** (30/30 [32]; EFSC FY2025 and CIVB FY2022 FILING-CHECKED 2026-10-22; 98.6% equal in shared periods): `InterestExpenseOperating` first for 2021-09 onward, `InterestExpense` for earlier periods and the 26 banks still on it. A single-tag lead of either is wrong for part of the 2015+ window (Sector Analyst B3 is right only for the latest filing). `InterestExpense` is already the approved `interest_expense` tag; `InterestExpenseOperating` is `candidate`, so bank interest expense goes blank in `interest_expense` once a bank switches tags: EFSC has `interest_expense` = 282,955K for FY2024 and NO FY2025 row, although its FY2025 10-K shows "Total interest expense" 261,672K on `InterestExpenseOperating` (canonical_fact read 2026-10-22, DATA-INFERRED for the population; `interest_expense` maps only `InterestExpense` p1 and `InterestExpenseDebt` p2); for non-banks `InterestExpense` covers operating+nonoperating, `InterestExpenseNonoperating` and `InterestExpenseDebt` are narrower. Per company only.
- `InvestmentIncomeInterest`: **NEVER bank interest income** (CCB, SFNC, CARV, FLG, BANR, FCCO, PEBK = three different meanings across seven banks). For non-banks it is the nonoperating interest income line (AMZN FILING-CHECKED) and is acceptable as "interest income" there.
- `InterestExpenseNonoperating`: conditional on the operating-income check (data-team/27 I-2). ~~Frames: 156 filers~~ (lower bound; 2,017 active companies, see section 2 correction), essentially a non-bank, below-the-line tag (PLD, AMZN FILING-CHECKED).
  - **NEW 2026-10-24 (Tag Expert, open-sources run): it is the current non-bank gross interest-expense line for filers on the 2024+ taxonomy, and `interest_expense` does not map it.** FILING-CHECKED: Colgate 10-Q 0000021665-25-000053 R2 "Interest expense" 67 (Q3 2025) and Avery Dennison 10-Q 0000008818-25-000049 R4 "Interest expense" 33.3 are both `InterestExpenseNonoperating` (FSDS 2025q4 num, us-gaap/2025); our `interest_expense` and `interest_expense_resolved` stop at FY2023 (CL) and Q1 2024 (AVY) (canonical_fact read 2026-10-24, DATA-INFERRED for the stored state). Population lead (DATA-INFERRED, `company_sec_tag`, not filtered to the operating universe): 1,917 companies have IEN with a last period on or after 2025-06-30; 1,542 of them have no `InterestExpense` or `InterestExpenseDebt` fact within 100 days of that period, so their recent `interest_expense` is blank or stale. Label caveat: 217 of 1,898 FSDS 2025q4 face rows read "Interest expense, net" (Rollins 0000084839-25-000100 R4, Agree Realty above), so a label check must flag the net perimeter. Mapping verdict: strong candidate as `interest_expense` fallback for non-banks, ahead of `InterestExpenseDebt`, keyed by the fact's filing (taxonomy vintage), with a same-period coexistence check against `InterestExpense` before any approval (Tag Mapper). Not yet coexistence-checked.
  - `InterestAndDebtExpense` (in every schema 2015-2026; FASB calc parent of IEN plus extinguishment/induced-conversion lines): the face interest line at TXN 0000097476-25-000060 R2 ("Interest and debt expense" 141), ODFL 0001193125-25-268415 R4 ("Interest expense" 4K) and OXY 0001628280-25-051071 R4 ("Interest and debt expense, net" 270, inside custom `CostsAndOtherDeductions` per OXY's own calc). ODFL's own calc (FSN 2025_11 cal.tsv) places it under `NonoperatingIncomeExpense` with weight -1, i.e. ODFL's NonoperatingIncomeExpense includes interest, unlike the FASB tree where they are siblings. Usable as interest expense only with a perimeter flag (may include debt-extinguishment items, may be net) and a calc/label check; 429 active companies.
- Provision for credit losses: **no safe single tag**; per-company, period-scoped tag set with a perimeter label.
- Evidence: FILING-CHECKED where named; populations DATA-INFERRED. Verified by: Tag Expert (me), Verifier [32].

## 7. FSN-era identification and inbox relays (Tag Expert, 2026-11-09)
The hybrid FSN store maps by statement line (`fsn.line_map`, rule `is.interest_expense_total@1`: InterestExpense p10, InterestExpenseNonoperating p20, InterestExpenseOperating p30, InterestAndDebtExpense p40) and fills from notes in select (`select.NOTE_TAGS`; InterestExpenseDebt only when it is the filing's sole interest-family tag). Playbook with counts: [`../playbooks/interest_expense.md`](../playbooks/interest_expense.md).

**Measured (production fsn.*, latest 10-K, 632 companies with line_map, DATA-INFERRED):** 427 mapped (IEN 235, InterestExpense 124, IEO 53, InterestAndDebtExpense 16). **40 of the 427 put a gross tag on a "…, net" label** (excluding "net of capitalized interest"): IEN 24 (e.g. ROL 84839, ADC 917251, "Interest expense, net"), InterestExpense 12 (e.g. 277509, 352915, 726958 "Interest, net"), InterestAndDebtExpense 2 (1510295 "Net interest and other financial costs", 1531152), IEO 2 (MTZ 15615, 1571123). Their served value can be net of interest income. **A Verifier stratum of its own**: open each R page and check for an interest-income line netted inside it. 205 gaps: the playbook gives the split (about 87 recoverable from notes, about 118 not; 98 print only a net-interest tag).

Relayed lessons processed this run (FILING-CHECKED by the named role unless marked; not re-opened by me, because sec.gov refuses this cloud session without a declared SEC_USER_AGENT):
- **Net lines carrying gross tags** (confirms §4 and §5): DAL tags its NET "Interest expense (income), net" segment-note line (396M) with `InterestExpense`, while the face uses `InterestIncomeExpenseNet` (Verifier, 0000027904-18-000006 R83/R4). MTZ prints "Interest expense, net" on `InterestExpenseOperating` (0000015615-26-000020 R3). IP holds IEO 372M equal to its net line. 21 negative IEO periods at 7 non-banks (SSRM 15) (Tag Mapper 2026-10-22).
- **Sign inconsistency between 10-K and 10-Q**: DIS FY `InterestExpense` is NEGATIVE in the 10-K (-1,812M FY25) and positive in its 10-Qs (487/471/438M), so FY minus the 9 months gives -3,208M (Period Engineer; 0001744489-25-000155; DATA-INFERRED + companyfacts). **Rule for Q4 derivation: never derive Q4 interest across a sign flip; hold it.**
- **InterestExpenseDebt is not a bank total and can be something else entirely**: at HWBK it is the face NON-interest-expense row "Loan expense" (0000893847-24-000016 R4); at RBB, MYFW and NBBK a debt-note or narrative figure; at COLB the face "Interest on borrowings" component (0000887343-24-000089 R5) (Standardization Lead, correcting the Tag Mapper's "component" reading). At TOL it is "Directly expensed interest" only, 0 in FY2021-22, because the rest is capitalized (Verifier, 0000794170-22-000049 R105). **So the sole-debt rule must also refuse a value of 0, and a label without "interest"** (select already refuses ≤ 0 and non-interest labels: consistent).
- **Bank vintage differences are of three kinds**, not one "filing vintage" (§2 wording corrected here): CIVB = disclosed error correction (ASC 860; cover box ticked); MNSB = undisclosed reclassification (0001437749-25-007641 vs -24-008676 R4); COLB FY2022 = reverse-acquisition entity change (Umpqua vs legacy Columbia) (Standardization Lead). For the FSN store, the latest filing printing a key wins, so all three resolve to the restated figure; COLB's pre-merger periods belong to the accounting acquirer.
- **Bank face tag**: 44 of 44 sampled banks print IEO or InterestExpense on the face; InterestExpense alone at only 2 of 44 (Sector Analyst, R-file rows). In the FSN measure, all 53 IEO-mapped companies are banks/brokers/finance companies, and AXP's "Total interest expense" is IEO (0000004962-26-000080).
- **InterestExpenseNonoperating is not a single-tag mapping by itself** (Tag Mapper check I-2): 136 periods have nonoperating + operating without InterestExpense; in 723 it exceeds InterestExpense; in 1,034 it equals a net-interest tag in absolute value. In the FSN store this is handled by line position (one face line), not by coexistence, and the 24 "net"-label IEN lines above are the residual risk.
- **Walmart**: debt interest (InterestExpenseDebt 563) and finance-lease interest (121) on separate face lines; FASB calc puts both, plus fees, under InterestExpenseNonoperating (0000104169-25-000191 R2). Gross interest expense = their sum when no IEN total is printed; the FSN calc-sum rule (G3) is the right tool, not one tag.
- **InterestAndDebtExpense** as the only face interest line: TXN 543M (0000097476-26-000059 R3), OSK 117.6M (0001193125-26-054061 R2) (Standardization Lead, Verifier). Already mapped at p40 in the FSN rules (16 companies).
- **Sector test**: `Deposits` + `InterestIncomeExpenseNet` co-occur at FCX, ZBRA, CPAY, WEX, CBC (customer deposits, net financing interest), so tag presence is not a bank test; classify by SIC, then confirm by face shape (Sector Analyst, DATA-INFERRED).
- **REIT totals that include interest**: OHI "Total expenses" on `OperatingExpenses` includes interest expense (58,238K of 177,670K, 0000888491-22-000029 R4); DOC likewise (0001628280-25-036063 R4). Revenue minus that total is after financing cost: never operating income (Standardization Lead, Data Chief). Cross-reference: operating-income.md.
- `InterestIncomeExpenseNet` sits at priority 2 under `other_income_expense_net` in the old concept_mapping (Standardization Lead 2026-10-24): an interest line under an other-income concept. Old-mapper issue only; the FSN write does not use it.

## 8. Folded in from the FSN-expert per-tag cards (2026-11-10)
- `InterestExpenseNonoperating` on the IS face for 42 top-100 names, 2024-2026 (320 lines): ABT, AMZN, ADI, AMAT, T, BLK, BKNG, AVGO, CAT ("Interest expense excluding Financial Products", 9), CSCO, KO, CRWD, DHR, ETN, FTNT, GILD, HD, JNJ, KLAC, LIN, LMT, MRVL, MA, MU, NFLX …; labels "Interest expense" 277, **"Interest expense - net" 13** (a net amount: keep the label check, §7), "…net of portion capitalized" 9.
- **MSFT: interest expense is never on the face** (inside "Other income (expense), net"); the NOTE tag switches from `InterestExpense` to IEN at the Q1 FY2025 10-Q 0000950170-24-118967 (FY2024 2,935M on the old tag; FY2025 2,385M, FY2026 3,051M on IEN). The old production `interest_expense` stopped at 2024-06-30 for that reason (task-board B6). In the FSN store, select's note fill reads IEN, so MSFT is recoverable.

## 9. Relays 2026-11-11 (cash-flow lane I7; Ritwik cloud; checked in fsn.*)
- Exelon: `InterestExpenseBorrowings` "Interest expense, net" + `InterestExpenseOther` / `InterestExpenseRelatedParty` "to affiliates": no seeded total; TMUS 2019-21 `InterestExpenseDebt` + `InterestExpenseRelatedParty`: interest expense = sum of the gross face lines (flag summed_components).
- SCCO latest 10-K 0001104659-26-021492: "Interest expense" on `InterestCostsIncurred` 416.7M, then "Capitalized interest" 47.4M (`InterestCostsCapitalizedAdjustment`): interest expense = 369.3M (incurred − capitalised).
- VRTX 2014-2024: plain "Interest expense" on `InterestIncomeExpenseNet` beside a separate interest-income line: gross expense with a misused net tag; serve abs(value) only under that condition. From 2024 VRTX uses `InterestExpenseNonoperating` (13.3M, latest 10-K 0000875320-26-000056).

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.


## 10. Public-source rules (read 2026-11-12)
- **Cash interest paid**: XBRL US DQC_0065 "Interest Paid Net (Operating) Not on Cash Flow" (final, released 2017-10-04, rule v5; github.com/DataQualityCommittee/dqc_us_rules docs/DQC_US_0065/DQC_0065.md) — the codification requires indirect-method filers to report interest paid net of capitalized interest; `InterestPaidNet` is that element; `InterestPaid` includes the capitalized component. So `InterestPaidNet` wins; `InterestPaid` only when the net element is not reported. This CORRECTS my earlier "InterestPaid wins" rule (shareholder-returns.md §9 and the library), which the readers' keys (41 of 43 on the net tag) had already contradicted.
- **2024 interest elements**: XBRL US DQC_0181 "Interest Expense Operating and Nonoperating" (final, released 2024-06-27, effective 2024-08-31; docs/DQC_US_0181/DQC_0181.md) — the 2024 US-GAAP taxonomy added `InterestExpenseNonoperating` and `InterestExpenseOperating`, and `InterestExpense` now means both together; filers are asked to replace `InterestExpense` with the specific element. Component 10180: InterestExpense/InterestExpenseOperating must not be calc descendants of `NonoperatingIncomeExpense`; 10181: InterestExpense/InterestExpenseNonoperating must not be descendants of `InterestIncomeExpenseNet` (operating net interest, the bank NII line); 10182: InterestExpense/InterestExpenseNonoperating must not sit under `OperatingExpenses`. Use: a 2024+ switch from InterestExpense to InterestExpenseNonoperating on the same face line is an era change, not a meaning change; an `InterestExpenseOperating` line is operating (bank or opex block).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 31 elements named in this card have library knowledge; the 30 most served are below. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `OperatingIncomeLoss`
- **Meaning:** Operating Income (Loss) (us-gaap, duration, credit). The net result for the period of deducting operating expenses from operating revenues.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; operating_income: Operating income: revenue minus all operating costs (COR, opex, restructuring and impairment), before interest, other non-operating items, equity-method income and tax. [not applicable: bank] (+1 more)
- **Data point:** operating_income; operating_expenses; other_income_expense_net
- **Rules:** C13; resolver functions resolve
- **Evidence:** 80 companies, 949 served, 34797 proven, 106 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpense`
- **Meaning:** Interest Expense, Operating and Nonoperating (us-gaap, duration, debit). Amount of interest expense classified as operating and nonoperating. Includes, but is not limited to, cost of borrowing accounted for as interest expense.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** interest_expense; other_income_expense_net; operating_expenses; interest_income; polarity interest_expense:positive; role interest_expense:primary#1
- **Rules:** X115; I21; I20; I22; I23; I24; resolver functions resolve_band; family resolve_all.NARROW[interest_expense]
- **Evidence:** 88 companies, 938 served, 24594 proven, 51 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 1 companies, e.g. META interest_expense 2021-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToInterestExpenseNet@2013; CashFlowHedgeGainReclassifiedToInterestExpense@2013; CashFlowHedgeLossReclassifiedToInterestExpense@2013; InterestExpenseRelatedParty@2023

### `InterestPaidNet`
- **Meaning:** Interest Paid, Excluding Capitalized Interest, Operating Activity (us-gaap, duration, credit). Amount of cash paid for interest, excluding capitalized interest, classified as operating activity. Includes, but is not limited to, payment to settle zero-coupon bond for accreted interest of debt discount and debt instrument with insignif...
- **Data point definition:** cash_paid_for_interest: Cash paid for interest, net of amounts capitalized (InterestPaidNet).
- **Data point:** cash_paid_for_interest; polarity cash_paid_for_interest:positive; role cash_paid_for_interest:primary#1
- **Rules:** K35
- **Evidence:** 98 companies, 883 served, 1627 proven, 69 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InvestmentIncomeInterest`
- **Meaning:** Investment Income, Interest (us-gaap, duration, credit). Amount before accretion (amortization) of purchase discount (premium) of interest income on nonoperating securities.
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_income; other_income_expense_net; polarity interest_income:signed; role interest_income:primary#2
- **Rules:** I26; I27; family resolve_all.NARROW[interest_income]
- **Evidence:** 50 companies, 616 served, 1444 proven, 48 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 4 open hit(s) at 3 companies, e.g. AMGN interest_income 2021-12-31 (export) (pattern_hits.csv); pattern P06 own_10k_year_hidden: 5 open hit(s) at 1 companies, e.g. CRM interest_income 2015-01-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (5); P05 (4)

### `OperatingExpenses`
- **Meaning:** Operating Expenses (us-gaap, duration, debit). Generally recurring costs associated with normal operations except for the portion of these expenses which can be clearly related to production and included in cost of sales or services. Includes selling, general and administrative expense.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#1
- **Rules:** I14; I09; I10; I11; I12; I13; family resolve_all.NARROW[operating_expenses]
- **Evidence:** 36 companies, 352 served, 11930 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestPaid`
- **Meaning:** Interest Paid, Including Capitalized Interest, Operating and Investing Activities (us-gaap, duration, credit). Amount of cash paid for interest, including, but not limited to, capitalized interest and payment to settle zero-coupon bond attributable to accreted interest of debt discount and debt instrument with insignificant coupon interest rate in r...
- **Data point definition:** cash_paid_for_interest: Cash paid for interest, net of amounts capitalized (InterestPaidNet).
- **Data point:** cash_paid_for_interest; polarity cash_paid_for_interest:positive; role cash_paid_for_interest:primary#2
- **Rules:** K35
- **Evidence:** 61 companies, 336 served, 313 proven, 46 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NoninterestExpense`
- **Meaning:** Noninterest Expense (us-gaap, duration, debit). Total aggregate amount of all noninterest expense.
- **Data point definition:** noninterest_expense: Total noninterest expense as printed. [not applicable: general,insurer,equity_reit,utility,bdc]; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** noninterest_expense; operating_expenses; polarity noninterest_expense:positive; operating_expenses:positive; role noninterest_expense:primary#1; operating_expenses:primary#3
- **Rules:** C28; I14; I09; I10; I11; I12; I13; resolver functions resolve
- **Evidence:** 9 companies, 215 served, 919 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces NoninterestExpenseMember@2013

### `NonoperatingIncomeExpense`
- **Meaning:** Nonoperating Income (Expense) (us-gaap, duration, credit). The aggregate amount of income or expense from ancillary business-related activities (that is to say, excluding major activities considered part of the normal operations of the business).
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+2 more)
- **Data point:** other_income_expense_net; interest_income; interest_expense; operating_expenses; polarity other_income_expense_net:signed; role other_income_expense_net:primary#1
- **Rules:** I29; I28; I30; I31; I32; I33; I34; I35; resolver functions resolve_band
- **Evidence:** 28 companies, 183 served, 242 proven, 14 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestAndDividendIncomeOperating`
- **Meaning:** Interest and Dividend Income, Operating (us-gaap, duration, credit). Represents the total of interest and dividend income, including any amortization and accretion (as applicable) of discounts and premiums, earned from (1) loans and leases whether held-for-sale or held-in-portfolio; (2) investment securities...
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).; total_interest_income: Total interest income as printed. [not applicable: general,insurer,equity_reit,utility,bdc]
- **Data point:** interest_income; total_interest_income; polarity interest_income:signed; role interest_income:primary#1; total_interest_income:primary#1
- **Rules:** I26; I27
- **Evidence:** 8 companies, 167 served, 985 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 12 open hit(s) at 2 companies, e.g. C interest_income 2023-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (12)

### `InterestIncomeExpenseNet`
- **Meaning:** Interest Income (Expense), Operating (us-gaap, duration, credit). Amount of interest income (expense) classified as operating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+4 more)
- **Data point:** interest_expense; net_interest_income; other_income_expense_net; revenue; interest_income; polarity interest_expense:positive; net_interest_income:signed; role interest_expense:combined#2; net_interest_income:primary#1
- **Rules:** X90; X125; I20; I21; I22; I23; I24
- **Evidence:** 14 companies, 149 served, 686 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InterestRevenueExpense@2012

### `InterestExpenseNonoperating`
- **Meaning:** Interest Expense, Nonoperating (us-gaap, duration, debit). Amount of interest expense classified as nonoperating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+1 more)
- **Data point:** interest_expense; other_income_expense_net; interest_income; polarity interest_expense:positive; role interest_expense:primary#2
- **Rules:** I20; I21; I22; I23; I24; family resolve_all.NARROW[interest_expense]
- **Evidence:** 55 companies, 132 served, 744 proven, 28 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NoninterestIncome`
- **Meaning:** Noninterest Income (us-gaap, duration, credit). The total amount of noninterest income which may be derived from: (1) fees and commissions; (2) premiums earned; (3) insurance policy charges; (4) the sale or disposal of assets; and (5) other sources not otherwise specified.
- **Data point definition:** noninterest_income: Total noninterest income as printed. [not applicable: general,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** noninterest_income; revenue; role noninterest_income:primary#1
- **Rules:** none
- **Evidence:** 8 companies, 114 served, 375 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpenseDebt`
- **Meaning:** Interest Expense, Debt (us-gaap, duration, debit). Amount of the cost of borrowed funds accounted for as interest expense for debt.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_expense; other_income_expense_net; polarity interest_expense:positive; role interest_expense:primary#3
- **Rules:** I20; I21; I22; I23; I24; family resolve_all.NARROW[interest_expense]
- **Evidence:** 10 companies, 113 served, 1434 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DebtInstrumentConvertibleInterestExpense@2013

### `Deposits`
- **Meaning:** Deposits (us-gaap, instant, credit). The aggregate of all deposit liabilities held by the entity, including foreign and domestic, interest and noninterest bearing; may include demand deposits, saving deposits, Negotiable Order of Withdrawal (NOW) and time deposits among others...
- **Data point definition:** deposits: Total deposits at period end. [not applicable: general,insurer,equity_reit,utility,bdc]
- **Data point:** deposits; role deposits:primary#1
- **Rules:** none
- **Evidence:** 9 companies, 108 served, 355 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CostsAndExpenses`
- **Meaning:** Costs and Expenses (us-gaap, duration, debit). Total costs of sales and operating expenses for the period.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses
- **Rules:** X117; I09; resolver functions apply_cost_and_opex
- **Evidence:** 21 companies, 95 served, 190 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DevelopmentStageEnterpriseCumulativeExpense@2012

### `InterestAndDebtExpense`
- **Meaning:** Interest and Debt Expense (us-gaap, duration, debit). Interest and debt related expenses associated with nonoperating financing activities of the entity.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+1 more)
- **Data point:** interest_expense; interest_income; other_income_expense_net; polarity interest_expense:positive; role interest_expense:primary#4
- **Rules:** I21; I20; I22; I23; I24; resolver functions resolve_band
- **Evidence:** 8 companies, 76 served, 228 proven, 22 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `ProvisionForLoanLeaseAndOtherLosses`
- **Meaning:** Provision for Loan, Lease, and Other Losses (us-gaap, duration, debit). Amount of expense related loan transactions, lease transactions, credit loss from transactions other than loan and lease transactions, and other loss based on assessment of uncollectability from the counterparty to reduce the account to the...
- **Data point definition:** provision_for_credit_losses: Provision for credit losses (loan losses pre-CECL) as printed;  a release is a real negative. [not applicable: general,insurer,equity_reit,utility,bdc]
- **Data point:** provision_for_credit_losses; polarity provision_for_credit_losses:signed; role provision_for_credit_losses:primary#1
- **Rules:** none
- **Evidence:** 8 companies, 58 served, 287 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FinancingReceivableAllowanceForCreditLossesProvisions@2012

### `InterestIncomeOperating`
- **Meaning:** Interest Income, Operating (us-gaap, duration, credit). Amount of operating interest income, including, but not limited to, amortization and accretion of premiums and discounts on securities.
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).
- **Data point:** interest_income; polarity interest_income:signed; role interest_income:primary#5
- **Rules:** I26; I27
- **Evidence:** 4 companies, 33 served, 140 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 1 companies, e.g. NFLX interest_income 2022-12-31 (export) (pattern_hits.csv); pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. NFLX interest_income 2024-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2); P06 (1)
- **Deprecation:** replaces InterestIncomeRelatedParty@2023; InvestmentsInAndAdvancesToAffiliatesDividendOrInterestCreditedToIncome@2023; InvestmentsInAndAdvancesToAffiliatesDividendsOrInterest@2023

### `ProvisionForLoanLossesExpensed`
- **Meaning:** Financing Receivable, Credit Loss, Expense (Reversal) (us-gaap, duration, debit). Amount of credit loss expense (reversal of expense) for financing receivable.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; provision_for_credit_losses: Provision for credit losses (loan losses pre-CECL) as printed (+1 more)
- **Data point:** provision_for_credit_losses; operating_expenses; polarity provision_for_credit_losses:signed; role provision_for_credit_losses:primary#4
- **Rules:** none
- **Evidence:** 5 companies, 25 served, 132 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `BenefitsLossesAndExpenses`
- **Meaning:** Benefits, Losses and Expenses (us-gaap, duration, debit). The total amount of expense recognized during the period for future policy benefits, claims and claims adjustment costs, and for selling, general and administrative costs.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#2
- **Rules:** I14; I09; I10; I11; I12; I13
- **Evidence:** 2 companies, 24 served, 101 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestIncomeExpenseNonoperatingNet`
- **Meaning:** Interest Income (Expense), Nonoperating (us-gaap, duration, credit). Amount of interest income (expense) classified as nonoperating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; interest_income: Consolidated interest income for the period (X94). (+1 more)
- **Data point:** interest_expense; interest_income; other_income_expense_net; polarity interest_expense:positive; role interest_expense:combined#1
- **Rules:** I20; I21; I22; I23; I24
- **Evidence:** 9 companies, 21 served, 51 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpenseOperating`
- **Meaning:** Interest Expense, Operating (us-gaap, duration, debit). Amount of interest expense classified as operating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).
- **Data point:** interest_expense; polarity interest_expense:positive; role interest_expense:primary#5
- **Rules:** I20; I21; I22; I23; I24
- **Evidence:** 11 companies, 20 served, 142 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestRevenueExpenseNet`
- **Meaning:** Interest Income (Expense), Operating and Nonoperating (us-gaap, duration, credit). Amount of interest income (expense) classified as operating and nonoperating.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_expense; other_income_expense_net; polarity interest_expense:positive; role interest_expense:combined#3
- **Rules:** X108; I20; I21; I22; I23; I24
- **Evidence:** 3 companies, 15 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InterestRevenueExpense@2012

### `InterestCostsIncurred`
- **Meaning:** Interest Costs Incurred (us-gaap, duration, debit). Total interest costs incurred during the period and either capitalized or charged against earnings.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).
- **Data point:** interest_expense
- **Rules:** none
- **Evidence:** 1 companies, 12 served, 55 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpenseOther`
- **Meaning:** Interest Expense, Other (us-gaap, duration, debit). Amount of interest expense classified as other.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_expense; other_income_expense_net
- **Rules:** none
- **Evidence:** 2 companies, 12 served, 2 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestExpenseRelatedParty`
- **Meaning:** Interest Expense, Related Party (Deprecated 2023) (us-gaap, duration, debit). Amount of interest expense incurred on a debt or other obligation to related party.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).
- **Data point:** interest_expense
- **Rules:** none
- **Evidence:** 2 companies, 10 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaced by InterestExpense@2023; InterestExpenseOperatingRelatedPartyTypeExtensibleEnumeration@2023; [RelatedPartyMember@2023; RelatedPartyTransactionsByRelatedPartyAxis]@2023

### `ProvisionForLoanAndLeaseLosses`
- **Meaning:** Provision for Loan and Lease Losses (us-gaap, duration, debit). Amount of expense related to estimated loss from loan and lease transactions.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; provision_for_credit_losses: Provision for credit losses (loan losses pre-CECL) as printed (+1 more)
- **Data point:** provision_for_credit_losses; operating_expenses; polarity provision_for_credit_losses:signed; role provision_for_credit_losses:primary#2
- **Rules:** none
- **Evidence:** 5 companies, 7 served, 45 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AllowanceForLoanAndLeaseLossesProvisionForLossGross@2013; AllowanceForLoanAndLeaseLossesProvisionForLossNet@2013

### `InterestExpenseBorrowings`
- **Meaning:** Interest Expense, Borrowings (us-gaap, duration, debit). Aggregate amount of interest expense on all borrowings.
- **Data point definition:** interest_expense: Total interest expense as printed on the income statement or stated in MD&A, incl. finance-lease and financing-obligation interest (matches the total_debt perimeter).
- **Data point:** interest_expense; polarity interest_expense:positive; role interest_expense:primary#6
- **Rules:** I20; I21; I22; I23; I24
- **Evidence:** 1 companies, 2 served, 14 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InterestAndFeeIncomeLoansAndLeases`
- **Meaning:** Interest and Fee Income, Financing Receivable (us-gaap, duration, credit). The aggregate interest and fee income generated by: (1) loans the Entity has positive intent and ability to hold for the foreseeable future, or until maturity or payoff, including commercial and consumer loans, whether domestic or foreign, ...
- **Data point:** none (the resolver never serves it)
- **Rules:** none
- **Evidence:** 0 companies, 0 served, 16 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `Dividends`
- **Meaning:** Dividends (us-gaap, duration, debit). Amount of paid and unpaid cash, stock, and paid-in-kind (PIK) dividends declared, for example, but not limited to, common and preferred stock.
- **Data point:** none (the resolver never serves it)
- **Rules:** X93; I35; K21; resolver functions PURE_II
- **Evidence:** 0 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
