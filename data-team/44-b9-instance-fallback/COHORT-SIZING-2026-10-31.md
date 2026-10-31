# B9 instance fallback: top-1000 cohort dry run (2026-10-31, flag OFF, nothing written)

Run: `scrooner-normalize instance-fallback --ciks <986 cohort CIKs>` on branch work/engineering/b9-instance-fallback (603b181),
one read-only connection, FSN sets from the local fsn-notes copy (59 periods). Per-filing report: `cohort-dryrun-2026-10-31.jsonl.gz`.

| measure | value |
|---|---|
| companies checked | 986 |
| 10-K/10-Q filings in core.filing with zero core.fact rows (≥14 days old, period ≥ 2014-01-01) | 549 |
| ... with an FSN structure (fillable) | 123 at 113 companies (10-Q 61, 10-K 49, 10-Q/A 11, 10-K/A 2) |
| facts planned from those | 21,755 (face columns only; 274 new core.period rows) |
| ... with structure but zero planned facts | 9 |
| ... not in their FSN set | 426 |

Fillable filings by period year: 2012-13: 70 (13,652 facts, FY2013 10-Ks in 2014q1), 2021: 1 (118), 2024: 3 (437), 2026: 42 (7,548; FSN 2026m07-m09). Almost nothing 2014-2025.

## Why 426 are not in any FSN set (checked against EDGAR's own submissions JSON `isXBRL`, 4 req/s)

| class | filings | companies |
|---|---|---|
| filing carries no XBRL at all (`isXBRL = 0`) | 419 | 236 (ARCC 36, CIK 0001736035 14, 0000003570 8) |
| XBRL filing absent from its FSN set | 7 | 7 (six 10-K/A for FY2015 in 2016q1, one 10-Q 2015q2, one 10-K 2017q1), listed in `cohort-not-found-isxbrl-2026-10-31.json` |

So the "missing facts" backlog is mostly filings with no instance document (BDCs and others before the XBRL mandate reached them): no source
exists, B9 cannot fill them, and the blank reason should say so (`filing_has_no_xbrl`), not `line_in_filing_not_extracted`.
The 7 XBRL-but-absent cases are the only ones that need source (b) (reading the instance from the filing itself).

Skip counters over all 549: comparative_column 32,898 · custom_taxonomy 4,131 · cf_three_month_note 538 · 10k_non_annual_duration 488 · ytd_length_mismatch 2 · accession_not_in_fsn_set 426.

Condition 1 (facts.py refactor, flag OFF): `facts-refactor-equivalence-2026-10-31.txt`, 20 cohort companies, old vs new core.fact rows byte-identical.
Condition 2: CI run 41215739169 (603b181) ran tests/unit/test_instance_fallback.py 2/2 against the migrated Postgres service.
