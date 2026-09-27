"""SEC Tag Library (2026-09-27, migration 0077) -- every XBRL tag, every
company that files it, and per (company, canonical concept) the exact tag
behind our value. Direct founder direction: "make a SEC tag library ...
tag -> metric, then company ... same as metric to company to tag mapping
... cover all the tag, and all the companies."

Three layers, all rebuilt from source tables, never hand-edited:
  analytics.company_sec_tag          company x tag   (~2.0M rows)
  analytics.sec_tag_library          tag -> companies/concepts/metrics
  analytics.company_concept_lineage  company x concept -> source tag(s)
plus the view analytics.metric_company_tag_lineage (metric -> company ->
concept -> tag).

The payoff is `gap_tags()`: for companies MISSING a concept, which tags
they file that the concept doesn't map -- ranked by company count. This
replaces finding mapping gaps by hand one company at a time (Chevron's
total debt sat under an unmapped tag the whole time).

Built in company-id chunks, each its own delete-then-insert + commit, so
a Supabase pooler drop mid-build costs one chunk, not the run (same
pattern as security_type.py / yfinance_industry.py). Everything is set-
based SQL -- no per-row Python loop over core.fact (76M rows)."""

import psycopg
import structlog

from scrooner_pipeline.common.config import settings

logger = structlog.get_logger()

CHUNK_SIZE = 150

_COMPANY_SEC_TAG_SQL = """
insert into analytics.company_sec_tag
    (company_id, concept_id, fact_count, first_period_end, last_period_end, latest_value, latest_period_type)
select f.company_id, f.concept_id, count(*),
       min(p.end_date), max(p.end_date),
       (array_agg(f.value order by p.end_date desc, f.id desc))[1],
       (array_agg(p.period_type order by p.end_date desc, f.id desc))[1]
from core.fact f
join core.period p on p.id = f.period_id
where f.company_id = any(%(ids)s) and f.is_authoritative
group by f.company_id, f.concept_id
"""

_LINEAGE_SQL = """
with cos as (select unnest(%(ids)s::bigint[]) as company_id),
latest as (
    select distinct on (cf.company_id, cf.canonical_concept_id)
           cf.company_id, cf.canonical_concept_id, p.end_date, cf.value, cf.source_fact_ids
    from analytics.canonical_fact cf
    join core.period p on p.id = cf.period_id
    where cf.company_id = any(%(ids)s) and cf.value is not null
    order by cf.company_id, cf.canonical_concept_id, p.end_date desc, p.period_type desc
),
src as (
    select l.company_id, l.canonical_concept_id,
           array_agg(distinct c.taxonomy || ':' || c.tag order by c.taxonomy || ':' || c.tag) as tags
    from latest l
    cross join lateral unnest(l.source_fact_ids) as sid(fact_id)
    join core.fact f on f.id = sid.fact_id
    join core.concept c on c.id = f.concept_id
    group by 1, 2
),
mapped as (
    select t.company_id, m.canonical_concept_id,
           array_agg(distinct c.taxonomy || ':' || c.tag order by c.taxonomy || ':' || c.tag) as tags
    from analytics.company_sec_tag t
    join analytics.concept_mapping m on m.concept_id = t.concept_id and m.confidence in ('approved', 'provisional')
    join core.concept c on c.id = t.concept_id
    where t.company_id = any(%(ids)s)
    group by 1, 2
),
cand as (
    select t.company_id, k.canonical_concept_id,
           array_agg(distinct k.taxonomy || ':' || k.tag order by k.taxonomy || ':' || k.tag) as tags
    from analytics.company_sec_tag t
    join core.concept c on c.id = t.concept_id
    join analytics.concept_tag_candidate k on k.taxonomy = c.taxonomy and k.tag = c.tag
    where t.company_id = any(%(ids)s)
    group by 1, 2
)
insert into analytics.company_concept_lineage
    (company_id, canonical_concept_id, has_value, latest_period_end, latest_value,
     source_tags, mapped_tags_filed, candidate_tags_filed, gap_reason)
select cos.company_id, cc.id,
       latest.company_id is not null,
       latest.end_date, latest.value,
       coalesce(src.tags, '{}'), coalesce(mapped.tags, '{}'), coalesce(cand.tags, '{}'),
       cov.gap_reason
from cos
cross join analytics.canonical_concept cc
left join latest on latest.company_id = cos.company_id and latest.canonical_concept_id = cc.id
left join src on src.company_id = cos.company_id and src.canonical_concept_id = cc.id
left join mapped on mapped.company_id = cos.company_id and mapped.canonical_concept_id = cc.id
left join cand on cand.company_id = cos.company_id and cand.canonical_concept_id = cc.id
left join analytics.company_data_point_coverage cov
       on cov.company_id = cos.company_id and cov.data_point_name = cc.name
"""

