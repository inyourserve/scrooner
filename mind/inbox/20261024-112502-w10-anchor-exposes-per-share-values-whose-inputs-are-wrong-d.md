---
id: w10-anchor-exposes-per-share-values-whose-inputs-are-wrong-d
title: W10 anchor exposes per-share values whose inputs are wrong (debt, NCI, preferred)
kind: lesson
tags: W10, per-share, book_value
evidence: FILING-CHECKED
source: data-team/strategy/team/VERIFY-W10-2026-10-24.md
created: 2026-10-24
verified: 2026-10-24
---
lane2 W10 (pershare.balance_sheet_date_anchor@1) pairs balance-sheet-date shares correctly in 23/23 cells (AAPL 7.36 = 107,520/14,608.963). Exposed values still wrong via inputs: net cash from wrong stored total debt (AAPL 84,297, AMZN 133,320, AVGO, BAC omits short-term borrowings), UNH equity includes NCI 6,066 (0000731766-26-000197 R2), BAC/MS BVPS include preferred. Release W10 with the total-debt fix.
