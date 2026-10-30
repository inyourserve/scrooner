# Card family: Operating income and the cost lines (written 2026-10-19 by the Tag Expert)

Tags: `us-gaap:OperatingIncomeLoss`, `CostsAndExpenses`, `OperatingExpenses`, `OperatingCostsAndExpenses`, `SellingGeneralAndAdministrativeExpense` (SG&A), `CostOfRevenue`, `CostOfGoodsAndServicesSold`, `CostOfGoodsSold`, `GrossProfit`.
Method, population scope and the skipped DB reads: same as `revenue.md` (Frames = all SEC filers; "bank-like" = also files `NoninterestExpense`; DB reads skipped because pg_stat_activity was 14-18, above 12).

## 1. Official meaning (taxonomy 2025, read 2026-10-19)
| Tag | Period / balance | Definition (shortened) | Status |
|---|---|---|---|
| OperatingIncomeLoss | duration / credit | "The net result for the period of deducting operating expenses from operating revenues." | current |
| CostsAndExpenses | duration / debit | "Total costs of sales and operating expenses for the period." (Calc tree and meta-model traits exclude interest; inbox line on CVX) | current |
| OperatingExpenses | duration / debit | Recurring costs of normal operations except the part in cost of sales; "**Includes** selling, general and administrative expense." | current |
| OperatingCostsAndExpenses | duration / debit | Same text but "**Excludes** Selling, General and Administrative Expense." | current |
| SellingGeneralAndAdministrativeExpense | duration / debit | Aggregate selling costs plus general and administrative | current |
| CostOfRevenue | duration / debit | Aggregate cost of goods produced and sold and services rendered | current |
| CostOfGoodsAndServicesSold | duration / debit | Costs of goods produced/sold and services rendered; "excludes costs ... related to financial services rendered and other revenue generating activities" | current |
| CostOfGoodsSold | n/a | not in the 2025 taxonomy (older; CY2013 only: 1,764 filers, no CY2023 frame) | retired |
| GrossProfit | duration / credit | Revenue less cost of goods and services sold or operating expenses directly attributable | current |

## 2. Who reports it (Frames, all SEC filers, DATA-INFERRED)
| Tag | CY2013 (bank-like) | CY2023 (bank-like) |
|---|---|---|
| OperatingIncomeLoss | 6,025 (17) | 5,351 (25) |
| CostsAndExpenses | 1,634 (2) | 1,329 (2) |
| OperatingExpenses | 4,207 (30) | 3,438 (18) |
| OperatingCostsAndExpenses | 409 (4) | 502 (2) |
| SG&A | 2,546 (14) | 2,097 (14) |
| CostOfRevenue | 1,417 (1) | 1,675 (6) |
| CostOfGoodsAndServicesSold | 988 (0) | 1,895 (6) |
| CostOfGoodsSold | 1,764 (2) | retired |
| GrossProfit | 3,214 (4) | 2,790 (11) |

Cross-tabs CY2023:
- 1,134 of the 1,329 `CostsAndExpenses` filers also file `OperatingIncomeLoss`; **195 file `CostsAndExpenses` with no operating-income fact** (the CVX/AJG/HTZ shape).
- 3,063 of 3,438 `OperatingExpenses` filers also file OperatingIncomeLoss.
- Cost of sales: CostOfRevenue 1,675 and CostOfGoodsAndServicesSold 1,895 overlap in only 172 filers, union 3,398. Companies pick one; 2013 -> 2023 shows a shift from `CostOfGoodsSold` (1,764) toward `CostOfGoodsAndServicesSold` (988 -> 1,895).
- Of the 5,025 filers with `Revenues` or RCFC in CY2023, **645 (13%) have no `OperatingIncomeLoss` fact**.
- Banks: 443 file `NoninterestExpense`; only **25 of them** also file OperatingIncomeLoss (BANR and PEBO are two, both mis-tags). 418 bank-like filers have none.
- Era: the OperatingIncomeLoss population fell from 6,025 to 5,351 (shell and small filer attrition; not a definition change). No ASC 842/CECL break for these tags. SIC-family split not done (DB unavailable).

