-- Adds "Other Income (Expense), Net" to the income statement walk-down,
-- right after Interest Expense (2026-09-08 -- see expanded_concepts.py's
-- other_income_expense_net docstring for the full finding: 1,618 of the
-- 2,368 companies whose Interest Expense goes blank in recent years
-- switched to this netted tag instead, a real closeable gap, not a
-- fabricated row).
--
-- Renumbers display_order 7-10 up by one to make room, same two-step
-- offset-then-set pattern as migration 0056 (avoids transiently
-- violating statement_line_statement_display_order_key).

update analytics.statement_line set display_order = display_order + 100
where statement = 'income_statement' and display_order >= 7;

update analytics.statement_line set display_order = display_order - 99
where statement = 'income_statement' and display_order >= 107;

insert into analytics.statement_line (statement, display_order, display_label, canonical_concept_id)
select 'income_statement', 7, 'Other Income (Expense), Net', id
from analytics.canonical_concept where name = 'other_income_expense_net';
