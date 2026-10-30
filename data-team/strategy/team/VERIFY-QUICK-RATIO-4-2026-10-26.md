# Verify: quick_ratio evidence V4 (work/data-engineer/quick-ratio-fix f4d33bf, dry-run), 2026-10-26

Verifier 2. Plan reproduced from quick_ratio_plan_v5.json plus the untouched v2 rows: 8,914 hidden cells at 767 companies, reasons exactly as claimed. Seed random.Random(20261113). Balance sheets read with the verifier kit 4d0dbf6 (`fetch_statements` / `parse_rpage`; 166 requests, nothing on disk). For each cell: face quick = (total current assets - every face inventory line) / total current liabilities in the cell's own column, compared with the stored value. Read-only DB on one connection with a 20s timeout. FILING-CHECKED unless marked.

## Result: GATE FAILS.
- **inventory_presented_not_extracted hides right values:** 18 of 18 readable sampled cells store exactly the face quick ratio. Inventory was already subtracted; the planner hides the cell only because the inventory canonical fact is absent. At risk: the 1,825 cells in this class whose stored value differs from the current ratio. The 146 cells where stored = current are the correct hides.
- **4 more right values hidden:** 3 statement_unavailable cells and 1 unmapped cell whose statements are readable.
- **2 wrong values kept:** materials-type lines that the stays rule misses.

## 1. Named cells
- **Values now stay (V3 false NULLs fixed):** 0001382574 2024-12-31 (0.7975), 0001506929 2014-12-31, 0001058811 2024-04-30 (6.3103).
- **UPS 2023-12-31: stays 1.0453.** Right.
- **0001907982 2020-12-31: stays 2.4746, but no 2020 statement was read.** The planner uses the fallback filing of the AssetsCurrent fact, 10-K/A 0001907982-24-000040. Its balance sheet (R page) shows only 2022-12-31 / 2021-12-31. FSDS lists 2020-12-31 for that filing only because another statement carries the date. This should be inventory_statement_unavailable. The value is not proven wrong, but it is unverified.
- **STE 2019-03-31: relabelled presented_not_extracted, but the stored 1.8175 is right.** (1,053,735 - 208,243) / 465,196 on 0001757898-19-000005. **Correction to my V3 verdict:** "blank is right" for STE was wrong.
- **WMS 2015-03-31: ambiguous.** The stored 0.8533 matches neither the face of 0001193125-16-521419 (0.8952) nor its current ratio (stored current ratio 2.0626 vs face 2.2609). The figures come from a different vintage, so the hide is acceptable pending the original FY2015 10-K.
- **OKE and HL:** materials hides right.
- **0001134765 2012-03-31 and EOG 2008/2009:** no stored quick ratio exists (DATA-INFERRED), so nothing is shown.

## 2. 20 of 1,971 presented_not_extracted: 18 right values hidden, 2 without R pages
Stored = face quick in all 18 readable cells, e.g.:
- 0000742278 2024-06-30: 3.8619 (inventories 113,426)
- 0000007084 2022-12-31: 0.8532
- TXN 2018-12-31: 2.3767 = (8,097 - 2,217) / 2,474. The face also prints the inventory components.
- STE 2024-03-31: 2.3569 and 2019-12-31: 1.7764
- 0000031667 2020-02-29: 0.4357

Rule fix: when the stored quick ratio differs from the current ratio and equals (CA - face inventory) / CL, keep it.

## 3. 15 of 106 statement_unavailable
- **No FilingSummary / R pages (404): 5.** 0001106213 x4 and 0001512922. Unreadable by R page, so hiding is acceptable; FSDS remains possible.
- **Right hides (stored = current ratio; face prints inventory): 7.** E.g. LEVI 2025-03-02 1.4992 vs face quick 0.8924 (0000094845-25-000019); 0000012040, 0001525769 x2, 0001634117 (merchandise and textbook inventories), 0001576942, 0000105418.
- **False hides (the statement IS readable and the stored value is right): 3.**
  - 0001162896 2019-03-31: Inventory row blank, 0.2548.
  - 0001314102 2016-06-30: no inventory line, 5.8832.
  - 0001792044 2020-09-27: no inventory line, 144.4684.

## 4. 10 of 41 materials_supplies_line_present
- 9 OKE cells: the face prints "Materials and supplies", so the hide follows the policy. Right.
- 1 has no R page.

## 5. 20 of 6,796 inventory_like_tag_unmapped
- **Right hides: 16.** The face shows an inventory or supplies line and stored = current ratio. E.g. FCX "Total materials and supplies, net" 1,335; DAL fuel and parts; 0000866787 merchandise inventories 2,531,210 (stored 0.7943 vs face quick 0.0870).
- **False hide: 1.** 0001522540 2023-06-30: no inventory line; stored 4.7553 = face.
- **No page: 3** (2009-2011 filings, or no filing).

## 6. 20 cells that stay (cohort, since 2015, stored = current ratio)
- **Right: 17.** No inventory line on the face; e.g. BBIO 2022-12-31 4.5200, 0001636282 2024-06-30 19.6970.
- **Wrong kept: 2** (materials-type face lines, stored = current ratio):
  - FDX FY2026: "Spare parts, supplies, and fuel" 669; face quick 1.4400 vs stored 1.4754 (0001048911-26-000105).
  - ConEd 2023-06-30: "Fuel oil, gas in storage, materials and supplies" 434; 0.9501 vs 1.0216 (0001047862-23-000140).
  - Each should hide as materials_supplies_line_present.
- **Not parsed: 1.** MAR 2015-12-31: no current subtotals; DATA-INFERRED right.

## Required before apply
1. Keep presented_not_extracted cells whose stored value equals the face quick ratio.
2. Base statement_unavailable on the balance sheet's own columns, not FSDS dates from any statement (0001907982).
3. Hide the stays that show a materials-type line (FDX, ConEd).
4. Re-check the 3 readable statement_unavailable cells and the 1 unmapped cell above.
