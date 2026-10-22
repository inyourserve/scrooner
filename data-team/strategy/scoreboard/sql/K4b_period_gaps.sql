-- K4b@1: open period gaps (unit = missing PERIOD, never added to cell counts; F9). Chunk of 100 ids.
-- READ ONLY. NOT RUN by the author. period_gap is joined to names through canonical_concept.
select cc.name as data_point_name, g.gap_cause, g.period_kind, count(*) as n
from analytics.period_gap g
join analytics.canonical_concept cc on cc.id = g.canonical_concept_id
where g.company_id = any(%(ids)s)
group by 1, 2, 3;
