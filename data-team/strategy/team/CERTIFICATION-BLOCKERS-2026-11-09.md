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

## 6. Status of every piece (2026-11-09, late)
| Step | Branch | SHA | CI | What it is |
|---|---|---|---|---|
| 3a | `work/certification-lead/i11-template-reasons` | `3792a3e0` | 42653854475 green | I11 reads the sector template (0120) and `cell_blank_reason` |
| 3b | `work/certification-lead/promote` | `3bc6c42a` | 42656798008 green (all jobs) | `scrooner-certify-promote` plus migration **0122 `analytics.verifier_check`** (claimed in doc 53, next free 0123; NOT applied) |
| 3c | `work/certification-lead/v11-cohort` | `1bbf083a` | 42657752304 green | `scrooner-certify --cohort-ranks 1-100` over cohort v1.1; workflow input `cohort_ranks` |

None is merged; each needs a founder merge. 0122 needs the founder's typed words to apply. The three branches are independent of each other: 3b carries its own template read, so it does not need 3a.

### 3b: the exact tests (founder-approved wording; any change from the Verifier review gets applied here)
- **reconciled.** For each headline concept in the company's template, at least one served `canonical_fact` cell since 2015. Every served cell has its newest `cell_proof` row (same data point, period start and end, basis latest) PROVEN, with `shown_value` equal to the value served now; a proof of an older value is stale. No headline `cell_proof` row is DISAGREE.
  - Headline concepts: revenue_sanity_resolved, operating_income_resolved, net_income_resolved, diluted_eps_resolved, cfo_resolved, capex_resolved, total_assets_resolved, stockholders_equity_resolved, shares_outstanding_resolved, total_debt_resolved.
  - market_cap has no filing line, so it is checked by the Verifier only.
- **verified.** For each headline concept, its latest PROVEN cell per grain (flows FY and Q; instants I) has a `right` `verifier_check` row with the same grain and period end and the same shown value. market_cap needs a `right` row checked within 31 days (ASSUMED; confirm). There must be no open `wrong` or `blank_wrong` row.
- **certified.** The company has a current template. Every in-template data point has `company_data_point_coverage.has_value`, or its newest blank reason is classified.
- **The command:** promote decides the highest rung that holds and writes it, demoting as well as promoting. It never leaves `uncertified`, never creates a row, and writes only `company_certification`. Run it after `scrooner-certify`. Tests: 15 (4 on real Postgres 16); 16/16 mutations caught.

### New blocker 11: the proof engine is not on main
`scrooner-proof` (the only `cell_proof` writer) exists only on `work/engineering/cell-proof`, last commit 2026-11-01; `pipeline-cells-proof.yml` checks out that branch. **No `reconciled` is possible until a proof run writes `cell_proof` for the written companies.** A write needs the founder's words. Merging the engine or freezing a ref is engineering's call.

### For the Verifier review ("can a wrong shown value be certified?")
**Yes, for a non-headline cell.**
- The `cell_proof` and Verifier rungs cover the 11 headline concepts only.
- Every other shown cell (SG&A, D&A, interest, tax, metrics and so on) is covered only by the I1–I11 invariant suite. A wrong value that passes every invariant can still be certified.
- **The fix, if the review asks for it:** add the other served data points to the reconciled list (`HEADLINE_PROVED` in `certification/promote.py`; a one-line change plus tests), so every served cell must be PROVEN. Cost: every family needs `cell_proof` coverage first.
- **A headline cell cannot be certified wrong** unless the proof position and the Verifier draw are both wrong about it.

## 7. One source, the hybrid (founder direction 2026-11-09, relayed by Dhairya)
Applied to 3a and 3b. Hybrid cell = a `canonical_fact` row whose `rule_run_id` points to an `fsn.*` rule run (the FSN write loads under `fsn.select@1`).

| Step | Branch | SHA | CI | Change |
|---|---|---|---|---|
| 3a | `work/certification-lead/i11-template-reasons` | `d0385e0e` | 42658994548 green | For a concept the hybrid writes for the company (an fsn-written cell, or a writer blank reason), a missing cell is explained **only** by a `cell_blank_reason`; old-mapper `period_gap` and fact inference no longer count. Other concepts are unchanged, not extended. 10 tests; mutation check 3/3 caught. |
| 3b | `work/certification-lead/promote` | `4c5561fc` | 42659375835 green (the frontend job flaked on attempt 1 and passed on the re-run; this commit touches `pipeline/` only) | **reconciled** also requires every served headline cell to be hybrid-written; an old-mapper cell blocks it (`reconciled:not_hybrid`). **certified** template coverage reads only hybrid outputs: an fsn-written cell by base name, a metric value, or a classified writer reason. `company_data_point_coverage` is no longer read. 16 tests (5 on real Postgres); mutation check 23/23 caught. |
| 3c | `work/certification-lead/v11-cohort` | `1bbf083a` | 42657752304 green | unchanged |

**Consequence:** no company can pass `reconciled` while any of its headline cells is still served from the old mapper. That includes the held families: total assets, equity, capex and debt (blocker 4).

## 8. Queue item (a): income-statement absent-line reasons
**Branch:** `work/certification-lead/is-absent-lines`, commit `87cc6147`, CI run 42661893040 green on every job. It is built on PR #4 (`work/cashflow/fsn-gaps-rebased`), **which must land first**.

