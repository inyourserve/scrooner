# Verify: Fix #1 balance-sheet identity (balance.identity_equity_basis@1), 2026-10-24

Verifier (independent pass). Subject: branch `work/data-engineer/identity-fix` a0748b9, plan file `identity_plan_final.jsonl` (7,703 rows, scratchpad of session b256f7de). Method: for each cell, the source fact ids in the plan were resolved to their filing (core.fact -> core.filing, read-only, 20s timeout, one connection); the filing's balance-sheet R page was opened on sec.gov; the expected value was written from the face before comparing: printed "Total liabilities" where printed, else the sum of the face liability lines (redeemable NCI / temporary equity / mezzanine lines kept outside liabilities, as printed); for the equity direction, the printed parent equity line. All verdicts FILING-CHECKED unless marked. Shared-parser note: one reader (regex on R-file rows); every sum was recomputed in code.

## Result: GATE FAILS. 7 wrong new values in 43 checked (2 equity-direction, 4 unread temporary-equity tags, 1 mixed vintage). 0 cells where the OLD value was right.

## Named cells (seed 20261024-identity) + re-confirmations
| Ticker | Instant | Accession, locator | Stored -> new ($M) | Filing value | Verdict |
|---|---|---|---|---|---|
| EMR | 2024-12-31 | 0000032604-25-000012 R5 | 28,009 -> 16,231 | 5,958+6,557+3,716 = 16,231 (no TL line) | RIGHT |
| DIS | 2020-03-28 | 0001744489-20-000102 R5 | 129,453 -> 102,321 | 35,473+42,770+7,965+16,113 = 102,321; RNCI 9,096 outside | RIGHT |
| DVN | 2015-12-31 | 0001193125-16-466687 R4 | 26,423 -> 18,543 | 3,295+12,137+1,370+853+888 = 18,543 | RIGHT for the original 10-K; FY2016 10-K 0001564590-17-001607 R4 restates assets to 29,451 (L = 18,462): vintage policy, Assets copies all non-authoritative |
| BX | 2019-06-30 | 0001193125-19-216805 R2 | SE 14,166.4 -> 13,963.8 | parent "Total The Blackstone Group L.P. Partners' Capital" 6,308.355; 13,963.776 is Total Partners' Capital incl. NCI 7,655.4 | WRONG (old also wrong) |
| KKR | 2015-06-30 | 0001404912-15-000005 R2 | SE 52,234.2 -> 51,998.1 | parent "Total KKR & Co. L.P. Partners' Capital" 5,947.415; 51,998.065 is Total Equity incl. NCI 46,050.7 | WRONG (old also wrong) |
| KO | 2019-06-28 | 0000021344-19-000034 R4 | 73,929 -> 69,701 | 29,382+29,296+8,336+2,687 = 69,701 | RIGHT |
| LYB | 2017-12-31 | 0001193125-18-054181 R4 | 17,258 -> 17,256 | 4,777+8,549+2,275+1,655 = 17,256 | RIGHT |
| HPE | 2025-04-30 | 0001645590-25-000068 R4 | 43,987 -> 43,927 | 24,538+12,378+7,011 = 43,927 (NCI 60 has no MinorityInterest fact) | RIGHT |
| CMCSA | 2024-06-30 | 0001166691-24-000048 R6 | 180,057 -> 178,615 | 35,342+97,107+26,252+19,914 = 178,615; RNCI 236 outside | RIGHT |
| WSO | 2023-03-31 | 0001193125-23-137075 R4 | 2,251.2 -> 1,492.3 | 953,083+448,139+91,095 = 1,492,317K | RIGHT |
| NWSA | 2024-03-31 | 0001564708-24-000249 R5 | 9,350 -> 7,636 | 3,042+2,844+135+124+1,053+438 = 7,636 | RIGHT |
| MGY | 2021-09-30 | 0001698990-21-000049 R2 | 891.1 -> 680.3 | 190,685+489,577 = 680,262K | RIGHT |
| MGY | 2023-03-31 | 0001698990-23-000016 R2 | 976.7 -> 809.0 | 311,244+497,733 = 808,977K | RIGHT |
| ITW | 2024-12-31 | 0000049826-25-000007 R5 | 11,751 -> 11,750 | 4,308+7,442 = 11,750 | RIGHT |
| ADM | 2017-06-30 | 0000007084-17-000027 R4 | 20,433 -> 20,372 | 11,421+8,951 = 20,372; RNCI 27 outside | RIGHT |
| GWW | 2018-09-30 | 0000277135-18-000029 R5 | 4,156.8 -> 3,832.1 | 1,467,332+2,148,399+115,644+100,754 = 3,832,129K | RIGHT |
| LYV | 2023-09-30 | 0001335258-23-000102 R2 | 20,397.8 -> 17,439.8 | 8,751,521+6,546,061+1,673,750+468,504 = 17,439,836K | RIGHT |
| BRKR | 2019-03-31 | 0001104659-19-027788 R2 | 1,359.7 -> 1,298.9 | lines sum 1,298.7; face does not foot (Total assets 2,242.5 vs TL&E 2,242.3) | RIGHT within the filer's own 0.2M rounding; informational |
| IAC (MTCH cik) | 2016-06-30 | 0000891103-16-000031 R2 | 2,968.5 -> 2,722.7 | 692,206+1,655,259+33,083+259,738+82,382 = 2,722,668K | RIGHT |
| MMC | 2026-09-30 | 0000062709-26-000258 R4 | blank -> 44,896 | 22,109+18,889+693+1,475+281+1,449 = 44,896 | RIGHT (fill) |
| WMT | 2026-07-31 | 0000104169-26-000154 R4 | 202,237 -> 189,115 | 115,630+36,462+14,798+5,952+16,273 = 189,115 | RIGHT (re-confirmed) |
| T | 2026-06-30 | 0000732717-26-000297 R5 | 319,920 -> 299,920 | 53,382+134,631+111,907 = 299,920 | RIGHT (re-confirmed) |
| VLO | 2020-12-31 | 0001035002-21-000051 R2 | 33,814 -> 32,132 | 9,283+13,954+5,275+3,620 = 32,132 | RIGHT (re-confirmed) |

