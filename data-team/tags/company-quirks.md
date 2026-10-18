# Company-specific tag quirks (filing-checked unless marked)

Never turn these into global mappings. Source file in brackets.

| Company | Tag | What it really is | Evidence |
|---|---|---|---|
| BANR | OperatingIncomeLoss | total noninterest income, not operating income | 10-K R-file [32] |
| PEBO | OperatingIncomeLoss | income before taxes | [32] |
| PEBK | LoansReceivableHeldForSaleAmount | mis-tag, not a loan balance mapping source | [32] |
| SFNC, CARV | IncomeLossAttributableToParent | used where other filers use a different line | [32] |
| HTZ | IncomeLossAttributableToParent | pretax income is tagged with this | [26] |
| CVX, AJG, HTZ | CostsAndExpenses | total includes interest expense; Revenues minus it equals pretax income, NOT operating income | CVX 0000093410-26-000078 R3; AJG 0001628280-26-008662 R3; HTZ 0001657853-26-000008 R7 [26] |
| CCB, SFNC, CARV | InvestmentIncomeInterest | interest from securities only | [32] |
| BANR (2023), FCCO (2021) | InvestmentIncomeInterest | total interest income | [32] |
| PEBK (Q2-23) | InvestmentIncomeInterest | net interest income itself | [32] |
| ANDE | RevenueFromContractWithCustomerExcludingAssessedTax | the ASC 606 subset only (1.40B vs 11.26B total revenue) | [28] |
| DCOM, MRBK, AX | RevenueFromContractWithCustomerExcludingAssessedTax | a fee subset (service charges / wealth management), not bank revenue | [32] |
| GE | quarterly revenue | the GE Capital segment figure, not GE consolidated | [28] |
| IVDA | cash tag | a TWD-unit component, not USD cash | core.fact 45910028 [29] |
| FDCT | plain-cash tag | filed as cash plus restricted cash in the 10-Q/A | [29] |
| CDNL | NotesPayable | gross total filed beside its own net parts; summing double-counts | 10-K 0001193125-26-120014 R60 [27] |
| MGNC, LRDC | cash-flow total tag | used for a continuing-operations subtotal once discontinued ops appear | [29] |
| UP, RTB, AIBT | full-year values | tagged with 3-month contexts in a 10-K | [28] |
| LGND | 10-K/A 0000886163-14-000119 | every column shifted one year | [28] |
| AEMD | NetIncomeLoss in DEF 14A | pay-versus-performance figure rounded to $10K; proxy facts are not financial-statement values | 0001683168-26 [28] |
| FLG | income statement title | labelled 'Comprehensive' with the two titles swapped; selecting by title picks the wrong report | [32] |
