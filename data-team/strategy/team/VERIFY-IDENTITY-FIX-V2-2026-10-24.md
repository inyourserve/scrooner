# Verify: Fix #1 V2, balance-sheet identity (branch work/data-engineer/identity-fix 0e6efbf), 2026-10-24

Verifier 2, fresh sample (no cell from the V1 check, /Users/vikash/scrooner/data-team/strategy/team/VERIFY-IDENTITY-FIX-2026-10-24.md, was re-used). Plan `identity_plan_final_v2.jsonl` (8,109 rows). Method as V1: source facts resolved to their filing (read-only, 20s), balance-sheet R page opened on sec.gov, expected value written from the face first (printed Total liabilities, else the sum of face liability lines with mezzanine lines kept outside, as printed). One reader (regex on R rows) plus sums recomputed in code. All verdicts FILING-CHECKED unless marked.

## Result: GATE FAILS. 4 defective new values in 38 replaced/filled cells checked (3 wrong, 1 not verifiable from any face statement); 3 false holds in 14 holds checked. Do not enable `on:`.

## Defective new values
| Ticker | Instant | Accession, locator | Stored -> new ($M) | Filing value | Cause |
|---|---|---|---|---|---|
| NI | 2023-12-31 | 0001111711-24-000011 R6 | 24,674.3 -> 19,580.9 | 11,055.5 LTD + 5,265.1 current + 4,620.3 other = 20,940.9 (= 31,077.2 - 10,136.3) | subtracted `RedeemableNoncontrollingInterestEquityOtherCarryingAmount` 1,360.0, which is NOT on the face (face has no mezzanine line; the element is absent from R6). Face-placement limit fails |
| FE | 2018-03-31 | 0001031296-18-000031 R5 | 31,420 -> 38,709 | 5,065 + 16,740 + 9,615 = 31,420; Total stockholders' equity 7,375, no NCI line | `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` = 86M in this filing is not the face total (face R5 does not use that element). **OLD value was right** |
| TRGP | 2021-09-30 | 0001564590-21-054348 R2 | 17,002.4 -> 10,572.8 | 2,868.3 + 6,434.1 + 151.2 + 78.7 + 290.8 = 9,823.1; "Total liabilities, Series A Preferred Stock and owners' equity"; Series A Preferred 749.7 | mezzanine filed on `TemporaryEquityCarryingAmountAttributableToParent` with a class-of-stock member only (no undimensioned fact), so it was not subtracted |
| DVN | 2017-03-31 | terms from 0001564590-18-010177 (Q1 2018 10-Q: R6 equity statement 13,017; assets 28,635 not on R4); own 10-Q 0001564590-17-008268 R4 | 26,625 -> 15,618 (base_assets, "solved") | own face: 2,470 + 10,381 + 1,067 + 643 + 651 = 15,212 | NOT VERIFIABLE: the "one filing" has no balance sheet for 2017-03-31 (restated successful-efforts basis; equity from the equity statement, assets not on any face). Should be held |

