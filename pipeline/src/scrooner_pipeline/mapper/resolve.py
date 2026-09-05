"""Stage 3b -- Canonical fact resolution (doc 11). Applies Stage 3a's
concept_mapping to core.fact, producing one resolved value per (company,
canonical_concept, period) in analytics.canonical_fact.

Two resolution modes, per canonical_concept.combination_mode:

- first_match: mapped tags are ALTERNATIVES. For a given period, try each
  non-rejected mapped concept_id in priority order; the first one with an
  authoritative fact for that exact period wins. Different tags can win
  for different periods of the same company (e.g. AAPL's revenue: older
  periods resolve via SalesRevenueNet, recent ones via
  RevenueFromContractWithCustomerExcludingAssessedTax) -- resolution is
  necessarily period-by-period, not "pick the company's one preferred tag."
- sum: mapped tags are SUMMANDS. For a given period, sum every non-rejected
  mapped concept_id that has an authoritative fact for that period.
  priority is ignored in this mode (irrelevant to summation).

Only core.fact rows with is_authoritative=true are ever considered --
Stage 2e/2f's unresolved conflicts and superseded facts never leak into a
canonical_fact value. This is Stage 3b's own hard gate, not just a
carried-over rule.

Batches the same way every other stage does from Day 1 onward (load
lookups + facts into memory, one pass, batched writes) -- Normalizer Day 7
already paid the cost of a stage that didn't (doc 04, CLAUDE.md).
"""

import psycopg
import structlog

from scrooner_pipeline.common.errors import log_error

logger = structlog.get_logger()


def _load_concept_mappings(conn: psycopg.Connection) -> dict[int, dict]:
    """canonical_concept_id -> {combination_mode, mappings: [(concept_id, priority, confidence)]}"""
    with conn.cursor() as cur:
        cur.execute("select id, combination_mode from analytics.canonical_concept")
        modes = dict(cur.fetchall())
        cur.execute(
            """
            select canonical_concept_id, concept_id, priority
            from analytics.concept_mapping
            where confidence != 'rejected'
            order by canonical_concept_id, priority, concept_id
            """
        )
        result: dict[int, dict] = {cc_id: {"combination_mode": mode, "mappings": []} for cc_id, mode in modes.items()}
        for cc_id, concept_id, priority in cur.fetchall():
            result[cc_id]["mappings"].append((concept_id, priority))
    return result


def _load_managed_concept_ids(conn: psycopg.Connection) -> set[int]:
    """Every canonical_concept_id that has EVER had a concept_mapping row,
    rejected or not -- the set resolve() is allowed to delete-then-reinsert
    for. A concept with zero concept_mapping rows (e.g. total_debt_resolved,
    populated only by mapper/concept_fallback.py) is deliberately excluded.

    Found live 2026-09-02: resolve_for_company()'s delete was scoped only by
    company_id, so every resolve-facts run silently wiped total_debt_resolved
    for the whole population (it has zero mappings, so resolve() never
    reinserted it) -- concept_fallback.py's own docstring already warned
    "must run after resolve-facts" for exactly this reason, but nothing
    enforced it, and two later reruns this session omitted that step,
    losing real coverage for debt_to_equity/roic/net_cash/net_cash_per_share
    silently until the next coverage snapshot caught it. Scoping the delete
    to only concepts resolve() actually manages makes this structurally
    impossible to repeat for this or any future zero-mapping concept,
    rather than relying on operators remembering the right run order."""
    with conn.cursor() as cur:
        cur.execute("select distinct canonical_concept_id from analytics.concept_mapping")
        return {row[0] for row in cur.fetchall()}


def _load_facts(conn: psycopg.Connection, company_id: int, mapped_concept_ids: set[int]) -> list[tuple]:
    """(concept_id, period_id, value, fact_id) for every authoritative fact
    this company has under a mapped concept -- unmapped concepts never
    enter the picture at all."""
    with conn.cursor() as cur:
        cur.execute(
            """
            select concept_id, period_id, value, id
            from core.fact
            where company_id = %s and is_authoritative and concept_id = any(%s)
            """,
            (company_id, list(mapped_concept_ids)),
        )
        return cur.fetchall()


