# Natural-language screening: 4 real parsing gaps closed (2026-10-02)

Prompted by a user-supplied design doc (`doc/create-screen/scrooner-natural-language-screening-flow (1).md`) asking to "make it fully workable." Rather than assume the described flow was missing, ran its own worked example live against the real parser first:

```
"Show US technology companies with a market cap above $10 billion and a P/E ratio below 25"
```

Came back entirely unrecognized. Isolated each clause individually (not guessed) to find the real, narrow causes — four independent gaps, not one:

1. **"P/E ratio" (with the slash) was never aliased, only the bare "P/E"/"pe ratio" forms were** (`ai_query/aliases.py`). Same gap existed for "P/B ratio", "P/S ratio", "D/E ratio" — every other abbreviated ratio metric had its bare form aliased but not the "... ratio"-suffixed one. Fixed: added all four.
2. **A leading article ("a market cap above $10 billion") was never stripped before metric lookup.** `_strip_filler()` looped through its filler-prefix list exactly once, so "with a market cap" stripped "with " but had no second pass to then strip "a ". Fixed: the loop now repeats until nothing more matches, and "a "/"an "/"the " were added to the list.
3. **The real structural gap: "{sector} companies with {metric clause}" (no literal "and"/"or") was entirely unrecognized**, even though "software companies" and "ROE above 30%" each parse fine alone. A single clause can only ever carry one of a metric OR a categorical predicate (`_parse_clause`'s own contract) — there was no mechanism to split a "with"/"having"-joined clause into two. Fixed with `_split_category_prefix()`: when the text before "with"/"having" resolves to a known sector via the existing `_lookup_sector()`, split into two independent clauses — the exact same shape "software companies and ROE above 30%" already produces — and let the existing AND-combination logic handle the rest, unchanged. Deliberately conservative: only triggers on a *recognized* sector name, so the pre-existing, unrelated "companies with {metric}" filler-stripping (where "companies" alone is not a sector) is completely untouched.
4. **A leading imperative ("Show ...", "Find ...", "List ...") and a redundant "US" qualifier in front of a sector name were never stripped.** Added a small, curated `LEADING_QUERY_FILLER_PREFIXES` list (silently stripped, same discipline as the existing metric-phrase filler list — not surfaced as a "correction," since there's nothing to show the user) and a "US"/"U.S." strip inside `_lookup_sector()` (doc 02 scopes this project to US-listed equities only, so "US" in front of a sector name is never a real second filter).

## One thing deliberately NOT done, and why

The source doc's own worked example notes: *"This example uses a positive trailing P/E ratio to exclude loss-making companies... Show that interpretation to the user so they can edit it."* Verified live: a literal "P/E ratio below 25" also matches a company with a **negative** P/E (Intel, -55.7; Semtech, -440.0, both genuinely matched in a real run against `analytics.company_screening_snapshot`) — numerically correct, but probably not what a user asking for "P/E below 25" means.

**Did not add a silent `P/E > 0` guard.** This project's own locked release gate (doc 02/03) is explicit: ambiguous queries are never silently reinterpreted, and every result must trace to exactly what was asked, not an inferred intent. Silently injecting an extra condition the user never typed is exactly the failure mode that gate exists to prevent — the source doc's own suggestion here is in real tension with Scrooner's stricter determinism principle, and the stricter one wins. The user's actual recourse already exists and needs no new code: `"P/E ratio between 0 and 25"` expresses the intended exclusion explicitly. (Found, not fixed, in the same pass: combining a `between` clause with another AND-joined clause in the same query is a separate, pre-existing, already-documented grammar limitation in `rules.py`'s own module docstring — not something this session introduced or attempted to fix.)

## Verification

- All 4 fixes tested in isolation and combined, live, against the real parser (`uv run python`, not mocked), including the literal doc example end to end through the real `run_query()` against the real dev database snapshot — 52 real companies matched, with the negative-P/E behavior above directly observed in real output, not hypothesized.
- 8 regression checks confirming every previously-working phrasing (`"roe above 30% and debt to equity below 0.5"`, `"companies with ROE above 30%"`, `"top 5 by roic"`, `"software companies"`, an OR query) is byte-identical to before.
- New test file `tests/unit/test_ai_query_natural_phrasing_gaps.py`, 19 tests. Full pipeline suite: 788 → 807 passing, zero regressions.

## The broader "Query Library" design in the source doc — evaluated, not built

The source doc also proposes a persistent, cross-user "query library": exact-match fingerprinting, similar-query suggestions, and reuse of a canonical stored query definition across *every* user asking an equivalent question. Most of its *intent* is already satisfied by what exists, just structured differently:

- English → structured query: `ai_query/rules.py::interpret()` (fixed this session).
- Exact-match fingerprint + reuse: `screener/cache_key.py::compute_query_hash()` (query + `dataset_version`) plus a **global** (not per-user) Redis cache (`cache.get_cached_result`/`set_cached_result`) — any user asking an identical normalized query already gets a shared, precomputed result, not a case-by-case recomputation.
- "Reuse the query definition, not stale results": already true in effect — a result is cache-scoped to `dataset_version`, so it's automatically invalidated the moment a new snapshot is built, without needing a "run against current data" step bolted on separately.
- "Query library vs. a user's personal saved screen": this is *exactly* the existing `app.screen_result` (shared/library-shaped, not personal) vs. `app.saved_screen` (personal name/reference) split — same concept, different vocabulary.

**One real, direct conflict, not silently resolved either way:** the doc asks to "deduplicate identical queries even when multiple users create them simultaneously" at the *storage* level. That existed once — and was deliberately removed 2026-09-20, by explicit founder direction ("i dont want unique key or whatever thing, please make sure to make it fastest"), because the dedup check's own overhead cost more than it saved while every round trip was slow and cross-region. The Redis layer still gives equivalent *result* reuse without that storage-level complexity. Given the same-region hosting decision made earlier today, the original cost/benefit tradeoff behind that removal may no longer hold as strongly — but reinstating it is a deliberate call to make, not something to quietly re-add under a new name. Flagged for a decision, not reversed here.

**Genuinely new and not built:** similarity-based "did you mean this existing screen?" suggestions (would need a real design — embeddings, or a cheaper heuristic like same-metrics-different-thresholds — this parser has neither), and a library-level "Title" distinct from a personal saved-screen name (overlaps with the deliberately-deferred-past-MVP SEO/Content Engine, doc 02/06 Part 12 — public/indexed screen pages). Neither built this pass; both are real product decisions, not engineering gaps.

## Same-day follow-up: "did you mean X" auto-suggestion for typos (2026-10-02)

Prompted by a direct discussion of the "user can write anything" problem: a rule-based parser can only ever recognize phrasing someone anticipated, and patching individual sentences (above) doesn't change that ceiling. A full LLM would generalize further but costs latency/money/vendor-decision and risks silent misreadings — this project's own release gate (doc 02/03) requires it to ask rather than guess even if one is ever added. The agreed middle ground, built this pass: a **typo-tolerant auto-suggestion layer**, not a silent auto-correct.

`_lookup_metric()` now falls back to `difflib.get_close_matches()` against the full `METRIC_ALIASES` vocabulary (cutoff 0.72, a real similarity ratio, not a loose substring check) whenever a phrase doesn't exactly match a known alias or a curated ambiguity. A near-miss is returned through the *exact same* `AmbiguityNote`/`candidates` shape the parser already uses for genuine ambiguity ("revenue growth" → YoY or 3Y CAGR?) — meaning the frontend's existing "choose a meaning" clickable-suggestion UI handles it with **zero frontend changes**. Nothing is ever substituted on the user's behalf; they still have to click a candidate.

Verified live, not guessed: "markt cap above $10 billion" → suggests `market_cap`; "p/e rtio below 25" → suggests `trailing_pe` (plus `peg_ratio` as a secondary candidate, since it also contains "ratio" — both shown, user picks); "retrun on equty above 20%" → suggests `roe` (a typo shape the existing curated spelling-fix regex in `normalizer.py` did *not* already cover — this is a genuinely more general mechanism, not a duplicate of that list). Confirmed no false positives: unrelated gibberish ("xyzzy quux above 5") correctly stays plain "unrecognized," not a confusing wrong suggestion. Confirmed existing curated ambiguities (`AMBIGUOUS_METRIC_PHRASES`) still take precedence and are completely unaffected, since they're checked first.

Deliberately scoped to **metrics only**, not sectors — a sector near-miss would need its own suggestion shape, since `AmbiguityNote.candidates` renders through the frontend's metric-name lookup today. Not built this pass; a real but smaller follow-up if wanted.

5 new tests, full pipeline suite: 807 → 812 passing, zero regressions.
