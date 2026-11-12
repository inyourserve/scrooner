# Rule proposals (LEARNING-SYSTEM.md §5)

Readers, the Verifier, the nightly path and Engineering propose rules here; the Tag Expert accepts only through the backtest (exam/tools/backtest.py: net gain, zero regression in classes at 99% or better).

File: `rules/inbox/<proposer>-<date>.csv`, the rule columns plus two:
`rule_id,version,namespace,data_point,scope,era,kind,when,then,precedence,evidence,author,date,note,proposed_by,finding`
- `kind`, `when`, `then`: as in rules/README.md (when/then are JSON).
- `evidence`: accession + R page, a DQC rule id, a FASB/taxonomy reference or a doc 02 entry. A proposal without evidence is rejected.
- `scope`: `all`, a template group, a sector, or a ticker (company override; precedence company > template > data point > default).
- `finding`: the graded miss or docmap row that motivates it (ticker, data_point, ledger row).
Status is tracked in `rules/inbox/STATUS.csv` (proposal file, rule_id, status = open / accepted / rejected, backtest delta, date).
