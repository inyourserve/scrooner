"""Multi-parser orchestrator (doc 42, built 2026-09-05).

Every canonical concept has, in principle, up to 3 independent
resolution mechanisms, tried in this order (cheapest/most-reliable
first, same idiom as `total_debt_resolved`'s "prefer A, else B"):

1. **XBRL tag resolution** (`mapper/resolve.py` + `analytics.
   concept_mapping`) -- frozen, unchanged, always tried first via the
   normal `scrooner-map resolve-facts` pipeline stage. This module does
   NOT re-implement or call into it; it only operates on whatever
   `resolve-facts` was NOT able to resolve.
2. **A sector-specific canonical concept** (e.g. `bdc_total_investment_
   income`) -- a real, DIFFERENT concept for a population whose
   business model genuinely doesn't produce the generic concept at all
   (doc 42 Part 4). Seeded via `mapper/expanded_concepts.py`, resolved
   by the same frozen `resolve()` -- also not this module's concern.
3. **A dedicated parser module** (this package, `parsers/*.py`) -- for
   the genuine residual population where a real value exists in the
   filing's own rendered statement, just under a company-specific tag
   no tag list could enumerate. This is what `main_parser.py` actually
   orchestrates.

PARSER_REGISTRY maps a canonical_concept name to the parser module that
knows how to look for it via rendered-report reading. Only concepts
with a real, built parser appear here -- most of the 45 canonical
concepts are pure `first_match`/`sum` XBRL resolution and need no entry
at all (adding one for a concept with no real custom-tag population
would just waste SEC fetch budget re-confirming what's already known:
a null concept for a bank/SPAC/pre-revenue company is a correct null,
not a parser target).

Each registered parser module must export:
  - `run(conn, ciks=None) -> dict` -- the same contract every parser in
    this package follows (see revenue_parser.py's own module docstring
    for why: registry writes, attempt-tracking, never touches
    `canonical_fact` directly).

Usage:
  uv run scrooner-map run-parser revenue                 # full population, skips already-attempted
  uv run scrooner-map run-parser revenue --ciks 0000...   # scoped, for piloting
"""

import psycopg
import structlog

from scrooner_pipeline.common.errors import safe_rollback
from scrooner_pipeline.parsers import cost_of_revenue_parser, revenue_parser
from scrooner_pipeline.sanity.tag_investigator import FIXABLE_CONCEPTS

logger = structlog.get_logger()

PARSER_REGISTRY = {
    "revenue": revenue_parser,
    "cost_of_revenue": cost_of_revenue_parser,
}


def run_parser(conn: psycopg.Connection, concept_name: str, ciks: set[str] | None = None) -> dict:
    if concept_name not in PARSER_REGISTRY:
        raise ValueError(
            f"No parser registered for concept {concept_name!r}. "
            f"Registered: {sorted(PARSER_REGISTRY)}"
        )
    module = PARSER_REGISTRY[concept_name]
    logger.info("main_parser.starting", concept=concept_name, module=module.__name__)
    result = module.run(conn, ciks)
    logger.info("main_parser.done", concept=concept_name, **result["stats"])
    return result


