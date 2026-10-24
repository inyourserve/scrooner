# Evidence for the root-cause pass: total_debt guards dry-run (Data Engineer, 2026-10-21; held uncommitted under the gate)

Code (held, not committed): mapper/concept_fallback.py (`evaluate_total_debt`, guards r1_containment, r5_zero, r5_floor, R4 preference filter), sanity/tag_investigator.py (12-line filter), tests/unit/test_total_debt_guards.py (33 tests, 17/17 mutants killed, full suite 1,295 passed). Dry-run: read-only, top 1000 (1,014 ids), every instant since 2015-01-01 = 36,995 company-instants. Evidence DATA-INFERRED (arithmetic identities among the company's own filed tags; no filing opened). Raw files: scratchpad tdg/ (verifier_changed_ids.json, changed_rows.json, dryrun_rows.jsonl, worse_candidates.json).

## What the guards change
1,257 instants (3.4%) at 201 of 974 companies: r1_containment 317 (72 companies), r5_floor to blank 664 + 16 combined (122), r5_zero 68 (37), R4 preference 192 (5). By era 354 / 348 / 555 (2015-17 / 2018-20 / 2021+). Correct in the clear cases: WFC 25,168M -> 207,307M; MAR 23M -> 16,915M; NOW 0 -> 1,486M; TSCO 150M -> 1,765M; DTE, LITE, TAP, SUN. Among the 20 largest companies only WMT changes (to blank). No new negatives; 5 old negatives (DD 2019-20) become positive.

## Where the patch approach itself produces risk (the argument for a mechanism, not guards)
1. The floor guard blanks a company's own stated total in 61 rows (WMT, HIG 9 yrs, WY 9, SCHW, BIIB, SNEX, UMBF, WEX, JLL, RJF); 40 of them differ by under 5%, which looks like face vs carrying, not an error. A fixed 2% tolerance cannot tell the cases apart.
2. The fallback can overcount: CVX 2016-12-31 43,330M -> 55,033M because DebtCurrent (19,840M) exceeds ShortTermBorrowings 10,840M + LongTermDebtCurrent 6,253M; PFE 2020, MMM 2024-03-31, COR 2018-19, PPG and DD 2020 (12 instants) unverified.
3. Falling to a path that omits a filed lease-inclusive tag: DPZ 2024-12-29 14.7M -> 3,825.8M while DebtAndCapitalLeaseObligations is 4,975M (still understated); LAD 2016.
4. Banks: the floor blanks UMBF 44 instants and EWBC 38 (honest 'undecidable', but it widens visible blanks until a bank template exists).
5. Not touched by any guard: face-value vs carrying at AAPL, GOOG, AMZN (data-team/35), ADP (0.6% over), the 160 'instrument tags on top of a matching total' cases.
6. Tolerance choices (2%) and path precedence were set by hand; ADP is missed by 2% but was in the Tag Mapper's list of 18.

## Reading for the strategy
Every guard decides 'what total debt is' from tag NAMES plus arithmetic checks against other names. The same fix class recurs for revenue, operating income, net income and shares. A structural resolver would take the balance sheet's own debt lines, their order and the calculation parent that sums them, and use arithmetic identities as the check; the guards then become the disagreement detector between the two paths, not the primary logic.

## Open decisions deferred to the root-cause pass (do not decide ad hoc)
Exempt the company's own total path from the floor, or widen the tolerance to about 5%; adopt R1 'prefer N + C'; face vs carrying; whether a bank template precedes these guards.

## Companion evidence from the certification dry-run (metric rows, S001+S002, 17 companies, DATA-INFERRED)
Metric cells with no stored row: not_defined_for_period_kind 29,145 (not a gap); input_gap 1,323 (carried causes mostly no_mapped_tag); insufficient_history 98; no_row_inputs_present 6,600, of which 6,200 are metrics whose registry rows declare NO inputs (composites and derived metrics: growth CAGRs, streaks, EBITDA-based, PEG, Piotroski), so the system cannot tell whether their inputs exist; the remaining ~400 are real Mapper gaps (inputs present, no row written). Root-cause reading: the metric registry does not carry its own formulas' dependencies for derived metrics, so completeness of derived metrics cannot be proven or even classified.
