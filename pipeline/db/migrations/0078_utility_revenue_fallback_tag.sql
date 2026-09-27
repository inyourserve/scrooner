-- revenue: RegulatedAndUnregulatedOperatingRevenue as the lowest-priority
-- fallback (2026-09-27, beta data-completeness audit).
--
-- Found because DTE Energy's and Xcel Energy's stock pages showed 2017 and
-- 2018 as their latest revenue. Both moved their income-statement total
-- to this utility tag after ASC 606 and stopped filing any mapped revenue
-- tag, so every later year was blank.
--
-- 2026-09-12 rejected this tag as a global widening: across ~4,800
-- coexisting pairs it disagreed with Revenues 62% of the time (Alliant
-- files it for both its total and a segment-only value). That risk does
-- not apply at priority 6. first_match only uses it for a company-period
-- with no value under any of the five tags above, so Alliant and every
-- other company that already has revenue is untouched.
--
-- Checked on exactly the periods it fills: 20 companies, 636 periods,
-- zero with more than one distinct authoritative value. Latest FY values
-- match each company's scale: DTE $15.81B (FY2025), Xcel $14.67B
-- (FY2025), Southwest Gas $1.94B, MGE Energy $0.74B.

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 6, 'provisional',
    'Verified 2026-09-27: lowest priority, fills only company-periods with no other revenue tag (utilities that moved to this tag, e.g. DTE, Xcel). Zero conflicting values across the 636 periods it fills. Rejected as a global mapping 2026-09-12 (disagrees with Revenues 62% where both exist); first_match at priority 6 never reaches those periods.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'revenue'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'RegulatedAndUnregulatedOperatingRevenue'
on conflict (canonical_concept_id, concept_id) do nothing;
