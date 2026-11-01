verify/msft-hd-capex-cash-2026-11-01 (verdict on rule_run 9f1a0908-ab25-48b9-b25f-88de9e1c84f0, cells.capex_da_cash_debt@1; file sha256 6f53c9456bc1, origin/work/cash-flow/da-capex 30b5504)
Seed 20261104. Source: analytics.canonical_fact where rule_run_id = 9f1a0908 and company_id in (4 MSFT, 1236 HD). SEC requests: 71 (sec.gov R pages, 4/s). Evidence class: FILING-CHECKED.

# Verify: MSFT and HD post-load draw, capex and cash (2026-11-01, Verifier scrooner-1a)

## Result
Error rate 0 of 30 shown cells: capex 15 of 15 right, cash 15 of 15 right. Of the 30, 11 are derived quarters (YTD minus prior YTD, Q4 = FY minus 9M); all 11 are right against the original-vintage filings. MSFT Q4 FY2026 capex of 35,802M (double the year before) is right: the FY2026 10-K's 12-month line minus the Q3 10-Q's 9-month line.
D&A: no MSFT or HD cell loaded. MSFT is correctly held (combined line). HD's D&A holds are false holds (see below).
cell_proof: 0 rows for MSFT and HD at draw time; this draw does not lean on it.

## Method
Rows matched by XBRL element from the R page HTML (defref), not by label; columns by end date within 10 days and by the months header. Capex is PaymentsToAcquirePropertyPlantAndEquipment (MSFT) / PaymentsToAcquireProductiveAssets (HD) on the cash flow statement. Cash is CashAndCashEquivalentsAtCarryingValue on the balance sheet. Shown value must equal face x scale within half a million.

## Sample
Per company and family: first, last, two seeded derived quarters, rest seeded random (8 MSFT + 7 HD per family). Population: MSFT capex 63, cash 50; HD capex 63, cash 51.

