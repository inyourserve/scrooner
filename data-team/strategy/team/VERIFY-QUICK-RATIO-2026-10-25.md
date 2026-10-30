# Verify: quick_ratio inventory-evidence fix (work/data-engineer/quick-ratio-fix, rule quick_ratio.inventory_evidence@1 at 9296ac7; head 3c42fe1), 2026-10-25

Verifier 2. Plan: `scratchpad/quick_ratio_plan.json` (12,250 would-NULL cells, all stored = current ratio). Cohort = non-excluded rows of `doc/data-moat/team/top1000/shards.csv`: 3,769 plan cells / 221 companies (2,564 since 2015). Reasons there: inventory_like_tag_unmapped 2,320, inventory_presented_not_extracted 1,447, presence_unknown 2. Each cell checked on the balance-sheet R page of the filing whose period_of_report is the cell's date. Our definition (analytics.metric_definition 42): **(Current Assets - Inventory) / Current Liabilities**; inventory maps only `InventoryNet`.

## Result: GATE FAILS. 7 of 20 random would-NULL cells are FALSE NULLs (the stored value is the right quick ratio: no inventory line on that balance sheet). 1 of 10 kept cells is wrong (CP).

## 1. Fixtures (inventory on the face; stored = current ratio = wrong)
| Cell | Accession | Face ($M) | Stored | True (our formula) | Cash + receivables (+ STI) / CL |
|---|---|---|---|---|---|
| NKE 2026-08-31 | 0000320187-26-000193 | CA 23,673; Inventories 7,846; CL 11,409 | 2.075 | **1.387** | 1.193 (6,903 + 1,465 + 5,242) |
| BA 2026-06-30 | 0001628280-26-050038 | CA 124,630; Inventories 88,388; CL 109,563 | 1.138 | **0.331** | 0.303 |
| GAP 2026-08-01 | 0001628280-26-059345 | CA 5,870; Merchandise inventory 2,297; CL 3,221 | 1.822 | **1.109** | 0.772 (no receivables line on the face) |
| AZO 2026-05-09 | 0001104659-26-073525 | CA 8,934,569K; Merchandise inventories 7,559,056K; CL 10,035,313K | 0.890 | **0.137** | 0.101 |
| XOM 2026-06-30 | 0000034088-26-000093 | CA 100,793; Inventories: crude oil, products and merchandise 22,363 + materials and supplies 3,200; CL 88,830 | 1.135 | **0.847** (0.883 if materials and supplies were excluded) | 0.801 |
Lane 3's numbers are right for OUR formula (CA - inventory). The brief's "cash + receivables [+ STI]" is a different (acid-test) definition and gives lower values; do not mix them.

## 2. Would-NULL random sample (seed random.Random(20261029); frame = 2,564 cohort cells since 2015, one per company, sorted by (company_id, period_end))
Right to NULL (inventory line on the face, stored = current ratio = wrong) 13: RL 2022-10-01 Inventories 1,261.4 (0001037038-22-000031); NI 2017-06-30 gas inventory, materials, production fuel lines (0001111711-17-000052; lines present, values not read by my parser); LNT 2015-06-30 production fuel 78.8 + materials 82.3 (0000352541-15-000022); UAL 2015-09-30 aircraft fuel, spare parts and supplies 704 (0001193125-15-350093); WEC 2017-06-30 materials, supplies and inventories 510.0 (0000107815-17-000210); CWST 2017-03-31 Inventory 5,338K (0000911177-17-000033); BA 2017-06-30 42,453 (0000012927-17-000044); DUK 2017-03-31 3,366 (0001326160-17-000109); MKC 2026-05-31 Total inventory 1,408.6 (0000063754-26-000274); EVRG 2020-12-31 fuel inventory and supplies 504.5 (0001711269-21-000023); FCX 2024-09-30 materials and supplies 2,328 (0000831259-24-000039); DDS 2026-08-01 1,283,251K (0000028917-26-000027); EXC 2016-06-30 fossil fuel 462 + materials 1,104 (0001193125-16-676366).

