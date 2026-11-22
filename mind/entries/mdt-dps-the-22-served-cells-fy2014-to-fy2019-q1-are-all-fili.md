---
id: mdt-dps-the-22-served-cells-fy2014-to-fy2019-q1-are-all-fili
title: MDT DPS: the 22 served cells (FY2014 to FY2019 Q1) are all filing-right; no served DPS after 2018-07-27 although FSN holds Declared values to 2026-07
kind: lesson
tags: dps, mdt, q4, share-basis, coverage
evidence: FILING-CHECKED
status: active
source: Verifier check 2026-11-10 of run 42649721096 cells
created: 2026-11-10
verified: 2026-11-10
---
Medtronic (3639) prints declared DPS on the income statement (R2) of every 10-Q and 10-K, and the 10-K Item 5 says 'X cents per share for each quarter', so Q4 can be checked directly. Q4 = FY - 9M on CommonStockDividendsPerShareDeclared is on one basis (1:1 Inc-to-plc conversion 2015-01-26, no split). All 22 served cells match the filings. Gap (DATA-INFERRED): canonical_fact has no MDT dividends_per_share_resolved row after 2018-07-27, though fsn.value has 125 Declared facts with ddate up to 2026-07-31. The cause is not investigated.
