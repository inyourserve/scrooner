# Cash-flow and per-share port to the FSN store (2026-11-01)

For: Dhairya. Branch: `work/cashflow/fsn-store-port` (also `claude/pensive-pasteur-vzx8w5`). Built on the BS port (`work/balance-sheet/fsn-store`, which includes the IS port). Nothing was written to the database or the bucket. No migration.

## 1. In plain words

- **Done.** The cash-flow rules (CFO, buybacks, dividends paid) and the per-share rules (EPS, DPS, shares) now run on one company directory (`companies/<cik10>/`, FORMATS-v1) instead of the whole cohort.
- **Gate A passes in CI.** On real SEC rows for 11 companies whose filings the Verifier opened, the new company mode gives exactly the cells that the unchanged run 7 code gives (175 cells). It also gives the Verifier's filing-checked values.
- **Gate B is written, not run.** A manual GitHub Actions job (`cf-port-regression-gate.yml`) runs both modes over the whole bucket and compares them with run 7 (CFO 37,121 / buybacks 23,989 / dividends 24,610 publishable). This session cannot read the bucket, so **engineering runs it**.
- **One real bug found and fixed** in the Q4 DPS rule (section 5). **One open question** for you (section 6).

## 2. What changed

| file | what |
|---|---|
| `slot_records/cf_family_replay.py` | run 7 code from `work/cashflow/v2-emit` 2e061bc, rules unchanged. Split into `primary_face`, `load`, `replay_company`, `write_outputs`; new `--company <dir\|parent\|@list> <out>` mode |
| `slot_records/fsn_company_cf.py` (new) | reads one company directory into the exact shapes `cf_face_rows` / `cf_num_rows` / `cf_cal_rows` produce, with the same filters |
| `slot_records/fsn_company_pershare.py` (new) | filed EPS, DPS, shares per company; Q4 DPS on one basis; EPS never derived |
| `per_share/pershare_fsn_rules.py` (new) | `eps_fsn_scan.py`'s selection functions, moved unchanged (a test compares the code tree) |
| `corporate_actions/share_basis.py` | the split-signal rule made a pure function (`split_signal_dates_from_rows`); the DB loader calls it; 171 existing tests pass |
| `slot_records/fsn_sec_fixture.py`, `fsn_company_fixture_cf.py` (new) | cut test fixtures straight from the SEC FSN zips (one request per set, rows copied, never edited) |
| `slot_records/cf_port_gate.py` (new) | compares two runs cell by cell, and verdict counts against run 7's summaries |
| `concept_rules/cf.jsonl`, `per_share.jsonl` | +9 seed rows (below); the existing capex, D&A and EPS rows untouched |
| `concept_rules/cf_pershare_not_extracted.md` | 36 rules that stay in the readers (label regexes, holds, the DPS rule) |
| `.github/workflows/cf-port-regression-gate.yml` (new) | gate B, manual, read-only, no DB connection, refuses to run in the 18:00–21:30 UTC window |

**Seed rows** (exported from the code by `export_concept_rule_seeds_cf_pershare.py`, source commit 4623e25):

| concept | tag | priority |
|---|---|---|
| cfo_resolved | NetCashProvidedByUsedInOperatingActivities | 10 |
| cfo_resolved | NetCashProvidedByUsedInOperatingActivitiesContinuingOperations | 20 (only valid with no discontinued line; the reader enforces it) |
| share_buybacks_resolved | PaymentsForRepurchaseOfCommonStock | 10 |
| dividends_paid_resolved | PaymentsOfDividends / PaymentsOfDividendsCommonStock / PaymentsOfOrdinaryDividends | 10–12 |
| dividends_per_share_resolved | CommonStockDividendsPerShareDeclared / …CashPaid | 10 / 20 |
| shares_outstanding_resolved | CommonStockSharesOutstanding | 10 |

The excluded buyback tags (tax withholding, preferred, NCI) are **not** seed rows. A `demote` row can only withdraw a std_tag match, and none of those tags is one, so the reader classes them instead.

## 3. Rules in force

