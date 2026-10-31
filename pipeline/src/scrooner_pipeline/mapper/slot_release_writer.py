"""The ONE production write path for reviewed slot-record value packages
(income-statement lane, 2026-11-04; replaces the per-family writers, design
approved by scrooner-0f). The OI blank-reason writer (slot_is_not_presented)
stays separate: it writes reasons, not values.

WHAT IT DOES. Each registered package (SPECS) is one cells file under
pipeline/scripts/slot_records/results/<package>/. An adapter turns that
package's own cell format into one common Cell; every cell is one of
    update   production's value is replaced (old row archived, 'replaced')
    insert   a row is added where none existed (logged 'inserted')
    hide     production's confirmed-wrong value is archived and removed and a
             guard_hidden blank reason is written
for one (company, canonical concept, period) key. Every written key also gets
an analytics.slot_protected_cell row (migration 0113; value NULL for a hide,
migration 0115) so no nightly resolver overwrites it, and one append-only
analytics.cell_evidence row (accession, locator with the package digest).
New and replaced rows carry the core.fact ids of the filing's own facts for
the slot's tag(s) when every tag resolves to exactly one fact in that filing
and period; otherwise source_fact_ids is empty and the evidence row is the
lineage (counted as lineage_evidence_only).

SAFETY CONTRACT (each guard has a test in tests/unit/test_slot_release_writer.py):
  * dry-run is the default and is read-only;
  * apply refuses unless the package's rule flag is ON, --confirm equals the
    package's token, and the cells file's sha256 equals BOTH PACKAGE.json and
    the reviewed --digest, all checked BEFORE any DB access;
  * apply refuses without migration 0113, and without 0115 when it hides;
  * STALE REFUSAL over the whole run before the first write: an unknown CIK, a
    missing or ambiguous period, an update/hide whose live value (or row id)
    is not the package's production value, an insert whose key now has a row,
    a key protected by another rule or at another value, or a duplicate key;
    a key already at the slot value and protected by this rule is skipped
    (resume after a failed batch);
  * one transaction per company under set local scrooner.slot_writer = 'on';
    a failure rolls back that company and stops; restore(run_id) undoes the
    committed ones;
  * restore(run_id) = canonical_archive.restore_run + delete of that run's
    protections and blank reasons, one transaction, recorded as a rollback
    rule_run. Evidence rows are append-only and stay (they name the run).

`export` writes the before-image and rollback SQL from the same plan the
writer applies, so they cannot drift from what it writes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.common.rule_flags import rule_enabled, rule_mode
from scrooner_pipeline.mapper import canonical_archive as ca

RESULTS_DIR = (
    Path(__file__).resolve().parents[3] / "scripts" / "slot_records" / "results"
)
RECORDED_BY = "slot_release_writer"
OPS = ("update", "insert", "hide")


class ReleaseRefused(RuntimeError):
    """A guard stopped the run; nothing (more) was written."""


# ------------------------------------------------------------------ model
@dataclass(frozen=True)
class Cell:
    cik: str
    start: date | None  # None for an instant
    end: date
    op: str
    new_value: Decimal | None  # None for a hide
    expected_before: Decimal | None  # None for an insert
    accession: str
    expected_cf_id: int | None = None
    source_tags: tuple[str, ...] = ()
    detail: str = ""  # gate / reading, carried into the evidence locator

    def __post_init__(self) -> None:
        if self.op not in OPS:
            raise ValueError(f"unknown op {self.op!r}")
        if (self.op == "hide") != (self.new_value is None):
            raise ValueError(
                f"{self.cik} {self.end}: new_value is required unless op is hide"
            )
        if (self.op == "insert") != (self.expected_before is None):
            raise ValueError(
                f"{self.cik} {self.end}: expected_before is required unless op is insert"
            )


@dataclass(frozen=True)
class Spec:
    name: str
    rule_id: str
    package: str  # directory under RESULTS_DIR
    concept: str
    data_point: str
    confirm: str
    instant: bool
    cells_file: Callable[[dict], str]  # PACKAGE.json -> cells file name
    package_sha: Callable[[dict], str]  # PACKAGE.json -> recorded sha256
    adapt: Callable[[dict], Cell | None]  # None = row is not part of the release
    hide_reason: str = ""
    hide_owner: str = ""
    hide_root_cause: str | None = None


@dataclass(frozen=True)
class Package:
    spec: Spec
    cells: tuple[Cell, ...]
    digest: str


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _d(v: Any) -> Decimal | None:
    return None if v is None or v == "" else Decimal(str(v))


def _cik(v: Any) -> str:
    return str(v).zfill(10)


def _date(v: Any) -> date | None:
    return date.fromisoformat(v) if v else None


# ------------------------------------------------------------------ adapters
IS_OPS = {"slot_differs": "update", "slot_fills_blank": "insert"}


def adapt_is(d: dict) -> Cell | None:
    """Income-statement packages (is_package.py): compare slot_differs /
    slot_fills_blank, slot_value vs prod_value, prod_cf_id, slot_tag or the
    summed members of a G3 total."""
    op = IS_OPS.get(d.get("compare", ""))
    if op is None:
        raise ReleaseRefused(
            f"IS cell with compare {d.get('compare')!r} is not a release cell"
        )
    tags = tuple(sorted(d["members"])) if d.get("members") else (d["slot_tag"],)
    return Cell(
        cik=_cik(d["cik"]),
        start=_date(d["start"]),
        end=date.fromisoformat(d["end"]),
        op=op,
        new_value=_d(d["slot_value"]),
        expected_before=_d(d["prod_value"]) if op == "update" else None,
        accession=d["accession"],
        expected_cf_id=d.get("prod_cf_id") if op == "update" else None,
        source_tags=tags,
        detail=f"gate={d.get('gate')}",
    )


BS_OPS = {
    "slot_differs": "update",
    "slot_fills_blank": "insert",
    "slot_holds_prod_has_value": "hide",
}


def adapt_bs_total_liabilities(d: dict) -> Cell | None:
    """bs_release_release1_cells.jsonl: state, slot vs production, instant."""
    if d.get("release") != "1":
        raise ReleaseRefused(f"cell outside release 1: {d.get('cik')} {d.get('end')}")
    op = BS_OPS.get(d["state"])
    if op is None:
        raise ReleaseRefused(f"BS cell with state {d['state']!r} is not a release cell")
    return Cell(
        cik=_cik(d["cik"]),
        start=None,
        end=date.fromisoformat(d["end"]),
        op=op,
        new_value=None if op == "hide" else _d(d["slot"]),
        expected_before=None if op == "insert" else _d(d["production"]),
        accession=d["accession"],
        detail=f"reading={d.get('reading')} rule={d.get('rule')} identity={d.get('identity')}",
    )


def _is_spec(
    name: str, rule_id: str, package: str, concept: str, data_point: str, confirm: str
) -> Spec:
    return Spec(
        name=name,
        rule_id=rule_id,
        package=package,
        concept=concept,
        data_point=data_point,
        confirm=confirm,
        instant=False,
        cells_file=lambda m: m["release1"]["file"],
        package_sha=lambda m: m["release1"]["sha256"],
        adapt=adapt_is,
    )


SPECS: dict[str, Spec] = {
    s.name: s
    for s in (
        _is_spec(
            "is_net_income_1",
            "slot.is_net_income@1",
            "release_is_net_income_1",
            "net_income_resolved",
            "net_income",
            "RELEASE-IS-NI-1",
        ),
        _is_spec(
            "is_operating_income_1",
            "slot.is_operating_income@1",
            "release_is_operating_income_1",
            "operating_income_resolved",
            "operating_income",
            "RELEASE-IS-OI-1",
        ),
        _is_spec(
            "is_revenue_1",
            "slot.is_revenue@1",
            "release_is_revenue_1",
            "revenue_sanity_resolved",
            "revenue",
            "RELEASE-IS-REV-1",
        ),
        _is_spec(
            "is_revenue_2",
            "slot.is_revenue_tagged_total_sum@1",
            "release_is_revenue_2",
            "revenue_sanity_resolved",
            "revenue",
            "RELEASE-IS-REV-2",
        ),
        _is_spec(
            "is_utilities_net_income_1",
            "slot.is_net_income@1",
            "release_is_utilities_addon_1/net_income",
            "net_income_resolved",
            "net_income",
            "RELEASE-IS-UTIL-NI-1",
        ),
        _is_spec(
            "is_utilities_revenue_1",
            "slot.is_revenue@1",
            "release_is_utilities_addon_1/revenue",
            "revenue_sanity_resolved",
            "revenue",
            "RELEASE-IS-UTIL-REV-1",
        ),
        Spec(
            name="bs_total_liabilities_1",
            rule_id="slot.bs_total_liabilities@1",
            package="release_bs_total_liabilities_1",
            concept="total_liabilities_resolved",
            data_point="total_liabilities",
            confirm="RELEASE-BS-TL-1",
            instant=True,
            cells_file=lambda m: m["release1"]["cells_file"],
            package_sha=lambda m: m["release1"]["sha256"],
            adapt=adapt_bs_total_liabilities,
            hide_reason="slot_bs_total_liabilities_r1_hide",
            hide_owner="data_engineer_l1",
            hide_root_cause="composition",
        ),
    )
}


def get_spec(name: str) -> Spec:
    if name not in SPECS:
        raise ReleaseRefused(f"unknown package {name!r}; registered: {sorted(SPECS)}")
    return SPECS[name]


def load_package(
    spec: Spec, reviewed_digest: str | None, *, root: Path = RESULTS_DIR
) -> Package:
    """File-only checks; nothing here touches the database."""
    pdir = root / spec.package
    meta = json.loads((pdir / "PACKAGE.json").read_text())
    if meta.get("rule_id") != spec.rule_id:
        raise ReleaseRefused(
            f"{spec.package}/PACKAGE.json is for {meta.get('rule_id')}, not {spec.rule_id}"
        )
    path = pdir / spec.cells_file(meta)
    actual = file_sha256(path)
    if actual != spec.package_sha(meta):
        raise ReleaseRefused(
            f"cells file sha256 {actual} != PACKAGE.json {spec.package_sha(meta)}"
        )
    if (reviewed_digest or "").strip().lower() != actual:
        raise ReleaseRefused(
            f"cells file sha256 {actual} != reviewed --digest {reviewed_digest!r}"
        )
    cells: list[Cell] = []
    for line in path.read_text().splitlines():
        if line.strip():
            c = spec.adapt(json.loads(line))
            if c is not None:
                cells.append(c)
    if spec.instant != all(c.start is None for c in cells):
        raise ReleaseRefused(
            f"{spec.name}: period shape does not match the spec (instant={spec.instant})"
        )
    if any(c.op == "hide" for c in cells) and not spec.hide_reason:
        raise ReleaseRefused(f"{spec.name}: hide cells but no hide reason registered")
    keys = [(c.cik, c.start, c.end) for c in cells]
    if len(set(keys)) != len(keys):
        dup = [k for k, n in Counter(keys).items() if n > 1]
        raise ReleaseRefused(f"duplicate cell keys in the package: {dup[:5]}")
    return Package(spec, tuple(cells), actual)


# ------------------------------------------------------------------ plan
@dataclass(frozen=True)
class Planned:
    cell: Cell
    company_id: int
    period_id: int
    live_cf_id: int | None
    source_fact_ids: tuple[int, ...] = ()
    already_applied: bool = False


@dataclass
class Plan:
    concept_id: int
    cells: list[Planned]
    summary: dict[str, Any] = field(default_factory=dict)


def grain(c: Cell) -> str:
    if c.start is None:
        return "I"
    months = round(((c.end - c.start).days + 1) / 30.4)
    return {3: "Q", 12: "FY"}.get(months, "TP")


def plan(cur, pkg: Package) -> Plan:
    """Read-only: resolve ids, run the stale refusal (raises on any drift),
    resolve lineage. Set-based: a handful of statements for the whole run."""
    spec, cells = pkg.spec, pkg.cells
    cur.execute(
        "select id from analytics.canonical_concept where name = %s", (spec.concept,)
    )
    row = cur.fetchone()
    if row is None:
        raise ReleaseRefused(f"no canonical concept {spec.concept}")
    concept_id = row[0]
    ciks = sorted({c.cik for c in cells})
    cur.execute("select cik, id from core.company where cik = any(%s)", (ciks,))
    company = dict(cur.fetchall())
    unknown = [k for k in ciks if k not in company]
    if unknown:
        raise ReleaseRefused(f"STALE: unknown CIKs {unknown[:5]}")
    cur.execute(
        """
        select u.i, count(p.id), min(p.id)
        from unnest(%(co)s::bigint[], %(s)s::date[], %(e)s::date[]) with ordinality as u(co, s, e, i)
        left join core.period p
          on p.company_id = u.co and p.end_date = u.e
         and p.period_type = %(pt)s
         and (%(pt)s = 'instant' or p.start_date = u.s)
        group by u.i
        """,
        {
            "co": [company[c.cik] for c in cells],
            "s": [c.start or c.end for c in cells],
            "e": [c.end for c in cells],
            "pt": "instant" if spec.instant else "duration",
        },
    )
    period: dict[int, int] = {}
    stale: list[str] = []
    for i, n, pid in cur.fetchall():
        c = cells[i - 1]
        if n != 1:
            stale.append(f"{c.cik} {c.start}..{c.end}: {n} matching periods (need 1)")
        else:
            period[i - 1] = pid
    if stale:
        raise ReleaseRefused(
            f"STALE: {len(stale)} cells; re-cut the package. First: {stale[:5]}"
        )
    pids = [period[i] for i in range(len(cells))]
    cos = [company[c.cik] for c in cells]
    cur.execute(
        """
        select u.co, u.p, cf.id, cf.value, sp.rule_id, sp.value, sp.company_id is not null
        from unnest(%(co)s::bigint[], %(p)s::bigint[]) as u(co, p)
        left join analytics.canonical_fact cf
          on cf.company_id = u.co and cf.canonical_concept_id = %(k)s and cf.period_id = u.p
        left join analytics.slot_protected_cell sp
          on sp.company_id = u.co and sp.canonical_concept_id = %(k)s and sp.period_id = u.p
        """,
        {"co": cos, "p": pids, "k": concept_id},
    )
    live = {(r[0], r[1]): r[2:] for r in cur.fetchall()}
    sources = _lineage(cur, cells, cos, pids)
    planned: list[Planned] = []
    for i, c in enumerate(cells):
        cf_id, value, prot_rule, prot_value, protected = live[(cos[i], pids[i])]
        value = None if value is None else Decimal(value)
        tag = f"{c.cik} {c.start}..{c.end} ({c.op})"
        target = c.new_value  # None for a hide: the protected value is NULL too
        done = (
            protected
            and prot_rule == spec.rule_id
            and (None if prot_value is None else Decimal(prot_value)) == target
            and value == target
        )
        if done:
            planned.append(Planned(c, cos[i], pids[i], cf_id, sources.get(i, ()), True))
            continue
        if protected:
            stale.append(f"{tag}: key already protected by {prot_rule} at {prot_value}")
        elif c.op == "insert" and cf_id is not None:
            stale.append(f"{tag}: blank in the package but production now has {value}")
        elif c.op != "insert" and cf_id is None:
            stale.append(f"{tag}: production row gone")
        elif c.op != "insert" and value != c.expected_before:
            stale.append(
                f"{tag}: production is {value}, package expected {c.expected_before}"
            )
        elif c.expected_cf_id is not None and cf_id != c.expected_cf_id:
            stale.append(
                f"{tag}: production row id {cf_id}, package expected {c.expected_cf_id}"
            )
        planned.append(Planned(c, cos[i], pids[i], cf_id, sources.get(i, ())))
    if stale:
        raise ReleaseRefused(
            f"STALE: {len(stale)} cells drifted since the package was cut; re-cut it. First: {stale[:5]}"
        )
    todo = [p for p in planned if not p.already_applied]
    summary = {
        "package": spec.name,
        "rule_id": spec.rule_id,
        "concept": spec.concept,
        "digest": pkg.digest,
        "cells": len(planned),
        "companies": len(ciks),
        "already_applied": len(planned) - len(todo),
        **{op: sum(1 for p in todo if p.cell.op == op) for op in OPS},
        "lineage_fact_ids": sum(
            1 for p in todo if p.cell.op != "hide" and p.source_fact_ids
        ),
        "lineage_evidence_only": sum(
            1 for p in todo if p.cell.op != "hide" and not p.source_fact_ids
        ),
    }
    return Plan(concept_id, planned, summary)


def _lineage(
    cur, cells: tuple[Cell, ...], cos: list[int], pids: list[int]
) -> dict[int, tuple[int, ...]]:
    """Cell index -> the core.fact ids of the filing's own facts for every
    slot tag, when each tag has exactly one fact in that filing and period."""
    idx, tags = [], []
    for i, c in enumerate(cells):
        for t in c.source_tags:
            idx.append(i)
            tags.append(t)
    if not idx:
        return {}
    cur.execute(
        """
        select u.i, u.t, array_agg(f.id order by f.id)
        from unnest(%(i)s::int[], %(t)s::text[], %(co)s::bigint[], %(p)s::bigint[], %(a)s::text[])
             as u(i, t, co, p, a)
        join core.concept k on k.tag = u.t
        join core.filing fi on fi.accession_number = u.a
        join core.fact f on f.company_id = u.co and f.concept_id = k.id
                        and f.period_id = u.p and f.filing_id = fi.id
        group by u.i, u.t
        """,
        {
            "i": idx,
            "t": tags,
            "co": [cos[i] for i in idx],
            "p": [pids[i] for i in idx],
            "a": [cells[i].accession for i in idx],
        },
    )
    found: dict[int, dict[str, list[int]]] = defaultdict(dict)
    for i, t, ids in cur.fetchall():
        found[i][t] = ids
    out = {}
    for i, by_tag in found.items():
        need = cells[i].source_tags
        if all(len(by_tag.get(t, [])) == 1 for t in need):
            out[i] = tuple(sorted(by_tag[t][0] for t in need))
    return out


# ------------------------------------------------------------------ apply
def _table_present(cur) -> bool:
    cur.execute("select to_regclass('analytics.slot_protected_cell') is not null")
    return bool(cur.fetchone()[0])


def _blank_protection_allowed(cur) -> bool:
    cur.execute(
        "select is_nullable = 'YES' from information_schema.columns "
        "where table_schema = 'analytics' and table_name = 'slot_protected_cell' and column_name = 'value'"
    )
    row = cur.fetchone()
    return bool(row and row[0])


_INSERT_EVIDENCE = """
insert into analytics.cell_evidence
    (company_id, data_point_name, period_grain, period_start, period_end, basis,
     state_claimed, rule_id, evidence_kind, accession, locator, source_hash,
     evidence_level, recorded_by)
