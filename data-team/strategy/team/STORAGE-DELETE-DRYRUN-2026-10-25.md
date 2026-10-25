# Storage delete and pre-2015 cut: plan, backup plan, dry-run (2026-10-25)

> REVISION 2 (same day, founder decisions): the floor is now 2014-01-01 (delete only period_end < 2014-01-01), the storage rule is S (keep objects referenced by core.fact), the backup goes to a private Supabase Storage bucket. Sections 1-6 below are the first draft (2015 floor, rule A); where they differ, section 7 at the end wins.

Role: Data Engineer. Mode: read-only. Nothing was deleted or written. Authorization quoted from the main session: (a) delete duplicate companyfacts objects in bucket `raw` after hash check, keep latest payload per CIK; (b) no data before 2015-01-01 in the live DB, with a cold, restore-verified backup first.
Evidence labels: M = measured today by query (DATA-INFERRED about meaning, exact about counts); H = hashes re-computed from downloaded bytes; C = read from code; A = assumed. No FILING-CHECKED claims are made (none needed: this is storage and retention, not accounting).
Connections: 2 at most (pg_stat_activity showed 14-18 backends, all platform plus one peer light reader; statement_timeout 55-280 s on every session; read-only. Temp tables only, session-local, dropped on disconnect).

## 1. Duplicate companyfacts objects (part a)

Rows in `raw.sec_companyfacts`: 45,770 (6,592 CIKs, fetched 2026-08-13 to 2026-10-24), one object each, 87.03 GB (M). Distinct (cik, sha256): 8,829 = 16.75 GB. Every row joins to a Storage object; 4 extra objects have no row (2026-08-26, 0.35 MB total, keep).
One sha256 is shared by 6 CIKs (identical payload text); grouping is by (cik, sha256), so each CIK keeps its own copy.

Rule used (recommended, "A"): for every (cik, sha256) keep exactly one object, the most recently fetched; delete the rest. Consequences, all measured:
| | objects | bytes |
|---|---|---|
| Today | 45,770 | 87.03 GB |
| Keep (8,829 = one per cik+hash; includes the latest payload of all 6,592 CIKs, 0 CIKs missing) | 8,829 | 16.75 GB |
| **Delete** | **36,941** | **70.28 GB** (by month: Aug 8,874 / 18.7 GB; Sep 15,965 / 28.9 GB; Oct 12,102 / 22.7 GB) |
| of the delete set, referenced by `core.fact.raw_object_id` (FK `fact_raw_object_id_fkey`) | 4,178 rows | 9.34 GB |

- Changed payloads are all kept: 1,436 CIKs have more than one distinct hash; every distinct version keeps one object, so immutability for changed filings holds.
- Referenced rows: 5,994 raw rows are referenced by core.fact (12.5 GB). 4,178 of them are not the keeper of their hash group. Their bytes equal the keeper's bytes (see proof), so provenance is preserved by hash, but their `storage_path` will no longer resolve. Stricter alternative "S" (also keep every referenced object): keep 13,007 objects / 26.10 GB, delete 32,763 / 60.93 GB. A is recommended; S is the fallback if the reviewer rejects redirect-by-hash. Decision for reviewer, see section 5.
- Postgres rows are NOT deleted (append-only table, FK from core.fact). Only Storage objects go. A migration (not written, not applied) should add `raw.storage_object_retired(raw_id pk, keeper_raw_id, sha256, retired_at)` so any tool can resolve a retired path to its keeper.
- Readers checked in code (C): `normalizer/facts.py` and `normalizer/periods.py` read only `order by fetched_at desc limit 1` per CIK, which is always a keeper. The only other reader of old paths is `collector/integrity.py` (reconciliation head/download of every row); it will report the 36,941 retired paths as missing unless it consults the retired table. Update it first.

