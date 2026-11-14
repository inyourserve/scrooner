-- Read-only input for resolve_all.py: undimensioned, consolidated facts at each 10-K's own column (qtrs 0/4) for every
-- element family the role rules name (rules/roles.csv), batched by CIK. Output rows (accession, 'tag|qtrs|value~...') -> notefacts.json.
-- Families: see the regex in the two pulls of 2026-11-14 (cash/supplemental, per-share, weighted shares, SBC, amortization,
-- comprehensive income, DPS, shares outstanding, bank lines; and the face-line families for the note fallback).
set statement_timeout='55s';
with fl as (select id, accession, period from fsn.filing where cik::bigint in (/* CIKs */) and form='10-K' and period>='2014-06-01'),
-- accretion facts (any standard tag matching %Accretion%) ride along: the D&A accretion-evidence rule
-- (resolve_is.accretion_reported, ACC_EVID) reads them from this input, and filters equity / loan accretion itself.
tg as (select id, tag from fsn.tag where not custom and (tag ~ '^(/* element families from rules/roles.csv */)$' or tag like '%Accretion%'))
select fl.accession a, string_agg(concat_ws('|',t.tag,v.qtrs,v.value::text),'~') vals
from fsn.value v join fl on fl.id=v.filing_id join tg t on t.id=v.tag_id
where v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate=fl.period and v.qtrs in (0,4) and v.value is not null
group by 1;
