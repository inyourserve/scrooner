# Queries behind the playbooks (read-only; run with `set statement_timeout = '15s'`)

Concept ids (analytics.canonical_concept, read 2026-11-09): 206 gross_profit, 207 cost_of_revenue, 219 revenue_sanity, 249 operating_income, 250 interest_expense, 251 income_before_tax, 252 income_tax_expense, 253 net_income, 254 diluted_eps, 262 cfo, 266 dividends_paid, 267 share_buybacks, 291 basic_eps, 292 dividends_per_share, 350 shares_outstanding (all `_resolved`).

Non-dimensional facts in `fsn.value`: `dim_id = 0 and coreg = ''` (not NULL).

```sql
-- the unit: latest non-amended 10-K per company, and the 632 with line_map rows
with f as materialized (select distinct on (company_id) id, company_id, cik, period from fsn.filing
                        where form='10-K' and not amendment order by company_id, period desc, accepted desc),
m as materialized (select distinct f.company_id, f.id, f.cik, f.period from f join fsn.line_map lm on lm.filing_id = f.id)
select count(*) from m;

-- mapped tag distribution for a concept
... select lm.canonical_concept_id, lm.rule_id, t.tag, l.stmt, count(distinct f.company_id)
from f join fsn.line_map lm on lm.filing_id=f.id and lm.status='mapped' and lm.canonical_concept_id in (...)
join fsn.line l on (l.filing_id, l.report, l.line) = (lm.filing_id, lm.report, lm.line)
join fsn.tag t on t.id = l.tag_id group by 1,2,3,4;

-- gap companies for concept C, and their unmapped candidate lines
has as materialized (select distinct m.company_id from m join fsn.line_map lm on lm.filing_id=m.id and lm.canonical_concept_id = C),
gap as materialized (select * from m where company_id not in (select company_id from has))
select t.tag, t.custom, coalesce(lm.status,'-'), count(distinct g.company_id), min(l.plabel)
from gap g join fsn.line l on l.filing_id=g.id and l.stmt='IS' join fsn.tag t on t.id=l.tag_id
left join fsn.line_map lm on (lm.filing_id, lm.report, lm.line) = (l.filing_id, l.report, l.line)
where <label/tag pattern> group by 1,2,3 order by 4 desc;

-- interest: gross tags anywhere in the gap filing (notes included), FY, non-dimensional
gt as materialized (select id, tag from fsn.tag where not custom and tag in
  ('InterestExpense','InterestExpenseNonoperating','InterestExpenseDebt','InterestAndDebtExpense','InterestCostsIncurred','InterestExpenseOperating'))
select g.company_id, gt.tag from gap g join fsn.value v on v.filing_id=g.id and v.ddate=g.period and v.qtrs=4
  and v.dim_id=0 and v.coreg='' join gt on gt.id=v.tag_id;

-- where a tag sits (statement, parenthetical or not, mapper status)
select tg.tag, l.stmt, (r.shortname ~* 'parenthetical') paren, coalesce(lm.status,'-'), count(distinct m.company_id)
from m join fsn.line l on l.filing_id=m.id join tg on tg.id=l.tag_id
join fsn.report r on (r.filing_id, r.report) = (l.filing_id, l.report)
left join fsn.line_map lm on (lm.filing_id, lm.report, lm.line) = (l.filing_id, l.report, l.line) group by 1,2,3,4;
```

Performance: joining `fsn.report` with a `menucat` filter across all 873 filings timed out at 15 s; materialise the tag ids first and probe `fsn.line` through `idx_fsn_line_tag` or `(filing_id, stmt, ...)`.