Hash check evidence:
- Full population, no download: for all 36,941 pairs (delete object vs keeper), Storage `eTag` and `size` are identical (0 mismatches) (M).
- Byte-level: 7 pairs (5 random under 3 MB, 2 referenced ones; largest 5.16 MB) downloaded from Storage and sha256 recomputed: 14 of 14 equal the sha256 recorded at ingest, for both the duplicate and the keeper (H).
- Before the real run the executor must repeat the byte check on a larger random sample (suggest 300 pairs, about 0.5 GB of download) and on every keeper that a retired row points to is not needed beyond that because eTag+size already match for all pairs.

Artifact: `data-team/strategy/team/STORAGE-DELETE-MANIFEST-2026-10-25.csv.gz` (36,941 lines, 1.0 MB): raw_id, cik, sha256, fetched_at, storage_path, bytes, referenced_by_core_fact, keeper_raw_id, keeper_storage_path. This manifest is itself the rollback map for the DB side; it is not a backup of the bytes.

Backup of the bytes before deleting: not required for the 36,941 duplicates, because an identical-bytes keeper (same eTag, size and, on the sample, recomputed sha256) stays in the bucket. Disk could not hold it anyway (70 GB vs 5.5 GB free). If the reviewer wants belt and braces, take one extra copy of the keepers' hashes (the manifest plus `select cik,sha256,storage_path from raw.sec_companyfacts`), about 5 MB.

Not covered (not authorized): `submissions` (bucket 16.7 GB, 91,571 objects; audit says 6.2 GB distinct, 0.6 GB latest). Same procedure could apply later with its own dry-run.

Required companion change (not done): the nightly collector must stop uploading identical bytes (audit lever 1), otherwise the bucket regrows 7-10 GB per week.

## 2. Pre-2015 cut in live tables (part b)

Cut definition: delete rows whose period end date is before 2015-01-01. Periods that straddle (start before 2015, end 2015 or later) stay: 5,142 periods (FY 894, Q1 151, Q2 109, Q3 106, Q4 156, YTD/unlabeled 1,114 plus other rows). `core.period` has 982,826 rows; 224,487 end before 2015.

Exact counts to delete (M, today):
| table | rows to delete | table total | approx bytes (pro rata of total relation size, A) |
|---|---|---|---|
| core.fact | 16,805,939 | 76.7M | about 7.0 GB (32 GB x 21.9%) |
| analytics.canonical_fact | 3,810,102 | 17.0M | about 1.05 GB |
| analytics.metric_value | 2,834,494 | 13.3M est | about 1.02 GB |
| analytics.timeseries_outlier_check | 462,118 | 2.1M est | about 0.18 GB |
| core.period | 224,487 | 982,826 | small (about 0.03 GB A) |
| core.fact_conflict_resolution (FK to fact) | 21,712 | 78,805 | small |
| analytics.identity_check_failure | 14,348 | about 55k | 0.01 GB |
| analytics.metric_plausibility_check | 2,253 | about 248k | small |
| analytics.company_stock_split (FK to fact) | 82 | 1,121 | small |
| core.employee_headcount_disclosure (report_date) | 13 | 9,835 | small |
| core.segment_revenue | 5 | 271 | small |
| canonical_fact_retired, canonical_fact_sanity_override, period_gap, cell_blank_reason, cell_evidence, certification_finding, concept_parser_result, frames_consistency_check, statement_comparison_finding, yfinance_statement_line | 0 | | |
| **Total logical** | about 24.2M rows | | **about 9.3 GB** |

