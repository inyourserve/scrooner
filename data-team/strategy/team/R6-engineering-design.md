# R6. Engineering design and cost: STRUCTURAL + COMPOSITION layer (2026-10-21)

Role: Scrooner data engineer. Read-only: no code, no migration, no DB query (pooler not probed; nothing here depends on a DB count). Labels: FILING-CHECKED / DATA-INFERRED / ASSUMED. Nothing below is an accounting definition: perimeter codes are PROPOSALS for the Standardization Lead and a named accountant.

Measured this session (sec.gov HEAD and Range requests only, about 0.5 MB downloaded in total, deleted; SEC_USER_AGENT from pipeline/.env, not printed):
- DATA-INFERRED, FSDS 2025q4 zip (local): zip 65.8 MB; members compressed/uncompressed: pre.txt 18.3/88.4 MB (719,346 rows), num.txt 43.2/567.6 MB (3,832,977 rows), sub.txt 0.5/1.9 MB, tag.txt 3.8/17.9 MB. pre rows by statement: BS 230k, CF 220k, IS 134k, EQ 93k, CI 18k, UN 20k, SI 4k. Custom-tag lines (pre `version` = the adsh): 81,536 of 719,346 = 11.3%.
- DATA-INFERRED, FSN (Financial Statement and Notes) 2025q3 zip, 463 MB, read from its central directory by HTTP Range (last 300 KB): `cal.tsv` 8.6 MB compressed / 92.8 MB uncompressed; `pre.tsv` 78.8 MB / 600 MB; `num.tsv` 111 MB / 1.19 GB; `txt.tsv` 209 MB. Whole-file sizes: 2023q1 631 MB, 2024q2 533 MB, 2025q2 520 MB, 2025q3 463 MB; monthly files from late 2025 range 56 MB (2026_09, 2025_12) to 308 MB (2026_03, 2026_05). FSN URL pattern: `https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets/{YYYYqN|YYYY_MM}_notes.zip` (the `financial-statement-and-notes` path 404s). FSDS URL: `.../financial-statement-data-sets/{YYYYqN}.zip` (2023q1 114 MB, 2026q2 60 MB).
- Consequence: a Range read of ONE zip member needs no whole-file download and no disk. The calculation member we need (`cal.tsv`) is about 9 MB per quarter, the statement presentation member (FSDS `pre.txt`) about 18 MB. This removes the disk constraint (local dev disk: 3.4 GB free, 99% full).
- Not verified: `cal.tsv` column layout (read `readme.htm`, 18.5 KB compressed, member in the same zip, before coding); whether Range requests are honoured on every file (they were on 2025q3 and 2026_05); FSN quarterly files before 2025 vs monthly after (the monthly files appear to be incremental slices: confirm they do not duplicate accessions across months).

---------------------------------------------------------------------------
## 1. Where each component sits (boundary rules) and tables reused vs new

Rule set (pipeline/CLAUDE.md): Collector fetch/retry/hash/store only; Normalizer no mapping and no formulas; Mapper never writes `core`, never bypasses `is_authoritative`; the six frozen modules are not to grow later-phase logic. So the new work does NOT go into the frozen folders except two thin, pure-fetch pieces. Precedent: `sanity/`, `ownership/`, `segments/`, `certification/` are adjacent packages that read/produce evidence without entering the frozen six.

| Component | Module (new) | Boundary | Writes |
|---|---|---|---|
| Range-zip fetcher (fetch member bytes, hash, log; no parse) | `collector/bulk_datasets.py` + one new method `SECClient.get_range(url, start, end)` in `common/sec_client.py` (shared file: tell its owner first; today `get()` has no header argument) | Collector. Dumb: URL, byte range, sha256, size, status. Does NOT keep the bytes (see below). | `raw.sec_bulk_dataset_fetch` |
| Parsers for pre / cal / num (pure functions over a line iterator) | `structure/parse_pre.py`, `structure/parse_cal.py`, `structure/parse_num.py` | New adjacent package `structure/` (evidence, not Normalizer): never touches `core`, never writes a value into `analytics.canonical_fact` | none (pure) |
| Loader (filter to our universe and accessions, stage, upsert) | `structure/load.py`, Typer CLI `jobs/structure.py` -> `scrooner-structure` | structure/ | `analytics.filing_statement_line`, `analytics.filing_calc_edge`, `analytics.structure_ingest_log` |
| Recipe/perimeter builder (per company+concept: which tags the line is made of, from cal edges) | `structure/recipe.py` | structure/ ; proposal output only | `analytics.company_concept_recipe` |
| Path-B resolver (line -> canonical concept by statement, position, cal rollup to anchor, label class) | `structure/resolver.py` | structure/ ; candidate generator and wrong-value detector. Never writes `canonical_fact`. | `analytics.structure_concept_candidate` |
| Identity engine on the filing's own numbers (num stream) | `structure/identities.py` | structure/ | `analytics.filing_identity_check` |
| Invariant adapter (rows -> `Finding`s) | `certification/structure_checks.py`, registered in `certification/runner.py` `CHECKS` | certification/ (observer, already allowed to read analytics) | via existing `certification_finding` |
| Adoption of a perimeter / path-B fill into displayed values | later `mapper/composition_resolve.py`, behind Standardization Lead sign-off and Verifier sample | Mapper. Out of scope of the first build; not designed beyond the interface (reads `company_concept_recipe` rows with `status='adopted'`). | `analytics.canonical_fact` via the existing `_resolved` pattern |

