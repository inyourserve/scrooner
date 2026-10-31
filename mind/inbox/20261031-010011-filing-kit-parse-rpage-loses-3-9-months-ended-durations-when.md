---
id: filing-kit-parse-rpage-loses-3-9-months-ended-durations-when
title: filing_kit.parse_rpage loses '3/9 Months Ended' durations when date header cells carry colspan=2 footnote spacers
kind: gotcha
tags: filing-kit, r-page, duration, verifier
paths: pipeline/src/scrooner_pipeline/verification/filing_kit.py, pipeline/src/scrooner_pipeline/mapper/derived_row_retirement.py
evidence: FILING-CHECKED
source: scrooner-bc Verifier 2, B15 verdict 2026-10-31
created: 2026-10-31
verified: 2026-10-31
---
Cheniere 10-Q 0000003570-25-000107 R2: the header '3 Months Ended'/'9 Months Ended' each have colspan=3 because the 'Sep. 30, 2024' date cells have colspan=2. parse_rpage expands spans by raw colspan (6) against 4 date columns, the length check fails, and months becomes all None. page.column(date, 9) then raises KeyError, and the fallback raises AmbiguousColumn (a KeyError subclass), so FilingFace.printed_unit returns None and Family B hid LNG Q4 2025 (right value 2,302M) as derived_scale_unverified. Fix: map durations to date cells by position. Verdict: data-team/strategy/team/VERIFY-RETIREMENT-B15-2026-10-31.md.
