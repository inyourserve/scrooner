---
id: a-split-is-proven-by-restated-per-share-comparatives-not-by-
title: A split is proven by restated per-share comparatives, not by a step in cover share counts
kind: rule
tags: certification, split, odfl, nem
paths: pipeline/src/scrooner_pipeline/certification/splits.py
evidence: DATA-INFERRED
source: certify round 3, held-out S010/S030/S060
created: 2026-10-23
verified: 2026-10-23
---
Cover share counts step 1.25-1.5x on acquisitions and offerings (NEM/Newcrest 2024, DOC/HCP, MPC/Andeavor), so a non-integer step is only an inferred split when a per-share cell lists the SAME period's EPS from two filings with older/newer = the same ratio within ~7 months (ODFL 3-for-2, Mar 2020: 1.64 in the 2019 10-Q, 1.09 in the 2020 comparative). Integer steps (2x+) are still inferred from the filing-dated share series alone (GGG 3:1, MPC 2:1 2015, NVDA 10:1 2024). Expected factor of any per-share or share cell = product of split ratios dated after its newest source filing date. Copies of the same fact live in other filings (core.fact), not only in the cell's source_fact_ids: load them (pershare_copies).
