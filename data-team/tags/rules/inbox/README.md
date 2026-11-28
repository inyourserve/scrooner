# Rule proposals (LEARNING-SYSTEM.md §5)

Readers, the Verifier, the nightly path and Engineering propose rules here; the Tag Expert accepts only through the backtest (exam/tools/backtest.py: net gain, zero regression in classes at 99% or better).

File: `rules/inbox/<proposer>-<date>.csv`, the rule columns plus two:
`rule_id,version,namespace,data_point,scope,era,kind,when,then,precedence,evidence,author,date,note,proposed_by,finding`
- `kind`, `when`, `then`: as in rules/README.md (when/then are JSON).
- `evidence`: accession + R page, a DQC rule id, a FASB/taxonomy reference or a doc 02 entry. A proposal without evidence is rejected.
- `scope`: `all`, a template group, a sector, or a ticker (company override; precedence company > template > data point > default).
- `finding`: the graded miss or docmap row that motivates it (ticker, data_point, ledger row).
Status is tracked in `rules/inbox/STATUS.csv` (proposal file, rule_id, status = open / accepted / rejected, backtest delta, date).

Automatic proposals (2026-11-28): `drill-auto.csv` is written by `data-team/tags/library/pattern_intake.py --drills` from the daily-drill commit step. One row per rule_gap miss class (class x data point x element, rule_id `drill.<data_point>.<hash>`, deduped across days), `kind = proposal_open` with empty when/then: the tag expert writes the rule body (kind, when, then) and accepts only through the backtest; a row edited past `proposal_open` is never overwritten except its evidence and finding. `evidence` links the drill day files on branch `drills`; `finding` starts with the pattern-intake row id and example cells. New rule_ids get an `open` row appended to STATUS.csv. Classes past the graduation bar are listed in `library/auto-map-eligible.csv`.
