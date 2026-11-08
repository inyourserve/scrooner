Under test: inyourserve/scrooner#4, branch work/cashflow/fsn-gaps-rebased 3e19657 (fixes in CF-GAPS-2026-11-02.md §7). Re-draw of VERIFY-CF-GAPS-2026-11-08.
Fresh picks: seed 20261108 from cf_gap_keys_classified.csv.gz, outside the lane's 15 companies and the earlier picks. SEC requests: 28 (sec.gov only, <= 3.4/s); the first draw's reads were reused. Verifier session scrooner-c3. DB: one read-only accession lookup.

# Verify: cash-flow gaps re-draw (2026-11-08)

## Status: PARTLY BLOCKED

The branch commits code, tests and the report, but **no outputs**. To finish, the lane needs to publish:
- **(b)** the list of the +41 new values and derived quarters (key, value, accession);
- **(c)** the store's claimed state and reason for cohort keys. §8 says the cohort was not re-run, and `cf_gap_keys_classified.csv.gz` is the old analysis classifier.

Without those, I graded what the report states and built a filing-checked answer key for the rest.

## (a) The 10 keys that failed the first draw

| key | §7 claim now | face | verdict |
|---|---|---|---|
| Brixmor dividends Q1 2014 | value 29,170 | 0001581068-15-000050 R8 "Distributions to common stockholders (29,170)"; the column ties | **RIGHT** |
| Brixmor CFO Q2 2014 | derived 132,064 | 6M 218,640 (0001581068-15-000073 R8) − Q1 86,576 (0001581068-15-000050 R8). Both columns tie on the primary registrant's block | **RIGHT** |
| Somnigroup dividends FY2018 | not_presented line_not_presented_in_filing | 0001206264-21-000053 R8: no dividend payment in the financing section | **RIGHT** |
| Cheniere Partners CFO Q4 2018 | FY2018 1,874M is now a value (stated) | 0001383650-21-000005 R7: 1,874; ties (1,874 − 804 − 1,118 = −48) | FY value **RIGHT**. The Q4 cell (FY − 9M) is not stated in §7: **pending output** |
| Somnigroup buybacks Q2 2020 | not stated | 6M 199.5 printed (0001206264-21-000208 R6), the column ties | **pending output** |
| **Brixmor buybacks Q4 2015 / Q4 2016** (and FY2015 / FY2016) | only_excluded_lines_presented (FY values 823K / 3,304K withdrawn) | **The latest copies print a common buyback line of 0.** 0001581068-18-000008 R8 (FY2015 column): "Repurchase of common shares 0" (PaymentsForRepurchaseOfCommonStock), with "Repurchase of common shares in conjunction with equity award plans (823)" on PaymentsRelatedToTaxWithholdingForShareBasedCompensation. 0001581068-19-000005 R8 (FY2016 column): "Repurchases of common shares 0" and the equity-award line (3,304) under the tax-withholding tag | **WRONG reason (dispute).** Withdrawing 823K / 3,304K is right. But §7's stated cause ("the FY2017 10-K reprints the equity-award line under the same tag as 'Repurchase of common shares'") is not what those R pages print. Under decision 02 rule 3 (latest print wins), FY2015 and FY2016 buybacks are **value 0**, not `only_excluded_lines_presented`. The new rule ("a period one filing excludes by label is never filled by a relabelled copy") overrides a latest print that is right. Ruling needed. For Q4, FY 0 − a 9M that holds only the equity-award line would give 0 buybacks if the bases are accepted as the same; otherwise it is a reasoned blank |
| Kraft Heinz buybacks Q2 2017 | not stated (store code said to test for a repurchase line first) | 0001637459-17-000101 R7: no repurchase line | **pending output** (expected: line_not_presented_in_filing) |
| Erie buybacks Q4 2018 | not stated | 0000922621-19-000008 R8: no repurchase line | **pending output** (expected: line_not_presented_in_filing) |
| BXP dividends Q3 2021 | not stated (`dividend_class`: "dividends and distributions" is combined) | 0001656423-21-000033 R8 "Dividends and distributions (513,381)"; "declared but not paid" is non-cash | **pending output** (expected: line_presented_combined_with_others) |

