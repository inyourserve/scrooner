"""Duplicate statement columns: rule period.duplicate_column_merge@1 (flag OFF by default).

THE DEFECT (sized read-only 2026-10-31, top-1000): one accounting column exists
as two core.period rows with the same fiscal year/period/type whose ends and
lengths are within 7 days. Two shapes carry statement facts on both rows:
  A. the same quarter spelled two ways (RBC Q2 FY26: 2025-06-29..09-27 with 77
     facts and 2025-07-01..09-27 with 1 fact) -- a stray context;
  B. a recast under a one-day-different context (MSFT Q1 FY17 revenue 20,453
     on 2016-07-01.. and 21,928 on 2016-07-02.., the ASC 606 recast).
Thousands of further pairs are EMPTY instant rows with mid-quarter event dates
(C, JPM, GS, MS: debt-tranche and cover dates that received a fiscal label);
rows without facts are out of scope here. apps/app keys statement columns by
(fiscal_year, fiscal_period, end_date), so shape A/B with different ends shows
two same-label columns; the UI guard in lib/company/db.ts is the other half.

THE RULE (founder ruling 2026-10-31: equal -> one column; different -> hide)
  cluster   period rows of one company with the same (fiscal_year,
            fiscal_period, period_type), ends within MAX_END_GAP_DAYS, lengths
            within MAX_LENGTH_GAP_DAYS, every row carrying at least one fact.
  canonical the row with the most facts (tie: lowest id, i.e. first seen).
  per (concept, unit) on a duplicate row:
    no counterpart on the canonical row     -> REPOINT the facts to the canonical
                                                period (the column gains a value)
    counterpart, values the same number at  -> MERGE: repoint when the unique key
    the company's presentation scale            (company, concept, unit, period,
    (common/presentation_scale)                 filing) stays free, else demote the
                                                duplicate copy (is_authoritative=false)
    counterpart, values differ              -> HIDE: demote every copy on BOTH rows
                                                and write one blank reason per
                                                displayed data point
                                                (analytics.cell_blank_reason,
                                                reason_code duplicate_period_values_differ),
                                                unless an entity rule names the
                                                accounting acquirer's recast (not
                                                built; the hook is `recast_picker`).
  Nothing is deleted. The emptied duplicate core.period row stays (release 1;
  a later cleanup may remove it), so rollback is a per-fact restore of
  (period_id, is_authoritative) from the before-image plus a delete of this
  run's reason rows.

Durability of a hide: dedupe.plan_authority leaves a lone periodic copy's
authority untouched (it only promotes a lone copy when non-periodic copies sit
beside it) and conflict-fill only fills groups of 2+ disagreeing copies in ONE
period, so demoted copies on two different period rows stay demoted and
unfilled. Re-pointed copies form an ordinary same-period group for dedupe.

Modes (common/rule_flags): off/dry_run -> plan only, nothing written; on ->
apply, one transaction per company, before-image first.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import psycopg
import structlog

from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.common.cell_store import (
    BlankReason,
    delete_run_blank_reasons,
    finish_rule_run,
    replace_rule_reasons,
    start_rule_run,
)
from scrooner_pipeline.common.presentation_scale import (
    company_presentation_scale,
    same_number,
)
from scrooner_pipeline.common.rule_flags import (
    ON,
    RULE_DUPLICATE_COLUMN_MERGE,
    rule_mode,
)

logger = structlog.get_logger()

RULE_ID = RULE_DUPLICATE_COLUMN_MERGE
MAX_END_GAP_DAYS = 7
MAX_LENGTH_GAP_DAYS = 7
REASON_CODE_DIFFER = "duplicate_period_values_differ"

REPOINT, MERGE, HIDE = "repoint", "merge", "hide"


@dataclass(frozen=True)
class PeriodRow:
    id: int
    start: date
    end: date
    period_type: str
    fiscal_year: int
    fiscal_period: str
    fact_count: int

    @property
    def length(self) -> int:
        return (self.end - self.start).days

    @property
    def grain(self) -> str:
        if self.period_type == "instant":
            return "I"
        return "FY" if self.fiscal_period == "FY" else "Q"


@dataclass
class Cluster:
    canonical: PeriodRow
    duplicates: list[PeriodRow]


@dataclass(frozen=True)
class FactCopy:
    id: int
    concept_id: int
    unit_id: int
    value: Decimal
    filing_id: int
    is_authoritative: bool
    is_derived: bool


@dataclass
class CellAction:
    action: str  # REPOINT | MERGE | HIDE
    concept_id: int
    unit_id: int
    duplicate: PeriodRow
    canonical: PeriodRow
    duplicate_values: list[Decimal]
    canonical_values: list[Decimal]
    repoint_fact_ids: list[int] = field(default_factory=list)
    demote_fact_ids: list[int] = field(default_factory=list)


@dataclass
class CompanyPlan:
    company_id: int
    scale: int
    clusters: list[Cluster]
    actions: list[CellAction]

    def stats(self) -> dict[str, int]:
        out = {
            "clusters": len(self.clusters),
            "duplicate_rows": sum(len(c.duplicates) for c in self.clusters),
            REPOINT: 0,
            MERGE: 0,
            HIDE: 0,
            "facts_repointed": 0,
            "facts_demoted": 0,
        }
        for a in self.actions:
            out[a.action] += 1
            out["facts_repointed"] += len(a.repoint_fact_ids)
            out["facts_demoted"] += len(a.demote_fact_ids)
        return out


# ---- clustering ---------------------------------------------------------------


def _load_period_rows(conn: psycopg.Connection, company_id: int) -> list[PeriodRow]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select p.id, p.start_date, p.end_date, p.period_type, p.fiscal_year, p.fiscal_period,
                   (select count(*) from core.fact f where f.period_id = p.id) as n
            from core.period p
            where p.company_id = %s and p.fiscal_year is not null and p.fiscal_period is not null
            order by p.fiscal_year, p.fiscal_period, p.period_type, p.end_date, p.id
            """,
            (company_id,),
        )
        return [PeriodRow(*r) for r in cur.fetchall()]


