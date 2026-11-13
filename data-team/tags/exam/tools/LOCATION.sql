set local statement_timeout='120s';
-- Location-member facts (IncomeStatementLocationAxis) for amortization of intangibles, D&A and SBC, latest 10-K, full year.
-- Dhairya 2026-11-13 (CSCO): an undimensioned fact that is only a location slice -> component_sum of the location members.
-- Default: latest 10-K per CIK (<CIKS>). --accession mode (tools/render_sql.py) swaps the f CTE for accession in (<ACCESSIONS>).
with f as (select distinct on (cik) id, cik, accession, period from fsn.filing where form='10-K' and cik in (<CIKS>) order by cik, period desc),
t as (select id, tag from fsn.tag where tag in ('AmortizationOfIntangibleAssets','DepreciationDepletionAndAmortization','DepreciationAndAmortization','Depreciation','ShareBasedCompensation','AllocatedShareBasedCompensationExpense'))
select f.cik, f.accession acc, string_agg(distinct t.tag || '@' || d.segments || '=' || round(v.value, 4)::text || '/' || coalesce(v.dcml::text, ''), '|') facts
from f join fsn.value v on v.filing_id = f.id join t on t.id = v.tag_id join fsn.dim d on d.id = v.dim_id
where v.dim_id <> 0 and v.coreg = '' and v.iprx = 0 and v.ddate = f.period and v.qtrs = 4
  and d.segments like 'StatementOfIncomeLocation%' and d.segments not like '%;%;%'
group by f.cik, f.accession;
