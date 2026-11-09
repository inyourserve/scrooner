# Certification: what blocks the first certified company (2026-11-09)

Certification lead (session 01GLmSE1SAPUBpeYGyM6GQmA), for Dhairya (session 01GLmSDyzegqZw4JqC91z7XH).

**Basis:** code and docs at main `787cc667`, read-only. No production query was run: this cloud container has no `DATABASE_URL`. Every live number below is cited from a file. Where a live check is needed it is listed in section 4.

## 1. Blockers, most fundamental first

| # | Blocker | Evidence | Kind |
|---|---|---|---|
| **1** | **No code can write `certified`.** The ladder is uncertified → checks_clean → reconciled → verified → certified. `scrooner-certify` only moves a company between `uncertified` and `checks_clean`. Nothing writes `reconciled`, `verified` or `certified`, or the `*_at` columns. | `certification/runner.py:165-176` (UPSERT_CERTIFICATION); 0097 header ("later states are written by the reconciliation job and the Verifier"); repo-wide search finds no other writer | code |
| **2** | **The `reconciled` rung is circular in the FSN era.** Doc 34 rung 3 is "R1: reconcile headline values to an independent parse of SEC FSDS num.txt". The values ARE now built from that same SEC dataset (FSN), and 0114 says comparing two feeds of the same XBRL instance "proves nothing". R1 (P2) was never built. The FSN-era equivalent is `analytics.cell_proof` PROVEN (position, identity ties and the printed-page sample). | doc 34 §R and P2 "to build"; `0114_cell_proof.sql` header; no R1 job in `pipeline/src` | **ruling** |
| **3** | **I11 cannot see FSN blanks or templates.** I11 classifies a missing cell only from `analytics.period_gap` and `metric_value.is_null_reason`. It never reads `analytics.cell_blank_reason` (where the FSN write records its reasoned blanks) or `analytics.company_data_point_template` (0120). So every FSN-reasoned blank and every out-of-template cell is `unclassified`, and an unclassified I11 cell blocks `checks_clean` by rule. | `certification/history.py:19-29,120`; `runner.py:180-185` (`is_blocking`); no `cell_blank_reason` or template reference under `certification/` | code |
| **4** | **4 of the 11 headline cells are held out of the write.** Doc 34 rung 4 has the Verifier check revenue, OI, NI, diluted EPS, **total assets, total equity**, CFO, **capex**, shares, **total debt** and market cap. The write's `data_points` excludes balance sheet, debt, capex and D&A "until the release approver clears them", so those 4 headline cells still serve old-mapping values. The old baseline had 977 of 986 companies with ≥1 wrong_value and 0 checks_clean. | `.github/workflows/pipeline-fsn-write.yml` header and `data_points` default; TASK-BOARD "Certify baseline" (40,774 wrong_value, 2026-10-26) | release |
| **5** | **The sector template is not seeded.** 0120 was applied 2026-11-01 with 0 rows. The seed built from Ritwik's approval (`work/data-engineer/sector-templates-seed`, CI green 41317933298) is not on main and has not been applied. Without it, "every template cell valued or reasoned" has no denominator, and I10 still covers banks only. | `data-team/42-release-applies-2026-11-01/apply_0120-log.txt`; main has no `SECTOR-TEMPLATES-SEED-*`; `certification/sector.py:1-4` | approval + founder |
| **6** | **MSFT and HD already have blank defects.** In the post-load Verifier draw, 62/62 shown values were right but **11 of 18 drawn blanks should have a value**: 5 HD D&A holds, 3 MSFT restatement blanks, and 3 MSFT 2026-09-30 blanks (10-Q filed 10-28, newer than the FSN set). There is also a false `no_filed_column_for_period` on MSFT Q1 FY2017. Doc 34 criterion 1 and doc 02 ("a blank is never a resting state") block certification on these. | `data-team/strategy/team/VERIFY-POSTLOAD-MSFT-HD-2026-11-01.md` | data |
| **7** | **Verifier verdicts are markdown only.** The `verified` rung needs, per company, a recorded headline-cell check with accession and locator. No table holds Verifier verdicts, so a promoter cannot read them. | no Verifier table in `pipeline/db/migrations/` | code + migration |
| **8** | **Metrics are not recomputed after the write.** The nightly refresh failed on 3d093b3 (normalize:facts, then the reprocess budget), so every map stage after calculate was skipped. Market cap, P/E and growth will not reflect the new values, and I7 (currency) will fire. Design §6 needs "metric recompute, then a coverage refresh" after each company. | NOW.md "Open issue" (run 42507618224); design §6 | ops |
| 9 | **I6 skips FSN-only cells.** I6 `continue`s when a cell has no `source_fact_ids`. FSN cells sourced only from `fsn.value` (derived Q4, note-sourced) are therefore unchecked by I6, so their proof must come from cell_proof (folds into blocker 2). | `certification/source_integrity.py:440-442` | code (minor) |
| 10 | **Cohort mismatch.** certify shards come from `shards.csv` (986 companies); the write uses v1.1 (1,000). 20 v1.1 companies (ranks 981–1000: BRK-A, SO, SRE, ETR, …) have no certify shard. The top 100 is unaffected (S001–S010). | `pipeline-certify.yml`; set comparison of the two files | code (minor) |

