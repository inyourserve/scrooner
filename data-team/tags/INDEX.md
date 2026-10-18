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