**What changed:**
- `select.absent_line_cell` takes a statement argument; the cash-flow default is unchanged.
- The pilot report classifies each filing's primary income statement for revenue, cost of revenue, interest expense, net income and basic EPS. The primary statement is the lowest-numbered report that prints the net-income anchor. Classification uses tag and label only.

**What it claims, per filing:**

| What the filing prints | Result |
|---|---|
| No line of the concept's family | not_presented, `line_not_presented_in_filing` |
| Only a "costs and expenses" total (for cost of revenue) | not_presented, `line_presented_combined_with_others` |
| Net interest only | defect, `perimeter_line_unresolved` |
| Per-unit EPS only (a partnership) | defect, `perimeter_line_unresolved` |
| Any line that may be the concept, or no anchored statement | nothing claimed |

**Safety:** it is applied only to keys that `select` left without a row, so it never blanks a served value (Ritwik C2). Net income can never be falsely claimed absent: its line is the statement's anchor, so without it the filing has no face column.

**Tests:** 33, the PR #4 suite passes unchanged, and the mutation check caught 11/11.

**Not done here:**
1. The measured effect on the 1,271 cohort pairs. That needs a cohort dry run against the FSN store, which this container cannot reach.
2. A Verifier draw on the new reasons.

## 9. Queue item (b): IS no_mapped_line (interest expense at banks and insurers printing net interest only)
- **With (a):** these keys become **classified defects** (`perimeter_line_unresolved`), not reasonless blanks, so they no longer block I11's `checks_clean`.
- **The rest needs data:** a company-level OUT row with evidence (`data-team/47-fsn-store/template_company_outs*.csv`) must cite each company's accessions from the FSN store. This container has no database or bucket access, so I have not fabricated rows.
- **Proposal:** whoever has production read runs a query over `fsn.line` / `fsn.tag` for the template's bank and insurer companies: every 10-K/10-Q primary IS prints `InterestIncomeExpenseNet` (or a "net interest" label) and no `InterestExpense*` line. The candidate rows, with their accessions, then go to Ritwik as `template_company_outs` (`APPROVE_OUT`). The classifier in `pilot.is_line_class` is the rule to reuse.

## 10. Verifier FIX 2026-11-09 (VERIFY-TEMPLATES-AND-LADDER-2026-11-09, branch verify/templates-and-ladder-2026-11-09 @ 01d203d)

### (1) Ladder: the six holes, closed
Branch `work/certification-lead/promote`, commit `d632042d`, CI run 42664611855 green on every job. Each hole has its own test (27 tests, 13 on real Postgres 16), and every mutation of a fix fails a test.

| Hole | Fix in `certification/promote.py` |
|---|---|
| 1. Scope: only the headline cells were checked | `verified` also needs the company's newest **all_cells** Verifier draw: at least 20 cells (ASSUMED number, for the approver to set), all `right` or `blank_right`. |
| 2. A DISAGREE outside the headline did not block | A DISAGREE in the newest proof row of **any** data point blocks `reconciled`. |
| 3. PROVEN did not prove the right concept | A proof counts only with a **face read**: face value (× scale) equal to the shown value, a recorded label, and a label that is not a segment line. Rejecting "net" lines for gross concepts stays with the proof engine; its label rules are its own. |
| 4. PROVEN did not prove the latest print | A proof counts only if **no later accepted filing** of the company prints the shown tag at that column. FSN ddate is month-end rounded and qtrs is FY 4 / Q 1 / I 0 (mind `fsn-data-set-facts-…`). |
| 5. Derived and note cells had no face to check | A derived cell counts only with `checks.derived`, `checks.inputs_proven` and a `checks.same_basis_witness` on its proof row. A note-sourced cell is read on its note page like a face. |
| 6. A value change after verification kept the company verified | The all_cells draw records the company's **shown-cell hash** (canonical values and metric values; `scrooner-certify-promote --print-hash`). Any later change drops the company below `verified` until the Verifier draws again. |
| Blanks: a false reason could be certified | `certified` also needs the newest **blanks** draw: at least min(10, reasoned cells) rows, all `blank_right`. |
| The record must be the Verifier's | Migration 0122 (NOT applied) gains `draw_kind`, `cells_hash` and `face_label` (required for value verdicts), plus a **writer guard trigger**: rows are written only in a session that sets `scrooner.writer = 'verifier'`. |

**Stated scope (as the Verifier asked):**
- `certified` proves the headline cells by proof plus a filing check.
- It covers every other shown cell by the invariant suite plus a seeded random draw. It does not prove each non-headline cell individually.
- The proof engine (`work/engineering/cell-proof`) must populate `face_value`, `face_label`, `face_scale` and the derived-cell `checks` keys for proofs to count. Until it does, no cell passes `reconciled`.

### (2) Sector-template seed
Branch `work/certification-lead/template-seed-fixes`, commit `f84a3251`, CI run 42663197962: every blocking job green. The advisory npm audit fails on main as well.
- **Fixed:** rows 1–5 and 8.
- **Open, decisions needed:** row 6 (bank-like brokers) and row 7 (the COND company overlay). Details are in `TEMPLATES-BUILD-2026-11-01.md` §9 on that branch.