values (%s, %s, %s, %s, %s, 'latest', %s, %s, 'detector_audit', %s, %s, %s, 'DATA-INFERRED', %s)
"""


def _key(spec: Spec, p: Planned) -> CellKey:
    c = p.cell
    return CellKey(p.company_id, spec.data_point, grain(c), c.start or c.end, c.end)


def apply_company(
    conn, run_id: str, pkg: Package, concept_id: int, batch: list[Planned]
) -> dict[str, int]:
    """One company in ONE transaction: archive + canonical_fact change +
    protection + evidence + hide reasons commit together or not at all."""
    spec = pkg.spec
    try:
        with conn.cursor() as cur:
            cur.execute("set local scrooner.slot_writer = 'on'")
            rows = [
                ca.CanonicalRow(
                    p.company_id,
                    concept_id,
                    p.period_id,
                    p.cell.new_value,
                    p.source_fact_ids,
                )
                for p in batch
                if p.cell.op != "hide"
            ]
            stats = ca.replace_rows(
                cur, rows, reason_code=f"{spec.name}_value", run_id=run_id
            )
            want = {
                "replaced": sum(1 for p in batch if p.cell.op == "update"),
                "inserted": sum(1 for p in batch if p.cell.op == "insert"),
            }
            if (
                stats["replaced"] != want["replaced"]
                or stats["inserted"] != want["inserted"]
            ):
                raise ReleaseRefused(
                    f"{batch[0].cell.cik}: wrote {stats}, planned {want}: production moved mid-run"
                )
            hide_ids = [p.live_cf_id for p in batch if p.cell.op == "hide"]
            removed = ca.archive_and_remove(
                cur, hide_ids, reason_code=spec.hide_reason or "hide", run_id=run_id
            )
            if removed != len(hide_ids):
                raise ReleaseRefused(
                    f"{batch[0].cell.cik}: removed {removed} of {len(hide_ids)} rows mid-run"
                )
            cur.executemany(
                """
                insert into analytics.slot_protected_cell
                    (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256)
                values (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        p.company_id,
                        concept_id,
                        p.period_id,
                        spec.rule_id,
                        p.cell.new_value,
                        run_id,
                        pkg.digest,
                    )
                    for p in batch
                ],
            )
            cur.executemany(
                _INSERT_EVIDENCE,
                [
                    (
                        p.company_id,
                        spec.data_point,
                        grain(p.cell),
                        p.cell.start or p.cell.end,
                        p.cell.end,
                        "defect" if p.cell.op == "hide" else "value",
                        spec.rule_id,
                        p.cell.accession,
                        f"package={spec.package} op={p.cell.op} run={run_id} {p.cell.detail}".strip(),
                        pkg.digest,
                        RECORDED_BY,
                    )
                    for p in batch
                ],
            )
            reasons = [
                cs.guard_hidden(
                    _key(spec, p),
                    spec.rule_id,
                    spec.hide_reason,
                    spec.hide_owner,
                    root_cause_class=spec.hide_root_cause,
                    reason_text="slot record does not tie; production value confirmed wrong by the Verifier",
                    input_refs={
                        "accession": p.cell.accession,
                        "package_digest": pkg.digest,
                    },
                )
                for p in batch
                if p.cell.op == "hide"
            ]
            n_reasons = cs.write_blank_reasons(conn, run_id, reasons) if reasons else 0
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return {
        **want,
        "removed": removed,
        "protected": len(batch),
        "evidence": len(batch),
        "reasons": n_reasons,
    }


