# Company-wise FSN statement store: design (Ritwik, approved by the founder 2026-11-01)

Status: APPROVED (founder to Dhairya, 2026-11-01). Replaces the family lanes' separate whole-cohort FSN passes and their quarter derivation. Numbers are labeled MEASURED, DATA-INFERRED or ASSUMED.

## 0. Facts checked
- The `fsn-notes` bucket holds cohort-filtered FSN extracts for 2014q1..2026m09 (sub, pre, num, cal, tag, dim, ren, txt, notes.zip). Manifest: `pipeline/scripts/slot_records/results/fsn_manifest_all.jsonl` (origin/work/income-statement/full-population). Local 2026m10 is empty.
- This is FSN, not FSDS: num carries dimh/durp/datp and the note facts. The mind entry "FSDS num has no note facts" is right for FSDS only.
- Migrations: company_slot_record is 0101 (not applied; 0110 is in SKIPPED.txt). 0117 is written but not applied. The next free number is **0118**. The 0113 guard `trg_slot_protected_cell_guard` is live on canonical_fact. cell_proof has 0 rows.
- About 40 modules read analytics.canonical_fact directly, so it stays the serving table. Doc 02: no switch view, no fallback.
- Teleflex reproduced from FSN num (DATA-INFERRED; the R page was not opened):
  - FY2025 10-K 0000096943-26-000019: revenue 1,992.713M.
  - Q3 10-Q 0000096943-25-000138: 9M 2,394.579M.
  - FY minus 9M = −401.9M.
  - The same 10-K reprints FY2024 as 1,699.546M; it was printed earlier as 3,047.324M. That is the witness of a recast.
  - The same 10-K prints Q4 2025 = 568.984M directly.
- The FSN cal `negative` column is the arc weight (+1/−1).

## 1. Data model (migration 0118, schema `fsn`)
Measured volumes, cohort 2014q1..2026m09:
- 44,962 10-K/10-Q filings (incl. amendments)
- num: 67.02M rows; non-dimensional 21.10M
- num on statement lines: 14.36M non-dimensional, 14.93M dimensional
- pre on statements: 7.03M
- distinct statement lines: 6.31M
- cal: 6.57M

Tables:
- `fsn.filing`: one row per accession. Columns: company_id, cik, form, period, fy, fp, fye, filed, accepted (the vintage order), amendment, prevrpt, aciks, fsn_set, src_sha256. Index (company_id, accepted).
- `fsn.report`: from ren; menucat 'S' = statement.
- `fsn.tag`: (tag, version), custom, datatype, iord, crdr, tlabel.
- `fsn.dim`: dimh, segments, dimn; id 0 = none.
- `fsn.line`: grain = pre row. PK (filing_id, report, line); stmt, inpth, tag_id, prole, plabel, negating.
- `fsn.value`: grain = num row; a period has many vintages = many rows. Unique (filing_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg). Partial series index (company_id, tag_id, ddate, qtrs) include (value, filing_id) where dim_id = 0.
- `fsn.calc_arc`: (filing_id, grp, arc), parent_tag_id, child_tag_id, weight.
- `fsn.company_load`: company_id PK, input_sha256, loader_commit, row_counts, run_id, loaded_at.
- `fsn.concept_rule`: canonical_concept_id, stmt, match_kind in (std_tag, calc_position, combined), tag, priority, rule_id, source_commit.
- `fsn.line_map`: PK (filing_id, report, line); canonical_concept_id, status in (mapped, combined, unmapped, excluded), rule_id, era, evidence.
- `fsn.filing_check`: PK (filing_id, stmt, ddate, qtrs, check_id); ok, lhs, rhs, tol, detail.
- `analytics.canonical_fact` gets `source_value_ids bigint[]` (fsn.value ids).

Notes:
- Vintage: no row is ever marked "current". "Latest" and "as filed" are queries; nothing is overwritten.
- Stored: every non-dimensional value of every 10-K/10-Q (notes included), every dimensional value on a statement line, statement pre rows (8.43M incl. CP/UN) and all cal arcs. Note-level pre and dimensional note values stay in the bucket.
- Size: about 36–40M value rows, about 10.5 GB in total (ASSUMED at ~200 B/row). The DB goes from 47 GB to about 58 GB. Lean option (non-dimensional only): about 6.5 GB.