def cluster_periods(rows: list[PeriodRow]) -> list[Cluster]:
    """Pure. Rows without facts never cluster (empty event-date instants)."""
    by_key: dict[tuple, list[PeriodRow]] = defaultdict(list)
    for r in rows:
        if r.fact_count > 0:
            by_key[(r.fiscal_year, r.fiscal_period, r.period_type)].append(r)
    clusters: list[Cluster] = []
    for _key, group in sorted(by_key.items()):
        group = sorted(group, key=lambda r: (r.end, r.id))
        taken: set[int] = set()
        for anchor in group:
            if anchor.id in taken:
                continue
            members = [anchor]
            for other in group:
                if other.id == anchor.id or other.id in taken:
                    continue
                if (
                    abs((other.end - anchor.end).days) <= MAX_END_GAP_DAYS
                    and abs(other.length - anchor.length) <= MAX_LENGTH_GAP_DAYS
                ):
                    members.append(other)
            if len(members) < 2:
                continue
            taken.update(m.id for m in members)
            canonical = max(members, key=lambda r: (r.fact_count, -r.id))
            clusters.append(
                Cluster(canonical, [m for m in members if m.id != canonical.id])
            )
    return clusters


# ---- planning -----------------------------------------------------------------


def _load_facts(
    conn: psycopg.Connection, period_ids: list[int]
) -> dict[int, list[FactCopy]]:
    out: dict[int, list[FactCopy]] = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            "select period_id, id, concept_id, unit_id, value, filing_id, is_authoritative, is_derived "
            "from core.fact where period_id = any(%s) order by id",
            (period_ids,),
        )
        for pid, fid, cid, uid, value, filing_id, auth, der in cur.fetchall():
            out[pid].append(
                FactCopy(
                    fid, cid, uid, Decimal(value), filing_id, bool(auth), bool(der)
                )
            )
    return out


RecastPicker = Callable[[int, int, PeriodRow, PeriodRow], PeriodRow | None]
"""(company_id, concept_id, duplicate, canonical) -> the row whose value is the
accounting acquirer's recast, or None. Not built; the hook exists so the
founder's exception ("unless an entity rule picks the recast") has a place."""


