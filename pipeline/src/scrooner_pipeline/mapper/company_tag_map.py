"""Tag-map selection of canonical facts (migration 0122, founder order 2026-11-11:
"FSN for learning, SEC for mapping").

For a company with rows in analytics.company_tag_map, a canonical fact is built ONLY from the map:

  * decision 'concept' / 'combined': the tag IS the concept (a 'combined' tag is the company's own total, its
    member tags are evidence); the fact of that tag whose period END lies in [era_from, era_to] is the value.
  * decision 'component': the fact is a summand of parent_concept_id, added with combine_sign (+1/-1), Decimal.
  * decision 'excluded': never used.
  * statement scope: a row only serves a concept on that concept's statement (IS/BS/CF); the same tag on another
    statement (NetIncomeLoss on the cash-flow statement) never feeds net income. Rows on another statement are
    counted in stats["stmt_mismatch_rows"], never silently applied.
  * only core.fact rows with is_authoritative are read; per (tag, period) the LATEST filing wins (filing_date,
    then filing id); EPS facts that are derived (is_derived) are never used.
  * two different values for one (concept, period) from different tags/routes are a conflict: nothing is written
    for that cell (counted in stats["conflict_cells"]), never an arbitrary pick.
  * calc-tree safety (Ritwik, 2026-11-11), per filing: (1) a printed 'concept'/'combined' fact for C beats the
    'component' rows for C; (2) components are summed only when C is not printed, from ONE filing, and every
    component is a direct calc child of the component rows' evidence_cal_parent in that filing's calc arcs
    (fsn.calc_arc); where C is printed in the same filing the components must tie to it (checks.tol_of) or the
    cell is HELD; (3) a component set in which one member is a calc ancestor of another is refused (HELD).
    Held cells are written nowhere and returned in stats["held"] with a reason code.
  * no concept_mapping, no company_tag_preference, no fallback is consulted for these companies.

Companies without rows are not touched by this module. The hook in mapper/resolve.py calls it only when rule
company_tag_map.select@1 is ON (SCROONER_RULES_ENABLED), so nothing changes until it is switched on.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import psycopg
import structlog

from scrooner_pipeline.common.rule_flags import ON, rule_mode
from scrooner_pipeline.fsn_store.checks import tol_of

logger = structlog.get_logger()

RULE_ID = "company_tag_map.select@1"
FAMILY = "company_tag_map"

# canonical_concept.statement -> FSN statement codes allowed to feed it. Per-share dividends are printed on
# the income or equity statement although the concept row says cash_flow (DPS-EQUITY-STATEMENT proposal).
STATEMENT_CODE = {"income_statement": "IS", "balance_sheet": "BS", "cash_flow": "CF"}
EXTRA_STMT = {
    "dividends_per_share": {"IS", "EQ"},
    "dividends_per_share_resolved": {"IS", "EQ"},
}
# EPS is never derived (founder standing rule): derived facts are not eligible for these concepts.
NEVER_DERIVED = {
    "basic_eps",
    "basic_eps_resolved",
    "diluted_eps",
    "diluted_eps_resolved",
}

_FAR = date.max


@dataclass(frozen=True)
class MapRow:
    taxonomy: str
    tag: str
    stmt: str
    decision: str
    canonical_concept_id: int | None
    parent_concept_id: int | None
    combine_sign: int | None
    era_from: date
    era_to: date | None
    evidence_cal_parent: str | None = None


@dataclass(frozen=True)
class Fact:
    value: Decimal
    fact_id: int
    end: date
    derived: bool
    filing_id: int
    accession: str


def enabled(environ=None) -> bool:
    return rule_mode(RULE_ID, environ) == ON


def load_tag_map_company_ids(
    conn: psycopg.Connection, company_ids: set[int]
) -> set[int]:
    """Subset of company_ids that have at least one company_tag_map row (one indexed query)."""
    if not company_ids:
        return set()
    with conn.cursor() as cur:
        cur.execute(
            "select distinct company_id from analytics.company_tag_map where company_id = any(%s)",
            (sorted(company_ids),),
        )
        return {r[0] for r in cur.fetchall()}


def _load_rows(conn: psycopg.Connection, company_id: int) -> list[MapRow]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select taxonomy, tag, stmt, decision, canonical_concept_id, parent_concept_id, combine_sign,
                   era_from, era_to, evidence_cal_parent
            from analytics.company_tag_map where company_id = %s
            """,
            (company_id,),
        )
        return [MapRow(*r) for r in cur.fetchall()]


