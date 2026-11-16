# Independent review of dd7995b5 (structural loader mechanisms), 2026-11-16

Reviewer: cloud GitHub-ops session. Read-only; no DB. The commit's own tests (`test_structural_loader_mechanisms.py`) pass: 6 passed.

Failing tests: `failing_tests_dd7995b5.py.txt` (kept out of `pipeline/tests` so CI stays green; rename to `.py` and run with dummy `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`).

| # | Where | Defect | Status |
|---|---|---|---|
| 1 | `mapper/structural_direct.py:177` `_fix_covers` | Treats every `docmap_fix@1` row as a hand fix, including `source=line_map` rows that the loader's new `is_hand_fix` demotes. A later docmap-load re-inserts the 136 stale rows from `data-team/companies/reads/fixes`, and direct serving re-serves them (NEE total_debt FY2018 = 63M lease part). Fix: apply `is_hand_fix` in `_fix_covers`. | Confirmed by `test_direct_fix_covers_agrees_with_loader_on_stale_line_map_fix` |
| 2 | `mapper/structural_loader.py` `fact_options` (`out[k] = exact.get(k) or near[k]`) | A stray authoritative fact dated exactly on the FSN month-end replaces the true 52/53-week period-end fact. | Confirmed by `test_fact_options_stray_exact_instant_beats_true_52week_end`; low impact |
| 3 | `mapper/reason_guard.py:52-73` | A ruling counts while the file's own `decision_before == decision_now`. It is never compared with the decision the resolver emits now, and the key has no fiscal year. A ruled tag therefore escapes the guard after the decision changes. | Plausible, from the code |
| 4 | `mapper/reason_guard.py:61` (`files[-1]`) | Only the newest rulings file is read, so a later partial sweep drops every earlier ruling. | Design risk; one file exists today |

Checked and sound: the rulings path does not depend on the working directory; accession and tag key formats match; `lru_cache` keeps no per-company state; the `source=line_map` substring appears only in generated fix notes; derived rows loaded as not_presented are tagless; `fact_options` windows exclude quarters and adjacent years; values stay `Decimal`.
