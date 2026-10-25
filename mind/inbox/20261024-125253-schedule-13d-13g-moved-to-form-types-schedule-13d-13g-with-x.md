---
id: schedule-13d-13g-moved-to-form-types-schedule-13d-13g-with-x
title: Schedule 13D/13G moved to form types SCHEDULE 13D/13G with XML on 2024-12-18; beneficial_ownership.py reads only SC 13D/G, so ingestion collapsed in 2025
kind: gotcha
tags: ownership, 13d, 13g, edgar, form-types
paths: pipeline/src/scrooner_pipeline/ownership/beneficial_ownership.py, data-team/strategy/team/EDGAR-ATLAS-2026-10-24.md
evidence: FILING-CHECKED
source: MU 0002100119-26-000795 primary_doc.xml (Vanguard classPercent 7.47, 84,297,629 sh); core.beneficial_ownership rows/quarter 2024: 1,452-12,818, 2025-26: 2-19 (read-only DB 2026-10-24)
created: 2026-10-24
verified: 2026-10-24
---
New filings use submission type 'SCHEDULE 13G'/'SCHEDULE 13D' (and /A) with xslSCHEDULE_13G_X0n/primary_doc.xml carrying issuerCik, issuerCusipNumber, classPercent, amountBeneficiallyOwned, voting powers. FORMS in beneficial_ownership.py = SC 13D/13G only. Also starves the 13F/N-PORT CUSIP crosswalk for new issuers. percent_of_class is now machine-readable, no text parsing needed.
