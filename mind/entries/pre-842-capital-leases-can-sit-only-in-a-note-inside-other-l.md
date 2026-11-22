---
id: pre-842-capital-leases-can-sit-only-in-a-note-inside-other-l
title: Pre-842 capital leases can sit only in a note (inside other liabilities); total_debt and its proof miss them unless the note is scanned; a proof using the map's tags cannot catch a perimeter error
kind: gotcha
tags: total_debt, capital_lease, asc842, perimeter, proof, certification
paths: data-team/strategy/approvals/MSFT-final-draw-2026-11-14.md
evidence: FILING-CHECKED
status: active
created: 2026-11-15
verified: 2026-11-15
---
MSFT FY2016 total_debt was served 53,461 (short-term debt 12,904 + current LTD 0 + LTD 40,557, FY2017 10-K 0001564590-17-014900 R5). The same filing's commitments note (R24/R102) discloses capital lease obligations of $25M in other current liabilities and $761M in other long-term liabilities, so the correct value is 54,247. No balance-sheet line shows them. Two independent samples first passed the narrower value, because the checker reused the proof's own tags, and the proof reused the map's tags. Rule for certification: check a sum cell against every face AND note line in the founder's 2026-11-04 debt perimeter (ST borrowings, CP, current/noncurrent debt, finance or capital leases), never just the tags the proof names. Every top-100 company's pre-FY2019 years need a note scan for capital leases. Source: cloud Ritwik final draw, f4238c25 on work/ritwik-cloud/tag-decisions-2026-11-11.