def _load_facts(conn: psycopg.Connection, company_id: int, tags: set[tuple[str, str]]):
    """(taxonomy, tag) -> period_id -> Fact of the latest authoritative filing. Authoritative only:
    is_authoritative=false is a hard filter."""
    out: dict[tuple[str, str], dict[int, Fact]] = defaultdict(dict)
    if not tags:
        return out
    with conn.cursor() as cur:
        cur.execute(
            """
            select distinct on (c.taxonomy, c.tag, f.period_id)
                   c.taxonomy, c.tag, f.period_id, f.value, f.id, p.end_date, f.is_derived,
                   f.filing_id, fl.accession_number
            from core.fact f
            join core.concept c on c.id = f.concept_id
            join core.period p on p.id = f.period_id
            join core.filing fl on fl.id = f.filing_id
            where f.company_id = %s and f.is_authoritative
              and c.tag = any(%s)
            order by c.taxonomy, c.tag, f.period_id,
                     fl.filing_date desc nulls last, f.filing_id desc, f.id desc
            """,
            (company_id, sorted({t for _, t in tags})),
        )
        for (
            taxonomy,
            tag,
            period_id,
            value,
            fact_id,
            end,
            derived,
            filing_id,
            acc,
        ) in cur.fetchall():
            if (taxonomy, tag) in tags:
                out[(taxonomy, tag)][period_id] = Fact(
                    Decimal(value), fact_id, end, derived, filing_id, acc
                )
    return out


def load_calc_evidence(conn: psycopg.Connection, accessions: set[str]):
    """(arcs, dcml): arcs[accession] = {(parent_tag, child_tag)} from fsn.calc_arc; dcml[(accession, tag, ddate)]
    = smallest decimals printed for that non-dimensional value (for the tie tolerance)."""
    arcs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    dcml: dict[tuple[str, str, date], int] = {}
    if not accessions:
        return arcs, dcml
    with conn.cursor() as cur:
        cur.execute(
            """
            select f.accession, pt.tag, ct.tag
            from fsn.calc_arc a
            join fsn.filing f on f.id = a.filing_id
            join fsn.tag pt on pt.id = a.parent_tag_id
            join fsn.tag ct on ct.id = a.child_tag_id
            where f.accession = any(%s)
            """,
            (sorted(accessions),),
        )
        for acc, parent, child in cur.fetchall():
            arcs[acc].add((parent, child))
        cur.execute(
            """
            select f.accession, t.tag, v.ddate, min(v.dcml)
            from fsn.value v
            join fsn.filing f on f.id = v.filing_id
            join fsn.tag t on t.id = v.tag_id
            where f.accession = any(%s) and v.dim_id = 0 and v.dcml is not null
            group by 1, 2, 3
            """,
            (sorted(accessions),),
        )
        for acc, tag, ddate, d in cur.fetchall():
            dcml[(acc, tag, ddate)] = d
    return arcs, dcml


def _in_era(row: MapRow, end: date) -> bool:
    return row.era_from <= end <= (row.era_to or _FAR)


def _local(tag: str | None) -> str | None:
    return None if tag is None else tag.rsplit(":", 1)[-1]


def _descendants(arcs: set[tuple[str, str]], tag: str) -> set[str]:
    seen: set[str] = set()
    stack = [tag]
    while stack:
        cur = stack.pop()
        for parent, child in arcs:
            if parent == cur and child not in seen:
                seen.add(child)
                stack.append(child)
    return seen


def _check_components(
    comps: list[tuple[MapRow, Fact]], arcs: dict[str, set[tuple[str, str]]]
) -> str | None:
    """Reason code if the component set must not be summed (rules 2 and 3), else None."""
    if len({f.filing_id for _, f in comps}) != 1:
        return "components_from_different_filings"
    acc = comps[0][1].accession
    filing_arcs = arcs.get(acc, set())
    if not filing_arcs:
        return "no_calc_evidence"
    tags = [r.tag for r, _ in comps]
    for r, _ in comps:  # rule 3: no member may be an ancestor of another member
        if _descendants(filing_arcs, r.tag) & (set(tags) - {r.tag}):
            return "ancestor_in_component_set"
    parents = {_local(r.evidence_cal_parent) for r, _ in comps}
    if len(parents) != 1 or None in parents:
        return "components_without_single_calc_parent"
    parent = parents.pop()
    if any(
        (parent, r.tag) not in filing_arcs for r, _ in comps
    ):  # rule 2: direct children only
        return "component_not_direct_child_of_parent"
    return None


