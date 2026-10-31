-- 0114 (claim in doc 53 before landing): a protected BLANK. NOT applied;
-- production applies need the founder's own words.
--
-- 0113 made analytics.slot_protected_cell.value NOT NULL (every protected key
-- carried a written slot value). The blank-reason release
-- slot.is_operating_income_not_presented@1 protects keys whose value is
-- deliberately ABSENT (the filing prints no operating income line), so a
-- nightly resolver cannot re-derive them. value null = a protected blank.
-- The guard trigger does not read value, so its behaviour is unchanged.

alter table analytics.slot_protected_cell alter column value drop not null;

comment on column analytics.slot_protected_cell.value is
    'the value the slot release wrote; null = a protected blank (blank-reason release)';
