"""Two-table coverage system (2026-09-05, by direct request) --
deliberately simple, no scoring/classification on top:

1. `analytics.data_point_registry` -- every concept/metric/ownership
   section this project tracks, and the SEC tag(s) it needs. Derived
   from `concept_mapping`/`metric_definition_input` (already the
   tag-requirement source of truth) -- rebuilt each run, not hand-
   maintained.
2. `analytics.company_data_point_coverage` -- one row per
   (company, data_point), has_value yes/no. Derived from
   `canonical_fact`/`metric_value`/the ownership tables -- a projection
   of data this project already has, not a new fetch or a new source of
   truth.

Ownership data points have no XBRL tag (Form 4/13F/N-PORT aren't XBRL) --
required_tags holds the SEC form type instead, the closest domain
equivalent to "what do I need to go fetch."
"""

import psycopg
import structlog

logger = structlog.get_logger()


def _tag_str(taxonomy: str, tag: str) -> str:
    return f"{taxonomy}:{tag}"


def build_registry(conn: psycopg.Connection) -> dict:
    """Rebuilds analytics.data_point_registry from concept_mapping and
    metric_definition_input -- always a fresh derivation, never edited
    by hand."""
    rows: list[dict] = []

    with conn.cursor() as cur:
        # LEFT JOIN, not INNER -- a concept with zero concept_mapping rows
        # (e.g. total_debt_resolved, populated by concept_fallback.py's
        # own "prefer A else B" logic rather than resolve()'s direct tag
        # matching) still needs a registry row, just with an empty tag
        # list, since canonical_fact rows for it genuinely exist and the
        # coverage table's cross-join below covers every canonical_concept
        # unconditionally.
        cur.execute(
            """
            select cc.name, coalesce(array_agg(distinct c.taxonomy || ':' || c.tag) filter (where c.tag is not null), '{}')
            from analytics.canonical_concept cc
            left join analytics.concept_mapping cm on cm.canonical_concept_id = cc.id
            left join core.concept c on c.id = cm.concept_id
            group by cc.name
            """
        )
        for name, tags in cur.fetchall():
            source = "mapper/resolve.py" if tags else "mapper/concept_fallback.py"
            rows.append({"data_point_name": name, "data_point_type": "concept", "required_tags": tags, "source_module": source})

        cur.execute(
            """
            select md.metric_name, array_agg(distinct c.taxonomy || ':' || c.tag)
            from analytics.metric_definition md
            join analytics.metric_definition_input mdi on mdi.metric_definition_id = md.id
            join analytics.concept_mapping cm on cm.canonical_concept_id = mdi.canonical_concept_id
            join core.concept c on c.id = cm.concept_id
            where md.status = 'active'
            group by md.metric_name
            """
        )
        metric_rows = {name: tags for name, tags in cur.fetchall()}

        # Metrics with no direct concept input (composite metrics reading
        # other metrics' own outputs, e.g. ev_ebitda reading ebitda +
        # market_cap) get an empty tag list here -- correct, not a bug:
        # their real "tags needed" is transitively their input metrics'
        # own registry rows, not a new XBRL tag of their own.
        cur.execute("select metric_name from analytics.metric_definition where status = 'active'")
        for (name,) in cur.fetchall():
            rows.append({"data_point_name": name, "data_point_type": "metric", "required_tags": metric_rows.get(name, []), "source_module": "mapper/"})

    # Ownership sections -- no XBRL tag; the SEC form type is the closest
    # equivalent "what do I need to go fetch" signal.
    rows.extend(
        [
            {"data_point_name": "insider_ownership", "data_point_type": "ownership", "required_tags": ["FORM 4"], "source_module": "ownership/insider.py"},
            {"data_point_name": "institutional_ownership", "data_point_type": "ownership", "required_tags": ["FORM 13F", "SCHEDULE 13D", "SCHEDULE 13G"], "source_module": "ownership/institutional.py"},
            {"data_point_name": "mutual_fund_ownership", "data_point_type": "ownership", "required_tags": ["FORM N-PORT"], "source_module": "ownership/mutual_fund.py"},
        ]
    )

    with conn.cursor() as cur:
        # Found live 2026-09-06: company_data_point_coverage has a FK to
        # data_point_name, so clearing the registry alone violates it the
        # moment any coverage rows still reference the old registry rows
        # (true on every rerun after the first). build_coverage() always
        # fully rebuilds the coverage table from scratch anyway, so
        # clearing it here first is correct, not just a workaround.
        cur.execute("delete from analytics.company_data_point_coverage")
        cur.execute("delete from analytics.data_point_registry")
        cur.executemany(
            """
            insert into analytics.data_point_registry (data_point_name, data_point_type, required_tags, source_module)
            values (%(data_point_name)s, %(data_point_type)s, %(required_tags)s, %(source_module)s)
            """,
            rows,
        )
        conn.commit()

    logger.info("coverage_matrix.registry_built", rows=len(rows))
    return {"rows": len(rows)}


