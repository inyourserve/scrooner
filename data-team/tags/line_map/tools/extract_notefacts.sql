-- Read-only input for resolve_all.py: consolidated facts at each 10-K's own column (qtrs 0/4) for every element family
-- the role rules name (rules/roles.csv), batched by CIK. Built and split by tools/standard_inputs.py (the placeholders below).
-- Output rows (accession, vals, mvals, cvals):
--   vals  'tag|qtrs|value~...'            undimensioned own-period facts (notefacts.json); accretion facts (%Accretion%) ride along:
--                                         the D&A accretion-evidence rule (resolve_is.accretion_reported) reads them from here.
--   mvals 'tag|qtrs|value|segments~...'   own-period facts with exactly ONE dimension member, on a statement line (face, incl.
--                                         parenthetical); axes EquityComponents (equity-statement column), RelatedPartyTransactionsByRelatedParty
--                                         (NonrelatedParty / RelatedParty: COP AP) and Scenario (ORCL comprehensive income). memberfacts.json.
--   cvals 'tag|qtrs|value|ddate~...'      undimensioned facts of the filing's earlier columns (FY-1, FY-2), face or note, incl. parenthetical
--                                         per-share lines (LLY DPS 2016 sits in the FY2018 equity parenthetical). compfacts.json.
-- Families: the element regex of rules/roles.csv plus the balance-sheet / cash-flow family modules; mvals also takes the AP/AR names.
set statement_timeout='55s';
with fl as (select id, accession, period from fsn.filing where cik::bigint in (/* CIKs */) and form='10-K' and period>='2014-06-01'),
tg as (select id, tag from fsn.tag where not custom and (tag ~ '^(/* element families from rules/roles.csv */)$' or tag like '%Accretion%')),
tgm as (select id, tag from fsn.tag where not custom and (tag ~ '^(/* element families from rules/roles.csv */)$' or tag ~ '^(AccountsPayable|AccountsReceivable|AccountsAndNotesReceivable|Receivables|DueTo|DueFrom)')),
own as (select fl.accession a, string_agg(concat_ws('|',t.tag,v.qtrs,v.value::text),'~') vals
  from fsn.value v join fl on fl.id=v.filing_id join tg t on t.id=v.tag_id
  where v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate=fl.period and v.qtrs in (0,4) and v.value is not null
  group by 1),
mem as (select fl.accession a, string_agg(concat_ws('|',t.tag,v.qtrs,v.value::text,d.segments),'~') mvals
  from fsn.value v join fl on fl.id=v.filing_id join tgm t on t.id=v.tag_id join fsn.dim d on d.id=v.dim_id
  where v.dim_id<>0 and coalesce(v.coreg,'')='' and v.ddate=fl.period and v.qtrs in (0,4) and v.value is not null
    and d.segments ~ '^(EquityComponents|RelatedPartyTransactionsByRelatedParty|Scenario)=[^;=]+;$'
    and exists (select 1 from fsn.line l where l.filing_id=fl.id and l.tag_id=v.tag_id)
  group by 1),
cmp as (select fl.accession a, string_agg(concat_ws('|',t.tag,v.qtrs,v.value::text,v.ddate::text),'~') cvals
  from fsn.value v join fl on fl.id=v.filing_id join tg t on t.id=v.tag_id
  where v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate<fl.period and v.ddate>=fl.period-interval '3 years 2 months' and v.qtrs in (0,4) and v.value is not null
  group by 1)
select fl.accession a, own.vals, mem.mvals, cmp.cvals
from fl left join own on own.a=fl.accession left join mem on mem.a=fl.accession left join cmp on cmp.a=fl.accession
where own.vals is not null or mem.mvals is not null or cmp.cvals is not null;
