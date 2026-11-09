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


## Update: (b) graded against new_values.csv (d8d3bf2)

`data-team/strategy/team/results/cf_gaps_2026-11-08/new_values.csv` has 67 rows: 40 new values, 2 withdrawn and 25 reason changes, for 4 companies. SEC requests for this update: 28 more.

**17 of the 40 new values checked: 17 right, 0 wrong.** Derived quarters were checked as YTD minus the prior YTD, each from the accession the store cites as the latest copy.

| key | claim | face | verdict |
|---|---|---|---|
| Reliance CFO Q3 2014 | derived 53.3M | 9M 162.8 (0001104659-15-074533 R6) − 6M 109.5 (0001104659-15-055210 R6) | RIGHT |
| Reliance CFO Q4 2014 | derived 193.2M | FY 356.0 (0001558370-17-000994 R8) − 9M 162.8 | RIGHT |
| Cheniere Partners CFO Q4 2015 | derived 6,695K | FY 5,748 (0001383650-16-000087 R7) − 9M (947) (0001383650-16-000137 R6) | RIGHT |
| Cheniere Partners CFO FY2018 | 1,874M | 0001383650-21-000005 R7 | RIGHT |
| Cheniere Partners CFO Q4 2018 | derived 610M | 1,874 − 9M 1,264 (0001383650-19-000038 R7) | RIGHT (also closes the pending item in (a)) |
| Brixmor CFO Q1 2014 | 86,576K | 0001581068-15-000050 R8 (primary block) | RIGHT |
| Brixmor CFO Q2 2014 | derived 132,064K | 218,640 − 86,576 | RIGHT |
| Brixmor CFO Q3 2014 | derived 153,650K | 9M 372,290 (0001581068-15-000092 R8, primary block) − 218,640 | RIGHT |
| Brixmor dividends Q1 2014 | 29,170K | 0001581068-15-000050 R8 | RIGHT |
| Somnigroup CFO FY2020 | 654.7M | 0001206264-23-000060 R9 | RIGHT |
| Somnigroup CFO Q1 2020 | 15.0M | 0001206264-21-000143 R6 | RIGHT |
| Somnigroup CFO Q4 2021 | derived 125.6M | FY 723.1 (0001206264-24-000050 R9) − 9M 597.5 (0001206264-22-000182 R7). The two inputs carry different tags (…ContinuingOperations vs plain) for the same "from continuing operations" line | RIGHT |
| Somnigroup buybacks FY2020 | 331.8M | 0001206264-23-000060 R9 "Treasury stock repurchased (331.8)" | RIGHT |
| Somnigroup buybacks Q1 2020 | 199.3M | 0001206264-21-000143 R6 | RIGHT |
| Somnigroup buybacks Q2 2020 | derived 0.2M | 6M 199.5 (0001206264-21-000208 R6) − 199.3 | RIGHT (also closes the pending item in (a)) |
| Somnigroup buybacks Q3 2021 | derived 191.4M | 9M 565.8 (0001206264-22-000182 R7) − 6M 374.4 (0001206264-22-000169 R7) | RIGHT |
| Somnigroup dividends Q1 2021 | 14.3M | 0001206264-22-000124 R6 | RIGHT |

**Withdrawn (2): WRONG.** Brixmor buybacks FY2015 and FY2016 move from value 0 to not_presented / only_excluded_lines_presented, citing 0001581068-17-000005. That is not the latest copy. The latest copies (FY2017 10-K R8 for 2015, FY2018 10-K R8 for 2016) print "Repurchase(s) of common shares 0". Dhairya's ruling (2026-11-08): serve 0 from the latest print. Keep both at 0 and cite those accessions.

**Reason changes (25):**
- **Somnigroup dividends 2015–2019 → line_not_presented_in_filing (17): right.** It matches the FY2018 face read in full (no dividend payment in the financing section), and Somnigroup resumed dividends only in 2021.
- **Somnigroup dividends Q2/Q3 2020 and Brixmor dividends Q2/Q3 2014 → no_basis_witness:** a defensible reason under rule 4. For Somnigroup 2020 both YTD inputs are 0 (Q1 0.0 and 6M 0.0 printed), so the hold is avoidable but harmless.
- **Brixmor buybacks FY2014 / Q4 2014 → only_excluded_lines_presented:** right; FY2014 prints only the equity-award line (0).
- **Brixmor Q4 2015 / Q4 2016:** must follow the FY ruling above.

**(a) after this update:** 5 right (adding Cheniere Q4 2018 and Somnigroup Q2 2020 buybacks), 1 to change under the ruling (Brixmor FY/Q4 2015-16), 3 pending the store run (Kraft Heinz, Erie, BXP).