def build_coverage(conn: psycopg.Connection) -> dict:
    """Rebuilds analytics.company_data_point_coverage for every active
    company x every registry data point. Batched delete-then-reinsert
    (whole-table, not per-company -- this is a full rebuild, not an
    incremental update) to stay well under the connection's statement
    timeout at ~600K rows, same batching discipline as every other
    full-population write this session."""
    with conn.cursor() as cur:
        # Found live 2026-09-06: the metric insert below (~428K company x
        # metric combinations, each running its own correlated gap_reason
        # subquery) exceeded the connection's default 2-minute
        # statement_timeout. This is a rare, admin-triggered rebuild, not
        # a per-company loop on any hot path, so a longer timeout for
        # just this connection is the right fix, not a query rewrite --
        # the existing idx_metric_value_company_metric index already
        # supports each subquery invocation efficiently, the cost is
        # purely the sheer combination count.
        cur.execute("set statement_timeout = '10min'")
        cur.execute("delete from analytics.company_data_point_coverage")
        conn.commit()

        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, cc.name, exists (
                select 1 from analytics.canonical_fact cf where cf.company_id = c.id and cf.canonical_concept_id = cc.id
            )
            from core.company c
            cross join analytics.canonical_concept cc
            where c.status = 'active'
            """
        )
        conn.commit()

        # gap_reason is only meaningful when has_value is false -- picked
        # from the most-recent period's is_null_reason (a company can have
        # several metric_value rows across periods, each with a
        # potentially different reason; the latest period is the one a
        # "why is this missing" lookup actually cares about). Left NULL
        # when has_value is true, and always NULL for concept/ownership
        # rows above/below -- neither tracks a per-row null reason today.
        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value, gap_reason)
            select
                c.id,
                md.metric_name,
                exists (select 1 from analytics.metric_value mv where mv.company_id = c.id and mv.metric_definition_id = md.id and mv.value is not null),
                (
                    select mv2.is_null_reason from analytics.metric_value mv2
                    where mv2.company_id = c.id and mv2.metric_definition_id = md.id
                    order by mv2.period_end desc limit 1
                )
            from core.company c
            cross join analytics.metric_definition md
            where c.status = 'active' and md.status = 'active'
            """
        )
        conn.commit()

        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, 'insider_ownership', exists (
                select 1 from core.insider_ownership_summary s where s.company_id = c.id
            )
            from core.company c where c.status = 'active'
            """
        )
        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, 'institutional_ownership', exists (
                select 1 from core.institutional_ownership o where o.company_id = c.id
            )
            from core.company c where c.status = 'active'
            """
        )
        cur.execute(
            """
            insert into analytics.company_data_point_coverage (company_id, data_point_name, has_value)
            select c.id, 'mutual_fund_ownership', exists (
                select 1 from core.fund_ownership_summary s where s.company_id = c.id
            )
            from core.company c where c.status = 'active'
            """
        )
        conn.commit()

        cur.execute("select count(*), count(*) filter (where has_value) from analytics.company_data_point_coverage")
        total, has_value = cur.fetchone()

    logger.info("coverage_matrix.coverage_built", total_rows=total, has_value=has_value)
    return {"total_rows": total, "has_value": has_value}
