---
id: ads-issuers-stored-share-counts-are-ordinary-shares-but-pric
title: ADS issuers: stored share counts are ordinary shares but price is per ADS, so market cap and P/E are off by the ratio
kind: gotcha
tags: ads, market-cap, pe
paths: data-team/strategy/team/WO-ADS-RATIO-AND-MULTICLASS-2026-10-22.md
evidence: FILING-CHECKED
created: 2026-10-23
verified: 2026-10-23
---
Ratios from cover text (dei:Security12bTitle): AKTX 80,000 since 2026-03-31 (10-K cover still said 2,000), ZLAB 10, SCNI 4,000, KZIA 500, DBVT 5, GPCR 3, AMRN 20, SLN 3. Stored AKTX cap 1.364T vs about 17M. P/E and dividend yield are wrong too. A scale test (200x) cannot detect it; detect from the cover text. RPAY and TBLA are filer unit errors (shares in full units tagged as thousands), propagated by _choose_shares preferring weighted-average over cover. 20-F filers (KZIA, SCNI) are out of V1 scope: exclude by form, compute no market cap.
