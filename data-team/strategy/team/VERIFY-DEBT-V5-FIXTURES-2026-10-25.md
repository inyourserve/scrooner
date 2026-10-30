# Verify: Debt V5 face-admission fixtures (origin/work/scrooner-25/slot-records e4f9830), 2026-10-25

Verifier 2. Each fixture's balance-sheet R page opened (element per row read from the R page's defref), plus COST's FY2018 debt note. FILING-CHECKED. The fixture checker itself (FSDS rows + cal) was not re-run; this checks the decisions against the face.

## Result: GATE FAILS on COST 2018-09-02 (shown 6,487M, total debt 6,577M). All 12 admission fixtures are decided correctly.

## Must-reject (each would double count)
| Fixture | Accession, R | Face | Verdict |
|---|---|---|---|
| CNP 2025-12-31 `OtherLongTermDebtNoncurrent` | 0001130310-26-000008 R6 | VIE securitization bonds 664 + Other long-term debt 19,902 = Total long-term debt, net 20,566 (`LongTermDebtNoncurrent`) | reject right (component of the member total) |
| D 2015-09-30 `OtherLongTermDebtNoncurrent` | 0001193125-15-363617 R6 | Long-term debt 19,790 + junior subordinated 1,370 + remarketable subordinated 2,085 = Total long-term debt 23,245 | reject right |
| WSO 2024-12-31 `LongTermLineOfCredit`, `FinanceLeaseLiabilityNoncurrent` | 0001193125-25-041730 R4 | revolver 0 + operating lease 321,715 + finance lease 15,475 = Total long-term obligations 337,190K (`LongTermDebtAndCapitalLeaseObligations`) | reject right. PERIMETER WARNING: that member total and the current `LongTermDebtAndCapitalLeaseObligationsCurrent` "Current portion of lease liabilities" 110,273K include OPERATING leases; WSO borrowings are 0 at this date. Any debt slot reading these two tags for WSO must be lease-inclusive, never borrowings |
| ICE 2016-12-31 `LongTermDebt` | 0001571949-17-000003 R2 | Long-term debt 6,364 = current 2,493 + noncurrent 3,871 | reject right |
| TXT 2021-01-02 `LongTermDebt` | 0000217346-21-000019 R4 | Manufacturing group: Long-term debt 3,707 = current 509 + noncurrent 3,198; Finance group long-term debt 662 (entity-axis blocks) | reject right |
| NFG 2019-03-31 `UnamortizedLossReacquiredDebtNoncurrent` | 0000070145-19-000013 R4 | not a liability row on the face (the only "unamortized" text is in the LTD line label) | reject right |

## Must-admit (real face debt)
| Fixture | Accession, R | Face debt | Verdict |
|---|---|---|---|
| AVGO 2018-05-06 `LongTermDebtCurrent` | 0001730168-18-000019 R2 | current 117 + long-term 17,481 = 17,598M | admit right |
| LMCA 2019-06-30 `DebtCurrent`, `LongTermDebtNoncurrent` | 0001558370-19-007718 R2 | 13 + 14,411 = 14,424M (tracking-stock blocks below are dimensioned) | admit right |
| LMCA 2019-09-30 `LongTermDebtNoncurrent` | 0001558370-19-010666 R2 | 14,707M (no current debt line this quarter) | admit right |
| ALSN 2025-09-30 `LongTermDebtCurrent`, `LongTermDebtNoncurrent` | 0001193125-25-257624 R2 | 5 + 2,393 = 2,398M | admit right |
| AR 2017-03-31 `LongTermDebtNoncurrent` | 0001558370-17-003802 R2 | 4,775,302K, no current debt line | admit right |
| NFG 2019-03-31 `LongTermDebtNoncurrent` | 0000070145-19-000013 R4 | 2,132,488K inside the capitalization block; current debt lines 0 | admit right |

## EW 0001099800-16-000044 (FY2015 10-K, R2)
Neither a securitization line nor "long-term debt due currently" is on this face, in either column: current liabilities are accounts payable 63.9 + accrued and other 412.3 = 476.2; long-term debt 599.9 (2014: 598.1). The fixture's two must-admit lines belong to some other EW filing; this one has nothing to admit. Fix the fixture (find the filing that prints 430 and 161) rather than expecting them here.

## face_admission_tie_pending (NFG under Total capitalization)
The hold is avoidable: on the same face, Total Capitalization 4,222,997K - Total Comprehensive Shareholders' Equity 2,090,509K = 2,132,488K = the LTD line exactly, so the capitalization identity confirms the value. List as a false hold (value right, withheld); resolve it with the capitalization tie.

## COST 2018-09-02 (0000909832-18-000013 R2, R39) - WRONG shown value
Face: "LONG-TERM DEBT, excluding current portion" 6,487M; no current debt line. Debt note R39: Total long-term debt, carrying value 6,577; less current portion 90 ("Included in other current liabilities in the consolidated balance sheets"); excluding current portion 6,487. The recorded verdict (replay30_v3: DISAGREES_with_lane3, slot 6,487, hold false) publishes 6,487, which omits the 90M current maturities. Lane 3's 6,577 is the right borrowings total. When the current portion sits inside a combined face line, the note's carrying total is required (or hold as face_note_gap_review, the class V4.1 named for exactly this cell); never publish the face-only noncurrent figure as total debt.

## Not tested
The checker's own run (FSDS rows + cals), replay values for the fixture companies, the finance-lease perimeter at COST.