_LIBRARY_SQL = """
with usage as (
    select t.concept_id,
           count(*) as company_count,
           count(*) filter (where co.status = 'active') as active_company_count,
           sum(t.fact_count) as fact_count,
           min(t.first_period_end) as first_period_end,
           max(t.last_period_end) as last_period_end
    from analytics.company_sec_tag t
    join core.company co on co.id = t.company_id
    group by 1
),
mapping as (
    select m.concept_id,
           array_agg(distinct cc.name order by cc.name) filter (where m.confidence in ('approved', 'provisional')) as concepts,
           bool_or(m.confidence = 'approved') as any_approved,
           bool_or(m.confidence = 'provisional') as any_provisional,
           bool_or(m.confidence = 'rejected') as any_rejected
    from analytics.concept_mapping m
    join analytics.canonical_concept cc on cc.id = m.canonical_concept_id
    group by 1
),
pref as (
    -- tags is jsonb: [{"tag": ..., "taxonomy": ...}]; older rows only have tag/taxonomy
    select distinct c.id as concept_id
    from analytics.company_tag_preference p
    cross join lateral (
        select e ->> 'taxonomy' as taxonomy, e ->> 'tag' as tag
        from jsonb_array_elements(coalesce(p.tags, '[]'::jsonb)) as e
        union
        select p.taxonomy, p.tag
    ) as t
    join core.concept c on c.taxonomy = t.taxonomy and c.tag = t.tag
),
cand as (
    select c.id as concept_id, array_agg(distinct cc.name order by cc.name) as concepts
    from analytics.concept_tag_candidate k
    join core.concept c on c.taxonomy = k.taxonomy and c.tag = k.tag
    join analytics.canonical_concept cc on cc.id = k.canonical_concept_id
    group by 1
),
metrics as (
    select m.concept_id, array_agg(distinct md.metric_name order by md.metric_name) as metrics
    from analytics.concept_mapping m
    join analytics.metric_definition_input i on i.canonical_concept_id = m.canonical_concept_id
    join analytics.metric_definition md on md.id = i.metric_definition_id
    where m.confidence in ('approved', 'provisional')
    group by 1
)
insert into analytics.sec_tag_library
    (concept_id, taxonomy, tag, company_count, active_company_count, fact_count,
     first_period_end, last_period_end, mapping_status, mapped_concepts,
     candidate_for_concepts, feeds_metrics)
select c.id, c.taxonomy, c.tag,
       coalesce(u.company_count, 0), coalesce(u.active_company_count, 0), coalesce(u.fact_count, 0),
       u.first_period_end, u.last_period_end,
       case when mp.any_approved then 'approved'
            when mp.any_provisional then 'provisional'
            when pref.concept_id is not null then 'company_preference'
            when cand.concept_id is not null then 'candidate'
            when mp.any_rejected then 'rejected'
            else 'unmapped' end,
       coalesce(mp.concepts, '{}'), coalesce(cand.concepts, '{}'), coalesce(metrics.metrics, '{}')
from core.concept c
left join usage u on u.concept_id = c.id
left join mapping mp on mp.concept_id = c.id
left join pref on pref.concept_id = c.id
left join cand on cand.concept_id = c.id
left join metrics on metrics.concept_id = c.id
"""


def _chunks(ids: list[int], size: int = CHUNK_SIZE) -> list[list[int]]:
    return [ids[i : i + size] for i in range(0, len(ids), size)]


def _company_ids(conn: psycopg.Connection, ciks: set[str] | None) -> list[int]:
    with conn.cursor() as cur:
        if ciks:
            cur.execute(
                "select id from core.company where cik = any(%s) order by id",
                (list(ciks),),
            )
        else:
            # every company with any stored fact -- "all companies", not just active
            cur.execute(
                "select id from core.company c where exists (select 1 from core.fact f where f.company_id = c.id) order by id"
            )
        return [r[0] for r in cur.fetchall()]


