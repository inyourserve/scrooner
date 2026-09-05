-- comprehensive_income: 1 new fallback tag, verified live 2026-09-03
-- (doc 41 item 2, third batch). Checked via coexistence: where a company
-- reports both the primary ComprehensiveIncomeNetOfTax tag and this
-- candidate for the same period, values are close (small differences
-- consistent with a noncontrolling-interest adjustment, e.g. 1-800-Flowers
-- $18,015K primary vs $17,974K candidate, $11,935K vs $11,571K) -- not the
-- large, systematic divergence a genuinely different quantity would show.
--
-- Rejected the same pass, with clear negative evidence:
-- effective_tax_rate_reported has NO safe candidate at all -- every
-- candidate in the tag universe checked is a component of the statutory-
-- to-effective RECONCILIATION (state/local adjustments, deferred tax
-- valuation allowance, etc.), never the effective rate itself.
-- interest_expense's InterestExpenseOther candidate showed massive,
-- systematic divergence on real companies (1st Source Corp: $53.1M
-- primary vs $550K candidate for the same period, a ~96x difference;
-- 1847 Holdings: $4.59M vs $49.7K, ~92x) -- clearly a small residual
-- sub-bucket, not a total-interest-expense substitute.

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'provisional',
    'Verified 2026-09-03: close match to the primary tag in real coexistence checks (1-800-Flowers, 8 period pairs) -- small differences consistent with a noncontrolling-interest adjustment, not a different quantity.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'comprehensive_income'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest'
on conflict (canonical_concept_id, concept_id) do nothing;
