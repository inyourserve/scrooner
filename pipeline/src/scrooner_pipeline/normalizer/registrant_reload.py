"""Reload plan for P1 (entity.shared_accession_primary_filer@1): move the
claims of shared accessions to their primary filer and drop the facts that were
loaded under the wrong company. DRY-RUN BY DEFAULT.

  plan_reload()   read-only. For each stored decision it reports what exists
                  today (who owns core.filing, how many facts under whom,
                  blockers that would stop a delete) and what apply would do.
  apply_reload()  the only writer. Refuses without (a) a backup file that holds
                  every fact row it will delete, (b) zero blockers, (c) a plan
                  whose accession set it was given. Does not commit. Moves the
                  filing (UPDATE core.filing.company_id, by accession), deletes
                  the wrong-company facts of exactly those filings (by id), and
                  nothing else. The nightly identity stage never does this.

After apply: run identity -> periods -> units -> facts -> dedupe -> ... for the
primary AND every holder CIK with SCROONER_RULES_ENABLED containing the rule
(the periods and facts stages then rebuild the primary's payload from the
co-registrants' payloads). Stale canonical_fact / metric_value rows of the holder
are rebuilt by that same recompute (their source facts no longer exist).
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import psycopg

from scrooner_pipeline.common.cell_store import RegistrantRow, write_filing_registrants
from scrooner_pipeline.normalizer.registrant import PrimaryFilerDecision


@dataclass
class AccessionPlan:
    accession_number: str
    primary_cik: str | None
    quarantined: bool
    reason: str | None
    primary_company_id: int | None
    filing_id: int | None
    filing_owner_company_id: int | None
    facts_under_owner: int = 0
    facts_to_delete: int = 0
    actions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


def _company_ids(conn: psycopg.Connection, ciks: Sequence[str]) -> dict[str, int]:
    with conn.cursor() as cur:
        cur.execute(
            "select cik, id from core.company where cik = any(%s)", (list(ciks),)
        )
        return dict(cur.fetchall())


def persist_decisions(
    conn: psycopg.Connection, decisions: Sequence[PrimaryFilerDecision]
) -> int:
    """Write core.filing_registrant rows (replaces the rows of each accession).
    Does not commit. Only shared or quarantined accessions need rows, but a
    single-filer decision is also stored so the table answers 'who is the
    primary' for every accession it has seen."""
    ids = _company_ids(conn, sorted({c for d in decisions for c in d.registrant_ciks}))
    for d in decisions:
        rows = [RegistrantRow(c, d.role_of(c), ids.get(c)) for c in d.registrant_ciks]
        write_filing_registrants(
            conn,
            d.accession_number,
            rows,
            dei_default_cik=d.dei_default_cik,
            header_first_filer_cik=d.header_first_filer_cik,
            quarantine_reason=d.quarantine_reason,
        )
    return len(decisions)