Lossless/immutable question: the Collector rule says raw is kept. Streaming-and-deleting the zip bytes breaks "re-derive from raw". Resolution proposed (ASSUMED acceptable, needs founder/architecture call): the bulk datasets are re-downloadable public files with a stable SEC URL; we store URL + member + byte length + sha256 + SEC `Last-Modified`/ETag in `raw.sec_bulk_dataset_fetch` (precedent: the 13F and N-PORT bulk fetch logs in `raw`), so any later change by SEC is detected and any result is reproducible by refetching. We do not keep the multi-GB bytes. If the founder wants lossless, store only the filtered per-company rows as the raw tier (see 2.4).

### Reused (no change)
`core.company`, `core.filing` (accession_number text unique; company_id; form; period_of_report) is the join key to FSDS `adsh` (dashed form matches `0001562762-25-000269`); `core.concept` (taxonomy, tag); `analytics.canonical_concept`/`concept_mapping` (path A vocabulary, read only); `analytics.company_filing_line_evidence` (face-line presence from R*.htm: keep, structure supersedes its evidence source over time but do not drop it); `sanity/accounting_identity.IDENTITIES` + `evaluate()` (reuse the declarative identity definitions and the NCI/temporary-equity adjustment powerset; it is the tested engine); `certification/` (model, loader, runner, `analytics.certification_finding`, `company_certification`); `analytics.tag_concept_verdict`/`company_data_finding` (decisions are recorded there via `record-verdict`/`record-finding`, not in new tables); `analytics.sec_tag_library`.