## Final grade at d1a0050 (store output for 60 cohort companies), 2026-11-08

Inputs: `results/cf_gaps_2026-11-08/` at d1a0050. That is `answer_key_vs_store.csv`, `store_cells_60_companies.csv.gz` (10,346 cells), and the final `new_values.csv` (47 new values, 32 reason changes, 0 withdrawn). SEC requests for this round: 14.

**Overall verdict for PR #4: PASS.** There are no wrong shown values, every sampled value and derived quarter is right, and all 15 cohort absent-line claims are right. One non-blocking reason residual is noted below.

### (c) The 12 fresh picks plus Kraft Heinz, Erie and BXP, against the store cells

I read each key from `store_cells_60_companies.csv.gz`, not from the lane's self-grade. All 15 match the answer-key file (Kraft Heinz is stored at the month-end 2017-06-30 for the 52-week date 2017-07-01).

**15 of 15 store claims are right against the filings.** Two of these needed my own answer key corrected; the lane's disputes are upheld:
- **Kraft Heinz buybacks Q2 2017 → only_excluded_lines_presented: RIGHT.** My key was wrong. The financing section of 0001637459-17-000101 R7 prints "Redemption of Series A Preferred Stock 0" (PaymentsForRepurchaseOfRedeemablePreferredStock). A preferred redemption is a line the buyback perimeter excludes. My label filter did not include "redemption".
- **International Seaways buybacks Q1 2018 → only_excluded_lines_presented: RIGHT.** My key was wrong. 0001144204-18-025525 R7 prints "Cash paid to tax authority upon vesting of stock-based compensation (278)" (PaymentsRelatedToTaxWithholdingForShareBasedCompensation), a tax-withholding line. This is consistent with Viasat Q1 FY16. My filter did not include "tax authority".
- **The other 13 match my key:**
  - Erie, Valaris, ESCO, Dominion, T-Mobile and Sunoco: line_not_presented_in_filing.
  - Public Storage and Atmos: only_excluded_lines_presented.
  - BXP, Ares, STAG and Clearway: line_presented_combined_with_others.
  - West Pharmaceutical: derived 12.6M = FY 48.1 − 9M 35.5 ("Dividend payments", 0000105770-21-000083 R7). The equal 12.6 of "Dividends declared, not paid" is a coincidence; the non-cash line is not used.

### (3) New since the last draw

- **Zero-input YTD derive to 0: RIGHT** on the keys drawn:
  - Modine buybacks Q2 FY19 (2018-09-30): 6M 0.0 (0001140361-19-020095 R7) − Q1 0.0 (0001140361-19-013948 R7), "Purchases of treasury stock under share repurchase program".
  - Brixmor buybacks Q2 2017: 6M 0 (0001581068-18-000024 R8) − Q1 0 (0001581068-18-000017 R8), "Repurchases of common shares". The equity-award line sits separately under the tax-withholding tag.
- **Reason from the cited filing's own lines (original before amendment): RIGHT** for Sunoco FY2023 (0001552275-24-000013) and Clearway FY2021 (0001567683-22-000006). Both are original 10-Ks whose financing sections were read above.
- **Tax-withholding lines as excluded: RIGHT** (Viasat Q1 FY16; International Seaways Q1 2018).
- **Brixmor FY2015 / FY2016 buybacks:** the final new_values has 0 withdrawals, so they stay at the printed 0 from the latest copies, per the ruling. RIGHT.
- **New reason changes in the final file: consistent with the faces read.** Viasat dividends FY2024-25 → line_not_presented_in_filing (Viasat pays no dividend), and Cheniere Partners buybacks 2022-23 → line_not_presented_in_filing (an LP with distributions only).

### Residual (non-blocking)

- **Brixmor buybacks Q4 2015 / Q4 2016** keep `defect no_prior_quarter_end` from the sampled run. The blank is safe, but the reason is not what the filings show. The 9M copies exist, and they carry only the equity-award line under the buyback tag, while the latest FY copies print a common buyback of 0. A mixed-basis reason (or 0 if the bases are accepted as the same) would describe it. Fix in a follow-up; it does not block the PR.

**Totals across both draws of PR #4:**
- **Shown values:** 0 wrong.
- **New and derived values checked:** 17 + 4 = 21, all right.
- **Cohort absent-line claims:** 15 of 15 right.
- **First-draw failures:** all fixed or ruled, except the one reason residual.

## Untested scope

Everything marked pending above.
