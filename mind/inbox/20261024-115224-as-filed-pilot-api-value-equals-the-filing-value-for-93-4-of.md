---
id: as-filed-pilot-api-value-equals-the-filing-value-for-93-4-of
title: As-filed pilot: API value equals the filing value for 93.4% of face facts, 0 non-custom face facts missing; custom tags are the gap
kind: lesson
tags: as-filed, companyfacts, hybrid
paths: data-team/strategy/team/AS-FILED-PILOT-2026-10-24.md
evidence: DATA-INFERRED
source: data engineer as-filed pilot 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
10 cohort companies, 461 10-K/10-Q since 2015: 98,711 face facts, 92,215 exact vs core.fact, 0 non-custom absent, 6,310 custom extension facts absent by design, 185 par-value diffs are FSDS truncation. Face route reproduces only 48% of stored us-gaap facts (rest are notes). Hybrid (calc-linkbase slot + API value) fixes 13 of 16 known debt/revenue/EPS cells; filing-only 10; both fail the 2 split-basis EPS cells. Weak spot of the hybrid is custom tags (TSLA 2,634K).
