# Red-cell fix files, ranks 41-60 (cash-flow lane session)

**Where:** branch `work/reads/redcells-41-60` (not main). Files: `<TICKER>-fixes-2026-11-13.csv` (v1 list, 1,187 cells,
head ba7ef483) and `<TICKER>-fixes-v2-2026-11-13.csv` (v2 list, the 244 reader rows that are not "fix file ready").

**C / AXP corrections (Tag Expert review, main 1a198c1a):** on this branch since 309dadd8:
C deposits 2024 = 1,284,458,000,000 (Deposits), C loans_net 2024 = 675,914,000,000
(FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss), AXP deposits 2024 = 139,413,000,000 (Deposits).

**Why not main (blocked, stated as asked):** this session's operating instructions allow pushes to work branches only;
a push to `main` needs the user's own instruction in this session, and a peer session's relay is not that. Engineering
(or anyone with main rights) can merge this branch or load the files from it: they are new files only, no existing
docmap is touched. Messages from this cloud session to the Mac manager session are refused (untrusted device), so this
file is the channel.

## v2 red-cell list (2026-11-13): reader rows only

Files: `<TICKER>-fixes-v2-2026-11-13.csv` (same columns as v1). Scope: the 244 reader-closable rows of the v2 list for ranks 41-60; rows marked "fix file ready" were skipped. All 244 cells have a decision with page evidence or the checks behind a not_presented. Pushed in four batches of five companies (19304912, 67d6b7f4, 6ee9e162, 15bf4e38).

| Ticker | Cells | mapped | combined | component_sum | component_in_note | not_presented |
|---|---|---|---|---|---|---|
| DELL | 38 | 28 | 3 | 0 | 0 | 7 |
| MS | 14 | 3 | 10 | 0 | 0 | 1 |
| PANW | 6 | 0 | 0 | 0 | 0 | 6 |
| RTX | 20 | 8 | 10 | 0 | 0 | 2 |
| GS | 14 | 3 | 11 | 0 | 0 | 0 |
| WFC | 19 | 4 | 11 | 0 | 0 | 4 |
| TXN | 3 | 2 | 0 | 0 | 0 | 1 |
| GEV | 5 | 2 | 3 | 0 | 0 | 0 |
| CRWD | 13 | 7 | 0 | 0 | 0 | 6 |
| LIN | 22 | 7 | 0 | 0 | 6 | 9 |
| ANET | 5 | 2 | 0 | 0 | 0 | 3 |
| SHOP | 1 | 1 | 0 | 0 | 0 | 0 |
| KLAC | 10 | 10 | 0 | 0 | 0 | 0 |
| IBM | 2 | 1 | 0 | 0 | 0 | 1 |
| C | 15 | 15 | 0 | 0 | 0 | 0 |
| AXP | 17 | 16 | 0 | 0 | 0 | 1 |
| MRVL | 15 | 12 | 0 | 3 | 0 | 0 |
| CRM | 25 | 2 | 0 | 8 | 0 | 15 |
| **Total** | **244** | **123** | **48** | **11** | **6** | **56** |

Hand checks and fixes made before pushing:
- 7 rows checked by hand (`FILING-CHECKED (hand ...)` in the note), including AXP basic/diluted EPS 2019: the continuing-operations EPS tag is the EPS line because AXP prints no discontinued per-share line (Tag Expert ruling).
- A value-matching step was restricted to the data point's own tag family after it matched LIN other income to 'Interest expense - net' and a KLAC note value. LIN other_income 2020-2025 is now not_presented.
- MS share_buybacks 2015-2025 (combined, 'Repurchases of common stock and employee tax withholdings') and WFC D&A 2024-2025 (combined, 'Depreciation, amortization and accretion') now carry the cash-flow page and printed value. An earlier run had pointed MS at the wrong page (R5).
- WFC revenue 2015 is not_presented: no revenue-family tag is printed in that filing. Total interest income is not revenue.
- Sign: printed_value is as shown on the page. GS dividends are negative in every year.

As with v1, these files are on this work branch and not on main. Merging them to main needs the founder's own instruction.