## Stratified random 15 (seed `20261024-identity-strat`, Python random.Random on the string)
Frame: plan rows with kind=replace, stored value nonzero, period_end >= 2015-01-01: 5,414 rows (buckets <0.1% 779 / 0.1-1% 1,710 / 1-5% 1,508 / 5-10% 609 / 10-25% 553 / 25%+ 255). Rows sorted by (cik, period_end, concept), shuffled per bucket; allocation 2/3/3/2/2/3; one cell per company; companies in the named list excluded.
| Bucket | Ticker | Instant | Accession, locator | Stored -> new ($M) | Filing value | Verdict |
|---|---|---|---|---|---|---|
| <0.1% | AMRX | 2023-12-31 | 0001723128-24-000014 R5 | 3,453.0 -> 3,452.6 | current 846,595 + LT 2,564,670 = 3,411,265K; RNCI 41,293K on `TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests` not subtracted | WRONG |
| <0.1% | FE | 2016-03-31 | 0001031296-16-000079 R5 | 40,233 -> 40,231 | 6,389+18,878+14,964 = 40,231 (capitalization format) | RIGHT |
| 0.1-1% | BA | 2019-06-30 | 0000012927-19-000063 R5 | 131,962 -> 131,204 | 92,189+4,486+14,831+4,839+14,859 = 131,204 (negative equity) | RIGHT |
| 0.1-1% | GILD | 2024-12-31 | 0000882095-25-000006 R3 | 39,581 -> 39,749 | 12,004+24,896+830+724+1,295 = 39,749 (NCI -84) | RIGHT |
| 0.1-1% | MCK | 2015-06-30 | 0000927653-15-000006 R4 | 47,158 -> 46,986 | 34,673+8,142+2,741 = 45,556; RNCI 1,430 on `RedeemableNoncontrollingInterestEquityCommonCarryingAmount` not subtracted | WRONG |
| 1-5% | IRM | 2018-12-31 | 0001020569-19-000018 R2; 0001020569-20-000029 R2 | 10,061.7 -> 9,919.3 | original 10-K 9,896,126K; restated (FY2019 10-K) 9,924,223K; new = original assets 11,852,247 - restated equity 1,862,463 - RNCI 70,532 | WRONG (mixed vintage) |
| 1-5% | IPG | 2024-06-30 | 0000029989-24-000021 R2 | 24,248.5 -> 23,128.3 | 14,957.1+881.0+806.2+5,489.4+533.8 = 22,667.5; RNCI 460.8 on `RedeemableNoncontrollingInterestEquityFairValue` not subtracted | WRONG |
| 1-5% | ATR | 2022-06-30 | 0000896622-22-000024 R4 | 2,338.4 -> 2,309.6 | 822,032+1,271,752+215,862 = 2,309,646K | RIGHT |
| 5-10% | ROK | 2020-12-31 | 0001024478-21-000005 R2 | 6,929.6 -> 6,297.2 | 2,188.6+1,980.3+1,287.2+268.2+572.9 = 6,297.2 | RIGHT |
| 5-10% | ACN | 2025-11-30 | 0001467373-25-000222 R2 | 34,885.7 -> 32,776.2 | 19,896,521+12,879,660 = 32,776,181K | RIGHT |
| 10-25% | CHK | 2015-06-30 | 0000895126-15-000203 R2 | 20,925 -> 18,355 | 5,128+13,227 = 18,355 | RIGHT |
| 10-25% | RYN | 2017-06-30 | 0000052827-17-000032 R4 | 1,477.5 -> 1,284.7 | 178,628+1,033,621+31,589+40,846 = 1,284,684K | RIGHT |
| 25%+ | MGM | 2021-06-30 | 0001564590-21-041935 R2 | 35,630.7 -> 25,561.7 | 2,036,371+2,170,945+12,574,939+8,403,862+375,615 = 25,561,732K | RIGHT |
| 25%+ | WMB | 2015-09-30 | 0000107263-15-000018 R5 | 54,305 -> 32,559 | 3,858+21,805+4,582+2,314 = 32,559 | RIGHT |
| 25%+ | ETP (cik 1276187) | 2015-09-30 | 0001276187-15-000094 R2 | 71,107 -> 47,087 | 5,049+36,332+4,256+189+1,246 = 47,072; mezzanine = preferred units 33 + RNCI 15 (`RedeemableNoncontrollingInterestEquityOtherCarryingAmount`, unread) | WRONG (by 15) |

