# Card family: Utility regulatory assets/liabilities and crypto (digital) assets (written 2026-10-22 by the Tag Expert)

Tags: `us-gaap:RegulatoryAssets`, `RegulatoryAssetsCurrent`, `RegulatoryAssetsNoncurrent`, `RegulatoryLiabilities`, `RegulatoryLiabilityCurrent`, `RegulatoryLiabilityNoncurrent`; `CryptoAssetFairValue`, `CryptoAssetFairValueCurrent`, `CryptoAssetFairValueNoncurrent`, `CryptoAssetCost`, `CryptoAssetRealizedGainLossOperating`, `CryptoAssetUnrealizedGainLossOperating`, `CryptoAssetUnrealizedGainOperating`, `CryptoAssetUnrealizedLossOperating`, `CryptoAssetRealizedAndUnrealizedGainLossOperating`, `CryptoAssetRealizedAndUnrealizedGainLossNonoperating`.
Asked by: Sector Analyst, SECTOR-ROWS-REVIEW row U2, section 4 (crypto) and section 8 items 4-5.
Method: FASB 2026 schema and documentation; one read-only DB connection (`sec_tag_library`; `core.fact` pairs, utilities = SIC 4900-4999, crypto = any filer of both tags, since 2015, authoritative, undimensioned, tolerance 0.5%); 3 filings opened (CPK, CLSK, MSTR).

## A. Regulatory assets and liabilities
### A1. Official meaning (FASB 2026)
| Tag | Period / balance | Definition |
|---|---|---|
| RegulatoryAssets | instant / debit | "The amount for the **individual regulatory asset as itemized in a table** of regulatory assets as of the end of the period." (written for use with a regulatory-asset axis) |
| RegulatoryAssetsCurrent | instant / debit | carrying amount of capitalized costs of regulated entities expected to be recovered within one year or the operating cycle |
| RegulatoryAssetsNoncurrent | instant / debit | same, not expected within one year |
| RegulatoryLiabilities / RegulatoryLiabilityCurrent / RegulatoryLiabilityNoncurrent | instant / credit | the individual itemized liability / current / noncurrent |
None deprecated.

### A2. Who reports it (DATA-INFERRED)
RegulatoryAssets 58 companies (57 active); RegulatoryAssetsCurrent 57 (53, `mapping_status = candidate`); RegulatoryAssetsNoncurrent 60 (56); RegulatoryLiabilities 53 (52); RegulatoryLiabilityCurrent 60 (56); RegulatoryLiabilityNoncurrent 59 (54). All unmapped except the one candidate. Sector Analyst face counts: Current/Noncurrent pairs 22/32 utilities, plain `RegulatoryAssets` 0/32 on the face.

### A3. How filers use it
| Filing | Rows | Finding |
|---|---|---|
| CPK 10-K 0001628280-26-011753 (cpk-20251231.htm) (me) | Face "Regulatory assets" `RegulatoryAssetsCurrent` 29.7M and `RegulatoryAssetsNoncurrent` 74.3M; note rows (under-recovered fuel 19.6M, infrastructure 3.2M, postretirement 6.7M, ...) on `RegulatoryAssets` with a member; **note "Total Regulatory Assets" undimensioned `RegulatoryAssets` 104.0M = 29.7 + 74.3** | plain tag = itemized note rows by member; undimensioned = note TOTAL |
Population: utility `RegulatoryAssets` vs Current + Noncurrent: 35 companies, 629 shared periods, **590 equal (94%)**, 39 differ (NFG: 308.0M vs 178.8M in FY2019 and similar, not opened). Against Noncurrent alone: 73 of 707 equal. So undimensioned `RegulatoryAssets` is the total (current + noncurrent), not the noncurrent face line.

### A4. Verdict
- `sr.util.regulatory_assets`: **Current + Noncurrent from the face (safe where both filed; CPK FILING-CHECKED)**, with the undimensioned plain `RegulatoryAssets` as an alternate TOTAL only where it equals the sum or where the face has one line (94% equal; DATA-INFERRED). Never read plain `RegulatoryAssets` as the noncurrent line. The draft lead (plain tag on the face) is wrong; the plain tag is still usable as a note total. NFG-type differences need a check before use.
- Regulatory liabilities: the same structure by definition; population not checked this run (ASSUMED by analogy, open).

