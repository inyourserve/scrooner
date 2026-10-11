-- period_gap.gap_cause: two evidence-based causes split out of 'no_mapped_tag'
-- (2026-10-10, data_limit ticket deep dive). 'no_mapped_tag' was filed as
-- finding_type 'data_limit' ("not reachable from our sources"), but a live
-- sample showed it mixed three different things:
--   unmapped_candidate_tag -- the filing DOES carry a known-equivalent tag we
--       don't map (pipeline_bug: fix by mapping it);
--   no_line_item_filed     -- the filing reports no such line item at all
--       (legitimate_absence: e.g. a loss-making shell with no income-tax line);
--   no_mapped_tag          -- what remains, still unexplained (data_limit).
alter table analytics.period_gap drop constraint period_gap_gap_cause_check;
alter table analytics.period_gap add constraint period_gap_gap_cause_check check (gap_cause in (
    'filing_not_processed', 'not_in_sec_feed', 'conflict_rounding', 'conflict_split',
    'conflict_material', 'not_resolved', 'q4_not_derived', 'quarter_not_derived',
    'no_mapped_tag', 'unmapped_candidate_tag', 'no_line_item_filed'
));