### New tables (DDL sketch; migrations in section 4)
```sql
-- raw tier: what we fetched (Collector precedent)
create table raw.sec_bulk_dataset_fetch (
  id bigserial primary key,
  dataset text not null check (dataset in ('fsds','fsn')),
  period_label text not null,              -- '2025q4' | '2026_05'
  member text not null,                    -- 'pre.txt' | 'cal.tsv' | 'num.txt' | 'sub.txt' | 'readme.htm'
  url text not null,
  http_status int not null,
  bytes_fetched bigint, member_uncompressed bigint,
  sha256 text,                             -- of the uncompressed member stream
  etag text, last_modified text,
  rows_read bigint,
  fetched_at timestamptz not null default now(),
  unique (dataset, period_label, member, sha256)
);

-- statement-line evidence (FSDS pre.txt, FSN pre.tsv for older): one row per displayed line per filing
create table analytics.filing_statement_line (
  accession_number text not null references core.filing(accession_number),
  company_id bigint not null references core.company(id),
  report int not null,                     -- pre.report
  line int not null,                       -- pre.line (display order)
  stmt text not null check (stmt in ('BS','IS','CF','EQ','CI')),
  inpth smallint not null,                 -- parenthetical flag
  tag text not null,
  taxonomy_version text not null,          -- 'us-gaap/2024' | accession (custom)
  is_custom boolean not null,              -- taxonomy_version = accession_number
  plabel text not null,
  negating boolean not null,
  primary key (accession_number, report, line)
);
create index on analytics.filing_statement_line (company_id, stmt);
create index on analytics.filing_statement_line (tag) where is_custom;

-- calculation tree (FSN cal.tsv): parent/child arcs with weight, per filing and statement role
create table analytics.filing_calc_edge (
  accession_number text not null references core.filing(accession_number),
  company_id bigint not null references core.company(id),
  stmt text,                               -- from the cal group joined to pre; null if unmatched
  grp int not null,                        -- cal group / role id as in cal.tsv (confirm from readme)
  parent_tag text not null, parent_is_custom boolean not null,
  child_tag text not null,  child_is_custom boolean not null,
  weight smallint not null check (weight in (-1,1)),
  ord int,
  primary key (accession_number, grp, parent_tag, child_tag)
);
create index on analytics.filing_calc_edge (company_id, parent_tag);

-- ingest bookkeeping (idempotency by accession)
create table analytics.structure_ingest_log (
  accession_number text primary key references core.filing(accession_number),
  company_id bigint not null,
  source text not null, source_period text not null, source_sha256 text not null,
  lines int not null, edges int not null,
  ingested_at timestamptz not null default now()
);

-- composition: per company, per canonical concept, per filing-scope: what the line is made of
create table analytics.concept_perimeter (       -- vocabulary; PROPOSED by Standardization Lead
  concept text not null, perimeter_code text not null, description text not null,
  status text not null default 'proposed' check (status in ('proposed','adopted','rejected')),
  decided_by text, decided_at timestamptz,
  primary key (concept, perimeter_code)
);                                                -- e.g. (capex,'gross_ppe_only'),(capex,'net_of_disposals'),(d_and_a,'depreciation_only'),(d_and_a,'dep_plus_amort_intangibles')
create table analytics.company_concept_recipe (
  id bigserial primary key,
  company_id bigint not null references core.company(id),
  concept text not null,                    -- base canonical concept
  anchor_tag text,                          -- the filer's total (cal parent) or the single line tag
  components jsonb not null,                -- [{tag,weight,label,is_custom,source:'cal'|'pre'}]
  recipe_hash text not null,                -- sha256 of canonical-sorted components
  perimeter_code text,                      -- null = unclassified
  status text not null default 'observed' check (status in ('observed','proposed','adopted','rejected')),
  first_accession text not null, last_accession text not null, n_filings int not null,
  unique (company_id, concept, recipe_hash)
);
-- recipe change between consecutive filings of one company = series break (invariant I13)

-- path B output: never publishes, only compares
create table analytics.structure_concept_candidate (
  accession_number text not null, company_id bigint not null,
  concept text not null, tag text not null, stmt text not null, line int not null,
  rule text not null,                       -- 'anchor_rollup'|'label_class'|'position_after'...
  path_a_tag text,                          -- what the vocabulary mapper picked for this filing (null = none)
  outcome text not null check (outcome in ('agree','disagree','b_only','a_only')),
  value_b numeric, value_a numeric, gap_rel numeric,
  checked_at timestamptz not null default now(),
  primary key (accession_number, concept)
);

-- identity results on the filing's own numbers (num stream) AND on stored canonical values
create table analytics.filing_identity_check (
  accession_number text not null, company_id bigint not null,
  identity text not null,                   -- 'balance','gross_profit','ni_is_vs_cf','cash_roll','calc_subtotal:<parent_tag>'
  period_end date not null, qtrs smallint not null,
  lhs numeric, rhs numeric, gap_rel numeric, tolerance_rel numeric,
  precision_floor numeric,                  -- rounding unit implied by the reported scale
  passed boolean not null,
  detail jsonb not null default '{}'::jsonb,-- adjustments used, missing children, children list
  method text not null check (method in ('filing_num','stored_canonical')),
  primary key (accession_number, identity, period_end, qtrs, method)
);
```
Row-count and size estimates (ASSUMED, from the measured 2025q4 mix; pilot measures them):
- `filing_statement_line`: IS+BS+CF are 584k of 719k pre rows (81%, measured), so full population is about 580k rows per quarter if all filings kept. Top-1000 only: ASSUMED 25% -> about 150k rows per quarter x 15 quarters (2023q1-2026q3) = about 2.2M rows, about 150 B/row incl. indexes = about 330 MB. Full population 8.7M rows, about 1.3 GB. The database is already about 46 GB and has restarted under load (2026-10-18/19): start with top-1000, 10-K and 10-Q only, and prune to the latest 8 10-K/10-Q per company (rolling) after the pilot reads size.
- `filing_calc_edge`: ASSUMED 20-30% of the 93 MB uncompressed cal member survives the universe and statement filter; about 40k-100k edges per quarter for top-1000.
- recipes: about 6 concepts x 1,000 companies x 1-3 recipes = under 20k rows.
- `filing_identity_check`: only failures plus a per-(company, identity) pass counter would be small; store passes too for the top-1000 (about 8 identities x 1,000 x 12 periods = 100k rows), failures in full for others.

---------------------------------------------------------------------------
## 2. Ingestion plan: FSDS / FSN given a full dev disk and Actions limits

### 2.1 Mechanism (zero disk)
1. `HEAD` the zip for Content-Length, then `GET Range: bytes=-300000` to read the end-of-central-directory and central directory (it listed 10 members in 300 KB for the 463 MB 2025q3 file; FILING-CHECKED in this session). If the directory does not fit, widen the tail once.
2. For each wanted member (pre, cal, sub; optionally num): read local header offset + compressed size from the central directory, `GET Range` that span, inflate with `zlib.decompressobj(-15)` in 1 MB chunks, split lines, feed the parser generator. Peak memory about 2 MB. Nothing is written to disk. If a Range is refused (non-206), fall back to `download_to_file` into the repo cache dir, parse, delete in a `finally`, and abort if `shutil.disk_usage` free < 2x the zip size.
3. Two sources, to avoid pulling FSN's 600 MB `pre.tsv`:
   - Statement presentation: FSDS `pre.txt` (statements only, 18.3 MB compressed per quarter). FSDS also gives `sub.txt` (form, fiscal period, adsh -> cik).
   - Calculation tree: FSN `cal.tsv` (about 9 MB compressed per quarter). FSN `sub.tsv` (1.5 MB) maps its adsh.
   - Values for the identity suite: FSDS `num.txt` (43.2 MB compressed per quarter), filtered at the stream to: universe accessions, `segments` empty and `coreg` empty (consolidated, no dimensions), and tags in `identity_tag_set` (anchors, their cal children, about 150 tags). Output of this pass is only identity rows (section 3), never the 3.8M raw rows.
