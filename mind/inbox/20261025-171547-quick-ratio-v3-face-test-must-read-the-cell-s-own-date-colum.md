---
id: quick-ratio-v3-face-test-must-read-the-cell-s-own-date-colum
title: quick_ratio V3: face test must read the cell's own date column; comparative-column inventory caused false NULLs
kind: lesson
tags: quick_ratio, inventory, face_column, false_null
paths: data-team/strategy/team/VERIFY-QUICK-RATIO-3-2026-10-25.md
evidence: FILING-CHECKED
source: 0001641172-25-000657; 0001557240-15-000080; 0001415889-12-000706; 0001213900-24-109054; UPS 0001090727-24-000008
created: 2026-10-25
verified: 2026-10-25
---
The V3 face fallback fixed the 14 earlier false NULLs but decides 'inventory line present' per statement, so a line filled only in the comparative column (blank or 0 in the cell's column) NULLs a right value (4 of 20 sampled). UPS 2023 materials-hide has no face materials line. EOG 2008/2009 kept-unverified cells keep wrong current ratios.