**FALSE NULLs 7** (no inventory line on that balance sheet; stored = CA / CL = the right quick ratio):
| Cell | Accession | Face | Stored | Rule reason |
|---|---|---|---|---|
| INSM 2016-12-31 | 0001047469-17-000856 | cash 162,591 + prepaid 5,816 = CA 168,407K; CL 27,989K | 6.017 | presented_not_extracted (latest statements have inventory; 2016 did not) |
| BBIO 2023-03-31 | 0000950170-23-017812 | CA 552,702K, no inventory; CL 96,596K | 5.722 | presented_not_extracted |
| MELI 2015-06-30 | 0001562762-15-000219 | CA 547,354K, no inventory; CL 345,679K | 1.583 | presented_not_extracted |
| AXSM 2022-03-31 | 0000950170-22-006901 | CA 86,829,926, no inventory; CL 24,549,582 | 3.537 | presented_not_extracted |
| CYTK 2025-09-30 | 0001193125-25-267059 | CA 977,349K, no inventory; CL 142,144K | 6.876 | presented_not_extracted |
| VAL 2018-09-30 | 0000314808-18-000140 | CA 1,382.5 (cash, STI, receivables, other 404.0), no inventory line; CL 535.8 | 2.580 | inventory_like_tag_unmapped (a supplies figure inside "other current assets") |
| WES 2018-06-30 | 0001423902-18-000022 | CA 249,357K, no inventory line; CL 517,163K | 0.482 | inventory_like_tag_unmapped (NGL line-fill inventory sits in noncurrent other assets, per the face footnote) |
Causes: (a) the filing-line evidence describes the LATEST statements and is applied to every period (companies that carried inventory only later: INSM, BBIO, MELI, AXSM, CYTK); (b) an inventory-like fact that is not a current face line (note figure, noncurrent line-fill) triggers inventory_like_tag_unmapped.
Reach (DATA-INFERRED proxy, cohort): 1,366 plan cells are dated before the company's first fact on any of 13 common inventory tags, or the company has none (presented_not_extracted 613 + 111; unmapped 137 + 505); 848 of them since 2015 at 39 companies. These are the likely false NULLs; the proxy does not see custom inventory tags.

## 3. Kept cells (not in the would-NULL set; zero inventory used; seed continued, one per company; frame 8,027 cohort cells since 2015 at 235 companies)
Right 9 (no inventory line; stored = CA/CL): TWLO 2018-12-31 (0001047469-19-000807), AON 2026-03-31 (0001628280-26-029322), EQT 2015-09-30 (0000033213-15-000014), GLXY 2026-06-30 (0001859392-26-000091), SNAP 2017-12-31 (0001564590-18-002721), CHRW 2020-06-30 (0001043277-20-000036), MOH 2025-12-31 (0001179929-26-000005), OVV 2025-06-30 (0000950170-25-098401), IQV 2021-06-30 (0001478242-21-000050).
**Wrong 1**: CP 2017-03-31 (0000016875-17-000029): face "Materials and supplies 201" (CAD) is the inventory line; stored 0.941 = 1,110 / 1,179 = current ratio; true (1,110 - 201) / 1,179 = 0.771. The evidence row says line_present = false; `_EXCLUDED` contains "Other", so OtherInventorySupplies-type tags never count as inventory-like. Utilities with the same line (LNT, WEC) are NULLed while CP is kept.

## Required before `on:`
1. Apply line evidence per filing / per period (that period's statement), not the latest statement to all history.
2. An inventory-like fact counts only if it is a CURRENT face line on that balance sheet (statement role + position), not a note or noncurrent figure.
3. Standardization Lead decides whether materials and supplies are inventory; apply it consistently (XOM expectation yes, LNT/WEC NULLed, CP kept at zero today).
4. Better than NULL: map the inventory face lines (only `InventoryNet` is mapped), so most of the 2,320 + 1,447 cells get a true value instead of a blank.
Not tested: pre-2015 cells, the 2 presence_unknown cells, TTM rows, non-cohort companies.
