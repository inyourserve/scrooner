# Card family: Net income, EPS and share counts (written 2026-10-19 by the Tag Expert)

Tags: `us-gaap:NetIncomeLoss`, `ProfitLoss`, `NetIncomeLossAttributableToNoncontrollingInterest`, `NetIncomeLossAvailableToCommonStockholdersBasic`, `IncomeLossFromContinuingOperations`, `IncomeLossAttributableToParent`, `EarningsPerShareBasic`, `EarningsPerShareDiluted`, `EarningsPerShareBasicAndDiluted`, `IncomeLossFromContinuingOperationsPerBasicShare` / `PerDilutedShare`, `WeightedAverageNumberOfSharesOutstandingBasic`, `WeightedAverageNumberOfDilutedSharesOutstanding`, `WeightedAverageNumberOfShareOutstandingBasicAndDiluted`, `CommonStockSharesOutstanding`, and the cover tags `dei:EntityCommonStockSharesOutstanding`, `dei:EntityPublicFloat`.
Method and limits: as in `revenue.md` (Frames = all SEC filers; DB reads skipped, connections 14-18 > 12). dei definitions come from the definition block inside the BRK 10-K R1 (the dei documentation URL returned 404).

## 1. Official meaning (us-gaap 2025 taxonomy, read 2026-10-19)
| Tag | Period / balance | Definition (shortened) | Status |
|---|---|---|---|
| NetIncomeLoss | duration / credit | "Portion of profit or loss for the period, net of income taxes, which is **attributable to the parent**." | current |
| ProfitLoss | duration / credit | "Consolidated profit or loss, net of income taxes, **including the portion attributable to the noncontrolling interest**." | current |
| NetIncomeLossAttributableToNoncontrollingInterest | duration / debit | Net income attributable to noncontrolling interest | current |
| NetIncomeLossAvailableToCommonStockholdersBasic | duration / credit | After tax, NCI, **preferred dividends** and participating securities: income available to common | current |
| IncomeLossFromContinuingOperations | duration / credit | After-tax income from continuing operations attributable to the parent | current |
| IncomeLossAttributableToParent | duration / credit | "**Before tax**, attributable to parent. Includes continuing, discontinued, equity method" | current |
| EarningsPerShareBasic / Diluted | duration / none | Net income (loss) per share of common stock / assuming dilutive issuance | current |
| EarningsPerShareBasicAndDiluted | duration | EPS where basic = diluted | present in 2017, 2019, 2020, 2021 and 2024 taxonomy files; **absent from the 2025 file**; the 2018 file check was inconclusive |
| WeightedAverageNumberOfSharesOutstandingBasic | duration | Basic weighted-average shares | current |
| WeightedAverageNumberOfDilutedSharesOutstanding | duration | Diluted weighted-average shares | current |
| WeightedAverageNumberOfShareOutstandingBasicAndDiluted | duration | Weighted-average shares where basic = diluted (note the singular "Share" in the name) | present in the 2019, 2021 and 2024 taxonomy files; **absent from the 2025 file** |
| CommonStockSharesOutstanding | instant | Shares of common stock outstanding (balance-sheet date) | current |
| dei:EntityCommonStockSharesOutstanding | instant | "number of shares ... outstanding of each of registrant's classes ... as stated on cover ... Where multiple classes exist define each class by adding class of stock items ... onto the Instrument [Domain]" | current |
| dei:EntityPublicFloat | instant / credit | "Aggregate market value of the voting and non-voting common equity held by non-affiliates ... as of the last business day of the registrant's most recently completed second fiscal quarter." | current |

