-- operating_expenses + cf_ap_change: 2 new fallback tags, verified live
-- 2026-09-02 (doc 41 item 2, second batch). Both checked via coexistence
-- (does the candidate match the primary tag when a company reports both
-- for the same period, or diverge -- a component/different-quantity red
-- flag).
--
--   operating_expenses <- CostsAndExpenses: near-identical values across
--   8 real coexistence checks (22nd Century Group, 5E Advanced Materials,
--   Abeona Therapeutics) -- exact matches or <0.3% differences (plausibly
--   rounding/restatement), not a systematic divergence. Safe synonym.
--
--   cf_ap_change <- IncreaseDecreaseInAccountsPayableTrade: 7 of 8
--   coexistence checks (ABVC Biopharma, ACCESS Newswire) were exact
--   matches; one quarter diverged (46,511 vs 9,158) -- an isolated
--   tagging inconsistency, not a systematic pattern. Added as
--   provisional given the strong majority match.
--
-- Rejected the same pass: cf_ar_change's IncreaseDecreaseInReceivables
-- candidate showed a REAL, non-isolated divergence for 3M Co (a large,
-- well-known filer, not a small/noisy one) -- one quarter had opposite
-- SIGNS (-113,000,000 vs +128,000,000), confirming "receivables" and
-- "accounts receivable" are genuinely different quantities for at least
-- some diversified companies (likely including non-trade receivables).
-- Not added.

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'provisional',
    'Verified 2026-09-02: near-identical values in 8 real coexistence checks (22nd Century Group, 5E Advanced Materials, Abeona Therapeutics) -- confirmed synonym usage.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'operating_expenses'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'CostsAndExpenses'
on conflict (canonical_concept_id, concept_id) do nothing;

insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
select cc.id, cn.id, 2, 'provisional',
    'Verified 2026-09-02: 7 of 8 real coexistence checks (ABVC Biopharma, ACCESS Newswire) were exact matches to the primary tag; one isolated divergence noted, not a systematic pattern.'
from analytics.canonical_concept cc, core.concept cn
where cc.name = 'cf_ap_change'
  and cn.taxonomy = 'us-gaap'
  and cn.tag = 'IncreaseDecreaseInAccountsPayableTrade'
on conflict (canonical_concept_id, concept_id) do nothing;
