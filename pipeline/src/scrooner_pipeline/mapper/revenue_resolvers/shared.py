"""Primitives shared by every revenue resolver -- kept out of
`mapper/concept_fallback.py` because these are revenue-specific
(the `revenue`/`revenue_sanity_resolved` concept pair, and the
single-writer-per-company exclusion set every revenue resolver must
respect), not the generic concept-vs-concept fallback machinery that
module still owns for `total_debt`/`gross_profit`/etc."""

import psycopg

from scrooner_pipeline.mapper.concept_fallback import _concept_id


def revenue_concept_ids(conn: psycopg.Connection) -> tuple[int, int]:
    """(revenue canonical_concept_id, revenue_sanity_resolved canonical_concept_id)."""
    return _concept_id(conn, "revenue"), _concept_id(conn, "revenue_sanity_resolved")


def companies_owned_by_other_revenue_writer(
    conn: psycopg.Connection, revenue_id: int
) -> set[int]:
    """Companies whose revenue_sanity_resolved row is already owned, for
    EVERY period, by another single-writer-per-company mechanism --
    sanity/tag_investigator.py's company_tag_preference (a confirmed
    per-company tag override) or parsers/revenue_parser.py's rendered-
    report extraction (analytics.concept_parser_result). No resolver in
    this package should touch a company one of those two mechanisms
    already owns -- same discipline concept_fallback.py's original
    ARITHMETIC_FALLBACKS already established for the gross_profit/
    cost_of_revenue family."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select company_id from analytics.company_tag_preference where canonical_concept_id = %(revenue_id)s
            union
            select company_id from analytics.concept_parser_result where canonical_concept_id = %(revenue_id)s
            """,
            {"revenue_id": revenue_id},
        )
        return {r[0] for r in cur.fetchall()}