- **EPS is never derived.** Only filed copies are used; a quarter with no filed 3-month copy gets no cell, and the calendar blanks it.
- **Q4 DPS = FY − 9M on one share basis only.** Both inputs must come from the same tag. No split signal may fall between the two filings (share_basis's own rule). A negative Q4 is never shown.
- **"Dividends and dividend equivalents" counts as common dividends paid** (founder ruling 2026-11-01). AAPL FY2024 = 15,234M.
- Instants (shares) are never derived. Copies that disagree by more than 0.005 are hidden.

## 4. Gate A results (CI: `pipeline/tests/unit/test_cf_pershare_fsn_port.py`, 16 tests)

Fixtures: 11 companies, 14 FSN sets, 1.2 MB (`pipeline/tests/fixtures/fsn_company_cf`). Run 7 baseline on the same rows: `results/cf_port_gate_2026-11-01/`.

| check | result |
|---|---|
| company mode = run 7 code, cell for cell | identical: CFO 67, buybacks 51, dividends 57 cells |
| refactored cohort mode = run 7 code | byte-identical |
| EMR FY2024 buybacks (VERIFY-BUYBACKS-R2) | 435M, AspenTech line excluded as subsidiary |
| GPN FY2022 buybacks | 2,921,307K |
| ROST FY2019 / LDOS FY2020 (VERIFY-BUYBACKS-RUN3) | held: multiple repurchase lines / combined line |
| SO FY2024, GM Q1 2016 CFO (VERIFY-CFO-BUYBACKS-RUN2) | 9,788M / −164M |
| CFG Q4 2017, OGE Q4 2018 DPS (VERIFY-SPLIT-RELEASE-2) | 0.18 / 0.365, derived |
| Charter Q4 2015, News Corp Q4 FY2015 basic EPS (VERIFY-EPS-FAMILY-C-V3) | −1.09 / −0.65, filed in the 10-K quarterly note |
| EPS never derived | no derived EPS cell anywhere; CFG has FY and 9M EPS but no Q4 cell |
| split between the DPS inputs (synthetic, temporary copy only) | hidden `dps_inputs_not_on_one_basis` |

**Mutation checks** (each test fails without its rule): the dividend-equivalents exemption, the split block, mixing tags in Q4 DPS, deriving EPS, and the ROST multiple-lines hold. **Not covered:** the `inpth` (parenthetical) filter. The fixtures happen to hold no parenthetical cash-flow rows, so removing that filter is not caught.

Full suite locally: 2,160 passed, 120 skipped (DB tests run in CI against Postgres 16). ruff, mypy, compileall, check_docs and check_secrets are clean.

CI run 41317042767 (2c8f3ac):
- Green: Python tests (with Postgres 16), migrations/docs/secrets, frontend build.
- Red: the advisory job's `npm audit`. A critical advisory against `next` 16.0–16.4 (GHSA-2464-fhr4-w9xw) appeared between main's green run 41316648185 and this one. Main pins the same `next` 16.4.0, so main's next run fails the same step. This change does not touch the frontend; the fix is a `next` bump (16.4.3) by the frontend owner.

## 5. Bug found by the gate (fixed)

CFG's FY2017 10-K (0000759944-18-000016) tags `CommonStockDividendsPerShareDeclared` = 0.18 on a **12-month** context; it is really the Q4 declared amount. `CashPaid` FY = 0.64 sits beside it. The first version chose the tag per key, so it subtracted the CashPaid 9M (0.46) from the Declared FY (0.18) and got **−0.28**. Fix: both inputs come from one tag series, and a negative Q4 is hidden. Result: 0.64 − 0.46 = 0.18, the Verifier's value.

## 6. Open question for you

That same CFG FY2017 cell **itself** shows 0.18 (Declared, the mapper's first-priority tag) where the cash paid for the year is 0.64. This is the lane's existing tag order (`CONCEPT_MAPPINGS`: Declared first), so I did not change it. A guard such as "a FY DPS below its own 9M is impossible: hold it" would catch it. Is that a rule you want, or a Verifier question first?

## 7. Gate B: how engineering runs it

Actions → "Cash-flow port regression gate vs run 7" → run on `work/cashflow/fsn-store-port`. Optional input `run7_cells`: a bucket folder holding run 7's `*_cells.jsonl.gz` (they are only on the dev Mac scratchpad today). Upload them there to get the per-cell check too.

It fails unless both of these hold, and also the third when `run7_cells` is given:
1. Company mode equals cohort mode, cell for cell.
2. The verdict counts equal `results/cf_run7/*_summary.json`.
3. The company-mode cells equal run 7's own cell files.

Things to watch on real shards:
- The shard keeps 10-KT/A and 10-QT/A, which `cf_face_rows` did not; the reader filters them out.
- A filing printed in two FSN sets: `cf_face_rows` kept the first set only, while the shard has rows from both.
- Runner disk: num is streamed one period at a time.

The workflow also runs the per-share reader over the cohort, as a report only.

## 8. Not done

- The `fsn.line_map` detector hook (`mapping.map_filing(detectors=…)`) for these families. The readers produce cells from company directories, as the IS and BS ports do.
- No Verifier draw exists for dividends paid, so its baseline is "equals run 7", not "Verifier-passed".
- The CFO investing/financing totals and the calendar cell emitter (scrooner-28 handoff, next steps 1–2).
