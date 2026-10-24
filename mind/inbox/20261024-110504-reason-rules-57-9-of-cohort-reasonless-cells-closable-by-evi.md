---
id: reason-rules-57-9-of-cohort-reasonless-cells-closable-by-evi
title: Reason rules: 57.9% of cohort reasonless cells closable by evidence, all pending audit (2026-10-24)
kind: lesson
tags: reason, blank, top1000, coverage
paths: pipeline/src/scrooner_pipeline/reasons/rules.py, data-team/strategy/reason-rules/dryrun-2026-10-24/dry_run_output.txt
evidence: DATA-INFERRED
created: 2026-10-24
verified: 2026-10-24
---
Dry-run over the 2026-10-20 baseline (13,349 reasonless cells, cohort v1 986): template.membership@1 3,749 (NIT rows of the draft template, group assignment with evidence accession), reason.twin_inherit@1 1,733 (F-1 base rows), reason.passthrough@1 1,340 (metric inherits a classified required input; never an unclassified one), evidence.evidenced_zero@1 624 (no dividend/buyback/interest/capex signal tag among all tags ever filed), evidence.not_presented_tag_absent@1 278 (cash-flow change lines), evidence.not_presented@1 (migration 0093) 0: the 15 reasonless cells on its data points all have line_present=NULL (statement not located). 7,724 closed, 5,625 residue. Every closure is evidence_pending (groups and detectors unaudited), none counts as covered. Gotcha: tag-name absence is NOT evidence for dimension-only disclosures (LLY/REGN/VRTX/ALNY/BMY collaboration revenue has no Collaborat tag in company_sec_tag), so collaborative_arrangement_revenue was dropped as a family.
