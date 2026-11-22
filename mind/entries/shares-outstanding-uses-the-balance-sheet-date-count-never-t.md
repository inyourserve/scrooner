---
id: shares-outstanding-uses-the-balance-sheet-date-count-never-t
title: shares_outstanding uses the balance-sheet-date count, never the dei cover count
kind: decision
evidence: DOC-CITED
status: active
created: 2026-11-12
verified: 2026-11-22
---
Dhairya ruling 2026-11-12, consistent with PGR 2026-11-11. shares_outstanding = us-gaap:CommonStockSharesOutstanding (or its class sum) at the balance-sheet date. dei:EntityCommonStockSharesOutstanding is the cover date, and post-period buybacks and splits move it, so it is never the period cell. If no BS-date count is printed, the cell is not_presented. 39 of 50 docmaps for ranks 51-100 got this wrong. A wider receivables tag maps to accounts_receivable only through a company-scoped FILING-CHECKED override, when the BS face prints it as the single receivables line.

[2026-11-22] 2026-11-22 curator: partly extended by supersedes-11-12-shares-outstanding-may-be-derived-as-issued (issued - treasury derivation allowed when no outstanding count is printed).
