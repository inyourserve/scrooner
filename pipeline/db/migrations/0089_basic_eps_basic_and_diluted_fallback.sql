-- basic_eps: EarningsPerShareBasicAndDiluted as a priority-2 fallback
-- (2026-10-10, data_limit ticket deep dive).
--
-- A simple-capital-structure company reports ONE combined EPS tag because
-- basic and diluted EPS are identical by definition. diluted_eps already
-- maps this tag (concepts.py, 2026-10-03, priority 3); basic_eps did not,
-- so those companies showed a permanent basic-EPS gap mislabeled
-- "data_limit" (no mapped tag in the filing).
--
-- Checked live before adding: 22,368 same-period (company, period) pairs
-- carry both tags, 19,334 (86.4%) agree within 1% -- the same agreement
-- rate that justified the diluted_eps mapping. 49,801 authoritative pairs
-- across 2,022 companies carry ONLY the combined tag. Priority 2 behind
-- EarningsPerShareBasic, so first_match only reaches it when the primary
-- tag is absent for that exact period -- it never overrides.

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'approved',
    '2026-10-10, verified: combined basic+diluted EPS tag used by simple-capital-structure filers; 86.4% agreement with EarningsPerShareBasic where both exist; fallback only when the primary tag is absent for the period.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'basic_eps'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'EarningsPerShareBasicAndDiluted'
on conflict (canonical_concept_id, concept_id) do nothing;
