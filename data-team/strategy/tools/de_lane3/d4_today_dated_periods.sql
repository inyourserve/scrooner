-- D-4 side effect list (read-only). Evidence label: DATA-INFERRED.
-- resolve_employee_count_fallback's yfinance tier created a core.period instant row dated the
-- run date for each yfinance fill. After D-4 these rows stay in core.period (never deleted).
-- A period is "yfinance-made" when an employee_count_resolved canonical row points at it with no
-- source facts and its end_date is not a report_date of a 10-K prose disclosure of that company.
-- Run: one connection, set statement_timeout = '20s', chunk by company id if it times out.
select p.id as period_id, p.company_id, p.end_date, p.fiscal_year, cf.value as yfinance_headcount
from analytics.canonical_fact cf
join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id and cc.name = 'employee_count_resolved'
join core.period p on p.id = cf.period_id
where (cf.source_fact_ids is null or cardinality(cf.source_fact_ids) = 0)
  and not exists (
    select 1 from core.employee_headcount_disclosure d
    where d.company_id = cf.company_id and d.report_date = p.end_date)
order by p.end_date, p.company_id;
