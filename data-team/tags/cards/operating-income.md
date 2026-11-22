# Card family: Operating income and the cost lines (written 2026-10-19 by the Tag Expert)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

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

## 7. FSN-era relays processed (Tag Expert, 2026-11-09)
FSN store: `operating_income_resolved` mapped at 466 of 632 latest 10-Ks, all `OperatingIncomeLoss` on the IS face; **never note-sourced** (Verifier draw 2026-11-03). Pre-tax: 501 `…BeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` + 71 `…MinorityInterestAndIncomeLossFromEquityMethodInvestments`. Tax: 612 `IncomeTaxExpenseBenefit`.
Relayed lessons (FILING-CHECKED by the named role; not re-opened by me):
- **Non-dimensional `OperatingIncomeLoss` used for SEGMENT totals that reconcile to pretax income**: ELV "Reportable segments' operating gain" (0001156039-26-000013 R116), SLB "Pretax segment operating income" (0000950170-24-006884 R85), IP segment operating profit (0000051434-16-000042 R136); WPC uses it for income before income taxes in the tax note (0001025378-16-000062 R106) (Verifier). This is why the FSN store never note-sources OI.
- PLD prints a custom pre-gains operating line 3,414,302K above the us-gaap `OperatingIncomeLoss` 4,357,864K (after gains) (0001193125-26-051453 R4) (Data Chief): the us-gaap line is the face OI; the custom line is a sub-measure.
- REIT totals: OHI "Total expenses" on `OperatingExpenses` includes interest (58,238K of 177,670K, 0000888491-22-000029 R4); DOC likewise. HCP's `OperatingExpenses` is only the property "Operating" line (0001628280-17-007720 R4). Revenue minus either is not operating income (Standardization Lead, Data Chief, Data Verifier).
- `NonoperatingIncomeExpense` on a face "Interest expense" row: DLH 15,031K = IEN 13,360 − interest income 71 + financing-cost amortization 1,742 (0000785557-25-000159 R3, R55). Never interest expense by name (Data Verifier). `OtherNonoperatingIncomeExpense` is the face "Other (income) expense-net" at USFD (0001665918-26-000008 R5).
- **Tax sign and scope**: ODFL's FY2018 10-K tags its 104.9M Tax Act remeasurement BENEFIT as a positive 3-month `IncomeTaxExpenseBenefit` in the provision note: not the Q4 provision (0001564590-19-004755 R33). CMG's FY2020 10-K flips the sign of the FY2018 comparative (−91,883K vs +91,883K) (Data Verifier). In the FSN store, the latest copy printing a key wins, so CMG's flipped comparative would win: a vintage-sign check is needed before Q4 derivation.
- `EffectiveIncomeTaxRateContinuingOperations` is unit `pure` (a ratio): never derive Q4 = FY − 9M (5,079 wrong derived cells at 618 cohort companies; 18,855 stored derived facts population-wide) (Data Triage, Data Engineer, DATA-INFERRED). Not an FSN-write data point.

## 8. Folded in from the FSN-expert per-tag cards (2026-11-10): the pretax pair
- `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` (100 top-100 names, 3,200 face lines) and `…MinorityInterestAndIncomeLossFromEquityMethodInvestments` (84 names, 2,330 lines). **Filers switch between them with no change in what is printed**: MSFT at the Q2 FY2022 10-Q 0001564590-22-002324, same label "Income before income taxes", both calc children of NetIncomeLoss (FSN expert; MSFT FY2026 10-K 0001193125-26-323660 R2 FILING-CHECKED by them). Rule: map either as pretax per filing; where a filing prints both, they are different lines (before vs after equity-method income), so check the calc tree. Consistent with the FSN rule (p10 / p20) and the playbook.

