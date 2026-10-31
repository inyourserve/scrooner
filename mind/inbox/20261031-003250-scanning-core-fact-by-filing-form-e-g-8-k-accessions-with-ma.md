---
id: scanning-core-fact-by-filing-form-e-g-8-k-accessions-with-ma
title: Scanning core.fact by filing form (e.g. 8-K accessions with many authoritative facts) times out even in 300-company chunks; use per-company planners (w3_population_dryrun.py section C) instead
kind: gotcha
tags: performance, statement_timeout, 8-K, scan
paths: pipeline/scripts/w3_population_dryrun.py
evidence: DATA-INFERRED
source: scrooner-0f 2026-10-30
created: 2026-10-31
verified: 2026-10-31
---
A join core.filing (form in 8-K) -> core.fact (is_authoritative, not is_derived) grouped by accession cancelled at 110-150s statement_timeout for the whole population and for 300-company chunks (company_id between). The per-company loader in normalizer/dedupe._load_fact_rows plus plan_authority, as driven by scripts/w3_population_dryrun.py (--ciks, --chunk 20), answers the same question (8-K copies that won conflict fills, 8-K singletons that would go blank) within budget on one read-only connection. Scope scans to the cohort CIK list (data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv column 2).