4. Bytes per quarter: pre 18.3 + cal 8.6 + sub 2.0 = about 29 MB; with num about 72 MB. 15 quarters (2023q1 to 2026q3): about 0.44 GB without num, about 1.1 GB with num. Everything is also fine on the local Mac (no disk) and the Actions runner (ubuntu-latest has about 14 GB free ASSUMED, irrelevant because nothing is written).
5. SEC etiquette: 5-6 requests per quarter (HEAD, tail, 3-4 member ranges), far below the 8 req/s ceiling; use `SECClient` (declared User-Agent, shared rate limiter), one SEC fetch process at a time (infra map rule 6). Make the rate limiter apply to each range request.

### 2.2 Runtime estimate (ASSUMED rates; the pilot measures them)
- Fetch: 29-72 MB at an assumed 3-10 MB/s from a GitHub runner = 5-25 s per quarter.
- Parse: Python `csv` about 150-300k rows/s: pre 0.72M rows = 3-5 s; cal about 1M rows = 4-7 s; num 3.8M rows = 15-30 s. Universe filter by a `set[str]` of adsh (loaded from `core.filing` once).
- DB load: COPY to a TEMP staging table then `insert ... on conflict do nothing` per accession batch (about 20 accessions): 150k rows/quarter = 10-30 s.
- Per quarter about 1-2 min; 15-quarter top-1000 backfill about 20-30 min; full-population backfill about 40-60 min. Steady state: one new quarter or one monthly FSN slice per run, about 2 min.

### 2.3 Scheduling and GitHub Actions
- New workflow `.github/workflows/pipeline-structure.yml`: monthly cron (SEC publishes FSDS quarterly, FSN monthly) plus `workflow_dispatch` (inputs: `period`, `top_n`). It must join `concurrency.group: heavy-db-jobs` (cancel-in-progress false) like `pipeline-sanity.yml`, `timeout-minutes: 90`, per-step caps 30 min (`scripts/lib/sharded.sh` STAGE_TIMEOUT_SECS convention). Do NOT add it to the nightly `pipeline-refresh.yml`: that job already has a 180-minute cap and four consecutive cancelled nights (2026-10-17); a second long stage there repeats the failure mode.
- Nightly gets only a cheap step: `scrooner-certify run --checks structure --top1000-shard ...` reading already-ingested tables (pure SELECT, bounded 20 min), so identity findings refresh when recompute changes stored values (this is where the nightly benefits: stored-vs-filing comparison is re-run after every reprocess without re-fetching).
- Freshness gap: a filing is in the structure tables only after SEC publishes the next monthly/quarterly set (up to about 5 weeks ASSUMED). For brand-new filings the existing `parsers/filing_line_evidence.py` R*.htm path stays the stopgap; do not build a second per-filing parser now.
- Free-minutes budget: unknown plan (ASSUMED private repo on a paid or free tier); the monthly job is about 30-60 min/month, but check `heavy-db-jobs` queue depth: GitHub keeps one pending run per group.

### 2.4 Cost summary
Storage top-1000 about 0.35 GB (+ recipes/candidates/identities under 0.1 GB) vs a database of about 46 GB; compute about 1 hour/month of Actions; engineer time section 5. The expensive part is human review, not machines.

---------------------------------------------------------------------------
## 3. Identity-check suite: code design

Principle (from data-team/34, 33 and 39): identities run on TWO substrates, because they answer different questions.
- `method='filing_num'`: the filing's own reported numbers (num stream). Question: "is the filing self-consistent, and what does its tree say?" Independent of our pipeline. A failure is mostly a filer error or a perimeter issue, rarely ours.
- `method='stored_canonical'`: our `canonical_fact` display layer (what certification already reads). Question: "did we pick/derive wrong?" A failure where the filing passes is OUR bug: highest-value signal.
The diagnostic table is the 2x2: filing passes/fails x stored passes/fails.

### 3.1 Module layout
```
structure/identities.py        pure engine over a dict {(tag, period_end, qtrs): Decimal} per accession
structure/identity_defs.py     declarative defs (tuples, same style as sanity/accounting_identity.IDENTITIES)
certification/structure_checks.py   rows -> Finding (reads analytics.filing_identity_check for the chunk)
certification/ties.py          unchanged (stored_canonical I1/I2 stay here)
```
Reuse `Identity`, `evaluate()` from `sanity/accounting_identity.py` for linear identities (it already has the tautology guard and the NCI/temporary-equity adjustment powerset). New code only for: tag-level (not concept-level) values, the cal-tree sum, and precision.

