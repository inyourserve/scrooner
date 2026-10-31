# The common cell format (v1, 2026-10-31) and the hybrid rebuild of analytics.canonical_fact

Status: design, scrooner-8a (engineering). Founder direction via scrooner-0f 2026-10-31 (second correction): NO side table,
NO fallback, NO switch view. The hybrid build (FSN structure + SEC API facts, filing instance via B9 as gap filler) REPLACES
the old companyfacts-mapping path and its values for the 1,000 cohort companies, writing `analytics.canonical_fact`
directly, full rebuild per company. The folder name keeps "v2" only as the project label.

## 1. Design in eight lines
1. **Store = `analytics.canonical_fact` as is** (key company, concept, period). The loader writes it directly: per
   company × family, `delete` that family's data points for the company, then `insert` the valued cells (value, source_fact_ids).
   Blank cells go to the existing run-scoped reason store `analytics.cell_blank_reason` under one `analytics.rule_run` per
   family load (`replace_rule_reasons`, scope run+company+rule). Proof results stay in `analytics.cell_proof` (0114). No new table.
2. **One additive schema change, needed for provenance of VALUED cells** (filed cells trace through `source_fact_ids`
   → core.fact accession/tag, but the producing rule/family does not): `alter table analytics.canonical_fact add column
   rule_run_id uuid references analytics.rule_run, add column family text` (nullable; old rows null). Written as 0117 only on your go.
3. **Cells, not facts**: one row per displayed cell (FY, Q, I grains); every blank carries a reason from the frozen eight-state
   contract; a key owned by two families is a load error (ownership table §4).
4. **One loader** `scrooner-cells load <family> <cells.jsonl.gz>` (pipeline/normalizer/cell_loader.py): validates each row
   against `common/cell_contract.py` + this spec, binds the period (§2.1: exact dates, else fiscal binding within 10 days),
   creates missing `core.period` rows, writes per company in one transaction, records the manifest sha256 on the rule_run.
   Idempotent: same file twice = same rows. No before-image, no rollback: re-load the family file.
5. **Proof** (`scrooner-proof run`) runs over the rebuilt cells, writes `cell_proof`; a derived cell is proven through its
   inputs. Served value = canonical_fact value unless proof says DISAGREE (served blank with `restated_copies_disagree` /
   `shown_differs_from_printed_line`); UNCHECKED never blanks (founder standing rule).
6. **Nightly, steady state**: new filing → core.fact via the SEC API path (fast) → the family rules recompute the touched
   company's cells → the same loader → proof. FSN monthly set published → structure re-check of the touched companies.
   Filing the API never carried → B9 (instance fallback) → core.fact → same family rules → same loader.
7. **Retirement**: once the family files are loaded and the Verifier draw passes, the mapper/conflict-fill/concept-fallback/
   derivation stages are skipped for cohort companies in the nightly (`--exclude-ciks cohort`); their code stays for the
   non-cohort population until the hybrid covers it.
8. **Cut-over order**: lanes emit full-population files → load (per family, any order; `instance_fallback` last, fills only
   unowned keys) → proof → Verifier draws 10 per family → certify dry run → old-stage skip switched on in the nightly.

## 2. The cell file
- **Format**: JSON Lines, gzip (`*.jsonl.gz`), UTF-8, one cell per line, plus `manifest.json` next to it:
  `{"family","rule_id","git_commit","produced_at","rows","sha256","companies","data_points":[...],"period_floor":"2014-01-01"}`.
- **Location**: bucket `fsn-notes`, prefix `cells/<family>/<YYYY-MM-DD>/cells.jsonl.gz` (+ manifest). Small files (<5 MB) may
  ALSO be committed under `data-team/46-canonical-fact-v2/cells/<family>/`. Give the loader the bucket URL or a local path. One file per family (all its data points, all 1,000 companies).
- **Scope**: the 1,000 cohort companies, every FY/Q/I cell with `period_end >= 2014-01-01` (history floor; serving window 2015+).
- **One row per key** `(company_id, data_point_name, period_grain, period_start, period_end, basis)`. Duplicates = load error.

### 2.1 Row fields (flat JSON; `null` where not applicable)
| field | type | rule |
|---|---|---|
| `company_id` | int | core.company.id (required; `cik` may be sent too and is checked against it) |
| `cik` | "0000320193" | optional cross-check |
| `data_point_name` | text | the `analytics.canonical_concept.name` (`revenue_sanity_resolved`, `basic_eps_resolved`, `capex_resolved`, ...). Never a metric. |
| `period_grain` | `FY` `Q` `I` | FY = the filing's annual column; Q = 3-month (filed or derived); I = instant. `TTM`/`TP` (YTD spans) rejected in v1: a held YTD-derived quarter is a Q blank with its reason. |
| `period_start`, `period_end` | ISO dates or null | EXACT dates of the company's `core.period` when you have them (they win). |
| `fiscal_year`, `fiscal_period`, `period_type`, `fsn_end` | int, `FY`/`Q1`..`Q4`, `duration`/`instant`, ISO date | **fiscal-period binding** (required when exact dates are null, recommended always): the loader binds to the company's `core.period` with that fiscal_year + fiscal_period + period_type whose end is within 10 days of `fsn_end` (FSN nominal month-end; KO 2015-03-31 → period 2015-04-03). No match → the loader creates the period ONLY when exact dates were given; otherwise the row is rejected and listed. `qtrs` (0/1/4) may be sent too and is checked against the grain. |
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
| `instance_fallback` | scrooner-8a (B9) | facts of a filing the API never carried go into core.fact; the owning family's rules then emit the cells (B9 emits no cells of its own) |
Metrics (quick ratio, ROE, P/E, ...) are NOT cells in v1: the metric layer recomputes them from canonical_fact; emit their INPUT concepts. Quick-ratio hides = reasons on the input cells.
A data point missing from this table has no owner yet: ask before emitting it.

## 5. What the loader rejects (whole file, with a listing)
unknown data_point_name · grain not in FY/Q/I · state outside the contract · value present on a blank state or missing on a valued one ·
reason_code missing on a blank state · defect fields inconsistent · rule_id not `family.rule@N` · duplicate key · key owned by another family ·
period unresolvable · company outside the cohort · period_end before 2014-01-01.