## 2. Who reports it (Frames, DATA-INFERRED; bank-like in brackets)
| Tag | CY2013 | CY2023 |
|---|---|---|
| NetIncomeLoss | 7,396 (588) | 6,386 (421) |
| ProfitLoss | 3,106 (127) | 3,565 (176) |
| NetIncomeLossAttributableToNoncontrollingInterest | 1,917 (78) | 1,728 (50) |
| EarningsPerShareBasic | 4,573 (562) | 5,821 (413) |
| EarningsPerShareDiluted | 4,279 (543) | 5,718 (405) |
| EarningsPerShareBasicAndDiluted | **3,156 (85)** | **8 (0)** |
| WeightedAverageNumberOfSharesOutstandingBasic | 4,952 (557) | 5,928 (411) |
| WeightedAverageNumberOfDilutedSharesOutstanding | 4,603 (535) | 5,839 (396) |
| WeightedAverageNumberOfShareOutstandingBasicAndDiluted | 2,806 (71) | 7 (0) |
| CommonStockSharesOutstanding | 5,991 (469) | 4,972 (348) |
| dei:EntityCommonStockSharesOutstanding (CY2023Q4I frame) | n/a | 2,717 (107) |
| dei:EntityPublicFloat (CY2023Q2I frame) | n/a | 4,565 (389) |
Findings:
- **Combined EPS/share tags nearly disappeared:** `EarningsPerShareBasicAndDiluted` 3,156 filers (2013) -> 8 (2023); `WeightedAverageNumberOfShareOutstandingBasicAndDiluted` 2,806 -> 7. In 2013 only 703 of the 3,156 also filed `EarningsPerShareBasic`. The 2025 taxonomy dropped both combined tags (they are in the 2024 file). This is the known `basic_eps` vs `EarningsPerShareBasicAndDiluted` gap (CLAUDE.md, 2026-10-10): for pre-2020 small filers it is the only EPS tag.
- CY2023: 3,330 filers carry both `NetIncomeLoss` and `ProfitLoss`; **235 carry only `ProfitLoss`** (no parent-attributable fact); 1,704 of the 1,728 NCI filers also file `ProfitLoss`.
- 205 filers carry EPS basic without diluted and 102 diluted without basic (CY2023).
- The dei frames count (2,717 shares; 4,565 float) is lower than the filer population because multi-class filers and single-class filers differ in dimension use and the frame returns undimensioned or one fact per filer; do not read it as coverage.
- `EntityPublicFloat` exists only for the annual cover (second-quarter date); scaling bug history: eBay $31 quintillion (doc 37).

## 3. How filers use it (filings opened)
| Filing | Statement and rows | Finding |
|---|---|---|
| AAPL 0000320193-25-000079 R3 (me) | "Net income" 112,010M `NetIncomeLoss`; EPS 7.49 / 7.46 `EarningsPerShareBasic/Diluted`; shares 14,948,500K / 15,004,697K `WeightedAverageNumberOfSharesOutstandingBasic` / `...DilutedSharesOutstanding` | clean layout |
| GE 0000040545-26-000008 R3 (me) | "Net income (loss)" 8,698M = **`ProfitLoss`**; "Less ... noncontrolling interests" (6)M `NetIncomeLossAttributableToNoncontrollingInterest`; "attributable to the Company" 8,704M = `NetIncomeLoss`; "attributable to common shareholders" `NetIncomeLossAvailableToCommonStockholdersBasic` (same 8,704M in 2025, 9,188M in 2023 after 295M preferred dividends); continuing-ops EPS tagged `IncomeLossFromContinuingOperationsPerBasicShare` 8.11 and net EPS `EarningsPerShareBasic` 8.20 | the row labelled "Net income" is `ProfitLoss` (incl. NCI), the parent figure is a different row |
| ANDE 0000821026-26-000010 R3 (me) | "Net income (loss)" 119,301K `ProfitLoss`; "attributable to The Andersons" 95,713K `NetIncomeLoss`; face EPS 2.81 / 2.79 tagged **`IncomeLossFromContinuingOperationsPerBasicShare` / `...PerDilutedShare`** | the FY2025 10-K has **no `EarningsPerShareBasic` fact**, while ANDE's FY2024 10-K (0000821026-25-000050) and its 10-Qs do (3.35 for FY2024): same company switched EPS tag between consecutive 10-Ks (companyconcept, me) |
| DHI 0000882184-25-000081 R4 (me) | "Net income" 3,620.9M `ProfitLoss`; "attributable to D.R. Horton" 3,585.2M `NetIncomeLoss`; EPS 11.62 / 11.57; shares 308.5M / 309.9M | standard NCI split |
| HTZ 0001657853-26-000008 R7 (me) | "Net income (loss)" `NetIncomeLoss` (no NCI); pretax `IncomeLossAttributableToParent` | mis-tagged pretax (carried) |
| BRK 0001193125-26-083899 R4 and R1 (me) | "Net earnings" 67,260M `ProfitLoss`; "attributable to Berkshire shareholders" 66,968M `NetIncomeLoss`; EPS on **two classes**: `EarningsPerShareBasic` with `StatementClassOfStockAxis` = Equivalent Class A (46,563) and Equivalent Class B (31.04), average equivalent shares 1,438,223 (A-equivalent) and 2,157,335,13x (B-equivalent). Cover: `EntityCommonStockSharesOutstanding` Class A 511,820 and Class B 1,389,605,139; `EntityPublicFloat` $902.7 billion | EPS and share facts exist only as dimensioned class facts; "Class B share = 1/1,500 Class A" (R4 footnote); an undimensioned EPS lookup finds nothing |
| GOOGL 0001652044-26-000018 R1 (me) | `EntityCommonStockSharesOutstanding`: Class A 5,822,000,000, Class C 5,438,000,000, third class 837,000,000; `EntityPublicFloat` rendered "$ 1.9" under the header "$ in Trillions" | three share facts at one date, one per class; total shares = the sum, not any single fact. The float is stored in dollars; the R-file scales it |
| PNC [32] | net income shown 6,997M is `ProfitLoss`, including 61M NCI; ROE divides by parent equity | the attribution policy is open |
| JPM / SFNC / BANR / DCOM / EWBC [32] | stored net income came from DEF 14A pay-versus-performance facts (57,000M vs 57,048M; BANR x1000) | proxy-statement `NetIncomeLoss` is rounded or scaled; never use |

