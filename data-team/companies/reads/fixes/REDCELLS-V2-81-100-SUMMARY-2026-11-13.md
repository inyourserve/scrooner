# Red cells v2 (top100-redcells-v2-2026-11-13.csv @5f92749c), ranks 81-100, reader rows: summary

Every decided cell was read on the SEC R page of the period's own 10-K (or, where no own 10-K prints it, the first 10-K whose comparative column does). Rows are merged into `<TICKER>-fixes-2026-11-13.csv`; v2 notes start with "v2 list (cls/coverage_reason)". A v2 row replaces a v1 row for the same cell.

| ticker | reader cells | decided | open |
|---|---|---|---|
| VRTX | 7 | 7 | 0 |
| ISRG | 2 | 2 | 0 |
| VLO | 12 | 9 | 3 |
| FTNT | 3 | 3 | 0 |
| BMY | 17 | 17 | 0 |
| MPC | 12 | 12 | 0 |
| STX | 6 | 6 | 0 |
| SCHW | 1 | 1 | 0 |
| BA | 11 | 11 | 0 |
| T | 18 | 18 | 0 |
| ETN | 23 | 23 | 0 |
| LMT | 22 | 22 | 0 |
| ACN | 12 | 11 | 1 |
| CB | 22 | 4 | 18 |
| SPGI | 12 | 12 | 0 |
| NOW | 20 | 20 | 0 |
| PGR | 2 | 2 | 0 |
| NEM | 20 | 19 | 1 |
| MO | 25 | 25 | 0 |
| UBER | 66 | 65 | 1 |
| total | 313 | 289 | 24 |

## Questions for the approver (flagged in the rows)

- **Own 10-K vs later recast comparative.** Where the served value is a later 10-K's restated column (ISRG/NOW/LMT/MPC/NEM/FTNT/BMY/MO revenue or cost, NOW 2017 EPS, LMT 2017 inventory), these rows claim the own 10-K value. If the rule should be "latest presentation", those rows flip.
- **BA operating_expenses FY2025 = 8**: the tying GP-to-OI span includes a 9,672 disposal gain (ruling 2026-11-12 counts every span line).
- **Trust preferred / build-to-suit obligations in total_debt** (CB excluded TruPS; VRTX included the construction financing obligation).
- **NEM inventory**: "Inventories" line mapped; current ore stockpiles are a separate face line.
- **Interest expense, net** lines (ETN, VRTX, SPGI, MO, MPC) are decided combined; SPGI tags its net line InterestExpense.

## Reader traps found

- R-page footnote spacer cells `class="fn"` shift value columns (MO FY2025 CF R7); drop them with `class="th"`.
- Pre-2016 FilingSummary.xml uses `<Report>` without attributes; a regex on `<Report instance=` misses every report.
- Statement pages filed under MenuCategory "Uncategorized" (SCHW, STX, MPC, LMT income statements).
- AT&T tags its FY2022+ "Inventories" BS line PrepaidExpenseCurrent; CB declares dividends in CHF.

## Open cells

| ticker | data point | FY | why open |
|---|---|---|---|
| ACN | shares_outstanding | 2025 | definition: ACN tags CommonStockSharesOutstanding = issued shares (treasury included); the BS parenthetical prints only Class X outstanding |
| CB | dividends_per_share | 2015 | currency: CB declares dividends in CHF (CommonStockDividendsPerShareDeclared in CHF/shares, e.g. 2015 2.56 CHF); the USD figure needs a decision |
| CB | dividends_per_share | 2020 | currency: CB declares dividends in CHF (CommonStockDividendsPerShareDeclared in CHF/shares, e.g. 2015 2.56 CHF); the USD figure needs a decision |
| CB | dividends_per_share | 2021 | currency: CB declares dividends in CHF (CommonStockDividendsPerShareDeclared in CHF/shares, e.g. 2015 2.56 CHF); the USD figure needs a decision |
| CB | dividends_per_share | 2022 | currency: CB declares dividends in CHF (CommonStockDividendsPerShareDeclared in CHF/shares, e.g. 2015 2.56 CHF); the USD figure needs a decision |
| CB | dividends_per_share | 2023 | currency: CB declares dividends in CHF (CommonStockDividendsPerShareDeclared in CHF/shares, e.g. 2015 2.56 CHF); the USD figure needs a decision |
| CB | dividends_per_share | 2024 | currency: CB declares dividends in CHF (CommonStockDividendsPerShareDeclared in CHF/shares, e.g. 2015 2.56 CHF); the USD figure needs a decision |
| CB | dividends_per_share | 2025 | currency: CB declares dividends in CHF (CommonStockDividendsPerShareDeclared in CHF/shares, e.g. 2015 2.56 CHF); the USD figure needs a decision |
| CB | ppe_net | 2015 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2016 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2017 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2018 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2019 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2020 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2021 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2022 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2023 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2024 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| CB | ppe_net | 2025 | not on the insurer's BS (inside other assets); PropertyPlantAndEquipmentNet exists only as a rounded narrative fact (e.g. $1.2 billion); no R page table located |
| NEM | dividends_per_share | 2019 | definition: the equity parenthetical (R11) prints regular 0.56 and special 0.88 dividends declared per share; regular only (served) or regular + special? |
| UBER | total_debt | 2018 | capital-lease part not located: FY2019 10-K prints 2018 debt (6,869 noncurrent + 27 current) but no pre-ASC 842 capital lease total for 2018 |
| VLO | capex | 2018 | printed capex + turnaround lines (2,667) do not reach the served 3,376; the missing 709 is not on the CF face as a capex line |
| VLO | capex | 2019 | printed capex + turnaround lines (2,774) vs served 2,846; 72 unexplained |
| VLO | cost_of_revenue | 2015 | the FY2015 IS has no cost-of-sales subtotal; later 10-Ks' 'Total cost of sales' includes opex and part of D&A, which the 2015 face does not split; no printed sum equals the served 80,689 |
