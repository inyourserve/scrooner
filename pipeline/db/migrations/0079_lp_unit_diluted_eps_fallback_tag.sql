-- diluted_eps: per-limited-partnership-unit diluted earnings as the
-- lowest-priority fallback (2026-09-27, beta data-completeness audit).
--
-- Master limited partnerships (Energy Transfer, MPLX, Plains, Sunoco,
-- Western Midstream, Alliance Resource) report earnings per unit, not per
-- share, under this tag and never file EarningsPerShareDiluted. So they had
-- no EPS and no P/E. For a partnership, per-unit earnings IS its EPS.
--
-- Priority 2 behind EarningsPerShareDiluted, so first_match only uses it
-- for a company-period with no per-share figure. Checked across every
-- company that files it: 36 companies, zero periods with more than one
-- distinct authoritative value. FY2025 values match reported per-unit
-- earnings: ET $1.21, MPLX $4.82, EPD $2.66, WES $2.98.

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'provisional',
    'Verified 2026-09-27: MLP per-unit diluted earnings, used only when EarningsPerShareDiluted is absent for the period. Zero conflicting values across all 36 filers.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'diluted_eps'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'NetIncomeLossNetOfTaxPerOutstandingLimitedPartnershipUnitDiluted'
on conflict (canonical_concept_id, concept_id) do nothing;
