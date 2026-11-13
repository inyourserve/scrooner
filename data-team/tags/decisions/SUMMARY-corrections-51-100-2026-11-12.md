# Summary: corrections from the document-first reads (Ritwik cloud, 2026-11-12)

For Dhairya. Every fix from your two read messages is applied to `companies-51-100-exceptions-2026-11-11.csv`. The rule changes are in the "Corrections" section of `card-notes-51-100-2026-11-11.md`.

## Store re-checks

I re-checked these against the FSN store, and all agree with the reader:

- **BA:** CostOfGoodsAndServicesSold has values only under members (73,761 + 11,413). Gross profit 4,289 = 89,463 − 85,174 (CostOfRevenue). My earlier trap call was wrong and is reversed.
- **T FY2025:** the lines are CostOfGoodsAndServicesSold 'Equipment' + OtherCostOfOperatingRevenue (R3 L11-12).
- **TMUS FY2025:** one CostOfGoodsAndServicesSold line.
- **WELL:** 'Property operating expenses' is on CostOfGoodsAndServicesSold.
- **ETN FY2025:** 'Interest expense - net' is on InterestExpenseNonoperating.
- **UBER:** the IS D&A line is DepreciationDepletionAndAmortization; the CF line is the custom tag that includes other income.
- **BA FY2025:** PaymentsOfDividends = 'Dividends paid on Mandatory convertible preferred'.

## Rows changed or added

| Ticker | Change |
|---|---|
| TMUS | cost_of_revenue FY2025 = members sum |
| WELL | cost_of_revenue map (IN-COND) and pretax map with serve_note, per your ruling |
| DHR | cash changed to map |
| T | FY2025 2-line cost of revenue; the 3-line rows are marked older eras |
| ETN | combined keyed to the line; InterestExpenseNonoperating row added |
| BA | CostOfRevenue map; the COGS members excluded; preferred dividends excluded |
| UBER | CF D&A combined; IS D&A map |
| NEE | line 30 included with serve_note, per your ruling |
| SCHW | cash = CF ending cash, per your ruling |
| NEM | interest map (net of capitalized) |
| COF | BS total cash map; CashAndDueFromBanks excluded; DPS not_presented; total_debt perimeter noted |
| BMY | interest_expense from note R72 |
| VRTX | sign-flip era ends at the tag change |
| BKNG | D&A component era ends 2018; dividends from FY2024 |
| MO | cost of sales as printed, per your ruling |
| VLO | opex not_presented, per your ruling |

## What I will apply to ranks 101-400

1. **Combined exceptions:** key them to the printed line.
2. **Dimensions:** check dim_id 0 before calling a tag present.
3. **Bank cash:** use ruling (a).
4. **BA-style costs:** test whether gross profit = Revenues − CostOfRevenue before excluding CostOfRevenue.

I will re-scan ranks 101-400 for these four patterns before starting ranks 401-500.

## Gaps in the reader's evidence

The reader's messages give no accessions for the FY2021 BA and older T and TMUS eras. So these era boundaries are approximate in the file:

- the TMUS members era start;
- the T 2-line era start;
- the WELL era start.
