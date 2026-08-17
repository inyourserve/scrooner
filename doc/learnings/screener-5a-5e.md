# Screener Engine — Stages 5a-5e

## Four of five stages were correct on first real test — worth noting plainly

Every prior phase's first build day found at least one real bug via live verification (Mapper Day 1: composite-concept double-counting; Normalizer Day 1: schema gaps; Company Master 4a: two bugs). Screener's schema, resolution rule, operator evaluation, and the four doc-14-specified test screens (`roe > 0.30`, `sic_code = '7372'`, `debt_to_equity between (0,1)`, `roic top_n(3)`) all matched real, independently hand-computed expected results on the first attempt. Plausibly because doc 14 itself was unusually evidence-heavy before any code was written — the "most recent value" resolution rule was checked against real `metric_value` data (TTM vs. FY vs. quarterly rows) *while writing the plan*, not discovered wrong after building against a guess. Worth recording as a data point for how much a well-evidenced plan actually reduces first-build bugs, not just as a "nothing to report."

## The one real bug: lineage gap on a field that wasn't also a filter

`query.py`'s matched-company output only included metric values for fields that were also filter predicates — reasonable-looking, since every doc-14 test screen filtered on the metric it cared about. Testing `sort_by` *without* also filtering on that metric (sort by `net_margin`, filter by `roe`) exposed the gap immediately: the result was correctly ordered, but nothing in the output showed what value produced that order. This is exactly the kind of thing "run the four specified test screens" wouldn't have caught, because none of them exercised `sort_by` as an independent field from the predicates — a reminder that a Definition of Done's named test cases are a floor, not a ceiling, and a genuinely new code path (here: a field referenced only for sorting) deserves its own explicit check even when it's not separately named in the plan.

Fixed by unioning `sort_by` into the set of metrics shown per match, not just the predicate metrics. Re-verified: descending sort showed real values in the correct order; a separate ascending-sort check against `debt_to_equity` (a metric with real nulls in the golden set) confirmed nulls sort last regardless of direction, exercising `query.py`'s two-pass stable-sort design (sort once for value order, sort again — stably — to move nulls to the end) rather than trusting the reasoning about why it should work.

## Verification summary

- All 9 locked operators exercised against real data; 4 concrete test screens from doc 14 matched hand-computed expectations exactly.
- Determinism confirmed: two consecutive runs of the same query produced byte-identical JSON output.
- Unknown-metric and malformed-predicate rejection confirmed at both the Pydantic structural layer and the catalog-validation layer in `query.py`.
- `sort_by`/`limit` verified after fixing the lineage gap above — both ascending and descending, both with and without nulls present.
- Exclusion reasoning (NKE's missing ROIC, ENB/TSM's missing everything) cross-checked against already-documented Mapper-phase findings rather than treated as new/suspicious — consistent with prior evidence, not a fresh anomaly.

## Why it matters going forward

The AI Query Engine (Part 6) will generate `ScreenQuery` objects programmatically, likely exercising field combinations no hand-written test screen anticipated — `sort_by` without a matching predicate is a preview of exactly that shape of gap. Any future extension to this schema (a new field, a new way to reference a metric) should get its own explicit "does this appear correctly in the output" check, not just a "does the filtering/ranking logic work" check — output completeness and input correctness are different properties, and this bug lived in the former while every doc-14 test screen only ever exercised the latter.
