# 2026-09-11 — Natural-language AND/OR/NOT + a frontend gap it exposed

Continuation of 2026-09-10's Screener work: the backend gained real AND/OR/NOT support (`ScreenQuery.where`) that day, but nothing could produce one — the NL parser (`ai_query/rules.py`) still only ever emitted flat AND lists, and the frontend had no way to display a `where`-tree result if one arrived. Closed both.

## NL parser: OR and a trailing NOT

Added to `ai_query/rules.py`, kept within doc 15's existing "deterministic, bounded grammar, never guess" discipline:

- **OR**: an all-"or" query ("roe above 30% or debt to equity below 0.5", "software companies or healthcare companies") splits on `\s+or\s+` and builds `where=PredicateGroup(op="or", ...)`.
- **Mixed AND/OR is rejected, not guessed**: "A and B or C" is genuinely ambiguous without parentheses (could mean either grouping) — detected and reported as unrecognized with an explicit explanation, the same "never guess" precedent `between`'s own `and`-collision limitation already set.
- **A trailing categorical exclusion** ("... excluding financials", "... except banks", "... not in the energy sector") wraps the rest of the query in `PredicateGroup(op="and", predicates=[..., NOT(sector)])`. Deliberately scoped to *categorical* exclusion only — "not ROE above 20%" has no single unambiguous meaning the way "not financials" does, so `_try_extract_exclusion` only commits to the reading when the captured phrase actually resolves to a known sector; otherwise the text is returned untouched and falls through to the ordinary unrecognized-clause path (verified: "software companies excluding penny stocks" correctly fails rather than silently matching every non-penny-stock software company).
- **Ranked queries (top N/bottom N) can't combine with OR** (rejected with an explicit explanation — a ranking operates over the whole result, not one branch of it) but **can combine with a trailing exclusion** ("top 5 by roic excluding financials") — the ranked predicate stays in `metric_predicates` (schema.py's own design: ranked ops never belong inside a boolean tree), only the exclusion goes into `where`.

15 new tests, `tests/unit/test_ai_query_boolean_logic.py`.

## A real bug found immediately testing the ranked+exclusion combination

"top 5 by roic excluding financials" correctly excluded every Financials-sector company from the top 5 — but every match showed a **null** `roic` value, despite being ranked by it. Root cause: `query.py`'s `where`-tree branch built `metric_names_to_show` by walking `query.where` alone (`_collect_metric_names`), which never contains a ranked predicate (schema.py forbids it there) — so the ranking metric's own name never made it into the per-company citation loop, even though its value was already being fetched into `resolved`. Fixed by unioning in `{p.metric_name for p in ranked}` — a one-line fix, but the kind of thing only surfaces by testing a *combination* of two features each already tested in isolation, not either alone. New regression test: `test_boolean_tree_query_still_cites_a_ranked_predicates_own_value` (`test_screener_complete.py`).

## The frontend had no way to show a `where`-tree result at all

Checked before assuming it "just worked" once the backend could produce one: `apps/app/lib/screener/types.ts`'s `ScreenQueryPayload` had no `where` field. Concretely, this meant:

- **`resultMetricNames`** (`ScreenerClient.tsx`) only read `lastQuery.metric_predicates`, which is *empty* for a pure-OR query — the results table would have rendered with zero metric columns for the exact query type this session just added.
- **`MatchReasons`** ("Why matched" per company) had the identical gap — an OR/NOT query's expandable detail would show nothing.
- **`queryToBuilderState`** would have built a `BuilderState` with 0-1 rows from the near-empty flat lists and returned it as if that were the whole query — a misleading "here are your filters" view for the Exact Filters panel, worse than not showing one at all.

Fixed: added `PredicateGroupPayload`/`where` to the type (plus a `collectMetricNames()` helper that recursively walks the tree, mirroring the backend's own `_collect_metric_names`), used it in `resultMetricNames` and `MatchReasons` (which now shows every referenced metric's real value for a combined-filter match, with an explicit note that it isn't the same per-predicate precision a flat AND gets — an honest, bounded fallback rather than a fabricated "matched because" story doc 05's traceability principle wouldn't allow), and made `queryToBuilderState` return `null` for any `where`-tree query so the builder panel is skipped entirely rather than shown empty/wrong.

**A second, unrelated, pre-existing gap surfaced by this same type fix, not introduced by it**: the old `categorical_predicates` type only allowed `"sic_code" | "sic_description"`, silently wrong ever since sector-bucket categorical predicates (`field: "sector"`, doc 28, 2026-08-21) started being possible — TypeScript was structurally incapable of catching it because the type itself was too narrow to be unsound in a way the compiler could see. Widening the type to match the backend's real three-value `field` union immediately (correctly) broke compilation at `queryToBuilderState`'s one call site — fixed by having it return `null` for a sector-field predicate too, since the builder's classification dropdown has never had UI for anything but SIC codes.

8 new pipeline tests (`test_ai_query_boolean_logic.py`), 1 new pipeline regression test (`test_screener_complete.py`), 8 new frontend tests (`lib/screener/types.test.ts`, `lib/screener/interpretation.test.ts`). Full pipeline suite 526→535, backend 27 (unchanged), frontend 71→79, all passing. Production build (`npm run build`) succeeds. Verified live end-to-end through the real HTTP API: an OR query's `matched[i].metrics` now correctly carries both branches' metric values, confirming the frontend fix actually closes the gap rather than just type-checking.
