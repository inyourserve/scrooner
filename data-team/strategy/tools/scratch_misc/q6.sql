select distinct on (f.company_id) f.company_id, f.accession_number, f.form, f.filing_date, f.period_of_report from core.filing f where f.company_id in (4432,1409,3113,105,1928,3406,3062,4637,1740,2835,2003,2031,1,2052,635,318,4325,4294,3885,1168,1553,5480,4969,1488,1886,2746,1427,5023,1171,688,1733,611,605,1439,2566,2889,1036,1925,5307,391) and f.form in ('10-K','10-K/A','10-KT') order by f.company_id, (f.form='10-K') desc, f.filing_date desc
;
select id, accession_number, form, filing_date from core.filing where company_id=5307 order by filing_date desc limit 5
