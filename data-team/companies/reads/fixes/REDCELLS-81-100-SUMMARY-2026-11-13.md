# Top-100 red cells, ranks 81-100: closing summary (2026-11-13)

Source: data-team/tags/red-cells/top100-redcells-2026-11-13.csv (main 0b364d35), causes (a) value in the filing not served, (b) FY-1 from the next 10-K comparative column, (c) proof DISAGREE; loader and superseded rows skipped. One file per company: `<TICKER>-fixes-2026-11-13.csv`. Every closed cell was read on the SEC R page (FILING-CHECKED); (a) cells also equal the value in the red-cell evidence, and every (b) and second-pass value equals SEC companyfacts for the same accession, tag and period (44 of 44; NOW interest income 2024 is the one tag companyfacts lacks, value printed on the face).

| rank | ticker | cells | closed | open |
|---|---|---|---|---|
| 81 | T | 38 | 38 | 0 |
| 82 | SCHW | 37 | 28 | 9 |
| 83 | ETN | 29 | 27 | 2 |
| 84 | BA | 42 | 30 | 12 |
| 85 | ISRG | 8 | 6 | 2 |
| 86 | NOW | 39 | 35 | 4 |
| 87 | STX | 8 | 4 | 4 |
| 88 | UBER | 32 | 11 | 21 |
| 89 | ACN | 33 | 17 | 16 |
| 90 | CB | 13 | 3 | 10 |
| 91 | MPC | 36 | 30 | 6 |
| 92 | VLO | 28 | 24 | 4 |
| 93 | LMT | 53 | 37 | 16 |
| 94 | VRTX | 41 | 37 | 4 |
| 95 | PGR | 23 | 12 | 11 |
| 96 | SPGI | 34 | 19 | 15 |
| 97 | MO | 27 | 23 | 4 |
| 98 | NEM | 38 | 21 | 17 |
| 99 | FTNT | 43 | 39 | 4 |
| 100 | BMY | 38 | 34 | 4 |
| | total | 640 | 475 | 165 |

## Proof DISAGREE decisions (24 cells)

- Map wrong (1): UBER interest_expense FY2024: the face line "Interest expense" is InterestExpenseNonoperating 523 (R5, 0001543151-25-000008); the map serves InterestExpenseDebt 489.
- Proof wrong (23): the value served equals the printed line. Revenue totals flagged only_a_component_line_presented (T 4, UBER 2, MPC 7: MPC revenue is "Sales and other operating revenues"; RevenuesAndOtherIncome is not a revenue total); components_sum failures from overlapping or missing component lists (T assets 2019, SCHW interest expense 2021, ETN CFO 2017 and current assets 2015, BA CFO 2020, NOW net income 2021, STX current liabilities 2020 (omitted LongTermDebtCurrent 19) and tax 2021, ACN current liabilities 2020, LMT gross profit 2021 (severance inside cost of sales, subtracted twice)).

## Other corrections found while closing

- BA inventory 2024: docmap said not_presented; the face prints Inventories 87,550 (InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings).
- STX interest_expense: era tag change from the FY2025 10-K (InterestExpenseNonoperating; earlier InterestExpense).
- VLO cf_ar_change 2024: component_in_note (R100), the face prints only the combined working-capital line.
- Statement pages filed in FilingSummary as "Uncategorized" (SCHW, STX, MPC, LMT income statements; R3) and footnote cells that shift columns (MO 2025 10-K R7) are reader traps.

## Open cells and why