## 9. Pretax income under non-pretax tags (Ritwik relay 2026-11-11, work/tag-library/ranks-1-50 aea0cf4 data-team/47-fsn-store/company_tag_map/ranks_1_50.csv (evidence_adsh + label per row); DATA-INFERRED, not yet filing-checked by the Verifier)
- "Income before income taxes" on `IncomeLossAttributableToParent` (COST, SHOP; standard label is "…before Tax", so this is correct use, see library row), on `IncomeLossIncludingPortionAttributableToNoncontrollingInterest` (PG) and on `IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest` (ORCL; an AFTER-tax tag, a misuse of the same kind as Chubb/ACE 2014-15, net-income-and-shares.md §10).
- **Rule**: identify pretax income by structure, not tag: the line that is the +1 calc sibling of the income-tax line under one parent (parent = net income / ProfitLoss), with a pretax label. A ProfitLoss-family NI rule must exclude a line that has a tax line beneath it.

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.

## 10. Ritwik (cloud) card notes 1, 20, 23, 28 (2026-11-11; DATA-INFERRED)
- Both "…before Tax" concepts are PRETAX by standard label: `IncomeLossAttributableToParent` (MRVL, COP 2022-24, TMUS 2021) and `IncomeLossIncludingPortionAttributableToNoncontrollingInterest` (MCK 0000927653-26-000069 IS l11; PSX 0001534701-26-000006 IS l18; PG). Map income_before_tax below the two standard pretax tags.
- After-tax continuing-ops tags on a face "income before income taxes" line: EQIX, GLW, ORCL, Chubb/ACE 2014-15: map by label and position, flag.
- Insurer "Income from operations before income tax expense" (ALL) is pretax, not operating income.
- Cost of revenue = the line directly above Gross profit as printed (LMT 0001193125-16-476010 l13; later 0001628280-26-004195 l13, not the same-label subtotal at l10); a CostOfRevenue "total costs and expenses" with no gross-profit line is not cost of revenue (BA incl. Boeing Capital interest); no total cost line = sum of lines under the cost heading (VZ, TMUS, T, DIS 2014-18; ruling (a)).
- Not interest expense: MET "interest credited to policyholder account balances"; HPE financing interest inside cost of sales; HOOD "net interest revenues".

## 11. operating_expenses definition (Dhairya ruling 2026-11-12; applies analytics.canonical_concept 53 / 208, "SG&A + R&D…", resolved = gross profit − operating income)
1. Opex = operating costs below cost of revenue, down to operating income; never includes cost of revenue.
2. A printed total that excludes cost of revenue (ties to GP − OI: MRVL 2,857.8) is mapped.
3. Otherwise: component sum of EVERY face line between gross profit (or cost of revenue) and operating income, tying EXACTLY to GP − OI (credit-typed lines enter negated: QCOM R&D 9,042 + SG&A 3,110 + other 39 = 12,191 = 44,284 − 19,738 − 12,355), else blank with a reason.
4. CostsAndExpenses or any total that includes cost of revenue → combined, never opex (ACN, MPC, VRTX, STX, SPGI, UBER, T, TMUS, BMY, NEM, SCCO, WELL keyed otherwise: reader key errors).
5. (REFINED by Dhairya 2026-11-12) A corporate IS that prints NO cost-of-revenue-type line anywhere, and whose printed total contains no cost-of-sales-type component (cost of products/services, fuel, purchased power, food and paper, cost of operations, production/operating costs, direct or distribution/servicing costs), maps that total as opex: no COGS, so GP = revenue and the total = GP − OI (BKNG `OperatingExpenses`; Visa `CostsAndExpenses` 17,793M). If the total contains any cost-of-sales-type line → combined (NEE fuel and purchased power; UNP fuel; MCD food and paper; BLK distribution/servicing and direct fund costs; the sector template decides display). Banks/insurers → sector template.
6. Applied (Dhairya 2026-11-12): COP production and operating costs and VLO `CostOfGoodsAndServicesSoldOverhead` are cost of sales, so never opex; DHR, MDT, LMT, BA = rule-3 component sums where the R page shows the tie; DE, IBM, KLAC, DIS, VZ blank only where the R page confirms no OI line or no exact tie (cite the R page, else a dispute).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.93). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.93. 30 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `IncomeTaxExpenseBenefit`
- **Meaning:** Income Tax Expense (Benefit) (us-gaap, duration, debit). Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations.
- **Data point definition:** income_tax_expense: Income tax expense (benefit) for the period, as printed;  a benefit is a real negative.
- **Data point:** income_tax_expense; polarity income_tax_expense:signed; role income_tax_expense:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1302 served, 44905 proven, 117 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces IncomeTaxExpenseBenefitContinuingOperations@2013; RestatementOfPriorYearIncomeTaxEffects@2020

