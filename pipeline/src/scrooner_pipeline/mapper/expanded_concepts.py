"""Expanded-metric canonical concepts (doc 18 Tier A / doc 26, built
2026-08-18 to raise data-point coverage). Same additive pattern as
statements/classify.py: Mapper's own frozen mapper/concepts.py and
mapper/resolve.py are NOT modified -- new, separate code writing to the
same shared tables, reusing resolve()'s unchanged resolution logic.

depreciation_and_amortization is `first_match`, deliberately NOT `sum`
-- checked live before writing this: AAPL FY2015 reports BOTH
DepreciationAndAmortization and DepreciationDepletionAndAmortization
for the exact same period. Summing them would silently double-count
D&A for that one period; `first_match` (priority order) picks exactly
one, the same discipline already proven for cost_of_revenue's own two
alternates (doc 17).

inventory and sbc (ShareBasedCompensation) are both single-tag,
first_match by convention (room for a real alternate if one turns up,
same as every other concept here) -- not checked for overlap since only
one tag was found for either across the golden-10's concept list.
"""

import psycopg
import structlog

logger = structlog.get_logger()

NEW_CANONICAL_CONCEPTS: list[tuple[str, str, str, str]] = [
    ("inventory", "balance_sheet", "first_match", "Inventory, net -- needed for Quick Ratio"),
    ("sbc", "income_statement", "first_match", "Stock-based compensation expense"),
    (
        "depreciation_and_amortization",
        "income_statement",
        "first_match",
        "D&A -- confirmed live (AAPL FY2015) that a company can report this under two "
        "different tags for the same period; first_match (not sum) avoids double-counting. "
        "Feeds ebitda.",
    ),
]

NEW_CONCEPT_MAPPINGS: list[tuple[str, str, str, int, str, str]] = [
    ("inventory", "us-gaap", "InventoryNet", 1, "approved", ""),
    ("sbc", "us-gaap", "ShareBasedCompensation", 1, "approved", ""),
    ("depreciation_and_amortization", "us-gaap", "DepreciationAndAmortization", 1, "approved",
     "Priority 1 -- confirmed live this is the tag AAPL's FY2015 filing itself treats as authoritative when both appear."),
    ("depreciation_and_amortization", "us-gaap", "DepreciationDepletionAndAmortization", 2, "approved",
     "Alternate, not summand -- see module docstring's AAPL FY2015 overlap finding."),
]


def seed_new_canonical_concepts(conn: psycopg.Connection) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.executemany(
            """
            insert into analytics.canonical_concept (name, statement, combination_mode, description)
            values (%s, %s, %s, %s)
            on conflict (name) do update
                set statement = excluded.statement,
                    combination_mode = excluded.combination_mode,
                    description = excluded.description
            """,
            NEW_CANONICAL_CONCEPTS,
        )
        conn.commit()
        cur.execute("select name, id from analytics.canonical_concept")
        return dict(cur.fetchall())


def seed_new_concept_mappings(conn: psycopg.Connection, canonical_id_by_name: dict[str, int]) -> dict:
    stats = {"considered": len(NEW_CONCEPT_MAPPINGS), "mapped": 0, "unresolved_tag": 0}
    with conn.cursor() as cur:
        for canonical_name, taxonomy, tag, priority, confidence, notes in NEW_CONCEPT_MAPPINGS:
            cur.execute("select id from core.concept where taxonomy = %s and tag = %s", (taxonomy, tag))
            row = cur.fetchone()
            if row is None:
                stats["unresolved_tag"] += 1
                logger.warning("expanded_concepts.tag_not_in_core", taxonomy=taxonomy, tag=tag, canonical=canonical_name)
                continue
            concept_id = row[0]
            canonical_id = canonical_id_by_name[canonical_name]
            cur.execute(
                """
                insert into analytics.concept_mapping (canonical_concept_id, concept_id, priority, confidence, notes)
                values (%s, %s, %s, %s, %s)
                on conflict (canonical_concept_id, concept_id) do update
                    set priority = excluded.priority, confidence = excluded.confidence, notes = excluded.notes
                """,
                (canonical_id, concept_id, priority, confidence, notes),
            )
            stats["mapped"] += 1
    conn.commit()
    logger.info("expanded_concepts.mappings_seeded", **stats)
    return stats


def seed(conn: psycopg.Connection) -> dict:
    canonical_id_by_name = seed_new_canonical_concepts(conn)
    mapping_stats = seed_new_concept_mappings(conn, canonical_id_by_name)
    return {"new_canonical_concepts": len(NEW_CANONICAL_CONCEPTS), **mapping_stats}