## B. Crypto (digital) assets
### B1. Official meaning (FASB 2026; that these elements came with ASU 2023-08 fair-value crypto accounting is ASSUMED, not checked in the release notes)
| Tag | Period / balance | Definition |
|---|---|---|
| CryptoAssetFairValue | instant / debit | "Fair value of crypto asset. Excludes crypto asset held for platform user." |
| CryptoAssetFairValueCurrent / ...Noncurrent | instant / debit | fair value classified as current / noncurrent |
| CryptoAssetCost | instant / debit | cost of crypto asset |
| CryptoAssetRealizedGainLossOperating, ...UnrealizedGainLossOperating, ...RealizedAndUnrealizedGainLossOperating | duration / credit | realized / unrealized / both, from remeasurement, operating |
| CryptoAssetRealizedAndUnrealizedGainLossNonoperating | duration / credit | same, nonoperating |
| `CryptoAssetNoncurrent` | n/a | **not an element** of the 2025 or 2026 schema (the Sector Analyst's earlier lead) |
`CryptoAssetUnrealizedGainOperating` and `CryptoAssetUnrealizedLossOperating` are in the face data (1/8 each in the Sector Analyst's cohort) and MSTR uses the loss tag; I did not read their definitions this run.

### B2. Who reports it (DATA-INFERRED)
CryptoAssetFairValue 158 companies, first period 2022-07-10; Current 59; Noncurrent 64; Cost 127 (126 active); gain/loss tags 19-41 each. All unmapped. Era: nothing before 2022 (ASU 2023-08 adoption, early adopters 2023).

### B3. How filers use it
| Filing | Rows | Finding |
|---|---|---|
| MSTR 10-K 0001050446-26-000020 R3, R5 (me) | Face "Digital assets" `CryptoAssetFairValue` 58,854,028K (unclassified balance sheet); "Unrealized loss on digital assets" `CryptoAssetUnrealizedLossOperating` 5,403,476K; "Digital asset impairment losses" custom `mstr_` 0 | the plain tag is the face line when the balance sheet has no current/noncurrent split |
| CLSK 10-Q 0001193125-26-039538 (clsk-20251231.htm) (me) | Face "Bitcoin - current" `CryptoAssetFairValueCurrent` 830,073K and "Bitcoin - noncurrent" `CryptoAssetFairValueNoncurrent` 171,924K; **undimensioned `CryptoAssetFairValue` 144,163K is a narrative ("1,648 bitcoin with a fair value of $144,163"), a subset** | the plain tag can be a narrative subset next to the classified face lines |
Population (any filer with both): `CryptoAssetFairValue` vs Current + Noncurrent: 12 companies, 33 shared periods, **11 equal, 22 differ** (CLSK, MARA). vs Noncurrent alone: 106 of 147 equal. Custom extensions carry operations, collateral and borrowed crypto at COIN, GLXY, HUT (Sector Analyst face data).

### B4. Verdict
- `sr.crypto.digital_assets`: **Current + Noncurrent where the face is classified; plain `CryptoAssetFairValue` only where it is the face line (MSTR) or equals the sum.** Never add the plain tag to the classified pair (CLSK double count). FILING-CHECKED (MSTR, CLSK); counts DATA-INFERRED. Only from 2022 on (no earlier facts exist under these tags in our data; that earlier crypto sat in intangible assets at cost, often custom-tagged, is ASSUMED, as is the era cause).
- `sr.crypto.digital_asset_gains_losses`: a SET, not one tag: realized, unrealized, combined, and the separate unrealized gain / unrealized loss tags (MSTR uses the loss tag), operating and nonoperating. The Sector Analyst's 3-tag set misses `CryptoAssetUnrealizedLossOperating` / `...GainOperating` and the nonoperating tag. Sign follows the tag (credit: gain positive), and the row label can be negated (MSTR prints a loss as positive 5,403,476).
- Verified by: Tag Expert (me), 2026-10-22.
