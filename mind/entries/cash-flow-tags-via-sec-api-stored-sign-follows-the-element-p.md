---
id: cash-flow-tags-via-sec-api-stored-sign-follows-the-element-p
title: Cash-flow tags via SEC API: stored sign follows the element, printed = stored x -1 where FSN negating; Proceeds and loss tags can be negative
kind: rule
tags: cash-flow, sign, companyfacts, fsn
paths: data-team/tags/library/fsn-cash-flow.csv, data-team/tags/cards/fsn-cash-flow.md
evidence: FILING-CHECKED
status: active
source: AAPL 0000320193-25-000079 R8; PODD 0001145197-26-000169 R7; TRMB 0000864749-26-000108 R7
created: 2026-11-11
verified: 2026-11-11
---
AAPL OtherNoncashIncomeExpense prints (89), stored +89M; PODD GainsLossesOnExtinguishmentOfDebt prints 123.9, stored -123.9M; TRMB ProceedsFromIssuanceOfCommonStock net of withholding stored -32.5M. Payments* stored positive = outflow. Never abs(). Also: LRCX buyback tag includes excise (doc 02 item 4 -> combined); XOM/HPQ/DUK D&A tag includes impairment/accretion (combined); FSN UN rows are co-registrant statements.
