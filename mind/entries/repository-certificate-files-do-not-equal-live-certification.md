---
id: repository-certificate-files-do-not-equal-live-certification
title: Repository certificate files do not equal live certification state
kind: gotcha
tags: certification, production, audit
paths: data-team/strategy/approvals/registry.csv, pipeline/db/migrations/0114_cell_proof.sql
evidence: CODE-CHECKED
status: active
source: Independent live audit 2026-11-21
created: 2026-11-21
verified: 2026-11-21
---
On 2026-11-21 the repository registry carried GILD and JNJ PASS verdicts, while live analytics.company_certification had zero rows. Report evidence-certified files separately from production certification state until an explicit synchronized writer and reconciliation check exist.
