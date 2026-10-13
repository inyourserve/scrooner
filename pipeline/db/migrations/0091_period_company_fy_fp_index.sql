-- Found live 2026-10-13: sanity/timeseries_check.py's _load_yoy_pairs()
-- self-joins core.period on (company_id, fiscal_year, fiscal_period) to
-- find the prior-year comparison period, with no supporting index --
-- confirmed via EXPLAIN that core.period (982K rows) had only
-- period_pkey and a (company_id, start_date, end_date, period_type)
-- unique constraint, neither usable for this join. At the data volume
-- this project has grown to (core.period 982K rows, canonical_fact
-- 16.8M rows), this made the check pathologically slow -- compounded by
-- (and easy to mistake for) a separate, real connectivity degradation
-- hit the same night that made every long-running query unreliable
-- regardless. This index is additive and safe at any table size.
create index if not exists idx_period_company_fy_fp
    on core.period (company_id, fiscal_year, fiscal_period);