def apply(
    conn,
    pkg: Package,
    *,
    confirm: str,
    environ: Mapping[str, str] | None = None,
    git_commit: str | None = None,
) -> dict[str, Any]:
    """Flag and token first (no DB access before they pass), then plan, then
    one transaction per company."""
    spec = pkg.spec
    if not rule_enabled(spec.rule_id, environ):
        raise ReleaseRefused(
            f"{spec.rule_id} is not ON (mode {rule_mode(spec.rule_id, environ)})"
        )
    if confirm != spec.confirm:
        raise ReleaseRefused(f"--confirm must equal {spec.confirm}")
    with conn.cursor() as cur:
        if not _table_present(cur):
            raise ReleaseRefused(
                "migration 0113 (analytics.slot_protected_cell) is not applied"
            )
        if any(c.op == "hide" for c in pkg.cells) and not _blank_protection_allowed(
            cur
        ):
            raise ReleaseRefused("migration 0115 (protected blanks) is not applied")
        pl = plan(cur, pkg)
    conn.rollback()
    by_cik: dict[str, list[Planned]] = defaultdict(list)
    for p in pl.cells:
        if not p.already_applied:
            by_cik[p.cell.cik].append(p)
    ciks = sorted(by_cik)
    run_id = cs.start_rule_run(
        conn,
        spec.rule_id,
        "apply",
        "on",
        ciks,
        train=f"slot-release-{spec.name}",
        git_commit=git_commit,
        before_image_ref=f"analytics.canonical_fact_retired by run_id; package {spec.name} sha256 {pkg.digest}",
    )
    conn.commit()
    totals: Counter[str] = Counter()
    for k in ciks:
        totals.update(apply_company(conn, run_id, pkg, pl.concept_id, by_cik[k]))
    result = {
        "run_id": run_id,
        "companies_committed": len(ciks),
        "plan": pl.summary,
        **totals,
    }
    cs.finish_rule_run(conn, run_id, result)
    conn.commit()
    return {**result, "touched_ciks": ciks}


