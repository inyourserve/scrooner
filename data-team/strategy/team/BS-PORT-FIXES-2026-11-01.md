# Balance-sheet port: fixes for the independent review of b0ac12d (2026-11-01)

For Dhairya. Branch `work/balance-sheet/fsn-port-fixes` (from `main` 485e38d). It answers the review relayed by the HD pilot proof session, which found b0ac12d not fit for the pilot. All four points are fixed, and every difference the gate shows is explained in section 3. Nothing here writes to the database.

## 1. The four review points

| # | review finding | fix | proof |
|---|---|---|---|
| 1 | `bs_port_gate.sh` cannot fail: Gate A prints DIFFERENT and goes on, and `bs_port_compare.py` always exits 0 (its own run: 18 C diffs, 79 D diffs, 10 missing records, exit 0). The shared helpers and `bs_assemble.py` are not in Gate A. | **The compare step fails closed.** Every difference becomes a row `{gate, key, class, detail}`. Exit 1 on any difference. With `EXPECTED=<file>` it passes only if the observed set equals that pinned set **exactly**: a new difference fails, and a pinned one that no longer occurs fails. Generic classes cannot be pinned (`value_differs`, `*_unexplained`, `file_differs`, `only_in_*`, `cell_missing`, ...). **Gate A** now also runs the old shared helpers (`common`, `build_debt_slots`, `face_admission`, `taxonomy_attrs` at c0925d1) and `bs_assemble.py` in cohort mode on the boundary filings' `_cal.xml`. Any failed step fails the gate (`set -euo pipefail`). | `test_gate_fails_closed`: identical outputs pass; a 195-vs-155 value fails strictly; a pin of a generic class is refused. The test fails if the strict exit is mutated away. Manual runs: one cell +1 → FAIL; one pin removed → FAIL; one Gate A file changed → FAIL. |
| 2 | `replay_debt_fsn.py:210-233` double-counts finance leases when the face has `FinanceLeaseLiabilityNoncurrent` as a member and the note prints the `FinanceLeaseLiability` total (195 instead of 155). | The note adds only what no member carries: total minus the face lease members, or else only the parts that are not members. A note total *below* the face members holds as `note_finance_lease_below_face_members` (it never subtracts). | `test_note_finance_lease_total_is_not_added_twice` (155, note adds 15). It fails with the old line. |
| 3 | `:75` picks the as-first-filed print; design §4 says the latest accepted print wins. | The winner is the latest `accepted` filing that prints the instant **on its balance-sheet face**. A face column needs the statement's own closing total (L&E) valued at that date; Assets alone also matches a later 10-K's segment note. The record applied is the one covering the chosen filing's own period, because its face names the members. Design §4 also says the latest copy is never swapped for an older one. So when an earlier copy prints a finance-lease figure that the latest copy lacks, the cell is blank `latest_copy_lacks_note_finance_lease`, rather than silently dropping the leases (AAPL 2025-09-30 would lose 1,230M). | `test_latest_accepted_print_wins_and_cells_start_2015`. It fails with the old rank. |
| 4 | `:73` window: values are stored from 2014, but cells are 2015+ (invariant I11). | `CELL_FROM = 20150101` (I11, `data-team/34-TOP1000-CERTIFICATION-PROGRAM.md:55`). 2014 values are still read, e.g. as restatement witnesses. | Same test: 2013/2014 instants give no cell. It fails with 2014. |

Small extra fix: `common.SecClient` hard-coded the dev Mac's `/private/tmp` for its disk floor. It now uses that path when present, else the system temp dir (needed to fetch the `_cal.xml` files here).

## 2. Gate result (29 companies, 59 FSN sets, real shards; `results/bs_port_gate_2026-11-01/`)

- **Strict:** 858 differences → exit 1, as designed.
- **Pinned:** `EXPECTED=results/bs_port_gate_2026-11-01/expected_diffs.json` → 858 pinned, 0 unexpected, 0 vanished → exit 0. Each pinned row carries its class and reason.

**Gate A:** old code (lane scripts **and** shared helpers at c0925d1) vs ported code. All 9 files are byte-identical, now including `bs_records.jsonl` from `bs_assemble` on `_cal.xml`. So the refactor, the `face_tags` default and the helper changes are inert. The debt replay differs only through the review fixes. An ablation run isolates the selection change (`REPLAY_DEBT_ABLATE=first_filed`; gate-only, never set in production paths).

## 3. Every difference, explained

**A1. Old replay vs ported replay with the old selection: the effect of fixes 2 and 4 and the face test (135 cells)**

