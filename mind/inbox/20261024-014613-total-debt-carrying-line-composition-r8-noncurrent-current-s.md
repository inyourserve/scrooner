---
id: total-debt-carrying-line-composition-r8-noncurrent-current-s
title: Total debt carrying-line composition (r8): noncurrent + current [+ short-term]; hold when DebtCurrent is contradicted by overlapping parts
kind: lesson
tags: total_debt, carrying_lines, debt
paths: pipeline/src/scrooner_pipeline/common/debt_carrying.py
evidence: FILING-CHECKED
source: lane3 2026-10-24, branch work/data-engineer/lane3-total-debt
created: 2026-10-24
verified: 2026-10-24
---
Targets reproduced from tags: AAPL Q3 FY26 84,344; GOOG FY2025 48,543; AMZN FY2025 68,851 and Q2 2026 132,549; PFE 39,836; DPZ 4,975,338K; MU FY2026 5,179. CVX FY2016 (46,033 printed) cannot be derived from tags: short-term debt 10,840 already contains the 6,253 current maturities and DebtCurrent 19,840 is not a subset sum of its parts, so it is held. AAPL FY2015: LongTermDebtNoncurrent 53,463 exists only as a non-authoritative conflict copy, so the total stays blank (r7). A DebtCurrent at or above the sum of the listed parts (TSLA) is the printed line and is accepted.
