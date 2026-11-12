# Blind exam (Tag Expert)

Protocol agreed with Dhairya 2026-11-12 (founder correction: the blind exam replaces the 20-card re-check).
- Ranks: data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv. Dev set ranks 51-100 (already read): scored separately, never blind.
- `<TICKER>-prediction.csv`: one row per docmap data point, predicted from FSN face lines (latest 10-K) + the tag library and company overrides only, by `tools/predict.py` (deterministic). A prediction counts only if its commit is earlier than the first commit of that ticker's docmap on any work/reads/* branch.
- Grading: `tools/grade.py` against data-team/companies/reads/<TICKER>-docmap-*.csv. Correct = status matches and, for mapped/combined/component_sum/component_in_note, the tag set matches. Error classes: status, tag, missed; no_prediction is never correct.
- Every miss: a card fix (accession, R page) and a predict.py fix, the same day.
