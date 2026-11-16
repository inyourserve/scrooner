# BA display certification, 2026-11-16: FAIL

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/BA-request-2026-11-15.md`.
Coverage: `data-team/strategy/certification/BA-coverage-2026-11-15.csv`, sha256 `d0d3a6f1c47070bd954819e0c78213fbba25fb54074f66b452941db4e3b3a904` (checked against the request). Cells: HIDDEN_ROW=11, HIDDEN_YEAR=18, SHOWN_VALUE=477.
Method: CERTIFICATION-METHOD-2026-11-16.md, run by `pipeline/scripts/certify_display.py --request ... --live` in workflow run https://github.com/inyourserve/scrooner/actions/runs/43813141621 (read-only). Every check reads SEC's Financial Statement and Notes data for the cited filing (fsn.*); nothing was re-downloaded.

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession and R page on every shown cell and part; signed parts sum | pass |
| 32 random shown cells (seed `BA-d0d3a6f1c470`) | 32 match, 0 wrong |
| total_debt census, face debt lines plus note leases | 11 of 11 years match |
| Hidden rows and hidden years | see findings |

**Bound:** 0 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for BA alone. Pooled over certified companies (registry.csv): GILD and JNJ, 0 wrong in 64, upper bound 4.57%. The 0.10% target needs about 2,995 pooled cells.

## Findings

- **18 HIDDEN_YEAR cells are not pre-filing years.** A Boeing 10-K or 10-Q presents each of these year ends (own or comparative column), so under CERTIFICATION-METHOD-2026-11-16 they are in-row gaps that must be shown with the filing's value (a printed zero or dash is a value), not hidden:
  - comprehensive_income FY2015-FY2019 (5 cells)
  - dividends_paid FY2023-FY2025 (3 cells)
  - dividends_per_share FY2020-FY2025 (6 cells)
  - share_buybacks FY2022-FY2025 (4 cells)
- Everything else checked clean: 32 of 32 random shown cells match the filing, total_debt matches in all 11 years.

## The 32 drawn cells

Each matched the cited filing in fsn.*: same tag, period end (within 7 days, for 52/53-week years), duration and dimensions; presented on the cited R page; summed cells match part by part; derived cells match their identity (total liabilities = assets less total equity including NCI; gross profit = shown revenue less shown cost of revenue).

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | accounts_payable | 2018 | 12916000000 | 0000012927-19-000010 | R5 | AccountsPayableCurrent |
| 2 | accounts_payable | 2020 | 12928000000 | 0000012927-21-000011 | R4 | AccountsPayableCurrent |
| 3 | accounts_receivable | 2022 | 2517000000 | 0000012927-23-000007 | R6 | AccountsReceivableNetCurrent |
| 4 | amortization_of_intangibles | 2024 | 223000000 | 0000012927-25-000015 | R67 | AmortizationOfIntangibleAssets |
| 5 | cash_flow_investing | 2023 | -2437000000 | 0000012927-24-000010 | R8 | NetCashProvidedByUsedInInvestingActivities |
| 6 | cash_flow_investing | 2024 | -11973000000 | 0000012927-25-000015 | R8 | NetCashProvidedByUsedInInvestingActivities |
| 7 | cash_paid_for_interest | 2019 | 973000000 | 0000012927-20-000014 | R109 | InterestPaid |
| 8 | cash_paid_for_interest | 2023 | 2408000000 | 0000012927-24-000010 | R104 | InterestPaid |
| 9 | cfo | 2015 | 9363000000 | 0000012927-16-000099 | R8 | NetCashProvidedByUsedInOperatingActivities |
| 10 | cfo | 2018 | 15322000000 | 0000012927-19-000010 | R7 | NetCashProvidedByUsedInOperatingActivities |
| 11 | cost_of_revenue | 2018 | 81490000000.0000 | 0000012927-19-000010 | R2 | CostOfRevenue |
| 12 | depreciation_and_amortization | 2017 | 2047000000 | 0000012927-20-000014 | R7 | DepreciationDepletionAndAmortization |
| 13 | diluted_eps | 2015 | 7.4400 | 0000012927-16-000099 | R2 | EarningsPerShareDiluted |
| 14 | dividends_per_share | 2016 | 4.6900 | 0000012927-17-000006 | R9 | CommonStockDividendsPerShareDeclared |
| 15 | goodwill | 2015 | 5126000000 | 0000012927-16-000099 | R6 | Goodwill |
| 16 | goodwill | 2024 | 8084000000 | 0000012927-25-000015 | R6 | Goodwill |
| 17 | income_before_tax | 2018 | 11604000000 | 0000012927-19-000010 | R2 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
| 18 | income_before_tax | 2020 | -14476000000 | 0000012927-21-000011 | R2 | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest |
| 19 | income_tax_expense | 2021 | -743000000 | 0000012927-22-000010 | R3 | IncomeTaxExpenseBenefit |
| 20 | inventory | 2015 | 47257000000 | 0000012927-16-000099 | R6 | InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings |
| 21 | inventory | 2022 | 78151000000 | 0000012927-23-000007 | R6 | InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings |
| 22 | inventory | 2024 | 87550000000 | 0000012927-25-000015 | R6 | InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings |
| 23 | net_income | 2021 | -4202000000 | 0000012927-22-000010 | R3 | NetIncomeLoss |
| 24 | ppe_net | 2024 | 11412000000 | 0000012927-25-000015 | R6 | PropertyPlantAndEquipmentNet |
| 25 | research_and_development | 2024 | 3812000000 | 0000012927-25-000015 | R3 | ResearchAndDevelopmentExpense |
| 26 | revenue | 2017 | 94005000000 | 0000012927-20-000014 | R2 | Revenues |
| 27 | sga_expense | 2019 | 3909000000 | 0000012927-20-000014 | R2 | GeneralAndAdministrativeExpense |
| 28 | share_buybacks | 2016 | 7001000000 | 0000012927-17-000006 | R7 | PaymentsForRepurchaseOfCommonStock |
| 29 | shares_outstanding | 2015 | 1012261159 | 0000012927-16-000099 | R123 | CommonStockSharesOutstanding |
| 30 | stockholders_equity | 2023 | -17233000000 | 0000012927-24-000010 | R6 | StockholdersEquity |
| 31 | weighted_basic_shares | 2025 | 759800000 | 0001628280-26-004357 | R75 | WeightedAverageNumberOfSharesOutstandingBasic |
| 32 | weighted_diluted_shares | 2019 | 565400000 | 0000012927-20-000014 | R69 | WeightedAverageNumberOfDilutedSharesOutstanding |

## Limits

- This certifies evidence for the coverage file above. It is not approval for a production write (that needs the founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
- fsn.* is SEC's own extraction. Where it lacks a fact, the tool reports NOT_FOUND for the approver; there were none in this run.

## To re-request

Fix the findings, re-export the coverage file, and file a new request. The new file's hash gives a new seed and a new draw.
