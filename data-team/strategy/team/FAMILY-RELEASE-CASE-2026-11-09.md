# Family release case: balance sheet, total debt, capex, D&A for the FSN write (2026-11-09)

For the release approver, via Dhairya (manager session `session_01GLmSDyzegqZw4JqC91z7XH`). Written by the family-release-prep cloud session. Repo read at origin/main 787cc66. **Nothing was written to production.** DB reads were read-only with `statement_timeout` 15s. No SEC requests.

The question: `.github/workflows/pipeline-fsn-write.yml` writes only income-statement, cash-flow and per-share data points. Which held families can be added to its `data_points`?

## 0. Verdicts

| Family | data_points name(s) | Values | Verdict |
|---|---|---|---|
| Capex | `capex_resolved` | Verifier-passed | **Ready for the approver.** Proposed on the branch. Costs done companies (see §1). |
| D&A | `depreciation_and_amortization_resolved` | Verifier-passed | **Ready for the approver**, with one defect: a combined line becomes a reasonless gap, not a `combined` reason. Proposed on the branch. |
| Total assets, equity, current assets/liabilities, cash | `total_assets_resolved`, `stockholders_equity_resolved`, `current_assets_resolved`, `current_liabilities_resolved`, `cash_and_equivalents_resolved` | Plausibly right, **not Verifier-drawn on store values** | **Not yet.** Needs one Verifier draw of store-selected BS cells and a ruling on the vintage policy (P-6). |
| Total liabilities | `total_liabilities_resolved` | Seed rule defect | **Not ready.** A seed rule maps custom lines as total liabilities, giving false conflict blanks in 4,479 filings (§3). PR #6 (derived TL) is not on main. |
| Total debt | `total_debt_resolved` | Seed rule defect | **Not ready (blocked on the build, not on approval).** The store maps any custom current-liability line as total debt: 7,335 lines in 5,441 filings at 236 companies, in `fsn.*` today. It never sums lines, has no CommercialPaper or note finance-lease path, and leaves every standard debt tag unmapped (§2). |

None of these is an accounting call I am making. The rulings the approver or founder must give are in §5.

## 1. The constraint that matters more than any family: the done gate

`pilot.done_gate` (`pipeline/src/scrooner_pipeline/fsn_store/pilot.py:510`, criterion 4) fails a company when it has **any** reasonless gap key in **any** listed data point. The write step then writes **no** family for that company. So adding a family with held or unmapped keys does more than leave that family's cells out: the company's income-statement and cash-flow cells are not written either.

Measured on the latest full cohort dry run with artifacts, run 41708119011 (2026-11-03, main bd05470: capex/D&A detector and its gate fix included; artifact `fsn-cohort`, `gaps.csv`, 960 companies). Count = companies with zero gap keys in the listed data points (criterion 4 only; criteria 1, 2 and 5 can only lower it):

| data_points | companies passing criterion 4 |
|---|---|
| **today's default (15 IS/CF/per-share names)** | **13 of 960** |
| + capex | 9 |
| + D&A | 7 |
| + capex + D&A (the branch) | 5 |
| + total assets, equity, cash | 7 |
| + five BS std-tag points | 5 |
| + total liabilities | 10 |
| + total debt | 0 |

**Today's default already passes only 13 of 960 companies.** Companies blocked per data point, from the same file: share buybacks 876, dividends paid 817, CFO 668, revenue 633, interest expense 614, basic EPS 588, net income 573. The largest causes are `dividends_paid no_mapped_line` (12,699 keys) and `share_buybacks quarter_not_printed_or_derivable` (11,948). This run predates PR #4 (CF gaps: FX identity tags, buyback/dividend detector, absent-line reasons), which should lower these numbers; it has not been re-measured. **Re-run the cohort dry run on main + PR #4 + PR #6 before any write, and read this table again from its `gaps.csv`.**

