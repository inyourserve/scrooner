---
id: balance-sheet-identity-fallback-adds-nci-instead-of-subtract
title: Balance-sheet identity fallback adds NCI instead of subtracting (concept_fallback.py)
kind: lesson
tags: derive, identity, nci, total_liabilities
paths: pipeline/src/scrooner_pipeline/mapper/concept_fallback.py
evidence: FILING-CHECKED
source: WMT 0000104169-26-000154 R4; T 0000732717-26-000297 R5; ledger 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
resolve_balance_sheet_identity_fallback computes assets - equity + adj (docstring says minus). Correct: L = LiabilitiesAndStockholdersEquity - total equity incl NCI - temporary equity. WMT stored 202,237M vs 189,115M; T 319,920M vs 299,920M. 5,252 cohort cells since 2015 carry a nonzero adj (DATA-INFERRED).
