# Pinnacle's Synovus 8-K and the periodic-form rule (W3): root cause, dry-run, release plan, 2026-10-30

Prepared by Dhairya (scrooner-0f). Evidence levels marked per section. Flags OFF everywhere; nothing applied.

## 1. The live wrong value (FILING-CHECKED by Verifier 2, VERIFY-RETIREMENT-B14-2026-10-26.md)
Pinnacle Financial Partners (company_id 4938, CIK 0002082866) shows FY2025 net income 791,980K and FY2024 482,460K. Its 10-K 0002082866-26-000018 prints 641,865K and 475,056K. The shown figures are Synovus Financial's, carried in Pinnacle's holdco 8-K 0002082866-26-000020 (Items 8.01/9.01, filed 2026-03-02, the same day as the 10-K).

## 2. How it got there (DATA-INFERRED from core.fact, checked live 2026-10-30)
- The 8-K holds 769 facts under company 4938; 410 are authoritative today.
- The 8-K shares 15 keys (tag, unit, period) with the 10-K: all 15 disagree (net income, tax, CFO/CFI/CFF for FY2023-FY2025).
- 350 of the 8-K's 359 non-authoritative facts sit in conflict groups where the 10-K's copy is also non-authoritative: Stage 2e saw two values and demoted both.
- Stage 2e-b ("latest filing wins", normalizer/conflict_latest_filed.py) lists 8-K among the eligible winners. Same filing date, so the tie went to the higher fact id: the 8-K copy. analytics.canonical_fact net_income FY2025 points at fact 73889302 (8-K).
- The remaining 395 authoritative 8-K facts are singletons (no 10-K copy for that key), so they are shown as Pinnacle's own.
Lesson: a fill rule that lets an 8-K win cannot tell a recast of the registrant's own statements from another entity's statements. Only the form rule can.

## 3. The root fix already written: source.periodic_form_only@1 (RF-03, W3)
Branch work/data-engineer/lane1-identity-fixes-v2 carries it in two commits that cherry-pick cleanly onto origin/main c5b6997 (no conflicts; 52 unit tests pass, 2 skipped for want of a test database):
- a60a44c: Stage 2e ignores non-periodic filings (common/periodic_forms.py is the one list); a group that shrinks to one periodic copy promotes it; repair list mapper/periodic_source_repair.py for stored canonical cells sourced from non-periodic filings; population dry-run script scripts/w3_population_dryrun.py.
- 4bf20f1: Stage 2e-b no longer lets 8-K, 8-K/A, 6-K win; retire list for stored winners; flag-OFF golden file.
This branch (work/dhairya/w3-periodic-form-only) is exactly origin/main + those two commits + this note.

## 4. Pinnacle-only dry-run (scripts/w3_population_dryrun.py --ciks 0002082866; DATA-INFERRED)
| class | groups | forms |
|---|---|---|
| conflict_cleared (10-K copy becomes the one authoritative copy) | 318 | 8-K |
| authority_value_changed (8-K value replaced by the 10-K value) | 15 | 8-K: NetIncomeLoss, IncomeTaxExpenseBenefit, CFO, CFI, CFF x FY2023-25 |
| value_to_none (only non-periodic copies existed; cell goes blank) | 432 | 8-K 395, DEF 14A 37 |
| non_periodic_demoted_same_value | 6 | 8-K |
| periodic_conflict_remains | 32 | 8-K |
Stored canonical cells to purge and refill: 76 (70 sourced from the 8-K, 6 from DEF 14A), all class all_sources_non_periodic. Stage 2e-b winners from now-ineligible forms: 15, all value_changed.

## 5. Cohort dry-run (1,000 companies of cohort v1.1; DATA-INFERRED from stored is_authoritative, no filing opened; second full run, 0 errors, 2026-10-31)
Package: data-team/strategy/team/w3_cohort_dryrun_2026-10-31/ (summary.json, manifest.json, changes_by_class.csv.gz = every changed group, canonical_non_periodic_cells.csv, named_cases.csv, ban_winners_sample.csv = all Stage 2e-b winners, verifier_draw.csv). 1,000 companies, 18,845,753 facts read. Live data moved a little between the first run and this one; this one is the reference.

