---
id: balance-sheet-identity-subtract-total-equity-incl-nci-and-te
title: Balance-sheet identity: subtract total equity incl NCI and temporary equity; NCI-inclusive equity tag is already total
kind: lesson
tags: identity, liabilities, nci, temporary-equity
paths: pipeline/src/scrooner_pipeline/mapper/balance_identity.py
evidence: FILING-CHECKED
source: WMT 0000104169-26-000154 R4; T 0000732717-26-000297 R5; VLO 0001035002-21-000051 R2
created: 2026-10-24
verified: 2026-10-24
---
Liabilities = Assets - total equity (parent + NCI) - temporary equity. Legacy SQL added the adjustment (sign) and counted NCI again when the equity input was the NCI-inclusive tag. Corrected values match WMT 189,115M, T 299,920M, VLO 2020 32,132M. Temporary equity incl-NCI tag replaces (not adds to) parent + redeemable NCI. Equity-direction cells without a MinorityInterest fact (BX, KKR) remain lower confidence. Branch work/data-engineer/identity-fix, rule balance.identity_equity_basis@1 (flag OFF).