## 4. Siblings and confusables
- `NetIncomeLoss` (parent) vs `ProfitLoss` (consolidated incl. NCI) vs `NetIncomeLossAvailableToCommonStockholdersBasic` (after preferred dividends and participating securities; can carry a different sign convention: QWTR, BEEM stored values were opposite-signed [28]) vs `IncomeLossFromContinuingOperations` (parent, continuing) vs `IncomeLossAttributableToParent` (**pre-tax**, used by HTZ and others as a pretax row).
- Per-share: `EarningsPerShareBasic` (net) vs `IncomeLossFromContinuingOperationsPerBasicShare` (continuing) vs `...DiscontinuedOperations...PerBasicShare`; the face "Basic EPS" can carry the continuing-ops tag (ANDE, DUK).
- Shares: weighted-average (period, duration) vs `CommonStockSharesOutstanding` (balance sheet instant) vs `dei:EntityCommonStockSharesOutstanding` (cover date, after year end, per class).
- `EntityPublicFloat` is not market capitalisation (non-affiliates only, second-quarter date).

## 5. Known misuses and company quirks
- RELAYED (shards S019/S015/S018, FILING-CHECKED by them): LITE (0001628280-26-057358 R3) and INTU tag "Loss/Income before income taxes" with `IncomeLossAttributableToParent`; ITW tags "Income Before Taxes" with `IncomeLossIncludingPortionAttributableToNoncontrollingInterest`. Never map either as net income; accept as pretax only where it equals net income + income tax for the same context.
- Carried: AEMD `NetIncomeLoss` in a DEF 14A rounded to $10K [28]; BANR DEF 14A fact x1000 [32]; BURU/GURE/NCRA/SVMB EPS re-based after reverse splits the split table lacks (ledger 22).
- NEW (me): ANDE EPS tag switch across consecutive 10-Ks (above).
- NEW (me): BRK and GOOGL carry their EPS/shares/cover shares only as class-dimensioned facts; any "one value per company" rule fails or picks one class.
- NEW (me): the row named "Net income" is `ProfitLoss` at GE, DHI, ANDE, BRK, PNC; stored `net_income` must say which one it is.
- NEW (me): EPS and share counts for BRK Class A (46,563 per share) and Class B (31.04) differ by 1,500; the pair must not be averaged or compared across companies without the class.

## 6. Mapping verdict
- `NetIncomeLoss`: **safe as parent net income** from the 10-K/10-Q statements of operations (AAPL, GE, ANDE, DHI, BRK FILING-CHECKED); never from DEF 14A or other proxy forms; fall back to `ProfitLoss` only with the NCI split visible (235 CY2023 filers have only `ProfitLoss`). `ProfitLoss` is consolidated, not parent.
- `NetIncomeLossAttributableToNoncontrollingInterest`: safe as the NCI deduction; sign: debit element, GE shows (6) for a negative NCI.
- `NetIncomeLossAvailableToCommonStockholdersBasic`: not a substitute for `NetIncomeLoss` (preferred dividends, sign issues).
- `IncomeLossAttributableToParent`: **never** as net income (pre-tax by definition; HTZ uses it for pretax).
- `EarningsPerShareBasic/Diluted`: safe where a statement-level undimensioned fact exists for the filing's own period (AAPL, GE, DHI). Per-class filers (BRK) and ANDE-type tag switches need a company-scoped exception; `EarningsPerShareBasicAndDiluted` is safe only for pre-2021 periods and 8 CY2023 filers.
- Weighted shares: `...SharesOutstandingBasic` and `...DilutedSharesOutstanding` safe as filed (AAPL, ANDE, DHI, HTZ); the combined basic-and-diluted share tag is era-limited (2,806 -> 7).
- `CommonStockSharesOutstanding` (balance-sheet date) vs `dei:EntityCommonStockSharesOutstanding` (cover): different dates; for multi-class filers sum the class facts, and only after confirming every class is present.
- `dei:EntityPublicFloat`: safe only as "public float" with unit/scale validated (dei can be mis-scaled; ledger 22, doc 37); never as market cap.
- Evidence: FILING-CHECKED for the named filings and the companyconcept series; populations DATA-INFERRED. Verified by: Tag Expert (me), Verifier [28][32].
