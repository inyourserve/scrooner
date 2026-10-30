---
id: face-column-test-via-one-section-total-tag-fails-when-the-fi
title: Face-column test via one section-total tag fails when the filer switches between plain and ContinuingOperations cash-flow totals
kind: lesson
tags: d_and_a, capex, cash_flow, face_column, continuing_operations
paths: data-team/strategy/team/VERIFY-DA-CAPEX-V3-2026-10-25.md
evidence: FILING-CHECKED
source: ABBV 0001551152-21-000008; CAT 0000018230-21-000260; INTC 0000050863-21-000030; AMD 0000002488-26-000018
created: 2026-10-26
verified: 2026-10-26
---
slot-records D&A/capex V3 marks a duration a face column only if the record's section total tag is filed for it. Records carry NetCashProvidedByUsedIn...ContinuingOperations, while ABBV/CAT/INTC/MSFT/MU filings tag the plain total, so printed FY/YTD/Q1 values (ABBV FY2020 D&A 666+5,805, capex 798) are thrown away: 7 of 10 sampled. Accept either total. AMD FY2025: PaymentsForProceedsFromProductiveAssets 38M is a sibling line, not a net-capex total; capex reads 974M.
