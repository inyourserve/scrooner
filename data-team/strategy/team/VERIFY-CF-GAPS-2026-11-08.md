Under test: inyourserve/scrooner#4, branch work/cashflow/fsn-gaps-rebased 93c0a19. Sample: data-team/strategy/team/VERIFY-SAMPLE-CF-GAPS-2026-11-08.csv (38 keys, 15 companies, seed 20261108) plus 12 Verifier picks from cf_gaps_2026-11-02/cf_gap_keys_classified.csv.gz (seed 20261101, outside the lane's 15 companies).
SEC requests: 96 (sec.gov only, <= 3.4/s, the repo's declared User-Agent). Verifier session scrooner-c3. DB: one read-only lookup of 10-Q accessions.

# Verify: cash-flow gaps (buyback / dividend detector, FX identity, evidenced blanks), 2026-11-08

## Result

| part | keys | right | wrong | wrong shown values |
|---|---|---|---|---|
| Lane sample | 38 | **31** | **7** | **0** |
| Verifier picks (cohort classification) | 12 | **9** | **3** | n/a (classification only) |

- **Every value the branch shows matches its filing:** 22 values, including the 3 derived quarters. The detector's new mappings (`PaymentsForRepurchaseOfEquity`, `PaymentsOfCapitalDistribution`, `PaymentsOfOrdinaryDividends…`) are the companies' own common buyback and dividend lines.
- **The FX identity change is right.** Nucor, Abbott and Viasat each tie only once the FX line is counted.
- **The 7 lane errors are all blanks or reasons, and fall in three groups:**
  1. **`latest_copy_fails_identity` is false on 4 keys** (S3 Brixmor Q1 2014 dividends, plus S5 Somnigroup 6M 2020, Brixmor 6M 2014 and Cheniere Partners FY2018). Each column ties on its own face: operating + investing + financing (+ discontinued + FX) = the printed net change. Two are Brixmor co-registrant pages that print a second block (the operating partnership) with near-identical numbers. The likely cause is that the check mixes the two blocks, or, for Somnigroup, does not count the discontinued-operations line. **Brixmor Q1 2014 dividends 29,170 should not be withdrawn.** The latest copy (0001581068-15-000050 R8) prints "Distributions to common stockholders (29,170)" and the column ties (86,576 − 39,774 − 105,021 = −58,219).
  2. **Somnigroup FY2018 dividends: wrong reason.** The filing prints no dividend payment, only "Dividends received from unconsolidated affiliates", an operating inflow. The right state is `not_presented` / `line_not_presented_in_filing`, not `perimeter_line_unresolved`. EchoStar (a Verifier pick) shows the same line classified correctly, so the classifier is inconsistent.
  3. **Brixmor Q4 2015 and Q4 2016 buybacks: the withdrawal is right, the reason is not.** `no_prior_quarter_end` is not what the filing shows. The year prints only the equity-award (SBC-plan) line, so the reason is `only_excluded_lines_presented`.
- **The cohort classification has a fault that change 4 would write into production.** `only_excluded_lines` is assigned when the only "lines" are section headers (`…Abstract`) or rows from a non-cash-flow page. Kraft Heinz Q2 2017 and Erie Q4 2018 print no repurchase line at all, so the true reason is `line_not_presented_in_filing`. Erie's `lines` field lists related-party table rows, so a non-cash-flow page was read as its face. BXP's "Dividends and distributions" is classed as a common line, and its non-cash "Dividends and distributions declared but not paid" is listed as a common dividend line.

## Lane sample, cell by cell

Values in the filer's printed unit ($K unless noted). "Ties" means CFO + CFI + CFF (+ discontinued + FX) = printed net change in that column.

| stratum | key | claim | filing (accession, page): what it prints | verdict |
|---|---|---|---|---|
| S1 | Nucor CFO FY2018 | value 2,393,952 | 0001564590-21-009503 R9: 2,393,952; 2,393,952 − 1,030,069 − 908,177 − 5,924 (FX) = 449,782 = printed change | RIGHT |
| S1 | Brixmor dividends Q4 2018 | derived 82,525 | FY 333,411 (0001581068-21-000012 R8) − 9M 250,886 (0001581068-18-000028 R8) | RIGHT |
| S1 | MSA buybacks Q4 2016 | derived 0 | FY 1,881 (0000066570-19-000010 R6) − 9M 1,881 (0000066570-16-000112 R6) | RIGHT |
| S1 | Abbott CFO FY2023 | 7,261 ($M) | 0001628280-26-010185 R6: 7,261; 7,261 − 3,133 − 7,091 − 23 = −2,986 = printed | RIGHT |
| S1 | Viasat CFO Q1 FY23 (2022-06-30) | 39,637 | 0000950170-23-040747 R4: 39,637; ties with FX −1,930 | RIGHT |
| S1 | Oracle buybacks Q1 FY25 (2024-08-31) | 150 ($M) | 0001193125-25-200095 R7: "Payments for repurchases of common stock (150)"; the tax-withholding line (851) is separate and excluded | RIGHT |
| S2 | MSA buybacks FY2014 | 5,654 | 0000066570-17-000011 R6 "Company stock purchases (5,654)" | RIGHT |
| S2 | Brixmor dividends FY2025 | 354,224 | 0001581068-26-000007 R9 "Distributions to common stockholders (354,224)" | RIGHT |
| S2 | Reliance dividends Q1 2019 | 39.6 ($M) | 0001558370-20-004910 R8 "Dividends and dividend equivalents paid (39.6)" | RIGHT |
| S2 | Somnigroup buybacks Q1 2019 | 3.7 ($M) | 0001206264-20-000137 R6 "Treasury stock repurchased (3.7)" | RIGHT (face) |
| S2 | MSA buybacks FY2025 | 89,962 | 0000066570-26-000005 R7 "Company stock purchases (89,962)" | RIGHT |
| S2 | MSA buybacks FY2023 | 3,961 | same R7, 2023 column (3,961) | RIGHT |
| S2 | Brixmor dividends Q1 2023 | 80,080 | 0001581068-24-000020 R8 (80,080) | RIGHT |
| S2 | MSA buybacks Q1 2017 | 3,811 | 0000066570-18-000018 R6 (3,811) | RIGHT |
| S3 | Brixmor dividends Q1 2014 | defect latest_copy_fails_identity (old 29,170) | Latest copy 0001581068-15-000050 R8: "Distributions to common stockholders (29,170)"; 86,576 − 39,774 − 105,021 = −58,219 = printed (operating-partnership block also ties: 86,623 − 39,771 − 104,629 = −57,777) | **WRONG: avoidable hold, a right value withdrawn** |
| S3 | Brixmor buybacks Q1 2015 | not_presented only_excluded | 0001581068-16-000117 R8: only "Repurchase of common shares in conjunction with equity award plans (329)" | RIGHT |
| S3 | Brixmor buybacks FY2014 | no cell (old 0) | 0001581068-17-000005 R8: the equity-award line prints 0 | RIGHT (old 0 was not a buyback) |
| S3 | Brixmor buybacks Q1 2016 | not_presented only_excluded | 0001581068-16-000117 R8: equity-award line (1,165) only | RIGHT |
| S3 | Brixmor buybacks Q4 2016 | defect no_prior_quarter_end (old 98) | 0001581068-17-000005 R8 FY2016: only the equity-award line (3,304) | **WRONG reason** (withdrawal right; should be only_excluded_lines_presented) |
| S3 | Brixmor buybacks Q4 2015 | defect no_prior_quarter_end (old 823) | same R8 FY2015: equity-award line (823) only | **WRONG reason** (as above) |
| S4 | Viasat dividends FY2017 | not_presented line_not_presented | 0001564590-19-020649 R5: no dividend line | RIGHT |
| S4 | Waters dividends FY2020 | not_presented line_not_presented | 0001193125-23-050827 R6: "Purchases of treasury shares" only | RIGHT |
| S4 | Cheniere Partners buybacks 9M 2015 | not_presented line_not_presented | 0001383650-16-000137 R6: "Distributions to owners" only | RIGHT |
| S4 | Modine dividends 6M 2016 | not_presented only_excluded | 0001140361-17-040436 R7: "Dividend paid to noncontrolling interest 0.0" only | RIGHT |
| S4 | Viasat buybacks Q1 FY16 | not_presented only_excluded | 0001193125-16-676890 R4: "…in treasury … related to tax withholdings (531)" only | RIGHT |
| S4 | Brixmor buybacks Q1 2025 | not_presented only_excluded | The cited 0001581068-26-000026 R9 prints 6M columns only (no 2025-03-31 values). Brixmor's only repurchase line in every copy read is the equity-award line | RIGHT in substance. The cited accession does not carry that column; cite the Q1 2026 10-Q |
| S4 | Morgan Stanley buybacks FY2021 / 9M 2024 / FY2019 | not_presented combined | 0000895421-24-000300 R8 / -25-000539 R7 / -22-000400 R8: "Repurchases of common stock and employee tax withholdings" (12,075 / 3,347 / 5,954) | RIGHT (3) |
| S4 | Cheniere Partners dividends FY2016 and FY2018 | defect perimeter_line_unresolved | 0001383650-19-000005 R6 / -21-000005 R7: "Distributions to owners" (99 / 1,113 $M), an LP distribution | RIGHT (blank is safe; `perimeter_partnership_distribution` fits the label better) (2) |
| S4 | Somnigroup dividends FY2018 | defect perimeter_line_unresolved | 0001206264-21-000053 R8: full face read; no dividend payment; only operating "Dividends received from unconsolidated affiliates 14.8"; column ties (207.5 − 71.2 − 107.0 − 22.3 − 3.1 = 3.9) | **WRONG reason**: not_presented / line_not_presented_in_filing |
| S5 | Somnigroup buybacks Q2 2020 | defect latest_copy_fails_identity | 0001206264-21-000208 R6 6M 2020: 170.4 − 87.2 + 1.4 = 84.6; − 1.0 (discontinued) − 1.7 (FX) = 81.9 = printed. Buyback 6M (199.5) printed | **WRONG: the identity holds** (the check likely omits NetCashProvidedByUsedInDiscontinuedOperations) |
| S5 | Brixmor CFO Q2 2014 | defect latest_copy_fails_identity | 0001581068-15-000073 R8 6M 2014: 218,640 − 81,875 − 188,850 = −52,085 = printed; OP block 218,637 − 81,868 − 188,095 = −51,326 = printed | **WRONG: ties** (co-registrant blocks) |
| S5 | Cheniere Partners CFO Q4 2018 | defect latest_copy_fails_identity | 0001383650-21-000005 R7 FY2018: 1,874 − 804 − 1,118 = −48 = printed | **WRONG: ties** |
| S6 | CPKC buybacks Q3 2022 | not_presented line_not_presented | 0000016875-23-000044 R5 (read raw: CAD headers defeat the kit): "Dividends paid", "Issuance of Common Shares", no repurchase line | RIGHT |
| S6 | Imperial Oil buybacks Q1 2015 | not_presented line_not_presented | 0001193125-16-576599 R7: dividends only | RIGHT |
| S6 | Honeywell buybacks FY2024 | 1,655,000,000 | 0000773840-26-000013 R7 "Repurchases of common stock (1,655,000,000)" | RIGHT |

## Verifier picks from the cohort classification (outside the 15 companies)

| key | class claimed | face | verdict |
|---|---|---|---|
| Kraft Heinz (0001637459) buybacks Q2 2017 | only_excluded_lines | 0001637459-17-000101 R7: no repurchase line; the classifier's "lines" are section headers | **WRONG**: should be no_line_on_face |
| 0001334036 dividends FY2020 | only_excluded_lines | 0001334036-21-000035 R8: only "Dividends — Series A convertible preferred stock" | RIGHT |
| 0001377121 buybacks FY2025 | only_excluded_lines | 0001104659-26-019696 R7: "Tax withholding payments related to net settlement of RSUs" only | RIGHT |
| Erie Indemnity (0000922621) buybacks Q4 2018 | only_excluded_lines | 0000922621-19-000008 R8: no repurchase line; the classifier's "lines" are related-party table rows (a non-cash-flow page) | **WRONG**: should be no_line_on_face |
| 0001061983 dividends FY2022 | no_line_on_face | 0000950170-23-005515 R6: none | RIGHT |
| Block (0001512673) dividends 9M 2023 | no_line_on_face | 0001628280-23-036406 R8: none | RIGHT |
| EchoStar (0001415404) dividends FY2020 | no_line_on_face | 0001415404-21-000005 R7: only dividends received (inflows) | RIGHT |
| 0000764065 dividends 6M 2025 | no_line_on_face | 0000764065-25-000124 R6: none | RIGHT |
| APi Group (0001796209) dividends FY2021 | held_lines_only | 0000950170-22-002474 R8: "Distributions paid" blank in 2021 | RIGHT (a hold is safe) |
| Energy Transfer (0001276187) dividends FY2015 | held_lines_only | 0001276187-16-000132 R7: "Distributions to partners (1,090)", NCI distributions | RIGHT (partnership perimeter) |
| Targa (0001389170) buybacks Q2 2026 | common_line_unseeded_tag | 0001193125-26-337729 R6: "Repurchases of common stock (135.1)" 6M, tagged PaymentsForRepurchaseOfEquity | RIGHT class (the `lines` field is junk: table and axis rows) |
| BXP (0001037540) dividends Q3 2021 | common_line_unseeded_tag | 0001656423-21-000033 R8: "Dividends and distributions (513,381)" 9M. Also listed as "common": "Dividends and distributions declared but not paid", a non-cash supplemental item | **WRONG**: a combined line; the non-cash item must never count |

## Findings for the lane

1. **Identity check:** count `NetCashProvidedByUsedInDiscontinuedOperations` and the cash-flow lines for discontinued operations. Evaluate each co-registrant block (LegalEntityAxis) on its own. Re-verify: the 4 keys above.
2. **Do not withdraw Brixmor Q1 2014 dividends** (29,170). Restore the value.
3. **"Dividends received …" (operating inflows) must never make a dividend-paid line `unresolved`.** Somnigroup FY2018 is `line_not_presented_in_filing`.
4. **Brixmor Q4 2015 and Q4 2016 buybacks:** use `only_excluded_lines_presented`.
5. **Change 4 (evidenced blanks):** classify only rows of the cash-flow face. Ignore `…Abstract` header rows, table and axis rows, and supplemental non-cash items. A filing with no concept line must get `line_not_presented_in_filing`, never `only_excluded_lines_presented`. Treat "Dividends and distributions" at REITs with OP units as combined. Re-verify: re-draw only_excluded_lines keys after the fix.
6. **Evidence pointer:** for Brixmor Q1 2025, cite the filing that prints the column.

## Untested scope

- D&A keys were not drawn, and neither were cohort counts beyond the 12 picks.
- Same-basis checks on derived quarters were not drawn beyond the 3 derived keys.
- The local reproduction (scratch Postgres) was not re-run.