## 2. Load (company-atomic)
1. **Shard** (local, read-only): stream each period's bucket files once into `companies/<cik>/*.tsv.zst`, deleting each download after use. Keep a 4 GB free-disk floor; the dev Mac is near full, so run under `caffeinate -i -s` or in Actions. Write `input_sha256` per company.
2. **Load** (one transaction per company): `set local statement_timeout='5min'`; COPY into temp tables; upsert tag/dim; delete fsn.* for the company; insert; upsert company_load; commit.
   - Idempotency key: (company_id, input_sha256, loader_commit); a match means skip.
   - Rerunning the same command resumes. A half-written company is impossible.
3. **Budget**: at most 4 connections, outside the 18:00–21:30 UTC nightly window.
4. **Runtime**: about 57k rows per company; 15–30 min for 1,000 (ASSUMED; the pilot measures it).

## 3. Mapping (line → canonical concept)
Done per filing × statement, in O(lines + arcs). Structures:
- lines sorted by `line` number (pre file order is NOT statement order)
- a tag→line dict
- a calc DAG restricted to arcs whose parent and child are both lines of that statement
- a value matrix line × column; a column is on the face only if that statement's anchor total has a value for it in the same filing

Rule order:
1. **Standard tag**: hash lookup in `fsn.concept_rule`. Seed it from the Verifier-passed lane code (is_detect, bs_totals_detect, era_detect/assemble_fsn, cf_face_rows, cf_da_capex_variants, eps_fsn_scan) and the tag cards. Do not retype rules.
2. **Custom tag**: map by calc position in the slot the lane detectors define. A label may only demote a line, never promote it.
3. **Combined line** (e.g. AccountsPayableAndAccruedLiabilitiesCurrent, or a custom parent spanning two concepts): status `combined`, blank `line_presented_combined_with_others`. Never mapped as a single concept.
4. **Era boundaries**: from `era_detect.py`, unchanged.

**Regression gate**: with identical inputs, the ported detectors reproduce the lanes' last emitted cells exactly:
- is_core 281,761 rows, sha 77f5846a
- capex_da_cash_debt 155,257 rows, sha 6f53c945
- CFO run 7: 37,121 publishable cells

## 4. Value selection and derivation (`fsn_select.py`)
**Candidates** for (company, concept, grain, period) are prints where:
- the line maps to the concept,
- the column is on the face,
- all of that column's filing_checks pass.

**Winner** = latest `accepted`.
- Two different values in one filing → defect.
- If the latest print fails a check → blank `latest_copy_fails_identity`. Never fall back to an older vintage.
- Value, accession and source_value_ids come from the same row.

**Quarter flows with no printed 3-month face column**, in order:
- (a) a 3-month value printed in the same accession as the winning FY/YTD (quarterly-data note); marked note-sourced, with its own Verifier stratum.
- (b) YTD_n − YTD_(n−1), same fiscal start, only if SAME_BASIS(A, B, L).

**SAME_BASIS**, where L = the mapped concept:
- A filing F is a **break** for L if any period F prints for L differs, beyond rounding, from the latest earlier print of that period.
- SAME_BASIS(A, B, L), with accepted(A) ≤ accepted(B), holds iff:
  - A = B, or
  - no break for L lies in (accepted(A), accepted(B)], and B re-prints at least one earlier period of L (a witness).
- Otherwise the cell is a blank `mixed_vintage_inputs` / `no_basis_witness`.
- Fallback: the restated pair from the N+1 filings, only if that pair is itself SAME_BASIS.
- EPS is never derived. Q4 DPS = FY − 9M on one share basis only. Instants are never derived.
- Residual guard: revenue Q4 ≥ 0 and |Q4| ≤ |FY|.

**Teleflex**: the 10-K is a break (FY2024 1,699.5M vs 3,047.3M), so Q4 comes from (a) = 568.984M, or the cell stays blank. −401.9M is impossible.

**Coverage cost** (DATA-INFERRED, tag level):
- 3,323 of 11,184 10-Ks change a prior-year IS value.
- Of 235,851 FY cells: Q4 printed in the same 10-K 31,599 (13.4%); the line rule allows 155,063, blocks 10,618 as a break and 38,571 as no witness.
- Concept-level mapping should cut the no-witness count; the pilot measures it.

