-- B0(a) of the top-1000 fix plan (2026-10-19): has_value now means "the
-- company's LATEST period for the metric has a value". The previous meaning
-- ("any period ever had a value") is kept here as a secondary column so the
-- history is not lost and the overstatement can be measured.
alter table analytics.company_data_point_coverage
    add column if not exists has_value_any_period boolean;
