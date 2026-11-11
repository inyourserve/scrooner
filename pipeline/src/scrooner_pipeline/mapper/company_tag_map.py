"""Tag-map selection of canonical facts (migration 0122, founder order 2026-11-11:
"FSN for learning, SEC for mapping").

For a company with rows in analytics.company_tag_map, a canonical fact is built ONLY from the map:

  * decision 'concept': the tag IS the concept; the fact of that tag whose period END lies in
    [era_from, era_to] is the value.
  * decision 'component': the fact is a summand of parent_concept_id, added with its sign (+1/-1), Decimal.
  * every value-bearing row ('concept' and 'component') carries sign: the served value is sign x fact value.
  * decision 'excluded': never used.
  * statement scope: a row only serves a concept on that concept's statement (IS/BS/CF); the same tag on another
    statement (NetIncomeLoss on the cash-flow statement) never feeds net income. Rows on another statement are
    counted in stats["stmt_mismatch_rows"], never silently applied.
  * only core.fact rows with is_authoritative are read; per (tag, period) the LATEST filing wins (filing_date,
    then filing id); EPS facts that are derived (is_derived) are never used.
  * two different values for one (concept, period) from different tags/routes are a conflict: nothing is written
    for that cell (counted in stats["conflict_cells"]), never an arbitrary pick.
  * calc-tree safety (Ritwik, 2026-11-11), per filing: (1) a printed 'concept' fact for C beats the
    'component' rows for C; (2) components are summed only when C is not printed, from ONE filing, and every
    component is a direct calc child of the component rows' evidence_cal_parent in that filing's calc arcs
    (fsn.calc_arc); where C is printed in the same filing the components must tie to it (checks.tol_of) or the
    cell is HELD; (3) a component set in which one member is a calc ancestor of another is refused (HELD).
    Held cells are written nowhere and returned in stats["held"] with a reason code.
  * decision 'combined': one printed line spanning several concepts. It NEVER feeds a concept (even if
    canonical_concept_id is set). It is served as the company's own line in analytics.company_combined_line
    (printed label, sign x stored value); each spanned concept without a separately printed value in that period
    is marked not_in_template "shown as the company's combined line '<plabel>'".
  * sign means: multiply the value STORED in core.fact (the tag's own direction, not the printed sign) by it. The
    mapper never takes abs() and never flips a sign from a label; core.fact is non-dimensional by construction.
  * decision 'not_presented' / 'not_in_template' (tagless, concept-level): for each of the company's periods in the
    era (instant periods for a balance-sheet concept, FY or quarter durations otherwise) that has no value cell the
    result is a reasoned blank (stats["blanks"], written to analytics.cell_blank_reason by resolve()). A printed
    value for that concept and period wins; the clash is reported in stats["blank_conflicts"].
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
    taxonomy: str | None
    tag: str | None
    stmt: str
    decision: str
    canonical_concept_id: int | None
    parent_concept_id: int | None
    sign: int | None
    era_from: date
    era_to: date | None
    evidence_cal_parent: str | None = None
    reason: str | None = None
    rule_id: str | None = None
    components: tuple[str, ...] | None = None
    evidence_plabel: str | None = None
    serve_note: str | None = None
    map_id: int | None = None


@dataclass(frozen=True)
class Fact:
    value: Decimal
    fact_id: int
    end: date
    derived: bool
    filing_id: int
    accession: str
    filed: date | None = None


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
            select taxonomy, tag, stmt, decision, canonical_concept_id, parent_concept_id, sign,
                   era_from, era_to, evidence_cal_parent, reason, rule_id, components, evidence_plabel, serve_note, id
            from analytics.company_tag_map where company_id = %s
            """,
            (company_id,),
        )
        return [
            MapRow(*r[:12], tuple(r[12]) if r[12] else None, r[13], r[14], r[15])
            for r in cur.fetchall()
        ]


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
                   f.filing_id, fl.accession_number, fl.filing_date
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
            filed,
        ) in cur.fetchall():
            if (taxonomy, tag) in tags:
                out[(taxonomy, tag)][period_id] = Fact(
                    Decimal(value), fact_id, end, derived, filing_id, acc, filed
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


def _sign(row: MapRow) -> int:
    return int(row.sign or 1)


def _note(pairs) -> str | None:
    """The label note of the rows that built a cell (e.g. 'face line including restricted cash, as printed').
    canonical_fact has no per-cell note column: the note is returned with the cell and stays on the map row."""
    notes = sorted({r.serve_note for r, _ in pairs if r.serve_note})
    return "; ".join(notes) or None


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
    # evidence_cal_parent may list several parents ('A;B', the line's calc parents): the components must share
    # one parent, and each must be a DIRECT child of it in this filing's arcs (rule 2)
    parent_sets = [
        {_local(p) for p in (r.evidence_cal_parent or "").split(";") if p.strip()}
        for r, _ in comps
    ]
    common = set.intersection(*parent_sets)
    if not common:
        return "components_without_single_calc_parent"
    if not any(all((p, r.tag) in filing_arcs for r, _ in comps) for p in common):
        return "component_not_direct_child_of_parent"
    return None


def _grain(start: date, end: date, ptype: str) -> str | None:
    if ptype == "instant":
        return "I"
    days = (end - start).days
    if 350 <= days <= 380:
        return "FY"
    if 80 <= days <= 100:
        return "Q"
    return None


def build_cells(
    rows: list[MapRow],
    facts: dict[tuple[str, str], dict[int, Fact]],
    concept_info: dict[int, tuple[str, str]],
    arcs: dict[str, set[tuple[str, str]]] | None = None,
    dcml: dict[tuple[str, str, date], int] | None = None,
    periods: dict[int, tuple[date, date, str]] | None = None,
) -> tuple[list[dict], dict]:
    """Pure core: map rows + facts + calc evidence -> canonical cells. concept_info: id -> (name, statement)."""
    arcs = arcs or {}
    dcml = dcml or {}
    stats = {
        "stmt_mismatch_rows": 0,
        "conflict_cells": 0,
        "derived_eps_skipped": 0,
        "held": [],
        "blanks": [],
        "blank_conflicts": [],
        "combined_lines": [],
    }

    def stmt_ok(concept_id: int, stmt: str) -> bool:
        name, statement = concept_info[concept_id]
        return stmt in ({STATEMENT_CODE[statement]} | EXTRA_STMT.get(name, set()))

    direct: dict[tuple[int, int], list[tuple[MapRow, Fact]]] = defaultdict(list)
    comp: dict[tuple[int, int], list[tuple[MapRow, Fact]]] = defaultdict(list)
    for row in rows:
        if row.decision in ("excluded", "not_presented", "not_in_template", "combined"):
            continue  # 'combined' never feeds a concept (only a reasoned blank below)
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
    conflicts: set[tuple[int, int]] = set()
    for key in sorted(set(direct) | set(comp)):
        d = direct.get(key, [])
        c = comp.get(key, [])
        if d:
            # several 'concept' rows may list different tags for one concept (10-Q vs 10-K tags, a mid-year
            # switch; never printed together in one filing): the LATEST filing's value wins, never a sum, never
            # tag order. Two listed tags printing different values in that same latest filing: reasoned blank.
            newest = max((f.filed or date.min, f.filing_id) for _, f in d)
            d = [(r, f) for r, f in d if (f.filed or date.min, f.filing_id) == newest]
            if len({f.value * _sign(r) for r, f in d}) > 1:
                stats["conflict_cells"] += 1
                hold(key, "conflicting_values_in_filing")
                conflicts.add(key)
                continue
            ref = d[0][1]
            ref_value = ref.value * _sign(d[0][0])
            # rule 1: the printed concept wins; components of the SAME filing must still tie (rule 2)
            same = [(r, f) for r, f in c if f.filing_id == ref.filing_id]
            if same:
                total = sum(f.value * _sign(r) for r, f in same)
                tol = tol_of(
                    [dcml.get((f.accession, r.tag, f.end)) for r, f in same]
                    + [dcml.get((ref.accession, d[0][0].tag, ref.end))]
                )
                if abs(total - ref_value) > tol:
                    hold(key, "printed_total_does_not_tie_to_components")
                    continue
            cells.append(
                {
                    "canonical_concept_id": key[0],
                    "period_id": key[1],
                    "value": ref_value,
                    "source_fact_ids": sorted({f.fact_id for _, f in d}),
                    "serve_note": _note(d),
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
                "value": sum((f.value * _sign(r) for r, f in c), Decimal(0)),
                "source_fact_ids": sorted({f.fact_id for _, f in c}),
                "serve_note": _note(c),
            }
        )
    value_keys = {(c["canonical_concept_id"], c["period_id"]) for c in cells}
    held_keys = {(h["canonical_concept_id"], h["period_id"]) for h in stats["held"]}
    name_to_id = {n: i for i, (n, _) in concept_info.items()}
    for row in rows:
        if row.decision == "combined":
            # one printed line spanning several concepts (founder ruling doc 02, sector templates item 3): it is
            # SERVED as the company's own combined line (analytics.company_combined_line: label, sign x stored
            # value) and never feeds a spanned concept; each spanned concept leaves the company's template for
            # that period (state not_in_template), unless a separate 'concept' row prints it.
            for period_id, fact in sorted(
                facts.get((row.taxonomy, row.tag), {}).items()
            ):
                if not _in_era(row, fact.end) or period_id not in (periods or {}):
                    continue
                start, end, ptype = periods[period_id]
                grain = _grain(start, end, ptype)
                if grain is None:
                    continue
                stats["combined_lines"].append(
                    {
                        "period_id": period_id,
                        "stmt": row.stmt,
                        "taxonomy": row.taxonomy,
                        "tag": row.tag,
                        "plabel": row.evidence_plabel or row.tag,
                        "components": list(row.components or ()),
                        "value": fact.value * _sign(row),
                        "source_fact_ids": [fact.fact_id],
                        "tag_map_id": row.map_id,
                    }
                )
                for name in row.components or ():
                    cid = name_to_id.get(name)
                    if cid is not None and (cid, period_id) in value_keys:
                        continue  # a separate 'concept' row prints it: the value wins
                    stats["blanks"].append(
                        {
                            "canonical_concept_id": cid,
                            "concept_name": name,
                            "period_id": period_id,
                            "state": "not_in_template",
                            "reason": f"shown as the company's combined line '{row.evidence_plabel}'",
                            "rule_id": row.rule_id,
                            "period_start": start,
                            "period_end": end,
                            "grain": grain,
                        }
                    )
            continue
        if row.decision not in ("not_presented", "not_in_template"):
            continue
        concept = row.canonical_concept_id
        if concept not in concept_info or not stmt_ok(concept, row.stmt):
            stats["stmt_mismatch_rows"] += 1
            continue
        for period_id, (start, end, ptype) in sorted((periods or {}).items()):
            key = (concept, period_id)
            if not _in_era(row, end) or key in held_keys:
                continue
            if (ptype == "instant") != (concept_info[concept][1] == "balance_sheet"):
                continue
            grain = _grain(start, end, ptype)
            if grain is None:
                continue
            if (
                key in value_keys
            ):  # a printed value wins; the clash is reported, never hidden
                stats["blank_conflicts"].append(
                    {
                        "canonical_concept_id": concept,
                        "period_id": period_id,
                        "state": row.decision,
                    }
                )
                continue
            stats["blanks"].append(
                {
                    "canonical_concept_id": concept,
                    "concept_name": concept_info[concept][0],
                    "period_id": period_id,
                    "state": row.decision,
                    "reason": row.reason,
                    "rule_id": row.rule_id,
                    "period_start": start,
                    "period_end": end,
                    "grain": grain,
                }
            )
    for concept, period_id in sorted(conflicts):
        if period_id not in (periods or {}):
            continue
        start, end, ptype = periods[period_id]
        grain = _grain(start, end, ptype)
        if grain is None:
            continue
        stats["blanks"].append(
            {
                "canonical_concept_id": concept,
                "concept_name": concept_info[concept][0],
                "period_id": period_id,
                "state": "defect",
                "defect_class": "finding_open",
                "owner": "tag_mapper",
                "reason_code": "conflicting_values_in_filing",
                "reason": "two listed tags print different values for this concept in the latest filing",
                "rule_id": RULE_ID,
                "period_start": start,
                "period_end": end,
                "grain": grain,
            }
        )
    return cells, stats


def _load_periods(
    conn: psycopg.Connection, company_id: int
) -> dict[int, tuple[date, date, str]]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, start_date, end_date, period_type from core.period where company_id = %s",
            (company_id,),
        )
        return {i: (s, e, t) for i, s, e, t in cur.fetchall()}


