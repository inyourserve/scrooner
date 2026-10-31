# Verify: quick_ratio plan v7 (origin/work/per-share/quick-ratio-v6 5a948cd), 2026-11-01

Seed 20261101. Files: fsn-notes/derived/per-share/2026-10-31/quick_ratio_plan_v7.json.gz (sha256 401aee96... verified) and qr_face_v7.jsonl.gz (03e67075... verified). Claimed: 2,772 hides at 177 companies. Evidence class: FILING-CHECKED (balance-sheet R page of each hide's accession). Production formula: (current_assets - inventory) / current_liabilities (expanded_definitions.py). Verifier 2 (scrooner-bc).

## Result
**Ready for apply review: YES.** 25 of 25 readable hides are right (production's ratio is wrong or unproven); 2 unreadable.
- under_review: 10 of 10. Every face prints an inventory line, and production's ratio equals the current ratio (inventory taken as zero, the B7 bug).
- materials: 10 of 10 (all ratios differ from the current ratio). Production subtracts product inventory but leaves "materials and supplies" or "restaurant supplies" in quick assets. Quick assets exclude all inventories, so production overstates the ratio; hiding until materials are subtracted is right.
- unclassified: 5 of 7 confirmed. The face prints no current-asset and/or current-liability total, so production's ratio is not from printed totals. 2 not gradable (pages unparsed or period not on the page).

## Sample
All 7 `balance_sheet_unclassified`; `random.Random(20261101)`: 10 of 78 materials hides that differ from the current ratio, then 10 of 1,948 `inventory_value_under_review`.

## Cell table
| Class | Company (CIK) | Period | Face | Production | Verdict |
|---|---|---|---|---|---|
| uncl | GE (40545) | FY2019 | Inventories 14,104; no total current assets (unclassified, multi-column) | 1.3072 = current ratio | hide right |
| uncl | 922621 | FY2014 | no current subtotals printed | 1.3326 = current | hide right |
| uncl | FTAI (1590364) | FY2023 | Inventory 316,637; no current subtotals | 1.9511 | hide right |
| uncl | 1707925 | FY2017 | page parsed no columns | 0.8077 | not graded |
| uncl | 2080126 | 2025-06-30 | that column not on the claimed 10-Q page | 1.1630 | not graded |
| uncl | 2080126 | 2025-12-31 | no current subtotals | 1.2022 | hide right |
| uncl | 1326110 | FY2014 | Total current assets 59,373; no current-liabilities total | 31.51 = current | hide right |
| mat | 703351 (Brinker) | Q2 FY2019 | CA 196.0; Inventories 24.0; Restaurant supplies 46.8; CL 488.0 | 0.3525 = (196-24)/488 | hide right (0.2566 with supplies) |
| mat | 703351 | Q1 FY2020 | 173.7; 25.6; 51.8; 516.4 | 0.2868 | hide right |
| mat | OKE (1039684) | Q3 2017 | CA 1,518,865; Materials and supplies 77,366; CL 2,741,080 | 0.4395 | hide right (materials not subtracted) |
| mat | 703351 | Q1 FY2018 | 140,876; 24,202; 46,516; 414,362 | 0.2816 | hide right |
| mat | 703351 | Q2 FY2017 | 224,268; 25,784; 45,972; 469,804 | 0.4225 | hide right |
| mat | 703351 | Q3 FY2017 | 148,196; 26,317; 46,328; 437,267 | 0.2787 | hide right |
| mat | 703351 | Q3 FY2023 | 213.4; 34.1; 55.7; 585.7 | 0.3061 | hide right |
| mat | 703351 | Q2 FY2025 | 210.7; 36.7; 53.5; 644.3 | 0.2701 | hide right |
| mat | 719413 | Q2 2026 | CA 771,971; product inventories 36,832; materials and supplies 59,907; CL 148,549 | 4.9488 = (771,971-36,832)/148,549 | hide right (4.5455 with materials) |
| mat | 703351 | Q3 FY2020 | 315.3; 26.3; 51.2; 520.0 | 0.5558 | hide right |
| rev | GME (39911) | FY2025 | CA 5,777; merchandise inventory 2,207; CL 3,300 | 1.7506 = current | hide right (1.0818) |
| rev | 783325 | Q1 2021 | CA 2,355.5; materials, supplies and inventories 353.5; CL 3,714.9 | 0.6341 = current | hide right |
| rev | 911177 | Q1 2023 | 187,828; inventory 14,175; 145,122 | 1.2943 = current | hide right |
| rev | 1164727 | Q2 2022 | 6,907; inventories 922; 2,451 | 2.8180 = current | hide right |
| rev | 1164727 | Q2 2026 | 13,306; 1,478; 5,226 | 2.5461 = current | hide right |
| rev | 1164727 | Q3 2024 | 12,577; 1,487; 6,408 | 1.9627 = current | hide right |
| rev | 831259 | Q2 2015 | 8,697; materials and supplies 2,014; 4,739 | 1.8352 = current | hide right |
| rev | DAL (27904) | Q2 2024 | 11,588; fuel, expendable parts and supplies 1,486; 28,759 | 0.4029 = current | hide right |
| rev | GME (39911) | Q1 FY2023 | 4,283; 2,299; 2,918 | 1.4678 = current | hide right |
| rev | 1403568 | FY2017 | 1,693,743; merchandise inventories 1,096,424; 642,166 | 2.6375 = current | hide right |

## Withheld cells (avoidable holds)
None found: every graded hide has an inventory-type line or an unclassified balance sheet.

## False holds
None.

## Findings for the builder
1. The plan is right to hide. To publish later, quick assets must exclude every inventory-type current line (inventories, materials and supplies, restaurant supplies, fuel and expendable parts), not only the `inventory` concept.
2. The `under_review` class can move straight to a corrected value wherever the face prints one inventory line plus both subtotals (all 10 sampled do).
3. Unclassified balance sheets (GE 2019, FTAI 2023) have no quick ratio from printed totals; keep them as a stated-reason blank.

## Requests and disk
SEC requests: 54. Bucket reads: 2 objects (hash-checked). No DB access.

## Untested scope
68 `inventory_presented_not_extracted` and 189 `inventory_fact_not_authoritative` hides not sampled; 1,938 under_review and 550 materials hides not drawn.
