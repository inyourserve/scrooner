# NVDA / STX open cells: 52/53-week period-key trace (2026-11-16)

Read-only code trace at `dd7995b`. No DB access; anything that needs a live row is marked **UNCONFIRMED (needs DB)**.
Inputs: `data-team/strategy/top100-open-cells-causes-2026-11-15.csv`, `top100-coverage.csv`,
`top100-open-cells-20261115T1943Z.csv`, `data-team/tags/line_map/resolver-all110-2026-11-14.csv`,
`data-team/companies/reads/{NVDA,STX}-docmap-2026-11-12.csv`, `data-team/tags/exam/eras/NVDA-*-prediction.csv`.

Background fact (code): `fsn.filing.period` is month-end rounded on both load paths (FSN `sub.period`, and
`fsn_store/xbrl_fsn.py:1064` `round_month_end(...)`). `core.period.end_date` is the true 52/53-week date.

| Cell | Period-key? | Where |
|---|---|---|
| NVDA cash_paid_for_interest FY2026 | **Yes** (confirmed from code + CSV pattern) | `mapper/top100_coverage.py:707` vs `:956-957` |
| STX other_income_expense_net FY2026 | **Yes** (code path confirmed; map rows UNCONFIRMED) | stub era from `docmap_loader.py:519-520`, chosen at `proof/shown.py:153,167-172` |
| NVDA total_debt FY2018 | **Not shown to be period-key** | hold at `mapper/company_tag_map.py:1369,1412`; root cause UNCONFIRMED |
| NVDA total_debt FY2019 | **Not shown to be period-key** | fall-through `mapper/top100_coverage.py:595`; root cause UNCONFIRMED |

## 1. NVDA cash_paid_for_interest FY2026 — reason_own_filing_unverified

**Cause (period key, report layer only).** `_statement_pages` keys the own-year 10-K by the FSN month-end period:
```
top100_coverage.py:707   k = (cid, period, stmt)            # period = fsn.filing.period, e.g. 2026-01-31
top100_coverage.py:956   own_acc, own_page = stmt_pages.get(
top100_coverage.py:957       (c.company_id, e, dstmt), ("", ""))   # e = core.period end, 2026-01-25
```
The cell is REASON (docmap/map `not_presented`) with no covering evidence accession, so the locator falls to the
own-year lookup, misses on exact date equality, `acc` stays `""`, and `own_period_reason` downgrades it:
`top100_coverage.py:248-249  if cls == "REASON" and acc not in eligible_filings(...): return "UNCHECKED", OWN_UNVERIFIED`.

**Evidence.**
- Coverage row: `NVDA,cash_paid_for_interest,2026,2026-01-25,UNCHECKED,reason_own_filing_unverified,...,locator_source=none`, accession blank.
- Resolver: `NVDA,cash_paid_for_interest,2026-01-31,FY,not_presented,...,0001045810-26-000021,own` (the reason is real).
- Docmap: `not_presented ... accn 0001045810-26-000021 period 2025-01-27..2026-01-25`.
- Whole `top100-coverage.csv`: `locator_source=own_year` occurs on 12,486 rows, **all** with a month-end `period_end`, and
  **0** rows with a non-month-end end. The only other `reason_own_filing_unverified` + `none` + non-month-end row is
  `AAPL goodwill FY2026 (2026-09-26)` — same mechanism.

**Fix (proposed).** Key `stmt_pages` by period tolerantly: either look up with
`next((v for (cid_, p, s), v in stmt_pages.items() if cid_ == cid and s == dstmt and fsn_end_matches(p, e)), ("",""))`
(precompute per company to stay O(1)), or select `core.filing.period_of_report` (true date) joined by accession
instead of `fsn.filing.period` in `_statement_pages` (`top100_coverage.py:693-713`). The first is safer (no new join).
Re-run the coverage report afterwards; the cell should become REASON citing `0001045810-26-000021`.

**Test outline** (`pipeline/tests/test_top100_coverage.py`, next to `test_r_page_comes_from_the_years_own_filing_not_the_docmap_read`):
1. Fake `_statement_pages` rows with `period=date(2026,1,31)`, CF report 9, accession A.
2. Call the own-year lookup helper (extract the lookup at :956 into a pure `own_year_page(stmt_pages, cid, e, stmt)`)
   with `e=date(2026,1,25)` → expect `(A, "R9.htm")`. Today it returns `("", "")` → fails before the fix.