def registry_summary(conn: psycopg.Connection) -> list[dict]:
    """The 'which parser resolved this' view the routing table exists
    for -- one row per (concept, parser) pair this session has ever
    attempted, with real counts. Read-only."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select cc.name as concept_name,
                   cpa.parser_name,
                   count(*) filter (where cpa.outcome = 'matched') as matched,
                   count(*) filter (where cpa.outcome = 'no_report') as no_report,
                   count(*) filter (where cpa.outcome = 'no_row_matched') as no_row_matched,
                   count(*) filter (where cpa.outcome = 'errored') as errored,
                   count(*) as total_attempted
            from analytics.concept_parser_attempt cpa
            join analytics.canonical_concept cc on cc.id = cpa.canonical_concept_id
            group by cc.name, cpa.parser_name
            order by cc.name, cpa.parser_name
            """
        )
        columns = ["concept_name", "parser_name", "matched", "no_report", "no_row_matched", "errored", "total_attempted"]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def resolve_parser_results(conn: psycopg.Connection, concept_name: str) -> dict:
    """Merges analytics.concept_parser_result into the concept's own
    `*_sanity_resolved` display concept (FIXABLE_CONCEPTS, the same
    dict sanity/tag_investigator.py uses) -- added 2026-09-20, closing a
    real gap found live: concept_parser_result had ZERO readers since
    Parser 3 was built 2026-09-05, so a real value this parser found
    (APA Corp's real revenue, once the title-pattern/label/scale fixes
    landed) would have sat in that table forever, invisible to the
    company page, screener, or any metric calculation. Only overwrites
    the ONE period a parser result exists for -- never touches a
    company's other periods, which still come from resolve()/
    concept_fallback.py/tag preferences exactly as before.

    Period matching: concept_parser_result stores only `period_end`
    (the rendered report has no structured period_id to attach to), and
    a real company can have SEVERAL duration periods sharing the same
    end_date (a 10-Q's "3 Months Ended"/"6 Months Ended" columns both
    ending the filing's quarter-end -- confirmed live, APA Corp has
    both for 2026-06-30). The parser always extracts its value from the
    report's FIRST data column, which is consistently the shortest/most
    recent span in every real report checked -- so among duration
    periods sharing that end_date, the one with the LATEST start_date
    (shortest span) is the correct match, never the cumulative YTD one.

    source_fact_ids is intentionally empty for these rows (no core.fact
    row underlies a rendered-table extraction) -- full provenance
    (source_form/accession/report) lives in concept_parser_result
    itself, joinable by (company_id, canonical_concept_id).

    Commits per company, not once at the end -- found live 2026-09-21
    running this against 52 companies at once (cost_of_revenue's own
    initial full-population parser rollout): a single `conn.commit()`
    after the whole loop meant one uncommitted transaction spanning
    every company's own delete+insert+period-lookup round trip, fully
    exposed to a real, reproducible Supabase pooler connection drop
    partway through -- losing the ENTIRE batch's work, not just the one
    company mid-flight, and forcing a full blind retry from scratch
    every time (confirmed live: 4 consecutive attempts all failed with
    an identical `OperationalError`/`SSL SYSCALL... Operation timed out`
    partway through). A prior, smaller run (5 companies) never exposed
    this, since it finished before any drop occurred. Committing after
    each company's own write makes a mid-batch drop lose at most one
    company's progress, and the function stays idempotent on rerun."""
    if concept_name not in FIXABLE_CONCEPTS:
        raise ValueError(f"{concept_name!r} has no *_sanity_resolved companion in FIXABLE_CONCEPTS")
    resolved_concept_name = FIXABLE_CONCEPTS[concept_name]

    with conn.cursor() as cur:
        cur.execute("select id from analytics.canonical_concept where name = %s", (concept_name,))
        primary_id = cur.fetchone()[0]
        cur.execute("select id from analytics.canonical_concept where name = %s", (resolved_concept_name,))
        resolved_id = cur.fetchone()[0]

        cur.execute(
            "select company_id, value, period_end from analytics.concept_parser_result where canonical_concept_id = %s",
            (primary_id,),
        )
        parser_results = cur.fetchall()

    stats = {"considered": len(parser_results), "applied": 0, "no_matching_period": 0, "errored": 0}
    for company_id, value, period_end in parser_results:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select id from core.period
                    where company_id = %s and end_date = %s and period_type = 'duration'
                    order by start_date desc limit 1
                    """,
                    (company_id, period_end),
                )
                row = cur.fetchone()
                if row is None:
                    stats["no_matching_period"] += 1
                    conn.commit()
                    continue
                period_id = row[0]
                cur.execute(
                    "delete from analytics.canonical_fact where canonical_concept_id = %s and company_id = %s and period_id = %s",
                    (resolved_id, company_id, period_id),
                )
                cur.execute(
                    """
                    insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                    values (%s, %s, %s, %s, %s)
                    """,
                    (company_id, resolved_id, period_id, value, []),
                )
                stats["applied"] += 1
            conn.commit()
        except Exception:
            logger.warning("main_parser.resolve_parser_results.company_failed", company_id=company_id, exc_info=True)
            stats["errored"] += 1
            conn = safe_rollback(conn, stage="resolve_parser_results")
    logger.info("main_parser.resolve_parser_results.done", concept=concept_name, **stats)
    return stats
