# FSN store: the company directory and the concept_rule seed (formats v1, 2026-11-01)

Owner: scrooner-8a. Implements data-team/strategy/FSN-STORE-DESIGN-2026-11-01.md §2 (shard) and §3 rule 1 (seed).
Both formats are inputs to code; a change is a version bump here, never a silent edit.

## 1. Company directory: `companies/<cik10>/`
One directory per cohort company, written by `fsn_shard.py` from the bucket extracts (2014q1 → latest set), read by
`fsn_store_load.py` and by every lane reader. SEC column names and order are kept exactly; the only additions are marked.

| file | rows kept (per the design) | columns |
|---|---|---|
| `sub.tsv.zst` | every 10-K, 10-K/A, 10-Q, 10-Q/A of this CIK (and filings where it is a co-registrant via `aciks`) | the SEC sub columns + first column **`fsn_set`** (`2014q1`, `2025m10`, ...) |
| `pre.tsv.zst` | rows of those filings with `stmt` in BS IS CF CI EQ CP UN (statement presentation incl. cover/unclassified); note-level pre (stmt empty) stays in the bucket | SEC pre columns: adsh report line stmt inpth tag version prole plabel negating |
| `num.tsv.zst` | every non-dimensional row (`dimh` = the no-dimension hash, notes included) + every dimensional row whose (adsh, tag, version) appears on a kept pre row | SEC num columns: adsh tag version ddate qtrs uom dimh iprx value footnote footlen dimn coreg durp datp dcml |
| `cal.tsv.zst` | all arcs of those filings | adsh grp arc negative ptag pversion ctag cversion |
| `ren.tsv.zst` | all reports of those filings | SEC ren columns (adsh report rfile menucat shortname longname roleuri parentroleuri parentreport ultparentrpt) |
| `tag.tsv.zst` | every (tag, version) referenced by the kept pre/num/cal rows | SEC tag columns (tag version custom abstract datatype iord crdr tlabel doc) |
| `dim.tsv.zst` | every `dimh` referenced by the kept num rows | SEC dim columns (dimhash segments segt) |
| `manifest.json` | see below | |

Encoding: UTF-8 TSV with header, zstd. Values are the SEC strings untouched (no rounding, no reformatting); `ddate` is the
SEC month-end date, `qtrs` the SEC quarter count, `negative` the arc weight sign (1 = subtract).

`manifest.json`:
```json
{"cik":"0000789019","company_id":4,"fsn_sets":["2014q1","...","2026m09"],"accessions":["0001193125-14-029112","..."],
 "row_counts":{"sub":51,"pre":9130,"num":61204,"cal":5820,"ren":2900,"tag":1410,"dim":880},
 "file_sha256":{"sub":"...","pre":"...","num":"...","cal":"...","ren":"...","tag":"...","dim":"..."},
 "input_sha256":"sha256 of the seven file_sha256 values joined by newline in the table order above",
 "shard_commit":"<git sha>","created_at":"2026-11-01T12:00:00Z","bucket_manifest":"fsn_manifest_all.jsonl sha256"}
```
`input_sha256` is the load's idempotency key together with the loader commit (design §2). Lane readers read ONE directory
and must not need any other file.

Reading a directory in Python: `fsn_store.company_dir.read(path)` (fsn_shard.py's sibling) yields the seven tables as
lists of dict rows with the SEC column names; the lanes port their detectors onto that (regression gate §3).

## 2. concept_rule seed: `concept_rules/<lane>.jsonl`
One JSON object per rule; loaded into `fsn.concept_rule` by `fsn_store_load.py seed-rules`, which validates every row and
refuses the whole file on the first error (listed). Exported from the Verifier-passed lane code, never retyped.

| field | type | rule |
|---|---|---|
| `canonical_concept` | text | an `analytics.canonical_concept.name` (`revenue_sanity_resolved`, ...) |
| `stmt` | `BS` `IS` `CF` | the statement the line must be on |
| `match_kind` | `std_tag` \| `calc_position` \| `combined` | design §3 rules 1-3 |
| `tag` | `us-gaap:Revenues` (prefix:tag, version-agnostic) or null | required for std_tag and combined; null for calc_position |
| `position` | object or null | required for calc_position: `{"slot":"<detector slot name>","anchor_concept":"<concept the slot is relative to>","relation":"child_of"\|"sibling_after"\|"parent_of","sign":1\|-1}` |
| `components` | [concept, ...] or null | required for combined: the concepts the line combines (never mapped as one) |
| `priority` | int | lower wins when several rules match one line; unique per (canonical_concept, stmt, match_kind, tag) |
| `era_from`, `era_to` | ISO date or null | rule valid for filings with `period` in [era_from, era_to); from `era_detect.py`, unchanged |
| `rule_id` | `family.rule@N` | the lane rule the seed comes from (contract pattern) |
| `source_commit` | git sha | the lane code the rule was exported from |
| `evidence` | text | one line: the tag card or the Verifier draw that passed this rule |

Example:
```json
{"canonical_concept":"revenue_sanity_resolved","stmt":"IS","match_kind":"std_tag","tag":"us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax","position":null,"components":null,"priority":10,"era_from":"2018-01-01","era_to":null,"rule_id":"is.revenue_total@1","source_commit":"78ca35e","evidence":"tag card revenue ASC 606; Verifier is_core 10/10"}
{"canonical_concept":"current_liabilities_resolved","stmt":"BS","match_kind":"combined","tag":"us-gaap:AccountsPayableAndAccruedLiabilitiesCurrent","position":null,"components":["accounts_payable_resolved","accrued_liabilities_resolved"],"priority":50,"era_from":null,"era_to":null,"rule_id":"bs.combined_line@1","source_commit":"fec7140","evidence":"design §3 rule 3"}
```
A `combined` row records that the TAG is a combined line (blank `line_presented_combined_with_others` for each component);
`canonical_concept` is the concept the line would otherwise be mistaken for.
