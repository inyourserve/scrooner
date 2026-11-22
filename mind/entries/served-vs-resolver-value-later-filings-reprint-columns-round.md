---
id: served-vs-resolver-value-later-filings-reprint-columns-round
title: Served vs resolver value: later filings reprint columns rounded to millions; compare at the coarser scale
kind: gotcha
tags: resolver, serving, rounding, authority-v2
paths: pipeline/src/scrooner_pipeline/mapper/structural_direct.py, pipeline/scripts/resolver_served_census.py
evidence: DATA-INFERRED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Census 2026-11-21 over 96 template companies: 646 served cells differ from the structural resolver's value for the same key. 307 of them agree once you allow rounding (a later 10-K reprints the column in millions with one decimal, e.g. MRVL sbc 241,500,000 vs 241,539,000). 256 are restated or recast columns from a strictly later filing (authority v2 keeps them). 83 are wrong or stale and are held by structural_direct.enforce_resolver (sha 51972357). Use structural_direct.agrees() and shape(), not ==, to compare values across filings.
