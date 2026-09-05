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

from scrooner_pipeline.parsers import revenue_parser

logger = structlog.get_logger()

PARSER_REGISTRY = {
    "revenue": revenue_parser,
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
