-- K12a@1: periodic filings since 2026-07-01 with zero facts (fixed cut-off, comparable over time).
-- Chunk of 100 ids. READ ONLY. NOT RUN by the author. core.fact.filing_id has an index (migration 0019).
select f.company_id, count(*) as filings
from core.filing f
where f.company_id = any(%(ids)s) and f.form in ('10-Q','10-K') and f.filing_date >= date '2026-07-01'
  and not exists (select 1 from core.fact x where x.filing_id = f.id)
group by f.company_id;