def restore(
    conn, run_id: str, spec: Spec, *, confirm: str, git_commit: str | None = None
) -> dict[str, Any]:
    """Undo one apply run exactly, in one transaction."""
    if confirm != spec.confirm:
        raise ReleaseRefused(f"--confirm must equal {spec.confirm}")
    try:
        with conn.cursor() as cur:
            cur.execute(
                "select rule_id, mode, ciks, train from analytics.rule_run where run_id = %s::uuid",
                (run_id,),
            )
            row = cur.fetchone()
            if (
                row is None
                or row[0] != spec.rule_id
                or row[1] != "apply"
                or row[3] != f"slot-release-{spec.name}"
            ):
                raise ReleaseRefused(
                    f"run {run_id} is not an apply run of package {spec.name}"
                )
            cur.execute("set local scrooner.slot_writer = 'on'")
            restored = ca.restore_run(cur, run_id)
            cur.execute(
                "delete from analytics.slot_protected_cell where run_id = %s", (run_id,)
            )
            unprotected = cur.rowcount
            reasons = cs.delete_run_blank_reasons(conn, run_id)
        rb = cs.start_rule_run(
            conn,
            spec.rule_id,
            "rollback",
            "on",
            row[2] or [],
            train=f"slot-release-{spec.name}",
            git_commit=git_commit,
            before_image_ref=f"restores run {run_id}",
        )
        out = {
            "rollback_run_id": rb,
            "restores": run_id,
            "restored_rows": restored,
            "protection_removed": unprotected,
            "reasons_deleted": reasons,
        }
        cs.finish_rule_run(conn, rb, out)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return out


