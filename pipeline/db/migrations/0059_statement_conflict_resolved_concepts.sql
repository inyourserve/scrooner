-- Generic conflict-fill resolved concepts (2026-09-09). Found live via a
-- real user report (Etsy's Q1/Q2/Q4 2025 revenue blank on the company
-- page) that dedupe.py's Stage 2e conflict policy ("2+ filings disagree
-- on a period's value -> mark ALL non-authoritative -> resolve() returns
-- null") is correct and deliberate (pipeline/CLAUDE.md's 2026-08-19
-- total_debt entry already documents this), but leaves a real, sizeable
-- number of statement-table cells blank for every concept, not just
-- revenue -- scoped live: 2,164 companies / 14,031 periods for revenue
-- alone; the same shape recurs across the other 23 statement-table rows.
--
-- Same "new resolved concept, zero concept_mapping rows, resolve() never
-- touches it" idiom as total_debt_resolved (0033) / gross_profit_resolved
-- (0047) / revenue_sanity_resolved (0049) -- but the fallback mechanism
-- here is neither a concept-vs-concept coalesce nor an arithmetic
-- derivation, it's a FILL-ONLY conflict reconciliation: for a (company,
-- period) where the primary concept resolves to null specifically because
-- every candidate fact under its mapped tags disagrees and none is
-- authoritative, and the worst-case disagreement is small (<=15%,
-- consistent with dedupe.py's own documented "small non-material
-- cross-filing revision" characterization -- NOT a blanket "trust most
-- recent" policy, which a real, larger regression this session already
-- caught and reverted proved unsafe when applied per-company/per-tag
-- instead of per-period), pick the most-recently-filed value. Populated
-- by mapper/conflict_resolution.py's resolve_conflict_fill(), which is
-- purely ADDITIVE (INSERT ... ON CONFLICT DO NOTHING, never a delete) --
-- it can only fill an existing null, never touch or remove a value any
-- other writer (resolve() or an existing arithmetic-fallback module)
-- already produced. Safe to run in any order, any number of times, after
-- any other Mapper stage.
--
-- The 5 statement-table concepts that already have their own `_resolved`
-- companion (revenue_sanity_resolved, cost_of_revenue_resolved,
-- gross_profit_resolved, operating_expenses_resolved, total_debt_resolved)
-- are NOT duplicated here -- resolve_conflict_fill() runs against their
-- existing resolved concept as an additional fill-only pass on top of
-- whatever arithmetic fallback already populated it, same function, no
-- special-casing needed since it only ever inserts into currently-null
-- slots.

insert into analytics.canonical_concept (name, statement, combination_mode, description)
values
    ('operating_income_resolved', 'income_statement', 'first_match', 'operating_income, plus a fill for periods where the tag conflicts across filings by <=15% and none is authoritative. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('interest_expense_resolved', 'income_statement', 'first_match', 'interest_expense, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('income_before_tax_resolved', 'income_statement', 'first_match', 'income_before_tax, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('income_tax_expense_resolved', 'income_statement', 'first_match', 'income_tax_expense, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('net_income_resolved', 'income_statement', 'first_match', 'net_income, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('diluted_eps_resolved', 'income_statement', 'first_match', 'diluted_eps, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('cash_and_equivalents_resolved', 'balance_sheet', 'first_match', 'cash_and_equivalents, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('current_assets_resolved', 'balance_sheet', 'first_match', 'current_assets, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('ppe_net_resolved', 'balance_sheet', 'first_match', 'ppe_net, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('total_assets_resolved', 'balance_sheet', 'first_match', 'total_assets, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('current_liabilities_resolved', 'balance_sheet', 'first_match', 'current_liabilities, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('total_liabilities_resolved', 'balance_sheet', 'first_match', 'total_liabilities, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('stockholders_equity_resolved', 'balance_sheet', 'first_match', 'stockholders_equity, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('cfo_resolved', 'cash_flow', 'first_match', 'cfo, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('capex_resolved', 'cash_flow', 'first_match', 'capex, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('cash_flow_investing_resolved', 'cash_flow', 'first_match', 'cash_flow_investing, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('cash_flow_financing_resolved', 'cash_flow', 'first_match', 'cash_flow_financing, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('dividends_paid_resolved', 'cash_flow', 'first_match', 'dividends_paid, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.'),
    ('share_buybacks_resolved', 'cash_flow', 'first_match', 'share_buybacks, plus a same-shape conflict fill. Populated by mapper/conflict_resolution.py, NOT resolve.py.')
on conflict (name) do nothing;
