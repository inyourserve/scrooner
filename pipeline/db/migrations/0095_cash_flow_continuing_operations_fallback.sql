-- cash_flow_investing / cash_flow_financing: the ...ContinuingOperations
-- totals as priority-2 fallbacks (2026-10-13, data_limit ticket triage).
--
-- cfo already maps NetCashProvidedByUsedInOperatingActivitiesContinuingOperations
-- at priority 2; investing and financing did not, so filers that tag only
-- the continuing-operations total (typically those with discontinued
-- operations) showed permanent gaps filed as data_limit.
--
-- Checked live before adding (authoritative facts only): the tags are the
-- SOLE cash-flow total for 28,718 (investing) / 29,111 (financing)
-- company-periods across about 1,700 companies each. Where both tags exist
-- for the same period they agree within 1% in 80% (investing, 21,250 of
-- 26,485) and 88% (financing, 21,825 of 24,736) of pairs; the rest are
-- filers with discontinued operations, where the continuing-operations
-- total is a subset. Priority 2 behind the plain total, so first_match
-- uses it only when the plain total is absent for that exact period.

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'approved',
    '2026-10-13, verified: continuing-operations cash-flow total, used only when the plain total is absent for the period; 80-88% agreement with the plain tag where both exist, the remainder being filers with discontinued operations.'
from analytics.canonical_concept cc
join core.concept cn on cn.taxonomy = 'us-gaap'
 and cn.tag = case cc.name
        when 'cash_flow_investing' then 'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations'
        when 'cash_flow_financing' then 'NetCashProvidedByUsedInFinancingActivitiesContinuingOperations'
     end
where cc.name in ('cash_flow_investing', 'cash_flow_financing')
on conflict (canonical_concept_id, concept_id) do nothing;
