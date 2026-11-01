---
id: duplicate-core-period-rows-banks-dominate-only-via-empty-ins
title: Duplicate core.period rows: banks dominate only via EMPTY instant rows with event dates; real double columns are duration pairs with facts on both sides
kind: gotcha
tags: periods, duplicates, banks, instants, company-page
paths: apps/app/lib/company/db.ts, pipeline/src/scrooner_pipeline/normalizer/periods.py
evidence: DATA-INFERRED
status: active
created: 2026-10-31
verified: 2026-10-31
---
Sizing the double-period defect (same company/FY/period/type, ends and lengths within 7 days) across the top-1000 on 2026-10-31 gave 11,095 pairs at 922 companies, with C 617, JPM 599, GS 533, MS 510 on top. Those bank pairs are instant periods labeled Q1-Q3 with mid-quarter dates (C 2026-05-14/05-13/05-11/05-08; JPM 04-17/04-14/04-10) and ZERO facts on both rows: debt-tranche and cover dates that received a fiscal label. Any rule about duplicate columns must first drop period rows without facts and treat instants separately. The statement-affecting shape is a duration pair where one row carries the statement (RBC Q2 FY26 06-29..09-27, 77 facts) and the other a stray context (07-01..09-27, 1 fact) or a recast (MSFT Q1 FY17 revenue 20,453 on 07-01 vs 21,928 on 07-02, the ASC 606 recast). Shown cells with values on both rows: revenue 204 pairs (33 differ), net income 241 (53), operating income 159 (28), diluted EPS 202 (47). apps/app getStatement keys columns by (fiscal_year, fiscal_period, end_date): ends 1-7 days apart render as two same-label columns; same end with different start collapses to one with an arbitrary winner.
