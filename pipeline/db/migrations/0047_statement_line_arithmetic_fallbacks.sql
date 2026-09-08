-- Statement-table arithmetic fallbacks (2026-09-07). Found live investigating
-- a direct user report ("lots of row and column have no value" on the
-- company page's Income/Balance Sheet/Cash Flow tables): the Income
-- Statement's Gross Profit/Cost of Revenue/Operating Expenses rows were
-- each backed by exactly ONE XBRL tag with no fallback at all, despite
-- doc 40 (2026-09-02) already establishing that gross_margin (the METRIC)
-- derives cleanly from Revenue minus Cost of Revenue for the ratio engine --
-- that derivation was never extended to the canonical_fact layer the
-- statement TABLE reads from. Real, measured gap before this fix (active
-- population, 5,216 companies, "ever had a value" basis): gross_profit
-- 2,528 (48.5%), cost_of_revenue 3,087 (59.2%), operating_expenses 3,748
-- (71.9%) -- the three weakest Income Statement rows by a wide margin.
-- Per-period fill opportunity confirmed before trusting the derivation:
-- 45,001 (company, period) rows have Revenue + Cost of Revenue but no
-- Gross Profit; 11,412 have Revenue + Gross Profit but no Cost of Revenue;
-- 53,303 have Gross Profit + Operating Income but no Operating Expenses.
-- Accounting-identity sanity check against the 128,885 periods that
-- already report all three: 92.0% match Revenue-CostOfRevenue exactly,
-- another 1.8% within 2% (immaterial rounding/reclass), 6.3% genuinely
-- disagree -- of those, the periods checked by hand all trace to a
-- SEPARATE, already-flagged data-quality bug (see
-- doc/learnings/2026-09-07-statement-table-coverage-and-revenue-zero-bug.md):
-- resolve.py's `first_match` falls through to a lower-priority revenue tag
-- reporting a spurious authoritative $0 when the priority-1 tag has real,
-- consensus-close values that got marked non-authoritative over a trivial
-- (<1%) cross-filing rounding difference (Stage 2e's own documented,
-- correct-by-design conflict policy -- see pipeline/CLAUDE.md's 2026-08-19
-- total_debt entry for the same mechanism). That bug is NOT fixed by this
-- migration -- it lives in resolve.py/dedupe.py, a frozen Mapper boundary
-- this migration deliberately doesn't touch. Instead, every derivation
-- below requires revenue > 0 as a guard, which structurally can't fire on
-- exactly the periods the $0 bug corrupts -- confirmed live: Flowserve's 7
-- known-bad zero-revenue FY periods produce NO gross_profit_resolved row
-- (an honest blank cell) rather than a nonsensical negative-billions
-- "Gross Profit" figure.
--
-- Same "new THIRD concept, zero concept_mapping rows, resolve() never
-- touches it" idiom as total_debt_resolved (migration 0033) -- but an
-- ARITHMETIC merge (primary tag if present, else derived from two OTHER
-- concepts) rather than 0033's simple concept-vs-concept coalesce, so
-- these are populated by a new function in mapper/concept_fallback.py,
-- not resolve() at all (zero concept_mapping rows below, on purpose).
--
-- operating_expenses_resolved intentionally derives from
-- gross_profit_resolved (not raw gross_profit) for maximum coverage --
-- run AFTER gross_profit_resolved is populated, see concept_fallback.py's
-- ARITHMETIC_FALLBACKS list ordering.

insert into analytics.canonical_concept (name, statement, combination_mode, description)
values
    ('gross_profit_resolved', 'income_statement', 'first_match',
     'Prefers the reported gross_profit tag when present for a period, else derives Revenue - Cost of Revenue when both are present AND revenue > 0 (the guard that keeps this immune to a separately-flagged revenue-resolves-to-authoritative-$0 bug, see doc/learnings/2026-09-07-statement-table-coverage-and-revenue-zero-bug.md). Populated by mapper/concept_fallback.py, NOT resolve.py.'),
    ('cost_of_revenue_resolved', 'income_statement', 'first_match',
     'Prefers the reported cost_of_revenue tag when present, else derives Revenue - Gross Profit when both are present AND revenue > 0. Populated by mapper/concept_fallback.py, NOT resolve.py.'),
    ('operating_expenses_resolved', 'income_statement', 'first_match',
     'Prefers the reported operating_expenses tag when present, else derives gross_profit_resolved - Operating Income when both present (no revenue guard needed -- gross_profit_resolved already carries its own guard when it was itself derived). Populated by mapper/concept_fallback.py, NOT resolve.py.')
on conflict (name) do nothing;