## Negative controls: stored value from a real `Liabilities` fact (seed `20261024-identity-neg`)
Frame: 1,520 single-source `total_liabilities_resolved` rows since 2015 in the 205 plan companies, all on `us-gaap:Liabilities`; **0 of 1,520 appear in the plan** (DATA-INFERRED, full frame). 5 drawn, one per company:
| Ticker | Instant | Accession, locator | Stored | Printed Total liabilities | Verdict |
|---|---|---|---|---|---|
| CAKE | 2024-10-01 | 0001410578-24-001742 R2 | 2,539,409K | 2,539,409 | RIGHT, untouched |
| DD | 2025-06-30 | 0001666700-25-000043 R4 | 13,043M | 13,043 | RIGHT, untouched |
| CELH | 2021-12-31 | 0001829126-23-002816 R2 (10-K/A) | 96,973K | 96,973 | RIGHT, untouched |
| CL | 2021-03-31 | 0000021665-21-000010 R4 | 15,138M | 15,138 | RIGHT, untouched |
| VFC | 2023-07-01 | 0000103379-23-000015 R2 | 11,327,135K | 11,327,135 | RIGHT, untouched |

## Root causes (send to the Data Engineer; do not enable `on:`)
1. **Misspelled temp-equity tag.** `mapper/balance_identity.py` line 43 `TEMP_INCL = "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterest"`; the filed element (core.concept 32640) ends in `...NoncontrollingInterests`. The singular spelling matches no concept, so the "including-NCI" branch never runs (AMRX). The same misspelling is in the Data Engineer's feedback-inbox line of 2026-10-24.
2. **Redeemable-NCI tag family only partly read.** Only `RedeemableNoncontrollingInterestEquityCarryingAmount` and `TemporaryEquityCarryingAmountAttributableToParent` are loaded. Face lines were found on `...EquityCommonCarryingAmount` (MCK), `...EquityFairValue` (IPG), `...EquityOtherCarryingAmount` (ETP). Reach (DATA-INFERRED, plan cells with a nonzero fact on an unread temp/redeemable tag at the same instant and no read temp tag): 390 cells, 27 companies, 278 since 2015. Some of those tags (RedemptionValue, FairValue) can be note disclosures rather than the face line, so the fix needs face/statement-role evidence, not a longer tag list alone.
3. **Mixed vintage.** Inputs are picked per term with no same-filing constraint: IRM 2018-12-31 used the original 10-K assets with the restated FY2019 10-K equity. Require Assets, equity and adjustment terms from one accession (or one consistent vintage), else no value.
4. **Equity direction without an NCI fact.** BX/KKR (partnerships) carry NCI on `PartnersCapitalAttributableToNoncontrollingInterest` (+ bx custom `NonControllingInterestInPartnerships`); parent is `PartnersCapital`. Assets - Liabilities - RNCI is total equity incl. NCI, not parent. Hold the equity direction when no NCI fact is read (as the plan proposed), and consider `PartnersCapital` for parent equity (mapping decision, Standardization Lead).
5. Informational: when Assets and LiabilitiesAndStockholdersEquity differ (BRKR 2,242.5 vs 2,242.3), the right side of the identity is L&E; prefer it as the base.

## Bound and untested scope
- Random 15: 5 wrong. Named 20 are risk-selected, not random. No population accuracy claim; the defect classes above are measured only as stated.
- Not tested: the 17 fills beyond MMC; the 90 equity rows beyond BX/KKR; pre-2015 rows; the 49-cell "legacy adjustment 0" class beyond HPE; second reader (iXBRL) on 10%.