### 3.2 The identities
1. Balance: `Assets = Liabilities + LiabilitiesAndStockholdersEquity`-style. Use the filing's own `Assets` vs `LiabilitiesAndStockholdersEquity` (these are two face totals that must be equal exactly, up to rounding) as the primary tie, and `Assets = Liabilities + Equity (+ MinorityInterest + temporary equity)` via the existing powerset as the secondary. Tolerance: relative 2% (existing) but not looser than `max(rel, 2 x reporting unit)`. Failure beyond 25% = `wrong_value` (existing `WRONG_GAP`), else `review`.
2. Gross profit: `GrossProfit = Revenues - CostOfRevenue` only when all three tags are present as lines in the same IS report; skip (not pass) when gross profit is derived from its own terms (tautology guard). Tolerance 1%. Do not run for filers whose IS has no cost line (banks): `is_bank`/`sector.py` reuse.
3. Net income IS vs CF (the 324/324 PoC check). Caveat that must be in the code docstring: when IS and CF use the SAME element and the same context the facts are identical and the check is vacuous; it only bites where the tags differ (`ProfitLoss` vs `NetIncomeLoss`, or a custom line) or where OUR stored `net_income` differs from the filing. So implement as three comparisons: (a) filing IS net income line vs filing CF first line (value, allowing ProfitLoss vs NetIncomeLoss+NCI), (b) stored `net_income` vs (a), (c) stored `net_income_resolved` vs (a). (b)/(c) are the real wrong-pick detector. Also report `ProfitLoss - NetIncomeLossAttributableToNoncontrollingInterest = NetIncomeLoss`.
4. Cash roll: `CashAndCashEquivalentsPeriodIncreaseDecrease = CFO + CFI + CFF (+ EffectOfExchangeRate...)` on the filing; stored side already exists in `ties.py` (CASH_ROLL_TOLERANCE 10%, restricted-cash caveat). Add: choose the cash-change tag from the CF's last subtotal line by `pre` position instead of by name.
5. Subtotal tree sums (new, the composition core): for each cal parent in {BS, IS, CF} with all children valued in the same context: `parent = sum(weight x child)`. Tolerance `max(0.5%, n_children x unit_rounding)`, unit from the `num.decimals`/scale (num.txt has no decimals column in the sample header: `adsh tag version ddate qtrs uom segments coreg value footnote`; use trailing zeros of values as the rounding unit). Outcomes: `passed`; `children_missing` (a child has no value: tree incomplete, NOT a failure); `failed`. A failed tree on a parent that maps to one of our concepts (e.g. CostsAndExpenses -> opex, per the CVX ledger case) is the evidence for a `company_concept_recipe` row, not a finding by itself. Weights are signed from `cal`; never infer sign from labels.
6. Cross-statement: `CashAndCashEquivalents (BS) = ending cash (CF)` where both exist; `Depreciation...` appears on CF and IS notes only if same tag: skip.
Out of scope: retained earnings roll-forward (needs EQ statement parsing and dividends; propose later), quarterly YTD tie (Period Engineer lane).

