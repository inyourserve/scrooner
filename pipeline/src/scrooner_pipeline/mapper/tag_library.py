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
from psycopg.types.json import Jsonb

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


# Verdicts mirrored from concept_mapping; an 'investigation' verdict for the
# same (tag, concept) is never overwritten -- a recorded finding outranks
# the mapping table's bare confidence.
_SYNC_VERDICTS_SQL = """
insert into analytics.tag_concept_verdict (taxonomy, tag, canonical_concept_id, verdict, reason, source)
select c.taxonomy, c.tag, cm.canonical_concept_id,
       case cm.confidence when 'approved' then 'approved'
                          when 'rejected' then 'rejected'
                          else 'needs_review' end,
       coalesce(nullif(cm.notes, ''), 'concept_mapping confidence=' || cm.confidence),
       'concept_mapping'
from analytics.concept_mapping cm
join core.concept c on c.id = cm.concept_id
on conflict (taxonomy, tag, canonical_concept_id) do update
    set verdict = excluded.verdict, reason = excluded.reason, decided_at = now()
    where analytics.tag_concept_verdict.source = 'concept_mapping'
"""
_PRUNE_VERDICTS_SQL = """
delete from analytics.tag_concept_verdict v
where v.source = 'concept_mapping'
  and not exists (
      select 1 from analytics.concept_mapping cm
      join core.concept c on c.id = cm.concept_id
      where c.taxonomy = v.taxonomy and c.tag = v.tag
        and cm.canonical_concept_id = v.canonical_concept_id)
"""

# Verdicts that mean "don't propose this tag for this concept again".
EXCLUDED_VERDICTS = ("rejected", "different_concept", "partial_component")