def resolve_for_company(
    conn: psycopg.Connection,
    company_id: int,
    managed_concept_ids: set[int],
    concept_info: dict[int, tuple[str, str]],
    run_id: str | None = None,
) -> dict:
    """Rebuild this company's canonical_fact rows from its tag map. Deletes every concept resolve() manages
    (plus every concept the map targets), so no value of the old path survives for a tag-map company."""
    rows = _load_rows(conn, company_id)
    used = {
        (r.taxonomy, r.tag)
        for r in rows
        if r.tag is not None and r.decision != "excluded"
    }
    facts = _load_facts(conn, company_id, used)
    comp_tags = {(r.taxonomy, r.tag) for r in rows if r.decision == "component"}
    accessions = {
        f.accession for k in comp_tags | used for f in facts.get(k, {}).values()
    }
    arcs, dcml = load_calc_evidence(conn, accessions)
    periods = _load_periods(conn, company_id)
    cells, stats = build_cells(rows, facts, concept_info, arcs, dcml, periods)
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
                    (company_id, canonical_concept_id, period_id, value, source_fact_ids, family, rule_run_id)
                values (%s, %s, %s, %s, %s, %s, %s::uuid)
                """,
                [
                    (
                        company_id,
                        c["canonical_concept_id"],
                        c["period_id"],
                        c["value"],
                        c["source_fact_ids"],
                        FAMILY,
                        run_id,
                    )
                    for c in cells
                ],
            )
        cur.execute(
            "delete from analytics.company_combined_line where company_id = %s",
            (company_id,),
        )
        if stats["combined_lines"]:
            cur.executemany(
                """
                insert into analytics.company_combined_line
                    (company_id, period_id, stmt, taxonomy, tag, plabel, components, value,
                     source_fact_ids, tag_map_id, run_id)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid)
                """,
                [
                    (
                        company_id,
                        b["period_id"],
                        b["stmt"],
                        b["taxonomy"],
                        b["tag"],
                        b["plabel"],
                        b["components"],
                        b["value"],
                        b["source_fact_ids"],
                        b["tag_map_id"],
                        run_id,
                    )
                    for b in stats["combined_lines"]
                ],
            )
        if stats["blanks"]:
            if run_id is None:
                raise ValueError(
                    "blank reasons need the rule_run id of the resolve run"
                )
            _write_blanks(conn, company_id, run_id, stats["blanks"], concept_info)
        conn.commit()
    stats["resolved"] = len(cells)
    stats["held_cells"] = len(stats["held"])
    stats["blank_cells"] = len(stats["blanks"])
    stats["combined_line_cells"] = len(stats["combined_lines"])
    logger.info(
        "company_tag_map.company_done",
        company_id=company_id,
        **{
            k: v
            for k, v in stats.items()
            if k not in ("held", "blanks", "blank_conflicts", "combined_lines")
        },
    )
    return stats


def _write_blanks(
    conn, company_id: int, run_id: str, blanks: list[dict], concept_info
) -> int:
    """Reasoned blanks into analytics.cell_blank_reason (state not_presented / not_in_template); the data point
    name is the canonical concept name; the reason and rule_id come from the map row."""
    from scrooner_pipeline.common import cell_store as cs
    from scrooner_pipeline.common.cell_contract import CellKey

    return cs.write_blank_reasons(
        conn,
        run_id,
        [
            cs.BlankReason(
                key=CellKey(
                    company_id,
                    b["concept_name"],
                    b["grain"],
                    b["period_start"],
                    b["period_end"],
                ),
                state=b["state"],
                rule_id=b["rule_id"],
                reason_code=b.get("reason_code", b["state"]),
                defect_class=b.get("defect_class"),
                owner=b.get("owner"),
                reason_text=b["reason"],
                input_refs={"source": "analytics.company_tag_map", "selector": RULE_ID},
            )
            for b in blanks
        ],
    )


def load_concept_info(conn: psycopg.Connection) -> dict[int, tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute("select id, name, statement from analytics.canonical_concept")
        return {i: (n, s) for i, n, s in cur.fetchall()}
