# Tag Expert scorecard

Each builder question or claim I hand out: my answer, its evidence level, and whether the Verifier (or a filing) later confirmed it. A claim that turns out wrong stays here with the cause, and CHANGELOG.md gets the lesson.

| # | Date | Asked by / handed to | Question or claim | My answer (short) | Evidence | Later confirmed? |
|---|---|---|---|---|---|---|
| 1 | 2026-11-09 | mapping builder | Why is shares_outstanding_resolved at 18 of 632? | The mapper excludes parentheticals and never reads EQ; `CommonStockSharesOutstanding` sits in the BS parenthetical at 407 companies and on EQ at 254 | DATA-INFERRED (fsn.* + mapping.py) | pending |
| 2 | 2026-11-09 | mapping builder | DPS 64 of 632 | `CommonStockDividendsPerShareDeclared` sits on the EQ parenthetical at 215 and EQ face at 35; never read | DATA-INFERRED | pending |
| 3 | 2026-11-09 | mapping builder | net income gap 63 | 30 companies tag the parent bottom line `NetIncomeLossAvailableToCommonStockholdersBasic` with no preferred line; ProfitLoss − NCI identity holds at CAT and ES | DATA-INFERRED (FSN rows, values) | pending; needs filing check |
| 4 | 2026-11-09 | mapping builder | interest gap 205 | ~87 recoverable by the existing note fill; ~118 not: net-only (≈75 of 98), no face line, custom tags (18). Net tags must not be mapped | DATA-INFERRED | pending |
| 5 | 2026-11-09 | mapping builder | IS statement-class trap | GATX (IS classed CI, OCI classed IS), Revvity (IS classed UN): every IS concept blank | DATA-INFERRED (fsn.report/line) | pending |
| 6 | 2026-11-09 | cash-flow lane | buyback/dividend tags missing | `PaymentsForRepurchaseOfEquity` (10 + 6, coexists with the common tag in 13 of 16: sum-or-parent check); custom excise-inclusive buyback tags; `PaymentsOfCapitalDistribution` mixed perimeter (Up-C/NCI) | DATA-INFERRED | pending |
| 7 | 2026-11-09 | mapping builder, cash-flow lane | Two mapped face lines per key | revenue blanked as conflicting_values_in_filing at 33 companies (RCFC component + Revenues total; excise pairs), CFO at 16 (continuing + total) | DATA-INFERRED (fsn.* + select.py) | pending |
| 8 | 2026-11-09 | release prep | Debt lane perimeter vs debt card | no conflict with dropping the seeds; seven double-count traps (CP inside ShortTermBorrowings, LongTermDebt incl. current, leases inside DebtCurrent/combined tags, bank FHLB, segment-only debt, face value, capitalization format) | FILING-CHECKED (card rows) | pending |
| 9 | 2026-11-09 | (card) | 40 of 427 mapped interest lines are gross tags on a 'net' label | Verifier stratum | DATA-INFERRED | pending |

Calibration: 0 of 9 confirmed yet (all new). SEC filing checks were not possible this run (no declared SEC_USER_AGENT in the cloud session).
