---
id: a-component-sum-with-a-missing-part-serves-a-partial-total-u
title: A component sum with a missing part serves a partial total unless every listed part is required
kind: lesson
evidence: DATA-INFERRED
status: active
created: 2026-11-12
verified: 2026-11-12
---
MSFT sga FY2016-FY2017 was written as G&A alone on 2026-11-12 (FY2016 4,563 vs 19,260): S&M's copies were all is_authoritative=false after the FY2018 10-K restated them (14,697 vs 14,635). Fix: commit 88b46920, a sum needs every part the map lists in era (component_without_authoritative_fact / component_missing_for_period); 47 cells held across 18 companies (MSFT 21, PANW 16, AMAT 7, META 2, AAPL 1). Cause: cross-filing value disagreement (rounding PANW/META; restatement MSFT/AMAT/AAPL) leaves no authoritative copy in core.fact; that is an authority-policy question for the resolver owner, not a mapping fix.