## 2. Ranked plan: MSFT and HD first, then the top 100

| Step | What | Who | Needs |
|---|---|---|---|
| 1 | When run 42649721096 finishes: run cell_proof on the top 100 (`pipeline-cells-proof.yml`), then a certify **dry run** on S001–S010. Either run gives the first real post-FSN numbers. Restore any company with a served DISAGREE (design §5 criterion 6). | engineering (8a) or the CI/CD session; certification lead analyses | dispatch outside the nightly window; restore needs the founder's words |
| 2 | **Ruling on the FSN-era ladder:** `checks_clean` = I1–I11 clean (template- and reason-aware); **`reconciled` = every headline cell PROVEN in cell_proof, none DISAGREE** (replaces R1); `verified` = a recorded Verifier check of the headline cells (latest FY + latest Q) with accession and locator; `certified` = all of these plus every template cell valued or reasoned. | Dhairya proposes, founder rules; doc 02 entry | ruling |
| 3 | **Code (certification lead), on a branch with tests, mutation-checked, CI green, dry run by default:** (a) I11 reads `cell_blank_reason` and the template, so an out-of-template cell is not expected and an FSN-reasoned blank is classified; (b) `scrooner-certify promote` writes reconciled/verified/certified from cell_proof, a Verifier record table and template coverage; (c) the certify cohort option for v1.1. | certification lead | (b) needs a migration (Verifier record table, next free 0122) and the step-2 ruling; applying it needs the founder |
| 4 | Ritwik checks the seed branch → founder's words → `seed-sector-templates --apply`. | Ritwik, founder | approval |
| 5 | Release the held families into the write, BS first: PR #6 (Verifier PASS 2026-11-08) after its cohort dry run; then debt, capex, D&A. Without them no company reaches `verified`. | lanes plus the release approver; founder merges | release |
| 6 | Fix the MSFT and HD blank defects (blocker 6): HD D&A single-line hold, MSFT restatement witness, the newer-than-FSN filing via B9/SEC API, the MSFT Q1 FY2017 false reason. Verifier re-draws MSFT and HD. | income-statement and capex/D&A lanes; Verifier | — |
| 7 | Fix the nightly refresh and recompute metrics for written companies (blocker 8). | CI/CD session (the founder must hand it over) | — |
| 8 | Verifier headline draw per company: MSFT and HD (11 cells × latest FY + latest Q each) recorded in the new table, then promote. Then the top 100: a stratified draw of 200 cells over 100 companies (design §5) plus the headline draw per company. | Verifier; certification lead runs promote (dry run) | founder's words for the promote apply |

**Critical path to MSFT and HD:** 1 → 2 → 3 → 4 → 5 (at least BS and debt) → 6 → 8.

**Parallel now:** 3a, 4, 6 and 7 do not depend on each other.

## 3. Starting now (this session)
Step 3a: template- and reason-aware I11, on `work/certification-lead/i11-template-reasons`, with tests and CI. It does not depend on the ruling. Step 3b starts when the ruling lands.

## 4. Live checks for whoever has production read (statement_timeout ≤ 15s)
- `select state, count(*) from analytics.company_certification group by 1` (expect 0 rows)
- `select count(*) from analytics.company_data_point_template` (expect 0)
- `select count(*) from analytics.cell_proof where company_id in (<MSFT>, <HD>) group by status` (proof state after the write)
- `select count(*) from analytics.slot_protected_cell where created_at > '2026-11-09 15:56'` (did run 42649721096 write)

## 5. Update: step 3a done (blocker 3)
Branch `work/certification-lead/i11-template-reasons`, commit `3792a3e0`; CI run 42653854475 green on every job (pipeline 2,387 passed, 0 failed). **Not merged: it needs a founder merge.**

What changed in certify I11:
- **Template:** a data point OUT of the company's current template (0120) is no longer an expected cell.
- **Writer reasons:** a missing cell with a `cell_blank_reason` row (newest per key, latest basis, grains FY/Q/I) is classified as `blank_reason:<code>`. That reason is checked before `period_gap`.
- **Still blocking:** a `defect` row whose class is unclassified, and a blank with no reason at all.
- **No rows in either table:** the behaviour is unchanged.

Tests: 9 (1 on real Postgres 16); 12/12 mutations caught; the 236 existing certification tests are unchanged and pass.

**Next:** `certify promote` plus a Verifier record table, once the ladder ruling (blocker 2) lands. Until then this lane stays off production. It analyses the cell_proof and certify dry-run outputs once someone dispatches them after run 42649721096.
