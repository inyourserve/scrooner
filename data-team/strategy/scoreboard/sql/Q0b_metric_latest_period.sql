-- Q0b-metric: the period of the row that defines has_value (same ordering as build_coverage).
-- READ ONLY. NOT RUN by the author. Chunk <= 25 ids; statement_timeout 60s.
select mv.company_id, md.metric_name as data_point_name,
       (array_agg(mv.period_end   order by mv.period_end desc, mv.period_start desc, mv.period_label))[1] as latest_period_end,
       (array_agg(mv.period_label order by mv.period_end desc, mv.period_start desc, mv.period_label))[1] as latest_label,
       (array_agg(mv.value is not null order by mv.period_end desc, mv.period_start desc, mv.period_label))[1] as latest_has_value
from analytics.metric_value mv
join analytics.metric_definition md on md.id = mv.metric_definition_id
where mv.company_id = any(%(ids)s) and md.status = 'active'
group by mv.company_id, md.metric_name;
