# Tag index (seed; the Tag Expert extends it)

| Tag | Family | Verdict | Evidence | Note |
|---|---|---|---|---|
| InterestIncomeExpenseNet | bank net interest income | safe single tag | FILING-CHECKED, 29 of 30 banks [32] | still needs the full-population check |
| NoninterestIncome | bank | safe single tag | 29/30 [32] | |
| NoninterestExpense | bank | safe single tag | 30/30 [32] | |
| InterestAndDividendIncomeOperating / InterestIncomeOperating | bank total interest income | safe | 30/30 [32] | |
| InterestExpenseOperating / InterestExpense | bank total interest expense | safe as a pair chosen per FILING vintage (IEO exists only from the us-gaap 2024 schema; "2021-09" is the earliest comparative period, REFINED 2026-10-24) | FILING-CHECKED 30/30 [32] + EFSC, CIVB 2026-10-22; 98.6% equal in 2,254 shared bank periods (DATA-INFERRED) | `interest_expense` maps only InterestExpense: banks go blank after the switch (EFSC FY2025); Frames under-counts InterestExpenseOperating ~10x |
| Deposits | bank | safe, 27 of 30 | [32] | BANR, CARV components only; TFSL no total |
| FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss | bank net loans | per-period set with a face check (CECL era); LoansAndLeasesReceivableNetReportedAmount before | FILING-CHECKED (EFSC, OSBC) 2026-10-22; cards/bank-loans-and-allowance.md | OSBC: undimensioned value = collateral-dependent loans note total |
| InvestmentIncomeInterest | bank | NEVER map as bank interest income | FILING-CHECKED [32] | three different meanings |
| OperatingIncomeLoss | bank | NEVER map for banks without a row-label check | [32] | BANR, PEBO mis-tags |
| CostsAndExpenses | non-bank | do NOT derive operating income from it | FILING-CHECKED [26] | includes interest at CVX/AJG/HTZ |
| Revenues | bank | NOT safe | [32] | net revenue at BAC/PNC, gross at GABC/ACNB |
| NotesPayable | debt | sole-tag last resort only, if checks pass | proposal [27] | CDNL double-count counterexample |
| SeniorNotes, SubordinatedDebt | debt | sole-tag last resort only | proposal [27] | fill none of the named cells |
| InterestExpenseNonoperating | interest | conditional on check I-2 | proposal [27] | |
| Revenues | revenue | per company-period; NEVER bank | FILING-CHECKED 6 filers + [32]; cards/revenue.md 2026-10-19 | net at BAC/PNC/Citigroup, gross by definition; GE quarterly = GE Capital |
| RevenueFromContractWithCustomerExcludingAssessedTax | revenue | total only if no other total; subset at ANDE and banks | FILING-CHECKED (AAPL, BBW; counterexamples) 2026-10-19 | no pre-ASC 606 frame |
| SalesRevenueNet / GoodsNet / ServicesNet | revenue | pre-ASC 606 periods only, per company | FILING-CHECKED (GE R164) + DATA-INFERRED | absent from 2021/2024/2025 taxonomy files |
| InterestAndDividendIncomeOperating | revenue / interest | bank total interest income only | FILING-CHECKED; PGR counterexample (insurer) 2026-10-19 | not a bank detector |
| RevenuesNetOfInterestExpense | revenue | bank presented total (JPM, WFC) | FILING-CHECKED [32] | 64 CY2023 filers |
| OperatingIncomeLoss | operating income | non-banks with face label; NEVER banks; PLD includes real-estate gains | FILING-CHECKED (AAPL, AMZN, DUK) 2026-10-19 | 13% of revenue filers have none |
| CostsAndExpenses | operating income | never derive OI; includes interest at CVX/AJG/HTZ/GE/XOM, excludes it at AMZN; opex-only at HP | FILING-CHECKED 2026-10-19, 2026-10-21 | FY2025 10-K: 958 filers, perimeters 651 all-op / 29 opex-only / 42 incl. interest / 115 no OI / 64 other (R2 report) |
| OperatingExpenses | operating income | total only where an OI line coexists; component at AJG | FILING-CHECKED 2026-10-19 | |
| OperatingCostsAndExpenses | operating income | component (excludes SG&A); never total opex | FILING-CHECKED (CVX) | |
| SellingGeneralAndAdministrativeExpense | operating income | component; sole-opex OI formula proposal only | FILING-CHECKED (DHI, BBW) | |
| CostOfRevenue / CostOfGoodsAndServicesSold | operating income | cost of sales; take whichever is filed | FILING-CHECKED (AAPL, DHI, BBW) | 172 filers carry both |
| InterestIncomeExpenseNet | interest | bank NII only; non-banks use it as net interest expense | FILING-CHECKED 29/30 [32] + Citigroup/FLG/ANDE 2026-10-19 | 768 non-bank-like CY2023 filers (Frames proxy) |
| InterestRevenueExpenseNet | interest | NOT an exact synonym of NII | definition FILING-CHECKED; usage DATA-INFERRED | operating + nonoperating |
| InterestExpense / InterestExpenseOperating | interest | bank total interest expense, period-scoped (see bank row); non-banks per company | FILING-CHECKED 30/30 [32]; era 2026-10-22 | |
| InterestExpenseNonoperating / InterestIncomeExpenseNonoperatingNet | interest | non-bank below-the-line; conditional on check I-2 | FILING-CHECKED (PLD, AMZN, BBW) | R-file sign differs from stored sign |
| InterestExpenseDebt | interest | debt interest only; inside CostsAndExpenses at CVX | FILING-CHECKED | |
| InvestmentIncomeInterest | interest | NEVER bank interest income; fine for non-bank interest income | FILING-CHECKED (AMZN; banks [32]; FLG 2026-10-19) | |
| LongTermDebt | debt | total long-term debt (net, no leases) where present AND it matches the BS carrying lines; face value at AMZN/GOOG, rounded at AAPL 10-Q, sub-item at MAR/TSCO (relayed) | FILING-CHECKED (PLD, ARCC) 2026-10-19; CORRECTED 2026-10-21 by Verifier file 35 | do not add current on top |
| LongTermDebtNoncurrent + LongTermDebtCurrent | debt | safe pair | FILING-CHECKED (AAPL, DUK) | AMZN noncurrent only |
| NotesPayable / NotesPayableCurrent / LongTermNotesPayable / ConvertibleNotesPayable / LongTermLineOfCredit | debt | components or last resort; NotesPayable includes current portion | definition FILING-CHECKED; coexistence NOT_RUN [31] | |
| AdvancesFromFederalHomeLoanBanks / SubordinatedDebt | debt | bank components, not totals | FILING-CHECKED (EWBC, AX) | stored bank total debt misses them |
| FinanceLeaseLiability* | debt | lease, not debt unless policy says so | definition FILING-CHECKED | ASC 842 tag |
| CashAndCashEquivalentsAtCarryingValue | cash | safe cash-and-equivalents; USD only | FILING-CHECKED 7 filers 2026-10-19 | |
| Cash | cash | only where it is the face cash row (PGR) | FILING-CHECKED | not "cash excluding equivalents" |
| CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | cash | cash-flow total from 2018; not balance-sheet cash | FILING-CHECKED | 7 filers in 2013, 5,475 in 2023 |
| RestrictedCash family | cash | components; sum within one family | FILING-CHECKED (ARCC, HTZ, AX) | |
| NetIncomeLoss | net income | parent net income from 10-K/10-Q; never DEF 14A | FILING-CHECKED 5 filers 2026-10-19 | |
| ProfitLoss | net income | consolidated incl. NCI; the row named "Net income" at GE/DHI/ANDE/BRK/PNC | FILING-CHECKED | 235 CY2023 filers have only ProfitLoss |
| IncomeLossAttributableToParent | net income | NEVER net income (pre-tax by definition) | FILING-CHECKED (HTZ) | |
| EarningsPerShareBasic / Diluted | EPS | statement-level undimensioned fact; exceptions BRK (class axis), ANDE FY2025 | FILING-CHECKED | |
| EarningsPerShareBasicAndDiluted / WeightedAverageNumberOfShareOutstandingBasicAndDiluted | EPS | era-limited, pre-2021 mostly | DATA-INFERRED (Frames) + taxonomy presence | 3,156 -> 8 filers; gone from 2025 taxonomy |
| WeightedAverageNumberOfSharesOutstandingBasic / DilutedSharesOutstanding | shares | safe as filed | FILING-CHECKED | |
| dei:EntityCommonStockSharesOutstanding | shares | per class; sum classes | FILING-CHECKED (BRK, GOOGL) | |
| dei:EntityPublicFloat | shares | public float only, validate scale; never market cap | FILING-CHECKED (BRK, GOOGL) | |
| LongTermDebtAndCapitalLeaseObligations (+Current) | debt | label check required; often plain debt; dimension-only at CAT/APD | FILING-CHECKED (CAT, APD) 2026-10-21 | 297 FY2025 10-K filers use it on a debt-only label (R2 report) |
| CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents (on the balance sheet) | cash | perimeter uncertain when labelled plain cash | FILING-CHECKED presentation (CMI) 2026-10-21 | 272 FY2025 BS cash rows, 207 labelled plain cash |
| PaymentsToAcquirePropertyPlantAndEquipment | capex | safe as one capex line; NOT total capex where other capex lines exist | FILING-CHECKED (Air Lease) 2026-10-21; no card yet | 193 FY2025 filers have it plus other capex lines |
| DepreciationDepletionAndAmortization / DepreciationAndAmortization | D&A | per statement; IS and CF values can differ | FILING-CHECKED (AEO) 2026-10-21; no card yet | 300 filers add other D&A lines beside the combined tag |
| GrossInvestmentIncomeOperating | investment income | BDC total investment income ONLY (null-SIC funds); NEVER insurers/ETPs/SPACs | FILING-CHECKED (ARCC; CINF, TRV, PRU) 2026-10-22; cards/investment-income-and-funds.md | sole tag of `bdc_total_investment_income`: 47 of its 118 filers are insurers (gross note line), 42 BDCs |
| NetInvestmentIncome | investment income | two concepts: insurer face NII (safe) / BDC PRE-tax NII; never pooled | FILING-CHECKED (CINF, TRV, PRU, ARCC) 2026-10-22 | unmapped; does NOT feed bdc_total_investment_income |
| InvestmentIncomeOperatingAfterExpenseAndTax | investment income | BDC after-tax NII; first choice for the BDC NII row | FILING-CHECKED (ARCC) 2026-10-22 | exists from 2020-09 only |
| InvestmentIncomeNet | investment income | NOT insurer NII (differs in 252 of 778 periods; includes gains at PGR) | DATA-INFERRED (PGR arithmetic on face R3) 2026-10-22 | |
| AssetsNet / StockholdersEquity | BDC net assets | StockholdersEquity first (face), AssetsNet alternate after equality check | FILING-CHECKED (ARCC equity); AssetsNet DATA-INFERRED (86% equal, 36 BDCs) 2026-10-22 | |
| LoansAndLeasesReceivableNetReportedAmount / NotesReceivableNet | bank net loans | pre-CECL era / alternate inside the period-scoped set | FILING-CHECKED (OSBC face) 2026-10-22 | `LoansReceivableNet` = removed element, keep for 2015-2020 (143 cos to 2020-03) |
| FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest / FinancingReceivableAllowanceForCreditLosses / LoansAndLeasesReceivableAllowance | bank allowance | period-scoped set (CECL -> generic -> pre-CECL); reject 0 when another is non-zero | FILING-CHECKED (EFSC, OSBC) 2026-10-22; pairs 94-97% equal | `AllowanceForLoanAndLeaseLosses*` are roll-forward components, never the balance |
| PremiumsEarnedNet | insurer / managed care | safe single tag where filed (current periods) | FILING-CHECKED (UNH, PGR) 2026-10-22; cards/insurance-and-managed-care.md | managed-care history pre-2024 on removed/deprecated health tags |
| PolicyholderBenefitsAndClaimsIncurredNet | insurer / managed care | safe single tag where filed; never BenefitsLossesAndExpenses | FILING-CHECKED (UNH "Medical costs", PGR) 2026-10-22 | PolicyholderBenefitsAndClaimsIncurredHealthCare deprecated 2024 |
| RegulatoryAssetsCurrent + RegulatoryAssetsNoncurrent | utility | safe pair from the face; plain RegulatoryAssets = note TOTAL (94% equal), never the noncurrent line | FILING-CHECKED (CPK) 2026-10-22; cards/utility-regulatory-and-crypto.md | |
| CryptoAssetFairValue (+Current/Noncurrent) | crypto | classified pair where the face is classified; plain tag only where it is the face line (MSTR) | FILING-CHECKED (MSTR, CLSK) 2026-10-22 | CLSK plain tag = narrative subset; `CryptoAssetNoncurrent` is not an element; from 2022 only |
| InterestExpenseNonoperating | non-bank gross interest expense (2024+ schema) | strong `interest_expense` fallback candidate, label check for ", net"; NOT mapped today | FILING-CHECKED (CL 0000021665-25-000053 R2, AVY 0000008818-25-000049 R4, ROL net label) 2026-10-24; element absent from 2015-2023 schemas | ~1,542 companies with recent IEN and no recent mapped interest tag (DATA-INFERRED); cards/interest.md |
| InterestAndDebtExpense | non-bank interest | usable only with a perimeter flag (FASB calc parent of IEN + extinguishment items; can be net) | FILING-CHECKED (TXN, ODFL, OXY) 2026-10-24 | ODFL's own calc puts it under NonoperatingIncomeExpense |
| IncreaseDecreaseInAccountsPayableAndAccruedLiabilities | cash-flow working capital | NEVER map as cf_ap_change (FASB calc parent of IncreaseDecreaseInAccountsPayable + accrued); a visible "combined" reason | FILING-CHECKED (LNG 0000003570-25-000107 R6, PCAR, PGR labels via FSDS) 2026-10-24 | face line of 244 of 358 cf_ap_change residue companies (FSDS 2025q4) |
| IncreaseDecreaseInReceivables / IncreaseDecreaseInAccountsAndOtherReceivables / IncreaseDecreaseInAccountsAndNotesReceivable | cash-flow working capital | perimeter decision (all receivables / AR + other / AR + notes), never a silent cf_ar_change synonym | DOC-CHECKED (FASB 2026 calc and definitions); XEL 0000072903-25-000257 R4 prints "Accounts receivable" on AccountsAndOther | 174 of 329 cf_ar_change residue companies; 3M sign split (migration 0036) |
| OtherNonoperatingIncomeExpense | other income | FASB calc CHILD of NonoperatingIncomeExpense ("other" component); fills other_income_expense_net only if the concept is defined as the presented "other" line | FILING-CHECKED (SWKS 0000004127-25-000085 R3, ROL R4) 2026-10-24 | face line of 185 of 275 residue companies; definition decision for the Standardization Lead |
| PaymentsOfOrdinaryDividends | dividends paid | safe dividends_paid fallback (FASB calc child of PaymentsOfDividends; same perimeter wording incl. preferred/NCI) | FILING-CHECKED (PFE 0000078003-25-000150 R8) 2026-10-24; JNJ, WWD, WTS, ZTS via FSDS | not mapped; 176 active companies |
| DepreciationAmortizationAndAccretionNet | D&A (financials) | cash-flow D&A line of banks/insurers (JPM, C, AIG, ALL, AJG); includes accretion, so a perimeter flag | FILING-CHECKED (JPM 0001628280-25-048859 R8) 2026-10-24 | no calc relationship in FASB 2026 |
| Depreciation + AdjustmentForAmortization / AmortizationOfIntangibleAssets | D&A composition | sum of FASB calc children of DepreciationDepletionAndAmortization when no total is on the CF face | FILING-CHECKED (NUE 0001193125-25-276207 R6: 910 + 191) 2026-10-24 | 66 of 126 D&A residue companies; debt-cost amortization excluded |
