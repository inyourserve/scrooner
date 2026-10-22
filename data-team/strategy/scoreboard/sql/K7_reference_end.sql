-- K7 reference date per company (chunk of 100 ids). READ ONLY. NOT RUN by the author.
-- The staleness thresholds (400 / 230 days) are NOT in SQL: sb_lib.staleness_thresholds() reads them
-- from pipeline/src/scrooner_pipeline/common/staleness.py (AT-7.12).
select company_id, max(period_of_report) as ref_end
from core.filing
where company_id = any(%(ids)s) and period_of_report is not null
  and form in ('10-K','10-K/A','10-KT','10-KT/A','10-Q','10-Q/A','10-QT','10-QT/A','20-F','20-F/A','40-F','40-F/A')
group by company_id;
