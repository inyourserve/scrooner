set local statement_timeout='90s';
with f as (select distinct on (cik) id,cik,accession,period from fsn.filing where cik in (<CIKS>) and form='10-K' order by cik, period desc),
f4 as (select distinct on (p.cik) p.id,p.cik from fsn.filing p join f on f.cik=p.cik where p.form='10-K' and p.period <= f.period - interval '3 years 10 months' order by p.cik, p.period desc),
l as (select f.cik,f.accession,f.period,l.report,l.line,l.stmt,l.inpth,l.plabel,l.negating,t.tag,t.version,t.crdr,l.tag_id,f.id fid from f join fsn.line l on l.filing_id=f.id join fsn.tag t on t.id=l.tag_id where l.stmt in ('BS','IS','CF','EQ','CI','UN')),
p4 as (select f4.cik, l.stmt, lower(l.plabel) pl, min(t.tag) ptag from f4 join fsn.line l on l.filing_id=f4.id join fsn.tag t on t.id=l.tag_id group by 1,2,3),
v as (select distinct on (l.fid,l.tag_id) l.fid,l.tag_id,v.value,v.dcml,v.qtrs from l join fsn.value v on v.filing_id=l.fid and v.tag_id=l.tag_id and v.dim_id=0 and v.coreg='' and v.iprx=0 and v.ddate=l.period order by l.fid,l.tag_id,v.qtrs desc)
select l.cik, l.accession acc, l.period::text per, l.stmt st, l.report r, l.line ln, l.inpth::int pth, l.negating::int neg, l.tag, (l.version !~ '^(us-gaap|dei|srt|ifrs)')::int cu, l.crdr cr, l.plabel lab, v.value::text val, v.dcml dc, v.qtrs q, p4.ptag prior
from l left join v on v.fid=l.fid and v.tag_id=l.tag_id left join p4 on p4.cik=l.cik and p4.stmt=l.stmt and p4.pl=lower(l.plabel)
order by l.cik, l.stmt, l.report, l.line;