Consequence for this case: a family can be right and still not be worth listing yet. Whether criterion 4 should apply per family (a company writes the families it completes) or per company (design §5, the founder's 2026-11-01 decision, doc 02) is a founder decision. I do not change it.

## 2. Total debt: not ready

### Evidence on main
- Lane (slot-records, not the store): debt v3 14/14 right (VERIFY-DEBT-V3-2026-11-04: MSFT, HD, KO, AAPL, META, note finance leases included); AMZN release 1 3/3 (VERIFY-DEBT-RELEASE1-AMZN-2026-11-04); debt port META 2022-12-31 corrected to **10,610** = 9,923 + 687 (VERIFY-DEBT-PORT-2026-11-01 §2). The port's new values were never published (same file: "partly BLOCKED"), and 7 of 7 equity-block guard reclasses were wrong.
- Founder ruling 2026-11-04 item 5 (doc 02): total debt includes finance leases disclosed in the notes.
- FSN expert (branch docs/fsn-expert 8d36808, `data-team/fsn/companies/MSFT.md` §6.7 and §7, PROPOSALS P-4): production `total_debt` is wrong for MSFT FY2016 (12,904 vs face 53,461) and FY2024 (44,937; misses "Short-term debt" tagged `CommercialPaper` 6,693; face 51,630, accession 0000950170-24-087843 R4). The rule must include a face `CommercialPaper` line (13 top-100 names). MSFT finance leases are note-only.

### What the store actually does (CODE-CHECKED and DB-CHECKED)
The six `total_debt_resolved` seeds (`data-team/47-fsn-store/concept_rules/bs.jsonl`) are all `calc_position`. In `fsn_store/mapping.py`:
- Rule 2 (calc_position) runs only for **custom** tags. Standard `LongTermDebtNoncurrent`, `LongTermDebtCurrent`, `CommercialPaper`, `ShortTermBorrowings`, `FinanceLeaseLiability` stay **unmapped**.
- The seed's `slot` ("borrowing", "finance_lease", "combined") is written to the evidence but **never tested**. `bs.debt_member_parent@1` (priority 20, child_of current liabilities) therefore maps **every custom child of `LiabilitiesCurrent`** as total debt.
- `select.select_concept` takes one line per key and never sums. One line gives that line's value; two give `conflicting_values_in_filing`.

Reproduced with the real `map_filing` and the committed seeds on a synthetic classified balance sheet: the custom "Accrued compensation" line is mapped `total_debt_resolved` by `bs.debt_member_parent@1`, and the standard `LongTermDebtNoncurrent` is unmapped.

In production `fsn.line_map` (loaded by run 42561798991, 893 companies), all `total_debt_resolved` mappings come from `bs.debt_member_parent@1`: **7,335 lines, 5,441 filings, 236 companies**. **4,027 filings map exactly one line**, so the select step would serve it as total debt. 5,756 of the 7,335 lines have neither a debt-like tag nor a debt-like label. Examples of single-line filings (store value at the period end, DB-CHECKED, not opened on sec.gov):
- 0001289419-26-000013 (10-K 2025-12-31): "Accounts payable and accrued liabilities" 97.9M;
- 0000908937-26-000006 (10-K 2025-12-31): "Accounts payable and accrued expenses" 1,290M;
- 0001335258-26-000009 (10-K 2025-12-31): "Accounts payable, client accounts" 1,941.4M.

### Remaining work (builder, then Verifier)
1. Port the Verifier-passed debt lane (sum of face borrowing lines + note finance leases, `CommercialPaper`, operating leases excluded) into the store as a detector, as capex/D&A were (`fsn_store/detectors.py`), or make select sum declared members. Enforce the slot.
2. Until then, delete or disable the three `bs.debt_*@1` seeds that fire on `current_liabilities_resolved`. Re-map. Re-measure.
3. Gate: MSFT FY2014-FY2026 face series (FSN-expert §6.7: 22,645 / 35,292 / 53,461 / 86,194 / 76,240 / 72,178 / 63,327 / 58,146 / 49,781 / 47,237 / 51,630 / 43,151 / 40,294, plus note finance leases from FY2018), META 2022-12-31 = 10,610, AMZN 3/3, HD 2016-01-31 21,216 (latest print).
4. The open ruling on `latest_copy_lacks_note_finance_lease` (META 2025-12-31 and 2022-12-31; Verifier's reading: avoidable hold) must be given before the note-lease path ships.

## 3. Balance sheet

### 3a. Total liabilities: not ready
- Seed `bs.liab_cal_child@1` (priority 21) maps every custom child of `Liabilities` as `total_liabilities_resolved`. The printed total is mapped too, so the key gets two different values and becomes the defect blank `conflicting_values_in_filing` ("The filing prints two different values for this line and period"). That reason is false. Reproduced with `map_filing`. In production `fsn.line_map`: **6,469 lines in 4,479 filings**. Not every one is the winning print of a key, so the number of affected cells is lower and has not been measured. These are blanks, not wrong values, but they replace production values and break the "true reason" goal.
- On main, a company that prints no `Liabilities` line is a gap (`no_mapped_line`: 9,129 keys, 202 companies in run 41708119011). The derived route is draft PR #6 (`work/bs/derive-tl-current`): Verifier PASS 33/33 after the KMB fix, plus 19/19 Kimberly-Clark keys (VERIFY-BS-DERIVE-2026-11-08). It is not merged and its cohort dry run is still pending.
- Fix: drop `bs.liab_cal_child@1` and `@2` (a child is never the total). Merge PR #6. Re-run the cohort.

### 3b. Total assets, equity, current assets and liabilities, cash: values plausible, evidence thin
- These five use `std_tag` rules only (`Assets`; `StockholdersEquity` and four partners/members equity tags; `AssetsCurrent`; `LiabilitiesCurrent`; `CashAndCashEquivalentsAtCarryingValue`, `Cash`). They are not exposed to the calc_position defect.
- Evidence: FSN-expert MSFT comparison 195 of 196 FY/instant values agree (the exception is equity 2016-06-30, 71,997 on the FY2017 BS vs 83,090 on the FY2018 equity statement: vintage policy P-6). The cash pure-line rule is from Verifier v1 17/17 (lane). The seed provenance says "identity gate only, no own release draw located" for total assets and "Verifier evidence not located" for equity. **No Verifier draw of store-selected BS cells exists.** The 2026-10-24..26 BS reports verified the slot-record lane, not the store.
- cell_proof v4 (VERIFY-CELL-PROOF-FIRST10-V4-2026-11-04): the real DISAGREEs MSFT total assets 2016-06-30 and HD current liabilities 2016-01-31 are production values that predate a restatement. The store's latest-print rule is the intended fix. Confirm it in the draw.
- Unclassified balance sheets (banks, insurers, REITs): current assets and liabilities are gaps on main (7,112 keys each, 162 companies). The `unclassified_balance_sheet` reason is in PR #6.
- Needed: (1) a Verifier draw of about 30 store cells across the five points (seed it; include restated instants and partners-capital filers); (2) a ruling on P-6 (does a restated equity-statement opening balance outrank the BS print?); (3) PR #6 for the current items.

## 4. Capex and D&A: ready for the approver

### Evidence on main
- The store maps capex and D&A only through the ported lane detector (`fsn_store/detectors.py`, last change 482244f). It overrides every seeded calc_position line, so the loose CF seeds cannot leak. One line per concept per filing: otherwise the filing is held.
- Store gate (VERIFY-CAPEX-GATE-2026-11-03, 482244f, 11 companies): 300 keys equal the lane's Verifier-passed file, 0 `value_differs`. The 63 keys where the store differs from the lane are **23 of 23 right** in a draw (all 8 non-XOM keys plus 15 of 55 XOM keys).
- Capex lane: single-member cut YES 14/14 (VERIFY-CAPEX-R1-SINGLE-MEMBER-2026-11-04); release 1 single 10/10. Founder ruling 2026-11-04 item 3 (capex includes capitalized software, leased fleets, discontinued block, turnarounds, TI and CIP; excludes O&G property and acreage acquisitions) settles the KEY "premises, equipment, and software" hold.
- D&A lane: release 1 YES 15/15 and fills 10/10 (VERIFY-DA-RELEASE1-2026-11-02); gate D&A keys right (JPM recast 1,208, PLD, XOM).
- MSFT (FSN expert §7 and unit test `test_msft_combined_da_line_stays_combined`): capex maps `PaymentsToAcquirePropertyPlantAndEquipment`, matching production FY2014-FY2026. "Depreciation, amortization, and other" is held as `combined`, never a value.
- Production today is wrong where these replace it: INTC D&A (24 cells), HD (18), AAPL (2), GE D&A (1) and GE capex (23) (task board A8).

### Remaining defects and risks
1. **D&A combined line is a gap, not a reason.** The detector writes the `combined` line_map row with no concept id. `pilot.library` joins on the concept name, so MSFT D&A keys become `no_mapped_line` gaps, not `line_presented_combined_with_others`. Each such company fails criterion 4. Fix: carry the concept on combined rows (or emit a combined reason cell). FSN-expert MSFT §6.9 and P-3.
2. **Multi-member filings are held, so they become gaps.** Capex with 2+ member lines and D&A outside the release classes (HD in every filing) are not served. Production values there are deleted by the write and not replaced. The summed classes the Verifier passed (capex release 2a 18/18, VERIFY-CAPEX-RELEASE2A-2026-11-04) are lane outputs, not ported to the store.
3. **Understatement risk on single-member capex.** The lane can miss a second PP&E line it does not recognize: AEE FY2021 omits "Wind generation expenditures" 525M (fills v19, VERIFY-CAPEX-R1-FINAL-FILLS-V19). Not measured on store cells.
4. **Gate scope.** The store-vs-lane gate covered 11 companies, not the cohort. Under the operating model (load, `cell_proof`, Verifier draw after; a failed draw means fix and reload), draw capex and D&A store cells after the write.

## 5. Decisions needed (not mine)

| # | Decision | Who |
|---|---|---|
| 1 | Clear capex and D&A for the write, accepting the done-set cost in §1 | release approver |
| 2 | Done gate criterion 4 per company (design §5, today) or per family | founder |
| 3 | `latest_copy_lacks_note_finance_lease`: value from the 10-K note (10,610 for META 2022-12-31) or hold | founder / Dhairya (Verifier reading: avoidable hold) |
| 4 | Vintage policy P-6: restated equity-statement instant vs BS print (MSFT 2016-06-30: 83,090 vs 71,997) | founder / Standardization Lead |
| 5 | DVN 2017-12-31 debt basis change (EnLink recast to discontinued) under rule 3 | Standardization Lead (VERIFY-DEBT-PORT §1) |
| 6 | VLO "Acquisition of undivided interests" excluded from capex beyond the O&G wording | Dhairya (VERIFY-CAPEX-RELEASE2A note) |

## 6. Also found

- **`shares_outstanding_resolved` is never emitted, so it is removed from the default** (update 2026-11-09, Dhairya's job 4). There are two causes, both CODE-CHECKED and DB-CHECKED:
  1. The only seed is `us-gaap:CommonStockSharesOutstanding` on the BS. At most filers that line is the balance-sheet parenthetical, which `mapping.map_filing` excludes (`inpth`). MSFT, company 140 and company 7 have 51 of 51 such lines excluded. The line is mapped only where it is a face line: 781 filings at 104 companies in production `fsn.line_map`.
  2. Where it is mapped, `pilot.report_company` selects with unit USD (only names containing "eps" are per-share), so every `shares` print is filtered out.

  The 960-company dry run's reports mention the point 0 times. Serving it needs a definition, not a code tweak: which count (BS-date shares from the parenthetical vs the cover-page `dei:EntityCommonStockSharesOutstanding`, mapper priority 2 per `cf_pershare_not_extracted.md`), how the split re-base (B2) applies, and whether parenthetical lines may map. That is for the founder or the Standardization Lead. The guard test now fails if the name is listed again.
- **Dividends per share: split-basis scope (report only, Dhairya's job 5).**
  - `pilot.report_company` selects DPS with unit `USD` and `derive=True`, so the store derives DPS quarters: route (a) note quarter, route (b) YTD difference under SAME_BASIS. Ruling 2026-11-04 item 2 allows FY − 9M for DPS "on the same share basis".
  - Nothing checks the share basis directly. The only guard is indirect: a split usually makes a later filing re-print earlier DPS split-adjusted. That re-print is a break, and a break blocks the difference across it (`mixed_vintage_inputs`).
  - The guard fails when no later filing re-prints an earlier DPS period between the two YTD filings.
  - Scope: 131 of the loaded companies have 159 splits since 2014 (`analytics.company_stock_split` joined to `fsn.company_load`, read 2026-11-09). How many derived DPS cells span a split was not measured, because DPS is outside the pilot template, so the dry run has no per-point counts.
  - Proposal for the period engineer: refuse a derived DPS quarter when a split with an effective date inside (YTD_(n−1) end, YTD_n end] exists, reason `split_between_inputs`. Also write DPS cells with unit `USD/shares` (today `to_row` labels them `USD`).

## 7. Proposed change (branch `work/release/family-release-case-2026-11-09`)

- The workflow's default `data_points` adds `capex_resolved,depreciation_and_amortization_resolved` and drops `shares_outstanding_resolved` (never emitted, §6). The header comment explains why debt and BS stay out and how the done-gate coupling works.
- New `pipeline/tests/unit/test_fsn_write_data_points.py`:
  - every default name has a seed concept rule;
  - `total_debt_resolved` and `total_liabilities_resolved` stay out while the seed defect stands;
  - capex and D&A are listed;
  - no never-emitted name is listed (`shares_outstanding_resolved`).

  Mutation-checked: it fails on the old default (capex/D&A missing) and when `total_debt_resolved` or an unseeded name is added.
- Follow-up branches (Dhairya's jobs, 2026-11-09):
  - D&A combined reason: `work/fsn/da-combined-reason`;
  - total-liabilities seeds dropped: `work/fsn/drop-liab-child-seeds`, lands after PR #6;
  - debt port: in progress.
- **Recommendation:** merge only with the approver's words. Given §1, dispatch with capex and D&A only after the D&A combined-reason fix (§4.1) and a fresh cohort dry run show the done set does not shrink unacceptably. Until then, dispatch with an explicit `data_points` input.
