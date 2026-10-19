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
| FLG | InvestmentIncomeInterest | securities interest line only ("Interest" 19,785K of 116,469K total interest and dividend income, Q3-25) | 10-Q 0001104659-25-106961 R4 (2026-10-19) |
| Citigroup | Revenues | "Total revenues, net of interest expense" (net revenue; 9M 2025 65,354M = NII 44,127M + noninterest 21,227M) | 10-Q 0000831001-25-000154 R2 (2026-10-19) |
| PGR | InterestAndDividendIncomeOperating | insurer's "Investment income" (3,583M), not bank interest income | 10-K 0000080661-26-000086 R3 |
| PGR | Cash | row "Cash and cash equivalents" (125M) | 10-K 0000080661-26-000086 R4 |
| ANDE | InterestIncomeExpenseNet | non-bank "Interest expense, net"; stored -47,159K while the R-file prints 47,159 | 10-K 0000821026-26-000010 R3 + companyconcept |
| ANDE | EPS (FY2025 10-K) | face EPS tagged IncomeLossFromContinuingOperationsPerBasicShare / PerDilutedShare; EarningsPerShareBasic absent in that 10-K, present FY2024 (3.35) and in 10-Qs | 10-K 0000821026-26-000010 R3 vs 0000821026-25-000050 |
| BBW | InterestIncomeExpenseNonoperatingNet | "Interest income, net"; stored +801K, R-file prints (801) | 10-K 0001437749-26-012501 R4 |
| PLD | OperatingIncomeLoss | includes ~943.6M of real estate disposition gains; pre-gains operating income is custom pld_ | 10-K 0001193125-26-051453 R4 |
| AJG | OperatingExpenses | one expense line labelled "Operating", not a total | 10-K 0001628280-26-008662 R3 |
| AJG | RevenueFromContractWithCustomerExcludingAssessedTax | "Total revenues" (custom components) | same R3 |
| CVX | Revenues | "Total Revenues and Other Income" incl. equity-affiliate and other income; sales are RCFC | 10-K 0000093410-26-000078 R3 |
| CVX | cash and long-term debt | balance-sheet cash is custom cvx_CashAndCashEquivalentsExcludingTimeDeposits; "Long-term debt" is LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities | 10-K 0000093410-26-000078 R5 |
| GE | CostsAndExpenses | includes "Interest and other financial charges" 843M; no operating income line | 10-K 0000040545-26-000008 R3 |
| GE | Revenues (quarterly, FY2016 10-K) | 3-month undimensioned facts are the GE Capital total (Q2 2015 = 2,690M, frame CY2015Q2) while the 12-month facts are consolidated | 0000040545-17-000010 R164 + companyconcept |
| DUK | ShortTermBorrowings | row "Notes payable and commercial paper" | 10-K 0001326160-26-000014 R6 |
| BRK, GOOGL | EPS / EntityCommonStockSharesOutstanding | only class-dimensioned facts (Class A/B equivalents; A/B/C cover) | BRK 0001193125-26-083899 R1/R4; GOOGL 0001652044-26-000018 R1 |