### `NetIncomeLoss`
- **Meaning:** Net Income (Loss) Attributable to Parent (us-gaap, duration, credit). The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income; role net_income:primary#1
- **Rules:** X77; C29; resolver functions resolve
- **Evidence:** 105 companies, 1212 served, 28185 proven, 106 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InvestmentCompanyNetAssetsFromOperationsIncreaseDecrease@2023; RestatementOfPriorYearIncomeNetOfTax@2020

### `SellingGeneralAndAdministrativeExpense`
- **Meaning:** Selling, General and Administrative Expense (us-gaap, duration, debit). The aggregate total costs related to selling a firm's product and services, as well as all other general and administrative expenses. Direct selling expenses (for example, credit, warranty, and advertising) are expenses that can be directly...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.; sga_expense: Selling, general and administrative expense for the period.
- **Data point:** sga_expense; operating_expenses; polarity sga_expense:positive; role sga_expense:primary#1
- **Rules:** I15; I16; I17; I18; family resolve_all.NARROW[sga_expense]
- **Evidence:** 66 companies, 1140 served, 3623 proven, 73 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces RelatedPartyTransactionSellingGeneralAndAdministrativeExpensesFromTransactionsWithRelatedParty@2023

### `CostOfGoodsAndServicesSold`
- **Meaning:** Cost of Product and Service Sold (us-gaap, duration, debit). The aggregate costs related to goods produced and sold and services rendered by an entity during the reporting period. This excludes costs incurred during the reporting period related to financial services rendered and other revenue generat...
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#2
- **Rules:** I02; I03; I04
- **Evidence:** 65 companies, 955 served, 16174 proven, 62 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AdvertisingRevenueCost@2018; AssetManagementCosts@2018; CasinoExpenses@2018; ConcessionsCosts@2018 (+62 more)

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

### `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`
- **Meaning:** Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest (us-gaap, duration, credit). Amount of income (loss) from continuing operations, including income (loss) from equity method investments, before deduction of income tax expense (benefit), and income (loss) attributable to noncontrolling interest.
- **Data point definition:** income_before_tax: Income from continuing operations before income taxes, as printed (incl. equity-method income where the filer places it above tax).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** income_before_tax; other_income_expense_net; role income_before_tax:primary#1
- **Rules:** I36; I37
- **Evidence:** 95 companies, 816 served, 32500 proven, 81 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; RetrospectiveEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAmountAfterApplication@2012 (+2 more)

### `Revenues`
- **Meaning:** Revenues (us-gaap, duration, credit). Amount of revenue recognized from goods sold, services rendered, insurance premiums, or other activities that constitute an earning process. Includes, but is not limited to, investment and interest income before deduction of interest expens...
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; revenue: Total revenues (net sales) for the period as printed: the top line of the income statement, after returns and allowances (+1 more)
- **Data point:** revenue; gross_profit
- **Rules:** X123
- **Evidence:** 69 companies, 708 served, 12391 proven, 34 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToRevenueNet@2013; CashFlowHedgeGainReclassifiedToRevenue@2013; CashFlowHedgeLossReclassifiedToRevenue@2013; DevelopmentStageEnterpriseCumulativeRevenue@2012 (+10 more)

