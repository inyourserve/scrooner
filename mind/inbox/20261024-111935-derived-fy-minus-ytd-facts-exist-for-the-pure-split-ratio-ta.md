---
id: derived-fy-minus-ytd-facts-exist-for-the-pure-split-ratio-ta
title: Derived (FY minus YTD) facts exist for the pure split-ratio tag StockholdersEquityNoteStockSplitConversionRatio1 (values -5, -6, 0, authoritative)
kind: gotcha
tags: derivation, split, allowlist, RF-27
paths: pipeline/src/scrooner_pipeline/normalizer/derived.py
evidence: DATA-INFERRED
source: core.fact TSLA 0000950170-23-001409 (Q4 2021 -5, Q4 2022 -6), ODFL 0001564590-20-037340 (Q2 2020 0.0), read 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
normalizer/derived.py subtracts YTD/FY values of a pure ratio tag. Any split detector reading core.fact must exclude is_derived rows; the additive allowlist (derive.additive_allowlist@1, RF-27) must exclude pure-unit and ratio tags. Population count not measured (full scan timed out at 20s).
