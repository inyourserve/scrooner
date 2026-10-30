---
id: companyfacts-carries-only-numeric-undimensioned-standard-fac
title: companyfacts carries only numeric, undimensioned, standard facts: dei text flags (AuditorName, DocumentFinStmtErrorCorrectionFlag, IcfrAuditorAttestationFlag), cyd and ecd text never reach core.fact
kind: gotcha
tags: companyfacts, dei, ecd, cyd, coverage
paths: data-team/strategy/team/EDGAR-ATLAS-2026-10-24.md
evidence: FILING-CHECKED
source: MU 10-K 0000723125-26-000023 instance: 1,421 facts (682 dimensional, 137 undimensioned text, 77 custom) vs 519 core.fact rows for filing_id 8791247; core.concept has 5 dei tags only (read-only DB 2026-10-24)
created: 2026-10-24
verified: 2026-10-24
---
For restatement/auditor/ICFR/cyber/10b5-1-arrangement flags read the instance or FSN TXT. ecd pay-versus-performance NUMERIC facts from DEF 14A ARE in companyfacts and already in core.fact unmapped (PeoTotalCompAmt 1,226 active companies, TotalShareholderRtnAmt 1,773).
