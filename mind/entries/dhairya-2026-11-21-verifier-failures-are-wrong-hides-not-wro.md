---
id: dhairya-2026-11-21-verifier-failures-are-wrong-hides-not-wro
title: Dhairya 2026-11-21: verifier failures are wrong HIDES, not wrong shown values; a year any 10-K/10-Q presents must be shown; Form 10/S-1-only periods hide as no_10k_presents_period
kind: decision
tags: certification, display, hide, verifier, ruling
paths: data-team/strategy/approvals/registry.csv, data-team/strategy/approvals/BA-final-draw-2026-11-16.md, data-team/strategy/approvals/MO-final-draw-2026-11-16.md, data-team/strategy/approvals/STX-final-draw-2026-11-16-r2.md, data-team/strategy/approvals/GEV-final-draw-2026-11-15.md
evidence: FILING-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
Ritwik's display-certify draws (registry.csv, 2026-11-15/16) found 0 wrong in 32 random SHOWN cells at every company (GILD, JNJ PASS; BA, MO, STX, GEV FAIL). Every FAIL was a hide or scale defect: BA 18 HIDDEN_YEAR cells whose year end a 10-K/10-Q presents (own or comparative column); MO other_income_expense_net hidden as never reported though the FY2015 10-K prints 'Other income, net' (OtherNonoperatingIncomeExpense); STX DPS FY2022 served 2,770,000 for 2.77 (filer scale error); GEV reason code no_public_filing_for_period used where a Form 10 was public. Rulings (Dhairya, under founder delegation): (1) a year hide is valid only when no 10-K or 10-Q presents the period end; a printed zero or dash is a value; (2) a never_reported row hide needs a full-text search of every 10-K finding no line; (3) Form 10/S-1-only periods are out of V1 scope and hide with the honest code no_10k_presents_period; (4) every per-share value passes a plausibility check before it is shown. Engineering builds a structural hide audit over the 96 template companies; filing agents prefer VALUE whenever any 10-K/10-Q prints the number.
