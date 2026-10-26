---
id: never-infer-a-value-s-rounding-unit-from-trailing-zeros-use-
title: Never infer a value's rounding unit from trailing zeros; use XBRL decimals or printed precision
kind: gotcha
tags: rounding, decimals, derived_quarter, net_income
paths: data-team/strategy/team/VERIFY-RETIREMENT-B10-2026-10-26.md
evidence: FILING-CHECKED
source: AKTX 0001493152-25-022390; CACC 0000885550-25-000124; GIS 0001193125-24-072690
created: 2026-10-26
verified: 2026-10-26
---
B10 rounds mixed-unit Q4s to the coarsest input scale detected by trailing zeros. 96.0M (CACC), 4,274.0M (MCD), 1,979.0M (GIS) and 12,000K (AKTX) look round but are printed at 0.1M / 1K, so Q4s were over-rounded (151.9 -> 152; AKTX -5.298M -> -5M, wrong). Take the unit from the fact's decimals attribute or the face.
