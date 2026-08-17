# Normalizer Day 3 — Unit Normalization

## Finding: filer-invented count units really do collide across companies, registered units don't

Before writing `units.py`, pulled every distinct unit string across all 10 golden companies' companyfacts payloads (29 raw strings total) to see what "standardize units" actually had to handle, rather than assuming `USD`/`shares`/`pure` was the whole story.

### What was found

XBRL's registered units (`USD`/`CAD`/`TWD`/`EUR` — ISO 4217 currency codes; `shares`, `pure` — the standard non-currency units) were consistently cased across every filer, no collisions. But units filers invent themselves for count-type facts (e.g. "how many reportable segments") have no such registry: found `segment` (141 datapoints, 5 companies) and `Segment` (13 datapoints, 2 companies) both used for `us-gaap:NumberOfReportableSegments`-style concepts — same real unit, inconsistent casing. Same pattern spotted for `Year` vs `years` (same exact concept, `us-gaap:EmployeeServiceShareBasedCompensation...PeriodForRecognition`, reported under both).

### Decision

Case-fold (lower + strip) as the only standardization — deliberately nothing fuzzier. `Segment`/`segment` collapse to one `core.unit` row (`segment`); `Year`/`years` deliberately stay two separate rows (`year`, `years`) since plural-stemming would be a fuzzier heuristic risking a false-positive merge elsewhere, and case-folding alone was enough to resolve every real collision actually observed. Explicitly did NOT attempt to merge different custom count units that share a shape (e.g. `Store` counts vs `Job` counts vs `operating_segment` counts) — those measure genuinely different things; conflating them on the theory that "they're all just counts" would be a Mapper-level judgment about meaning, not Normalizer-level string standardization. This line is explicit in doc 04's boundary table ("standardize units" is Normalizer's job; deciding what a concept means is not).

### Verification

- 29 raw unit strings → 28 canonical `core.unit` rows (only the `segment`/`Segment` pair collapsed).
- Confirmed directly: zero rows in `core.unit` differ only by case.
- Reran the job — identical row count (28), confirming idempotency.
- DB size unchanged (15 MB) — `core.unit` is tiny by design, as intended (doc 09's Supabase capacity section).

### Why it matters going forward

Don't assume a phase's "hard part" from the schema/docs alone — the actual edge cases (which specific units collide, and which superficially-similar ones must NOT be merged) only showed up by pulling real payloads and counting. Same generalizable lesson as Days 1-2, now confirmed a third time on this project: check live data before designing the transform, not after.
