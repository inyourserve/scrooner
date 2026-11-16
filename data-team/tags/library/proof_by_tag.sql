-- Refresh data-team/tags/library/proof_by_tag.csv (read-only): analytics.cell_proof aggregated by shown_tag.
set statement_timeout='90s';
select shown_tag as element, count(*) as proof_cells, count(*) filter (where verdict='PROVEN') as proven_cells,
       count(distinct company_id) as proof_companies, max(proved_at)::date as last_proved
from analytics.cell_proof where shown_tag is not null and shown_tag !~ '[+\-\[]' group by 1 order by 2 desc;
