# canonical_fact_v2 — the common cell format (v1, 2026-10-31) and the system design

Status: design, scrooner-8a (engineering). Founder direction via scrooner-0f 2026-10-31: v2 is THE serving store for the
1,000-company cohort going forward (hybrid source: SEC API for speed, FSN sets for structure, filing instance via B9 as gap
filler); the old companyfacts-mapping path is retired for the cohort once v2 is switched in; `analytics.canonical_fact`
stays untouched only as the temporary fallback. Rebuild per company, no before-images, no dual maintenance.

## 1. Design in eight lines
1. **Table** `analytics.canonical_fact_v2` (migration 0117, file in this branch, NOT applied): same key as canonical_fact
   `(company_id, canonical_concept_id, period_id)` plus `basis`; shape adds state, source (accession, tag, fact ids, fsn set/line),
   derivation, rule id/run, reason fields (the blank lives in the same row as a value would), evidence level, proof verdict.
2. **Cells, not facts**: one row per displayed cell (FY, Q, I grains; TTM later); a blank is a row with `value null` and a reason.
   Every state of the frozen eight-state contract is representable; nothing else is accepted.
3. **One loader** `scrooner-v2 load <family> <cells.jsonl.gz>`: validates every row against `common/cell_contract.py` + this spec,
   resolves/creates `core.period` by exact dates, then per company `delete where family = X and company_id = Y` + insert.
   Idempotent (manifest sha256 recorded; same file twice = same rows). No rollback machinery: rerun the family file.
4. **Ownership**: a data point belongs to exactly one family (table in §4); a key from two families is a load error, not a merge.
5. **Proof** runs over v2 (`scrooner-proof run --store v2`), writes `proof_verdict`/`proof_reason` back; FSN position + identity
   tie + components sum as today; a derived cell is proven through its inputs.
6. **Served view** `analytics.canonical_fact_served`: one setting row (`analytics.serving_switch`, 'v1'|'v2'); the site
   (`apps/backend/company_page.py`) and the screener read ONLY the view. v2 branch of the view: value shown when state in
   (value, derived) and proof_verdict in (PROVEN, UNCHECKED [founder standing rule: UNCHECKED never blanks a screen cell]);
   DISAGREE is served blank with reason `restated_copies_disagree`/`shown_differs_from_printed_line`; blank states carry their reason.
7. **Nightly for v2 (steady state)**: new filing → facts via the SEC API path (fast) → family rules recompute the touched
   company's cells → loader (same code path as the files) → proof → served. When the month's FSN set publishes, the structure
   check reruns the touched companies; filings the API never carried go through B9 (instance fallback) into the same loader.
8. **Cut-over**: lanes emit full-population files → load → proof → Verifier draws → switch to v2 (one UPDATE). Switch back = one UPDATE.
   After the switch the cohort's mapper/conflict-fill stages stop writing canonical_fact (retired, not deleted).

## 2. The cell file
- **Format**: JSON Lines, gzip (`*.jsonl.gz`), UTF-8, one cell per line, plus `manifest.json` next to it:
  `{"family","rule_id","git_commit","produced_at","rows","sha256","companies","data_points":[...],"period_floor":"2014-01-01"}`.
- **Location**: bucket `fsn-notes`, prefix `v2-cells/<family>/<YYYY-MM-DD>/cells.jsonl.gz` (+ manifest). Small files (<5 MB) may
  ALSO be committed under `data-team/46-canonical-fact-v2/cells/<family>/`. Give the loader the bucket URL or a local path.
- **Scope**: the 1,000 cohort companies, every FY/Q/I cell with `period_end >= 2014-01-01` (history floor; serving window 2015+).
- **One row per key** `(company_id, data_point_name, period_grain, period_start, period_end, basis)`. Duplicates = load error.

