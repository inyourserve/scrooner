---
id: split-re-base-at-cohort-scale-filer-units-errors-and-exchang
title: Split re-base at cohort scale: filer units errors and exchange ratios, not splits, drive most false values
kind: lesson
tags: split, per-share, shares, units, cohort
paths: pipeline/src/scrooner_pipeline/corporate_actions/share_basis.py
evidence: DATA-INFERRED
source: branch work/period-engineer/split-rebase d7fdefd; data-team/strategy/team/SPLIT-REBASE-COHORT-DRYRUN-2026-10-24.md
created: 2026-10-24
verified: 2026-10-24
---
1,000-company dry-run: 237 confirmed splits at 174 companies, 73 missing from analytics.company_stock_split; 55 table rows are not splits (pre-IPO splits before any held filing, or exchange ratios CFG 165.582, JXN 104.96, WMG 47.72 that the old adjuster divides history by). Guards that mattered: one nearest event per ratio disclosure (WAB/CGNX re-disclosures, TTD files 10:1 as 0.1); restated share counts as share evidence when class-dimensioned covers leave no series (MA, CSX, CME); invariant only on the company's own event ratios (CRM restatement looked like 3x); latest-filed copy can be a units error (PCG shares x10^6 vs its own cover; VICI DPS 262,500; DLTR 123.5): check against the same filing's cover/WASO, then 50x off the company's own median; label shift before 'restated' (AMZN FY2012 10-K, NVDA FY2018 10-K). Mixed DPS tags (declared vs paid) are common: hiding whole series costs 25.6k cells vs 9.7k off-basis only.