| ticker | data point | FY | reason |
|---|---|---|---|
| SCHW | cash_and_equivalents | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SCHW | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| SCHW | goodwill | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SCHW | ppe_net | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SCHW | stockholders_equity | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SCHW | total_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SCHW | total_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SCHW | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| SCHW | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| ETN | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| ETN | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| BA | accounts_payable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | accounts_receivable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | cash_and_equivalents | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | current_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | current_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | goodwill | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | inventory | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | ppe_net | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | shares_outstanding | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | stockholders_equity | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | total_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| BA | total_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| ISRG | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| ISRG | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| NOW | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| NOW | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| NOW | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| NOW | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| STX | cash_paid_for_income_taxes | 2025 | Engineering's data point (skipped per instructions) |
| STX | cash_paid_for_interest | 2025 | Engineering's data point (skipped per instructions) |
| STX | weighted_basic_shares | 2025 | Engineering's data point (skipped per instructions) |
| STX | weighted_diluted_shares | 2025 | Engineering's data point (skipped per instructions) |
| UBER | accounts_payable | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | accounts_receivable | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | cash_paid_for_income_taxes | 2017 | Engineering's data point (skipped per instructions) |
| UBER | cash_paid_for_income_taxes | 2018 | Engineering's data point (skipped per instructions) |
| UBER | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| UBER | cash_paid_for_interest | 2017 | Engineering's data point (skipped per instructions) |
| UBER | cash_paid_for_interest | 2018 | Engineering's data point (skipped per instructions) |
| UBER | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| UBER | current_assets | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | current_liabilities | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | ppe_net | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | shares_outstanding | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | total_assets | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | total_debt | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | total_liabilities | 2017 | no 10-K prints it: UBER first 10-K is FY2019, its balance sheet covers 2019 and 2018 only (FY2017 BS only in the S-1) |
| UBER | weighted_basic_shares | 2017 | Engineering's data point (skipped per instructions) |
| UBER | weighted_basic_shares | 2018 | Engineering's data point (skipped per instructions) |
| UBER | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| UBER | weighted_diluted_shares | 2017 | Engineering's data point (skipped per instructions) |
| UBER | weighted_diluted_shares | 2018 | Engineering's data point (skipped per instructions) |
| UBER | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| ACN | cash_paid_for_income_taxes | 2025 | Engineering's data point (skipped per instructions) |
| ACN | cash_paid_for_interest | 2025 | Engineering's data point (skipped per instructions) |
| ACN | shares_outstanding | 2015 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2016 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2017 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2018 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2019 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2020 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2021 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2022 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2023 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2024 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2025 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | shares_outstanding | 2026 | definition question: ACN tags CommonStockSharesOutstanding = issued shares (treasury included; equity statement R6 Class A 658,549,000 = issued) and prints no Class A outstanding net of treasury; Class X only on the BS parenthetical |
| ACN | weighted_basic_shares | 2025 | Engineering's data point (skipped per instructions) |
| ACN | weighted_diluted_shares | 2025 | Engineering's data point (skipped per instructions) |
| CB | cash_and_equivalents | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| CB | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| CB | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| CB | goodwill | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| CB | shares_outstanding | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| CB | stockholders_equity | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| CB | total_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| CB | total_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| CB | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| CB | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| MPC | amortization_of_intangibles | 2016 | note value not found: the tag is on no R page column for the year by its MetaLinks presentation roles (value only in companyfacts) |
| MPC | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| MPC | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| MPC | sbc | 2018 | note value not found: the tag is on no R page column for the year by its MetaLinks presentation roles (value only in companyfacts) |
| MPC | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| MPC | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| VLO | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| VLO | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| VLO | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| VLO | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| LMT | accounts_payable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | accounts_receivable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | cash_and_equivalents | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| LMT | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| LMT | current_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | current_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | goodwill | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | inventory | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | ppe_net | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | shares_outstanding | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | stockholders_equity | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | total_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | total_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| LMT | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| LMT | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| VRTX | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| VRTX | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| VRTX | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| VRTX | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| PGR | cash_and_equivalents | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| PGR | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| PGR | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| PGR | ppe_net | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| PGR | share_buybacks | 2024 | definition question: CF face prints open-market repurchases 13 and tax-withholding repurchases 121 (docmap says not_presented) |
| PGR | stockholders_equity | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| PGR | total_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| PGR | total_debt | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| PGR | total_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| PGR | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| PGR | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| SPGI | accounts_payable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | accounts_receivable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | cash_and_equivalents | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| SPGI | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| SPGI | current_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | current_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | goodwill | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | ppe_net | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | shares_outstanding | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | stockholders_equity | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | total_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | total_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| SPGI | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| SPGI | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| MO | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| MO | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| MO | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| MO | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| NEM | accounts_payable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | accounts_receivable | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | cash_and_equivalents | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| NEM | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| NEM | current_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | current_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | goodwill | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | inventory | 2024 | definition question: face prints Inventories 1,423 and current Stockpiles and ore on leach pads 761 as separate lines; whether inventory includes the current stockpiles (docmap says not_presented) |
| NEM | inventory | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | ppe_net | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | shares_outstanding | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | stockholders_equity | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | total_assets | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | total_liabilities | 2026 | open year: FY2026 has no 10-K yet (placeholder period end 2026-09-12) |
| NEM | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| NEM | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| FTNT | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| FTNT | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| FTNT | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| FTNT | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
| BMY | cash_paid_for_income_taxes | 2024 | Engineering's data point (skipped per instructions) |
| BMY | cash_paid_for_interest | 2024 | Engineering's data point (skipped per instructions) |
| BMY | weighted_basic_shares | 2024 | Engineering's data point (skipped per instructions) |
| BMY | weighted_diluted_shares | 2024 | Engineering's data point (skipped per instructions) |
