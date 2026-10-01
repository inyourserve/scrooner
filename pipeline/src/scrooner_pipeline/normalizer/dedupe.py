"""Stage 2e -- Duplicate/overlap resolution (doc 09). Resolves
core.fact.is_authoritative for every (company, concept, unit, period) group
with more than one row -- no new writes to raw or reads of companyfacts;
this operates entirely on what Stage 2d already wrote.

Verified live 2026-08-15 across the golden-8: 48,360 (company, concept,
unit, period) groups have more than one core.fact row (the same period
reported in an original filing and again as a later comparative), and
3,178 of those (~6.6%) genuinely DISAGREE on value -- not a rare edge case.
Inspected real examples: these are small, non-material revisions companies
make to prior-period comparatives in later filings WITHOUT filing a formal
10-K/A (e.g. JPM's DerivativeNotionalAmount for 2013-12-31 quietly shifts
from $70.430T to $70.413T starting mid-2014, no amendment on file). Real,
expected EDGAR messiness, not a bug in extraction -- and too common to
"flag" with just a log line, so the flagging mechanism has to be something
actually queryable.

Rule, per doc 09's "deterministic when they agree, flag when they don't":

- Singleton group (1 row): untouched, stays is_authoritative=true (the
  column's default from Stage 2d).
- Duplicate group, all rows agree on value: the EARLIEST-FILED row becomes
  is_authoritative=true, every later repeat becomes false. Earliest-filed
  is the most defensible choice of "primary source" -- it's where the
  value was first disclosed, and it's independent of how many times a
  later filing happens to repeat it as a comparative.
- Duplicate group, rows DISAGREE on value: every row in the group becomes
  is_authoritative=false. This is the "flag, don't silently resolve" case
  -- picking any single value here (even "most recent") would be a guess
  the Mapper shouldn't inherit as settled fact. No new table needed to
  surface this: a group where more than one row exists and NONE is
  authoritative is a genuine unresolved conflict, fully queryable directly
  against core.fact (see conflict_summary below).

Formal restatements (10-K/A) are Stage 2f's job, not this one's -- 2e only
handles same-form-type disagreement (a 10-Q quietly repeating a slightly
different number than the original 10-K), not amendment supersession.
"""

from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error, safe_rollback

logger = structlog.get_logger()


def _load_fact_rows(conn: psycopg.Connection, company_id: int) -> list[tuple]:
    """(fact_id, concept_id, unit_id, period_id, value, filing_date, filing_id)
    for every fact belonging to this company, pre-sorted so the first row in
    each (concept_id, unit_id, period_id) group is the earliest-filed
    (ties broken by fact_id, i.e. insertion order) -- makes "earliest wins"
    a matter of taking members[0], not a separate min() pass."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.id, f.concept_id, f.unit_id, f.period_id, f.value, fl.filing_date, f.filing_id
            from core.fact f
            join core.filing fl on fl.id = f.filing_id
            where f.company_id = %s
            order by f.concept_id, f.unit_id, f.period_id, fl.filing_date, f.id
            """,
            (company_id,),
        )
        return cur.fetchall()


def resolve_authoritative_for_company(
    conn: psycopg.Connection, company_id: int
) -> dict:
    rows = _load_fact_rows(conn, company_id)
    groups: dict[tuple, list[tuple]] = {}
    for fact_id, concept_id, unit_id, period_id, value, filing_date, filing_id in rows:
        groups.setdefault((concept_id, unit_id, period_id), []).append((fact_id, value))

    make_authoritative: list[int] = []
    make_non_authoritative: list[int] = []
    agreed_duplicate_groups = 0
    conflict_groups = 0

    for members in groups.values():
        if len(members) == 1:
            continue  # singleton -- leave the Stage 2d default (true) alone
        distinct_values = {v for _, v in members}
        if len(distinct_values) == 1:
            winner_id = members[0][
                0
            ]  # earliest-filed, by construction of the query order
            make_authoritative.append(winner_id)
            make_non_authoritative.extend(fact_id for fact_id, _ in members[1:])
            agreed_duplicate_groups += 1
        else:
            make_non_authoritative.extend(fact_id for fact_id, _ in members)
            conflict_groups += 1

    with conn.cursor() as cur:
        if make_authoritative:
            cur.execute(
                "update core.fact set is_authoritative = true where id = any(%s)",
                (make_authoritative,),
            )
        if make_non_authoritative:
            cur.execute(
                "update core.fact set is_authoritative = false where id = any(%s)",
                (make_non_authoritative,),
            )
    conn.commit()

    stats = {
        "duplicate_groups": agreed_duplicate_groups + conflict_groups,
        "agreed_duplicate_groups": agreed_duplicate_groups,
        "conflict_groups": conflict_groups,
    }
    logger.info("dedupe.resolved", company_id=company_id, **stats)
    return stats


def resolve_authoritative(conn: psycopg.Connection, ciks: set[str]) -> dict:
    totals = {
        "considered": 0,
        "ok": 0,
        "no_company": 0,
        "errored": 0,
        "duplicate_groups": 0,
        "agreed_duplicate_groups": 0,
        "conflict_groups": 0,
    }
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        company_id_by_cik = dict(cur.fetchall())

    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = resolve_authoritative_for_company(conn, company_id)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "core.normalizer_error", cik, "dedupe", exc)
            conn = safe_rollback(conn, stage="dedupe", cik=cik)
            continue
        totals["ok"] += 1
        for k in ("duplicate_groups", "agreed_duplicate_groups", "conflict_groups"):
            totals[k] += stats[k]

    logger.info("dedupe.resolve.done", **totals)
    return totals


def conflict_summary(conn: psycopg.Connection, ciks: set[str]) -> list[dict]:
    """Every unresolved conflict group -- for review, not automated
    resolution. A group is a genuine conflict iff it has more than one row
    and none of them is authoritative (see module docstring)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select c.cik, co.taxonomy, co.tag, u.unit_name, p.start_date, p.end_date, p.period_type,
                   array_agg(f.value order by fl.filing_date) as values,
                   array_agg(fl.form order by fl.filing_date) as forms,
                   array_agg(fl.filing_date order by fl.filing_date) as filing_dates
            from core.fact f
            join core.company c on c.id = f.company_id
            join core.concept co on co.id = f.concept_id
            join core.unit u on u.id = f.unit_id
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            where c.cik = any(%s)
            group by c.cik, co.taxonomy, co.tag, u.unit_name, p.start_date, p.end_date, p.period_type
            having count(*) > 1 and bool_or(f.is_authoritative) = false
            order by c.cik, co.tag, p.end_date
            """,
            (sorted(ciks),),
        )
        cols = [d.name for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