def resolve_for_company(conn: psycopg.Connection, company_id: int, mapping_index: dict[int, dict], managed_concept_ids: set[int]) -> dict:
    mapped_concept_ids = {concept_id for cc in mapping_index.values() for concept_id, _priority in cc["mappings"]}
    facts = _load_facts(conn, company_id, mapped_concept_ids)

    # concept_id -> period_id -> (value, fact_id)
    facts_by_concept: dict[int, dict[int, tuple]] = {}
    for concept_id, period_id, value, fact_id in facts:
        facts_by_concept.setdefault(concept_id, {})[period_id] = (value, fact_id)

    rows: list[dict] = []
    stats = {"resolved": 0, "unresolved_concepts": 0}

    for canonical_concept_id, info in mapping_index.items():
        mode = info["combination_mode"]
        mappings = info["mappings"]  # already priority-ordered
        if not mappings:
            stats["unresolved_concepts"] += 1
            continue

        # Every period any mapped tag reports for this company, for this concept.
        periods_seen: set[int] = set()
        for concept_id, _priority in mappings:
            periods_seen.update(facts_by_concept.get(concept_id, {}).keys())

        concept_resolved_any = False
        for period_id in periods_seen:
            if mode == "first_match":
                for concept_id, _priority in mappings:  # already priority order
                    hit = facts_by_concept.get(concept_id, {}).get(period_id)
                    if hit is not None:
                        value, fact_id = hit
                        rows.append(
                            {
                                "company_id": company_id,
                                "canonical_concept_id": canonical_concept_id,
                                "period_id": period_id,
                                "value": value,
                                "source_fact_ids": [fact_id],
                            }
                        )
                        concept_resolved_any = True
                        break
            else:  # sum
                total = None
                fact_ids = []
                for concept_id, _priority in mappings:
                    hit = facts_by_concept.get(concept_id, {}).get(period_id)
                    if hit is not None:
                        value, fact_id = hit
                        total = value if total is None else total + value
                        fact_ids.append(fact_id)
                if total is not None:
                    rows.append(
                        {
                            "company_id": company_id,
                            "canonical_concept_id": canonical_concept_id,
                            "period_id": period_id,
                            "value": total,
                            "source_fact_ids": fact_ids,
                        }
                    )
                    concept_resolved_any = True
        if not concept_resolved_any:
            stats["unresolved_concepts"] += 1

    # Delete-then-reinsert this company's rows entirely, rather than
    # upsert-only. Found live (Mapper Day 2): an upsert-only write left 3
    # stale Block rows in place after `OtherLongTermDebtNoncurrent` was
    # rejected -- those specific periods had no OTHER qualifying tag, so a
    # rerun had nothing to overwrite them with and silently left the old,
    # now-wrong value sitting in the table. A mapping change (new tag
    # approved, existing one rejected) must never be able to leave orphaned
    # data behind -- recomputing a company's canonical facts always starts
    # from a clean slate for that company, same truncate-and-reload
    # discipline the Collector already applies to raw.company_universe.
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = any(%s)",
            (company_id, list(managed_concept_ids)),
        )
        if rows:
            cur.executemany(
                """
                insert into analytics.canonical_fact
                    (company_id, canonical_concept_id, period_id, value, source_fact_ids)
                values
                    (%(company_id)s, %(canonical_concept_id)s, %(period_id)s, %(value)s, %(source_fact_ids)s)
                """,
                rows,
            )
        conn.commit()
    stats["resolved"] = len(rows)
    logger.info("resolve.company_done", company_id=company_id, **stats)
    return stats


def resolve(conn: psycopg.Connection, ciks: set[str]) -> dict:
    mapping_index = _load_concept_mappings(conn)
    managed_concept_ids = _load_managed_concept_ids(conn)
    with conn.cursor() as cur:
        cur.execute("select cik, id from core.company where cik = any(%s)", (sorted(ciks),))
        company_id_by_cik = dict(cur.fetchall())

    totals = {"considered": 0, "ok": 0, "no_company": 0, "errored": 0, "resolved": 0, "unresolved_concepts": 0}
    for cik in sorted(ciks):
        totals["considered"] += 1
        company_id = company_id_by_cik.get(cik)
        if company_id is None:
            totals["no_company"] += 1
            continue
        try:
            stats = resolve_for_company(conn, company_id, mapping_index, managed_concept_ids)
        except Exception as exc:
            totals["errored"] += 1
            log_error(conn, "analytics.mapper_error", cik, "resolve", exc)
            continue
        totals["ok"] += 1
        totals["resolved"] += stats["resolved"]
        totals["unresolved_concepts"] += stats["unresolved_concepts"]

    logger.info("resolve.done", **totals)
    return totals