3. Chain: `own_period_reason("REASON", "company_tag_map:not_presented", A, [(date(2026,1,31), A)], date(2026,1,25), False)`
   → stays REASON (guards the downstream step). Mutation-check: revert the lookup to exact `.get` and the test fails.

## 2. STX other_income_expense_net FY2026 — shown_differs_from_printed_line (-150 vs -404)

**Cause (period key, via a stub era).** The resolver row's era ends on the FSN date
(`structural_loader.py:515  b = c.era_to or c.period_end` → 2026-06-30). The library docmap row
(`STX docmap: other_income_expense_net,mapped,us-gaap:NonoperatingIncomeExpense, 'Other expense, net' 404`) is open-ended
(`docmap_loader.py:113 era_to = None`) and is clipped around the structural span (`structural_loader.py:1035` →
`docmap_loader.py:519-520  if hi is None or hi > b: nxt.append((b + timedelta(days=1), hi))`), leaving a library
concept row **2026-07-01..open**. The true year end 2026-07-03 is *after* 2026-06-30, so:
- `era_holds` holds it in the structural component era (month-end rounding → 2026-06-30), **and**
- it lies literally inside the stub library era 2026-07-01..open.

The proof's `claim_for` then prefers the concept row: `shown.py:153 held = [r for r in rows if era_holds(...)]`,
`shown.py:167-172 concept = sorted(... r[1] == "concept" ...); if concept: return Claim("concept", ...)`. So `_prove_cell`
takes the concept path (`prove.py:1104` skips `prove_component`) and compares the served component sum -150 with
the printed `NonoperatingIncomeExpense` (-404, which includes interest income 30 and interest expense -284) →
`prove.py:802 shown_differs_from_printed_line`. So the "proof defect" in the causes CSV is this same period-key effect.

Why only FY2026: earlier past-month-end years (FY2015 2015-07-03, FY2020 2020-07-03, FY2021 2021-07-02) have the next
year's structural era starting the day after the FSN date, so no library stub survives there; only the newest year
falls into the open remainder. NVDA ends (Jan 25-31) are never past the month end, so NVDA cannot hit this variant.

**Evidence.** Resolver `STX,other_income_expense_net,2026-06-30,FY,component_sum, ... 4 band lines = -150,000,000`;
coverage `DISAGREE ... production shows -150000000 (GainLossOnTerminationOfInterestRateSwapNet), the printed
NonoperatingIncomeExpense line reads -404000000`; FY2024/FY2025 (ends 06-28, 06-27) PROVEN via `proof_tag` with all four parts.
**UNCONFIRMED (needs DB):** that `analytics.company_tag_map` holds the STX library concept row with `era_from = 2026-07-01`.
Check: `select decision, tag, era_from, era_to, rule_id from analytics.company_tag_map m join analytics.canonical_concept c
on c.id = m.canonical_concept_id where m.company_id = 3886 and c.name like 'other_income_expense_net%' order by era_from;`

**Fix (proposed), two parts.**
1. Root: make the stub impossible. In `assign_eras` (or in `plan_company` before building `spans`), extend the last
   claim's era_to to the true end, i.e. `max(c.period_end, nearest true end)`, or simpler: clip with month-end tolerance —
   in `clip_rows` start the remainder at `b + 16 days` when `b` is a month end (no true year end lies more than
   ~15 days past its FSN month end). Same treatment for the leading edge (`a - 1`).
2. Belt: in `claim_for`, when a held concept row holds the date only *literally* while a component row holds it only
   *by rounding* (or vice versa), prefer the row whose era contains the month-end rounding of a 52/53-week end, i.e. the
   resolver's own era. A cheaper guard: never let a row with `rule_id != structural@1` beat a `structural@1` row that
   holds the date.

**Test outline.**
- `tests/unit/test_structural_loader.py`: `plan_company` with an open library concept row (era 2014-07-01..None) and
  structural component claims ending 2025-06-30 and 2026-06-30 → assert no merged non-structural row has
  `era_holds(era_from, era_to, date(2026,7,3))`. Fails today (stub 2026-07-01..None).
- `tests/proof/test_shown.py`: `claim_for(rows=[component rows ..2026-06-30, concept row 2026-07-01..None],
  'other_income_expense_net', date(2026,7,3))` → expect `kind == "component"`. Fails today (returns concept).
