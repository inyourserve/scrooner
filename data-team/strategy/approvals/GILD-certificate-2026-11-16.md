# GILD display certification, 2026-11-16: PASS

Approver: Ritwik (cloud), session_01GLmSDz8UUfjBrVex2j8ugb. Request: `data-team/strategy/approvals/requests/GILD-request-2026-11-15.md`.
Coverage: `data-team/strategy/certification/GILD-coverage-2026-11-15.csv`, sha256 `77c9df26065e64bfd467032473b1f87001142c642ed60747c162bbee0c178c62` (checked against the request). Cells: HIDDEN_ROW=11, SHOWN_VALUE=495.
Method: CERTIFICATION-METHOD-2026-11-16.md, run by `pipeline/scripts/certify_display.py --request ... --live` in workflow run https://github.com/inyourserve/scrooner/actions/runs/43813141621 (read-only). Every check reads SEC's Financial Statement and Notes data for the cited filing (fsn.*); nothing was re-downloaded.

| Check | Result |
|---|---|
| Gate: 0 OPEN; value, accession and R page on every shown cell and part; signed parts sum | pass |
| 32 random shown cells (seed `GILD-77c9df26065e`) | 32 match, 0 wrong |
| total_debt census, face debt lines plus note leases | 11 of 11 years match |
| Hidden rows and hidden years | evidenced |

**Bound:** 0 wrong in 32 random shown cells: Clopper-Pearson 95% upper bound **8.94%** for GILD alone. Pooled over certified companies (registry.csv): GILD and JNJ, 0 wrong in 64, upper bound 4.57%. The 0.10% target needs about 2,995 pooled cells.

## Hides evidenced

- interest_income: no presented, undimensioned, annual interest-income fact at a display-year end in any periodic filing.

## The 32 drawn cells

Each matched the cited filing in fsn.*: same tag, period end (within 7 days, for 52/53-week years), duration and dimensions; presented on the cited R page; summed cells match part by part; derived cells match their identity (total liabilities = assets less total equity including NCI; gross profit = shown revenue less shown cost of revenue).

| # | Data point | FY | Shown | Filing | R page | Tag or parts |
|---|---|---|---|---|---|---|
| 1 | accounts_payable | 2019 | 713000000 | 0000882095-20-000006 | R2 | AccountsPayableCurrent |
| 2 | basic_eps | 2017 | 3.5400 | 0000882095-18-000008 | R4 | EarningsPerShareBasic |
| 3 | cash_and_equivalents | 2017 | 7588000000 | 0000882095-18-000008 | R2 | CashAndCashEquivalentsAtCarryingValue |
| 4 | cash_paid_for_income_taxes | 2020 | 2639000000 | 0000882095-21-000008 | R8 | IncomeTaxesPaid |
| 5 | cash_paid_for_income_taxes | 2021 | 2509000000 | 0000882095-22-000007 | R9 | IncomeTaxesPaid |
| 6 | cash_paid_for_income_taxes | 2023 | 3990000000 | 0000882095-26-000006 | R104 | IncomeTaxesPaidNet |
| 7 | cf_ar_change | 2019 | 218000000 | 0000882095-20-000006 | R8 | IncreaseDecreaseInAccountsReceivable |
| 8 | cf_inventory_change | 2024 | 426000000 | 0000882095-25-000006 | R9 | IncreaseDecreaseInInventories |
| 9 | cost_of_revenue | 2022 | 5657000000 | 0000882095-23-000007 | R5 | CostOfGoodsAndServicesSold |
| 10 | current_liabilities | 2021 | 11610000000 | 0000882095-22-000007 | R3 | LiabilitiesCurrent |
| 11 | current_liabilities | 2023 | 11280000000 | 0000882095-24-000007 | R3 | LiabilitiesCurrent |
| 12 | depreciation_and_amortization | 2015 | 1098000000 | 0000882095-16-000039 | R8 | Depreciation + AdjustmentForAmortization |
| 13 | depreciation_and_amortization | 2020 | 1480000000 | 0000882095-21-000008 | R8 | Depreciation + AdjustmentForAmortization |
| 14 | gross_profit | 2024 | 22503000000 | 0000882095-25-000006 | R5 | derived |
| 15 | income_tax_expense | 2015 | 3553000000 | 0000882095-16-000039 | R4 | IncomeTaxExpenseBenefit |
| 16 | income_tax_expense | 2016 | 3609000000 | 0000882095-17-000006 | R4 | IncomeTaxExpenseBenefit |
| 17 | income_tax_expense | 2025 | 1286000000 | 0000882095-26-000006 | R5 | IncomeTaxExpenseBenefit |
| 18 | interest_expense | 2015 | 688000000 | 0000882095-16-000039 | R4 | InterestExpense |
| 19 | interest_expense | 2021 | 1001000000 | 0000882095-22-000007 | R5 | InterestExpense |
| 20 | net_income | 2023 | 5665000000 | 0000882095-24-000007 | R5 | NetIncomeLoss |
| 21 | operating_income | 2019 | 4287000000 | 0000882095-20-000006 | R4 | OperatingIncomeLoss |
| 22 | other_income_expense_net | 2018 | 676000000 | 0000882095-19-000006 | R4 | NonoperatingIncomeExpense |
| 23 | ppe_net | 2015 | 2276000000 | 0000882095-16-000039 | R2 | PropertyPlantAndEquipmentNet |
| 24 | revenue | 2015 | 32639000000.0000 | 0000882095-16-000039 | R4 | SalesRevenueNet |
| 25 | revenue | 2020 | 24689000000 | 0000882095-21-000008 | R4 | RevenueFromContractWithCustomerExcludingAssessedTax |
| 26 | sga_expense | 2016 | 3398000000 | 0000882095-17-000006 | R4 | SellingGeneralAndAdministrativeExpense |
| 27 | shares_outstanding | 2025 | 1241000000 | 0000882095-26-000006 | R4 | CommonStockSharesOutstanding |
| 28 | stockholders_equity | 2018 | 21387000000 | 0000882095-19-000006 | R2 | StockholdersEquity |
| 29 | total_liabilities | 2022 | 41962000000 | 0000882095-23-000007 | R3 | derived |
| 30 | weighted_basic_shares | 2017 | 1307000000 | 0000882095-18-000008 | R4 | WeightedAverageNumberOfSharesOutstandingBasic |
| 31 | weighted_basic_shares | 2018 | 1298000000 | 0000882095-19-000006 | R4 | WeightedAverageNumberOfSharesOutstandingBasic |
| 32 | weighted_basic_shares | 2019 | 1270000000 | 0000882095-20-000006 | R4 | WeightedAverageNumberOfSharesOutstandingBasic |

## Limits

- This certifies evidence for the coverage file above. It is not approval for a production write (that needs the founder's typed words in the applying session).
- Any changed cell, a proof-version bump that changes a verdict, or a new filing period voids the affected cells until re-drawn.
- fsn.* is SEC's own extraction. Where it lacks a fact, the tool reports NOT_FOUND for the approver; there were none in this run.
