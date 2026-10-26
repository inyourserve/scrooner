---
id: split-re-base-run-6-one-dividend-basis-per-company-generic-p
title: Split re-base run 6: one dividend basis per company; generic PaymentsOfDividends is not common-dividend evidence; clerical copy rules
kind: decision
tags: dividends, AC-24, share_basis, PaymentsOfDividends, amendment, units-scale
paths: pipeline/src/scrooner_pipeline/corporate_actions/share_basis.py
evidence: DATA-INFERRED
source: work/period-engineer/split-rebase run 6; VERIFY-SPLIT-RUN5-2026-10-26.md
created: 2026-10-26
verified: 2026-10-26
---
(1) One DPS basis per company: tag with more filed quarters since 2015 (fallbacks: whole history, all spans; tie Declared); off-basis cells take the basis tag's agreeing own-vintage value or hide dividend_basis_pending; an off-basis 6M/9M/FY equal to the basis quarters' sum stays. Cohort: mixed companies 240 -> 0. (2) Generic PaymentsOfDividends includes preferred/NCI/dividend equivalents (BPOP, WYNN, TDG): evidence only >= 1 cent/quarter over the filing's share count and >= 1/4 the nearest filed rate. (3) Per-share copies off by x1000/x1e6: majority, else local magnitude (NPO, BE). Share counts: an /A within 60 days corrects the original and the typo leaves the share series (ANF, BWXT, SNDK); the original count stands over a lone later copy (TSCO, TTEK). (4) Share-step-only events at offering-sized ratios (1/2..2) are rejected (SYRE); balance-sheet/WASO counts > 130 days older than their filing leave the series (LYFT); zero EPS is basis-free (QXO); a confirmed split inside an issuance step within 1.5x places earlier filings (NLY, SIRI).