### `InvestmentIncomeInterest`
- **Meaning:** Investment Income, Interest (us-gaap, duration, credit). Amount before accretion (amortization) of purchase discount (premium) of interest income on nonoperating securities.
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).; other_income_expense_net: All non-operating, non-interest income and expense between operating income and pretax income (ruling 2026-11-21 d).
- **Data point:** interest_income; other_income_expense_net; polarity interest_income:signed; role interest_income:primary#2
- **Rules:** I26; I27; family resolve_all.NARROW[interest_income]
- **Evidence:** 50 companies, 616 served, 1444 proven, 48 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 4 open hit(s) at 3 companies, e.g. AMGN interest_income 2021-12-31 (export) (pattern_hits.csv); pattern P06 own_10k_year_hidden: 5 open hit(s) at 1 companies, e.g. CRM interest_income 2015-01-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (5); P05 (4)

### `OtherNonoperatingIncomeExpense`
- **Meaning:** Other Nonoperating Income (Expense) (us-gaap, duration, credit). Amount of income (expense) related to nonoperating activities, classified as other.
- **Data point definition:** interest_income: Consolidated interest income for the period (X94).; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. (+1 more)
- **Data point:** other_income_expense_net; interest_income; operating_expenses; polarity other_income_expense_net:signed; role other_income_expense_net:primary#2
- **Rules:** X59; I28; I29; I30; I31; I32; I33; I34; I35; resolver functions COMBINED_YIELDS_TO
- **Evidence:** 67 companies, 607 served, 1993 proven, 46 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `GrossProfit`
- **Meaning:** Gross Profit (us-gaap, duration, credit). Aggregate revenue less cost of goods and services sold or operating expenses directly attributable to the revenue generation activity.
- **Data point definition:** gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc]; operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** gross_profit; operating_expenses
- **Rules:** X36; X56; X80; C10; I08; resolver functions apply_absent_in_own_filing; resolve; derive_gross_profit
- **Evidence:** 44 companies, 499 served, 17157 proven, 71 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationGrossProfitLoss@2020

### `CostOfRevenue`
- **Meaning:** Cost of Revenue (us-gaap, duration, debit). The aggregate cost of goods produced and sold and services rendered during the reporting period.
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#1
- **Rules:** I02; I03; I04
- **Evidence:** 32 companies, 429 served, 7811 proven, 27 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCostOfSales@2020; RelatedPartyCosts@2023

### `OperatingExpenses`
- **Meaning:** Operating Expenses (us-gaap, duration, debit). Generally recurring costs associated with normal operations except for the portion of these expenses which can be clearly related to production and included in cost of sales or services. Includes selling, general and administrative expense.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#1
- **Rules:** I14; I09; I10; I11; I12; I13; family resolve_all.NARROW[operating_expenses]
- **Evidence:** 36 companies, 352 served, 11930 proven, 11 certified cells; last verified 2026-11-15
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

### `CostOfGoodsSold`
- **Meaning:** Cost of Goods Sold (Deprecated 2018-01-31) (us-gaap, duration, debit). Total costs related to goods produced and sold during the reporting period.
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#3
- **Rules:** I02; I03; I04
- **Evidence:** 29 companies, 141 served, 2199 proven, 3 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaced by CostOfGoodsAndServicesSold@2018; [ProductMember@2018; srt:ProductOrServiceAxis]@2018; replaces CashFlowHedgeGainLossReclassifiedToCostOfSalesNet@2013; CashFlowHedgeGainReclassifiedToCostOfSales@2013; CashFlowHedgeLossReclassifiedToCostOfSales@2013

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

### `CostsAndExpenses`
- **Meaning:** Costs and Expenses (us-gaap, duration, debit). Total costs of sales and operating expenses for the period.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses
- **Rules:** X117; I09; resolver functions apply_cost_and_opex
- **Evidence:** 21 companies, 95 served, 190 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces DevelopmentStageEnterpriseCumulativeExpense@2012

