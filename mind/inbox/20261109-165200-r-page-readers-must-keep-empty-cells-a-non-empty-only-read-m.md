---
id: r-page-readers-must-keep-empty-cells-a-non-empty-only-read-m
title: R-page readers must keep empty cells; a non-empty-only read misplaces values into the wrong column
kind: gotcha
tags: verifier, method, rpage
paths: data-team/22-FILING-LESSONS-LEDGER.md
evidence: FILING-CHECKED
source: 0001326801-24-000012 R64
created: 2026-11-09
verified: 2026-11-09
---
META 2023 10-K R64 prints finance lease 690 only under Dec 31 2023 (2022 cell empty); a dump of non-empty cells put it under 2022 (10,613 instead of 10,610). Align cells to headers with blanks kept.