## Cell table
| Co | Data point | Period | Why | Shown $M | Face $M | Verdict | Evidence |
|---|---|---|---|---|---|---|---|
| MSFT | capex | 2014-01-01 to 2014-03-31 | first | 1,192 | 1,192 | RIGHT | R7.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2014-03-31/3m x1000000 |
| MSFT | capex | 2016-10-01 to 2016-12-31 | random | 1,988 | 1,988 | RIGHT | R7.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2016-12-31/3m x1000000 |
| MSFT | capex | 2017-07-01 to 2018-06-30 | random | 11,632 | 11,632 | RIGHT | R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2018-06-30/Nonem x1000000 |
| MSFT | capex | 2018-10-01 to 2018-12-31 | random | 3,707 | 3,707 | RIGHT | R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2018-12-31/3m x1000000 |
| MSFT | capex | 2020-04-01 to 2020-06-30 | random | 4,744 | 4,744 | RIGHT | 0001564590-20-034944 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2020-06-30/Nonem x1000000 MINUS 0001564590-20-019706 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2020-03-31/9m x1000000 |
| MSFT | capex | 2024-04-01 to 2024-06-30 | derived | 13,873 | 13,873 | RIGHT | 0000950170-24-087843 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2024-06-30/12m x1000000 MINUS 0000950170-24-048288 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2024-03-31/9m x1000000 |
| MSFT | capex | 2025-04-01 to 2025-06-30 | derived | 17,079 | 17,079 | RIGHT | 0000950170-25-100235 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2025-06-30/12m x1000000 MINUS 0000950170-25-061046 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2025-03-31/9m x1000000 |
| MSFT | capex | 2026-04-01 to 2026-06-30 | last | 35,802 | 35,802 | RIGHT | 0001193125-26-323660 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2026-06-30/12m x1000000 MINUS 0001193125-26-191507 R6.htm us-gaap:PaymentsToAcquirePropertyPlantAndEquipment col=2026-03-31/9m x1000000 |
| HD | capex | 2013-02-04 to 2014-02-02 | first | 1,389 | 1,389 | RIGHT | R8.htm us-gaap:PaymentsToAcquireProductiveAssets col=2014-02-02/Nonem x1000000 |
| HD | capex | 2014-02-03 to 2014-05-04 | random | 287 | 287 | RIGHT | R6.htm us-gaap:PaymentsToAcquireProductiveAssets col=2014-05-04/3m x1000000 |
| HD | capex | 2014-08-04 to 2014-11-02 | derived | 368 | 368 | RIGHT | 0000354950-14-000047 R6.htm us-gaap:PaymentsToAcquireProductiveAssets col=2014-11-02/9m x1000000 MINUS 0000354950-14-000032 R6.htm us-gaap:PaymentsToAcquireProductiveAssets col=2014-08-03/6m x1000000 |
| HD | capex | 2018-10-29 to 2019-02-03 | derived | 731 | 731 | RIGHT | 0000354950-19-000010 R7.htm us-gaap:PaymentsToAcquireProductiveAssets col=2019-02-03/12m x1000000 MINUS 0000354950-18-000065 R6.htm us-gaap:PaymentsToAcquireProductiveAssets col=2018-10-28/9m x1000000 |
| HD | capex | 2019-05-06 to 2019-08-04 | random | 565 | 565 | RIGHT | 0000354950-19-000057 R7.htm us-gaap:PaymentsToAcquireProductiveAssets col=2019-08-04/6m x1000000 MINUS 0000354950-19-000024 R7.htm us-gaap:PaymentsToAcquireProductiveAssets col=2019-05-05/3m x1000000 |
| HD | capex | 2022-01-31 to 2023-01-29 | random | 3,119 | 3,119 | RIGHT | R8.htm us-gaap:PaymentsToAcquireProductiveAssets col=2023-01-29/12m x1000000 |
| HD | capex | 2026-05-04 to 2026-08-02 | last | 880 | 880 | RIGHT | 0001628280-26-058715 R7.htm us-gaap:PaymentsToAcquireProductiveAssets col=2026-08-02/6m x1000000 MINUS 0001628280-26-038247 R7.htm us-gaap:PaymentsToAcquireProductiveAssets col=2026-05-03/3m x1000000 |
| MSFT | cash_and_equivalents | 2014-03-31 to 2014-03-31 | first | 11,572 | 11,572 | RIGHT | R5.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2014-03-31/Nonem x1000000 |
| MSFT | cash_and_equivalents | 2015-06-30 to 2015-06-30 | random | 5,595 | 5,595 | RIGHT | R5.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2015-06-30/Nonem x1000000 |
| MSFT | cash_and_equivalents | 2021-09-30 to 2021-09-30 | random | 19,165 | 19,165 | RIGHT | R4.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2021-09-30/Nonem x1000000 |
| MSFT | cash_and_equivalents | 2022-12-31 to 2022-12-31 | random | 15,646 | 15,646 | RIGHT | R4.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2022-12-31/Nonem x1000000 |
| MSFT | cash_and_equivalents | 2023-09-30 to 2023-09-30 | random | 80,452 | 80,452 | RIGHT | R4.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2023-09-30/Nonem x1000000 |
| MSFT | cash_and_equivalents | 2024-03-31 to 2024-03-31 | random | 19,634 | 19,634 | RIGHT | R4.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2024-03-31/Nonem x1000000 |
| MSFT | cash_and_equivalents | 2025-06-30 to 2025-06-30 | random | 30,242 | 30,242 | RIGHT | R4.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2025-06-30/Nonem x1000000 |
| MSFT | cash_and_equivalents | 2026-06-30 to 2026-06-30 | last | 20,935 | 20,935 | RIGHT | R4.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2026-06-30/Nonem x1000000 |
| HD | cash_and_equivalents | 2014-02-02 to 2014-02-02 | first | 1,929 | 1,929 | RIGHT | R2.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2014-02-02/Nonem x1000000 |
| HD | cash_and_equivalents | 2014-08-03 to 2014-08-03 | random | 4,216 | 4,216 | RIGHT | R2.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2014-08-03/Nonem x1000000 |
| HD | cash_and_equivalents | 2016-10-30 to 2016-10-30 | random | 3,589 | 3,589 | RIGHT | R2.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2016-10-30/Nonem x1000000 |
| HD | cash_and_equivalents | 2020-05-03 to 2020-05-03 | random | 8,696 | 8,696 | RIGHT | R2.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2020-05-03/Nonem x1000000 |
| HD | cash_and_equivalents | 2021-05-02 to 2021-05-02 | random | 6,648 | 6,648 | RIGHT | R2.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2021-05-02/Nonem x1000000 |
| HD | cash_and_equivalents | 2025-02-02 to 2025-02-02 | random | 1,659 | 1,659 | RIGHT | R3.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2025-02-02/Nonem x1000000 |
| HD | cash_and_equivalents | 2026-08-02 to 2026-08-02 | last | 2,085 | 2,085 | RIGHT | R2.htm us-gaap:CashAndCashEquivalentsAtCarryingValue col=2026-08-02/Nonem x1000000 |

## Withheld cells (avoidable holds)
HD depreciation_and_amortization_resolved: 22 cells held as held_pending_verifier, da_class multi_member, but each has ONE member, the cash flow line DepreciationDepletionAndAmortization. Checked 2 against the face: FY2013 (0000354950-14-000008 R8) prints 1,757 = held member value; Q1 FY2024 (2024-01-29 to 2024-04-28, R7) prints 837 = held member value. These are publishable values held by the classifier. File-wide: 1,366 single-member D&A holds at 155 companies carry the same multi_member label (not checked one by one).

## False holds
MSFT D&A (63 cells): reason line_presented_combined_with_others. MSFT prints "Depreciation, amortization, and other", so the hold is right.

## Findings for the builder
1. capex_da_cash_debt.d_and_a_face@21 labels single-member D&A cells multi_member and holds them (HD, 22 cells; 1,366 file-wide). Fix the class test to count members, then re-emit and reload. Owner: scrooner-15 lane.
2. Out-of-window cells: 3,585 of 46,823 loaded cells in this family (7.7%, 354 companies) end before 2015-01-01 (MSFT 9, HD 8), against the Jan 2015 window. The values sampled there are right (MSFT 2014-03-31, HD FY2013); they should not be loaded. Loader or emitter should drop end_date < 2015-01-01.
3. cell_proof has not run on MSFT and HD after the load; certificates need it.

## Requests and disk
SEC requests: 71. Downloads deleted: yes (sec_cache and the cell file removed after the draw).

## Untested scope
D&A values (none loaded for MSFT/HD); total_debt (not in this file); the other 983 companies; the is_core load (not yet applied); the 110 suspect derived-quarter keys (check after is_core).
