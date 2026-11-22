# Card family: Cash and restricted cash (written 2026-10-19 by the Tag Expert)
<!-- HAND-WRITTEN card: all prose outside the generated block at the end is written by hand and never rewritten. The block between the BEGIN/END GENERATED markers is rebuilt from library.csv by data-team/tags/library/build_library.py. -->

Tags: `us-gaap:Cash`, `CashAndCashEquivalentsAtCarryingValue`, `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` (CCRC), `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations` (CCRC-incl-DO), `RestrictedCash`, `RestrictedCashCurrent`, `RestrictedCashNoncurrent`, `RestrictedCashAndCashEquivalents`, `RestrictedCashAndCashEquivalentsAtCarryingValue`, `CashAndDueFromBanks`, `CashCashEquivalentsAndShortTermInvestments`.
Method and limits: as in `revenue.md`. Instants; Frames CY2013Q4I / CY2023Q4I, calendar year-end filers only. DB reads skipped (connections 14-18 > 12).

## 1. Official meaning (taxonomy 2025, read 2026-10-19; all instant / debit)
| Tag | Definition (shortened) |
|---|---|
| Cash | Currency on hand and demand deposits with banks; "Excludes cash and cash equivalents within disposal group and discontinued operation." |
| CashAndCashEquivalentsAtCarryingValue | Cash plus cash equivalents (short-term, highly liquid, near maturity) |
| CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents | Cash and cash equivalents **plus** restricted cash and equivalents, "attributable to **continuing operation**" |
| ...IncludingDisposalGroupAndDiscontinuedOperations | Same total "including ... discontinued operation" |
| RestrictedCash | Cash restricted as to withdrawal or usage (pure cash) |
| RestrictedCashCurrent / RestrictedCashNoncurrent | Restricted cash by classification |
| RestrictedCashAndCashEquivalents | Cash and cash equivalents restricted as to withdrawal or usage |
| RestrictedCashAndCashEquivalentsAtCarryingValue | Same, "classified as current" |
| CashAndDueFromBanks | Banks: currency and coin, items in collection, noninterest-bearing due from banks and the Fed |
| CashCashEquivalentsAndShortTermInvestments | Cash, equivalents and short-term investments (broader, includes investments) |
No tag is deprecated in 2025. `CashAndCashEquivalentsPeriodIncreaseDecrease` is absent from the 2025 taxonomy (older name).

## 2. Who reports it (Frames, DATA-INFERRED; bank-like in brackets)
| Tag | CY2013Q4I | CY2023Q4I |
|---|---|---|
| Cash | 1,615 (27) | 1,171 (16) |
| CashAndCashEquivalentsAtCarryingValue | 7,599 (534) | 5,349 (233) |
| CCRC (restricted-inclusive total) | **7 (0)** | **5,475 (363)** |
| RestrictedCash | none | 1,076 (41) |
| RestrictedCashCurrent / Noncurrent | none | 831 (6) / 625 (0) |
| RestrictedCashAndCashEquivalents(AtCarryingValue) | 919 (10) | 550 (7) |
| CashAndDueFromBanks | 536 (518) | 381 (340) |
Findings:
- **Era break at ASU 2016-18 (statement of cash flows must include restricted cash, effective 2018):** CCRC went from 7 filers to 5,475. Before the break the cash-flow ending balance was plain cash; after, it is the restricted-inclusive total. Any series that mixes the two tags across 2017/2018 changes perimeter with no real change in cash.
- In CY2023, 5,349 file CCE-at-carrying-value, 5,475 file the total, 4,380 file both, 1,095 file the total **without** CCE (they use a different balance sheet cash tag or custom tag), 511 file `Cash` without CCE, 660 file both `Cash` and CCE. Union of the three: 6,586 filers.
- Banks mostly use `CashAndDueFromBanks` (340 of 381) as a balance-sheet component and CCE/CCRC for the combined figure.
- SIC-family split not done (DB).