# ------------------------------------------------------------------ export
def before_image(cur, pl: Plan) -> list[dict[str, Any]]:
    """The live canonical_fact rows the plan replaces or removes."""
    ids = [
        p.live_cf_id
        for p in pl.cells
        if p.live_cf_id is not None and not p.already_applied
    ]
    cur.execute(
        "select id, company_id, canonical_concept_id, period_id, value, source_fact_ids, resolved_at "
        "from analytics.canonical_fact where id = any(%s) order by id",
        (ids,),
    )
    return [
        {
            "canonical_fact_id": r[0],
            "company_id": r[1],
            "canonical_concept_id": r[2],
            "period_id": r[3],
            "value": str(r[4]),
            "source_fact_ids": list(r[5] or []),
            "resolved_at": r[6].isoformat(),
        }
        for r in cur.fetchall()
    ]


def rollback_sql(pkg: Package, pl: Plan, image: list[dict[str, Any]]) -> str:
    """Manual rollback for the Release Manager, keyed by this package's digest:
    remove what the package wrote at its keys, put the before-image back.
    restore(run_id) is the primary undo; this is the file-only fallback."""
    keys = sorted({(p.company_id, p.period_id) for p in pl.cells})
    lines = [
        f"-- rollback for package {pkg.spec.name} ({pkg.spec.rule_id}), cells sha256 {pkg.digest}",
        "begin;",
        "set local scrooner.slot_writer = 'on';",
        (
            "delete from analytics.canonical_fact where canonical_concept_id = "
            f"{pl.concept_id} and (company_id, period_id) in ("
        ),
        ",\n".join(f"  ({c}, {p})" for c, p in keys) + ");",
    ]
    for b in image:
        lines.append(
            "insert into analytics.canonical_fact (company_id, canonical_concept_id, period_id, value, source_fact_ids, resolved_at) "
            f"values ({b['company_id']}, {b['canonical_concept_id']}, {b['period_id']}, {b['value']}, "
            f"'{{{','.join(map(str, b['source_fact_ids']))}}}'::bigint[], '{b['resolved_at']}');"
        )
    lines += [
        f"delete from analytics.slot_protected_cell where package_sha256 = '{pkg.digest}' and rule_id = '{pkg.spec.rule_id}';",
        "commit;",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ CLI
def _git_commit() -> str | None:
    import subprocess

    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main(
    argv: list[str] | None = None, environ: Mapping[str, str] | None = None
) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("dry-run", "apply", "export"):
        sp = sub.add_parser(name)
        sp.add_argument("package", choices=sorted(SPECS))
        sp.add_argument(
            "--digest",
            required=True,
            help="reviewed sha256 of the package's cells file",
        )
    sub.choices["apply"].add_argument("--confirm", default="")
    sub.choices["export"].add_argument("--out-dir", type=Path, required=True)
    sp = sub.add_parser("restore")
    sp.add_argument("package", choices=sorted(SPECS))
    sp.add_argument("--run-id", required=True)
    sp.add_argument("--confirm", default="")
    sp = sub.add_parser("digest")
    sp.add_argument("package", choices=sorted(SPECS))
    args = ap.parse_args(argv)
    spec = get_spec(args.package)

    from scrooner_pipeline.db.connection import get_connection

    try:
        if args.cmd == "digest":
            meta = json.loads((RESULTS_DIR / spec.package / "PACKAGE.json").read_text())
            print(file_sha256(RESULTS_DIR / spec.package / spec.cells_file(meta)))
            return 0
        if args.cmd == "restore":
            with get_connection() as conn:
                print(
                    json.dumps(
                        restore(
                            conn,
                            args.run_id,
                            spec,
                            confirm=args.confirm,
                            git_commit=_git_commit(),
                        ),
                        indent=1,
                    )
                )
            return 0
        pkg = load_package(spec, args.digest)  # before any DB access
        if args.cmd in ("dry-run", "export"):
            with get_connection() as conn:
                conn.read_only = True
                with conn.cursor() as cur:
                    cur.execute("set statement_timeout = '120s'")
                    guard = _table_present(cur)
                    blanks = guard and _blank_protection_allowed(cur)
                    pl = plan(cur, pkg)
                    image = before_image(cur, pl) if args.cmd == "export" else []
            if args.cmd == "export":
                args.out_dir.mkdir(parents=True, exist_ok=True)
                bi = args.out_dir / f"{spec.name}_before_image.jsonl"
                bi.write_text(
                    "".join(json.dumps(b, sort_keys=True) + "\n" for b in image)
                )
                rb = args.out_dir / f"{spec.name}_rollback.sql"
                rb.write_text(rollback_sql(pkg, pl, image))
                print(
                    json.dumps(
                        {
                            **pl.summary,
                            "before_image_rows": len(image),
                            "before_image_sha256": file_sha256(bi),
                            "rollback_sha256": file_sha256(rb),
                        },
                        indent=1,
                    )
                )
                return 0
            print(
                f"package {spec.name} rule {spec.rule_id} mode={rule_mode(spec.rule_id, environ)} DRY RUN, nothing written"
            )
            print(
                f"  guard table (0113): {'present' if guard else 'ABSENT: apply will refuse'}"
            )
            print(f"  protected blanks (0115): {'yes' if blanks else 'no'}")
            for k, v in pl.summary.items():
                print(f"  {k}: {v}")
            return 0
        with get_connection() as conn:
            res = apply(
                conn,
                pkg,
                confirm=args.confirm,
                environ=environ,
                git_commit=_git_commit(),
            )
        print(
            json.dumps(
                {k: v for k, v in res.items() if k != "touched_ciks"},
                indent=1,
                default=str,
            )
        )
        print("touched ciks (certify rerun):", len(res["touched_ciks"]))
        return 0
    except ReleaseRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
