-- Read-only companion of extract_notefacts.sql (same CIK batch, same element regex): the undimensioned own-period and earlier-column
-- facts of every element printed on a statement line (BS/IS/CF) of the filing that the family regex does not cover, plus custom
-- elements named like a family (case-insensitive: TMUS LongtermDebtandLongtermDebttoAffiliates). The core statement roles
-- (OperatingIncomeLoss, LOW/WMT GainsLossesOnExtinguishmentOfDebt), custom face debt lines (total_debt comparative column) and
-- treasury stock (member_facts) read these. Output rows (accession, vals, cvals, clines): vals / cvals in the extract_notefacts formats,
-- appended to that extract's by standard_inputs.merge_rows; clines 'tag|report|line|label~...' the comprehensive-income statement lines of
-- ComprehensiveIncome* elements (standard_inputs.ci_face_lines: the CI-incl-NCI point reason cites its line).
set statement_timeout='55s';
with rx as (select '^(/* element families from rules/roles.csv */)$'::text r),
-- which filings belong to the company: the shared rule (common/company_filings.py, fsn_filings_cte), embedded verbatim; `cik` below is the COMPANY's cik
company_filings as (
 select f.id, co.id as company_id, co.cik, f.cik as filer_cik, f.accession, f.form, f.period, f.fy, f.fp, f.filed,
        case when f.cik = co.cik then 'own' else 'predecessor' end as via
 from core.company co
 join fsn.filing f on f.cik = any(array[co.cik] || array(
      select h.source_cik from core.company_history_source h where h.company_id = co.id and h.relation = 'predecessor'))
 where co.cik::bigint in (/* CIKs */)
   and (
     (f.cik = co.cik and not exists (select 1 from core.company_history_source x
                 where x.company_id = co.id and x.relation = 'exclude'
                   and f.period between x.valid_from and x.valid_to))
     or (f.cik <> co.cik
         and exists (select 1 from core.company_history_source h
                     where h.company_id = co.id and h.relation = 'predecessor' and h.source_cik = f.cik
                       and f.period between h.valid_from and h.valid_to)
         and not exists (select 1 from fsn.filing s
                         where s.cik = co.cik and s.period = f.period
                           and replace(s.form, '/A', '') = replace(f.form, '/A', '')
                           and not exists (select 1 from core.company_history_source x
                 where x.company_id = co.id and x.relation = 'exclude'
                   and s.period between x.valid_from and x.valid_to)))
   )
),
fl as (select id, accession, period from company_filings where form in ('10-K','20-F','40-F') and period>='2014-06-01'),
ct as (select distinct fl.id fid, t.id, t.tag from fl join fsn.line l on l.filing_id=fl.id and l.stmt in ('BS','IS','CF') join fsn.tag t on t.id=l.tag_id
         where t.custom or not (t.tag ~ (select r from rx) or t.tag like '%Accretion%')
       union select distinct v.filing_id, t.id, t.tag from fsn.value v join fl on fl.id=v.filing_id
         join (select id, tag from fsn.tag where custom and tag ~* (select r from rx)) t on t.id=v.tag_id),
own as (select fl.accession a, string_agg(concat_ws('|',ct.tag,v.qtrs,v.value::text),'~') vals
  from fl join ct on ct.fid=fl.id join fsn.value v on v.filing_id=fl.id and v.tag_id=ct.id
  where v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate=fl.period and v.qtrs in (0,4) and v.value is not null group by 1),
cmp as (select fl.accession a, string_agg(concat_ws('|',ct.tag,v.qtrs,v.value::text,v.ddate::text),'~') cvals
  from fl join ct on ct.fid=fl.id join fsn.value v on v.filing_id=fl.id and v.tag_id=ct.id
  where v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate<fl.period and v.ddate>=fl.period-interval '3 years 2 months' and v.qtrs in (0,4) and v.value is not null group by 1),
cl as (select fl.accession a, string_agg(concat_ws('|',t.tag,l.report,l.line,translate(coalesce(l.plabel,''),'|~','/-')),'~') clines
  from fl join fsn.line l on l.filing_id=fl.id and l.stmt='CI' join fsn.tag t on t.id=l.tag_id and t.tag ~ '^ComprehensiveIncome'
  group by 1)
select fl.accession a, own.vals, cmp.cvals, cl.clines from fl left join own on own.a=fl.accession left join cmp on cmp.a=fl.accession left join cl on cl.a=fl.accession
where own.vals is not null or cmp.cvals is not null or cl.clines is not null;