**Tally: 3 right; 1 right on the FY value with the quarter pending; 1 dispute (Brixmor FY/Q4 2015-16); 5 pending output.**

## (b) The +41 identity-fix values

The two named in §7 are right: Brixmor CFO Q2 2014 = 132,064 and Cheniere Partners CFO FY2018 = 1,874M (see above). The other 39 are pending the list.

## (c) Answer key for 12 fresh cohort picks (outside the lane's 15 companies)

Shapes drawn as asked:
- **Kraft Heinz shape:** `only_excluded_lines` whose "lines" are all `…Abstract` headers.
- **Erie shape:** lines that include table, axis or member rows.
- **BXP shape:** a "dividends and distributions" or "declared / not paid" line counted as common.

The expected state below is what the cash-flow face supports. Grading the store becomes a lookup once its output is published.

| shape | company (CIK), key | accession, page: financing section | expected store state / reason |
|---|---|---|---|
| KHC | 0001679049 buybacks Q1 2018 | 0001144204-18-025525 R7: no repurchase line | not_presented / line_not_presented_in_filing |
| KHC | Valaris (0000314808) buybacks FY2019 | 0000314808-20-000015 R6: dividends only | not_presented / line_not_presented_in_filing |
| KHC | Public Storage (0001393311) buybacks 6M 2016 | 0001393311-16-000059 R8: "Cash paid upon vesting in lieu of issuing common shares (13,304)" only | not_presented / only_excluded_lines_presented (a vesting settlement, not a buyback) |
| KHC | Atmos Energy (0000731802) buybacks 9M 2016 | 0000731802-16-000055 R7: "Repurchase of equity awards 0" (PaymentsForRepurchaseOfOtherEquity) only | not_presented / only_excluded_lines_presented |
| Erie | 0000866706 buybacks 6M 2019 | 0001144204-19-024737 R6: dividends only | not_presented / line_not_presented_in_filing |
| Erie | Dominion (0000715957) buybacks Q1 2022 (combined Dominion / Virginia Power filing) | 0001564590-22-018135 R10: issuance and dividends only, in the parent's block | not_presented / line_not_presented_in_filing (read the parent's block only) |
| Erie | T-Mobile (0001283699) buybacks 9M 2015 | 0001283699-15-000055 R6: no repurchase line | not_presented / line_not_presented_in_filing |
| Erie | Sunoco LP (0001552275) buybacks FY2023 | 0001552275-24-000013 R6: "Cash distribution to unitholders" only | not_presented / line_not_presented_in_filing (an LP; no unit repurchase) |
| BXP | Ares Management (0001176948) dividends 6M 2024 | 0001628280-24-035320 R7 (multi-block page): "Dividends and distributions (632,260)" | not_presented / line_presented_combined_with_others |
| BXP | West Pharmaceutical (0000105770) dividends Q4 2020 | 0000105770-21-000008 R8 (read raw; the kit cannot parse the header): "Dividend payments (48.1)" FY2020; "Dividends declared, not paid 12.6" is non-cash | **value** from "Dividend payments" (Q4 = FY 48.1 − 9M). The non-cash line must never be used |
| BXP | STAG Industrial (0001479094) dividends Q1 2015 | 0001558370-15-000693 R7: "Dividends and distributions (25,314)"; "declared but not paid 7,696" is non-cash | not_presented / line_presented_combined_with_others |
| BXP | Clearway Energy (0001567683) dividends Q4 2021 | 0001567683-22-000006 R8: "Payments of dividends and distributions (268)" FY2021 | not_presented / line_presented_combined_with_others |

## Findings for the lane

1. **Publish outputs:** the +41 list and a store run on the 12 fresh picks (or the cohort). Then (b) and (c) can be graded.
2. **Brixmor FY / Q4 2015-16 buybacks:** the FY2017 and FY2018 10-Ks print "Repurchase(s) of common shares 0" with the equity-award line under the tax-withholding tag. Either serve 0 as the latest print, or get a ruling that an earlier exclusion overrides it. Either way, correct §7's stated cause.
3. **Combined filings** (Dominion / Virginia Power; Ares' multi-block page): absent-line claims must read the primary registrant's block only.

## Untested scope

Everything marked pending above.
