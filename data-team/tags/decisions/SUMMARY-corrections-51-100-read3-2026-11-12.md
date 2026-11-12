# Summary: third document-first read, corrections applied (Ritwik cloud, 2026-11-12)

For Dhairya. The read covered 17 companies:

> KLAC IBM C AXP MRVL CRM GILD ADI DIS SNDK VZ ABT QCOM PEP COP BLK DE

All 10 disagreements and both rulings are applied to `companies-51-100-exceptions-2026-11-11.csv`. The rules are in the "third document-first read" section of `card-notes-51-100-2026-11-11.md`.

## Changes by company

| Company | Change |
|---|---|
| KLAC | equity = StockholdersEquity; cash = CashAndCashEquivalentsAtCarryingValue, mapped |
| C | CashAndDueFromBanks excluded; cash = CF ending 349,579 (no BS total) |
| AXP | CashAndDueFromBanks excluded; BS total if printed, else CF ending 47,792 |
| MRVL | 'Interest expense' 202.6 mapped |
| QCOM | interest expense 689 mapped; D&A = CF DepreciationDepletionAndAmortization 1,630 |
| CRM | dividends 1,587 and buybacks 12,596 mapped (R9) |
| GILD | cash mapped |
| COP | Revenues excluded through FY2021 ('Total revenues and other income'); mapped from FY2022 ('Sales and other operating revenues'); per filing by the printed line |
| BLK | from FY2025 the amortization line is combined (with impairment) |
| DIS, VZ, DE | cost_of_revenue = sum of the dimensioned printed rows |
| SNDK | AP not_presented, related-party axis only (recorded; outside my concept list) |
| C, CRM, DIS | DPS not_presented (ruling) |
| DE | capex = PP&E + equipment on operating leases (ruling) |
| IBM | capex = PP&E + investment in software (ruling) |

## Caveat

The read covers the latest 10-K only. So the new rows run to 2606, and their era starts are blank or approximate. Older eras keep the earlier rows.

## What the reads show

Three reads have now found 21 disagreements in ranks 51-100, and the filing supported the reader every time. The store-only pass mostly missed these patterns:

1. **Dimensioned face rows:** BA, TMUS, DIS, VZ, DE.
2. **Combined calls keyed to a tag that later moved:** ETN, COP.
3. **Bank cash read from CashAndDueFromBanks:** C, AXP, COF.
4. **Printed lines my label regex missed:** MRVL, QCOM, CRM.

Before ranks 401-500, I'll re-scan ranks 101-400 for these four patterns. Pattern 1 uses fsn.value dim_id and pattern 3 uses the bank list.
