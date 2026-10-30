---
id: quick-ratio-v2-latest-statement-fallback-still-nulls-right-v
title: quick_ratio V2: latest-statement fallback still NULLs right values where our stored current lines fail to foot
kind: lesson
tags: quick_ratio, inventory, false_null, footing
paths: data-team/strategy/team/VERIFY-QUICK-RATIO-2-2026-10-25.md
evidence: FILING-CHECKED
source: BBIO 0000950170-23-017812 R2; SWX 0001692115-21-000040; DVN 0001564590-20-021639; GOOG 0001652044-16-000021; MP 0001801368-20-000009
created: 2026-10-25
verified: 2026-10-25
---
At f96d17c 6 of 7 earlier false NULLs are fixed, but 14 more false NULLs appear in a 35-cell draw (biotechs, SPAC/shell predecessors, royalty and service companies): the face has no inventory line, yet the footing test fails on our stored lines and the latest-statement fallback NULLs the right value. Materials-and-supplies hides fire on manufacturers whose MaterialsSupplies fact is a note component beside a face Inventory line.
