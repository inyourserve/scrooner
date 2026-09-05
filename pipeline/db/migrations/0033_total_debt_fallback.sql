-- total_debt fallback resolver (doc 40, 2026-09-02). Closes a real,
-- previously-declined gap named in expanded_concepts.py's own docstring:
-- 360 companies report split debt tags (LongTermDebtCurrent +
-- LongTermDebtNoncurrent) instead of the combined LongTermDebt tag
-- total_debt's existing `sum`-mode mapping relies on -- but naively
-- adding the split tags to that same sum-mode mapping would double-
-- count debt for the ~2,168 companies that report BOTH forms (resolve.py's
-- `sum` mode has no "prefer group A, else group B" logic -- confirmed by
-- reading it directly).
--
-- Design: two NEW concepts, resolve.py/calculate.py both reused
-- completely unchanged (per this project's own established idiom for
-- every additive Mapper extension so far):
--   total_debt_split: sum mode over just the 2 split tags -- genuinely
--     additive, no double-count risk BETWEEN these two tags themselves
--     (current + noncurrent portions are mutually exclusive slices).
--     Resolved via the existing, unmodified resolve() call.
--   total_debt_resolved: a THIRD concept, populated by a new standalone
--     module (mapper/concept_fallback.py), NOT by resolve() -- has zero
--     concept_mapping rows, so resolve() naturally produces zero rows
--     for it and never conflicts with what concept_fallback.py writes.
--     Prefers total_debt when present, else total_debt_split, per
--     (company, period) -- the same "prefer resolved value A, else B"
--     idiom already live in expanded_metrics.py's/price_metrics.py's
--     shares-outstanding fallback.

insert into analytics.canonical_concept (name, statement, combination_mode, description)
values
    ('total_debt_split', 'balance_sheet', 'sum', 'Sum of LongTermDebtCurrent + LongTermDebtNoncurrent -- a fallback source for total_debt, used only when the combined LongTermDebt tag is absent. Never consumed directly by any metric; see total_debt_resolved.'),
    ('total_debt_resolved', 'balance_sheet', 'first_match', 'Prefers total_debt (the combined-tag concept) when present for a period, else falls back to total_debt_split (the split-tag sum) -- populated by mapper/concept_fallback.py, NOT by resolve.py (zero concept_mapping rows on purpose, so resolve() never writes here). Every metric that previously consumed total_debt directly (debt_to_equity, roic, net_debt_ebitda, ev_ebitda, ev_sales) should read this concept instead.')
on conflict (name) do nothing;

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 1, 'approved', 'Split-tag debt components -- mutually exclusive current/noncurrent slices, genuinely additive, verified 2026-09-02 (see doc 40).'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'total_debt_split'
  and cn.taxonomy = 'us-gaap'
  and cn.tag in ('LongTermDebtCurrent', 'LongTermDebtNoncurrent')
on conflict (canonical_concept_id, concept_id) do nothing;
