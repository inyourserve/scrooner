"""Co-registrant copies of a combined filing: demote and archive
(rule entity.shared_accession_demote_coregistrant_facts@1, flag OFF by default).

THE DEFECT (found post-apply by Ritwik, 2026-10-31): entity.shared_accession_
primary_filer@1 moved 499 combined 10-K/10-Q rows of core.filing to their
primary registrant, but the facts a CO-REGISTRANT had normalized from those
filings stayed authoritative, because normalizer/facts.py upserts and never
deletes (the dry-run report in data-team/38 wrongly said a re-normalize would
drop them). Live: Entergy Arkansas 467, Southern California Edison 388,
SoCalGas 543, Consumers Energy 374 core.fact rows (1,772) and 600
analytics.canonical_fact cells that show the PARENT's consolidated numbers
under the subsidiary's CIK.

THE RULE
  scope   a company's core.fact rows whose filing is now owned by another
          company that core.filing_registrant names as the accession's
          primary (so the move was the rule's, not a data error)
  facts   is_authoritative = false (demoted, never deleted; the rows stay
          inspectable and dedupe leaves a lone demoted copy alone)
  cells   every analytics.canonical_fact row of the company whose
          source_fact_ids include a demoted fact is archived to
          analytics.canonical_fact_retired and removed (mapper/canonical_archive,
          the one archive-then-remove path), and one blank reason per cell is
          written (cell_blank_reason, reason_code
          parent_values_filed_under_coregistrant_cik) so the page shows a
          reason, never a value
  before-image per company (facts: id + is_authoritative; cells: full rows)
  rollback: restore authority from the image, restore_run() the archived
          cells, delete the run's reason rows
Modes: off/dry_run -> plan only; on -> apply, one transaction per company.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
import structlog

from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.common.cell_store import (
    BlankReason,
    finish_rule_run,
    replace_rule_reasons,
    start_rule_run,
)
from scrooner_pipeline.common.rule_flags import (
    ON,
    RULE_SHARED_ACCESSION_DEMOTE_COREGISTRANT,
    rule_mode,
)
from scrooner_pipeline.mapper.canonical_archive import archive_and_remove, restore_run

logger = structlog.get_logger()

RULE_ID = RULE_SHARED_ACCESSION_DEMOTE_COREGISTRANT
REASON_CODE = "parent_values_filed_under_coregistrant_cik"


@dataclass
class CompanyPlan:
    company_id: int
    cik: str
    fact_ids: list[int] = field(default_factory=list)  # authoritative copies to demote
    already_demoted: int = 0
    filings: dict[str, tuple[int, str]] = field(
        default_factory=dict
    )  # accession -> (owner id, owner cik)
    cells: list[dict[str, Any]] = field(
        default_factory=list
    )  # canonical rows sourced from those facts

    def stats(self) -> dict[str, int]:
        return {
            "facts_to_demote": len(self.fact_ids),
            "facts_already_demoted": self.already_demoted,
            "filings": len(self.filings),
            "cells_to_archive": len(self.cells),
        }


def plan_company(conn: psycopg.Connection, company_id: int) -> CompanyPlan:
    with conn.cursor() as cur:
        cur.execute("select cik from core.company where id = %s", (company_id,))
        row = cur.fetchone()
        if row is None:
            raise LookupError(company_id)
        plan = CompanyPlan(company_id, row[0])
        cur.execute(
            """
            select f.id, f.is_authoritative, fl.accession_number, fl.company_id, oc.cik
            from core.fact f
            join core.filing fl on fl.id = f.filing_id
            join core.filing_registrant r
              on r.accession_number = fl.accession_number and r.role = 'primary' and r.company_id = fl.company_id
            join core.company oc on oc.id = fl.company_id
            where f.company_id = %s and fl.company_id <> %s
            order by f.id
            """,
            (company_id, company_id),
        )
        all_ids: list[int] = []
        for fid, auth, acc, owner_id, owner_cik in cur.fetchall():
            all_ids.append(fid)
            plan.filings[acc] = (owner_id, owner_cik)
            if auth:
                plan.fact_ids.append(fid)
            else:
                plan.already_demoted += 1
        if all_ids:
            cur.execute(
                """
                select cf.id, cf.canonical_concept_id, cc.name, cf.period_id, p.period_type, p.fiscal_period,
                       p.start_date, p.end_date, cf.value, cf.source_fact_ids, cf.resolved_at
                from analytics.canonical_fact cf
                join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
                join core.period p on p.id = cf.period_id
                where cf.company_id = %s and cf.source_fact_ids && %s::bigint[]
                order by cf.id
                """,
                (company_id, all_ids),
            )
            for r in cur.fetchall():
                plan.cells.append(
                    {
                        "id": r[0],
                        "canonical_concept_id": r[1],
                        "name": r[2],
                        "period_id": r[3],
                        "period_type": r[4],
                        "fiscal_period": r[5],
                        "start_date": r[6],
                        "end_date": r[7],
                        "value": r[8],
                        "source_fact_ids": list(r[9] or []),
                        "resolved_at": r[10],
                    }
                )
    return plan


def _grain(cell: dict[str, Any]) -> str:
    if cell["period_type"] == "instant":
        return "I"
    if cell["fiscal_period"] == "FY":
        return "FY"
    days = (cell["end_date"] - cell["start_date"]).days
    return "Q" if days <= 100 else "TP"


def reasons_for(plan: CompanyPlan) -> list[BlankReason]:
    out = []
    seen: set[tuple] = set()
    for c in plan.cells:
        key = CellKey(
            plan.company_id,
            c["name"],
            _grain(c),
            c["start_date"],
            c["end_date"],
            "latest",
        )
        k = (key.data_point_name, key.period_grain, key.period_start, key.period_end)
        if k in seen:
            continue
        seen.add(k)
        owners = sorted(
            {f"{cik} (company {cid})" for cid, cik in plan.filings.values()}
        )
        out.append(
            BlankReason(
                key=key,
                state="defect",
                rule_id=RULE_ID,
                reason_code=REASON_CODE,
                defect_class="identity",
                owner="company_master",
                root_cause_class="identity",
                reason_text=(
                    f"value {c['value']} came from a combined filing whose primary registrant is "
                    f"{', '.join(owners)}; SEC attributed the parent's consolidated figures to this CIK. "
                    "Demoted; nothing is shown until this company's own figures are sourced."
                ),
                input_refs={
                    "accessions": sorted(plan.filings),
                    "canonical_fact_id": c["id"],
                    "value": str(c["value"]),
                },
                source_fact_ids=tuple(c["source_fact_ids"]),
            )
        )
    return out


def _json_default(o: Any) -> Any:
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(type(o))


def apply_company(
    conn: psycopg.Connection, plan: CompanyPlan, run_id: str, backup_dir: Path
) -> dict[str, Any]:
    if rule_mode(RULE_ID) != ON:
        raise RuntimeError(f"{RULE_ID} is not ON; refusing to write")
    backup_dir.mkdir(parents=True, exist_ok=True)
    path = backup_dir / f"{plan.company_id}.jsonl"
    with path.open("w") as fh:
        fh.write(
            json.dumps(
                {
                    "company_id": plan.company_id,
                    "cik": plan.cik,
                    "run_id": run_id,
                    "rule_id": RULE_ID,
                    "taken_at": datetime.now().isoformat(timespec="seconds"),
                    "facts": len(plan.fact_ids),
                    "cells": len(plan.cells),
                }
            )
            + "\n"
        )
        for fid in plan.fact_ids:
            fh.write(
                json.dumps({"kind": "fact", "id": fid, "is_authoritative": True}) + "\n"
            )
        for c in plan.cells:
            fh.write(json.dumps({"kind": "cell", **c}, default=_json_default) + "\n")
    reasons = reasons_for(plan)
    with conn.transaction():
        with conn.cursor() as cur:
            if plan.fact_ids:
                cur.execute(
                    "update core.fact set is_authoritative = false where id = any(%s)",
                    (plan.fact_ids,),
                )
            archived = (
                archive_and_remove(
                    cur,
                    [c["id"] for c in plan.cells],
                    reason_code=REASON_CODE,
                    run_id=run_id,
                )
                if plan.cells
                else 0
            )
        written = replace_rule_reasons(conn, run_id, plan.company_id, RULE_ID, reasons)
    out = plan.stats()
    out.update(
        {
            "cells_archived": archived,
            "reasons_written": written,
            "before_image": str(path),
        }
    )
    logger.info("shared_accession_cleanup.applied", company_id=plan.company_id, **out)
    return out


def rollback_company(conn: psycopg.Connection, image_path: Path) -> dict[str, int]:
    lines = [json.loads(l) for l in image_path.open()]
    head, rows = lines[0], lines[1:]
    fact_ids = [r["id"] for r in rows if r["kind"] == "fact"]
    with conn.transaction():
        with conn.cursor() as cur:
            if fact_ids:
                cur.execute(
                    "update core.fact set is_authoritative = true where id = any(%s)",
                    (fact_ids,),
                )
            restored = restore_run(cur, head["run_id"])
            cur.execute(
                "delete from analytics.cell_blank_reason where run_id = %s::uuid and company_id = %s and rule_id = %s",
                (head["run_id"], head["company_id"], head["rule_id"]),
            )
            deleted = cur.rowcount
    return {
        "facts_restored": len(fact_ids),
        "cells_restored": restored,
        "reasons_deleted": deleted,
    }


def run(
    conn: psycopg.Connection, ciks: set[str], *, backup_dir: Path | None = None
) -> dict[str, Any]:
    mode = rule_mode(RULE_ID)
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (sorted(ciks),)
        )
        ids = dict(cur.fetchall())
    totals: dict[str, Any] = {
        "mode": mode,
        "companies": 0,
        "facts_to_demote": 0,
        "facts_already_demoted": 0,
        "filings": 0,
        "cells_to_archive": 0,
        "errored": 0,
        "per_company": {},
    }
    run_id = None
    if mode == ON:
        if backup_dir is None:
            raise ValueError("backup_dir is required when the rule is ON")
        run_id = start_rule_run(
            conn, RULE_ID, "apply", "on", sorted(ciks), before_image_ref=str(backup_dir)
        )
        conn.commit()
    for cik in sorted(ciks):
        company_id = ids.get(cik)
        if company_id is None:
            continue
        totals["companies"] += 1
        try:
            plan = plan_company(conn, company_id)
            if run_id is not None and (plan.fact_ids or plan.cells):
                apply_company(conn, plan, run_id, backup_dir)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001
            totals["errored"] += 1
            logger.error(
                "shared_accession_cleanup.company_failed",
                cik=cik,
                error=repr(exc)[:200],
            )
            conn.rollback()
            continue
        st = plan.stats()
        st["filings_owned_by"] = sorted({cik2 for _cid, cik2 in plan.filings.values()})
        totals["per_company"][cik] = st
        for k in (
            "facts_to_demote",
            "facts_already_demoted",
            "filings",
            "cells_to_archive",
        ):
            totals[k] += st[k]
    if run_id is not None:
        finish_rule_run(
            conn, run_id, {k: v for k, v in totals.items() if k != "per_company"}
        )
        conn.commit()
        totals["run_id"] = run_id
    logger.info(
        "shared_accession_cleanup.done",
        **{k: v for k, v in totals.items() if k != "per_company"},
    )
    return totals


def rollback_run_dir(conn: psycopg.Connection, backup_dir: Path) -> dict[str, int]:
    out = {
        "companies": 0,
        "facts_restored": 0,
        "cells_restored": 0,
        "reasons_deleted": 0,
    }
    for path in sorted(backup_dir.glob("*.jsonl")):
        r = rollback_company(conn, path)
        out["companies"] += 1
        for k in ("facts_restored", "cells_restored", "reasons_deleted"):
            out[k] += r[k]
    return out
