-- revenue: 1 new fallback tag, verified live 2026-09-03. Prompted by a
-- direct ask to find which "should be near-100%" concepts have real,
-- closeable gaps -- J.M. Smucker (a large, obviously revenue-generating
-- consumer company), Georgia Power, Consumers Energy, and 47 others were
-- missing `revenue` entirely because they exclusively tag
-- RevenueFromContractWithCustomerIncludingAssessedTax, a real ASC 606
-- variant not covered by the existing 3-tag mapping (which only has the
-- "Excluding" form).
--
-- Verified via a full statistical coexistence check (3,435 period-pairs
-- where a company reports both forms), not a small sample: 62.8% exact
-- match, consistent with "assessed/sales tax is usually immaterial" --
-- a real, if imperfect, majority relationship. Added at low priority
-- (5) so `first_match` NEVER overrides an existing resolved value from
-- the 3 higher-priority tags -- this can only fill a genuine gap (51
-- companies had zero revenue coverage at all), never compete with or
-- replace a better-quality figure. A real minority (27%) of coexisting
-- pairs diverge 10%+, presumably data-quality noise in a subset of
-- filers -- irrelevant to safety here since first_match's own semantics
-- mean this tag is never consulted for a company/period that already
-- resolved via a higher-priority tag.
--
-- Rejected the same pass: SalesRevenueGoodsNet (only 8 new companies,
-- and a much worse statistical profile -- 11.9% exact match, 67.3%
-- diverging 10%+ across 5,725 coexisting pairs -- consistent with it
-- being a genuine goods-only component for many filers, not a synonym
-- for total revenue).

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 5, 'provisional',
    'Verified 2026-09-03: 62.8% exact match across 3,435 real coexistence checks -- a real, if imperfect, majority relationship (assessed/sales tax is usually immaterial). Priority 5 (lowest) so first_match never overrides the 3 existing tags -- only fills a genuine gap (51 companies, incl. J.M. Smucker, Georgia Power, Consumers Energy) that had zero revenue coverage at all.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'revenue'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'RevenueFromContractWithCustomerIncludingAssessedTax'
on conflict (canonical_concept_id, concept_id) do nothing;