## Right new values (FILING-CHECKED)
| Set | Ticker | Instant | Accession, locator | New ($M) | Face check |
|---|---|---|---|---|---|
| 3 Common | HON | 2023-09-30 | 0000773840-23-000085 R4 | 43,514 | lines sum 43,514; RNCI 7 on face |
| 3 Common | MCK | 2025-12-31 | 0000927653-26-000017 R4 | 84,289 | sum 84,289; RNCI 802 on face |
| 3 Common | RIG | 2017-06-30 | 0001451505-17-000052 R4 | 9,596 | 1,858 + 7,738; RNCI 42 on face |
| 3 Other | ET | 2021-09-30 | 0001276187-21-000079 R2 | 60,566 | sum 60,566; RNCI 783 on face |
| 3 generic (pre-2015) | CVS | 2012-03-31 | 0001104659-12-031650 R4 | 27,924 | sum 27,924; RNCI 29 on face |
| 3 generic (pre-2015) | HCA | 2011-09-30 | 0001193125-11-304797 R3 | 32,818 | sum 32,818; contingent-redemption line 0 on face |
| 1 temp_incl | AES | 2025-03-31 | 0000874761-25-000035 R2 | 39,991 | 9,344 + 30,647 |
| 1 temp_incl | AMRX | 2020-06-30 | 0001723128-20-000013 R4 | 3,673.4 | 655,019 + 3,018,341 K |
| 1 temp_incl | ILMN | 2017-12-31 | 0001110803-18-000009 R2 | 2,288 | 746 + 1,182 + 360 |
| 2 solved | ADM | 2022-12-31 | 0000007084-23-000010 R4 | 35,158 | 24,191 + 10,967 |
| 2 solved | SYY | 2023-09-30 | 0000096021-23-000201 R2 | 21,112.4 | 8,454,164 + 12,658,238 K |
| 2 solved | BWA | 2016-12-31 | 0000908255-17-000011 R2 | 5,532.8 | 2,091.8 + 2,043.6 + 1,397.4 |
| 2 solved | MMC | 2015-06-30 | 0000062709-15-000023 R4 | 10,541 | sum 10,541 (fiduciary nets 0) |
| 4 b0 | OTEX | 2022-06-30 | 0001002638-22-000029 R3 | 6,146.7 | 1,468,258 + 4,678,455 K |
| 4 b0 | TTEK | 2019-03-31 | 0000831641-19-000045 R2 | 961.3 | sum 961,260 K |
| 4 b0 | LYB | 2017-06-30 | 0001193125-17-239999 R4 | 17,250 | sum 17,250 |
| 4 b1 | PCG | 2020-03-31 | 0001004980-20-000026 R5 | 80,929 | 8,253 + 21,925 + 50,751 (combined filing; PG&E Corp block) |
| 4 b1 | ARMK | 2021-07-02 | 0001584509-21-000169 R2 | 11,354.1 | sum 11,354,101 K |
| 4 b1 | GILD | 2019-12-31 | 0000882095-20-000006 R2 | 38,977 | sum 38,977 |
| 4 b1 | AXTA | 2024-12-31 | 0000950170-25-023852 R4 | 5,519 | lines 5,518; face does not foot (2,276 + 10 vs 2,285; 7,803 vs 7,804): within filer rounding, informational |
| 4 b2 | DGX | 2018-03-31 | 0001022079-18-000106 R4 | 5,552 | 1,117 + 3,718 + 717 |
| 4 b2 | ATR | 2023-06-30 | 0000896622-23-000034 R4 | 2,159.3 | sum 2,159,286 K |
| 4 b2 | DUK | 2020-12-31 | 0001326160-21-000063 R4 | 113,204 | 16,305 + 55,625 + 41,274 |
| 4 b2 | IRM | 2025-03-31 | 0001020569-25-000110 R2 | 19,786.1 | sum 19,786,125 K |
| 4 b3 | IAC | 2016-09-30 | 0000891103-16-000034 R2 | 2,669.8 | sum 2,669,801 K |
| 4 b3 | NWS | 2016-03-31 | 0001193125-16-580872 R5 | 3,871 | 3,851 + redeemable preferred 20 shown under non-current liabilities |
| 4 b3 | DIS | 2023-12-30 | 0001744489-24-000081 R4 | 92,273 | sum 92,273 |
| 4 b4 | LYV | 2019-09-30 | 0001335258-19-000141 R2 | 8,025.5 | sum 8,025,485 K |
| 4 b4 | APA | 2024-09-30 | 0002040266-24-000003 R5 | 13,216 | 2,925 + 6,370 + 3,921 |
| 4 b5 | WSO | 2016-03-31 | 0001193125-16-581368 R4 | 656.2 | 347,251 + 238,366 + 70,569 K |
| 4 b5 | CF | 2022-09-30 | 0001324404-22-000028 R4 | 6,183 | sum 6,183 |
Random set 4: seed `20261024-identity-v2-b<k>` per bucket; frame = replace rows, stored nonzero, period_end >= 2015: 5,208 (<0.1% 714 / 0.1-1% 1,657 / 1-5% 1,469 / 5-10% 590 / 10-25% 541 / 25%+ 237); allocation 3/4/4/3/3/3; one cell per company; V1 cells excluded. 18 of 20 right; FE and TRGP wrong. Set 3 drew 3 Common + 2 Other with seed `...-parts-<element>`; every generic `TemporaryEquityCarryingAmount` replacement is pre-2015, so CVS, HCA (and Entergy 2010, which has no R files: not checked) were taken as the latest cell per company.