## 5. Automatic proof (`fsn.filing_check`)
Tolerance = Σ 0.5·10^−dcml over the children, or `common.rounding_unit`. Checks:
- BS: Assets = L&E; L&E = liabilities + temporary equity + equity incl. NCI.
- Every calc parent with all children valued: parent = Σ weight·child.
- CF: CFO + CFI + CFF + FX (+ discontinued) = change in cash; opening + change = closing.
- IS: GP = revenue − COR; NI incl. NCI − NCI = NI attributable; the pretax/tax/NI arcs.
- Cross-statement, same accession: CF NI = IS NI; CF closing cash = BS cash (+ restricted).

**A company is done when all of these hold:**
1. Store counts = shard counts, with input_sha256 recorded.
2. Every 10-K/10-Q since 2014 is stored or has a no-XBRL/B9 reason.
3. Every served cell comes from a passing column.
4. Zero reasonless blanks over the expected calendar keys.
5. Zero derived cells without SAME_BASIS evidence.
6. Zero served cell_proof DISAGREE.
7. The Verifier stratum is clean.

**Verifier draws:**
- Pilot: 40 cells each for MSFT and HD, stratified face / restated / derived Q / note Q4 / custom-mapped / blank.
- Cohort: 200 cells over 100 companies, seed 20261101.
- One wrong cell → fix the class, reload, redraw.

## 6. Serving
canonical_fact stays the serving table: no view, no fallback. For each company that is done, `cell_loader` does this in one transaction:
- deletes that company's owned concepts,
- inserts cells with source_value_ids (plus source_fact_ids where they resolve),
- writes cell_blank_reason and cell_proof.

Retire `materialize_fsn_fact`.

**Migration 0119**: `analytics.company_value_owner(company_id pk, owner, since)` and an extension of the 0113 guard. For an owned company, any canonical_fact write without `scrooner.writer='fsn_cells'` is skipped and logged. This stops nightly writes for owned companies.

After each company: metric recompute, then a coverage refresh.

## 7. Execution plan
1. Founder approves (done 2026-11-01). Ritwik records it in doc 02; the GitHub session claims 0118/0119 in doc 53.
2. scrooner-8a builds: migrations 0118/0119 (with a CI clean replay), `fsn_shard.py`, `fsn_store_load.py`, `fsn_select.py`, `fsn_checks.py`, and cell_loader `source_value_ids`. In parallel, the lanes port their input readers to read one company directory and export concept_rule seeds; each passes the regression gate.
3. **G1 (CI green)**, with fixtures:
   - Teleflex Q4 2025 = 568.984M or blank
   - the 105 mixed-vintage keys blocked or equal
   - KO 2015-04-03 date binding
   - AMZN leases
   - GE double context
4. **Founder authorization #1** (Ritwik's session): apply 0117, 0118, 0119.
5. **Founder authorization #2**: pilot MSFT and HD (store, map, select, check, write), then proof, recompute, page render and Verifier 40 + 40.
   - **G2**: 0 wrong, 0 reasonless, 0 unevidenced derived cells, and the load rate measured.
6. **Founder authorization #3**: all 1,000 companies, 4 shards × 1 connection, outside the nightly window. A company switches only when done.
   - **G3**: per-company done report, the 200-cell draw, and a certify dry run.

## 8. Kept, retired, risks
**Kept:**
- the bucket extracts and manifest; common.py
- the lane detector rules; the share_basis engine
- the expected-period calendar; the CELL-FORMAT v1.1 states and reasons
- cell_loader, cell_proof, the 0113 guard, filing_kit

**Retired:**
- each lane's whole-cohort FSN pass and its quarter derivation
- `unrestated_single_value`
- is_replay's production reads
- materialize_fsn_fact
- 0101 company_slot_record (leave it unapplied)
- the patch packages
- nightly canonical_fact writes for owned companies

**Risks:**
1. Filings after 2026m09 are not in FSN yet. Use B9/the SEC API with the same selection rules, or a blank `filing_newer_than_fsn_set`.
2. Ported rules drift from the Verifier-passed output → the regression gate.
3. Dev Mac disk and sleep → stream with a floor, `caffeinate`, or Actions; at most 4 connections.
4. The witness rule blanks more quarters (~19% at tag level) → concept-level witness, note Q4, the restated pair.
5. Company-page lineage expects source_fact_ids → keep resolving them; check apps/backend/company_page.py in the pilot.

Scratch measurement scripts (count.sh, count2.sh, breaks.py, breaks2.py) were in Dhairya's scratchpad and are not committed.
