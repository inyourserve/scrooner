---
id: structural-total-debt-debt-role-nodes-under-liabilities-leas
title: Structural total_debt: debt-role nodes under liabilities + leases the filing locates outside them
kind: rule
evidence: FILING-CHECKED
created: 2026-11-14
verified: 2026-11-14
---
2026-11-13 (Tag Expert, main 79a0c0a3; MSFT 12/12 backtest; FY2016 53,461, FY2017 88,732, FY2025 89,323 vs served 43,151): total_debt = every debt-role node between the asset total and equity, deduped by the calc tree, plus finance leases when the ExtensibleList says out (or by absence, flagged CHECK), plus pre-842 capital leases whose calc parent is not a debt line; lines whose tag/label names leases already include them. Each cell from the latest-filed face column. Proof v9 enforces the perimeter (perimeter_incomplete); ~324 cells in 54 companies had omitted short-term debt or leases.
