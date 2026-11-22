# FSN line → concept lookup for the mapper (Tag Expert, 2026-11-11; for the two Ritwik sessions)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

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

## N. Known filer label errors (tag right, label wrong): exempt them from label-DEMOTION rules (2026-11-11)
A label rule can demote a correct line when the filer's label linkbase is wrong. Known cases (FILING-CHECKED unless marked):
| Filer | Filing | Error |
|---|---|---|
| STX | 0001137789-26-000309 | label shifted: Goodwill 1,221 labelled "Other intangible assets" |
| POWL | 0000080420-23-000051 | labels swapped |
| EXLS | 0001297989-23-000009 | labels swapped |
| DY | 0000067215-19-000043 | label shifted |
| HLI | 0001302215-23-000079 | "other assets" label on total assets |
| TRU | 0001552033-17-000027 | label shifted |
| LH | 0000920148-24-000118 | label shifted (10,427.1M) |
| MUR | 0000717423-20-000008 | label shifted (5,913,893K) |
| T | ranks 68-84 read | "Inventories" tagged PrepaidExpenseCurrent (TAG error: company override) |
| MCD | ranks 68-84 read | weighted shares stored unscaled (713.4): scale override |
| MSI | 2018-12 filing | basic/diluted EPS labels swapped (Ritwik; DATA-INFERRED) |
| FIVE | 0001177609-20-000030 R6 | withholding label on two rows (12,663)K vs (3,789)K |
| ETSY | 0001370637-18-000020 R7 | two rows with one label (10,301)K / (6,417)K |
| FICO | (fsn-balance-sheet-assets) | "…Current" label on a noncurrent position (DATA-INFERRED) |
| XOM | latest 10-K R3 / R54 | basic and diluted EPS labels swapped (same value 6.70) |
| PLTR | latest 10-K CF | net-change-in-cash row labelled as financing |
Guard: when a label would demote a line, check it against the calc position and the value (e.g. a "Goodwill" tag whose value equals the goodwill note) before demoting; a demotion that breaks the statement's calc tie is a label error, not a component.

## O. Full 10-K reads of 24 top-50 companies (Dhairya 2026-11-11; FILING-CHECKED, latest 10-K; 2.1% FAIL on 1,031 data points)
- `MarketingExpense` = the S&M component of SG&A (AMZN "Sales and marketing" 47,129M). `AccountsPayableTradeCurrent` is META's face AP tag (2021+).
- `CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization` = cost of revenue, labelled "excl. D&A" (LIN 17,389M).
- `InvestmentIncomeNet` can be the face "Interest income" (MU 1,084M). `IncreaseDecreaseInAccountsAndOtherReceivables` is LLY's AR change line.
- `ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest` is NOT comprehensive income attributable to the parent (PG 15,801M, PM).
- CAT "interest expense excluding Financial Products" is a segment component, not consolidated interest expense.
- Brokers (MS): "Total non-interest expenses" = operating expenses; "Customer and other receivables/payables" = combined (tags `OtherReceivables` and `Payables`, 0000895421-26-000086); `PaymentsForProceedsFromProductiveAssets` on "premises, equipment and software" = capex.
- Never use a rounded note figure when the face prints the value under another tag: AMD amortization 2,254M on the CF (`AdjustmentForAmortization`) vs 2,300M in the note (the iprx/face rule, debt.md §8-9).

