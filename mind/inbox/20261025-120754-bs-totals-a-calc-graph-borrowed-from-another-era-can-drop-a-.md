---
id: bs-totals-a-calc-graph-borrowed-from-another-era-can-drop-a-
title: BS totals: a calc graph borrowed from another era can drop a sibling line as a 'descendant'; the accounting identity gate catches it, the filer's own cal file fixes it
kind: lesson
evidence: DATA-INFERRED
created: 2026-10-25
verified: 2026-10-25
---
slot_records/bs_assemble.py borrows the filer's calc graph from its other boundary filings when an era's own cal file is missing (Verifier BS-V1 item 2: 129 clean ties were held as hold_no_cal_for_dedup). Replay 2026-10-25 showed the failure mode: a line that was a child of LiabilitiesCurrent/LiabilitiesNoncurrent in the borrowed filing is a separately printed sibling in this era (FE LongTermDebt 14 instants; BRKR DeferredIncomeCurrent 149.9M; NI DerivativeLiabilitiesCurrent 43.2M and AssetRetirementObligationCurrent 84.6M/55.0M; ET AccountsPayableRelatedParties 7M), so the roots double count or omit, and the gap equals that line exactly. Rules kept: (1) a face-sum value is PUBLISHED only when L&E total (else assets) = liabilities + mezzanine + equity incl. NCI within the filer's rounding unit, on the same accession; (2) the identity reads equity two ways (including-NCI total, parent + NCI under the filer's own nci tag) and accepts either (FE carries a stray 86M including-NCI fact); (3) use the filer's LiabilitiesAndStockholdersEquity as the right-hand side (BRKR 2019-03-31 assets 2,242.5 vs L&E 2,242.3). Borrowing is a fallback; fetching the boundary cal file is the fix.
