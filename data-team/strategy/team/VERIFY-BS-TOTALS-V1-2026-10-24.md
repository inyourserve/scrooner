# Verify: BS totals v1 (origin/work/scrooner-25/slot-records 68ed251), 2026-10-25

Verifier 2. Method as v0: read-only copy of the branch's `bs_replay.py` with a per-instant dump (reproduced 432 ties / 61 gaps; one connection, 20s), then the balance-sheet R page of the cell's own filing, face value first. FILING-CHECKED unless marked.

## Result: GATE FAILS on one class. AWK still shows a wrong liabilities value on 11 instants (all 2016-03-31..2018-09-30 cells that compute); everything else I checked that is shown is right. Separately, `hold_no_cal_for_dedup` creates many false holds.

## A. The three open questions
1. **TRGP 2021-09-30** (0001564590-21-054348 R2). There is no printed total liabilities line; the closing row is "Total liabilities, Series A Preferred Stock and owners' equity 15,972.7". Liability rows: Accounts payable 1,652.3; Accrued liabilities 240.2; Distributions payable 71.0; Interest payable 79.9; Liabilities from risk management activities 472.3 (`trgp_DerivativeLiabilityBeforeEffectsOfMasterNettingArrangementsCurrent`); Current debt obligations 352.6; **Total current liabilities 2,868.3**; Long-term debt 6,434.1; **Long-term liabilities from risk management activities 151.2 (`trgp_DerivativeLiabilityBeforeEffectsOfMasterNettingArrangementsNoncurrent`, a TRGP custom element)**; Deferred income taxes, net 78.7; Other long-term liabilities 290.8. Sum 9,823.1. The missing 151.2 is that custom noncurrent risk-management line, which the replay cannot read from companyfacts; the cell is held as needs_instance_reader (right to hold). The 749.7 Series A preferred is outside liabilities (mezzanine, class-member only).
2. **AWK 2017-12-31** (0001410636-18-000076 R2). Rows in order: Total common stockholders' equity 5,385 → Long-term debt 6,490 (`LongTermDebtAndCapitalLeaseObligations`) → **Redeemable preferred stock at redemption value 8 (`PreferredStockRedemptionAmount`)** → **Total long-term debt 6,498** (`awk_LongTermDebtIncludesRedeemablePreferredStockAtRedemptionValue`) → Total capitalization 11,883 → Current liabilities. The preferred is the row just ABOVE "Total long-term debt", i.e. INSIDE that total (6,490 + 8 = 6,498), not after it. Same at 2016-06-30 (5,850 + 11 = 5,861, 0001564590-16-022379 R2) and 2026-06-30 (redeemable preferred 3 inside Total long-term debt 14,046, 0001410636-26-000120). Correct liabilities: replace the Long-term debt member with the "Total long-term debt" subtotal (or add the preferred).
3. **Brown & Brown (CIK 0000079282)**. FY2018 10-K 0000079282-19-000006: R1 Document Period End Date Dec. 31, 2018; balance sheet R3 column "Dec. 31, 2018", Total shareholders' equity **3,000,568K**, total assets 6,688,668K. The 2019-01-01 instant exists only in the Q1 2019 10-Q (0000079282-19-000016 R3) as the ASC 842 adoption column (total assets 6,863,968K, lease lines only; no equity printed in that column). So the anchor instant is 2018-12-31; 2019-01-01 equity is not printed (it equals 3,000,568K only by A - L).

