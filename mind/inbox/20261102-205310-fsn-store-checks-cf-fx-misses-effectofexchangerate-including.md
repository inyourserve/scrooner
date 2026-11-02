---
id: fsn-store-checks-cf-fx-misses-effectofexchangerate-including
title: fsn_store checks CF_FX misses EffectOfExchangeRate...IncludingDisposalGroupAndDiscontinuedOperations: the cash identity fails and CFO/dividends/buybacks blank for 19 top-100 filers
kind: gotcha
tags: fsn, cash-flow, identity, fx, pilot
paths: pipeline/src/scrooner_pipeline/fsn_store/checks.py
evidence: CODE-CHECKED
source: MSFT 0001193125-26-323660; pilot run 41490670432
created: 2026-11-02
verified: 2026-11-02
---
checks.py CF_FX (origin/main b785ec5) holds only EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents and EffectOfExchangeRateOnCashAndCashEquivalents. MSFT uses ...IncludingDisposalGroupAndDiscontinuedOperations from the FY2022 10-K (FY2025: CFO+CFI+CFF 11,864 + FX 63 = change 11,927); pilot run 41490670432 blanks MSFT cfo/dividends/buybacks FY2020-FY2026 as latest_copy_fails_identity (22 cells each). FSN pre shows 19 top-100 EDGAR names print it on the CF face 2018-2026 (ABT, AMZN, DELL, GE, GEV, GS, NEM, ORCL, PM, PLD, QCOM, RTX, TSLA, TMO, DIS, MSFT); CSCO/RTX use the twin ...DisposalGroupIncludingDiscontinuedOperations. Proposal P-1 in data-team/fsn/PROPOSALS.md.