## P. Full 10-K reads of 12 more companies (Dhairya 2026-11-12; CSCO CVX DELL GE GEV GOOG GS HD INTC JNJ JPM KO; 7.8% FAIL; FILING-CHECKED)
- CVX `Revenues` 189,031M = "Total revenues and other income"; revenue = "Sales and other operating revenues" 184,432M (0000093410-26-000078 R3). Same trap as COP: a "total" that adds other income is not revenue.
- CSCO undimensioned `AmortizationOfIntangibleAssets` = the opex portion only (916M); total amortization 1,863M (R67).
- JNJ "interest expense, net of portion capitalized" is clean (the expensed amount), not a net-interest perimeter.
- JNJ latest 10-K: the incl-NCI equity and comprehensive-income tags are the only lines (no parent and no NCI line): equity maps by the rule in TOP-TAGS row 70.
- GE `AllocatedShareBasedCompensationExpense` is after tax (R126): never SBC at GE.
- GE prints no consolidated cost of revenue; Equipment and Services cost lines only (R3): cost of revenue = their sum under ruling (a) (printed duration components, same section).
- JPM: "cash and due from banks" + "deposits with banks" = CF ending cash 343,338M. Serving the BS sum would be a derived instant (doc 02 item 4); the CF ending-cash line is a PRINTED instant with the same value: serve it, labelled (ACCEPTED by Dhairya 2026-11-12, for every bank that splits cash across BS lines).
- DELL, GOOG, INTC "Interest and other, net" / other income and expense totals include interest: combined.
- HD's latest 10-K uses `IncomeTaxesPaidNet` (R68), not `IncomeTaxesPaid`.
- Tooling (CORRECTED 2026-11-12, Data Verifier): companyconcept returns 404 for custom prefixes AND companyfacts carries only the us-gaap, dei, ecd and ffd namespaces: every extension-prefix fact and every dimensioned fact is absent. Custom and dimensioned rows can be checked only against the R page (the filing's own XBRL).

## Q. Sums rule (Dhairya 2026-11-12, D3 narrowed to doc 02)
- Durations: printed face-line sums allowed (opex, cost of revenue, interest, capex, D&A, NI = ProfitLoss − NCI). Instants: never summed, except total_debt (founder definition, doc 02 2026-11-04 item 5). Total liabilities, inventory or shares with no printed total = not_presented.

## R. Full 10-K reads of 13 more companies (Dhairya 2026-11-12; FILING-CHECKED)
- XOM `InterestPaidNet` = the operating portion only; `InterestPaid` = total cash interest (R109). The gross/net reading of the two paid tags is filer-specific (JNJ is the reverse case: net of capitalised): read the label.
- XOM basic/diluted EPS labels swapped (R3/R54, both 6.70); PLTR's net-change-in-cash row labelled as financing: added to §N.
- SHOP FY2024: pretax on `IncomeLossAttributableToParent` (standard label "…before Tax"); CF SBC on `StockOptionPlanExpense`.
- TXN software amortization: `AmortizationOfIntangibleAssets` in 10-Qs, `CapitalizedComputerSoftwareAmortization1` in the 10-K (a form-specific tag switch: map per filing).
- WMT inventory change = `IncreaseDecreaseInRetailRelatedInventories`. WFC total revenue = `RevenuesNetOfInterestExpense`.
- RTX "Interest expense, net" on `InterestIncomeExpenseNonoperatingNet`: a net line, never gross interest expense.
- Comprehensive income incl. NCI was served at 7 companies where the parent line is printed: the library row was wrong (component with parent comprehensive_income); corrected to excluded, mapping only with no parent and no NCI line (TOP-TAGS #170/#349 were right).
- EPS printed per class only (Visa, SHOP): RULING (Dhairya) serve Class A as printed.

## S. Era and company switches from the 50 full 10-K reads, group 3 (Dhairya 2026-11-12; data-team/companies/reads/ on main 92291fd9; FILING-CHECKED)
- LLY capex moved to `PaymentsToAcquireOtherPropertyPlantAndEquipment` from Q4 2022 (map per filing era).
- PANW `OtherNonoperatingIncomeExpense` is a component after 2018; a custom total carries the face line (find the total by calc position).
- META switched AP tags several times (AccountsPayableCurrent / AccountsPayableTradeCurrent / AccountsPayableAndOtherAccruedLiabilitiesCurrent; balance-sheet §8): map per filing by label + calc.
- MA and MS DPS moved off the face into equity notes after 2019: read the note fact (fsn.value), never treat it as absent.
- LRCX goodwill sits inside a combined face line from 2024: combined, never goodwill.
- MU and MS CF "Receivables" change lines are changes of COMBINED BS lines: not cf_ar_change.
- LIN "Cost of sales, exclusive of D&A" = `CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization` (§O).

## T. Lessons mined from the 50 full 10-K reads (data-team/companies/reads/, main 92291fd9; 187 non-PASS rows: 54 new tag lessons, 66 already carded, 65 non-tag causes; FILING-CHECKED by Dhairya's reads)
**Interest** — AMGN "Interest expense, net" on `InterestExpenseDebt` is gross (0000318154-26-000010 R3 2,755M; interest income in other income, R82 `InvestmentIncomeInterest` 408M). AVGO "Interest expense" switched `InterestExpense` → `InterestExpenseNonoperating` in the FY2025 10-K (3,210M). Combined custom lines: GE `ge:InterestAndOtherFinancialCharges` 843M (no InterestExpense* element); GEV "Interest and other financial income (charges) - net" 186M. LIN note R68 prints gross "Interest incurred on debt and other" 575M (`InterestExpenseDebt`), capitalised (111)M and interest income (209)M (`InterestIncomeOther`); the face line is net. GOOG interest income 4,337M on `InterestIncomeOther` (R74). WMT gross = Debt 2,318M + `wmt:FinanceLeaseAndFinancingObligationInterestExpense` 481M = 2,799M. SHOP "Interest income" 331M on `InterestIncomeExpenseNonoperatingNet`. PANW cash interest on `panw:InterestPaidContractualInterest`.
**Investment income** — `InvestmentIncomeInterestAndDividend` and `InvestmentIncomeNet` are combined lines: DELL "Investment income, primarily interest" 256M; MSFT "Interest and dividends income" 3,301M; UNH "Investment and other income" 3,920M (never interest_income).
**Cash taxes paid (ASU 2023-09 era)** — moved from the CF face to the tax note, same tag `IncomeTaxesPaidNet`: AAPL (34,588M), BAC (3,930M), LRCX, WFC (1,419M), CSCO (4,821M). Switched `IncomeTaxesPaid` → `IncomeTaxesPaidNet` in the note: ABBV, LIN, NFLX, PG, TSLA. TXN prints both net 296M and gross 556M: never alternates.
**D&A and capex** — GE D&A = `DepreciationAmortizationAndAccretionNet` 863M (PP&E only) + intangibles 357M = 1,220M. CSCO CF "Depreciation, amortization, and other" is a custom combined line (2,540M); `DepreciationDepletionAndAmortization` 700M is PP&E only, rounded. CRWD custom D&A excluding intangibles and contract costs 250,218K + `AmortizationOfIntangibleAssets` 31,233K. TSLA `tsla:DepreciationAmortizationAndImpairment` 6,148M = combined. Two-line eras: MRK since 2020, TMO since 2018, INTC since 2019 (depreciation + amortization lines). ANET capex on `PaymentsToAcquireProductiveAssets` incl. intangibles (119.5M). PM amortization only in a roll-forward labelled "Amortization & Impairment". KO's "$224M amortization" is tax-credit investments, not intangibles.
**Balance sheet** — PP&E including operating-lease ROU on custom tags: GE (7,987M), GEV (6,006M), JPM "Premises and equipment" 36,244M (note `PropertyPlantAndEquipmentNet` 19,041M): combined, flag. JPM "Goodwill, MSRs and other intangible assets" 64,458M = combined (note Goodwill 52,731M). TSLA goodwill moved into "Other non-current assets" in FY2025 (note 257M). MU trade receivables `AccountsReceivableNetCurrent` 31,793M inside combined `ReceivablesNetCurrent` 36,197M. NFLX trade receivables on `TradeReceivablesHeldForSaleAmount`. GEV "current receivables" change on `IncreaseDecreaseInOtherReceivables`; PM `pm:IncreaseDecreaseInAccruedLiabilitiesAndOtherCurrentAssets` = combined.
**Income statement** — GE's only `GrossProfit` facts are notes (premium deficiency 992M; associates 1,239M): never GE gross profit. CVX `cvx:NonoperatingIncome` 1,599M sits inside "Revenues and Other Income". ORCL custom nonoperating total incl. NCI elimination. MU `OtherOperatingIncomeExpenseNet` 567M is an opex component. V `CostsAndExpenses` 17,793M = opex total (no cost-of-revenue line); V comprehensive income switched to `ComprehensiveIncomeNetOfTax` in FY26. COST dividends on `PaymentsOfDividendsCommonStock` from the FY2024 10-K.
**Contradictions resolved here**: C1 receivables change (label-gated), C2 CostsAndExpenses (V exception), C3 InvestmentIncomeInterestAndDividend (combined), C4 InterestPaid net/gross (filer-specific; shareholder-returns line superseded), C5 OtherOperatingIncomeExpenseNet (opex component), C6 TOP-TAGS #349 aligned with the library.

## U. No label promotion at library level (Dhairya 2026-11-12, doc 02 item 2)
- A wider tag never maps to a narrower concept because its label is plain. Defaults are combined: ReceivablesNetCurrent, BS CashCashEquivalentsRestrictedCash…, IncreaseDecreaseInAccountsAndOtherReceivables. Plain-label cases live in library/company-overrides.csv, company-scoped and FILING-CHECKED (RTX, FITB, LLY; GILD/DHR pending an R-page read).

## V. CostsAndExpenses → operating_expenses: structural rule (Dhairya 2026-11-12)
- Allowed only when the IS face prints NO cost-of-revenue line and CostsAndExpenses is the last expense total above operating income (V 0001403161-26-000134 R5 17,793M: revenue 45,903 − 17,793 = OI 28,110). This is the statement's shape, not a label promotion.
- Engineering test cases (a printed cost-of-revenue line must block it): V → map; AMZN 0001018724-26-000004 R4 (cost of sales 356,414M inside 636,949M) → blocked; CVX/AJG (total includes interest) → blocked.

## W. Document-first reads, ranks 68-84 (Dhairya 2026-11-12; FILING-CHECKED)
- Capex: T and ISRG carry their real capex line on `PaymentsToAcquireProductiveAssets`; MCD FY2025 restaurant purchases on `PaymentsToAcquireOtherProductiveAssets` (acquisitions). The capex rule DEMOTES by acquisition label or by a separate PP&E purchases line; it never promotes.
- TMUS, T, BA: `CostOfGoodsAndServicesSold` only on ProductOrServiceAxis members, no undimensioned total (BA face cost of revenue = `CostOfRevenue`). **Clarified (Dhairya 2026-11-12): members that are each PRINTED as their own face line with no printed total are an allowed duration sum (TMUS cost of services + cost of equipment; T FY2025 "Equipment" + other cost line); members that are not face lines (segment or product disaggregation in notes) are never summed.**
- ETN net interest moved `InterestIncomeExpenseNet` → `InterestExpenseNonoperating` on the same line. UBER CF D&A `DepreciationAndAmortizationIncludingAmountFromOtherIncomeExpense` = combined.
- Era switches: `InterestExpense` → `InterestExpenseNonoperating` (UNP, DHR, STX, T, UBER); SCHW → `InterestExpenseOperating`; WELL `InterestExpenseDebt` → `InterestExpenseBorrowings`; UBER `NonoperatingIncomeExpense` → `OtherNonoperatingIncomeExpense`; NEE FPL capex custom tag renamed. company_tag_map keys per filing era.
- Filer errors (overrides only after a filing check): T inventories on `PrepaidExpenseCurrent`; MCD weighted shares unscaled (713.4). STX Goodwill labelled "Other intangible assets" is a LABEL error (tag right: no override, §N).
- BA `PaymentsOfDividends` FY2025 = mandatory convertible preferred only.

## X. Document-first reads, ranks 85-100 (Dhairya 2026-11-12; FILING-CHECKED)
- Cash: PGR on `Cash` (125M; the sole cash line). CB: the PERIMETER changed with the tag (plain cash → incl. restricted) from 2018: served as printed, labelled. **Bank cash rule refined: the BS total cash line when printed (COF 57,434M), else the CF printed ending cash** (never a sum of BS lines).
- Receivables on other tags: MO `OtherReceivablesNetCurrent`, BKNG `AccountsAndOtherReceivablesNetCurrent` (company overrides; library default stays non-AR / combined).
- Interest: FTNT interest income on `InvestmentIncomeNet`; PH note "Interest income" 14M on the net tag `InterestIncomeExpenseNonoperatingNet` (overrides). SPGI "Interest expense, net" on the gross `InterestExpenseNonoperating`: the caption demotes it to combined. NEM "interest expense, net of capitalized interest" is clean.
- NEM SBC on `EmployeeBenefitsAndShareBasedCompensation` (override; library default combined).
- LMT cost moved `CostOfGoodsAndServicesSold` → `CostOfRevenue` (the line above gross profit); LMT D&A → `DepreciationAmortizationAndAccretionNet`.
- VLO capex = PP&E + capital improvements (turnarounds, founder perimeter); VLO has no undimensioned companyfacts after FY2018 (read the face/FSN).

## Y. Document-first reads, ranks 51-67 (Data Verifier docmaps, 2026-11-12; FILING-CHECKED; feedback-inbox lines processed)
- COP `Revenues` moved lines in FY2022: the total ("Revenues and Other Income") until FY2021, then "Sales and other operating revenues" (78,494), with the total on custom `cop:RevenuesAndOtherIncome`. Map per filing; the "and other income" caption demotes.
- `CostsAndExpenses` perimeter varies on one tag: MRVL excludes COGS (= gross profit − OI); QCOM, ABT, GILD, VZ include cost of revenue; DE includes interest. Map operating_expenses only after the value check (library row); both map cases (V: revenue − OI with no cost line; MRVL: gross profit − OI) confirmed structural by Dhairya.
- PEP "Net interest expense and other" on `InterestExpense`: combined (the label demotes). DIS "Interest expense, net" on the net tag. MRVL "Interest income and other, net" 1,926.3 on `OtherNonoperatingIncomeExpense` inside the `NonoperatingIncomeExpense` subtotal 1,723.7.
- CRM misuses `AmortizationOfAboveAndBelowMarketLeases` for intangibles amortization (override: excluded); CF D&A 3,631 is CRM's only face amortization line.
- DIS, VZ, DE: face cost lines exist only as dimensioned rows (ProductOrServiceAxis); each is a printed face line: DIS cost of services 52,677 + products 6,089, VZ 27,789 + 28,976 = allowed duration sums; DE "Cost of sales" 28,159 on the Net Sales member.
- SNDK AP only by related-party axis: not_presented (an instant is never summed).
- DPS: C prints only the quarterly rate (0.60 / 0.56), CRM 0.416 quarterly, DIS per-payment instants: never read a parenthetical rate as annual. RULED (Dhairya 2026-11-12): annual DPS = the sum of the four quarterly DPS facts printed in the same 10-K (same declared/paid basis, each on its own quarter context, no unflagged special dividend), served "sum of printed quarterly dividends"; else not_presented (C 2.32, COF, CRM 1.664, DIS dated payments). EPS stays never derived.
- GILD/DHR CCRC plain-label cash: handled by the FILING-CHECKED company overrides (the library default stays combined, doc 02: no label promotion). KLAC's latest BS uses the pure cash tag. Banks: the CF printed ending cash (C 349,579; AXP).
- BLK amortization era change: pure 151 (FY2023) → custom amortization-and-impairment 775 (FY2025, combined). BLK dividends/buybacks combined with Subco units; note "Aggregate dividends" 3,265 vs CF 3,347.
- Capex needs two printed CF lines at DE (PP&E 1,360 + equipment on operating leases 2,868) and IBM (PP&E 1,091 + investment in software 647): printed duration sums under the founder perimeter.

## Z. Expander rows and custom value sources (Dhairya / Engineering 2026-11-12)
- Library rows set for the largest undecided pairs: BS `CommonStockParOrStatedValuePerShare`, `PreferredStockSharesAuthorized` = excluded `share_terms_parenthetical`; CI `ComprehensiveIncomeNetOfTax` = comprehensive_income (attributable); EQ `CommonStockSharesOutstanding` = shares_outstanding_resolved (undimensioned period-end row); CF `CashCashEquivalentsRestrictedCash…` = excluded `cash_rollforward` (except the bank/split-cash source); IS `ProfitLoss` = excluded where NetIncomeLoss is printed, else ruling (b); CF `NetIncomeLoss` / `ProfitLoss` = excluded `cf_start_line`.
- **core.fact holds no extension tags**: a custom-tag face line cannot be a companyfacts value source today. **FOUNDER DECISION 2026-11-12 (doc 02 "Founder decision of 2026-11-12: value source for custom-tag lines" (doc/foundational/02_Scrooner_Decision_Register.md, main fcf1425d)):** custom-tag lines take their VALUE from the filing's own XBRL via SEC's FSN data, checked against the printed R page; standard tags stay on the SEC API. company-overrides.csv carries `value_source` = `fsn_xbrl` (custom: IBM investment in software, and every similar row) or `sec_api` (standard). The interim `custom_value_source_pending` status is retired.

## AA. Older inbox lines absorbed 2026-11-12 (17 lines; FILING-CHECKED unless marked)
- `CapitalLeaseObligations`: AMZN FY2016 10-K uses it for GROSS minimum lease payments 9,406 (not the present value 9,077, the element's meaning): 0001018724-17-000011 R51. Never debt at AMZN without the PV line.
- `FinanceLeaseLiabilityNoncurrent`: META FY2019 10-K prints the 2019 value 418 under the 2018-12-31 context (filer context error; 473 = 55 + 418 is the 2019 total): 0001326801-20-000013 R47. Rule: a noncurrent component equal to (total − current) at another instant of the same filing is a context error; META 2018-12-31 debt is 0.
- `LongTermDebtAndCapitalLeaseObligations` / `LongTermDebtNoncurrent` at capitalization-format utilities (NI 0001111711-17-000032 R5, FE 0001031296-18-000015 R5, AWK 0001564590-15-003448 R2): printed after common equity inside "Total capitalization" but still a liability (equity + LTD = total capitalization).
- `InterestExpense`: DAL tags the NET segment-note line "Interest expense (income), net" with it while the face uses `InterestIncomeExpenseNet` for the same 396M (0000027904-18-000006 R83, R4): a note copy on a gross tag is not gross interest.
- `OperatingIncomeLoss`: used non-dimensionally for segment-measure totals that reconcile to pretax (ELV 0001156039-26-000013 R116, SLB 0000950170-24-006884 R85, IP) and misused by WPC for income before taxes in the tax note (0001025378-16-000062 R106): only the IS face line is consolidated operating income.
- `DepreciationDepletionAndAmortization`: HD from FY2025 = D&A EXCLUDING intangibles amortization (separate line), before FY2025 the single total (0000354950-25-000165 R7; 0000354950-24-000152 R7). `msft:DepreciationAmortizationAndOther` is MSFT's only CF D&A line, combined, 2014-2026 (0001193125-14-380252 R7; 0001193125-26-436133 R6).
- `DepreciationAmortizationAndAccretionNet`: KeyCorp prints "Depreciation and amortization expense, net" on it: held as a net label in every period once it nets below intangibles amortization (carried by fsn_store.detectors company_net_labels).
- `PaymentsOfDividends` is not evidence of a COMMON dividend (BPOP Q1 2015 preferred 620K; WYNN Q1 2021 295K while suspended; TDG FY2016 equivalents 3M). `CommonStockDividendsPerShareDeclared` vs `…CashPaid` are different bases within one company (LMT Q2 2016 declared 3.30 = two declarations): one basis per company series (period-engineer AC-24).
- `RevenueFromContractWithCustomerExcludingAssessedTax`: Teleflex recast FY2024 for discontinued operations in its FY2025 10-K (1,699.5M vs 3,047.3M originally) while the Q3 2025 9M was not recast: Q4 = FY − 9M across bases is wrong (basis break; SAME_BASIS rule).
- Tooling: FSDS num.txt carries per-share values to 4 decimals (par 0.00001 reads 0.0000: AAPL 0001193125-15-023697): per-share and tiny values come from the API or the instance, never FSDS. Tag-name ABSENCE in analytics.company_sec_tag is evidence only for undimensioned primary-statement lines (collaboration revenue sits on members/custom tags at LLY, REGN, VRTX, ALNY, BMY).
- The filer's own calc linkbase lists `OtherShortTermBorrowings`, `ShortTermBorrowings`, `CapitalLeaseObligationsNoncurrent`, `DebtCurrent` directly under LiabilitiesCurrent/Liabilities (AAPL 0000320193-20-000062, ABBV 0001551152-22-000017, CVX 0000093410-15-000020, MU 0000723125-21-000065): debt slots come from tags, not from calc position.
- `Deposits` + `InterestIncomeExpenseNet` co-occur at FCX, ZBRA, CPAY, WEX, CBC: not a bank test (sector-faces.md).

## AB. Status convention for data points found only in notes (Dhairya ruling 2026-11-12)
- The data point's fact is in the filing's note → **mapped**, stmt NOTE, with the R page (e.g. `IncomeTaxesPaidNet` in the tax or supplemental-cash note under ASU 2023-09).
- The fact is nowhere in the filing (face or notes, checked in the filing's XBRL and its R pages) → **not_presented**, with the evidence of absence.
- **component_in_note** only when the note value is a COMPONENT of the data point, not the data point itself.
- A face miss alone is never not_presented. Rows a reader marks "AUTO / not hand-verified" are not answer key (graded key_unverified; Engineering's loader rejects them).

## AC. Exam-driven fixes (v6, 2026-11-12; 120 graded companies)
- Net income without a parent line: `NetIncomeLossAvailableToCommonStockholdersBasic` when no preferred line is printed; `ProfitLoss` when no NCI line is printed (net-income card rules, now in predict.py).
- A lone CF `Depreciation` / `OtherDepreciationAndAmortization` line is the D&A line; two or more CF D&A component lines are a duration sum.
- New library rows: `IncreaseDecreaseInAccountsPayableTrade` → cf_ap_change; unclassified `AccountsReceivableNet` → accounts_receivable; `AccountsPayableCurrentAndNoncurrent` → accounts_payable.
- Reader keys graded as key errors under existing rulings: tax-withholding or `ProceedsFromRepurchaseOfEquity` keyed as buybacks (founder 2026-11-04 item 4); NCI or preferred dividends keyed as common dividends; interest, notes or financing receivables keyed as accounts receivable.

## AD. Rulings 2026-11-13 (Dhairya)

1. **OUT vs not_presented.** This applies to every data point, not only current assets and liabilities. A data point outside the company's template group is OUT. A data point inside the template that the filing does not print is not_presented. Banks and insurers present no classified balance sheet, so current_assets and current_liabilities are OUT for them (SYF). cost_of_revenue, gross_profit, research_and_development and inventory are outside the bank and insurer templates, so they are OUT as well. The one exception is a company-scope rule where the filing really prints the line: a conglomerate insurer with an operating segment, such as L, may print cost of revenue, and that row is mapped or combined, never OUT. exam/tools/grade.py grades a reader key of not_presented where the predictor says OUT as a key error (Dhairya 2026-11-13, second message).
2. **Opex as a difference of two totals** (WYNN: CostsAndExpenses − COGS). Status component_sum, tags = the printed face lines between COGS and operating income. The difference of the two totals is only a cross-check, and it must tie to that sum. The predictor still returns `mapped CostsAndExpenses` there. The fix is queued for the backtest (rules/inbox), with no rule change before exam/tools/backtest.py is on main.
3. **Headline.** Hand-verified rows stay the headline, and graduation counts hand rows only, until exam/results/key-adjudication-2026-11-13.csv (the Verifier's 30 + 30 filing check) decides hand against machine.
4. **Cost of revenue printed only by member** (WYNN, with the same pattern at BLCO, CZR, HST, TMUS and ASTS). The face line has no undimensioned value; the R page hides the member rows. cost_of_revenue = component_sum of the printed ProductOrServiceAxis member facts, which is allowed as a duration sum of printed face lines. Its value_source is fsn_xbrl, because companyfacts carries no dimensioned facts. Opex = component_sum of the valued lines after the cost line, but only where total = those lines + the sum of the members exactly. Each tie is checked in the filing's XBRL instance and cited in exam/tools/adjudications.csv. All six tied to 0 on 2026-11-13. Where the lines carry interest (DE Financial Services), the rule stands down and the total is combined.

## AE. Rulings 2026-11-13, second batch (Dhairya; evidence exam/results/key-adjudication-2026-11-13.csv, 60 rows, R pages opened)

1. **Key evidence has three buckets.** A row is hand only when its note carries `check: hand`. `machine-full-filing` is machine. Everything else is tool. In the adjudication, machine keys were right in 28 of 30 sampled rows, with no shared blind spot. The old hand bucket mixed in 367 unmarked tool rows. exam/tools/grade.py and exam_score.py report hand / machine / tool / all.
2. **Note-only mapping** accepts only an undimensioned, consolidated fact. It never takes an investee's gross profit (BWXT) or a segment's overhead (SEIC).
3. **Face line printed only under a class member** (STZ diluted shares, Class A). It is still the face line: map it to that member's fact.
4. **Custom tag for a standard concept on the face** (AKAM akam:PropertyPlantAndEquipmentAndCapitalizedSoftwareNet → PP&E). Map it through a company rule with value_source fsn_xbrl.
5. **SG&A with G&A alone.** Lone G&A → sga_expense is mapped only when the face prints no selling or marketing line anywhere and no other selling-type line sits in the opex block (TLN). Otherwise it is component_sum or combined. SG&A is never G&A alone when S&M exists (the MSFT incident).
6. **Bank capex** "Purchases of premises and equipment, net", net of disposals → combined, as before (DEMOTE net of proceeds).
7. **Capex perimeter** (doc 02 line 119) includes turnarounds (PBF: key and prediction both wrong) and purchased real property used in operations (GKOS second line).
8. **total_debt** includes finance leases disclosed in the notes (RL).

## AF. Machine docmap errors caught by hand checks, ranks 101-110 (relayed 2026-11-13; fixes proposed in data-team/tags/decisions/NOTES-TAG-EXPERT-reads-101-110-2026-11-12.md on work/ritwik-cloud/tag-decisions-2026-11-11 @26564cdf)

The predictor (v7 engine, rules as of ee1a40ec) already gets each case right. The errors live in the docmap tool:
- **PLD dividends.** "Dividends on common and preferred stock/units" is combined, not mapped (PaymentsOfDividends covers preferred stock and OP units).
- **PLD debt.** Count debt once. The co-registrant (Prologis LP) repeats the parent's debt: 70,074M is the double count, 35,037M is right. A fact with coreg ≠ '' is never consolidated (the same as the note-only rule in AE.2).
- **MCK and SYK D&A.** The CF D&A is the sum of Depreciation and AdjustmentForAmortization.
- **MCK and PSX notes.** Values from VIE notes (total liabilities, AR) belong to the VIE, not the company. Take note values only from undimensioned, consolidated facts (AE.2). exam/tools/NOTES.sql enforces this with dim_id=0 and coreg=''.
- **PSX.** The face line "Interest and debt expense" is InterestAndDebtExpense, which maps to interest_expense.
- **PLD capex.** A REIT's capex lines (development, acquisitions of real estate) need a perimeter check. The predictor keys PaymentsToDevelopRealEstateAssets as combined. Pending Dhairya's capex perimeter (doc 02 line 119) for REITs.
5. **Location slices** (Dhairya 2026-11-13, CSCO). An undimensioned AmortizationOfIntangibleAssets, D&A or SBC fact can be only one income-statement-location slice. In FSN segments, the location axis appears as IncomeStatementLocation= or StatementOfIncomeLocationBalance=. When the location members sum to more than the undimensioned fact (beyond the dcml tolerance), the data point is component_sum of the location members, value_source fsn_xbrl. A printed location total (an OperatingIncomeLoss or CostsAndExpenses member) must tie. Otherwise the undimensioned fact stays mapped. Cohort scan (exam/tools/LOCATION.sql, 2026-11-13): the slice occurs only at CSCO, with 947 + 916 = 1,863, the location total. The LYFT and FIG SBC location sums tie exactly to the printed CF line.
6. **Accretion tag.** DepreciationAmortizationAndAccretionNet is combined for D&A, even when the label reads "Depreciation and amortization". It includes accretion by definition, and a label never promotes a wider tag (doc 02; DUK ruling).
7. **"Could be classified as G&A" disclosures are not SG&A** (HCA, 2026-11-13). HCA's policy note tags its corporate office costs (548M FY2025) as GeneralAndAdministrativeExpense, undimensioned and consolidated, but says most expenses are costs of revenues. The fact is a slice of a natural-expense income statement, not the company's SG&A, so sga_expense is not_presented. Undimensioned does not by itself mean the whole concept: read the caption or sentence that carries the fact.
8. **Turnarounds count as capex only in investing activities** (Dhairya 2026-11-13, DINO). A turnaround line in operating activities (DINO IncreaseDecreaseInTurnaroundExpenditures, 437M) is already inside CFO. Adding it to capex would subtract it twice in FCF (CFO − capex). Investing-section turnaround lines are capex components: PBF PaymentsForDeferredTurnaroundCosts and CVI PaymentsForTurnaroundCosts (company extension tags).
9. **Finance leases in total_debt** (founder 2026-11-04 item 5; Dhairya 2026-11-13). Total debt includes finance leases, printed or disclosed in the notes. Guards:
   - If a debt line's tag or label already includes leases ("and finance lease obligations", "capital lease", LongTermDebtAndCapitalLeaseObligations…), add no separate lease line.
   - Never add both the note total and a face current/noncurrent split.
   - Use the note FinanceLeaseLiability only when no face line carries leases.
   - Operating leases never count.
   - The deterministic location signal is FinanceLeaseLiability(Current|Noncurrent)StatementOfFinancialPositionExtensibleList. For IBM it points to ShortTermBorrowings/LongTermDebtNoncurrent, so leases are already in debt and nothing is added. For AAPL and COST it points to OtherLiabilitiesCurrent/Noncurrent, so the leases are added (AAPL 538 + 692 = 1,230M; COST 94 + 1,319 = 1,413M).
   - exam/tools/grade.py (with GRADE_LINES_DIR) grades a total_debt key that omits a printed finance-lease line as a key error.

## AG. Rulings 2026-11-13, third batch (Dhairya; binding)

- **(a)** Bank operating_expenses = NoninterestExpense, mapped. Interest expense and the credit-loss provision stay out (EWBC KEY RF SOFI SYF keys were wrong).
- **(b)** Insurer: a total that includes benefits, losses or policyholder charges (BenefitsLossesAndExpenses, or CostsAndExpenses with benefits) is combined. Exception: printed expense lines that exclude benefits and tie are component_sum (MKL, RGA). The engine rule is is.operating_expenses.insurer_total_combined.
- **(c)** Multi-class shares_outstanding = the sum of the class members at the BS date, value_source fsn_xbrl, never the dei count (per_share.shares_outstanding.multi_class_sum; keys CRWD MA META SCHW SHOP V wrong).
- **(d)** A note-only InterestExpenseDebt is mapped (stmt NOTE) when it is the gross charge and no broader total exists. It is component_in_note when a broader gross total exists anywhere (finance-lease interest, other interest).
  - APA: mapped (key right).
  - GPN: component_in_note (key wrong; FinanceLeaseInterestExpense 0.7M + face InterestAndOtherExpense 649.6M).
  - RGLD: component_in_note (key right).
  - NTNX: no undimensioned FY fact in FSN, undecided.
- **(e)** A dividend paid to a former parent before a spin is not dividends_paid. It is not_presented, reason pre_spin_parent_distribution, unless public common dividends were also paid (FDXF).
- **Opex.** When the printed band between GP and OI ties, the key is component_sum, not combined. grade.py marks the combined keys as key errors (16), plus the bank keys (5).
- **(f) Interest printed only per debt series** (NTNX ruling 2026-11-13; rule notes.interest_expense.debt_series_sum; input notes.jsonl `debt_series` built by exam/tools/fetch_debt_series.py from each filing instance, because FSN does not hold the two-dimension series contexts).
  - When there is no undimensioned interest-expense total, interest_expense = component_sum of the per-series InterestExpenseDebt facts, value_source fsn_xbrl.
  - This applies ONLY when the series are the company's only interest-bearing debt: no FinanceLeaseInterestExpense, no credit facility, revolver, term-loan or line-of-credit member, and no other undimensioned interest-expense element.
  - Otherwise component_in_note.
  - An aggregate member that equals the sum of the others is a tie, not a component (VRNS).
  - Cohort scan of 83 filers: NTNX 10,467k, VRNS 9,533k and PRU 1,967M qualify; RGLD (facility) and EG (other interest) are component_in_note.

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.91). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.91. 132 elements named in this card have library knowledge; the 30 most served are below. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `LiabilitiesCurrent`
- **Meaning:** Liabilities, Current (us-gaap, instant, credit). Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
- **Data point definition:** current_liabilities: Total current liabilities as printed on a classified balance sheet. [not applicable: bank,insurer,bdc]; total_liabilities: Total liabilities as printed.
- **Data point:** current_liabilities; total_liabilities
- **Rules:** X39; C03; C09; B01; B04; resolver functions resolve; regions; resolve_family
- **Evidence:** 95 companies, 1440 served, 32338 proven, 114 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCurrentLiabilities@2020; FreshStartAdjustmentIncreaseDecreaseCurrentLiabilities@2021; PostconfirmationCurrentLiabilities@2021; PreconfirmationCurrentLiabilities@2021 (+3 more)

### `WeightedAverageNumberOfSharesOutstandingBasic`
- **Meaning:** Weighted Average Number of Shares Outstanding, Basic (us-gaap, duration). Number of [basic] shares or units, after adjustment for contingently issuable shares or units and other shares or units not deemed outstanding, determined by relating the portion of time within a reporting period that common shares or units...
- **Data point definition:** weighted_basic_shares: Weighted average basic common shares as printed.
- **Data point:** weighted_basic_shares; role weighted_basic_shares:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1316 served, 4583 proven, 116 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000063908-24-000072: MCD FY2023 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average basic shares 727.9;  the XBRL fact is 727.9 shares (scale ; filer XBRL error 0000063908-25-000012: MCD FY2024 10-K consolidated statement of income ($ in millions, shares in millions): weighted-average basic shares 718.3;  the XBRL fact is 718.3 shares (scale  (+4 more)
- **Pattern hits:** P03 (5); P04 (3)
- **Deprecation:** replaces WeightedAverageNumberOfShareOutstandingBasicAndDiluted@2022

### `IncomeTaxExpenseBenefit`
- **Meaning:** Income Tax Expense (Benefit) (us-gaap, duration, debit). Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations.
- **Data point definition:** income_tax_expense: Income tax expense (benefit) for the period, as printed;  a benefit is a real negative.
- **Data point:** income_tax_expense; polarity income_tax_expense:signed; role income_tax_expense:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1302 served, 44905 proven, 117 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces IncomeTaxExpenseBenefitContinuingOperations@2013; RestatementOfPriorYearIncomeTaxEffects@2020

### `EarningsPerShareBasic`
- **Meaning:** Earnings Per Share, Basic (us-gaap, duration). The amount of net income (loss) for the period per each share of common stock or unit outstanding during the reporting period.
- **Data point definition:** basic_eps: Basic EPS per common share as printed (latest print = split-adjusted history, X92).
- **Data point:** basic_eps; role basic_eps:primary#1
- **Rules:** none
- **Evidence:** 109 companies, 1236 served, 4644 proven, 116 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemAdjustmentAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemPreviouslyReportedAmount@2012; CumulativeEffectOfChangeInAccountingPrincipleTabularPresentationByFinancialStatementLineItemRestatedAmount@2012; EarningsPerShareBasicAndDiluted@2022 (+5 more)

### `NetIncomeLoss`
- **Meaning:** Net Income (Loss) Attributable to Parent (us-gaap, duration, credit). The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
- **Data point definition:** net_income: Net income attributable to the parent (common and preferred holders) as printed.
- **Data point:** net_income; role net_income:primary#1
- **Rules:** X77; C29; resolver functions resolve
- **Evidence:** 105 companies, 1212 served, 28185 proven, 106 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces InvestmentCompanyNetAssetsFromOperationsIncreaseDecrease@2023; RestatementOfPriorYearIncomeNetOfTax@2020

### `Goodwill`
- **Meaning:** Goodwill (us-gaap, instant, debit). Amount, after accumulated impairment loss, of asset representing future economic benefit arising from other asset acquired in business combination or from joint venture formation or both, that is not individually identified and separately r...
- **Data point definition:** goodwill: Goodwill at period end as printed.
- **Data point:** goodwill; role goodwill:primary#1
- **Rules:** X78; B20
- **Evidence:** 105 companies, 1206 served, 4387 proven, 114 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces BusinessCombinationGoodwillRecognizedSegmentAllocation@2013; FreshStartAdjustmentIncreaseDecreaseGoodwill@2021; FreshStartAdjustmentIncreaseDecreaseReorganizationValueInExcessOfAmountsAllocableToIdentifiableAssets@2021; PostconfirmationGoodwill@2021 (+2 more)

### `ComprehensiveIncomeNetOfTax`
- **Meaning:** Comprehensive Income (Loss), Net of Tax, Attributable to Parent (us-gaap, duration, credit). Amount after tax of increase (decrease) in equity from transactions and other events and circumstances from net income and other comprehensive income, attributable to parent entity. Excludes changes in equity resulting from investments by o...
- **Data point definition:** comprehensive_income: Comprehensive income attributable to the parent as printed.
- **Data point:** comprehensive_income; role comprehensive_income:primary#1
- **Rules:** X43; X67; X76; I38; I39; I40; I41; I42; resolver functions COMBINED_YIELDS_TO; comparative_fill; DERIVED_YIELDS_TO; fill_printed_zero_and_comparative; resolve_ci
- **Evidence:** 108 companies, 1205 served, 4365 proven, 76 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `StockholdersEquity`
- **Meaning:** Equity, Attributable to Parent (us-gaap, instant, credit). Amount of equity (deficit) attributable to parent. Excludes temporary equity and equity attributable to noncontrolling interest.
- **Data point definition:** stockholders_equity: Equity attributable to the parent at period end.
- **Data point:** stockholders_equity
- **Rules:** X78; C06; resolver functions resolve
- **Evidence:** 104 companies, 1190 served, 22897 proven, 103 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces CommonStockholdersEquity@2013; EquityMethodInvestmentSummarizedFinancialInformationEquityOrCapital@2020; FreshStartAdjustmentIncreaseDecreaseStockholdersEquity@2021; PostconfirmationStockholdersEquity@2021 (+1 more)

### `AmortizationOfIntangibleAssets`
- **Meaning:** Intangible Asset, Finite-Lived, Amortization Expense (us-gaap, duration, debit). Amount of amortization expense for finite-lived intangible asset. Excludes goodwill and capitalized cost for software to be sold, leased, or marketed.
- **Data point definition:** amortization_of_intangibles: Amortization of acquired finite-lived intangible assets for the period (face line, cash-flow line or note).; depreciation_and_amortization: Depreciation and amortization add-back on the cash-flow statement (incl. depletion for extractive filers). (+1 more)
- **Data point:** amortization_of_intangibles; depreciation_and_amortization; operating_expenses; polarity amortization_of_intangibles:positive; depreciation_and_amortization:positive; role depreciation_and_amortization:primary-part#1; depreciation_and_amortization:primary-part#2; depreciation_and_amortization:primary-part#3; depreciation_and_amortization:primary-part#8 (+1 more)
- **Rules:** I51; I52; I53; I54; I43; I44; I45; I46; I47; I48; I49; I50; family resolve_all.NARROW[amortization_of_intangibles]
- **Evidence:** 92 companies, 1180 served, 2150 proven, 91 certified cells; last verified 2026-11-15
- **Known problems:** FSN dropped fact 0001413329-23-000025 (fsn_dropped_facts.csv); FSN dropped fact 0001413329-24-000013 (fsn_dropped_facts.csv); pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. ISRG amortization_of_intangibles 2025-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (1)
- **Deprecation:** replaces AmortizationOfAcquiredIntangibleAssets@2013; AmortizationOfIntangiblesNonproductionMember@2013; FiniteLivedIntangibleAssetsAmortizationExpense@2012

### `NetCashProvidedByUsedInFinancingActivities`
- **Meaning:** Cash Provided by (Used in) Financing Activity, Including Discontinued Operation (us-gaap, duration, debit). Amount of cash inflow (outflow) from financing activity, including, but not limited to, discontinued operation. Financing activity includes, but is not limited to, obtaining resource from owner and providing return on, and return of, their ...
- **Data point definition:** cash_flow_financing: Net cash provided by (used in) financing activities as printed.
- **Data point:** cash_flow_financing; polarity cash_flow_financing:signed; role cash_flow_financing:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1161 served, 42499 proven, 115 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `NetCashProvidedByUsedInInvestingActivities`
- **Meaning:** Cash Provided by (Used in) Investing Activity, Including Discontinued Operation (us-gaap, duration, debit). Amount of cash inflow (outflow) from investing activity, including, but not limited to, discontinued operation. Investing activity includes, but is not limited to, making and collecting loan, acquiring and disposing of debt and equity instr...
- **Data point definition:** cash_flow_investing: Net cash provided by (used in) investing activities as printed.
- **Data point:** cash_flow_investing; polarity cash_flow_investing:signed; role cash_flow_investing:primary#1
- **Rules:** none
- **Evidence:** 110 companies, 1161 served, 42135 proven, 115 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CashAndCashEquivalentsAtCarryingValue`
- **Meaning:** Cash and Cash Equivalent (us-gaap, instant, debit). Amount of cash and cash equivalent. Cash includes, but is not limited to, currency on hand, demand deposit with financial institution, and account with general characteristic of demand deposit. Cash equivalent includes, but is not limited t...
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents; role cash_and_equivalents:primary#1
- **Rules:** B05; B06; B07; B08; family resolve_all.NARROW[cash_and_equivalents]
- **Evidence:** 103 companies, 1156 served, 22866 proven, 108 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 2 companies, e.g. DELL cash_and_equivalents 2015-01-30 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseCashAndCashEquivalents@2021; PostconfirmationCashAndCashEquivalents@2021; PreconfirmationCashAndCashEquivalents@2021

### `NetCashProvidedByUsedInOperatingActivities`
- **Meaning:** Cash Provided by (Used in) Operating Activity, Including Discontinued Operation (us-gaap, duration). Amount of cash inflow (outflow) from operating activity, including, but not limited to, discontinued operation. Operating activity includes, but is not limited to, transaction, adjustment, and change in value not defined as investing or fin...
- **Data point definition:** cfo: Net cash provided by (used in) operating activities as printed.
- **Data point:** cfo; polarity cfo:signed; role cfo:primary#1
- **Rules:** X84
- **Evidence:** 110 companies, 1154 served, 40731 proven, 115 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `SellingGeneralAndAdministrativeExpense`
- **Meaning:** Selling, General and Administrative Expense (us-gaap, duration, debit). The aggregate total costs related to selling a firm's product and services, as well as all other general and administrative expenses. Direct selling expenses (for example, credit, warranty, and advertising) are expenses that can be directly...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]; sga_expense: Selling, general and administrative expense for the period.
- **Data point:** sga_expense; operating_expenses; polarity sga_expense:positive; role sga_expense:primary#1
- **Rules:** I15; I16; I17; I18; family resolve_all.NARROW[sga_expense]
- **Evidence:** 66 companies, 1140 served, 3623 proven, 73 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces RelatedPartyTransactionSellingGeneralAndAdministrativeExpensesFromTransactionsWithRelatedParty@2023

### `AssetsCurrent`
- **Meaning:** Assets, Current (us-gaap, instant, debit). Amount of asset recognized for present right to economic benefit, classified as current.
- **Data point definition:** current_assets: Total current assets as printed on a classified balance sheet. [not applicable: bank,insurer,bdc]
- **Data point:** current_assets
- **Rules:** X39; C09; B01; B04; resolver functions resolve; regions; resolve_family
- **Evidence:** 95 companies, 1118 served, 32318 proven, 114 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationCurrentAssets@2020; FreshStartAdjustmentIncreaseDecreaseCurrentAssets@2021; PostconfirmationCurrentAssets@2021; PreconfirmationCurrentAssets@2021 (+3 more)

### `PaymentsForRepurchaseOfCommonStock`
- **Meaning:** Payments for Repurchase of Common Stock (us-gaap, duration, credit). The cash outflow to reacquire common stock during the period.
- **Data point definition:** share_buybacks: Cash repurchases of the company's own common stock;  excludes tax-withholding shares, excise tax, employee-plan purchases, subsidiary buybacks and swaps (founder 2026-11-04).
- **Data point:** share_buybacks; polarity share_buybacks:positive; role share_buybacks:primary#1
- **Rules:** K10; K11; K12; K13; K14; K15; K16; resolver functions resolve_cf; family resolve_all.NARROW[share_buybacks]
- **Evidence:** 106 companies, 1118 served, 29887 proven, 108 certified cells; last verified 2026-11-15
- **Known problems:** pattern P06 own_10k_year_hidden: 1 open hit(s) at 1 companies, e.g. AXP share_buybacks 2018-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P06 (1)

### `PropertyPlantAndEquipmentNet`
- **Meaning:** Property, Plant, and Equipment, after Accumulated Depreciation, Depletion, and Amortization (us-gaap, instant, debit). Amount, after accumulated depreciation, depletion, and amortization, of property, plant, and equipment. Includes, but is not limited to, land and land improvement; building; machinery and equipment; furniture and fixture; and work of art, h...
- **Data point definition:** ppe_net: Property, plant and equipment net of accumulated depreciation at period end (incl. finance-lease ROU only where the filer prints them together).
- **Data point:** ppe_net; role ppe_net:primary#1
- **Rules:** B22
- **Evidence:** 106 companies, 1096 served, 32159 proven, 98 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FlightEquipmentOwnedNet@2016; FreshStartAdjustmentIncreaseDecreasePropertyAndEquipmentNet@2021; PostconfirmationPropertyAndEquipmentNet@2021; PreconfirmationPropertyAndEquipmentNet@2021

### `ShareBasedCompensation`
- **Meaning:** Share-Based Payment Arrangement, Noncash Expense (us-gaap, duration, debit). Amount of noncash expense for share-based payment arrangement.
- **Data point definition:** sbc: Stock-based compensation add-back on the cash-flow statement (pre-tax).
- **Data point:** sbc; polarity sbc:positive; role sbc:primary#1
- **Rules:** X66; K24; K25; resolver functions apply_sbc_award_members; member_facts; resolve_cf
- **Evidence:** 91 companies, 1047 served, 4504 proven, 79 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CommonStockSharesOutstanding`
- **Meaning:** Common Stock, Shares, Outstanding (us-gaap, instant). Number of shares of common stock outstanding. Common stock represent the ownership interest in a corporation.
- **Data point definition:** shares_outstanding: Common shares outstanding at period end (all economic classes).
- **Data point:** shares_outstanding; role shares_outstanding:primary#1
- **Rules:** X67; X111; B23; B24; B29; resolver functions DERIVED_YIELDS_TO; comparative_fill; fill_printed_zero_and_comparative; shares
- **Evidence:** 83 companies, 992 served, 2408 proven, 68 certified cells; last verified 2026-11-15
- **Known problems:** pattern P04 round_share_count: 3 open hit(s) at 3 companies, e.g. CVS shares_outstanding 2022-12-31 (resolver) (pattern_hits.csv); pattern P05 comparative_only_year_hidden: 1 open hit(s) at 1 companies, e.g. WFC shares_outstanding 2023-12-31 (export) (pattern_hits.csv)
- **Pattern hits:** P04 (3); P05 (1)

### `AccountsPayableCurrent`
- **Meaning:** Accounts Payable, Current (us-gaap, instant, credit). Carrying value as of the balance sheet date of liabilities incurred (and for which invoices have typically been received) and payable to vendors for goods and services received that are used in an entity's business. Used to reflect the curr...
- **Data point definition:** accounts_payable: Trade accounts payable at period end. [not applicable: bank]
- **Data point:** accounts_payable; role accounts_payable:primary#1
- **Rules:** B16; B17; B18; B19; family resolve_all.NARROW[accounts_payable]
- **Evidence:** 84 companies, 985 served, 3404 proven, 111 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AccountsPayableRelatedPartiesCurrent@2023; FreshStartAdjustmentIncreaseDecreaseAccountsPayable@2021; PostconfirmationAccountsPayable@2021; PreconfirmationAccountsPayable@2021

### `ResearchAndDevelopmentExpense`
- **Meaning:** Research and Development Expense (us-gaap, duration, debit). Amount of expense for research and development. Includes, but is not limited to, cost for computer software product to be sold, leased, or otherwise marketed and writeoff of research and development assets acquired in transaction other than...
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]; research_and_development: Research and development expense for the period (incl. acquired IPR&D only when the filer prints it inside the R&D line). [not applicable: bank,broker_am,insurer,equity_reit,utility,bdc]
- **Data point:** research_and_development; operating_expenses; polarity research_and_development:positive; role research_and_development:primary#1
- **Rules:** I19
- **Evidence:** 66 companies, 985 served, 2774 proven, 75 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CostOfGoodsAndServicesSold`
- **Meaning:** Cost of Product and Service Sold (us-gaap, duration, debit). The aggregate costs related to goods produced and sold and services rendered by an entity during the reporting period. This excludes costs incurred during the reporting period related to financial services rendered and other revenue generat...
- **Data point definition:** cost_of_revenue: Cost of goods sold / cost of revenue for the period: the costs the filer matches to revenue above gross profit. [not applicable: bank,insurer,bdc]; gross_profit: Revenue minus cost of revenue for the period. [not applicable: bank,lender,broker_am,insurer,equity_reit,utility,bdc] (+1 more)
- **Data point:** cost_of_revenue; gross_profit; operating_expenses; polarity cost_of_revenue:positive; role cost_of_revenue:primary#2
- **Rules:** I02; I03; I04
- **Evidence:** 65 companies, 955 served, 16174 proven, 62 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces AdvertisingRevenueCost@2018; AssetManagementCosts@2018; CasinoExpenses@2018; ConcessionsCosts@2018 (+62 more)

### `Liabilities`
- **Meaning:** Liabilities (us-gaap, instant, credit). Amount of liability recognized for present obligation requiring transfer or otherwise providing economic benefit to others.
- **Data point definition:** total_liabilities: Total liabilities as printed.
- **Data point:** total_liabilities
- **Rules:** C03; F02; B25; resolver functions resolve; run; apply_tl_corroboration
- **Evidence:** 83 companies, 950 served, 29466 proven, 87 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000101829-20-000013: RTX (UTX) FY2019 10-K utx-20191231.htm consolidated balance sheet prints Total Liabilities 95,390 (2018: 93,492);  the XBRL tags only the 2018 value (R4.htm show
- **Pattern hits:** none
- **Deprecation:** replaces EquityMethodInvestmentSummarizedFinancialInformationLiabilities@2020; FreshStartAdjustmentIncreaseDecreaseLiabilities@2021; PostconfirmationLiabilities@2021; PreconfirmationLiabilities@2021 (+4 more)

### `OperatingIncomeLoss`
- **Meaning:** Operating Income (Loss) (us-gaap, duration, credit). The net result for the period of deducting operating expenses from operating revenues.
- **Data point definition:** operating_expenses: Operating expenses excluding cost of revenue: SG&A, R&D, D&A and other operating lines between gross profit (or revenue) and operating income. [not applicable: bank]; operating_income: Operating income: revenue minus all operating costs (COR, opex, restructuring and impairment), before interest, other non-operating items, equity-method income and tax. [not applicable: bank]
- **Data point:** operating_income; operating_expenses
- **Rules:** C13; resolver functions resolve
- **Evidence:** 80 companies, 948 served, 34797 proven, 106 certified cells; last verified 2026-11-15
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

### `PaymentsToAcquirePropertyPlantAndEquipment`
- **Meaning:** Payments to Acquire Property, Plant, and Equipment (us-gaap, duration, credit). The cash outflow associated with the acquisition of long-lived, physical assets that are used in the normal conduct of business to produce goods and services and not intended for resale; includes cash outflows to pay for construction of sel...
- **Data point definition:** capex: Payments for property, plant and equipment incl. capitalized software, leased fleets, turnarounds, construction in progress and REIT tenant improvements;  excludes oil and gas property and acreage acquisitions (founder 2026-11-04). [not applicable: bank,insurer,equity_reit,bdc]
- **Data point:** capex; polarity capex:positive; role capex:primary#1
- **Rules:** K03; K04; K05; K06; K07; K08; K09; K40; family resolve_cf.CAPEX; resolve_all.NARROW[capex]
- **Evidence:** 82 companies, 914 served, 17784 proven, 99 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `InventoryNet`
- **Meaning:** Inventory, Net (us-gaap, instant, debit). Amount after valuation and LIFO reserves of inventory expected to be sold, or consumed within one year or operating cycle, if longer.
- **Data point definition:** inventory: Inventories at period end as printed. [not applicable: bank,lender,broker_am,insurer,equity_reit,bdc]
- **Data point:** inventory; role inventory:primary#1
- **Rules:** B15; B14; resolver functions inventory_header_sum
- **Evidence:** 80 companies, 895 served, 3308 proven, 92 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseInventories@2021; PostconfirmationInventories@2021; PreconfirmationInventories@2021

### `InterestPaidNet`
- **Meaning:** Interest Paid, Excluding Capitalized Interest, Operating Activity (us-gaap, duration, credit). Amount of cash paid for interest, excluding capitalized interest, classified as operating activity. Includes, but is not limited to, payment to settle zero-coupon bond for accreted interest of debt discount and debt instrument with insignif...
- **Data point definition:** cash_paid_for_interest: Cash paid for interest, net of amounts capitalized (InterestPaidNet).
- **Data point:** cash_paid_for_interest; polarity cash_paid_for_interest:positive; role cash_paid_for_interest:primary#1
- **Rules:** K35
- **Evidence:** 98 companies, 883 served, 1627 proven, 69 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `IncomeTaxesPaidNet`
- **Meaning:** Income Tax Paid, after Refund Received (us-gaap, duration, credit). Amount, after refund, of cash paid to foreign, federal, state, and local jurisdictions as income tax.
- **Data point definition:** cash_paid_for_income_taxes: Cash paid for income taxes, net of refunds, as printed.
- **Data point:** cash_paid_for_income_taxes; polarity cash_paid_for_income_taxes:signed; role cash_paid_for_income_taxes:primary#1
- **Rules:** K32; K34; K33
- **Evidence:** 105 companies, 866 served, 1547 proven, 70 certified cells; last verified 2026-11-15
- **Known problems:** filer XBRL error 0000040545-17-000010: GE FY2016 10-K R7.htm statement of cash flows: Cash recovered (paid) during the year for income taxes (7,469): 7,469 paid;  IncomeTaxesPaidNet is positive for ta; filer XBRL error 0000040545-16-000145: GE FY2016 10-K R7.htm (0000040545-17-000010) prints the FY2015 column: Cash recovered (paid) during the year for income taxes (2,486): 2,486 paid;  the FY2015 10 (+2 more)
- **Pattern hits:** none

### `IncreaseDecreaseInInventories`
- **Meaning:** Increase (Decrease) in Inventories (us-gaap, duration, credit). The increase (decrease) during the reporting period in the aggregate value of all inventory held by the reporting entity, associated with underlying transactions that are classified as operating activities.
- **Data point definition:** cf_inventory_change: Cash-flow change in inventories, raw XBRL sign.
- **Data point:** cf_inventory_change; polarity cf_inventory_change:raw; role cf_inventory_change:primary#1
- **Rules:** none; family resolve_cf.WC[cf_inventory_change]
- **Evidence:** 74 companies, 862 served, 2794 proven, 94 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
