# Income-statement missing quarters — classifier, fixes, what is left (2026-11-09)

Queue item from Dhairya (2026-11-09): income-statement Q1–Q4 keys missing while the year is served, systematic per
company (MA net income 47 Q keys, PNC, Exelon, ELS, Oshkosh). Build a key-level classifier like `cf_gap_classify`,
run it on MA, PNC, EXC, PEP and AT&T (2017 Q4) first, then fix mapping or derivation, with reasoned blanks where a
quarter truly cannot be derived. All work is inside the hybrid store code (`pipeline/src/scrooner_pipeline/fsn_store`).

Branch `work/income-statement/quarter-gap-classify` (from `main` 787cc667). Evidence level: DATA-INFERRED from the
SEC FSN rows of each filing (loaded into a scratch store, the same rows production loads); no filing page was
opened for this note, so nothing here is FILING-CHECKED. No production read or write.

## 1. What I ran

- SEC FSN sets 2014q1 → 2026m09 (59 sets, sec.gov only, declared User-Agent) cut to the 7 companies' 10-K/10-Q
  filings with `fsn_sec_fixture.py`; loaded with `scrooner-fsn load`, seeds applied, then
  `mapping.map_company` → `checks.check_company` → `pilot.report_company` (the cohort dry run's per-company steps).
- `pipeline/scripts/slot_records/is_quarter_gap_classify.py <db> <gaps.csv> <out>`: one class per income-statement
  gap key, from what the covering filing holds (the class list is in the script's docstring).
- Before/after on 67 companies (these 7 + the 60 of the CF-gaps work) for regressions: every cell of every concept.

## 2. What the 954 gap keys were (7 companies, before)

| class | keys | what it means |
|---|---|---|
| other_tag_on_face | 372 | the face prints the line under a tag the seed does not map (mostly net income as `ProfitLoss`) |
| mapped_line_no_value_for_column | 258 | the mapped line has no value for the key's column (PepsiCo key/date mismatch; AT&T member-only cost line; Exelon subsidiaries-only `NetIncomeLoss`) |
| no_line_for_concept | 146 | nothing of the concept on the face (ELS: no operating income / income tax / interest-expense line) |
| printed_other_statement | 65 | the tag is printed only on the equity statement (ELS net income) |
| printed_not_face_column | 49 | the column is printed, but the store does not count it as a face column (PNC 2021–23) |
| no_covering_filing | 46 | the key's filing is not in the sets yet (2026-09-30 quarter) |
| ytd_only_* | 18 | only a year-to-date column; derivation not possible or held |

Per company (before → after): MA 65 → 8, PNC 93 → 57, Exelon 128 → 89, PepsiCo 160 → 10, AT&T 70 → 70,
ELS 273 → 264, Oshkosh 165 → 108. Net income alone: MA 58 → 1, PepsiCo 16 → 1, Oshkosh 58 → 1, Exelon 56 → 17,
ELS 58 → 49, PNC 57 → 57. Total 954 → 606.

Your two hypotheses: "the 10-Q maps a different tag than the 10-K" — no; the tag is the same in both, it is the
SEED that misses it (`ProfitLoss`), on the 10-K too, so FY was blank in the store as well (the FY you saw served is
the old table's). "3M-column selection failing on 3M+YTD statements" — not found in these 7; the store reads both
columns. The one column problem was PepsiCo's date (below).

## 3. Fixes (all in the store code, tests mutation-checked)

1. **Net-income detector** `fsn_store/is_detector.py`, registered in `detectors.DEFAULT`. The income-statement seed
   maps only `NetIncomeLoss`; the lane's two conditional rules were left out of the seed
   (`concept_rules/is_not_extracted.md`) and never ran in the store. The detector imports the lane's own code
   (`is_detect.primary_face`, `net_income_slot`), nothing retyped:
   - G1b: `ProfitLoss` is the parent's net income when the face prints no `NetIncomeLoss` line and nothing below
     takes a share (no NCI line on IS/CI, no preferred line below it). MA, Oshkosh.
   - G2b: a face that bridges `ProfitLoss` to the "attributable to <parent>" line
     (`NetIncomeLossAvailableToCommonStockholdersBasic`) through NCI / subsidiary-preferred lines only maps that line.
   - Exelon: its combined filings print `NetIncomeLoss` only for the subsidiaries (member columns); when the line has
     no undimensioned parent value and the G2b bridge holds, the bridge line is mapped and `NetIncomeLoss` unmapped.
2. **52/53-week quarters** (`pilot._match`, 10 → 16 days): FSN rounds a period end to the NEAREST month end, so
   PepsiCo's 12-week Q2 ending 2015-06-13 is stored as 2015-05-31, 13 days from the calendar key. Every PepsiCo Q2
   (and three Q1s) was an unexplained gap. Period ends are about 3 months apart, so 16 days never reaches a neighbour.
3. **PNC face columns** (`select.ANCHOR_TAGS["IS"]`): PNC's 2021–2023 10-Qs print the bottom line as
   `IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest`; with no other anchor on
   the face, none of those columns counted as face, so revenue, pretax, tax, EPS and interest were blank.
4. **Derivation order** (`select.select_concept`), found by the 67-company regression run: a blank that a 9M input
   gave no longer shuts out the FY route (FY − 9M or the 10-K's quarterly note). Rhythm Q4 2018 had lost its value
   once `ProfitLoss` was mapped (an equity-statement 9M column). A blank keeps its first reason; a printed or
   derived value is never changed.
5. **Q4 from an older 10-K's printed note** (`select._note_quarter`), also found by the regression run: mapping
   `ProfitLoss` / the bridge line made later 10-Ks (which repeat old years as comparatives, without their notes) the
   FY winner, so Q4 fell back to FY − 9M (Arrowhead, Tesla moved by $1–2,419). The note of an older filing that
   prints the same FY value is now used (the period-engineer rule: a printed quarter beats a derived one). See §4
   for its wider effect.

Tests: `pipeline/tests/unit/test_fsn_is_quarter_gaps.py` (12: 9 unit, 3 on the real schema). Each fix was reverted
in a copy of the source and the suite failed (9 mutations). FSN/CF/BS/per-share suites: 750 passed.

## 4. Regression run, 67 companies (every cell of every concept)

`main` (787cc667) vs this branch on the same scratch store, every cell of every concept, 67 companies. Full list:
`pipeline/scripts/slot_records/results/is_quarter_gaps_2026-11-09/regression_67_companies_changes.csv.gz`.

| change | cells | companies |
|---|---|---|
| new value (was a gap or a blank) | 494 (net income 340) | 50 |
| value changed: Q4 is now the filer's PRINTED quarterly-note figure (fix 5) | 124 | 35 |
| value changed: a later restated print wins (AT&T D&A Q2/Q3 2021, 5,761 → 4,429 and 5,619 → 4,457: the 2022 10-Qs recast 2021 to continuing operations after WarnerMedia) | 2 | 1 |
| value lost | 1 | 1 |
| derived → printed, same value | 848 | — |

The lost value: NCLH FY2016 net income (633,085). Its latest copy is now the FY2018 10-K, whose FY2016 column fails
the filer's own `calc:DirectOperatingCosts` (2,850,225 printed vs 1,894,875 from three children); the store holds
the column (latest_copy_fails_identity), as it already does for every other line of that column. Same cause as
AT&T 2017 below.

The 124 printed-note changes come from **fix 5** (`select._note_quarter`): when the FY winner (the latest copy) is
a later 10-K that repeats the year as a comparative and carries no quarterly note for it, the note of an older
filing printing the SAME FY value is used. Most moves are the filer's rounding (FY − 9M vs the printed quarter:
Amazon ±1M, Arrowhead $1–2,419). Some are basis corrections: Erie Q4 2014 revenue 1,589M → 337M and AT&T Q4 2021
revenue 40,958M → 31,095M. In both the store serves the RECAST FY (Erie 1,407M after deconsolidating the
Exchange; AT&T 134,038M continuing operations), but the quarter was derived from the ORIGINAL FY and 9M (the
"other printed pairs" route of `_ytd_difference`), so Q1–Q4 did not add up to the FY shown beside them. These
change shown numbers: **they need the Verifier before release** (sample from the CSV, `after_rule =
fsn.select_note_quarter@1`).

7 companies after all fixes: 954 → 606 gap keys; the remaining classes: other_tag_on_face 221,
no_line_for_concept 146, mapped_line_no_value_for_column 81, the parent-NI common line held 50 (ELS),
no_covering_filing 46, FY input held (latest copy fails identity) 32, printed on another statement 22.

## 5. What is left, and why (not a mapping bug)

- **Parent net income not printed** (PNC all years, ELS Q2–Q4): the face prints consolidated `ProfitLoss`, the NCI
  line, then the PARENT's preferred dividends, then income available to common. Net income attributable to the
  parent is not a printed line; the lane deliberately holds this (mind entry `profitloss-is-the-parent-s-net-income-only-if-nothing-below-`).
  Serving it needs `ProfitLoss − NCI` as a derivation: a definition decision for the Standardization Lead, not a
  mapping. Until then these keys should be a reasoned blank (`parent_net_income_not_printed`).
- **AT&T 2017 Q4** (and FY2017): the latest copy of FY2017 is the FY2019 10-K (0001562762-20-000064), and its
  2017 column fails `calc:NonoperatingIncomeExpense` (−4,831M printed vs −4,575M from the calc children: a child
  line is missing from the filer's calc). The store holds the whole column, so FY2017 is blank and Q4 (= FY − 9M)
  cannot be computed. On `main` the quarter has no cell at all; PR #4's held-input rule gives it the reason
  `latest_copy_fails_identity`. Proposal (needs a decision, changes many cells): a failed subtotal calc should hold
  only the concepts under that subtotal, not every line of the column. Same shape: NCLH FY2016 (the FY2018 10-K's
  `calc:DirectOperatingCosts`).
- **AT&T cost of revenue**: the face prints cost components ("Equipment" under a member, "Other cost of services")
  with no total line. A reasoned blank (`no_total_line`); the lane's calc-sum rule G3 is not ported.
- **Oshkosh EPS**: the face prints only `IncomeLossFromContinuingOperationsPerBasicShare` / `...PerDilutedShare`
  labelled "Basic" / "Diluted". Mapping continuing-operations EPS as total EPS is a definition decision (only safe
  with no discontinued line); proposed to the Standardization Lead, not done.
- **Exelon interest expense**: "Interest expense, net" (`InterestExpenseBorrowings`) plus "to affiliates"; no seeded
  tag. A Tag Mapper lead.
- **ELS operating income / income tax / interest**: a REIT face prints none (interest is `InterestExpenseDebt`,
  "Interest and related amortization"). Template-OUT or sole-debt-interest reasons, owned by the sector templates.

## 6. Requirement recorded (founder direction relayed by Dhairya, 2026-11-09)

The old normalizer/mapper get no fixes; the nightly-refresh `normalize:facts` work is dropped (branch
`work/pipeline/refresh-cohort-cap` 4877e04d is superseded, not to merge). For the nightly incremental session:
derived metrics (growth, TTM, margins, ratios, P/E) must recompute from `canonical_fact` after the hybrid store
writes. Not built here.

## 7. Next

1. Reasoned blanks for §5 (parent NI not printed, no total line) once PR #4 merges: it carries the
   `absent_line_cell` / held-input machinery these extend.
2. Run the classifier on the full cohort dry-run output (`gaps.csv`) to size each class across 1,000 companies.
3. The calc-hold scope proposal (§5, AT&T) to Dhairya / Standardization Lead.