def build_cells(
    rows: list[MapRow],
    facts: dict[tuple[str, str], dict[int, Fact]],
    concept_info: dict[int, tuple[str, str]],
    arcs: dict[str, set[tuple[str, str]]] | None = None,
    dcml: dict[tuple[str, str, date], int] | None = None,
) -> tuple[list[dict], dict]:
    """Pure core: map rows + facts + calc evidence -> canonical cells. concept_info: id -> (name, statement)."""
    arcs = arcs or {}
    dcml = dcml or {}
    stats = {
        "stmt_mismatch_rows": 0,
        "conflict_cells": 0,
        "derived_eps_skipped": 0,
        "held": [],
    }

    def stmt_ok(concept_id: int, stmt: str) -> bool:
        name, statement = concept_info[concept_id]
        return stmt in ({STATEMENT_CODE[statement]} | EXTRA_STMT.get(name, set()))

    direct: dict[tuple[int, int], list[tuple[MapRow, Fact]]] = defaultdict(list)
    comp: dict[tuple[int, int], list[tuple[MapRow, Fact]]] = defaultdict(list)
    for row in rows:
        if row.decision == "excluded":
            continue
        target = (
            row.parent_concept_id
            if row.decision == "component"
            else row.canonical_concept_id
        )
        if target is None or not stmt_ok(target, row.stmt):
            stats["stmt_mismatch_rows"] += 1
            continue
        for period_id, fact in facts.get((row.taxonomy, row.tag), {}).items():
            if not _in_era(row, fact.end):
                continue
            if fact.derived and concept_info[target][0] in NEVER_DERIVED:
                stats["derived_eps_skipped"] += 1
                continue
            (comp if row.decision == "component" else direct)[
                (target, period_id)
            ].append((row, fact))

    def hold(key, reason):
        stats["held"].append(
            {"canonical_concept_id": key[0], "period_id": key[1], "reason": reason}
        )

    cells: list[dict] = []
    for key in sorted(set(direct) | set(comp)):
        d = direct.get(key, [])
        c = comp.get(key, [])
        if len({f.value for _, f in d}) > 1:
            stats["conflict_cells"] += (
                1  # two printed tags disagree: never an arbitrary pick
            )
            continue
        if d:
            ref = d[0][1]
            # rule 1: the printed concept wins; components of the SAME filing must still tie (rule 2)
            same = [(r, f) for r, f in c if f.filing_id == ref.filing_id]
            if same:
                total = sum(f.value * int(r.combine_sign) for r, f in same)
                tol = tol_of(
                    [dcml.get((f.accession, r.tag, f.end)) for r, f in same]
                    + [dcml.get((ref.accession, d[0][0].tag, ref.end))]
                )
                if abs(total - ref.value) > tol:
                    hold(key, "printed_total_does_not_tie_to_components")
                    continue
            cells.append(
                {
                    "canonical_concept_id": key[0],
                    "period_id": key[1],
                    "value": ref.value,
                    "source_fact_ids": sorted({f.fact_id for _, f in d}),
                }
            )
            continue
        reason = _check_components(c, arcs)
        if reason:
            hold(key, reason)
            continue
        cells.append(
            {
                "canonical_concept_id": key[0],
                "period_id": key[1],
                "value": sum((f.value * int(r.combine_sign) for r, f in c), Decimal(0)),
                "source_fact_ids": sorted({f.fact_id for _, f in c}),
            }
        )
    return cells, stats


def resolve_for_company(
    conn: psycopg.Connection,
    company_id: int,
    managed_concept_ids: set[int],
    concept_info: dict[int, tuple[str, str]],
) -> dict:
    """Rebuild this company's canonical_fact rows from its tag map. Deletes every concept resolve() manages
    (plus every concept the map targets), so no value of the old path survives for a tag-map company."""
    rows = _load_rows(conn, company_id)
    used = {(r.taxonomy, r.tag) for r in rows if r.decision != "excluded"}
    facts = _load_facts(conn, company_id, used)
    comp_tags = {(r.taxonomy, r.tag) for r in rows if r.decision == "component"}
    accessions = {
        f.accession for k in comp_tags | used for f in facts.get(k, {}).values()
    }
    arcs, dcml = load_calc_evidence(conn, accessions)
    cells, stats = build_cells(rows, facts, concept_info, arcs, dcml)
    targets = set(managed_concept_ids)
    for r in rows:
        targets.update(
            x for x in (r.canonical_concept_id, r.parent_concept_id) if x is not None
        )
    with conn.cursor() as cur:
        cur.execute(
            "delete from analytics.canonical_fact where company_id = %s and canonical_concept_id = any(%s)",
            (company_id, sorted(targets)),
        )
        if cells:
            cur.executemany(
                """
                insert into analytics.canonical_fact
                    (company_id, canonical_concept_id, period_id, value, source_fact_ids, family)
                values (%s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        company_id,
                        c["canonical_concept_id"],
                        c["period_id"],
                        c["value"],
                        c["source_fact_ids"],
                        FAMILY,
                    )
                    for c in cells
                ],
            )
        conn.commit()
    stats["resolved"] = len(cells)
    stats["held_cells"] = len(stats["held"])
    logger.info(
        "company_tag_map.company_done",
        company_id=company_id,
        **{k: v for k, v in stats.items() if k != "held"},
    )
    return stats


def load_concept_info(conn: psycopg.Connection) -> dict[int, tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("select id, name, statement from analytics.canonical_concept")
        return {i: (n, s) for i, n, s in cur.fetchall()}
