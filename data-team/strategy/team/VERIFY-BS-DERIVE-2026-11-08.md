Under test: inyourserve/scrooner#6, branch work/bs/derive-tl-current 5e4f616. Sample: data-team/strategy/team/results/bs-derive-tl-current/verifier_sample.csv (33 rows, seed 20261108; ConEd 2014-12-31 is listed twice, so 32 distinct keys).
SEC requests: 87 (sec.gov only, <= 3.4/s, the repo's declared User-Agent). Verifier session scrooner-c3. No DB access for this verdict.

# Verify: derived total liabilities and unclassified-balance-sheet reasons (2026-11-08)

## Result

**32 distinct keys: 31 right, 1 wrong.**

| route | keys | right | wrong |
|---|---|---|---|
| calc, no blank child | 8 | 7 | **1** (Kimberly-Clark) |
| calc, blank `CommitmentsAndContingencies` | 5 | 5 | 0 |
| calc, other blank children | 5 | 5 | 0 |
| identity | 6 | 6 | 0 |
| `unclassified_balance_sheet` (bank 2, insurer 2, REIT 2, general 3) | 9 | 9 | 0 |

Each derived value was re-derived independently from the face, with the kit's `face_liabilities` rule: printed total L&E − total equity including NCI − printed mezzanine, never a sum of children. The kit's first block was confirmed as the registrant in every combined filing.

**The one wrong value, Kimberly-Clark 2024-03-31.** The claim is 15,908M; the face gives **15,882M**. The face (0000055785-24-000054 R4) prints "Redeemable Preferred Securities of Subsidiaries $26" (RedeemableCommonAndPreferredSecuritiesOfSubsidiaries) after Other Liabilities and before Stockholders' Equity, with no total-liabilities line. That position is mezzanine, so 17,092 − 1,184 − 26 = 15,882. The calc route counted it as a liability. Action: classify redeemable/temporary lines that sit between the last liability and equity as mezzanine, as the BS lane's own face rule does. Re-verify KMB's other dates.

## The two cells the brief asked about

- **Sempra 2015-12-31 (combined Sempra / SDG&E / SoCalGas filing 0000086521-17-000017, R2): RIGHT.** The face column used is the parent's. The first block is Sempra's own:
  - Total assets 41,150.
  - Total equity 12,579 = shareholders' equity 11,809 + preferred stock of subsidiary 20 + other NCI 750.
  - Total liabilities and equity 41,150.

  The five blank children are SDG&E and SoCalGas line items. SDG&E's block prints Interest payable 39 and current asset retirement obligations 99; SoCalGas's prints Income taxes payable 3 and Pension obligation, net of plan assets 716. Sempra's own block does not carry them, so counting them as zero in Sempra's column is right. 41,150 − 12,579 = **28,571** = claim.
- **News Corp 2019-03-31 (0001193125-19-143603 R5): RIGHT.** The temporary-equity child is "Redeemable preferred stock" (TemporaryEquityCarryingAmount…), printed **0** for 2019-03-31. It sits outside total liabilities and changes nothing. 16,058 − 10,458 (total equity incl. NCI 1,169) = **5,600** = claim.

## Cell table (derived total liabilities, $M unless noted)

| stratum | company, date | accession, page | face: L&E − equity (− mezzanine) | claim | verdict |
|---|---|---|---|---|---|
| calc_plain | Con Edison 2014-12-31 | 0001047862-16-000225 R5 (combined; first block ConEd) | 44,071 − 12,585 = 31,486 | 31,486 | RIGHT |
| calc_plain | Essential Utilities 2015-09-30 | 0000078128-15-000011 R2 ($K) | 5,701,345 − 1,728,681 = 3,972,664 | same | RIGHT |
| calc_plain | Landstar 2020-03-31 | 0001193125-20-129965 R2 ($K) | 1,236,433 − 627,095 = 609,338 | same | RIGHT |
| calc_plain | **Kimberly-Clark 2024-03-31** | 0000055785-24-000054 R4 | 17,092 − 1,184 − 26 (redeemable preferred of subsidiaries) = **15,882** | 15,908 | **WRONG (+26)** |
| calc_plain | Accenture 2017-08-31 | 0001467373-18-000318 R2 ($K) | 22,689,890 − 9,710,200 = 12,979,690 | same | RIGHT |
| calc_plain | Dick's 2022-10-31 | 0001089063-23-000145 R4 ($K) | 8,956,600 − 2,377,172 = 6,579,428 | same | RIGHT |
| calc_plain | Honeywell 2016-09-30 | 0000930413-16-008530 R4 | 53,556 − 19,371 − redeemable NCI = 34,182 | same | RIGHT |
| calc_plain | Occidental 2024-09-30 | 0000797468-24-000164 R2 | 85,803 − 34,934 = 50,869 | same | RIGHT |
| calc_blank_commitments | Service Corp 2019-09-30 | 0000089089-19-000039 R5 ($K) | 13,316,321 − 1,775,520 = 11,540,801 | same | RIGHT |
| calc_blank_commitments | Crown Holdings 2014-06-30 | 0001219601-14-000027 R4 | 9,895 − 412 = 9,483 | same | RIGHT |
| calc_blank_commitments | GoDaddy 2024-03-31 | 0001609711-24-000072 R2 | 7,978.8 − 414.8 = 7,564.0 | same | RIGHT |
| calc_blank_commitments | Iron Mountain 2019-12-31 | 0001020569-21-000067 R2 ($K) | 13,816,816 − 1,464,227 − 67,682 (redeemable NCI) = 12,284,907 | same | RIGHT |
| calc_blank_commitments | SAIC 2023-01-31 | 0001571123-24-000045 R5 | 5,543 − 1,704 = 3,839 | same | RIGHT |
| calc_blank_other | Albertsons 2024-02-29 | 0001646972-25-000052 R3 | 26,221.1 − 2,747.5 = 23,473.6 | same | RIGHT |
| calc_blank_other | AeroVironment 2019-10-31 | 0001558370-19-011303 R2 ($K) | 544,493 − 490,357 = 54,136 | same | RIGHT |
| calc_blank_other | News Corp 2019-03-31 | 0001193125-19-143603 R5 | 16,058 − 10,458 = 5,600 (redeemable preferred 0) | same | RIGHT |
| calc_blank_other | Rayonier 2021-09-30 | 0000052827-21-000176 R4 ($K; combined Rayonier Inc / LP, first block Inc) | 3,706,414 − 1,792,460 − 140,555 (NCI in the operating partnership, temporary equity) = 1,773,399 | same | RIGHT |
| calc_blank_other | Sempra 2015-12-31 | 0000086521-17-000017 R2 (combined; first block Sempra) | 41,150 − 12,579 = 28,571 | same | RIGHT |
| identity | Armstrong World 2024-09-30 | 0000950170-24-117930 R3 | 1,804.0 − 717.0 = 1,087.0 | same | RIGHT |
| identity | Oracle 2024-08-31 | 0000950170-24-104905 R2 | 144,214 − 11,269 = 132,945 | same | RIGHT |
| identity | HCA 2024-06-30 | 0000950170-24-087322 R4 | 57,379 − 1,339 = 56,040 | same | RIGHT |
| identity | PSEG 2024-09-30 | 0000950170-24-120749 R5 (combined; first block PSEG) | 54,080 − 16,095 = 37,985 | same | RIGHT |
| identity | Watts Water 2024-09-30 | 0001558370-24-014022 R2 | 2,399.1 − 1,689.1 = 710.0 | same | RIGHT |
| identity | Transocean 2024-09-30 | 0001451505-24-000142 R4 | 19,510 − 10,228 = 9,282 | same | RIGHT |

## Unclassified-balance-sheet reasons (current assets / current liabilities = not_presented)

For each filing I searched the full XBRL instance for any `us-gaap:AssetsCurrent` or `us-gaap:LiabilitiesCurrent` fact, in any context including dimensional ones, and the balance-sheet face for a "Total current assets/liabilities" label. All 9 have none, so the reason is RIGHT.

| class | company, date | accession (instance) |
|---|---|---|
| bank | Zions 2014-06-30 | 0000109380-14-000171 (zion-20140630.xml) |
| bank | Valley National 2015-09-30 | 0000714310-15-000156 |
| insurer | Cincinnati Financial 2018-03-31 | 0000020286-18-000030 |
| insurer | Unum 2014-12-31 | 0000005513-16-000045 |
| equity REIT | Healthcare Realty 2023-03-31 | 0001360604-23-000043 |
| REIT (mortgage) | AGNC 2025-06-30 | 0001423689-25-000073 |
| general | Invesco 2024-09-30 | 0000914208-24-000427 |
| general | Goldman Sachs 2020-06-30 | 0001193125-20-212201 |
| general | Victory Capital 2018-09-30 | 0001558370-18-009272 |

Caveat: a custom-extension current total, outside us-gaap, would not be caught by the instance search. The face label check covers it on the balance sheet only. AGNC is a mortgage REIT, sampled under `equity_reit`; the stratum label is off, but the reason holds.

## Findings for the lane

1. **Mezzanine classification in the calc route:** a redeemable or temporary line between the last liability and equity is not a liability (KMB `RedeemableCommonAndPreferredSecuritiesOfSubsidiaries`). Fix it and re-draw calc keys whose children include a `Redeemable*` or `Temporary*` tag.
2. **Sample file:** ConEd 2014-12-31 is listed twice.

## Untested scope

- The 486 total-liabilities and 471 current-item keys still open were not drawn.
- The ±10-day pilot match (12 keys) was not checked.
- Current-asset/liability values derived elsewhere were not part of this sample.