### `BenefitsLossesAndExpenses`
- **Meaning:** Benefits, Losses and Expenses (us-gaap, duration, debit). The total amount of expense recognized during the period for future policy benefits, claims and claims adjustment costs, and for selling, general and administrative costs.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses; polarity operating_expenses:positive; role operating_expenses:primary#2
- **Rules:** I14; I09; I10; I11; I12; I13
- **Evidence:** 2 companies, 24 served, 101 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `ProfitLoss`
- **Meaning:** Net Income (Loss), Including Portion Attributable to Noncontrolling Interest (us-gaap, duration, credit). The consolidated profit or loss for the period, net of income taxes, including the portion attributable to the noncontrolling interest.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income
- **Rules:** X77; F03; F04; resolver functions run
- **Evidence:** 3 companies, 23 served, 1314 proven, 11 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CashFlowHedgeGainLossReclassifiedToEarningsNet@2013; CashFlowHedgeGainReclassifiedToEarnings@2013; CashFlowHedgeLossReclassifiedToEarnings@2013; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012 (+8 more)

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

### `OperatingCostsAndExpenses`
- **Meaning:** Operating Costs and Expenses (us-gaap, duration, debit). Generally recurring costs associated with normal operations except for the portion of these expenses which can be clearly related to production and included in cost of sales or services. Excludes Selling, General and Administrative Expense.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses
- **Rules:** none
- **Evidence:** 3 companies, 18 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces RelatedPartyTransactionExpensesFromTransactionsWithRelatedParty@2023

### `IncomeLossIncludingPortionAttributableToNoncontrollingInterest`
- **Meaning:** Income (Loss), Including Portion Attributable to Noncontrolling Interest, before Tax (us-gaap, duration, credit). Amount, before tax, of income (loss) including portion attributable to noncontrolling interest. Includes, but is not limited to, income (loss) from continuing operations, discontinued operations and equity method investments.
- **Data point definition:** income_before_tax: Income from continuing operations before income taxes, as printed (incl. equity-method income where the filer places it above tax).
- **Data point:** income_before_tax
- **Rules:** none
- **Evidence:** 4 companies, 15 served, 85 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces RestatementOfPriorYearIncomeGross@2020

### `IncomeLossAttributableToParent`
- **Meaning:** Income (Loss) Attributable to Parent, before Tax (us-gaap, duration, credit). Amount, before tax, of income (loss) attributable to parent. Includes, but is not limited to, income (loss) from continuing operations, discontinued operations and equity method investments.
- **Data point definition:** income_before_tax: Income from continuing operations before income taxes, as printed (incl. equity-method income where the filer places it above tax).
- **Data point:** income_before_tax
- **Rules:** none
- **Evidence:** 3 companies, 11 served, 39 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `TaxesOther`
- **Meaning:** Taxes, Other (us-gaap, duration, debit). Amount of tax expense classified as other.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income.
- **Data point:** operating_expenses
- **Rules:** none
- **Evidence:** 1 companies, 8 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none

### `IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest`
- **Meaning:** Income (Loss) from Continuing Operations, Net of Tax, Including Portion Attributable to Noncontrolling Interest (us-gaap, duration, credit). Amount after tax of income (loss) from continuing operations including portion attributable to the noncontrolling interest.
- **Data point definition:** income_before_tax: Income from continuing operations before income taxes, as printed (incl. equity-method income where the filer places it above tax).
- **Data point:** income_before_tax
- **Rules:** none
- **Evidence:** 1 companies, 2 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationIncomeLossFromContinuingOperationsBeforeExtraordinaryItems@2020; NewAccountingPronouncementOrChangeInAccountingPrincipleEffectOfChangeOnIncomeFromContinuingOperations@2016; NewAccountingPronouncementOrChangeInAccountingPrincipleEffectOfChangeOnOperatingResults@2020

### `Capital`
- **Meaning:** Banking Regulation, Total Capital, Actual (us-gaap, instant, credit). Amount of total capital as defined by regulatory framework.
- **Data point:** none (the resolver never serves it)
- **Rules:** C02; B29; resolver functions resolve; shares
- **Evidence:** 0 companies, 0 served, 0 proven, 0 certified cells; last verified -
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
