# Blind exam (Tag Expert)

Protocol agreed with Dhairya 2026-11-12 (founder correction: the blind exam replaces the 20-card re-check).
- Ranks: data-team/strategy/data/cohort_v1_1_proposal_2026-10-24.csv. Dev set ranks 51-100 (already read): scored separately, never blind.
- `<TICKER>-prediction.csv`: one row per docmap data point, predicted from FSN face lines (latest 10-K) + the tag library and company overrides only, by `tools/predict.py` (deterministic). A prediction counts only if its commit is earlier than the first commit of that ticker's docmap on any work/reads/* branch.
- Grading: `tools/grade.py` against data-team/companies/reads/<TICKER>-docmap-*.csv. Correct = status matches and, for mapped/combined/component_sum/component_in_note, the tag set matches. Error classes: status, tag, missed; no_prediction is never correct.
- Every miss: a card fix (accession, R page) and a predict.py fix, the same day.

## Predictor versions (dev = ranks 51-100, never blind)
| Version | Commit time | Dev accuracy | Notes |
|---|---|---|---|
| v1 | 2026-11-12 18:10Z (7fca0d0b) | 82.4% (407 wrong / 2,314) | first frozen predictor |
| v2 | 2026-11-12 (7d58f467) | 87.7% (280 wrong / 2,275; 39 shares rows are key errors under Dhairya's 2026-11-12 ruling) | opex rules, combined-perimeter concepts, capex demote fix, sole-debt interest, lone G&A, note-default majority, field normalisation |
Re-prediction: only tickers with no docmap on any work/reads/* branch or main at commit time; an earlier prediction of a read ticker is never replaced.
| v3 | 2026-11-12 (b9e50b58) | 88.1% (269 wrong / 2,261; 53 key errors: 39 dei shares + 14 opex totals incl. cost of revenue) | Dhairya opex ruling 2026-11-12 (canonical_concept 53/208): printed total excl. COR, else every face line between GP/COR and OI tied to GP − OI, COR-inclusive total = combined, one-step corporate IS = not_presented; integer line numbers; credit-sign in the tie |
| v4 | 2026-11-12 (ca6d73ff) | 89.8% (229 wrong / 2,253; 61 key errors incl. 8 opex adjudications) | note-fact presence per filing (inputs/notes.jsonl from tools/NOTES.sql), refined opex rule 5, combined interest-income pattern |
| v5 | 2026-11-12 (ca8b82e8) | 90.3% on the 100-company dev set (dev 51-100 + the 50 already graded blind; 383 wrong / 3,950; 85 key errors, 259 key_unverified set aside) | AR single-line override outcome, plain-caption net interest (AAON), summed CF capex lines, note convention (SBC note fact = mapped), docmap-loadable columns (fy0_api, evidence_class); VERSION constant |
| v6 | 2026-11-12 (01401b7a) | 91.0% on 120 companies (dev 51-100 + 70 already graded blind; 415 wrong / 4,622) | net income without a parent line, lone/summed CF D&A, InterestPaidNet / IncomeTaxesPaidNet preference (DQC_0065), 3 library rows, more rule-based key errors |
| v7 | this commit | = v6 (parity: 997 companies, 52,841 rows, 0 differences) | ENGINE: all knowledge moved to data-team/tags/rules/*.csv (761 rules); predict.py evaluates rules and writes rule_ids on every row; VERSION = hash of the rule files |
