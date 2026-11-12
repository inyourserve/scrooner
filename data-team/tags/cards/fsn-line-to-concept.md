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
- **core.fact holds no extension tags**: a custom-tag face line cannot be a companyfacts value source today. Every row whose value would come from a custom tag is `custom_value_source_pending` (company-overrides.csv status) until the founder rules on the source. Custom tags still define structure (calc position, combined lines), but serve no value yet.