## B. Named re-checks (v1 value vs face)
| Cell | v1 | Face (locator from my v0 / identity reports) | Verdict |
|---|---|---|---|
| T 2026-06-30 | 299,920 | 0000732717-26-000297 R5 | right |
| OXY 2018-12-31 | 22,524 | 0000797468-19-000004 R2 | right |
| NI 2023-12-31 | 20,940.9 | 0001111711-24-000011 R6 | right |
| NI 2025-03-31 / 2025-09-30 | held (no_cal_for_dedup) | 22,159.1 / 23,161.1 (R5) | v0 wrong value removed; hold avoidable |
| MCK 2015-06-30 | 45,556 | 0000927653-15-000006 R4 | right |
| ET 2025-06-30 | held | 79,165 (0001276187-25-000086 R2) | wrong value removed; hold avoidable |
| DVN 2017-09-30 / 2018-03-31 | held | 15,625 / 15,591 | wrong values removed; holds avoidable |
| BRKR 2015-12-31 | 998.0 | FY2015 10-K 0001047469-16-010532 prints 1,730.9 - 732.9 = 998.0 | right (original vintage now) |
| BRKR 2019-03-31 | 1,298.7 (anchor) but per-instant state needs_instance_reader | lines sum 1,298.7 (0001104659-19-027788 R2) | value right; LATENT DEFECT: the member list contains the custom EQUITY element `OthersShareholdersEquity` ("Other shareholders' equity" 1,309.7); once an instance reader fills it the sum becomes wrong. Extend the equity guard to custom elements by balance/position |
| AWK 2016 era (2016-06-30, 09-30, 12-31) and 2017-12-31 | 12,542 / 12,722 / 13,254 / 14,089 | 12,553 / 12,733 / 13,264 / 14,097 | **WRONG** (redeemable preferred inside Total long-term debt; identity gap 8-11M now correctly exceeds the 1M tolerance, but the value is still produced) |
| TRGP 2021-09-30 | held (needs_instance_reader) | 9,823.1 | hold right |

AWK shown-wrong population (DATA-INFERRED from the dump, same mechanism): 11 instants 2016-03-31..2018-09-30, identity gap 7-11M = the preferred. If a gap state is meant to withhold publication, say so in the record; today the face_sum value is emitted.

## C. Fresh draw (seed random.Random(20261028); frame = v1 computed instants since 2015: 432 ties, 61 gaps; 292 held; v0 sample cells excluded; max 2 per company)
Ties 10/10 right: KKR 2025-09-30 323,078,973K printed (0001404912-25-000042); VLO 2019-03-31 30,316 (0001035002-19-000025); EMR 2023-12-31 19,958 (0000032604-24-000008); DIS 2023-07-01 92,841 = 203,783 - 102,056 - RNCI 8,886 (0001744489-23-000171); OXY 2015-06-30 21,067 (0000797468-15-000012; long-term debt now included); GE 2023-03-31 131,649 printed (0000040545-23-000136); BRKR 2023-12-31 2,836.6 printed (0000950170-24-023038); ET 2021-03-31 61,195 (0001276187-21-000050); ET 2019-06-30 58,295 (0001276187-19-000034); FE 2022-06-30 33,806 (0001031296-22-000053).
Gaps 5: BX 2016-06-30 10,926,238K, BX 2017-12-31 20,699,355K, KKR 2017-12-31 25,171,919K, KKR 2018-03-31 25,810,215K: printed totals, right; the gap is the cross-check's unread partnership NCI (BX "Non-Controlling Interests in Consolidated Entities / in Blackstone Holdings"; KKR "Noncontrolling Interests"), not a liabilities error. AWK 2016-06-30 12,542: WRONG (above).

## D. False holds (`hold_no_cal_for_dedup`)
FILING-CHECKED false holds (value held although the face gives it and v0 computed it right): WMT 2021-04-30 151,989 (0000104169-21-000042); WMT 2026-01-31 178,488 (0000104169-26-000055); NI 2016-09-30 14,255.6 (0001111711-16-000084); NI 2017-12-31 15,641.6 (0001111711-18-000008); MCK 2024-06-30 73,051 (0000927653-24-000098); EMR 2020-06-30 13,852 = 21,730 - 7,878 (0000032604-20-000033). Held cells whose face also gives a clean value (no v0 value to compare): AWK 2026-06-30 24,788 = 36,453 - 11,665 (redeemable preferred 3 inside debt); BRO 2025-12-31 17,418 = 29,991 - 12,573 (0001193125-26-046984); BRO 2020-03-31 4,102,504K = 7,582,345 - 3,479,841 (0001564590-20-019783). TRGP 2018-09-30 not adjudicated (my column reader failed on that page).
Reach (DATA-INFERRED): 292 cells held as hold_no_cal_for_dedup; 129 of them were v0 identity ties (WMT 34, NI 32, MCK 15, EMR 13, FE 12, ET 6, AWK 6, DVN 5, BRKR 5, VLO 1). Not all v0 ties were right (MCK's equity "Other", AWK), so 129 is an upper bound on false holds; BRO has 47 held instants and 0 computed. A missing calc file should fall back to the face-sum when the sum equals LSE - total equity - printed mezzanine on the same accession, not to a hold.

## Untested
GE multi-entity layout, cells with dimension-only mezzanine, TRGP 2018 page, a second reader.
