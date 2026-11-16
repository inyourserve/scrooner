set statement_timeout='115s';
-- Read-only. BS-family extract: BS face lines (own-period, undimensioned value), the balance-sheet parenthetical (BS lines with inpth) share values at the
-- balance sheet date including ClassOfStock dimension segments, and the filing's calc arcs. __CIKS__ = comma list of CIKs.
-- which filings belong to the company: the shared rule (common/company_filings.py, fsn_filings_cte), embedded verbatim; `cik` below is the COMPANY's cik
with company_filings as (
 select f.id, co.id as company_id, co.cik, f.cik as filer_cik, f.accession, f.form, f.period, f.fy, f.fp, f.filed,
        case when f.cik = co.cik then 'own' else 'predecessor' end as via,
        case when f.cik <> co.cik and exists (select 1 from fsn.filing s
                         where s.cik = co.cik and s.period = f.period
                           and replace(s.form, '/A', '') = replace(f.form, '/A', '')
                           and not exists (select 1 from core.company_history_source x
                 where x.company_id = co.id and x.relation = 'exclude'
                   and s.period between x.valid_from and x.valid_to))
             then 'shell_successor_report' end as reason
 from core.company co
 join fsn.filing f on f.cik = any(array[co.cik] || array(
      select h.source_cik from core.company_history_source h where h.company_id = co.id and h.relation = 'predecessor'))
 where co.cik::bigint in (__CIKS__)
   and (
     (f.cik = co.cik and not exists (select 1 from core.company_history_source x
                 where x.company_id = co.id and x.relation = 'exclude'
                   and f.period between x.valid_from and x.valid_to)
      and not exists (select 1 from fsn.filing p
                      where p.cik = any(array(select h.source_cik from core.company_history_source h
                              where h.company_id = co.id and h.relation = 'predecessor'
                                and f.period between h.valid_from and h.valid_to))
                        and p.period = f.period and replace(p.form, '/A', '') = replace(f.form, '/A', '')
                        and ((select count(*) from fsn.filing ff join fsn.line fln on fln.filing_id = ff.id
          where ff.accession = f.accession and fln.stmt in ('BS', 'IS', 'CF') and not fln.inpth
            and exists (select 1 from fsn.value fv where fv.filing_id = fln.filing_id and fv.tag_id = fln.tag_id
                        and fv.dim_id = 0 and coalesce(fv.coreg, '') = '' and fv.ddate = ff.period
                        and fv.qtrs = (case when fln.stmt = 'BS' then 0 else 4 end)
                        and fv.value is not null)) * 4 < (select count(*) from fsn.filing ff join fsn.line fln on fln.filing_id = ff.id
          where ff.accession = p.accession and fln.stmt in ('BS', 'IS', 'CF') and not fln.inpth
            and exists (select 1 from fsn.value fv where fv.filing_id = fln.filing_id and fv.tag_id = fln.tag_id
                        and fv.dim_id = 0 and coalesce(fv.coreg, '') = '' and fv.ddate = ff.period
                        and fv.qtrs = (case when fln.stmt = 'BS' then 0 else 4 end)
                        and fv.value is not null)))))
     or (f.cik <> co.cik
         and exists (select 1 from core.company_history_source h
                     where h.company_id = co.id and h.relation = 'predecessor' and h.source_cik = f.cik
                       and f.period between h.valid_from and h.valid_to)
         and not exists (select 1 from fsn.filing s
                         where s.cik = co.cik and s.period = f.period
                           and replace(s.form, '/A', '') = replace(f.form, '/A', '')
                           and not exists (select 1 from core.company_history_source x
                 where x.company_id = co.id and x.relation = 'exclude'
                   and s.period between x.valid_from and x.valid_to)
                           and not ((select count(*) from fsn.filing ff join fsn.line fln on fln.filing_id = ff.id
          where ff.accession = s.accession and fln.stmt in ('BS', 'IS', 'CF') and not fln.inpth
            and exists (select 1 from fsn.value fv where fv.filing_id = fln.filing_id and fv.tag_id = fln.tag_id
                        and fv.dim_id = 0 and coalesce(fv.coreg, '') = '' and fv.ddate = ff.period
                        and fv.qtrs = (case when fln.stmt = 'BS' then 0 else 4 end)
                        and fv.value is not null)) * 4 < (select count(*) from fsn.filing ff join fsn.line fln on fln.filing_id = ff.id
          where ff.accession = f.accession and fln.stmt in ('BS', 'IS', 'CF') and not fln.inpth
            and exists (select 1 from fsn.value fv where fv.filing_id = fln.filing_id and fv.tag_id = fln.tag_id
                        and fv.dim_id = 0 and coalesce(fv.coreg, '') = '' and fv.ddate = ff.period
                        and fv.qtrs = (case when fln.stmt = 'BS' then 0 else 4 end)
                        and fv.value is not null)))))
   )
),
fl as (select id, cik, accession, period, filed from company_filings where form in ('10-K','20-F','40-F') and period>='2014-06-01'),
ln as (select l.filing_id, l.stmt, l.report, l.line, l.inpth, t.tag, t.custom, l.negating, l.prole, replace(replace(left(coalesce(l.plabel,''),60),'|',' '),'~',' ') lb, l.tag_id
 from fsn.line l join fl on fl.id=l.filing_id join fsn.tag t on t.id=l.tag_id where l.stmt in ('BS','CP')),
lv as (select ln.*, (select v.value from fsn.value v join fl f2 on f2.id=ln.filing_id where v.filing_id=ln.filing_id and v.tag_id=ln.tag_id and v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate=f2.period and v.qtrs=0 limit 1) val from ln where ln.stmt='BS' and not ln.inpth),
cp as (select ln.filing_id, ln.report, ln.line, ln.tag, ln.lb, d.segments seg, v.value
 from ln join fl f2 on f2.id=ln.filing_id join fsn.tag t2 on t2.tag=ln.tag join fsn.value v on v.filing_id=ln.filing_id and v.tag_id=t2.id and v.ddate=f2.period and v.qtrs=0 and coalesce(v.coreg,'')='' join fsn.dim d on d.id=v.dim_id
 where ln.stmt='BS' and ln.inpth and v.value is not null and v.uom='shares'),
ca as (select a.filing_id, a.grp, pt.tag p, ct.tag c, a.weight w from fsn.calc_arc a join fl on fl.id=a.filing_id join fsn.tag pt on pt.id=a.parent_tag_id join fsn.tag ct on ct.id=a.child_tag_id
 where exists (select 1 from ln where ln.filing_id=a.filing_id and ln.tag_id=a.parent_tag_id and ln.stmt='BS' and not ln.inpth))
select fl.cik::text cik, fl.accession a, fl.period::text p, fl.filed::text fd,
 (select string_agg(concat_ws('|',stmt,report,line,tag,custom::int,negating::int,coalesce(prole,''),lb,coalesce(val::text,'')),'~' order by stmt,report,line) from lv where lv.filing_id=fl.id) lines,
 (select string_agg(concat_ws('|',grp,p,c,w),'~') from ca where ca.filing_id=fl.id) calc,
 (select string_agg(concat_ws('|',report,line,tag,replace(lb,'~',' '),seg,value::text),'~' order by report,line) from cp where cp.filing_id=fl.id) cpv
from fl;
