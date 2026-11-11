# FSN line → concept lookup for the mapper (Tag Expert, 2026-11-11; for the two Ritwik sessions)

Goal (Dhairya, founder order 2026-11-11): unmapped statement lines in the top 100 → 0. Each line gets a concept, or an explicit "structural, not a data point" status with a reason. Every verdict cites the family card that proves it. Nothing here is approved; the mapper still needs its coexistence check and a Verifier draw.

## Baseline (production fsn.*, latest non-amended 10-K per company, top 100 of cohort v1.1, BS/IS/CF, 2026-11-11)
| | lines | companies |
|---|---|---|
| no `line_map` row at all (mapper never ran on that filing) | 5,050 | **41** |
| `unmapped` | 5,670 | 59 |
| `mapped` | 1,079 | 59 |
| `excluded` (parenthetical) / `combined` | 650 / 7 | |
**Step 0 (Engineering, not tags): run the mapper on the 41 companies' filings.** Their lines carry the same standard tags the 62 rules already cover (NetIncomeLoss, Assets, EPS, IncomeTaxExpenseBenefit …), so ~5,000 lines move without any new tag knowledge.

Live rules: 62 rules / 24 concepts (`fsn.concept_rule`). Two rule risks found today:
- **`SalesRevenueGoodsNet` is a revenue rule at p10**: it is usually a COMPONENT ("Product") under `SalesRevenueNet` (MSFT FY2014-17 conflict; revenue.md §8). Keep it only when it is not a calc child of another revenue candidate.
- **Plain `PaymentsToAcquirePropertyPlantAndEquipment` has no std_tag rule**: capex relies on calc position, and 39 top-100 capex lines are unmapped. It is the main capex line at 94 top-100 names (capex-and-da.md §4).

## A. Existing concept, rule missing: map now (counts = top-100 companies printing the tag on the face, unmapped or no row)
| Tag (stmt) | Cos | Concept | Guard (card) |
|---|---|---|---|
| NetCashProvidedByUsedInFinancingActivities (CF) | 100 | cash_flow_financing(_resolved) | `…ContinuingOperations` twin: use only when no total printed (shareholder-returns §4/§6) |
| NetCashProvidedByUsedInInvestingActivities (CF) | 100 | cash_flow_investing(_resolved) | same |
| Goodwill (BS) | 84 | goodwill | face line; never a note segment fact |
| PropertyPlantAndEquipmentNet (BS) | 67 | ppe_net(_resolved) | `PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAsset…AfterAccumulatedDepreciation…` (25 cos) = PP&E incl. finance-lease ROU: map with a perimeter flag, never both |
| AccountsPayableCurrent (BS) | 67 | accounts_payable | not `AccountsPayableAndAccruedLiabilitiesCurrent` (combined) |
| InventoryNet (BS) | 64 | inventory | other face totals exist (FG-only, `InventoryNetOfAllowancesCustomerAdvances…`, `InventoryGross`; OMC WIP is NOT inventory) (balance-sheet-…-other §2) |
| AccountsReceivableNetCurrent (BS) | 63 | accounts_receivable | |
| ShareBasedCompensation (CF) | 74 | sbc | CF add-back; `AllocatedShareBasedCompensationExpense` is the note twin |
| SellingGeneralAndAdministrativeExpense (IS) | 58 | sga_expense | `GeneralAndAdministrativeExpense` (26) + `SellingAndMarketingExpense` (17) are components when printed separately: sum by calc, never one as SG&A |
| ResearchAndDevelopmentExpense (IS) | 48 | research_and_development | JNJ: face R&D is `…ExcludingAcquiredInProcessCost`; RDE there is only the CF IPR&D add-back |
| IncreaseDecreaseInInventories (CF) | 61 | cf_inventory_change | sign: increase in inventory = cash outflow |
| IncreaseDecreaseInAccountsReceivable (CF) | 55 | cf_ar_change | `IncreaseDecreaseInReceivables` (18) and `…AccountsAndNotesReceivable` (CMI) are wider perimeters |
| IncreaseDecreaseInAccountsPayable (CF) | 47 | cf_ap_change | `IncreaseDecreaseInAccountsPayableAndAccruedLiabilities` (30) is COMBINED: never cf_ap_change |
| OperatingExpenses (IS) | 26 | operating_expenses(_resolved) | REITs: OHI's includes interest, DOC's is property-only (operating-income §7) |
| InvestmentIncomeInterest (IS) | 18 | interest_income | NON-banks only; never bank interest income (interest §6) |
| OtherNonoperatingIncomeExpense / NonoperatingIncomeExpense (IS) | 54 / 34 | other_income_expense_net | NonoperatingIncomeExpense can CONTAIN interest (DLH, ODFL calc); label "Interest and other…" = combined |
| PaymentsToAcquirePropertyPlantAndEquipment (CF) | 39 | capex_resolved | add as std_tag (above) |
| LongTermDebtNoncurrent / LongTermDebtCurrent / DebtCurrent / ShortTermBorrowings / LongTermDebtAndCapitalLeaseObligations (BS) | 48/22/26/20/25 | total_debt components (debt lane) | DebtCurrent has 4+ perimeters; LTDACLO includes leases; ShortTermBorrowings can equal LongTermDebtCurrent (debt §8) |
| AmortizationOfIntangibleAssets (IS/CF) | | amortization_of_intangibles | |