def plan_cells(
    company_id: int,
    clusters: list[Cluster],
    facts_by_period: dict[int, list[FactCopy]],
    scale: int,
    recast_picker: RecastPicker | None = None,
) -> list[CellAction]:
    """Pure. One CellAction per (concept, unit) present on a duplicate row."""
    actions: list[CellAction] = []
    for cl in clusters:
        can = cl.canonical
        can_by_cell: dict[tuple[int, int], list[FactCopy]] = defaultdict(list)
        for f in facts_by_period.get(can.id, []):
            can_by_cell[(f.concept_id, f.unit_id)].append(f)
        for dup in cl.duplicates:
            dup_by_cell: dict[tuple[int, int], list[FactCopy]] = defaultdict(list)
            for f in facts_by_period.get(dup.id, []):
                dup_by_cell[(f.concept_id, f.unit_id)].append(f)
            for (concept_id, unit_id), dfacts in sorted(dup_by_cell.items()):
                cfacts = can_by_cell.get((concept_id, unit_id), [])
                dvals = sorted({f.value for f in dfacts})
                cvals = sorted({f.value for f in cfacts})
                if not cfacts:
                    actions.append(
                        CellAction(
                            REPOINT,
                            concept_id,
                            unit_id,
                            dup,
                            can,
                            dvals,
                            cvals,
                            repoint_fact_ids=[f.id for f in dfacts],
                        )
                    )
                    continue
                agree = all(same_number(a, b, scale) for a in dvals for b in cvals)
                if agree:
                    taken = {f.filing_id for f in cfacts}
                    act = CellAction(MERGE, concept_id, unit_id, dup, can, dvals, cvals)
                    for f in dfacts:
                        if f.filing_id in taken:
                            if f.is_authoritative:
                                act.demote_fact_ids.append(f.id)
                        else:
                            act.repoint_fact_ids.append(f.id)
                            taken.add(f.filing_id)
                    actions.append(act)
                    continue
                if recast_picker is not None:
                    chosen = recast_picker(company_id, concept_id, dup, can)
                    if chosen is not None:
                        loser = dfacts if chosen.id == can.id else cfacts
                        actions.append(
                            CellAction(
                                HIDE,
                                concept_id,
                                unit_id,
                                dup,
                                can,
                                dvals,
                                cvals,
                                demote_fact_ids=[
                                    f.id for f in loser if f.is_authoritative
                                ],
                            )
                        )
                        continue
                actions.append(
                    CellAction(
                        HIDE,
                        concept_id,
                        unit_id,
                        dup,
                        can,
                        dvals,
                        cvals,
                        demote_fact_ids=[
                            f.id for f in dfacts + cfacts if f.is_authoritative
                        ],
                    )
                )
    return actions


def plan_company(
    conn: psycopg.Connection, company_id: int, recast_picker: RecastPicker | None = None
) -> CompanyPlan:
    rows = _load_period_rows(conn, company_id)
    clusters = cluster_periods(rows)
    if not clusters:
        return CompanyPlan(company_id, 0, [], [])
    scale = company_presentation_scale(conn, company_id)
    pids = [c.canonical.id for c in clusters] + [
        d.id for c in clusters for d in c.duplicates
    ]
    facts = _load_facts(conn, pids)
    return CompanyPlan(
        company_id,
        scale,
        clusters,
        plan_cells(company_id, clusters, facts, scale, recast_picker),
    )


# ---- reasons ------------------------------------------------------------------


def _canonical_names(
    conn: psycopg.Connection, concept_ids: list[int]
) -> dict[int, list[str]]:
    if not concept_ids:
        return {}
    out: dict[int, list[str]] = defaultdict(list)
    with conn.cursor() as cur:
        cur.execute(
            "select cm.concept_id, cc.name from analytics.concept_mapping cm "
            "join analytics.canonical_concept cc on cc.id = cm.canonical_concept_id "
            "where cm.concept_id = any(%s) and cm.confidence <> 'rejected' order by 1, 2",
            (sorted(set(concept_ids)),),
        )
        for cid, name in cur.fetchall():
            out[cid].append(name)
    return dict(out)


