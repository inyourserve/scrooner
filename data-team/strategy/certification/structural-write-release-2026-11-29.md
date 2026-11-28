# Structural write: release note and dry run (2026-11-29)

Stage 3 Resolve, M1. For Ritwik's switch review (founder rule: Ritwik reviews the one switch). Nothing was flipped.
All numbers come from read-only sessions (one connection, `default_transaction_read_only=on`, statement_timeout set)
on 2026-11-28 between 19:00Z and 19:35Z, with origin/main code at b2d3956f5. Top100-flow run 46174337050 was still
writing companies during the measurement, so the numbers are a snapshot.

## 1. What holds the write

- **No flag or config holds `structural-load`.** It runs inside `scripts/top100_flow.sh` (top100-flow.yml, dispatch
  only, also dispatched by top100-auto-trigger.yml while `AUTO_LOOP=true`). It last ran on 2026-11-28 and its rows are live.
- **What is held is the M1 nightly write**, gated on "155 top-100 DISAGREE cleared + the founder's typed words"
  (data-team/PIPELINE.md section 7; memory note "Review response 2026-11-21"):
  - repo variable `FSN_NIGHTLY_STAGE` = `load` (set 2026-11-28 18:30Z), not `write`, so
    pipeline-refresh.yml does not run `tagmap-plan --apply`;
  - `HYBRID_NEW_PATH` is unset (off);
  - the `select_write` stage of pipeline-fsn-write.yml runs only when dispatched by hand.
- The census's 70 era_unmapped cells with a resolver value are **not held by the loader**. The loader dry run below
  accepts 64 of the 68 cells we could match and plans **no change** to any of them. The other 4 are refused by the
  loader's own rules: 3 AXP `loans_net` (member part has no stored dimensioned fact) and 1 NEE `interest_income`
  FY2020 (the filing is quarantined because its calc check FAILs). 12 of the 64 are text_stated or stated_zero
  (CVX/TMUS DPS), which never get a map row and are served only through `structural_direct`.
  In the live export at 19:07Z, 66 of the 68 are still BLANK with reason era_unmapped. So the gap sits in the serve and
  guard step (tagmap-plan, structural_direct, era-guard: "not backed by the cell proof"), not in the structural write.
  Turning on `FSN_NIGHTLY_STAGE=write` would not serve them.

## 2. Gate condition: DISAGREE (live export 2026-11-28T19:07Z, `pipeline/scripts/top100_coverage.py`)

| Measure | Count |
|---|---|
| Top-100 template cells whose latest cell_proof verdict is DISAGREE | 129 (16:55Z export: 130) |
| of which a value is served (SHOWN_VALUE) | 2: ORCL cost_of_revenue FY2024 (15,143,000,000); CRM total_debt FY2018 (2,233,015,000) |
| of which the row is shown with no value (OPEN) | 127 |

The figure of 4 measured by another session is not reproduced here. The literal gate (155 DISAGREE cleared) is not
met: 129 remain, although only 2 of them serve a value.

## 3. Dry run of `structural_loader.load(apply=False)`, top-100 (96 companies with claims)

70,718 claims and 1,695 rejects. The run took 161 s. Live structural rows: 52,186. Planned: 52,177. Row diff: 34 removed, 27 added, all in
4 companies. The cause is resolver refreshes .93.d8 and .93.d9, which landed after the flow had loaded these companies.

| Company / data point | Cells | Now | After the write |
|---|---|---|---|
| AMZN cf_ar_change FY2015-25 | 11 | OPEN, not_in_template | new value (IncreaseDecreaseInAccountsReceivableAndOtherOperatingAssets) |
| XOM cf_ap_change FY2015-25 | 11 | OPEN, not_in_template | new value (IncreaseDecreaseInAccountsPayable) |
| T cf_inventory_change FY2022-25 | 4 | OPEN, not_in_template | new value (IncreaseDecreaseInOtherOperatingAssets) |
| T cf_inventory_change FY2015-21 | 7 | OPEN, not_presented | reason row dropped: the loader refuses a false reason because the filing's column holds a value; the cell stays open |
| NEE cf_ar_change FY2015 | 1 | PROVEN -90,000,000 | same value; the row changes from not_in_template to concept |

- **Cells changed: 34.** That is 26 new values where nothing is served now, 7 reason rows dropped and 1 relabel with the same value.
- **Red flags: 0.** No currently served PROVEN value changes.
- **Review items for Ritwik (perimeter, not proof):** T maps cf_inventory_change to IncreaseDecreaseInOtherOperatingAssets,
  and AMZN maps cf_ar_change to a tag that includes other operating assets. The 26 new values have no cell_proof
  row yet, so they serve only after `proof --write`.

## 4. Ask

Ritwik: review the one switch (`FSN_NIGHTLY_STAGE=write` + `HYBRID_NEW_PATH=on`) against sections 2 and 3. Separately,
the 70 era_unmapped cells need a serve and guard fix (era-guard and structural_direct), not this switch.