| class | n | what |
|---|---|---|
| `cell_before_2015_window` | 109 | fix 4 (I11) |
| `note_finance_lease_overlap_removed` | 13 | **fix 2 removes real wrong values**: WMT year-ends 2021–2026 were 4.3–6.8B too high (e.g. 2026-01-31 58,284M → 51,523M; the face finance-lease members were added again from the note total); NVDA 2015–2017, 1–14M |
| `note_fields_differ_same_value` | 9 | WMT held cells; only the note-lease flag text changes |
| `old_cell_was_not_a_face_column` | 2 | KKR 2023-03-31 / 06-30: the old cell was a 2024 10-Q's segment-note Assets. FSN has only dimensional totals for KKR's own 10-Q, so no face column exists; the store gives a reasoned blank |
| `covered_by_the_filing_s_own_period_record` | 1 | DIS 2018-09-30 (new CIK): the record of the filing's own period now covers it |
| `members_differ_same_value` | 1 | KKR, held either way |

**A2. Selection change alone: first-filed → latest accepted (358 cells)**

| class | n | what |
|---|---|---|
| `latest_accepted_print_same_value` | 268 | same value from the later copy |
| `latest_accepted_print_restated` | 32 | the later filing prints a different value for a fact the replay reads (restated or reclassified comparatives) |
| `latest_accepted_print_verdict_differs` | 44 | the later copy's face decides. 19 are the new `latest_copy_lacks_note_finance_lease` blank (earlier copy has the lease, latest does not); others release or hold under the later face (ET 7, META 7, GOOG 5, WMT 5, DIS 3, NI 3, ...) |
| `latest_accepted_print_same_total_borrowings_split_differs` | 9 | same total debt; only the borrowings-only split moves |
| `latest_accepted_print_note_lease_differs` | 3 | e.g. GOOG 2024-12-31: the latest copy carries the 1,677M note lease the first copy lacked |
| `latest_accepted_print_covering_record_differs` | 2 | T 2022-12-31, NVDA 2017-01-31: the later copy is presented under a later record era |

**B. Company mode vs cohort mode:** 1 difference. DVN 0000950170-24-092424: its FSN cal has no balance-sheet group, so company mode borrows the company's cal, while its `_cal.xml` has its own. This is the known FSN gap (BS-PORT 4.3); the record is face-sum, so the identity tie still decides publication.

**C. vs the Verifier-passed `report_v4.json` (460 cells):** 228 identical. The rest:

| class | n |
|---|---|
| `covering_record_differs_same_value` | 103 |
| `latest_accepted_print_same_value` | 73 |
| `latest_accepted_print_restated` | 13 |
| `latest_accepted_print_verdict_differs` (9 `latest_copy_lacks_note_finance_lease`: META 7, AAPL 1, NVDA 1) | 18 |
| `held_securities_loaned_candidate` (MSFT 9, GOOG 4: pre-existing, BS-PORT 5.1, fails safe) | 13 |
| `note_finance_lease_overlap_removed` (NVDA: **report_v4 itself had the double count**) | 4 |
| `latest_accepted_print_note_lease_differs` | 4 |
| `latest_accepted_print_same_total_borrowings_split_differs` | 4 |

**D. vs the Verifier-passed `bs_records_v3.jsonl` (338 records):** 249 identical. The rest:

| class | n | cause |
|---|---|---|
| `equity_block_guard_reclassed_a_v3_member` (+1 with era span) | 70 | BS-PORT 5.2: the post-v3 UPS guard; identical in `main`'s code (Gate A) |
| `record_before_v3_window` | 29 | FSN 2014q1 vs v3 2015q1 |
| `same_era_starts_earlier_in_fsn` | 10 | same cause |
| `same_era_starts_earlier_in_fsn_port_side` | 5 | port-side twin of the line above |
| `record_split_by_equity_block_guard` | 6 | 5.2 |
| `era_span_only` | 4 | FSN vs FSDS face rows (4.1) |
| `era_split_inside_a_v3_era` | 3 | port-side twin of the line above |
| `equity_parent_tag_none_vs_default` | 3 | same line read (4.2) |
| `fsn_cal_has_no_bs_group_borrowed` | 1 | DVN (4.3) |
| `fsn_face_has_extra_liability_line` | 1 | ET (4.3) |

## 4. What the Verifier should look at

1. **WMT and NVDA debt values the old code produced were double-counted.** NVDA is inside the Verifier-passed report_v4. The corrected values need a draw before any release.
2. **New blank `latest_copy_lacks_note_finance_lease`** (19 cells here): confirm that is the right reading of design §4 for a total that needs a note fact.
3. Still open, unchanged, from BS-PORT: 5.1 securities-loaned holds and 5.2 the equity-block guard at utilities. Both fail safe. Each fix changes a lane rule, so each needs its own draw.

## 5. Rerun

The cal dir is filled by `fetch_boundary_cal.py`: sec.gov only, ≤4 requests/s, 993 requests for these 29 companies.

```bash
EXPECTED=pipeline/scripts/slot_records/results/bs_port_gate_2026-11-01/expected_diffs.json \
  bash pipeline/scripts/slot_records/bs_port_gate.sh <period_dir> <companies_dir> <cohort.csv> <work_dir> <cal_dir>
```

Next in this session: the capex/D&A/debt detectors (`CAPEX-DA-DEBT-PORT-2026-11-01.md`).
