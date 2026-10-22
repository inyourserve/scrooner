---
id: composite-concepts-need-slot-level-perimeter-records-not-tag
title: Composite concepts need slot-level perimeter records, not tag lists (D&A, capex, debt, interest)
kind: lesson
tags: standardization, perimeter, d&a, capex, total_debt, finance_lease, interest
paths: data-team/strategy/team/R3-standardization-model.md, pipeline/src/scrooner_pipeline/mapper/concept_fallback.py, pipeline/src/scrooner_pipeline/mapper/definitions.py
evidence: FILING-CHECKED
status: active
source: R3 standardization model 2026-10-21
created: 2026-10-21
verified: 2026-10-21
---
FASB 2025 calc: LongTermDebtAndCapitalLeaseObligations = LongTermDebtNoncurrent + FinanceLeaseLiabilityNoncurrent and DebtCurrent includes current finance leases, yet compute_total_debt treats them as alternates (lease perimeter depends on tag choice). fcf/fcf_yield read raw capex while statements show capex_resolved (+software). D&A max-of-two-tags misses composed D&A (AMD 0000002488-25-000166 R6: 556 OtherD&A + 1,697 intangibles). Aptiv capex on PaymentsToAcquireProductiveAssets. FSDS 2025q4: D&A face lines not matched by our tags in 1,202 of 4,262 non-fin filings; capex 676 + 577 of 3,846. Model: versioned definitions of slots, per company-period perimeter record, reported vs standardized value; screens use complete standardized only.