Mutation-check each by reverting the clip/priority change.

## 3. NVDA total_debt FY2018 — HELD component_missing_for_period

**Where emitted.** `company_tag_map.py:1360-1373` (part listed for the era but no fact) / `:1412` (absent part without
zero evidence). Cell keys and era tests on this path all use `_in_era` → `era_holds` (`company_tag_map.py:732-736`) and
`fsn_end_matches`; the only exact-date comparisons left (`structural_loader.py:1229`, `structural_direct.py:103`) are
tie-breakers that fall back to the tolerant match. NVDA's ends are before the month end, so the STX stub variant
cannot hit. **I found no period-key defect on this path.**

**Evidence.** Resolver `NVDA,total_debt,2018-01-31,I,component_sum, ConvertibleDebtCurrent=15 [R4:18]; LongTermDebt=1,985
[R4:20]; CapitalLeaseObligations=5 [NOTE]` = 2,005, acc `0001045810-18-000010`. Old predictor (`exam/eras/NVDA-0001045810-18-000010-prediction.csv:50`)
names `CapitalLeaseObligationsCurrent+CapitalLeaseObligationsNoncurrent` instead. Coverage: HELD, no served value.

**Most likely causes — UNCONFIRMED (needs DB):**
(a) structural-direct rejected the claim (e.g. `CapitalLeaseObligations: no stored fact for the part in that filing and
column`, `structural_direct.py:494`), so the tag-era path's hold stands; or (b) the FY2018 structural claim was rejected
by `structural_loader.load` (rejects CSV), leaving older predictor/machine component rows (CapitalLeaseObligations
Current/Noncurrent) in the era, whose parts are missing → `component_missing_for_period`.
Check: run the mapper dry-run for company 2733 and read `stats["structural_direct_rejected"]` and the structural-load
rejects for `total_debt 2018-01-31`; and list `company_tag_map` component rows for total_debt with eras covering 2018-01-28.

**Fix / test.** Depends on (a)/(b). If (a) with a fsn.value present only dimensioned, it is a resolver/loader gap,
not a date key. Test outline once known: a `direct_cells` unit case with the three parts and a NOTE part stored only in
`fsn.value` at ddate 2018-01-31, period end 2018-01-28 → expect one served cell of 2,005.

## 4. NVDA total_debt FY2019 — BLANK docmap_component_sum_not_loaded

**Where emitted.** `top100_coverage.py:595`, the last fall-through of `classify`: no served value, no proof, no
`cell_blank_reason` row, no map reason, docmap status `component sum`. Lookups are exact on `(cid, name, start, end)`
(`top100_coverage.py:855-866`), but every writer keys by `period_id` of the same `core.period`, so this is consistent.

**Evidence.** Resolver `NVDA,total_debt,2019-01-31,I,component_sum, ConvertibleDebtCurrent=0.0000 [R4:18]; LongTermDebt=1,988`.
The FY2019 face prints a dash for convertible short-term debt.

**Most likely cause — UNCONFIRMED (needs DB):** not a period key. If no `ConvertibleDebtCurrent` fact is stored for
2019-01-27, `structural_direct` rejects (`no stored fact`): the printed-zero rule is limited to `mapped` claims
(`structural_direct.py:221-225 if claim.decision != "mapped" ... return False`), so a dash *part* of a component sum
is never served as 0. The absence of any hold row suggests the tag-era path had no covering component rows for that
era either (structural claim rejected at load, or era gap). Same DB checks as cell 3.

**Fix (if confirmed).** Allow `printed_zero` per part of a `component_sum` when the resolver node is exactly 0 and the
line is on the face (ruling needed: doc 02 / Dhairya 2026-11-14 covers `mapped` only). Test: `printed_zero_ok`-style
unit case for a component_sum part → served 1,988; fails today.

## Summary
Period-key defects found: `top100_coverage.py:707/956` (exact own-year key; NVDA FY2026, also AAPL goodwill FY2026)
and the month-end stub era (`docmap_loader.py:519-520` via `structural_loader.py:1035`, chosen by `shown.py:153-172`;
STX FY2026). NVDA total_debt FY2018/FY2019 are not explained by any period-key comparison in code; their cause needs
the DB checks above.
