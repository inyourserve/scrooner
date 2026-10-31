"""Production write path for blank-reason package 2 of rule
slot.is_operating_income_not_presented@1 (income-statement lane, 2026-10-31;
same contract as mapper/slot_bs_total_liabilities.py on the BS release branch).

WHAT IT DOES. Applies the reviewed package
(pipeline/scripts/slot_records/results/release_is_operating_income_2/) for
data point operating_income / concept operating_income_resolved:
    prod_blank_reason_only        a cell_blank_reason row (state not_presented,
                                  reason line_not_presented_in_filing, the filing's
                                  accession in input_refs); production stays blank
    prod_has_value_would_hide     the same reason row, AND production's derived
    q4_prod_has_value_would_hide  value is archived to canonical_fact_retired and
                                  removed (canonical_archive.archive_and_remove)
Every written key also gets an analytics.slot_protected_cell row with value
NULL (a protected blank, migration 0113) so no nightly resolver re-derives it.

SAFETY CONTRACT (each guard has a test in tests/unit/test_slot_is_not_presented*.py):
  * dry-run is the default; it opens a read-only session and writes nothing;
  * apply refuses unless rule_flags says the rule is ON, --confirm equals
    CONFIRM_TOKEN, and the package digest (sha256 over the three stratum
    digests) equals the reviewed --digest; every stratum file's own sha256 must
    match PACKAGE.json. All of this is checked BEFORE any DB access;
  * apply refuses when migration 0113 (slot_protected_cell) is absent (without
    it the next nightly would re-derive the removed values) or 0115 (value
    nullable, a protected blank) is not applied;
  * STALE REFUSAL before the first write: an unknown CIK, a would-hide row whose
    canonical_fact id, value or sources differ from the before-image, or a
    reason-only cell that now has a production row refuses the WHOLE run;
  * one transaction per batch of companies (reasons + archive/remove +
    protection commit together or not at all), under
    set local scrooner.slot_writer = 'on'; a failure rolls back the batch and
    stops; earlier batches stay and restore(run_id) undoes them;
  * restore(run_id) = canonical_archive.restore_run + delete of that run's
    blank reasons + its protection rows, one transaction, recorded as a
    rule_run in mode 'rollback'.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from scrooner_pipeline.common import cell_store as cs
from scrooner_pipeline.common.cell_contract import CellKey
from scrooner_pipeline.common.rule_flags import rule_enabled, rule_mode
from scrooner_pipeline.mapper import canonical_archive as ca

RULE_ID = "slot.is_operating_income_not_presented@1"
CONCEPT_NAME = "operating_income_resolved"
DATA_POINT = "operating_income"
REASON_CODE = "line_not_presented_in_filing"
CONFIRM_TOKEN = "RELEASE-IS-OI-NOT-PRESENTED-2"
TRAIN = "slot-is-operating-income-not-presented-package-2"
DEFAULT_BATCH_COMPANIES = 25
PACKAGE_DIR = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "slot_records"
    / "results"
    / "release_is_operating_income_2"
)
REASON_ONLY = "prod_blank_reason_only"
HIDE_STRATA = ("prod_has_value_would_hide", "q4_prod_has_value_would_hide")


class ReleaseRefused(RuntimeError):
    pass


@dataclass(frozen=True)
class Cell:
    cik: str
    stratum: str
    period_grain: str
    period_start: date
    period_end: date
    reason_text: str
    input_refs: dict
    prod_cf_id: int | None
    prod_value: Decimal | None


@dataclass(frozen=True)
class Package:
    cells: tuple[Cell, ...]
    before: dict  # canonical_fact_id -> before-image row
    digest: str


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_digest(pkg_json: dict) -> str:
    """sha256 over the stratum digests in a fixed order: the one number a
    reviewer signs for the whole package."""
    parts = [
        f"{k}:{pkg_json['strata'][k]['sha256']}" for k in sorted(pkg_json["strata"])
    ]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def load_package(pkg_dir: Path, reviewed_digest: str) -> Package:
    """Every check here is file-only: nothing touches the database."""
    meta = json.loads((pkg_dir / "PACKAGE.json").read_text())
    if meta.get("rule_id") != RULE_ID or meta.get("kind") != "blank_reasons":
        raise ReleaseRefused(f"PACKAGE.json is not a {RULE_ID} blank-reason package")
    digest = package_digest(meta)
    if digest != reviewed_digest:
        raise ReleaseRefused(
            f"package digest {digest} != reviewed --digest {reviewed_digest}"
        )
    cells = []
    for st, m in meta["strata"].items():
        path = pkg_dir / m["file"]
        if file_sha256(path) != m["sha256"]:
            raise ReleaseRefused(f"{m['file']} sha256 does not match PACKAGE.json")
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if (
                r["rule_id"] != RULE_ID
                or r["reason_code"] != REASON_CODE
                or r["state"] != "not_presented"
            ):
                raise ReleaseRefused(
                    f"cell outside the package rule: {r['cik']} {r['period_end']}"
                )
            if (st in HIDE_STRATA) != (r.get("prod_cf_id") is not None):
                raise ReleaseRefused(
                    f"stratum/prod_cf_id mismatch: {r['cik']} {r['period_end']}"
                )
            cells.append(
                Cell(
                    r["cik"],
                    st,
                    r["period_grain"],
                    date.fromisoformat(r["period_start"]),
                    date.fromisoformat(r["period_end"]),
                    r["reason_text"],
                    r["input_refs"],
                    r.get("prod_cf_id"),
                    Decimal(r["prod_value"]) if r.get("prod_value") else None,
                )
            )
    bi = pkg_dir / meta["before_image"]["file"]
    if file_sha256(bi) != meta["before_image"]["sha256"]:
        raise ReleaseRefused("before-image sha256 does not match PACKAGE.json")
    before = {
        b["canonical_fact_id"]: b for b in map(json.loads, bi.read_text().splitlines())
    }
    if len(before) != sum(1 for c in cells if c.stratum in HIDE_STRATA):
        raise ReleaseRefused("before-image rows != would-hide cells")
    return Package(tuple(cells), before, digest)


@dataclass(frozen=True)
class PlannedCell:
    cell: Cell
    company_id: int
    period_id: int | None
    action: str  # reason | hide


def plan(cur, pkg: Package) -> tuple[list[PlannedCell], dict[str, Any]]:
    """Read-only. Resolves ids and runs the stale refusal; raises on any drift."""
    cur.execute(
        "select id from analytics.canonical_concept where name = %s", (CONCEPT_NAME,)
    )
    row = cur.fetchone()
    if row is None:
        raise ReleaseRefused(f"no canonical concept {CONCEPT_NAME}")
    concept_id = row[0]
    ciks = sorted({c.cik for c in pkg.cells})
    cur.execute("select cik, id from core.company where cik = any(%s)", (ciks,))
    company = dict(cur.fetchall())
    unknown = [k for k in ciks if k not in company]
    if unknown:
        raise ReleaseRefused(f"unknown CIKs: {unknown[:5]}")
    ids = sorted(pkg.before)
    cur.execute(
        "select id, value, source_fact_ids, period_id from analytics.canonical_fact where id = any(%s)",
        (ids,),
    )
    live = {r[0]: r for r in cur.fetchall()}
    stale = []
    for fid, b in pkg.before.items():
        lv = live.get(fid)
        if lv is None:
            stale.append(f"{b['cik']} {b['end']}: production row {fid} gone")
        elif Decimal(lv[1]) != Decimal(b["value_before"]) or list(lv[2] or []) != list(
            b["source_fact_ids_before"] or []
        ):
            stale.append(
                f"{b['cik']} {b['end']}: production row {fid} changed since the before-image"
            )
    cur.execute(
        """
        select u.cik, u.s, u.e, p.id,
               exists (select 1 from analytics.canonical_fact cf
                       where cf.company_id = co.id and cf.canonical_concept_id = %s and cf.period_id = p.id)
        from unnest(%s::text[], %s::date[], %s::date[]) as u(cik, s, e)
        join core.company co on co.cik = u.cik
        left join core.period p on p.company_id = co.id and p.period_type = 'duration'
                               and p.start_date = u.s and p.end_date = u.e
        """,
        (
            concept_id,
            [c.cik for c in pkg.cells],
            [c.period_start for c in pkg.cells],
            [c.period_end for c in pkg.cells],
        ),
    )
    periods = {(r[0], r[1], r[2]): (r[3], r[4]) for r in cur.fetchall()}
    planned = []
    for c in pkg.cells:
        pid, has_row = periods.get((c.cik, c.period_start, c.period_end), (None, False))
        if c.stratum == REASON_ONLY:
            if has_row:
                stale.append(
                    f"{c.cik} {c.period_start}..{c.period_end}: reason-only cell now has a production value"
                )
            planned.append(PlannedCell(c, company[c.cik], pid, "reason"))
        else:
            planned.append(
                PlannedCell(
                    c,
                    company[c.cik],
                    live[c.prod_cf_id][3] if c.prod_cf_id in live else None,
                    "hide",
                )
            )
    if stale:
        raise ReleaseRefused(
            f"STALE: {len(stale)} cells drifted since the package was cut; re-cut it. First: {stale[:5]}"
        )
    summary = {
        "concept_id": concept_id,
        "cells": len(planned),
        "reasons": len(planned),
        "hides": sum(1 for p in planned if p.action == "hide"),
        "companies": len(ciks),
        "reason_only_without_period_row": sum(
            1 for p in planned if p.period_id is None
        ),
    }
    return planned, summary


def _guard_present(cur) -> bool:
    cur.execute("select to_regclass('analytics.slot_protected_cell') is not null")
    return bool(cur.fetchone()[0])


def _blank_protection_allowed(cur) -> bool:
    cur.execute(
        "select is_nullable = 'YES' from information_schema.columns "
        "where table_schema = 'analytics' and table_name = 'slot_protected_cell' and column_name = 'value'"
    )
    row = cur.fetchone()
    return bool(row and row[0])


def apply_batch(
    conn, run_id: str, digest: str, batch: list[PlannedCell], concept_id: int
) -> dict[str, int]:
    """One company batch in ONE transaction: reasons, archive/remove, protection."""
    try:
        with conn.cursor() as cur:
            cur.execute("set local scrooner.slot_writer = 'on'")
            reasons = [
                cs.BlankReason(
                    key=CellKey(
                        p.company_id,
                        DATA_POINT,
                        p.cell.period_grain,
                        p.cell.period_start,
                        p.cell.period_end,
                    ),
                    state="not_presented",
                    rule_id=RULE_ID,
                    reason_code=REASON_CODE,
                    reason_text=p.cell.reason_text,
                    input_refs={
                        **p.cell.input_refs,
                        "package_digest": digest,
                        "stratum": p.cell.stratum,
                    },
                )
                for p in batch
            ]
            n_reasons = cs.write_blank_reasons(conn, run_id, reasons)
            hide_ids = [p.cell.prod_cf_id for p in batch if p.action == "hide"]
            removed = ca.archive_and_remove(
                cur, hide_ids, reason_code=REASON_CODE, run_id=run_id
            )
            if removed != len(hide_ids):
                raise ReleaseRefused(
                    f"removed {removed} of {len(hide_ids)} rows: production moved mid-run"
                )
            prot = [
                (p.company_id, concept_id, p.period_id)
                for p in batch
                if p.period_id is not None
            ]
            cur.executemany(
                """
                insert into analytics.slot_protected_cell
                    (company_id, canonical_concept_id, period_id, rule_id, value, run_id, package_sha256)
                values (%s, %s, %s, %s, null, %s, %s)
                on conflict (company_id, canonical_concept_id, period_id) do nothing
                """,
                [(c, k, pid, RULE_ID, run_id, digest) for c, k, pid in prot],
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return {"reasons": n_reasons, "removed": removed, "protected": len(prot)}


def apply(
    conn,
    pkg: Package,
    *,
    confirm: str,
    environ=None,
    batch_companies: int = DEFAULT_BATCH_COMPANIES,
    git_commit: str | None = None,
) -> dict[str, Any]:
    """Guards first (no DB access before they pass), then plan, then batches."""
    if not rule_enabled(RULE_ID, environ):
        raise ReleaseRefused(
            f"{RULE_ID} is not ON (mode {rule_mode(RULE_ID, environ)})"
        )
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused(f"--confirm must equal {CONFIRM_TOKEN}")
    if batch_companies < 1:
        raise ReleaseRefused("batch_companies must be >= 1")
    with conn.cursor() as cur:
        if not _guard_present(cur):
            raise ReleaseRefused(
                "migration 0113 (analytics.slot_protected_cell) is not applied: "
                "removed values would be re-derived by the next nightly"
            )
        if not _blank_protection_allowed(cur):
            raise ReleaseRefused(
                "migration 0115 (slot_protected_cell.value nullable) is not applied: "
                "protected blanks cannot be written"
            )
        planned, summary = plan(cur, pkg)
    conn.rollback()
    by_cik: dict[str, list[PlannedCell]] = defaultdict(list)
    for p in planned:
        by_cik[p.cell.cik].append(p)
    ciks = sorted(by_cik)
    run_id = cs.start_rule_run(
        conn,
        RULE_ID,
        "apply",
        "on",
        ciks,
        train=TRAIN,
        git_commit=git_commit,
        before_image_ref=f"analytics.canonical_fact_retired by run_id; package digest {pkg.digest}",
    )
    conn.commit()
    totals = {"reasons": 0, "removed": 0, "protected": 0}
    batches = 0
    for i in range(0, len(ciks), batch_companies):
        s = apply_batch(
            conn,
            run_id,
            pkg.digest,
            [p for k in ciks[i : i + batch_companies] for p in by_cik[k]],
            summary["concept_id"],
        )
        batches += 1
        for k, v in s.items():
            totals[k] += v
    result = {
        "run_id": run_id,
        "rule_id": RULE_ID,
        "batches_committed": batches,
        "touched_ciks": ciks,
        "plan": summary,
        **totals,
    }
    cs.finish_rule_run(
        conn, run_id, {k: v for k, v in result.items() if k != "touched_ciks"}
    )
    conn.commit()
    return result


def restore(
    conn, run_id: str, *, confirm: str = "", git_commit: str | None = None
) -> dict[str, Any]:
    """Undo one apply run exactly, in one transaction."""
    if confirm != CONFIRM_TOKEN:
        raise ReleaseRefused(f"--confirm must equal {CONFIRM_TOKEN}")
    try:
        with conn.cursor() as cur:
            cur.execute(
                "select rule_id, mode, ciks from analytics.rule_run where run_id = %s::uuid",
                (run_id,),
            )
            row = cur.fetchone()
            if row is None or row[0] != RULE_ID or row[1] != "apply":
                raise ReleaseRefused(f"run {run_id} is not an apply run of {RULE_ID}")
            cur.execute("set local scrooner.slot_writer = 'on'")
            restored = ca.restore_run(cur, run_id)
            reasons = cs.delete_run_blank_reasons(conn, run_id)
            unprotected = 0
            if _guard_present(cur):
                cur.execute(
                    "delete from analytics.slot_protected_cell where run_id = %s and rule_id = %s",
                    (run_id, RULE_ID),
                )
                unprotected = cur.rowcount
        rb = cs.start_rule_run(
            conn,
            RULE_ID,
            "rollback",
            "on",
            row[2] or [],
            train=TRAIN,
            git_commit=git_commit,
            before_image_ref=f"restores run {run_id}",
        )
        out = {
            "rollback_run_id": rb,
            "restored_rows": restored,
            "reasons_deleted": reasons,
            "protection_removed": unprotected,
            "restores": run_id,
        }
        cs.finish_rule_run(conn, rb, out)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return out


def _git_commit() -> str | None:
    import subprocess

    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main(argv: list[str] | None = None, environ=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("dry-run", "apply"):
        sp = sub.add_parser(name)
        sp.add_argument("--package-dir", type=Path, default=PACKAGE_DIR)
        sp.add_argument(
            "--digest",
            required=True,
            help="reviewed package digest (sha256 over the stratum digests)",
        )
    sub.choices["apply"].add_argument("--confirm", default="")
    sub.choices["apply"].add_argument(
        "--batch-companies", type=int, default=DEFAULT_BATCH_COMPANIES
    )
    sp = sub.add_parser("restore")
    sp.add_argument("--run-id", required=True)
    sp.add_argument("--confirm", default="")
    sp = sub.add_parser("digest")
    sp.add_argument("--package-dir", type=Path, default=PACKAGE_DIR)
    args = ap.parse_args(argv)

    from scrooner_pipeline.db.connection import get_connection

    try:
        if args.cmd == "digest":
            print(
                package_digest(
                    json.loads((args.package_dir / "PACKAGE.json").read_text())
                )
            )
            return 0
        if args.cmd == "restore":
            with get_connection() as conn:
                print(
                    json.dumps(
                        restore(
                            conn,
                            args.run_id,
                            confirm=args.confirm,
                            git_commit=_git_commit(),
                        ),
                        indent=1,
                    )
                )
            return 0
        pkg = load_package(args.package_dir, args.digest)  # before any DB access
        if args.cmd == "dry-run":
            with get_connection() as conn:
                conn.read_only = True
                with conn.cursor() as cur:
                    cur.execute("set statement_timeout = '120s'")
                    guard = _guard_present(cur)
                    blanks_ok = guard and _blank_protection_allowed(cur)
                    _planned, summary = plan(cur, pkg)
            print(
                f"rule {RULE_ID} mode={rule_mode(RULE_ID, environ)} digest={pkg.digest} DRY RUN, nothing written"
            )
            print(
                f"  guard table (0113): {'present' if guard else 'ABSENT: apply will refuse'}"
            )
            print(
                f"  protected blanks (0115, value nullable): {'yes' if blanks_ok else 'NO: apply will refuse'}"
            )
            for k, v in summary.items():
                print(f"  {k}: {v}")
            return 0
        with get_connection() as conn:
            res = apply(
                conn,
                pkg,
                confirm=args.confirm,
                environ=environ,
                batch_companies=args.batch_companies,
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
