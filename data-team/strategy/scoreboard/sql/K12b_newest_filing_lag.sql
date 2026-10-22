-- K12b@1: companies whose newest periodic filing is newer than their newest filing with any fact.
-- Chunk of 100 ids; returns the company ids (sum client-side). READ ONLY. NOT RUN by the author.
with p as (
  select f.company_id, f.filing_date,
         exists (select 1 from core.fact x where x.filing_id = f.id) as has_fact
  from core.filing f
  where f.company_id = any(%(ids)s) and f.form in ('10-K','10-K/A','10-Q','10-Q/A'))
select company_id from p group by company_id
having max(filing_date) > coalesce(max(filing_date) filter (where has_fact), date '1900-01-01');
