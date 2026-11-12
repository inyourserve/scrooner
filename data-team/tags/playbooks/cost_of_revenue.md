# Playbook: cost_of_revenue_resolved and gross_profit_resolved

Card: [`../cards/operating-income.md`](../cards/operating-income.md) (CostsAndExpenses has 4 perimeters over 958 filers) and [`../cards/revenue.md`](../cards/revenue.md). Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows).

## 1. Mapped

| Concept | Tag | Companies |
|---|---|---|
| cost_of_revenue (`is.cost_of_revenue_total@1`), 424 | `CostOfGoodsAndServicesSold` | 320 |
| | `CostOfRevenue` | 111 |
| gross_profit (`is.gross_profit_line@1`), 236 | `GrossProfit` | 236 |

Only 236 companies print a gross profit line; the gross identity check (G2, revenue − cost = gross profit) is the derivation path for the others, and it applies only where cost of revenue is a full cost-of-sales perimeter (see the traps).

## 2. The 208 cost-of-revenue gap companies: what their IS shows (unmapped lines in those filings)

| Rank | Tag | Companies | Meaning | Status |
|---|---|---|---|---|
| 1 | `CostsAndExpenses` | 77 | "Total costs and expenses": NOT cost of revenue (it includes SG&A, R&D; four perimeters in the card) | correctly unmapped |
| 2 | `CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization` | 36 | cost of sales printed **without D&A**, with D&A as a separate face line | held: `hold_perimeter_excl_da` (accountant ruling pending, `is_not_extracted.md`) |
| 3 | `CostDirectMaterial` (6), `CostDirectLabor` (3), `CostOfPropertyRepairsAndMaintenance` (3), `CostOfOtherPropertyOperatingExpense` (4) | | components of an expense list (utilities' "purchased power and fuel", REIT property costs) | components, never the total |
| 4 | `OtherCostOfOperatingRevenue` | 3 | "Cost of sales" at a few filers (label = total) | candidate, per filing |
| 5 | `CostOfGoodsAndServicesSoldAmortization` / `...DepreciationAndAmortization` / `...Depreciation` | 2-3 each | the D&A slice of cost of sales | components |
| 6 | custom cost-of-sales tags, one company each: `CostOfGoodsAndServicesSoldOperating` (1711279), `CostOfGoodsSoldExcludingAmortizationOfIntangibleAssetsAndShareBasedCompensation` (1032975), `CostOfProductSalesExcludingAmortizationOf...` (1232524), `CostOfServices` (1865782), `CostofnaturalGasSoldandTransported` (72903), `CostOfHomesSold` (912593, "Home costs and selling": includes selling!) | ~8 | | candidates only with the label and calc check; several are "excluding X" perimeters |

Most of the remaining gap is legitimately absent: banks, insurers, REITs, utilities and service companies that print a single-step expense list with no cost-of-revenue line. That is a template "not applicable" reason, not a tag gap.

## 3. Candidates (not approved)
1. The 36 `...ExcludingDepreciationDepletionAndAmortization` filers wait on one ruling: is "cost of sales excluding D&A" acceptable as cost_of_revenue (with a perimeter note), or blank with a reason? It is the second-largest pattern; the ruling decides 36 companies at once. Note that gross profit derived from it is overstated by the D&A in cost of sales.
2. A custom tag whose label is exactly "Cost of sales" / "Cost of goods sold" / "Cost of revenue(s)" / "Cost of services", that is a calc child of the operating-expense total, with no us-gaap cost-of-revenue tag in the filing. Flag every "excluding ..." in the tag name or label as a perimeter variant (same ruling as item 1).

## 4. Traps
- `CostsAndExpenses` is never cost of revenue (77 companies would be wrong).
- Two cost lines (product + service) with no printed total: the sum is a derivation (G3 calc-sum rule, `is_not_extracted.md`), never one line.
- "Cost of sales, including occupancy" (retailers) and "cost of homes sold and selling" are wider perimeters; the label must be read.
