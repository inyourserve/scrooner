# Tag index (seed; the Tag Expert extends it)

| Tag | Family | Verdict | Evidence | Note |
|---|---|---|---|---|
| InterestIncomeExpenseNet | bank net interest income | safe single tag | FILING-CHECKED, 29 of 30 banks [32] | still needs the full-population check |
| NoninterestIncome | bank | safe single tag | 29/30 [32] | |
| NoninterestExpense | bank | safe single tag | 30/30 [32] | |
| InterestAndDividendIncomeOperating / InterestIncomeOperating | bank total interest income | safe | 30/30 [32] | |
| InterestExpenseOperating / InterestExpense | bank total interest expense | safe | 30/30 [32] | |
| Deposits | bank | safe, 27 of 30 | [32] | BANR, CARV components only; TFSL no total |
| FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss | bank net loans | per-period set | 22/30 [32] | pre-CECL tags still used (FCCO) |
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
| InterestExpense / InterestExpenseOperating | interest | bank total interest expense; non-banks per company | FILING-CHECKED 30/30 [32] | |
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