## 3. How filers use it (filings opened)
| Filing | Row | Tag | Observation |
|---|---|---|---|
| AAPL 0000320193-25-000079 R5/R8 (me) | Balance sheet "Cash and cash equivalents" 35,934M; cash-flow "Cash, cash equivalents, and restricted cash and cash equivalents, ending" 35,934M | CCE-at-carrying-value; CCRC | equal for AAPL FY2025 (no restricted cash); beginning balance 29,943M is the same on both |
| AMZN 0001018724-26-000004 R7/R3 (me) | Balance sheet 86,810M; cash-flow end "CASH, CASH EQUIVALENTS, AND RESTRICTED CASH" 90,106M | CCE; CCRC | **differ by 3,296M** (restricted cash) |
| PGR 0000080661-26-000086 R4 (me) | "Cash and cash equivalents" 125M; "Restricted cash and cash equivalents" 13M; "Total cash, cash equivalents, restricted cash, and restricted cash equivalents" 138M | **`Cash`**; `RestrictedCashAndCashEquivalents`; CCRC | an insurer uses plain `Cash` for the line labelled cash AND cash equivalents; the three tags sum exactly |
| ARCC 0001287750-26-000006 R3 (me) | "Cash and cash equivalents" 638M; "Restricted cash" 286M | CCE; `RestrictedCash` | two separate balance-sheet lines; no total tag on the face |
| HTZ 0001657853-26-000008 R3 (me) | cash 565M; restricted 602M; total 1,167M | CCE; `RestrictedCashAndCashEquivalents`; CCRC | restricted cash is a different tag from ARCC's |
| GE 0000040545-26-000008 cash flow (me) | "Cash, cash equivalents and restricted cash at December 31" | **CCRC-incl-DO** (`...IncludingDisposalGroupAndDiscontinuedOperations`) plus custom continuing-ops total `ge_CashCashEquivalentsRestrictedCashandRestrictedCashEquivalentsIncludingAssetsHeldforSale` | a filer with discontinued operations uses the including-DO tag and a subtract line "Less cash ... of discontinued operations" |
| PLD 0001193125-26-051453 R8 (me) | balance sheet CCE 1,145,647K; cash-flow end uses the including-DO tag | CCE; CCRC-incl-DO | |
| CVX 0000093410-26-000078 R5 (me) | "Cash and cash equivalents" 6,293M | **custom `cvx_CashAndCashEquivalentsExcludingTimeDeposits`**; cash-flow end 7,285M uses the standard CCRC | the balance-sheet cash is a custom tag, so a standard-tag lookup finds only the cash-flow total (7,285M, which includes restricted cash and time deposits) |
| Banks | EWBC 0001069157-26-000009 [32]/me | "Cash and due from banks" 656,125K = `CashAndDueFromBanks`; "Cash and cash equivalents" 4,188,139K = CCE | the combined figure is the CCE; do not take `CashAndDueFromBanks` as cash for banks |
| Broker-bank | AX 0001299709-26-000060 [32]/me | cash 1,108,633K (CCE); restricted 199,169K (`RestrictedCashAndCashEquivalents`); total 1,307,802K (CCRC) | |
| Regional bank | ZION [32]/me | "Cash and due from banks" 683M | `CashAndDueFromBanks`; cash-flow begin 651M uses CCRC |

## 4. Siblings and confusables
- `Cash` (demand deposits only, excl. equivalents) vs CCE (cash + equivalents) vs CCRC (adds restricted cash). PGR shows that the filer's chosen tag can be `Cash` even when the row is "cash and cash equivalents".
- CCRC (continuing operations) vs CCRC-incl-DO (including discontinued operations): GE uses the second with a reconciling line.
- `RestrictedCash` (pure cash) vs `RestrictedCashAndCashEquivalents` (cash and equivalents) vs `...AtCarryingValue` (current only) vs Current/Noncurrent splits; a filer picks one of several families (ARCC, HTZ, AX).
- `CashAndDueFromBanks` (bank component) vs bank CCE.
- `CashCashEquivalentsAndShortTermInvestments` includes investments and is not cash.

## 5. Known misuses and company quirks
- IVDA: authoritative cash fact is a TWD-unit component (core.fact 45910028; 0001641172-25-015284 R34/R56) -> require unit USD [carried].
- FDCT: plain-cash tag filed as cash plus restricted cash in a 10-Q/A [carried].
- MGNC (0001683168-26-007689 R6), LRDC (0001199835-26-000359 R6): cash-flow total tag used for a continuing-operations subtotal once discontinued operations appear [carried].
- NEW (me): CVX balance-sheet cash is a custom tag.
- NEW (me): PGR uses `Cash` for cash and cash equivalents (so "Cash" is not "cash excluding equivalents" there).
- NEW (me): AMZN, HTZ, AX show balance-sheet cash and cash-flow ending cash differ by exactly the restricted amount; a free-cash-flow or net-cash calculation that uses the cash-flow ending tag against the balance-sheet tag will be off by restricted cash.

