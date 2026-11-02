# Capex, D&A and debt lane on the FSN store: detectors (2026-11-01)

For Dhairya. Lane owner: this session (handed over by the HD pilot proof session, 2026-11-01). Branch `work/capex-da-debt/fsn-detectors`; it merges `main` and `work/balance-sheet/fsn-port-fixes`. Lane handoff: `data-team/strategy/handoff/CAPEX-DA-CASH-DEBT-2026-11-01.md`. Nothing writes to a shared database.

**Status: capex and D&A are done and pushed (f17217a9). Debt is still waiting on the decision in section 4.**

## 1. What changed

| file | change |
|---|---|
| `pipeline/scripts/slot_records/cf_da_capex_variants.py` | The Verifier-passed version (e79ff33, the one behind file 6f53c945), first imported verbatim (666f7b63). Its per-(filing, column) loop body is now `evaluate(cik, ddate, q, f)`, and the module-level work moved into `main()`. **No rule changed:** the cohort run on 29 companies (59 FSN sets) gives byte-identical cells, summary and examples to the verbatim file. `main` had an older copy (3346020). |
| `pipeline/src/scrooner_pipeline/fsn_store/detectors.py` (new) | `capex_da_detector`, a FORMATS-v1.1 detector. It runs the lane's own `evaluate` on every cash-flow face column of ONE filing and applies `emit_capex_da_cash`'s release rule: capex = an interim value with exactly one member; D&A = class `is_anchor` / `single_line_ties_is` / `single_line_clean`. Section 2 has the per-filing rule. |
| `fsn_store/mapping.py`, `jobs/fsn.py` | `map_company(..., detectors=)`. The `pilot` command passes `detectors.DEFAULT`. |
| `concept_rules/bs.jsonl` | The `current_liabilities_resolved` anchor I added earlier is **removed**. `main` now seeds the same row in `bs_current.jsonl`, and the two rows collided on `uq_fsn_concept_rule`; with both, seeding would have failed in the pilot. |
| `capex_da_store_gate.py` (new) | The regression gate through the real store path (section 3). |

## 2. The per-filing rule (your two Verifier findings)

`select` takes one mapped line per concept and reads it in every column of the filing. So:

- A line is **mapped** only if every face column of the filing that prints a candidate publishes through that same line, AND the store's raw print equals the lane's value in each column (the lane reads signs as presented).
- Otherwise the filing is **held** for that concept. Every capex/D&A line the seeds mapped is returned `unmapped` (rule `cf.capex_da_held@1`) with the lane's reasons, so no rival value reaches select. That removes the pilot's `conflicting_values_in_filing` cells, e.g. JPM's several D&A lines in one 10-K. A test loads that JPM 10-K: the seeds map ≥2 D&A lines, the detector maps exactly 1.
- **Per filing, not per company.** AWK's Q1 2015 10-Q publishes one D&A column and holds the other, so that filing holds (test). The lane's company-wide "net line" rule (KEY) is the one cross-filing rule; the detector applies it within the filing only.
- **MSFT** "Depreciation, amortization, and other" → `da_combined_with_other_items` → the line is returned `combined` (test).
- **HD: a decision for you.** Before FY2025, HD's cash-flow statement prints ONE D&A line (e.g. FY2019 2,296M). Its income statement prints a different "Depreciation and amortization" (1,989M), which excludes D&A inside cost of sales. The lane's release classes publish a single CF line only when there is no IS D&A total or the two tie, so **the Verifier-passed file holds all 63 HD D&A cells**, and the detector reproduces that (test). Publishing HD's CF line widens the release scope, so it needs a Verifier draw of the class "one CF line, IS total smaller". I have not changed it.

## 3. Gate: the store path vs the lane's Verifier-passed file

A local scratch Postgres 16 built from every migration; the gate refuses any other database. It loads the 10 pilot companies' real company directories (MSFT HD AAPL JPM TRV PLD NEE XOM JNJ WMT, sharded by `fsn_store.shard` from the SEC FSN sets) with `fsn_store.load`, seeds the committed `concept_rules`, then runs `map_company` + `select_company` twice. Each capex/D&A key (FY / Q, not derived) is compared with `cells/capex_da_cash_debt` 6f53c945. Evidence: `results/capex_da_store_gate_2026-11-01/store_gate.json`.

| class | seeds only | with detectors |
|---|---|---|
| same value as the lane | 0 | **290** (all of the lane's published keys) |
| lane has a value, store blank | 224 | **0** |
| `conflicting_values_in_filing` | 170 | **0** |
| value differs from the lane | 12 | **0** |
| store publishes where the lane holds the same filing | 2 | **0** |
| a later vintage publishes where the lane held the original filing | 27 | 5 |
| store print where the lane's derived quarter is held or different (later vintage; PLD Q 2014-09-30) | 39 | 1 |
| store print equals the lane's derived quarter | 10 | 27 |
| store key before the lane window (2011–2013 comparatives) | 14 | 29 |
| key the lane file does not have (PLD Q 2026-06-30, newer than the file) | 0 | 1 |
| both blank | 178 | 269 |

Verdict: **PASS** (0 keys published against the lane, 0 conflicts). The 6 later-vintage keys are JPM Q 2014-03-31, AAPL capex FY2016 / FY2017 / Q 2017-12-31, PLD D&A FY2014 and PLD Q 2014-09-30. The store takes the latest accepted filing (design §4), and the lane's own single-line rule passes on that later filing, while the lane held the original. **Worth a Verifier look before the pilot publishes them.**

## 4. Debt: still waiting on your decision

Total debt is a sum of members (+ note finance leases). `select` cannot sum lines, so no line-level detector can produce it. The seeds' debt slots fire only for custom tags (`map_filing` rule 2), and those lines are not mapped as rivals today. So the 419 `no_mapped_line` debt keys stay blank, with no wrong values.

- **(A) Recommended:** emit total-debt cells from `replay_debt_fsn --company`, reviewed and gated on `work/balance-sheet/fsn-port-fixes`, as a family file the pilot loads.
- **(B):** a summing path in `select.py` (scrooner-8a's engine).

I'll build (A) as soon as you say so.

## 5. Rerun

```bash
SCRATCH_DATABASE_URL=postgresql://<local scratch> pipeline/.venv/bin/python pipeline/scripts/slot_records/capex_da_store_gate.py <cells.jsonl.gz of 6f53c945> <out_dir> <companies>/<cik10> ...
```
