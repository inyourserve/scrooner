set statement_timeout='115s';
-- Read-only. BS-family extract: BS face lines (own-period, undimensioned value), the balance-sheet parenthetical (BS lines with inpth) share values at the
-- balance sheet date including ClassOfStock dimension segments, and the filing's calc arcs. __CIKS__ = comma list of CIKs.
with fl as (select id, cik, accession, period, filed from fsn.filing where cik::bigint in (__CIKS__) and form='10-K' and period>='2014-06-01'),
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
