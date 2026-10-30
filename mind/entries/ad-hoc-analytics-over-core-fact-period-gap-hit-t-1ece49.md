---
id: ad-hoc-analytics-over-core-fact-period-gap-hit-t-1ece49
title: Ad-hoc analytics over `core.fact`/`period_gap` hit the DB `statement_timeout` (~2 min) and roll back whole multi-statement scripts
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
Run with `set statement_timeout=0`, chunk by company batch, background it. Also: `analytics.company_data_finding`/`period_gap` use `*_resolved` concept ids (`revenue_sanity_resolved`, ...) while `company_concept_lineage` is keyed on the base concept — join via the name with `_resolved`/`_sanity_resolved` stripped, or the join silently returns no lineage rows. Found 2026-10-10: most `data_limit` tickets are mislabeled (e.g. `basic_eps` doesn't map `EarningsPerShareBasicAndDiluted`, which `diluted_eps` does) — verify a ticket's cause against raw tags before trusting its `finding_type`.
