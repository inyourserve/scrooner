---
id: the-yfinance-sanity-gate-fails-on-regressions-no-71b272
title: The yfinance sanity gate fails on regressions, not absolute counts
kind: gotcha
tags: repo, root
paths: CLAUDE.md
evidence: DOC-CITED
source: CLAUDE.md
created: 2026-10-21
verified: 2026-10-21
---
(founder direction) — it compares against a stored baseline that only updates on a passing run. Don't reintroduce a fixed threshold; make it stricter by working down the backlog and letting the baseline ratchet.