Physical reality: a DELETE does not shrink Postgres files. Space comes back only after a table rewrite (VACUUM FULL or pg_repack, locks and needs temporary free space on the DB disk, which is Supabase's, not this Mac). core.fact has never been autovacuumed (10.6M dead tuples). Plan the rewrite as its own reviewed step. Also drop-order matter: delete children before parents because of FKs (fact_conflict_resolution, company_stock_split.source_fact_id, fact.supersedes_fact_id, canonical/other period_id FKs).

Other FK checks: the 82 stock-split events with pre-2015 source facts all have effective dates before 2015 (0 events dated 2015+ rely on a pre-2015 source fact), so they can be archived with the cut. A cross-boundary supersedes check (2015+ fact superseding a pre-2015 fact) timed out; it must be run chunked before the delete (any such row needs `supersedes_fact_id` set null, else the FK blocks).

### Hard dependency, must be fixed before the cut
The Normalizer (`normalizer/facts.py`) has no date floor (grep for 2015/floor: none). Every nightly reprocess re-reads the latest companyfacts payload, which contains all history, and would re-insert the deleted pre-2015 facts. A floor (skip facts with end date before 2015-01-01) in the Normalizer is therefore a precondition, shipped and tested separately. Same for `derived.py` and the Mapper if they query by period.

### What reads pre-2015 rows, and can it be served without them?
Counts are rows currently stored (M) unless noted; "affected" means value changes or turns blank after the cut.

1. Split bases. Split events: 1,121 total, 82 before 2015. Adjustment only touches values dated before the split, so 2015+ values do not need pre-2015 facts. Can be served: YES. Action: archive the 82 events with the cut. 0 cells affected.
2. Prior-year comparatives in 2015 filings, growth metrics (`mapper/ttm.py` GROWTH_METRICS lags 1, 3, 5, 10 years, `fcf_growth.py` 1, 3, 5). The prior period is pre-2015 for rows dated 2015 through 2014+lag. Metric rows in that range (M by period_end year, all period labels; non-null in brackets): yoy family and 3y/5y/10y CAGR total 992,935 rows (422,823 non-null). Largest: net_income_growth_10y 183,054 (41,420), eps_growth_10y 155,976 (37,135), revenue_growth_10y 155,983 (41,767), 5y families about 52-77k each, 3y families about 15-44k each, yoy families about 2-14k each. Can it be served without pre-2015: NO for all FY2015 yoy, FY2015-2017 3y, FY2015-2019 5y, and every 10y CAGR up to FY2024 (a 10y CAGR for FY2025 onward is fine). The current non-null values would become blank with a stated reason (`history_floor_2015`), which is consistent with doc 38 ("pre-2015 not a source of truth"). The 10y CAGR is the main loss: about 120k non-null cells (net income 41,420 + EPS 37,135 + revenue 41,767), and it can only exist again from FY2025 (10 years after 2015) or if founder keeps a flagged opening value.
3. 2015 TTM and Q4/interim derivation. Calendar-year companies need nothing before 2015 (Q4 = FY2015 minus 9M 2015, all dated 2015). Non-calendar companies whose fiscal 2015 started in 2014 (FY ends Jan-Sep 2015; 894 FY periods, 862 companies with a straddling FY) derive Q3/Q4 from YTD facts that ended in 2014. Upper bound of cells at risk: 85,834 derived facts in the 6,232 Q2-Q4 periods ended in 2015 of those companies (is_derived true, authoritative 85,782); 13,170 derived facts sit on straddling periods themselves. Also trailing-twelve-month rows ended during 2015 (Mar-Dec 2015 quarters) use quarters ended 2014; count of TTM rows for 2015 not isolated (period_label TTM shares the metric_value table; run `period_label='TTM'` per year chunk before deciding). Can be served: partially. Where the YTD chain starts before 2015, the derived value would be lost on the next nightly rederive (derive retires and rewrites). Minimal change: either accept a blank with reason `history_floor_2015` for those derived cells (at most 85.8k facts, likely far fewer once restricted to chains that really start in 2014; A) or keep the single needed YTD fact per such company-year as a flagged opening value (see item 4).
4. Opening balances. Instant facts dated 2014-12-31: 2,531 periods, 670,855 facts (204,482 authoritative). All instants in Q4 2014: 5,975 periods, 735,340 facts (235,697 authoritative). Used as the prior-year balance for FY2015 (Piotroski F-Score FY2015 compares with FY2014; FY2015 yoy share growth; cash opening balance for 2015 cash-flow tie-outs; average-balance ratios if any). Piotroski for FY2015 is metric rows of 2015: needs FY2014 inputs. Can be served: NO without the FY2014 balance and income inputs. Minimal change: a small `opening_value` table (company, concept, as-of date, value, source fact id, flagged "opening, pre-floor") holding only the FY2014 values of the concepts that the formulas read (not the 16.8M rows). Estimated size: about 78 concepts x 5.2k companies = under 0.4M rows (A, upper bound), versus 16.8M. Without it: FY2015 Piotroski and FY2015 yoy blank with reason.
5. Streak metrics (profitable_streak_years, dividend_growth_streak_years). Values change rather than blank: after the cut, streaks count only back to FY2015 (maximum about 11 by FY2025). Today 945 of 4,870 non-null profitable streaks and 230 of 1,786 non-null dividend streaks are 10 or longer (max 20 and 18). So at least 1,175 company values are shortened, and any streak above 11 becomes wrong rather than blank. Recommended: either blank them with reason or label "since 2015" in the UI. This is the one place where the cut could produce a wrong-looking number instead of an empty one; decision D4 below.
6. Per-share and share-count series (dilution trend, ~1yr ago comparisons): dated within 1-2 years of today, no pre-2015 need. dei:EntityPublicFloat and price metrics: price table is separate (Alpaca) and not in the cut.
7. Display: `apps/app` already floors history at 2015 (doc 38 rule 5: "Floor: 2015-01-01"), so no page loses a column; the 10-year metrics are the only visible change.

### Short decision list for the founder (counts of cells affected)
- D1. 10-year CAGR (revenue, EPS, net income) and 5-year CAGR before FY2020, 3-year CAGR before FY2018, yoy for FY2015: serve blank with reason `history_floor_2015` (about 120k non-null 10y cells plus about 300k other growth cells; 422,823 non-null growth cells in the affected years in total), OR keep a small flagged opening-value table. Recommended: blank with reason; it matches doc 38. They repopulate by themselves each year (10y CAGR returns at FY2025).
- D2. FY2015 Piotroski and balance-based FY2015 comparisons: accept blank for FY2015 only, OR keep the FY2014 opening values (under 0.4M rows, A). Recommended: keep the opening-value table only if the founder wants FY2015 shown; otherwise blank.
- D3. Non-calendar companies' 2015 derived quarters (upper bound 85.8k derived facts, 862 companies): accept blank/not-derived reason for chains that start in 2014, or keep the one YTD fact per chain. Recommended: accept blank; the first fully supported year for them is FY2016.
- D4. Streak metrics (at least 1,175 values shortened): blank, or relabel "since 2015". Recommended: relabel or blank; do not show a truncated count as if it were the whole streak.
- D5. Fiscal years 2014 and earlier stay out of the product entirely (no archive served). Cold backup is for restore only.
Anything the founder rejects in D1-D4 means the corresponding opening values stay in a separate small table, never the 16.8M-row history.

## 3. Backup plan (cold, compressed, restorable, verified)

Disk check (df): Data volume 228 GB, 5.5 GB free right now (it was 11 GB, then 8.0, then 7.9, then 5.5 during this session: other processes are consuming it; re-check immediately before running). Therefore: stream, never stage.

What is exported (exact filters, every column, ids preserved so a restore is a plain COPY back):
- core.fact where period_id in pre-2015 periods: 16,805,939 rows; core.period (224,487), canonical_fact (3,810,102), metric_value (2,834,494), timeseries_outlier_check (462,118), fact_conflict_resolution (21,712), company_stock_split (82), identity_check_failure (14,348), metric_plausibility_check (2,253), headcount (13), segment_revenue (5). Plus the retired-storage manifest and `raw.sec_companyfacts` row list (about 5 MB).
Format: `psql -c "\copy (query) to stdout with csv"` piped to `zstd -3`, one file per table and per chunk (chunk by period_id ranges of 3,000 periods, as measured: each chunk 3-5 min on the pooler; the whole fact export about 25-30 min of read time, one connection). Use `psql -q` and no `-c "set ..."` before it: a `SET` status line leaked into my first sample file (fixed by `sed 1d`); set the timeout via `PGOPTIONS=-c statement_timeout=...` instead.
Size (measured on a 274,117-row sample of pre-2015 fact rows): 83.7 B per row as CSV, 12.2 B per row zstd-3 (6.9x). Projection (A, linear): core.fact 1.41 GB CSV, about 0.21 GB compressed; whole export about 0.4 GB compressed (canonical_fact and metric_value are somewhat wider, assume up to 0.6 GB). That fits on this Mac (5.5 GB free) as a transient staging area if the destination is reachable; keep local copy under 1 GB, never extract.
Destination: outside the live database and not served. Candidates: a private bucket in a different system (founder-owned cloud drive / S3-compatible bucket) or at minimum a separate Supabase Storage bucket `cold-archive` (not counted as DB; counts against Storage allowance, which the dedupe frees). The founder picks; I did not choose a paid service. Keep two copies (Mac + external) until the live cut has run for 30 days.
Verification (done on a sample, to be repeated on the full export):
1. Per-file sha256 written to `MANIFEST.sha256`, and per-table row counts compared with the live counts above.
2. Restore test, run today on the sample (M): decompressed the 274,117-row file into a session temp table `like core.fact` with COPY: 274,117 rows restored (ids 3,548,668 to 299,445,762); then for 69 chunks of 4,000 ids the md5 of the row text of restored rows equalled the md5 of the live rows: 0 mismatches. Compressed sample file sha256 `cb52e1aa850a8eb731edf17f7d2601ed04b1a34f1d1244260fcf51c86fcfc4e3` (3.34 MB).
3. For the full run: restore every file into a scratch schema in a throwaway local Postgres (not the shared DB), compare per-table count and per-chunk md5 against live, then restore one full company (all tables) and re-run its pre-2015 metric calculation to confirm identical values.
The backup is exported BEFORE the Normalizer floor ships and before any delete; the live rows are re-exported for any period touched afterwards.

## 4. Rollback

Storage side: the deleted objects are byte-identical to a retained keeper (eTag, size and sampled sha256), so no bytes are lost. Rollback = copy the keeper object back to the retired path using the manifest (`keeper_storage_path` to `storage_path`, `x-upsert`), 36,941 server-side copies; the DB rows were never touched. Run the first delete on a pilot of 500 objects from the manifest, verify the normalizer reprocess of 20 of their CIKs and the integrity report, and only then the rest, in batches of 2,000 with the manifest ledger of what was done.
DB side: restore from the cold backup with COPY in this order: core.period, core.fact, fact_conflict_resolution, company_stock_split, canonical_fact, metric_value, then the check tables; re-point sequences are not needed because ids are explicit. Because the cut is a transaction per table chunk, a failed chunk rolls back by itself. Take a Supabase point-in-time/daily backup reference on the day of the cut (A: Pro plan has daily backups; confirm in the dashboard, I cannot see it). The pre-2015 cut also requires the migration for the opening-value table and retired-object table, each with a down-statement.

## 5. Steps and reviewers

1. Founder decides D1-D5 and the backup destination, and chooses rule A or S for referenced objects. (Founder)
2. Data Engineer: ship the Normalizer/derive date floor plus the `storage_object_retired` migration and the integrity.py change as one reviewed PR with tests (floor stops re-insertion; retired path resolves). Reviewer: Verifier plus Release Manager. Not yet written.
3. Data Engineer: run the full cold export (df first, ListAgents first, 1 connection, statement_timeout per chunk, chunks as above); Verifier restores it in a throwaway local Postgres and signs the counts and md5s. A different agent from the exporter (preparer is not approver).
4. Data Engineer: dry-run SQL for the cut that returns, per table, rows that would be deleted and the three FK cross-checks (supersedes, conflict-resolution, stock-split), expected to equal section 2 counts exactly; Release Manager reviews. Zero mismatch required.
5. Storage pilot of 500 objects, then batches, with the manifest as the ledger; Verifier re-samples 300 pairs by byte hash before and the normalizer reprocess for 20 CIKs after.
6. DB cut in chunked transactions, children before parents, off-peak, no peer heavy job running (ListAgents), then recompute affected metrics so blanks carry `history_floor_2015` and re-run `scrooner-certify`; then VACUUM FULL/pg_repack per table as a separate approved step.
7. Keep backups 30 days, then founder decides on retention.
Nothing in this document has been executed beyond read-only queries, temp tables, and 14 read-only Storage downloads. NOT_RUN: full export, full-byte hash check, cross-boundary supersedes count, TTM row count for 2015, VACUUM impact measurement.

## 6. Commands actually run (summary)
Read-only SQL on raw.sec_companyfacts and storage.objects (counts, hash groups, eTag comparison), core.fact/period/canonical_fact counts by chunked period_id lists, metric_value group-by on metric and year, pg_constraint for FKs, pg_stat_activity; `psql \copy` of 274,117 sample rows to zstd and restore into a session temp table with md5 comparison; 14 authenticated GETs of Storage objects with sha256; `df -h`. No secrets printed.

## 7. Revision 2: floor 2014-01-01, Rule S, private-bucket backup (all counts measured 2026-10-25)

### 7.1 Storage deletion list under Rule S (Rule A kept for comparison)
| | keep | delete |
|---|---|---|
| Today | 45,770 objects / 87.03 GB | |
| Rule A (one per cik+hash) | 8,829 / 16.75 GB | 36,941 / 70.28 GB |
| **Rule S (A plus every object referenced by core.fact.raw_object_id)** | **13,007 / 26.10 GB** | **32,763 / 60.93 GB** |
Manifest for S: `data-team/strategy/team/STORAGE-DELETE-MANIFEST-RULE-S-2026-10-25.csv.gz` (32,763 rows; every row has an identical-bytes keeper by eTag+size, 0 mismatches; none is referenced by core.fact, so no redirect table is needed under S, though it is still useful for integrity.py). The Rule A manifest stays for comparison. Nothing deleted. Because the delete set under S contains no referenced object, core.fact provenance paths all still resolve. Caveat: new fetches after today change the sets; regenerate the manifest on the day of execution and re-check "0 referenced".

### 7.2 Pre-2014 cut: rows and bytes (period_end < 2014-01-01)
| table | rows to delete | approx bytes (pro rata, assumed) |
|---|---|---|
| core.fact | 9,890,507 | about 4.1 GB |
| analytics.canonical_fact | 2,347,010 | about 0.65 GB |
| analytics.metric_value | 2,192,009 | about 0.79 GB |
| analytics.timeseries_outlier_check | 366,043 | about 0.14 GB |
| core.period | 177,558 (of 982,826) | about 0.03 GB |
| core.fact_conflict_resolution | 16,747 | small |
| analytics.identity_check_failure | 11,477 | small |
| analytics.metric_plausibility_check | 1,619 | small |
| core.employee_headcount_disclosure | 11 | small |
| core.segment_revenue | 5 | small |
| analytics.company_stock_split | 30 (all 30 have effective date before 2014) | small |
| frames_consistency_check, yfinance_statement_line, statement_comparison_finding, period_gap, canonical_fact_retired, canonical_fact_sanity_override, cell_blank_reason, cell_evidence, certification_finding, concept_parser_result | 0 | |
| **Total** | **about 15.0M rows** | **about 5.7 GB logical** (first draft at the 2015 floor: 24.2M rows / 9.3 GB) |
Space is only returned to the disk after VACUUM FULL or pg_repack, as before.
Straddling periods that stay (start before 2014-01-01, end 2014-01-01 or later): 5,519 (FY 874, Q1 177, Q4 121, Q2 108, Q3 100, YTD/unlabeled 1,180 and a few over 400 days). They keep all their facts, including values whose start date is in 2013. The instant 2013-12-31 is the only boundary instant that goes: 2,395 periods / 579,614 facts (180,300 authoritative), the opening balances of FY2014, which is why FY2014 is not fully supported (below).

### 7.3 Supersedes cross-boundary FK check (chunked, run)
core.fact.supersedes_fact_id: scanned in 2,000,000-id chunks of the target id, joined to both periods. Rows with a supersedes link covered: 890,743 (the count of 919,684 taken earlier today included rows written by the nightly job in between, A). Cross-boundary links (a fact with period end 2014+ superseding a fact with period end before 2014): **0**. Links whose target is pre-2014 (and whose superseding fact is therefore also deleted): 147,824, so the delete set is closed under the FK and `supersedes_fact_id` needs no nulling. The other FKs to core.fact are child tables deleted in the same cut (fact_conflict_resolution 16,747, company_stock_split 30). Delete order: fact_conflict_resolution and company_stock_split first, then core.fact (any chunk order, since 0 cross links), then canonical_fact and other period_id children, then core.period last.

### 7.4 Normalizer date floor design (floor = 2014-01-01)
Not written. Design for the PR:
- One constant `HISTORY_FLOOR = date(2014, 1, 1)` in `common/` (next to `derivation_policy.py`), imported by normalizer and derive code; `sanity/period_completeness.py` keeps its own display floor of 2015-01-01 (the two floors are different concepts: storage floor 2014, display floor 2015; document both in doc 38).
- Apply the filter at insert time, not when scanning the payload: in `normalizer/facts.py` right after `end_date = _parse_date(r["end"])` (about line 199) add `if end_date < HISTORY_FLOOR: stats["skipped_before_floor"] += 1; continue`. In `normalizer/periods.py` drop periods with `end < floor` only after the fiscal-year-end anchors and `fy_tagged_spans` are computed from the full payload (lines ~138-220 use old periods to infer the company's fiscal year ends; filtering earlier would change fiscal_year/fiscal_period labels of 2014 periods). Duration facts that start before the floor but end on or after it are kept.
- Derivation (`derived.py`) and the Mapper read only core.fact, so they need no change, but add a test that a rerun for one company inserts 0 rows with end before the floor and leaves the retained rows byte-identical (idempotent).
- Order of shipping: floor code merged and one nightly run observed (0 pre-2014 rows inserted) BEFORE the delete, otherwise the delete is undone by the next reprocess.
- Companyfacts payload size is unchanged (the raw bytes keep all history; only core drops it). The payload remains the source for rematerialization.

### 7.5 What the 2014 floor supports (honest first-year window)
Display floor stays 2015-01-01 (doc 38). With data kept from 2014-01-01 the following hold (derived from the code paths and the counts above; A for the row-label boundaries because metric_value rows are keyed by period end year, not fiscal-year label):
- Fully supported from FY2015 (all 2015 quarters and the FY): level metrics, margins, ratios, TTM, Q2/Q3/Q4 derivation for calendar-year companies and for non-calendar companies whose fiscal 2015 began in 2014 (their YTD chains start in 2014), 1-year growth (FY2015 compares with FY2014), Piotroski FY2015 (needs FY2014 balances and flows: retained), opening balances for 2015 (2014-12-31 instants: 2,531 periods / 670,855 facts, retained).
- FY2014 itself is only partly supported and is not displayed: its opening balances (2013-12-31 instants) and its prior-year comparatives are gone, so 2014 yoy growth, Piotroski FY2014 and TTM for Q1-Q3 2014 blank. Derived facts in the Q2-Q4 2014 periods of companies whose fiscal 2014 started in 2013: 5,970 periods, 264,890 facts, 72,516 derived and authoritative; those are the 2014 derived cells that may not be recomputable on a rerun. They are not shown in the product.
- Multi-year growth needs the prior value N years back, which stays at or after 2014:
  | metric family | first fully supported fiscal year | cells that stay blank among displayed years (period_end 2015 onward), non-null today |
  |---|---|---|
  | yoy (revenue, EPS, net income, dps, shares, FCF) | FY2015 | 0 |
  | 3-year CAGR | FY2017 (FY2015, FY2016 blank) | 71,646 non-null today (rows 109,888) |
  | 5-year CAGR | FY2019 (FY2015 to FY2018 blank) | 112,870 (rows 212,578) |
  | 10-year CAGR | FY2024 (FY2015 to FY2023 blank) | 95,785 (rows 432,839) |
  | total | | **280,301 non-null cells** that become blank with reason `history_floor_2014` (was 422,823 with the 2015 floor) |
  By metric (displayed years): 10y: net_income 32,919, revenue 33,391, eps 29,475; 5y: net_income 28,987, revenue 28,277, eps 26,407, diluted_shares 24,489, fcf 4,710; 3y: net_income 16,320, diluted_shares 15,760, revenue 15,068, eps 14,910, dps 7,090, fcf 2,498. Counts include all period labels (quarter rows as well as FY), so treat them as the cell upper bound.
  Note this is wider than "10-year CAGR only": the 3-year and 5-year CAGRs of the early years also go blank. Each is a blank with a stated reason, never a wrong number.
- Streak metrics (profitable_streak_years, dividend_growth_streak_years) walk back to the first retained FY2014, so the maximum becomes FY2014 through the latest FY (12 years if the latest is FY2025). Today: profitable streak values above 12: 809, equal to 12: 40 (max 20); dividend streak above 12: 152, equal to 12: 37 (max 18). So at least 961 values would be shortened to 12 and 77 more may be exactly truncated. These are the one case where the cut yields a lower number, not a blank. Rule: store the capped value with the flag/ reason `history_floor_2014` ("12+ years" style), or blank them. margin_expanding_3yr is unaffected (value 0/1 over 3 years).
- Split bases: all 30 pre-2014 events have effective dates before 2014; no retained value needs them. 0 cells.

### 7.6 D1-D5 after the 2014 floor
- D1 (growth metrics): shrinks from 422,823 to 280,301 non-null cells (3y, 5y, 10y early years); yoy no longer affected. Reason code `history_floor_2014`.
- D2 (opening balances / Piotroski FY2015): resolved, kept. No opening-value table needed. FY2014 Piotroski blank (not displayed).
- D3 (2015 derived quarters, non-calendar): resolved for 2015 (chains starting in 2014 retained). Only 2014 derived cells (up to 72,516) lose inputs, not displayed.
- D4 (streaks): remains, at least 961 shortened values (809 profitable + 152 dividend) plus up to 77 at exactly 12.
- D5: cold backup only; nothing before 2014 served.
So the remaining visible effects are exactly: CAGR early years (280,301 cells, reason `history_floor_2014`) and streak metrics (961 to 1,038 values).

### 7.7 Backup to a private Supabase Storage bucket
Same export as section 3 with the 2014 filter (fewer rows: fact 9.89M; projected 0.12 GB compressed for fact at the measured 12.2 B/row, about 0.25-0.35 GB for the whole export, A). Destination: a new private bucket `cold-archive` (public = false, no policies for anon/authenticated; accessed with the service role only), path `pre2014/YYYY-MM-DD/<table>/<chunk>.csv.zst` plus `MANIFEST.sha256` and row counts. Creating the bucket is a write and needs the go-ahead; not done. Note this bucket is in the same Supabase project, so it is not protected against loss of the project; keep a second local copy (under 0.4 GB) until the cut has been stable for 30 days. Stream each chunk (psql to zstd to HTTP upload) without writing large temp files; disk free was 5.5 GB. The restore test on the sample (274,117 rows, 69 md5 chunks, 0 mismatches, section 3) stands; repeat it on the real files from the bucket before the delete.

### 7.8 Commands run for revision 2
Read-only: chunked counts over pre-2014 period ids for core.fact and canonical_fact (177,558 periods, chunks of 3,000, adaptive split on timeout); counts per table with the date filter; supersedes scan in 2,000,000-id chunks joined to both periods; straddling-period and 2013-12-31 instant counts; streak value distribution; derived-fact counts for 2014 Q2-Q4 of straddling companies; local transformation of the Rule A manifest into the Rule S manifest. Two connections at most. NOT_RUN: full export, bucket creation, full byte-hash check, TTM row count by year.