# Tag leads per concept, with value evidence (2026-09-30). A first version
# ranked by lift (tags distinctive of companies missing a concept) and was
# nonsense for sparse concepts -- AssetsCurrent "led" BDC income. A lead now
# needs two things:
#   1. It is filed by companies that SHOULD have the concept (its
#      data_point_registry.applicable_population) but don't.
#   2. Its values agree with the concept where both exist: for companies
#      that have the concept and file the tag for the same period, the share
#      of values within LEAD_AGREE_TOLERANCE. This is the coexistence check
#      every mapping change already needs, run automatically.
# Only concepts with concept_mapping rows (the ones a tag can fill) get
# leads; mapped tags and tags with a rejected / different_concept /
# partial_component verdict are skipped.
LEAD_MIN_COMPANIES = 10
LEAD_CANDIDATES_PER_CONCEPT = 40
LEAD_MIN_PAIRS = 20
LEAD_MIN_AGREE_RATE = 0.5
LEAD_AGREE_TOLERANCE = 0.02
LEADS_PER_CONCEPT = 25
# Scored one concept at a time over the last ~4 years only: one query over
# every candidate tag x all history joined 76M-row core.fact at once and
# risked large temp-file spills -- the production disk went read-only
# (2026-09-30) while that query and a population-wide rewrite ran together.
LEAD_EVIDENCE_DAYS = 1460
_LEAD_CANDIDATES_SQL = """
create temp table lead_candidates on commit drop as
with missing as (
    select l.canonical_concept_id, l.company_id
    from analytics.company_concept_lineage l
    join analytics.canonical_concept cc on cc.id = l.canonical_concept_id
    join analytics.data_point_registry r on r.data_point_name = cc.name
    join analytics.company_population cp
      on cp.company_id = l.company_id and cp.population_name = r.applicable_population
    where not l.has_value
      and exists (select 1 from analytics.concept_mapping cm where cm.canonical_concept_id = l.canonical_concept_id)
),
filed as (
    select m.canonical_concept_id, t.concept_id, count(*) as miss_f
    from missing m
    join analytics.company_sec_tag t on t.company_id = m.company_id
    where t.last_period_end >= current_date - 730
    group by 1, 2
    having count(*) >= %(min_companies)s
),
eligible as (
    select f.*, row_number() over (partition by f.canonical_concept_id order by f.miss_f desc) as rnk
    from filed f
    join analytics.sec_tag_library lib on lib.concept_id = f.concept_id
    where not exists (
          select 1 from analytics.concept_mapping cm
          where cm.concept_id = f.concept_id and cm.canonical_concept_id = f.canonical_concept_id)
      and not exists (
          select 1 from analytics.tag_concept_verdict v
          where v.taxonomy = lib.taxonomy and v.tag = lib.tag
            and v.canonical_concept_id = f.canonical_concept_id
            and v.verdict = any(%(excluded)s))
)
select canonical_concept_id, concept_id, miss_f from eligible where rnk <= %(candidates)s
"""
_LEAD_SCORE_SQL = """
with scored as (
    select c.canonical_concept_id, c.concept_id, c.miss_f,
           count(*) as pairs,
           count(*) filter (where abs(f.value - cf.value) <= %(tolerance)s * abs(cf.value)) as agree
    from lead_candidates c
    join core.fact f on f.concept_id = c.concept_id and f.is_authoritative
    join core.period p on p.id = f.period_id and p.end_date >= current_date - %(evidence_days)s
    join analytics.canonical_fact cf
      on cf.company_id = f.company_id and cf.period_id = f.period_id
     and cf.canonical_concept_id = c.canonical_concept_id and cf.value <> 0
    where c.canonical_concept_id = %(concept)s
    group by 1, 2, 3
),
ranked as (
    select *, agree::numeric / pairs as agree_rate,
           row_number() over (partition by canonical_concept_id
                              order by (agree::numeric / pairs) * miss_f desc) as rnk
    from scored
    where pairs >= %(min_pairs)s and agree::numeric / pairs >= %(min_agree)s
)
insert into analytics.concept_gap_lead
    (canonical_concept_id, concept_id, missing_companies_filing, rank, coexist_pairs, agree_rate)
select canonical_concept_id, concept_id, miss_f, rnk, pairs, round(agree_rate, 3)
from ranked where rnk <= %(per_concept)s
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
    """stages: subset of {"company_tags", "library", "lineage", "leads"};
    default all, in that order (library and lineage read company_sec_tag;
    leads read library + lineage). With `ciks`, company_tags and lineage
    refresh just those companies; library, verdict sync and leads are
    always population-wide (each one set-based statement)."""
    stages = stages or {"company_tags", "library", "lineage", "leads"}
    ids = _company_ids(conn, ciks)
    if "company_tags" in stages:
        conn = _run_chunked(
            conn, ids, "analytics.company_sec_tag", _COMPANY_SEC_TAG_SQL, "company_tags"
        )
    if "library" in stages:
        with conn.cursor() as cur:
            cur.execute("set statement_timeout = 0")
            cur.execute(_SYNC_VERDICTS_SQL)
            cur.execute(_PRUNE_VERDICTS_SQL)
            cur.execute("delete from analytics.sec_tag_library")
            cur.execute(_LIBRARY_SQL)
        conn.commit()
    if "lineage" in stages:
        conn = _run_chunked(
            conn, ids, "analytics.company_concept_lineage", _LINEAGE_SQL, "lineage"
        )
    if "leads" in stages:
        with conn.cursor() as cur:
            cur.execute("set statement_timeout = 0")
            cur.execute("delete from analytics.concept_gap_lead")
            cur.execute(
                _LEAD_CANDIDATES_SQL,
                {
                    "min_companies": LEAD_MIN_COMPANIES,
                    "candidates": LEAD_CANDIDATES_PER_CONCEPT,
                    "excluded": list(EXCLUDED_VERDICTS),
                },
            )
            cur.execute("select distinct canonical_concept_id from lead_candidates")
            for (concept,) in cur.fetchall():
                cur.execute(
                    _LEAD_SCORE_SQL,
                    {
                        "concept": concept,
                        "evidence_days": LEAD_EVIDENCE_DAYS,
                        "tolerance": LEAD_AGREE_TOLERANCE,
                        "min_pairs": LEAD_MIN_PAIRS,
                        "min_agree": LEAD_MIN_AGREE_RATE,
                        "per_concept": LEADS_PER_CONCEPT,
                    },
                )
        conn.commit()
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
    conn: psycopg.Connection, concept_name: str, limit: int = 25
) -> list[dict]:
    """Ranked tag leads for companies MISSING `concept_name`, from
    analytics.concept_gap_lead (lift-ranked, already excluding mapped tags
    and tags with a rejected / different_concept / partial_component
    verdict). A lead list, never an approval: doc 40's lesson is that tags
    sharing vocabulary are often a different concept, so each lead still
    needs a coexistence check, then record_verdict() either way."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select lib.taxonomy || ':' || lib.tag, gl.missing_companies_filing, gl.rank,
                   lib.active_company_count, lib.mapped_concepts, gl.coexist_pairs, gl.agree_rate,
                   (select count(*) from analytics.company_concept_lineage l
                     join core.company co on co.id = l.company_id and co.status = 'active'
                    where l.canonical_concept_id = gl.canonical_concept_id and not l.has_value)
            from analytics.concept_gap_lead gl
            join analytics.canonical_concept cc on cc.id = gl.canonical_concept_id
            join analytics.sec_tag_library lib on lib.concept_id = gl.concept_id
            where cc.name = %s
            order by gl.rank
            limit %s
            """,
            (concept_name, limit),
        )
        return [
            {
                "tag": r[0],
                "missing_companies_filing": r[1],
                "rank": r[2],
                "active_companies_filing": r[3],
                "mapped_to_other_concepts": r[4],
                "coexist_pairs": r[5],
                "agree_rate": r[6],
                "missing_total": r[7],
            }
            for r in cur.fetchall()
        ]


def gap_report(conn: psycopg.Connection, limit: int = 20) -> dict:
    """The fix queue: concepts ranked by unexplained missing market cap,
    metrics by unexplained missing companies, and the biggest companies
    missing core data."""
    with conn.cursor() as cur:
        cur.execute("set statement_timeout = 0")
        cur.execute(
            """select concept, coverage_pct, missing, missing_explained, missing_unexplained,
                      unexplained_market_cap, top_lead_tag, top_lead_companies, top_lead_agree_rate
               from analytics.data_gap_by_concept
               order by unexplained_market_cap desc nulls last, missing_unexplained desc
               limit %s""",
            (limit,),
        )
        concepts = cur.fetchall()
        cur.execute(
            """select metric_name, coverage_pct, missing, missing_unexplained, input_concepts
               from analytics.data_gap_by_metric
               order by missing_unexplained desc limit %s""",
            (limit,),
        )
        metrics = cur.fetchall()
        cur.execute(
            """select primary_ticker, company_name, market_cap, core_concepts_missing,
                      core_concepts_unexplained, missing_concepts, open_findings
               from analytics.data_gap_by_company
               where core_concepts_unexplained > 0
               order by market_cap desc nulls last limit %s""",
            (limit,),
        )
        companies = cur.fetchall()
    return {"concepts": concepts, "metrics": metrics, "companies": companies}


def _canonical_concept_id(cur, name: str) -> int:
    cur.execute("select id from analytics.canonical_concept where name = %s", (name,))
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"unknown canonical concept {name!r}")
    return row[0]


def record_verdict(
    conn: psycopg.Connection,
    tag: str,
    concept_name: str,
    verdict: str,
    reason: str,
    evidence: dict | None = None,
    taxonomy: str = "us-gaap",
) -> None:
    """Record what an investigation concluded about a (tag, concept) pair.
    Overrides a concept_mapping-mirrored verdict for the same pair."""
    with conn.cursor() as cur:
        concept_id = _canonical_concept_id(cur, concept_name)
        cur.execute(
            """
            insert into analytics.tag_concept_verdict
                (taxonomy, tag, canonical_concept_id, verdict, reason, evidence, source)
            values (%s, %s, %s, %s, %s, %s, 'investigation')
            on conflict (taxonomy, tag, canonical_concept_id) do update
                set verdict = excluded.verdict, reason = excluded.reason,
                    evidence = excluded.evidence, source = 'investigation', decided_at = now()
            """,
            (
                taxonomy,
                tag,
                concept_id,
                verdict,
                reason,
                Jsonb(evidence) if evidence else None,
            ),
        )
    conn.commit()


def record_finding(
    conn: psycopg.Connection,
    ticker: str,
    finding_type: str,
    summary: str,
    concept_name: str | None = None,
    status: str = "open",
    evidence: dict | None = None,
) -> None:
    """Record a per-company finding (bug, filer error, legitimate absence,
    data limit). Re-recording the same summary updates its status."""
    with conn.cursor() as cur:
        cur.execute(
            "select id from core.company where upper(primary_ticker) = upper(%s) order by (status = 'active') desc limit 1",
            (ticker,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"no company with primary ticker {ticker!r}")
        concept_id = _canonical_concept_id(cur, concept_name) if concept_name else None
        cur.execute(
            """
            insert into analytics.company_data_finding
                (company_id, canonical_concept_id, finding_type, status, summary, evidence, resolved_at)
            values (%s, %s, %s, %s, %s, %s, case when %s = 'open' then null else now() end)
            on conflict (company_id, canonical_concept_id, summary) do update
                set status = excluded.status, finding_type = excluded.finding_type,
                    evidence = coalesce(excluded.evidence, analytics.company_data_finding.evidence),
                    resolved_at = excluded.resolved_at
            """,
            (
                row[0],
                concept_id,
                finding_type,
                status,
                summary,
                Jsonb(evidence) if evidence else None,
                status,
            ),
        )
    conn.commit()
