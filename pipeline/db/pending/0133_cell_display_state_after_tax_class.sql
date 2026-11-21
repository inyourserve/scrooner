-- 0133: add hide class 'only_after_tax_disclosed' to analytics.cell_display_state (ruling 2026-11-21, Dhairya: share-based
-- compensation a filing discloses ONLY after tax is never served as sbc; VZ FY2017-25 and GE FY2015-17 reads hide the year
-- with this class). 0130 is applied, so its file is not edited (ledger rule, doc 53): this file replaces the CHECK.
-- Value set = cell_display_state.HIDE_CLASSES (pipeline/src/scrooner_pipeline/mapper/cell_display_state.py).
-- Until this is applied, a write of a hidden cell of the new class fails the old CHECK (no such resolver row exists yet).
-- ROLLBACK: alter table analytics.cell_display_state drop constraint cell_display_state_hide_class_check;
--           alter table analytics.cell_display_state add constraint cell_display_state_hide_class_check check (hide_class in
--           ('structural_not_presented', 'line_presented_combined', 'pre_filing', 'verified_absent'));
alter table analytics.cell_display_state drop constraint if exists cell_display_state_hide_class_check;
alter table analytics.cell_display_state add constraint cell_display_state_hide_class_check
    check (hide_class in ('structural_not_presented', 'line_presented_combined', 'pre_filing', 'verified_absent',
                          'only_after_tax_disclosed'));
