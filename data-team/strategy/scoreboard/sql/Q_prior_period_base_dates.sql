-- Prior-period base dates: for each quarter-label prior-period gap, the real period_start / period_end of the base
-- period, so the "base before 2015-01-01" count is made on DATES, not fiscal labels (labels are unreliable, core.period
-- comment). READ ONLY. NOT RUN by the author (no database in this task).
-- Input arrays come from lists/prior_period_quarter_label_bases_2026-10-20.csv: company ids, base fiscal years, base
-- fiscal periods (Q1..Q4). Chunk of at most 100 triples; one connection; statement_timeout 60s; connections <= 14.
-- Result per input row: every core.period with that fiscal label (a label can map to more than one real period).
select t.company_id, t.fy, t.fp, p.start_date, p.end_date, p.period_type
from unnest(%(company_ids)s::bigint[], %(fys)s::int[], %(fps)s::text[]) as t(company_id, fy, fp)
left join core.period p
       on p.company_id = t.company_id and p.fiscal_year = t.fy and p.fiscal_period = t.fp
      and p.period_type = 'duration';
-- The count is then: input rows whose EVERY matching period has start_date < date '2015-01-01' (all-before),
-- split from rows with at least one match before 2015 (any-before), and rows with no match (no_period_found).
