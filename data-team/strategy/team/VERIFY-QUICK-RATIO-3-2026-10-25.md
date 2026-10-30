# Verify: quick_ratio evidence V3 (work/data-engineer/quick-ratio-fix 3b5d079, dry-run), 2026-10-25

Verifier 2. Decisions reproduced from the dry-run artifacts (`qr_p1.json` fallback cells + `qr_face.jsonl` FSDS face decisions: 1,866 zero-stands, 301 NULL, 12 kept-unverified, exactly as claimed) and the branch planner run read-only for the fixtures and materials companies. Seed random.Random(20261106), one cell per company. Each drawn cell checked on the balance sheet of its own accession. FILING-CHECKED.

## Result: GATE FAILS. 6 right stored values are still NULLed or hidden (4 because the face test looks for an inventory line in ANY column, not the cell's column; 1 because the face used is a different period's filing; 1 materials hide with no face line). The 14 earlier false NULLs are fixed.

## 1. Named cells
All 14 earlier false NULLs now keep their value (zero stands): BBIO 2023-03-31 and 2024-03-31, SWX 2021-06-30, TGTX, IOVA, IBRX, DVN 2020-03-31, QXO 2018-03-31, GOOG 2016-03-31, T 2015-06-30, MP 2020-09-30, RGLD 2015-09-30, ASTS 2023-09-30, VTRS 2020-09-27; INSM 2016-12-31 kept. CP 2017-03-31 and the 5 fixtures (NKE, BA, GAP, AZO, XOM) are NULL: right.

## 2. 20 of the 301 NULLs where the face decided "inventory line present"
Right 15 (inventory in the cell's own column): e.g. AVT 2016-07-02 2,856,231K; SNX 2020-11-30; ARMK 2023-09-29; EOG 2012-06-30; MTDR 2013-03-31 "lease and well equipment inventory" 966K; CIK 1829794 2025-03-31 "inventory and inventory deposits".
**False NULLs 4** - the inventory line exists only in the COMPARATIVE column; the cell's column is blank or zero:
| CIK | Cell | Accession | Face |
|---|---|---|---|
| 0001382574 | 2024-12-31 | 0001641172-25-000657 | "Inventory | (blank) | 968" (only Dec 2023) |
| 0001506929 | 2014-12-31 | 0001557240-15-000080 | Inventories blank at Dec 31 2014, 64,204 at Jun 30 2014 |
| 0001134765 | 2012-03-31 | 0001415889-12-000706 | Inventory blank at Mar 31 2012, 1,853 at Dec 31 2011 |
| 0001058811 | 2024-04-30 | 0001213900-24-109054 | Merchandise inventories 0 and textbook rental inventories 0 at Apr 30 2024 (values only at Oct 31 2024) |
**Wrong evidence 1**: CIK 0001907982 2020-12-31 was decided from 0001907982-24-000040, whose balance sheet shows Dec 2022 / Dec 2021 only; the 2020 statement was not read.
Rule fix: the face decision must read the cell's own date column (FSDS `num` for that ddate, or the R-page column), not "the statement has an inventory row".

## 3. The 12 kept-unverified cells
10 statements are readable and show no inventory line in the cell's column (e.g. TGTX 2013-03-31, SWX 2019-12-31, IOVA 2011-09-30, CIK 1162896 2019-03-31 "Inventory" row blank): kept values right. EOG 2008-12-31 and 2009-06-30 (0000821189-09-000047): no R pages, statement NOT read. EOG's later balance sheets (e.g. 2012-06-30) print an inventories line, so these kept values are probably current ratios (DATA-INFERRED, not filing-checked; pre-2015, outside the display window). They should be hidden as kept_unverified:face_unavailable, not shown.

## 4. 30 of the 1,866 zero-stands cells
30 of 30 right: none of the 30 balance sheets shows an inventory or supplies line in the current-assets section (shells, biotechs, service companies, T 2013, SNPS 2017, DVN 2016).

## 5. Materials-and-supplies hides (5 drawn; cohort since 2015 has 5 companies)
Right 2: OKE 2022-09-30 "Materials and supplies" 155,158K and HL 2026-06-30 materials and supplies 59,907K (both current face lines).
Mislabelled 2: STE 2019-03-31 and WMS 2015-03-31 print "Inventories" (no materials line): blank is right, reason should be inventory_presented_not_extracted.
**False hide 1**: UPS 2023-12-31 (0001090727-24-000008) shows no inventory or materials line on the face (materials sit inside other current assets), so the stored 1.0453 is the face quick ratio.

## What the 1,165 "inventory-named supplies sub-line" hides are
In my earlier draw (SWKS, EW, ENTG, NXPI, PWR, STE, WTS, ECHO, FLEX, ST) every one prints a face "Inventory/Inventories" line, and the MaterialsSupplies-named fact is a component of that inventory in the inventory note (raw materials and supplies). Blanking is right because the stored value is the current ratio; the cause is our missing inventory value, not a materials line.