def hide_reasons(
    company_id: int, action: CellAction, names: list[str]
) -> list[BlankReason]:
    can, dup = action.canonical, action.duplicate
    text = (
        f"Two filed versions of {can.fiscal_period} {can.fiscal_year} differ: "
        f"{', '.join(str(v) for v in action.canonical_values)} ({can.start}..{can.end}) vs "
        f"{', '.join(str(v) for v in action.duplicate_values)} ({dup.start}..{dup.end}); "
        "neither is shown until a recast rule picks one."
    )
    refs = {
        "canonical_period_id": can.id,
        "duplicate_period_id": dup.id,
        "canonical_values": [str(v) for v in action.canonical_values],
        "duplicate_values": [str(v) for v in action.duplicate_values],
        "demoted_fact_ids": list(action.demote_fact_ids),
    }
    out = []
    for name in names:
        out.append(
            BlankReason(
                key=CellKey(company_id, name, can.grain, can.start, can.end, "latest"),
                state="defect",
                rule_id=RULE_ID,
                reason_code=REASON_CODE_DIFFER,
                defect_class="period",
                owner="period_engineer",
                root_cause_class="period",
                reason_text=text,
                input_refs=refs,
                source_fact_ids=tuple(action.demote_fact_ids),
            )
        )
    return out


# ---- apply / rollback -----------------------------------------------------------


def _json_default(o: Any) -> Any:
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(type(o))


def _before_image(conn: psycopg.Connection, fact_ids: list[int]) -> list[dict]:
    if not fact_ids:
        return []
    with conn.cursor() as cur:
        cur.execute(
            "select id, period_id, is_authoritative from core.fact where id = any(%s) order by id",
            (fact_ids,),
        )
        return [
            {"id": i, "period_id": p, "is_authoritative": a}
            for i, p, a in cur.fetchall()
        ]


def apply_company(
    conn: psycopg.Connection, plan: CompanyPlan, run_id: str, backup_dir: Path
) -> dict[str, Any]:
    """ONE transaction: before-image to <backup_dir>/<company_id>.jsonl, then the
    fact updates and the reason rows. Raises unless the rule is ON."""
    if rule_mode(RULE_ID) != ON:
        raise RuntimeError(f"{RULE_ID} is not ON; refusing to write")
    touched = sorted(
        {f for a in plan.actions for f in a.repoint_fact_ids + a.demote_fact_ids}
    )
    image = _before_image(conn, touched)
    backup_dir.mkdir(parents=True, exist_ok=True)
    path = backup_dir / f"{plan.company_id}.jsonl"
    with path.open("w") as fh:
        fh.write(
            json.dumps(
                {
                    "company_id": plan.company_id,
                    "run_id": run_id,
                    "rule_id": RULE_ID,
                    "taken_at": datetime.now().isoformat(timespec="seconds"),
                    "facts": len(image),
                },
                default=_json_default,
            )
            + "\n"
        )
        for row in image:
            fh.write(json.dumps(row, default=_json_default) + "\n")
    names = _canonical_names(
        conn, [a.concept_id for a in plan.actions if a.action == HIDE]
    )
    reasons: list[BlankReason] = []
    with conn.transaction():
        with conn.cursor() as cur:
            for a in plan.actions:
                if a.repoint_fact_ids:
                    cur.execute(
                        "update core.fact set period_id = %s where id = any(%s)",
                        (a.canonical.id, a.repoint_fact_ids),
                    )
                if a.demote_fact_ids:
                    cur.execute(
                        "update core.fact set is_authoritative = false where id = any(%s)",
                        (a.demote_fact_ids,),
                    )
                if a.action == HIDE:
                    reasons.extend(
                        hide_reasons(plan.company_id, a, names.get(a.concept_id, []))
                    )
        written = replace_rule_reasons(conn, run_id, plan.company_id, RULE_ID, reasons)
    stats = plan.stats()
    stats["reasons_written"] = written
    stats["before_image"] = str(path)
    logger.info("duplicate_columns.applied", company_id=plan.company_id, **stats)
    return stats


def rollback_company(conn: psycopg.Connection, image_path: Path) -> dict[str, int]:
    """Restore (period_id, is_authoritative) of every fact in the image and
    delete the run's reason rows for this company. One transaction."""
    lines = [json.loads(l) for l in image_path.open()]
    head, rows = lines[0], lines[1:]
    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(
                "update core.fact set period_id = %(period_id)s, is_authoritative = %(is_authoritative)s where id = %(id)s",
                rows,
            )
            cur.execute(
                "delete from analytics.cell_blank_reason where run_id = %s::uuid and company_id = %s and rule_id = %s",
                (head["run_id"], head["company_id"], head["rule_id"]),
            )
            deleted = cur.rowcount
    return {"facts_restored": len(rows), "reasons_deleted": deleted}