## Holds (is the hold right?)
| Reason | Ticker | Instant | Accession, locator | Stored | Filing | Verdict |
|---|---|---|---|---|---|---|
| mixed_vintage | OXY | 2018-12-31 | 0000797468-19-000004 R2; 0000797468-20-000004 R2 | 22,524 | 7,412 + 10,201 + 4,911 = 22,524 in both vintages | **FALSE HOLD** |
| redeemable_nci_measurement_only | AWK | 2017-12-31 | 0001410636-18-000076 R2 | 14,097 | 6,490 + 8 (redeemable preferred inside total long-term debt, `PreferredStockRedemptionAmount`) + 2,325 + 3,998 + 1,276 = 14,097 | **FALSE HOLD** (the trigger is a note fact) |
| nci_not_read (equity) | BRO (CIK 0000079282; first version mislabeled it AJG) | 2019-01-01 | 0000079282-19-000016 R3 | 3,000,568 K | 6,863,968 - 3,863,400; printed Total shareholders' equity 3,000,568, no NCI on face | **FALSE HOLD** |
| mixed_vintage | OKE | 2021-12-31 | 0001039684-22-000015 R7 | 17,605.6 | 17,606.45 (= 23,621,613 - 6,015,163 K); stored mixes a millions-rounded equity copy | hold acceptable (stored off by 0.84M); solvable from the FY2021 10-K alone |
| mixed_vintage | RYN | 2015-12-31 | 0000052827-16-000059 R4; 0000052827-17-000004 R4 | 1,101.5 | 957.5 original / 954.2 restated | right |
| mixed_vintage | TSN | 2020-06-27 | 0000100493-20-000103 R4 | 19,638 | 19,554 | right |
| mixed_vintage | CWST | 2015-03-31 | 0001193125-15-177266 R2 | 657.3 | 675.3 (654,404 + 20,856 K) | right |
| mixed_vintage | PLNT | 2015-12-31 | 0001564590-16-014027 R2 | 728.9 | 700.3 | right |
| measurement_only | IPG | 2026-03-31 | 0000029989-26-000011 R2 | 41,162.6 | 39,549.4 (RNCI 343.2 on the face, FairValue element) | right |
| measurement_only (equity) | CG | 2015-06-30 | 0001527166-15-000006 R2 | 16,731.9 | parent partners' capital about 684 | right |
| partnership (equity) | BX | 2018-06-30 | 0001193125-18-242726 R2 | 14,794.4 | parent 7,047.3 | right |
| partnership (equity) | MPLX | 2019-06-30 | 0001552000-19-000064 R5 | 7,874 | parent 6,619 (preferred 1,005 in mezzanine) | right |
| partnership (equity) | WES | 2021-09-30 | 0001423902-21-000044 R4 | 3,096.4 | parent 2,954.7 | right |
| nci_not_read (equity) | SPAC 1819994 | 2020-09-30 | 0001213900-20-037159 R2 | 576.7 | printed equity 5.0 | right |

## Negative controls (seed `20261024-identity-v2-neg`)
Frame: 1,520 single-source `Liabilities`-tag rows since 2015 in plan companies; 0 of 1,520 in the V2 plan (DATA-INFERRED). STLD 2025-09-30 6,994,705K (0001104659-25-102052 R2), FE 2023-09-30 36,526 (0001031296-23-000061 R5), ECL 2018-06-30 12,043.1 (0001558370-18-006163 R5), NXPI 2020-03-29 10,253 (0001413447-20-000026 R4), SEIC 2017-09-30 318,856K (0000350894-17-000066 R2): all equal printed Total liabilities, untouched.

## Root causes for lane 3
1. **Off-face carrying elements (NI).** A carrying-amount element is not proof of a face line. Require the element to sit on the balance-sheet presentation (FilingSummary statement role / pre linkbase), or tie the result to the face: base - total equity - temp must equal the sum of the face liability lines or a printed total.
2. **NCI-inclusive total not consistent (FE).** Require SE_incl - SE = MinorityInterest when both are filed; if MinorityInterest is absent and SE_incl differs from SE, hold. DATA-INFERRED reach in V2 replacements: 150 cells / 14 companies (122 since 2015), FE 2017-03-31 to 2019-03-31 among them (SE_incl 36-175M against SE 6-8B).
3. **Dimension-only mezzanine (TRGP).** The temporary-equity line can be filed only with a class-of-stock member; sum the members (as the CAT debt lesson) or hold when a dimensioned temp-equity fact exists for the instant without an undimensioned one.
4. **"One filing" is not "one balance sheet" (DVN).** Terms must come from the balance-sheet statement for that instant in that filing (a later 10-Q's equity statement and a note assets figure do not qualify); else hold.
5. **False holds.** (a) mixed_vintage fires when the filing's values are identical to other copies (OXY): compare values, not accessions; (b) measurement_only fires on a note fact while the face shows no redeemable NCI (AWK): apply the trigger only to face elements; (c) the equity direction holds every company without NCI (BRO, CIK 0000079282; first version said AJG): accept "no NCI" when the face shows none (no MinorityInterest/NCI element in the statement role).

## Untested scope
The 16 equity replacements; 16 of 17 fills; the 237 temp_incl cells beyond 4; Entergy-type combined filings; pre-2015 beyond CVS/HCA; second reader. Clean rows are clean rows, not a population claim.
