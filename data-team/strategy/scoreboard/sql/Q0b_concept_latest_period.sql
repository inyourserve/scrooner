-- Q0b-concept: latest stored period of each concept cell. READ ONLY. NOT RUN by the author.
-- Chunk: at most 25 company ids per statement (core/canonical aggregates); statement_timeout 60s.
-- If the first chunk exceeds 60 s, halve the chunk; never raise the timeout.
select cf.company_id, cc.name as data_point_name,
       max(p.end_date) as latest_period_end,
       (array_agg(p.fiscal_period order by p.end_date desc, p.start_date desc))[1] as latest_label
from analytics.canonical_fact cf
join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
join core.period p on p.id = cf.period_id
where cf.company_id = any(%(ids)s)
group by cf.company_id, cc.name;