Stage 2e change classes (groups = company/concept/unit/period keys, "cells" in the verifier sense):
| class | groups | companies | non-periodic forms behind it |
|---|---|---|---|
| authority_value_changed | 804 | 185 | 8-K 342, DEF 14A 453, 8-K/A 4, DEFR14A 5 |
| value_to_none | 21,145 | 562 | DEF 14A 12,224, 8-K 8,065, 424B5 646, 8-K/A 184, DEFM14A 35, DEFR14A 62 |
| conflict_cleared | 6,676 | 157 | 8-K 6,470, 8-K/A 155, DEF 14A 75 |
| non_periodic_demoted_same_value | 109,168 | 508 | mostly 8-K 106,066 |
| periodic_conflict_remains | 18,821 | 196 | (periodic copies still disagree) |
| other | 145 | 21 | 424B5, DEF 14A, 8-K |
| matching_copies_resolved (WO-23, separate rule) | 32,288 | 652 | n/a |
authority_value_changed top tags: NetIncomeLoss 489, OperatingIncomeLoss 89, Revenues 46, GrossProfit 44, IncomeTaxExpenseBenefit 32, pre-tax income 28, CFO 25, CFI 21, CFF 18, RevenueFromContractWithCustomer 12.
value_to_none: about 12,400 of the 21,145 are DEF 14A pay-versus-performance and offering-fee tags (PeoTotalCompAmt, TotalShareholderRtnAmt, CoSelectedMeasureAmt, ...) that no product concept reads; 8,713 are other tags (NetIncomeLoss 468, OperatingIncome 396, IncomeTax 225, CFO 189, GrossProfit 166, ...). Whether any of those 8,713 blanks hides a value that a periodic filing carries is for the Verifier draw.

Stored canonical cells that need the purge (find_non_periodic_sourced_cells): 6,508 cells in 316 companies. all_sources_non_periodic 5,392, mixed_sources 1,116. By bad form: 8-K 5,633, DEF 14A 774, 8-K/A 95, DEFR14A 15. Top concepts (base + _resolved): net_income 325+796, revenue 226+392, operating_income 246+296, diluted_eps 47+241, basic_eps 48+234, gross_profit 97+203, operating_expenses_resolved 203, income_tax 129+178, CFO 132+143.

Stage 2e-b ineligible winners: 776 stored winners from now-ineligible forms: value_changed 440, value_same 311, value_to_blank 25 (by form: 8-K and 8-K/A 734, DEF 14A 37, DEFR14A 5; the 25 blanks are 20 DEF 14A + 5 DEFR14A).

Named cases (net income FY cells, named_cases.csv):
- Pinnacle 0002082866: FY2025 791,980K -> 641,865K; FY2024 482,460K -> 475,056K; FY2023 543,705K -> 562,152K (all authority_value_changed, 8-K 0002082866-26-000020 replaced by the 10-K). 10-K prints 641,865K and 475,056K (FILING-CHECKED earlier by Verifier 2). The FY2023 value is a prior-year column in the 10-K and is not yet filing-checked.
- JPM 0000019617: FY2021-FY2025 net income had no authoritative copy (class conflict_cleared, DEF 14A copy competing). After: one copy each, 48,334M / 37,676M / 49,552M / 58,471M / 57,048M.

Verifier draw (seed 20261031, cells are the unit): verifier_draw.csv, 100 rows = 40 authority_value_changed, 30 value_to_none on financial tags + 10 on pay-versus-performance/fee tags, 20 Stage 2e-b winners (11 value_changed, 8 value_same, 1 value_to_blank, random over the 776 so class mix follows the population).

## 6. Release plan (every step behind the flag; founder's own words for every production write)
1. Release Manager lands this branch on main (flag OFF: byte-for-byte legacy behaviour; golden test proves it).
2. Verifier 2 draws from the cohort dry-run: authority_value_changed (value must equal the 10-K/10-Q face), value_to_none (confirm no periodic copy carries the line), and the Stage 2e-b retire list.
3. Founder types, in the engineering session: dedupe + conflict fill rerun for the cohort with SCROONER_RULES_ENABLED=source.periodic_form_only@1; then periodic_source_repair.purge_cells with its backup file; then resolve-facts, passthrough, conflict fill, derive stages for the touched companies.
4. Certify dry-run rerun; the delta goes on the task board. Rollback: restore is_authoritative from the dry-run before-image and the canonical backup.
Not in scope: the other 4,200 companies (founder scope order 2026-10-23).
