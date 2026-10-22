"""Repair list for rule source.periodic_form_only@1 (W3): stored canonical
values whose source facts include a non-periodic filing.

Why a separate step exists: every writer of a `*_resolved` concept is INSERT
... ON CONFLICT DO NOTHING (conflict_resolution.py), so fixing Stage 2e and
the fill query does not remove a value filled earlier from a rounded DEF 14A
copy (JPM FY net income 57,000M, MA, SCHW, MDT -- data-team/36 item 2). The
stale cell must be deleted, then the normal chain (resolve-facts, baseline
passthrough, conflict fill) refills it from the periodic copies. Doing that
blind would turn some cells into blanks (no periodic copy exists), so:

- find_non_periodic_sourced_cells() is READ-ONLY and classifies every cell;
- purge_cells() is the only writer. It refuses to run without a backup file
  that already holds every id it is about to delete, deletes by canonical_fact
  id only (never by company or concept: the recurring delete-scope bug), and
  does not commit -- the caller's transaction decides.

It is wired into nothing. The first live run is a separate, reviewed step.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg

from scrooner_pipeline.common.periodic_forms import PERIODIC_FORMS_ALL_ORDERED

CLASS_ALL_NON_PERIODIC = "all_sources_non_periodic"  # no periodic source at all
CLASS_MIXED = "mixed_sources"  # some periodic, some not (a combined value used a proxy copy)

FIND_SQL = """
select cf.id, cf.company_id, cc.name, cf.period_id, p.start_date, p.end_date, cf.value,
       cf.source_fact_ids,
       array_agg(distinct fl.form order by fl.form) filter (where fl.form <> all(%(forms)s)) as bad_forms,
       array_agg(distinct f.id order by f.id) filter (where fl.form <> all(%(forms)s)) as bad_fact_ids,
       count(*) filter (where fl.form = any(%(forms)s)) as periodic_sources
from analytics.canonical_fact cf
join analytics.canonical_concept cc on cc.id = cf.canonical_concept_id
join core.period p on p.id = cf.period_id
cross join lateral unnest(cf.source_fact_ids) as src(fact_id)
join core.fact f on f.id = src.fact_id
join core.filing fl on fl.id = f.filing_id
where cf.company_id = any(%(company_ids)s)
group by cf.id, cf.company_id, cc.name, cf.period_id, p.start_date, p.end_date, cf.value, cf.source_fact_ids
having count(*) filter (where fl.form <> all(%(forms)s)) > 0
order by cf.company_id, cc.name, p.end_date
"""


@dataclass(frozen=True)
class SourcedCell:
    canonical_fact_id: int
    company_id: int
    concept: str
    period_id: int
    period_start: date
    period_end: date
    value: Decimal
    source_fact_ids: tuple[int, ...]
    bad_forms: tuple[str, ...]
    bad_fact_ids: tuple[int, ...]
    periodic_sources: int

    @property
    def klass(self) -> str:
        return CLASS_MIXED if self.periodic_sources else CLASS_ALL_NON_PERIODIC

    def to_json(self) -> dict:
        return {
            "canonical_fact_id": self.canonical_fact_id,
            "company_id": self.company_id,
            "concept": self.concept,
            "period_id": self.period_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "value": str(self.value),
            "source_fact_ids": list(self.source_fact_ids),
            "bad_forms": list(self.bad_forms),
            "bad_fact_ids": list(self.bad_fact_ids),
            "periodic_sources": self.periodic_sources,
            "class": self.klass,
        }


def find_non_periodic_sourced_cells(
    conn: psycopg.Connection, company_ids: Sequence[int]
) -> list[SourcedCell]:
    """Read-only. company_ids should be a chunk of at most ~100 companies
    (canonical_fact is indexed company-first; a wider scan hits the timeout)."""
    with conn.cursor() as cur:
        cur.execute(
            FIND_SQL,
            {"company_ids": list(company_ids), "forms": list(PERIODIC_FORMS_ALL_ORDERED)},
        )
        return [
            SourcedCell(
                canonical_fact_id=r[0],
                company_id=r[1],
                concept=r[2],
                period_id=r[3],
                period_start=r[4],
                period_end=r[5],
                value=r[6],
                source_fact_ids=tuple(r[7]),
                bad_forms=tuple(r[8] or ()),
                bad_fact_ids=tuple(r[9] or ()),
                periodic_sources=r[10],
            )
            for r in cur.fetchall()
        ]


def write_backup(cells: Iterable[SourcedCell], path: Path) -> int:
    """JSON lines, one per canonical_fact row about to be deleted. The full
    row (company, concept, period, value, source ids) is enough to re-insert it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as fh:
        for c in cells:
            fh.write(json.dumps(c.to_json(), sort_keys=True) + "\n")
            n += 1
    return n


def backup_ids(path: Path) -> set[int]:
    return {
        json.loads(line)["canonical_fact_id"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def purge_cells(
    conn: psycopg.Connection, cells: Sequence[SourcedCell], backup_path: Path
) -> int:
    """Delete exactly these canonical_fact rows (by id). Requires that
    backup_path already contains every id. Does not commit."""
    ids = {c.canonical_fact_id for c in cells}
    if not ids:
        return 0
    if not backup_path.exists():
        raise FileNotFoundError(f"backup file {backup_path} missing: refusing to delete")
    missing = ids - backup_ids(backup_path)
    if missing:
        raise ValueError(f"{len(missing)} ids are not in the backup file: refusing to delete")
    deleted = 0
    ordered = sorted(ids)
    with conn.cursor() as cur:
        for i in range(0, len(ordered), 5000):
            cur.execute(
                "delete from analytics.canonical_fact where id = any(%s)",
                (ordered[i : i + 5000],),
            )
            deleted += cur.rowcount
    return deleted