def _run_chunked(conn, ids, table, insert_sql, stage) -> psycopg.Connection:
    for n, chunk in enumerate(_chunks(ids), 1):
        for attempt in (1, 2):
            try:
                with conn.cursor() as cur:
                    cur.execute("set statement_timeout = 0")
                    cur.execute(
                        f"delete from {table} where company_id = any(%s)", (chunk,)
                    )
                    cur.execute(insert_sql, {"ids": chunk})
                conn.commit()
                break
            except psycopg.OperationalError:
                if attempt == 2:
                    raise
                logger.warning("tag_library.reconnect", stage=stage, chunk=n)
                conn = psycopg.connect(settings.database_url)
        logger.info(
            "tag_library.chunk_done",
            stage=stage,
            chunk=n,
            of=len(ids) // CHUNK_SIZE + 1,
        )
    return conn


def build_tag_library(
    conn: psycopg.Connection,
    ciks: set[str] | None = None,
    stages: set[str] | None = None,
) -> dict:
    """stages: subset of {"company_tags", "library", "lineage"}; default all,
    in that order (library and lineage both read company_sec_tag)."""
    stages = stages or {"company_tags", "library", "lineage"}
    ids = _company_ids(conn, ciks)
    if "company_tags" in stages:
        conn = _run_chunked(
            conn, ids, "analytics.company_sec_tag", _COMPANY_SEC_TAG_SQL, "company_tags"
        )
    if "library" in stages:
        with conn.cursor() as cur:
            cur.execute("set statement_timeout = 0")
            cur.execute("delete from analytics.sec_tag_library")
            cur.execute(_LIBRARY_SQL)
        conn.commit()
    if "lineage" in stages:
        conn = _run_chunked(
            conn, ids, "analytics.company_concept_lineage", _LINEAGE_SQL, "lineage"
        )
    with conn.cursor() as cur:
        cur.execute(
            """select (select count(*) from analytics.company_sec_tag),
                      (select count(*) from analytics.sec_tag_library),
                      (select count(*) from analytics.company_concept_lineage)"""
        )
        company_tags, tags, lineage = cur.fetchone()
    stats = {
        "companies": len(ids),
        "company_sec_tag_rows": company_tags,
        "sec_tag_library_rows": tags,
        "lineage_rows": lineage,
    }
    logger.info("tag_library.done", **stats)
    return stats


def gap_tags(
    conn: psycopg.Connection,
    concept_name: str,
    limit: int = 30,
    active_only: bool = True,
    period_type: str | None = None,
) -> list[dict]:
    """For companies that do NOT have `concept_name`, rank every tag they
    file by how many of them file it. A lead list, never an approval --
    doc 40's lesson: tags sharing vocabulary are often a different concept,
    so each lead still needs a coexistence check before concept_mapping."""
    with conn.cursor() as cur:
        cur.execute(
            """
            with missing as (
                select l.company_id from analytics.company_concept_lineage l
                join analytics.canonical_concept cc on cc.id = l.canonical_concept_id
                join core.company co on co.id = l.company_id
                where cc.name = %(concept)s and not l.has_value
                  and (not %(active_only)s or co.status = 'active')
            )
            select lib.taxonomy || ':' || lib.tag, lib.mapping_status, lib.mapped_concepts,
                   count(*) as missing_companies_filing,
                   (select count(*) from missing) as missing_total
            from missing m
            join analytics.company_sec_tag t on t.company_id = m.company_id
            join analytics.sec_tag_library lib on lib.concept_id = t.concept_id
            where %(period_type)s::text is null or t.latest_period_type = %(period_type)s
            group by 1, 2, 3
            order by 4 desc
            limit %(limit)s
            """,
            {
                "concept": concept_name,
                "active_only": active_only,
                "period_type": period_type,
                "limit": limit,
            },
        )
        return [
            {
                "tag": r[0],
                "status": r[1],
                "mapped_concepts": r[2],
                "missing_companies_filing": r[3],
                "missing_total": r[4],
            }
            for r in cur.fetchall()
        ]
