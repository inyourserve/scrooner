---
id: cross-vintage-arithmetic-is-wrong-only-when-no-single-filing
title: Cross-vintage arithmetic is wrong only when no single filing reproduces the stored value
kind: gotcha
tags: certification, vintage, bmy, alle, spgi
paths: pipeline/src/scrooner_pipeline/certification/source_integrity.py
evidence: DATA-INFERRED
source: certify round 3 vs data-team/36 verdicts
created: 2026-10-23
verified: 2026-10-23
---
BMY gross profit 6M 2017 (revenue from the 2017 10-Q, cost of sales from the 2018 recast 10-Q) is wrong; ALLE FY2017 gross profit and SPGI opex Q1 2024 (also two filings 200+ days apart, inputs restated since) are right. Separator: for a two-input cell, rebuild the value from every filing that holds BOTH inputs at its own values; wrong_value only if one exists and none reproduces the stored number (gap 0.1%-5%). No complete filing = not provable = silent. A "restated input" test alone is not enough: it fired 112 times on the held-out frame, mostly on right cells. Still unverified: SPGI gross profit (36 cells), TXT, MPC.
