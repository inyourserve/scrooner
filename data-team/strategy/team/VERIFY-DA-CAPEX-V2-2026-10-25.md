# Verify: D&A and capex member-level gate V2 (origin/work/scrooner-25/slot-records 4752cb5), 2026-10-25

Verifier 2. Cash-flow statement R page of every sampled cell's own accession (185 filings + 2), rows read by element (defref); YTD/FY cells compared with the printed line(s) (sign through the outflow parentheses, scale from the page header); 3-month cells after Q1 compared with (YTD of this filing - YTD of the previous filing). Seed random.Random(20261105) for the draws (one cell per company). FILING-CHECKED.

## Result: GATE FAILS on 2 replay values (ABBV Q4 2020 D&A, KRUS Q3 FY2021 D&A). Production holds many wrong or vintage-shifted values; the replay is right on 115 of the 118 production-different cells.

## 1. The 118 production-different cells (45 D&A, 73 capex)
Replay right on 115, production on the face for only 14.
**Production wrong (replay right):**
| Family | Cells | Example (accession, R page) | Production | Face |
|---|---|---|---|---|
| D&A INTC | 24 | FY2015 0000050863-16-000105 CF: Depreciation 7,821 + Amortization of intangibles 890 = 8,711 | 265M | 8,711M |
| D&A HD | 18 (5 production not on the face) | FY2022 0000354950-23-000059: Depreciation and amortization 2,975 | 2,455M | 2,975M |
| D&A AAPL | 2 | FY2015 0001193125-15-356351: 11,257 | 9,200M | 11,257M |
| D&A GE | 1 | FY2018 0000040545-19-000014: 5,562 + 2,662 = 8,224 (consolidated block) | 8,223M | 8,224M |
| capex GE | 23 | Q1 2015 0000040545-15-000054: Additions to PP&E (3,011) consolidated (GE 1,013, GECC 2,202 below) | 1,496M | 3,011M |
**Production = a later copy (both filed; the replay holds the original filing's value):** META x10 (FY2020 15,115 original vs 15,163 later), GOOG x4, KO x5 (FY2017 1,675 in 0000021344-18-000008 vs 1,750 later; FY2018 1,347 vs 1,548), MRK x5 (FY2019 3,473 vs 3,369), AMZN x4 (9M 2017 7,022 vs 8,336). Vintage policy decides; the original is what the cell's own filing prints.
**Production = rounded later copy (replay more precise, right):** NUE x5 (1,947,897K vs 1,948M), TSLA x10 (3,414,814K vs 3,415M), RPAY x5 (994,147 vs 994,000), AMAT x1 (164 vs 162).
**Perimeter:** AMD FY2025 replay 1,012 = Purchases of property and equipment (974) + "Payments for (Proceeds from) Productive Assets" (38), two printed investing lines (0000002488-26-000018 CF); production 974 is PP&E only. Both defensible; record the perimeter.
Replay not confirmed: INTC Q3 2017 D&A 2,055 (9M 4,990 + 999 = 5,989 confirmed; 6M filing not in the dump), GE capex 1 cell (multi-entity page).

## 2. Random draw, 30 publishable D&A cells
27 right on the face or by YTD difference (e.g. COST 16-week Q4 FY2018 431 = 1,437 - 1,006, 0000909832-18-000013 and -18-000008; CSCO/LRCX quarters by difference).
**Wrong (gate failures):**
- ABBV Q4 2020 (0001551152-21-000008, 0001551152-20-000032): replay 2,088M = derived amortization 1,861 + depreciation 227. Face: FY 666 + 5,805 = 6,471, 9M 439 + 3,967 = 4,406, so Q4 = 2,065 (amortization 1,838). The derived amortization fact used a 9M copy (3,944) that is not the 9M on the Q3 10-Q face. Production is blank, so V2 would publish a new wrong value.
- KRUS Q3 FY2021 (Mar-May 2021, 0001564590-21-036462 and -21-018716): replay 1,200K from a filed 3-month fact rounded to 0.1M; the cash-flow arithmetic is 3,314 - 2,098 = 1,216K. Prefer the precise YTD difference over a rounded narrative quarter value.
Within rounding: ORCL Q3 FY2015 705 vs CF difference 2,144 - 1,440 = 704 (0001193125-15-098586, 0001193125-14-448728): 1M, consistent with per-line rounding.

## 3. Random draw, 30 publishable capex cells
30 of 30 right (signs read through the outflow parentheses; YTD vs quarter lengths matched; no software/intangible line folded into PP&E except where the record lists it, e.g. RPAY PaymentsForSoftware + intangibles + PP&E, as printed).

## Required
1. Derived quarters must take both YTD inputs from the face of their own filings (same vintage); ABBV shows a derived component built from a non-face 9M copy.
2. A rounded narrative quarter fact must not beat the precise YTD difference (KRUS).
3. Production wrong-value classes to retire: INTC D&A (24), HD D&A (18), AAPL D&A (2), GE D&A (1), GE capex (23).