- NEW (me, 2026-10-21, FILING-CHECKED presentation): Cummins 0000026172-26-000009 R5 tags its balance-sheet row "Cash and cash equivalents" 2,845M with the restricted-inclusive total `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents` (whether restricted cash is inside was NOT verified); Badger Meter 0001193125-26-054739 R2 tags "Cash and cash equivalents" 226,016K with plain `Cash`. Population (FY2025 10-K face, DATA-INFERRED): the restricted-inclusive tag is the BS cash row at 272 filers, 207 of them labelled plain "cash and cash equivalents"; `Cash` is the cash row at 440 (shells 123); CF ending cash equals BS cash at 2,128, equals BS cash + restricted rows at 719, needs reconciliation at 660 (banks 191). Detail: R2 report sec. 11.

## 6. Mapping verdict
- `CashAndCashEquivalentsAtCarryingValue`: **safe as the cash-and-equivalents line** when present (AAPL, AMZN, ARCC, HTZ, PLD, EWBC, AX FILING-CHECKED); require unit USD (IVDA).
- `Cash`: acceptable only where it is the filer's face cash-and-equivalents row (PGR); never fill `Cash` ahead of CCE without a coexistence check (MOJO case [28]: CCE = 0 alongside `Cash`).
- CCRC: **a different concept** (restricted-inclusive, cash-flow statement); safe for the cash-flow ending balance from 2018; never a substitute for balance-sheet cash; for GE-type filers prefer the including-DO tag only with the discontinued-operations line.
- `RestrictedCash*` family: component; sum only inside one family (ARCC `RestrictedCash`; HTZ/AX `RestrictedCashAndCashEquivalents`); do not add to CCE if the filer's CCE already includes it (check the face).
- `CashAndDueFromBanks`: bank component only; never bank cash.
- Evidence: FILING-CHECKED for the rows named; populations DATA-INFERRED. Verified by: Tag Expert (me).

## Ranks 1-50 relay (Ritwik relay 2026-11-11, work/tag-library/ranks-1-50 aea0cf4 data-team/47-fsn-store/company_tag_map/ranks_1_50.csv (evidence_adsh + label per row); DATA-INFERRED, not yet filing-checked by the Verifier)
- Custom or variant cash tags in the standard position: GE 2015-2017 `CashAndEquivalentsExcludingAssetsHeldForSale`; CVX "…ExcludingTimeDeposits" (2019-2022 and 2024+); MS pre-2020 `CashAndDueFromBanks` (bank-style cash line).

> See also (FILING-CHECKED, Dhairya 2026-11-11): cards/fsn-cash-flow.md, fsn-balance-sheet-assets.md, fsn-balance-sheet-liabilities-equity.md, fsn-income-statement.md; conflicts settled in decisions/TAG-EXPERT-RECONCILE-FSN-CARDS-2026-11-11.md.

## Reconcile 2026-11-11 (final)
- BS `CashCashEquivalentsRestrictedCash…` = cash when it is the sole cash line with no restricted wording (GILD 7,564M, DHR 4,615M, FITB 4,374M); a label naming restricted cash is served as printed, labelled "includes restricted cash" (CB 0000896159-26-000005 BS l9; Dhairya). Bank cash = the BS line(s) equal to CF ending cash; `CashAndDueFromBanks` beside interest-bearing deposits is a component (PNC). LITE: cash tagged `CashAndCashEquivalentsFairValueDisclosure` (filer error; map by label, flag).

- Bank cash split across BS lines (JPM 343,338M): serve the CF statement's printed ending-cash line, labelled; never sum the BS lines (Dhairya 2026-11-12).

- Bank cash (refined, Dhairya 2026-11-12): the BS total cash line when printed (COF 57,434M), else the CF statement's printed ending cash; never a sum of BS lines. PGR cash on `Cash` (125M). CB perimeter change 2018+ (incl. restricted).