## 3. How filers use it (filings opened)
| Filing | Statement and rows | Finding |
|---|---|---|
| AAPL 0000320193-25-000079 R3 (me) | Net sales; Cost of sales (`CostOfGoodsAndServicesSold`); Gross margin (`GrossProfit`); R&D; SG&A; "Total operating expenses" (`OperatingExpenses` 62,151M = R&D + SG&A); "Operating income" (`OperatingIncomeLoss` 133,050M) | the textbook multi-step layout; `OperatingExpenses` is the total of operating lines below gross profit, cost of sales is separate |
| AMZN 0001018724-26-000004 R4 (me) | "Total operating expenses" = **`CostsAndExpenses`**, includes cost of sales, fulfilment, technology, marketing, G&A; then "Operating income" (`OperatingIncomeLoss`); then interest income `InvestmentIncomeInterest`, interest expense `InterestExpenseNonoperating` | here `CostsAndExpenses` EXCLUDES interest, as defined; Revenues - CostsAndExpenses = operating income |
| CVX 0000093410-26-000078 R3 (me) | "Total Revenues and Other Income" (`Revenues`, includes equity-affiliate income and other income); "Total Costs and Other Deductions" (`CostsAndExpenses`) includes "Interest and debt expense" (`InterestExpenseDebt`) and "Taxes other than on income"; "Operating expenses" = `OperatingCostsAndExpenses` | `CostsAndExpenses` INCLUDES interest; Revenues - CostsAndExpenses = pretax income; no operating-income line |
| AJG 0001628280-26-008662 R3 (me) | "Total revenues" is RCFC (custom components); "Total expenses" (`CostsAndExpenses`) includes "Interest" (`InterestExpense`), depreciation, amortization and earnout changes; its row "Operating" is **`OperatingExpenses`** used as one expense line, not a total | same shape; `OperatingExpenses` is a COMPONENT here |
| HTZ 0001657853-26-000008 R7 (me) | "Total expenses" (`CostsAndExpenses` 9,334M) includes "Interest expense, net" (`InterestExpenseOperating` 1,077M), gains and a legal settlement; "Income (loss) before income taxes" is tagged `IncomeLossAttributableToParent` | no operating income; interest is operating for a rental company |
| GE 0000040545-26-000008 R3 (me) | "Total costs and expenses" (`CostsAndExpenses` 37,342M) includes "Interest and other financial charges" 843M, R&D and non-operating benefit income; no operating income line | interest inside the total |
| DHI 0000882184-25-000081 R4 (me) | Revenues; Cost of sales (`CostOfRevenue`); SG&A; Other (income) expense; pretax | **no** OperatingIncomeLoss, no CostsAndExpenses, no total opex. Operating profit = Revenues - CostOfRevenue - SG&A (4,424.2M) is only derivable |
| BBW 0001437749-26-012501 R4 (me) | Revenue; cost of merchandise sold; gross profit; SG&A; interest income, net (`InterestIncomeExpenseNonoperatingNet`) ; pretax | no operating income line, SG&A is the only opex row |
| DUK 0001326160-26-000014 R3 (me) | "Total operating revenues"; utility-specific opex tags; "Operating Income" (`OperatingIncomeLoss` 8,626M) | OI present with utility cost tags |
| PLD 0001193125-26-051453 R4 (me) | Total revenues; total expenses (custom `pld_OperatingExpensesBeforeGainsOnRealEstateTransactionsNet`); custom "Operating income before gains"; **gains on real estate**; then "Operating income" (`OperatingIncomeLoss` 4,357.8M) | **the standard tag includes ~943M of disposition gains**; the pre-gains figure is custom |
| ARCC 0001287750-26-000006 R5 (me) | BDC: total investment income, total expenses (`InvestmentIncomeInvestmentExpense`), net investment income | no operating income, no cost of revenue |
| PGR 0000080661-26-000086 R3 (me) | Insurance: total revenues, "Total expenses" (`BenefitsLossesAndExpenses` 73,448M, includes "Interest expense" 278M), pretax | no operating income |
| Banks (30 cohort) [32] | NII, noninterest income/expense, provision, pretax | **no operating-income line on any of 30 face statements**; the only OperatingIncomeLoss facts are BANR's (noninterest income) and PEBO's (pretax) |

### Required answer: which companies report no operating-income subtotal, and what they tag instead
1. **Single-step income statements with `CostsAndExpenses` as total** (CVX, AJG, HTZ, GE: `Revenues` - `CostsAndExpenses` = pretax income). 195 CY2023 filers have `CostsAndExpenses` but no `OperatingIncomeLoss`.
2. **Gross-profit-then-SG&A shapes** (DHI, BBW): `CostOfRevenue` / `CostOfGoodsAndServicesSold`, `GrossProfit`, SG&A, then pretax.
3. **Banks and thrifts**: net interest income, `NoninterestIncome`, `NoninterestExpense`, provision, pretax (418 of 443 bank-like CY2023 filers have no OperatingIncomeLoss).
4. **Insurers**: premiums, `Revenues`, `BenefitsLossesAndExpenses` (PGR).
5. **BDCs / investment companies**: `GrossInvestmentIncomeOperating`, `InvestmentIncomeInvestmentExpense`, `NetInvestmentIncome`, `InvestmentIncomeOperatingAfterExpenseAndTax` (ARCC).
6. Reg S-X 5-03 has no "operating income" caption (data-team/27), so absence is legitimate for these shapes; our not having a fact does not prove the filing lacks the subtotal (custom subtotals exist, e.g. PLD).

