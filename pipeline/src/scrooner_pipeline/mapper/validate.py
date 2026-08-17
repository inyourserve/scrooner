"""Stage 3f -- validation and reconciliation checks (doc 11 Day 6).

Not new computation -- everything here reads back what Stages 3a-3e
already wrote and checks invariants that must hold if those stages are
correct: confidence states are genuinely spread across real curation
decisions (not just unused schema), no non-authoritative fact ever leaks
into a resolved value, and every source_fact_ids entry resolves to a real,
authoritative core.fact row. These are the same checks doc 08's
integrity.reconcile() and doc 09's Day 7 proof ran for their own phases,
adapted to what this phase actually writes (analytics.*, not raw/core).
"""

import psycopg
import structlog

logger = structlog.get_logger()


def confidence_distribution(conn: psycopg.Connection) -> list[tuple[str, int]]:
    with conn.cursor() as cur:
        cur.execute(
            "select confidence, count(*) from analytics.concept_mapping group by confidence order by confidence"
        )
        return cur.fetchall()


def non_authoritative_leaks(conn: psycopg.Connection) -> dict:
    """A canonical_fact or metric_value must never cite a core.fact that is
    not authoritative -- is_authoritative=false is a hard filter (doc 04),
    checked here directly rather than trusted from the resolver's own logic."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select count(*) from analytics.canonical_fact cf, unnest(cf.source_fact_ids) as fid
            join core.fact f on f.id = fid
            where f.is_authoritative = false
            """
        )
        canonical_fact_leaks = cur.fetchone()[0]
        cur.execute(
            """
            select count(*) from analytics.metric_value mv, unnest(mv.source_fact_ids) as fid
            join core.fact f on f.id = fid
            where f.is_authoritative = false
            """
        )
        metric_value_leaks = cur.fetchone()[0]
    return {"canonical_fact_leaks": canonical_fact_leaks, "metric_value_leaks": metric_value_leaks}


def lineage_integrity(conn: psycopg.Connection) -> dict:
    """Every non-null source_fact_ids entry across canonical_fact and
    metric_value must resolve to a real core.fact row -- a dangling id
    would silently break traceability (doc 04's core promise)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select count(*) from analytics.canonical_fact cf, unnest(cf.source_fact_ids) as fid
            left join core.fact f on f.id = fid
            where f.id is null
            """
        )
        canonical_fact_dangling = cur.fetchone()[0]
        cur.execute(
            """
            select count(*) from analytics.metric_value mv, unnest(mv.source_fact_ids) as fid
            left join core.fact f on f.id = fid
            where f.id is null
            """
        )
        metric_value_dangling = cur.fetchone()[0]
    return {"canonical_fact_dangling": canonical_fact_dangling, "metric_value_dangling": metric_value_dangling}


def run(conn: psycopg.Connection) -> dict:
    dist = confidence_distribution(conn)
    leaks = non_authoritative_leaks(conn)
    lineage = lineage_integrity(conn)
    clean = (
        leaks["canonical_fact_leaks"] == 0
        and leaks["metric_value_leaks"] == 0
        and lineage["canonical_fact_dangling"] == 0
        and lineage["metric_value_dangling"] == 0
    )
    result = {"confidence_distribution": dist, "leaks": leaks, "lineage": lineage, "clean": clean}
    logger.info("mapper.validate.done", clean=clean, leaks=leaks, lineage=lineage)
    return result
