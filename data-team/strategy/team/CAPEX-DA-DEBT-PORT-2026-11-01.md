# Capex, D&A and debt lane on the FSN store: status and plan (2026-11-01)

For Dhairya. Owner of the lane from now on: this session (request relayed by the HD pilot proof session, 2026-11-01). Branch `work/capex-da-debt/fsn-detectors` (on top of `work/balance-sheet/fsn-store`). Pattern: `data-team/strategy/team/BS-PORT-2026-11-01.md`. Lane handoff: `data-team/strategy/handoff/CAPEX-DA-CASH-DEBT-2026-11-01.md`.

**Status: started. One decision is needed from you (section 3) before the bulk of the port.** Nothing writes to the database.

## 1. What the pilot is missing (run 41312996998, `gaps.csv`)

| data point | `no_mapped_line` keys | why |
|---|---|---|
| total_debt_resolved | 419 | the debt calc_position rows anchor on `current_liabilities_resolved`, which no rule mapped; and the slot (`borrowing`, `finance_lease`, `combined`) is decided by `build_debt_slots.classify` plus the record's calc/face/lease guards, not by the seed |
| capex_resolved | 350 | slots `ppe` / `leased` / `software` exist only inside `cf_da_capex_variants.capex_nature` + the investing-block position |
| depreciation_and_amortization_resolved | 349 (+57 `no_mapped_line_cond`) | slot `asset_da` exists only inside `da_nature` + the operating-block position |

## 2. Done on this branch

- **Anchor seed:** `current_liabilities_resolved` = `us-gaap:LiabilitiesCurrent` (std_tag, priority 10), rule `bs.anchor_current_liabilities@1`. It is exported, not typed: the tag comes from the debt lane's `PARENTS`, the concept from the mapper's approved `CONCEPT_MAPPINGS`. With it, the `child_of current_liabilities_resolved` debt and liabilities slots can fire. `bs.jsonl` is now 17 rows; the exporter-equality test passes.

## 3. Decision needed: how total debt reaches a cell

`fsn_store.select` takes the one mapped line per concept and calls two different values in one filing a defect (`conflicting_values_in_filing`). Capex and D&A fit that today, because the lane publishes single-member cells only and holds multi-member ones (`held_pending_verifier`, handoff point 4). **Total debt does not fit:** it is almost always a sum (current + noncurrent members, plus note finance leases by your option b). Two ways to do it:

- **(A) Recommended: debt cells from the lane's own replay.** `replay_debt_fsn.py --company` already reads one store company directory. Gate C showed it equals the Verifier-passed report_v4 (442/460; the 18 are the "securities loaned" holds). It would emit a `capex_da_cash_debt` total_debt family file (grain I, calendar instants), loaded by `cell_loader` like the other families; select then skips `total_debt_resolved`. The detector only marks member lines (evidence: slot, class), status `excluded` with reason `summed_by_debt_family`, so select never sees them as rival values.
- **(B) Teach select to sum.** A `composed` concept list in `select.py` that sums the mapped members of one column (weights, completeness, note leases). This changes scrooner-8a's selection engine and needs its own gate; it would also have to re-implement the replay's note and lease rules.

I will build (A) unless you say (B).

## 4. Plan once decided (capex and D&A first: they need no decision)

1. **Detector module** `pipeline/src/scrooner_pipeline/fsn_store/detectors/cf_capex_da.py`. It reads one filing from `fsn.line` / `fsn.tag` / `fsn.calc_arc` / `fsn.value`, and its classifiers are the lane's `capex_nature`, `da_nature` and block rules, moved out of `cf_da_capex_variants.py` into an importable module. The script imports them back, so there is one copy of each rule. It returns FORMATS-v1.1 overrides `(report, line, concept_id | None, status, rule_id, evidence)`:
   - one counted member line → `mapped`
   - several → the lane's hold
   - combined lines → `combined`
2. **Your Verifier findings, honoured explicitly:**
   - The D&A multi-line hold is decided **per filing** (HD prints one D&A line before FY2025, so those filings map). A test pins HD.
   - MSFT "Depreciation, amortization, and other" stays `combined` (`da_nature` → `combined_other`). A test pins MSFT.
3. **Debt member detector** (`detectors/debt.py`): `build_debt_slots.classify` + the `assemble_fsn` record guards, per section 3.
4. **`jobs/fsn.py`**: `map_company` passes `detectors=[...]` (today it passes none).
5. **Regression gate** against the lane's last Verifier-passed output, `cells/capex_da_cash_debt/2026-11-04/cells.jsonl.gz` (155,257 rows, sha 6f53c945, committed on `work/cash-flow/da-capex`). Its inputs are cohort FSN extracts in the `fsn-notes` bucket, so the gate is a GitHub Actions workflow (it has the bucket credentials; read-only, no database writes, outside the nightly window). It does three things:
   - shard the cohort;
   - run the lane script in cohort mode (old vs ported, byte-identical, as in the BS gate);
   - run the store path (load → map with detectors → select) and compare each capex/D&A cell with the reference file.
6. Report the per-key result here, with every difference classified, as in the BS port.

## 5. Known risks

- `cf_da_capex_variants` decides on VALUES, not just lines: IS tie-out for generic amortization, sign tests for lease intangibles, discontinued-block CFO choice. A line-level mapping cannot carry those decisions, so the detector must read `fsn.value` for the filing's face columns, and a hold must stay a hold. The gate is what proves this.
- Window: the lane file starts 2014; the store does too. No difference expected there.
