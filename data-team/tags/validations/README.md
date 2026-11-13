# Validation checks for the predictor and the loader

`dqc-checks.csv`: one row per runnable check derived from a DQC rule, a FASB taxonomy implementation guide or SEC staff guidance (cards/dqc-and-public-guidance.md). Columns: check_id, source_rule, check_type (equality, less_or_equal, non_negative, preference, structure, mutual_exclusion, ratio, scale, value_check), data_points, condition, on_fail, source. Identity checks never derive an instant (doc 02); a failed check holds or flags the cell. Engineering wires them in (Dhairya 2026-11-12).
