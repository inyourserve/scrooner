-- accounts_receivable: 1 new fallback tag, verified live 2026-09-03
-- (doc 41 Priority 6). Checked via a full statistical coexistence check
-- (4,699 real period-pairs, not a sample): 62.5% exact match to the
-- primary AccountsReceivableNetCurrent tag -- the same statistical
-- profile as the already-approved `revenue` fallback tag (62.8% exact
-- match, migration 0038), which turned out safe in practice since
-- first_match mode can only fill gaps, never override a better value.
-- 275 new companies (zero prior accounts_receivable coverage) gain a
-- real value. Added at lowest priority for the same reason.
--
-- Rejected the same pass, with clear negative evidence: for
-- depreciation_and_amortization, OtherDepreciationAndAmortization
-- diverged 10%+ in 55.4% of 2,431 real coexisting pairs (a genuine
-- additional component, not a synonym). For sga_expense,
-- OtherSellingGeneralAndAdministrativeExpense diverged 10%+ in 84.8% of
-- 1,169 real pairs (clearly a separate supplementary line item most
-- filers add on top of, not instead of, their reported SG&A total).

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'provisional',
    'Verified 2026-09-03: 62.5% exact match across 4,699 real coexistence checks -- the same statistical profile as the already-approved revenue fallback tag. Priority 2 (lowest) so first_match never overrides the primary tag -- only fills a genuine gap (275 companies had zero accounts_receivable coverage at all).'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'accounts_receivable'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'AccountsReceivableNet'
on conflict (canonical_concept_id, concept_id) do nothing;
