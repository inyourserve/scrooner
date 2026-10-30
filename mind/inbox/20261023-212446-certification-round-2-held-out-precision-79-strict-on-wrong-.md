---
id: certification-round-2-held-out-precision-79-strict-on-wrong-
title: Certification round 2 held-out: precision 79% strict on wrong_value flags, recall about 74% (not 96%); suite misses non-integer splits, debt-below-component, flipped tax sign
kind: lesson
tags: certification, validation, held-out
paths: data-team/strategy/team/CERTIFY-HELDOUT-VALIDATION-2026-10-22.md
evidence: FILING-CHECKED
created: 2026-10-23
verified: 2026-10-23
---
S010/S030/S060 + TSLA, seed 20261022, 30 cells per frame, FILING-CHECKED. P flagged 22/28 strict (28/28 under the rule's own policy), P passed 0/30 wrong, K flagged 7/28 wrong value, K passed 0/28. Misses: ODFL 3-for-2 split 2020 invisible (split-ratio list lacks 1.5; FY2015-17 diluted EPS 1.785/1.78/2.815 should be 1.19/1.19/1.88), BAX total debt 2020-06-30 319M vs 6,374M (review flag only), CMG FY2018 income tax flipped sign by a re-tagged comparative. TSLA 2015-2016 quarterly diluted EPS are stored as filed, never split-adjusted (factor 15; e.g. Q1 2015 -1.22 vs -0.081). Derived Q4 tax rates were 7/7 wrong (PGR -40.4% vs 20.6%); derived Q4 EPS 6/11 wrong. Identity rules are false alarms from NCI, excise taxes, REIT layouts. Training recall 96% does not carry over; held-out about 74%.
