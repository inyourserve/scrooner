---
id: filer-calc-linkbase-gives-debt-slots-aapl-abbv-cvx-mu-borrow
title: Filer calc linkbase gives debt slots: AAPL, ABBV, CVX, MU borrowing/lease lines are cal children of the liabilities totals; GOOG DebtCurrent is a leaf
kind: lesson
tags: calc-linkbase, total-debt, slot
paths: data-team/strategy/team/AS-FILED-PILOT-2026-10-24.md
evidence: FILING-CHECKED
source: data engineer as-filed pilot 2026-10-24
created: 2026-10-24
verified: 2026-10-24
---
AAPL 0000320193-20-000062, ABBV 0001551152-22-000017, CVX 0000093410-15-000020, MU 0000723125-21-000065, TSLA 0001564590-18-026353 cal.xml: the missed lines (OtherShortTermBorrowings, ShortTermBorrowings, CapitalLeaseObligationsNoncurrent, related-party convertible) are children of the face total. GOOG 0001652044-24-000022: lease sits inside LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities in the debt-note cal role; GOOG 2015-16 DebtCurrent has no children (commercial paper plus current leases only in notes). FSDS has no cal; read _cal.xml from the filing folder.
