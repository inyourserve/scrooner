-- 2026-09-12: employee_count coverage was 3.7% because the canonical
-- concept only ever mapped the sparse dei:EntityNumberOfEmployees XBRL
-- tag -- it never read core.employee_headcount_disclosure (the 10-K
-- prose-extraction table built 2026-08-31/09-01, already covering 2,951
-- companies with zero new fetches needed) or yfinance's fullTimeEmployees.
-- New employee_count_resolved concept (zero concept_mapping rows, same
-- "prefer A else B else C" idiom as total_debt_resolved/revenue_sanity_resolved)
-- merges all three tiers.
insert into analytics.canonical_concept (name, statement, combination_mode, description)
values ('employee_count_resolved', 'balance_sheet', 'first_match', 'Employee headcount -- prefers XBRL dei:EntityNumberOfEmployees, else 10-K prose extraction, else yfinance fullTimeEmployees')
on conflict (name) do nothing;

-- yfinance employee-count fallback tier, same shape/naming as the
-- existing y_sector/y_industry/y_about_text/y_website columns.
alter table core.company add column if not exists y_employee_count bigint;
alter table core.company add column if not exists y_employee_count_status text;
alter table core.company add column if not exists y_employee_count_updated_at timestamptz;
