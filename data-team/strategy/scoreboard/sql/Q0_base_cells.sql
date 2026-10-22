-- Q0: cell extract (one chunk of at most 100 company ids). READ ONLY. NOT RUN by the author.
-- Gate before every chunk: select count(*) from pg_stat_activity must be <= 14. One connection,
-- statement_timeout 60s. Parameter: %(ids)s = array of company ids from doc/data-moat/team/top1000/shards.csv
-- (non-excluded rows). Test information_schema for has_value_any_period first (exists only after
-- migration 0096); extract_live.py picks the variant below. Allowed sources: coverage table + registry.
-- variant A (0096 NOT applied):
select cov.company_id, cov.data_point_name, r.data_point_type,
       cov.has_value, cov.gap_reason, cov.checked_at
from analytics.company_data_point_coverage cov
join analytics.data_point_registry r on r.data_point_name = cov.data_point_name
where cov.company_id = any(%(ids)s);
-- variant B (0096 applied): same, plus   cov.has_value_any_period   (NULL, not false, on concept rows)
