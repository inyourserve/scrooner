---
id: two-top-1000-cohort-files-differ-shards-csv-986-non-excluded
title: Two top-1000 cohort files differ: shards.csv (986 non-excluded) vs cohort_v1_1_proposal (1,000, no sic column); 980 shared
kind: gotcha
tags: cohort, top1000, sector-templates
paths: doc/data-moat/team/top1000/shards.csv, data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv, pipeline/src/scrooner_pipeline/mapper/sector_templates.py
evidence: CODE-CHECKED
created: 2026-11-01
verified: 2026-11-01
---
Checked 2026-11-01 by set comparison on company_id. shards.csv (FSN tooling, scrooner-fsn _cohort) has 986 rows with excluded empty and carries sic; ARCC, CBC and BXSL have no sic there. cohort_v1_1_proposal_2026-10-24.csv (used by the Sector Analyst's SECTOR-TEMPLATES proposal) has 1,000 rows and no sic column. 980 are shared, 20 only in v1.1 and 6 only in shards. Say which cohort a count is on before comparing numbers. seed-sector-templates takes either file via --cohort and reads core.company.sic_code when the sic column is missing.
