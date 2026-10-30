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

## 5. Cohort dry-run (1,000 companies of cohort v1.1)
PENDING: filled from w3_cohort/summary.json when the run completes.

## 6. Release plan (every step behind the flag; founder's own words for every production write)
1. Release Manager lands this branch on main (flag OFF: byte-for-byte legacy behaviour; golden test proves it).
2. Verifier 2 draws from the cohort dry-run: authority_value_changed (value must equal the 10-K/10-Q face), value_to_none (confirm no periodic copy carries the line), and the Stage 2e-b retire list.
3. Founder types, in the engineering session: dedupe + conflict fill rerun for the cohort with SCROONER_RULES_ENABLED=source.periodic_form_only@1; then periodic_source_repair.purge_cells with its backup file; then resolve-facts, passthrough, conflict fill, derive stages for the touched companies.
4. Certify dry-run rerun; the delta goes on the task board. Rollback: restore is_authoritative from the dry-run before-image and the canonical backup.
Not in scope: the other 4,200 companies (founder scope order 2026-10-23).