### 3.3 Where it plugs in
- `jobs/structure.py` `scrooner-structure identities --period 2025q4 --top-n 1000 [--apply]`: dry-run default (same convention as `scrooner-certify`), writes only `analytics.filing_identity_check`.
- `certification/runner.py`: add `structure_checks.check` to `CHECKS`; `loader.load_chunk` gets one extra SELECT (set-based over the chunk's company ids, `statement_timeout` explicit, same pattern as `debt_facts`) filling a new `CompanyData.identity_rows`. Findings: failures with `method='stored_canonical'` or (filing passes AND stored fails) map to the existing `I1` (balance) and `I2` (gross profit, net income, cash) with `evidence.source='structure'`. This needs NO constraint change.
- New invariants require widening the check constraint on `analytics.certification_finding.invariant` (migration; the current constraint allows I1-I11 only) and `INVARIANTS` in `certification/model.py`: `I12 structure_disagree` (path A vs path B outcome='disagree' on a value, severity review until Verifier-confirmed) and `I13 recipe_changed` (same company+concept, consecutive filings, `recipe_hash` differs: a series break, severity review, evidence lists added/removed components). Both are small; ship identities first, I12/I13 after the pilot.
- Nightly: the SELECT-only certify step described in 2.3. Findings feed `scrooner-incidents` through the existing path, no new dashboards.

---------------------------------------------------------------------------
## 4. Idempotency, incrementality, connection discipline, migrations, tests

Idempotency and incrementality (by accession)
- Unit of work = one accession. `structure_ingest_log(accession_number)` marks done. A run selects `accessions_in_zip ∩ universe(core.filing, form in 10-K,10-Q,10-K/A,10-Q/A) − already logged`. Re-run of a finished quarter is a no-op after the log lookup (no parse of rows for done accessions beyond the cheap adsh filter).
- Row keys are natural (accession, report, line) etc.; inserts are `on conflict do nothing`. If SEC republishes a member and `source_sha256` differs for an accession already logged: delete-then-insert that accession's rows in ONE transaction (`filing_statement_line`, `filing_calc_edge`, `filing_identity_check where method='filing_num'`, log row), never a partial replace.
- Recipes and candidates are derived tables: rebuilt per company by `delete where company_id = X and status='observed'` then insert, in one transaction per chunk of at most 25 companies; rows with status `proposed/adopted/rejected` are human decisions and are never deleted by the rebuild (the project's repeated shared-table delete-scope bug, pipeline/CLAUDE.md "Shared-table writes"). Scope every delete by (company_id, concept, status), not company alone.
- No writes to `core.*`, `analytics.canonical_fact`, `concept_mapping`, `canonical_concept`.

Connection / pooler / timeout
- One connection per process; `ListAgents` and `select count(*) from pg_stat_activity` (<= 14) before any apply; `structure` uses `common/config.py` keepalives and `db/connection.py::run_write_with_reconnect`, `common/errors.py::safe_rollback` per accession/company loop; no shard parallelism for bulk SQL (more shards = more fights over the same pages); SEC fetch is single-process.
- Explicit `set statement_timeout` per stage: 60 s reads (matches `certification` DEFAULT_TIMEOUT_S), `set local statement_timeout='10min'` for the staging merge, bulk writes chunked (COPY per accession batch; `executemany` <= 5,000 rows). A reconnect resets the timeout: the retry helper re-issues it.
- Heavy: ingest and rebuild join the `heavy-db-jobs` concurrency group; never run alongside nightly reprocess or sanity.
- Disk: nothing written; if the Range fallback is used, abort on free < 2x zip.

Migrations (doc/planning/53 ledger: next free 0098; 0096 and 0097 committed but NOT applied)
- 0098 `structure_evidence_tables`: `raw.sec_bulk_dataset_fetch`, `filing_statement_line`, `filing_calc_edge`, `structure_ingest_log` (+ indexes).
- 0099 `structure_composition_tables`: `concept_perimeter`, `company_concept_recipe`, `structure_concept_candidate`, `filing_identity_check`.
- 0100 `certification_invariants_i12_i13`: drop and re-add the invariant check on `certification_finding` with I12, I13 (a `alter table ... drop constraint` is fast on the empty/small table). Claim all three numbers in doc 53 BEFORE writing; ends with `;`; applied only after commit; no gap. Because 0097 is unapplied, apply order is 0097 then 0100 or the ALTER fails: note this dependency in the migration header comment. No `CONCURRENTLY` index (tables are new/empty at creation); later index additions use the `SET statement_timeout=0` detached `psql -f` procedure.
- CI: `scripts/check_migrations.py` and a clean-DB replay; PG16 in CI vs PG14 locally: avoid PG15+-only syntax (no `unique nulls not distinct`).

Tests (cd pipeline && uv run pytest tests/unit)
- `tests/unit/test_structure_parse.py`: pre/cal/num parsers on tiny tab-separated fixtures built from real rows (copy 30 lines of the 2025q4 files into `tests/fixtures/structure/`, including a custom-tag line and a parenthetical `inpth=1` line).
- `test_structure_zip_range.py`: build a zip in memory, serve a fake Range responder, assert member bytes equal `zipfile` output and that no file is created; test non-206 fallback deletes its temp file in `finally`.
- `test_structure_identities.py`: each identity has a pass fixture, a fail fixture, a "children missing" fixture (must be skipped, not failed), a tautology fixture, and a `ProfitLoss` vs `NetIncomeLoss` fixture.
- `test_structure_recipe.py`: same cal tree -> same `recipe_hash`; reordered children -> same hash; changed weight -> different hash.
- `test_structure_idempotency.py`: ingest twice on a scratch Postgres (CI `postgres:16`), row counts equal; changed sha256 triggers replace-per-accession; human-status recipe row survives a rebuild.
- `test_certification_structure_checks.py`: extends `tests/unit/certification_fixtures.py` (`clean_company()` must still yield ZERO findings).
- `test_connection_hardening.py` already enforces the safe_rollback/run_write patterns at call sites: new batch loops must be registered there.
- CLI-as-CI-invokes test (CLAUDE.md lesson 2026-10-13: a script passed tests that sourced helpers by absolute path and crashed in CI): invoke `scrooner-structure` via its entry point from a different cwd.
Mutation-check plan (each must make at least one test fail; record the mutation and the failing test in the PR):
1. flip the sign of a cal weight; 2. swap parent/child in the tree sum; 3. loosen tolerance to 1.0; 4. remove the tautology guard; 5. drop the `segments` empty filter in the num stream (a dimensioned value then enters the sum); 6. drop `is_custom` equality (`version == adsh`) so custom tags are treated as standard; 7. remove the "children missing -> skip" branch (incomplete trees become failures); 8. delete-scope without `status='observed'` (human decisions deleted); 9. ingest without the `already logged` filter (duplicate work). Run via a small `scripts/mutation_check_structure.sh` that applies each patch with `sed` on a temp copy and runs only `pytest -k structure -x`, never on the working tree.

---------------------------------------------------------------------------
## 5. Sequenced backlog (sizes in engineer-days; one data engineer unless noted)

| # | Item | Size | Owner | Depends on | Exit / evidence |
|---|---|---|---|---|---|
| 0 | Read `readme.htm` from an FSN zip (cal.tsv columns, group semantics, FSN vs FSDS adsh keys); freeze parsers' column lists | S, 0.5 d | Data Engineer | none | column list quoted with accession of one sample |
| 1 | Identity suite on STORED data only: NI stored vs filing-style checks that need no new tables (extend `ties.py` cash roll to restricted cash; add `ProfitLoss`/NCI relation if tags exist in `CompanyData`); dry-run on top-1000 shard | S-M, 2 d | Data Engineer | certify P1 (0097 applied for `--apply`, dry-run needs none) | dry-run counts per identity, Verifier samples 20 flags |
| 2 | `collector/bulk_datasets.py` + `SECClient.get_range` + range-zip reader + tests | M, 2-3 d | Data Engineer | owner of `common/sec_client.py` told; item 0 | fetch cal.tsv of 2025q3 with no disk write; sha256 logged |
| 3 | Migrations 0098-0099 written, committed, reviewed dry-run, applied | S, 1 d | Data Engineer + Release Manager | ledger claim in doc 53; pooler <= 14 | `check_migrations.py` green; clean-DB replay |
| 4 | Parsers + loader + `scrooner-structure ingest` for ONE quarter (2025q4), top-1000, dry-run then apply; size pilot (rows, bytes, index growth, seconds, peak memory) | M, 3 d | Data Engineer | 2, 3 | pilot report with measured numbers replacing this doc's ASSUMED ones; go/no-go on storage |
| 5 | Backfill 2023q1-2026q3 top-1000 (single process, ListAgents first) + monthly workflow `pipeline-structure.yml` | S-M, 2 d | Data Engineer | 4 | ingest log complete; workflow dry-run green; join of `adsh` to `core.filing` coverage reported (accessions missing from `core.filing` listed, not dropped silently) |
| 6 | Filing-substrate identities (`structure/identities.py`, num stream) + `structure_checks.py` + loader hook + 2x2 report | M, 3-4 d | Data Engineer | 4 | 2x2 table for 2025q4; failures classed filer-error vs ours by Verifier on 30 samples |
| 7 | Recipe builder (`structure/recipe.py`) for the 6 composite concepts (D&A, capex, interest, operating income, total debt, +1 chosen by Standardization Lead); explains-rate vs the PoC "values differ" counts (D&A 61, capex 29, interest 7, operating income 6) | M, 3 d | Data Engineer + Tag Mapper | 4, 5 | share of "values differ" cases explained by cal perimeter (the stop-rule number) |
| 8 | Perimeter vocabulary and definitions (`concept_perimeter`) | M, 3 d (human) | Standardization Lead + named accountant | 7 | adopted codes recorded; none adopted by the engineer |
| 9 | Path-B resolver (`resolver.py`) + `structure_concept_candidate`; anchor rollup via `cal`; first for revenue (4 utilities/custom misses from the PoC) | M-L, 4-5 d | Tag Mapper + Data Engineer | 4, 7 | agree/disagree/b-only counts; the 3 PoC revenue disagreements re-run and each rejected by the cal gate |
| 10 | Migration 0100 + I12/I13 invariants + nightly SELECT-only certify step | S-M, 2 d | Data Engineer | 6, 7, 9; 0097 applied | invariant tests + mutation checks green |
| 11 | Verifier sample: 10 companies x 3 concepts from original filings (R*.htm / the filing, not our tables) for recipes and B-only fills | M, 3 d | Data Verifier | 7, 9 | per-decision verdicts |
| 12 | Adoption path into displayed values (`mapper/composition_resolve.py`, `_resolved` concepts, delete-scope excluding them) | L, 5-8 d | Data Engineer + Standardization Lead | 8, 11, founder go | full-population coexistence check (not a 5-row sample); gated release |
| 13 | Widen from top-1000 to full population; prune to latest 8 filings; storage re-measure | S-M, 2 d | Data Engineer | 5, size pilot | DB size delta vs budget |

Totals: items 0-6 about 13-16 engineer-days to a measured identity layer and a size pilot (about 3 calendar weeks with reviews); 7-11 add about 15 days (two engineers, one human accountant review); 12-13 about 7-10 days gated on adoption decisions. Calendar estimate is ASSUMED; the 38-note "about 2 weeks" for a first resolver is optimistic if the accountant review of perimeters is on the path. Critical path: 0 -> 2 -> 3 -> 4 -> 7 -> 8 -> 11 -> 12.

Lane/coordination: `common/sec_client.py`, `certification/*` (Data Engineer, uncommitted modifications exist in the tree: coordinate before touching), `normalizer/derived.py` is Period Engineer's (not touched). Shared-module rules from doc 53 apply: tell the owner, named `git add`, push in the same turn.

---------------------------------------------------------------------------
## 6. What could go wrong and kill criteria

Risks
1. Join gap: FSDS/FSN `adsh` not found in `core.filing` (new filings, 10-K405, amendments, filers outside our universe). Mitigation: log every miss with count; never create `core.filing` rows from structure (that is Normalizer's). Kill signal if more than 5% of top-1000 10-K/10-Q accessions in range miss.
2. Cal trees are incomplete or filer-specific: partial calc linkbases (children not listed) make trees look wrong; `children_missing` must not become a finding. Also Q4 and YTD contexts: the `qtrs` selection must follow the filing's own context, not our `core.period` labels (YTD periods can have null `fiscal_period`).
3. Label matching noise (PoC false positives: NJR "accrued capex", Gladstone "unrealized depreciation"). Path B never publishes; label class is only a candidate generator gated by cal rollup.
4. Perimeter equality is a semantic call: forcing equality across filers (D&A with/without intangibles amortisation) would introduce wrong values. We expose the perimeter, we do not harmonise silently; adoption needs the Standardization Lead and an accountant.
5. Vacuous identities: NI IS vs CF passes trivially when both are the same fact; reporting "324/324 passes" as proof would overclaim (see 3.2 item 3). The stored-vs-filing comparison is the discriminating one.
6. Shared-source circularity: parsing the same XBRL for both paths hides shared errors (infra-map Verifier note). Verifier must read original statements, not our tables, for the sample.
7. Storage/DB load: database is small (shared buffers 256 MB per the workflow comment) and restarted twice in 2026-10-18/19 under overlapping jobs; the top-1000-first scope and `heavy-db-jobs` group are the guard. Pooler ceiling about 15 connections shared by all sessions.
8. SEC changes: member names/columns (`.txt` in FSDS vs `.tsv` in FSN), URL path (FSN `financial-statement-notes-data-sets`, the earlier-assumed `-and-notes` 404s), Range support, publication cadence. The parsers read the header row and fail closed on an unknown column set; the `readme.htm` member is archived by hash in the fetch log.
9. History gate: do not widen before 2015-01-01 for display-facing use (doc 38); the first backfill starts at 2023q1 and each extension re-reads the gate.
10. Organisational: several sessions share the tree and the pooler; `certification/` files are modified-uncommitted today; migration numbers collide if unclaimed.
11. Not cost-free to humans: every disagreement is a review item; the volume of `review` findings can swamp the Verifier. Cap new finding types per run and start in dry-run.

Kill / stop criteria (decided up front)
- K1 (from doc 39): after item 7, if cal perimeter explains fewer than half of the PoC "values differ" cases (D&A 61, capex 29) on the top-1000, stop the composition layer and report; keep the identity suite.
- K2: if the size pilot (item 4) shows top-1000 `filing_statement_line` plus `filing_calc_edge` above 1 GB for 15 quarters, or any pilot step pushes the pooler past 14 connections or triggers a statement timeout that a retry does not clear, stop and re-scope to latest-8-filings only.
- K3: if on a Verifier sample of 30 `wrong_value` identity flags, more than half are not real value problems in the filing or in our stored value, demote that identity to `review` and fix its tolerance/scoping before it can block certification (this is a check-quality gate, not an accepted error rate for displayed data).
- K4: if path B disagreements on revenue are not removed by the cal gate in the 3 known PoC cases ("Other revenues", "Sales income"), do not build the resolver beyond candidate listing.
- K5: if more than 5% of top-1000 accessions cannot be joined (risk 1), or Range requests are refused by SEC for repeated runs, stop and ask the founder about the bulk-download fallback (needs a disk or a runner-side job).
- K6: any proposal to auto-publish a B-only value, flip a sign, or close an accounting definition without the Standardization Lead and an accountant is out of scope and stops the work.

---------------------------------------------------------------------------
## What I did not verify
Live DB (no query run); `cal.tsv` columns; actual FSN monthly vs quarterly overlap; SEC Range behaviour over a long run; real row counts per quarter for the top-1000 (all row and byte estimates above except the measured sizes at the top are ASSUMED); GitHub Actions plan minutes; whether `canonical_fact` already carries tags for the CF net income line (not implemented per `certification/ties.py`); current state of uncommitted `certification/*.py` edits.

## Tag/mind notes not written (brief says write only this file)
Proposed `data-team/tags/feedback-inbox.md` line: FSN `cal.tsv` is about 9 MB compressed per quarter and can be Range-read from the 460-630 MB zip; custom tags are 11.3% of FSDS 2025q4 pre lines (`version` = adsh). Proposed `mind` entry: FSN zips are served at `.../financial-statement-notes-data-sets/{YYYYqN|YYYY_MM}_notes.zip` and support HTTP Range (checked 2026-10-21).
