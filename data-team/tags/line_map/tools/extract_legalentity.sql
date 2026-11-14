-- Read-only, run only for the filings whose face (BS/IS/CF) has no undimensioned own-period value (standard_run.py finds them
-- in the assembled filings.json): the own-period values of the face elements that carry exactly one LegalEntity member, with the
-- co-registrant name. Combined filings present the statements by legal entity (CEG FY2021: Constellation Energy Generation LLC).
-- Output rows (accession, lvals 'tag|qtrs|value|member|coreg~...'); standard_inputs.legal_entity_faces reads them.
set statement_timeout='55s';
with nf as (select id, accession, period from fsn.filing where accession in (/* ACCESSIONS */))
select nf.accession a, string_agg(distinct concat_ws('|',t.tag,v.qtrs,v.value::text,substr(d.segments,13,length(d.segments)-13),coalesce(v.coreg,'')),'~') lvals
  from nf join fsn.line l on l.filing_id=nf.id and l.stmt in ('BS','IS','CF') join fsn.tag t on t.id=l.tag_id
  join fsn.value v on v.filing_id=nf.id and v.tag_id=l.tag_id and v.ddate=nf.period and v.qtrs in (0,4) and v.value is not null
  join fsn.dim d on d.id=v.dim_id and d.segments ~ '^LegalEntity=[^;=]+;$'
  group by 1;
