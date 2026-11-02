Under test: origin/work/capex-da-debt/store-gate-followups 482244f, key file pipeline/scripts/slot_records/results/capex_da_store_gate_2026-11-03/store_gate_keys.csv (mode=detectors, fails_gate=True: 63 keys).
Seed 20261101 (XOM stratified: md5('20261101:'+concept+':'+grain+':'+fsn_end)). Cells checked: all 8 non-XOM failing keys + 15 of 55 XOM keys. SEC requests: 190 (sec.gov only, <= 3.4/s; 15 were 404s from first trying XOM under the new CIK 0002115436). Verifier session scrooner-c3, read-only.

# Verify: capex/D&A store gate failing keys (2026-11-03)

## Result

**23 of 23 store values right, 0 wrong.** Each store value equals the printed line, at the right period column and duration, in the store accession's own statement R page.
- **Non-XOM: 8/8 right.** For 7 of these, the lane's original filing prints the same number.
- **JPM Q1 2014 is a real recast.** The original Q1 2014 10-Q printed 1,077 and the later Q1 2015 10-Q comparative prints 1,208. The store value 1,208 is the latest print, which is right under decision 02 (2026-11-01, rule 3).
- **XOM: 15/15 right.** All values are read from predecessor CIK 0000034088's filings.

**Two things that are not value errors, flagged for decisions:**
1. **KEY capex Q1 2019 = 9.** It is printed as "Purchases of premises, equipment, and software" ((9), $M). The value is right as printed. The lane's `definition_outside_ruling` hold is about whether software belongs in capex. That is a Standardization Lead or founder definition call, not a filing error.
2. **JPM D&A Q1 2014.** Releasing it adopts the recast 1,208 over the as-filed 1,077. This is consistent with rule 3; noted here so the change is visible.

## Cell table

$ millions unless noted. Outflows print in parentheses; the store holds them positive, which is correct.

| key | store value | store accession, page, printed | lane's original filing | verdict |
|---|---|---|---|---|
| JPM (0000019617) D&A Q 2014-03-31 | 1,208 | 0000019617-15-000318 R8 CF "Depreciation and amortization" 3M: 1,208 | 0000019617-14-000339 R8: **1,077** (recast later) | RIGHT (latest print) |
| KEY (0000091576) capex Q 2019-03-31 | 9 | 0000091576-20-000014 R10 "Purchases of premises, equipment, and software" (9) | 0000091576-19-000017 R10: (9) | RIGHT value; definition open |
| AAPL capex FY 2016-09-24 | 12,734 | 0000320193-18-000145 R9 (12,734) | 0001628280-16-020309 R8: (12,734) | RIGHT |
| AAPL capex FY 2017-09-30 | 12,451 | 0000320193-19-000119 R7 (12,451) | 0000320193-17-000070 R8: (12,451) | RIGHT |
| AAPL capex Q 2017-12-30 | 2,810 | 0000320193-19-000010 R7 3M (2,810) | 0000320193-18-000007 R7: (2,810) | RIGHT |
| PLD (0001045609) D&A FY 2014 | 642,461 ($K) | 0001564590-17-001559 R4 IS (also R7 CF) 642,461 | 0001193125-15-062622 R4: 642,461 | RIGHT |
| PLD D&A Q 2014-09-30 | 149,202 ($K) | 0001564590-15-009022 R4 IS 3M 149,202 | n/a | RIGHT |
| PLD D&A Q 2026-06-30 | 689,518 ($K) | 0001193125-26-323746 R4 IS 3M 689,518 | n/a | RIGHT |
| XOM capex FY 2014 | 32,952 | 0000034088-17-000017 R7 "Additions to property, plant and equipment" (32,952) | | RIGHT |
| XOM capex FY 2020 | 17,282 | 0000034088-23-000020 R7 (17,282) | | RIGHT |
| XOM capex FY 2022 | 18,407 | 0000034088-25-000010 R7 (18,407) | | RIGHT |
| XOM capex FY 2024 | 24,306 | 0000034088-26-000045 R7 (24,306) | | RIGHT |
| XOM capex Q 2016-03-31 | 4,601 | 0000034088-17-000027 R7 3M (4,601) | | RIGHT |
| XOM capex Q 2023-03-31 | 5,412 | 0000034088-24-000029 R6 3M (5,412) | | RIGHT |
| XOM capex Q 2025-03-31 | 5,898 | 0000034088-26-000067 R6 3M (5,898) | | RIGHT |
| XOM D&A Q 2014-09-30 | 4,362 | 0000034088-15-000044 R2 IS "Depreciation and depletion" 3M 4,362 | | RIGHT |
| XOM D&A Q 2015-06-30 | 4,451 | 0000034088-16-000082 R2 3M 4,451 | | RIGHT |
| XOM D&A Q 2015-09-30 | 4,542 | 0000034088-16-000097 R2 3M 4,542 | | RIGHT |
| XOM D&A Q 2018-09-30 | 4,658 | 0000034088-19-000062 R2 3M 4,658 | | RIGHT |
| XOM D&A Q 2019-06-30 | 4,631 | 0000034088-20-000073 R2 3M 4,631 | | RIGHT |
| XOM D&A FY 2014 | 17,297 | 0000034088-17-000017 R2 IS (also R7 CF) 17,297 | | RIGHT |
| XOM D&A FY 2017 | 19,893 | 0000034088-20-000016 R2 (also R6 CF) 19,893 | | RIGHT |
| XOM D&A FY 2018 | 18,745 | 0000034088-20-000016 R2 (also R6 CF) 18,745 | | RIGHT |

## Method

For each key I opened the store accession's FilingSummary and every Statements R page. I matched rows by XBRL element (the store tag) and columns by end date (within 7 days) and duration (3 or 12 months). For non-XOM keys I also opened the lane's original accession. XOM history is filed under CIK 0000034088: the store's accessions resolve under that folder, not under the new CIK 0002115436.

## Untested scope

- The other 40 XOM keys were not checked.
- I did not check whether each store accession is the LATEST accepted print. I checked that it prints the stored value. For FY values, the cited filing is the last 10-K that prints that year, as expected.
- XOM derived Q4 values were not in the sample.
- The 328 failing keys in `seeds_only` mode were not part of this brief.
