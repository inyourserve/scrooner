---
id: shared-table-writes-must-be-scoped-to-every-dime-f8c740
title: Shared-table writes must be scoped to every dimension another writer keys on, not just the primary foreign key
kind: gotcha
tags: pipeline
paths: pipeline/CLAUDE.md
evidence: DOC-CITED
source: pipeline/CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
This exact bug (two writers into the same table/concept, one writer's delete silently wiping the other's rows) recurred at least 5 times across this project (`metric_value`'s `roic`/`roe` vs `period_label='TTM'`, `expanded_metrics.py`'s delete-scope bug, `concept_fallback.py` vs `parsers/main_parser.py`, institutional/mutual-fund ownership windows, revenue resolvers). Check this explicitly before adding any new write path to a shared table.
