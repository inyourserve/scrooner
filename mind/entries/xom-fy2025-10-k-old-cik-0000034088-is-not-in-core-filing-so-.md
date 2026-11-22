---
id: xom-fy2025-10-k-old-cik-0000034088-is-not-in-core-filing-so-
title: XOM FY2025 10-K (old CIK 0000034088) is not in core.filing, so XOM (company 5351, CIK 2115436) serves no FY2025 duration cells
kind: gotcha
tags: xom, cik-change, holding-company, coverage
evidence: DATA-INFERRED
status: active
source: core.filing has no 0000034088-26-000045; canonical_fact company 5351 FY 2025-12-31 holds only 18 balance-sheet rows from later 10-Q comparatives (query 2026-11-12); filing R4/R7/R94/R109 print the values
created: 2026-11-12
verified: 2026-11-12
---
The ExxonMobil holding-company reorganisation moved new filings to CIK 2115436, but the FY2025 10-K was filed under the old CIK 34088, which has no core.company row. Every FY2025 income statement, cash flow and note value for XOM is blank with no reason (comprehensive income 32,600M, cash interest paid 1,752M, R&D 1.2bn, AR change (3,042)M). Fix: load the old-CIK filings into the successor company before judging XOM coverage.