<!-- BEGIN GENERATED: tag library rows (build_library.py from library.csv, resolver-all110-.92). Do not edit by hand: the next build rewrites this block. -->
## From the tag library (generated)

Resolver resolver-all110-.92. 6 elements named in this card have library knowledge. Every element: `data-team/tags/library/library.csv` or `browser.html`.

### `CashAndCashEquivalentsAtCarryingValue`
- **Meaning:** Cash and Cash Equivalent (us-gaap, instant, debit). Amount of cash and cash equivalent. Cash includes, but is not limited to, currency on hand, demand deposit with financial institution, and account with general characteristic of demand deposit. Cash equivalent includes, but is not limited t...
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents; role cash_and_equivalents:primary#1
- **Rules:** B05; B06; B07; B08; family resolve_all.NARROW[cash_and_equivalents]
- **Evidence:** 103 companies, 1156 served, 22866 proven, 108 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 2 open hit(s) at 2 companies, e.g. DELL cash_and_equivalents 2015-01-30 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (2)
- **Deprecation:** replaces FreshStartAdjustmentIncreaseDecreaseCashAndCashEquivalents@2021; PostconfirmationCashAndCashEquivalents@2021; PreconfirmationCashAndCashEquivalents@2021

### `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`
- **Meaning:** Cash, Cash Equivalent, Restricted Cash, and Restricted Cash Equivalent, Continuing Operation (us-gaap, instant, debit). Amount of cash and cash equivalent, and cash and cash equivalent restricted to withdrawal or usage; attributable to continuing operation. Cash includes, but is not limited to, currency on hand, demand deposit with financial institution, and...
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents; role cash_and_equivalents:primary#6
- **Rules:** B05; B06; B07; B08
- **Evidence:** 17 companies, 84 served, 666 proven, 6 certified cells; last verified 2026-11-15
- **Known problems:** pattern P05 comparative_only_year_hidden: 4 open hit(s) at 4 companies, e.g. CRWD cash_and_equivalents 2018-01-31 (export) (pattern_hits.csv)
- **Pattern hits:** P05 (4)

### `CashAndDueFromBanks`
- **Meaning:** Cash and Due from Banks (us-gaap, instant, debit). For banks and other depository institutions: Includes cash on hand (currency and coin), cash items in process of collection, noninterest bearing deposits due from other financial institutions (including corporate credit unions), and noninte...
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents; role cash_and_equivalents:primary#4
- **Rules:** B05; B06; B07; B08
- **Evidence:** 4 companies, 21 served, 91 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CashAndEquivalentsExcludingAssetsHeldForSale`
- **Meaning:** (no taxonomy label) (custom)
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents
- **Rules:** none
- **Evidence:** 1 companies, 4 served, 7 proven, 0 certified cells; last verified 2026-11-15
- **Known problems:** none recorded
- **Pattern hits:** none

### `CashAndCashEquivalentsFairValueDisclosure`
- **Meaning:** Cash and Cash Equivalents, Fair Value Disclosure (us-gaap, instant, debit). Fair value portion of currency on hand as well as demand deposits with banks or financial institutions. Includes other kinds of accounts that have the general characteristics of demand deposits. Also includes short-term, highly liquid inves...
- **Data point:** none (the resolver never serves it)
- **Rules:** none
- **Evidence:** 0 companies, 0 served, 0 proven, 0 certified cells; last verified 2026-11-02
- **Known problems:** none recorded
- **Pattern hits:** none

### `CashCashEquivalentsAndShortTermInvestments`
- **Meaning:** Cash, Cash Equivalents, and Short-Term Investments (us-gaap, instant, debit). Cash includes currency on hand as well as demand deposits with banks or financial institutions. It also includes other kinds of accounts that have the general characteristics of demand deposits in that the customer may deposit additional fu...
- **Data point definition:** cash_and_equivalents: Cash and cash equivalents at period end as printed.
- **Data point:** cash_and_equivalents; role cash_and_equivalents:combined#1
- **Rules:** B05; B06; B07; B08
- **Evidence:** 1 companies, 0 served, 0 proven, 0 certified cells; last verified 2026-11-02
- **Known problems:** none recorded
- **Pattern hits:** none
<!-- END GENERATED: tag library rows -->