### 2.1 Row fields (flat JSON; `null` where not applicable)
| field | type | rule |
|---|---|---|
| `company_id` | int | core.company.id (required; `cik` may be sent too and is checked against it) |
| `cik` | "0000320193" | optional cross-check |
| `data_point_name` | text | the `analytics.canonical_concept.name` (`revenue_sanity_resolved`, `basic_eps_resolved`, `capex_resolved`, ...). Never a metric. |
| `period_grain` | `FY` `Q` `I` | FY = the filing's annual column; Q = 3-month (filed or derived); I = instant. `TTM`/`TP` rejected in v1. |
| `period_start`, `period_end` | ISO dates | EXACT dates of the company's period (core.period), not FSN month-end. `I`: start = end. If you only have `(fsn_end, qtrs)`, send them as `fsn_end`/`qtrs` instead and leave start/end null: the loader resolves to the company's period whose end is the nearest to `fsn_end` within 7 days and whose length matches `qtrs` (0 → I, 1 → Q, 4 → FY); unresolvable → row rejected and listed. |
| `basis` | `latest` \| `as_filed` | default `latest` |
| `state` | one of `value derived evidenced_zero undefined_by_math history_horizon not_presented not_in_template defect` | frozen contract |
| `value` | decimal **string** or null | required when state in (value, derived, evidenced_zero → "0"); null otherwise. Full precision, no scaling. |
| `unit` | `USD` `USD/shares` `shares` `pure` | required with a value |
| `decimals` | int or null | XBRL decimals of the source fact (for the proof's tolerance) |
| `source_fact_ids` | int[] | core.fact ids behind the value (filed cells: 1+; derived: the inputs) |
| `accession` | text or null | the filing the value was taken from (the carrier filing for a derived cell) |
| `tag` | text or null | the XBRL tag (filed), or null for derived/composed |
| `members` | array or null | composition detail: `[{"tag","value","accession","label"}]` (total debt, capex multi-member) |
| `fsn_set`, `fsn_stmt`, `fsn_line` | text/text/int or null | FSN period (`2026m07`), statement (`IS BS CF`), pre.tsv line number of the face line |
| `derivation` | object or null | `{"formula":"FY - 9M_YTD","input_fact_ids":[...],"input_accessions":[...],"policy":"same_vintage"}` ; required when state = derived |
| `rule_id` | `family.rule@N` | the rule that produced this row (contract pattern) |
| `rule_run_id` | uuid or null | the `analytics.rule_run` row, when the lane ran under one |
| `evidence_level` | `FILING-CHECKED` \| `DATA-INFERRED` | per contract |
| `reason_code` | text | required when state is a blank state; snake_case, from §3 or a new code declared in the manifest |
| `reason_text` | text | one sentence a user could read; required with reason_code |
| `defect_class`, `owner`, `root_cause_class` | contract enums | required iff state = defect |
| `input_refs` | object | anything else that explains the row (accessions, alternatives, tolerances) |

### 2.2 Example rows
```json
{"company_id":1,"cik":"0000320193","data_point_name":"revenue_sanity_resolved","period_grain":"Q","period_start":"2026-06-29","period_end":"2026-09-27","basis":"latest","state":"value","value":"102466000000","unit":"USD","decimals":-6,"source_fact_ids":[348812001],"accession":"0000320193-26-000079","tag":"RevenueFromContractWithCustomerExcludingAssessedTax","fsn_set":"2026m10","fsn_stmt":"IS","fsn_line":1,"rule_id":"is.revenue_total@1","rule_run_id":null,"evidence_level":"FILING-CHECKED","reason_code":null,"reason_text":null}
{"company_id":1,"data_point_name":"dividends_per_share_resolved","period_grain":"Q","period_start":"2025-06-29","period_end":"2025-09-27","basis":"latest","state":"derived","value":"0.26","unit":"USD/shares","source_fact_ids":[31,32],"accession":"0000320193-25-000073","tag":null,"derivation":{"formula":"FY - 9M_YTD","input_fact_ids":[31,32],"input_accessions":["0000320193-25-000073","0000320193-25-000057"],"policy":"same_vintage"},"rule_id":"pershare.q4_dps_by_subtraction@1","evidence_level":"DATA-INFERRED"}
{"company_id":7,"data_point_name":"operating_income_resolved","period_grain":"Q","period_start":"2014-01-01","period_end":"2014-03-31","basis":"latest","state":"defect","value":null,"rule_id":"ingest.instance_fallback@1","reason_code":"filing_has_no_xbrl","reason_text":"10-Q 0001104659-14-034914 has no XBRL instance (EDGAR isXBRL = 0); the statements exist only as HTML.","defect_class":"ingestion","owner":"data_engineer_l2","root_cause_class":"ingestion","evidence_level":"DATA-INFERRED","input_refs":{"accession":"0001104659-14-034914"}}
```

## 3. Reason codes (start set; declare any new code in the manifest with one line of meaning)
`line_not_presented_in_filing` · `line_presented_combined_with_others` · `filing_has_no_xbrl` · `value_in_note_not_on_statement_face` ·
`restated_copies_disagree` · `shown_differs_from_printed_line` · `quarters_do_not_sum_to_ytd` · `mixed_vintage_inputs` · `sign_conflict` ·
`no_prior_quarter_end` · `history_before_floor` · `not_in_template` · `derived_value_retired` · `held_pending_verifier`.

## 4. Family ownership (data_point_name → one lane)
| family (manifest `family`) | lane | data points |
|---|---|---|
| `is_core` | existing IS releases (Ritwik) | revenue_sanity, net_income, operating_income, gross_profit, cost_of_revenue, operating_expenses, income_before_tax, income_tax_expense |
| `pershare_filed` | scrooner-28 | basic_eps, diluted_eps (filed, split-adjusted), dividends_per_share (filed + derived Q4 by subtraction = state `derived`), shares |
| `pershare_derived` | scrooner-26 (Family C) | derived EPS quarters (state `derived`), their retirements (`derived_value_retired`), effective-tax-rate inputs; quick ratio = metric, emit INPUTS only |
| `cashflow` | scrooner-28 | cfo, cash_flow_investing, cash_flow_financing, share_buybacks, dividends_paid |
| `capex_da_cash_debt` | scrooner-15 | capex, d_and_a, cash_and_equivalents, total_debt (+ members) |
| `interest` | scrooner-26 | interest_expense (incl. 2024 era tags), interest_income |
| `bs_core` | existing BS releases | total_assets, total_liabilities, current_assets, current_liabilities, stockholders_equity, ppe_net, inventory |
| `instance_fallback` | scrooner-8a (B9) | any data point of a filing the API never carried; loads AFTER the family files (fills only keys no family emitted) |
Metrics (quick ratio, ROE, P/E, ...) are NOT v2 cells in v1: they are recomputed from the served view by the metric layer.
A data point missing from this table has no owner yet: ask before emitting it.

## 5. What the loader rejects (whole file, with a listing)
unknown data_point_name · grain not in FY/Q/I · state outside the contract · value present on a blank state or missing on a valued one ·
reason_code missing on a blank state · defect fields inconsistent · rule_id not `family.rule@N` · duplicate key · key owned by another family ·
period unresolvable · company outside the cohort · period_end before 2014-01-01.
