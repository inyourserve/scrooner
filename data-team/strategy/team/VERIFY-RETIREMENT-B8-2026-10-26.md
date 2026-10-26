# Verify: retirement Family B, plan 8 (work/data-engineer/derivation-gate dad6c3b; dryrun_B8), 2026-10-26

Verifier 2. Seed random.Random(20261114). Files: dryrun_B8/B_proxy_form_cells.csv and retirement_dryrun_summary.json. Claimed counts: cohort 783 = 646 replaced + 137 removed (44 proxy_only_source, 46 proxy_filed_copies_disagree, 36 derived_inputs_disagree, 10 derived_inputs_unverified, 1 nci); population re-derivation 669 same, 125 corrected, 115 filled. Cohort counts reproduced. Inputs read on income statements: kit 4d0dbf6 `fetch_statements` (213 requests), plus my own per-Report reader for the 35 pages the kit misread (about 70 requests). Read-only DB on one connection with a 20s timeout. FILING-CHECKED unless marked.

## Result: GATE FAILS on false removals.
- **10 right derived quarters hidden as derived_inputs_unverified:** every VRSN and SAIC cell in the cohort. Both companies tag their only bottom line as ProfitLoss and have no NCI line, and the re-derivation skips NCI-inclusive tags without the MA-style face check.
- **No wrong value shown in the sample**, with one precision defect: BAH Q4 FY2025 (section 5).
- The HIDE ruling is applied correctly to the restated quarters.

## 1. Still shown (all right; every input copy agrees, so no restatement hides them)
- **BAH Q4 FY2024 127,956K** = 605,706 (FY2024 10-K 0001443646-24-000075) - 477,750 (nine months, comparative column of 0001443646-25-000012). The other FY copy, 606,000, is rounding.
- **SM Q4 2024 188,278K** = 770,293 (0000893538-25-000008) - 582,015 (0000893538-25-000138).
- **WDAY Q4 FY2022 -73,253K** = 29,373 (0001327811-23-000024) - 102,626 (0001327811-22-000184). Also WDAY Q4 FY2023 -125,697K.
- **STE Q4 FY2025 145,672K** = attributable 614,641 (0001757898-25-000005) - 468,969 (0001757898-25-000002).

## 2. Now hidden as derived_inputs_disagree (genuine different vintages, so hidden per the founder ruling)
- **EQH Q4 2021:** FY -439 (0001333986-22-000006) vs 1,755 restated (0001333986-24-000009). EQH Q4 2022-2024 are also restated (9M copies 2,574 vs 2,091; FY 1,307 vs 1,280).
- **HOOD Q4 2021:** 9M -3,263,165K (0001783879-21-000054) vs -3,264M in the 2022 10-Q (0001783879-22-000230). -3,263.165M would round to -3,263, so the later figure is a different value, not a rounding.
- **HUBS Q4 2022:** FY -112,749 (0000950170-23-003077) vs -107,347 (0000950170-25-018873). HUBS Q4 2023 is also restated.

## 3. Named
- **MA, 10 cells:** shown 8,687 / 9,930 / 11,195 / 12,874 / 14,968M. Right.
- **LNG Q4:** -1,323M = -2,343 - (-1,020); 3,937M = 1,428 - (-2,509); 1,377M = 9,881 - 8,504. All nine-month figures read on the 10-Q faces (0000003570-22-000106, -23-000097, -24-000120). Also Q4 2024 977M and Q4 2025 2,302M (5,330 - 3,028).
- **CAG attributable:** Q4 FY2023 37.5M = 683.6 - 646.1; Q4 FY2024 -567.3M = 347.2 - 914.5. Both nine-month figures are the attributable lines (0001437749-24-011081, 0001558370-25-004399).

## 4. Sample: 20 of 73 corrected + 20 of 172 filled (population; I count more than the claimed 125 / 115)
- 40 of 40: the arithmetic equals the replacement.
- Each input agrees across its copies (rounding only), and was found on the face in its column for all but 8. The 8 not read are NOW, 4311, 4749 and 1546 pages titled "Comprehensive Income" and VRSN FY; these are DATA-INFERRED.
- Examples: ANET Q4 2023 613,636K; CHE Q4 2021 74,625K (stored garbage -193,656,450); MCD Q4 2023 2,039.0M; CSGP Q4 2021 92,900K; ST Q4 2024 5,787K.

## 5. 15 of 36 derived_inputs_disagree, and 10 of 10 derived_inputs_unverified
- **15 disagree removals: all right under the ruling.** Each has an input with filed copies from different vintages that differ beyond rounding: PFG FY2021 1,710.6 vs 1,580.2; MET 6,554 vs 6,855; MPWR, DXCM, CRWD, CHWY x2, WSM, GTLB, OMF, HUBS x2, EQH x3. HUBS, HOOD and EQH are FILING-CHECKED; the rest are DATA-INFERRED from core.fact copies.
- **10 unverified removals: false removals of right values.**
  - VRSN Q4 2022-2025 (8 cells): e.g. 264.7M = 817.6 - 552.9, with nine months 552.9 on the face (0001014473-23-000038).
  - SAIC Q4 FY2026 (2 cells): 85M = "Net income" 358 (0001571123-26-000029) - 273.
  - Fix: allow ProfitLoss when the face prints no NCI line (the MA rule).
- **Precision defect: BAH Q4 FY2025 shown 192,705K** = 935,000,000 - 742,295K.
  - The FY2025 10-K (0001443646-25-000076) and FY2026 10-K print 935 in millions, so the shown thousands are not supported by any filing.
  - The proxy's 935,030K (DATA) suggests about 192,735K.
  - 10 cohort derived quarters mix a millions-rounded input with a precise one (BAH, TJX, ABNB, CSGP and others). Show them at the coarser unit (192.7M), or use a precise copy.

## Findings for the kit owner
`fetch_statements(...,("IS",))` picks note pages ("Income Taxes", "Net Income Per Share", "Loss per Share", "Operations"). It also drops the first value column on statements with 3-month plus year-to-date columns: BAH, SM, WDAY, STE and LNG were read one column shifted. 35 pages had to be re-read by hand.