## B. Already a rule; unmapped only because the filing has no line_map (Step 0)
NetIncomeLoss, EarningsPerShareBasic/Diluted, IncomeTaxExpenseBenefit, Assets, Liabilities, AssetsCurrent, LiabilitiesCurrent, StockholdersEquity, CashAndCashEquivalentsAtCarryingValue, OperatingIncomeLoss, the pretax pair, CostOfGoodsAndServicesSold, RCFC/Revenues, NetCashProvidedByUsedInOperatingActivities, PaymentsForRepurchaseOfCommonStock, PaymentsOfDividends(CommonStock), InterestExpenseNonoperating, DepreciationDepletionAndAmortization.

## C. Statement lines that are NOT a data point today: give them an explicit structural status with the reason (so they leave the "unmapped" count without a value)
| Tag | Cos | Status reason |
|---|---|---|
| LiabilitiesAndStockholdersEquity | 100 | check total (= Assets; identity I-1), not a display cell |
| CashCashEquivalentsRestrictedCash…PeriodIncreaseDecreaseIncludingExchangeRateEffect; CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents (begin/end) | 96 / 92 | cash-flow identity lines (net change; opening/closing cash incl. restricted). The closing line is NOT `cash_and_equivalents` (includes restricted cash) |
| EffectOfExchangeRateOn… (4 siblings) | 65 | FX component of the cash identity (shareholder-returns §6) |
| AccumulatedOtherComprehensiveIncomeLossNetOfTax, RetainedEarningsAccumulatedDeficit, CommonStockValue, AdditionalPaidInCapital(CommonStock), CommonStocksIncludingAdditionalPaidInCapital, TreasuryStock(Common)Value, PreferredStockValue | 100/99/76/80/15/61/45 | equity components (stockholders_equity is their total) |
| MinorityInterest, StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | 51 / 56 | NCI and total equity incl. NCI: components of the identity; NOT stockholders_equity (UNH/AT&T trap, balance-sheet-…-other §1) |
| ProfitLoss, NetIncomeLossAttributableToNoncontrollingInterest (IS and CF top line) | 48 / 40 | NI components; NI to parent is NetIncomeLoss (or NIACSB under the identity rule, net-income-and-shares §7) |
| CommitmentsAndContingencies | 78 | caption line, normally no value |
| WeightedAverageNumberOfSharesOutstandingBasic / …DilutedSharesOutstanding | 83 / 83 | weighted-average shares: no concept today (a per-share input; propose a concept rather than force it into shares_outstanding) |
| Other*: OtherAssetsNoncurrent/Current, OtherLiabilitiesNoncurrent/Current, PrepaidExpenseAndOtherAssetsCurrent, AccruedLiabilitiesCurrent, EmployeeRelatedLiabilitiesCurrent, DeferredIncomeTax*, OperatingLease*, ContractWithCustomerLiability*, AccruedIncomeTaxes*, ShortTermInvestments, LongTermInvestments, IntangibleAssetsNetExcludingGoodwill | 15-81 | balance-sheet components without a concept |
| CF detail: PaymentsForProceedsFromOther…, ProceedsFromPaymentsForOther…, PaymentsToAcquireBusinessesNetOfCashAcquired, ProceedsFromIssuance/RepaymentsOf(LongTerm)Debt, ProceedsFromIssuanceOfCommonStock, ProceedsFromStockOptionsExercised, PaymentsRelatedToTaxWithholdingForShareBasedCompensation (buyback EXCLUSION), InterestPaidNet / IncomeTaxesPaidNet (supplemental), DeferredIncomeTaxExpenseBenefit, OtherNoncashIncomeExpense, IncreaseDecreaseInOther*, investment purchases/sales/maturities, ProceedsFromSaleOfPPE | 15-78 | cash-flow components without a concept |
| CostsAndExpenses | 35 | NOT cost of revenue and not opex by name: four perimeters (operating-income card) |
| IncomeLossFromEquityMethodInvestments | 22 | a component |

Custom extension lines: map only by structure (statement position, calc parent, label), never by name (the xbrl-structure skill). Ask me per line.

## M. Known misuse in the old concept_mapping (Ritwik relay, ranks 1-50, 2026-11-11; full rows: work/tag-library/ranks-1-50 data-team/47-fsn-store/company_tag_map/ranks_1_50.csv)
| Tag | Wrongly mapped as | What it is |
|---|---|---|
| LiabilitiesAndStockholdersEquity | total_assets | L&E total (equal in value, but a different line: never a source for assets) |
| CashCashEquivalentsRestrictedCash… | cash | includes restricted cash (cash only with a flag when it is the only cash line: GILD/DHR rule) |
| StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest | parent equity | includes NCI (parent = total − MinorityInterest when both printed) |
| ProfitLoss | net income | includes NCI; NI only with no NetIncomeLoss and no NCI line |
| NetIncomeLossAvailableToCommonStockholdersBasic | net income | after preferred dividends |
| CostsAndExpenses | opex | includes cost of revenue |
| InterestIncomeExpenseNet, InterestIncomeExpenseNonoperatingNet | other income | net interest |
| InterestExpenseDebt | gross interest | debt-only component (gross only under the sole-debt rule) |
| InterestAndDividendIncomeOperating | revenue | bank interest income |
| GeneralAndAdministrativeExpense | SG&A | G&A only; SG&A = S&M + G&A when S&M is separate |
Combined lines (reason `line_presented_combined_with_others`): AccountsPayableAndAccruedLiabilitiesCurrent and variants; CF IncreaseDecreaseIn…AndOther… lines.
