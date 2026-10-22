-- K4c@1: open findings by theme. Counts only, never used to classify a cell (finding_type is a lagging
-- label, CLAUDE.md). READ ONLY. NOT RUN by the author. Chunk of 100 ids.
select finding_type, status, count(*) as n
from analytics.company_data_finding
where company_id = any(%(ids)s)
group by 1, 2;
-- after migration 0097 is applied (separate statement, guarded by to_regclass('analytics.certification_finding')):
-- select invariant, severity, evidence->>'rule' as rule, count(*) as n
-- from analytics.certification_finding where resolved_at is null and company_id = any(%(ids)s) group by 1,2,3;