# ---- driver -----------------------------------------------------------------------


def run(
    conn: psycopg.Connection,
    ciks: set[str],
    *,
    backup_dir: Path | None = None,
    report_path: Path | None = None,
) -> dict[str, Any]:
    """Plan every company; apply only when the rule is ON (then backup_dir is
    required). Dry-run output: per-company stats and, in report_path (JSONL),
    every planned cell action with values and periods for the Verifier."""
    mode = rule_mode(RULE_ID)
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        ids = dict(cur.fetchall())
    totals: dict[str, Any] = {
        "mode": mode,
        "companies": 0,
        "companies_with_duplicates": 0,
        "clusters": 0,
        "duplicate_rows": 0,
        REPOINT: 0,
        MERGE: 0,
        HIDE: 0,
        "facts_repointed": 0,
        "facts_demoted": 0,
        "errored": 0,
    }
    run_id = None
    if mode == ON:
        if backup_dir is None:
            raise ValueError("backup_dir is required when the rule is ON")
        run_id = start_rule_run(
            conn, RULE_ID, "apply", "on", sorted(ciks), before_image_ref=str(backup_dir)
        )
        conn.commit()
    report = report_path.open("a") if report_path else None
    try:
        for cik in sorted(ciks):
            company_id = ids.get(cik)
            if company_id is None:
                continue
            totals["companies"] += 1
            try:
                plan = plan_company(conn, company_id)
                if run_id is not None and plan.actions:
                    apply_company(conn, plan, run_id, backup_dir)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                totals["errored"] += 1
                logger.error(
                    "duplicate_columns.company_failed", cik=cik, error=repr(exc)[:200]
                )
                conn.rollback()
                continue
            if plan.actions:
                totals["companies_with_duplicates"] += 1
            for k, v in plan.stats().items():
                totals[k] += v
            if report is not None:
                for a in plan.actions:
                    report.write(
                        json.dumps(
                            {
                                "company_id": company_id,
                                "cik": cik,
                                "scale": plan.scale,
                                "action": a.action,
                                "concept_id": a.concept_id,
                                "unit_id": a.unit_id,
                                "canonical": [
                                    a.canonical.id,
                                    a.canonical.start,
                                    a.canonical.end,
                                    a.canonical.fact_count,
                                ],
                                "duplicate": [
                                    a.duplicate.id,
                                    a.duplicate.start,
                                    a.duplicate.end,
                                    a.duplicate.fact_count,
                                ],
                                "fiscal": [
                                    a.canonical.fiscal_year,
                                    a.canonical.fiscal_period,
                                    a.canonical.period_type,
                                ],
                                "canonical_values": a.canonical_values,
                                "duplicate_values": a.duplicate_values,
                                "repoint_fact_ids": a.repoint_fact_ids,
                                "demote_fact_ids": a.demote_fact_ids,
                            },
                            default=_json_default,
                        )
                        + "\n"
                    )
    finally:
        if report is not None:
            report.close()
    if run_id is not None:
        finish_rule_run(conn, run_id, totals)
        conn.commit()
        totals["run_id"] = run_id
    logger.info("duplicate_columns.done", **totals)
    return totals


def rollback_run(conn: psycopg.Connection, backup_dir: Path) -> dict[str, int]:
    out = {"companies": 0, "facts_restored": 0, "reasons_deleted": 0}
    for path in sorted(backup_dir.glob("*.jsonl")):
        r = rollback_company(conn, path)
        out["companies"] += 1
        out["facts_restored"] += r["facts_restored"]
        out["reasons_deleted"] += r["reasons_deleted"]
    return out


__all__ = [
    "RULE_ID",
    "REASON_CODE_DIFFER",
    "PeriodRow",
    "Cluster",
    "FactCopy",
    "CellAction",
    "CompanyPlan",
    "cluster_periods",
    "plan_cells",
    "plan_company",
    "apply_company",
    "rollback_company",
    "run",
    "rollback_run",
    "delete_run_blank_reasons",
]
