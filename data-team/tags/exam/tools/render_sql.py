"""Render LINES.sql / NOTES.sql / LOCATION.sql for the latest 10-K of each CIK or for named accessions (era extension).
Usage: render_sql.py TEMPLATE.sql --ciks 0000320193,... | --accession 0000320193-23-000106,... | --eras 0000320193,...
  --eras: every 10-K of those CIKs from FY2015 up to FY-2 (skips the latest two), as used for exam/eras/."""
import re, sys
tpl, mode, vals = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
s = open(tpl).read()
q = ','.join("'%s'" % v.strip() for v in vals if v.strip())
if mode == '--ciks':
    print(s.replace('<CIKS>', q))
elif mode == '--accession':
    s = re.sub(r"with f as \(select distinct on \(cik\) id, ?cik, ?accession, ?period from fsn\.filing where (?:cik in \(<CIKS>\) and form='10-K'|form='10-K' and cik in \(<CIKS>\)) order by cik, period desc\),",
               "with f as (select id, cik, accession, period from fsn.filing where form='10-K' and accession in (%s))," % q, s)
    assert "accession in (%s))" % q in s, 'template f CTE not recognised'
    print(s)
elif mode == '--eras':
    s = re.sub(r"with f as \(select distinct on \(cik\) id, ?cik, ?accession, ?period from fsn\.filing where (?:cik in \(<CIKS>\) and form='10-K'|form='10-K' and cik in \(<CIKS>\)) order by cik, period desc\),",
               "with f as (select id, cik, accession, period from (select id, cik, accession, period, row_number() over (partition by cik order by period desc) rn from fsn.filing where form='10-K' and cik in (%s)) z where rn>=3 and period>='2015-01-01')," % q, s)
    assert "rn>=3 and period>='2015-01-01'" in s, 'template f CTE not recognised'
    print(s)
else:
    sys.exit(__doc__)
