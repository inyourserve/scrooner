---
id: filing-line-evidence-migration-0093-parsers-fili-56fb0b
title: Filing-line evidence (migration 0093, `parsers/filing_line_evidence.py`, `scrooner-map probe-filing-lines`, 2026-10-13)
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
Concept coverage (~86%) divides every concept by all real operating companies, but lines that vary by company (inventory, goodwill, R&D, gross profit, cost of revenue, AR/AP, interest income, opex) are simply not presented by most Financials/REITs. `analytics.company_filing_line_evidence` stores, per company, whether the line is on the face of its latest 10-K/10-Q statements (accession kept); `build-coverage-matrix` turns it into gap reasons (`line_not_presented_in_filing`, `line_presented_combined_with_others` = structural; `line_in_filing_not_extracted` = a real, investigable gap) and `snapshot-coverage` drops the structural ones from that concept's denominator. It is EVIDENCE, not proof (14-34% of values we HAVE show no face line, so wording is "not shown on the statements"); a combined "payable and accrued" line must never be mapped as plain AP; it never changes `has_value`; a no-op until the migration is applied. Nightly step is bounded to 20 min and incremental by accession. Results and method: `doc/learnings/2026-10-13-applicability-probe-why-concept-coverage-is-86pct.md`.
