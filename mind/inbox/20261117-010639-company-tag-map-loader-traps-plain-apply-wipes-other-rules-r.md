---
id: company-tag-map-loader-traps-plain-apply-wipes-other-rules-r
title: company_tag_map loader traps: plain --apply wipes other rules' rows; era-overlap check misses period-end vs month-end duplicates; per-FY rows with no open-ended row get skipped by the tagmap-plan concept gate
kind: gotcha
tags: company_tag_map, seeder, only-rule, era, tagmap-plan, loader
paths: pipeline/src/scrooner_pipeline/mapper/company_tag_map_seed.py, pipeline/scripts/tag_library/superseded_check.py
evidence: CODE-CHECKED
created: 2026-11-17
verified: 2026-11-17
---
(1) seed-company-tag-map --apply replaces ALL of a company's rows. Use --only-rule family.rule@N to replace only one rule's rows. That mode drops a tagless row a live row of another rule already decides (superseded_by_live). superseded_check.py (branch work/ritwik/superseded-check) lists, read-only, which rows load or are superseded, with every clashing live row. (2) The overlap check compares era dates exactly. A row dated by the actual period end (AAPL 2025-09-27) and one by the month end (2025-09-30) for the same FY don't overlap, so the cell gets two reasons. Date status eras by the FSN month-end period. (3) MSFT 2026-11-14: the per-FY fix rows loaded, but no row was open-ended after FY2026. tagmap-plan's concept gate then skipped the concept ('era short from 2026-09-30'), so the cells were never rewritten and the old not_in_template blanks stood. Verify the live cell_blank_reason after any tag-map load, not just the load count. A carried-forward decision is a loader mechanism only; a later period's reason must cite its own filing or stay UNCHECKED.
