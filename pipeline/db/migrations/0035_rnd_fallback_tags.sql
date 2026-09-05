-- research_and_development: 2 new fallback tags, verified live 2026-09-02
-- (doc 41 item 2). Both confirmed genuinely additive, not a component/
-- subset trap:
--
--   ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost: 32
--   companies use this tag with ZERO rows under the primary
--   ResearchAndDevelopmentExpense tag at all -- a real, non-overlapping
--   substitute (e.g. 10x Genomics, Inc.), not a partial figure.
--
--   OtherResearchAndDevelopmentExpense: where it coexists with the
--   primary tag for the same company/period, the values are IDENTICAL
--   (374Water Inc.: 84656=84656, 140980=140980, 192827=192827, checked
--   across 8 real period pairs) -- direct evidence this is a synonym some
--   filers use, not a sub-component that would understate total R&D if
--   used alone. 5 companies use it with zero rows under the primary tag.
--
-- Rejected the same pass, with equally real (negative) evidence, not
-- assumed: interest_income's InterestIncomeOperating/InterestIncomeOther
-- candidates both showed real, non-proportional value divergence in
-- coexistence checks (e.g. AH Realty Trust: 229,000 vs 4,004,000 for the
-- same period -- a genuinely different quantity, not a synonym).
-- dividends_paid's PaymentsOfDividendsPreferredStockAndPreferenceStock
-- coexistence check showed a consistent SUBSET relationship (Alexandria
-- Real Estate: $22-28M candidate vs $96-321M primary, every year) --
-- adding it would understate total dividends paid for any company that
-- also pays common dividends without cleanly tagging them. Neither
-- rejection is chased further this pass; see doc 41 for the full
-- ranked-list update.

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'provisional',
    'Verified 2026-09-02: 32 companies (e.g. 10x Genomics) use this tag with zero rows under the primary ResearchAndDevelopmentExpense tag -- genuinely additive, not a component.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'research_and_development'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost'
on conflict (canonical_concept_id, concept_id) do nothing;

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 3, 'provisional',
    'Verified 2026-09-02: identical values to the primary tag when both coexist for the same company/period (374Water Inc., 8 real period pairs checked) -- a confirmed synonym, not a partial sub-component.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'research_and_development'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'OtherResearchAndDevelopmentExpense'
on conflict (canonical_concept_id, concept_id) do nothing;
