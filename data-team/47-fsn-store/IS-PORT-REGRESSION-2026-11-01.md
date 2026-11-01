# Income-statement lane: port to the company-wise FSN store, regression gate (2026-11-01)

Owner: scrooner-a9 (income-statement lane). Design: data-team/strategy/FSN-STORE-DESIGN-2026-11-01.md; formats: FORMATS-v1 (scrooner-8a, feb7223).

## What changed
- `fsn_company.py` (new): reads one `companies/<cik10>/` directory (FORMATS-v1 section 1, raw SEC columns) into the detector's inputs, using `fsn_is_pre.py`'s own row transforms (`sub_record`, `pre_record`, `cal_record`, factored out, not copied). Only this CIK's filings; co-registrant filings come from `sub.aciks`.
- `is_detect.py`: `detect_filing` / `detect_filings` / `write_outputs` split out; new `--company <dir|parent|@list>` mode. Cohort mode is unchanged.
- `is_not_presented.py`: the face check reads `--company=<dir|parent|@list>` or the cohort `is_fsn` directory.
- `is_replay.py`: production (`analytics.canonical_fact`) is never read; output equals what `IS_REPLAY_PROD=0` wrote. It still reads `core.fact` face columns until `fsn.value` exists.
- `is_emit.py`: quarter derivation removed (fsn_select does it under SAME_BASIS). The last file with the lane's own derivation is is_core 2f98b025 (commit b9f3c4f).
- Seeds: `concept_rules/is.jsonl` (14 rows; `export_concept_rule_seeds_is.py`, imports is_detect's constants), plus bs/cf/per_share (24 rows; `export_concept_rule_seeds_lanes.py`, import or ast from the lane code on 1b4da8f). Not expressible in FORMATS-v1: `is_not_extracted.md` (16) and `lanes_not_extracted.md` (142).

## Gates (inputs: the is_core 77f5846a run's own intermediates)
| gate | result |
|---|---|
| A. cohort mode, refactored code: is_detect (6 files) and is_not_presented (3 families x 3 files) vs the verified outputs | 15/15 byte-identical |
| B. company mode on 999 raw-column company directories built from the same inputs (`is_port_synth_companies.py`), co-registrants from sub.aciks | 5 era files byte-identical; is_filing_slots identical as a set (223,575 rows); 9/9 not-presented files byte-identical |
| C. is_replay without production reads, 25 companies (MSFT, HD, TFX, ETR, AAPL, JPM, BA, F, NFG, GE, AJG, ...), vs the verified replay rows of those companies | 5/5 families identical as sets (5,762 cells); vs a fresh run of the old code: same content, only line order differs |
| D. is_emit without derivation vs 77f5846a | all 242,272 non-derived cells identical; every difference is a removed derivation (26,543 derived -> no_filed_column_for_period, 457 derived keys outside the calendar dropped, 12,483 quarter-derivation defects -> calendar blank or absent) |

Not yet run: the reader on REAL shards (fsn_shard.py output). Expected differences to check there: (1) the shard keeps 10-K/10-Q(/A) only, fsn_is_pre also took 10-KT/10-QT; (2) `sub.aciks` vs the coregistrant file `coreg_cohort_adsh.txt`; (3) cal row order inside a filing (the detector's arc dict keeps the last weight of a repeated parent/child pair, as before).

## Found for fsn_select (not fixed here)
- 77f5846a derived 6 quarters over a HELD printed 3-month column (gate D: derived -> G1_printed_total 2, G1_printed_line 3, hold_multiple_roots 1); "a printed 3-month column wins" must also hold when that column is held.
- Seeds carry the unconditional standard-tag maps only. The detector's holds (sector shapes, perimeter labels, siblings, position) must still demote a seed match, so the line_map needs the ported detector, not the seed alone.
