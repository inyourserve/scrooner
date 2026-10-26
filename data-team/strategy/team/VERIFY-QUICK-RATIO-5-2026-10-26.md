# Verify: quick_ratio + inventory@2 (work/data-engineer/quick-ratio-fix ff66d63, flag off, dry-run), 2026-10-26

Verifier 2. Plan: scratchpad quick_ratio_plan_v6.json, 6,216 hides at 591 companies, reasons as claimed. Seed random.Random(20261122). Balance sheets read with the kit on main (8b651bc): 213 requests, plus 4 hand reads; nothing on disk. Read-only DB on one connection with a 20s timeout. Face quick = (total current assets - face inventory) / total current liabilities in the cell's own column. FILING-CHECKED unless marked.

## Result: GATE FAILS narrowly.
- **2 right stored values hidden:** company 718332, 2023-12-24 and 2024-03-24 (0001140361-24-005023). The statement IS readable, shows no inventory line, and the stored value equals the face quick ratio (4.1874 / 4.2362). It is hidden as inventory_statement_unavailable.
- **1 wrong value kept:** company 1590364, 2023-12-31, stored 1.9511 (0001590364-24-000003). The balance sheet is unclassified (no current-asset or current-liability subtotal), so no quick ratio can be read from the face. Hide it.
- Everything else sampled is right.

## Results by draw
- **25 of 4,518 inventory_value_under_review: 25 right hides.** Stored = current ratio and the face shows an inventory, supplies or raw-materials line, e.g. company 66004 "Materials and Supplies (at average cost)" 4,826; CIK 0000019745 propane and other inventory.
- **15 of 911 materials_supplies_line_present: 15 right hides.**
  - 10 have stored = current ratio with a materials line on the face, e.g. FDX 2023-08-31 "Spare parts, supplies, and fuel" 631; ED 2022-06-30 "Fuel oil, gas in storage, materials and supplies" 449; CP 2019-09-30 "Materials and supplies" 188; IMO crude-oil inventories + "Materials, supplies and prepaid expenses".
  - 5 store (CA - product inventory) / CL but leave supplies in: OKE x2, HL 2026-06-30 4.9488, CIK 0000703351 0.2924, CIK 0000060714 1.1368. Hiding them under materials precedence is consistent with quick-ratio convention (supplies are not quick assets).
- **15 of 597 inventory_fact_not_authoritative: 15 right hides** (stored = current; face shows inventory).
- **10 statement / presented: 7 right hides, 2 false hides (718332), 1 ambiguous.**
  - EOG 2015-03-31 is a right hide with the wrong reason: the statement IS readable. Face quick = (4,793,368 - 764,206) / 3,094,752 = 1.302 vs stored current ratio 1.549.
  - BNED 2025-10-31: combined blocks; consolidated inventories exist, stored = current. Right hide.
  - 1425450 (ambiguous): its inventory lines sit below the current-liabilities block.
- **13 of the un-hide cells (SWX / OMC, vs V4):**
  - 2 are right keeps (CIK 0001692115, no inventory line).
  - 7 OMC cells kept with stored = current ratio while the face prints "Work in process" (e.g. 1,353.5 at 2018-06-30). This is the OMC contract-asset guard: an agency's billable production costs. Acceptable, but it is a definition call for the standardization lead. If WIP counts as inventory, these 7 are wrong values kept.
  - 4 unreadable: 3 from 2009 with no R pages; 1 € / $ header the kit cannot parse.
  - OMC 2015-2017: no OMC cell in that window is hidden or flagged; same guard.
- **30 cells that stay with stored != current (flag_keep): 29 right, 1 wrong** (1590364, above).
  - 25 equal the face quick ratio directly. 4 more equal it when the face total inventory line is used: CIK 0000764180 0.4679, 3M 1.5452, DINO 0.8147, EnerSys 2.4905 (the R page shows its inventory total as a bare "Total").
- **5 fixtures:** NKE 2026-08-31, BA 2026-06-30, GAP 2026-08-01, AZO 2026-05-09 and XOM 2026-06-30 (holdco CIK 0002115436) are all hidden as under_review. Stored 2.075 / 1.138 / 1.822 / 0.890 / 1.135 = current ratio. The face quick ratios are 1.387 / 0.331 / 1.109 / 0.137 / 0.847 (0000320187-26-000193, 0001628280-26-050038, 0001628280-26-059345, 0001104659-26-073525, 0000034088-26-000093), so hiding is right. The planner does not produce the face value (new = null).

## Required
1. Do not hide statement_unavailable cells whose statement is readable and shows no inventory line (718332). Re-check the 3 statement_unavailable cells.
2. Hide quick ratios of companies with an unclassified balance sheet (1590364).
3. Rule on OMC "Work in process".