## 4. Siblings and confusables
- `OperatingExpenses` (includes SG&A, "total opex" in the AAPL layout) vs `OperatingCostsAndExpenses` (excludes SG&A, CVX "Operating expenses") vs `CostsAndExpenses` (total, includes cost of sales) vs SG&A (a component). Same English label "Operating expenses" appears on all of them across filers.
- `CostOfRevenue` vs `CostOfGoodsAndServicesSold`: companies choose one; 172 file both (CY2023).
- `GrossProfit` for banks does not exist (30/30 [32]).
- `OperatingIncomeLoss` vs custom pre-gains/segment subtotals (PLD).
- `CostsAndExpenses` has two incompatible usages: operating-only (AMZN) and including interest (CVX, AJG, HTZ, GE).

## 5. Known misuses and quirks
- BANR: `OperatingIncomeLoss` = total noninterest income (72,814K FY2025; 44,409K FY2023) [32]. PEBO: = income before income taxes (134,809K FY2025 10-K 0000318300-26-000099; its Q3-2025 10-Q 0000318300-25-000293 R4 prints it that way too, per the inbox, DATA-INFERRED for the 10-Q). Both continue into FY2025 (inbox line, now covered by [32] for the 10-Ks).
- CVX, AJG, HTZ: `CostsAndExpenses` includes interest (reconfirmed by me on the R-files above; CVX's own calculation linkbase lists `InterestExpenseDebt` and `TaxesOther` as children, per inbox, FILING-CHECKED by the sources run). GE adds a fourth (me).
- HTZ pretax is `IncomeLossAttributableToParent`.
- NEW: AJG tags one expense line "Operating" with `OperatingExpenses`, so a rule "OperatingExpenses = total operating expense" is wrong there (me).
- NEW: PLD `OperatingIncomeLoss` includes real estate disposition gains, so it is not comparable with AAPL-type operating income (me).
- NEW: AMZN and CVX show the same tag (`CostsAndExpenses`) with opposite interest treatment (me). A screener "operating margin = 1 - CostsAndExpenses/Revenues" would be right for AMZN and wrong for CVX.

- NEW (me, 2026-10-21, FILING-CHECKED): `OperatingIncomeLoss` is pretax income at AFG 0001042046-26-000010 R5 ("Earnings before income taxes" 1,073M = revenues 8,174M - costs 7,101M) and ELS 0001628280-26-008722 R5 ("Income before taxes and other items" 391,349K); PEBO and BANR mis-tags recur in FY2025 10-Ks. 30 FY2025 10-K filers carry this label shift (DATA-INFERRED).
- NEW (me, 2026-10-21): `CostsAndExpenses` has four perimeters in 958 FY2025 10-K filers (DATA-INFERRED, identities): revenue - CE = OI 651; CE = operating expenses only (GP - CE = OI) 29, e.g. HP 0000047217-25-000071 R3 "Total operating expenses" 8,218M (FILING-CHECKED); revenue - CE = pretax (interest inside) 42, e.g. XOM 0000034088-26-000045 R3 (interest expense 603M inside "Total costs and other deductions" 290,970M, FILING-CHECKED); no OI line 115; other items between CE and OI 64. Detail: R2 report sec. 5.

## 6. Mapping verdict
- `OperatingIncomeLoss`: **safe per company for non-financial filers when the face row is labelled operating income** (FILING-CHECKED: AAPL, AMZN, DUK; PLD only with a gains caveat). **NEVER for banks without a row-label check** (BANR, PEBO).
- `CostsAndExpenses`: **never** to derive operating income or opex (CVX, AJG, HTZ, GE); usable only as "total costs as filed" with the interest question answered per filer. FILING-CHECKED.
- `OperatingExpenses`: safe as total only when a company also files `OperatingIncomeLoss` and the face row is a total (AAPL); component at AJG. Per-company.
- `OperatingCostsAndExpenses`: component; never total opex (CVX).
- SG&A: component, safe as SG&A itself; can serve a gated OI formula only where it is the sole opex row (DHI, BBW), per data-team/27 (PROPOSAL-ONLY).
- `CostOfRevenue` / `CostOfGoodsAndServicesSold`: safe as cost of sales when present and equal to the face "cost of sales" row (AAPL, DHI, BBW FILING-CHECKED); take whichever the company files, and check the other is not a zero component (SHFH [28]).
- `GrossProfit`: safe where present; absent for banks, insurers, BDCs, utilities.
- Evidence class FILING-CHECKED for the named filings; population counts DATA-INFERRED; verified by the Tag Expert (me).