def plan_reload(
    conn: psycopg.Connection, decisions: Sequence[PrimaryFilerDecision]
) -> list[AccessionPlan]:
    shared = [d for d in decisions if d.shared or d.quarantined]
    ids = _company_ids(conn, sorted({c for d in shared for c in d.registrant_ciks}))
    plans: list[AccessionPlan] = []
    with conn.cursor() as cur:
        for d in shared:
            cur.execute(
                "select id, company_id from core.filing where accession_number = %s",
                (d.accession_number,),
            )
            row = cur.fetchone()
            primary_id = ids.get(d.primary_cik) if d.primary_cik else None
            p = AccessionPlan(
                accession_number=d.accession_number,
                primary_cik=d.primary_cik,
                quarantined=d.quarantined,
                reason=d.quarantine_reason,
                primary_company_id=primary_id,
                filing_id=row[0] if row else None,
                filing_owner_company_id=row[1] if row else None,
            )
            if d.primary_cik is not None and primary_id is None:
                p.blockers.append(f"primary CIK {d.primary_cik} is not in core.company")
            if row:
                cur.execute(
                    "select count(*) from core.fact where filing_id = %s", (row[0],)
                )
                p.facts_under_owner = cur.fetchone()[0]
                wrong = (
                    "company_id <> %s"
                    if primary_id is not None and not d.quarantined
                    else "true"
                )
                params = (row[0], primary_id) if wrong != "true" else (row[0],)
                cur.execute(
                    f"select count(*) from core.fact where filing_id = %s and {wrong}",
                    params,
                )
                p.facts_to_delete = cur.fetchone()[0]
                if p.facts_to_delete:
                    cur.execute(
                        "select count(*) from analytics.company_stock_split s "
                        "join core.fact f on f.id = s.source_fact_id "
                        f"where f.filing_id = %s and {wrong.replace('company_id', 'f.company_id')}",
                        params,
                    )
                    n = cur.fetchone()[0]
                    if n:
                        p.blockers.append(
                            f"{n} analytics.company_stock_split rows cite these facts"
                        )
                if d.quarantined:
                    p.actions.append(
                        f"delete {p.facts_to_delete} facts of the quarantined accession"
                    )
                elif row[1] != primary_id:
                    p.actions.append(
                        f"move core.filing {row[0]} from company {row[1]} to {primary_id}"
                    )
                    p.actions.append(
                        f"delete {p.facts_to_delete} facts held under the wrong company"
                    )
            else:
                p.actions.append(
                    "no core.filing row yet: identity creates it for the primary"
                )
            plans.append(p)
    return plans


def write_backup(
    conn: psycopg.Connection, plans: Sequence[AccessionPlan], path: Path
) -> int:
    """JSON lines of every core.fact row apply would delete (full row)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with conn.cursor() as cur, path.open("w", encoding="utf-8") as fh:
        for p in plans:
            if p.filing_id is None or not p.facts_to_delete:
                continue
            if p.quarantined or p.primary_company_id is None:
                cur.execute(
                    "select * from core.fact where filing_id = %s", (p.filing_id,)
                )
            else:
                cur.execute(
                    "select * from core.fact where filing_id = %s and company_id <> %s",
                    (p.filing_id, p.primary_company_id),
                )
            cols = [c.name for c in cur.description]
            for r in cur.fetchall():
                fh.write(
                    json.dumps(dict(zip(cols, r)), default=str, sort_keys=True) + "\n"
                )
                n += 1
    return n


def apply_reload(
    conn: psycopg.Connection, plans: Sequence[AccessionPlan], backup_path: Path
) -> dict[str, int]:
    blockers = [(p.accession_number, b) for p in plans for b in p.blockers]
    if blockers:
        raise ValueError(f"refusing to apply: blockers {blockers}")
    if not backup_path.exists():
        raise FileNotFoundError(f"backup {backup_path} missing: refusing to delete")
    backed_up = {
        json.loads(line)["id"]
        for line in backup_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    moved = deleted = 0
    with conn.cursor() as cur:
        for p in plans:
            if p.filing_id is None:
                continue
            if p.quarantined or p.primary_company_id is None:
                cur.execute(
                    "select id from core.fact where filing_id = %s", (p.filing_id,)
                )
            else:
                cur.execute(
                    "select id from core.fact where filing_id = %s and company_id <> %s",
                    (p.filing_id, p.primary_company_id),
                )
            ids = [r[0] for r in cur.fetchall()]
            missing = set(ids) - backed_up
            if missing:
                raise ValueError(
                    f"{len(missing)} fact ids of {p.accession_number} are not in the backup"
                )
            for i in range(0, len(ids), 5000):
                chunk = ids[i : i + 5000]
                cur.execute(
                    "update core.fact set supersedes_fact_id = null where supersedes_fact_id = any(%s)",
                    (chunk,),
                )
                cur.execute("delete from core.fact where id = any(%s)", (chunk,))
                deleted += cur.rowcount
            if (
                not p.quarantined
                and p.primary_company_id is not None
                and p.filing_owner_company_id != p.primary_company_id
            ):
                cur.execute(
                    "update core.filing set company_id = %s where accession_number = %s",
                    (p.primary_company_id, p.accession_number),
                )
                moved += cur.rowcount
    return {"filings_moved": moved, "facts_deleted": deleted}
