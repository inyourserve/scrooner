# VERIFY: split release 1, held filed-source cells and derived-DPS removals (2026-11-04)
Branch work/cashflow/split-release fc111cf, results/split_release_1. Seeds 20261103 (held draw, 5 cells) and 20261104 (5 of 4,179 `no_filed_source` removals). Verifier 2 (scrooner-bc). 31 SEC requests.

## Result
- **Held cells: NO (4 of 5 right, 1 wrong).** IMO, CP, NXPI and CNH match the face. SHOP FY2017 diluted EPS -0.42 is the pre-split figure; held, it stays shown next to split-adjusted 2021+ values.
- **Removals: YES.** All 5 removed DPS values were derived Q4 cells. Each equals filed FY minus filed 9M, so hiding them loses right numbers but shows nothing wrong. They are avoidable holds under `pershare.never_derive@1`, not errors.

## Cell table, held draw
| Cell | Production | Face (accession, R page) | Verdict |
|---|---|---|---|
| IMO diluted EPS 6M to 2025-06-30 | 4.38 | 4.38 CAD, 6 months column (0000049938-25-000045, statement of income) | right |
| CP DPS 9M to 2017-09-30 | 0.325 | CAD 1.6250 9M (0000016875-17-000086, interim income statement); /5 for the 2021 split = 0.325 | right |
| NXPI shares 2018-12-31 | 328,702,719 | 328,702,719 (0001564590-19-005657 20-F, cover R1, period end Dec. 31, 2018) | right |
| CNH basic EPS FY2017 | 0.2 | 0.20 USD (0001628280-19-002353 20-F, statements of operations) | right |
| SHOP diluted EPS FY2017 | -0.42 | -0.42 (0001594805-18-000009 40-F, operations); 10-for-1 split in 2022, adjusted = -0.042 | **wrong shown value** |

## Findings for the builder
1. SHOP has no split-ratio fact in core.fact, so the 82-with-split-ratio check misses it. Of SHOP's 18 held cells, 16 are pre-split (EPS 2014-2020, shares 2014). FY2015 shares = 0 is also held. Only the 2021 EPS pair is on the adjusted basis. Action: hold-out SHOP 2014-2020 per-share and 2014-2015 shares as `basis_review`, or rebase by the 2022 10:1 split. Re-verify SHOP plus every held company lacking a split fact whose later filings show a split (check 40-F/20-F filers first).
2. Held zero share counts (SHOP 2015-12-31 = 0) contradict the release's own `zero_share_count_filed` rule. Apply that rule to held cells too.
3. Kit: `parse_rpage` reads currency-prefixed cells ("CAD 0.5625") as None. CP was read by hand.

## Removals (seed 20261104)
CFG Q4 2017 0.18 (FY 0.64), OGE Q4 2018 0.365 (FY 1.395), BRX Q4 2025 0.3075 (FY 1.17), PM Q4 2025 1.47 (FY 5.64), HRB Q4 FY2026 0.42 (FY 1.68). Every one is `is_derived=true` in core.fact from the 10-K, with no filed quarter fact.

## Untested scope
852 other held cells (CP 236, IMO 225 mostly CAD; currency display not judged here). Removal draw covered `no_filed_source` only.
